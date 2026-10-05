"""Owned immutable canonical inputs. Structural admission only; no source access."""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

from .errors import ContractError, ErrorCode
Cell: TypeAlias = int | str | bool | None
I64_MIN = -(2**63)
I64_MAX = 2**63 - 1

class DataKind(StrEnum):
    TRADE = "trade"
    QUOTE = "quote"
    BAR = "bar"
    DAILY = "daily"
    REFERENCE = "reference"

class DType(StrEnum):
    INT64 = "int64"
    UTC_NS = "utc_ns"
    DECIMAL128 = "decimal128"
    STRING = "string"
    BOOL = "bool"

@dataclass(frozen=True)
class Field:
    name: str
    dtype: DType
    nullable: bool = True
    required: bool = False

@dataclass(frozen=True)
class InputSchema:
    kind: DataKind
    fields: tuple[Field, ...]
    version: str = "1"

    def field(self, name: str) -> Field:
        for field in self.fields:
            if field.name == name:
                return field
        raise ContractError(ErrorCode.INVALID_SCHEMA, f"unknown field: {name}")

_ID = (Field("instrument_id", DType.STRING, False, True),
       Field("session_id", DType.STRING, False, True))
_EVENT = (Field("event_ns", DType.UTC_NS, False, True),
          Field("order_key", DType.INT64, False, True),
          Field("event_id", DType.STRING, False, True))
_BOUNDS = (Field("start_ns", DType.UTC_NS, False, True),
           Field("end_ns", DType.UTC_NS, False, True))
_KNOWN = (Field("known_at_ns", DType.UTC_NS),)
_OHLC = tuple(Field(x, DType.INT64) for x in ("open", "high", "low", "close", "volume", "trade_count"))
_SCHEMAS = (
    InputSchema(DataKind.TRADE, _ID + _EVENT + (Field("eligible", DType.BOOL, False, True), Field("price", DType.INT64), Field("size", DType.INT64), Field("condition", DType.STRING)) + _KNOWN),
    InputSchema(DataKind.QUOTE, _ID + _EVENT + tuple(Field(x, DType.INT64) for x in ("bid", "ask", "bid_size", "ask_size")) + _KNOWN),
    InputSchema(DataKind.BAR, _ID + _BOUNDS + _OHLC + (Field("actual_notional", DType.DECIMAL128),) + _KNOWN),
    InputSchema(DataKind.DAILY, _ID + _BOUNDS + _OHLC + (Field("actual_notional", DType.DECIMAL128),) + _KNOWN),
    InputSchema(DataKind.REFERENCE, _ID + (Field("reference_id", DType.STRING, False, True), Field("fact_kind", DType.STRING, False, True), Field("effective_start_ns", DType.UTC_NS, False, True), Field("effective_end_ns", DType.UTC_NS), Field("text", DType.STRING), Field("price", DType.INT64), Field("factor_num", DType.INT64), Field("factor_den", DType.INT64)) + _KNOWN),
)

def schema_for(kind: DataKind) -> InputSchema:
    for schema in _SCHEMAS:
        if schema.kind == kind:
            return schema
    raise ContractError(ErrorCode.INVALID_SCHEMA, "unsupported input kind")

@dataclass(frozen=True)
class PriceUnit:
    scale: int
    currency: str

    def __post_init__(self) -> None:
        if type(self.scale) is not int or not 0 <= self.scale <= 18 or (type(self.currency) is not str or not self.currency.strip()):
            raise ContractError(ErrorCode.INVALID_UNIT, "explicit scale 0..18 and currency required")

@dataclass(frozen=True)
class SourceBinding:
    source_id: str
    snapshot_id: str
    mapping_version: str
    input_id: str

    def __post_init__(self) -> None:
        if not all(type(x) is str and x.strip() for x in (self.source_id, self.snapshot_id, self.mapping_version, self.input_id)):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "source/snapshot/mapping/input identity required")

