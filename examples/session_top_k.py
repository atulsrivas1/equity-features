"""Synthetic bounded original trade evidence; all input is caller-owned in memory."""
from dataclasses import replace
from equity_feature_contracts import EntityKey, Parameter, TopKTrades
from equity_features.session import compute_top_k
from session_trades import batch, config
c=replace(config,parameters=config.parameters+(Parameter('top_k',2),Parameter('evidence_limit',2)))
r=compute_top_k(batch,c,entity=EntityKey('A','S'))
v=r.values[0].values[0]
assert isinstance(v,TopKTrades)
assert [x.event_id for x in v.rows] == ['t3','t2']
assert [e.row_id for e in r.evidence] == ['t3','t2']
print('Bounded deterministic topK original trade rows and provenance verified.')
