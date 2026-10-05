"""Event-weighted normalized quote summaries with explicit sampling and bounded diagnostics."""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction
from typing import cast
from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, Coverage, ContractError, DataKind, EntityKey, ErrorCode,
    EvidenceRow, FeatureColumn, FeatureResult, InputBinding, PriceUnit, QualityRow,
    QuoteObservation, QuoteStateCounts, Reason, ResultCell, ResultMetadata,
    SampledSpread, Status, ValidationReport, ValueType, builtin_registry,
    checked_decimal128, checked_int64, quote_state, validate_batch,
)
from equity_features import __version__
from ._reductions import _QuoteTotals, _quote_values
from .bars import _columns, _policy


def _admit_quotes(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey, policy: str) -> ValidationReport:
    if type(batch) is not CanonicalBatch or batch.kind != DataKind.QUOTE:
        raise ContractError(ErrorCode.INVALID_SCHEMA,"canonical quote batch required")
    meta=batch.metadata
    if meta.namespace != config.session.namespace:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"quote/config namespace mismatch")
    if meta.price_unit != config.price_unit:
        raise ContractError(ErrorCode.INVALID_UNIT,"quote/config price unit mismatch")
    if meta.adjustment != config.adjustment:
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT,"quote/config basis mismatch")
    scope=meta.scope
    if scope is None or scope.eligibility_policy != policy:
        raise ContractError(ErrorCode.INVALID_CONFIG,"compatible explicit quote scope required")
    if (scope.start_ns,scope.end_ns,scope.include_opening_auction,scope.include_closing_auction) != (config.session.open_ns,config.availability.market_cutoff_ns,config.session.include_opening_auction,config.session.include_closing_auction):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"quote target scope mismatch")
    if meta.coverage.observed != batch.row_count:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"quote delivery count mismatch")
    columns=_columns(batch)
    if any(x != entity.instrument_id for x in columns['instrument_id']) or any(x != entity.session_id for x in columns['session_id']):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"one requested quote entity required")
    return validate_batch(batch,session=config.session,availability=config.availability,required_fields=())


def compute_quotes(batch: CanonicalBatch | None, config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    """Two event-weighted quote IDs, never inferred continuous duration coverage."""
    if type(config) is not ConfigSpec:
        raise ContractError(ErrorCode.INVALID_CONFIG,"typed quote config required")
    params={p.name:p.value for p in config.parameters}
    if set(params) != {'eligibility_policy','observation_limit'} or type(params['observation_limit']) is not int or not 0 <= params['observation_limit'] <= 10000:
        raise ContractError(ErrorCode.INVALID_CONFIG,"explicit quote observation_limit0..10000 required")
    limit=params['observation_limit']
    policy=_policy(replace(config,parameters=tuple(p for p in config.parameters if p.name == 'eligibility_policy')))
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"typed quote entity/config required")
    if batch is not None: _admit_quotes(batch,config,entity,policy)
    inputs=(InputBinding('quotes',DataKind.QUOTE,batch.metadata),) if batch is not None else ()
    metadata=ResultMetadata(config.session.namespace,entity.session_id,config.availability,config.digest,inputs,'python-exact-compensated',__version__,limit)
    columns=_columns(batch) if batch is not None else {}
    state=_QuoteTotals(tuple(columns),limit=limit,scale=cast(PriceUnit,config.price_unit).scale)
    if batch is not None:
        known=columns.get('known_at_ns')
        for i in range(batch.row_count):
            reason=config.availability.knowledge_reason(cast(int | None,known[i]) if known is not None else None)
            state.add(columns,i,Reason(reason) if reason is not None else None,batch.metadata.source.input_id)
    coverage=batch.metadata.coverage if batch is not None else Coverage(None,0,False)
    override=(Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)) if batch is None else None
    return state.result(config,entity,coverage,metadata,batch.metadata.sampling if batch is not None else 'trade_snapshot',override)
