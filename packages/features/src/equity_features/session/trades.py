"""Eligible trade aggregates using checked exact numerators, without source access."""
from __future__ import annotations
from fractions import Fraction
from typing import cast
from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, Coverage, ContractError, DataKind, EntityKey, ErrorCode,
    FeatureColumn, FeatureResult, InputBinding, PriceUnit, QualityRow, Reason,
    ResultCell, ResultMetadata, Status, ValueType, builtin_registry,
    checked_decimal128, checked_int64, validate_batch,
)
from equity_feature_contracts._implemented import TRADE_IDS
from equity_features import __version__
from ._reductions import _TradeTotals
from .bars import _columns, _policy


def _admit_trades(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey, policy: str) -> None:
    if type(batch) is not CanonicalBatch or batch.kind != DataKind.TRADE:
        raise ContractError(ErrorCode.INVALID_SCHEMA,"canonical trade batch required")
    meta = batch.metadata
    if meta.namespace != config.session.namespace:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"input/config namespace mismatch")
    if meta.price_unit != config.price_unit:
        raise ContractError(ErrorCode.INVALID_UNIT,"input/config price unit mismatch")
    if meta.adjustment != config.adjustment:
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT,"input/config adjustment evidence mismatch")
    scope = meta.scope
    if scope is None or scope.eligibility_policy != policy:
        raise ContractError(ErrorCode.INVALID_CONFIG,"explicit compatible trade input scope required")
    if (scope.start_ns,scope.end_ns,scope.include_opening_auction,scope.include_closing_auction) != (config.session.open_ns,config.availability.market_cutoff_ns,config.session.include_opening_auction,config.session.include_closing_auction):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"target scope/auction construction mismatch")
    if meta.coverage.observed != batch.row_count:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"actual delivered trade population must match coverage")
    columns = _columns(batch)
    if any(x != entity.instrument_id for x in columns["instrument_id"]) or any(x != entity.session_id for x in columns["session_id"]):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"one requested trade entity required")
    validate_batch(batch,session=config.session,availability=config.availability,required_fields=())


def compute_trades(batch: CanonicalBatch | None, config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    """Five eligible aggregates using shared fixed-retention dependency reductions."""
    policy=_policy(config)
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"typed target entity/config identity required")
    if batch is not None: _admit_trades(batch,config,entity,policy)
    inputs=(InputBinding("trades",DataKind.TRADE,batch.metadata),) if batch is not None else ()
    metadata=ResultMetadata(config.session.namespace,entity.session_id,config.availability,config.digest,inputs,"python-exact",__version__)
    columns=_columns(batch) if batch is not None else {}
    state=_TradeTotals(tuple(columns))
    if batch is not None:
        known=columns.get("known_at_ns")
        for i in range(batch.row_count):
            reason=config.availability.knowledge_reason(cast(int | None,known[i]) if known is not None else None)
            state.add(columns,i,Reason(reason) if reason is not None else None)
    coverage=batch.metadata.coverage if batch is not None else Coverage(None,0,False)
    override=(Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)) if batch is None else None
    return state.result(config,entity,coverage,metadata,override)
