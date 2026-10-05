"""Pure adapter declarations and bounded in-memory conformance checks."""
from __future__ import annotations
from dataclasses import dataclass
from enum import StrEnum
from typing import AsyncIterator, Iterator, NoReturn, Protocol, cast
from .inputs import (AdjustmentSpec, CanonicalBatch, Column, Coverage, DataKind,
                     I64_MAX, I64_MIN, PriceUnit, SourceBinding)
from .specs import AvailabilitySpec
from .errors import ContractError
from .validation import validate_batch

class SourceErrorCode(StrEnum):
    UNSUPPORTED = "unsupported_capability"
    AUTHENTICATION = "authentication"
    ENTITLEMENT = "entitlement"
    RATE_LIMIT = "rate_limit"
    TRANSPORT = "transport"
    SCHEMA = "schema_mismatch"
    UNAVAILABLE = "unavailable_data"
    CANCELLED = "cancelled"
    LIMIT = "resource_limit"

class SourceError(ValueError):
    def __init__(self, code: SourceErrorCode, message: str) -> None:
        if type(code) is not SourceErrorCode or type(message) is not str or not message.strip():
            raise ValueError("typed source error code and nonempty safe message required")
        self.code = code
        super().__init__(message)

def _fail(message: str, code: SourceErrorCode = SourceErrorCode.SCHEMA) -> NoReturn:
    raise SourceError(code, message)

def _text(value: str) -> None:
    if type(value) is not str or not value.strip(): _fail("explicit identity required")

def _count(value: int) -> None:
    if type(value) is not int or not 1 <= value <= I64_MAX: _fail("positive int64 bound required")

def _stamp(value: int) -> None:
    if type(value) is not int or not I64_MIN <= value <= I64_MAX: _fail("exact UTCns int64 required")

@dataclass(frozen=True)
class AdapterCapabilities:
    kinds: tuple[DataKind, ...]
    namespaces: tuple[str, ...]
    price_units: tuple[PriceUnit, ...]
    adjustment_bases: tuple[str, ...] = ("raw",)
    sampling: tuple[str, ...] = ("none",)
    historical: bool = True
    live: bool = False
    max_batch_rows: int = 1024
    schema_version: str = "1"
    timestamp_precision: str = "UTCns-int64"

    def __post_init__(self) -> None:
        for name, rows, expected in (("kinds",self.kinds,DataKind),("namespaces",self.namespaces,str),("price_units",self.price_units,PriceUnit),("adjustment_bases",self.adjustment_bases,str),("sampling",self.sampling,str)):
            if type(rows) not in (tuple,list) or not rows or any(type(x) is not expected for x in rows) or len(set(rows)) != len(rows):
                _fail("concrete unique capability values required")
            object.__setattr__(self,name,tuple(rows))
        for namespace in self.namespaces: _text(namespace)
        if any(x not in ("raw","split","total_return") for x in self.adjustment_bases) or any(x not in ("none","continuous","trade_snapshot") for x in self.sampling): _fail("unsupported basis/sampling")
        if self.schema_version != "1" or self.timestamp_precision != "UTCns-int64": _fail("unsupported schema/precision")
        if type(self.historical) is not bool or type(self.live) is not bool: _fail("boolean modes required")
        _count(self.max_batch_rows)

@dataclass(frozen=True)
class AcquisitionRequest:
    request_id: str
    kind: DataKind
    namespace: str
    instruments: tuple[str, ...]
    sessions: tuple[str, ...]
    start_ns: int
    end_ns: int
    snapshot_id: str
    price_unit: PriceUnit
    availability: AvailabilitySpec
    adjustment: AdjustmentSpec = AdjustmentSpec()
    sampling: str = "none"
    max_batch_rows: int = 1024
    max_rows: int = 10000
    max_batches: int = 100
    selection: str = "event_half_open"
    schema_version: str = "1"

    def __post_init__(self) -> None:
        for value in (self.request_id,self.namespace,self.snapshot_id): _text(value)
        for name, rows in (("instruments",self.instruments),("sessions",self.sessions)):
            if type(rows) not in (tuple,list) or not rows or any(type(x) is not str or not x.strip() for x in rows) or len(set(rows))!=len(rows): _fail("concrete unique requested IDs required")
            object.__setattr__(self,name,tuple(rows))
        if type(self.kind) is not DataKind or type(self.price_unit) is not PriceUnit or type(self.availability) is not AvailabilitySpec or type(self.adjustment) is not AdjustmentSpec: _fail("typed request components required")
        _stamp(self.start_ns);_stamp(self.end_ns)
        if self.start_ns >= self.end_ns: _fail("positive acquisition interval required")
        expected = "event_half_open" if self.kind in (DataKind.TRADE,DataKind.QUOTE) else "completed_intervals" if self.kind in (DataKind.BAR,DataKind.DAILY) else "effective_start_half_open"
        if self.selection != expected or self.schema_version!="1": _fail("explicit compatible selection/schema required")
        if (self.kind==DataKind.QUOTE and self.sampling not in ("continuous","trade_snapshot")) or (self.kind!=DataKind.QUOTE and self.sampling!="none"): _fail("explicit compatible sampling required")
        for limit in (self.max_batch_rows,self.max_rows,self.max_batches): _count(limit)
        if self.max_batch_rows > self.max_rows: _fail("batch limit exceeds total bound")

