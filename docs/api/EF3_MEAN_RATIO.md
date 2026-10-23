# EF3 mean-ratio volume companion

Use `build_mean_ratio_config`, `decode_mean_ratio_config`, `compute_volume_ratio_mean` (or the closed `compute_ef3_robust`), `ef3_robust_definitions` and `require_ef3_robust_capability` from `equity_features.ef3`. Config identity is `ef3.volume_ratio_mean`, algorithm `ef3-volume-ratio-mean-v1`, schema `1`, policy `ef3-mean1`. Outputs: `mean.numerator` and `mean.baseline` (shares) and `mean.ratio` (fraction). It is a separate producer from the median/MAD profiles and never replaces them.

```python
from equity_features.ef3 import MEAN_POLICY, build_mean_ratio_config, compute_volume_ratio_mean

config = build_mean_ratio_config(policy_version=MEAN_POLICY, field="volume", numerator_window=1,
                                 baseline_window=20, numerator_inclusion="current_inclusive",
                                 baseline_inclusion="prior_only", session=target_session,
                                 availability=availability, adjustment=adjustment, price_unit=price_unit,
                                 evidence_limit=25)
result = compute_volume_ratio_mean((series, sessions), config, entity=entity,
                                   features=("mean.numerator", "mean.baseline", "mean.ratio"))
```

Parameters (no defaults): `policy_version`, `field` (`volume` only in v1), `numerator_window` S and `baseline_window` L (1..4096), `numerator_inclusion` and `baseline_inclusion` (`prior_only` ends the window at the previous session, `current_inclusive` at the target) and `evidence_limit`. The role slots are `series` (DAILY volume rows) and `sessions` (`ef3.session.bounds` facts only; any other fact kind is `INVALID_SCHEMA`). Windows may overlap and S may exceed L. A window must be complete and known (no exclusions, no shrunken denominator): fewer governed sessions than the window give `insufficient_history`, and any gap, absent, null, unknown or future session in it blocks. `mean.numerator = sum / S`, `mean.baseline = sum / L` and `mean.ratio = (L sumS) / (S sumL)` are exact with one final rounding; a zero baseline is `not_applicable`/`zero_denominator`. A prior-only window never reads the target row. Witnesses are the window sessions ascending (`mean.ratio`: the numerator window then the baseline window, each session once). See [implementation, gaps and contract nits](../ef3/ROBUST_PACE_IMPLEMENTATION.md).
