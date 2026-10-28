"""R8 repeat archives and fresh installed consumers; separate from core artifact gates."""
from __future__ import annotations

import base64
import csv
from email.parser import BytesParser
import gzip
import hashlib
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import shutil
import subprocess
import sys
import tarfile
import tempfile
import zipfile
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/_versions.py, also when loaded by path from tests
from _versions import VERSIONS, CONTRACTS, FEATURES


def _fill(code, component='strategies'):
    """Substitute the version placeholders of the isolated-interpreter probe snippets from tools/_versions.py."""
    return (code.replace('@CONTRACTS@', CONTRACTS).replace('@FEATURES@', FEATURES)
            .replace('@STRATEGIES@', VERSIONS[component]))

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist/research'
EPOCH = 1700000000
PACKAGES = {'contracts': ('equity_feature_contracts', CONTRACTS),
            'features': ('equity_features', FEATURES), 'strategies': ('equity_feature_strategies', VERSIONS['strategies']),
            'labels': ('equity_feature_labels', VERSIONS['labels'])}


def run(*args, cwd=ROOT, env=None):
    subprocess.run([str(a) for a in args], cwd=cwd, env=env, check=True)


def sha(content):
    return hashlib.sha256(content).hexdigest()


def normalize(path):
    """Match existing core gate's explicit reproducible TAR header policy."""
    data = io.BytesIO()
    with tarfile.open(path, 'r:gz') as source, tarfile.open(fileobj=data, mode='w', format=tarfile.PAX_FORMAT) as target:
        for member in sorted(source.getmembers(), key=lambda row: row.name):
            member.mtime = EPOCH; member.uid = member.gid = 0
            member.uname = member.gname = ''; member.pax_headers = {}
            member.mode = 0o755 if member.isdir() else 0o644
            target.addfile(member, source.extractfile(member) if member.isfile() else None)
    with path.open('wb') as output, gzip.GzipFile(fileobj=output, mode='wb', filename='', mtime=EPOCH) as zipped:
        zipped.write(data.getvalue())


def contents(path):
    if path.suffix == '.whl':
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist()
            assert len(names) == len(set(names)), 'duplicate archive entry'
            files = {name: archive.read(name) for name in names if not name.endswith('/')}
    else:
        with tarfile.open(path, 'r:gz') as archive:
            members = archive.getmembers()
            assert len(members) == len({m.name for m in members})
            assert all(m.isfile() or m.isdir() for m in members), 'nonregular archive entry'
            files = {m.name: archive.extractfile(m).read() for m in members if m.isfile()}
    for name in files:
        parts = PurePosixPath(name).parts
        assert not name.startswith(('/', '\\')) and '\\' not in name and '..' not in parts
        assert not any(part in ('__pycache__', '.git', '.env') for part in parts)
        assert not name.endswith(('.pyc', '.pyo'))
    return files


