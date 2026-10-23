# EF2 momentum and trend

Use `build_momentum_config`, `decode_momentum_config`, `compute_momentum`, `describe_momentum`, `momentum_catalog_digest` and `require_momentum_capability` from `equity_features_intraday`. The context is the unchanged R17 `IntradayContext` and must be `reset` mode (carry is out of v1). Config identity is `intraday.momentum.v1`, algorithm `intraday-momentum-v1`, schema `1`, convention group `ef2-conv1`.

```python
from equity_features_intraday import build_momentum_config, compute_momentum, describe_momentum

config = build_momentum_config(context, family="macd", fast_period=12, slow_period=26, signal_period=9,
                               availability=availability, adjustment=adjustment,
                               price_unit=price_unit, evidence_limit=8)
result = compute_momentum(batches, context, config,
                          features=("intraday.macd_histogram", "intraday.macd_line", "intraday.macd_signal"))
```

One config computes one homogeneous family and any subset of that family's outputs is selected per call. Parameters are exactly `momentum_family` (`macd`, `dmi` or `stochastic`), that family's periods, its convention parameters, `evidence_limit` (0..10000) and the R17 context transport (`context_schema`, `context_sha256`, `context_chunks`, `context_000`...). No period has a default. The builder takes only the family's period keywords (a missing or surplus one is `INVALID_CONFIG`); `conventions` is optional and defaults to the one `ef2-conv1` value of every convention parameter (any other value is `INCOMPATIBLE_VERSION`). `decode_momentum_config(context, config)` validates the closed envelope and returns `MomentumSettings(family, periods, evidence_limit)`.

| Family | Periods and bounds | Outputs (float64) |
| --- | --- | --- |
| `macd` | `fast_period`, `slow_period`, `signal_period`; 1 <= fast < slow; slow + signal - 1 <= 4096 | `intraday.macd_histogram`, `intraday.macd_line`, `intraday.macd_signal` (`currency/share`) |
| `dmi` | `di_period`, `adx_period` >= 1; di + adx <= 4096 | `intraday.adx`, `intraday.dx`, `intraday.minus_di`, `intraday.plus_di` (`DMI points`) |
| `stochastic` | `k_period`, `k_slowing`, `d_period` >= 1; k + slowing + d - 2 <= 4096 | `intraday.stoch_d`, `intraday.stoch_k` (`stochastic points`), `intraday.williams_r` (`Williams %R points`) |

`batches` is `None` (absent delivery) or a tuple of R17 BAR chunks on the governed grid with the R17 per-slot coverage, ordering, duplicate and cutoff rules. MACD needs `close`; DMI needs `close`, `high` and `low`; stochastic and Williams %R need `high`, `low` and `close`. The result has one scalar per selected feature in lexical order, each with its own quality row, column algorithm `intraday-momentum-v1`, backend `intraday.python` and the R17 input bindings `bars:000`.... Discovery (`describe_momentum`) lists the ten IDs with batch capability only; `require_momentum_capability` refuses update, restore and merge with `UNSUPPORTED_CAPABILITY`. The R17 `describe_intraday`, `compute_intraday` and the R17 catalog digest are unchanged. Numeric policy is the R17 Decimal120 recurrence policy with the R17 tolerance; exact zeros publish `+0.0`.

Typed refusals (no `FeatureResult`): `INVALID_CONFIG` (period shape and bounds, fast >= slow, boolean periods, missing or surplus parameter, evidence limit, carry mode), `INCOMPATIBLE_VERSION` (unsupported convention value, algorithm or context codec), `UNKNOWN_FEATURE` (an ID outside the catalog or owned by another family), `UNSUPPORTED_CAPABILITY`, `INCONSISTENT_IDENTITY`, `INVALID_UNIT`, `UNSUPPORTED_ADJUSTMENT`, `DUPLICATE`, `INVALID_ORDER`, `BOUNDS`, `INVALID_SCHEMA` (from shared BAR validation) and `OVERFLOW`. See [mathematics, readiness and open points](../ef2/MOMENTUM_TREND_IMPLEMENTATION.md) and the [frozen contract](../ef2/MOMENTUM_TREND_CONTRACT_PROPOSAL.md).
