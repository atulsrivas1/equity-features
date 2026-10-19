"""Deliberate rejected API shapes; diagnostics are checked exactly."""
from equity_features_intraday import IntradayRun, PreparedOperand

IntradayRun('S', 'wrong-time', 10, 1)

def mutate(view: PreparedOperand) -> None:
    view.expected = 0
