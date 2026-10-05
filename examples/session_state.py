"""Synthetic exact in-memory restore; the caller retains original declarations."""
from equity_feature_contracts import EntityKey, PrefixCoverage, Coverage, StreamPopulation
from equity_features.incremental import SessionAccumulator
from session_incremental import chunk
from session_trades import batch, config
population=StreamPopulation.from_batch(batch)
a=SessionAccumulator('trades',config,entity=EntityKey('A','S'),population=population)
a.update(chunk([0]),start_ordinal=0)
saved=a.export_state()
b=SessionAccumulator.restore_state(saved,'trades',config,entity=EntityKey('A','S'),population=population)
assert b.export_state()==saved
for calc in (a,b):calc.update(chunk([1,2]),start_ordinal=1)
assert a.finalize(PrefixCoverage(200,Coverage(3,3,True)))==b.finalize(PrefixCoverage(200,Coverage(3,3,True)))
print('Exact owned in-memory state and compatible restored execution verified.')
