# Canonical in-memory inputs (EQ-011)

Implemented in experimental0.0.1a1, schema1. `CanonicalBatch(kind, columns,
metadata)` owns immutable `Column` tuples; input lists/NumPy buffers are detached.
This reference boundary favors explicit admission and copy semantics. It is not a
high-throughput numerical kernel or a zero-copy performance promise.

## Fields and precision

All kinds require nonempty `instrument_id` and `session_id` strings. Instrument IDs
are opaque within `BatchMetadata.namespace`; source binding declares source,
snapshot, mapping version and input identity. These are caller assertions, not
certification of provider truth, access rights or historical completeness.

| Kind | Additional required, nonnull fields | Optional nullable payload fields |
| --- | --- | --- |
| trade | event_ns, order_key, event_id, eligible | price, size, condition, known_at_ns |
| quote | event_ns, order_key, event_id | bid, ask, bid_size, ask_size, known_at_ns |
| bar | start_ns, end_ns | open, high, low, close, volume, trade_count, actual_notional, known_at_ns |
| daily | start_ns, end_ns | open, high, low, close, volume, trade_count, actual_notional, known_at_ns |
| reference | reference_id, fact_kind, effective_start_ns | effective_end_ns, text, price, factor_num, factor_den, known_at_ns |

`schema_for(DataKind)` returns frozen `InputSchema`/`Field` descriptors. All time
fields are UTC nanoseconds with signed int64 bounds; no float epoch conversions.
Prices, quantities, order keys and rational coefficients use signed int64 admission;
Boolean values cannot masquerade as integers. `eligible` is Boolean; IDs, condition,
text and fact kind are strings. `actual_notional` is an exact decimal128 scale0
coefficient bounded strictly between -10^38 and10^38, in price units times shares.
Prices represent integer coefficient /10^scale, with scale0..18 and explicit currency.
Reference price columns also require a price unit. No float quantization is implicit.

Absent optional columns, present nulls and observed zero are distinct. Unknown
known-at remains absent/null, not a causal availability claim. Required columns
remain present even for zero-row observed batches. Coverage separately records
caller-governed expected/observed observations; a missing batch is not constructed
as an observed empty batch. Complete coverage requires a known matching count;
coverage may describe a larger supplied interval than one delivery chunk.

Quote sampling must be `trade_snapshot` or `continuous`; other kinds use `none`.
Adjustment basis is raw/split/total_return with policy version; adjusted inputs also
require an action snapshot and anchor. No corporate-action conversion occurs here.
Raw defaults explicitly mean raw-v1/no actions/no anchor. Quantity unit is shares.
Ordering declares `declared` or `unsorted`; duplicate policy is reject/preserve.
Declarations are retained, not proven by structural construction. Semantic order,
duplicate, OHLC, positivity and safe arithmetic checks are EQ-014. Crossed/locked
and null quotes are preserved for the agreed quote-state classification.

## Core and optional bridges

```python
from equity_feature_contracts import (
    BatchMetadata, CanonicalBatch, Column, Coverage, DataKind,
    PriceUnit, SourceBinding,
)
meta = BatchMetadata("demo:instrument:v1",
    SourceBinding("synthetic", "snapshot1", "map1", "input1"),
    Coverage(1, 1, True), PriceUnit(4, "USD"))
trade = CanonicalBatch(DataKind.TRADE, (
    Column("instrument_id", ("A",)), Column("session_id", ("S",)),
    Column("event_ns", (1700000000000000001,)), Column("order_key", (1,)),
    Column("event_id", ("e1",)), Column("eligible", (True,)),
    Column("price", (1234500,)), Column("size", (10,)),
    Column("known_at_ns", (None,)),
), meta)
```

Core import needs only the standard library. Explicitly importing
`equity_feature_contracts.columnar` requires the pinned `columnar` extra.
`to_arrow(trade)` yields a concrete RecordBatch; `from_arrow` accepts concrete
RecordBatch/Table only, requires schema1 envelope metadata, exact field types and
nullability, and materializes owned tuples. Timestamp type must be ns/UTC. Time
values are cast through int64 to avoid Python datetime microsecond truncation.
Wide notional values use Arrow decimal128(38,0) without floating conversion.
Envelope JSON serializes metadata only; it is an experimental in-memory exchange
convention, not a supported untrusted remote transport or executable serialization.

`to_numpy` returns a mapping from column name to `(array, validity_mask)`; True
means present. `from_numpy(kind, mapping, metadata)` requires a concrete dictionary and exact ndarray buffers (no subclasses),
one-dimensional
int64/Boolean/Unicode arrays and a same-shape Boolean mask. Masked physical filler
is zero/False/empty string, but remains logical null. Float epochs/prices, unsigned
integers, object arrays and wide notional conversion are rejected. Both directions
materialize copies; modifying an output array cannot change the canonical input.

## Evidence and remaining scope

28 unit cases cover all five schemas, required/optional/null/zero/empty inputs,
int64 and decimal128 extrema, nanosecond round trips, Arrow Table/type/unit checks,
NumPy masks/ownership, invalid units/sampling/adjustment and retained quote states.
CI and fresh wheel/sdist environments install pinned optional backends and run
these same tests against installed artifacts. Core isolation is tested separately
with optional backends forbidden. Backend-specific dynamic types are confined to
the optional bridge; strict mypy checks all core and bridge source, with only the
missing third-party PyArrow stubs excluded. Session/config/result/semantic validators,
registry and adapter protocols remain EQ-012â€“016. No numerical calculator exists.

## R1 additive scope contract (0.0.2a0)

BatchMetadata.scope optionally carries typed InputScope(start_ns,end_ns,eligibility_policy,include_opening_auction,include_closing_auction). Bounds are positive exact UTCns intervals; policy nonempty and auction flags Boolean. It survives Arrow envelopes and result input identity. Historical batches without scope still construct; executable bar calculations require matching scope/policy and actual population coverage. See [bar API](../api/SESSION_BARS.md). Source admission truth remains caller-owned.

EQ018 adds owned BatchMetadata.interval_coverage tuples of IntervalCoverage(name,start_ns,end_ns,Coverage), with unique names and bounds inside InputScope. Arrow serialization retains them; executable interval reduction matches configured window identity and actual selected whole-bar population. These are caller assertions, not inferred completeness.

EQ023/0.0.2a6 adds StreamPopulation and PrefixCoverage: fixed owned source/schema declaration and explicit requested-prefix coverage. Contiguous ordinals/order and known retained identities are checked; caller owns global nonretained identity proof. No unbounded source history. [Lifecycle contract](../api/INCREMENTAL.md).

EQ024 adds immutable AccumulatorState and exact compatible in-memory restore for all23 R1 IDs; see [incremental API](../api/INCREMENTAL.md). Strict schema/version/source/config checks and bounded owned state apply; digest is not authentication. Merge remains false.
