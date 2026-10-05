"""Independent synthetic adapter conformance and boundary regressions."""
import unittest
from dataclasses import replace
from equity_feature_contracts import (AvailabilitySpec, BatchMetadata, CanonicalBatch,
    Column, Coverage, DataKind, PriceUnit, SourceBinding, AdjustmentSpec)
from equity_feature_contracts.adapters import (AcquisitionRequest, AdapterBatch,
    AdapterCapabilities, SourceError, SourceErrorCode, require_adapter_capability,
    validate_delivery)
from examples.in_memory_adapter import InMemoryTradeAdapter, NeverCancelled, synthetic_adapter

class AdapterTests(unittest.TestCase):
    def setUp(self):
        self.adapter=synthetic_adapter()
        self.request=AcquisitionRequest("r1",DataKind.TRADE,"demo",("A",),("S",),100,104,
            "snapshot1",PriceUnit(4,"USD"),AvailabilitySpec(104,104,104),max_batch_rows=2)
        self.batches=tuple(self.adapter.iter_batches(self.request,NeverCancelled()))
    def error(self,code,call):
        with self.assertRaises(SourceError) as caught: call()
        self.assertEqual(caught.exception.code,code)
    def test_chunk_counts_and_original_coverage(self):
        validate_delivery(self.request,self.adapter.capabilities(),self.batches)
        self.assertEqual([b.batch.row_count for b in self.batches],[2,1])
        self.assertEqual([b.final for b in self.batches],[False,True])
        self.assertTrue(all(b.source_coverage==Coverage(3,3,True) for b in self.batches))
        self.assertEqual([b.delivery_coverage for b in self.batches],[Coverage(2,2,True),Coverage(1,1,True)])
    def test_known_at_null_and_future_preserved(self):
        self.assertEqual([x for b in self.batches for x in b.batch.column('known_at_ns').values],[101,None,999])
        later=replace(self.request,availability=AvailabilitySpec(104,1000,1000))
        self.assertEqual(tuple(self.adapter.iter_batches(later,NeverCancelled())),self.batches)
    def test_half_open_boundary(self):
        request=replace(self.request,start_ns=102,end_ns=103)
        batches=tuple(self.adapter.iter_batches(request,NeverCancelled()))
        self.assertEqual(batches[0].batch.column('event_ns').values,(102,))
        validate_delivery(request,self.adapter.capabilities(),batches)
    def test_observed_empty_is_not_missing(self):
        request=replace(self.request,instruments=('absent',))
        batch=tuple(self.adapter.iter_batches(request,NeverCancelled()))[0]
        self.assertEqual(batch.disposition,'observed');self.assertEqual(batch.batch.row_count,0)
        self.assertEqual(batch.delivery_coverage,Coverage(0,0,True))
        validate_delivery(request,self.adapter.capabilities(),(batch,))
    def test_missing_dataset_has_no_zero_observation(self):
        adapter=replace(self.adapter,data=None)
        batches=tuple(adapter.iter_batches(self.request,NeverCancelled()))
        self.assertIsNone(batches[0].batch);self.assertEqual(batches[0].disposition,'missing')
        self.assertEqual(batches[0].delivery_coverage,Coverage(None,0,False))
        validate_delivery(self.request,adapter.capabilities(),batches)
    def test_unavailable_envelope(self):
        b=AdapterBatch('r1',0,True,self.adapter.source,Coverage(None,0,False),Coverage(None,0,False),None,'unavailable','explicit fixture outage')
        validate_delivery(self.request,self.adapter.capabilities(),(b,))
    def test_bad_absent_coverage_and_reason(self):
        self.error(SourceErrorCode.SCHEMA,lambda: AdapterBatch('r1',0,True,self.adapter.source,Coverage(None,0,False),Coverage(0,0,True),None,'missing','missing'))
        self.error(SourceErrorCode.SCHEMA,lambda: AdapterBatch('r1',0,True,self.adapter.source,Coverage(None,0,False),Coverage(None,0,False),None,'missing'))
    def test_request_ownership_and_precision(self):
        ids=['A'];request=replace(self.request,instruments=ids,start_ns=101,end_ns=104)
        ids.append('B');self.assertEqual(request.instruments,('A',))
        for changes in ({'start_ns':100.0},{'start_ns':True},{'end_ns':2**63},{'end_ns':100},{'instruments':('A','A')},{'max_rows':0},{'max_batches':True},{'schema_version':'2'},{'selection':'closing_auction'}):
            self.error(SourceErrorCode.SCHEMA,lambda changes=changes:replace(self.request,**changes))
    def test_no_lazy_request_or_delivery(self):
        self.error(SourceErrorCode.SCHEMA,lambda:replace(self.request,instruments=iter(('A',))))
        self.error(SourceErrorCode.SCHEMA,lambda:validate_delivery(self.request,self.adapter.capabilities(),iter(self.batches)))
    def test_unsupported_live_and_unit_and_range(self):
        self.error(SourceErrorCode.UNSUPPORTED,lambda:require_adapter_capability(self.adapter.capabilities(),self.request,live=True))
        for changes in ({'namespace':'other'},{'price_unit':PriceUnit(5,'USD')},{'price_unit':PriceUnit(4,'EUR')},{'snapshot_id':'other'},{'end_ns':201},{'adjustment':AdjustmentSpec('split','p','a','s')}):
            self.error(SourceErrorCode.UNSUPPORTED,lambda changes=changes:tuple(self.adapter.iter_batches(replace(self.request,**changes),NeverCancelled())))
    def test_no_silent_resource_truncation(self):
        for changes in ({'max_rows':2},{'max_batches':1}):
            self.error(SourceErrorCode.LIMIT,lambda changes=changes:tuple(self.adapter.iter_batches(replace(self.request,**changes),NeverCancelled())))
    def test_cancellation_before_and_between_chunks(self):
        class Token:
            cancelled=True
            def is_cancelled(self):return self.cancelled
        token=Token()
        self.error(SourceErrorCode.CANCELLED,lambda:tuple(self.adapter.iter_batches(self.request,token)))
        token.cancelled=False;iterator=self.adapter.iter_batches(self.request,token)
        self.assertEqual(next(iterator).ordinal,0);token.cancelled=True
        self.error(SourceErrorCode.CANCELLED,lambda:next(iterator))
    def test_repeated_delivery_owns_identity(self):
        self.assertEqual(self.batches,tuple(self.adapter.iter_batches(self.request,NeverCancelled())))
        self.assertNotEqual(self.batches[0].source.input_id,self.batches[1].source.input_id)
        self.assertEqual(self.adapter.data.metadata.source,self.adapter.source)
    def test_envelope_ordinals_final_and_request_identity(self):
        for changes in ({'request_id':'other'},{'ordinal':1},{'final':True},{'source':replace(self.batches[0].source,snapshot_id='other')}):
            def action(changes=changes):
                first=replace(self.batches[0],**changes)
                validate_delivery(self.request,self.adapter.capabilities(),(first,self.batches[1]))
            self.error(SourceErrorCode.SCHEMA,action)
        self.error(SourceErrorCode.SCHEMA,lambda:validate_delivery(self.request,self.adapter.capabilities(),self.batches[:1]))
    def changed(self,index,**fields):
        env=self.batches[index];batch=env.batch
        columns=tuple(Column(c.name,fields.get(c.name,c.values)) for c in batch.columns)
        return replace(env,batch=replace(batch,columns=columns))
    def test_cross_batch_duplicate_and_reverse_order(self):
        for fields in ({'event_id':('e1',)},{'event_ns':(101,)},{'order_key':(2,),'event_ns':(102,)}):
            self.error(SourceErrorCode.SCHEMA,lambda fields=fields:validate_delivery(self.request,self.adapter.capabilities(),(self.batches[0],self.changed(1,**fields))))
    def test_delivery_entity_time_and_units(self):
        for fields in ({'instrument_id':('B',)},{'session_id':('X',)},{'event_ns':(104,)}):
            self.error(SourceErrorCode.SCHEMA,lambda fields=fields:validate_delivery(self.request,self.adapter.capabilities(),(self.batches[0],self.changed(1,**fields))))
        batch=replace(self.batches[1].batch,metadata=replace(self.batches[1].batch.metadata,price_unit=PriceUnit(5,'USD')))
        self.error(SourceErrorCode.SCHEMA,lambda:validate_delivery(self.request,self.adapter.capabilities(),(self.batches[0],replace(self.batches[1],batch=batch))))
    def test_delivery_total_and_batch_limits(self):
        self.error(SourceErrorCode.LIMIT,lambda:validate_delivery(replace(self.request,max_rows=2),self.adapter.capabilities(),self.batches))
        self.error(SourceErrorCode.LIMIT,lambda:validate_delivery(replace(self.request,max_batches=1),self.adapter.capabilities(),self.batches))
    def test_source_coverage_and_mapping_not_repaired(self):
        env=self.batches[1];source=replace(env.source,mapping_version='other')
        changed=replace(env,source=source,batch=replace(env.batch,metadata=replace(env.batch.metadata,source=source)))
        self.error(SourceErrorCode.SCHEMA,lambda:validate_delivery(self.request,self.adapter.capabilities(),(self.batches[0],changed)))
        self.error(SourceErrorCode.SCHEMA,lambda:replace(env,delivery_coverage=Coverage(2,2,True)))
    def test_fixture_rejects_auction_and_incomplete_source(self):
        data=self.adapter.data
        self.error(SourceErrorCode.UNSUPPORTED,lambda:replace(self.adapter,data=replace(data,columns=data.columns+(Column('condition',('closing_auction',None,None)),))))
        self.error(SourceErrorCode.SCHEMA,lambda:replace(self.adapter,data=replace(data,metadata=replace(data.metadata,coverage=Coverage(4,3,False)))))
    def test_capability_exact_schema_and_modes(self):
        for changes in ({'timestamp_precision':'milliseconds'},{'schema_version':'2'},{'historical':1},{'kinds':(DataKind.TRADE,DataKind.TRADE)},{'max_batch_rows':0}):
            self.error(SourceErrorCode.SCHEMA,lambda changes=changes:replace(self.adapter.capabilities(),**changes))
        self.error(SourceErrorCode.UNSUPPORTED,lambda:require_adapter_capability(replace(self.adapter.capabilities(),historical=False),self.request))
    def test_quote_completed_and_reference_selection_contracts(self):
        for kind,selection,sampling in ((DataKind.QUOTE,'event_half_open','continuous'),(DataKind.BAR,'completed_intervals','none'),(DataKind.DAILY,'completed_intervals','none'),(DataKind.REFERENCE,'effective_start_half_open','none')):
            request=replace(self.request,kind=kind,selection=selection,sampling=sampling)
            capabilities=replace(self.adapter.capabilities(),kinds=(kind,),sampling=(sampling,))
            require_adapter_capability(capabilities,request)
        self.error(SourceErrorCode.SCHEMA,lambda:replace(self.request,kind=DataKind.QUOTE))
    def test_changed_slice_cannot_reuse_input_identity(self):
        request=replace(self.request,start_ns=102,end_ns=104)
        other=tuple(self.adapter.iter_batches(request,NeverCancelled()))
        self.assertNotEqual(other[0].source.input_id,self.batches[0].source.input_id)
    def test_exact_nanoseconds_above_float_precision(self):
        base=1700000000000000000
        data=self.adapter.data
        columns=tuple(Column(c.name,tuple(base+x if c.name in ('event_ns','known_at_ns') and x is not None else x for x in c.values)) for c in data.columns)
        adapter=replace(self.adapter,range_start_ns=base+100,range_end_ns=base+200,data=replace(data,columns=columns))
        request=replace(self.request,start_ns=base+102,end_ns=base+103,availability=AvailabilitySpec(base+104,base+104,base+104))
        batches=tuple(adapter.iter_batches(request,NeverCancelled()))
        self.assertEqual(batches[0].batch.column('event_ns').values,(base+102,))
        validate_delivery(request,adapter.capabilities(),batches)
    def test_completed_bar_delivery_bounds(self):
        request=replace(self.request,kind=DataKind.BAR,selection='completed_intervals')
        caps=replace(self.adapter.capabilities(),kinds=(DataKind.BAR,))
        source=SourceBinding('synthetic','snapshot1','mapping1','bar1')
        metadata=BatchMetadata('demo',source,Coverage(1,1,True),PriceUnit(4,'USD'))
        batch=CanonicalBatch(DataKind.BAR,tuple(Column(name,(value,)) for name,value in (('instrument_id','A'),('session_id','S'),('start_ns',100),('end_ns',104),('close',10000))),metadata)
        envelope=AdapterBatch('r1',0,True,source,metadata.coverage,Coverage(1,1,True),batch)
        validate_delivery(request,caps,(envelope,))
        bad=replace(batch,columns=tuple(Column(c.name,(105,)) if c.name=='end_ns' else c for c in batch.columns))
        self.error(SourceErrorCode.SCHEMA,lambda:validate_delivery(request,caps,(replace(envelope,batch=bad),)))
    def test_typed_error_codes(self):
        self.assertEqual({x.value for x in SourceErrorCode},{'unsupported_capability','authentication','entitlement','rate_limit','transport','schema_mismatch','unavailable_data','cancelled','resource_limit'})
        for code in SourceErrorCode:self.assertEqual(SourceError(code,'synthetic failure').code,code)

if __name__=='__main__':unittest.main()
