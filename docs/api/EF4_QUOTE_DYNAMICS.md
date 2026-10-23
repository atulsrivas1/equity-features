# EF4 quote dynamics

Use `build_quote_dynamics_config`, `decode_quote_dynamics_config`, `compute_quote_dynamics` (or the closed `compute_quote_vwap`), `quote_vwap_definitions` and `require_quote_vwap_capability` from `equity_features.ef4`. Config identity is `ef4.quote_dynamics`, algorithm `ef4-quote-dynamics-v1`, schema `1`, policy `ef4-quote1`. It is separate from the accepted `session.quote.sampled_spread`, `session.quote.state_counts` and `session.quote.time_weighted_spread`, which are unchanged; it applies no duration weighting and no seed.

```python
from equity_features.ef4 import QUOTE_POLICY, build_quote_dynamics_config, compute_quote_dynamics

config = build_quote_dynamics_config(policy_version=QUOTE_POLICY, sampling="continuous", session=target_session,
                                     availability=availability, adjustment=adjustment, price_unit=price_unit,
                                     evidence_limit=25)
result = compute_quote_dynamics((bounds, quotes), config, entity=entity,
                                features=("quote.microprice.last", "quote.sampled.maximum_spread"))
```

Outputs (lexical): `quote.change.midpoint_bps` (`bps`), `quote.change.midpoint_change_count` (`pairs`), `quote.change.pair_count` (`pairs`), `quote.change.spread` (`currency/share`), `quote.microprice.last`, `quote.microprice.last_offset_bps`, `quote.microprice.mean`, `quote.sampled.maximum_midpoint_bps`, `quote.sampled.maximum_spread`. The four `quote.change.*` outputs need `sampling="continuous"`; selecting one on a `trade_snapshot` config is `UNSUPPORTED_SAMPLING`.

Parameters (no defaults): `policy_version`, `sampling` (`trade_snapshot` or `continuous`, equal to the quotes batch sampling) and `evidence_limit` (0..10000). Roles: `bounds` (exactly one REFERENCE `ef4.interval.bounds` fact with `effective_start_ns` = S, `effective_end_ns` = E, `text` the batch snapshot id and the original `known_at_ns`) and the nullable `quotes` QUOTE batch (full bid/ask states with optional sizes, `event_ns` in `[S, E)` and before the market cutoff, ordered by `(event_ns, order_key)`, with the declared `IntervalCoverage` for `[S, E)`).

An observation is invalid (a null or nonpositive side), normal (a > b), locked (a = b) or crossed (a < b); valid is normal or locked. The maxima are the largest per-observation cash spread and own-midpoint bps over all valid observations (earliest tie); the microprice is `(b Qa + a Qb) / (Qa + Qb)` and needs both sizes positive (zero removes the observation, a null size on a consumed valid observation is `null_field`); `last` uses only the final admitted observation; `change` uses the first and last valid observations and the counts use adjacent valid pairs. Exact arithmetic, one rounding per float64. The interval end after the market cutoff is `future_market`; a delivered row with null or later knowledge blocks every output. Evidence: the single selecting or final observation, the first and last valid observations, the contributing rows (mean) or the rows of counted pairs. See [the implementation notes](../ef4/QUOTE_VWAP_IMPLEMENTATION.md). Batch only; update, restore and merge are `UNSUPPORTED_CAPABILITY`.
