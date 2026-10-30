"""Closed logical typed content encoding; supplied content consistency, not execution proof."""
from __future__ import annotations
import hashlib
import json
import math
from typing import Iterator
import equity_feature_contracts as contracts
from equity_feature_contracts import inputs as i, results as r, specs as s
from . import _model as m

# The one contracts version this distribution is built against (pinned in pyproject.toml; tools/verify_versions.py checks both).
_CONTRACTS_VERSION = "0.0.4a6"
MAX_CONTENT_BYTES = 32 * 1024 * 1024
MAX_CONTENT_NODES = 1000000
MAX_CONTENT_DEPTH = 24
MAX_SEQUENCE = 100000
Root = i.CanonicalBatch | r.FeatureResult | s.ConfigSpec


def _fields(value: object) -> tuple[str, tuple[tuple[str, object], ...]]:
    if type(value) is i.CanonicalBatch:
        m.require(len(value.columns) <= 64, 'limit_exceeded')
        return 'inputs.CanonicalBatch', (('kind', value.kind), ('columns', tuple(sorted(value.columns, key=lambda c: c.name))), ('metadata', value.metadata),)
    if type(value) is i.Column:
        return 'inputs.Column', (('name', value.name), ('values', value.values),)
    if type(value) is i.BatchMetadata:
        m.require(len(value.interval_coverage) <= 256, 'limit_exceeded')
        return 'inputs.BatchMetadata', (('namespace', value.namespace), ('source', value.source), ('coverage', value.coverage), ('price_unit', value.price_unit), ('adjustment', value.adjustment), ('sampling', value.sampling), ('quantity_unit', value.quantity_unit), ('ordering', value.ordering), ('duplicate_policy', value.duplicate_policy), ('scope', value.scope), ('interval_coverage', value.interval_coverage),)
    if type(value) is i.SourceBinding:
        return 'inputs.SourceBinding', (('source_id', value.source_id), ('snapshot_id', value.snapshot_id), ('mapping_version', value.mapping_version), ('input_id', value.input_id),)
    if type(value) is i.Coverage:
        return 'inputs.Coverage', (('expected', value.expected), ('observed', value.observed), ('complete', value.complete),)
    if type(value) is i.PriceUnit:
        return 'inputs.PriceUnit', (('scale', value.scale), ('currency', value.currency),)
    if type(value) is i.AdjustmentSpec:
        return 'inputs.AdjustmentSpec', (('basis', value.basis), ('policy_version', value.policy_version), ('action_snapshot', value.action_snapshot), ('anchor', value.anchor),)
    if type(value) is i.InputScope:
        return 'inputs.InputScope', (('start_ns', value.start_ns), ('end_ns', value.end_ns), ('eligibility_policy', value.eligibility_policy), ('include_opening_auction', value.include_opening_auction), ('include_closing_auction', value.include_closing_auction),)
    if type(value) is i.IntervalCoverage:
        return 'inputs.IntervalCoverage', (('name', value.name), ('start_ns', value.start_ns), ('end_ns', value.end_ns), ('coverage', value.coverage),)
    if type(value) is s.ConfigSpec:
        return 'specs.ConfigSpec', (('identity', value.identity), ('algorithm_version', value.algorithm_version), ('parameters', value.parameters), ('session', value.session), ('window', value.window), ('availability', value.availability), ('adjustment', value.adjustment), ('price_unit', value.price_unit), ('schema_version', value.schema_version),)
    if type(value) is s.Parameter:
        return 'specs.Parameter', (('name', value.name), ('value', value.value),)
    if type(value) is s.SessionSpec:
        return 'specs.SessionSpec', (('namespace', value.namespace), ('session_id', value.session_id), ('open_ns', value.open_ns), ('close_ns', value.close_ns), ('timezone_label', value.timezone_label), ('intervals', value.intervals), ('scheduled_close_ns', value.scheduled_close_ns), ('early_close', value.early_close), ('include_opening_auction', value.include_opening_auction), ('include_closing_auction', value.include_closing_auction),)
    if type(value) is s.IntervalSpec:
        return 'specs.IntervalSpec', (('name', value.name), ('start_ns', value.start_ns), ('end_ns', value.end_ns),)
    if type(value) is s.WindowSpec:
        return 'specs.WindowSpec', (('count', value.count), ('target_session_id', value.target_session_id), ('governed_sessions', value.governed_sessions), ('anchor', value.anchor),)
    if type(value) is s.AvailabilitySpec:
        return 'specs.AvailabilitySpec', (('market_cutoff_ns', value.market_cutoff_ns), ('knowledge_cutoff_ns', value.knowledge_cutoff_ns), ('evaluation_ns', value.evaluation_ns), ('mode', value.mode), ('reconstruction_reason', value.reconstruction_reason),)
    if type(value) is r.FeatureResult:
        m.require(len(value.values) <= 256, 'limit_exceeded')
        return 'results.FeatureResult', (('values', value.values), ('quality', value.quality), ('metadata', value.metadata), ('evidence', value.evidence),)
    if type(value) is r.FeatureColumn:
        return 'results.FeatureColumn', (('feature_id', value.feature_id), ('algorithm_version', value.algorithm_version), ('dtype', value.dtype), ('unit', value.unit), ('entities', value.entities), ('values', value.values), ('schema_version', value.schema_version),)
    if type(value) is r.EntityKey:
        return 'results.EntityKey', (('instrument_id', value.instrument_id), ('session_id', value.session_id),)
    if type(value) is r.QualityRow:
        return 'results.QualityRow', (('entity', value.entity), ('feature_id', value.feature_id), ('status', value.status), ('expected', value.expected), ('observed', value.observed), ('reasons', value.reasons),)
    if type(value) is r.ResultMetadata:
        m.require(len(value.inputs) <= 64, 'limit_exceeded')
        return 'results.ResultMetadata', (('namespace', value.namespace), ('session_id', value.session_id), ('availability', value.availability), ('config_digest', value.config_digest), ('inputs', value.inputs), ('backend_id', value.backend_id), ('backend_version', value.backend_version), ('evidence_limit', value.evidence_limit), ('schema_version', value.schema_version), ('math_policy_version', value.math_policy_version),)
    if type(value) is r.InputBinding:
        return 'results.InputBinding', (('role', value.role), ('kind', value.kind), ('metadata', value.metadata), ('schema_version', value.schema_version),)
    if type(value) is r.EvidenceRow:
        return 'results.EvidenceRow', (('entity', value.entity), ('feature_id', value.feature_id), ('input_id', value.input_id), ('row_id', value.row_id), ('event_ns', value.event_ns), ('known_at_ns', value.known_at_ns), ('effective_start_ns', value.effective_start_ns), ('effective_end_ns', value.effective_end_ns), ('use', value.use), ('exclusion_reason', value.exclusion_reason), ('boundary', value.boundary),)
    if type(value) is r.BreadthCounts:
        return 'results.BreadthCounts', (('advancing', value.advancing), ('declining', value.declining), ('unchanged', value.unchanged), ('expected', value.expected),)
    if type(value) is r.BreadthFraction:
        return 'results.BreadthFraction', (('above', value.above), ('eligible', value.eligible), ('expected', value.expected),)
    if type(value) is r.TopKTrades:
        return 'results.TopKTrades', (('k', value.k), ('rows', value.rows),)
    if type(value) is r.TopKTradeRow:
        return 'results.TopKTradeRow', (('input_id', value.input_id), ('event_id', value.event_id), ('event_ns', value.event_ns), ('order_key', value.order_key), ('known_at_ns', value.known_at_ns), ('price', value.price), ('size', value.size),)
    if type(value) is r.QuoteStateCounts:
        return 'results.QuoteStateCounts', (('normal', value.normal), ('locked', value.locked), ('crossed', value.crossed), ('invalid', value.invalid),)
    if type(value) is r.QuoteObservation:
        return 'results.QuoteObservation', (('input_id', value.input_id), ('event_id', value.event_id), ('event_ns', value.event_ns), ('order_key', value.order_key), ('known_at_ns', value.known_at_ns), ('bid', value.bid), ('ask', value.ask), ('state', value.state), ('spread', value.spread), ('bps', value.bps),)
    if type(value) is r.SampledSpread:
        return 'results.SampledSpread', (('sampling', value.sampling), ('total', value.total), ('valid', value.valid), ('mean_spread', value.mean_spread), ('mean_bps', value.mean_bps), ('observation_limit', value.observation_limit), ('rows', value.rows),)
    if type(value) is r.QuoteDurations:
        return 'results.QuoteDurations', (('normal', value.normal), ('locked', value.locked), ('crossed', value.crossed), ('invalid', value.invalid), ('expired', value.expired), ('unknown', value.unknown),)
    if type(value) is r.TimeWeightedSpread:
        return 'results.TimeWeightedSpread', (('durations', value.durations), ('mean_spread', value.mean_spread), ('mean_bps', value.mean_bps), ('max_age_ns', value.max_age_ns), ('initial_state', value.initial_state),)
    if type(value) is r.IntervalOHLCV:
        return 'results.IntervalOHLCV', (('rows', value.rows),)
    if type(value) is r.IntervalOHLCVRow:
        return 'results.IntervalOHLCVRow', (('interval', value.interval), ('open_price', value.open_price), ('high_price', value.high_price), ('low_price', value.low_price), ('close_price', value.close_price), ('volume', value.volume), ('quality', value.quality),)
    if type(value) is r.IntervalVolumeShares:
        return 'results.IntervalVolumeShares', (('rows', value.rows),)
    if type(value) is r.IntervalVolumeShareRow:
        return 'results.IntervalVolumeShareRow', (('interval', value.interval), ('share', value.share), ('quality', value.quality),)

    raise m.EvidenceError()


