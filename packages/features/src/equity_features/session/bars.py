"""Checked exact bar reductions with independent field/reference readiness."""
from __future__ import annotations
from dataclasses import replace
from fractions import Fraction
from typing import cast
from equity_feature_contracts import (
    CanonicalBatch, Column, ConfigSpec, ContractError, Coverage, DataKind, EntityKey, ErrorCode,
    FeatureColumn, FeatureResult, InputBinding, QualityRow, Reason, ResultCell,
    ResultMetadata, Status, ValueType, PriceUnit, InputScope, IntervalOHLCV,
    IntervalOHLCVRow, IntervalVolumeShares, IntervalVolumeShareRow, checked_decimal128, checked_int64,
    require_compatible_inputs, validate_batch,
)
from equity_feature_contracts._implemented import BAR_IDS
from equity_features import __version__
from ._reductions import _BarTotals


def _columns(batch: CanonicalBatch) -> dict[str, tuple[int | str | bool | None, ...]]:
    return {c.name:c.values for c in batch.columns}


def _policy(config: ConfigSpec) -> str:
    if type(config) is not ConfigSpec or config.algorithm_version != "v1":
        raise ContractError(ErrorCode.INVALID_CONFIG, "typed v1 bar configuration required")
    if config.price_unit is None or not config.session.open_ns < config.availability.market_cutoff_ns <= config.session.close_ns:
        raise ContractError(ErrorCode.INVALID_CONFIG, "explicit price unit and positive target required")
    params = {p.name:p.value for p in config.parameters}
    if set(params) != {"eligibility_policy"} or type(params["eligibility_policy"]) is not str or not params["eligibility_policy"].strip():
        raise ContractError(ErrorCode.INVALID_CONFIG, "only explicit eligibility_policy is supported by bars")
    return params["eligibility_policy"]


def _admit(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey, policy: str, *, prior: bool = False) -> None:
    if type(batch) is not CanonicalBatch or batch.kind != (DataKind.DAILY if prior else DataKind.BAR):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "canonical daily prior close or bar target required")
    meta = batch.metadata
    if meta.namespace != config.session.namespace:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "input/config namespace mismatch")
    if meta.price_unit != config.price_unit:
        raise ContractError(ErrorCode.INVALID_UNIT, "input/config price unit mismatch")
    if meta.adjustment != config.adjustment:
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "input/config adjustment evidence mismatch")
    scope = meta.scope
    if scope is None or scope.eligibility_policy != policy:
        raise ContractError(ErrorCode.INVALID_CONFIG, "input scope and compatible eligibility policy required")
    if not prior and (scope.start_ns != config.session.open_ns or scope.end_ns != config.availability.market_cutoff_ns or scope.include_opening_auction != config.session.include_opening_auction or scope.include_closing_auction != config.session.include_closing_auction):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "target scope/auction construction mismatch")
    if prior:
        if scope.end_ns > config.session.open_ns:
            raise ContractError(ErrorCode.BOUNDS, "prior input scope extends into target")
        if scope.include_opening_auction != config.session.include_opening_auction or scope.include_closing_auction != config.session.include_closing_auction:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "incompatible prior auction construction")
    if meta.coverage.observed != batch.row_count:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "family batch must bind its actual observed population")
    columns = _columns(batch)
    target_id = entity.session_id
    if prior:
        slots = config.window.governed_sessions
        index = slots.index(entity.session_id)
        if index == 0:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "no governed preceding session")
        target_id = slots[index-1]
        if batch.row_count != 1:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "one prior daily observation required")
    if any(x != entity.instrument_id for x in columns["instrument_id"]) or any(x != target_id for x in columns["session_id"]):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "single requested instrument/session required")
    starts = cast(tuple[int,...],columns["start_ns"])
    ends = cast(tuple[int,...],columns["end_ns"])
    if any(a < scope.start_ns or b > scope.end_ns for a,b in zip(starts,ends,strict=True)):
        raise ContractError(ErrorCode.BOUNDS, "interval outside declared input coverage scope")
    if prior and (starts[0] != scope.start_ns or ends[0] != scope.end_ns):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "prior daily observation must cover declared prior scope")
    validate_batch(batch, session=None if prior else config.session, availability=config.availability, required_fields=())


