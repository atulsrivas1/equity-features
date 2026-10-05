"""Synthetic centered sample volatility with explicit square-root-time scaling."""
from dataclasses import replace
from decimal import Decimal, localcontext
from equity_feature_contracts import AvailabilitySpec, ConfigSpec, Parameter, Status, WindowSpec
from equity_features.history import compute_history
from history_windows import batch, context, ids, sessions, unit

config = ConfigSpec("volatility3", "v1", (Parameter("period", 3),), sessions[-1],
                    WindowSpec(4, "S5", ids, "completed_eod"), AvailabilitySpec(60, 60, 60), price_unit=unit)
result = compute_history(batch, config, context=context, feature_ids=("history.return_volatility",))
with localcontext() as decimal_context:
    decimal_context.prec = 80
    expected = float((Decimal(476449)/Decimal(44791488)).sqrt())
assert result.values[0].values == (expected,)
assert result.quality[0].status == Status.AVAILABLE
assert result.quality[0].expected == result.quality[0].observed == 4
scaled_config = replace(config, parameters=config.parameters+(Parameter("annualization_factor", 4),))
scaled = compute_history(batch, scaled_config, context=context, feature_ids=("history.return_volatility",))
assert scaled.values[0].values == (2*expected,)
print("Centered sample variance476449/44791488, Adefault1 and explicit A4 scaling verified.")
