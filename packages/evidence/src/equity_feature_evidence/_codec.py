"""Bounded canonical receipt JSON, with no executable-object deserialization."""
from __future__ import annotations

import hashlib
import json
from typing import Any
from equity_feature_contracts import inputs as i, results as r, specs as s
from equity_feature_contracts.errors import ContractError
from . import _model as m


def _project(value: object) -> object:
    if value is None or type(value) in (str, int, bool): return value
    if type(value) is i.DataKind: return value.value
    if type(value) is tuple: return [_project(item) for item in value]
    return {key: _project(item) for key, item in m.record_fields(value)}


def encode_receipt(receipt: m.ExecutionReceipt) -> bytes:
    """Encode a typed receipt, never read files or external content."""
    m.require(type(receipt) is m.ExecutionReceipt)
    m.validate_tree(receipt)
    output = json.dumps(_project(receipt), sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')
    m.require(len(output) <= m.MAX_BYTES, 'limit_exceeded')
    return output


def receipt_digest(receipt: m.ExecutionReceipt) -> str:
    """Digest declarations only; this is not content verification or authentication."""
    return hashlib.sha256(encode_receipt(receipt)).hexdigest()


def _preflight(text: str) -> None:
    """Iterative lexical budgets before the standard JSON parser allocates a tree."""
    pos = depth = nodes = 0
    while pos < len(text):
        char = text[pos]
        if char.isspace() or char in ',:': pos += 1; continue
        if char in '}]':
            depth -= 1; m.require(depth >= 0); pos += 1; continue
        nodes += 1; m.require(nodes <= m.MAX_NODES, 'limit_exceeded')
        if char in '{[':
            depth += 1; m.require(depth <= m.MAX_DEPTH, 'limit_exceeded'); pos += 1
        elif char == '"':
            pos += 1
            while pos < len(text):
                char = text[pos]; pos += 1
                if char == '\\': pos += 1
                elif char == '"': break
            else: raise m.EvidenceError()
        else:
            start = pos
            while pos < len(text) and text[pos] not in ',:[]{} \t\r\n': pos += 1
            token = text[start:pos]
            if not token: raise m.EvidenceError()
            if token not in ('null', 'true', 'false'):
                m.require(len(token) <= 20 and len(token.lstrip('-')) <= 19, 'limit_exceeded')
                m.require(not any(c in token for c in '.eE'))
    m.require(depth == 0)


def _object(value: Any, names: str) -> dict[str, Any]:
    m.require(type(value) is dict and set(value) == set(names.split()))
    assert isinstance(value, dict)
    return value


def _array(value: Any, maximum: int) -> list[Any]:
    m.require(type(value) is list)
    assert isinstance(value, list)
    m.require(len(value) <= maximum, 'limit_exceeded')
    return value


def _fingerprint(value: Any) -> m.ContentFingerprint:
    return m.ContentFingerprint(**_object(value, 'domain digest byte_length schema_version canonicalization algorithm'))


def _coverage(value: Any) -> i.Coverage:
    return i.Coverage(**_object(value, 'expected observed complete'))


def _batch_metadata(value: Any) -> i.BatchMetadata:
    data = _object(value, 'namespace source coverage price_unit adjustment sampling quantity_unit ordering duplicate_policy scope interval_coverage')
    intervals = _array(data['interval_coverage'], 256)
    interval_rows = []
    for row in intervals:
        entry = _object(row, 'name start_ns end_ns coverage')
        interval_rows.append(i.IntervalCoverage(entry['name'], entry['start_ns'], entry['end_ns'], _coverage(entry['coverage'])))
    return i.BatchMetadata(namespace=data['namespace'],
        source=i.SourceBinding(**_object(data['source'], 'source_id snapshot_id mapping_version input_id')),
        coverage=_coverage(data['coverage']),
        price_unit=None if data['price_unit'] is None else i.PriceUnit(**_object(data['price_unit'], 'scale currency')),
        adjustment=i.AdjustmentSpec(**_object(data['adjustment'], 'basis policy_version action_snapshot anchor')),
        sampling=data['sampling'], quantity_unit=data['quantity_unit'], ordering=data['ordering'], duplicate_policy=data['duplicate_policy'],
        scope=None if data['scope'] is None else i.InputScope(**_object(data['scope'], 'start_ns end_ns eligibility_policy include_opening_auction include_closing_auction')),
        interval_coverage=tuple(interval_rows))


def _metadata(value: Any) -> r.ResultMetadata:
    data = _object(value, 'namespace session_id availability config_digest inputs backend_id backend_version evidence_limit schema_version math_policy_version')
    bindings = []
    for row in _array(data['inputs'], 64):
        entry = _object(row, 'role kind metadata schema_version')
        bindings.append(r.InputBinding(entry['role'], i.DataKind(entry['kind']), _batch_metadata(entry['metadata']), entry['schema_version']))
    return r.ResultMetadata(namespace=data['namespace'], session_id=data['session_id'],
        availability=s.AvailabilitySpec(**_object(data['availability'], 'market_cutoff_ns knowledge_cutoff_ns evaluation_ns mode reconstruction_reason')),
        config_digest=data['config_digest'], inputs=tuple(bindings), backend_id=data['backend_id'], backend_version=data['backend_version'],
        evidence_limit=data['evidence_limit'], schema_version=data['schema_version'], math_policy_version=data['math_policy_version'])


def _unique(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        m.require(key not in result, 'duplicate'); result[key] = value
    return result


def _reject_number(value: str) -> Any:
    raise m.EvidenceError()


def decode_receipt(payload: bytes) -> m.ExecutionReceipt:
    """Strict canonical bytes only; no external resolver, imports or execution."""
    m.require(type(payload) is bytes)
    m.require(len(payload) <= m.MAX_BYTES, 'limit_exceeded')
    try:
        text = payload.decode('ascii')
        _preflight(text)
        raw = json.loads(text, object_pairs_hook=_unique, parse_float=_reject_number, parse_constant=_reject_number)
        data = _object(raw, 'domain schema_version canonicalization metadata configuration inputs output formulas environment execution evidence')
        # Fail unknown envelope versions before reconstructing nested records.
        m.require(data['schema_version'] == '1' and data['canonicalization'] == 'receipt-json-v1', 'unsupported_version')
        inputs = []
        for row in _array(data['inputs'], 64):
            entry = _object(row, 'role input_id content')
            inputs.append(m.InputFingerprint(entry['role'], entry['input_id'], _fingerprint(entry['content'])))
        formulas = tuple(m.FormulaBinding(**_object(row, 'feature_id formula_version')) for row in _array(data['formulas'], 256))
        environment = _object(data['environment'], 'python_implementation python_version platform packages')
        packages = tuple(m.PackageVersion(**_object(row, 'name version')) for row in _array(environment['packages'], 64))
        receipt = m.ExecutionReceipt(metadata=_metadata(data['metadata']), configuration=_fingerprint(data['configuration']),
            inputs=tuple(inputs), output=_fingerprint(data['output']), formulas=formulas,
            environment=m.EnvironmentDeclaration(environment['python_implementation'], environment['python_version'], environment['platform'], packages),
            execution=m.ExecutionClaim(**_object(data['execution'], 'executed_at_ns clock_source uncertainty_ns')),
            evidence=m.EvidenceDisclosure(**_object(data['evidence'], 'state retained_count total_count')),
            schema_version=data['schema_version'], canonicalization=data['canonicalization'], domain=data['domain'])
        m.require(encode_receipt(receipt) == payload)
        return receipt
    except m.EvidenceError:
        raise
    except (ContractError, ValueError, TypeError, KeyError, AttributeError, UnicodeError, RecursionError):
        raise m.EvidenceError() from None
