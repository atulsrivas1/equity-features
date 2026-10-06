"""Fail-closed import/call policy for project-owned pure Python packages."""
import ast
from pathlib import Path
import re
import tomllib

ROOT=Path(__file__).resolve().parents[1]
ALLOWED={'__future__','dataclasses','enum','typing','collections','math','fractions','decimal','json','hashlib','re','numpy','pyarrow','equity_feature_contracts','equity_features'}
DENIED={'open','__import__','eval','exec','compile','getattr','setattr','globals','locals','load','save','savez','memmap','fromfile','tofile','memory_map','OSFile','now','today','utcnow','time','perf_counter','connect','system','popen','genfromtxt','loadtxt','input_stream','output_stream','PythonFile','dump'}
BACKENDS={'numpy','pyarrow'}
# Small reviewed surface used by the owned in-memory bridges. New APIs need review.
BACKEND_APIS={
    'numpy.array','numpy.dtype','numpy.int64','numpy.ndarray',
    'pyarrow.array','pyarrow.bool_','pyarrow.decimal128','pyarrow.field',
    'pyarrow.float64','pyarrow.int64','pyarrow.list_','pyarrow.RecordBatch',
    'pyarrow.RecordBatch.from_arrays','pyarrow.schema','pyarrow.string',
    'pyarrow.struct','pyarrow.Table','pyarrow.Table.from_arrays',
    'pyarrow.Table.from_pydict','pyarrow.timestamp',
}

NEGATIVE_FIXTURES=(
    "import requests as r", "from pathlib import Path as P", "import os",
    "import time as t", "open('x')", "f=__import__", "getattr(x,'read')",
    "import pyarrow.parquet as pq", "np.load('x')", "pa.memory_map('x')",
    "clock.now()", "from numpy import load as loader",
    "from pyarrow import memory_map as mmap", "from numpy import *",
    "import numpy as np\nnp.genfromtxt('data.csv')",
    "import pyarrow as pa\npa.input_stream('data.arrow')",
    "from numpy import genfromtxt as loader\nloader('data.csv')",
    "from pyarrow import input_stream as loader\nloader('data.arrow')",
    "import numpy as np\nother=np\nother.genfromtxt('data.csv')",
    "import pyarrow as pa\nother=pa\nother.input_stream('data.arrow')",
    "import numpy as np\nreader=np.genfromtxt\nagain=reader\nagain('data.csv')",
    "from numpy import loadtxt as reader",
    "import numpy.lib as lib", "from pyarrow.csv import read_csv as reader",
    "import numpy as np\nnp.unreviewed_api()",
    "import pyarrow as pa\npa.unreviewed_api()",
    "import pyarrow as pa\nother:object=pa\nother.input_stream('x')",
    "import numpy as np\nuse(np)", "import pyarrow as pa\nmodules=[pa]",
    "import numpy as np\ndef leak(): return np",
    "import numpy as np\nnamespace=np\nnamespace.lib.npyio.genfromtxt('x')",
    "import pyarrow as pa\npa.Table.unreviewed_api()",
    "import numpy as np\narray=np.array([1])\narray.dump('x')",
    "import numpy as np\narray=np.array([1])\nwriter=array.tofile\nwriter('x')",
    "from pyarrow import Table as T\nT.unreviewed_api()",
    "import numpy as np\n(other:=np).genfromtxt('x')",
    "from .columnar import np as backend\nbackend.genfromtxt('x')",
    "from .columnar import *",
)
POSITIVE_FIXTURES=(
    'from dataclasses import dataclass\nfrom .types import T',
    'import numpy as np\nx=np.array([1],dtype=np.int64)\nx.tolist()',
    'from numpy import array as make\nmake([1])',
    'import numpy as np\nother=np\nother.array([1])',
    'import numpy as np\nmake=np.array\nagain=make\nagain([1])',
    'import pyarrow as pa\npa.array([1],type=pa.int64())',
    'from pyarrow import Table as T\nT.from_pydict({"x":[1]})',
    'import pyarrow as pa\nother:object=pa\nother.schema([other.field("x",other.int64())])',
    'import pyarrow as pa\npa.RecordBatch.from_arrays([pa.array([1])],names=["x"])',
    'import numpy as np\nnp.ndarray[int,int]\nnp.dtype(np.int64)',
)

