"""Repeat Git-source builds, closed archives and four fresh installed forms."""
from __future__ import annotations
import json
import hashlib
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import subprocess
import sys
import tempfile

from build_explanations import run, normalize, sha
from continuous_archives import inspect

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/continuous'
PACKAGES={'contracts':('equity_feature_contracts','0.0.4a4'),
          'features':('equity_features','0.0.4a5'),
          'continuous':('equity_feature_continuous','0.1.0a2')}
SCOPES=['packages/'+name for name in PACKAGES]+[
    'tests/continuous','tests/unit/test_continuous_capability.py',
    'docs/stories/EQ112_MATHEMATICS.md','docs/stories/EQ112_DECISIONS.md',
    'docs/stories/EQ112_FIXTURES.json','docs/stories/EQ112_SCHEMAS.json',
    'docs/stories/EQ113_PLAN.md','docs/stories/EQ113_BUILD_DESIGN.md',
    'docs/stories/EQ113_ADMISSION_FIXTURES.json',
    'docs/stories/EQ114_PLAN.md','docs/stories/EQ114_CASE_MANIFEST.json',
    'docs/stories/EQ114_OVERSIZE_INPUT.json','docs/stories/EQ114_READINESS.json',
    'docs/stories/EQ114_PREPARED_REVIEW.json','docs/stories/EQ114_VALIDATION.json',
    'docs/stories/EQ115_PLAN.md','docs/stories/EQ115_DELIVERY_DESIGN.md',
    'docs/stories/EQ115_SYNTHETIC_ORACLES.json','docs/stories/EQ115_READINESS.json',
    'docs/stories/EQ115_PREPARED_REVIEW.json','docs/stories/EQ115_VALIDATION.json',
    'docs/stories/EQ115_RELEASE_EVIDENCE.json','docs/CONTINUOUS_SUPPLIED_WEEK.md',
    'docs/releases/R12/R12_ACCEPTANCE.md','examples/continuous_supplied_week.py',
    'docs/contracts/REGISTRY.md',
    'docs/CONTINUOUS_API.md',
    'docs/api/CONTINUOUS_RESEARCH.md','docs/features/CROSS_VENUE_FORMULAS.md',
    'docs/stories/EQ113_VALIDATION.json','README.md','docs/CHANGELOG.md',
    'docs/CONTINUOUS_MARKET_DESIGN.md','docs/COMPATIBILITY.md','docs/BUILD_DELIVERY.md',
    'docs/PROJECT_KNOWLEDGE.md','docs/SESSION_HANDOFF.md','docs/knowledge/LESSONS.md',
    'examples/typing/continuous_positive.py','examples/typing/continuous_negative.py',
    'examples/typing/continuous_negative_expected.json',
    'tools/build_continuous.py','tools/continuous_archives.py','tools/continuous_installed.py','tools/continuous_legacy.py',
    'tools/check_boundary.py','tools/check_continuous_boundary.py','tools/build_explanations.py',
    'requirements-dev.txt','mypy.ini','.github/workflows/continuous.yml']


def output(*args,cwd=ROOT,env=None):
    effective=dict(os.environ if env is None else env)
    for name in ('MYPYPATH','PYTHONPATH','PYTHONHOME','PYTHONUSERBASE'):effective.pop(name,None)
    return subprocess.check_output([str(arg) for arg in args],cwd=cwd,env=effective)


