"""Independent pre-code byte oracles and supplied-content mutation checks."""
from dataclasses import replace
import hashlib
import json
import math
from pathlib import Path
import unittest
from unittest.mock import patch
from equity_feature_contracts import inputs as i, results as r, specs as s
from equity_feature_evidence import canonical_content, content_chunks, fingerprint_config, fingerprint_batch, fingerprint_result, verify_content, EvidenceError
from equity_feature_evidence import _content as c
from equity_feature_evidence import make_content_receipt, verify_receipt_content, EnvironmentDeclaration, ExecutionClaim, EvidenceDisclosure, PackageVersion


def config():
    return s.ConfigSpec('fixture-config', 'v1', (s.Parameter('negative_zero', -0.0), s.Parameter('precise', 9007199254740993)),
        s.SessionSpec('fixture', 'S', i.I64_MIN, i.I64_MAX, 'caller'), s.WindowSpec(1, 'S', ('P', 'S')),
        s.AvailabilitySpec(9007199254740993, 9007199254740993, i.I64_MAX), price_unit=i.PriceUnit(0, 'USD'))


def result():
    entity = r.EntityKey('A', 'S')
    return r.FeatureResult((r.FeatureColumn('fixture.scalar','v1',r.ValueType.FLOAT64,'ratio',(entity,),(-0.0,)),),
        (r.QualityRow(entity,'fixture.scalar',r.Status.AVAILABLE,1,1),),
        r.ResultMetadata('fixture','S',s.AvailabilitySpec(0,0,0),'0'*64,(),'fixture','v1'))


def batch():
    return i.CanonicalBatch(i.DataKind.TRADE, tuple(i.Column(k,(v,)) for k,v in (
        ('instrument_id','A'),('session_id','S'),('event_ns',i.I64_MIN),('order_key',9007199254740993),
        ('event_id','t1'),('eligible',True),('price',None),('size',17),('known_at_ns',None))),
        i.BatchMetadata('fixture',i.SourceBinding('synthetic','snapshot0','v1','input0'),i.Coverage(1,1,True),i.PriceUnit(2,'USD')))


def lexical_stats(value, depth=0):
    if isinstance(value, dict):
        stats = [lexical_stats(x, depth+1) for pair in value.items() for x in pair]
        return 1+sum(x[0] for x in stats), max([depth+1]+[x[1] for x in stats])
    if isinstance(value, list):
        stats = [lexical_stats(x,depth+1) for x in value]
        return 1+sum(x[0] for x in stats), max([depth+1]+[x[1] for x in stats])
    return 1, depth