def violations(source):
    tree=ast.parse(source);nodes=list(ast.walk(tree));found=[]
    parents={child:parent for parent in nodes for child in ast.iter_child_nodes(parent)}
    imported={};aliases={}
    for node in nodes:
        if isinstance(node,ast.Import):
            for item in node.names:
                name=item.asname or item.name.split('.')[0]
                imported.setdefault(name,set()).add(item.name if item.asname else item.name.split('.')[0])
                if item.name.split('.')[0] not in ALLOWED or (item.name.split('.')[0] in BACKENDS and item.name not in BACKENDS):
                    found.append(f'{node.lineno}: forbidden import {item.name}')
        elif isinstance(node,ast.ImportFrom):
            if node.level:
                for item in node.names:
                    if item.name in ("*","np","pa","numpy","pyarrow"):
                        found.append(f'{node.lineno}: forbidden relative namespace/wildcard import {item.name}')
                continue
            module=node.module or ''
            if module.split('.')[0] not in ALLOWED or (module.split('.')[0] in BACKENDS and module not in BACKENDS):
                found.append(f'{node.lineno}: forbidden import {module}')
            for item in node.names:
                imported.setdefault(item.asname or item.name,set()).add(module+'.'+item.name)
                if item.name in DENIED or item.name.startswith(('read_','write_')) or item.name=='*':
                    found.append(f'{node.lineno}: forbidden imported access {item.name}')
                if module in BACKENDS and module+'.'+item.name not in BACKEND_APIS:
                    found.append(f'{node.lineno}: unreviewed backend import {module}.{item.name}')
        elif isinstance(node,(ast.Assign,ast.AnnAssign,ast.NamedExpr)):
            targets=node.targets if isinstance(node,ast.Assign) else [node.target]
            if isinstance(node.value,(ast.Name,ast.Attribute)):
                for target in targets:
                    if isinstance(target,ast.Name):aliases.setdefault(target.id,[]).append(node.value)
    def resolve(node,seen=frozenset()):
        if isinstance(node,ast.Name):
            paths=set(imported.get(node.id,()))
            if node.id not in seen:
                for value in aliases.get(node.id,()):paths.update(resolve(value,seen|{node.id}))
            return paths
        if isinstance(node,ast.Attribute):return {path+'.'+node.attr for path in resolve(node.value,seen)}
        if isinstance(node,ast.NamedExpr):return resolve(node.value,seen)
        return set()
    for node in nodes:
        if isinstance(node,(ast.Name,ast.Attribute)):
            name=node.id if isinstance(node,ast.Name) else node.attr
            if name in DENIED or name.startswith(('read_','write_','__builtins__')):
                found.append(f'{node.lineno}: forbidden access {name}')
            if not isinstance(node.ctx,ast.Load):continue
            paths=resolve(node)
            for path in sorted(paths):
                if path.split('.')[0] in BACKENDS and path not in BACKENDS and path not in BACKEND_APIS:
                    found.append(f'{node.lineno}: unreviewed backend access {path}')
            if isinstance(node,ast.Name) and paths & BACKENDS:
                parent=parents.get(node)
                # Module namespaces can qualify reviewed APIs or alias to local names.
                attribute=isinstance(parent,ast.Attribute) and parent.value is node
                alias=isinstance(parent,(ast.Assign,ast.AnnAssign,ast.NamedExpr)) and parent.value is node and all(isinstance(target,ast.Name) for target in (parent.targets if isinstance(parent,ast.Assign) else [parent.target]))
                if not attribute and not alias:
                    found.append(f'{node.lineno}: backend namespace escapes reviewed access')
    return sorted(set(found))


def check():
    allowed_dependencies={'equity-feature-contracts','numpy','pyarrow'}
    pure_packages=(ROOT/'packages/contracts',ROOT/'packages/features')
    known_packages={*pure_packages,ROOT/'packages/duckdb'}
    assert {p.parent for p in (ROOT/'packages').glob('*/pyproject.toml')} <= known_packages,'unreviewed package boundary'
    for p in (root/'pyproject.toml' for root in pure_packages):
        project=tomllib.loads(p.read_text(encoding='utf-8'))['project']
        deps=list(project['dependencies'])
        for extra in project.get('optional-dependencies',{}).values(): deps.extend(extra)
        assert all(re.split(r'[\[<>=!~; ]',d)[0] in allowed_dependencies for d in deps),p
    for root in pure_packages:
        for p in root.glob('src/**/*.py'):
            errors=violations(p.read_text(encoding='utf-8'))
            assert not errors,f'{p.relative_to(ROOT)}: {errors}'
    adapter=ROOT/'packages/duckdb/pyproject.toml'
    if adapter.exists():
        project=tomllib.loads(adapter.read_text(encoding='utf-8'))['project']
        assert project['dependencies']==['equity-feature-contracts==0.0.4a4','duckdb==1.5.6','numpy==2.2.6']
        assert not project.get('optional-dependencies'), 'unreviewed adapter dependencies'
    for source in NEGATIVE_FIXTURES:
        assert violations(source),source
    for source in POSITIVE_FIXTURES:
        assert not violations(source),(source,violations(source))
    print(f'Pure boundary: {len(NEGATIVE_FIXTURES)} negative and {len(POSITIVE_FIXTURES)} positive policy fixtures verified.')


if __name__=='__main__': check()
