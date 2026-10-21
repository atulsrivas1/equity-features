"""Fresh eight-distribution qualification of the external EQ116 consumer.

Run only after exact source/tool review. Retain failed work; never overwrite a
prior output. Archive helpers are the unchanged accepted ledger builder.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist/evidence-pilot'
IO = ROOT / '.eq116-inputs/io'
IO_HEAD = '18d86761aa3eebb7414e51e8fa2aba089717b5eb'
PACKAGES = {
    'contracts': ('equity_feature_contracts', '0.0.4a4'),
    'features': ('equity_features', '0.0.4a5'),
    'evidence': ('equity_feature_evidence', '0.1.0a2'),
    'explanations': ('equity_feature_explanations', '0.1.0a2'),
    'diagnostics': ('equity_feature_diagnostics', '0.1.0a1'),
    'agent-evidence': ('equity_feature_agent_evidence', '0.1.0a1'),
    'agent-ledger': ('equity_feature_agent_ledger', '0.1.0a1'),
    'bundles': ('equity_feature_bundles', '0.1.0a1'),
}


def sha(raw):return hashlib.sha256(raw).hexdigest()
def git(root, *args):return subprocess.check_output(['git', *args], cwd=root)
def dump(value):return (json.dumps(value, sort_keys=True, indent=2, ensure_ascii=True) + '\n').encode()


def tree(root, head):
    result = {}
    for entry in git(root, 'ls-tree', '-rz', head).split(b'\0'):
        if not entry:continue
        fields, name = entry.split(b'\t', 1)
        mode, kind, oid = fields.decode('ascii').split()
        assert kind == 'blob' and mode in ('100644', '100755')
        result[name.decode('utf-8')] = dict(mode=mode, git_blob=oid)
    return result


def main():
    assert sys.version_info[:2] == (3, 12) and platform.machine().lower() in ('amd64', 'x86_64')
    assert not OUT.exists(), 'Fresh owned output required; preserve previous evidence'
    head = git(ROOT, 'rev-parse', 'HEAD').decode().strip()
    assert git(IO, 'rev-parse', 'HEAD').decode().strip() == IO_HEAD
    full_tree, io_tree = tree(ROOT, head), tree(IO, IO_HEAD)
    inputs = json.loads(git(ROOT, 'show', head + ':docs/stories/EQ116_INPUTS.json'))
    canonical = {p: git(ROOT, 'show', head + ':' + p) for p in full_tree if
        any(p.startswith('packages/' + n + '/') for n in PACKAGES if n != 'bundles') or
        p.startswith(('tests/evidence_pilot/', 'tests/evidence_pilot_archives/')) or p in (
            'examples/evidence_pilot.py', 'examples/evidence_pilot_typed.py', 'examples/agent_research.py',
            'docs/stories/EQ116_ORACLES.json', 'docs/stories/EQ116_PROTOCOL.md',
            'docs/stories/EQ116_INPUTS.json', 'tools/build_evidence_pilot.py',
            'tools/evidence_pilot_archives.py', 'tools/build_agent_ledger.py', '.github/workflows/evidence-pilot.yml', 'requirements-dev.txt')}
    selected_io = {p: git(IO, 'show', IO_HEAD + ':' + p) for p in io_tree if p.startswith('packages/bundles/')}
    assert set(selected_io) == set(inputs['io'])
    for p, desc in inputs['canonical'].items():
        if p.startswith('packages/') or p in ('examples/agent_research.py', 'tools/build_agent_ledger.py'):
            assert p in canonical and len(canonical[p]) == desc['bytes'] and sha(canonical[p]) == desc['sha256']
    for p, desc in inputs['io'].items():assert len(selected_io[p]) == desc['bytes'] and sha(selected_io[p]) == desc['sha256']
    materialized = {p: (ROOT / p).read_bytes() for p in canonical}
    for p, raw in canonical.items():assert materialized[p].replace(b'\r\n', b'\n') == raw
    assert not git(ROOT, 'status', '--porcelain', '--untracked-files=all', '--', *canonical)
    OUT.mkdir(parents=True)
    work = ROOT / 'work';work.mkdir(exist_ok=True)
    owned = Path(tempfile.mkdtemp(prefix='eq116-', dir=work)).resolve()
    assert owned.parent == work.resolve() and not owned.is_symlink()
    verification = owned / 'verification'
    for p, raw in canonical.items():
        path = verification / p;path.parent.mkdir(parents=True, exist_ok=True);path.write_bytes(raw)
    spec = importlib.util.spec_from_file_location('_eq116_accepted_archive_helpers', verification / 'tools/build_agent_ledger.py')
    assert spec and spec.loader
    helper = importlib.util.module_from_spec(spec);spec.loader.exec_module(helper)
    helper.PACKAGES = PACKAGES
    spec = importlib.util.spec_from_file_location('_eq116_archive_closure', verification / 'tools/evidence_pilot_archives.py')
    assert spec and spec.loader
    audit = importlib.util.module_from_spec(spec);spec.loader.exec_module(audit)
    counter = 0
    logs = []
    def run(*args, cwd=owned, env=None):
        nonlocal counter
        counter += 1
        prefix = '%03d' % counter
        effective = dict(os.environ if env is None else env)
        for key in ('PYTHONPATH', 'PYTHONHOME', 'MYPYPATH'):effective.pop(key, None)
        stdout, stderr = OUT / (prefix + '.stdout'), OUT / (prefix + '.stderr')
        with stdout.open('xb') as out, stderr.open('xb') as err:
            result = subprocess.run([str(x) for x in args], cwd=cwd, env=effective, stdout=out, stderr=err)
        logs.append(dict(id=prefix, returncode=result.returncode, stdout=sha(stdout.read_bytes()), stderr=sha(stderr.read_bytes())))
        if result.returncode:
            print(stdout.read_text(errors='replace')[-12000:], flush=True)
            print(stderr.read_text(errors='replace')[-12000:], flush=True)
        assert result.returncode == 0, 'Retained command failure ' + prefix
        return stdout.read_bytes()
    helper.run = run
    report = dict(schema='eq116.qualification.v1', source_commit=head, io_head=IO_HEAD,
        system=platform.system(), python=platform.python_version(), machine=platform.machine(),
        status='running', whole_git_tree=full_tree, whole_io_git_tree=io_tree,
        effective_source={p: dict(bytes=len(raw), sha256=sha(raw)) for p, raw in canonical.items()},
        io_source=inputs['io'], artifacts={}, cohorts={}, logs=logs)
    def save():(OUT / 'qualification.json').write_bytes(dump(report))
    def closure():
        assert git(ROOT, 'rev-parse', 'HEAD').decode().strip() == head and tree(ROOT, head) == full_tree
        assert git(IO, 'rev-parse', 'HEAD').decode().strip() == IO_HEAD and tree(IO, IO_HEAD) == io_tree
        assert all((ROOT / p).read_bytes() == raw for p, raw in materialized.items())
        assert not git(ROOT, 'status', '--porcelain', '--untracked-files=all', '--', *canonical)
    save()
    try:
        run(sys.executable, '-I', '-c',
            'import sys,unittest;s=unittest.defaultTestLoader.discover(sys.argv[1]);r=unittest.TextTestRunner(verbosity=2).run(s);assert r.testsRun==5 and r.wasSuccessful() and not r.skipped',
            verification / 'tests/evidence_pilot_archives')
        report['inert_archive_control_methods'] = 5;save()
        sources = {}
        for repeat in (0, 1):
            dest = owned / ('archives-' + str(repeat));dest.mkdir()
            for name, (module, version) in PACKAGES.items():
                source = owned / ('source-%d-%s' % (repeat, name));source.mkdir()
                selected = selected_io if name == 'bundles' else canonical
                prefix = 'packages/' + name + '/'
                for p, raw in selected.items():
                    if p.startswith(prefix):
                        path = source / p.removeprefix(prefix);path.parent.mkdir(parents=True, exist_ok=True);path.write_bytes(raw)
                sources[name] = source
                run(sys.executable, '-m', 'build', '--no-isolation', '--outdir', dest, source,
                    env=dict(os.environ, SOURCE_DATE_EPOCH='1700000000', PYTHONHASHSEED='0'))
                archives = list(dest.glob(module + '-*'));assert len(archives) == 2
                for path in archives:
                    if path.suffix != '.whl':helper.contents(path);helper.normalize(path)
                    proof = audit.inspect(path, name, source, helper)
                    if repeat == 0:
                        report['artifacts'][path.name] = proof;shutil.copyfile(path, OUT / path.name)
                    else:assert proof == report['artifacts'][path.name], 'Repeat archive differs'
                save()
        assert len(report['artifacts']) == 16
        report['repeat_16_archive_parity'] = True
        # Fully materialize every SDist, including generated files, and rebuild
        # its wheel. Do not substitute the original source directory.
        rebuilt = {}
        for name, (module, version) in PACKAGES.items():
            archive = next(OUT.glob(module + '-*.tar.gz'))
            members = helper.contents(archive);prefix = archive.name.removesuffix('.tar.gz') + '/'
            source = owned / ('sdist-selected-' + name);source.mkdir()
            for relative, raw in members.items():
                assert relative.startswith(prefix)
                target = source / relative.removeprefix(prefix);target.parent.mkdir(parents=True, exist_ok=True);target.write_bytes(raw)
            before_build = audit.file_map(source)
            dest = owned / ('rebuilt-' + name);dest.mkdir()
            run(sys.executable, '-m', 'build', '--wheel', '--no-isolation', '--outdir', dest, source,
                env=dict(os.environ, SOURCE_DATE_EPOCH='1700000000', PYTHONHASHSEED='0'))
            after_build = audit.file_map(source)
            generated_transition = audit.sdist_transition(before_build, after_build, module, source)
            wheel = next(dest.glob('*.whl'));proof = audit.inspect(wheel, name, source, helper)
            assert proof == report['artifacts'][wheel.name], 'Selected SDist wheel closure differs'
            rebuilt[name] = wheel
            report.setdefault('selected_sdist_closure', {})[name] = dict(
                archive_sha256=sha(archive.read_bytes()), wheel_sha256=sha(wheel.read_bytes()),
                materialized={p: dict(bytes=len(raw), sha256=sha(raw)) for p, raw in members.items()},
                generated_transition=generated_transition)
            save()
        harness = verification / 'examples/evidence_pilot.py'
        exports = {}
        for form in ('wheel-compute', 'wheel-light', 'sdist-compute', 'sdist-light'):
            compute = form.endswith('compute')
            selected = [name for name in PACKAGES if compute or name != 'features']
            paths = [rebuilt[name] if form.startswith('sdist') else next(OUT.glob(PACKAGES[name][0] + '-*.whl')) for name in selected]
            py = helper.install(paths, owned / form)
            modules = [PACKAGES[name][0] for name in selected]
            before = audit.installed(py, selected, paths, helper, run)
            env_fact = json.loads(run(py, '-I', '-c',
                'import sys,platform,json,importlib.util;print(json.dumps(dict(executable=sys.executable,prefix=sys.prefix,version=platform.python_version(),features=importlib.util.find_spec("equity_features") is not None)))'))
            assert env_fact['features'] is compute and Path(env_fact['prefix']).resolve() == py.parent.parent.resolve()
            if compute:
                export = owned / (form + '-export')
                run(py, '-I', harness, 'record', export)
                exports[form.split('-')[0]] = export
            else:export = exports[form.split('-')[0]]
            observations = json.loads(run(py, '-I', harness, 'replay', export, form))
            expected = json.loads(canonical['docs/stories/EQ116_ORACLES.json'])['reader_expectations']
            assert observations == [x for x in expected if x['form'] == form] and len(observations) == 16
            if compute:
                # Separate methods, not extra scenario observations.
                run(py, '-I', '-c',
                    'import sys,unittest; s=unittest.defaultTestLoader.discover(sys.argv[1]);r=unittest.TextTestRunner(verbosity=2).run(s);assert r.testsRun==19 and r.wasSuccessful() and not r.skipped',
                    verification / 'tests/evidence_pilot')
            after = audit.installed(py, selected, paths, helper, run);assert before == after
            export_map = {case.name: {p.name: dict(bytes=p.stat().st_size, sha256=sha(p.read_bytes())) for p in case.iterdir()} for case in export.iterdir()}
            if compute:
                export_copy = OUT / 'exports' / form.split('-')[0]
                for case in export.iterdir():
                    for path in case.iterdir():
                        target = export_copy / case.name / path.name
                        target.parent.mkdir(parents=True, exist_ok=True)
                        with target.open('xb') as output:output.write(path.read_bytes())
            else:
                assert export_map == report['cohorts'][form.replace('light', 'compute')]['raw_export'], 'Shared export changed across readers'
            proof = dict(environment=env_fact, installed=after, observations=observations,
                selected_archives={p.name: sha(p.read_bytes()) for p in paths},
                raw_export=export_map)
            report['cohorts'][form] = proof;save();closure()
        assert sum(len(x['observations']) for x in report['cohorts'].values()) == 64
        run(sys.executable, '-m', 'mypy', '--strict', '--no-incremental', '--python-executable',
            owned / 'wheel-compute' / ('Scripts/python.exe' if os.name == 'nt' else 'bin/python'),
            verification / 'examples/evidence_pilot.py', verification / 'examples/evidence_pilot_typed.py')
        closure();report['status'] = 'passed';save()
    except BaseException:
        report['status'] = 'failed';save();raise


if __name__ == '__main__':main()
