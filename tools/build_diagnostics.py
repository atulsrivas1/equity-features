"""Committed-source repeat archives and four fresh installed diagnostic forms."""
from __future__ import annotations
import json
import os
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import tempfile
from email.parser import BytesParser
import build_explanations as common

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'dist/diagnostics'
EPOCH=1700000000
PACKAGES={'contracts':('equity_feature_contracts','0.0.4a4'),
    'features':('equity_features','0.0.4a4'), 'evidence':('equity_feature_evidence','0.1.0a2'),
    'diagnostics':('equity_feature_diagnostics','0.1.0a1')}
# Reuse the unchanged reviewed archive/install functions with this closed table.
common.PACKAGES=PACKAGES
run=common.run
sha=common.sha
normalize=common.normalize
install=common.install
installed_map=common.installed_map
verify_installed=common.verify_installed

def inspect(path,name,source):
    value=common.inspect(path,name,source)
    if name=='diagnostics':
        files=common.contents(path)
        metadata=next(v for k,v in files.items() if k.endswith('/METADATA') or k==path.name.removesuffix('.tar.gz')+'/PKG-INFO')
        parsed=BytesParser().parsebytes(metadata)
        assert parsed.get_all('Requires-Dist',[])==['equity-feature-contracts==0.0.4a4','equity-feature-evidence==0.1.0a2']
        assert not parsed.get_all('Provides-Extra',[])
    return value


def main():
    OUT.mkdir(parents=True,exist_ok=True); assert not list(OUT.iterdir()), 'fresh dist/diagnostics required; preserve old qualification'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,encoding='utf-8').strip()
    scopes=['packages/'+p for p in PACKAGES]+['tests/diagnostics','tests/evidence',
        'examples/diagnostic_declarations.py','examples/diagnostic_producer.py',
        'docs/stories/EQ-096_RECEIPT_ORACLE.json','docs/stories/EQ-097_*',
        'docs/stories/EQ-101_TRUTH_TABLE.json','docs/stories/EQ-102_PLAN.md',
        'docs/stories/EQ-102_TEST_MATRIX.json','docs/api/POINT_IN_TIME_DIAGNOSTICS.md',
        'tools/build_diagnostics.py','tools/build_explanations.py','tools/check_boundary.py',
        '.github/workflows/diagnostics.yml','requirements-dev.txt','mypy.ini']
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
    report={'schema':'diagnostics-qualification:1','source_commit':head,'system':platform.system(),'python':platform.python_version(),
            'source':source_map,'artifacts':{},'installed':[],'status':'running','epoch':EPOCH}
    def save():(OUT/'qualification.json').write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    closure(); save(); work=ROOT/'work'; work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='diagnostics-',dir=work) as owned:
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
        assert len(report['artifacts'])==8; report['repeat_archive_parity']=True; save()
        for form,suffix in [('wheel','.whl'),('sdist','.tar.gz')]:
            archives={n:next(OUT.glob(module+'-*'+suffix)) for n,(module,_) in PACKAGES.items()}
            for combined in (False,True):
                selected=[archives['contracts'],archives['evidence']]+([archives['features']] if combined else [])
                py=install(selected,owned/(form+('-combined' if combined else '-isolated')))
                modules=[PACKAGES[n][0] for n in ('contracts','evidence','features') if n in ('contracts','evidence') or combined]
                before=installed_map(py,modules); verify_installed(before,selected)
                run(py,'-m','pip','install','--no-index','--no-deps','--no-build-isolation',archives['diagnostics'])
                run(py,'-m','pip','check')
                after=installed_map(py,[*modules,'equity_feature_diagnostics']); verify_installed(after,[*selected,archives['diagnostics']])
                assert all(after[n]==digest for n,digest in before.items())
                if not combined:
                    run(py,'-I','-c',"import importlib.util; assert all(importlib.util.find_spec(n) is None for n in ('equity_features','equity_feature_io_contracts','equity_feature_workers','equity_feature_strategies','equity_feature_labels'))",cwd=py.parent)
                run(py,'-I','-m','unittest','discover','-s',verification/'tests/diagnostics',cwd=py.parent)
                run(py,'-I',verification/'examples/diagnostic_declarations.py',cwd=py.parent)
                run(py,'-I','-m','unittest','discover','-s',verification/'tests/evidence',cwd=py.parent)
                if combined:
                    run(py,'-I',verification/'examples/diagnostic_producer.py',cwd=py.parent)
                assert after==installed_map(py,[*modules,'equity_feature_diagnostics'])
                typing=py.parent/'explanation_typed_consumer.py'
                typing.write_text('from equity_feature_diagnostics import DecisionContext, DiagnosticPolicy, KnowledgeCheck, DiagnosticReport, evaluate_diagnostics\ndef typed(context: DecisionContext) -> DiagnosticReport:\n    return evaluate_diagnostics(context, DiagnosticPolicy("explicit", "strict", "deny"), (KnowledgeCheck("k", "cited", None),))\n',encoding='utf-8')
                run(sys.executable,'-m','mypy','--strict','--python-executable',py,typing,cwd=py.parent)
                report['installed'].append({'form':form,'combined_actual_core_producer':combined,'optional_independence':not combined,
                    'installed_map':after,'unchanged_original_packages':True,'tests_passed':True,'typing_passed':True}); save()
    closure(); report['source_head_and_materialization_closure']=True; report['status']='completed'; save()


if __name__=='__main__': main()
