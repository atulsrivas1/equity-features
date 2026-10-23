# EF3 observed-population session breadth

Use `build_observed_breadth_config`, `decode_observed_breadth_config`, `compute_observed_breadth` (or the closed `compute_ef3_breadth`), `ef3_breadth_definitions` and `require_ef3_breadth_capability` from `equity_features.ef3`. Config identity is `ef3.observed_breadth`, algorithm `ef3-observed-breadth-v1`, schema `1`, policy `ef3-obsbreadth1`. The roster defines the population, so there is no expected universe and `expected` in the quality row is a record count; observed records can never feed the declared producer ([EF3 session breadth](EF3_SESSION_BREADTH.md)).

```python
from equity_features.ef3 import OBSERVED_POLICY, build_observed_breadth_config, compute_observed_breadth

config = build_observed_breadth_config(policy_version=OBSERVED_POLICY, scope="group", group_label="g1",
                                       record_set_id="records-1", floor_price_num=10, floor_price_den=1,
                                       floor_volume=100, session=target_session, availability=availability,
                                       adjustment=adjustment, price_unit=price_unit, evidence_limit=25)
result = compute_observed_breadth((members, change, qualifier_price, qualifier_volume), config, entity=entity,
                                  features=("breadth.observed.advance_fraction",
                                            "breadth.observed.qualifying_member_count"))
```

Outputs (lexical): `advance_fraction`, `advancing_member_count`, `nonadvancing_member_count`, `observed_member_count`, `qualifying_fraction`, `qualifying_member_count`, `unknown_member_count` (all `breadth.observed.*`; units `fraction` and `members`).

Parameters (no defaults): `policy_version`, `scope` (`cohort` or `group`), `group_label` (exactly when the scope is `group`), `record_set_id`, `floor_price_num`/`den` (a reduced rational at least 0), `floor_volume` (int64 at least 0) and `evidence_limit`. The four nullable REFERENCE role slots are `members` (kind `ef3.observed.member`, `text` the group label), `change` (sign only), `qualifier_price` (positive coefficient at the price scale) and `qualifier_volume` (shares); the fact roles are keyed by member and share the roster record-set id.

The observed population is the roster records with an event time before the market cutoff (records at or after it are not yet observed and never block), then the group filter. A member qualifies when its price reaches the price floor and its volume the volume floor (both inclusive) and advances when it qualifies with a strictly positive change; a known failure decides without the other input. `advance_fraction = advancing / qualifying` and `qualifying_fraction = qualifying / observed` (a zero denominator is `not_applicable`/`zero_denominator`); non-advancing members are not split into declining and unchanged. An empty scope gives available zero counts. `unknown_member_count` is available whenever the roster is. Evidence cites the `qualifier_price` rows of qualifying members and the `change` rows of advancing members. See [implementation, gaps and contract nits](../ef3/BREADTH_ADAPTIVE_IMPLEMENTATION.md).
