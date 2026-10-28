"""Closed in-memory canonical bytes. No decoder or dynamic record/class discovery."""
from __future__ import annotations

from enum import Enum
import hashlib
import json
import math
from typing import cast

from equity_feature_contracts import __version__ as CORE_VERSION
from equity_feature_contracts import inputs as i, results as r, specs as s
from . import _model as m

# The one contracts version this distribution is built against (pinned in pyproject.toml; tools/verify_versions.py checks both).
_CONTRACTS_VERSION = "0.0.4a5"

# Exact labels and fields from the accepted v1 record whitelist, never __dict__/pickle.
RECORDS: dict[type[object], tuple[str, tuple[str, ...]]] = {
    r.EntityKey: ('results.EntityKey', ('instrument_id', 'session_id')),
    r.FeatureColumn: ('results.FeatureColumn', ('feature_id', 'algorithm_version', 'dtype', 'unit', 'entities', 'values', 'schema_version')),
    r.QualityRow: ('results.QualityRow', ('entity', 'feature_id', 'status', 'expected', 'observed', 'reasons')),
    r.InputBinding: ('results.InputBinding', ('role', 'kind', 'metadata', 'schema_version')),
    r.ResultMetadata: ('results.ResultMetadata', ('namespace', 'session_id', 'availability', 'config_digest', 'inputs', 'backend_id', 'backend_version', 'evidence_limit', 'schema_version', 'math_policy_version')),
    r.EvidenceRow: ('results.EvidenceRow', ('entity', 'feature_id', 'input_id', 'row_id', 'event_ns', 'known_at_ns', 'effective_start_ns', 'effective_end_ns', 'use', 'exclusion_reason', 'boundary')),
    r.FeatureResult: ('results.FeatureResult', ('values', 'quality', 'metadata', 'evidence')),
    i.PriceUnit: ('inputs.PriceUnit', ('scale', 'currency')),
    i.SourceBinding: ('inputs.SourceBinding', ('source_id', 'snapshot_id', 'mapping_version', 'input_id')),
    i.Coverage: ('inputs.Coverage', ('expected', 'observed', 'complete')),
    i.AdjustmentSpec: ('inputs.AdjustmentSpec', ('basis', 'policy_version', 'action_snapshot', 'anchor')),
    i.InputScope: ('inputs.InputScope', ('start_ns', 'end_ns', 'eligibility_policy', 'include_opening_auction', 'include_closing_auction')),
    i.IntervalCoverage: ('inputs.IntervalCoverage', ('name', 'start_ns', 'end_ns', 'coverage')),
    i.BatchMetadata: ('inputs.BatchMetadata', ('namespace', 'source', 'coverage', 'price_unit', 'adjustment', 'sampling', 'quantity_unit', 'ordering', 'duplicate_policy', 'scope', 'interval_coverage')),
    s.AvailabilitySpec: ('specs.AvailabilitySpec', ('market_cutoff_ns', 'knowledge_cutoff_ns', 'evaluation_ns', 'mode', 'reconstruction_reason')),
    m.Entity: ('Entity', ('namespace', 'instrument_id', 'session_id')),
    m.FeatureRequirement: ('FeatureRequirement', ('feature_id', 'schema_version', 'algorithm_version', 'dtype', 'unit', 'expected_result_config_digest', 'expected_input_semantic_digest')),
    m.Predicate: ('Predicate', ('requirement', 'operator', 'threshold')),
    m.Ranking: ('Ranking', ('requirement', 'direction')),
    m.StrategyConfig: ('StrategyConfig', ('schema_version', 'algorithm_version', 'predicates', 'ranking', 'top_k')),
    m.StrategyRequest: ('StrategyRequest', ('schema_version', 'namespace', 'session_id', 'availability', 'universe', 'feature_results', 'config')),
    m.PredicateDisposition: ('PredicateDisposition', ('predicate_index', 'feature_id', 'state', 'reason')),
    m.StrategyRow: ('StrategyRow', ('entity', 'status', 'predicate_dispositions', 'ranking_value', 'ranking_reason', 'rank')),
    m.StrategyResult: ('StrategyResult', ('schema_version', 'algorithm_version', 'config_digest', 'request_digest', 'input_content_digests', 'rows', 'ranked', 'selected', 'expected', 'eligible', 'matching', 'coverage_numerator', 'coverage_denominator', 'readiness', 'producer_version')),
    m.InputSemantic: ('InputSemantic', ('role', 'kind', 'schema_version', 'namespace', 'source_id', 'mapping_version', 'price_unit', 'adjustment', 'sampling', 'quantity_unit', 'ordering', 'duplicate_policy', 'scope', 'interval_bounds')),
    m.IntervalSemantic: ('IntervalSemantic', ('name', 'start_ns', 'end_ns')),
}
ENUMS: dict[type[object], str] = {r.Status: 'results.Status', r.Reason: 'results.Reason',
    r.ValueType: 'results.ValueType', i.DataKind: 'inputs.DataKind'}
DOMAINS: dict[str, type[object]] = {'strategy-config:1': m.StrategyConfig, 'strategy-request:1': m.StrategyRequest,
    'strategy-result:1': m.StrategyResult, 'core-feature-result:1': r.FeatureResult, 'core-input-semantics:1': tuple}


def _json(value: object) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('ascii')


def _entity(value: r.EntityKey) -> tuple[str, str]:
    return value.instrument_id, value.session_id