class _Budget:
    def __init__(self) -> None:
        self.size = 0
        self.nodes = 0

    def node(self) -> None:
        self.nodes += 1
        m.require(self.nodes <= MAX_CONTENT_NODES, 'limit_exceeded')

    def token(self, data: bytes) -> bytes:
        self.size += len(data)
        m.require(self.size <= MAX_CONTENT_BYTES, 'limit_exceeded')
        return data


def _string(value: str, payload: bool) -> bytes:
    if payload:
        m.require(len(value) <= 4096, 'limit_exceeded')
        m.require(not any(0xD800 <= ord(c) <= 0xDFFF for c in value))
        m.require(len(value.encode('utf-8')) <= 16384, 'limit_exceeded')
    else:
        m.label(value)
    return json.dumps(value, ensure_ascii=True).encode('ascii')


def _object(fields: tuple[tuple[str, object], ...], depth: int, budget: _Budget,
            payload_keys: tuple[str, ...] = ()) -> Iterator[bytes]:
    budget.node()
    m.require(depth < MAX_CONTENT_DEPTH, 'limit_exceeded')
    yield budget.token(b'{')
    for n, (key, child) in enumerate(sorted(fields)):
        if n: yield budget.token(b',')
        yield from _visit(key, depth + 1, budget)
        yield budget.token(b':')
        yield from _visit(child, depth + 1, budget, key in payload_keys)
    yield budget.token(b'}')


