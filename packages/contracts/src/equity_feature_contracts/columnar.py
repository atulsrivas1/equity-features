"""Explicit materializing Arrow/NumPy bridges; never lazy source execution."""
from __future__ import annotations
from dataclasses import asdict
from decimal import Decimal
import json
from typing import Any, Mapping
import numpy as np
import pyarrow as pa
from .errors import ContractError, ErrorCode
from .results import BreadthCounts, BreadthFraction, FeatureResult, ValueType, IntervalOHLCV, IntervalVolumeShares
from .inputs import (
    AdjustmentSpec, BatchMetadata, CanonicalBatch, Cell, Column, Coverage,
    DataKind, DType, InputScope, IntervalCoverage, PriceUnit, SourceBinding, schema_for,
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
    if type(batch) is not CanonicalBatch:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete CanonicalBatch required")
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

def _from_arrow(value: Any) -> CanonicalBatch:
    if not isinstance(value, (pa.RecordBatch, pa.Table)):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "only concrete in-memory Arrow RecordBatch/Table accepted")
    raw = (value.schema.metadata or {}).get(b"equity.inputs")
    if raw is None:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "canonical Arrow envelope required")
    envelope = json.loads(raw)
    if envelope["schema_version"] != "1":
        raise ContractError(ErrorCode.INVALID_SCHEMA, "unsupported input schema version")
    kind = DataKind(envelope["kind"])
    meta = envelope["metadata"]
    unit = meta["price_unit"]
    metadata = BatchMetadata(namespace=meta["namespace"], source=SourceBinding(**meta["source"]), coverage=Coverage(**meta["coverage"]), price_unit=PriceUnit(**unit) if unit is not None else None, adjustment=AdjustmentSpec(**meta["adjustment"]), sampling=meta["sampling"], quantity_unit=meta["quantity_unit"], ordering=meta["ordering"], duplicate_policy=meta["duplicate_policy"], scope=InputScope(**meta["scope"]) if meta.get("scope") is not None else None, interval_coverage=tuple(IntervalCoverage(x["name"],x["start_ns"],x["end_ns"],Coverage(**x["coverage"])) for x in meta.get("interval_coverage",())))
    schema = schema_for(kind)
    columns = []
    for index, field in enumerate(value.schema):
        expected = schema.field(field.name)
        if field.type != _arrow_type(expected.dtype) or field.nullable != expected.nullable:
            raise ContractError(ErrorCode.INVALID_SCHEMA, f"Arrow dtype/unit/nullability mismatch: {field.name}")
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
    if type(batch) is not CanonicalBatch:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete CanonicalBatch required")
    result: dict[str, NumpyColumn] = {}
    for column in batch.columns:
        dtype = schema_for(batch.kind).field(column.name).dtype
        if dtype == DType.DECIMAL128:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "wide decimal128 requires Arrow; no int64 truncation")
        fill: Cell = "" if dtype == DType.STRING else False if dtype == DType.BOOL else 0
        values = [fill if v is None else v for v in column.values]
        array = np.array(values, dtype=str if dtype == DType.STRING else bool if dtype == DType.BOOL else np.int64)
        mask = np.array([v is not None for v in column.values], dtype=bool)
        result[column.name] = array, mask
    return result

def _from_numpy(kind: DataKind, columns: Mapping[str, NumpyColumn], metadata: BatchMetadata) -> CanonicalBatch:
    if type(columns) is not dict:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete NumPy column dictionary required; no lazy mapping")
    result = []
    for name, (array, mask) in columns.items():
        dtype = schema_for(kind).field(name).dtype
        if type(array) is not np.ndarray or type(mask) is not np.ndarray or array.ndim != 1 or mask.ndim != 1 or array.shape != mask.shape or mask.dtype != np.dtype(bool):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "one-dimensional array and Boolean validity mask required")
        if dtype == DType.DECIMAL128 or (dtype == DType.STRING and array.dtype.kind != "U") or (dtype == DType.BOOL and array.dtype != np.dtype(bool)) or (dtype in (DType.INT64, DType.UTC_NS) and array.dtype != np.dtype(np.int64)):
            raise ContractError(ErrorCode.INVALID_SCHEMA, f"NumPy exact dtype required: {name}")
        values = tuple(v if valid else None for v, valid in zip(array.tolist(), mask.tolist(), strict=True))
        result.append(Column(name, values))
    return CanonicalBatch(kind, tuple(result), metadata)


def from_arrow(value: Any) -> CanonicalBatch:
    try:
        return _from_arrow(value)
    except ContractError:
        raise
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "invalid Arrow canonical envelope") from error


