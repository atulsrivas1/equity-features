# EF1 multi-venue status

Use `build_ef1_config`, `decode_ef1_context`, `ef1_definitions` and `compute_ef1` from `equity_features.ef1`. Choose context version `ef1-context1`, producer `multivenue_status`, `calendar=None` and `selection={"clock_dimensions":[...],"epoch":<label>,"max_age_ns":<null|int>=0,"population_id":<label>,"population_revision":<label>,"state_policy":{"policy_id":"venue_precedence_v1","policy_version":"1","precedence":[<permutation of active, halted, closed>]}}`. `clock_dimensions` is a nonempty strictly ascending subset of `quoting`, `ssr`, `trading`. Config identity is `ef1.multivenue_status`, algorithm `v1`, schema `1`; price unit must be null and the window target-only.

```python
from equity_features.ef1 import compute_ef1

result = compute_ef1((venue_population, venue_seed, venue_states, venue_prefix, venue_validity), config, entity=entity)
```

Exactly five nullable positional REFERENCE slots in that order. Row grammars (B is unpadded base64url, D is `t`, `q` or `s`): population `vp1:B(population_id):B(revision):B(publisher)`; seed `vs1:D:B(epoch):B(publisher):seq19`; states `v1:D:B(epoch):B(publisher):seq19:B(event)`; prefix and validity `vc1:D:B(epoch):B(publisher):B(states_input_id):B(certificate)`. Fact kinds are `ef1.venue.population_member`, `ef1.venue.seed`, `ef1.venue.state.<dimension>`, `ef1.venue.prefix_complete`, `ef1.venue.validity`; mapping version `ef1-venue-map1`. Rows arrive in effective-start then reference order; nothing is sorted.

The result has seven scalars (`session.venue_status.*`), one quality row each, input bindings in lexical role order and evidence limit 4. A missing or incomplete population, an empty population, or unknown or future knowledge give null values with `aggregate_reason` naming the cause. Selected-publisher status is not read or replaced. See [behavior and validation](../ef1/MULTI_VENUE_STATUS_IMPLEMENTATION.md) and the [frozen contract](../ef1/MULTI_VENUE_STATUS_CONTRACT_PROPOSAL.md).
