"""Fail-closed import/call policy for project-owned pure Python packages."""
import ast
from pathlib import Path
import re
import tomllib

ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'__future__','dataclasses','enum','typing','collections','math','fractions','decimal','json','hashlib','re','numpy','pyarrow','equity_feature_contracts','equity_features'}
DENIED={'open','__import__','eval','exec','compile','getattr','setattr','globals','locals','load','save','savez','memmap','fromfile','tofile','memory_map','OSFile','now','today','utcnow','time','perf_counter','connect','system','popen'}


def violations(source):
    tree=ast.parse(source);found=[]
    for node in ast.walk(tree):
        if isinstance(node,(ast.Import,ast.ImportFrom)):
            modules=[n.name for n in node.names] if isinstance(node,ast.Import) else [node.module or '']
            if isinstance(node,ast.ImportFrom) and node.level: continue
            for m in modules:
                if m.split('.')[0] not in ALLOWED or m.startswith(('pyarrow.dataset','pyarrow.fs','pyarrow.parquet','pyarrow.csv','numpy.lib.npyio')):
                    found.append(f'{node.lineno}: forbidden import {m}')
            if isinstance(node,ast.ImportFrom):
                for imported in node.names:
                    if imported.name in DENIED or imported.name.startswith(('read_','write_')) or imported.name=='*':
                        found.append(f'{node.lineno}: forbidden imported access {imported.name}')
        if isinstance(node,(ast.Name,ast.Attribute)):
            name=node.id if isinstance(node,ast.Name) else node.attr
            if name in DENIED or name.startswith(('read_','write_','__builtins__')):
                found.append(f'{node.lineno}: forbidden access {name}')
    return found


def check():
    allowed_dependencies={'equity-feature-contracts','numpy','pyarrow'}
    for p in (ROOT/'packages').glob('*/pyproject.toml'):
        project=tomllib.loads(p.read_text(encoding='utf-8'))['project']
        deps=list(project['dependencies'])
        for extra in project.get('optional-dependencies',{}).values(): deps.extend(extra)
        assert all(re.split(r'[\[<>=!~; ]',d)[0] in allowed_dependencies for d in deps),p
    for p in (ROOT/'packages').glob('*/src/**/*.py'):
        errors=violations(p.read_text(encoding='utf-8'))
        assert not errors,f'{p.relative_to(ROOT)}: {errors}'
    for source in ["import requests as r", "from pathlib import Path as P", "import os", "import time as t", "open('x')", "f=__import__", "getattr(x,'read')", "import pyarrow.parquet as pq", "np.load('x')", "pa.memory_map('x')", "clock.now()", "from numpy import load as loader", "from pyarrow import memory_map as mmap", "from numpy import *"]:
        assert violations(source),source
    assert not violations('from dataclasses import dataclass\nfrom .types import T\nimport pyarrow as pa\npa.array([1])')
    print('Pure boundary and 14 negative policy fixtures verified.')


if __name__=='__main__': check()
