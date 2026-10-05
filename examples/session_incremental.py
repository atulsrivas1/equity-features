"""Synthetic chunk lifecycle with explicit supplied prefix coverage."""
from dataclasses import replace
from equity_feature_contracts import Column, Coverage, EntityKey, PrefixCoverage, StreamPopulation
from equity_features.incremental import SessionAccumulator
from session_trades import batch, config

def chunk(indices):
    return replace(batch,columns=tuple(Column(x.name,tuple(x.values[i] for i in indices)) for x in batch.columns),metadata=replace(batch.metadata,coverage=Coverage(len(indices),len(indices),True)))
a=SessionAccumulator('trades',config,entity=EntityKey('A','S'),population=StreamPopulation.from_batch(batch))
a.update(chunk([0]),start_ordinal=0)
r=a.snapshot(PrefixCoverage(120,Coverage(1,1,True)))
assert r.values[0].values[0]==1
assert r.metadata.availability.market_cutoff_ns==120
a.update(chunk([1,2]),start_ordinal=1)
r=a.finalize(PrefixCoverage(200,Coverage(3,3,True)))
v={x.feature_id:x.values[0] for x in r.values}
assert v['session.trade.count']==3 and v['session.trade.volume']==10 and v['session.trade.notional']==1011
print('Bounded supplied-chunk lifecycle and explicit prefix/final certificates verified.')
