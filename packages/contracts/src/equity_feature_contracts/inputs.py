"""Owned immutable canonical inputs. Structural admission only; no source access."""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import TypeAlias

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
        raise ValueError(f"unknown field: {name}")

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
    raise ValueError("unsupported input kind")

@dataclass(frozen=True)
class PriceUnit:
    scale: int
    currency: str

    def __post_init__(self) -> None:
        if type(self.scale) is not int or not 0 <= self.scale <= 18 or not self.currency.strip():
            raise ValueError("explicit scale 0..18 and currency required")

@dataclass(frozen=True)
class SourceBinding:
    source_id: str
    snapshot_id: str
    mapping_version: str
    input_id: str

    def __post_init__(self) -> None:
        if not all(x.strip() for x in (self.source_id, self.snapshot_id, self.mapping_version, self.input_id)):
            raise ValueError("source/snapshot/mapping/input identity required")

@dataclass(frozen=True)
class Coverage:
    expected: int | None
    observed: int
    complete: bool

    def __post_init__(self) -> None:
        if type(self.observed) is not int or self.observed < 0 or type(self.complete) is not bool:
            raise ValueError("invalid coverage")
        if self.expected is not None and (type(self.expected) is not int or self.expected < self.observed):
            raise ValueError("expected coverage below observed")
        if self.complete and self.expected != self.observed:
            raise ValueError("complete coverage requires known matching count")

@dataclass(frozen=True)
class AdjustmentSpec:
    basis: str = "raw"
    policy_version: str = "raw-v1"
    action_snapshot: str = "none"
    anchor: str = "none"

    def __post_init__(self) -> None:
        if self.basis not in ("raw", "split", "total_return") or not all(x.strip() for x in (self.policy_version, self.action_snapshot, self.anchor)):
            raise ValueError("unsupported or unidentified adjustment basis")
        if self.basis != "raw" and (self.action_snapshot == "none" or self.anchor == "none"):
            raise ValueError("adjusted input requires action snapshot and anchor")

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

    def __post_init__(self) -> None:
        if not self.namespace.strip() or self.quantity_unit != "shares":
            raise ValueError("explicit namespace and share quantities required")
        if self.sampling not in ("none", "trade_snapshot", "continuous"):
            raise ValueError("unsupported quote sampling")
        if self.ordering not in ("declared", "unsorted") or self.duplicate_policy not in ("reject", "preserve"):
            raise ValueError("unsupported order/duplicate declaration")

@dataclass(frozen=True)
class Column:
    name: str
    values: tuple[Cell, ...]

    def __post_init__(self) -> None:
        object.__setattr__(self, "values", tuple(self.values))

@dataclass(frozen=True)
class CanonicalBatch:
    kind: DataKind
    columns: tuple[Column, ...]
    metadata: BatchMetadata

    def __post_init__(self) -> None:
        object.__setattr__(self, "columns", tuple(self.columns))
        schema = schema_for(self.kind)
        names = tuple(c.name for c in self.columns)
        if len(set(names)) != len(names):
            raise ValueError("duplicate column")
        if any(f.required and f.name not in names for f in schema.fields):
            raise ValueError("required identity/time/eligibility column missing")
        if len({len(c.values) for c in self.columns}) > 1:
            raise ValueError("column length mismatch")
        if self.kind != DataKind.REFERENCE and self.metadata.price_unit is None:
            raise ValueError("market input requires price unit")
        if "price" in names and self.metadata.price_unit is None:
            raise ValueError("reference price requires price unit")
        if (self.kind == DataKind.QUOTE) != (self.metadata.sampling != "none"):
            raise ValueError("quote input requires explicit sampling; other kinds use none")
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
            raise ValueError(f"null required field: {field.name}")
        return
    if field.dtype == DType.STRING:
        valid = type(value) is str and (field.nullable or bool(value.strip()))
    elif field.dtype == DType.BOOL:
        valid = type(value) is bool
    elif field.dtype == DType.DECIMAL128:
        valid = type(value) is int and -(10**38) < value < 10**38
    else:
        valid = type(value) is int and I64_MIN <= value <= I64_MAX
    if not valid:
        raise ValueError(f"type/precision violation: {field.name}")
