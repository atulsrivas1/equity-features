# EF3 robust volume pace

Use `build_pace_config`, `decode_pace_config`, `compute_volume_pace_robust` (or the closed `compute_ef3_robust`), `ef3_robust_definitions` and `require_ef3_robust_capability` from `equity_features.ef3`. Config identity is `ef3.volume_pace_robust`, algorithm `ef3-volume-pace-robust-v1`, schema `1`, policy `ef3-pace1`. Outputs: `pace.baseline_median` and `pace.baseline_mad` (shares), `pace.ratio` and `pace.robust_z` (fraction).

```python
from equity_features.ef3 import PACE_POLICY, build_pace_config, compute_volume_pace_robust

config = build_pace_config(policy_version=PACE_POLICY, profile="cumulative", window=20, min_history=15,
                           grid_version="grid-2026-1", scale_num=3, scale_den=2, session=target_session,
                           availability=availability, adjustment=adjustment, price_unit=price_unit,
                           evidence_limit=25)
result = compute_volume_pace_robust((grid, sessions, bars), config, entity=entity,
                                    features=("pace.baseline_median", "pace.ratio", "pace.robust_z"))
```

Parameters (no defaults): `policy_version`, `profile` (`cumulative` or `bucket`), `window` N (1..4096), `min_history` m (1..N), `grid_version` (equal to the grid facts' `text`), `scale_num`/`scale_den` (the positive reduced pair k, present exactly when `pace.robust_z` is selected) and `evidence_limit`. The role slots are `grid` (`ef3.bucket.edge` facts: offsets from the actual open, first edge 0, strictly increasing, 2..4097 edges), `sessions` (`ef3.session.bounds` plus optional `ef3.session.excluded` facts) and `bars` (BAR, one consolidated volume row per session per grid bucket).

The evaluation bucket is the last bucket that has fully elapsed at the market cutoff and lies inside the actual target session; with none inside the session the outputs are `missing_input`/`ineligible`, with none elapsed `incomplete_coverage`/`future_market`. The operand is the bucket volume (`bucket`) or the sum of buckets 0 to b (`cumulative`, every bucket required). The baseline is the median and raw MAD of the retained prior sample of the N governed sessions before the target; declared exclusions and prior sessions that closed before the end of the evaluation bucket are removed from the sample and from `expected` (never zero, never a gap), and the target never enters the baseline. `pace.ratio = y / M` and `pace.robust_z = (y - M) / (k D)` are exact; `M = 0` or `D = 0` is `not_applicable`/`zero_denominator`; z is not clamped. Each output has its own readiness (the baseline stays available while the current observation is unready). Witnesses are `target:<id>` (ratio and z first), `session:<id>` per retained session (the evaluation bucket, or the buckets 0 to b aggregated), then `excluded:<id>` and `ineligible:<id>`. See [implementation, gaps and contract nits](../ef3/ROBUST_PACE_IMPLEMENTATION.md).
