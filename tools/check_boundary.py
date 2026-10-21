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
    "import types", "import types as t", "from types import CodeType",
    "from types import FunctionType", "from types import *",
    "from types import MappingProxyType, CodeType",
    "import base64", "import base64 as b64",
    "from base64 import *", "from base64 import encode", "from base64 import decode",
    "from base64 import urlsafe_b64decode, decode",
    "from base64 import urlsafe_b64encode, encode",
    "from base64.extra import urlsafe_b64decode",
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
    "from types import MappingProxyType\nx=MappingProxyType({'a':1})",
    "from types import MappingProxyType as ReadOnly\nx=ReadOnly({'a':1})",
    "from base64 import urlsafe_b64decode\nx=urlsafe_b64decode(b'ZQ==')",
    "from base64 import urlsafe_b64encode\nx=urlsafe_b64encode(b'e')",
    "from base64 import urlsafe_b64decode, urlsafe_b64encode\nx=urlsafe_b64encode(urlsafe_b64decode(b'ZQ=='))",
    "from base64 import urlsafe_b64decode as decode_id, urlsafe_b64encode as encode_id\nx=encode_id(decode_id(b'ZQ=='))",
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

def _civil_import(node):
    return (isinstance(node, ast.ImportFrom) and node.level == 0
            and node.module == 'datetime' and bool(node.names)
            and all(item.name in {'date', 'timedelta'} for item in node.names))


def civil_date_violations(source, *, timestamp_resolver=None):
    """Closed civil constructors; advisory AST lint, not a Python sandbox.

    Import aliases are supported. Extraction through imported class bindings is
    refused. Constructed instance method/value flow is not tracked completely.
    """
    tree = ast.parse(source)
    nodes = list(ast.walk(tree))
    parents = {child: node for node in nodes for child in ast.iter_child_nodes(node)}
    imported = {}
    rebound = set()
    annotations = set()
    found = []
    ambient = {'today', 'now', 'utcnow', 'fromtimestamp', 'utcfromtimestamp', 'timestamp',
               'astimezone', 'strftime', 'strptime', 'localtime', 'gmtime', 'mktime', 'tzset',
               '__dict__', '__class__', '__getattribute__', '__mro__', '__subclasses__',
               '__reduce__', '__reduce_ex__'}
    for node in nodes:
        if isinstance(node, ast.Import):
            for item in node.names:
                name = item.asname or item.name.split('.')[0]
                rebound.add(name)
        elif isinstance(node, ast.ImportFrom) and not _civil_import(node):
            rebound.update(item.asname or item.name for item in node.names)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            rebound.add(node.id)
        elif isinstance(node, ast.arg):
            rebound.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            rebound.add(node.name)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            rebound.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            rebound.update(node.names)
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
            rebound.add(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest:
            rebound.add(node.rest)
        if isinstance(node, ast.Import) and any(item.name.split('.')[0] == 'datetime' for item in node.names):
            found.append('civil date namespace import')
        if isinstance(node, ast.ImportFrom) and (node.module or '').split('.')[0] == 'datetime' and not node.level:
            if not _civil_import(node):
                found.append('unreviewed civil date import')
            else:
                for item in node.names:
                    imported.setdefault(item.asname or item.name, set()).add(item.name)
        annotation = (node.annotation if isinstance(node, (ast.arg, ast.AnnAssign))
                      else node.returns if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) else None)
        if annotation is not None:
            annotations.update(ast.walk(annotation))
    if set(imported) & rebound or any(len(kinds) != 1 for kinds in imported.values()):
        found.append('ambiguous civil date binding')
    for node in nodes:
        parent = parents.get(node)
        columnar_timestamp = (isinstance(node, ast.Attribute) and node.attr == 'timestamp'
                              and timestamp_resolver is not None
                              and timestamp_resolver(node) == {'pyarrow.timestamp'})
        if (isinstance(node, ast.Attribute) and node.attr in ambient
                and (not node.attr.startswith('__') or imported) and not columnar_timestamp):
            # Also covers methods exposed by date instances/helper returns.
            found.append('ambient civil date access ' + node.attr)
        if not isinstance(node, ast.Name) or not isinstance(node.ctx, ast.Load) or node.id not in imported:
            continue
        if node.id in rebound:
            found.append('ambiguous civil date binding')
            continue
        constructor = isinstance(parent, ast.Call) and parent.func is node
        parsedate = (imported[node.id] == {'date'} and isinstance(parent, ast.Attribute)
                     and parent.value is node and parent.attr == 'fromisoformat'
                     and isinstance(parents.get(parent), ast.Call) and parents[parent].func is parent)
        annotation = node in annotations
        ancestor = parents.get(node)
        while annotation and ancestor in annotations:
            if not isinstance(ancestor, (ast.Subscript, ast.Tuple, ast.List, ast.BinOp)):
                annotation = False
            ancestor = parents.get(ancestor)
        if not (constructor or parsedate or annotation):
            found.append('civil date class or method escapes closed access')
    return sorted(set(found))


