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
    "import equity_feature_io_contracts", "import equity_feature_io_sdk",
    "import equity_feature_workers", "import equity_feature_duckdb",
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


def research_violations(source, *, codec=False):
    """Separate stdlib/contracts-only policy; existing core/backend policy is unchanged."""
    tree=ast.parse(source)
    parents={child:node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    allowed={'__future__','dataclasses','enum','typing','math','json','hashlib','re','operator','equity_feature_contracts'}
    found=[]
    def closed_field_lookup(node):
        if not codec or not isinstance(node,ast.Call) or not isinstance(node.func,ast.Name) or node.func.id!='getattr':return False
        if node.keywords or len(node.args)!=2 or not all(isinstance(a,ast.Name) for a in node.args):return False
        if [a.id for a in node.args]!=['value','name']:return False
        parent=parents.get(node)
        while parent is not None and not isinstance(parent,ast.FunctionDef):parent=parents.get(parent)
        return parent is not None and parent.name=='_fields'
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            if any(a.name.split('.')[0] not in allowed for a in node.names):found.append('forbidden research import')
        elif isinstance(node,ast.ImportFrom):
            if node.level:
                if node.level!=1 or (node.module or '') not in ('','_model','_codec','_engine'):found.append('foreign relative import')
                if not node.module and any(a.name not in ('_model','_codec','_engine') for a in node.names):found.append('foreign relative namespace')
            elif (node.module or '').split('.')[0] not in allowed:found.append('forbidden research import')
            if any(a.name=='*' for a in node.names):found.append('wildcard import')
            if any(a.name in DENIED or a.name.startswith(('read_','write_','__builtins__')) for a in node.names):found.append('forbidden research imported access')
        elif isinstance(node,(ast.Name,ast.Attribute)):
            name=node.id if isinstance(node,ast.Name) else node.attr
            if name=='getattr' and isinstance(node,ast.Name) and closed_field_lookup(parents.get(node)):continue
            if name in DENIED or name in ('__dict__','__getattribute__','__subclasses__') or name.startswith(('read_','write_','__builtins__')):
                found.append('forbidden research access '+name)
    return sorted(set(found))


def check():
    allowed_dependencies={'equity-feature-contracts','numpy','pyarrow'}
    pure_packages=(ROOT/'packages/contracts',ROOT/'packages/features')
    research_packages=(ROOT/'packages/strategies',ROOT/'packages/labels')
    evidence_packages=(ROOT/'packages/evidence',)
    known_packages=set(pure_packages)|set(research_packages)|set(evidence_packages)
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
    for source in NEGATIVE_FIXTURES:
        assert violations(source),source
    for source in POSITIVE_FIXTURES:
        assert not violations(source),(source,violations(source))
    for research in (*research_packages,*evidence_packages):
        if not research.exists(): continue
        project=tomllib.loads((research/'pyproject.toml').read_text(encoding='utf-8'))['project']
        assert project['dependencies']==['equity-feature-contracts==0.0.4a4']
        assert not project.get('optional-dependencies',{}),'unreviewed research extras'
        for path in research.glob('src/**/*.py'):
            errors=research_violations(path.read_text(encoding='utf-8'),codec=path.name=='_codec.py')
            assert not errors,f'{path.relative_to(ROOT)}: {errors}'
    for source in ('import equity_features','import equity_feature_labels','import equity_feature_strategies','import numpy','import pyarrow',
                   'import os','from pathlib import Path','import socket','f=open','obj.connect()',
                   'obj.__dict__','x=getattr','getattr(value,name)','from .other import loader'):
        assert research_violations(source),source
    for source in ('from json import load as reader; reader(stream)', 'from json import dump as writer; writer(value,stream)'):
        assert research_violations(source),source
    assert not research_violations('from equity_feature_contracts import FeatureResult\nimport operator')
    assert not research_violations('def _fields(value):\n return {name:getattr(value,name) for name in ()}',codec=True)
    assert research_violations('def other(value):\n return getattr(value,name)',codec=True)
    print(f'Pure boundary: {len(NEGATIVE_FIXTURES)} negative and {len(POSITIVE_FIXTURES)} positive policy fixtures verified.')


if __name__=='__main__': check()
