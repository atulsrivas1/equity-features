# EF3 intraday realized variance

Use `build_realized_variance_config`, `decode_realized_variance_config`, `compute_realized_variance`, `describe_realized_variance`, `realized_variance_catalog_digest` and `require_realized_variance_capability` from `equity_features_intraday`. The context is the unchanged R17 `IntradayContext` in `reset` mode (carry is out of v1). Config identity is `ef3.intraday_realized_variance`, algorithm `ef3-realized-variance-v1`, schema `1`, policy `ef3-rv1`.

```python
from equity_features_intraday import (
    REALIZED_VARIANCE_POLICY, REALIZED_VARIANCE_SAMPLING, build_realized_variance_config, compute_realized_variance)

config = build_realized_variance_config(context, policy_version=REALIZED_VARIANCE_POLICY,
                                        sampling=REALIZED_VARIANCE_SAMPLING, annualization_factor=252,
                                        availability=availability, adjustment=adjustment,
                                        price_unit=price_unit, evidence_limit=2)
result = compute_realized_variance(batches, context, config,
                                   features=("intraday.realized_variance", "intraday.realized_volatility"))
```

Parameters are exactly `policy_version` (`ef3-rv1`), `sampling` (the single value `every_governed_slot`; any other string is `UNSUPPORTED_SAMPLING`), `evidence_limit` (0..10000), `annualization_factor` A (1..2^63-1, present exactly when `intraday.realized_volatility` is selected; missing or surplus is `INVALID_CONFIG`) and the R17 context transport. `batches` is `None` or a tuple of R17 BAR chunks with the R17 per-slot coverage, ordering, duplicate and cutoff rules; only `close` is read (a zero-volume interval has null OHLC by the shared BAR rule). Over the epoch of the target session, `RV = sum ln(C_i / C_{i-1})^2` for the consecutive governed bars `a+1..t` and `realized_volatility = sqrt(A * RV)`; the first bar is only the base close, no return crosses a session boundary, and every slot from the anchor to the target must be READY (no bridging, forward fill or rescaling). A coverage-proven empty slot has no close and is `not_applicable/no_eligible_observations`. One return is the minimum: `t = a` is `insufficient_history` with expected 2, observed 1.

Each logarithm is a Decimal120 evaluation of the exact close ratio; a step with equal closes contributes exactly zero, so a flat epoch is exactly `+0.0` and every other result is published unsnapped. Outputs are float64 `fraction` in lexical order (`intraday.realized_variance`, `intraday.realized_volatility`), column algorithm `ef3-realized-variance-v1`, backend `intraday.python` and the R17 input bindings `bars:000`...; expected is `max(2, t - a + 1)`, observed the READY bars among `a..t`; witnesses (available only) are the anchor then the target bar (`slot:<index>`, `completed_interval`), bounded by the result-wide `evidence_limit`. Discovery lists the two ids with batch capability only; `describe_intraday` and its digest are unchanged. Refusals: `INVALID_CONFIG` (including carry mode and the annualization closure), `INCOMPATIBLE_VERSION`, `UNSUPPORTED_SAMPLING`, `INVALID_ORDER`, `DUPLICATE`, `INVALID_SCHEMA`, `BOUNDS`, `INCONSISTENT_IDENTITY`, `INVALID_UNIT`, `UNSUPPORTED_ADJUSTMENT`, `UNKNOWN_FEATURE`, `UNSUPPORTED_CAPABILITY`. See [implementation and open points](../ef3/RELATIVE_RV_IMPLEMENTATION.md).