def _fields(value: object) -> dict[str, object]:
    record_label, names = RECORDS[type(value)]
    fields = {name: getattr(value, name) for name in names}
    if record_label.startswith(('results.', 'inputs.', 'specs.')):
        for field in fields.values():
            if type(field) is str:
                m.label(field)
    if type(value) is r.FeatureColumn:
        column = value
        m.require(column.feature_id in m.FEATURES, 'unsupported_feature')
        m.version(column.schema_version, '1'); m.version(column.algorithm_version, 'v1')
        m.require(type(column.dtype) is r.ValueType and (column.dtype, column.unit) == m.FEATURES[column.feature_id], 'invalid_unit')
        pairs = sorted(zip(column.entities, column.values, strict=True), key=lambda pair: _entity(pair[0]))
        fields['entities'] = tuple(pair[0] for pair in pairs)
        fields['values'] = tuple(pair[1] for pair in pairs)
    elif type(value) is r.QualityRow:
        fields['reasons'] = tuple(sorted(value.reasons, key=lambda reason: reason.value))
    elif type(value) is r.ResultMetadata:
        metadata = value
        m.version(metadata.schema_version, '1'); m.version(metadata.math_policy_version, 'v1')
        fields['inputs'] = tuple(sorted(metadata.inputs, key=lambda binding: binding.role))
    elif type(value) is r.InputBinding:
        m.version(value.schema_version, '1')
    elif type(value) is i.BatchMetadata:
        fields['interval_coverage'] = tuple(sorted(value.interval_coverage, key=lambda row: row.name))
    elif type(value) is s.AvailabilitySpec:
        availability = value
        m.require(availability.mode == 'known_at' and availability.reconstruction_reason is None, 'inconsistent_identity')
    elif type(value) is r.FeatureResult:
        result = value
        fields['values'] = tuple(sorted(result.values, key=lambda column: column.feature_id))
        fields['quality'] = tuple(sorted(result.quality, key=lambda row: (_entity(row.entity), row.feature_id)))
        fields['evidence'] = tuple(sorted(result.evidence, key=lambda row: _json(_encoded(row, set()))))
    elif type(value) is m.StrategyRequest:
        request = value
        fields['universe'] = tuple(sorted(request.universe))
        fields['feature_results'] = tuple(sorted(request.feature_results, key=feature_result_digest))
    elif type(value) is m.StrategyResult:
        output = value
        fields['rows'] = tuple(sorted(output.rows, key=lambda row: row.entity))
        fields['input_content_digests'] = tuple(sorted(output.input_content_digests))
    return fields


def _encoded(value: object, active: set[int]) -> object:
    kind = type(value)
    if kind in ENUMS:
        return {'enum': ENUMS[kind], 'value': cast(Enum, value).value}
    if value is None or kind is bool:
        return value
    if kind is str:
        text = cast(str, value)
        m.require(not any(0xD800 <= ord(c) <= 0xDFFF for c in text))
        return text
    if kind is int:
        return {'int': str(value)}
    if kind is float:
        number = cast(float, value)
        m.require(math.isfinite(number))
        return {'float64': number.hex()}
    m.require(kind in (tuple, list) or kind in RECORDS)
    identity = id(value)
    m.require(identity not in active)
    active.add(identity)
    try:
        if kind in (tuple, list):
            return [_encoded(item, active) for item in cast(tuple[object, ...] | list[object], value)]
        record_label = RECORDS[kind][0]
        return {'record': record_label, 'fields': {name: _encoded(field, active) for name, field in _fields(value).items()}}
    finally:
        active.remove(identity)


def encode(value: object) -> bytes:
    """ASCII canonical bytes for this closed record/primitive set; never file I/O."""
    m.version(CORE_VERSION, _CONTRACTS_VERSION)
    return _json(_encoded(value, set()))


def digest(domain: str, value: object) -> str:
    """Domain-separated full content identity, including normalized source records."""
    m.require(type(domain) is str)
    m.require(domain in DOMAINS, 'incompatible_version')
    if domain == 'core-input-semantics:1':
        semantics = m.sequence(value, m.InputSemantic)
        m.require(len({row.role for row in semantics}) == len(semantics), 'duplicate')
        value = tuple(sorted(semantics, key=lambda row: row.role))
    else:
        m.require(type(value) is DOMAINS[domain])
    return hashlib.sha256(domain.encode('ascii') + b'\0' + encode(value)).hexdigest()


def feature_result_digest(result: r.FeatureResult) -> str:
    return digest('core-feature-result:1', result)


def input_semantic_digest(result: r.FeatureResult) -> str:
    m.require(type(result) is r.FeatureResult)
    # Check the full supported record graph; no metadata-only shortcut admits a foreign result.
    feature_result_digest(result)
    rows = []
    for binding in result.metadata.inputs:
        metadata = binding.metadata
        rows.append(m.InputSemantic(binding.role, binding.kind, binding.schema_version, metadata.namespace,
            metadata.source.source_id, metadata.source.mapping_version, metadata.price_unit, metadata.adjustment,
            metadata.sampling, metadata.quantity_unit, metadata.ordering, metadata.duplicate_policy, metadata.scope,
            tuple(m.IntervalSemantic(v.name, v.start_ns, v.end_ns) for v in metadata.interval_coverage)))
    return digest('core-input-semantics:1', tuple(rows))
