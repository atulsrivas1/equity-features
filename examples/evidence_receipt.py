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
# Deliberately placeholder supplied references. No content verification is claimed in EQ096.
# EQ097 will compute the full canonical typed payload digests and replace this demonstration.
receipt = make_receipt(result,
    configuration=ContentFingerprint('configuration','0'*64,0),
    inputs=(InputFingerprint('trades','trades1',ContentFingerprint('canonical_batch','1'*64,0)),),
    output=ContentFingerprint('feature_result','2'*64,0),
    formulas=tuple(FormulaBinding(c.feature_id,c.algorithm_version) for c in result.values),
    environment=EnvironmentDeclaration('CPython','3.12','caller-declared',(
        PackageVersion('equity-feature-contracts','0.0.4a4'),PackageVersion('equity-features','0.0.4a4'))),
    execution=ExecutionClaim(), evidence=EvidenceDisclosure('not_supplied',0))
assert decode_receipt(encode_receipt(receipt)) == receipt
assert len(receipt_digest(receipt)) == 64
assert result == before
values = {c.feature_id:c.values[0] for c in result.values}
assert values['session.trade.count'] == 3 and values['session.trade.volume'] == 10
assert values['session.trade.notional'] == 1011 and values['session.trade.vwap'] == 101.1
print('Receipt structure, actual synthetic producer parity, unknown execution and supplied-only fingerprint claims verified.')
