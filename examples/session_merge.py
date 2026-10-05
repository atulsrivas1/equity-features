"""Synthetic legal adjacent disjoint merge; caller certifies global ordinals."""
from equity_feature_contracts import EntityKey, PartitionSpan, PrefixCoverage, Coverage, StreamPopulation
from equity_features.incremental import SessionAccumulator
from session_incremental import chunk
from session_trades import batch, config
population=StreamPopulation.from_batch(batch)
def partition(indices):
    a=SessionAccumulator('trades',config,entity=EntityKey('A','S'),population=population)
    a.update(chunk(indices),start_ordinal=0)
    return a
left=partition([0]);right=partition([1,2]);saved=left.export_state()
a=left.merge_partitions(right,left=PartitionSpan(0,1),right=PartitionSpan(1,3))
assert left.export_state()==saved
values={x.feature_id:x.values[0] for x in a.finalize(PrefixCoverage(200,Coverage(3,3,True))).values}
assert values['session.trade.volume']==10 and values['session.trade.notional']==1011
print('Owned legal adjacent partition merge and exact aggregate golden verified.')