CIVIL_DATE_POSITIVE_FIXTURES = (
    'from datetime import date\nx=date(2026,10,21)',
    'from datetime import date\nx=date.fromisoformat("2026-10-21").isoformat()',
    'from datetime import date as D, timedelta as T\ndef shift(d:D)->D:\n return d+T(days=1)',
    'from datetime import timedelta, date\ndef start(d:date)->date:\n return d-timedelta(days=d.weekday())',
    'from datetime import date\ndef month(d:date)->date:\n return d.replace(day=1,month=1)',
    'from datetime import date\ndef parts(d:date)->tuple[int,int,int]:\n return d.year,d.month,d.day',
    'from datetime import date as D\nfrom datetime import date as D\nx=D(2026,1,1)',
)
CIVIL_DATE_NEGATIVE_FIXTURES = (
    'import datetime', 'import datetime as dt', 'from datetime import *',
    'from datetime.extra import date', 'from datetime import datetime',
    'from datetime import time as T', 'from datetime import date, timezone',
    'from datetime import date as D, datetime as X',
    'from datetime import date as D\nD.today()',
    'from datetime import date as D\nD.fromtimestamp(0)',
    'from datetime import date as D\nd=D(2026,1,1)\nd.today()',
    'from datetime import date as D\nd=D(2026,1,1)\nd.fromtimestamp(0)',
    'from datetime import date as D\nD.fromisoformat(s).fromtimestamp(0)',
    'def consume(d):\n return d.fromtimestamp(0)',
    'from datetime import date as D\nf=D.fromisoformat',
    'from datetime import date as D\nuse(D.fromisoformat)',
    'from datetime import date as D\nuse(D)',
    'from datetime import date as D\ndef leak():\n return D',
    'from datetime import date as D\nx=[D]',
    'from datetime import date as D\nx={"d":D}',
    'from datetime import date as D\nholder.value=D',
    'from datetime import date as D\ndef f(factory=D):\n pass',
    'from datetime import date as D\nalias=D\nalias(2026,1,1)',
    'from datetime import date as D\nalias:object=D\nalias.today()',
    'from datetime import date as D\n(alias:=D).fromtimestamp(0)',
    'from datetime import date as D\nx=D.__dict__',
    'from datetime import date as D\nx=D.__mro__',
    'from datetime import date as D\nx=D.__getattribute__',
    'from datetime import date as D\nD(2026,1,1).__class__.today()',
    'from datetime import date as D\nD(2026,1,1).strftime("%c")',
    'from datetime import timedelta as T\nx=T.max',
    'from datetime import date as D\nx: D.__mro__',
    'from datetime import date as D\nx: use(D)',
    'from datetime import date as D\nuse(D(2026,1,1).__class__)',
    'from datetime import date as D\nD(2026,1,1).__reduce__()',
    'from datetime import date as D\nD=supplied\nD.fromisoformat(s)',
    'from datetime import date as D\ndef f(D):\n return D.fromisoformat(s)',
    'from datetime import date as D\ndef D(): pass\nD.fromisoformat(s)',
    'from datetime import date as D\nclass D: pass\nD.fromisoformat(s)',
    'from datetime import date as D\nfrom other import D\nD.fromisoformat(s)',
    'from datetime import date as D\n(D:=supplied).fromisoformat(s)',
    'from datetime import date as D\ntry: pass\nexcept Error as D: pass\nD.fromisoformat(s)',
    'from datetime import date as D\ndef f():\n global D\n return D.fromisoformat(s)',
    'from datetime import date as D\nd=D(2026,1,1)\nd.timestamp()',
    'from datetime import date as D, timedelta as D\nx=D(1)',
)

TIMESTAMP_POSITIVE_FIXTURES = (
    'import pyarrow as pa\npa.timestamp("ns")',
    'from pyarrow import timestamp as TS\nTS("ns")',
    'import pyarrow as pa\nother=pa\nother.timestamp("ns")',
    'import pyarrow as pa\nmake=pa.timestamp\nmake("ns")',
    'import pyarrow as pa\nother=pa\nmake=other.timestamp\nagain=make\nagain("ns")',
)
TIMESTAMP_NEGATIVE_FIXTURES = (
    'obj.timestamp()',
    'import pyarrow as pa\npa=supplied\npa.timestamp("ns")',
    'import pyarrow as pa\nother=pa\nother=supplied\nother.timestamp("ns")',
    'import pyarrow as pa\ndef f(pa):\n return pa.timestamp("ns")',
    'import pyarrow as pa\nmake=pa.timestamp\nmake=supplied\nmake("ns")',
)

REGEX_COMPILE_POSITIVE_FIXTURES = (
    'import re\nx=re.compile("synthetic",re.ASCII)',
    'import re as regex\nx=regex.compile("synthetic")',
)
REGEX_COMPILE_NEGATIVE_FIXTURES = (
    'compile("x","synthetic","exec")', 'obj.compile("x")',
    'f=compile\nf("x","synthetic","exec")',
    'import re\nf=re.compile',
    'from re import compile as f\nf("x")',
    'import re\nre=obj\nre.compile("x")',
    'import re\ndef f(re):\n return re.compile("x")',
    'import re\nre:object=obj\nre.compile("x")',
    'import re\n(re:=obj).compile("x")',
    'import re\nre.compile=obj\nre.compile("x")',
    'import re\nuse(re)\nre.compile("x")',
    'import re\nre.__dict__["compile"]=obj\nre.compile("x")',
    'import re\nimport other as re\nre.compile("x")',
    'import re\nmatch value:\n case re: pass\nre.compile("x")',
)

