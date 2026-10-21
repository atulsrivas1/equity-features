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
import tomllib
import zipfile
from packaging.requirements import Requirement
from packaging.specifiers import SpecifierSet

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist/agent-ledger-corrected'
EPOCH = 1700000000
PACKAGES = {'contracts':('equity_feature_contracts','0.0.4a4'),
            'features':('equity_features','0.0.4a5'), 'evidence':('equity_feature_evidence','0.1.0a2'),
            'agent-evidence':('equity_feature_agent_evidence','0.1.0a1'),
            'agent-ledger':('equity_feature_agent_ledger','0.1.0a1')}


def run(*args, cwd=ROOT, env=None):
    effective=dict(os.environ if env is None else env)
    for name in ('PYTHONPATH','PYTHONHOME','MYPYPATH'):effective.pop(name,None)
    subprocess.run([str(a) for a in args], cwd=cwd, env=effective, check=True)


def sha(data): return hashlib.sha256(data).hexdigest()


def member_audit(items):
    """Validate every physical member, including directories, before filtering."""
    result={};physical={}
    reserved={'con','prn','aux','nul'}|{f'{p}{i}' for p in ('com','lpt') for i in range(1,10)}
    for name,is_directory,size,mode in items:
        assert type(size) is int and size>=0 and type(is_directory) is bool
        assert not is_directory or size==0, 'directory payload'
        assert type(name) is str and name and name.isascii()
        assert not any(ord(c)<32 or ord(c)==127 for c in name)
        assert not name.startswith(('/','\\')) and '\\' not in name and ':' not in name
        plain=name[:-1] if is_directory and name.endswith('/') else name
        parts=plain.split('/')
        assert all(p not in ('','.','..') and not p.endswith(('.',' ')) and p.split('.')[0].lower() not in reserved for p in parts)
        assert not any(p in ('.git','__pycache__','.env') for p in parts)
        assert not name.endswith(('.pyc','.pyo'))
        identity='/'.join(parts).casefold()
        assert name not in result and identity not in physical, 'duplicate physical archive member'
        result[name]={'kind':'directory' if is_directory else 'file','bytes':size,'mode':mode}
        physical[identity]=is_directory
    for name in physical:
        parts=name.split('/')
        for end in range(1,len(parts)):
            parent='/'.join(parts[:end]);assert parent not in physical or physical[parent], 'file ancestor alias'
    return result


