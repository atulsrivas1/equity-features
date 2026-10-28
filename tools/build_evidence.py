"""Closed Git-source repeat builds and fresh installed receipt consumers on either OS."""
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

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist/evidence'
EPOCH = 1700000000
PACKAGES = {'contracts':('equity_feature_contracts',CONTRACTS),
            'features':('equity_features',FEATURES), 'evidence':('equity_feature_evidence',VERSIONS['evidence'])}


def run(*args, cwd=ROOT, env=None):
    subprocess.run([str(a) for a in args], cwd=cwd, env=env, check=True)


def sha(data): return hashlib.sha256(data).hexdigest()


def contents(path):
    if path.suffix == '.whl':
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist(); assert len(names) == len(set(names))
            files = {name:archive.read(name) for name in names if not name.endswith('/')}
    else:
        with tarfile.open(path, 'r:gz') as archive:
            members = archive.getmembers(); assert len(members) == len({m.name for m in members})
            assert all(m.isfile() or m.isdir() for m in members)
            files = {m.name:archive.extractfile(m).read() for m in members if m.isfile()}
    for name in files:
        assert not name.startswith(('/', '\\')) and '\\' not in name and '..' not in PurePosixPath(name).parts
        assert not any(p in ('.git','__pycache__','.env') for p in PurePosixPath(name).parts)
        assert not name.endswith(('.pyc','.pyo'))
    return files


def normalize(path):
    raw = io.BytesIO()
    with tarfile.open(path, 'r:gz') as source, tarfile.open(fileobj=raw, mode='w', format=tarfile.PAX_FORMAT) as target:
        for member in sorted(source.getmembers(), key=lambda m:m.name):
            member.mtime=EPOCH; member.uid=member.gid=0; member.uname=member.gname=''; member.pax_headers={}
            member.mode=0o755 if member.isdir() else 0o644
            target.addfile(member, source.extractfile(member) if member.isfile() else None)
    with path.open('wb') as output, gzip.GzipFile(fileobj=output, mode='wb', filename='', mtime=EPOCH) as zipped:
        zipped.write(raw.getvalue())


def inspect(path, name, source):
    module,version = PACKAGES[name]; files = contents(path); wheel=path.suffix=='.whl'
    prefix='' if wheel else path.name.removesuffix('.tar.gz')+'/'
    metadata_name=next(n for n in files if (n.endswith('/METADATA') if wheel else n==prefix+'PKG-INFO'))
    metadata=BytesParser().parsebytes(files[metadata_name])
    assert metadata['Name']==module.replace('_','-') and metadata['Version']==version
    assert metadata['License-Expression']=='Apache-2.0' and metadata['Requires-Python']=='<3.13,>=3.12'
    if name=='evidence': assert metadata.get_all('Requires-Dist',[])==[f'equity-feature-contracts=={CONTRACTS}']
    package_prefix=module+'/' if wheel else prefix+'src/'+module+'/'
    expected={p.relative_to(source/'src').as_posix():p.read_bytes() for p in (source/'src'/module).rglob('*') if p.is_file()}
    actual={module+'/'+n.removeprefix(package_prefix):body for n,body in files.items() if n.startswith(package_prefix)}
    assert actual==expected and module+'/py.typed' in actual
    license_name=next(n for n in files if n.endswith('/licenses/LICENSE')) if wheel else prefix+'LICENSE'
    assert files[license_name]==(source/'LICENSE').read_bytes()
    if wheel:
        assert all(n.startswith((module+'/',module+'-')) for n in files)
        record=next(n for n in files if n.endswith('/RECORD'))
        rows=list(csv.reader(io.StringIO(files[record].decode('utf-8'))))
        assert len(rows)==len(files) and {r[0] for r in rows}==set(files)
        for relative,digest,size in rows:
            if relative==record: assert digest==size==''
            else:
                assert digest=='sha256='+base64.urlsafe_b64encode(hashlib.sha256(files[relative]).digest()).rstrip(b'=').decode()
                assert int(size)==len(files[relative])
    else:
        allowed={prefix+n for n in ('LICENSE','README.md','pyproject.toml','PKG-INFO','setup.cfg')}
        assert all(n in allowed or n.startswith((prefix+'src/'+module+'/',prefix+'src/'+module+'.egg-info/')) for n in files)
        assert files[prefix+'pyproject.toml']==(source/'pyproject.toml').read_bytes()
    return {'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size,'version':version,
            'entries':{n:{'sha256':sha(b),'bytes':len(b)} for n,b in sorted(files.items())},
            'source_map':{n:sha(b) for n,b in sorted(expected.items())},'record_verified':wheel}


