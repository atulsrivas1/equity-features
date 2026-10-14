"""Synthetic actual producer/scanner prefix with separate future label/as-of facts."""
from dataclasses import replace
from equity_feature_contracts import (AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec,
    Coverage, DataKind, EntityKey, InputScope, Parameter, PriceUnit, SessionSpec, SourceBinding, ValueType, WindowSpec)
from equity_features.session import compute_trades
from equity_feature_strategies import (Entity as SignalEntity, FeatureRequirement, Predicate, Ranking,
    StrategyConfig, StrategyError, StrategyRequest, encode as signal_encode, input_semantic_digest, scan)
from equity_feature_labels import (BasisWitness, Entity, LabelConfig, LabelOrigin, LabelRequest,
    LabelResult, PriceObservation, evaluate_label)


def signal() -> StrategyRequest:
    availability = AvailabilitySpec(100, 100, 100)
    config = ConfigSpec('synthetic-trades', 'v1', (Parameter('eligibility_policy', 'synthetic-v1'),),
        SessionSpec('synthetic', 'S0', 0, 100, 'supplied'), WindowSpec(1, 'S0', ('prior', 'S0')),
        availability, price_unit=PriceUnit(0, 'USD'))
    facts = dict(instrument_id=('A', 'A'), session_id=('S0', 'S0'), event_ns=(10, 20),
        order_key=(1, 2), event_id=('t1', 't2'), eligible=(True, True), price=(100, 102),
        size=(3, 5), known_at_ns=(10, 20))
    batch = CanonicalBatch(DataKind.TRADE, tuple(Column(n, v) for n, v in facts.items()),
        BatchMetadata('synthetic', SourceBinding('synthetic-fixture', 'snapshot-1', 'mapping-1', 'input-1'),
            Coverage(2, 2, True), PriceUnit(0, 'USD'), scope=InputScope(0, 100, 'synthetic-v1')))
    produced = compute_trades(batch, config, entity=EntityKey('A', 'S0'))
    ids = ('session.trade.count', 'session.trade.volume')
    projected = replace(produced, values=tuple(c for c in produced.values if c.feature_id in ids),
        quality=tuple(q for q in produced.quality if q.feature_id in ids),
        evidence=tuple(e for e in produced.evidence if e.feature_id in ids))
    semantic = input_semantic_digest(projected)
    count = FeatureRequirement(ids[0], '1', 'v1', ValueType.INT64, 'trades', config.digest, semantic)
    volume = FeatureRequirement(ids[1], '1', 'v1', ValueType.INT64, 'shares', config.digest, semantic)
    return StrategyRequest('synthetic', 'S0', availability, [SignalEntity('synthetic', 'A', 'S0')],
        [projected], StrategyConfig([Predicate(count, 'ge', 2)], Ranking(volume, 'descending'), 1))


def as_of(origin: LabelOrigin, selected: LabelRequest, output: LabelResult, join: AvailabilitySpec) -> bool:
    """Explicit application selection, outside both pure libraries."""
    signal_time = origin.signal_availability
    return (join.mode == 'known_at' and join.reconstruction_reason is None and
        max(join.market_cutoff_ns, join.knowledge_cutoff_ns) <= join.evaluation_ns and
        signal_time.market_cutoff_ns <= join.market_cutoff_ns and
        signal_time.knowledge_cutoff_ns <= join.knowledge_cutoff_ns and signal_time.evaluation_ns <= join.evaluation_ns and
        selected.origin == origin and output.entity == origin.entity and
        output.origin_digest == origin.identity_digest and output.request_digest == selected.identity_digest and
        output == evaluate_label(selected) and output.status == 'mature' and
        output.horizon_endpoint_ns <= join.market_cutoff_ns and output.label_known_at_ns is not None and
        output.label_known_at_ns <= join.knowledge_cutoff_ns)


def main() -> None:
    prefix = signal()
    scanned = scan(prefix)
    assert scanned.selected == (SignalEntity('synthetic', 'A', 'S0'),)
    assert scanned.rows[0].ranking_value == 8
    signal_bytes = signal_encode(scanned)
    origin = LabelOrigin(Entity('synthetic', 'A', 'S0'), prefix.identity_digest, scanned.identity_digest,
        prefix.availability, 20, 102.0, 20, 'origin-1', BasisWitness('raw', 'raw-v1', 'none', 'none', 'basis-1', 0, 0))
    basis = BasisWitness('raw', 'raw-v1', 'none', 'none', 'path-basis-1', 0, 100)
    request = LabelRequest(origin, AvailabilitySpec(110, 110, 110), (
        PriceObservation(20, 102.0, 20, 'path-1', origin.identity_digest, basis),
        PriceObservation(110, 112.2, 110, 'path-1', origin.identity_digest, basis)), LabelConfig(90))
    mature = evaluate_label(request)
    assert mature.status == 'mature' and abs(mature.value - 0.1) < 1e-12
    adjusted_basis = BasisWitness('split', 'split-v1', 'action-1', 'anchor-1', 'basis-2', 105, 110)
    adjusted = replace(request, observations=(
        PriceObservation(20, 51.0, 110, 'path-2', origin.identity_digest, adjusted_basis),
        PriceObservation(110, 51.0, 110, 'path-2', origin.identity_digest, adjusted_basis)))
    future = replace(request, availability=AvailabilitySpec(109, 110, 110))
    unknown = replace(request, observations=(request.observations[0], replace(request.observations[1], known_at_ns=None)))
    outputs = [evaluate_label(r) for r in (request, adjusted, future, unknown)]
    assert [o.status for o in outputs] == ['mature', 'mature', 'pending', 'pending']
    assert outputs[1].value == 0.0 and origin.anchor_price == 102.0
    for r in (request, adjusted, future, unknown):
        assert r.origin == origin and r.origin.identity_digest == origin.identity_digest
        assert signal_encode(scan(prefix)) == signal_bytes
        assert signal_encode(scan(signal())) == signal_bytes
        assert scan(prefix).identity_digest == scanned.identity_digest
        try:
            replace(prefix, feature_results=(evaluate_label(r),))
        except StrategyError as error:
            assert error.code == 'invalid_schema'
        else:
            raise AssertionError('label admitted as signal feature')
    # Explicitly exercise the applicable predicate-order identity requirement.
    first = prefix.config.predicates[0]
    second = replace(first, operator='gt', threshold=1)
    ordered = replace(prefix, config=replace(prefix.config, predicates=(first, second)))
    reversed_rules = replace(ordered, config=replace(ordered.config, predicates=(second, first)))
    assert ordered.config.identity_digest != reversed_rules.config.identity_digest
    assert ordered.identity_digest != reversed_rules.identity_digest
    assert scan(ordered).selected == scan(reversed_rules).selected
    assert not as_of(origin, request, mature, AvailabilitySpec(110, 109, 110))
    assert as_of(origin, request, mature, AvailabilitySpec(110, 110, 110))
    assert not as_of(origin, request, mature, AvailabilitySpec(109, 110, 110))
    assert not as_of(origin, adjusted, mature, AvailabilitySpec(110, 110, 110))
    assert not as_of(origin, future, outputs[2], AvailabilitySpec(110, 110, 110))
    assert not as_of(origin, unknown, outputs[3], AvailabilitySpec(110, 110, 110))
    assert not as_of(replace(origin, anchor_source_revision='other'), request, mature, AvailabilitySpec(110, 110, 110))
    print('Actual core prefix count=2 volume=8; future-label invariance, rejection and as-of joins verified')


if __name__ == '__main__':
    main()
