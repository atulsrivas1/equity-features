"""Continuous quote integration with original-anchor expiry and explicit initialization."""
from __future__ import annotations
from dataclasses import dataclass, field, replace
from fractions import Fraction
from typing import cast
from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, ContractError, DataKind, EntityKey, ErrorCode,
    EvidenceRow, FeatureColumn, FeatureResult, InputBinding, PriceUnit, QualityRow,
    QuoteDurations, Reason, ResultMetadata, Status, TimeWeightedSpread, ValueType,
    builtin_registry, checked_decimal128, checked_int64, validate_batch,
)
from equity_features import __version__
from .bars import _columns, _policy
from .quotes import _admit_quotes, _quote_values

_CATEGORIES=('normal','locked','crossed','invalid','expired','unknown')

@dataclass
class _TimeReducer:
    cursor: int
    max_age_ns: int
    scale: int
    state: str = 'unknown'
    anchor: int | None = None
    bid: int | None = None
    ask: int | None = None
    duration: dict[str,int] = field(default_factory=lambda:{x:0 for x in _CATEGORIES})
    spread_sum: int = 0
    bps_sum: float = 0.0
    compensation: float = 0.0

    def _add(self, state: str, duration: int) -> None:
        if duration == 0: return
        self.duration[state]=checked_int64(self.duration[state]+duration)
        if state in ('normal','locked'):
            self.spread_sum=checked_decimal128(self.spread_sum+(cast(int,self.ask)-cast(int,self.bid))*duration)
            bps=cast(float,_quote_values(self.bid,self.ask,self.scale)[2])
            adjusted=bps*duration-self.compensation
            updated=self.bps_sum+adjusted;self.compensation=(updated-self.bps_sum)-adjusted;self.bps_sum=updated

    def advance(self, end_ns: int) -> None:
        if end_ns < self.cursor:
            raise ContractError(ErrorCode.BOUNDS,'cannot integrate an earlier cutoff')
        expiry=self.anchor+self.max_age_ns if self.anchor is not None else None
        fresh_end=end_ns if expiry is None else max(self.cursor,min(end_ns,expiry))
        self._add(self.state,checked_int64(fresh_end-self.cursor))
        self._add('expired',checked_int64(end_ns-fresh_end))
        self.cursor=end_ns

    def update(self, event_ns: int, bid: int | None, ask: int | None) -> None:
        self.advance(event_ns)
        self.state=_quote_values(bid,ask,self.scale)[0]
        self.anchor=event_ns;self.bid=bid;self.ask=ask

    def summary(self, initial_state: str) -> TimeWeightedSpread:
        durations=QuoteDurations(*(self.duration[x] for x in _CATEGORIES))
        ready=durations.valid > 0 and durations.unknown == 0
        return TimeWeightedSpread(durations,float(Fraction(self.spread_sum,durations.valid*10**self.scale)) if ready else None,self.bps_sum/durations.valid if ready else None,self.max_age_ns,initial_state)


def _admit_seed(seed: CanonicalBatch, config: ConfigSpec, entity: EntityKey, policy: str, target: CanonicalBatch | None) -> Reason | None:
    if type(seed) is not CanonicalBatch or seed.kind != DataKind.QUOTE or seed.row_count != 1:
        raise ContractError(ErrorCode.INVALID_SCHEMA,'one canonical quote seed required')
    meta=seed.metadata
    if meta.sampling != 'continuous':
        raise ContractError(ErrorCode.UNSUPPORTED_SAMPLING,'continuous seed required')
    if meta.namespace != config.session.namespace:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'seed namespace mismatch')
    if meta.price_unit != config.price_unit:
        raise ContractError(ErrorCode.INVALID_UNIT,'seed price unit mismatch')
    if meta.adjustment != config.adjustment:
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT,'seed adjustment mismatch')
    if not meta.coverage.complete or meta.coverage.observed != 1:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'complete one-row seed delivery required')
    columns=_columns(seed)
    if not {'bid','ask'} <= set(columns):
        raise ContractError(ErrorCode.INVALID_SCHEMA,'seed sides must be supplied; null explicitly allowed')
    if columns['instrument_id'][0] != entity.instrument_id or columns['session_id'][0] != entity.session_id:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'seed entity mismatch')
    event=cast(int,columns['event_ns'][0]);scope=meta.scope
    if scope is None or scope.eligibility_policy != policy or not scope.start_ns <= event < scope.end_ns <= config.session.open_ns:
        raise ContractError(ErrorCode.BOUNDS,'seed must lie in compatible supplied preopen scope')
    if target is not None:
        source=target.metadata.source
        if (meta.source.source_id,meta.source.mapping_version) != (source.source_id,source.mapping_version):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'seed source/mapping incompatible')
        if meta.source.input_id == source.input_id or columns['event_id'][0] in _columns(target)['event_id']:
            raise ContractError(ErrorCode.DUPLICATE,'seed cannot duplicate target input/event identity')
    report=validate_batch(seed,availability=config.availability,required_fields=())
    return report.knowledge_exclusions[0].reason if report.knowledge_exclusions else None


