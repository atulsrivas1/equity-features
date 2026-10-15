"""Fixed synthetic cost protocol; run outside pure packages in a combined installed consumer."""
from dataclasses import replace
import hashlib
import json
import platform
import sys
import time
import tracemalloc
from equity_feature_contracts import (AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec,
    Coverage, DataKind, EntityKey, InputScope, Parameter, PriceUnit, SessionSpec, SourceBinding, WindowSpec)
from equity_features.session import compute_trades
from equity_feature_evidence import (canonical_content, fingerprint_batch, make_content_receipt,
    verify_receipt_content, EnvironmentDeclaration, ExecutionClaim, EvidenceDisclosure, PackageVersion)


def fixture(rows):
    cfg=ConfigSpec('cost-fixture','v1',(Parameter('eligibility_policy','fixture-v1'),),
        SessionSpec('cost','S',0,rows+1,'caller'),WindowSpec(1,'S',('P','S')),
        AvailabilitySpec(rows+1,rows+1,rows+1),price_unit=PriceUnit(0,'USD'))
    batch=CanonicalBatch(DataKind.TRADE,tuple(Column(name,values) for name,values in (
        ('instrument_id',('A',)*rows),('session_id',('S',)*rows),('event_ns',tuple(range(rows))),
        ('order_key',tuple(range(rows))),('event_id',tuple('t'+str(n) for n in range(rows))),
        ('eligible',(True,)*rows),('price',(100,)*rows),('size',(2,)*rows),('known_at_ns',tuple(range(rows))))),
        BatchMetadata('cost',SourceBinding('synthetic','fixed-v1','map-v1','trades'),Coverage(rows,rows,True),
            PriceUnit(0,'USD'),scope=InputScope(0,rows+1,'fixture-v1')))
    return cfg,batch,compute_trades(batch,cfg,entity=EntityKey('A','S'))


def measure():
    report={'schema':'evidence-content-cost:1','python':platform.python_version(),'implementation':platform.python_implementation(),
        'platform':platform.platform(),'existing_input_storage':'excluded: input graph, precomputed result and hash-only wire already owned',
        'limits':'tracemalloc incremental Python peak only; not native allocation/RSS/physical quota; no speedup claim', 'samples':[]}
    for rows in (1000,10000):
        cfg,batch,result=fixture(rows); wire=canonical_content(batch); fp=fingerprint_batch(batch)
        assert hashlib.sha256(wire).hexdigest()==fp.digest and len(wire)==fp.byte_length
        values={c.feature_id:c.values[0] for c in result.values}
        assert tuple(values.values())==(rows,2*rows,200*rows,100.0,2.0)
        env=EnvironmentDeclaration('CPython','3.12','synthetic-cost-caller',(PackageVersion('equity-feature-contracts','0.0.4a4'),))
        def receipt(): return make_content_receipt(result,cfg,(('trades',batch),),env,ExecutionClaim(),EvidenceDisclosure('not_supplied',0))
        assert verify_receipt_content(receipt(),cfg,(('trades',batch),),result)
        operations=(('materialize',lambda:canonical_content(batch)),('hash_owned_bytes',lambda:hashlib.sha256(wire).hexdigest()),
            ('stream_fingerprint',lambda:fingerprint_batch(batch)),('content_receipt',receipt))
        for name,operation in operations:
            for repeat in range(3):
                tracemalloc.start()
                start=time.perf_counter_ns(); actual=operation(); elapsed=time.perf_counter_ns()-start
                _,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
                if name=='materialize': assert actual==wire
                elif name=='hash_owned_bytes': assert actual==fp.digest
                elif name=='stream_fingerprint': assert actual==fp
                else: assert verify_receipt_content(actual,cfg,(('trades',batch),),result)
                report['samples'].append({'rows':rows,'encoded_bytes':len(wire),'operation':name,'repeat':repeat,
                    'elapsed_ns':elapsed,'incremental_python_peak_bytes':peak,'parity':True})
    assert len(report['samples'])==24
    return report


if __name__=='__main__':
    json.dump(measure(),sys.stdout,sort_keys=True);print()
