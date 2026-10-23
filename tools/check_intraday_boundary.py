"""Reviewed pure intraday source policy; static controls, not a Python sandbox."""
from __future__ import annotations
import ast
from pathlib import Path
import tomllib

ROOT = Path(__file__).resolve().parents[1]
SYMBOLS = {
    '__future__': {'annotations'},
    'bisect': {'bisect_left', 'bisect_right'},
    'dataclasses': {'dataclass', 'asdict'},
    'fractions': {'Fraction'},
    'typing': {'NoReturn', 'SupportsIndex', 'cast'},
    'decimal': {'Context', 'Decimal', 'DecimalException', 'localcontext', 'ROUND_HALF_EVEN',
                'InvalidOperation', 'DivisionByZero', 'Overflow', 'Underflow', 'Subnormal',
                'Clamped', 'FloatOperation'},
    'math': {'isfinite'},
    'equity_feature_contracts': {
        'AdjustmentSpec', 'AvailabilitySpec', 'ConfigSpec', 'ContractError', 'ErrorCode',
        'Parameter', 'PriceUnit', 'SessionSpec', 'WindowSpec', 'CanonicalBatch',
        'Coverage', 'DataKind', 'InputBinding', 'Reason', 'Status', 'validate_batch', 'FeatureResult',
        'EntityKey', 'EvidenceRow', 'FeatureColumn', 'QualityRow', 'ResultMetadata', 'ValueType',
    },
}
MODULES = {'json': {'loads', 'dumps'}, 'hashlib': {'sha256'}}
INTERNAL = {'_context', '_admission', '_prepare', '_registry', '_dispatch', '_indicators', '_bands',
            '_flow', '_flow_config', '_flow_registry'}
FORBIDDEN = {
    'open', '__import__', 'eval', 'exec', 'compile', 'getattr', 'setattr', 'delattr',
    'globals', 'locals', 'vars', 'dir', 'input', 'print', 'breakpoint', 'help',
    '__builtins__', '__file__', 'load', 'dump', 'read', 'write', 'read_text', 'write_text',
    'read_bytes', 'write_bytes', 'connect', 'send', 'recv', 'system', 'popen',
    'now', 'today', 'utcnow', 'time', 'perf_counter', 'monotonic',
}
FACTORY_FIELDS = {'context_digest', 'config_digest', 'requirements', 'input_bindings',
                  'batches', '_views', '_issuer', 'schema_version'}


def intraday_violations(source: str) -> list[str]:
    tree = ast.parse(source)
    parents = {child: node for node in ast.walk(tree) for child in ast.iter_child_nodes(node)}
    errors: list[str] = []
    aliases: dict[str, str] = {}
    def report(node: ast.AST, reason: str) -> None:
        errors.append(f'{getattr(node, "lineno", 0)}:{reason}')
    def function(node: ast.AST) -> str | None:
        while node in parents:
            node = parents[node]
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                return node.name
        return None
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for item in node.names:
                if item.name not in MODULES:
                    report(node, 'unreviewed module import')
                else:
                    aliases[item.asname or item.name] = item.name
        elif isinstance(node, ast.ImportFrom):
            if node.level:
                if node.level != 1 or node.module not in INTERNAL or any(a.name == '*' for a in node.names):
                    report(node, 'unreviewed relative import')
            elif node.module not in SYMBOLS or any(a.name not in SYMBOLS[node.module] for a in node.names):
                report(node, 'unreviewed public symbol import')
        elif isinstance(node, ast.Name):
            if node.id in FORBIDDEN or (node.id == 'object' and isinstance(node.ctx, ast.Store)):
                report(node, 'forbidden builtin/reflection/source alias')
        elif isinstance(node, ast.Attribute):
            if node.attr in FORBIDDEN:
                report(node, 'forbidden I/O/clock/stream alias')
            if isinstance(node.value, ast.Name) and node.value.id in aliases:
                if node.attr not in MODULES[aliases[node.value.id]]:
                    report(node, 'unreviewed imported module API')
            if node.attr.startswith('__'):
                parent = parents.get(node)
                direct = isinstance(parent, ast.Call) and parent.func is node
                if not (isinstance(node.value, ast.Name) and node.value.id == 'object' and direct):
                    report(node, 'unreviewed reflection')
                    continue
                assert isinstance(parent, ast.Call)
                if node.attr == '__new__':
                    if (function(node) != 'prepare_intraday' or len(parent.args) != 1 or parent.keywords
                            or not isinstance(parent.args[0], ast.Name) or parent.args[0].id != 'IntradayPreparation'):
                        report(node, 'unreviewed factory allocation')
                elif node.attr == '__setattr__':
                    if len(parent.args) != 3 or parent.keywords or not isinstance(parent.args[1], ast.Constant):
                        report(node, 'dynamic attribute mutation')
                        continue
                    name = parent.args[1].value
                    target = parent.args[0]
                    allowed = (function(node) == '__post_init__' and isinstance(target, ast.Name)
                               and target.id == 'self' and name in {'sessions', 'runs'})
                    allowed = allowed or (function(node) == 'prepare_intraday' and isinstance(target, ast.Name)
                                          and target.id == 'result' and name in FACTORY_FIELDS)
                    if not allowed:
                        report(node, 'unreviewed owned attribute mutation')
                else:
                    report(node, 'unreviewed object API')
    return errors


