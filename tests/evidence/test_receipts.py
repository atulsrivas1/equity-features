"""Independent fixed wire oracle and contract-negative cases, no provider/data access."""
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import unittest

from equity_feature_contracts import inputs as i, results as r, specs as s
from equity_feature_evidence import (
    ContentFingerprint, InputFingerprint, FormulaBinding, PackageVersion,
    EnvironmentDeclaration, ExecutionClaim, EvidenceDisclosure, ExecutionReceipt,
    EvidenceError, encode_receipt, decode_receipt, receipt_digest, make_receipt,
)

ORACLE = Path(__file__).resolve().parents[2] / 'docs/stories/EQ-096_RECEIPT_ORACLE.json'
ORACLE_SHA = 'a59809b288709a51abe17bd2fde1109d0c041cef61a352ebd5e8b68946ea2a86'


def detached():
    # Construct expected records independently; never decode our oracle to produce inputs.
    return ExecutionReceipt(
        r.ResultMetadata('fixture', 'S', s.AvailabilitySpec(0, 0, 0), '0'*64, (), 'python', '0.0.4a4'),
        ContentFingerprint('configuration', '0'*64, 0), (),
        ContentFingerprint('feature_result', '1'*64, 0),
        (FormulaBinding('session.trade.count', 'v1'),),
        EnvironmentDeclaration('CPython', '3.12', 'fixture', (PackageVersion('equity-feature-contracts', '0.0.4a4'),)),
        ExecutionClaim(), EvidenceDisclosure('not_supplied', 0))


def with_input():
    receipt = detached()
    meta = i.BatchMetadata('fixture', i.SourceBinding('synthetic', 'snapshot', 'mapping', 'trades1'),
        i.Coverage(1, 1, True), i.PriceUnit(2, 'USD'), scope=i.InputScope(0, 10, 'fixture'),
        interval_coverage=(i.IntervalCoverage('regular', 0, 10, i.Coverage(1, 1, True)),))
    return replace(receipt, metadata=replace(receipt.metadata, inputs=(r.InputBinding('trades', i.DataKind.TRADE, meta),)),
        inputs=(InputFingerprint('trades', 'trades1', ContentFingerprint('canonical_batch', '2'*64, 123)),))


