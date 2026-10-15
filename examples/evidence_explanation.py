"""Actual synthetic producer composed with pure bounded explanation APIs."""
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage,
    DataKind, EntityKey, InputScope, Parameter, PriceUnit, SessionSpec, SourceBinding, WindowSpec,
)
from equity_features.session import compute_trades
from equity_feature_evidence import (
    EnvironmentDeclaration, EvidenceDisclosure, ExecutionClaim, PackageVersion,
    make_content_receipt,
)
from equity_feature_explanations import explain_result, encode_explanation, ExplanationFinding

config = ConfigSpec('explanation-demo', 'v1', (Parameter('eligibility_policy', 'example-v1'),),
    SessionSpec('demo', 'S', 100, 200, 'caller'), WindowSpec(1, 'S', ('P', 'S')),
    AvailabilitySpec(200, 210, 210), price_unit=PriceUnit(0, 'USD'))
batch = CanonicalBatch(DataKind.TRADE, tuple(Column(name, values) for name, values in (
    ('instrument_id', ('A',) * 3), ('session_id', ('S',) * 3), ('event_ns', (110, 130, 160)),
    ('order_key', (1, 2, 3)), ('event_id', ('t1', 't2', 't3')), ('eligible', (True,) * 3),
    ('price', (100, 102, 101)), ('size', (2, 3, 5)), ('known_at_ns', (110, 130, 210)),
)), BatchMetadata('demo', SourceBinding('synthetic', 'snapshot1', 'map1', 'trades1'),
    Coverage(3, 3, True), PriceUnit(0, 'USD'), scope=InputScope(100, 200, 'example-v1')))
entity = EntityKey('A', 'S')
result = compute_trades(batch, config, entity=entity)
before = result
assert tuple(column.values[0] for column in result.values) == (3, 10, 1011, 101.1, 10 / 3)
receipt = make_content_receipt(result, config, (('trades', batch),),
    EnvironmentDeclaration('CPython', '3.12', 'caller-declared', (
        PackageVersion('equity-feature-contracts', '0.0.4a4'), PackageVersion('equity-features', '0.0.4a4'))),
    ExecutionClaim(), EvidenceDisclosure('not_supplied', 0))
summary = explain_result(result, receipt, config, entity=entity, feature_id='session.trade.count',
    inputs=(('trades', batch),), evidence_limit=0)
assert summary.quality.expected == summary.quality.observed == 3
assert summary.formula == 'n=len(T)' and summary.inputs[0].content_verified
assert summary.findings == (ExplanationFinding('global_evidence_not_supplied'),)
assert summary.omitted_retained_count == 0
assert not summary.source_authenticated and not summary.execution_verified
assert len(encode_explanation(summary)) <= 262144 and result == before
unavailable = explain_result(result, receipt, config, entity=entity, feature_id='session.trade.count')
assert not unavailable.inputs[0].content_verified
assert unavailable.findings[0] == ExplanationFinding('input_content_unverified', 'trades')
print('Actual five-output parity, receipt/context/content binding and bounded explanation passed; reported facts are not source or original-execution proof.')
