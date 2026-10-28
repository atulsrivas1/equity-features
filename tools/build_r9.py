"""Closed two-repository repeat builds and fresh installed R9 composition."""
from __future__ import annotations
from email.parser import BytesParser
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
import tomllib
from packaging.markers import Marker
from packaging.requirements import Requirement
import build_explanations as common
sys.path.insert(0, str(Path(__file__).resolve().parent))  # tools/_versions.py
from _versions import SIBLINGS, SIBLING_COMMITS

ROOT=Path(__file__).resolve().parents[1]
IO=ROOT/'work/r9-io'
IO_HEAD=SIBLING_COMMITS['io']
OUT=ROOT/'dist/r9'
PACKAGES={**common.PACKAGES,'bundles':('equity_feature_bundles',SIBLINGS['bundles'])}
common.PACKAGES=PACKAGES
run=common.run
sha=common.sha


def snapshot(root,head,scopes):
    paths=tuple(subprocess.check_output(['git','ls-files','--',*scopes],cwd=root,encoding='utf-8').splitlines())
    assert paths
    committed={};live={}
    for n in paths:
        data=subprocess.check_output(['git','show',head+':'+n],cwd=root)
        actual=(root/n).read_bytes();assert actual==data or actual.replace(b'\r\n',b'\n')==data
        committed[n]=data;live[n]=actual
    def closure():
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,encoding='utf-8').strip()==head
        assert tuple(subprocess.check_output(['git','ls-files','--',*scopes],cwd=root,encoding='utf-8').splitlines())==paths
        assert not subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',*scopes],cwd=root)
        assert all((root/n).read_bytes()==body for n,body in live.items())
    closure()
    return committed,{n:{'git_sha256':sha(b),'materialized_sha256':sha(live[n]),'built_from':'committed-Git-bytes'} for n,b in committed.items()},closure


def inspect(path,name,source):
    result=common.inspect(path,name,source)
    files=common.contents(path)
    metadata=BytesParser().parsebytes(next(b for n,b in files.items() if n.endswith('/METADATA') or n.count('/')==1 and n.endswith('/PKG-INFO')))
    project=tomllib.loads((source/'pyproject.toml').read_text(encoding='utf-8'))['project']
    expected=[str(Requirement(s)) for s in project.get('dependencies',[])]
    for extra,items in project.get('optional-dependencies',{}).items():
        for text in items:
            requirement=Requirement(text)
            requirement.marker=Marker(f'({requirement.marker}) and extra == "{extra}"' if requirement.marker else f'extra == "{extra}"')
            expected.append(str(requirement))
    assert sorted(str(Requirement(s)) for s in metadata.get_all('Requires-Dist',[]))==sorted(expected)
    result['exact_dependencies_verified']=True
    return result


