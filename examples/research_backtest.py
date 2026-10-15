"""Finite chronological research targets; no portfolio, fills or alpha claim."""
from dataclasses import replace
import math
from equity_feature_contracts import (AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec,
    Coverage, DataKind, EntityKey, FeatureColumn, InputScope, Parameter, PriceUnit, QualityRow,
    SessionSpec, SourceBinding, Status, ValueType, WindowSpec)
from equity_features.session import compute_trades
from equity_feature_strategies import (Entity as SignalEntity, FeatureRequirement, Predicate, Ranking,
    StrategyConfig, StrategyError, StrategyRequest, encode as signal_encode, input_semantic_digest, scan)
from equity_feature_labels import (BasisWitness, Entity, LabelConfig, LabelError, LabelOrigin, LabelRequest,
    LabelResult, PriceObservation, encode as label_encode, evaluate_label)


def signal() -> StrategyRequest:
    """Use the actual core producer; missing C is an explicit universe member."""
    availability = AvailabilitySpec(100, 100, 100)
    config = ConfigSpec('synthetic-trades', 'v1', (Parameter('eligibility_policy', 'synthetic-v1'),),
        SessionSpec('synthetic', 'S0', 0, 100, 'supplied'), WindowSpec(1, 'S0', ('prior', 'S0')),
        availability, price_unit=PriceUnit(0, 'USD'))
    results = []
    for instrument, price in (('A', 100), ('B', 200)):
        facts = dict(instrument_id=(instrument, instrument), session_id=('S0', 'S0'), event_ns=(10, 20),
            order_key=(1, 2), event_id=(instrument + '-t1', instrument + '-t2'), eligible=(True, True),
            price=(price, price), size=(3, 5), known_at_ns=(10, 20))
        batch = CanonicalBatch(DataKind.TRADE, tuple(Column(n, v) for n, v in facts.items()),
            BatchMetadata('synthetic', SourceBinding('synthetic-fixture', 'snapshot-' + instrument, 'mapping-1', 'input-' + instrument),
                Coverage(2, 2, True), PriceUnit(0, 'USD'), scope=InputScope(0, 100, 'synthetic-v1')))
        produced = compute_trades(batch, config, entity=EntityKey(instrument, 'S0'))
        ids = ('session.trade.count', 'session.trade.volume')
        results.append(replace(produced, values=tuple(c for c in produced.values if c.feature_id in ids),
            quality=tuple(q for q in produced.quality if q.feature_id in ids),
            evidence=tuple(e for e in produced.evidence if e.feature_id in ids)))
    semantic = input_semantic_digest(results[0])
    assert semantic == input_semantic_digest(results[1])
    count = FeatureRequirement('session.trade.count', '1', 'v1', ValueType.INT64, 'trades', config.digest, semantic)
    volume = FeatureRequirement('session.trade.volume', '1', 'v1', ValueType.INT64, 'shares', config.digest, semantic)
    return StrategyRequest('synthetic', 'S0', availability, [SignalEntity('synthetic', i, 'S0') for i in ('C', 'B', 'A')],
        list(reversed(results)), StrategyConfig([Predicate(count, 'ge', 2)], Ranking(volume, 'descending'), 2))


def as_of(origin: LabelOrigin, selected: LabelRequest, output: LabelResult, join: AvailabilitySpec) -> bool:
    """Application joins an explicitly selected immutable revision, never latest-by-guess."""
    signal_time = origin.signal_availability
    return (join.mode == 'known_at' and join.reconstruction_reason is None and
        max(join.market_cutoff_ns, join.knowledge_cutoff_ns) <= join.evaluation_ns and
        signal_time.market_cutoff_ns <= join.market_cutoff_ns and
        signal_time.knowledge_cutoff_ns <= join.knowledge_cutoff_ns and signal_time.evaluation_ns <= join.evaluation_ns and
        selected.origin == origin and output.entity == origin.entity and output.origin_digest == origin.identity_digest and
        output.request_digest == selected.identity_digest and output == evaluate_label(selected) and
        output.status == 'mature' and output.horizon_endpoint_ns <= join.market_cutoff_ns and
        output.label_known_at_ns is not None and output.label_known_at_ns <= join.knowledge_cutoff_ns)


