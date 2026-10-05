"""Synthetic installed-artifact example, no source access."""
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

from equity_feature_contracts.columnar import from_arrow, to_arrow
assert from_arrow(to_arrow(trade)) == trade
assert trade.column("price").values == (1234500,)
print("Canonical synthetic input and exact Arrow round trip verified")