def to_arrow_result(result: "FeatureResult") -> dict[str, Any]:
    """Copied values tables per feature, one quality table and bounded evidence."""
    if type(result) is not FeatureResult:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete FeatureResult required")
    metadata = {b"equity.result": result.metadata_json().encode()}
    values: dict[str, Any] = {}
    for column in result.values:
        dtype = column.dtype
        if dtype == ValueType.INT64: arrow_type = pa.int64()
        elif dtype == ValueType.DECIMAL128: arrow_type = pa.decimal128(38, 0)
        elif dtype == ValueType.FLOAT64: arrow_type = pa.float64()
        elif dtype == ValueType.BOOL: arrow_type = pa.bool_()
        elif dtype == ValueType.STRING: arrow_type = pa.string()
        elif dtype in (ValueType.INTERVAL_OHLCV,ValueType.INTERVAL_VOLUME_SHARES):
            interval_type=pa.struct([pa.field("name",pa.string(),False),pa.field("start_ns",pa.timestamp("ns",tz="UTC"),False),pa.field("end_ns",pa.timestamp("ns",tz="UTC"),False)])
            entity_type=pa.struct([pa.field("instrument_id",pa.string(),False),pa.field("session_id",pa.string(),False)])
            quality_type=pa.struct([pa.field("entity",entity_type,False),pa.field("feature_id",pa.string(),False),pa.field("status",pa.string(),False),pa.field("expected",pa.int64(),True),pa.field("observed",pa.int64(),False),pa.field("reasons",pa.list_(pa.string()),False)])
            fields=[pa.field("interval",interval_type,False),pa.field("quality",quality_type,False)]
            fields += [pa.field(name,pa.float64(),True) for name in ("open_price","high_price","low_price","close_price")] + [pa.field("volume",pa.int64(),True)] if dtype == ValueType.INTERVAL_OHLCV else [pa.field("share",pa.float64(),True)]
            arrow_type=pa.list_(pa.struct(fields))
        else:
            names = ("advancing","declining","unchanged","eligible","expected") if dtype == ValueType.BREADTH_COUNTS else ("above","eligible","expected")
            arrow_type = pa.struct([pa.field(name,pa.int64(),nullable=False) for name in names])
        payload: list[Any] = []
        for value in column.values:
            if isinstance(value,BreadthCounts): payload.append({**asdict(value),"eligible":value.eligible})
            elif isinstance(value,BreadthFraction): payload.append(asdict(value))
            elif isinstance(value,(IntervalOHLCV,IntervalVolumeShares)): payload.append([asdict(row) for row in value.rows])
            elif value is not None and dtype == ValueType.DECIMAL128: payload.append(Decimal(value))
            else: payload.append(value)
        schema = pa.schema([pa.field("instrument_id",pa.string(),nullable=False),pa.field("session_id",pa.string(),nullable=False),pa.field("value",arrow_type,nullable=True)],metadata=metadata)
        values[column.feature_id] = pa.Table.from_arrays([pa.array([x.instrument_id for x in column.entities],type=pa.string()),pa.array([x.session_id for x in column.entities],type=pa.string()),pa.array(payload,type=arrow_type)],schema=schema)
    quality_schema = pa.schema([pa.field("instrument_id",pa.string(),False),pa.field("session_id",pa.string(),False),pa.field("feature_id",pa.string(),False),pa.field("status",pa.string(),False),pa.field("expected",pa.int64(),True),pa.field("observed",pa.int64(),False),pa.field("reasons",pa.list_(pa.string()),False)],metadata=metadata)
    quality_data = {"instrument_id":[q.entity.instrument_id for q in result.quality],"session_id":[q.entity.session_id for q in result.quality],"feature_id":[q.feature_id for q in result.quality],"status":[q.status.value for q in result.quality],"expected":[q.expected for q in result.quality],"observed":[q.observed for q in result.quality],"reasons":[[x.value for x in q.reasons] for q in result.quality]}
    quality = pa.Table.from_pydict(quality_data,schema=quality_schema)
    time_type = pa.timestamp("ns",tz="UTC")
    evidence_schema = pa.schema([pa.field(name,pa.string(),nullable=False) for name in ("instrument_id","session_id","feature_id","input_id","row_id","use","boundary")] + [pa.field("event_ns",time_type,False),pa.field("known_at_ns",time_type,True),pa.field("effective_start_ns",time_type,True),pa.field("effective_end_ns",time_type,True),pa.field("exclusion_reason",pa.string(),True)],metadata=metadata)
    evidence_data = {"instrument_id":[e.entity.instrument_id for e in result.evidence],"session_id":[e.entity.session_id for e in result.evidence],"feature_id":[e.feature_id for e in result.evidence],"input_id":[e.input_id for e in result.evidence],"row_id":[e.row_id for e in result.evidence],"use":[e.use for e in result.evidence],"boundary":[e.boundary for e in result.evidence],"event_ns":[e.event_ns for e in result.evidence],"known_at_ns":[e.known_at_ns for e in result.evidence],"effective_start_ns":[e.effective_start_ns for e in result.evidence],"effective_end_ns":[e.effective_end_ns for e in result.evidence],"exclusion_reason":[e.exclusion_reason.value if e.exclusion_reason is not None else None for e in result.evidence]}
    evidence = pa.Table.from_pydict(evidence_data,schema=evidence_schema)
    return {"values":values,"quality":quality,"evidence":evidence}


def from_numpy(kind: DataKind, columns: Mapping[str, NumpyColumn], metadata: BatchMetadata) -> CanonicalBatch:
    try:
        return _from_numpy(kind, columns, metadata)
    except ContractError:
        raise
    except (ValueError, TypeError, KeyError, AttributeError) as error:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "invalid NumPy canonical mapping") from error
