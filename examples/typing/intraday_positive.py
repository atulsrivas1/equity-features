"""Installed typed discovery/context/immutable preparation inspection."""
from equity_features_intraday import IntradayFeature, PreparedOperand, describe_intraday
from equity_feature_contracts import CanonicalBatch, ConfigSpec, FeatureResult
from equity_features_intraday import IntradayContext, compute_intraday

def inspect(view: PreparedOperand) -> int:
    return view.expected

entries: tuple[IntradayFeature, ...] = describe_intraday()
assert len(entries) == 8

def snapshot(batches: tuple[CanonicalBatch, ...] | None, context: IntradayContext,
             config: ConfigSpec) -> FeatureResult:
    return compute_intraday(batches, context, config, features=('intraday.ema','intraday.band_middle','intraday.band_position'))