def inspect(path, package, source):
    files = contents(path)
    module, version = PACKAGES[package]
    wheel = path.suffix == '.whl'
    prefix = '' if wheel else path.name.removesuffix('.tar.gz') + '/'
    metadata_name = next(n for n in files if n.endswith('/METADATA' if wheel else '/PKG-INFO') and
        (wheel or n == prefix + 'PKG-INFO'))
    metadata = BytesParser().parsebytes(files[metadata_name])
    assert metadata['Name'] == module.replace('_', '-')
    assert metadata['Version'] == version
    assert metadata['License-Expression'] == 'Apache-2.0'
    assert metadata['Requires-Python'] == '<3.13,>=3.12'
    if package in ('strategies', 'labels'):
        assert metadata.get_all('Requires-Dist', []) == [f'equity-feature-contracts=={CONTRACTS}']
    module_prefix = module + '/' if wheel else prefix + 'src/' + module + '/'
    expected = {p.relative_to(source / 'src').as_posix(): p.read_bytes()
                for p in (source / 'src' / module).rglob('*') if p.is_file() and '__pycache__' not in p.parts}
    actual = {module + '/' + name.removeprefix(module_prefix): body
              for name, body in files.items() if name.startswith(module_prefix)}
    assert actual == expected, 'complete source/package byte map differs'
    assert module + '/py.typed' in actual
    license_name = next(n for n in files if n.endswith('/licenses/LICENSE')) if wheel else prefix + 'LICENSE'
    assert files[license_name] == (source / 'LICENSE').read_bytes()
    if wheel:
        assert all(n.startswith((module + '/', module + '-')) for n in files)
        record = next(n for n in files if n.endswith('/RECORD'))
        rows = list(csv.reader(io.StringIO(files[record].decode('utf-8'))))
        assert len(rows) == len(files) and {r[0] for r in rows} == set(files)
        for name, encoded, size in rows:
            if name == record:
                assert encoded == size == ''
            else:
                assert encoded == 'sha256=' + base64.urlsafe_b64encode(hashlib.sha256(files[name]).digest()).rstrip(b'=').decode()
                assert int(size) == len(files[name])
    else:
        allowed = {prefix + x for x in ('LICENSE', 'README.md', 'pyproject.toml', 'PKG-INFO', 'setup.cfg')}
        assert all(n in allowed or n.startswith((prefix + 'src/' + module + '/', prefix + 'src/' + module + '.egg-info/')) for n in files)
        assert files[prefix + 'pyproject.toml'] == (source / 'pyproject.toml').read_bytes()
    return {'sha256': sha(path.read_bytes()), 'bytes': path.stat().st_size,
            'entries': {name: {'sha256': sha(body), 'bytes': len(body)} for name, body in sorted(files.items())},
            'source_map': {name: sha(body) for name, body in sorted(expected.items())},
            'record_verified': wheel, 'version': version}


def fingerprint(py, modules):
    code = '''import hashlib,importlib,json,sys
from pathlib import Path
from importlib.metadata import distribution
result={}
for module_name in sys.argv[1:]:
    module=importlib.import_module(module_name)
    root=Path(module.__file__).resolve().parent
    assert 'site-packages' in root.parts
    for path in root.rglob('*'):
        if path.is_file() and '__pycache__' not in path.parts:
            result[module_name+'/'+path.relative_to(root).as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
    dist=distribution(module_name.replace('_','-'))
    for relative in dist.files:
        path=Path(dist.locate_file(relative)).resolve()
        if path.is_file() and '__pycache__' not in path.parts:
            assert 'site-packages' in path.parts
            result[relative.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
print(json.dumps(result,sort_keys=True))
'''
    return json.loads(subprocess.check_output([str(py), '-I', '-c', _fill(code), *modules], cwd=py.parent, encoding='utf-8'))


def install(paths, directory):
    run(sys.executable, '-m', 'venv', directory)
    py = directory / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python')
    if paths[0].suffix != '.whl':
        run(py, '-m', 'pip', 'install', '--no-deps', 'setuptools==80.9.0')
    run(py, '-m', 'pip', 'install', '--no-index', '--no-deps', '--no-build-isolation', *paths)
    run(py, '-m', 'pip', 'check')
    return py


def installed_core_maps(actual, paths):
    """Verify every installed core package payload against its selected archive."""
    for name, artifact in paths.items():
        module = PACKAGES[name][0]
        prefix = module + '/' if artifact.suffix == '.whl' else artifact.name.removesuffix('.tar.gz') + '/src/' + module + '/'
        expected = {module + '/' + entry.removeprefix(prefix): sha(body)
                    for entry, body in contents(artifact).items() if entry.startswith(prefix)}
        assert expected
        assert {entry: hashed for entry, hashed in actual.items() if entry.startswith(module + '/')} == expected


def core_only(py):
    """Actual installed imports before either research distribution is installed."""
    code = '''import importlib.util,json,sys
from pathlib import Path
from importlib.metadata import distribution
import equity_feature_contracts as c
import equity_features as f
assert (c.__version__,f.__version__,f.contracts_version)==('@CONTRACTS@','@FEATURES@','@CONTRACTS@')
assert distribution('equity-feature-contracts').version=='@CONTRACTS@'
assert distribution('equity-features').version=='@FEATURES@'
assert distribution('equity-feature-contracts').requires is not None
required=[r for r in distribution('equity-features').requires if ';' not in r]
assert required==['equity-feature-contracts==@CONTRACTS@']
assert all('equity-feature-strategies' not in r and 'equity-feature-labels' not in r for d in ('equity-feature-contracts','equity-features') for r in distribution(d).requires)
for module in (c,f):
    root=Path(module.__file__).resolve().parent
    assert 'site-packages' in root.parts and (root/'py.typed').is_file()
absent=('equity_feature_strategies','equity_feature_labels','numpy','pyarrow','duckdb')
assert all(importlib.util.find_spec(name) is None for name in absent)
assert not any(name.split('.')[0] in absent for name in sys.modules)
print(json.dumps({'contracts_version':c.__version__,'features_version':f.__version__,'site_packages_origins':True,'optional_and_native_absent':list(absent),'required_features_dependency':required},sort_keys=True))
'''
    return json.loads(subprocess.check_output([str(py), '-I', '-c', _fill(code)], cwd=py.parent, encoding='utf-8'))


