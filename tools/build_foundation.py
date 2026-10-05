"""Pinned repeat-build, archive inspection and clean-install gate for R0."""
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
    package='equity_feature_contracts' if 'contracts' in path.name else 'equity_features'
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
    for name,content in files.items():
        assert not name.startswith(('/','\\')) and '..' not in Path(name).parts,name
        assert not any(x in name for x in ['__pycache__','.pyc','.env','fixtures','work/']),name
        assert b'C:\\Users\\' not in content and b'/home/runner/' not in content,name


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
        tests=ROOT/'tests/unit'
        if tests.exists(): run(str(py),'-m','unittest','discover','-s',str(tests))
        for name in ('canonical_inputs','in_memory_adapter','session_bars','session_structure','session_trades','session_top_k'):
            example=ROOT/f'examples/{name}.py'
            if example.exists(): run(str(py),str(example))


def main():
    output=ROOT/'dist';output.mkdir(exist_ok=True)
    repeat=ROOT/'work/repeat-dist';repeat.mkdir(parents=True,exist_ok=True)
    env=dict(os.environ,SOURCE_DATE_EPOCH=str(EPOCH))
    for out in [output,repeat]:
        assert out.resolve().is_relative_to(ROOT.resolve())
        for pattern in ('equity_feature_contracts-*.whl', 'equity_features-*.whl', 'equity_feature_contracts-*.tar.gz', 'equity_features-*.tar.gz'):
            for old in out.glob(pattern): old.unlink()
        for name in ['contracts','features']:
            run(sys.executable,'-m','build','--no-isolation','--outdir',str(out),str(ROOT/'packages'/name),env=env)
        for p in out.glob('*.tar.gz'): normalize_sdist(p)
    paths=sorted([*output.glob('*.whl'),*output.glob('*.tar.gz')])
    assert len(paths)==4,'stale or missing artifact set'
    for p in paths:
        assert digest(p)==digest(repeat/p.name),f'reproducibility: {p.name}'
        inspect(p)
    clean_install([p for p in paths if p.suffix=='.whl'])
    clean_install([p for p in paths if p.suffix!='.whl'])
    commit=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip()
    dirty=bool(subprocess.check_output(['git','status','--porcelain','--','packages'],cwd=ROOT,text=True).strip())
    manifest=dict(schema_version='1',commit=commit,source_dirty=dirty,epoch=EPOCH,python=platform.python_version(),system=platform.system(),artifacts={p.name:digest(p) for p in paths})
    (output/'manifest.json').write_text(json.dumps(manifest,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('Four reproducible foundation artifacts inspected and clean-installed; manifest written.')


if __name__=='__main__': main()