def contents(path, *, with_members=False):
    if path.suffix == '.whl':
        with zipfile.ZipFile(path) as archive:
            names = archive.namelist(); assert len(names) == len(set(names))
            infos=archive.infolist()
            assert all(x.orig_filename==x.filename for x in infos), 'normalized physical ZIP name'
            for info in infos:
                kind=(info.external_attr>>16)&0o170000
                assert kind in ((0,0o040000) if info.is_dir() else (0,0o100000)), 'ZIP name/mode contradiction or special entry'
                if info.is_dir():
                    assert info.file_size==0 and info.CRC==0, 'directory payload/CRC'
                    assert archive.read(info)==b'', 'directory compressed payload'
            members=member_audit((x.orig_filename,x.is_dir(),x.file_size,x.external_attr>>16) for x in infos)
            files = {name:archive.read(name) for name in names if not name.endswith('/')}
    else:
        with tarfile.open(path, 'r:gz') as archive:
            infos = archive.getmembers(); assert len(infos) == len({m.name for m in infos})
            assert all(m.isfile() or m.isdir() for m in infos)
            members=member_audit((x.name,x.isdir(),x.size,x.mode) for x in infos)
            files = {m.name:archive.extractfile(m).read() for m in infos if m.isfile()}
    return (files,members) if with_members else files


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
    module,version = PACKAGES[name]; files,members = contents(path,with_members=True); wheel=path.suffix=='.whl'
    prefix='' if wheel else path.name.removesuffix('.tar.gz')+'/'
    metadata_name=next(n for n in files if (n.endswith('/METADATA') if wheel else n==prefix+'PKG-INFO'))
    metadata=BytesParser().parsebytes(files[metadata_name])
    project=tomllib.loads((source/'pyproject.toml').read_text(encoding='utf-8'))['project']
    assert project['name']==module.replace('_','-') and project['version']==version
    assert metadata['Name']==module.replace('_','-') and metadata['Version']==version
    assert metadata['License-Expression']=='Apache-2.0' and metadata['Requires-Python']=='<3.13,>=3.12'
    assert metadata['Summary']==project['description']
    assert str(SpecifierSet(metadata['Requires-Python']))==str(SpecifierSet(project['requires-python']))
    assert project['license']=='Apache-2.0' and metadata.get_all('License-File',[])==project['license-files']==['LICENSE']
    assert all(set(author)=={'name'} for author in project['authors'])
    assert metadata['Author']==', '.join(author['name'] for author in project['authors'])
    assert sorted(metadata.get_all('Project-URL',[]))==sorted(k+', '+v for k,v in project['urls'].items())
    assert metadata.get_all('Classifier',[])==project.get('classifiers',[])
    extras=project.get('optional-dependencies',{})
    assert sorted(metadata.get_all('Provides-Extra',[]))==sorted(extras)
    requires=list(project['dependencies'])
    for extra,values in extras.items():
        for requirement in values:
            assert ';' not in requirement, 'unselected optional marker composition'
            requires.append(requirement+'; extra == "'+extra+'"')
    assert sorted(str(Requirement(v)) for v in metadata.get_all('Requires-Dist',[]))==sorted(str(Requirement(v)) for v in requires)
    assert project['readme']=='README.md' and metadata['Description-Content-Type']=='text/markdown'
    readme=(source/'README.md').read_bytes()
    body=metadata.get_payload(decode=True)
    assert type(body) is bytes and body.replace(b'\r\n',b'\n')==readme.replace(b'\r\n',b'\n'), 'metadata README drift'
    if name=='evidence': assert metadata.get_all('Requires-Dist',[])==['equity-feature-contracts==0.0.4a4']
    if name=='agent-evidence': assert metadata.get_all('Requires-Dist',[])==['equity-feature-contracts==0.0.4a4','equity-feature-evidence==0.1.0a2']
    package_prefix=module+'/' if wheel else prefix+'src/'+module+'/'
    expected={p.relative_to(source/'src').as_posix():p.read_bytes() for p in (source/'src'/module).rglob('*') if p.is_file()}
    actual={module+'/'+n.removeprefix(package_prefix):body for n,body in files.items() if n.startswith(package_prefix)}
    assert actual==expected and module+'/py.typed' in actual
    license_name=next(n for n in files if n.endswith('/licenses/LICENSE')) if wheel else prefix+'LICENSE'
    assert files[license_name]==(source/'LICENSE').read_bytes()
    if wheel:
        dist_info=module+'-'+version+'.dist-info/'
        assert set(files)==set(expected)|{dist_info+n for n in ('METADATA','WHEEL','top_level.txt','licenses/LICENSE','RECORD')}
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
        assert files[prefix+'README.md']==readme, 'sdist README drift'
    return {'sha256':sha(path.read_bytes()),'bytes':path.stat().st_size,'version':version,
            'entries':{n:{'sha256':sha(b),'bytes':len(b)} for n,b in sorted(files.items())},
            'members':members,'source_map':{n:sha(b) for n,b in sorted(expected.items())},
            'metadata_source_readme_verified':True,'record_verified':wheel}


