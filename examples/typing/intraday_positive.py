"""Installed typed discovery/context/immutable preparation inspection."""
from equity_features_intraday import IntradayFeature, PreparedOperand, describe_intraday

def inspect(view: PreparedOperand) -> int:
    return view.expected

entries: tuple[IntradayFeature, ...] = describe_intraday()
assert len(entries) == 8
