"""Checked exact bar reductions with independent field/reference readiness."""
from __future__ import annotations
from fractions import Fraction
from typing import cast
from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, ContractError, DataKind, EntityKey, ErrorCode,
    FeatureColumn, FeatureResult, InputBinding, QualityRow, Reason, ResultCell,
    ResultMetadata, Status, ValueType, PriceUnit, checked_decimal128, checked_int64,
    require_compatible_inputs, validate_batch,
)
from equity_feature_contracts._implemented import BAR_IDS
from equity_features import __version__


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


def compute_bars(batch: CanonicalBatch | None, config: ConfigSpec, *, entity: EntityKey,
                 prior_close: CanonicalBatch | None = None) -> FeatureResult:
    """Compute twelve bar/price IDs for a caller-certified target, without fetching."""
    policy = _policy(config)
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "typed target entity/config identity required")
    if batch is not None: _admit(batch,config,entity,policy)
    if prior_close is not None:
        _admit(prior_close,config,entity,policy,prior=True)
        if batch is not None: require_compatible_inputs(batch,prior_close)
    inputs = tuple(InputBinding(role,b.kind,b.metadata) for role,b in (("bars",batch),("prior_close",prior_close)) if b is not None)
    metadata = ResultMetadata(config.session.namespace,entity.session_id,config.availability,config.digest,inputs,"python-exact",__version__)
    columns = _columns(batch) if batch is not None else {}
    expected = batch.metadata.coverage.expected if batch is not None else None
    observed = batch.row_count if batch is not None else 0
    qualities: list[QualityRow] = []
    values: list[FeatureColumn] = []
    base_status = Status.AVAILABLE
    base_reasons: tuple[Reason,...] = ()
    if batch is None:
        base_status,base_reasons = Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
    elif not batch.metadata.coverage.complete:
        base_status,base_reasons = Status.INCOMPLETE_COVERAGE,(Reason.GOVERNED_GAP,)
    else:
        report = validate_batch(batch,session=config.session,availability=config.availability,required_fields=())
        if report.knowledge_exclusions:
            base_status = Status.MISSING_INPUT
            base_reasons = tuple(dict.fromkeys(x.reason for x in report.knowledge_exclusions))

    def numbers(name: str) -> tuple[int | None,...] | None:
        return cast(tuple[int | None,...],columns[name]) if name in columns else (() if observed == 0 else None)

    def readiness(fields: tuple[str,...]) -> tuple[Status,tuple[Reason,...]]:
        if base_status != Status.AVAILABLE: return base_status,base_reasons
        for field in fields:
            seq = numbers(field)
            if seq is None: return Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
            if any(x is None for x in seq): return Status.MISSING_INPUT,(Reason.NULL_FIELD,)
        return Status.AVAILABLE,()

    volumes = numbers("volume")
    price_rows = tuple(i for i,v in enumerate(volumes or ()) if v is not None and v > 0)
    scale = 10**cast(PriceUnit,config.price_unit).scale
    aggregate: dict[str,int] = {}
    if readiness(("volume",))[0] == Status.AVAILABLE:
        aggregate["volume"] = checked_int64(sum(cast(tuple[int,...],volumes)))
        for field in ("open","high","low","close"):
            seq = numbers(field)
            if seq is not None and price_rows and all(seq[i] is not None for i in price_rows):
                vals = tuple(cast(int,seq[i]) for i in price_rows)
                aggregate[field] = vals[0] if field == "open" else vals[-1] if field == "close" else max(vals) if field == "high" else min(vals)
        seq = numbers("actual_notional")
        if not price_rows or (seq is not None and all(seq[i] is not None for i in price_rows)):
            aggregate["notional"] = checked_decimal128(sum(cast(int,seq[i]) for i in price_rows)) if price_rows and seq is not None else 0
        closes = numbers("close")
        if price_rows and closes is not None and all(closes[i] is not None for i in price_rows):
            aggregate["proxy_numerator"] = checked_decimal128(sum(cast(int,closes[i])*cast(int,cast(tuple[int | None,...],volumes)[i]) for i in price_rows))

    prior_status = Status.AVAILABLE
    prior_reasons: tuple[Reason,...] = ()
    prior_value: int | None = None
    if prior_close is None:
        prior_status,prior_reasons = Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
    else:
        prior_report = validate_batch(prior_close,availability=config.availability,required_fields=("close",))
        if not prior_close.metadata.coverage.complete:
            prior_status,prior_reasons = Status.INCOMPLETE_COVERAGE,(Reason.GOVERNED_GAP,)
        elif prior_report.knowledge_exclusions:
            prior_status,prior_reasons = Status.MISSING_INPUT,tuple(dict.fromkeys(x.reason for x in prior_report.knowledge_exclusions))
        elif prior_report.missing_fields or prior_report.null_fields:
            prior_status,prior_reasons = Status.MISSING_INPUT,(Reason.ABSENT_INPUT if prior_report.missing_fields else Reason.NULL_FIELD,)
        else:
            prior_value = cast(int,_columns(prior_close)["close"][0])
            if prior_value <= 0:
                raise ContractError(ErrorCode.INVALID_SCHEMA, "positive prior close required")

    for feature_id in BAR_IDS:
        name = feature_id.rsplit(".",1)[1]
        dtype = ValueType.INT64 if name == "volume" else ValueType.DECIMAL128 if name == "notional" else ValueType.FLOAT64
        unit = "shares" if name == "volume" else "currency coefficient / 10^price_scale" if name == "notional" else "currency/share; proxy" if name == "close_weighted_price" else "currency/share" if name in ("open","high","low","close") else "fraction"
        status,reasons = readiness(("volume",))
        value: ResultCell = None
        required = {"open":("open",),"high":("high",),"low":("low",),"close":("close",),"notional":("actual_notional",),"close_weighted_price":("close",),"open_close_return":("open","close"),"range_fraction":("high","low","close"),"close_location":("high","low","close"),"overnight_gap":("open",),"close_close_return":("close",)}.get(name,())
        if status == Status.AVAILABLE:
            if name == "volume": value = aggregate["volume"]
            elif name == "notional" and name in aggregate: value = aggregate[name]
            elif not price_rows:
                status,reasons = Status.NOT_APPLICABLE,(Reason.NO_ELIGIBLE_OBSERVATIONS,)
            elif any(field not in aggregate for field in required):
                status,reasons = Status.MISSING_INPUT,(Reason.ABSENT_INPUT if any(numbers(field) is None for field in required) else Reason.NULL_FIELD,)
            elif name in ("open","high","low","close"): value = float(Fraction(aggregate[name],scale))
            elif name == "close_weighted_price": value = float(Fraction(aggregate["proxy_numerator"],aggregate["volume"]*scale))
            elif name == "open_close_return": value = float(Fraction(aggregate["close"]-aggregate["open"],aggregate["open"]))
            elif name == "range_fraction": value = float(Fraction(aggregate["high"]-aggregate["low"],aggregate["close"]))
            elif name == "close_location":
                width = aggregate["high"]-aggregate["low"]
                if width == 0: status,reasons = Status.NOT_APPLICABLE,(Reason.ZERO_DENOMINATOR,)
                else: value = float(Fraction(aggregate["close"]-aggregate["low"],width))
            elif name in ("overnight_gap","close_close_return"):
                if prior_status != Status.AVAILABLE: status,reasons = prior_status,prior_reasons
                else:
                    numerator = aggregate["open" if name == "overnight_gap" else "close"]
                    value = float(Fraction(numerator-cast(int,prior_value),cast(int,prior_value)))
        values.append(FeatureColumn(feature_id,"v1",dtype,unit,(entity,),(value,)))
        qualities.append(QualityRow(entity,feature_id,status,expected,observed,reasons))
    return FeatureResult(tuple(values),tuple(qualities),metadata)
