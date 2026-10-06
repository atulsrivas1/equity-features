"""Pinned experimental core/consumer repeat-build and actual install gates."""
import gzip
import hashlib
import io
import json
import os
from pathlib import Path
import platform
import subprocess
import sys
import tarfile
import tempfile
import zipfile

ROOT=Path(__file__).resolve().parents[1]
EPOCH=1700000000


def run(*args,**kwargs):
    subprocess.run(args,check=True,cwd=ROOT,**kwargs)


def normalize_sdist(path):
    with tarfile.open(path,'r:gz') as src:
        data=io.BytesIO()
        with tarfile.open(fileobj=data,mode='w',format=tarfile.PAX_FORMAT) as dst:
            for member in sorted(src.getmembers(),key=lambda x:x.name):
                member.mtime=EPOCH;member.uid=member.gid=0;member.uname=member.gname=''
                member.pax_headers={};member.mode=0o755 if member.isdir() else 0o644
                dst.addfile(member,src.extractfile(member) if member.isfile() else None)
    with path.open('wb') as output:
        with gzip.GzipFile(fileobj=output,mode='wb',filename='',mtime=EPOCH) as out:
            out.write(data.getvalue())


def digest(path): return hashlib.sha256(path.read_bytes()).hexdigest()


def inspect(path):
    consumer=path.name.startswith('equity_feature_demo-')
    package='equity_feature_demo' if consumer else 'equity_feature_contracts' if 'contracts' in path.name else 'equity_features'
    if path.suffix=='.whl':
        with zipfile.ZipFile(path) as z: files={n:z.read(n) for n in z.namelist() if not n.endswith('/')}
        assert all(n.startswith((package+'/',package+'-')) for n in files),files.keys()
        assert package+'/py.typed' in files
        metadata=next(v for k,v in files.items() if k.endswith('/METADATA'))
        assert b'License-Expression: Apache-2.0' in metadata
        assert any(k.endswith('/licenses/LICENSE') for k in files)
    else:
        with tarfile.open(path,'r:gz') as t:
            assert not any(m.issym() or m.islnk() for m in t.getmembers())
            files={m.name:t.extractfile(m).read() for m in t.getmembers() if m.isfile()}
        assert any(k.endswith('/src/'+package+'/py.typed') for k in files)
        assert any(k.endswith('/LICENSE') for k in files)
        assert any(k.endswith('/pyproject.toml') for k in files)
        if consumer:
            prefix=path.name.removesuffix('.tar.gz')+'/'
            assert all(n.startswith((prefix+'src/'+package+'/',prefix+'src/'+package+'.egg-info/')) or n in {prefix+x for x in ('LICENSE','PKG-INFO','pyproject.toml','setup.cfg')} for n in files),files.keys()
    for name,content in files.items():
        assert not name.startswith(('/','\\')) and '..' not in Path(name).parts,name
        assert not any(x in name for x in ['__pycache__','.pyc','.env','fixtures','work/']),name
        assert b'C:\\Users\\' not in content and b'/home/runner/' not in content,name


def core_fingerprint(py):
    """Actual installed core bytes before and after independent installation."""
    code='''import hashlib,json
from importlib.metadata import distribution
from pathlib import Path
import equity_features as f,equity_feature_contracts as c
roots=(Path(f.__file__).parent,Path(c.__file__).parent)
assert all('site-packages' in root.parts for root in roots)
result={root.name+'/'+p.relative_to(root).as_posix():hashlib.sha256(p.read_bytes()).hexdigest() for root in roots for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
for name in ('equity-features','equity-feature-contracts'):
    dist=distribution(name)
    for relative in dist.files:
        path=Path(dist.locate_file(relative)).resolve()
        assert 'site-packages' in path.parts
        if '__pycache__' not in path.parts and path.is_file():result[relative.as_posix()]=hashlib.sha256(path.read_bytes()).hexdigest()
print(json.dumps(result,sort_keys=True))
'''
    return json.loads(subprocess.check_output([str(py),'-I','-c',code],text=True,cwd=ROOT))


