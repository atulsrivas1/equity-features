# EF1 regular completed-BAR prices

Use the existing `equity_features.ef1` functions `build_ef1_config`, `decode_ef1_context`, `ef1_definitions` and `compute_ef1`. Select `producer="regular_bar_prices"`, context version `ef1-context1`, and exactly `selection={"phase_profile":"regular_no_auctions1","sampling":"completed_bar_close"}`. Config identity is `ef1.regular_bar_prices`, algorithm `v1`, schema `1`. Supply one target calendar/window and explicit PriceUnit; both auction flags are false and regular open < market cutoff <= regular end.

```python
from equity_features.ef1 import compute_ef1, ef1_definitions

# Supplied canonical inputs; acquisition and original causal proofs belong to callers.
result = compute_ef1((calendar_provenance, bars, population_proof), config, entity=entity)
assert [column.feature_id for column in result.values] == [
    "session.close.calculated_price",
    "session.regular.first_completed_bar_open",
]
```

The concrete tuple/list has exactly three nullable positional slots, with kinds REFERENCE/BAR/REFERENCE. A present empty batch is distinct from None. Metadata binds every present original input in lexical role order, never inventing absent bindings. Counts refer only to delivered BAR rows; available scalar cells each carry one selected BAR witness, with exact evidence declaration two and at most two actual rows. One BAR may supply both per-feature witnesses.

Discovery describes only batch capability. No state/replay capability or new generic DTO, codec, registry, scheduler or storage API is claimed. Backend metadata remains `python-exact/0.0.4a5`, math policy `v1`, schema `1`; ConfigSpec has no build-version field. See [formulas, readiness and validation](../ef1/REGULAR_BAR_PRICES_IMPLEMENTATION.md) and the [complete frozen input contract](../ef1/regular_bar_prices/REGULAR_BAR_PRICES_CONTRACT_V3.md).
