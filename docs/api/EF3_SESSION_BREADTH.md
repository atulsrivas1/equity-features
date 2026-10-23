# EF3 declared-universe session breadth

Use `build_session_breadth_config`, `decode_session_breadth_config`, `compute_session_breadth` (or the closed `compute_ef3_breadth`), `ef3_breadth_definitions` and `require_ef3_breadth_capability` from `equity_features.ef3`. Config identity is `ef3.session_breadth`, algorithm `ef3-session-breadth-v1`, schema `1`, policy `ef3-breadth1`. It is separate from the accepted historical `breadth.direction_counts` and `breadth.above_sma_fraction`, which are unchanged, and from the observed-population companion ([EF3 observed breadth](EF3_OBSERVED_BREADTH.md)); the denominators are never mixed.

```python
from equity_features.ef3 import BREADTH_POLICY, build_session_breadth_config, compute_session_breadth

config = build_session_breadth_config(policy_version=BREADTH_POLICY, membership_profile="static_snapshot",
                                      population_id="universe-1", population_revision="rev-7",
                                      near_high_tol_num=1, near_high_tol_den=4, session=target_session,
                                      availability=availability, adjustment=adjustment, price_unit=price_unit,
                                      evidence_limit=25)
result = compute_session_breadth((population, prior_ref, current_return, volume, endpoint, vwap, momentum,
                                  high, low), config, entity=entity,
                                 features=("breadth.session.advancing_count", "breadth.session.near_high_fraction"))
```

Outputs (lexical): `above_vwap_fraction`, `advance_decline_ratio`, `advancing_count`, `declining_count`, `direction_net_count`, `down_volume`, `latest_observed_member_event_ns`, `near_high_fraction`, `near_low_fraction`, `positive_momentum_fraction`, `prior_reference_coverage_fraction`, `prior_reference_eligible_count`, `selected_member_count`, `unchanged_count`, `up_down_volume_ratio`, `up_volume` (all `breadth.session.*`; units `fraction`, `ratio`, `members`, `shares`, `utc_ns`).

Parameters (no defaults): `policy_version`, `membership_profile` (`static_snapshot` or `ordered_history`), `population_id`, `population_revision`, `near_high_tol_num`/`den` (exactly when `near_high_fraction` is selected) and `near_low_tol_num`/`den` (exactly when `near_low_fraction` is selected; reduced pairs in [0, 1]) and `evidence_limit`. The nine nullable REFERENCE role slots are `population`, `prior_reference_availability`, `current_return`, `cumulative_volume`, `endpoint_price`, `vwap`, `momentum`, `selected_high`, `selected_low`; roles that no selected output needs are not examined. Every role batch carries the config `PriceUnit` and one snapshot id; values travel in the REFERENCE `price` column (sign-only return and momentum, share volume, positive price coefficients, VWAP as `price * factor_num / factor_den`).

The declared population is the set of selected members at the market cutoff C (`static_snapshot`: kind `ef3.population.member`; `ordered_history`: kind `ef3.breadth.membership_interval`, `start <= C < end`). Every denominator is N, the declared size; a missing member never shrinks it. Each member predicate is three valued (a known false decides without the other inputs) and an output is available only when no member is unknown for it (`expected` N, `observed` N minus the unknown members). Direction needs an available prior reference and an exact signed return (zero is unchanged); `up_volume` and `down_volume` move a member's whole cumulative volume with its current direction; ratios with a zero denominator are `not_applicable`/`zero_denominator`; `above_vwap_fraction` is strict and exact; proximity is range based and inclusive (`H = L` is not near, an inverted pair or an endpoint outside the range is `ineligible`); `latest_observed_member_event_ns` is the maximum endpoint event time, or `C - 1` when saturated (quality 1/1). `N = 0` is `not_applicable`/`empty_universe`. Evidence cites the deciding fact rows (`member:<id>`) of the first contributing members in population order. See [implementation, gaps and contract nits](../ef3/BREADTH_ADAPTIVE_IMPLEMENTATION.md).
