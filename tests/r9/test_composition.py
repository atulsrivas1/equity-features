"""Independent pre-code R9 state/math expectations against installed APIs."""
import base64
from dataclasses import replace
import importlib.util
import io
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
import zipfile
from equity_feature_bundles import BundleError, read_bundle, write_bundle
from equity_feature_bundles import replay
from equity_feature_evidence import canonical_content, make_content_receipt, ExecutionClaim, EvidenceDisclosure
from equity_feature_explanations import explain_result, encode_explanation

ROOT = Path(__file__).resolve().parents[2]
EXPECT = json.loads((ROOT / 'docs/stories/EQ-100_EXPECTATIONS.json').read_bytes())
ORACLE = json.loads((ROOT / 'io/tests/fixtures/bundle_oracle.json').read_bytes())
RAW = base64.b64decode(ORACLE['archive_base64'])
HAS_FEATURES = importlib.util.find_spec('equity_features') is not None
spec = importlib.util.spec_from_file_location('trusted_r9_example', ROOT / 'examples/r9_reproduction.py')
example = importlib.util.module_from_spec(spec)
spec.loader.exec_module(example)


def repack(entries):
    output = io.BytesIO()
    with zipfile.ZipFile(output, 'w') as archive:
        for name in sorted(entries):
            info = zipfile.ZipInfo(name, (1980, 1, 1, 0, 0, 0))
            info.create_system = 3; info.create_version = info.extract_version = 20
            info.external_attr = 0o100600 << 16
            archive.writestr(info, entries[name])
    return output.getvalue()