@dataclass(frozen=True)
class Coverage:
    expected: int | None
    observed: int
    complete: bool

    def __post_init__(self) -> None:
        if type(self.observed) is not int or self.observed < 0 or type(self.complete) is not bool:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "invalid coverage")
        if self.observed > I64_MAX or (type(self.expected) is int and self.expected > I64_MAX):
            raise ContractError(ErrorCode.OVERFLOW, "coverage count exceeds int64")
        if self.expected is not None and (type(self.expected) is not int or self.expected < self.observed):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "expected coverage below observed")
        if self.complete and self.expected != self.observed:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "complete coverage requires known matching count")

@dataclass(frozen=True)
class AdjustmentSpec:
    basis: str = "raw"
    policy_version: str = "raw-v1"
    action_snapshot: str = "none"
    anchor: str = "none"

    def __post_init__(self) -> None:
        if self.basis not in ("raw", "split", "total_return") or not all(type(x) is str and x.strip() for x in (self.policy_version, self.action_snapshot, self.anchor)):
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "unsupported or unidentified adjustment basis")
        if self.basis != "raw" and (self.action_snapshot == "none" or self.anchor == "none"):
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "adjusted input requires action snapshot and anchor")

@dataclass(frozen=True)
class InputScope:
    """Caller assertion binding delivery coverage and constituent admission policy."""
    start_ns: int
    end_ns: int
    eligibility_policy: str
    include_opening_auction: bool = False
    include_closing_auction: bool = False

    def __post_init__(self) -> None:
        if any(type(x) is not int or not I64_MIN <= x <= I64_MAX for x in (self.start_ns, self.end_ns)) or self.start_ns >= self.end_ns:
            raise ContractError(ErrorCode.BOUNDS, "positive exact UTCns input scope required")
        if type(self.eligibility_policy) is not str or not self.eligibility_policy.strip():
            raise ContractError(ErrorCode.INVALID_CONFIG, "explicit eligibility policy required")
        if any(type(x) is not bool for x in (self.include_opening_auction, self.include_closing_auction)):
            raise ContractError(ErrorCode.INVALID_CONFIG, "Boolean auction construction policy required")

@dataclass(frozen=True)
class IntervalCoverage:
    name: str
    start_ns: int
    end_ns: int
    coverage: Coverage

    def __post_init__(self) -> None:
        if type(self.name) is not str or not self.name.strip() or type(self.coverage) is not Coverage:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "named typed interval coverage required")
        if any(type(x) is not int or not I64_MIN <= x <= I64_MAX for x in (self.start_ns,self.end_ns)) or self.start_ns >= self.end_ns:
            raise ContractError(ErrorCode.BOUNDS, "positive UTCns interval coverage bounds required")

@dataclass(frozen=True)
class BatchMetadata:
    namespace: str
    source: SourceBinding
    coverage: Coverage
    price_unit: PriceUnit | None
    adjustment: AdjustmentSpec = AdjustmentSpec()
    sampling: str = "none"
    quantity_unit: str = "shares"
    ordering: str = "declared"
    duplicate_policy: str = "reject"
    scope: InputScope | None = None
    interval_coverage: tuple[IntervalCoverage, ...] = ()

    def __post_init__(self) -> None:
        if self.scope is not None and type(self.scope) is not InputScope:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed input scope required")
        if type(self.interval_coverage) not in (tuple,list) or any(type(x) is not IntervalCoverage for x in self.interval_coverage):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete typed interval coverage required")
        object.__setattr__(self,"interval_coverage",tuple(self.interval_coverage))
        if len({x.name for x in self.interval_coverage}) != len(self.interval_coverage):
            raise ContractError(ErrorCode.DUPLICATE, "duplicate interval coverage name")
        if self.interval_coverage and (self.scope is None or any(x.start_ns < self.scope.start_ns or x.end_ns > self.scope.end_ns for x in self.interval_coverage)):
            raise ContractError(ErrorCode.BOUNDS, "interval coverage outside declared input scope")
        if type(self.source) is not SourceBinding or type(self.coverage) is not Coverage or type(self.adjustment) is not AdjustmentSpec or (self.price_unit is not None and type(self.price_unit) is not PriceUnit):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed immutable metadata components required")
        if (type(self.namespace) is not str or not self.namespace.strip()) or self.quantity_unit != "shares":
            raise ContractError(ErrorCode.INVALID_SCHEMA, "explicit namespace and share quantities required")
        if self.sampling not in ("none", "trade_snapshot", "continuous"):
            raise ContractError(ErrorCode.UNSUPPORTED_SAMPLING, "unsupported quote sampling")
        if self.ordering not in ("declared", "unsorted") or self.duplicate_policy not in ("reject", "preserve"):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "unsupported order/duplicate declaration")