def _visit(value: object, depth: int, budget: _Budget, payload: bool = False) -> Iterator[bytes]:
    # Record/float wrappers count as ordinary JSON objects, including their keys.
    if type(value) is float:
        m.require(math.isfinite(value))
        yield from _object((('float64', value.hex()),), depth, budget)
        return
    if value is not None and type(value) not in (bool, int, str, tuple, i.DataKind, i.DType, r.Status, r.Reason, r.ValueType):
        tag, fields = _fields(value)
        # Fixed two-layer record wrapper; no full graph projection.
        budget.node(); m.require(depth < MAX_CONTENT_DEPTH, 'limit_exceeded')
        yield budget.token(b'{')
        yield from _visit('fields', depth + 1, budget)
        yield budget.token(b':')
        keys = ('values',) if type(value) in (i.Column, r.FeatureColumn) else ('value',) if type(value) is s.Parameter else ()
        yield from _object(fields, depth + 1, budget, keys)
        yield budget.token(b',')
        yield from _visit('type', depth + 1, budget)
        yield budget.token(b':')
        yield from _visit(tag, depth + 1, budget)
        yield budget.token(b'}')
        return
    budget.node()
    if value is None: yield budget.token(b'null')
    elif type(value) is bool: yield budget.token(b'true' if value else b'false')
    elif type(value) is int:
        m.require(abs(value) < 10**38)
        yield budget.token(str(value).encode('ascii'))
    elif type(value) is str: yield budget.token(_string(value, payload))
    elif type(value) in (i.DataKind, i.DType, r.Status, r.Reason, r.ValueType):
        assert isinstance(value, (i.DataKind, i.DType, r.Status, r.Reason, r.ValueType))
        yield budget.token(_string(value.value, False))
    else:
        m.require(type(value) is tuple)
        assert isinstance(value, tuple)
        m.require(len(value) <= MAX_SEQUENCE, 'limit_exceeded')
        m.require(depth < MAX_CONTENT_DEPTH, 'limit_exceeded')
        yield budget.token(b'[')
        for n, child in enumerate(value):
            if n: yield budget.token(b',')
            yield from _visit(child, depth + 1, budget, payload)
        yield budget.token(b']')


def _domain(value: object) -> str:
    m.require(contracts.__version__ == _CONTRACTS_VERSION, 'unsupported_version')
    if type(value) is i.CanonicalBatch: return 'canonical_batch'
    if type(value) is r.FeatureResult: return 'feature_result'
    if type(value) is s.ConfigSpec: return 'configuration'
    raise m.EvidenceError()