SCALAR_TIME_POSITIVE_FIXTURES = (
    'def f(columns,i):\n time=columns["event_ns"][i]\n return time<10',
    'def f(columns):\n return all(time<10 for time in columns["market"]["event_ns"])',
    'def f(columns,role):\n for i,time in enumerate(columns[role]["effective_start_ns"]):\n  if 0<time<10: pass',
)
SCALAR_TIME_NEGATIVE_FIXTURES = (
    'import time', 'from time import time', 'obj.time()', 'time()',
    'def f(columns,i):\n time=columns["event_ns"][i]\n return time()',
    'def f(columns,i):\n time=columns["event_ns"][i]\n return time.now()',
    'def f(columns,i):\n time=columns["event_ns"][i]\n alias=time',
    'def f(time):\n return time<10',
    'def f(columns,i,supplied):\n time=columns["event_ns"][i]\n time=supplied\n return time<10',
    'def f(supplied):\n for time in supplied:\n  if time<10: pass',
    'def f(columns,i):\n time=columns["event_ns"][i]\n return use(time)',
    'def f(columns,i):\n time=columns["event_ns"][i]\n def time(): pass\n return time<10',
    'def f(columns,i):\n time=columns["event_ns"][i]\n from math import gcd as time\n return time<10',
)


def _scalar_time_name(node, parents, nodes):
    """Admit only bounded column-scalar bindings used directly in comparisons."""
    if not isinstance(node, ast.Name) or node.id != 'time':
        return False
    def scope(item):
        parent = parents.get(item)
        while parent is not None and not isinstance(parent, (ast.FunctionDef, ast.AsyncFunctionDef)):
            parent = parents.get(parent)
        return parent
    owner = scope(node)
    if owner is None or (isinstance(node.ctx, ast.Load) and not isinstance(parents.get(node), ast.Compare)):
        return False
    def column_values(value):
        fields = []
        while isinstance(value, ast.Subscript):
            if isinstance(value.slice, ast.Constant):
                fields.append(value.slice.value)
            value = value.value
        return (isinstance(value, ast.Name) and value.id == 'columns'
                and any(field in ('event_ns', 'effective_start_ns') for field in fields))
    bound = False
    for item in nodes:
        if scope(item) is not owner:
            continue
        if isinstance(item, ast.arg) and item.arg == 'time':
            return False
        if isinstance(item, (ast.Global, ast.Nonlocal)) and 'time' in item.names:
            return False
        if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)) and item.name == 'time':
            return False
        if isinstance(item, ast.ExceptHandler) and item.name == 'time':
            return False
        if isinstance(item, (ast.Import, ast.ImportFrom)) and any(
                (part.asname or part.name.split('.')[0]) == 'time' for part in item.names):
            return False
        if isinstance(item, (ast.MatchAs, ast.MatchStar)) and item.name == 'time':
            return False
        if isinstance(item, ast.MatchMapping) and item.rest == 'time':
            return False
        if not isinstance(item, ast.Name) or item.id != 'time' or isinstance(item.ctx, ast.Load):
            continue
        parent = parents.get(item)
        assignment = (isinstance(parent, (ast.Assign, ast.AnnAssign)) and column_values(parent.value)
                      and (parent.target is item if isinstance(parent, ast.AnnAssign)
                           else len(parent.targets) == 1 and parent.targets[0] is item))
        comprehension = (isinstance(parent, ast.comprehension) and parent.target is item
                         and column_values(parent.iter))
        loop = parents.get(parent) if isinstance(parent, ast.Tuple) else None
        enumerated = (isinstance(loop, ast.For) and loop.target is parent
                      and len(parent.elts) == 2 and parent.elts[1] is item
                      and isinstance(loop.iter, ast.Call) and isinstance(loop.iter.func, ast.Name)
                      and loop.iter.func.id == 'enumerate' and len(loop.iter.args) == 1
                      and not loop.iter.keywords and column_values(loop.iter.args[0]))
        if not isinstance(item.ctx, ast.Store) or not (assignment or comprehension or enumerated):
            return False
        bound = True
    return bound


