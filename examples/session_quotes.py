"""Synthetic normalized snapshot quotes, supplied entirely in memory."""
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage,
    DataKind, EntityKey, InputScope, Parameter, PriceUnit, QuoteStateCounts,
    SampledSpread, SessionSpec, SourceBinding, WindowSpec,
)
from equity_features.session import compute_quotes
config=ConfigSpec('synthetic-quotes','v1',(Parameter('eligibility_policy','example-v1'),Parameter('observation_limit',4)),
    SessionSpec('demo','S',100,200,'caller-supplied'),WindowSpec(1,'S',('P','S')),
    AvailabilitySpec(200,210,210),price_unit=PriceUnit(0,'USD'))
batch=CanonicalBatch(DataKind.QUOTE,tuple(Column(k,v) for k,v in (
    ('instrument_id',('A',)*4),('session_id',('S',)*4),('event_ns',(110,120,130,140)),
    ('order_key',(1,2,3,4)),('event_id',('q1','q2','q3','q4')),('known_at_ns',(110,120,130,140)),
    ('bid',(100,102,105,None)),('ask',(102,102,104,102)),
)),BatchMetadata('demo',SourceBinding('synthetic','snapshot1','mapping1','quotes1'),Coverage(4,4,True),
    PriceUnit(0,'USD'),sampling='trade_snapshot',scope=InputScope(100,200,'example-v1')))
r=compute_quotes(batch,config,entity=EntityKey('A','S'))
s=r.values[0].values[0];n=r.values[1].values[0]
assert isinstance(s,SampledSpread) and isinstance(n,QuoteStateCounts)
assert (n.total,n.valid,n.locked,n.crossed,n.invalid)==(4,2,1,1,1)
assert s.mean_spread==1.0 and abs(s.mean_bps-10000/101)<1e-12
assert len(r.evidence)==4
print('Synthetic event-weighted quote states, valid means and bounded diagnostics verified.')
