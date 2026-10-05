"""Synthetic finite fixture adapter; outside the calculation distributions."""
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
import hashlib
import json
from typing import Iterator, cast
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, Coverage, DataKind,
    PriceUnit, SourceBinding,
)
from equity_feature_contracts.adapters import (
    AcquisitionRequest, AdapterBatch, AdapterCapabilities, Cancellation,
    HistoricalAdapter, SourceError, SourceErrorCode, require_adapter_capability,
    validate_delivery,
)
from equity_feature_contracts.validation import validate_batch

@dataclass(frozen=True)
class NeverCancelled:
    def is_cancelled(self) -> bool:
        return False

@dataclass(frozen=True)
class InMemoryTradeAdapter:
    source: SourceBinding
    namespace: str
    price_unit: PriceUnit
    range_start_ns: int
    range_end_ns: int
    data: CanonicalBatch | None

    def __post_init__(self) -> None:
        # Reuse exact request admission for certified synthetic fixture bounds.
        AcquisitionRequest("fixture",DataKind.TRADE,self.namespace,("fixture",),
            ("fixture",),self.range_start_ns,self.range_end_ns,self.source.snapshot_id,
            self.price_unit,AvailabilitySpec(self.range_end_ns,self.range_end_ns,self.range_end_ns))
        if self.data is not None:
            meta=self.data.metadata
            if self.data.kind!=DataKind.TRADE or meta.namespace!=self.namespace or meta.price_unit!=self.price_unit or meta.source!=self.source or meta.adjustment.basis!="raw" or meta.ordering!="declared" or meta.duplicate_policy!="reject":
                raise SourceError(SourceErrorCode.SCHEMA,"fixture metadata mismatch")
            if meta.coverage!=Coverage(self.data.row_count,self.data.row_count,True):
                raise SourceError(SourceErrorCode.SCHEMA,"synthetic fixture requires explicit complete source coverage")
            validate_batch(self.data,required_fields=())
            fields={c.name:c.values for c in self.data.columns}
            if any(not self.range_start_ns<=cast(int,x)<self.range_end_ns for x in fields['event_ns']):
                raise SourceError(SourceErrorCode.SCHEMA,"fixture row outside certified range")
            if any(x in ("opening_auction","closing_auction") for x in fields.get('condition',())):
                raise SourceError(SourceErrorCode.UNSUPPORTED,"fixture supports ordinary events only")

    def capabilities(self) -> AdapterCapabilities:
        return AdapterCapabilities((DataKind.TRADE,),(self.namespace,),(self.price_unit,),max_batch_rows=1024)

    def iter_batches(self, request: AcquisitionRequest, cancellation: Cancellation) -> Iterator[AdapterBatch]:
        require_adapter_capability(self.capabilities(),request)
        if request.snapshot_id!=self.source.snapshot_id or request.start_ns<self.range_start_ns or request.end_ns>self.range_end_ns or request.adjustment.policy_version!="raw-v1" or request.adjustment.action_snapshot!="none" or request.adjustment.anchor!="none":
            raise SourceError(SourceErrorCode.UNSUPPORTED,"request outside fixed fixture snapshot/range/basis")
        if cancellation.is_cancelled(): raise SourceError(SourceErrorCode.CANCELLED,"cancelled at batch boundary")
        if self.data is None:
            yield AdapterBatch(request.request_id,0,True,self.source,Coverage(None,0,False),Coverage(None,0,False),None,"missing","synthetic dataset absent")
            return
        fields={c.name:c.values for c in self.data.columns}
        indices=tuple(i for i in range(self.data.row_count) if fields['instrument_id'][i] in request.instruments and fields['session_id'][i] in request.sessions and request.start_ns<=cast(int,fields['event_ns'][i])<request.end_ns)
        count=len(indices)
        chunks=max(1,(count+request.max_batch_rows-1)//request.max_batch_rows)
        if count>request.max_rows or chunks>request.max_batches: raise SourceError(SourceErrorCode.LIMIT,"complete fixture slice exceeds explicit resource bounds")
        for ordinal in range(chunks):
            if cancellation.is_cancelled(): raise SourceError(SourceErrorCode.CANCELLED,"cancelled at batch boundary")
            selected=indices[ordinal*request.max_batch_rows:(ordinal+1)*request.max_batch_rows]
            slice_digest=hashlib.sha256(json.dumps({"source":asdict(self.source),"rows":selected},sort_keys=True,separators=(",",":")).encode()).hexdigest()
            source=replace(self.source,input_id=f"{self.source.input_id}:slice:{slice_digest}")
            metadata=replace(self.data.metadata,source=source)
            batch=CanonicalBatch(DataKind.TRADE,tuple(Column(c.name,tuple(c.values[i] for i in selected)) for c in self.data.columns),metadata)
            yield AdapterBatch(request.request_id,ordinal,ordinal==chunks-1,source,metadata.coverage,Coverage(len(selected),len(selected),True),batch)


def synthetic_adapter() -> InMemoryTradeAdapter:
    source=SourceBinding("synthetic","snapshot1","mapping1","fixture1")
    unit=PriceUnit(4,"USD")
    metadata=BatchMetadata("demo",source,Coverage(3,3,True),unit)
    batch=CanonicalBatch(DataKind.TRADE,tuple(Column(name,values) for name,values in (
        ("instrument_id",("A","A","A")),("session_id",("S","S","S")),
        ("event_ns",(101,102,103)),("order_key",(1,2,3)),("event_id",("e1","e2","e3")),
        ("eligible",(True,True,True)),("price",(10001,10002,10003)),("size",(1,2,3)),
        ("known_at_ns",(101,None,999)),)),metadata)
    return InMemoryTradeAdapter(source,"demo",unit,100,200,batch)


def main() -> None:
    adapter: HistoricalAdapter = synthetic_adapter()
    request=AcquisitionRequest("demo-request",DataKind.TRADE,"demo",("A",),("S",),
        100,104,"snapshot1",PriceUnit(4,"USD"),AvailabilitySpec(104,104,104),max_batch_rows=2)
    batches=tuple(adapter.iter_batches(request,NeverCancelled()))
    validate_delivery(request,adapter.capabilities(),batches)
    assert [x.batch.row_count for x in batches if x.batch is not None]==[2,1]
    assert batches[1].batch is not None
    known = batches[1].batch.column("known_at_ns")
    assert known is not None and known.values==(999,)  # retained for caller admission
    print("Synthetic historical Protocol, bounded chunks and original knowledge evidence verified")

if __name__ == "__main__":
    main()
