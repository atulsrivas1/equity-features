"""Pure semantic checks; no sorting, filtering, arithmetic wrapping or source I/O."""
from __future__ import annotations
from dataclasses import dataclass
from typing import cast
from .errors import ContractError, ErrorCode
from .inputs import CanonicalBatch, Cell, DataKind, I64_MIN, I64_MAX
from .results import Reason
from .specs import AvailabilitySpec, SessionSpec

@dataclass(frozen=True)
class KnowledgeExclusion:
    row_index: int
    reason: Reason

@dataclass(frozen=True)
class ValidationReport:
    row_count: int
    missing_fields: tuple[str, ...]
    null_fields: tuple[tuple[str, int], ...]
    knowledge_exclusions: tuple[KnowledgeExclusion, ...]
    quote_states: tuple[str, ...]

    @property
    def supplied_fields_ready(self) -> bool:
        return not (self.missing_fields or self.null_fields or self.knowledge_exclusions)

def checked_int64(value: int) -> int:
    if type(value) is not int:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "exact integer required")
    if not I64_MIN <= value <= I64_MAX:
        raise ContractError(ErrorCode.OVERFLOW, "int64 arithmetic overflow")
    return value

def checked_decimal128(value: int) -> int:
    if type(value) is not int:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "exact integer coefficient required")
    if not -(10**38) < value < 10**38:
        raise ContractError(ErrorCode.OVERFLOW, "decimal128 arithmetic overflow")
    return value

def checked_sum(values: tuple[int, ...], *, representation: str = "int64") -> int:
    if type(values) not in (tuple,list) or any(type(x) is not int for x in values):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete exact integer sum required")
    if representation not in ("int64","decimal128"):
        raise ContractError(ErrorCode.INVALID_CONFIG, "unsupported sum representation")
    for value in values:
        if representation == "int64": checked_int64(value)
        else: checked_decimal128(value)
    result = sum(values)
    return checked_int64(result) if representation == "int64" else checked_decimal128(result)

def checked_product(left: int, right: int, *, representation: str = "decimal128") -> int:
    checked_int64(left); checked_int64(right)
    if representation not in ("int64","decimal128"):
        raise ContractError(ErrorCode.INVALID_CONFIG, "unsupported product representation")
    value = left * right
    return checked_int64(value) if representation == "int64" else checked_decimal128(value)

def quote_state(bid: int | None, ask: int | None) -> str:
    for value in (bid,ask):
        if value is not None: checked_int64(value)
    if bid is None or ask is None or bid <= 0 or ask <= 0: return "invalid"
    if bid > ask: return "crossed"
    if bid == ask: return "locked"
    return "normal"

