"""Independent dependency truth tables and immutable leaf-equivalence fixtures."""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import re
import unittest

import ci_gate

PACKAGES = ('agent-evidence', 'agent-ledger', 'conformance', 'continuous', 'diagnostics',
            'evidence', 'evidence-evaluation', 'evidence-pilot', 'explanations', 'packages',
            'provenance', 'quickstart', 'r9', 'r10', 'research', 'transport')
ROOTS = ('scope', 'docs', *PACKAGES)

# EQ136 adds one exact mathematical-reference operation. Remove only this
# literal step for the historical CI002 equivalence comparison; retain the
# immutable baseline hash and every original operation/routing check.
INTRADAY_DOC_TEST = '''      - name: Verify original intraday mathematics references
        run: python tools/verify_intraday_examples.py

'''


# EQ137 admits exactly one reviewed additive block after foundation upload.
# Historical hashes remain unchanged; arbitrary altered suffixes stay visible.
INTRADAY_PACKAGE_BLOCK = '      - name: Install intraday preparation package\n        run: python -m pip install --no-deps --no-build-isolation -e packages/intraday\n      - run: python -m pip check\n      - run: python -B tools/check_intraday_boundary.py\n      - run: python -B -m mypy --strict packages/intraday/src\n      - run: python -I -B -m unittest discover -s tests/intraday\n      - run: python -B tools/build_intraday.py\n      - name: Retain verified experimental intraday artifacts\n        uses: actions/upload-artifact@v4\n        with:\n          name: intraday-${{ github.sha }}-${{ matrix.os }}-attempt-${{ github.run_attempt }}\n          path: dist/intraday/\n          retention-days: 30\n          if-no-files-found: error\n'


def normalize_intraday_package_block(text: str) -> str:
    if text.count(INTRADAY_PACKAGE_BLOCK) != 1 or not text.endswith(INTRADAY_PACKAGE_BLOCK):
        raise ValueError('exact single final intraday package block required')
    return text[:-len(INTRADAY_PACKAGE_BLOCK)]


def record(docs: bool = False) -> dict:
    return dict(schema='equity-features.ci-scope.v1', valid=True, decision='DOCS' if docs else 'FULL',
                reason='READERS_ONLY' if docs else 'NON_READER_CHANGE', repository='atulsrivas1/equity-features',
                event='push', base='1'*40, source_head='2'*40, checkout_head='2'*40,
                checkout_tree='3'*40, diff_sha256='4'*64,
                allowlist_sha256='fe8860b35869529b4cabdf940905d7bc3979974e031dd041a228d8eb0b3cf2ee', changes_count=1)


def needs(value: dict) -> dict:
    result = {name: {'result': 'skipped' if value['decision'] == 'DOCS' and name in PACKAGES else 'success',
                     'outputs': {}} for name in ROOTS}
    result['scope']['outputs']['record'] = json.dumps(value)
    return result