def _prior_info(prior_close: CanonicalBatch | None, config: ConfigSpec) -> tuple[Status,tuple[Reason,...],int | None]:
    if prior_close is None: return Status.MISSING_INPUT,(Reason.ABSENT_INPUT,),None
    report=validate_batch(prior_close,availability=config.availability,required_fields=("close",))
    if not prior_close.metadata.coverage.complete: return Status.INCOMPLETE_COVERAGE,(Reason.GOVERNED_GAP,),None
    if report.knowledge_exclusions: return Status.MISSING_INPUT,tuple(dict.fromkeys(x.reason for x in report.knowledge_exclusions)),None
    if report.missing_fields or report.null_fields:
        return Status.MISSING_INPUT,(Reason.ABSENT_INPUT if report.missing_fields else Reason.NULL_FIELD,),None
    value=cast(int,_columns(prior_close)["close"][0])
    if value <= 0: raise ContractError(ErrorCode.INVALID_SCHEMA,"positive prior close required")
    return Status.AVAILABLE,(),value


def compute_bars(batch: CanonicalBatch | None, config: ConfigSpec, *, entity: EntityKey,
                 prior_close: CanonicalBatch | None = None) -> FeatureResult:
    """Twelve bar/price IDs using the same fixed-retention reduction as updates."""
    policy=_policy(config)
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"typed target entity/config identity required")
    if batch is not None: _admit(batch,config,entity,policy)
    if prior_close is not None:
        _admit(prior_close,config,entity,policy,prior=True)
        if batch is not None: require_compatible_inputs(batch,prior_close)
    inputs=tuple(InputBinding(role,b.kind,b.metadata) for role,b in (("bars",batch),("prior_close",prior_close)) if b is not None)
    metadata=ResultMetadata(config.session.namespace,entity.session_id,config.availability,config.digest,inputs,"python-exact",__version__)
    columns=_columns(batch) if batch is not None else {}
    state=_BarTotals(tuple(columns))
    if batch is not None:
        known=columns.get("known_at_ns")
        for i in range(batch.row_count):
            reason=config.availability.knowledge_reason(cast(int | None,known[i]) if known is not None else None)
            state.add(columns,i,Reason(reason) if reason is not None else None)
    coverage=batch.metadata.coverage if batch is not None else Coverage(None,0,False)
    override=(Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)) if batch is None else None
    return state.result(config,entity,coverage,metadata,_prior_info(prior_close,config),override)


