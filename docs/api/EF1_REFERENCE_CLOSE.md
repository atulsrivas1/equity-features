# EF1 supplied close reconciliation

Use `build_ef1_config`, `decode_ef1_context`, `ef1_definitions` and `compute_ef1` from `equity_features.ef1`. Choose context version `ef1-context1`, producer `reference_close`, the same target-only calendar as `regular_bar_prices`, and exactly `selection={"phase_profile":"regular_no_auctions1","sampling":"completed_bar_close","policy_version":"ef1-close-compare1","scope_id":<label>,"tolerance_bps_num":<int>,"tolerance_bps_den":<int>}`. The tolerance is an explicit reduced non-negative integer pair (`num` in 0..2^63-1, `den` in 1..2^63-1, `gcd = 1`, `num = 0` only with `den = 1`); there is no default. Config identity is `ef1.reference_close`, algorithm `v1`, schema `1`. Supply an explicit PriceUnit, both auction flags false and regular open < market cutoff <= regular end.

```python
from equity_features.ef1 import compute_ef1

result = compute_ef1((calendar_provenance, bars, population_proof, authoritative_close), config, entity=entity)
assert [c.feature_id for c in result.values] == [
    "reference.close.absolute_difference_bps", "reference.close.comparison_state",
    "reference.close.supplied_price", "reference.close.within_tolerance"]
```

The concrete tuple/list has exactly four nullable positional slots with kinds REFERENCE/BAR/REFERENCE/REFERENCE. The first three are the unchanged EQ166 `regular_bar_prices` roles. `authoritative_close` carries at most one row of fact kind `ef1.close.authoritative` with `reference_id = k1:B(scope_id):B(source_close_id)` (reversible unpadded base64url of UTF8), `effective_start_ns` equal to the actual session close, `text` equal to the batch `source.snapshot_id`, an int64 `price` coefficient at the config scale, no factor values and a causal `known_at_ns`. Batch unit, currency and adjustment equal the config; mapping version is `ef1-reference-map1`; admission requires complete coverage.

The result has four scalars with one quality row each, every present input binding in lexical role order, evidence limit 7 and original witnesses (the selected completed BAR and the supplied close row). `supplied_price` is the decimal128 coefficient and never the calculated close; published BPS is one final binary64 conversion of the exact rational; `within_tolerance` is the exact inclusive integer verdict; `comparison_state` is one of `within_tolerance`, `outside_tolerance`, `reference_unavailable`, `reference_future`, `reference_invalid`, `calculated_unavailable`. A comparison never authenticates the close or its source rights. Discovery advertises batch capability only; no state, replay, storage, registry or DTO change is introduced. See [mathematics, readiness and source validation](../ef1/CLOSE_RECONCILIATION_IMPLEMENTATION.md) and the [frozen contract](../ef1/CLOSE_RECONCILIATION_CONTRACT_PROPOSAL.md).