class GateTests(unittest.TestCase):
    def test_full_and_docs_keep_original_results(self):
        for docs in (False, True):
            expected = record(docs)
            got = ci_gate.validate(needs(expected), expected)
            self.assertEqual(set(got), set(ROOTS))
            self.assertEqual(got['scope'], 'success')
            self.assertEqual(got['docs'], 'success')
            self.assertEqual({got[n] for n in PACKAGES}, {'skipped' if docs else 'success'})

    def test_every_root_non_success_and_unexpected_execution(self):
        for docs in (False, True):
            expected = record(docs)
            for name in ROOTS:
                wanted = 'skipped' if docs and name in PACKAGES else 'success'
                for result in {'success', 'failure', 'cancelled', 'skipped', 'unknown'} - {wanted}:
                    with self.subTest(docs=docs, name=name, result=result):
                        value = needs(expected); value[name]['result'] = result
                        with self.assertRaises(ValueError): ci_gate.validate(value, expected)

    def test_missing_or_extra_root(self):
        expected = record()
        for name in ROOTS:
            value = needs(expected); del value[name]
            with self.assertRaises(ValueError): ci_gate.validate(value, expected)
        value = needs(expected); value['new-unreviewed-root'] = {'result': 'success', 'outputs': {}}
        with self.assertRaises(ValueError): ci_gate.validate(value, expected)

    def test_nested_closed_types_and_outputs(self):
        expected = record()
        for name in ROOTS:
            for replacement in (None, [], {'result': True, 'outputs': {}}, {'result': 'success'},
                                {'result': 'success', 'outputs': {}, 'extra': 'success'}):
                value = needs(expected); value[name] = replacement
                with self.assertRaises(ValueError): ci_gate.validate(value, expected)
            value = needs(expected); value[name]['outputs']['unreviewed'] = 'success'
            with self.assertRaises(ValueError): ci_gate.validate(value, expected)

    def test_actual_record_must_equal_recomputed_identity(self):
        expected = record()
        for key in expected:
            changed = copy.deepcopy(expected)
            changed[key] = 'wrong'
            value = needs(changed)
            with self.assertRaises(ValueError): ci_gate.validate(value, expected)

    def test_closed_classification_and_invalid_fallback(self):
        for key in record():
            expected = record(); del expected[key]
            with self.assertRaises(ValueError): ci_gate.validate(needs(expected) if key != 'decision' else {}, expected)
        expected = record(); expected['extra'] = 1
        with self.assertRaises(ValueError): ci_gate.validate(needs(expected), expected)
        expected = record(); expected.update(valid=False, reason='SOURCE_INVALID')
        with self.assertRaises(ValueError): ci_gate.validate(needs(expected), expected)

    def test_boolean_or_float_is_not_count(self):
        for count in (True, False, 1.0, None, -1):
            expected = record(); expected['changes_count'] = count
            with self.assertRaises(ValueError): ci_gate.validate(needs(expected), expected)

    def test_initial_push_and_empty_diff_remain_full(self):
        initial = record(); initial.update(reason='INITIAL_PUSH', base=None, diff_sha256=None, changes_count=None)
        self.assertEqual(ci_gate.validate(needs(initial), initial)['packages'], 'success')
        empty = record(); empty.update(reason='EMPTY_DIFF', changes_count=0)
        self.assertEqual(ci_gate.validate(needs(empty), empty)['packages'], 'success')
        for changed in (dict(initial, event='pull_request'), dict(empty, decision='DOCS'), dict(empty, changes_count=1)):
            with self.assertRaises(ValueError): ci_gate.validate(needs(changed), changed)

    def test_duplicate_json_keys_and_nonstandard_constants_reject(self):
        for raw in ('{"scope":1,"scope":2}', '{"scope":{"x":1,"x":2}}', '{"x":NaN}', '{"x":Infinity}'):
            with self.assertRaises(ValueError): ci_gate.loads(raw)
        expected = record(); value = needs(expected)
        value['scope']['outputs']['record'] = '{"valid":true,"valid":true}'
        with self.assertRaises(ValueError): ci_gate.validate(value, expected)


EXTRA_DOC_TESTS = '''      - name: Verify aggregate CI gate and preserved workflows
        run: python tools/test_ci_gate.py

      - name: Verify immutable CI policy provenance
        run: python tools/test_ci_provenance.py

'''


