"""Actual synthetic core producer; detached fingerprints remain explicit assertions."""
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage,
    DataKind, EntityKey, InputScope, Parameter, PriceUnit, SessionSpec, SourceBinding, WindowSpec,
)
from equity_features.session import compute_trades
from equity_feature_evidence import (
    ContentFingerprint, InputFingerprint, FormulaBinding, PackageVersion,
    EnvironmentDeclaration, ExecutionClaim, EvidenceDisclosure,
    make_receipt, encode_receipt, decode_receipt, receipt_digest,
)

config = ConfigSpec('receipt-demo','v1',(Parameter('eligibility_policy','example-v1'),),
    SessionSpec('demo','S',100,200,'caller'),WindowSpec(1,'S',('P','S')),
    AvailabilitySpec(200,210,210),price_unit=PriceUnit(0,'USD'))
batch = CanonicalBatch(DataKind.TRADE, tuple(Column(name, values) for name, values in (
    ('instrument_id',('A',)*3),('session_id',('S',)*3),('event_ns',(110,130,160)),
    ('order_key',(1,2,3)),('event_id',('t1','t2','t3')),('eligible',(True,)*3),
    ('price',(100,102,101)),('size',(2,3,5)),('known_at_ns',(110,130,210)),
)), BatchMetadata('demo',SourceBinding('synthetic','snapshot1','map1','trades1'),
    Coverage(3,3,True),PriceUnit(0,'USD'),scope=InputScope(100,200,'example-v1')))
result = compute_trades(batch, config, entity=EntityKey('A','S'))
before = result
from dataclasses import replace
from equity_feature_evidence import make_content_receipt, verify_receipt_content, verify_content, fingerprint_batch, fingerprint_result
receipt = make_content_receipt(result, config, (('trades',batch),),
    EnvironmentDeclaration('CPython','3.12','caller-declared',(
        PackageVersion('equity-feature-contracts','0.0.4a4'),PackageVersion('equity-features','0.0.4a4'))),
    ExecutionClaim(), EvidenceDisclosure('not_supplied',0))
assert verify_receipt_content(receipt,config,(('trades',batch),),result)
assert decode_receipt(encode_receipt(receipt)) == receipt
assert result == before
values={c.feature_id:c.values[0] for c in result.values}
assert tuple(values.values()) == (3,10,1011,101.1,10/3)
changed_batch=replace(batch,columns=tuple(replace(c,values=(2,3,6)) if c.name=='size' else c for c in batch.columns))
assert changed_batch.metadata == batch.metadata
assert not verify_content(fingerprint_batch(batch),changed_batch)
assert not verify_receipt_content(receipt,config,(('trades',changed_batch),),result)
changed_result=replace(result,values=tuple(replace(c,values=(4,)) if c.feature_id=='session.trade.count' else c for c in result.values))
assert changed_result.metadata == result.metadata
assert not verify_content(fingerprint_result(result),changed_result)
assert not verify_receipt_content(receipt,config,(('trades',batch),),changed_result)
assert not verify_receipt_content(receipt,replace(config,identity='different'),(('trades',batch),),result)
print('Actual core five-output parity and full supplied content verification passed; execution/environment declarations remain unauthenticated.')