def compute_time_weighted(batch: CanonicalBatch | None, config: ConfigSpec, *, entity: EntityKey, seed: CanonicalBatch | None = None) -> FeatureResult:
    """One continuous metric; unknown initial time never becomes an all-session mean."""
    if type(config) is not ConfigSpec:
        raise ContractError(ErrorCode.INVALID_CONFIG,'typed continuous quote config required')
    params={p.name:p.value for p in config.parameters}
    if set(params) != {'eligibility_policy','max_age_ns','initial_state'} or type(params['max_age_ns']) is not int or not 1 <= params['max_age_ns'] <= 2**63-1 or params['initial_state'] not in ('seed','inactive','unknown'):
        raise ContractError(ErrorCode.INVALID_CONFIG,'explicit positive max age and initialization required')
    age=params['max_age_ns'];initial=cast(str,params['initial_state'])
    policy=_policy(replace(config,parameters=tuple(p for p in config.parameters if p.name == 'eligibility_policy')))
    checked_int64(config.availability.market_cutoff_ns-config.session.open_ns)
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'typed continuous quote entity/config required')
    if initial != 'seed' and seed is not None:
        raise ContractError(ErrorCode.INVALID_CONFIG,'extraneous seed contradicts initialization')
    if batch is not None and (type(batch) is not CanonicalBatch or batch.kind != DataKind.QUOTE):
        raise ContractError(ErrorCode.INVALID_SCHEMA,'canonical continuous quote batch required')
    if batch is not None and batch.metadata.sampling != 'continuous':
        raise ContractError(ErrorCode.UNSUPPORTED_SAMPLING,'time weighting requires continuous quote updates')
    report=_admit_quotes(batch,config,entity,policy) if batch is not None else None
    seed_reason=_admit_seed(seed,config,entity,policy,batch) if seed is not None else Reason.ABSENT_INPUT if initial == 'seed' else None
    inputs: list[InputBinding]=[]
    if batch is not None: inputs.append(InputBinding('quotes',DataKind.QUOTE,batch.metadata))
    if seed is not None: inputs.append(InputBinding('quote_seed',DataKind.QUOTE,seed.metadata))
    metadata=ResultMetadata(config.session.namespace,entity.session_id,config.availability,config.digest,tuple(inputs),'python-exact-compensated',__version__,1)
    expected=batch.metadata.coverage.expected if batch is not None else None
    observed=batch.row_count if batch is not None else 0
    status=Status.AVAILABLE;reasons: tuple[Reason,...]=()
    if batch is None: status,reasons=Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
    elif not batch.metadata.coverage.complete: status,reasons=Status.INCOMPLETE_COVERAGE,(Reason.GOVERNED_GAP,)
    elif report is not None and report.knowledge_exclusions:
        status,reasons=Status.MISSING_INPUT,tuple(dict.fromkeys(x.reason for x in report.knowledge_exclusions))
    elif observed and not {'bid','ask'} <= set(_columns(batch)):
        status,reasons=Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
    value: TimeWeightedSpread | None=None
    evidence: tuple[EvidenceRow,...]=()
    feature_id='session.quote.time_weighted_spread'
    if status == Status.AVAILABLE and batch is not None:
        reducer=_TimeReducer(config.session.open_ns,age,cast(PriceUnit,config.price_unit).scale,state='invalid' if initial == 'inactive' else 'unknown')
        if seed is not None:
            columns=_columns(seed);event=cast(int,columns['event_ns'][0]);known=cast(int | None,columns['known_at_ns'][0]) if 'known_at_ns' in columns else None
            if seed_reason is None:
                reducer.anchor=event;reducer.bid=cast(int | None,columns['bid'][0]);reducer.ask=cast(int | None,columns['ask'][0]);reducer.state=_quote_values(reducer.bid,reducer.ask,reducer.scale)[0]
            evidence=(EvidenceRow(entity,feature_id,seed.metadata.source.input_id,cast(str,columns['event_id'][0]),event,known,use='excluded' if seed_reason is not None else 'consumed',exclusion_reason=seed_reason),)
        columns=_columns(batch)
        for i in range(batch.row_count):
            reducer.update(cast(int,columns['event_ns'][i]),cast(int | None,columns['bid'][i]),cast(int | None,columns['ask'][i]))
        reducer.advance(config.availability.market_cutoff_ns);value=reducer.summary(initial)
        if value.durations.unknown:
            status=Status.INCOMPLETE_COVERAGE;reasons=tuple(dict.fromkeys((Reason.UNKNOWN_AVAILABILITY,)+( (seed_reason,) if seed_reason is not None else () )))
        elif not value.durations.valid: status,reasons=Status.NOT_APPLICABLE,(Reason.ZERO_DENOMINATOR,)
    output=builtin_registry().get(feature_id).outputs[0]
    return FeatureResult((FeatureColumn(feature_id,'v1',ValueType.TIME_WEIGHTED_SPREAD,output.unit,(entity,),(value,)),),(QualityRow(entity,feature_id,status,expected,observed,reasons),),metadata,evidence)