def typing(py,verification,cwd):
    example=verification/'examples/typing'
    command=[py,'-I','-B','-m','mypy','--strict','--no-incremental','--show-error-codes','--no-warn-unused-configs',
             '--no-error-summary','--config-file',verification/'mypy.ini']
    positive=output(*command,example/'continuous_positive.py',cwd=cwd)
    expected=json.loads((example/'continuous_negative_expected.json').read_bytes())
    assert output(py,'-I','-B','-m','mypy','--version',cwd=cwd).decode().startswith('mypy '+expected['mypy_version'])
    env=dict(os.environ)
    for key in ('MYPYPATH','PYTHONPATH','PYTHONHOME','PYTHONUSERBASE'):env.pop(key,None)
    result=subprocess.run([str(arg) for arg in [*command,example/'continuous_negative.py']],
        cwd=cwd,env=env,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
    assert result.returncode==1 and not result.stderr, result.stdout+result.stderr
    lines=result.stdout.decode().splitlines();diagnostics=[]
    for line in lines:
        if not line.strip():continue
        match=re.fullmatch(r'.*continuous_negative\.py:(\d+): error: (.*)  \[([a-z-]+)\]',line)
        assert match, line
        diagnostics.append((int(match[1]),match[3],match[2]))
    assert len(diagnostics)==len(expected['diagnostics'])
    for actual,want in zip(diagnostics,expected['diagnostics']):
        assert actual[0]==want['line'] and actual[1]==want['code'] and want['contains'] in actual[2]
    run(py,'-I','-B',example/'continuous_positive.py',cwd=cwd)
    return {'positive_sha256':sha(positive),'negative_sha256':sha(result.stdout),
            'negative_diagnostics':expected['diagnostics'],'mypy':expected['mypy_version']}


def verify_sdist_rebuild_inputs(selected,files,prefix,module):
    """Permit only pinned setuptools' exact generated SOURCES transition."""
    manifest=prefix+'src/'+module+'.egg-info/SOURCES.txt'
    expected=dict(files)
    names=set(files[manifest].decode('utf-8').splitlines())|{'setup.cfg'}
    ordered=sorted(names,key=lambda name:(str(PurePosixPath(name).parent),PurePosixPath(name).name))
    # setuptools80.9.0 manifest_maker writes POSIX UTF8 lines, no final LF.
    expected[manifest]='\n'.join(ordered).encode('utf-8')
    for relative,body in expected.items():
        assert (selected/relative.removeprefix(prefix)).read_bytes()==body, ('SDist rebuild changed selected input',relative)
    return {name:{'sha256':sha(body),'bytes':len(body)} for name,body in sorted(expected.items())}


def supplied_week(py,verification,cwd):
    """Run the external example against selected independent literals, installed only."""
    fixture=verification/'docs/stories/EQ115_SYNTHETIC_ORACLES.json'
    raw=fixture.read_bytes();packet=json.loads(raw)
    assert len(packet['cases'])==12
    expected={'schema':'continuous-supplied-week:1','fixture_sha256':sha(raw),'case_count':12,
        'cases':[{'case_id':case['case_id'],'result_digest':case['expected_result_digest']} for case in packet['cases']],
        'batch_feature_ids':['cross_venue.basis','cross_venue.premium','cross_venue.freeze_max_abs',
            'cross_venue.freeze_mean_abs','cross_venue.reopen_gap','cross_venue.reopen_premium']}
    example=verification/'examples/continuous_supplied_week.py'
    typed=output(py,'-I','-B','-m','mypy','--strict','--no-incremental','--no-error-summary',
        '--no-warn-unused-configs','--config-file',verification/'mypy.ini',example,cwd=cwd)
    actual=output(py,'-I','-B',example,fixture,cwd=cwd)
    assert 0<len(actual)<=16384 and actual.endswith(b'\n')
    assert actual==(json.dumps(expected,sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode()
    return {'receipt':expected,'stdout_sha256':sha(actual),'strict_typing_stdout_sha256':sha(typed)}


def main():
    assert sys.version_info[:2]==(3,12)
    assert not OUT.exists() or not list(OUT.iterdir()), 'preserve earlier qualification'
    head=output('git','rev-parse','HEAD').decode().strip()
    tree=output('git','ls-tree','-r','--full-tree',head)
    whole=[]
    for line in tree.decode().splitlines():
        prefix,name=line.split('\t');mode,kind,blob=prefix.split()
        assert kind=='blob' and mode in ('100644','100755')
        whole.append((name,mode,blob))
    assert len(whole)==len({name for name,_,_ in whole})
    def whole_map():
        batch=subprocess.run(['git','cat-file','--batch'],cwd=ROOT,check=True,
            input=b''.join(blob.encode()+b'\n' for _,_,blob in whole),stdout=subprocess.PIPE).stdout
        offset=0;result={}
        for name,mode,blob in whole:
            end=batch.index(b'\n',offset);header=batch[offset:end].split()
            assert header[:2]==[blob.encode(),b'blob'] and len(header)==3
            size=int(header[2]);start=end+1;body=batch[start:start+size]
            assert len(body)==size and batch[start+size:start+size+1]==b'\n'
            assert hashlib.sha1(b'blob '+str(size).encode()+b'\x00'+body).hexdigest()==blob
            result[name]={'mode':mode,'blob':blob,'bytes':size,'sha256':sha(body)}
            offset=start+size+1
        assert offset==len(batch)
        return result
    whole_before=whole_map()
    paths=output('git','ls-files','--',*SCOPES).decode().splitlines()
    assert all(any(name==scope or name.startswith(scope+'/') for name in paths) for scope in SCOPES)
    assert not output('git','status','--porcelain','--untracked-files=all','--',*SCOPES)
    snapshot={name:output('git','show',head+':'+name) for name in paths}
    live={name:(ROOT/name).read_bytes() for name in paths}
    assert all(live[name].replace(b'\r\n',b'\n')==body for name,body in snapshot.items())
    modes={}
    for line in tree.decode().splitlines():
        prefix,name=line.split('\t');mode,kind,blob=prefix.split()
        if name in snapshot:
            assert mode=='100644' and kind=='blob'
            modes[name]={'mode':mode,'blob':blob,'bytes':len(snapshot[name]),
                'git_sha256':sha(snapshot[name]),'materialized_sha256':sha(live[name])}
    assert set(modes)==set(snapshot)
    def closure():
        assert output('git','rev-parse','HEAD').decode().strip()==head
        assert output('git','ls-tree','-r','--full-tree',head)==tree
        assert whole_map()==whole_before
        assert output('git','ls-files','--',*SCOPES).decode().splitlines()==paths
        assert not output('git','status','--porcelain','--untracked-files=all','--',*SCOPES)
        assert all((ROOT/name).read_bytes()==body for name,body in live.items())
    OUT.mkdir(parents=True,exist_ok=True)
    report={'schema':'continuous-qualification:1','source_commit':head,'whole_git_tree_sha256':sha(tree),
        'system':platform.system(),'python':platform.python_version(),'source':modes,'whole_tree':whole_before,
        'artifacts':{},'forms':[],'status':'running','limits':'Pure supplied batch and package/example qualification; no operating-system-kernel or physical host containment proof.'}
    def save():(OUT/'qualification.json').write_bytes((json.dumps(report,sort_keys=True,indent=2)+'\n').encode())
    save();work=ROOT/'work';work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='continuous-',dir=work) as temporary:
        owned=Path(temporary).resolve();assert owned.is_relative_to(work.resolve())
        verification=owned/'verification'
        for name,body in snapshot.items():
            target=verification/name;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
        def verify_snapshot():
            assert {p.relative_to(verification).as_posix():p.read_bytes() for p in verification.rglob('*') if p.is_file()}==snapshot
        verify_snapshot();closure()
        env=dict(os.environ,SOURCE_DATE_EPOCH='1700000000',PYTHONHASHSEED='0')
        source_maps={};wheel_files={};archives={};rebuilt={}
        for repeat in (0,1):
            dest=owned/f'build-{repeat}';dest.mkdir()
            for name,(module,version) in PACKAGES.items():
                prefix='packages/'+name+'/'
                source={path.removeprefix(prefix):body for path,body in snapshot.items() if path.startswith(prefix)}
                source_maps[name]=source
                directory=owned/f'source-{repeat}-{name}'
                for relative,body in source.items():
                    target=directory/relative;target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
                run(sys.executable,'-I','-B','-m','build','--no-isolation','--outdir',dest,directory,env=env)
                assert all((directory/relative).read_bytes()==body for relative,body in source.items()), 'build changed source input'
                for suffix in ('.whl','.tar.gz'):
                    artifact=dest/(module+'-'+version+('-py3-none-any.whl' if suffix=='.whl' else suffix))
                    # Inspect generator output before normalization can erase modes.
                    try:
                        files,receipt=inspect(artifact,source,module)
                    except BaseException:
                        # Preserve rejected bytes as opaque failure evidence;
                        # they are never extracted or relabeled qualified.
                        shutil.copyfile(artifact,OUT/('FAILED_UNVERIFIED-'+artifact.name))
                        report.update(status='failed',failed_archive=artifact.name)
                        save()
                        raise
                    if suffix=='.tar.gz':normalize(artifact);files,receipt=inspect(artifact,source,module)
                    if repeat==0:
                        report['artifacts'][artifact.name]=receipt
                        target=OUT/artifact.name;shutil.copyfile(artifact,target);archives[name,suffix]=target
                        if suffix=='.whl':wheel_files[name]=files
                    else:assert receipt==report['artifacts'][artifact.name], 'repeat archive drift'
        assert len(report['artifacts'])==6;report['repeat_archive_parity']=True;save()
        for name,(module,version) in PACKAGES.items():
            files,receipt=inspect(archives[name,'.tar.gz'],source_maps[name],module)
            prefix=module+'-'+version+'/'
            selected=owned/('selected-sdist-'+name);selected.mkdir()
            for relative,body in files.items():
                target=selected/relative.removeprefix(prefix);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
            assert {prefix+p.relative_to(selected).as_posix():p.read_bytes() for p in selected.rglob('*') if p.is_file()}==files
            dest=owned/('rebuilt-'+name);dest.mkdir()
            run(sys.executable,'-I','-B','-m','build','--wheel','--no-isolation','--outdir',dest,selected,env=env)
            after_materialization=verify_sdist_rebuild_inputs(selected,files,prefix,module)
            wheel=dest/(module+'-'+version+'-py3-none-any.whl')
            actual,rebuilt_receipt=inspect(wheel,source_maps[name],module)
            assert actual==wheel_files[name], 'selected SDist rebuilt wheel differs'
            rebuilt[name]=wheel
            report.setdefault('selected_sdist_rebuilds',{})[name]={'materialized_entries':receipt['entries'],
                'after_build_selected_entries':after_materialization,
                'generated_manifest_transition':'setuptools80.9.0 adds existing setup.cfg; dirname/basename sorted UTF8 LF without final LF',
                'rebuilt':rebuilt_receipt}
        for form in ('light-wheel','light-sdist','combined-wheel','combined-sdist'):
            selected=rebuilt if form.endswith('sdist') else {name:archives[name,'.whl'] for name in PACKAGES}
            directory=owned/form;run(sys.executable,'-I','-B','-m','venv',directory)
            py=directory/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
            run(py,'-I','-B','-m','pip','install','--no-compile','--no-deps','pip==25.1.1',
                'mypy==1.15.0','mypy_extensions==1.1.0','typing_extensions==4.16.0')
            names=['contracts']+(['features'] if form.startswith('combined') else [])
            run(py,'-I','-B','-m','pip','install','--no-compile','--no-index','--no-deps',*[selected[name] for name in names])
            def installed(names):
                payload=owned/(form+'-selected.json')
                payload.write_bytes(json.dumps([{'module':PACKAGES[name][0],'archive':str(selected[name])} for name in names]).encode())
                return json.loads(output(py,'-I','-B',verification/'tools/continuous_installed.py',payload,cwd=directory))
            before=installed(names)
            run(py,'-I','-B',verification/'tools/continuous_legacy.py',cwd=directory)
            if 'features' in names:
                run(py,'-I','-B','-m','unittest','discover','-s',verification/'tests/unit','-p','test_continuous_capability.py',cwd=directory)
            run(py,'-I','-B','-m','pip','install','--no-compile','--no-index','--no-deps',selected['continuous'])
            after=installed([*names,'continuous'])
            run(py,'-I','-B',verification/'tools/continuous_legacy.py','--continuous',cwd=directory)
            assert all(after[module]==receipt for module,receipt in before.items()), 'old installed distribution drift'
            run(py,'-I','-B','-m','pip','check')
            absent=('equity_feature_workers','equity_feature_io_contracts','equity_feature_io_sdk','equity_feature_evidence',
                    'equity_feature_agent_evidence','equity_feature_agent_ledger','equity_feature_mcp','numpy','pyarrow')
            if 'features' not in names:absent+=('equity_features',)
            run(py,'-I','-B','-c','import importlib.util,sys; assert all(importlib.util.find_spec(n) is None for n in sys.argv[1:])',*absent,cwd=directory)
            run(py,'-I','-B','-m','unittest','discover','-s',verification/'tests/continuous',cwd=directory)
            if 'features' in names:
                run(py,'-I','-B','-m','unittest','discover','-s',verification/'tests/unit','-p','test_continuous_capability.py',cwd=directory)
            typed=typing(py,verification,directory)
            week=supplied_week(py,verification,directory)
            assert installed([*names,'continuous'])==after
            verify_snapshot();closure()
            report['forms'].append({'form':form,'installed':after,'old_distributions_unchanged':True,
                'typing':typed,'synthetic_week':week,'source_tests_passed':True,'optional_absence':list(absent)});save()
        verify_snapshot();closure()
    report.update(status='completed',source_head_and_materialization_closure=True)
    save()


if __name__=='__main__':main()
