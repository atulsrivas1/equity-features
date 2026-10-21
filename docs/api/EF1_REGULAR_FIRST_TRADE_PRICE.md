# EF1 regular first eligible trade price

Use `build_ef1_config`, `decode_ef1_context`, `ef1_definitions` and `compute_ef1` from `equity_features.ef1`. Choose context version `ef1-context1`, producer `regular_first_trade_price`, and exactly `selection={"phase_profile":"regular_no_auctions1","sampling":"eligible_trade"}`. Config identity is `ef1.regular_first_trade_price`, algorithm `v1`, schema `1`. Supply one target calendar/window, explicit PriceUnit and both session auction flags false. Require regular open < market cutoff <= regular end.

```python
from equity_features.ef1 import compute_ef1

result = compute_ef1((calendar_provenance, trades, population_proof), config, entity=entity)
assert result.values[0].feature_id == "session.regular.first_trade_price"
```

The concrete tuple/list has exactly three nullable positional slots with kinds REFERENCE/TRADE/REFERENCE. Present-empty inputs retain their actual bindings. Calendar and independent closed trade population proof establish causal complete membership in both availability modes. The first original eligible row supplies the price only when its original numerical clock is known by K. No later eligible price substitutes an unavailable first price; optional whole size absence is irrelevant. All supplied eligible numerical cells are structurally validated before absence/readiness.

The result contains one scalar, one quality row, every present input binding in lexical role order, exact declared evidence_limit1 and zero or one original selected trade witness. Quality counts describe delivered trades. Discovery advertises batch capability only; no state/replay/storage/registry/DTO changes are introduced. Backend remains python-exact/0.0.4a5, canonical package0.0.4a4, schema1/mathv1. See [formula/readiness/source validation and remaining gates](../ef1/REGULAR_FIRST_TRADE_PRICE_IMPLEMENTATION.md), [normative contract](../ef1/regular_first_trade_price/REGULAR_FIRST_TRADE_PRICE_CONTRACT_V2.md) and [synthetic example](../../examples/ef1_regular_first_trade_price.py). Example fixture loading occurs outside calculations.
