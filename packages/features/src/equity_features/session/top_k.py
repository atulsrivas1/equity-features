"""Bounded deterministic largest-trade rows; no source access or implicit merge."""
from __future__ import annotations
from dataclasses import replace
from typing import cast
from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, Coverage, ContractError, DataKind, EntityKey, ErrorCode,
    EvidenceRow, FeatureColumn, FeatureResult, InputBinding, QualityRow, Reason,
    ResultMetadata, Status, TopKTradeRow, TopKTrades, ValueType, builtin_registry,
    validate_batch,
)
from equity_features import __version__
from ._reductions import _TopTotals
from .bars import _columns, _policy
from .trades import _admit_trades


def compute_top_k(batch: CanonicalBatch | None, config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    """Rank up toK eligible original trade rows, retaining at mostK+1 candidates."""
    if type(config) is not ConfigSpec:
        raise ContractError(ErrorCode.INVALID_CONFIG,"typed topK config required")
    params={p.name:p.value for p in config.parameters}
    if set(params) != {"eligibility_policy","top_k","evidence_limit"}:
        raise ContractError(ErrorCode.INVALID_CONFIG,"explicit eligibility/topK/evidence parameters required")
    k=params["top_k"];limit=params["evidence_limit"]
    if type(k) is not int or not 1 <= k <= 10000 or type(limit) is not int or not k <= limit <= 10000:
        raise ContractError(ErrorCode.INVALID_CONFIG,"1<=K<=evidence_limit<=10000 required")
    policy_config=replace(config,parameters=tuple(p for p in config.parameters if p.name == "eligibility_policy"))
    policy=_policy(policy_config)
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"typed target entity/config identity required")
    if batch is not None: _admit_trades(batch,config,entity,policy)
    inputs=(InputBinding("trades",DataKind.TRADE,batch.metadata),) if batch is not None else ()
    metadata=ResultMetadata(config.session.namespace,entity.session_id,config.availability,config.digest,inputs,"python-exact",__version__,limit)
    columns=_columns(batch) if batch is not None else {}
    state=_TopTotals(tuple(columns),k=k)
    if batch is not None:
        known=columns.get("known_at_ns")
        for i in range(batch.row_count):
            reason=config.availability.knowledge_reason(cast(int | None,known[i]) if known is not None else None)
            state.add(columns,i,Reason(reason) if reason is not None else None,batch.metadata.source.input_id)
    coverage=batch.metadata.coverage if batch is not None else Coverage(None,0,False)
    override=(Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)) if batch is None else None
    return state.result(config,entity,coverage,metadata,override)