class CompositionTests(unittest.TestCase):
    def setUp(self):
        self.bundle = read_bundle(RAW)

    def check_report(self, report, status):
        expected = EXPECT['replay_reports'][status]
        for name in ('status','execution_state','content_state','compatibility_state','calculation_count','result_match','declared_environment_verified'):
            self.assertEqual(getattr(report, name), expected[name])
        self.assertEqual(report.replayed_output is not None, expected['replayed_output_present'])
        if status == 'matched': self.assertTrue(type(report.elapsed_ns) is int and 0 <= report.elapsed_ns <= 5000000000)
        else: self.assertIsNone(report.elapsed_ns)

    def test_independent_bundle_and_explanation(self):
        bundle = self.bundle
        self.assertEqual(tuple(c.values[0] for c in bundle.result.values), tuple(EXPECT['normal']['values']))
        entity = bundle.manifest.entity
        inputs = tuple((x.role, x.batch) for x in bundle.inputs if x.batch is not None)
        summary = explain_result(bundle.result, bundle.receipt, bundle.configuration, entity=entity,
            feature_id='session.trade.count', inputs=inputs)
        self.assertTrue(summary.inputs[0].content_verified)
        self.assertEqual([x.code for x in summary.findings], EXPECT['normal']['findings'])
        self.assertFalse(summary.execution_verified); self.assertFalse(summary.source_authenticated)
        wire = json.loads(encode_explanation(summary))
        self.assertEqual((wire["quality"]["expected"],wire["quality"]["observed"]),(3,3))
        self.assertFalse(wire["source_authenticated"]);self.assertFalse(wire["execution_verified"])

    def test_optional_import_and_actual_replay_state(self):
        if not HAS_FEATURES: self.assertNotIn('equity_features', sys.modules)
        report = replay.replay_bundle(self.bundle)
        self.check_report(report, 'matched' if HAS_FEATURES else 'incompatible')

    def test_reference_missing_and_explicit_resolution(self):
        b = self.bundle
        reference = read_bundle(write_bundle(b.receipt, b.configuration, b.result, (), b.manifest.publication))
        self.check_report(replay.replay_bundle(reference), 'unavailable')
        s = explain_result(reference.result, reference.receipt, reference.configuration,
            entity=reference.manifest.entity, feature_id='session.trade.count')
        self.assertEqual([x.code for x in s.findings], EXPECT['reference_explanation_findings'])
        inputs = tuple((x.role, x.batch) for x in b.inputs if x.batch is not None)
        self.check_report(replay.replay_bundle(reference, inputs), 'matched' if HAS_FEATURES else 'incompatible')

    def test_cancellation_zero_loader_calls(self):
        with patch.object(replay, '_installed_calculator', side_effect=AssertionError('must not load')) as loader:
            self.check_report(replay.replay_bundle(self.bundle, cancel_before_start=True), 'cancelled_before_start')
        self.assertEqual(loader.call_count, 0)

    def test_result_payload_crc_refusal(self):
        with zipfile.ZipFile(io.BytesIO(RAW)) as archive:
            info = archive.getinfo('result.json')
            start = info.header_offset + 30 + len(info.filename.encode('ascii')) + len(info.extra)
        damaged = bytearray(RAW); damaged[start] ^= 1
        with patch.object(replay, '_installed_calculator', side_effect=AssertionError('must not load')) as loader:
            with self.assertRaises(BundleError) as caught: read_bundle(bytes(damaged))
        self.assertEqual(caught.exception.code, EXPECT['refusals']['result_payload_crc']); self.assertEqual(loader.call_count, 0)

    def test_manifest_registry_and_version_refusal(self):
        with zipfile.ZipFile(io.BytesIO(RAW)) as archive: entries = {n:archive.read(n) for n in archive.namelist()}
        self.assertEqual(repack(entries), RAW)
        for key in ('manifest_registry','manifest_features_version'):
            changed = dict(entries); manifest = json.loads(changed['manifest.json'])
            if key == 'manifest_registry': manifest['registry'] = 'os.system'
            else: manifest['versions']['features'] = '9'
            changed['manifest.json'] = json.dumps(manifest, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')
            with patch.object(replay, '_installed_calculator', side_effect=AssertionError('must not load')) as loader:
                with self.assertRaises(BundleError) as caught: read_bundle(repack(changed))
            self.assertEqual(caught.exception.code, EXPECT['refusals'][key]); self.assertEqual(loader.call_count, 0)

    def test_changed_reference_content_zero_loader_calls(self):
        b = self.bundle; original = b.inputs[0].batch
        altered = replace(original, columns=tuple(replace(c, values=(2,3,6)) if c.name == 'size' else c for c in original.columns))
        reference = read_bundle(write_bundle(b.receipt, b.configuration, b.result, (), b.manifest.publication))
        with patch.object(replay, '_installed_calculator', side_effect=AssertionError('must not load')) as loader:
            with self.assertRaises(BundleError) as caught: replay.replay_bundle(reference, (('trades', altered),))
        self.assertEqual(caught.exception.code, EXPECT['refusals']['caller_changed_size_same_metadata']); self.assertEqual(loader.call_count, 0)

    @unittest.skipUnless(HAS_FEATURES, 'optional actual calculator absent in light form')
    def test_actual_public_example(self):
        example.demonstrate()

    @unittest.skipUnless(HAS_FEATURES, 'optional actual calculator absent in light form')
    def test_future_knowledge_matches_unavailable_not_safety(self):
        from equity_features.session import compute_trades
        config, batch = example.sample(future=True)
        result = compute_trades(batch, config, entity=example.ENTITY)
        expected = EXPECT['future_knowledge']
        self.assertEqual([c.values[0] for c in result.values], expected['values'])
        for q in result.quality:
            self.assertEqual(q.status.value, expected['status']); self.assertEqual([r.value for r in q.reasons], expected['reasons'])
            self.assertEqual((q.expected,q.observed),(expected['expected'],expected['observed']))
        receipt = make_content_receipt(result, config, (('trades',batch),), example.ENVIRONMENT, ExecutionClaim(), EvidenceDisclosure('not_supplied',0))
        bundle = read_bundle(write_bundle(receipt, config, result, (('trades',batch),), example.PUBLICATION))
        self.check_report(replay.replay_bundle(bundle),'matched')
        summary = explain_result(bundle.result,bundle.receipt,bundle.configuration,entity=example.ENTITY,feature_id='session.trade.count',inputs=(('trades',batch),))
        self.assertEqual([f.code for f in summary.findings],expected['findings']);self.assertTrue(summary.inputs[0].content_verified)
        self.assertEqual(canonical_content(bundle.result),canonical_content(result))

    @unittest.skipUnless(HAS_FEATURES, 'optional actual calculator absent in light form')
    def test_missing_batch_result_can_reproduce(self):
        from equity_features.session import compute_trades
        config,_ = example.sample(); result=compute_trades(None,config,entity=example.ENTITY); expected=EXPECT['missing_batch']
        self.assertEqual([c.values[0] for c in result.values],expected['values'])
        for q in result.quality:
            self.assertEqual(q.status.value,expected['status']);self.assertEqual([r.value for r in q.reasons],expected['reasons'])
            self.assertEqual((q.expected,q.observed),(expected['expected'],expected['observed']))
        receipt=make_content_receipt(result,config,(),example.ENVIRONMENT,ExecutionClaim(),EvidenceDisclosure('not_supplied',0))
        self.check_report(replay.replay_bundle(read_bundle(write_bundle(receipt,config,result,(),example.PUBLICATION))),'matched')


if __name__ == '__main__': unittest.main()
