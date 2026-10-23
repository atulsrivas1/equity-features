# EF3 robust history

Use `build_robust_history_config`, `decode_robust_history_config`, `compute_robust_history` (or the closed `compute_ef3_robust`), `ef3_robust_definitions` and `require_ef3_robust_capability` from `equity_features.ef3`. Config identity is `ef3.robust_history`, algorithm `ef3-robust-history-v1`, schema `1`, policy `ef3-robust1`. Outputs: `robust.median`, `robust.mad`, `robust.quantile` (operand unit), `robust.percentile_rank` (fraction), `cohort.percentile_rank` (fraction) and `cohort.rank` (int64, unit `members`).

```python
from equity_features.ef3 import ROBUST_POLICY, build_robust_history_config, compute_robust_history

config = build_robust_history_config(policy_version=ROBUST_POLICY, field="volume", window=20, min_history=15,
                                     quantile_num=1, quantile_den=2, session=target_session,
                                     availability=availability, adjustment=adjustment, price_unit=price_unit,
                                     evidence_limit=25)
result = compute_robust_history((series, sessions, None, None), config, entity=entity,
                                features=("robust.median", "robust.mad", "robust.quantile",
                                          "robust.percentile_rank"))
```

Parameters (no defaults): `policy_version`, `field` (`volume`, `open`, `high`, `low`, `close`), `window` N (1..4096), `min_history` m (1..N), `quantile_num`/`quantile_den` (a reduced int64 pair with 0 <= p <= 1, present exactly when `robust.quantile` is selected), `min_population` (1..65536, present exactly when a cohort output is selected) and `evidence_limit` (0..10000). The role slots are `series` (DAILY, the target instrument, the `field` column), `sessions` (REFERENCE, `ef3.session.bounds` per governed session and optional `ef3.session.excluded` facts with an opaque non-empty reason label), `population` (`ef3.population.member` facts, one per declared member) and `cohort_values` (DAILY, one row per member for the target session); roles a selection does not need may be `None`.

The sample is the retained prior sessions of the N governed sessions before the target (the target never enters it); declared exclusions are removed from the sample and from `expected`; a gap, absent, null, unknown or future slot in the window is never tolerated. Median averages the two middle values for even n, MAD is raw (scale 1), the quantile is Hyndman-Fan type 7 with the exact rational p, and the ranks are exact (`(L + E/2)/n`, history against the prior sample, cohort including the target; `cohort.rank = 1 + #{larger}`, competition rank). Every float is one correctly rounded value of the exact rational. A partial declared population gives `partial_universe` and withholds the cohort outputs; a declared size below `min_population` gives `insufficient_history`. Witnesses are `session:<id>` (the target first for the rank), then `excluded:<id>`, or `member:<instrument>` in declaration order. Refusals are the typed codes of the contract (RF01 to RF48). See [implementation, gaps and contract nits](../ef3/ROBUST_PACE_IMPLEMENTATION.md).
