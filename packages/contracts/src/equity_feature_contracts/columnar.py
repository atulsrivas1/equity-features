"""Explicit materializing Arrow/NumPy bridges; never lazy source execution."""
from __future__ import annotations
from dataclasses import asdict
from decimal import Decimal
import json
from typing import Any, Mapping
import numpy as np
import pyarrow as pa
from .inputs import (
    AdjustmentSpec, BatchMetadata, CanonicalBatch, Cell, Column, Coverage,
    DataKind, DType, PriceUnit, SourceBinding, schema_for,
)

# Backend objects are untyped at this optional bridge; core admission checks every cell.
def _arrow_type(dtype: DType) -> Any:
    if dtype == DType.UTC_NS:
        return pa.timestamp("ns", tz="UTC")
    if dtype == DType.INT64:
        return pa.int64()
    if dtype == DType.DECIMAL128:
        return pa.decimal128(38, 0)
    if dtype == DType.BOOL:
        return pa.bool_()
    return pa.string()

def to_arrow(batch: CanonicalBatch) -> Any:
    schema = schema_for(batch.kind)
    fields = [pa.field(c.name, _arrow_type(schema.field(c.name).dtype), nullable=schema.field(c.name).nullable) for c in batch.columns]
    arrays = []
    for c in batch.columns:
        dtype = schema.field(c.name).dtype
        values: Any = c.values
        if dtype == DType.DECIMAL128:
            values = [Decimal(v) if v is not None else None for v in c.values]
        arrays.append(pa.array(values, type=_arrow_type(dtype)))
    envelope = {"schema_version": schema.version, "kind": batch.kind.value, "metadata": asdict(batch.metadata)}
    arrow_schema = pa.schema(fields, metadata={b"equity.inputs": json.dumps(envelope, sort_keys=True, separators=(",", ":")).encode()})
    return pa.RecordBatch.from_arrays(arrays, schema=arrow_schema)

def from_arrow(value: Any) -> CanonicalBatch:
    if not isinstance(value, (pa.RecordBatch, pa.Table)):
        raise ValueError("only concrete in-memory Arrow RecordBatch/Table accepted")
    raw = (value.schema.metadata or {}).get(b"equity.inputs")
    if raw is None:
        raise ValueError("canonical Arrow envelope required")
    envelope = json.loads(raw)
    if envelope["schema_version"] != "1":
        raise ValueError("unsupported input schema version")
    kind = DataKind(envelope["kind"])
    meta = envelope["metadata"]
    unit = meta["price_unit"]
    metadata = BatchMetadata(namespace=meta["namespace"], source=SourceBinding(**meta["source"]), coverage=Coverage(**meta["coverage"]), price_unit=PriceUnit(**unit) if unit is not None else None, adjustment=AdjustmentSpec(**meta["adjustment"]), sampling=meta["sampling"], quantity_unit=meta["quantity_unit"], ordering=meta["ordering"], duplicate_policy=meta["duplicate_policy"])
    schema = schema_for(kind)
    columns = []
    for index, field in enumerate(value.schema):
        expected = schema.field(field.name)
        if field.type != _arrow_type(expected.dtype) or field.nullable != expected.nullable:
            raise ValueError(f"Arrow dtype/unit/nullability mismatch: {field.name}")
        array = value.column(index)
        if expected.dtype == DType.UTC_NS:
            array = array.cast(pa.int64())
        values = array.to_pylist()
        if expected.dtype == DType.DECIMAL128:
            values = [int(v) if v is not None else None for v in values]
        columns.append(Column(field.name, tuple(values)))
    return CanonicalBatch(kind, tuple(columns), metadata)

# Every nullable array has an explicit validity mask (True = present).
NumpyColumn = tuple[np.ndarray[Any, Any], np.ndarray[Any, Any]]

def to_numpy(batch: CanonicalBatch) -> dict[str, NumpyColumn]:
    result: dict[str, NumpyColumn] = {}
    for column in batch.columns:
        dtype = schema_for(batch.kind).field(column.name).dtype
        if dtype == DType.DECIMAL128:
            raise ValueError("wide decimal128 requires Arrow; no int64 truncation")
        fill: Cell = "" if dtype == DType.STRING else False if dtype == DType.BOOL else 0
        values = [fill if v is None else v for v in column.values]
        array = np.array(values, dtype=str if dtype == DType.STRING else bool if dtype == DType.BOOL else np.int64)
        mask = np.array([v is not None for v in column.values], dtype=bool)
        result[column.name] = array, mask
    return result

def from_numpy(kind: DataKind, columns: Mapping[str, NumpyColumn], metadata: BatchMetadata) -> CanonicalBatch:
    result = []
    for name, (array, mask) in columns.items():
        dtype = schema_for(kind).field(name).dtype
        if not isinstance(array, np.ndarray) or not isinstance(mask, np.ndarray) or array.ndim != 1 or mask.ndim != 1 or array.shape != mask.shape or mask.dtype != np.dtype(bool):
            raise ValueError("one-dimensional array and Boolean validity mask required")
        if dtype == DType.DECIMAL128 or (dtype == DType.STRING and array.dtype.kind != "U") or (dtype == DType.BOOL and array.dtype != np.dtype(bool)) or (dtype in (DType.INT64, DType.UTC_NS) and array.dtype != np.dtype(np.int64)):
            raise ValueError(f"NumPy exact dtype required: {name}")
        values = tuple(v if valid else None for v, valid in zip(array.tolist(), mask.tolist(), strict=True))
        result.append(Column(name, values))
    return CanonicalBatch(kind, tuple(result), metadata)
