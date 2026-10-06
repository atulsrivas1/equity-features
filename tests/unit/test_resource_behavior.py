"""Resource diagnostics distinguish retained input, bounded evidence and controls."""
import importlib.util
from pathlib import Path
import sys
import unittest

spec=importlib.util.spec_from_file_location('resource_evidence',Path(__file__).resolve().parents[2]/'benchmarks/resource_behavior.py')
resource=importlib.util.module_from_spec(spec);spec.loader.exec_module(resource)


class ResourceEvidenceTests(unittest.TestCase):
    def test_shared_object_graph_excludes_interpreter_globals(self):
        from equity_feature_contracts import Column
        column=Column('price',(100,100))
        measured=resource.reachable({'data':[column,column],'module':sys,'class':dict})
        self.assertEqual(measured['object_counts']['Column'],1)
        self.assertIn('module',measured['excluded_types']);self.assertIn('type',measured['excluded_types'])
        self.assertGreater(measured['bytes'],0)

    def test_positive_detector_finds_raw_input_retention(self):
        from equity_feature_contracts import StreamPopulation
        from equity_features.incremental import SessionAccumulator
        batch,config,entity=resource.fixture('trades',8)
        accumulator=SessionAccumulator('trades',config,entity=entity,population=StreamPopulation.from_batch(batch))
        self.assertNotIn('CanonicalBatch',resource.reachable(accumulator)['object_counts'])
        accumulator.diagnostic_injected_input=batch
        self.assertEqual(resource.reachable(accumulator)['object_counts']['CanonicalBatch'],1)

    def test_all_families_bounded_records_atomic_failures_and_parity(self):
        for family in ('bars','structure','trades','top_k','quotes','continuous'):
            with self.subTest(family=family):
                result=resource.run_case(family,8,2,k=3,observations=2,windows=2)
                self.assertTrue(result['batch_stream_restore_merge_parity'])
                self.assertTrue(result['no_hidden_pool_creation_observed'])
                self.assertNotIn('CanonicalBatch',result['retained_python']['object_counts'])
                self.assertEqual(result['retained_top_rows'],3 if family=='top_k' else 0)
                self.assertEqual(result['retained_quote_rows'],2 if family=='quotes' else 0)
                self.assertEqual(result['retained_window_rows'],2 if family=='structure' else 0)
                self.assertEqual({x['case']:x['code'] for x in result['atomic_rejections']},
                    {'wrong_ordinal':'inconsistent_identity','contradictory_certificate':'inconsistent_identity',
                     'incompatible_restore':'invalid_schema','corrupt_restore':'invalid_schema'})

    def test_actual_external_cancel_limits_and_kernel_control_rejection(self):
        result=resource.controls()
        self.assertEqual({x['case']:x['code'] for x in result['adapter_outcomes']},
            {'cancel_before':'cancelled','row_limit':'resource_limit','chunk_limit':'resource_limit','cancel_between':'cancelled',
             'unsupported_kernel_threads':'invalid_config','unsupported_kernel_cancelled':'invalid_config'})
        self.assertEqual(result['caller_stopped_prefix_count'],1)
        self.assertEqual(next(x for x in result['adapter_outcomes'] if x['case']=='cancel_between')['yielded'],1)


if __name__=='__main__':unittest.main()