class ContentTests(unittest.TestCase):
    def test_three_independent_oracles(self):
        cases = [('CONFIG',config(),1341,'e1b12d267ef25cadd48549725e7ff1c8f1f4254bde30b910ee8fd27aaee5585d',129,7),
            ('RESULT',result(),1219,'4f78413ee898ed72031423695a16bdb4d8a3d7f5b38b4f814bd709fbed8dc287',121,9),
            ('BATCH',batch(),1558,'fa7e282711dc54e88bf2ae51a247a4969ea416be74e1bfe3e4e633207998e1bf',183,7)]
        for name,value,size,digest,nodes,depth in cases:
            with self.subTest(name=name):
                expected=(Path(__file__).resolve().parents[2]/f'docs/stories/EQ-097_{name}_ORACLE.json').read_bytes()
                self.assertEqual((len(expected),hashlib.sha256(expected).hexdigest()),(size,digest))
                self.assertEqual(canonical_content(value),expected)
                self.assertEqual(b''.join(content_chunks(value)),expected)
                b=c._Budget(); c._validate(value,b)
                self.assertEqual((b.size,b.nodes),(size,nodes))
                self.assertEqual(lexical_stats(json.loads(expected)),(nodes,depth))
                with patch.object(c,'MAX_CONTENT_BYTES',size),patch.object(c,'MAX_CONTENT_NODES',nodes),patch.object(c,'MAX_CONTENT_DEPTH',depth):
                    self.assertEqual(canonical_content(value),expected)
                for key,bound in [('MAX_CONTENT_BYTES',size-1),('MAX_CONTENT_NODES',nodes-1),('MAX_CONTENT_DEPTH',depth-1)]:
                    with patch.object(c,key,bound), self.assertRaises(EvidenceError): next(content_chunks(value))

    def test_column_presentation_only_sort(self):
        value=batch(); other=replace(value,columns=tuple(reversed(value.columns)))
        self.assertEqual(fingerprint_batch(value),fingerprint_batch(other))
        changed=replace(value,columns=tuple(replace(x,values=(18,)) if x.name=='size' else x for x in value.columns))
        self.assertEqual(value.metadata,changed.metadata)
        self.assertNotEqual(fingerprint_batch(value),fingerprint_batch(changed))
        self.assertFalse(verify_content(fingerprint_batch(value),changed))

    def test_metadata_quality_and_output_mutations(self):
        value=result(); ref=fingerprint_result(value)
        for changed in (replace(value,values=(replace(value.values[0],values=(0.0,)),)),
                        replace(value,metadata=replace(value.metadata,backend_version='v2')),
                        replace(value,quality=(replace(value.quality[0],expected=2,observed=2),))):
            self.assertFalse(verify_content(ref,changed))
        changed=replace(value,values=(replace(value.values[0],values=(math.ulp(0.0),)),))
        self.assertNotEqual(ref,fingerprint_result(changed))

    def test_payload_precision_types_and_unicode(self):
        value=config()
        variants=[None,True,1,1.0,0.0,-0.0,10**38-1,-(10**38-1),'', 'a\x00\n', 'é', 'e\u0301', math.ulp(0.0)]
        digests=set()
        for item in variants:
            actual=replace(value,parameters=(s.Parameter('x',item),))
            digests.add(fingerprint_config(actual).digest)
        self.assertEqual(len(digests),len(variants))
        for item in (10**38,-10**38,'\ud800','x'*4097):
            with self.assertRaises(EvidenceError): canonical_content(replace(value,parameters=(s.Parameter('x',item),)))

    def test_unsupported_objects_no_callbacks_or_lazy_iteration(self):
        class Trap:
            def __iter__(self): raise AssertionError('must not iterate')
            def __str__(self): raise AssertionError('must not stringify')
        for item in (Trap(),{},[],b'bytes',1):
            with self.assertRaises(EvidenceError): canonical_content(item)
        with patch.object(c.contracts,'__version__','9'):
            with self.assertRaises(EvidenceError) as caught: fingerprint_config(config())
        self.assertEqual(caught.exception.code,'unsupported_version')

    def test_stream_chunk_limits_and_source_immutable(self):
        value=replace(config(),parameters=tuple(s.Parameter(str(n),'𐀀'*1000) for n in range(20)))
        before=value.to_json(); chunks=list(content_chunks(value))
        self.assertGreater(len(chunks),1)
        self.assertTrue(all(0<len(x)<=65536 for x in chunks))
        self.assertEqual(b''.join(chunks),canonical_content(value))
        self.assertEqual(value.to_json(),before)
        self.assertEqual(hashlib.sha256(b''.join(chunks)).hexdigest(),fingerprint_config(value).digest)

    def test_all_batch_kinds_missing_null_and_row_order(self):
        for kind in i.DataKind:
            columns=[]
            for field in i.schema_for(kind).fields:
                if not field.required: continue
                value = 'A' if field.dtype == i.DType.STRING else True if field.dtype == i.DType.BOOL else 1
                columns.append(i.Column(field.name,(value,)))
            meta=replace(batch().metadata,sampling='continuous' if kind==i.DataKind.QUOTE else 'none')
            value=i.CanonicalBatch(kind,tuple(columns),meta)
            self.assertTrue(verify_content(fingerprint_batch(value),value))
            optional=next(f for f in i.schema_for(kind).fields if not f.required)
            other=replace(value,columns=value.columns+(i.Column(optional.name,(None,)),))
            self.assertNotEqual(fingerprint_batch(value),fingerprint_batch(other))
        value=batch()
        two=replace(value,columns=tuple(replace(x,values=x.values*2) for x in value.columns))
        two=replace(two,columns=tuple(replace(x,values=(1,2)) if x.name=='order_key' else x for x in two.columns))
        reverse=replace(two,columns=tuple(replace(x,values=tuple(reversed(x.values))) for x in two.columns))
        self.assertNotEqual(fingerprint_batch(two),fingerprint_batch(reverse))

    def test_every_result_value_type(self):
        entity=r.EntityKey('A','S'); quality=r.QualityRow(entity,'fixture.scalar',r.Status.AVAILABLE,1,1)
        interval=s.IntervalSpec('regular',0,10)
        samples=(1,10**38-1,1.0,'a\n',True,r.BreadthCounts(1,0,0,1),r.BreadthFraction(1,1,1),
            r.TimeWeightedSpread(r.QuoteDurations(1,0,0,0,0,0),1.0,1.0,1,'seed'),
            r.QuoteStateCounts(1,0,0,0),r.SampledSpread('continuous',1,1,1.0,1.0,1,
                (r.QuoteObservation('input','event',0,0,0,1,2,'normal',1.0,1.0),)),
            r.TopKTrades(1,(r.TopKTradeRow('input','event',0,0,0,1,1),)),
            r.IntervalOHLCV((r.IntervalOHLCVRow(interval,1.0,1.0,1.0,1.0,1,quality),)),
            r.IntervalVolumeShares((r.IntervalVolumeShareRow(interval,1.0,quality),)))
        self.assertEqual(len(samples),len(r.ValueType))
        for dtype,sample in zip(r.ValueType,samples):
            with self.subTest(dtype=dtype):
                meta=result().metadata; evidence=()
                if dtype in (r.ValueType.TIME_WEIGHTED_SPREAD,r.ValueType.QUOTE_STATE_COUNTS,r.ValueType.SAMPLED_SPREAD,r.ValueType.TOP_K_TRADES):
                    quote=dtype != r.ValueType.TOP_K_TRADES
                    bm=replace(batch().metadata,source=i.SourceBinding('synthetic','snapshot','v1','input'),
                        sampling='continuous' if quote else 'none',scope=i.InputScope(0,1,'fixture'))
                    meta=replace(meta,availability=s.AvailabilitySpec(1,1,1),
                        inputs=(r.InputBinding('quotes' if quote else 'trades',i.DataKind.QUOTE if quote else i.DataKind.TRADE,bm),),evidence_limit=1)
                    if dtype in (r.ValueType.SAMPLED_SPREAD,r.ValueType.TOP_K_TRADES):
                        evidence=(r.EvidenceRow(entity,'fixture.scalar','input','event',0,0),)
                value=replace(result(),values=(replace(result().values[0],dtype=dtype,values=(sample,)),),metadata=meta,evidence=evidence)
                wire=canonical_content(value)
                self.assertEqual(hashlib.sha256(wire).hexdigest(),fingerprint_result(value).digest)
                self.assertEqual(json.loads(wire)['value']['fields']['values'][0]['fields']['dtype'],dtype.value)

    def test_valid_fingerprint_mismatch(self):
        value=config(); ref=fingerprint_config(value)
        self.assertFalse(verify_content(replace(ref,byte_length=ref.byte_length+1),value))
        self.assertFalse(verify_content(replace(ref,domain='canonical_batch'),value))

    def test_receipt_full_binding_and_aggregate_prevalidation(self):
        cfg=config(); data=batch()
        output=replace(result(),metadata=replace(result().metadata,availability=cfg.availability,
            config_digest=cfg.digest,inputs=(r.InputBinding('trades',data.kind,data.metadata),)))
        env=EnvironmentDeclaration('CPython','3.12','caller',(PackageVersion('equity-feature-contracts','0.0.4a4'),))
        receipt=make_content_receipt(output,cfg,(('trades',data),),env,ExecutionClaim(),EvidenceDisclosure('not_supplied',0))
        self.assertTrue(verify_receipt_content(receipt,cfg,(('trades',data),),output))
        for changed in (replace(data,metadata=replace(data.metadata,ordering='unsorted')),
                        replace(data,metadata=replace(data.metadata,source=replace(data.metadata.source,snapshot_id='revision')))):
            self.assertFalse(verify_receipt_content(receipt,cfg,(('trades',changed),),output))
        self.assertFalse(verify_receipt_content(receipt,cfg,(('other',data),),output))
        self.assertFalse(verify_receipt_content(receipt,replace(cfg,identity='different'),(('trades',data),),output))
        size=sum(len(canonical_content(v)) for v in (cfg,data,output))
        with patch.object(c,'MAX_CONTENT_BYTES',size):
            self.assertEqual(make_content_receipt(output,cfg,(('trades',data),),env,ExecutionClaim(),EvidenceDisclosure('not_supplied',0)),receipt)
        with patch.object(c,'MAX_CONTENT_BYTES',size-1),patch.object(c,'_fingerprint',side_effect=AssertionError('must prevalidate')):
            with self.assertRaises(EvidenceError) as caught:
                make_content_receipt(output,cfg,(('trades',data),),env,ExecutionClaim(),EvidenceDisclosure('not_supplied',0))
        self.assertEqual(caught.exception.code,'limit_exceeded')

    def test_nonfinite_and_string_label_rejection(self):
        for value in (float('nan'),float('inf'),float('-inf')):
            with self.assertRaises(EvidenceError): list(c._visit(value,0,c._Budget()))
        with self.assertRaises(EvidenceError): canonical_content(replace(config(),identity='bad\nlabel'))

if __name__ == '__main__': unittest.main()
