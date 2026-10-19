"""Preserve frozen measurement evidence and report partial failed repetitions."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import benchmark_intraday_indicators as benchmark


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


class ResultParityTests(unittest.TestCase):
    def test_all_declared_output_sets_and_unavailable_profiles(self):
        self.assertEqual(len(benchmark.CASES),24)
        report=benchmark.verify_quality_parity()
        self.assertTrue(report['passed'])
        self.assertEqual(report['complete_projection_comparisons'],28)

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
        self.assertEqual({row.feature_id for row in joined.evidence},{'intraday.atr'})
        changed=replace(results[-1],metadata=replace(results[-1].metadata,backend_version='different'))
        with self.assertRaises(AssertionError):benchmark.join_results((*results[:-1],changed))


if __name__=='__main__':unittest.main(verbosity=2)
