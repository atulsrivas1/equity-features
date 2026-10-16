"""Typed synthetic public batch computation; no source acquisition."""
from equity_feature_continuous import (
    ContinuousConfig, ContinuousFeature, ContinuousInput, ContinuousResult, ConversionFact,
    FeedFact, Leg, MetricValue, PriceObservation, Rational, compute_basis, config_digest,
    config_from_json, list_features, require_capability, to_json,
)
from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, Coverage, IntervalSpec, PriceUnit, SourceBinding,
)

config = ContinuousConfig('synthetic:example', '1', '1', 'basis',
    IntervalSpec('window', 0, 100), AvailabilitySpec(100, 100, 100),
    99, None, 10, 10, 10, 3, 'observation_count', 'supplied_last_trade')
decoded: ContinuousConfig = config_from_json(to_json(config))
digest: str = config_digest(decoded)
observation = PriceObservation('synthetic:trade', 99, 0, 100, 99)
metric = MetricValue('cross_venue.basis', Rational(2, 4))
assert decoded == config and len(digest) == 64
assert metric.value == Rational(1, 2) and observation.event_ns == 99

continuous = Leg('c', 'c-feed', 'c-product', 'supplied-underlying', 'unit', 'last_trade',
    SourceBinding('synthetic', 'c-snapshot', 'map1', 'c-input'), PriceUnit(0, 'USD'),
    AdjustmentSpec('raw', 'raw-v1', 'none', 'none'), IntervalSpec('c-scope', 90, 100),
    Coverage(1, 1, True), 100, (PriceObservation('c1', 99, 0, 110, 99),))
reference = Leg('r', 'r-feed', 'r-product', 'supplied-underlying', 'unit', 'last_trade',
    SourceBinding('synthetic', 'r-snapshot', 'map1', 'r-input'), PriceUnit(0, 'USD'),
    AdjustmentSpec('raw', 'raw-v1', 'none', 'none'), IntervalSpec('r-scope', 90, 100),
    Coverage(1, 1, True), 100, (PriceObservation('r1', 98, 0, 100, 98),))
facts = (FeedFact('c-live', '1', 'c-feed', 'c-product', IntervalSpec('c-live', 90, 100), 'live', 80),
         FeedFact('r-live', '1', 'r-feed', 'r-product', IntervalSpec('r-live', 90, 100), 'live', 80))
mapping = ConversionFact('same-quantity', '1', 'c', 'r', 'supplied-underlying', 'unit', 'unit',
    'USD', IntervalSpec('mapping', 90, 100), 1, 1, 80)
supplied = ContinuousInput(config, continuous, reference, facts, (mapping,))
result: ContinuousResult = compute_basis(supplied)
metadata: tuple[ContinuousFeature, ...] = list_features()
require_capability('cross_venue.basis', 'batch')
assert result.status == 'available' and result.available_at_ns == 100
assert tuple(item.value for item in result.metrics) == (Rational(10, 1), Rational(1, 10))
assert len(metadata) == 6 and all(item.batch and not item.update for item in metadata)