def main():
    assert IO.is_dir() and subprocess.check_output(['git','rev-parse','HEAD'],cwd=IO,encoding='utf-8').strip()==IO_HEAD
    assert not OUT.exists() or not list(OUT.iterdir()),'preserve prior dist/r9 before new qualification'
    OUT.mkdir(parents=True,exist_ok=True)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,encoding='utf-8').strip()
    scopes=['packages/'+p for p in PACKAGES if p!='bundles']+['tests/evidence','tests/explanations','tests/r9',
        'examples/r9_reproduction.py','tools/measure_r9.py','tools/build_r9.py','tools/build_explanations.py','tools/check_boundary.py','tools/_versions.py','requirements-dev.txt']
    # Only pinned test vectors, not recursively copied validation receipts.
    scopes+=['docs/stories/'+n for n in ('EQ-096_RECEIPT_ORACLE.json','EQ-097_BATCH_ORACLE.json','EQ-097_CONFIG_ORACLE.json',
        'EQ-097_RESULT_ORACLE.json','EQ-099_EXPLANATION_ORACLE.json','EQ-099_REFERENCE_ORACLE.json','EQ-099_COUNT_ORACLE.json','EQ-100_EXPECTATIONS.json')]
    canonical,cmap,cclosure=snapshot(ROOT,head,scopes)
    foreign,imap,iclosure=snapshot(IO,IO_HEAD,['packages/bundles','tests/bundles','tests/fixtures/bundle_oracle.json'])
    report={'schema':'r9-qualification:1','source_commit':head,'io_commit':IO_HEAD,'system':platform.system(),'python':platform.python_version(),
        'source':{'canonical/'+n:v for n,v in cmap.items()}|{'io/'+n:v for n,v in imap.items()},
        'artifacts':{},'installed':[],'status':'running','epoch':common.EPOCH,'costs':None}
    def save():(OUT/'qualification.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    save();work=ROOT/'work';work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='r9-qualification-',dir=work) as owned_name:
        owned=Path(owned_name).resolve();assert owned.is_relative_to(work.resolve())
        verification=owned/'verification'
        for prefix,items in (('',canonical),('io/',foreign)):
            for n,body in items.items():
                target=verification/(prefix+n);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
        env=dict(os.environ,SOURCE_DATE_EPOCH=str(common.EPOCH),PYTHONHASHSEED='0')
        for repeat in (0,1):
            dest=owned/f'build-{repeat}';dest.mkdir()
            for name,(module,version) in PACKAGES.items():
                source=owned/f'source-{repeat}-{name}';prefix='packages/'+name+'/'
                for n,body in (foreign if name=='bundles' else canonical).items():
                    if n.startswith(prefix):
                        target=source/n.removeprefix(prefix);target.parent.mkdir(parents=True,exist_ok=True);target.write_bytes(body)
                run(sys.executable,'-m','build','--no-isolation','--outdir',dest,source,env=env)
                archives=list(dest.glob(module+'-*'));assert len(archives)==2
                for path in archives:
                    if path.suffix!='.whl':common.normalize(path)
                    details=inspect(path,name,source)
                    if repeat==0:report['artifacts'][path.name]=details;shutil.copyfile(path,OUT/path.name)
                    else:assert details==report['artifacts'][path.name],'repeat archive differs'
        assert len(report['artifacts'])==10;report['repeat_archive_parity']=True;save()
        for form,suffix in (('wheel','.whl'),('sdist','.tar.gz')):
            archives={n:next(OUT.glob(module+'-*'+suffix)) for n,(module,_) in PACKAGES.items()}
            for combined in (False,True):
                original=['contracts','evidence']+(['features'] if combined else [])
                selected=[archives[n] for n in original]
                py=common.install(selected,owned/(form+('-combined' if combined else '-light')))
                modules=[PACKAGES[n][0] for n in original]
                before=common.installed_map(py,modules);common.verify_installed(before,selected)
                optional=[archives[n] for n in ('explanations','bundles')]
                run(py,'-m','pip','install','--no-index','--no-deps','--no-build-isolation',*optional)
                run(py,'-m','pip','check');modules+=['equity_feature_explanations','equity_feature_bundles']
                after=common.installed_map(py,modules);common.verify_installed(after,[*selected,*optional]);assert all(after[n]==digest for n,digest in before.items())
                run(py,'-I','-c',"import sys,importlib.util,equity_feature_evidence,equity_feature_explanations,equity_feature_bundles; assert 'equity_features' not in sys.modules; "+("assert importlib.util.find_spec('equity_features') is None" if not combined else "assert importlib.util.find_spec('equity_features') is not None"),cwd=py.parent)
                cohorts=['tests/evidence','tests/explanations','io/tests/bundles','tests/r9']
                for cohort in cohorts:run(py,'-I','-m','unittest','discover','-s',verification/cohort,cwd=py.parent)
                if combined:run(py,'-I',verification/'examples/r9_reproduction.py',cwd=py.parent)
                typing=py.parent/'r9_typed_consumer.py'
                typing.write_text('from equity_feature_bundles import ReproductionBundle, read_bundle\nfrom equity_feature_bundles.replay import replay_bundle\nfrom equity_feature_explanations import Explanation, explain_result, encode_explanation\ndef inspect(raw: bytes) -> bytes:\n    b: ReproductionBundle = read_bundle(raw)\n    replay_bundle(b)\n    s: Explanation = explain_result(b.result,b.receipt,b.configuration,entity=b.manifest.entity,feature_id="session.trade.count")\n    return encode_explanation(s)\n',encoding='utf-8')
                run(sys.executable,'-m','mypy','--strict','--python-executable',py,typing,cwd=py.parent)
                if form=='wheel' and combined:
                    run(py,'-I',verification/'tools/measure_r9.py',OUT/'costs.json',cwd=py.parent)
                    report['costs']=json.loads((OUT/'costs.json').read_bytes());assert report['costs']['status']=='completed' and len(report['costs']['samples'])==30
                assert after==common.installed_map(py,modules)
                report['installed'].append({'form':form,'combined_actual_core_producer':combined,'optional_independence':not combined,
                    'installed_map':after,'unchanged_original_packages':True,'tests_passed':True,'typing_passed':True,'cohorts':cohorts});save()
    cclosure();iclosure();report['source_head_and_materialization_closure']=True;report['status']='completed';save()


if __name__=='__main__':main()
