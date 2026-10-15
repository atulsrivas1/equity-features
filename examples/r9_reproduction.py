"""Caller-owned synthetic R9 reproduction; installed public APIs only."""
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage,
    DataKind, EntityKey, InputScope, Parameter, PriceUnit, SessionSpec, SourceBinding, WindowSpec,
)
from equity_feature_evidence import (
    EnvironmentDeclaration, EvidenceDisclosure, ExecutionClaim, PackageVersion,
    canonical_content, make_content_receipt,
)
from equity_feature_bundles import PublicationDeclaration, read_bundle, write_bundle
from equity_feature_bundles.replay import replay_bundle
from equity_feature_explanations import explain_result, encode_explanation

ENTITY = EntityKey('A', 'S')
PUBLICATION = PublicationDeclaration('synthetic', 'Caller-created synthetic example', 'caller_owned')
ENVIRONMENT = EnvironmentDeclaration('CPython', '3.12', 'caller-declared', (
    PackageVersion('equity-feature-contracts', '0.0.4a4'), PackageVersion('equity-features', '0.0.4a4')))


def sample(*, future: bool = False) -> tuple[ConfigSpec, CanonicalBatch]:
    config = ConfigSpec('r9-demo', 'v1', (Parameter('eligibility_policy', 'example-v1'),),
        SessionSpec('demo', 'S', 100, 200, 'caller'), WindowSpec(1, 'S', ('P', 'S')),
        AvailabilitySpec(200, 210, 210), price_unit=PriceUnit(0, 'USD'))
    batch = CanonicalBatch(DataKind.TRADE, tuple(Column(name, values) for name, values in (
        ('instrument_id', ('A',) * 3), ('session_id', ('S',) * 3), ('event_ns', (110, 130, 160)),
        ('order_key', (1, 2, 3)), ('event_id', ('t1', 't2', 't3')), ('eligible', (True,) * 3),
        ('price', (100, 102, 101)), ('size', (2, 3, 5)), ('known_at_ns', (110, 130, 211 if future else 210)),
    )), BatchMetadata('demo', SourceBinding('synthetic', 'snapshot1', 'map1', 'trades1'),
        Coverage(3, 3, True), PriceUnit(0, 'USD'), scope=InputScope(100, 200, 'example-v1')))
    return config, batch


def demonstrate() -> None:
    from equity_features.session import compute_trades
    config, batch = sample()
    result = compute_trades(batch, config, entity=ENTITY)
    original = canonical_content(result)
    assert tuple(c.values[0] for c in result.values) == (3, 10, 1011, 101.1, 10 / 3)
    receipt = make_content_receipt(result, config, (('trades', batch),), ENVIRONMENT,
        ExecutionClaim(), EvidenceDisclosure('not_supplied', 0))
    summary = explain_result(result, receipt, config, entity=ENTITY, feature_id='session.trade.count', inputs=(('trades', batch),))
    assert summary.inputs[0].content_verified and not summary.source_authenticated and not summary.execution_verified
    assert encode_explanation(summary)
    raw = write_bundle(receipt, config, result, (('trades', batch),), PUBLICATION)
    bundle = read_bundle(raw)
    report = replay_bundle(bundle)
    assert report.status == 'matched' and report.result_match is True and report.calculation_count == 1
    assert not report.declared_environment_verified
    assert canonical_content(bundle.result) == original == canonical_content(result)
    decoded = explain_result(bundle.result, bundle.receipt, bundle.configuration, entity=ENTITY,
        feature_id='session.trade.count', inputs=tuple((x.role, x.batch) for x in bundle.inputs if x.batch is not None))
    assert encode_explanation(decoded) == encode_explanation(summary)
    reference = read_bundle(write_bundle(receipt, config, result, (), PUBLICATION))
    unresolved = replay_bundle(reference)
    assert unresolved.status == 'unavailable' and unresolved.calculation_count == 0
    unknown = explain_result(reference.result, reference.receipt, reference.configuration,
        entity=ENTITY, feature_id='session.trade.count')
    assert not unknown.inputs[0].content_verified
    resolved = replay_bundle(reference, (('trades', batch),))
    assert resolved.status == 'matched' and resolved.calculation_count == 1
    cancelled = replay_bundle(bundle, cancel_before_start=True)
    assert cancelled.status == 'cancelled_before_start' and cancelled.calculation_count == 0
    config, future = sample(future=True)
    unavailable = compute_trades(future, config, entity=ENTITY)
    assert all(c.values == (None,) for c in unavailable.values)
    assert all(q.status.value == 'missing_input' and tuple(r.value for r in q.reasons) == ('future_knowledge',)
        and q.expected == q.observed == 3 for q in unavailable.quality)
    receipt = make_content_receipt(unavailable, config, (('trades', future),), ENVIRONMENT,
        ExecutionClaim(), EvidenceDisclosure('not_supplied', 0))
    matched = replay_bundle(read_bundle(write_bundle(receipt, config, unavailable, (('trades', future),), PUBLICATION)))
    assert matched.status == 'matched' and matched.calculation_count == 1
    summary = explain_result(unavailable, receipt, config, entity=ENTITY, feature_id='session.trade.count', inputs=(('trades', future),))
    assert tuple(f.code for f in summary.findings) == ('global_evidence_not_supplied', 'result_unavailable')
    print('R9 synthetic full-result reproduction, explicit reference resolution and unavailable-quality fidelity passed; source, rights and original execution remain unverified.')


if __name__ == '__main__':
    demonstrate()
