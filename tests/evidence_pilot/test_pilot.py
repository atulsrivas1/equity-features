"""Independent fixed-case outcomes and hostile export controls.

Expected observations come from the reviewed pre-code data, never the producer.
No usefulness measurement or independent operator is implied.
"""
from __future__ import annotations

import hashlib
import importlib.util
import io
import json
from pathlib import Path
import shutil
import sys
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('pilot', ROOT / 'examples/evidence_pilot.py')
assert spec is not None and spec.loader is not None
pilot = importlib.util.module_from_spec(spec)
sys.modules['pilot'] = pilot
spec.loader.exec_module(pilot)
ORACLE = json.loads((ROOT / 'docs/stories/EQ116_ORACLES.json').read_bytes())


def canonical(value: object, lf: bool = True) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode() + (b'\n' if lf else b'')


def rewrite(directory: Path, name: str, raw: bytes) -> None:
    """Owner tamper control refreshes outer hash to reach deeper binding checks."""
    (directory / name).write_bytes(raw)
    complete = json.loads((directory / 'completion.json').read_bytes())
    complete['files'][name] = dict(bytes=len(raw), digest=hashlib.sha256(raw).hexdigest())
    (directory / 'completion.json').write_bytes(canonical(complete))


class PilotTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.temp = tempfile.TemporaryDirectory(prefix='eq116-tests-')
        cls.parent = Path(cls.temp.name)
        cls.export = cls.parent / 'original'
        pilot.record(cls.export)

    @classmethod
    def tearDownClass(cls) -> None:
        cls.temp.cleanup()

    def copy_case(self, case_id: str = 'P01') -> Path:
        target = self.parent / self.id().split('.')[-1]
        shutil.copytree(self.export / case_id, target)
        return target

    def test_all_sixteen_compute_observations_equal_full_independent_literals(self) -> None:
        got = pilot.replay(self.export, 'wheel-compute')
        self.assertEqual(canonical(got), canonical([x for x in ORACLE['reader_expectations'] if x['form'] == 'wheel-compute']))
        self.assertEqual(sum(x['calculator_calls'] for x in got), 12)

    def test_full_strict_findings_bind_every_original_row_and_batch(self) -> None:
        for case_id in ('P01', 'P02', 'P05'):
            reports = json.loads((self.export / case_id / 'reports.json').read_bytes())
            strict = reports['strict'];future = case_id == 'P02'
            self.assertEqual(canonical(strict), canonical(ORACLE['strict_reports']['future' if future else 'clean']))
            self.assertEqual([x['subject_id'] for x in strict['findings']], ['trades:t1', 'trades:t2', 'trades:t3'])
            self.assertEqual([x['check_id'] for x in strict['findings']], ['known-1', 'known-2', 'known-3'])
            self.assertEqual([x['content'] for x in strict['findings']], [ORACLE['strict_input_fingerprints']['future' if future else 'clean']] * 3)

    def test_canonical_column_order_roundtrip_preserves_full_literal_input(self) -> None:
        for case_id, expected in [('P01', ORACLE['clean_batch']['value']), ('P02', ORACLE['future_batch_typed_json'])]:
            with zipfile.ZipFile(self.export / case_id / 'bundle.zip') as archive:
                raw = archive.read('inputs/000.json')
            self.assertEqual(raw, canonical(expected, False))
            names = [x['fields']['name'] for x in json.loads(raw)['value']['fields']['columns']]
            self.assertEqual(names, sorted(names))
            self.assertNotEqual(names, ['instrument_id', 'session_id', 'event_ns', 'order_key', 'event_id', 'eligible', 'price', 'size', 'known_at_ns'])

    def test_eight_event_semantics_and_exact_public_reference_graph(self) -> None:
        for case_id in ('P01', 'P02', 'P08'):
            events = json.loads((self.export / case_id / 'events.json').read_bytes())
            self.assertEqual(len(events), 8)
            self.assertEqual([e['subject']['kind'] for e in events], ['request', 'model_declaration', 'tool_call',
                'tool_result', 'tool_call', 'tool_result', 'feature_read', 'decision'])
            previous = '0' * 64
            for i, event in enumerate(events, 1):
                self.assertEqual(event['sequence'], i)
                self.assertEqual(event['event_id'], case_id + ':e' + str(i))
                self.assertEqual(event['chain_id'], 'pilot:' + case_id)
                self.assertEqual(event['previous_hash'], previous)
                self.assertEqual(event['actor'], dict(actor_id='eq116-pilot', kind='software'))
                self.assertEqual(event['occurred'], dict(at_ns=None, clock_source=None, uncertainty_ns=None))
                self.assertEqual(event['recorded'], event['occurred'])
                previous = hashlib.sha256(canonical(event, False)).hexdigest()
            for child, field, parent in [(2, 'request', 0), (3, 'call', 2), (4, 'request', 0), (5, 'call', 4), (6, 'result', 3), (7, 'request', 0)]:
                ref = events[child]['subject'][field];target = events[parent]
                self.assertEqual(ref, dict(chain_id=target['chain_id'], sequence=target['sequence'],
                    event_id=target['event_id'], kind=target['subject']['kind'], digest=hashlib.sha256(canonical(target, False)).hexdigest()))
            self.assertEqual(events[7]['subject']['feature_reads'][0]['sequence'], 7)
            self.assertEqual(events[6]['subject']['inputs'][0]['content'], ORACLE['strict_input_fingerprints']['future' if case_id == 'P02' else 'clean'])
            self.assertEqual(events[0]['subject']['context'], dict(namespace='demo', session_id='S',
                availability=dict(market_cutoff_ns=200, knowledge_cutoff_ns=210, evaluation_ns=210, mode='known_at', reconstruction_reason=None)))
            model = events[1]['subject']
            self.assertEqual(model['identity_state'], 'not_supplied' if case_id == 'P08' else 'declared')
            self.assertEqual([model[k] for k in ('provider', 'model', 'version')], [None] * 3 if case_id == 'P08' else ['synthetic', 'fixture-model', 'v1'])

    def test_plain_facts_independently_carry_same_artifacts_and_bindings(self) -> None:
        directory = self.export / 'P01'
        plain = json.loads((directory / 'plain-log.json').read_bytes())
        with zipfile.ZipFile(directory / 'bundle.zip') as archive:
            result, receipt = archive.read('result.json'), archive.read('receipt.json')
        self.assertEqual(plain[3]['facts']['payload'].encode(), result)
        self.assertEqual(plain[6]['facts']['receipt'].encode(), receipt)
        self.assertEqual([r['sequence'] for r in plain], list(range(1, 9)))
        self.assertEqual(plain[0]['facts']['narrative'], 'session.trade.count=3')
        self.assertEqual(plain[5]['facts']['report'], ORACLE['strict_reports']['clean'])
        self.assertEqual(plain[7]['facts']['action'], 'DEFER')
        self.assertEqual(plain[7]['facts']['reason_code'], 'diagnostic_not_admitted')

    def test_future_known_all_five_nulls_keep_quality_and_original_metadata(self) -> None:
        with zipfile.ZipFile(self.export / 'P02/bundle.zip') as archive:
            result = json.loads(archive.read('result.json'))['value']['fields']
            batch = json.loads(archive.read('inputs/000.json'))['value']['fields']
        self.assertEqual([x['fields']['values'] for x in result['values']], [[None]] * 5)
        for row in result['quality']:
            self.assertEqual(row['fields']['status'], 'missing_input')
            self.assertEqual(row['fields']['reasons'], ['future_knowledge'])
            self.assertEqual(row['fields']['expected'], 3)
            self.assertEqual(row['fields']['observed'], 3)
        self.assertEqual(next(x['fields']['values'] for x in batch['columns'] if x['fields']['name'] == 'known_at_ns'), [110, 130, 211])
        self.assertEqual(result['metadata']['fields']['backend_id'], 'python-exact')

    def test_prefix_preserves_original_terminal_for_both_arms(self) -> None:
        directory = self.export / 'P06'
        terminals = json.loads((directory / 'terminals.json').read_bytes())
        self.assertEqual(terminals['expected_count'], 8)
        self.assertEqual(terminals['ledger']['sequence'], 8)
        self.assertEqual(terminals['ordinary_log']['record_count'], 8)
        for name in ('plain-log.json', 'events.json'):
            self.assertEqual(len(json.loads((directory / name).read_bytes())), 7)
        for arm in ('ordinary_log', 'evidence_ledger'):
            observation = pilot.read_case(directory, 'P06', arm, 'wheel-compute')
            self.assertEqual(observation['anchor'], 'not_covered')
            self.assertEqual(observation['consistency'], 'verified')

    def test_missing_input_is_reference_not_synthesized_for_replay(self) -> None:
        with zipfile.ZipFile(self.export / 'P05/bundle.zip') as archive:
            self.assertNotIn('inputs/000.json', archive.namelist())
            manifest = json.loads(archive.read('manifest.json'))
        self.assertEqual(manifest['inputs'][0]['storage'], 'reference')
        self.assertIsNone(manifest['inputs'][0]['entry'])
        for arm in ('ordinary_log', 'evidence_ledger'):
            observation = pilot.read_case(self.export / 'P05', 'P05', arm, 'wheel-compute')
            self.assertEqual((observation['replay_status'], observation['calculator_calls']), ('unavailable', 0))

    def test_corrupt_bundle_refuses_before_either_arm_calculator(self) -> None:
        for arm in ('ordinary_log', 'evidence_ledger'):
            observation = pilot.read_case(self.export / 'P07', 'P07', arm, 'wheel-compute')
            self.assertEqual(observation['load'], 'integrity_mismatch')
            self.assertEqual(observation['calculator_calls'], 0)
            for key in ('consistency', 'anchor', 'retention', 'narrative_status', 'decision', 'model_state', 'strict_admission'):
                self.assertIsNone(observation[key])

    def test_existing_output_refused_without_altering_complete_exports(self) -> None:
        before = (self.export / 'P01/completion.json').read_bytes()
        with self.assertRaises(pilot.PilotError) as caught:pilot.record(self.export)
        self.assertEqual(caught.exception.code, 'existing_output')
        self.assertEqual((self.export / 'P01/completion.json').read_bytes(), before)

    def test_wrong_row_binding_cannot_pass_status_only(self) -> None:
        directory = self.copy_case()
        reports = json.loads((directory / 'reports.json').read_bytes())
        reports['strict']['findings'][0]['subject_id'] = 'trades:t2'
        rewrite(directory, 'reports.json', canonical(reports))
        with self.assertRaises(pilot.PilotError):pilot.read_case(directory, 'P01', 'ordinary_log', 'wheel-compute')

    def test_bool_count_is_not_integer_parity(self) -> None:
        directory = self.copy_case()
        reports = json.loads((directory / 'reports.json').read_bytes())
        reports['strict']['findings'][0]['unknown_prerequisites'] = False
        rewrite(directory, 'reports.json', canonical(reports))
        with self.assertRaises(pilot.PilotError):pilot.read_case(directory, 'P01', 'evidence_ledger', 'wheel-compute')

    def test_extra_report_field_refused_despite_correct_outer_hash(self) -> None:
        directory = self.copy_case()
        reports = json.loads((directory / 'reports.json').read_bytes());reports['extra'] = 1
        rewrite(directory, 'reports.json', canonical(reports))
        with self.assertRaises(pilot.PilotError):pilot.read_case(directory, 'P01', 'ordinary_log', 'wheel-compute')

    def test_missing_completion_and_renamed_file_refused(self) -> None:
        directory = self.copy_case();(directory / 'completion.json').unlink()
        with self.assertRaises(pilot.PilotError):pilot.read_case(directory, 'P01', 'ordinary_log', 'wheel-compute')

    def test_plain_log_changed_despite_recomputed_completion_refused(self) -> None:
        directory = self.copy_case();plain = json.loads((directory / 'plain-log.json').read_bytes())
        plain[0]['facts']['narrative'] = 'session.trade.count=4'
        rewrite(directory, 'plain-log.json', canonical(plain))
        with self.assertRaises(pilot.PilotError):pilot.read_case(directory, 'P01', 'ordinary_log', 'wheel-compute')

    def test_event_reference_changed_despite_recomputed_completion_refused(self) -> None:
        directory = self.copy_case();events = json.loads((directory / 'events.json').read_bytes())
        events[3]['subject']['call']['digest'] = '0' * 64
        rewrite(directory, 'events.json', canonical(events))
        with self.assertRaises((pilot.PilotError, ValueError)):pilot.read_case(directory, 'P01', 'evidence_ledger', 'wheel-compute')

    def test_duplicate_nonfinite_extra_data_and_unknown_forms_refused(self) -> None:
        for raw in (b'{"a":1,"a":1}', b'{"a":NaN}', b'{}{}', b'{"a":1.0}\n'):
            with self.assertRaises(pilot.PilotError):pilot.parsed(raw)
        with self.assertRaises(pilot.PilotError):pilot.read_case(self.export / 'P01', 'P01', 'unknown', 'wheel-compute')
        with self.assertRaises(pilot.PilotError):pilot.replay(self.export, 'unknown')

    def test_archive_duplicate_compressed_and_traversal_refused(self) -> None:
        for names, compression in [(['manifest.json', 'manifest.json'], zipfile.ZIP_STORED),
                                   (['../result.json'], zipfile.ZIP_STORED),
                                   (['manifest.json'], zipfile.ZIP_DEFLATED)]:
            stream = io.BytesIO()
            with zipfile.ZipFile(stream, 'w', compression=compression) as archive:
                for name in names:archive.writestr(name, b'{}')
            with self.assertRaises(pilot.PilotError):pilot._archive(stream.getvalue())

    def test_fixed_layout_and_literal_caps(self) -> None:
        self.assertEqual(len(pilot.FILES), 8)
        for case_id in pilot.CASE_IDS:
            directory = self.export / case_id
            self.assertEqual({x.name for x in directory.iterdir()}, set(pilot.FILES))
            self.assertLessEqual(sum((directory / name).stat().st_size for name in pilot.FILES if name != 'ledger.sqlite'), 1048576)
        directory = self.copy_case();rewrite(directory, 'reports.json', b' ' * 65537)
        with self.assertRaises(pilot.PilotError) as caught:pilot.read_case(directory, 'P01', 'ordinary_log', 'wheel-compute')
        self.assertEqual(caught.exception.code, 'limit_exceeded')


if __name__ == '__main__':unittest.main()
