"""Archive and installed closure for EQ116's eight unchanged distributions."""
import base64
import csv
from email.parser import BytesParser
import hashlib
import io
import json
import sysconfig
import tomllib
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet


def sha(raw):return hashlib.sha256(raw).hexdigest()


def inspect(path, name, source, helper):
    """Accepted complete member policy, with optional project URLs handled explicitly."""
    module, version = helper.PACKAGES[name]
    files, members = helper.contents(path, with_members=True)
    wheel = path.suffix == '.whl'
    prefix = '' if wheel else path.name.removesuffix('.tar.gz') + '/'
    metadata_name = module + '-' + version + '.dist-info/METADATA' if wheel else prefix + 'PKG-INFO'
    metadata = BytesParser().parsebytes(files[metadata_name])
    project = tomllib.loads((source / 'pyproject.toml').read_text(encoding='utf-8'))['project']
    assert project['name'] == module.replace('_', '-') and project['version'] == version
    assert metadata['Name'] == project['name'] and metadata['Version'] == version
    assert metadata['License-Expression'] == project['license'] == 'Apache-2.0'
    assert metadata.get_all('License-File', []) == project['license-files'] == ['LICENSE']
    assert metadata['Summary'] == project['description']
    assert str(SpecifierSet(metadata['Requires-Python'])) == str(SpecifierSet(project['requires-python'])) == '<3.13,>=3.12'
    assert all(set(author) == {'name'} for author in project['authors'])
    assert metadata['Author'] == ', '.join(author['name'] for author in project['authors'])
    assert sorted(metadata.get_all('Project-URL', [])) == sorted(k + ', ' + v for k, v in project.get('urls', {}).items())
    assert metadata.get_all('Classifier', []) == project.get('classifiers', [])
    extras = project.get('optional-dependencies', {})
    assert sorted(metadata.get_all('Provides-Extra', [])) == sorted(extras)
    requires = list(project['dependencies'])
    for extra, values in extras.items():
        for requirement in values:
            assert ';' not in requirement
            requires.append(requirement + '; extra == "' + extra + '"')
    assert sorted(str(Requirement(v)) for v in metadata.get_all('Requires-Dist', [])) == sorted(str(Requirement(v)) for v in requires)
    readme = (source / 'README.md').read_bytes()
    assert project['readme'] == 'README.md' and metadata['Description-Content-Type'] == 'text/markdown'
    assert metadata.get_payload(decode=True).replace(b'\r\n', b'\n') == readme.replace(b'\r\n', b'\n')
    package_prefix = module + '/' if wheel else prefix + 'src/' + module + '/'
    expected = {p.relative_to(source / 'src').as_posix(): p.read_bytes() for p in (source / 'src' / module).rglob('*') if p.is_file()}
    actual = {module + '/' + n.removeprefix(package_prefix): raw for n, raw in files.items() if n.startswith(package_prefix)}
    assert actual == expected and module + '/py.typed' in actual
    license_name = module + '-' + version + '.dist-info/licenses/LICENSE' if wheel else prefix + 'LICENSE'
    assert files[license_name] == (source / 'LICENSE').read_bytes()
    if wheel:
        info = module + '-' + version + '.dist-info/'
        assert set(files) == set(expected) | {info + n for n in ('METADATA', 'WHEEL', 'top_level.txt', 'licenses/LICENSE', 'RECORD')}
        rows = list(csv.reader(io.StringIO(files[info + 'RECORD'].decode('utf-8'))))
        assert len(rows) == len(files) and {r[0] for r in rows} == set(files)
        for relative, identity, size in rows:
            if relative == info + 'RECORD':assert identity == size == ''
            else:
                assert identity == 'sha256=' + base64.urlsafe_b64encode(hashlib.sha256(files[relative]).digest()).rstrip(b'=').decode()
                assert int(size) == len(files[relative])
    else:
        allowed = {prefix + n for n in ('LICENSE', 'README.md', 'pyproject.toml', 'PKG-INFO', 'setup.cfg')}
        assert all(n in allowed or n.startswith((prefix + 'src/' + module + '/', prefix + 'src/' + module + '.egg-info/')) for n in files)
        assert files[prefix + 'pyproject.toml'] == (source / 'pyproject.toml').read_bytes()
        assert files[prefix + 'README.md'] == readme
    return dict(sha256=sha(path.read_bytes()), bytes=path.stat().st_size, version=version,
        entries={n: dict(sha256=sha(raw), bytes=len(raw)) for n, raw in sorted(files.items())},
        members=members, source_map={n: sha(raw) for n, raw in sorted(expected.items())},
        metadata_source_readme_verified=True, record_verified=wheel)