def installed_map(py, names):
    script='''import hashlib,importlib,json,sys
from pathlib import Path
from importlib.metadata import distribution
result={}
for name in sys.argv[1:]:
    module=importlib.import_module(name); root=Path(module.__file__).resolve().parent
    assert 'site-packages' in root.parts
    for relative in distribution(name.replace('_','-')).files:
        path=Path(distribution(name.replace('_','-')).locate_file(relative)).resolve()
        if path.is_file() and '__pycache__' not in path.parts:
            assert 'site-packages' in path.parts
            result[relative.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
print(json.dumps(result,sort_keys=True))
'''
    return json.loads(subprocess.check_output([str(py),'-I','-c',script,*names],cwd=py.parent,encoding='utf-8'))


def verify_installed(mapping, paths):
    expected={}
    for path in paths:
        module=path.name.split('-')[0]
        files=contents(path)
        prefix=module+'/' if path.suffix=='.whl' else path.name.removesuffix('.tar.gz')+'/src/'+module+'/'
        expected.update({module+'/'+n.removeprefix(prefix):sha(b) for n,b in files.items() if n.startswith(prefix)})
    modules=tuple(module for module,version in PACKAGES.values())
    actual={n:digest for n,digest in mapping.items() if any(n.startswith(module+'/') for module in modules)}
    assert actual==expected, 'installed source/archive complete payload differs'


def install(paths, directory):
    run(sys.executable,'-m','venv',directory)
    py=directory/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
    if paths[0].suffix!='.whl': run(py,'-m','pip','install','--no-deps','setuptools==80.9.0')
    run(py,'-m','pip','install','--no-index','--no-deps','--no-build-isolation',*paths)
    run(py,'-m','pip','check')
    return py


