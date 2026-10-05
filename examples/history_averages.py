"""Synthetic SMA/explicitly anchored EMA and exact supplied SMA comparison."""
from dataclasses import replace
from fractions import Fraction
from equity_feature_contracts import AvailabilitySpec, ConfigSpec, Parameter, WindowSpec
from equity_features.history import compute_history, compute_sma_reference
from history_windows import batch, context, ids, sessions, unit

anchored = replace(context, initialization_anchor="S0")
config = ConfigSpec("averages3", "v1", (Parameter("period", 3),), sessions[-1],
                    WindowSpec(3, "S5", ids, "completed_eod"), AvailabilitySpec(60, 60, 60), price_unit=unit)
result = compute_history(batch, config, context=anchored, feature_ids=("history.sma", "history.ema"))
assert tuple(c.values for c in result.values) == ((float(Fraction(365, 3)),), (float(Fraction(975, 8)),))
assert [(q.expected, q.observed) for q in result.quality] == [(3, 3), (6, 6)]
reference = compute_sma_reference(batch, config, context=anchored)
assert (reference.numerator, reference.denominator) == (365, 3)
assert reference.compare_price(130, unit) == 1
print("SMA3=365/3, anchored EMA3=975/8 and exact supplied SMA comparison verified.")