def file_map(root):
    result = {}
    for path in root.rglob('*'):
        assert not path.is_symlink()
        name = path.relative_to(root).as_posix()
        if path.is_file():result[name] = dict(kind='file', bytes=path.stat().st_size, sha256=sha(path.read_bytes()))
        else:assert path.is_dir();result[name] = dict(kind='directory')
    return result


def sdist_transition(before, after, module, source):
    """Preserve all source; admit only the fixed backend's generated build files."""
    egg = 'src/' + module + '.egg-info/'
    egg_names = {'PKG-INFO', 'SOURCES.txt', 'dependency_links.txt', 'requires.txt', 'top_level.txt'}
    tag = sysconfig.get_platform()
    assert tag in ('win-amd64', 'linux-x86_64')
    bdist = 'build/bdist.' + tag
    for name, entry in before.items():
        if name == egg + 'SOURCES.txt':
            assert entry['kind'] == 'file' and after.get(name, {}).get('kind') == 'file'
            continue
        assert after.get(name) == entry, 'Selected SDist source changed during wheel build'
    for name, entry in after.items():
        if name in before:continue
        assert name == 'build' or name == 'build/lib' or name == bdist or name == 'build/lib/' + module or name.startswith('build/lib/' + module + '/') or name.startswith(egg), 'Unselected generated build path'
        if name in ('build', 'build/lib', 'build/lib/' + module):assert entry['kind'] == 'directory'
        if name == bdist:assert entry['kind'] == 'directory'
        if name.startswith('build/lib/' + module + '/') and entry['kind'] == 'file':
            original = 'src/' + name.removeprefix('build/lib/')
            assert before.get(original) == entry, 'Generated package bytes differ from selected source'
        if name.startswith(egg):
            assert entry['kind'] == 'file' and name.removeprefix(egg) in egg_names
            # Generated metadata other than the refreshed source manifest must
            # have been selected by the original SDist, byte-identical above.
            assert name == egg + 'SOURCES.txt', 'Unselected new egg metadata'
    sources = (source / egg / 'SOURCES.txt').read_text(encoding='utf-8').splitlines()
    assert len(sources) == len(set(sources))
    for name in sources:
        assert name and not name.startswith(('/', '\\')) and '\\' not in name and ':' not in name and '..' not in name.split('/')
        assert name in after and after[name]['kind'] == 'file'
    required = {n for n, e in before.items() if e['kind'] == 'file' and (n.startswith('src/' + module + '/') or n in ('LICENSE', 'README.md', 'pyproject.toml', 'setup.cfg'))}
    assert required <= set(sources), 'Generated SOURCES omits selected package/build input'
    return dict(before=before, after=after, changed={n: dict(before=before.get(n), after=after.get(n)) for n in before.keys() | after.keys() if before.get(n) != after.get(n)}, sources=sources)


