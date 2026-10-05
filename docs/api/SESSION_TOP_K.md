# Bounded largest trades — experimental0.0.2a3

`equity_features.session.compute_top_k(batch, config, *, entity)` returns
`session.trade.top_k` in the existing FeatureResult. Use parameters
`eligibility_policy`, `top_k` and `evidence_limit`. K must be an exact integer
1..10000; evidence_limit must be an exact integer K..10000 (booleans rejected).
This explicit operational ceiling bounds retained original row evidence.

Eligible supplied trades rank by `(-size,event_ns,order_key,event_id)`. Up to
min(K,n) original rows are retained. Input admission requires the EQ019 source,
unit/basis, session/scope/auction, order/duplicate, C/K/E and coverage contracts.
No input sorting or deduplication is performed. Missing price/size on a nonempty
eligible population is missing_input; supplied malformed eligible values reject.
Incomplete delivery or unavailable knowledge yields null without retained evidence.
Fully covered empty/all-ineligible input yields an available empty table.

`TopKTrades(k, rows)` is an immutable typed cell containing owned
`TopKTradeRow(input_id,event_id,event_ns,order_key,known_at_ns,price,size)` rows.
Prices are original exact coefficients with scale/currency in the bound metadata;
size is original shares. Each retained row has matching consumed EvidenceRow,
including explicit closing-auction boundary when admitted at C. No float rounding
or derived notional is used. Arrow copies a struct `{k,rows:list<struct>}` with
UTCns timestamps and int64 payloads; metadata and evidence remain separately bound.
The API preserves the schema1 envelope while adding `ValueType.TOP_K_TRADES`;
consumers must handle this new structured dtype and registry digest.

The reducer retains at mostK+1 candidates transiently and K results; insertion
sorting costs O(n K log K). Canonical input ownership/validation and Arrow copies
still scale with supplied batch rows; this is bounded reduction retention, not
constant-memory source admission or a throughput promise. K is bounded by10000.
No unbounded raw-row list is retained.

For disjoint populations, topK(union of per-partition topK) equals full topK;
production-invoking tests independently verify this conservation. R1 qualifies batch/update/restore and conditional legal merge through
[SessionAccumulator](INCREMENTAL.md). Retained identities
can detect retained duplicates; summaries cannot prove disjointness of opaque IDs
that were not retained. The caller must govern population disjointness; overlap
and duplicates in the actual CanonicalBatch reject. Qualified modes require the explicit certificates and preconditions in the incremental API. Example: [session_top_k.py](../../examples/session_top_k.py).
