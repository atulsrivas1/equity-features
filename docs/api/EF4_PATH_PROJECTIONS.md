# EF4 statistical projections

Use `build_*_config`, `decode_*_config` and `compute_*` from `equity_features.ef4`, the closed `compute_ef4_path_projections`, `ef4_path_projections_definitions` and `require_ef4_path_projections_capability`. Batch only; update, restore and merge are unsupported. All parameters are explicit (no defaults).

| Producer | Identity / algorithm / policy | Roles | Outputs |
| --- | --- | --- | --- |
| Session projection | `ef4.session_projection` / `ef4-session-projection-v1` / `ef4-proj1` | `daily` (close-only BAR on a `DailyGrid`) | `projection.up_session_fraction`, `down_session_fraction`, `drawdown_fraction`, `max_drawdown_fraction`, `distance_from_low_fraction`, `close_vs_sma_fraction`, `close_above_sma` |
| Bar projection | `ef4.bar_projection` / `ef4-bar-projection-v1` / `ef4-proj1` | `bars` (BAR on a `BarGrid`) | `projection.up_volume`, `down_volume`, `up_volume_fraction`, `up_dollar_volume`, `down_dollar_volume`, `up_dollar_volume_fraction` |
| Relative excess | `ef4.relative_excess` / `ef4-relative-excess-v1` / `ef4-rel1` | `legs`, `membership` (REFERENCE) | `relative.session.{primary,secondary,sector}.{prior_close,window}_excess_fraction`, `core.benchmark_direction_agreement_fraction`, `core.benchmark_return_dispersion_fraction` |
| Rate projection | `ef4.rate_projection` / `ef4-rate-projection-v1` / `ef4-rate1` | `tape`, `legs` (REFERENCE) | `rate.window.trade_rate`, `notional_rate`, `share_volume_rate`, `raw_return_fraction`, `return_rate_difference` |

```python
from equity_features.ef4 import RELATIVE_POLICY, build_relative_excess_config, compute_relative_excess

config = build_relative_excess_config(policy_version=RELATIVE_POLICY, primary_benchmark_id=primary_id,
                                      alignment_tolerance_ns=5_000_000, max_endpoint_age_ns=60_000_000_000,
                                      session=target_session, availability=availability, adjustment=adjustment,
                                      price_unit=price_unit, evidence_limit=25)
result = compute_relative_excess((legs, None), config, entity=entity,
                                 features=("relative.session.primary.prior_close_excess_fraction",))
```

Session: `window` N in 1..4096; up/down need N+1 closes, the others N. Bar: epoch-to-date population, direction by close versus open, flat bars and empty bars in the denominators only, dollar volume from actual notional only. Relative excess: `alignment_tolerance_ns`, `max_endpoint_age_ns`, `window_ns` (when a window profile is used), benchmark ids per selected role, `core_benchmark_ids` (2..16, JSON text via `encode_core_ids`) with `core_profile`; fact kinds `ef4.leg.start|end` and `ef4.sector.membership`. Rate: `window_ns`, `max_endpoint_age_ns`, `alignment_tolerance_ns` (return outputs) and `adjacency` (`adjacent`|`disjoint`, difference output); tape facts `ef4.tape.count|volume|notional` (provisional carrier). Units: `fraction`, `boolean`, `shares`, `currency`, `trades_per_second`, `currency_per_second`, `shares/s`, `fraction_per_second`. See the [contract](../ef4/PATH_PROJECTIONS_CONTRACT_PROPOSAL.md) and the [implementation, rulings and limits](../ef4/PATH_PROJECTIONS_IMPLEMENTATION.md).
