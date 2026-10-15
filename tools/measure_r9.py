"""Measured R9 composition cost; trusted qualification tool, never a calculation API."""
from __future__ import annotations
import gc
import importlib.util
from importlib.metadata import version
import json
from pathlib import Path
import platform
import sys
from time import perf_counter_ns
import tracemalloc
from equity_feature_contracts import (AvailabilitySpec,BatchMetadata,CanonicalBatch,Column,ConfigSpec,Coverage,
    DataKind,InputScope,Parameter,PriceUnit,SessionSpec,SourceBinding,WindowSpec)
from equity_feature_evidence import canonical_content,make_content_receipt,encode_receipt,ExecutionClaim,EvidenceDisclosure
from equity_feature_explanations import explain_result,encode_explanation
from equity_feature_bundles import read_bundle,write_bundle
from equity_feature_bundles.replay import replay_bundle
from equity_features.session import compute_trades

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('trusted_r9_example',ROOT/'examples/r9_reproduction.py')
example=importlib.util.module_from_spec(spec);spec.loader.exec_module(example)


def population(n):
    config=ConfigSpec('r9-cost','v1',(Parameter('eligibility_policy','example-v1'),),
        SessionSpec('demo','S',0,n+1,'caller'),WindowSpec(1,'S',('P','S')),
        AvailabilitySpec(n+1,n+1,n+1),price_unit=PriceUnit(0,'USD'))
    batch=CanonicalBatch(DataKind.TRADE,tuple(Column(k,v) for k,v in (
        ('instrument_id',('A',)*n),('session_id',('S',)*n),('event_ns',tuple(range(1,n+1))),
        ('order_key',tuple(range(1,n+1))),('event_id',tuple('t'+str(i) for i in range(1,n+1))),
        ('eligible',(True,)*n),('price',(100,)*n),('size',(1,)*n),('known_at_ns',tuple(range(1,n+1))),
    )),BatchMetadata('demo',SourceBinding('synthetic','snapshot1','map1','trades1'),
        Coverage(n,n,True),PriceUnit(0,'USD'),scope=InputScope(0,n+1,'example-v1')))
    return config,batch


def measure():
    samples=[]
    for n in (10,1000):
        config,batch=population(n);inputs=(('trades',batch),)
        result=compute_trades(batch,config,entity=example.ENTITY)
        assert tuple(c.values[0] for c in result.values)==(n,n,100*n,100.0,1.0)
        receipt=make_content_receipt(result,config,inputs,example.ENVIRONMENT,ExecutionClaim(),EvidenceDisclosure('not_supplied',0))
        raw=write_bundle(receipt,config,result,inputs,example.PUBLICATION)
        summary=explain_result(result,receipt,config,entity=example.ENTITY,feature_id='session.trade.count',inputs=inputs)
        sizes={'input_bytes':len(canonical_content(batch)),'result_bytes':len(canonical_content(result)),
            'receipt_bytes':len(encode_receipt(receipt)),'explanation_bytes':len(encode_explanation(summary)),'bundle_bytes':len(raw)}
        def calculate():return compute_trades(batch,config,entity=example.ENTITY)
        def receipt_encode():
            r=make_content_receipt(result,config,inputs,example.ENVIRONMENT,ExecutionClaim(),EvidenceDisclosure('not_supplied',0))
            return r,encode_receipt(r)
        def explain_encode():
            s=explain_result(result,receipt,config,entity=example.ENTITY,feature_id='session.trade.count',inputs=inputs)
            return s,encode_explanation(s)
        def bundle_write():return write_bundle(receipt,config,result,inputs,example.PUBLICATION)
        def read_replay_explain_encode():
            b=read_bundle(raw);r=replay_bundle(b)
            s=explain_result(b.result,b.receipt,b.configuration,entity=b.manifest.entity,feature_id='session.trade.count',
                inputs=tuple((x.role,x.batch) for x in b.inputs if x.batch is not None))
            return b,r,s,encode_explanation(s)
        phases=(('calculate',calculate),('receipt_encode',receipt_encode),('explain_encode',explain_encode),
            ('bundle_write',bundle_write),('read_replay_explain_encode',read_replay_explain_encode))
        for repeat in range(3):
            for name,operation in phases:
                gc.collect();tracemalloc.start()
                try:
                    start=perf_counter_ns();output=operation();elapsed=perf_counter_ns()-start
                    current,peak=tracemalloc.get_traced_memory()
                finally:tracemalloc.stop()
                assert type(elapsed) is int and elapsed>=0 and 0<=current<=peak
                replay_ns=None
                if name=='calculate':assert canonical_content(output)==canonical_content(result)
                elif name=='receipt_encode':assert output[1]==encode_receipt(receipt)
                elif name=='explain_encode':assert output[1]==encode_explanation(summary)
                elif name=='bundle_write':assert output==raw
                else:
                    b,r,s,encoded=output
                    assert canonical_content(b.result)==canonical_content(result)
                    assert r.status=='matched' and r.result_match is True and r.calculation_count==1 and not r.declared_environment_verified
                    assert encoded==encode_explanation(summary) and not s.source_authenticated and not s.execution_verified
                    replay_ns=r.elapsed_ns
                samples.append({'rows':n,'repeat':repeat,'phase':name,'elapsed_ns':elapsed,'traced_current_bytes':current,
                    'traced_peak_bytes':peak,'replay_elapsed_ns':replay_ns,'sizes':sizes,'parity':True})
                del output
    assert len(samples)==30
    return {'schema':'r9-costs:1','system':platform.system(),'python':platform.python_version(),
        'packages':{n:version(n) for n in ('equity-feature-contracts','equity-features','equity-feature-evidence','equity-feature-explanations','equity-feature-bundles')},
        'preparation_calculations':2,'measured_direct_calculations':6,'measured_replay_calculations':6,
        'samples':samples,'status':'completed','protocol':'EQ-100_PLAN.md; traced Python allocations exclude preowned inputs/baselines, not RSS/native/physical quota or interruption deadline; no warmup/randomization/speedup claim'}


if __name__=='__main__':
    destination=Path(sys.argv[1]);assert not destination.exists()
    result=measure();destination.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('R9 cost protocol completed30raw samples; tracing overhead included, no physical-memory/deadline claim.')