NEGATIVE = (
    'import os', 'import time', 'import pathlib', 'import equity_feature_workers',
    'import equity_feature_io_sdk', 'import equity_features', 'import numpy',
    'from equity_feature_contracts.inputs import CanonicalBatch',
    'from json import load', 'import json as j\nf=j.dump',
    'open("x")', 'f=getattr', 'x.__dict__', 'print("x")',
    'from .._context import Slot', 'from .other import f',
    'object.__setattr__(x,"unknown",value)',
    'def prepare_intraday():\n object.__setattr__(result,name,value)',
    'f=object.__setattr__', 'object=other',
    'from decimal import getcontext', 'from decimal import setcontext',
    'import decimal', 'from decimal import DefaultContext',
)
POSITIVE = (
    'from fractions import Fraction', 'import json as j\nx=j.loads("{}")',
    'from equity_feature_contracts import CanonicalBatch', 'from ._context import Slot',
    'from decimal import Context, Decimal, localcontext',
    'def prepare_intraday():\n result=object.__new__(IntradayPreparation)\n object.__setattr__(result,"batches",())',
)


def check_intraday() -> None:
    package = ROOT/'packages/intraday'
    project = tomllib.loads((package/'pyproject.toml').read_text(encoding='utf-8'))['project']
    assert project['name'] == 'equity-features-intraday'
    assert project['dependencies'] == ['equity-feature-contracts==0.0.4a4']
    assert not project.get('optional-dependencies')
    assert project['license'] == 'Apache-2.0' and project['license-files'] == ['LICENSE']
    assert (package/'LICENSE').read_bytes() == (ROOT/'LICENSE').read_bytes()
    namespace = package/'src/equity_features_intraday'
    assert (namespace/'py.typed').is_file()
    expected = {'__init__.py'} | {name+'.py' for name in INTERNAL}
    assert {p.relative_to(namespace).as_posix() for p in namespace.rglob('*.py')} == expected
    for path in namespace.rglob('*.py'):
        assert not path.is_symlink()
        errors = intraday_violations(path.read_text(encoding='utf-8'))
        assert not errors, (path.relative_to(ROOT), errors)
    for source in NEGATIVE:
        assert intraday_violations(source), source
    for source in POSITIVE:
        assert not intraday_violations(source), (source, intraday_violations(source))
    print(f'Intraday static purity: {len(NEGATIVE)} negative/{len(POSITIVE)} positive controls; not a sandbox.')


if __name__ == '__main__':
    check_intraday()
