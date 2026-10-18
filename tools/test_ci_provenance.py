"""Synthetic immutable Git fixtures; no package imports, network or installs."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import ci_provenance
import ci_scope

WORKFLOWS = ('qualification', 'docs', 'agent-evidence', 'agent-ledger', 'conformance', 'continuous',
             'diagnostics', 'evidence', 'evidence-evaluation', 'evidence-pilot', 'explanations',
             'packages', 'provenance', 'quickstart', 'r9', 'r10', 'research', 'transport')


class ProvenanceTests(unittest.TestCase):
    def setUp(self):
        self.owner = tempfile.TemporaryDirectory(prefix='ci-policy-fixture-')
        self.addCleanup(self.owner.cleanup)
        self.root = Path(self.owner.name)/'repo'; self.root.mkdir()
        self.git('init', '-q')
        for name, value in [('user.name', 'CI synthetic fixture'), ('user.email', 'fixture@example.invalid'),
                            ('commit.gpgsign', 'false'), ('core.autocrlf', 'false'),
                            ('core.hooksPath', str(Path(self.owner.name)/'no-hooks'))]:
            self.git('config', name, value)
        tools = self.root/'tools'; tools.mkdir()
        for name in ('ci_scope.py', 'ci_gate.py', 'ci_provenance.py'):
            (tools/name).write_bytes(Path(__file__).with_name(name).read_bytes())
        workflows = self.root/'.github/workflows'; workflows.mkdir(parents=True)
        for name in WORKFLOWS: (workflows/(name+'.yml')).write_bytes(b'name: synthetic fixture\n')
        (self.root/'binary.dat').write_bytes(b'\x00\xff\nfixture\n')
        (self.root/'same.dat').write_bytes(b'\x00\xff\nfixture\n')
        self.git('add', '--all'); self.git('commit', '-qm', 'synthetic initial')
        self.head = self.git('rev-parse', 'HEAD').decode().strip()

    def git(self, *args, data=None):
        result = subprocess.run(['git', *args], cwd=self.root, input=data, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE, check=False)
        self.assertEqual(result.returncode, 0, result.stderr.decode(errors='replace'))
        return result.stdout

    def commit(self):
        self.git('add', '--all'); self.git('commit', '-qm', 'synthetic change')
        self.head = self.git('rev-parse', 'HEAD').decode().strip()

    def context(self):
        return dict(GITHUB_REPOSITORY='atulsrivas1/equity-features', GITHUB_EVENT_NAME='push',
                    GITHUB_SHA=self.head, GITHUB_REF='refs/heads/fixture', GITHUB_RUN_ID='1234',
                    GITHUB_RUN_ATTEMPT='1', GITHUB_WORKFLOW_SHA=self.head,
                    GITHUB_WORKFLOW_REF='atulsrivas1/equity-features/.github/workflows/qualification.yml@refs/heads/fixture')

    def invoke(self, change=None, needs_change=None):
        event = dict(repository={'full_name':'atulsrivas1/equity-features'}, before='0'*40,
                     after=self.head, ref='refs/heads/fixture', deleted=False)
        context = self.context()
        expected = ci_scope.classify(self.root, event, context)
        self.assertIs(expected['valid'], True); self.assertEqual(expected['reason'], 'INITIAL_PUSH')
        logical = {name: {'result':'success', 'outputs':{}} for name in ('scope', 'docs', *WORKFLOWS[2:])}
        logical['scope']['outputs']['record'] = json.dumps(expected)
        if needs_change: needs_change(logical)
        path = Path(self.owner.name)/'event.json'; path.write_text(json.dumps(event), encoding='utf-8')
        context.update(GITHUB_EVENT_PATH=str(path), CI_NEEDS=json.dumps(logical))
        if change: context.update(change)
        env = dict(os.environ); env.update(context)
        done = subprocess.run([sys.executable, str(self.root/'tools/ci_provenance.py')], cwd=self.root,
                              env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        target = self.root/'dist/ci/policy/qualification.json'
        return done, json.loads(target.read_bytes())

    def test_complete_inventory_and_exact_hashes(self):
        got = ci_provenance.inventory(self.root, self.head)
        expected = {'.github/workflows/'+n+'.yml' for n in WORKFLOWS} | {'tools/'+n for n in ('ci_scope.py', 'ci_gate.py', 'ci_provenance.py')} | {'binary.dat', 'same.dat'}
        self.assertEqual(set(got), expected)
        for name, item in got.items():
            data = (self.root/name).read_bytes()
            self.assertEqual(set(item), {'git_oid','kind','mode','bytes','sha256'})
            self.assertEqual(item, {'git_oid':hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest(),
                                    'kind':'blob','mode':'100644','bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        self.assertEqual(got['binary.dat'], got['same.dat'])

    def test_cli_closed_success_and_canonical_digest(self):
        done, value = self.invoke()
        self.assertEqual((done.returncode, done.stdout, done.stderr), (0, b'', b''))
        self.assertEqual(set(value), {'schema','stage','repository','event','run_id','run_attempt','ref',
                                     'checkout_head','checkout_tree','workflow_ref','workflow_sha','classification',
                                     'logical_results','source_map_sha256','declared_external_boundaries','gate_qualified','source_map'})
        self.assertEqual(value['schema'], 'equity-features.ci-policy.v1')
        self.assertEqual(value['stage'], 'GATE_EVALUATED_NOT_FINAL_RUN_ACCEPTANCE')
        self.assertIs(value['gate_qualified'], True)
        self.assertEqual(value['checkout_head'], self.head)
        self.assertEqual(value['run_id'], 1234); self.assertEqual(value['run_attempt'], 1)
        preimage = json.dumps(value['source_map'], ensure_ascii=True, sort_keys=True, separators=(',', ':')).encode()
        self.assertEqual(value['source_map_sha256'], hashlib.sha256(preimage).hexdigest())
        self.assertEqual(set(value['logical_results'].values()), {'success'})
        raw = (self.root/'dist/ci/policy/qualification.json').read_bytes()
        self.assertTrue(raw.endswith(b'\n')); self.assertNotIn(b'\r\n', raw)

    def test_untracked_outputs_do_not_change_inventory(self):
        before = ci_provenance.inventory(self.root, self.head)
        (self.root/'untracked.txt').write_bytes(b'not committed')
        self.assertEqual(before, ci_provenance.inventory(self.root, self.head))

    def test_working_executed_tool_drift_rejected(self):
        path = self.root/'tools/ci_gate.py'; path.write_bytes(path.read_bytes()+b'\n# uncommitted drift\n')
        done, value = self.invoke()
        self.assertEqual(done.returncode, 1); self.assertIs(value['gate_qualified'], False)
        self.assertEqual(value['schema'], 'equity-features.ci-policy-error.v1')

    def test_different_workflow_commit_with_identical_definitions_is_supported(self):
        prior = self.head
        (self.root/'new.txt').write_bytes(b'new committed payload'); self.commit()
        done, value = self.invoke({'GITHUB_WORKFLOW_SHA':prior})
        self.assertEqual(done.returncode, 0)
        self.assertEqual(value['workflow_sha'], prior)
        self.assertEqual(value['checkout_head'], self.head)

    def test_workflow_definition_drift_rejected(self):
        prior = self.head
        (self.root/'.github/workflows/qualification.yml').write_bytes(b'name: changed definition\n'); self.commit()
        done, value = self.invoke({'GITHUB_WORKFLOW_SHA':prior})
        self.assertEqual(done.returncode, 1); self.assertIs(value['gate_qualified'], False)

    def test_unknown_workflow_rejected(self):
        (self.root/'.github/workflows/unreviewed.yml').write_bytes(b'name: extra\n'); self.commit()
        done, value = self.invoke()
        self.assertEqual(done.returncode, 1); self.assertIs(value['gate_qualified'], False)

    def test_symlink_and_gitlink_modes_reject_without_materializing_them(self):
        blob = self.git('hash-object', '-w', '--stdin', data=b'target').decode().strip()
        self.git('update-index', '--add', '--cacheinfo', '120000,'+blob+',link')
        self.git('commit', '-qm', 'synthetic link index')
        head = self.git('rev-parse', 'HEAD').decode().strip()
        with self.assertRaises(ValueError): ci_provenance.inventory(self.root, head)
        self.git('update-index', '--force-remove', 'link')
        self.git('update-index', '--add', '--cacheinfo', '160000,'+head+',submodule')
        self.git('commit', '-qm', 'synthetic gitlink index')
        head = self.git('rev-parse', 'HEAD').decode().strip()
        with self.assertRaises(ValueError): ci_provenance.inventory(self.root, head)

    def test_invalid_utf8_tree_path_rejected(self):
        blob = self.git('hash-object', '-w', '--stdin', data=b'fixture').decode().strip()
        tree = self.git('mktree', '-z', data=b'100644 blob '+blob.encode()+b'\tbad\xff\0').decode().strip()
        head = self.git('commit-tree', tree, '-p', self.head, data=b'synthetic nonUTF8 tree\n').decode().strip()
        with self.assertRaises(UnicodeError): ci_provenance.inventory(self.root, head)

    def test_malformed_batch_stream_cannot_qualify(self):
        original = subprocess.run
        def damaged(args, **kwargs):
            result = original(args, **kwargs)
            if args[-2:] == ['cat-file', '--batch']:
                result.stdout += b'extra trailing bytes'
            return result
        with patch('ci_provenance.subprocess.run', side_effect=damaged):
            with self.assertRaises(ValueError): ci_provenance.inventory(self.root, self.head)

    def test_error_schema_for_invalid_context_and_failed_dependency(self):
        done, value = self.invoke({'GITHUB_RUN_ID':'0','GITHUB_RUN_ATTEMPT':'true'},
                                  lambda x: x['docs'].update(result='failure'))
        self.assertEqual(done.returncode, 1)
        self.assertEqual(value, {'schema':'equity-features.ci-policy-error.v1','gate_qualified':False,
                                 'reason':'QUALIFICATION_REJECTED','run_id':None,'run_attempt':None})

    def test_stale_output_is_not_overwritten_or_qualified(self):
        done, _ = self.invoke(); self.assertEqual(done.returncode, 0)
        target = self.root/'dist/ci/policy/qualification.json'; raw = target.read_bytes()
        done, _ = self.invoke(); self.assertEqual(done.returncode, 1)
        self.assertEqual(target.read_bytes(), raw)


if __name__ == '__main__': unittest.main(verbosity=2)
