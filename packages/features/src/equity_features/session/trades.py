"""Eligible trade aggregates using checked exact numerators, without source access."""
from __future__ import annotations
from fractions import Fraction
from typing import cast
from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, ContractError, DataKind, EntityKey, ErrorCode,
    FeatureColumn, FeatureResult, InputBinding, PriceUnit, QualityRow, Reason,
    ResultCell, ResultMetadata, Status, ValueType, builtin_registry,
    checked_decimal128, checked_int64, validate_batch,
)
from equity_feature_contracts._implemented import TRADE_IDS
from equity_features import __version__
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
    """Five trade aggregates; missing price/size affects only dependent features."""
    policy = _policy(config)
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"typed target entity/config identity required")
    if batch is not None: _admit_trades(batch,config,entity,policy)
    inputs = (InputBinding("trades",DataKind.TRADE,batch.metadata),) if batch is not None else ()
    metadata = ResultMetadata(config.session.namespace,entity.session_id,config.availability,config.digest,inputs,"python-exact",__version__)
    expected = batch.metadata.coverage.expected if batch is not None else None
    observed = batch.row_count if batch is not None else 0
    columns = _columns(batch) if batch is not None else {}
    eligible = tuple(i for i,x in enumerate(columns.get("eligible",())) if x is True)
    base_status = Status.AVAILABLE
    base_reasons: tuple[Reason,...] = ()
    if batch is None: base_status,base_reasons = Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
    elif not batch.metadata.coverage.complete:
        base_status,base_reasons = Status.INCOMPLETE_COVERAGE,(Reason.GOVERNED_GAP,)
    else:
        report = validate_batch(batch,session=config.session,availability=config.availability,required_fields=())
        if report.knowledge_exclusions:
            base_status,base_reasons = Status.MISSING_INPUT,tuple(dict.fromkeys(x.reason for x in report.knowledge_exclusions))

    def readiness(fields: tuple[str,...]) -> tuple[Status,tuple[Reason,...]]:
        if base_status != Status.AVAILABLE: return base_status,base_reasons
        if not eligible: return Status.AVAILABLE,()
        for field in fields:
            if field not in columns: return Status.MISSING_INPUT,(Reason.ABSENT_INPUT,)
            if any(columns[field][i] is None for i in eligible):
                return Status.MISSING_INPUT,(Reason.NULL_FIELD,)
        return Status.AVAILABLE,()

    count = checked_int64(len(eligible))
    volume: int | None = None
    notional: int | None = None
    if readiness(("size",))[0] == Status.AVAILABLE:
        volume = checked_int64(sum(cast(int,columns["size"][i]) for i in eligible))
    if readiness(("price","size"))[0] == Status.AVAILABLE:
        notional = checked_decimal128(sum(cast(int,columns["price"][i])*cast(int,columns["size"][i]) for i in eligible))
    scale = 10**cast(PriceUnit,config.price_unit).scale
    fields = {"count":(),"volume":("size",),"notional":("price","size"),"vwap":("price","size"),"mean_size":("size",)}
    values: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    registry = builtin_registry()
    for feature_id in TRADE_IDS:
        name = feature_id.rsplit(".",1)[1]
        status,reasons = readiness(fields[name])
        value: ResultCell = None
        if status == Status.AVAILABLE:
            if name == "count": value = count
            elif name == "volume": value = volume
            elif name == "notional": value = notional
            elif count == 0: status,reasons = Status.NOT_APPLICABLE,(Reason.NO_ELIGIBLE_OBSERVATIONS,)
            elif name == "vwap": value = float(Fraction(cast(int,notional),cast(int,volume)*scale))
            else: value = float(Fraction(cast(int,volume),count))
        output = registry.get(feature_id).outputs[0]
        values.append(FeatureColumn(feature_id,"v1",ValueType(output.dtype),output.unit,(entity,),(value,)))
        quality.append(QualityRow(entity,feature_id,status,expected,observed,reasons))
    return FeatureResult(tuple(values),tuple(quality),metadata)