def require_adapter_capability(capabilities: AdapterCapabilities, request: AcquisitionRequest, *, live: bool = False) -> None:
    if type(capabilities) is not AdapterCapabilities or type(request) is not AcquisitionRequest or type(live) is not bool: _fail("typed capability/request/mode required")
    if not (capabilities.live if live else capabilities.historical): _fail("unsupported acquisition mode",SourceErrorCode.UNSUPPORTED)
    if request.kind not in capabilities.kinds or request.namespace not in capabilities.namespaces or request.price_unit not in capabilities.price_units or request.adjustment.basis not in capabilities.adjustment_bases or request.sampling not in capabilities.sampling or request.max_batch_rows>capabilities.max_batch_rows:
        _fail("unsupported kind/namespace/unit/basis/sampling/batch size",SourceErrorCode.UNSUPPORTED)

@dataclass(frozen=True)
class AdapterBatch:
    request_id: str
    ordinal: int
    final: bool
    source: SourceBinding
    source_coverage: Coverage
    delivery_coverage: Coverage
    batch: CanonicalBatch | None
    disposition: str = "observed"
    reason: str | None = None

    def __post_init__(self) -> None:
        _text(self.request_id)
        if type(self.ordinal) is not int or not 0<=self.ordinal<I64_MAX or type(self.final) is not bool: _fail("bounded ordinal/final flag required")
        if type(self.source) is not SourceBinding or type(self.source_coverage) is not Coverage or type(self.delivery_coverage) is not Coverage: _fail("typed provenance/coverage required")
        if self.disposition == "observed":
            if type(self.batch) is not CanonicalBatch or self.reason is not None: _fail("observed requires canonical batch, including observed-empty")
            assert self.batch is not None
            if self.batch.metadata.source != self.source or self.batch.metadata.coverage!=self.source_coverage or self.delivery_coverage.observed!=self.batch.row_count: _fail("source or delivered count mismatch")
        elif self.disposition in ("missing","unavailable"):
            if self.batch is not None or self.ordinal!=0 or not self.final or self.delivery_coverage!=Coverage(None,0,False): _fail("absent input cannot claim observed-empty/complete coverage")
            if self.reason is None: _fail("missing/unavailable reason required")
            _text(self.reason)
        else: _fail("unknown delivery disposition")

class Cancellation(Protocol):
    def is_cancelled(self) -> bool: ...

class HistoricalAdapter(Protocol):
    def capabilities(self) -> AdapterCapabilities: ...
    def iter_batches(self, request: AcquisitionRequest, cancellation: Cancellation) -> Iterator[AdapterBatch]: ...

class LiveAdapter(Protocol):
    def capabilities(self) -> AdapterCapabilities: ...
    def stream_batches(self, request: AcquisitionRequest, cancellation: Cancellation) -> AsyncIterator[AdapterBatch]: ...

def validate_delivery(request: AcquisitionRequest, capabilities: AdapterCapabilities,
                      batches: tuple[AdapterBatch, ...], *, live: bool = False) -> None:
    """Finite conformance helper; may allocate at most requested max_rows."""
    require_adapter_capability(capabilities,request,live=live)
    if type(batches) not in (tuple,list) or not batches or any(type(x) is not AdapterBatch for x in batches): _fail("concrete finite typed delivery required")
    if len(batches)>request.max_batches: _fail("batch bound exceeded",SourceErrorCode.LIMIT)
    total=0
    first: CanonicalBatch | None = None
    combined: list[CanonicalBatch] = []
    input_ids: set[str] = set()
    for i,envelope in enumerate(batches):
        if envelope.request_id!=request.request_id or envelope.ordinal!=i or envelope.final!=(i==len(batches)-1): _fail("request/ordinal/final mismatch")
        if envelope.source.snapshot_id!=request.snapshot_id: _fail("snapshot mismatch")
        batch=envelope.batch
        if batch is None:
            if len(batches)!=1: _fail("absent delivery must be a single terminal envelope")
            continue
        if envelope.source.input_id in input_ids: _fail("duplicate delivered input identity")
        input_ids.add(envelope.source.input_id)
        total+=batch.row_count
        if batch.row_count>request.max_batch_rows or total>request.max_rows: _fail("row bound exceeded",SourceErrorCode.LIMIT)
        meta=batch.metadata
        if batch.kind!=request.kind or meta.namespace!=request.namespace or meta.price_unit!=request.price_unit or meta.adjustment!=request.adjustment or meta.sampling!=request.sampling or meta.ordering!="declared" or meta.duplicate_policy!="reject": _fail("kind/namespace/unit/basis/sampling/order mismatch")
        if first is not None:
            if tuple(c.name for c in first.columns)!=tuple(c.name for c in batch.columns) or (meta.source.source_id,meta.source.mapping_version,meta.coverage)!=(first.metadata.source.source_id,first.metadata.source.mapping_version,first.metadata.coverage): _fail("inconsistent batch schema/source/mapping/coverage")
        else: first=batch
        fields={c.name:c.values for c in batch.columns}
        for j in range(batch.row_count):
            if fields['instrument_id'][j] not in request.instruments or fields['session_id'][j] not in request.sessions: _fail("unrequested entity")
            if request.selection=="completed_intervals":
                start=cast(int,fields['start_ns'][j]);end=cast(int,fields['end_ns'][j])
                if not request.start_ns<=start<end<=request.end_ns: _fail("interval outside acquisition bounds")
            else:
                stamp=cast(int,fields['event_ns' if request.selection=="event_half_open" else 'effective_start_ns'][j])
                if not request.start_ns<=stamp<request.end_ns: _fail("row outside half-open acquisition bounds")
        combined.append(batch)
    if first is not None:
        columns=tuple(Column(c.name,tuple(value for batch in combined for value in batch.columns[index].values)) for index,c in enumerate(first.columns))
        try: validate_batch(CanonicalBatch(first.kind,columns,first.metadata),required_fields=())
        except ContractError as error: raise SourceError(SourceErrorCode.SCHEMA,"canonical delivery validation failed") from error