def installed_component(py, artifact, component):
    files = contents(artifact)
    module = PACKAGES[component][0]
    prefix = module + '/' if artifact.suffix == '.whl' else artifact.name.removesuffix('.tar.gz') + '/src/' + module + '/'
    expected = {name.removeprefix(prefix): sha(body) for name, body in files.items() if name.startswith(prefix)}
    code = '''import ast,base64,csv,hashlib,importlib.util,io,json,sys
from pathlib import Path
from importlib.metadata import distribution,version
import equity_feature_strategies as s
root=Path(s.__file__).resolve().parent
assert 'site-packages' in root.parts
assert s.__version__==version('equity-feature-strategies')=='@STRATEGIES@'
assert distribution('equity-feature-strategies').requires==['equity-feature-contracts==@CONTRACTS@']
dist=distribution('equity-feature-strategies')
record=next(f for f in dist.files if f.name=='RECORD')
rows=list(csv.reader(io.StringIO(Path(dist.locate_file(record)).read_text(encoding='utf-8'))))
assert len(rows)==len({r[0] for r in rows})==len(dist.files)
assert {r[0] for r in rows}=={str(f) for f in dist.files}
for name,encoded,size in rows:
    path=Path(dist.locate_file(name)).resolve()
    assert 'site-packages' in path.parts and path.is_file()
    if encoded:
        content=path.read_bytes()
        assert encoded=='sha256='+base64.urlsafe_b64encode(hashlib.sha256(content).digest()).rstrip(b'=').decode()
        assert int(size)==len(content)
    else:
        assert name.endswith(('/RECORD','.pyc')) and size==''
assert (root/'py.typed').is_file()
assert all(importlib.util.find_spec(name) is None for name in ('equity_features','equity_feature_labels','numpy','pyarrow','duckdb'))
allowed={'__future__','dataclasses','math','re','typing','enum','hashlib','json','operator','equity_feature_contracts'}
for path in root.rglob('*.py'):
    for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
        if isinstance(node,ast.Import):assert all(a.name.split('.')[0] in allowed for a in node.names)
        elif isinstance(node,ast.ImportFrom) and not node.level:assert node.module.split('.')[0] in allowed
assert not any(name.split('.')[0] in ('equity_features','equity_feature_labels','numpy','pyarrow','duckdb') for name in sys.modules)
print(json.dumps({p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts},sort_keys=True))
'''
    if component == 'labels':
        code = code.replace('equity_feature_labels', '__SIBLING__').replace('equity_feature_strategies', 'equity_feature_labels').replace('__SIBLING__', 'equity_feature_strategies')
        code = code.replace('equity-feature-strategies', 'equity-feature-labels')
    actual = json.loads(subprocess.check_output([str(py), '-I', '-c', _fill(code, component)], cwd=py.parent, encoding='utf-8'))
    assert actual == expected, 'installed component differs from archive source'
    return actual