def main():
    OUT.mkdir(parents=True,exist_ok=True); assert not list(OUT.iterdir()), 'fresh dist/evidence required; preserve old qualification'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,encoding='utf-8').strip()
    scopes=['packages/'+p for p in PACKAGES]+['tests/evidence','examples/evidence_receipt.py','examples/evidence_content.py','examples/evidence_content_cost.py',
        'docs/stories/EQ-097_CONFIG_ORACLE.json','docs/stories/EQ-097_RESULT_ORACLE.json','docs/stories/EQ-097_BATCH_ORACLE.json',
        'docs/stories/EQ-096_RECEIPT_ORACLE.json','tools/build_evidence.py','tools/check_boundary.py','tools/_versions.py',
        '.github/workflows/evidence.yml','requirements-dev.txt']
    paths=tuple(subprocess.check_output(['git','ls-files','--',*scopes],cwd=ROOT,encoding='utf-8').splitlines())
    assert paths
    snapshot={}; materialized={}; source_map={}
    for name in paths:
        data=subprocess.check_output(['git','show',head+':'+name],cwd=ROOT); live=(ROOT/name).read_bytes()
        assert live==data or live.replace(b'\r\n',b'\n')==data, 'uncommitted build input'
        snapshot[name]=data; materialized[name]=live
        source_map[name]={'git_sha256':sha(data),'materialized_sha256':sha(live),'built_from':'committed-Git-bytes'}
    def closure():
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,encoding='utf-8').strip()==head
        assert tuple(subprocess.check_output(['git','ls-files','--',*scopes],cwd=ROOT,encoding='utf-8').splitlines())==paths
        assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',*scopes],cwd=ROOT)
        assert all((ROOT/n).read_bytes()==b for n,b in materialized.items())
    report={'schema':'evidence-qualification:1','source_commit':head,'system':platform.system(),'python':platform.python_version(),
            'source':source_map,'artifacts':{},'installed':[],'status':'running','epoch':EPOCH}
    def save():(OUT/'qualification.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    closure(); save(); work=ROOT/'work'; work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='evidence-',dir=work) as owned:
        owned=Path(owned).resolve(); assert owned.is_relative_to(work.resolve())
        verification=owned/'verification'
        for name,data in snapshot.items():
            target=verification/name; target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
        env=dict(os.environ,SOURCE_DATE_EPOCH=str(EPOCH),PYTHONHASHSEED='0')
        for repeat in (0,1):
            dest=owned/f'build-{repeat}'; dest.mkdir()
            for name,(module,version) in PACKAGES.items():
                source=owned/f'source-{repeat}-{name}'; prefix='packages/'+name+'/'
                for relative,data in snapshot.items():
                    if relative.startswith(prefix):
                        target=source/relative.removeprefix(prefix); target.parent.mkdir(parents=True,exist_ok=True); target.write_bytes(data)
                run(sys.executable,'-m','build','--no-isolation','--outdir',dest,source,env=env)
                artifacts=list(dest.glob(module+'-*')); assert len(artifacts)==2
                for path in artifacts:
                    if path.suffix!='.whl': normalize(path)
                    inspection=inspect(path,name,source)
                    if repeat==0:
                        report['artifacts'][path.name]=inspection; shutil.copyfile(path,OUT/path.name)
                    else: assert inspection==report['artifacts'][path.name], 'repeat archive differs'
        assert len(report['artifacts'])==6; report['repeat_archive_parity']=True; save()
        for form,suffix in [('wheel','.whl'),('sdist','.tar.gz')]:
            archives={n:next(OUT.glob(module+'-*'+suffix)) for n,(module,_) in PACKAGES.items()}
            for combined in (False,True):
                selected=[archives['contracts']]+([archives['features']] if combined else [])
                py=install(selected,owned/(form+('-combined' if combined else '-isolated')))
                modules=[PACKAGES[n][0] for n in ('contracts','features') if n in ('contracts',) or combined]
                before=installed_map(py,modules); verify_installed(before,selected)
                run(py,'-m','pip','install','--no-index','--no-deps','--no-build-isolation',archives['evidence'])
                run(py,'-m','pip','check')
                after=installed_map(py,[*modules,'equity_feature_evidence']); verify_installed(after,[*selected,archives['evidence']])
                assert all(after[n]==digest for n,digest in before.items())
                if not combined:
                    run(py,'-I','-c',"import importlib.util; assert all(importlib.util.find_spec(n) is None for n in ('equity_features','equity_feature_io_contracts','equity_feature_workers','equity_feature_strategies','equity_feature_labels'))",cwd=py.parent)
                run(py,'-I','-m','unittest','discover','-s',verification/'tests/evidence',cwd=py.parent)
                if combined:
                    run(py,'-I',verification/'examples/evidence_receipt.py',cwd=py.parent)
                    run(py,'-I',verification/'examples/evidence_content.py',cwd=py.parent)
                    if form == 'wheel':
                        cost=json.loads(subprocess.check_output([str(py),'-I',str(verification/'examples/evidence_content_cost.py')],cwd=py.parent,encoding='utf-8'))
                        assert len(cost['samples'])==24 and all(x['parity'] for x in cost['samples'])
                        report['content_cost']=cost; save()
                assert after==installed_map(py,[*modules,'equity_feature_evidence'])
                typing=py.parent/'evidence_typed_consumer.py'
                typing.write_text('from equity_feature_evidence import ExecutionClaim, ExecutionReceipt, decode_receipt, fingerprint_config, content_chunks\nfrom equity_feature_contracts import ConfigSpec\ndef typed(config: ConfigSpec) -> int:\n    return fingerprint_config(config).byte_length + sum(len(c) for c in content_chunks(config))\nclaim: ExecutionClaim = ExecutionClaim()\nreceipt: ExecutionReceipt = decode_receipt(b"{}")\n',encoding='utf-8')
                run(sys.executable,'-m','mypy','--strict','--python-executable',py,typing,cwd=py.parent)
                report['installed'].append({'form':form,'combined_actual_core_producer':combined,'optional_independence':not combined,
                    'installed_map':after,'unchanged_original_packages':True,'tests_passed':True,'typing_passed':True}); save()
    closure(); report['source_head_and_materialization_closure']=True; report['status']='completed'; save()


if __name__=='__main__': main()
