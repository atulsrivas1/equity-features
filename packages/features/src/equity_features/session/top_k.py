"""Bounded deterministic largest-trade rows; no source access or implicit merge."""
from __future__ import annotations
from dataclasses import replace
from typing import cast
from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, ContractError, DataKind, EntityKey, ErrorCode,
    EvidenceRow, FeatureColumn, FeatureResult, InputBinding, QualityRow, Reason,
    ResultMetadata, Status, TopKTradeRow, TopKTrades, ValueType, builtin_registry,
    validate_batch,
)
from equity_features import __version__
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
    feature_id="session.trade.top_k"
    inputs=(InputBinding("trades",DataKind.TRADE,batch.metadata),) if batch is not None else ()
    metadata=ResultMetadata(config.session.namespace,entity.session_id,config.availability,config.digest,inputs,"python-exact",__version__,limit)
    expected=batch.metadata.coverage.expected if batch is not None else None
    observed=batch.row_count if batch is not None else 0
    status=Status.AVAILABLE
    reasons: tuple[Reason,...]=()
    if batch is None: status,reasons=Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
    elif not batch.metadata.coverage.complete: status,reasons=Status.INCOMPLETE_COVERAGE,(Reason.GOVERNED_GAP,)
    else:
        report=validate_batch(batch,session=config.session,availability=config.availability,required_fields=())
        if report.knowledge_exclusions:
            status,reasons=Status.MISSING_INPUT,tuple(dict.fromkeys(x.reason for x in report.knowledge_exclusions))
    columns=_columns(batch) if batch is not None else {}
    if status == Status.AVAILABLE and any(x is True for x in columns.get("eligible",())) and not {"price","size"} <= set(columns):
        status,reasons=Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
    known = columns.get("known_at_ns")
    retained: list[TopKTradeRow]=[]
    if status == Status.AVAILABLE and batch is not None:
        for i,eligible in enumerate(columns["eligible"]):
            if eligible is not True: continue
            row=TopKTradeRow(batch.metadata.source.input_id,cast(str,columns["event_id"][i]),cast(int,columns["event_ns"][i]),cast(int,columns["order_key"][i]),cast(int | None,known[i]) if known is not None else None,cast(int,columns["price"][i]),cast(int,columns["size"][i]))
            retained.append(row);retained.sort(key=lambda x:x.rank_key)
            if len(retained) > k: retained.pop()
    value=TopKTrades(k,tuple(retained)) if status == Status.AVAILABLE else None
    evidence=tuple(EvidenceRow(entity,feature_id,x.input_id,x.event_id,x.event_ns,x.known_at_ns,boundary="closing_auction" if x.event_ns == config.availability.market_cutoff_ns else "ordinary") for x in retained)
    output=builtin_registry().get(feature_id).outputs[0]
    return FeatureResult((FeatureColumn(feature_id,"v1",ValueType.TOP_K_TRADES,output.unit,(entity,),(value,)),),(QualityRow(entity,feature_id,status,expected,observed,reasons),),metadata,evidence)