def clean_install(paths):
    work=ROOT/'work';work.mkdir(exist_ok=True)
    with tempfile.TemporaryDirectory(prefix='install-',dir=work) as tmp:
        env=Path(tmp).resolve();assert env.is_relative_to(work.resolve())
        run(sys.executable,'-m','venv',str(env))
        py=env/('Scripts/python.exe' if os.name=='nt' else 'bin/python')
        # Build tools are necessary only for sdist installation. Runtime remains stdlib.
        if paths[0].suffix!='.whl': run(str(py),'-m','pip','install','--no-deps','setuptools==80.9.0')
        run(str(py),'-m','pip','install','--no-index','--no-deps','--no-build-isolation',*[str(p) for p in paths])
        run(str(py),'-m','pip','check')
        run(str(py),'-I','-c','import equity_feature_contracts as c; import equity_features as f; assert c.__version__==f.__version__==f.contracts_version; print("Clean installed foundation imports verified",c.__version__)')
        run(str(py),'-m','pip','install','--no-deps','numpy==2.2.6','pyarrow==20.0.0')
        consumer_paths=sorted(p for p in paths[0].parent.glob('equity_feature_demo-*') if (p.suffix=='.whl')==(paths[0].suffix=='.whl'))
        assert len(consumer_paths)==1,'matching standalone consumer artifact required'
        for p in consumer_paths:inspect(p)
        before_install=core_fingerprint(py)
        run(str(py),'-m','pip','install','--no-index','--no-deps','--no-build-isolation',*[str(p) for p in consumer_paths])
        after_install=core_fingerprint(py)
        assert before_install==after_install,'consumer installation overwrote installed core'
        if consumer_paths:
            run(str(py),'-I','-c',"""import ast, hashlib
from pathlib import Path
import equity_features as f, equity_feature_contracts as c, equity_feature_demo as d
from equity_feature_demo.walkthrough import main as walkthrough
roots=(Path(f.__file__).parent,Path(c.__file__).parent)
def fingerprint():
    return {str(p):hashlib.sha256(p.read_bytes()).hexdigest() for root in roots for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
for module in (f,c,d):
    assert 'site-packages' in Path(module.__file__).parts, module.__file__
for path in Path(d.__file__).parent.rglob('*.py'):
    for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
        if isinstance(node,ast.Import):
            names=[x.name for x in node.names]
        elif isinstance(node,ast.ImportFrom):
            names=[node.module or '']+[x.name for x in node.names]
            assert node.level==0, 'relative consumer imports are not qualified'
        else:
            continue
        assert not any(part.startswith('_') for name in names for part in name.split('.')), names
before=fingerprint()
d.main()
walkthrough()
assert fingerprint()==before, 'installed core changed during external execution'
print('Independent installed consumer public imports and immutable core verified.')
""")
            run(str(py),'-I','-m','equity_feature_demo.walkthrough')
            # Development tools qualify installed typing; they are not core runtime requirements.
            run(str(py),'-m','pip','install','--no-deps','mypy==1.15.0','mypy_extensions==1.1.0','typing_extensions==4.16.0')
            run(str(py),'-I',str(ROOT/'tools/verify_public_typing.py'))
        after_execution=core_fingerprint(py)
        assert before_install==after_execution,'consumer execution changed installed core'
        fingerprint_digest=lambda values:hashlib.sha256(json.dumps(values,sort_keys=True,separators=(',',':')).encode()).hexdigest()
        consumer_version=subprocess.check_output([str(py),'-I','-c',"from importlib.metadata import version;print(version('equity-feature-demo'))"],text=True).strip()
        consumer_report=dict(schema='consumer-install1',source_commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
            system=platform.system(),consumer_version=consumer_version,artifact=consumer_paths[0].name,artifact_sha256=digest(consumer_paths[0]),
            core_files=len(before_install),before_install_sha256=fingerprint_digest(before_install),after_install_sha256=fingerprint_digest(after_install),
            after_execution_sha256=fingerprint_digest(after_execution),public_only_installed_execution=True)
        (ROOT/'dist'/('consumer-'+platform.system()+'-'+paths[0].suffix.lstrip('.')+'.json')).write_text(json.dumps(consumer_report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
        benchmark=ROOT/'benchmarks/run_baseline.py'
        if benchmark.exists():
            benchmark_output=ROOT/'dist'/('benchmark-'+platform.system()+'-'+paths[0].suffix.lstrip('.')+'.json')
            run(str(py),'-I',str(benchmark),'--quick','--repetitions','2','--output',str(benchmark_output))
        resource=ROOT/'benchmarks/resource_behavior.py'
        if resource.exists():
            resource_output=ROOT/'dist'/('resource-'+platform.system()+'-'+paths[0].suffix.lstrip('.')+'.json')
            run(str(py),'-I',str(resource),'--quick','--output',str(resource_output))
        tests=ROOT/'tests/unit'
        if tests.exists(): run(str(py),'-m','unittest','discover','-s',str(tests))
        for name in ('canonical_inputs','in_memory_adapter','session_bars','session_structure','session_trades','session_top_k','session_quotes','continuous_quotes','session_incremental','session_state','session_merge','action_policies','history_windows','history_averages','history_recursive','history_volatility','daily_volume','interval_volume','relative_returns','declared_breadth','feature_composition','legacy_comparison'):
            example=ROOT/f'examples/{name}.py'
            if example.exists(): run(str(py),str(example))


def main():
    output=ROOT/'dist';output.mkdir(exist_ok=True)
    repeat=ROOT/'work/repeat-dist';repeat.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,SOURCE_DATE_EPOCH=str(EPOCH))
    for out in [output,repeat]:
        assert out.resolve().is_relative_to(ROOT.resolve())
        for pattern in ('equity_feature_contracts-*.whl', 'equity_features-*.whl', 'equity_feature_contracts-*.tar.gz', 'equity_features-*.tar.gz','equity_feature_demo-*.whl','equity_feature_demo-*.tar.gz'):
            for old in out.glob(pattern): old.unlink()
        for source in [ROOT/'packages/contracts',ROOT/'packages/features',ROOT/'examples/external_consumer']:
            run(sys.executable,'-m','build','--no-isolation','--outdir',str(out),str(source),env=env)
        for p in out.glob('*.tar.gz'): normalize_sdist(p)
    paths=sorted([*output.glob('*.whl'),*output.glob('*.tar.gz')])
    assert len(paths)==6,'stale or missing core/consumer artifact set'
    for p in paths:
        assert digest(p)==digest(repeat/p.name),f'reproducibility: {p.name}'
        inspect(p)
    core_paths=[p for p in paths if not p.name.startswith('equity_feature_demo-')]
    consumer_paths=[p for p in paths if p.name.startswith('equity_feature_demo-')]
    assert len(core_paths)==4 and len(consumer_paths)==2
    clean_install([p for p in core_paths if p.suffix=='.whl'])
    clean_install([p for p in core_paths if p.suffix!='.whl'])
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    dirty=bool(subprocess.check_output(['git','status','--porcelain','--','packages','examples/external_consumer'],cwd=ROOT,text=True).strip())
    manifest=dict(schema_version='1',commit=commit,source_dirty=dirty,epoch=EPOCH,python=platform.python_version(),system=platform.system(),artifacts={p.name:digest(p) for p in core_paths},consumer_artifacts={p.name:digest(p) for p in consumer_paths})
    (output/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('Four core and TWO standalone consumer reproducible artifacts inspected and clean-installed; manifest written.')


if __name__=='__main__': main()