INSTALLED = r'''
import base64,csv,hashlib,importlib,importlib.util,io,json,sys
from pathlib import Path
from importlib.metadata import distribution
from urllib.parse import urlparse,unquote
from urllib.request import url2pathname
selected=json.loads(sys.argv[1]);prefix=Path(sys.prefix).resolve();result={}
assert prefix==Path(sys.argv[2]).resolve()
for item in selected:
 module=item['module'];version=item['version'];expected=item['entries'];wheel=Path(item['wheel']).resolve()
 obj=importlib.import_module(module);origin=Path(obj.__file__).resolve()
 assert origin.is_relative_to(prefix) and 'site-packages' in origin.parts and not origin.is_symlink()
 dist=distribution(module.replace('_','-'));assert dist.version==version
 paths=tuple(dist.files);names={p.as_posix() for p in paths};assert len(names)==len(paths)
 info=module+'-'+version+'.dist-info/'
 record=info+'RECORD';assert record in names
 locate=lambda n:Path(dist.locate_file(n)).resolve()
 rows=list(csv.reader(io.StringIO(locate(record).read_text(encoding='utf-8'))))
 assert len(rows)==len(names) and {r[0] for r in rows}==names
 actual={};generated={}
 for relative,identity,size in rows:
  path=locate(relative);assert path.is_relative_to(prefix) and 'site-packages' in path.parts and path.is_file() and not path.is_symlink()
  raw=path.read_bytes();h=hashlib.sha256(raw).hexdigest();actual[relative]=dict(bytes=len(raw),sha256=h)
  if identity:
   assert identity=='sha256='+base64.urlsafe_b64encode(hashlib.sha256(raw).digest()).rstrip(b'=').decode() and int(size)==len(raw)
  else:assert size=='' and (relative==record or '/__pycache__/' in relative)
  if relative in expected and relative!=record:
   assert actual[relative]==expected[relative],'Installed archive metadata/source/license drift'
  elif relative==record:generated[relative]=dict(kind='installer_record',**actual[relative])
  elif relative==info+'INSTALLER':assert raw==b'pip\n';generated[relative]=dict(kind='installer',**actual[relative])
  elif relative==info+'REQUESTED':assert raw==b'';generated[relative]=dict(kind='explicit_request',**actual[relative])
  elif relative==info+'direct_url.json':
   value=json.loads(raw);assert set(value)=={'url','archive_info'}
   u=urlparse(value['url']);assert u.scheme=='file' and not u.netloc and not u.query and not u.fragment
   assert Path(url2pathname(unquote(u.path))).resolve()==wheel
   archive=value['archive_info'];assert set(archive)<= {'hash','hashes'} and archive
   if 'hash' in archive:assert archive['hash']=='sha256='+item['wheel_sha256']
   if 'hashes' in archive:assert archive['hashes']=={'sha256':item['wheel_sha256']}
   generated[relative]=dict(kind='selected_archive_origin',**actual[relative])
  else:
   assert relative.startswith(module+'/') and '/__pycache__/' in relative and relative.endswith('.cpython-312.pyc')
   parent,leaf=relative.rsplit('/__pycache__/',1);source=parent+'/'+leaf.removesuffix('.cpython-312.pyc')+'.py'
   assert source in expected and raw[:4]==importlib.util.MAGIC_NUMBER
   generated[relative]=dict(kind='cpython312_cache',source=source,**actual[relative])
 assert set(expected)|{info+'INSTALLER',info+'REQUESTED',info+'direct_url.json'}<=names
 on_disk={p.relative_to(origin.parent.parent).as_posix() for p in origin.parent.rglob('*') if p.is_file()}
 on_disk|={p.relative_to(locate(record).parent.parent).as_posix() for p in locate(record).parent.rglob('*') if p.is_file()}
 assert on_disk==names,'Unrecorded installed package/metadata file'
 result[module]=dict(origin=str(origin),prefix=str(prefix),files=actual,generated=generated)
print(json.dumps(result,sort_keys=True))
'''


def installed(py, names, archives, helper, run):
    selected = []
    for name, path in zip(names, archives, strict=True):
        module, version = helper.PACKAGES[name]
        files = helper.contents(path)
        selected.append(dict(module=module, version=version, wheel=str(path.resolve()), wheel_sha256=sha(path.read_bytes()),
            entries={p: dict(bytes=len(raw), sha256=sha(raw)) for p, raw in files.items()}))
    return json.loads(run(py, '-I', '-c', INSTALLED, json.dumps(selected), py.parent.parent))