class ReceiptTests(unittest.TestCase):
    def reject(self, fn, code=None):
        with self.assertRaises(EvidenceError) as caught: fn()
        if code: self.assertEqual(caught.exception.code, code)
        return caught.exception

    def test_frozen_independent_wire_oracle(self):
        wire = ORACLE.read_bytes()
        self.assertEqual(len(wire), 1313)
        self.assertEqual(hashlib.sha256(wire).hexdigest(), ORACLE_SHA)
        self.assertEqual(encode_receipt(detached()), wire)
        self.assertEqual(receipt_digest(detached()), ORACLE_SHA)
        self.assertEqual(decode_receipt(wire), detached())

    def test_full_metadata_projection_no_dropped_fields(self):
        receipt = with_input()
        wire = encode_receipt(receipt)
        self.assertEqual(decode_receipt(wire), receipt)
        data = json.loads(wire)
        self.assertEqual(data['metadata']['inputs'][0]['metadata']['scope']['eligibility_policy'], 'fixture')
        self.assertEqual(data['metadata']['inputs'][0]['metadata']['interval_coverage'][0]['coverage'], {'expected':1,'observed':1,'complete':True})
        for change in ({'sampling':'continuous'}, {'ordering':'unsorted'}, {'duplicate_policy':'preserve'},
                       {'adjustment':i.AdjustmentSpec('split','v2','actions','anchor')}):
            metadata = replace(receipt.metadata.inputs[0].metadata, **change)
            changed = replace(receipt, metadata=replace(receipt.metadata, inputs=(replace(receipt.metadata.inputs[0],metadata=metadata),)))
            self.assertNotEqual(receipt_digest(receipt), receipt_digest(changed))

    def test_every_root_claim_changes_digest(self):
        receipt = detached()
        mutations = [replace(receipt, configuration=replace(receipt.configuration, digest='2'*64)),
            replace(receipt, output=replace(receipt.output, digest='3'*64)),
            replace(receipt, formulas=(FormulaBinding('session.trade.count', 'v2'),)),
            replace(receipt, environment=replace(receipt.environment, platform='another')),
            replace(receipt, execution=ExecutionClaim(-1, 'declared', 0)),
            replace(receipt, evidence=EvidenceDisclosure('unknown', 0)),
            replace(receipt, metadata=replace(receipt.metadata, availability=s.AvailabilitySpec(-1,-1,0))),
            replace(receipt, metadata=replace(receipt.metadata, backend_id='another')),
            replace(receipt, metadata=replace(receipt.metadata, config_digest='4'*64)),
            replace(receipt, metadata=replace(receipt.metadata, math_policy_version='v2'))]
        for changed in mutations: self.assertNotEqual(receipt_digest(receipt), receipt_digest(changed))

    def test_value_different_content_refs_not_metadata_identity(self):
        receipt = with_input()
        changed = replace(receipt, inputs=(replace(receipt.inputs[0], content=replace(receipt.inputs[0].content, digest='9'*64)),))
        self.assertEqual(receipt.metadata.identity_digest, changed.metadata.identity_digest)
        self.assertNotEqual(receipt_digest(receipt), receipt_digest(changed))

    def test_unknown_execution_separate_from_historical_cutoffs(self):
        for at in (i.I64_MIN, -1, 2**53+1, i.I64_MAX):
            receipt = replace(detached(), execution=ExecutionClaim(at, 'caller', i.I64_MAX))
            self.assertEqual(decode_receipt(encode_receipt(receipt)), receipt)
        self.reject(lambda: ExecutionClaim(None, 'clock'))
        self.reject(lambda: ExecutionClaim(None, None, 0))

    def test_boolean_never_integer(self):
        for value in (True, False, 1.0, '1'):
            self.reject(lambda: ContentFingerprint('configuration', '0'*64, value))
            self.reject(lambda: ExecutionClaim(value))
            self.reject(lambda: EvidenceDisclosure('retained_complete', 0, value))

    def test_disclosure_states_are_distinct(self):
        for state,count,total in [('retained_complete',0,0),('truncated',0,1),('not_supplied',0,None),('unknown',2,None)]:
            receipt = replace(detached(), evidence=EvidenceDisclosure(state,count,total))
            self.assertEqual(decode_receipt(encode_receipt(receipt)), receipt)
        for args in [('retained_complete',1,None),('truncated',1,1),('not_supplied',1,None),('unknown',0,0),('unverified',0,None)]:
            self.reject(lambda: EvidenceDisclosure(*args))

    def test_missing_extra_duplicate_bindings(self):
        receipt = with_input()
        self.reject(lambda: replace(receipt, inputs=()), 'inconsistent_binding')
        self.reject(lambda: replace(receipt, inputs=(replace(receipt.inputs[0],input_id='foreign'),)), 'inconsistent_binding')
        self.reject(lambda: replace(receipt, inputs=receipt.inputs*2), 'duplicate')
        self.reject(lambda: replace(receipt, formulas=receipt.formulas*2), 'duplicate')
        self.reject(lambda: replace(receipt.environment, packages=receipt.environment.packages*2), 'duplicate')

    def test_immutable_copies_and_presentation_order(self):
        items = [FormulaBinding('z','v1'),FormulaBinding('a','v2')]
        receipt = replace(detached(), formulas=items)
        items.clear()
        self.assertEqual(tuple(f.feature_id for f in receipt.formulas), ('a','z'))
        with self.assertRaises(FrozenInstanceError): receipt.schema_version='2'
        reverse = replace(receipt, formulas=tuple(reversed(receipt.formulas)))
        self.assertEqual(encode_receipt(receipt), encode_receipt(reverse))

    def test_fingerprint_domain_digest_version(self):
        for digest in ('A'*64,'0'*63,'not-a-secret-but-invalid'):
            self.reject(lambda: ContentFingerprint('configuration',digest,1))
        for kw in ({'domain':'unknown'},{'schema_version':'2'},{'canonicalization':'future'},{'algorithm':'sha1'}):
            self.reject(lambda: replace(detached().configuration, **kw))
        self.reject(lambda: replace(detached(), output=detached().configuration))

    def test_unicode_preserved_without_normalization(self):
        for name in ('é', 'e\u0301', '😀'):
            receipt = replace(detached(), environment=replace(detached().environment, platform=name))
            self.assertEqual(decode_receipt(encode_receipt(receipt)), receipt)
        self.assertNotEqual(receipt_digest(replace(detached(), execution=ExecutionClaim(0,'é'))), receipt_digest(replace(detached(), execution=ExecutionClaim(0,'e\u0301'))))
        for value in ('', ' ', 'x\0y','x\u007fy','\ud800'):
            self.reject(lambda: PackageVersion(value,'1'))

    def test_nested_label_and_interval_limits(self):
        receipt = with_input(); binding = receipt.metadata.inputs[0]
        for text in ('x'*257,'\ud800'):
            bad = replace(binding, metadata=replace(binding.metadata, namespace=text))
            # Keep namespace agreement to exercise receipt bounds, not core agreement checks.
            metadata = replace(receipt.metadata, namespace=text, inputs=(bad,))
            self.reject(lambda: replace(receipt, metadata=metadata))
        intervals = tuple(i.IntervalCoverage(str(n),0,10,i.Coverage(1,1,True)) for n in range(257))
        metadata = replace(binding.metadata, interval_coverage=intervals[:256])
        self.assertIsInstance(replace(receipt, metadata=replace(receipt.metadata, inputs=(replace(binding, metadata=metadata),))), ExecutionReceipt)
        metadata = replace(metadata, interval_coverage=intervals)
        self.reject(lambda: replace(receipt, metadata=replace(receipt.metadata, inputs=(replace(binding,metadata=metadata),))), 'limit_exceeded')

    def test_top_level_limits_before_copy(self):
        formula = FormulaBinding('a','v1')
        self.reject(lambda: replace(detached(), formulas=[formula]*257), 'limit_exceeded')
        self.reject(lambda: replace(detached().environment, packages=[PackageVersion('a','v1')]*65), 'limit_exceeded')
        self.reject(lambda: replace(detached(), inputs=[with_input().inputs[0]]*65), 'limit_exceeded')
        self.reject(lambda: replace(detached(), formulas=(f for f in (formula,))))

    def test_aggregate_nested_budgets_before_projection(self):
        receipt=with_input(); template=receipt.metadata.inputs[0]
        intervals=tuple(i.IntervalCoverage(str(n),0,10,i.Coverage(1,1,True)) for n in range(128))
        bindings=tuple(replace(template, role=str(n), metadata=replace(template.metadata,
            source=replace(template.metadata.source,input_id=str(n)),interval_coverage=intervals)) for n in range(64))
        references=tuple(InputFingerprint(str(n),str(n),ContentFingerprint('canonical_batch','0'*64,1)) for n in range(64))
        metadata=replace(receipt.metadata,inputs=bindings)
        self.reject(lambda: replace(receipt,metadata=metadata,inputs=references), 'limit_exceeded')

    def test_exact_label_and_numeric_boundaries(self):
        self.assertEqual(PackageVersion('😀'*256,'v1').name,'😀'*256)
        self.reject(lambda: PackageVersion('😀'*257,'v1'),'limit_exceeded')
        for length in (0,i.I64_MAX):
            self.assertEqual(ContentFingerprint('configuration','0'*64,length).byte_length,length)
        for length in (-1,i.I64_MAX+1):
            self.reject(lambda: ContentFingerprint('configuration','0'*64,length))

    def test_strict_json_negatives(self):
        wire = ORACLE.read_bytes()
        for bad in (wire+b'\n', b' '+wire, wire+b'{}', wire.replace(b'"byte_length":0',b'"byte_length":0.0'),
                    wire.replace(b'"byte_length":0',b'"byte_length":true'), wire.replace(b'"byte_length":0',b'"byte_length":NaN'),
                    wire.replace(b'"byte_length":0',b'"byte_length":'+b'9'*10000), b'\xef\xbb\xbf'+wire,
                    wire.replace(b'"platform":"fixture"', b'"platform":"\xff"'), wire.replace(b'"platform":"fixture"', b'"platform":"\\ud800"'),
                    wire.replace(b'"platform":"fixture"',b'"platform":"fixture","platform":"duplicate"')):
            self.reject(lambda: decode_receipt(bad))

    def test_closed_fields_and_versions(self):
        original = json.loads(ORACLE.read_bytes())
        for field in original:
            changed = dict(original); changed.pop(field)
            self.reject(lambda: decode_receipt(json.dumps(changed).encode()))
        changed = dict(original); changed['unrecognized'] = 'sensitive'
        self.reject(lambda: decode_receipt(json.dumps(changed).encode()))
        changed = dict(original); changed['schema_version']='99'
        self.reject(lambda: decode_receipt(json.dumps(changed).encode()), 'unsupported_version')

    def test_lexical_depth_nodes_and_byte_caps(self):
        self.reject(lambda: decode_receipt(b'['*17+b'0'+b']'*17), 'limit_exceeded')
        self.reject(lambda: decode_receipt(b'['+b'0,'*32768+b'0]'), 'limit_exceeded')
        self.reject(lambda: decode_receipt(b' '*(1048576+1)), 'limit_exceeded')
        # Delimiters and escaped quotes inside strings do not consume container depth.
        receipt = replace(detached(), environment=replace(detached().environment, platform='[{'*100+'"\\'))
        self.assertEqual(decode_receipt(encode_receipt(receipt)), receipt)

    def test_make_receipt_matches_actual_result_versions_and_evidence(self):
        receipt = detached(); entity = r.EntityKey('A','S')
        result = r.FeatureResult((r.FeatureColumn('session.trade.count','v1',r.ValueType.INT64,'trades',(entity,),(1,)),),
            (r.QualityRow(entity,'session.trade.count',r.Status.AVAILABLE,1,1),), receipt.metadata)
        kwargs = dict(configuration=receipt.configuration,inputs=(),output=receipt.output,formulas=receipt.formulas,
            environment=receipt.environment,execution=receipt.execution,evidence=receipt.evidence)
        self.assertEqual(make_receipt(result,**kwargs), receipt)
        self.reject(lambda: make_receipt(result,**dict(kwargs, formulas=(FormulaBinding('session.trade.count','v2'),))), 'inconsistent_binding')
        self.reject(lambda: make_receipt(result,**dict(kwargs, evidence=EvidenceDisclosure('unknown',1))), 'inconsistent_binding')

    def test_payload_free_errors(self):
        wire = ORACLE.read_bytes().replace(b'"domain":"configuration"', b'"domain":"PRIVATE_SENTINEL"')
        error = self.reject(lambda: decode_receipt(wire))
        self.assertNotIn('PRIVATE_SENTINEL', str(error))
        self.assertEqual(EvidenceError('PRIVATE_SENTINEL').code, 'invalid_schema')


if __name__ == '__main__': unittest.main()
