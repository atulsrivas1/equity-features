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
    AvailabilitySpec(200,200,210),price_unit=PriceUnit(0,'USD'))
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
from equity_feature_diagnostics import DecisionContext, DiagnosticPolicy, KnowledgeCheck, evaluate_diagnostics
from equity_feature_evidence import canonical_content
before_result=canonical_content(result);before_receipt=encode_receipt(receipt)
assert all(q.status.value=='missing_input' and 'future_knowledge' in q.reasons for q in result.quality)
known=next(c.values for c in batch.columns if c.name=='known_at_ns')
report=evaluate_diagnostics(DecisionContext('demo',EntityKey('A','S'),config.availability),
    DiagnosticPolicy('selected-rows','strict','deny'),
    tuple(KnowledgeCheck('row'+str(k),'trades1:'+str(k),t,content=fingerprint_batch(batch)) for k,t in enumerate(known)))
assert tuple(f.status for f in report.findings)==('passed','passed','failed')
assert report.findings[2].reasons==('late_knowledge',) and report.admission=='denied'
assert canonical_content(result)==before_result and encode_receipt(receipt)==before_receipt
assert verify_receipt_content(receipt,config,(('trades',batch),),result)
print('Actual producer unavailable quality remains faithfully content-bound; selected later row fails diagnostic, full result/receipt unchanged.')
