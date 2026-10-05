"""Explicit synthetic window coverage; importing session_bars supplies no source I/O."""
from dataclasses import replace
from equity_feature_contracts import Coverage, EntityKey, IntervalCoverage, IntervalSpec, IntervalVolumeShares
from equity_features.session import compute_structure
from session_bars import batch, config

windows=(IntervalSpec("first",100,150),IntervalSpec("last",150,200))
config=replace(config,session=replace(config.session,intervals=windows))
batch=replace(batch,metadata=replace(batch.metadata,interval_coverage=tuple(
    IntervalCoverage(w.name,w.start_ns,w.end_ns,Coverage(1,1,True)) for w in windows)))
result=compute_structure(batch,config,entity=EntityKey("A","S"))
shares=result.values[1].values[0]
assert isinstance(shares,IntervalVolumeShares)
assert [row.share for row in shares.rows] == [.4,.6]
print("Whole-bar interval shares and independent window quality verified.")
