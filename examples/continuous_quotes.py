"""Synthetic continuous update integral; source data is supplied in memory."""
from dataclasses import replace
from equity_feature_contracts import AvailabilitySpec, Column, EntityKey, Parameter, TimeWeightedSpread
from equity_features.session import compute_time_weighted
from session_quotes import batch, config
c=replace(config,parameters=(Parameter('eligibility_policy','example-v1'),Parameter('max_age_ns',6),Parameter('initial_state','unknown')),
    session=replace(config.session,close_ns=112),availability=AvailabilitySpec(112,200,200))
b=replace(batch,columns=tuple(Column(x.name,(100,103,107,109) if x.name in ('event_ns','known_at_ns') else x.values) for x in batch.columns),metadata=replace(batch.metadata,sampling='continuous',scope=replace(batch.metadata.scope,end_ns=112)))
r=compute_time_weighted(b,c,entity=EntityKey('A','S'));v=r.values[0].values[0]
assert isinstance(v,TimeWeightedSpread)
assert (v.durations.normal,v.durations.locked,v.durations.crossed,v.durations.invalid)==(3,4,2,3)
assert v.durations.valid==7 and v.durations.total==12
assert abs(v.mean_spread-6/7)<1e-12 and abs(v.mean_bps-60000/707)<1e-12
print('Continuous quote expiry, duration conservation and valid time weights verified.')
