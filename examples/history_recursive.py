"""Synthetic explicitly anchored Wilder RSI/ATR with independent membership."""
from dataclasses import replace
from fractions import Fraction
import math
from equity_feature_contracts import AvailabilitySpec, ConfigSpec, Parameter, Status, WindowSpec
from equity_features.history import compute_history
from history_windows import batch, context, ids, sessions, unit

for feature, anchor, count, expected in (("history.rsi", "S0", 4, Fraction(4700, 57)),
                                         ("history.atr", "S1", 3, Fraction(122, 9))):
    anchored = replace(context, initialization_anchor=anchor)
    config = ConfigSpec(feature, "v1", (Parameter("period", 3),), sessions[-1],
                        WindowSpec(count, "S5", ids, "completed_eod"), AvailabilitySpec(60, 60, 60), price_unit=unit)
    result = compute_history(batch, config, context=anchored, feature_ids=(feature,))
    value = result.values[0].values[0]
    assert type(value) is float and math.isclose(value, float(expected), rel_tol=1e-12, abs_tol=1e-12)
    assert result.quality[0].status == Status.AVAILABLE
    assert result.quality[0].expected == result.quality[0].observed == 6
print("Anchored RSI3=4700/57 and ATR3=122/9 with required previous close verified.")