def violations(source):
    tree=ast.parse(source);nodes=list(ast.walk(tree));found=[]
    parents={child:parent for parent in nodes for child in ast.iter_child_nodes(parent)}
    # Only an unambiguously imported re namespace may compile a regex directly.
    # Python's compile and arbitrary .compile capabilities remain denied.
    regex_names = set()
    rebound = set()
    for node in nodes:
        if isinstance(node, ast.Import):
            for item in node.names:
                name = item.asname or item.name.split('.')[0]
                if item.name == 're':
                    regex_names.add(name)
                else:
                    rebound.add(name)
        elif isinstance(node, ast.ImportFrom):
            rebound.update(item.asname or item.name for item in node.names)
        elif isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            rebound.add(node.id)
        elif isinstance(node, ast.arg):
            rebound.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            rebound.add(node.name)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            rebound.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            rebound.update(node.names)
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
            rebound.add(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest:
            rebound.add(node.rest)
    for node in nodes:
        if isinstance(node, ast.Name) and node.id in regex_names and isinstance(node.ctx, ast.Load):
            parent = parents.get(node)
            if (not isinstance(parent, ast.Attribute) or parent.value is not node
                    or parent.attr.startswith('__')):
                rebound.add(node.id)
    regex_names -= rebound
    def regex_compile(node):
        parent = parents.get(node)
        return (isinstance(node, ast.Attribute) and node.attr == 'compile'
                and isinstance(node.value, ast.Name) and node.value.id in regex_names
                and isinstance(parent, ast.Call) and parent.func is node)
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
            # A single explicit read-only mapping constructor is a reviewed pure
            # API. Do not admit the types namespace or any code/function API.
            pure_mapping = module == 'types' and len(node.names) == 1 and node.names[0].name == 'MappingProxyType'
            # Only the two deterministic in-memory identity codecs are admitted;
            # base64's namespace and file-oriented encode/decode APIs stay denied.
            pure_base64 = module == 'base64' and bool(node.names) and all(
                item.name in {'urlsafe_b64decode', 'urlsafe_b64encode'} for item in node.names)
            if (module.split('.')[0] not in ALLOWED and not (pure_mapping or pure_base64 or _civil_import(node))) or (module.split('.')[0] in BACKENDS and module not in BACKENDS):
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
    stores = {}
    ambiguous = set()
    for node in nodes:
        if isinstance(node, ast.Name) and isinstance(node.ctx, (ast.Store, ast.Del)):
            stores[node.id] = stores.get(node.id, 0) + 1
        elif isinstance(node, ast.arg):
            ambiguous.add(node.arg)
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            ambiguous.add(node.name)
        elif isinstance(node, ast.ExceptHandler) and node.name:
            ambiguous.add(node.name)
        elif isinstance(node, (ast.Global, ast.Nonlocal)):
            ambiguous.update(node.names)
        elif isinstance(node, (ast.MatchAs, ast.MatchStar)) and node.name:
            ambiguous.add(node.name)
        elif isinstance(node, ast.MatchMapping) and node.rest:
            ambiguous.add(node.rest)
    def resolve(node,seen=frozenset(), *, strict=False):
        if isinstance(node,ast.Name):
            if strict and (node.id in seen or node.id in ambiguous or stores.get(node.id, 0) > 1
                           or (node.id in imported and stores.get(node.id, 0))
                           or (stores.get(node.id, 0) and len(aliases.get(node.id, ())) != 1)):
                return set()
            paths=set(imported.get(node.id,()))
            if node.id not in seen:
                for value in aliases.get(node.id,()):paths.update(resolve(value,seen|{node.id},strict=strict))
            return paths
        if isinstance(node,ast.Attribute):return {path+'.'+node.attr for path in resolve(node.value,seen,strict=strict)}
        if isinstance(node,ast.NamedExpr):return resolve(node.value,seen,strict=strict)
        return set()
    found.extend(civil_date_violations(source, timestamp_resolver=lambda node: resolve(node, strict=True)))
    for node in nodes:
        if isinstance(node,(ast.Name,ast.Attribute)):
            name=node.id if isinstance(node,ast.Name) else node.attr
            if ((name in DENIED or name.startswith(('read_','write_','__builtins__')))
                    and not regex_compile(node) and not _scalar_time_name(node, parents, nodes)):
                found.append(f'{node.lineno}: forbidden access {name}')
            if not isinstance(node.ctx,ast.Load):continue
            paths=resolve(node)
            if 'pyarrow.timestamp' in paths and resolve(node, strict=True) != {'pyarrow.timestamp'}:
                found.append(f'{node.lineno}: ambiguous backend timestamp binding')
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


def research_violations(source, *, codec=False, explanation=False, diagnostics=False, conformance=False):
    """Separate stdlib/contracts-only policy; existing core/backend policy is unchanged."""
    tree=ast.parse(source)
    parents={child:node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    allowed={'__future__','dataclasses','enum','typing','math','json','hashlib','re','operator','equity_feature_contracts'}
    if explanation: allowed.add('equity_feature_evidence')
    if diagnostics: allowed={'__future__','dataclasses','typing','equity_feature_contracts','equity_feature_evidence'}
    if conformance: allowed={'__future__','dataclasses','typing','equity_feature_contracts','equity_feature_evidence','equity_feature_diagnostics'}
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
                relative=('', '_model', '_evaluate') if diagnostics else (('', '_explain') if explanation else ('','_model','_codec','_engine','_content'))
                if conformance: relative=('', '_model', '_run')
                if node.level!=1 or (node.module or '') not in relative:found.append('foreign relative import')
                namespace=('_model','_evaluate') if diagnostics else ('_model','_codec','_engine','_content')
                if conformance: namespace=('_model','_run')
                if not node.module and any(a.name not in namespace for a in node.names):found.append('foreign relative namespace')
            elif (node.module or '').split('.')[0] not in allowed:found.append('forbidden research import')
            if any(a.name=='*' for a in node.names):found.append('wildcard import')
            if any(a.name in DENIED or a.name.startswith(('read_','write_','__builtins__')) for a in node.names):found.append('forbidden research imported access')
            if conformance and any(a.name in ('fingerprint_result','fingerprint_batch','fingerprint_config','canonical_content','content_chunks','make_content_receipt','receipt_digest','verify_content') for a in node.names):found.append('unselected conformance content operation')
        elif isinstance(node,(ast.Name,ast.Attribute)):
            name=node.id if isinstance(node,ast.Name) else node.attr
            if name=='getattr' and isinstance(node,ast.Name) and closed_field_lookup(parents.get(node)):continue
            if name in DENIED or name in ('__dict__','__getattribute__','__subclasses__') or name.startswith(('read_','write_','__builtins__')):
                found.append('forbidden research access '+name)
            if conformance and name in ('fingerprint_result','fingerprint_batch','fingerprint_config','canonical_content','content_chunks','make_content_receipt','receipt_digest','verify_content'):found.append('unselected conformance content operation')
    return sorted(set(found))


def provenance_violations(source):
    """Explicit outer profile; never added to the pure calculation allowlist."""
    tree=ast.parse(source);found=civil_date_violations(source)
    allowed={'__future__','dataclasses','typing','math','json',
        'equity_feature_contracts','equity_feature_evidence','equity_feature_io_contracts',
        'equity_feature_io_sdk','equity_feature_duckdb','equity_feature_duckdb_sink','equity_feature_workers'}
    parents={child:node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            if any(a.name.split('.')[0] not in allowed for a in node.names):found.append('unsupported outer import')
        if isinstance(node,ast.ImportFrom):
            if node.level:
                if node.level!=1 or node.module not in ('_model','_bind','_preflight'):found.append('unsupported outer relative')
            elif (node.module or '').split('.')[0] not in allowed and not _civil_import(node):found.append('unsupported outer import')
            if any(a.name=='*' or a.name.startswith(('compute_','__builtins__')) for a in node.names):found.append('unsupported outer import access')
        if isinstance(node,(ast.Name,ast.Attribute)):
            name=node.id if isinstance(node,ast.Name) else node.attr
            if name in ('open','eval','exec','compile','__import__','__dict__','__getattribute__','__subclasses__','connect','acquire','system','popen') or name.startswith(('compute_','read_','write_','__builtins__')):found.append('unsupported outer access')
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='getattr':
            parent=parents.get(node)
            while parent is not None and not isinstance(parent,ast.FunctionDef):parent=parents.get(parent)
            if parent is None or parent.name!='_fields' or len(node.args)!=2 or not all(isinstance(a,ast.Name) for a in node.args) or [a.id for a in node.args]!=['value','name'] or node.keywords:found.append('unsupported outer reflection')
    return sorted(set(found))


def agent_violations(source):
    """Separate pure agent profile; only two accepted public record imports."""
    found=[]
    allowed={'__future__','dataclasses','enum','typing','json','hashlib','re'}
    public={'equity_feature_contracts':{'AvailabilitySpec'},
            'equity_feature_evidence':{'ContentFingerprint','InputFingerprint'}}
    relative={'_model','_codec','_verify'}
    for node in ast.walk(ast.parse(source)):
        if isinstance(node,ast.Import):
            if any(x.name not in allowed for x in node.names):found.append('unsupported agent import')
        elif isinstance(node,ast.ImportFrom):
            if node.level:
                if node.level!=1 or (node.module or '') not in relative|{''}:found.append('unsupported agent relative import')
                if not node.module and any(x.name not in relative for x in node.names):found.append('unsupported agent namespace')
            elif node.module in public:
                if any(x.name not in public[node.module] for x in node.names):found.append('unsupported accepted public agent import')
            elif node.module not in allowed:found.append('unsupported agent import')
            if any(x.name=='*' or x.name in DENIED for x in node.names):found.append('unsupported agent imported access')
        elif isinstance(node,(ast.Name,ast.Attribute)):
            name=node.id if isinstance(node,ast.Name) else node.attr
            if name in DENIED or name in ('__dict__','__getattribute__','__subclasses__') or name.startswith(('read_','write_','__builtins__')):
                found.append('unsupported agent access')
    return sorted(set(found))


AGENT_NEGATIVE_FIXTURES=('import equity_features','import equity_feature_evidence',
    'from equity_feature_evidence import _codec','from equity_feature_evidence._codec import encode_receipt',
    'from equity_feature_contracts import ConfigSpec','from .other import factory',
    'from . import other','from equity_feature_agent_ledger import Store','import pathlib',
    'import time','import os','import socket','import sqlite3','import requests',
    'import equity_feature_workers','from ._model import *','x=getattr(value,name)',
    'obj.__dict__','open("x")','json.dump(value,stream)')
AGENT_POSITIVE_FIXTURES=('from equity_feature_contracts import AvailabilitySpec',
    'from equity_feature_evidence import ContentFingerprint, InputFingerprint',
    'from . import _model as m','from ._codec import encode_event',
    'from dataclasses import dataclass\nfrom enum import Enum',
    'import hashlib\nimport json\nx=json.dumps({"synthetic":True})')


def ledger_violations(source, *, storage=False):
    """External storage is explicit; no private event codec or execution imports."""
    allowed={'__future__','dataclasses','enum','json','re','typing','equity_feature_agent_evidence'}
    if storage:allowed|={'contextlib','os','pathlib','sqlite3','stat','urllib'}
    event_public={'AgentEvidenceError','EventRecord','EventReference','encode_event','decode_event','EventKind','event_reference','ToolCallSubject','ToolResultSubject','FeatureReadSubject','DecisionSubject','HumanReviewSubject','CancellationSubject','ErrorSubject','CorrectionSubject'}
    errors=[]
    for node in ast.walk(ast.parse(source)):
        if isinstance(node,ast.Import):
            for name in node.names:
                if name.name.split('.')[0] not in allowed:errors.append('import '+name.name)
                if name.name.startswith('equity_feature_agent_evidence.'):errors.append('private event import')
                if name.name.split('.')[0]=='urllib':errors.append('unreviewed network namespace')
        if isinstance(node,ast.ImportFrom):
            if node.level:
                if node.level!=1:errors.append('outside owned relative namespace')
                if node.module not in (None,'_model','_verify','_schema','_store'):errors.append('relative import')
                if node.module is None and any(x.name not in ('_model','_verify','_schema','_store') for x in node.names):errors.append('unknown relative member')
            elif (node.module or '').split('.')[0] not in allowed:errors.append('import '+str(node.module))
            if (node.module or '').split('.')[0]=='urllib' and not (storage and node.module=='urllib.parse' and all(x.name=='quote' for x in node.names)):errors.append('unreviewed network import')
            if node.module=='equity_feature_agent_evidence' and any(x.name not in event_public for x in node.names):errors.append('unreviewed event member')
            if (node.module or '').startswith('equity_feature_agent_evidence.') or any(x.name=='*' for x in node.names):errors.append('private or wildcard import')
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id in {'eval','exec','compile','__import__','globals','locals'}:errors.append('dynamic execution')
        if not storage and isinstance(node,ast.Call):
            called=node.func.id if isinstance(node.func,ast.Name) else node.func.attr if isinstance(node.func,ast.Attribute) else ''
            if called in DENIED or called in {'read','read_bytes','read_text','write','write_bytes','write_text','input','print','unlink','mkdir','rmdir','remove','replace','rename','close','flush'}:errors.append('pure side effect')
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name) and node.func.id=='getattr':
            if not (storage and len(node.args)>=2 and isinstance(node.args[1],ast.Constant) and node.args[1].value=='sqlite_errorcode'):errors.append('dynamic access')
    return errors


def continuous_violations(source):
    """Dedicated continuous contracts policy; not a Python sandbox."""
    tree=ast.parse(source);found=[]
    allowed={'__future__','dataclasses','typing','fractions','json','hashlib'}
    relative={'_model','_rational','_codec','_engine','_registry'}
    public={'AvailabilitySpec','IntervalSpec','SourceBinding','PriceUnit',
            'AdjustmentSpec','Coverage','ContractError','ErrorCode'}
    parents={child:node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            if any(x.name not in allowed for x in node.names):found.append('unsupported continuous import')
        elif isinstance(node,ast.ImportFrom):
            if node.level:
                if node.level!=1 or (node.module or '') not in relative|{''}:found.append('unsupported continuous relative')
                if not node.module and any(x.name not in relative for x in node.names):found.append('unsupported continuous namespace')
            elif node.module=='equity_feature_contracts':
                if any(x.name not in public for x in node.names):found.append('unsupported continuous public import')
            elif node.module not in allowed:found.append('unsupported continuous import')
            if any(x.name=='*' or x.name in DENIED for x in node.names):found.append('unsupported continuous imported access')
        elif isinstance(node,(ast.Name,ast.Attribute)):
            name=node.id if isinstance(node,ast.Name) else node.attr
            # A scalar loop variable named time is not clock access; imports of
            # clock modules are forbidden above and attribute time stays denied.
            denied=DENIED-{'time'} if isinstance(node,ast.Name) else DENIED
            if name in denied or name in {'__dict__','__getattribute__','__subclasses__','__setattr__','input','print','read','write','close','flush'} or name.startswith(('read_','write_','__builtins__')):
                # Frozen initializers may set one literal owned field on self.
                call=parents.get(node);function=call
                while function is not None and not isinstance(function,ast.FunctionDef):function=parents.get(function)
                owner=parents.get(function)
                fields={statement.target.id for statement in owner.body if isinstance(statement,ast.AnnAssign) and isinstance(statement.target,ast.Name)} if isinstance(owner,ast.ClassDef) else set()
                fixed=(name=='__setattr__' and isinstance(node,ast.Attribute) and isinstance(node.value,ast.Name) and node.value.id=='object'
                       and isinstance(call,ast.Call) and call.func is node and len(call.args)==3 and not call.keywords
                       and isinstance(call.args[0],ast.Name) and call.args[0].id=='self'
                       and isinstance(call.args[1],ast.Constant) and type(call.args[1].value) is str
                       and call.args[1].value in fields
                       and function is not None and function.name in ('__init__','__post_init__'))
                if not fixed:found.append('unsupported continuous access '+name)
    return sorted(set(found))


def check_continuous():
    root=ROOT/'packages/continuous'
    if not root.exists():return
    project=tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))['project']
    assert project['dependencies']==['equity-feature-contracts==0.0.4a4']
    assert not project.get('optional-dependencies',{}),'unreviewed continuous extras'
    for path in root.glob('src/**/*.py'):
        errors=continuous_violations(path.read_text(encoding='utf-8'))
        assert not errors,(path.relative_to(ROOT),errors)
    negative=('import os','import equity_features','import fractions.private',
              'from equity_feature_contracts._codec import encode','from equity_feature_contracts import to_json',
              'from .other import f','from .._model import X','from . import other',
              'from json import load as f; f(stream)','import json as j; f=j.dump; f(x,s)',
              'x=getattr','f=open','x.__dict__','object.__setattr__(x,name,value)',
              'def __init__(self):\n object.__setattr__(self,name,value)',
              'def other(self):\n object.__setattr__(self,"x",value)',
              'class X:\n x: int\n def __init__(self):\n  object.__setattr__(self,"undeclared",value)')
    positive=('from fractions import Fraction','import json as j; j.loads(b"{}")',
              'from . import _model as m','from ._rational import Rational',
              'from equity_feature_contracts import AvailabilitySpec',
              'class X:\n x: int\n def __init__(self):\n  object.__setattr__(self,"x",value)')
    for source in negative:assert continuous_violations(source),source
    for source in positive:assert not continuous_violations(source),(source,continuous_violations(source))
    print(f'Continuous static policy: {len(negative)} negative/{len(positive)} positive controls; not a Python sandbox.')


def check():
    # Apply the same civil-only exception to calculations and outer preflight.
    # These are source fixtures: no date/clock or numerical code is executed.
    for source in CIVIL_DATE_NEGATIVE_FIXTURES:
        assert violations(source), source
        assert provenance_violations(source), source
    for source in CIVIL_DATE_POSITIVE_FIXTURES:
        assert not violations(source), (source, violations(source))
        assert not provenance_violations(source), (source, provenance_violations(source))
    for source in REGEX_COMPILE_NEGATIVE_FIXTURES:
        assert violations(source), source
    for source in REGEX_COMPILE_POSITIVE_FIXTURES:
        assert not violations(source), (source, violations(source))
    for source in SCALAR_TIME_NEGATIVE_FIXTURES:
        assert violations(source), source
    for source in SCALAR_TIME_POSITIVE_FIXTURES:
        assert not violations(source), (source, violations(source))
    for source in TIMESTAMP_NEGATIVE_FIXTURES:
        assert violations(source), source
    for source in TIMESTAMP_POSITIVE_FIXTURES:
        assert not violations(source), (source, violations(source))
    print(f'Civil date static policy: {len(CIVIL_DATE_NEGATIVE_FIXTURES)} negative/'
          f'{len(CIVIL_DATE_POSITIVE_FIXTURES)} positive controls; not a Python sandbox.')
    print(f'Regex compile static policy: {len(REGEX_COMPILE_NEGATIVE_FIXTURES)} negative/'
          f'{len(REGEX_COMPILE_POSITIVE_FIXTURES)} positive controls.')
    print(f'Scalar time static policy: {len(SCALAR_TIME_NEGATIVE_FIXTURES)} negative/'
          f'{len(SCALAR_TIME_POSITIVE_FIXTURES)} positive controls.')
    print(f'Timestamp compatibility policy: {len(TIMESTAMP_NEGATIVE_FIXTURES)} negative/'
          f'{len(TIMESTAMP_POSITIVE_FIXTURES)} positive controls.')
    allowed_dependencies={'equity-feature-contracts','numpy','pyarrow'}
    pure_packages=(ROOT/'packages/contracts',ROOT/'packages/features')
    research_packages=(ROOT/'packages/strategies',ROOT/'packages/labels')
    evidence_packages=(ROOT/'packages/evidence',)
    explanation_packages=(ROOT/'packages/explanations',)
    diagnostic_packages=(ROOT/'packages/diagnostics',)
    provenance_packages=(ROOT/'packages/provenance',)
    conformance_packages=(ROOT/'packages/conformance',)
    agent_packages=(ROOT/'packages/agent-evidence',)
    ledger_packages=(ROOT/'packages/agent-ledger',)
    continuous_packages=(ROOT/'packages/continuous',)
    known_packages=set(pure_packages)|set(research_packages)|set(evidence_packages)|set(explanation_packages)|set(diagnostic_packages)|set(provenance_packages)|set(conformance_packages)|set(agent_packages)|set(ledger_packages)
    known_packages|=set(continuous_packages)
    # EQ137 explicitly admits only the separately checked pure intraday package.
    intraday_package=ROOT/'packages/intraday'
    known_packages.add(intraday_package)
    assert {p.parent for p in (ROOT/'packages').glob('*/pyproject.toml')} <= known_packages,'unreviewed package boundary'
    if (intraday_package/'pyproject.toml').is_file():
        # Historical selected-source snapshots omit this optional package/tool.
        # Full checkouts containing it must supply and pass its dedicated policy.
        from check_intraday_boundary import check_intraday
        check_intraday()
    check_continuous()
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
    for root in explanation_packages:
        if not root.exists(): continue
        project=tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))['project']
        assert project['dependencies']==['equity-feature-contracts==0.0.4a4','equity-feature-evidence==0.1.0a2']
        assert not project.get('optional-dependencies',{})
        for path in root.glob('src/**/*.py'):
            errors=research_violations(path.read_text(encoding='utf-8'),explanation=True)
            assert not errors,f'{path.relative_to(ROOT)}: {errors}'
    assert research_violations('import equity_feature_evidence')
    assert not research_violations('from equity_feature_evidence import encode_receipt',explanation=True)
    for source in ('import equity_features','import pathlib','from ._codec import decode','x=getattr(obj,name)'):
        assert research_violations(source,explanation=True),source
    for source in ('from json import load as reader; reader(stream)', 'from json import dump as writer; writer(value,stream)'):
        assert research_violations(source),source
    assert not research_violations('from equity_feature_contracts import FeatureResult\nimport operator')
    assert not research_violations('def _fields(value):\n return {name:getattr(value,name) for name in ()}',codec=True)
    assert research_violations('def other(value):\n return getattr(value,name)',codec=True)
    for root in diagnostic_packages:
        if not root.exists(): continue
        project=tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))['project']
        assert project['dependencies']==['equity-feature-contracts==0.0.4a4','equity-feature-evidence==0.1.0a2']
        assert not project.get('optional-dependencies',{})
        for path in root.glob('src/**/*.py'):
            errors=research_violations(path.read_text(encoding='utf-8'),diagnostics=True)
            assert not errors,f'{path.relative_to(ROOT)}: {errors}'
    for source in ('import equity_features','import time','import json','import pathlib',
                   'from ._codec import decode','from . import _codec','x=getattr(obj,name)',
                   'import equity_feature_workers','from equity_feature_io_sdk import Client'):
        assert research_violations(source,diagnostics=True),source
    for source in ('from ._evaluate import evaluate_diagnostics',
                   'from . import _model','from equity_feature_evidence import ContentFingerprint',
                   'from equity_feature_contracts import policies as p\nfrom dataclasses import dataclass'):
        assert not research_violations(source,diagnostics=True),source
    for root in provenance_packages:
        if not root.exists():continue
        project=tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))['project']
        assert project['dependencies']==['equity-feature-contracts==0.0.4a4','equity-feature-evidence==0.1.0a2','equity-feature-diagnostics==0.1.0a1','equity-feature-workers==0.1.0a15','equity-feature-io-contracts==0.1.0a2','equity-feature-io-sdk==0.1.0a2','equity-feature-duckdb==0.1.0a9','equity-feature-duckdb-sink==0.1.0a0']
        assert not project.get('optional-dependencies',{})
        for path in root.glob('src/**/*.py'):
            errors=provenance_violations(path.read_text(encoding='utf-8'));assert not errors,(path,errors)
    for source in ('import pathlib','import socket','import equity_features','open("x")','from .other import factory','x=getattr(obj,name)','from equity_features.session import compute_trades','obj.__dict__'):
        assert provenance_violations(source),source
    for source in ('from equity_feature_workers import GenerationStore','from ._preflight import preflight','def _fields(value):\n return tuple((name,getattr(value,name)) for name in ())'):
        assert not provenance_violations(source),source
    for root in conformance_packages:
        if not root.exists():continue
        project=tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))['project']
        assert project['dependencies']==['equity-feature-contracts==0.0.4a4','equity-feature-evidence==0.1.0a2','equity-feature-diagnostics==0.1.0a1']
        assert not project.get('optional-dependencies',{})
        for path in root.glob('src/**/*.py'):
            errors=research_violations(path.read_text(encoding='utf-8'),conformance=True);assert not errors,(path,errors)
    conformance_negative=('import equity_features','import equity_feature_provenance','import time',
        'from pathlib import Path','from equity_feature_evidence import fingerprint_result',
        'x=getattr(obj,name)','from .other import factory')
    conformance_positive=('from equity_feature_diagnostics import evaluate_diagnostics',
        'import equity_feature_diagnostics as d','from ._run import check_diagnostics',
        'from dataclasses import dataclass\nfrom equity_feature_evidence import ContentFingerprint')
    for source in conformance_negative:assert research_violations(source,conformance=True),source
    for source in conformance_positive:assert not research_violations(source,conformance=True),source
    for root in agent_packages:
        if not root.exists():continue
        project=tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))['project']
        assert project['dependencies']==['equity-feature-contracts==0.0.4a4','equity-feature-evidence==0.1.0a2']
        assert not project.get('optional-dependencies',{})
        for path in root.glob('src/**/*.py'):
            errors=agent_violations(path.read_text(encoding='utf-8'));assert not errors,(path,errors)
    for source in AGENT_NEGATIVE_FIXTURES:assert agent_violations(source),source
    for source in AGENT_POSITIVE_FIXTURES:assert not agent_violations(source),source
    for root in ledger_packages:
        if not root.exists():continue
        project=tomllib.loads((root/'pyproject.toml').read_text(encoding='utf-8'))['project']
        assert project['dependencies']==['equity-feature-agent-evidence==0.1.0a1'] and not project.get('optional-dependencies',{})
        for path in root.glob('src/**/*.py'):
            errors=ledger_violations(path.read_text(encoding='utf-8'),storage=path.name=='_store.py');assert not errors,(path,errors)
    for source in ['import socket','import subprocess','import equity_features','from equity_feature_agent_evidence._codec import decode_event','import equity_feature_agent_evidence._codec','from equity_feature_agent_evidence import _codec','from . import arbitrary_module','from .. import _store','from .._model import Checkpoint','import urllib.request','import urllib','from urllib.request import urlopen','from equity_feature_agent_evidence import *','eval(x)','__import__(x)','getattr(obj,name)']:
        assert ledger_violations(source,storage=True),source
    for source in ['import os','import sqlite3','from pathlib import Path']:
        assert ledger_violations(source),source
        assert not ledger_violations(source,storage=True),source
    for source in ['open("synthetic")','value.read()','value.write_bytes(b"x")']:
        assert ledger_violations(source),source
    for source in ['from equity_feature_agent_evidence import EventRecord','from ._model import Checkpoint','import json']:
        assert not ledger_violations(source),source
    assert not ledger_violations('from urllib.parse import quote',storage=True)
    print('External ledger static policy: 22 negative/7 positive controls; pure files cannot access storage, private event codecs or unreviewed relative modules. This is not a Python sandbox.')
    print(f'Pure boundary: {len(NEGATIVE_FIXTURES)} negative and {len(POSITIVE_FIXTURES)} positive policy fixtures verified; outer profile 8 negative/3 positive; conformance 7 negative/4 positive; agent {len(AGENT_NEGATIVE_FIXTURES)} negative/{len(AGENT_POSITIVE_FIXTURES)} positive controls.')


if __name__=='__main__': check()
