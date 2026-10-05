"""Synthetic, source-independent bar calculation; tiny supplied UTCns for arithmetic."""
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage,
    DataKind, EntityKey, InputScope, Parameter, PriceUnit, SessionSpec, SourceBinding,
    WindowSpec,
)
from equity_features.session import compute_bars

unit = PriceUnit(0,"USD")
config = ConfigSpec("synthetic-bars","v1",(Parameter("eligibility_policy","example-v1"),),
    SessionSpec("demo","S",100,200,"caller-supplied"),
    WindowSpec(1,"S",("P","S")),AvailabilitySpec(200,210,210),price_unit=unit)
batch = CanonicalBatch(DataKind.BAR,tuple(Column(name,values) for name,values in (
    ("instrument_id",("A","A")),("session_id",("S","S")),
    ("start_ns",(100,150)),("end_ns",(150,200)),("known_at_ns",(150,210)),
    ("open",(100,102)),("high",(103,104)),("low",(99,101)),("close",(102,103)),
    ("volume",(200,300)),("actual_notional",(20300,30900)),
)),BatchMetadata("demo",SourceBinding("synthetic","snapshot1","map1","bars1"),
    Coverage(2,2,True),unit,scope=InputScope(100,200,"example-v1")))
result = compute_bars(batch,config,entity=EntityKey("A","S"))
values = {column.feature_id:column.values[0] for column in result.values}
assert values["session.bar.volume"] == 500
assert values["session.bar.notional"] == 51200
assert values["session.bar.close_weighted_price"] == 102.6
assert values["session.price.overnight_gap"] is None  # independently absent prior
print("Synthetic bar metrics verified; actual notional differs from proxy; prior returns unavailable.")