def rejected(code, call, kind):
    try:
        call()
    except kind as error:
        assert error.code == code
    else:
        raise AssertionError('invalid research input admitted')


def main() -> None:
    prefix = signal()
    result = scan(prefix)
    a, b, c = (SignalEntity('synthetic', i, 'S0') for i in ('A', 'B', 'C'))
    assert result.ranked == result.selected == (a, b)
    assert (result.expected, result.eligible, result.matching, result.coverage_numerator,
        result.coverage_denominator, result.readiness) == (3, 2, 2, 2, 3, 'incomplete')
    assert tuple(r.entity for r in result.rows) == (a, b, c)
    for row, rank in zip(result.rows[:2], (1, 2)):
        assert (row.status, row.ranking_value, row.ranking_reason, row.rank) == ('matching', 8, None, rank)
        assert len(row.predicate_dispositions) == 1
        disposition = row.predicate_dispositions[0]
        assert (disposition.predicate_index, disposition.feature_id, disposition.state, disposition.reason) == (
            0, 'session.trade.count', 'pass', None)
    absent = result.rows[2]
    assert (absent.status, absent.ranking_value, absent.ranking_reason, absent.rank) == ('unavailable', None, 'absent_entity', None)
    assert len(absent.predicate_dispositions) == 1
    assert (absent.predicate_dispositions[0].state, absent.predicate_dispositions[0].reason) == ('unavailable', 'absent_entity')
    frozen_signal = signal_encode(result)
    origins, requests = {}, {}
    for instrument, anchor, end in (('A', 100.0, 110.0), ('B', 200.0, 180.0)):
        origin = LabelOrigin(Entity('synthetic', instrument, 'S0'), prefix.identity_digest, result.identity_digest,
            prefix.availability, 20, anchor, 20, 'origin-' + instrument,
            BasisWitness('raw', 'raw-v1', 'none', 'none', 'origin-basis-1', 0, 0))
        basis = BasisWitness('raw', 'raw-v1', 'none', 'none', 'path-basis-1', 0, 100)
        observations = (PriceObservation(20, anchor, 20, 'path-' + instrument + '-1', origin.identity_digest, basis),
            PriceObservation(110, end, 110, 'path-' + instrument + '-1', origin.identity_digest, basis))
        origins[instrument] = origin
        requests[instrument] = LabelRequest(origin, AvailabilitySpec(110, 110, 110), observations, LabelConfig(90))
    first_a, first_b = requests['A'], requests['B']
    mature_a, mature_b = evaluate_label(first_a), evaluate_label(first_b)
    assert math.isclose(mature_a.value, 1 / 10, rel_tol=1e-12, abs_tol=1e-12)
    assert math.isclose(mature_b.value, -1 / 10, rel_tol=1e-12, abs_tol=1e-12)
    assert mature_a.label_known_at_ns == mature_b.label_known_at_ns == 110
    pending = replace(first_a, availability=AvailabilitySpec(100, 100, 100))
    before_horizon = replace(first_a, availability=AvailabilitySpec(109, 109, 109))
    missing = replace(first_b, observations=first_b.observations[:1])
    unknown = replace(first_a, observations=(first_a.observations[0], replace(first_a.observations[1], known_at_ns=None)))
    revised_rows = tuple(replace(r, source_revision='path-A-2',
        price=120.0 if r.event_ns == 110 else r.price, known_at_ns=120 if r.event_ns == 110 else r.known_at_ns)
        for r in first_a.observations)
    revised_pending = replace(first_a, observations=revised_rows)
    revised = replace(revised_pending, availability=AvailabilitySpec(120, 120, 120))
    split = BasisWitness('split', 'split-v1', 'action-1', 'split-anchor-1', 'split-basis-1', 105, 120)
    adjusted = replace(revised, observations=(PriceObservation(20, 50.0, 120, 'path-A-3', origins['A'].identity_digest, split),
        PriceObservation(110, 60.0, 120, 'path-A-3', origins['A'].identity_digest, split)))
    for req, state, reasons in ((pending, 'pending', ('horizon_not_elapsed',)),
        (before_horizon, 'pending', ('horizon_not_elapsed',)), (missing, 'incomplete', ('missing_horizon_endpoint',)),
        (unknown, 'pending', ('unknown_availability',)), (revised_pending, 'pending', ('future_knowledge',))):
        out = evaluate_label(req)
        assert (out.status, out.reasons, out.value, out.label_known_at_ns) == (state, reasons, None, None)
        assert not as_of(req.origin, req, out, AvailabilitySpec(120, 120, 120))
    revised_out, adjusted_out = evaluate_label(revised), evaluate_label(adjusted)
    for out in (revised_out, adjusted_out):
        assert out.status == 'mature' and out.label_known_at_ns == 120
        assert math.isclose(out.value, 1 / 5, rel_tol=1e-12, abs_tol=1e-12)
    history = {r.identity_digest: label_encode(evaluate_label(r)) for r in (first_a, first_b, revised, adjusted)}
    assert len(history) == 4 and history[first_a.identity_digest] == label_encode(mature_a)
    assert origins['A'].anchor_price == 100.0 and revised.origin == adjusted.origin == first_a.origin
    for req in (first_a, first_b, pending, before_horizon, missing, unknown, revised_pending, revised, adjusted):
        assert signal_encode(scan(prefix)) == frozen_signal
        assert signal_encode(scan(signal())) == frozen_signal
        assert scan(prefix).identity_digest == result.identity_digest
        rejected('invalid_schema', lambda: replace(prefix, feature_results=(evaluate_label(req),)), StrategyError)
    join109, join110, join120 = (AvailabilitySpec(t, t, t) for t in (109, 110, 120))
    assert not as_of(origins['A'], first_a, mature_a, join109)
    assert not as_of(origins['A'], first_a, mature_a, AvailabilitySpec(110, 109, 110))
    assert as_of(origins['A'], first_a, mature_a, join110)
    assert as_of(origins['B'], first_b, mature_b, join110)
    assert not as_of(origins['A'], revised, revised_out, join110)
    assert as_of(origins['A'], revised, revised_out, join120)
    assert as_of(origins['A'], first_a, mature_a, join120)  # Explicit older revision remains selectable.
    assert not as_of(origins['A'], revised, mature_a, join120)
    assert not as_of(origins['A'], replace(first_a, config=LabelConfig(91)), mature_a, join120)
    assert not as_of(replace(origins['A'], anchor_source_revision='other'), first_a, mature_a, join120)
    rejected('incompatible_version', lambda: replace(prefix.config, schema_version='strategy-config:2'), StrategyError)
    rejected('incompatible_version', lambda: LabelConfig(90, algorithm_version='forward-price-return:v2'), LabelError)
    wrong = replace(prefix.config.predicates[0], requirement=replace(prefix.config.predicates[0].requirement,
        expected_result_config_digest='0' * 64))
    rejected('inconsistent_identity', lambda: replace(prefix, config=replace(prefix.config, predicates=(wrong,))), StrategyError)
    rejected('inconsistent_identity', lambda: replace(first_a, observations=(first_a.observations[0],
        replace(first_a.observations[1], basis=split))), LabelError)
    forged = replace(prefix.feature_results[0], values=(FeatureColumn('label.forward.return', 'v1', ValueType.FLOAT64,
        'fraction', (EntityKey('A', 'S0'),), (0.1,)),),
        quality=(QualityRow(EntityKey('A', 'S0'), 'label.forward.return', Status.AVAILABLE, 1, 1, ()),), evidence=())
    rejected('unsupported_feature', lambda: replace(prefix, feature_results=(forged,)), StrategyError)
    print('Chronological synthetic targets: ranked/selected A,B; coverage2/3; returns+1/10,-1/10; revision+1/5; causal joins verified')


if __name__ == '__main__':
    main()
