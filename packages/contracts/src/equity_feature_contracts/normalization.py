"""Explicit owned transformations with immutable provenance; no basis conversion."""
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
from decimal import Decimal
import hashlib
import json
import math
from typing import cast
from .errors import ContractError, ErrorCode
from .inputs import CanonicalBatch, Cell, Column, DataKind, PriceUnit
from .validation import checked_int64, validate_batch

@dataclass(frozen=True)
class NormalizationReport:
    original_input_id: str
    output_input_id: str
    original_row_indices: tuple[int, ...]
    discarded_row_indices: tuple[int, ...]
    sorted: bool
    rescaled: bool
    rounded_cells: int
    rounding: str
    original_price_unit: PriceUnit | None
    output_price_unit: PriceUnit | None
    deduplication: str

@dataclass(frozen=True)
class NormalizedBatch:
    batch: CanonicalBatch
    report: NormalizationReport

def _rounded(value: int, divisor: int, policy: str) -> tuple[int, bool]:
    quotient,remainder = divmod(abs(value),divisor)
    if remainder and policy == "exact":
        raise ContractError(ErrorCode.INVALID_UNIT, "nonexact rescale requires explicit rounding")
    if policy == "half_even" and (2*remainder > divisor or (2*remainder == divisor and quotient%2)):
        quotient += 1
    return (-quotient if value < 0 else quotient),bool(remainder)

def normalize_batch(batch: CanonicalBatch, *, sort: bool = False,
                    deduplicate: str = "reject", price_unit: PriceUnit | None = None,
                    rounding: str = "exact") -> NormalizedBatch:
    if type(batch) is not CanonicalBatch or type(sort) is not bool:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete batch and Boolean sort required")
    if deduplicate not in ("reject","identical") or rounding not in ("exact","half_even"):
        raise ContractError(ErrorCode.INVALID_CONFIG, "unsupported explicit normalization policy")
    if price_unit is not None and type(price_unit) is not PriceUnit:
        raise ContractError(ErrorCode.INVALID_UNIT, "typed target unit required")
    columns = {c.name:c.values for c in batch.columns}
    ids = ("instrument_id","session_id") + (("event_id",) if batch.kind in (DataKind.TRADE,DataKind.QUOTE) else ("start_ns","end_ns") if batch.kind == DataKind.BAR else ("reference_id",) if batch.kind == DataKind.REFERENCE else ())
    seen: dict[tuple[Cell, ...], int] = {}; indices: list[int] = []; discarded: list[int] = []
    for i in range(batch.row_count):
        key = tuple(columns[name][i] for name in ids)
        if key in seen:
            old = seen[key]
            if deduplicate != "identical" or any(c.values[old] != c.values[i] for c in batch.columns):
                raise ContractError(ErrorCode.DUPLICATE, "duplicate/conflicting identity requires explicit compatible normalization")
            discarded.append(i)
        else: seen[key] = i; indices.append(i)
    original_indices = tuple(indices)
    if sort:
        if batch.kind in (DataKind.TRADE,DataKind.QUOTE): fields = ("instrument_id","session_id","event_ns","order_key")
        elif batch.kind == DataKind.DAILY: fields = ("instrument_id","start_ns","end_ns","session_id")
        elif batch.kind == DataKind.BAR: fields = ("instrument_id","session_id","start_ns","end_ns")
        else: fields = ("instrument_id","session_id","effective_start_ns","reference_id")
        indices.sort(key=lambda i: tuple(cast(str | int,columns[name][i]) for name in fields))
    old_unit = batch.metadata.price_unit
    rescaled = price_unit is not None and price_unit != old_unit
    if rescaled and (old_unit is None or price_unit is None or old_unit.currency != price_unit.currency):
        raise ContractError(ErrorCode.INVALID_UNIT, "no inferred unit or currency/FX conversion")
    rounded_cells = 0; output: list[Column] = []
    price_names = {"price","bid","ask","open","high","low","close","actual_notional"}
    for column in batch.columns:
        values: list[Cell] = []
        for i in indices:
            value = column.values[i]
            if rescaled and column.name in price_names and value is not None:
                assert price_unit is not None and old_unit is not None
                difference = price_unit.scale-old_unit.scale
                if difference >= 0: value = cast(int,value)*10**difference
                else:
                    value,did_round = _rounded(cast(int,value),10**(-difference),rounding)
                    rounded_cells += did_round
            values.append(value)
        output.append(Column(column.name,tuple(values)))
    changed = tuple(indices) != tuple(range(batch.row_count)) or rescaled
    metadata = replace(batch.metadata,price_unit=price_unit if price_unit is not None else old_unit,ordering="declared",duplicate_policy="reject")
    # Coverage describes original source observation, not automatically repaired completeness.
    if changed:
        payload = {"kind":batch.kind.value,"columns":[asdict(x) for x in output],"metadata":asdict(metadata),"indices":indices,"rounding":rounding,"deduplicate":deduplicate}
        digest = hashlib.sha256(json.dumps(payload,sort_keys=True,separators=(",",":"),ensure_ascii=True).encode()).hexdigest()
        source = replace(metadata.source,input_id=metadata.source.input_id+":normalized:"+digest,mapping_version=metadata.source.mapping_version+":normalized:"+digest)
        metadata = replace(metadata,source=source)
    owned = CanonicalBatch(batch.kind,tuple(output),metadata)
    validate_batch(owned)
    report = NormalizationReport(batch.metadata.source.input_id,metadata.source.input_id,tuple(indices),tuple(discarded),tuple(indices)!=original_indices,rescaled,rounded_cells,rounding,old_unit,metadata.price_unit,deduplicate)
    return NormalizedBatch(owned,report)

@dataclass(frozen=True)
class QuantizedPrices:
    values: tuple[int | None, ...]
    unit: PriceUnit
    interpretation: str
    rounding: str
    rounded_cells: int

def quantize_float_prices(values: tuple[float | None, ...], *, unit: PriceUnit,
                          interpretation: str, rounding: str) -> QuantizedPrices:
    if type(values) not in (tuple,list) or type(unit) is not PriceUnit:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete float values and typed unit required")
    if interpretation not in ("binary64_exact","decimal_repr") or rounding not in ("exact","half_even"):
        raise ContractError(ErrorCode.INVALID_CONFIG, "explicit supported float interpretation/rounding required")
    result: list[int | None] = []; rounded = 0
    for value in values:
        if value is None: result.append(None); continue
        if type(value) is not float or not math.isfinite(value):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "finite float64 source value required")
        decimal = Decimal.from_float(value) if interpretation == "binary64_exact" else Decimal(str(value))
        numerator,denominator = decimal.as_integer_ratio()
        coefficient,did_round = _rounded(numerator*10**unit.scale,denominator,rounding)
        result.append(checked_int64(coefficient)); rounded += did_round
    return QuantizedPrices(tuple(result),unit,interpretation,rounding,rounded)
