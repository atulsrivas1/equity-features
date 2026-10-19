"""Preserve frozen measurement evidence and report partial failed repetitions."""
import hashlib
import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
import benchmark_intraday_preparation as benchmark


class BenchmarkGuardTests(unittest.TestCase):
    def test_original_committed_measurement_and_baseline_bytes_are_preserved(self):
        root=benchmark.ROOT/'docs/stories'
        report=(root/'EQ-137_PREPARATION_BENCHMARK.json').read_bytes()
        baseline=(root/'EQ-137_PREPARATION_BASELINE.json').read_bytes()
        self.assertEqual(hashlib.sha256(report).hexdigest(),'78f33000ae88ff0ad1612fb86813d2b8081de92567108eaacd6c4c710aa55996')
        baseline_sha=hashlib.sha256(baseline).hexdigest()
        self.assertEqual(baseline_sha,'66b76dba6582cedab49c6a37dc9e174085b76e74e90b733cba72a72510be6c38')
        value=json.loads(report)
        self.assertEqual(value['frozen_baseline_sha256'],baseline_sha)
        self.assertEqual(value['source_commit'],'c7a46d6489ad9fde4c0bbfc401e9ccafaa6ad2b3')
        self.assertEqual(value['status'],'completed')

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
            result=benchmark.measure('small','separate')
        self.assertEqual(result['status'],'failed')
        self.assertEqual(result['failed_repeat'],3)
        self.assertEqual(len(result['samples']),1)
        self.assertEqual(result['failure_type'],'RuntimeError')


    def test_failed_final_source_closure_retains_all_seven_samples(self):
        with patch.object(benchmark,'source_identity',side_effect=[{'source':'first'},{'source':'changed'}]),patch.object(benchmark,'inputs',return_value=[]):
            result=benchmark.measure('small','separate')
        self.assertEqual(result['status'],'failed')
        self.assertEqual(result['failed_phase'],'post-measurement closure')
        self.assertEqual(len(result['samples']),7)
        self.assertEqual(result['failure_type'],'AssertionError')


if __name__=='__main__':unittest.main(verbosity=2)
