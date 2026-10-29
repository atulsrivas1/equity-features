"""Preserve frozen measurement evidence and report partial failed repetitions."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import benchmark_intraday_bands as benchmark


class BenchmarkGuardTests(unittest.TestCase):
    def test_committed_band_measurement_retains_all_profiles_and_original_bytes(self):
        # The committed measurement is immutable evidence of one run at the recorded commit. Its source identity is checked against that
        # commit's Git blobs, never against the current tree (the tree legitimately moves on). The EQ-139 record of the original Windows run
        # (docs/stories/EQ-139_BAND_BENCHMARK.json) is retained as history; this record is the fresh measurement after the EF5 layers.
        root=benchmark.ROOT/'docs/stories'
        report=(root/'EQ-139_BAND_BENCHMARK_20261029.json').read_bytes()
        baseline=(root/'EQ-139_BAND_BENCHMARK_20261029.baseline.json').read_bytes()
        self.assertEqual(hashlib.sha256(report).hexdigest(),'3a46c6269fa6ee3ba1a919e7a3e192a84c86330f14478e8bd0f9cb2840f13c1b')
        digest=hashlib.sha256(baseline).hexdigest()
        self.assertEqual(digest,'6cdca5c9956aca42b4a20db4591c9fce179377a0990dcf301eecf58f6995737b')
        value=json.loads(report);frozen=json.loads(baseline)
        head=value['source_commit']
        self.assertEqual(head,value['source_identity']['head'])
        self.assertEqual(value['status'],'completed')
        self.assertEqual(value['frozen_baseline_sha256'],digest)
        self.assertEqual(value['baseline'],frozen['baseline'])
        self.assertEqual(value['thresholds'],frozen['thresholds'])
        self.assertEqual(frozen['candidate'],{})
        self.assertEqual(frozen['decisions'],{})
        self.assertEqual(set(value['baseline']),set(value['candidate']))
        self.assertEqual(set(value['decisions']),set(value['cases']))
        self.assertEqual(len(value['cases']),36)
        samples=[]
        for side in ('baseline','candidate'):
            for item in value[side].values():
                self.assertEqual(item['status'],'completed')
                self.assertEqual(item['source_identity'],value['source_identity'])
                self.assertEqual(item['warmups'],2)
                self.assertEqual(len(item['samples']),7)
                samples.extend(item['samples'])
        self.assertEqual(len(samples),504)
        # Adoption is a measured, hardware-dependent outcome recorded in the file; the guard pins its presence, not its value.
        self.assertTrue(all(isinstance(v['adopt_shared_for_case'],bool) for v in value['decisions'].values()))
        self.assertTrue(all(v['conditions']['full_projection_parity'] for v in value['decisions'].values()))
        ancestor=subprocess.run(['git','merge-base','--is-ancestor',head,'HEAD'],cwd=benchmark.ROOT)
        self.assertEqual(ancestor.returncode,0,'recorded measurement commit must be an ancestor of the checkout')
        self.assertEqual(len(value['source_identity']['source']),58)
        for name,identity in value['source_identity']['source'].items():
            blob=subprocess.check_output(['git','show',head+':'+name],cwd=benchmark.ROOT)
            self.assertEqual(hashlib.sha256(blob).hexdigest(),identity['git_sha256'])

    def test_existing_report_or_baseline_is_never_overwritten(self):
        for existing in ('result.json','result.baseline.json'):
            with tempfile.TemporaryDirectory() as temporary:
                root=Path(temporary);protected=root/existing;protected.write_bytes(b'original evidence')
                process=subprocess.run([sys.executable,'-I','-B',benchmark.__file__,'--output',str(root/'result.json')],stdout=subprocess.PIPE,stderr=subprocess.PIPE)
                self.assertNotEqual(process.returncode,0)
                self.assertEqual(protected.read_bytes(),b'original evidence')
                self.assertEqual({p.name for p in root.iterdir()},{existing})

    def test_failed_sample_keeps_prior_measured_samples(self):
        count=0
        def supplied(case):
            nonlocal count
            count+=1
            if count==4:raise RuntimeError('synthetic failure after warmups and first measured sample')
            return []
        with patch.object(benchmark,'source_identity',return_value={'test':'no source claim'}),patch.object(benchmark,'inputs',side_effect=supplied):
            result=benchmark.measure('small/all','separate')
        self.assertEqual(result['status'],'failed')
        self.assertEqual(result['failed_repeat'],3)
        self.assertEqual(len(result['samples']),1)
        self.assertEqual(result['failure_type'],'RuntimeError')


    def test_failed_final_source_closure_retains_all_seven_samples(self):
        with patch.object(benchmark,'source_identity',side_effect=[{'source':'first'},{'source':'changed'}]),patch.object(benchmark,'inputs',return_value=[]):
            result=benchmark.measure('small/all','separate')
        self.assertEqual(result['status'],'failed')
        self.assertEqual(result['failed_phase'],'post-measurement closure')
        self.assertEqual(len(result['samples']),7)
        self.assertEqual(result['failure_type'],'AssertionError')

    def test_parent_source_closure_failure_retains_completed_child_samples(self):
        from types import SimpleNamespace
        identity={'source':'original'}
        sample={'wall_seconds':1,'core_seconds':1,'peak_process_bytes':10,'projection_sha256':'p'}
        completed={'status':'completed','source_identity':identity,'samples':[sample]*7,'warmups':2}
        def git(*args,**kwargs):
            return b'synthetic-head\n' if args[0][-1]=='HEAD' else b''
        with tempfile.TemporaryDirectory() as temporary:
            target=Path(temporary)/'result.json'
            with patch.object(sys,'argv',[str(benchmark.__file__),'--output',str(target)]), \
                 patch.object(benchmark.subprocess,'check_output',side_effect=git), \
                 patch.object(benchmark,'source_identity',side_effect=[identity,{'source':'changed'}]), \
                 patch.object(benchmark,'capacity',return_value={'memory_budget_bytes':1000}), \
                 patch.object(benchmark,'verify_quality_parity',return_value={'passed':True}), \
                 patch.object(benchmark,'peak_memory',return_value=10), \
                 patch.object(benchmark.subprocess,'run',return_value=SimpleNamespace(
                     returncode=0,stdout=json.dumps(completed).encode(),stderr=b'')):
                with self.assertRaises(AssertionError):benchmark.main()
            result=json.loads(target.read_bytes())
            self.assertEqual(result['status'],'failed')
            self.assertEqual(result['failure']['case'],'small/middle')
            self.assertEqual(result['failure']['mode'],'separate')
            self.assertEqual(result['failure']['failed_phase'],'parent-child source closure')
            self.assertEqual(result['failure']['samples'],completed['samples'])
            self.assertEqual(result['failure']['source_identity'],identity)
            self.assertFalse(target.with_suffix('.baseline.json').exists())


    def test_all_baselines_are_frozen_before_any_candidate(self):
        from types import SimpleNamespace
        identity={'source':'synthetic protocol test only'}
        observed=[]
        def git(*args,**kwargs):
            return b'synthetic-head\n' if args[0][-1]=='HEAD' else b''
        with tempfile.TemporaryDirectory() as temporary:
            target=Path(temporary)/'result.json'
            baseline=target.with_suffix('.baseline.json')
            def child(command,**kwargs):
                case=command[command.index('--child')+1]
                mode=command[command.index('--mode')+1]
                if mode=='separate':
                    self.assertFalse(baseline.exists())
                    self.assertFalse(any(item[1]=='shared' for item in observed))
                else:
                    self.assertEqual([c for c,m in observed if m=='separate'],list(benchmark.CASES))
                    frozen=json.loads(baseline.read_bytes())
                    self.assertEqual(set(frozen['baseline']),set(benchmark.CASES))
                    self.assertEqual(set(frozen['thresholds']),set(benchmark.CASES))
                    self.assertEqual(frozen['candidate'],{})
                    self.assertEqual(frozen['decisions'],{})
                observed.append((case,mode))
                value=1 if mode=='separate' else .5
                sample={'wall_seconds':value,'core_seconds':value,'peak_process_bytes':10,'projection_sha256':'p'}
                result={'status':'completed','source_identity':identity,'samples':[sample]*7,'warmups':2}
                return SimpleNamespace(returncode=0,stdout=json.dumps(result).encode(),stderr=b'')
            with patch.object(sys,'argv',[str(benchmark.__file__),'--output',str(target)]), \
                 patch.object(benchmark.subprocess,'check_output',side_effect=git), \
                 patch.object(benchmark,'source_identity',return_value=identity), \
                 patch.object(benchmark,'capacity',return_value={'memory_budget_bytes':1000}), \
                 patch.object(benchmark,'verify_quality_parity',return_value={'passed':True}), \
                 patch.object(benchmark,'peak_memory',return_value=10), \
                 patch.object(benchmark.subprocess,'run',side_effect=child):
                benchmark.main()
            result=json.loads(target.read_bytes())
            self.assertEqual(result['status'],'completed')
            self.assertEqual(len(observed),72)
            self.assertEqual(result['frozen_baseline_sha256'],hashlib.sha256(baseline.read_bytes()).hexdigest())
            self.assertTrue(all(d['adopt_shared_for_case'] for d in result['decisions'].values()))


class ResultParityTests(unittest.TestCase):
    def test_all_declared_output_sets_and_unavailable_profiles(self):
        self.assertEqual(len(benchmark.CASES),36)
        report=benchmark.verify_quality_parity()
        self.assertTrue(report['passed'])
        self.assertEqual(report['complete_projection_comparisons'],72)

    def test_separate_join_preserves_real_metadata_and_global_sorted_cap(self):
        from dataclasses import replace
        from equity_feature_contracts import FeatureResult
        batches,context,config=benchmark.inputs('small/all')[0]
        results=tuple(benchmark.compute_intraday(batches,context,config,features=(name,))
                      for name in benchmark.SELECTED['all'])
        joined=benchmark.join_results(results)
        self.assertEqual(joined.metadata,results[0].metadata)
        self.assertEqual(joined.values,tuple(column for result in results for column in result.values))
        self.assertEqual(joined.quality,tuple(row for result in results for row in result.quality))
        self.assertEqual(joined.evidence,results[0].evidence)
        self.assertEqual(len(joined.evidence),16)
        self.assertEqual({row.feature_id for row in joined.evidence},{'intraday.band_lower'})
        changed=replace(results[-1],metadata=replace(results[-1].metadata,backend_version='different'))
        with self.assertRaises(AssertionError):benchmark.join_results((*results[:-1],changed))


if __name__=='__main__':unittest.main(verbosity=2)