def installed_typing(py, directory, component):
    """Actual strict consumers against installed py.typed; type tools are not runtime deps."""
    run(py, '-m', 'pip', 'install', '--no-deps', 'mypy==1.15.0',
        'mypy_extensions==1.1.0', 'typing_extensions==4.16.0')
    positive = '''from equity_feature_strategies import StrategyRequest, StrategyResult, StrategyError, scan, encode
def consume(request: StrategyRequest) -> StrategyResult:
    result: StrategyResult = scan(request)
    content: bytes = encode(result)
    identity: str = result.identity_digest
    code: str = StrategyError('invalid_schema').code
    assert content and identity and code
    return result
'''
    negative = '''from equity_feature_strategies import StrategyResult, scan
def invalid() -> StrategyResult:
    return scan(23)
'''
    if component == 'labels':
        positive = positive.replace('equity_feature_strategies', 'equity_feature_labels').replace('StrategyRequest', 'LabelRequest').replace('StrategyResult', 'LabelResult').replace('StrategyError', 'LabelError').replace('scan', 'evaluate_label')
        negative = negative.replace('equity_feature_strategies', 'equity_feature_labels').replace('StrategyResult', 'LabelResult').replace('scan', 'evaluate_label')
    operation = 'scan' if component == 'strategies' else 'evaluate_label'
    rows = {}
    for name, source in (('positive', positive), ('negative', negative)):
        path = directory / (name + '.py')
        path.write_text(source, encoding='utf-8')
        process = subprocess.run([str(py), '-I', '-m', 'mypy', '--strict', '--no-incremental',
            '--python-executable', str(py), str(path)], cwd=directory, capture_output=True, encoding='utf-8')
        output = process.stdout + process.stderr
        if name == 'positive':
            assert process.returncode == 0, output
        else:
            assert process.returncode == 1 and '[arg-type]' in output and operation in output, output
            assert 'import-untyped' not in output and 'import-not-found' not in output
        rows[name] = {'source_sha256': sha(source.encode('utf-8')), 'exit_code': process.returncode,
                      'output_sha256': sha(output.encode('utf-8'))}
    run(py, '-m', 'pip', 'check')
    return rows


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    assert not list(OUT.iterdir()), 'fresh dist/research required; preserve previous reports before rerun'
    report = {'schema': 'research-qualification:2', 'system': platform.system(), 'python': platform.python_version(),
        'source_commit': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, encoding='utf-8').strip(),
        'epoch': EPOCH, 'sdist_policy': 'normalized TAR metadata; source payload unchanged', 'artifacts': {}, 'installed': [], 'combined': [], 'source': {}, 'status': 'running'}
    scopes = ['packages/' + name for name in PACKAGES] + ['tests/research', 'examples/research_scanner.py', 'examples/research_labels.py', 'examples/research_backtest.py',
        'tools/build_research.py', 'tools/check_boundary.py','tools/_versions.py', '.github/workflows/research.yml', 'requirements-dev.txt',
        'docs/stories/EQ-089_FIXTURES.json']
    head = report['source_commit']
    source_paths = tuple(subprocess.check_output(['git', 'ls-files', '--', *scopes], cwd=ROOT, encoding='utf-8').splitlines())
    assert source_paths
    # Artifacts AND executed test/example inputs come only from this closed Git snapshot.
    # No recursive live-directory copy can smuggle untracked or ignored files into the build.
    snapshot, materialization = {}, {}
    for relative in source_paths:
        committed = subprocess.check_output(['git', 'show', head + ':' + relative], cwd=ROOT)
        materialized = (ROOT / relative).read_bytes()
        assert materialized == committed or materialized.replace(b'\r\n', b'\n') == committed, 'uncommitted qualification bytes'
        snapshot[relative] = committed
        materialization[relative] = materialized
        report['source'][relative] = {'git_sha256': sha(committed), 'materialized_sha256': sha(materialized),
            'materialization': 'exact' if materialized == committed else 'CRLF-only', 'built_from': 'committed-Git-bytes'}
    def source_closure():
        assert subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, encoding='utf-8').strip() == head
        assert tuple(subprocess.check_output(['git', 'ls-files', '--', *scopes], cwd=ROOT, encoding='utf-8').splitlines()) == source_paths
        assert not subprocess.check_output(['git', 'status', '--porcelain', '--untracked-files=all', '--', *scopes], cwd=ROOT), 'qualification source changed'
        assert all((ROOT / name).read_bytes() == body for name, body in materialization.items()), 'materialized source changed'
    source_closure()
    def save():
        (OUT / 'qualification.json').write_text(json.dumps(report, sort_keys=True, indent=2) + '\n', encoding='utf-8')
    save()
    work = ROOT / 'work'; work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='research-', dir=work) as temp:
        temp = Path(temp).resolve()
        assert temp.is_relative_to(work.resolve())
        verification = temp / 'qualification-inputs'
        for relative, body in snapshot.items():
            target = verification / relative
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(body)
        env = dict(os.environ, SOURCE_DATE_EPOCH=str(EPOCH), PYTHONHASHSEED='0')
        built = []
        for repeat in (0, 1):
            destination = temp / f'build-{repeat}'; destination.mkdir()
            for name in PACKAGES:
                source = temp / f'source-{repeat}-{name}'
                prefix = 'packages/' + name + '/'
                for relative, body in snapshot.items():
                    if relative.startswith(prefix):
                        target = source / relative.removeprefix(prefix)
                        target.parent.mkdir(parents=True, exist_ok=True)
                        target.write_bytes(body)
                run(sys.executable, '-m', 'build', '--no-isolation', '--outdir', destination, source, env=env)
                for path in destination.glob('*.tar.gz'):
                    normalize(path)
                artifacts = list(destination.glob(PACKAGES[name][0] + '-*'))
                assert len(artifacts) == 2
                for path in artifacts:
                    inspection = inspect(path, name, source)
                    if repeat == 0:
                        report['artifacts'][path.name] = inspection
                    else:
                        assert report['artifacts'][path.name] == inspection, 'repeat archive differs'
            built.append(destination)
        assert len(report['artifacts']) == 8
        for path in built[0].iterdir():
            shutil.copyfile(path, OUT / path.name)
        report['repeat_archive_parity'] = True; save()
        for form in ('wheel', 'sdist'):
            suffix = '.whl' if form == 'wheel' else '.tar.gz'
            artifact_paths = {name: next(OUT.glob(module + '-*' + suffix)) for name, (module, _) in PACKAGES.items()}
            for component in ('strategies', 'labels'):
                isolated = temp / ('isolated-' + component + '-' + form)
                py = install([artifact_paths['contracts']], isolated)
                before = fingerprint(py, ['equity_feature_contracts'])
                installed_core_maps(before, {'contracts': artifact_paths['contracts']})
                run(py, '-m', 'pip', 'install', '--no-index', '--no-deps', '--no-build-isolation', artifact_paths[component])
                run(py, '-m', 'pip', 'check')
                installed = installed_component(py, artifact_paths[component], component)
                run(py, '-I', '-m', 'unittest', 'discover', '-s', verification / 'tests/research', '-p', 'test_' + component + '.py')
                typing = installed_typing(py, isolated, component)
                after = fingerprint(py, ['equity_feature_contracts'])
                assert before == after, 'research install/execution changed contracts'
                report['installed'].append({'component': component, 'form': form, 'component_source': installed,
                    'contracts_before_after': before, 'isolated_origins': True,
                    'independent_fixtures_passed': True, 'installed_typing': typing})
                save()
            # Both research packages are explicit dependencies of this separate application.
            consumer = temp / ('consumer-' + form)
            cpy = install([artifact_paths['contracts'], artifact_paths['features']], consumer)
            core_before = fingerprint(cpy, ['equity_feature_contracts', 'equity_features'])
            installed_core_maps(core_before, {'contracts': artifact_paths['contracts'], 'features': artifact_paths['features']})
            core_isolation = core_only(cpy)
            run(cpy, '-m', 'pip', 'install', '--no-index', '--no-deps', '--no-build-isolation', artifact_paths['strategies'], artifact_paths['labels'])
            run(cpy, '-m', 'pip', 'check')
            run(cpy, '-I', verification / 'examples/research_scanner.py')
            run(cpy, '-I', verification / 'examples/research_labels.py')
            run(cpy, '-I', verification / 'examples/research_backtest.py')
            assert core_before == fingerprint(cpy, ['equity_feature_contracts', 'equity_features'])
            report['combined'].append({'form': form, 'consumer_core_before_after': core_before,
                'actual_core_producer_passed': True, 'signal_invariance_and_as_of_joins_passed': True,
                'chronological_watchlist_labels_revisions_passed': True, 'core_only_isolation': core_isolation})
            save()
    source_closure()
    report['source_head_and_materialization_closure'] = True
    report['status'] = 'completed'; save()


if __name__ == '__main__':
    main()