class WorkflowTests(unittest.TestCase):
    root = Path(__file__).resolve().parents[1]

    def test_preserved_leaf_operations_match_immutable_baseline(self):
        fixture = json.loads((self.root/'docs/stories/CI-002_WORKFLOW_EQUIVALENCE.json').read_bytes())
        self.assertEqual(fixture['baseline_commit'], '684074e43b80171e81ff4a309c0c2c4d6a75497e')
        hashes = fixture['preserved_permissions_jobs_sha256']
        self.assertEqual(set(hashes), {'.github/workflows/'+n+'.yml' for n in ('docs', *PACKAGES)})
        for path, expected in hashes.items():
            text = (self.root/path).read_text(encoding='utf-8')
            text = text[text.index('permissions:\n'):]
            if path.endswith('/docs.yml'):
                self.assertEqual(text.count(INTRADAY_DOC_TEST), 1)
                text = text.replace(INTRADAY_DOC_TEST, '')
                self.assertEqual(text.count(EXTRA_DOC_TESTS), 1)
                text = text.replace(EXTRA_DOC_TESTS, '')
                # Deliberate owner-requested planning allocation extension, not CI routing.
                migration = json.loads((self.root/'docs/stories/GOV-031_DOCS_GATE_EXTENSION.json').read_bytes())
                self.assertEqual(migration['schema'], 'equity-features.planning-gate-extension.v1')
                self.assertEqual(migration['planning_issue'], 464)
                self.assertEqual(len(migration['replacements']), 4)
                for change in reversed(migration['replacements']):
                    self.assertEqual(text.count(change['after']), 1)
                    text = text.replace(change['after'], change['before'])
            elif path.endswith('/evidence-evaluation.yml'):
                marker = '      - uses: actions/upload-artifact@v4\n'
                pieces = text.split(marker); self.assertEqual(len(pieces), 3)
                self.assertIn("if: always() && github.event_name == 'workflow_dispatch'", pieces[1])
                normal = pieces[1].replace("== 'workflow_dispatch'", "!= 'workflow_dispatch'")
                normal = normal.replace('${{ matrix.os }}\n', '${{ matrix.os }}-attempt-${{ github.run_attempt }}\n')
                self.assertEqual(pieces[2], normal)
                text = pieces[0]+marker+pieces[1].replace("if: always() && github.event_name == 'workflow_dispatch'", 'if: always()')
            else:
                if path.endswith('/packages.yml'):
                    text = normalize_intraday_package_block(text)
                text = text.replace('-attempt-${{ github.run_attempt }}', '')
            self.assertEqual(hashlib.sha256(text.encode()).hexdigest(), expected, path)

    def test_intraday_addition_is_exact_single_final_block(self):
        original=(self.root/'.github/workflows/packages.yml').read_text(encoding='utf-8')
        base=normalize_intraday_package_block(original)
        self.assertEqual(original,base+INTRADAY_PACKAGE_BLOCK)
        altered=(base,original+INTRADAY_PACKAGE_BLOCK,original+'# extra\n',
                 original.replace('tools/build_intraday.py','tools/skip_intraday.py'),
                 original.replace('path: dist/intraday/','path: dist/'),
                 original.replace('python -m pip check\n      - run: python -B tools/check_intraday',
                                  'python -m pip check --help\n      - run: python -B tools/check_intraday'))
        for value in altered:
            with self.subTest(value=value[-100:]),self.assertRaises(ValueError):
                normalize_intraday_package_block(value)

    def test_leaf_trigger_migration_and_manual_evaluation_contract(self):
        for name in ('docs', *PACKAGES):
            text = (self.root/'.github/workflows'/f'{name}.yml').read_text(encoding='utf-8')
            trigger = text[text.index('on:\n')+4:text.index('permissions:\n')]
            if name == 'evidence-evaluation':
                self.assertEqual(trigger, '''  workflow_call:
  workflow_dispatch:
    inputs:
      study_id:
        description: Reviewed fixed study reservation ID (one attempt, no adaptive reruns)
        required: true
        type: string
''')
            else: self.assertEqual(trigger, '  workflow_call:\n')

    def test_root_has_exact_literal_calls_and_always_terminal_check(self):
        text = (self.root/'.github/workflows/qualification.yml').read_text(encoding='utf-8')
        self.assertIn('on:\n  push:\n  pull_request:\npermissions:\n  contents: read\n  actions: read\n', text)
        self.assertEqual(re.findall(r'^    uses: (.+)$', text, re.M),
                         ['./.github/workflows/'+n+'.yml' for n in ('docs', *PACKAGES)])
        terminal = text[text.index('  check:\n'):]
        self.assertTrue(terminal.startswith('  check:\n    if: always()\n'))
        keys = json.loads(re.search(r'^    needs: (\[.+\])$', terminal, re.M).group(1))
        self.assertEqual(keys, list(ROOTS))
        self.assertIn('CI_NEEDS: ${{ toJSON(needs) }}', terminal)
        self.assertNotIn('continue-on-error', text)
        self.assertNotIn('paths:', text)
        self.assertNotIn('concurrency:', text)
        self.assertEqual(text.count("if: ${{ needs.scope.result == 'success' && fromJSON(needs.scope.outputs.record).valid && fromJSON(needs.scope.outputs.record).decision == 'FULL' }}"), 16)


if __name__ == '__main__': unittest.main(verbosity=2)
