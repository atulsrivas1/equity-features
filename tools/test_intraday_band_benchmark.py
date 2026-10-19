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