@dataclass(frozen=True)
class Column:
    name: str
    values: tuple[Cell, ...]

    def __post_init__(self) -> None:
        if type(self.name) is not str or not self.name.strip():
            raise ContractError(ErrorCode.INVALID_SCHEMA, "nonempty column name required")
        if type(self.values) not in (tuple, list):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete tuple/list values required; no lazy iterable")
        object.__setattr__(self, "values", tuple(self.values))

@dataclass(frozen=True)
class CanonicalBatch:
    kind: DataKind
    columns: tuple[Column, ...]
    metadata: BatchMetadata

    def __post_init__(self) -> None:
        if type(self.kind) is not DataKind or type(self.columns) not in (tuple, list):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "DataKind and concrete columns required")
        if type(self.metadata) is not BatchMetadata or any(type(c) is not Column for c in self.columns):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed metadata and columns required")
        object.__setattr__(self, "columns", tuple(self.columns))
        schema = schema_for(self.kind)
        names = tuple(c.name for c in self.columns)
        if len(set(names)) != len(names):
            raise ContractError(ErrorCode.DUPLICATE, "duplicate column")
        if any(f.required and f.name not in names for f in schema.fields):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "required identity/time/eligibility column missing")
        if len({len(c.values) for c in self.columns}) > 1:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "column length mismatch")
        if self.kind != DataKind.REFERENCE and self.metadata.price_unit is None:
            raise ContractError(ErrorCode.INVALID_UNIT, "market input requires price unit")
        if "price" in names and self.metadata.price_unit is None:
            raise ContractError(ErrorCode.INVALID_UNIT, "reference price requires price unit")
        if (self.kind == DataKind.QUOTE) != (self.metadata.sampling != "none"):
            raise ContractError(ErrorCode.UNSUPPORTED_SAMPLING, "quote input requires explicit sampling; other kinds use none")
        for column in self.columns:
            field = schema.field(column.name)
            for value in column.values:
                _admit(field, value)

    @property
    def row_count(self) -> int:
        return len(self.columns[0].values) if self.columns else 0

    def column(self, name: str) -> Column | None:
        return next((c for c in self.columns if c.name == name), None)


def _admit(field: Field, value: Cell) -> None:
    if value is None:
        if not field.nullable:
            raise ContractError(ErrorCode.INVALID_SCHEMA, f"null required field: {field.name}")
        return
    if field.dtype == DType.STRING:
        valid = type(value) is str and (field.nullable or bool(value.strip()))
    elif field.dtype == DType.BOOL:
        valid = type(value) is bool
    elif field.dtype == DType.DECIMAL128:
        valid = type(value) is int and -(10**38) < value < 10**38
    else:
        valid = type(value) is int and I64_MIN <= value <= I64_MAX
    if not valid and type(value) is int and field.dtype in (DType.INT64, DType.UTC_NS, DType.DECIMAL128):
        raise ContractError(ErrorCode.OVERFLOW, f"precision overflow: {field.name}")
    if not valid:
        raise ContractError(ErrorCode.INVALID_SCHEMA, f"type/precision violation: {field.name}")