def validate_batch(batch: CanonicalBatch, *, session: SessionSpec | None = None,
                   availability: AvailabilitySpec | None = None,
                   required_fields: tuple[str, ...] | None = None) -> ValidationReport:
    if type(batch) is not CanonicalBatch:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete canonical input required")
    if session is not None and type(session) is not SessionSpec:
        raise ContractError(ErrorCode.INVALID_CONFIG, "typed supplied session required")
    if availability is not None and type(availability) is not AvailabilitySpec:
        raise ContractError(ErrorCode.INVALID_CONFIG, "typed supplied timing required")
    if required_fields is not None and type(required_fields) not in (tuple,list):
        raise ContractError(ErrorCode.INVALID_CONFIG, "concrete required field sequence required")
    from .inputs import schema_for
    schema = schema_for(batch.kind)
    for name in required_fields or (): schema.field(name)
    defaults = {DataKind.TRADE:("price","size"),DataKind.QUOTE:("bid","ask"),DataKind.BAR:("open","high","low","close","volume"),DataKind.DAILY:("open","high","low","close","volume"),DataKind.REFERENCE:()}
    required = tuple(dict.fromkeys(defaults[batch.kind] if required_fields is None else required_fields))
    if session is not None and availability is not None and not session.open_ns <= availability.market_cutoff_ns <= session.close_ns:
        raise ContractError(ErrorCode.BOUNDS, "session market cutoff outside actual bounds")
    columns = {c.name:c.values for c in batch.columns}
    missing = tuple(name for name in required if name not in columns)
    nulls = tuple((name,columns[name].count(None)) for name in required if name in columns and None in columns[name])
    exclusions: list[KnowledgeExclusion] = []
    states: list[str] = []
    seen: set[tuple[Cell, ...]] = set()
    last: dict[tuple[Cell, ...], tuple[int, ...]] = {}
    previous_end: dict[tuple[Cell, ...], int] = {}
    reference_last: dict[tuple[Cell, ...], tuple[int, str]] = {}
    for i in range(batch.row_count):
        instrument = columns["instrument_id"][i]; session_id = columns["session_id"][i]
        group = (instrument,session_id)
        def number(name: str) -> int | None:
            return cast(int | None,columns[name][i]) if name in columns else None
        if session is not None and (batch.metadata.namespace != session.namespace or session_id != session.session_id):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "input/supplied session namespace or ID mismatch")
        identity: tuple[Cell, ...]
        if batch.kind in (DataKind.TRADE,DataKind.QUOTE):
            stamp = cast(int,number("event_ns")); order = cast(int,number("order_key"))
            identity = group+(columns["event_id"][i],)
            if identity in seen: raise ContractError(ErrorCode.DUPLICATE, "duplicate canonical event identity")
            key = (stamp,order)
            if group in last and key <= last[group]:
                code = ErrorCode.DUPLICATE if key == last[group] else ErrorCode.INVALID_ORDER
                raise ContractError(code, "ambiguous tie or nonmonotonic event order")
            last[group] = key
            if session is not None:
                condition = columns["condition"][i] if "condition" in columns else None
                auction = "opening" if condition == "opening_auction" else "closing" if condition == "closing_auction" else "none"
                cutoff = availability.market_cutoff_ns if availability is not None else session.close_ns
                if not session.admits_event(stamp,cutoff,auction=auction,quote=batch.kind == DataKind.QUOTE):
                    raise ContractError(ErrorCode.BOUNDS, "event outside supplied session/cutoff/auction policy")
            elif availability is not None and stamp >= availability.market_cutoff_ns:
                raise ContractError(ErrorCode.BOUNDS, "ordinary event at/after market cutoff; auction requires session evidence")
            if batch.kind == DataKind.TRADE:
                if columns["eligible"][i] is True:
                    for name in ("price","size"):
                        if name in columns and (number(name) is None or cast(int,number(name)) <= 0):
                            raise ContractError(ErrorCode.INVALID_SCHEMA, "eligible trade needs positive supplied price/size")
            else: states.append(quote_state(number("bid"),number("ask")))
        elif batch.kind in (DataKind.BAR,DataKind.DAILY):
            start = cast(int,number("start_ns")); end = cast(int,number("end_ns"))
            if start >= end: raise ContractError(ErrorCode.BOUNDS, "nonpositive bar interval")
            order_group = (instrument,) if batch.kind == DataKind.DAILY else group
            identity = group if batch.kind == DataKind.DAILY else group+(start,end)
            if identity in seen: raise ContractError(ErrorCode.DUPLICATE, "duplicate canonical interval identity")
            if order_group in previous_end and start < previous_end[order_group]:
                raise ContractError(ErrorCode.INVALID_ORDER, "overlapping or unordered intervals")
            previous_end[order_group] = end
            if session is not None and (start < session.open_ns or end > session.close_ns):
                raise ContractError(ErrorCode.BOUNDS, "bar outside supplied session")
            if availability is not None and end > availability.market_cutoff_ns:
                raise ContractError(ErrorCode.BOUNDS, "forming/future bar exceeds cutoff")
            volume = number("volume")
            prices = {name:number(name) for name in ("open","high","low","close") if name in columns}
            notional = number("actual_notional")
            if volume != 0:
                if any(v is not None and v <= 0 for v in prices.values()):
                    raise ContractError(ErrorCode.INVALID_SCHEMA, "supplied price-bearing OHLC must be positive independently of volume")
                independent_low = prices.get("low"); independent_high = prices.get("high")
                if independent_low is not None and independent_high is not None and (independent_low > independent_high or any(v is not None and not independent_low <= v <= independent_high for v in prices.values())):
                    raise ContractError(ErrorCode.INVALID_SCHEMA, "OHLC coherence violation independently of volume")
            if volume == 0:
                if any(v is not None for v in prices.values()) or notional not in (None,0):
                    raise ContractError(ErrorCode.INVALID_SCHEMA, "zero-volume interval requires null OHLC and zero/absent notional")
            elif volume is not None and volume > 0:
                if any(v is None or v <= 0 for v in prices.values()):
                    raise ContractError(ErrorCode.INVALID_SCHEMA, "positive-volume bar needs positive nonnull supplied OHLC")
                low = prices.get("low"); high = prices.get("high")
                if low is not None and high is not None:
                    if low > high or any(v is not None and not low <= v <= high for v in prices.values()):
                        raise ContractError(ErrorCode.INVALID_SCHEMA, "OHLC coherence violation")
                    if notional is not None and not low*volume <= notional <= high*volume:
                        raise ContractError(ErrorCode.INVALID_SCHEMA, "actual notional outside exact traded bounds")
        else:
            start = cast(int,number("effective_start_ns")); reference_end = number("effective_end_ns")
            identity = group+(columns["reference_id"][i],)
            if identity in seen: raise ContractError(ErrorCode.DUPLICATE, "duplicate canonical reference identity")
            reference_key = (start,cast(str,columns["reference_id"][i]))
            if group in reference_last and reference_key < reference_last[group]:
                raise ContractError(ErrorCode.INVALID_ORDER, "unordered effective reference facts")
            reference_last[group] = reference_key
            if reference_end is not None and start >= reference_end:
                raise ContractError(ErrorCode.BOUNDS, "invalid reference effective bounds")
            numerator = number("factor_num"); denominator = number("factor_den")
            if numerator is not None and numerator <= 0 or denominator is not None and denominator <= 0:
                raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "adjustment rational factors must be positive")
        if identity in seen:
            raise ContractError(ErrorCode.DUPLICATE, "duplicate canonical row identity")
        seen.add(identity)
        for quantity in ("size","bid_size","ask_size","volume","trade_count"):
            value = number(quantity)
            if value is not None and value < 0:
                raise ContractError(ErrorCode.BOUNDS, "negative quantity/count")
        if availability is not None:
            reason = availability.knowledge_reason(number("known_at_ns"))
            if reason is not None: exclusions.append(KnowledgeExclusion(i,Reason(reason)))
    return ValidationReport(batch.row_count,missing,nulls,tuple(exclusions),tuple(states))

def require_compatible_inputs(left: CanonicalBatch, right: CanonicalBatch) -> None:
    if type(left) is not CanonicalBatch or type(right) is not CanonicalBatch:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete canonical batches required")
    a,b = left.metadata,right.metadata
    if a.namespace != b.namespace:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "incompatible input namespaces")
    if a.price_unit != b.price_unit or a.quantity_unit != b.quantity_unit:
        raise ContractError(ErrorCode.INVALID_UNIT, "normalize compatible scales explicitly before combining")
    if (a.adjustment.basis,a.adjustment.policy_version,a.adjustment.anchor) != (b.adjustment.basis,b.adjustment.policy_version,b.adjustment.anchor):
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "incompatible declared adjustment basis/policy/anchor")
