"""Synthetic exact trade aggregates; no feed, database or file acquisition."""
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage,
    DataKind, EntityKey, InputScope, Parameter, PriceUnit, SessionSpec, SourceBinding,
    WindowSpec,
)
from equity_features.session import compute_trades

config=ConfigSpec("synthetic-trades","v1",(Parameter("eligibility_policy","example-v1"),),
    SessionSpec("demo","S",100,200,"caller-supplied"),WindowSpec(1,"S",("P","S")),
    AvailabilitySpec(200,210,210),price_unit=PriceUnit(0,"USD"))
batch=CanonicalBatch(DataKind.TRADE,tuple(Column(name,values) for name,values in (
    ("instrument_id",("A",)*3),("session_id",("S",)*3),
    ("event_ns",(110,130,160)),("order_key",(1,2,3)),("event_id",("t1","t2","t3")),
    ("eligible",(True,)*3),("price",(100,102,101)),("size",(2,3,5)),("known_at_ns",(110,130,210)),
)),BatchMetadata("demo",SourceBinding("synthetic","snapshot1","map1","trades1"),
    Coverage(3,3,True),PriceUnit(0,"USD"),scope=InputScope(100,200,"example-v1")))
result=compute_trades(batch,config,entity=EntityKey("A","S"))
values={c.feature_id:c.values[0] for c in result.values}
assert values['session.trade.count']==3
assert values['session.trade.volume']==10
assert values['session.trade.notional']==1011
assert values['session.trade.vwap']==101.1
print("Synthetic eligible trade count/volume/exact notional/VWAP verified.")
