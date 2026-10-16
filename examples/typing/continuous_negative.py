"""Exactly five deliberately ill-typed public calls; never a runnable example."""
from equity_feature_continuous import (
    ContinuousConfig, ContinuousResult, MetricValue, PriceObservation,
    config_from_json,
)
from equity_feature_contracts import FeatureResult

def consume_old(value: FeatureResult) -> None:
    pass

def invalid(config: ContinuousConfig, result: ContinuousResult) -> None:
    PriceObservation('synthetic:trade', '99', 0, 100, 99)
    MetricValue('cross_venue.basis', 1)
    config_from_json('{}')
    consume_old(result)
    config.operation = 1
