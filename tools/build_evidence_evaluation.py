"""Fresh EQ117 wheel-compute qualification, optionally followed by one fixed study.

Reuses accepted archive verification functions, not EQ116 study observations.
Every output/work directory is new. Failed outputs are retained.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import shutil
import stat
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT/'dist/evidence-evaluation'
IO = ROOT/'.eq117-inputs/io'
IO_HEAD = '18d86761aa3eebb7414e51e8fa2aba089717b5eb'
PACKAGES = {
 'contracts':('equity_feature_contracts','0.0.4a4'), 'features':('equity_features','0.0.4a5'),
 'evidence':('equity_feature_evidence','0.1.0a2'), 'explanations':('equity_feature_explanations','0.1.0a2'),
 'diagnostics':('equity_feature_diagnostics','0.1.0a1'), 'agent-evidence':('equity_feature_agent_evidence','0.1.0a1'),
 'agent-ledger':('equity_feature_agent_ledger','0.1.0a1'), 'bundles':('equity_feature_bundles','0.1.0a1')}
HELPERS = tuple('examples/evidence_evaluation_'+name+'.py' for name in
                ('observer','producer','instrumentation','worker','scoring'))
HARNESS = HELPERS+('examples/evidence_pilot.py','examples/agent_research.py',
 'docs/stories/EQ116_ORACLES.json','tools/run_evidence_evaluation.py')
CONTROL = ('tools/build_evidence_evaluation.py','tools/build_agent_ledger.py',
 'tools/evidence_pilot_archives.py','tests/evidence_evaluation/test_evaluation.py',
 'docs/stories/EQ116_INPUTS.json','docs/stories/EQ117_EVALUATION_PROPOSAL.json',
 'docs/stories/EQ117_OWNER_DECISION.json','docs/stories/EQ117_MEASUREMENT_PROTOCOL.md',
 '.github/workflows/evidence-evaluation.yml','requirements-dev.txt',
 'docs/ef1/EVIDENCE_EVALUATION_SOURCE_EVOLUTION.json')

def sha(raw):return hashlib.sha256(raw).hexdigest()
def encoded(value):return (json.dumps(value,sort_keys=True,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
def git(root,*args):return subprocess.check_output(['git',*args],cwd=root)
def tree(root,head):
    result={}
    for entry in git(root,'ls-tree','-rz',head).split(b'\0'):
        if not entry:continue
        fields,name=entry.split(b'\t',1);mode,kind,oid=fields.decode().split()
        assert kind=='blob' and mode in ('100644','100755')
        result[name.decode('utf-8')]=dict(mode=mode,git_blob=oid)
    return result
def module(name,path):
    spec=importlib.util.spec_from_file_location(name,path)
    value=importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value)
    return value

def main():
    assert len(sys.argv) in (2,3) and sys.argv[1] in ('qualify','study')
    study=sys.argv[1]=='study'
    assert len(sys.argv)==(3 if study else 2)
    assert sys.version_info[:2]==(3,12) and platform.system() in ('Windows','Linux')
    assert platform.machine().lower() in ('amd64','x86_64') and not OUT.exists()
    if study:
        assert os.environ.get('GITHUB_RUN_ATTEMPT','1')=='1'
        assert 0<len(sys.argv[2])<=128 and all(c.isascii() and (c.isalnum() or c in '-_.') for c in sys.argv[2])
    head=git(ROOT,'rev-parse','HEAD').decode().strip()
    assert git(IO,'rev-parse','HEAD').decode().strip()==IO_HEAD
    whole,io_whole=tree(ROOT,head),tree(IO,IO_HEAD)
    selected={p:git(ROOT,'show',head+':'+p) for p in whole if p in HARNESS+CONTROL or
              any(p.startswith('packages/'+n+'/') for n in PACKAGES if n!='bundles')}
    assert set(HARNESS+CONTROL)<=set(selected)
    io_source={p:git(IO,'show',IO_HEAD+':'+p) for p in io_whole if p.startswith('packages/bundles/')}
    pin_bytes=selected['docs/stories/EQ116_INPUTS.json']
    assert len(pin_bytes)==19347 and sha(pin_bytes)=='5da427709f7b28da6c79156fe3d1bc91254b0511417317cbe1d50b500fb4fe5a'
    pins=json.loads(pin_bytes)
    assert set(io_source)==set(pins['io'])
    historical={p:d for p,d in pins['canonical'].items() if p.startswith('packages/') or
                p in ('examples/agent_research.py','tools/build_agent_ledger.py')}
    governed={p for p in selected if p.startswith('packages/') or
              p in ('examples/agent_research.py','tools/build_agent_ledger.py')}
    source_evolution=None
    if study:
        # Historical owner acceptance does not authorize a study of this new cohort.
        assert governed==set(historical)
        for p,d in historical.items():
            assert len(selected[p])==d['bytes'] and sha(selected[p])==d['sha256']
    else:
        evolution_bytes=selected['docs/ef1/EVIDENCE_EVALUATION_SOURCE_EVOLUTION.json']
        assert len(evolution_bytes)==3404 and sha(evolution_bytes)=='05831d44907d2d544d04faa0cb4f99bc441f4d985e95ee664dafe612d142b0e9'
        source_evolution=json.loads(evolution_bytes)
        assert source_evolution['schema']=='ef1.eq117.qualification-source-evolution:1'
        assert source_evolution['historical_pin_receipt']==dict(bytes=len(pin_bytes),sha256=sha(pin_bytes))
        modified,added=source_evolution['modified'],source_evolution['added']
        assert len(modified)==7 and len(added)==4
        assert set(modified)<=set(historical) and not set(added)&set(historical)
        assert governed==set(historical)|set(added), 'undeclared package source addition/deletion'
        for p,d in historical.items():
            current=d
            if p in modified:
                assert modified[p]['historical']==d
                current=modified[p]['current']
            assert len(selected[p])==current['bytes'] and sha(selected[p])==current['sha256'], 'undeclared source drift: '+p
        for p,d in added.items():
            assert len(selected[p])==d['bytes'] and sha(selected[p])==d['sha256']
    for p,d in pins['io'].items():assert len(io_source[p])==d['bytes'] and sha(io_source[p])==d['sha256']
    assert sha(selected['docs/stories/EQ117_EVALUATION_PROPOSAL.json'])=='7405067b0360126a462bb7a66b5a89416cf93399843b0933b358760804e45073'
    assert json.loads(selected['docs/stories/EQ117_OWNER_DECISION.json'])['accepted'] is True
    materialized={p:(ROOT/p).read_bytes() for p in selected}
    assert all(materialized[p].replace(b'\r\n',b'\n')==raw for p,raw in selected.items())
    assert not git(ROOT,'status','--porcelain','--untracked-files=all','--',*selected)
    OUT.mkdir(parents=True)
    work=ROOT/'work';work.mkdir(exist_ok=True)
    owned=Path(tempfile.mkdtemp(prefix='eq117-',dir=work)).resolve()
    verification=owned/'verification';verification.mkdir()
    for p,raw in selected.items():
        path=verification/p;path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(raw)
    helper=module('_eq117_archives',verification/'tools/build_agent_ledger.py');helper.PACKAGES=PACKAGES
    audit=module('_eq117_archive_audit',verification/'tools/evidence_pilot_archives.py')
    logs=[]
    def run(*args,cwd=owned,env=None):
        index='%03d'%(len(logs)+1)
        effective=dict(os.environ if env is None else env)
        for key in ('PYTHONPATH','PYTHONHOME','MYPYPATH'):effective.pop(key,None)
        stdout,stderr=OUT/(index+'.stdout'),OUT/(index+'.stderr')
        with stdout.open('xb') as out,stderr.open('xb') as err:
            result=subprocess.run([str(x) for x in args],cwd=cwd,env=effective,stdout=out,stderr=err)
        logs.append(dict(id=index,returncode=result.returncode,stdout_sha256=sha(stdout.read_bytes()),stderr_sha256=sha(stderr.read_bytes())))
        assert result.returncode==0,'Retained failed command '+index
        return stdout.read_bytes()
    helper.run=run
    report=dict(schema='eq117.qualification.v1',status='running',source_commit=head,io_head=IO_HEAD,
        system=platform.system(),python=platform.python_version(),machine=platform.machine(),
        whole_git_tree=whole,whole_io_git_tree=io_whole,
        effective_source={p:dict(bytes=len(raw),sha256=sha(raw)) for p,raw in selected.items()},
        io_source=pins['io'],archives={},logs=logs,study_requested=study,
        source_evolution=source_evolution,historical_study_source_parity=source_evolution is None)
    def save():(OUT/'qualification.json').write_bytes(encoded(report))
    def closure():
        assert git(ROOT,'rev-parse','HEAD').decode().strip()==head and tree(ROOT,head)==whole
        assert git(IO,'rev-parse','HEAD').decode().strip()==IO_HEAD and tree(IO,IO_HEAD)==io_whole
        assert all((ROOT/p).read_bytes()==raw for p,raw in materialized.items())
        assert not git(ROOT,'status','--porcelain','--untracked-files=all','--',*selected)
    save()
    try:
        build_env=dict(os.environ,SOURCE_DATE_EPOCH='1700000000',PYTHONHASHSEED='0')
        for repeat in (0,1):
            dest=owned/('archives-'+str(repeat));dest.mkdir()
            for name,(mod,version) in PACKAGES.items():
                source=owned/('source-%d-%s'%(repeat,name));source.mkdir()
                prefix='packages/'+name+'/'
                for p,raw in (io_source if name=='bundles' else selected).items():
                    if p.startswith(prefix):
                        target=source/p.removeprefix(prefix);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
                run(sys.executable,'-m','build','--no-isolation','--outdir',dest,source,env=build_env)
                archives=list(dest.glob(mod+'-*'));assert len(archives)==2
                for path in archives:
                    if path.suffix!='.whl':helper.contents(path);helper.normalize(path)
                    proof=audit.inspect(path,name,source,helper)
                    if repeat==0:
                        report['archives'][path.name]=proof;shutil.copyfile(path,OUT/path.name)
                    else:assert proof==report['archives'][path.name]
                save()
        assert len(report['archives'])==16
        report['repeat_archive_parity']=True
        for name,(mod,version) in PACKAGES.items():
            archive=next(OUT.glob(mod+'-*.tar.gz'));members=helper.contents(archive)
            prefix=archive.name.removesuffix('.tar.gz')+'/'
            source=owned/('selected-sdist-'+name);source.mkdir()
            for p,raw in members.items():
                assert p.startswith(prefix)
                target=source/p.removeprefix(prefix);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(raw)
            before=audit.file_map(source);dest=owned/('rebuilt-'+name);dest.mkdir()
            run(sys.executable,'-m','build','--wheel','--no-isolation','--outdir',dest,source,env=build_env)
            transition=audit.sdist_transition(before,audit.file_map(source),mod,source)
            wheel=next(dest.glob('*.whl'));assert audit.inspect(wheel,name,source,helper)==report['archives'][wheel.name]
            report.setdefault('selected_sdist_closure',{})[name]=dict(archive_sha256=sha(archive.read_bytes()),
                materialized={p:dict(bytes=len(raw),sha256=sha(raw)) for p,raw in members.items()},generated_transition=transition)
            save()
        paths=[next(OUT.glob(mod+'-*.whl')) for mod,version in PACKAGES.values()]
        py=helper.install(paths,owned/'wheel-compute')
        before=audit.installed(py,list(PACKAGES),paths,helper,run)
        harness=owned/'harness';harness.mkdir()
        for p in HARNESS+('tests/evidence_evaluation/test_evaluation.py',):
            (harness/Path(p).name).write_bytes(selected[p])
        harness_map={Path(p).name:sha(selected[p]) for p in HARNESS+('tests/evidence_evaluation/test_evaluation.py',)}
        assert len(harness_map)==len(HARNESS)+1
        # Verify the owned verifier source and exact flat input set before import.
        assert {p.name for p in harness.iterdir()}==set(harness_map)
        for name,digest in harness_map.items():
            path=harness/name
            assert stat.S_ISREG(path.lstat().st_mode) and sha(path.read_bytes())==digest
        driver_tools=module('_eq117_harness_closure',harness/'run_evidence_evaluation.py')
        def check_harness(stage):
            snapshot=driver_tools.harness_snapshot(harness,harness_map)
            report.setdefault('harness_closure',{})[stage]=snapshot
            save()  # Preserve actual node/type/hash evidence even on refusal.
            driver_tools.verify_harness_snapshot(snapshot,harness_map)
        check_harness('before_qualification')
        run(py,'-I','-B',harness/'test_evaluation.py')
        check_harness('after_qualification')
        report['qualification_methods']=9
        after=audit.installed(py,list(PACKAGES),paths,helper,run);assert before==after
        environment=json.loads(run(py,'-I','-c',
            'import sys,platform,json,os,time;c=time.get_clock_info("perf_counter");print(json.dumps(dict(prefix=sys.prefix,executable=sys.executable,python=platform.python_version(),platform=platform.platform(),machine=platform.machine(),processor=platform.processor(),logical_cpu_count=os.cpu_count(),clock=dict(implementation=c.implementation,monotonic=c.monotonic,adjustable=c.adjustable,resolution_seconds=c.resolution),runner={k:os.environ.get(k) for k in ("GITHUB_RUN_ID","GITHUB_RUN_ATTEMPT","GITHUB_JOB","RUNNER_NAME","RUNNER_OS","ImageOS","ImageVersion")},concurrency_scope="Sequential trial requests; two retained warm actors; provider host co-load is unobserved and uncontrolled.")))'))
        assert environment['clock']['monotonic'] is True and environment['clock']['adjustable'] is False
        assert Path(environment['prefix']).resolve()==py.parent.parent.resolve()
        report.update(installed=after,environment=environment,harness_source_map=harness_map,
                      selected_wheels={p.name:sha(p.read_bytes()) for p in paths},status='qualified')
        closure();save()
        if study:
            source_map={Path(p).name:sha(selected[p]) for p in HARNESS}
            context=dict(schema='eq117.study.context.v1',study_id=sys.argv[2],source_head=head,
                proposal_sha256='7405067b0360126a462bb7a66b5a89416cf93399843b0933b358760804e45073',
                owner_accepted=True,system=platform.system(),prefix=environment['prefix'],python=environment['python'],
                environment=environment,source_map=source_map,installed_map_sha256=sha(encoded(after)))
            context_path=owned/'context.json';context_raw=encoded(context);assert len(context_raw)<=65536
            context_path.write_bytes(context_raw)
            # The study root must be absent; the driver creates it exactly once.
            run(py,'-I','-B',harness/'run_evidence_evaluation.py',OUT/'study',context_path)
            assert audit.installed(py,list(PACKAGES),paths,helper,run)==after
            check_harness('after_study')
            closure();report['status']='study_recorded';save()
    except BaseException:
        report['status']='failed';save();raise

if __name__=='__main__':main()