def compute_structure(batch: CanonicalBatch | None, config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    """Whole-bar interval OHLCV and shares with explicitly scoped delivery evidence."""
    policy = _policy(config)
    if not config.session.intervals:
        raise ContractError(ErrorCode.INVALID_CONFIG,"at least one supplied interval required")
    whole = compute_bars(batch,config,entity=entity)
    total = next(c.values[0] for c in whole.values if c.feature_id == "session.bar.volume")
    total_quality = next(q for q in whole.quality if q.feature_id == "session.bar.volume")
    ohlcv_id = "session.structure.interval_ohlcv"
    share_id = "session.structure.interval_volume_share"
    if batch is None:
        return FeatureResult((FeatureColumn(ohlcv_id,"v1",ValueType.INTERVAL_OHLCV,"currency/share; shares",(entity,),(None,)),FeatureColumn(share_id,"v1",ValueType.INTERVAL_VOLUME_SHARES,"fraction",(entity,),(None,))),tuple(QualityRow(entity,f,Status.MISSING_INPUT,None,0,(Reason.ABSENT_INPUT,)) for f in (ohlcv_id,share_id)),whole.metadata)
    ohlcv_rows: list[IntervalOHLCVRow] = []
    share_rows: list[IntervalVolumeShareRow] = []
    columns = _columns(batch) if batch is not None else {}
    declared = {x.name:x for x in batch.metadata.interval_coverage} if batch is not None else {}
    configured = {x.name:x for x in config.session.intervals}
    for name,item in declared.items():
        if name not in configured or (item.start_ns,item.end_ns) != (configured[name].start_ns,configured[name].end_ns):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"interval delivery/config identity mismatch")
    for interval in config.session.intervals:
        selected: tuple[int,...] = ()
        if batch is not None:
            starts = cast(tuple[int,...],columns["start_ns"])
            ends = cast(tuple[int,...],columns["end_ns"])
            if any(a < bound < b for a,b in zip(starts,ends,strict=True) for bound in (interval.start_ns,interval.end_ns)):
                raise ContractError(ErrorCode.BOUNDS,"requested interval straddles a whole bar")
            selected = tuple(i for i,(a,b) in enumerate(zip(starts,ends,strict=True)) if interval.start_ns <= a and b <= interval.end_ns)
        delivery = declared.get(interval.name)
        observed = len(selected)
        expected = delivery.coverage.expected if delivery is not None else None
        if delivery is not None and delivery.coverage.observed != observed:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"interval coverage population mismatch")
        qstatus = Status.AVAILABLE
        qreasons: tuple[Reason,...] = ()
        if batch is None:
            qstatus,qreasons = Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
        elif interval.end_ns > config.availability.market_cutoff_ns or delivery is None or not delivery.coverage.complete:
            qstatus,qreasons = Status.INCOMPLETE_COVERAGE,(Reason.GOVERNED_GAP,)
        volume: int | None = None
        prices: tuple[float | None,...] = (None,None,None,None)
        volume_status,volume_reasons = qstatus,qreasons
        if qstatus == Status.AVAILABLE and batch is not None and delivery is not None:
            scoped_metadata = replace(batch.metadata,scope=InputScope(interval.start_ns,interval.end_ns,policy,config.session.include_opening_auction,config.session.include_closing_auction),coverage=delivery.coverage,interval_coverage=())
            scoped = replace(batch,columns=tuple(Column(c.name,tuple(c.values[i] for i in selected)) for c in batch.columns),metadata=scoped_metadata)
            # Transient reduction bounds are a window, not a new exchange calendar.
            # The public result retains the original target configuration/identity.
            session = replace(config.session,open_ns=interval.start_ns,close_ns=interval.end_ns,intervals=(),scheduled_close_ns=None,early_close=False)
            timing = replace(config.availability,market_cutoff_ns=interval.end_ns)
            reduced = compute_bars(scoped,replace(config,session=session,availability=timing),entity=entity)
            reduced_values = {c.feature_id.rsplit(".",1)[1]:c.values[0] for c in reduced.values}
            reduced_quality = {q.feature_id.rsplit(".",1)[1]:q for q in reduced.quality}
            volume_quality = reduced_quality["volume"]
            volume_status,volume_reasons = volume_quality.status,volume_quality.reasons
            volume = cast(int | None,reduced_values["volume"])
            qstatus,qreasons = volume_status,volume_reasons
            if qstatus == Status.AVAILABLE and volume != 0:
                bad = next((reduced_quality[x] for x in ("open","high","low","close") if reduced_quality[x].status != Status.AVAILABLE),None)
                if bad is not None: qstatus,qreasons = bad.status,bad.reasons
                else: prices = tuple(cast(float,reduced_values[x]) for x in ("open","high","low","close"))
        ohlcv_quality = QualityRow(entity,ohlcv_id,qstatus,expected,observed,qreasons)
        ohlcv_rows.append(IntervalOHLCVRow(interval,prices[0],prices[1],prices[2],prices[3],volume if qstatus == Status.AVAILABLE else None,ohlcv_quality))
        share_status,share_reasons = volume_status,volume_reasons
        share: float | None = None
        if share_status == Status.AVAILABLE:
            if total_quality.status != Status.AVAILABLE:
                share_status,share_reasons = total_quality.status,total_quality.reasons
            elif total == 0:
                share_status,share_reasons = Status.NOT_APPLICABLE,(Reason.ZERO_DENOMINATOR,)
            else: share = float(Fraction(cast(int,volume),cast(int,total)))
        share_rows.append(IntervalVolumeShareRow(interval,share,QualityRow(entity,share_id,share_status,expected,observed,share_reasons)))
    tables: tuple[IntervalOHLCV | IntervalVolumeShares,...] = (IntervalOHLCV(tuple(ohlcv_rows)),IntervalVolumeShares(tuple(share_rows)))
    features: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    for feature_id,dtype,unit,table in zip((ohlcv_id,share_id),(ValueType.INTERVAL_OHLCV,ValueType.INTERVAL_VOLUME_SHARES),("currency/share; shares","fraction"),tables,strict=True):
        ready=sum(row.quality.status == Status.AVAILABLE for row in table.rows)
        reasons=tuple(dict.fromkeys(reason for row in table.rows for reason in row.quality.reasons))
        status=Status.AVAILABLE if ready == len(table.rows) else Status.INCOMPLETE_COVERAGE
        features.append(FeatureColumn(feature_id,"v1",dtype,unit,(entity,),(table,)))
        quality.append(QualityRow(entity,feature_id,status,len(table.rows),ready,reasons))
    return FeatureResult(tuple(features),tuple(quality),replace(whole.metadata,backend_version=__version__))
