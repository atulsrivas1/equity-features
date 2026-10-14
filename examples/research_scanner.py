"""Synthetic producer-to-consumer example, outside the pure scanner package."""
from dataclasses import replace

from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage, DataKind, EntityKey,
    InputScope, Parameter, PriceUnit, SessionSpec, SourceBinding, ValueType, WindowSpec,
)
from equity_features.session import compute_trades
from equity_feature_strategies import (
    Entity, FeatureRequirement, Predicate, Ranking, StrategyConfig, StrategyRequest,
    input_semantic_digest, scan,
)


def main() -> None:
    availability = AvailabilitySpec(100, 100, 100)
    config = ConfigSpec('synthetic-trades', 'v1', (Parameter('eligibility_policy', 'synthetic-v1'),),
        SessionSpec('synthetic', 'S0', 0, 100, 'supplied'), WindowSpec(1, 'S0', ('prior', 'S0')),
        availability, price_unit=PriceUnit(0, 'USD'))
    # Two supplied eligible prints: count=2, volume=3+5=8. No fetched prices or future facts.
    facts = dict(instrument_id=('A', 'A'), session_id=('S0', 'S0'), event_ns=(10, 20),
        order_key=(1, 2), event_id=('t1', 't2'), eligible=(True, True), price=(100, 102),
        size=(3, 5), known_at_ns=(10, 20))
    batch = CanonicalBatch(DataKind.TRADE,
        tuple(Column(name, values) for name, values in facts.items()),
        BatchMetadata('synthetic', SourceBinding('synthetic-fixture', 'snapshot-1', 'mapping-1', 'input-1'),
            Coverage(2, 2, True), PriceUnit(0, 'USD'), scope=InputScope(0, 100, 'synthetic-v1')))
    produced = compute_trades(batch, config, entity=EntityKey('A', 'S0'))
    ids = ('session.trade.count', 'session.trade.volume')
    # Projection is explicit caller work. Unsupported aggregate columns never enter the scanner.
    projected = replace(produced, values=tuple(c for c in produced.values if c.feature_id in ids),
        quality=tuple(q for q in produced.quality if q.feature_id in ids),
        evidence=tuple(e for e in produced.evidence if e.feature_id in ids))
    semantic = input_semantic_digest(projected)
    count = FeatureRequirement(ids[0], '1', 'v1', ValueType.INT64, 'trades', config.digest, semantic)
    volume = FeatureRequirement(ids[1], '1', 'v1', ValueType.INT64, 'shares', config.digest, semantic)
    selected = scan(StrategyRequest('synthetic', 'S0', availability, [Entity('synthetic', 'A', 'S0')],
        [projected], StrategyConfig([Predicate(count, 'ge', 2)], Ranking(volume, 'descending'), 1)))
    assert selected.rows[0].ranking_value == 8 and selected.rows[0].rank == 1
    assert selected.selected == (Entity('synthetic', 'A', 'S0'),)
    assert selected.readiness == 'complete' and selected.coverage_numerator == 1
    print('Synthetic installed producer/scanner count=2 volume=8 selected=A verified')


if __name__ == '__main__':
    main()