def installed_map(py, names):
    script='''import base64,csv,hashlib,importlib,io,json,sys
from pathlib import Path
from importlib.metadata import distribution
result={}
for name in sys.argv[1:]:
    module=importlib.import_module(name); root=Path(module.__file__).resolve().parent
    assert 'site-packages' in root.parts
    dist=distribution(name.replace('_','-'));files=tuple(dist.files)
    record=next(p for p in files if p.name=='RECORD' and '.dist-info' in p.as_posix())
    record_path=Path(dist.locate_file(record)).resolve();assert 'site-packages' in record_path.parts
    rows=list(csv.reader(io.StringIO(record_path.read_text(encoding='utf-8'))))
    assert len(rows)==len({row[0] for row in rows})
    assert {row[0] for row in rows}=={p.as_posix() for p in files}
    for relative,digest,size in rows:
        path=Path(dist.locate_file(relative)).resolve();assert 'site-packages' in path.parts
        assert path.is_file()
        if '__pycache__' in path.parts:continue
        data=path.read_bytes()
        if digest:
            assert digest=='sha256='+base64.urlsafe_b64encode(hashlib.sha256(data).digest()).rstrip(b'=').decode()
            assert int(size)==len(data)
        else:assert relative==record.as_posix() and size==''
        result[relative]=hashlib.sha256(data).hexdigest()
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


def run_suite(py, path, form, combined, label):
    script="""import json,sys,unittest
suite=unittest.defaultTestLoader.discover(sys.argv[1])
result=unittest.TextTestRunner(verbosity=1).run(suite)
record={'methods':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped)}
print(json.dumps(record,sort_keys=True))
raise SystemExit(not result.wasSuccessful() or bool(result.skipped))
"""
    result=subprocess.run([str(py),'-I','-c',script,str(path)],cwd=py.parent,text=True,encoding='utf-8',capture_output=True)
    log=OUT/(form+('-producer-' if combined else '-declarations-')+label+'.log')
    assert not log.exists();log.write_text(result.stdout+'\n'+result.stderr,encoding='utf-8')
    if result.returncode:
        # Preserve the complete local raw log; expose a bounded failure tail in CI.
        print('FAILED installed cohort '+log.name+' SHA256 '+sha(log.read_bytes()),flush=True)
        print(log.read_text(encoding='utf-8')[-32768:],flush=True)
    assert result.returncode==0, 'installed test failure; retained log '+log.name
    record=json.loads(result.stdout.splitlines()[-1])
    assert record['methods']=={'declarations':26,'ledger':34,'crash':4,'producer':1,'accepted-evidence':31,'archive-controls':8}[label]
    assert record['failures']==record['errors']==record['skipped']==0
    return {**record,'log':log.name,'log_sha256':sha(log.read_bytes())}


def main():
    OUT.mkdir(parents=True,exist_ok=True);assert not list(OUT.iterdir()), 'fresh dist/agent-ledger-corrected required'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,encoding='utf-8').strip()
    scopes=['packages/'+p for p in PACKAGES]+[
        'tests/agent_evidence','tests/agent_ledger','tests/agent_ledger_crash','tests/agent_ledger_producer','tests/agent_ledger_qualification','tests/evidence',
        'examples/agent_ledger.py','examples/agent_ledger_producer.py','examples/agent_ledger_typed.py',
        'examples/agent_event_producer.py','examples/evidence_content.py','examples/agent_events.py',
        'docs/stories/EQ-106_EVENT_ORACLE.json','docs/stories/EQ-106_KIND_CASES.json','docs/stories/EQ-106_REFUSAL_CASES.json','docs/stories/EQ-106_OPERATION_CONTROLS.json',
        'docs/stories/EQ-107_PROFILE.json','docs/stories/EQ-107_ORACLE.json','docs/stories/EQ-107_CASES.json','docs/stories/EQ-107_PAGES.json','docs/stories/EQ-107_BOUNDARIES.json','docs/stories/EQ-107_ACCEPTED_ARCHIVES.json','docs/stories/EQ-107_CRASH_PROPOSAL.json',
        'docs/stories/EQ-097_CONFIG_ORACLE.json','docs/stories/EQ-097_RESULT_ORACLE.json','docs/stories/EQ-097_BATCH_ORACLE.json','docs/stories/EQ-096_RECEIPT_ORACLE.json',
        'tools/build_agent_ledger.py','tools/qualification','tools/check_boundary.py','.github/workflows/agent-ledger.yml','requirements-dev.txt']
    paths=tuple(subprocess.check_output(['git','ls-files','--',*scopes],cwd=ROOT,encoding='utf-8').splitlines());assert paths
    snapshot={};materialized={};source_map={}
    for name in paths:
        data=subprocess.check_output(['git','show',head+':'+name],cwd=ROOT);live=(ROOT/name).read_bytes()
        assert live==data or live.replace(b'\r\n',b'\n')==data, 'uncommitted build input'
        snapshot[name]=data;materialized[name]=live;source_map[name]={'git_sha256':sha(data),'materialized_sha256':sha(live),'built_from':'committed-Git-bytes'}
    def closure():
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,encoding='utf-8').strip()==head
        assert tuple(subprocess.check_output(['git','ls-files','--',*scopes],cwd=ROOT,encoding='utf-8').splitlines())==paths
        assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',*scopes],cwd=ROOT)
        assert all((ROOT/n).read_bytes()==b for n,b in materialized.items())
    report={'schema':'agent-ledger-qualification:1','source_commit':head,'system':platform.system(),'python':platform.python_version(),
            'source':source_map,'artifacts':{},'installed':[],'status':'running','epoch':EPOCH}
    def save():(OUT/'qualification.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    closure();save();work=(ROOT/'work').resolve();work.mkdir(exist_ok=True)
    # Explicit ownership instead of automatic exceptional cleanup: failed runs retain source/evidence.
    owned=Path(tempfile.mkdtemp(prefix='agent-ledger-',dir=work)).resolve()
    assert owned.parent==work and owned.name.startswith('agent-ledger-') and not owned.is_symlink()
    verification=owned/'verification'
    for name,data in snapshot.items():
        target=verification/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
    report['archive_controls']=run_suite(Path(sys.executable),verification/'tests/agent_ledger_qualification','source',False,'archive-controls');save()
    env=dict(os.environ,SOURCE_DATE_EPOCH=str(EPOCH),PYTHONHASHSEED='0')
    for repeat in (0,1):
        dest=owned/f'build-{repeat}';dest.mkdir()
        for name,(module,version) in PACKAGES.items():
            source=owned/f'source-{repeat}-{name}';prefix='packages/'+name+'/'
            for relative,data in snapshot.items():
                if relative.startswith(prefix):
                    target=source/relative.removeprefix(prefix);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(data)
            run(sys.executable,'-m','build','--no-isolation','--outdir',dest,source,env=env)
            artifacts=list(dest.glob(module+'-*'));assert len(artifacts)==2
            for path in artifacts:
                if path.suffix!='.whl':contents(path);normalize(path)
                inspection=inspect(path,name,source)
                if repeat==0:report['artifacts'][path.name]=inspection;shutil.copyfile(path,OUT/path.name)
                else:assert inspection==report['artifacts'][path.name], 'repeat archive differs'
    assert len(report['artifacts'])==10;report['repeat_archive_parity']=True
    baseline=json.loads(snapshot['docs/stories/EQ-107_ACCEPTED_ARCHIVES.json']);expected=baseline['systems'][platform.system()]['archives'];assert len(expected)==8
    for name,item in expected.items():
        assert report['artifacts'][name]['sha256']==item['sha256'] and report['artifacts'][name]['bytes']==item['bytes'], 'accepted archive drift'
    report['accepted_eight_archive_parity']={'head':baseline['head'],'archives':expected};save()
    for form,suffix in [('wheel','.whl'),('sdist','.tar.gz')]:
        archives={n:next(OUT.glob(module+'-*'+suffix)) for n,(module,_) in PACKAGES.items()}
        for combined in (False,True):
            selected=[archives[n] for n in ('contracts','evidence','agent-evidence')]+([archives['features']] if combined else [])
            py=install(selected,owned/(form+('-combined' if combined else '-isolated')))
            modules=[PACKAGES[n][0] for n in ('contracts','evidence','agent-evidence','features') if n!='features' or combined]
            before=installed_map(py,modules);verify_installed(before,selected)
            run(py,'-m','pip','install','--no-index','--no-deps','--no-build-isolation',archives['agent-ledger']);run(py,'-m','pip','check')
            names=[*modules,'equity_feature_agent_ledger']
            after=installed_map(py,names);verify_installed(after,[*selected,archives['agent-ledger']]);assert all(after[n]==d for n,d in before.items())
            if not combined:
                run(py,'-I','-c',"import importlib.util; assert all(importlib.util.find_spec(n) is None for n in ('equity_features','equity_feature_io_contracts','equity_feature_io_sdk','equity_feature_workers','equity_feature_service','equity_feature_mcp','equity_feature_diagnostics','equity_feature_provenance','equity_feature_conformance','equity_feature_strategies','equity_feature_labels','numpy','pyarrow'))",cwd=py.parent)
            methods={label:run_suite(py,verification/'tests'/directory,form,combined,label) for label,directory in [('ledger','agent_ledger'),('crash','agent_ledger_crash'),('declarations','agent_evidence')]}
            run(py,'-I',verification/'examples/agent_ledger.py',cwd=py.parent)
            if combined:
                methods['producer']=run_suite(py,verification/'tests/agent_ledger_producer',form,combined,'producer')
                methods['accepted_evidence']=run_suite(py,verification/'tests/evidence',form,combined,'accepted-evidence')
                run(py,'-I',verification/'examples/agent_ledger_producer.py',cwd=py.parent)
            assert after==installed_map(py,names)
            run(sys.executable,'-m','mypy','--strict','--no-incremental','--python-executable',py,verification/'examples/agent_ledger_typed.py',cwd=py.parent)
            runtime_script="""import sqlite3,sys,json
import equity_feature_agent_ledger as l
store=l.Ledger.create(sys.argv[1],'probe:runtime')
try:
    pragmas={name:store._conn.execute('PRAGMA '+name).fetchone()[0] for name in ('journal_mode','synchronous','foreign_keys','trusted_schema','busy_timeout','application_id','user_version')}
    assert pragmas=={'journal_mode':'delete','synchronous':2,'foreign_keys':1,'trusted_schema':0,'busy_timeout':0,'application_id':1161907249,'user_version':1}
    print(json.dumps({'python':sys.version,'sqlite':sqlite3.sqlite_version,'threadsafety':sqlite3.threadsafety,'pragmas':pragmas}))
finally:store.close()
"""
            runtime=json.loads(subprocess.check_output([str(py),'-I','-c',runtime_script,str(owned/(form+('-combined' if combined else '-isolated')+'-runtime.sqlite'))],cwd=py.parent,text=True,encoding='utf-8'))
            report['installed'].append({'form':form,'combined_actual_core_producer':combined,'optional_independence':not combined,'installed_map':after,'runtime':runtime,
                 'installed_record_rows_verified':True,'methods':methods,'unchanged_original_packages':True,'tests_passed':True,'typing_passed':True});save()
    closure()
    assert owned.parent==work and owned.name.startswith('agent-ledger-') and not owned.is_symlink()
    shutil.rmtree(owned);assert not owned.exists()
    closure()
    report['owned_temporary_cleanup_completed']=True;report['source_head_and_materialization_closure']=True;report['status']='completed';save()

if __name__=='__main__':main()
