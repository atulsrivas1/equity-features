"""Event-weighted normalized quote summaries with explicit sampling and bounded diagnostics."""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction
from typing import cast
from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, ContractError, DataKind, EntityKey, ErrorCode,
    EvidenceRow, FeatureColumn, FeatureResult, InputBinding, PriceUnit, QualityRow,
    QuoteObservation, QuoteStateCounts, Reason, ResultCell, ResultMetadata,
    SampledSpread, Status, ValidationReport, ValueType, builtin_registry,
    checked_decimal128, checked_int64, quote_state, validate_batch,
)
from equity_features import __version__
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


def _quote_values(bid: int | None, ask: int | None, scale: int) -> tuple[str,float | None,float | None]:
    state=quote_state(bid,ask)
    if state == 'invalid': return state,None,None
    b=cast(int,bid);a=cast(int,ask)
    return state,float(Fraction(a-b,10**scale)),float(Fraction(20000*(a-b),a+b))


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
    report=_admit_quotes(batch,config,entity,policy) if batch is not None else None
    inputs=(InputBinding('quotes',DataKind.QUOTE,batch.metadata),) if batch is not None else ()
    metadata=ResultMetadata(config.session.namespace,entity.session_id,config.availability,config.digest,inputs,'python-exact-compensated',__version__,limit)
    expected=batch.metadata.coverage.expected if batch is not None else None
    observed=batch.row_count if batch is not None else 0
    status=Status.AVAILABLE
    reasons: tuple[Reason,...]=()
    columns=_columns(batch) if batch is not None else {}
    if batch is None: status,reasons=Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
    elif not batch.metadata.coverage.complete: status,reasons=Status.INCOMPLETE_COVERAGE,(Reason.GOVERNED_GAP,)
    elif report is not None and report.knowledge_exclusions:
        status,reasons=Status.MISSING_INPUT,tuple(dict.fromkeys(x.reason for x in report.knowledge_exclusions))
    elif observed and not {'bid','ask'} <= set(columns):
        status,reasons=Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
    counts={'normal':0,'locked':0,'crossed':0,'invalid':0}
    spread_sum=0;bps_sum=0.0;compensation=0.0
    scale=cast(PriceUnit,config.price_unit).scale
    retained: list[QuoteObservation]=[]
    if status == Status.AVAILABLE and batch is not None:
        known=columns.get('known_at_ns')
        for i in range(batch.row_count):
            bid=cast(int | None,columns['bid'][i]);ask=cast(int | None,columns['ask'][i])
            state,spread,bps=_quote_values(bid,ask,scale);counts[state]+=1
            if state in ('normal','locked'):
                spread_sum=checked_decimal128(spread_sum+cast(int,ask)-cast(int,bid))
                adjusted=cast(float,bps)-compensation
                updated=bps_sum+adjusted;compensation=(updated-bps_sum)-adjusted;bps_sum=updated
            if len(retained) < limit:
                retained.append(QuoteObservation(batch.metadata.source.input_id,cast(str,columns['event_id'][i]),cast(int,columns['event_ns'][i]),cast(int,columns['order_key'][i]),cast(int | None,known[i]) if known is not None else None,bid,ask,state,spread,bps))
    count_value=QuoteStateCounts(*(checked_int64(counts[x]) for x in ('normal','locked','crossed','invalid')))
    sampled_status=status;sampled_reasons=reasons
    sample_value: ResultCell=None
    if status == Status.AVAILABLE and batch is not None:
        valid=count_value.valid
        if not valid: sampled_status,sampled_reasons=Status.NOT_APPLICABLE,(Reason.NO_ELIGIBLE_OBSERVATIONS,)
        sample_value=SampledSpread(batch.metadata.sampling,count_value.total,valid,float(Fraction(spread_sum,valid*10**scale)) if valid else None,bps_sum/valid if valid else None,limit,tuple(retained))
    registry=builtin_registry()
    count_id='session.quote.state_counts';sample_id='session.quote.sampled_spread'
    values=(FeatureColumn(sample_id,'v1',ValueType.SAMPLED_SPREAD,registry.get(sample_id).outputs[0].unit,(entity,),(sample_value,)),FeatureColumn(count_id,'v1',ValueType.QUOTE_STATE_COUNTS,registry.get(count_id).outputs[0].unit,(entity,),(count_value if status == Status.AVAILABLE else None,)))
    quality=(QualityRow(entity,sample_id,sampled_status,expected,observed,sampled_reasons),QualityRow(entity,count_id,status,expected,observed,reasons))
    evidence=tuple(EvidenceRow(entity,sample_id,x.input_id,x.event_id,x.event_ns,x.known_at_ns) for x in retained)
    return FeatureResult(values,quality,metadata,evidence)
