"""Public typed continuous contracts; no computation or source acquisition."""
from equity_feature_continuous import (
    ContinuousConfig, MetricValue, PriceObservation, Rational, config_digest,
    config_from_json, to_json,
)
from equity_feature_contracts import AvailabilitySpec, IntervalSpec

config = ContinuousConfig('synthetic:example', '1', '1', 'basis',
    IntervalSpec('window', 0, 100), AvailabilitySpec(100, 100, 100),
    99, None, 10, 10, 10, 3, 'observation_count', 'supplied_last_trade')
decoded: ContinuousConfig = config_from_json(to_json(config))
digest: str = config_digest(decoded)
observation = PriceObservation('synthetic:trade', 99, 0, 100, 99)
metric = MetricValue('cross_venue.basis', Rational(2, 4))
assert decoded == config and len(digest) == 64
assert metric.value == Rational(1, 2) and observation.event_ns == 99
