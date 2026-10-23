# EF3 daily log volatility

Use `DailyGrid`, `build_log_volatility_config`, `decode_log_volatility_config`, `compute_log_volatility` (or the closed `compute_ef3`), `ef3_definitions` and `require_ef3_capability` from `equity_features.ef3`. Config identity is `ef3.daily_log_volatility`, algorithm `ef3-daily-log-vol-v1`, schema `1`, policy `ef3-dlv1`. The output `history.log_return_volatility` is a distinct id from the simple-return `history.return_volatility`, which is unchanged.

```python
from equity_features.ef3 import LOG_VOL_POLICY, build_log_volatility_config, compute_log_volatility

config = build_log_volatility_config(grid, policy_version=LOG_VOL_POLICY, period=20, annualization_factor=252,
                                     availability=availability, adjustment=adjustment, price_unit=price_unit,
                                     evidence_limit=2)
result = compute_log_volatility((daily_bars,), grid, config, features=("history.log_return_volatility",))
```

Parameters are exactly `policy_version` (`ef3-dlv1`), `period` N (2..4096), `annualization_factor` A (1..2^63-1, caller supplied, 1 is unannualized, no default; the contract does not claim A is sessions per year) and `evidence_limit` (0..10000), plus the grid identity (`grid_schema`, `grid_sha256`). `batches` is the fixed single nullable role `daily`: a close-only BAR batch on the governed daily grid as described for [relative statistics](EF3_RELATIVE_STATS.md). The window is strict: N+1 READY consecutive closes ending at the target; any non-READY slot makes the value unavailable (no shrinking or bridging) and fewer than N+1 governed slots up to the target adds `insufficient_history`.

`vol = sqrt(A * s2)` with `s2` the centered sample variance (denominator N-1) of `ln(C_i / C_{i-1})`, evaluated in Decimal120 from the exact close ratio with a two-pass variance. When all N close ratios are equal (decided by integer cross-multiplication) the value is exactly `+0.0`; every other value is published unsnapped. The result is one float64 with unit `fraction`, backend `python-exact`, input binding `daily`; expected is N+1 and observed the READY closes in the window; witnesses are the bar of slot `t-N` then of `t`. Refusals mirror relative statistics (`INVALID_CONFIG`, `INCOMPATIBLE_VERSION`, `INCONSISTENT_IDENTITY`, `INVALID_UNIT`, `UNSUPPORTED_ADJUSTMENT`, `INVALID_ORDER`, `DUPLICATE`, `INVALID_SCHEMA`, `UNKNOWN_FEATURE`, `UNSUPPORTED_CAPABILITY`). See [implementation and open points](../ef3/RELATIVE_RV_IMPLEMENTATION.md).