def _tokens(value: Root, budget: _Budget) -> Iterator[bytes]:
    domain = _domain(value)
    yield from _object((('algorithm', 'sha256'), ('canonicalization', 'typed-json-v1'),
        ('contracts_version', _CONTRACTS_VERSION), ('domain', domain), ('project', 'equity-features'),
        ('schema_version', '1'), ('value', value)), 0, budget)


def _validate(value: Root, budget: _Budget | None = None) -> None:
    for _ in _tokens(value, budget if budget is not None else _Budget()):
        pass


def content_chunks(value: Root) -> Iterator[bytes]:
    """Prevalidate the entire immutable graph before exposing any encoded prefix."""
    _validate(value)
    pending = bytearray()
    for token in _tokens(value, _Budget()):
        if len(pending) + len(token) > 65536:
            yield bytes(pending)
            pending.clear()
        pending.extend(token)
    if pending: yield bytes(pending)


def canonical_content(value: Root) -> bytes:
    """Materialize bounded bytes; the final immutable conversion copies the buffer."""
    data = bytearray()
    for chunk in content_chunks(value): data.extend(chunk)
    return bytes(data)


def _fingerprint(value: Root) -> m.ContentFingerprint:
    digest = hashlib.sha256()
    size = 0
    for chunk in content_chunks(value):
        digest.update(chunk); size += len(chunk)
    return m.ContentFingerprint(_domain(value), digest.hexdigest(), size)


def fingerprint_batch(value: i.CanonicalBatch) -> m.ContentFingerprint:
    m.require(type(value) is i.CanonicalBatch)
    return _fingerprint(value)


def fingerprint_result(value: r.FeatureResult) -> m.ContentFingerprint:
    m.require(type(value) is r.FeatureResult)
    return _fingerprint(value)


def fingerprint_config(value: s.ConfigSpec) -> m.ContentFingerprint:
    m.require(type(value) is s.ConfigSpec)
    return _fingerprint(value)


def verify_content(reference: m.ContentFingerprint, value: Root) -> bool:
    m.require(type(reference) is m.ContentFingerprint)
    return reference == _fingerprint(value)


def make_content_receipt(result: r.FeatureResult, configuration: s.ConfigSpec,
        inputs: tuple[tuple[str, i.CanonicalBatch], ...], environment: m.EnvironmentDeclaration,
        execution: m.ExecutionClaim, evidence: m.EvidenceDisclosure) -> m.ExecutionReceipt:
    """Bind actual supplied content. No claim that these inputs caused execution."""
    m.require(type(result) is r.FeatureResult and type(configuration) is s.ConfigSpec)
    m.require(type(inputs) is tuple)
    m.require(len(inputs) <= 64, 'limit_exceeded')
    for pair in inputs:
        m.require(type(pair) is tuple and len(pair) == 2)
        m.label(pair[0]); m.require(type(pair[1]) is i.CanonicalBatch)
    m.require(len({pair[0] for pair in inputs}) == len(inputs), 'duplicate')
    # Budget all roots before any hash or full configuration digest projection.
    aggregate = _Budget()
    _validate(configuration, aggregate)
    for _, batch in inputs: _validate(batch, aggregate)
    _validate(result, aggregate)
    meta = result.metadata
    m.require(meta.namespace == configuration.session.namespace and meta.session_id == configuration.session.session_id
        and meta.availability == configuration.availability and meta.config_digest == configuration.digest, 'inconsistent_binding')
    expected = tuple(sorted((x.role, x.kind, x.metadata) for x in meta.inputs))
    actual = tuple(sorted((role, batch.kind, batch.metadata) for role, batch in inputs))
    m.require(actual == expected, 'inconsistent_binding')
    return m.make_receipt(result, configuration=fingerprint_config(configuration),
        inputs=tuple(m.InputFingerprint(role, batch.metadata.source.input_id, fingerprint_batch(batch)) for role, batch in inputs),
        output=fingerprint_result(result), formulas=tuple(m.FormulaBinding(c.feature_id, c.algorithm_version) for c in result.values),
        environment=environment, execution=execution, evidence=evidence)


def verify_receipt_content(receipt: m.ExecutionReceipt, configuration: s.ConfigSpec,
        inputs: tuple[tuple[str, i.CanonicalBatch], ...], result: r.FeatureResult) -> bool:
    m.require(type(receipt) is m.ExecutionReceipt)
    try:
        expected = make_content_receipt(result, configuration, inputs, receipt.environment, receipt.execution, receipt.evidence)
    except m.EvidenceError as error:
        if error.code == 'inconsistent_binding': return False
        raise
    return receipt == expected
