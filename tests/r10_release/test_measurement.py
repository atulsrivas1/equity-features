from copy import deepcopy
from unittest.mock import patch
import unittest
from release_fixture import measurement as m


class Measurement(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.oracle=m.load_oracle()
        # Exact deterministic instrumentation control, not actual timing evidence.
        cls.reads=iter(range(160));cls.control=m.measure(cls.oracle,_timer=lambda:next(cls.reads))

    def test_literal_half_negative_and_zero_statistics(self):
        for case in self.oracle['statistics_controls']:
            b=m.statistics(case['baseline_raw_ns']);w=m.statistics(case['wrapper_raw_ns'])
            self.assertEqual((b['min_ns'],b['max_ns'],b['median_ns']),(case['baseline_min_ns'],case['baseline_max_ns'],case['baseline_median_ns']))
            self.assertEqual((w['min_ns'],w['max_ns'],w['median_ns']),(case['wrapper_min_ns'],case['wrapper_max_ns'],case['wrapper_median_ns']))
            self.assertEqual(m.comparison(b,w),(case['extra_median_ns'],case['median_ratio']))
        with self.assertRaises(m.MeasurementError):m.fraction({'numerator':22,'denominator':4})

    def test_pair_clock_order_and_exact_call_counts(self):
        self.assertEqual([x['id'] for x in self.control['workloads']],list(m.IDS))
        with self.assertRaises(StopIteration):next(self.reads)
        for w in self.control['workloads']:
            self.assertEqual(w['baseline']['raw_ns'],[1]*10);self.assertEqual(w['wrapper']['raw_ns'],[1]*10)
        calls=[];baseline=m.d.evaluate_diagnostics;wrapper=m.c.check_diagnostics
        def b(*args):calls.append('baseline');return baseline(*args)
        def w(*args):calls.append('wrapper');return wrapper(*args)
        reads=iter(range(160))
        with patch.object(m.d,'evaluate_diagnostics',side_effect=b),patch.object(m.c,'check_diagnostics',side_effect=w):
            # Wrapper internally invokes the diagnostic evaluator once. Distinguish
            # outer baseline/wrapper order from that internal accepted call.
            result=m.measure(self.oracle,_timer=lambda:next(reads))
        self.assertEqual(calls,['baseline','wrapper','baseline']*52)
        self.assertEqual(len(result['workloads']),4)

    def test_raw_clock_refusals_and_zero_elapsed(self):
        for case in self.oracle['raw_clock_controls']:
            reads=iter(case['reads'])
            if 'code' in case:
                with self.assertRaises(m.MeasurementError) as error:m.timed(lambda:'value',lambda:next(reads))
                self.assertEqual(error.exception.code,case['code'])
            else:self.assertEqual(m.timed(lambda:'value',lambda:next(reads)),('value',case['expected_ns']))
        for bad in ([0]*9,[0]*9+[True],[0]*9+[-1],[0]*9+[1.0]):
            with self.assertRaises(m.MeasurementError):m.statistics(bad)

    def test_closed_report_refuses_tampered_counts_snapshots_types_and_stats(self):
        mutations=[lambda v:v.update(extra=True),lambda v:v.update(sample_pairs=True),
            lambda v:v['metadata'].update(extra='field'),lambda v:v['metadata'].update(cpu_count=True),
            lambda v:v['metadata'].update(timer_resolution_seconds='NaN'),lambda v:v['metadata'].update(timer_monotonic=1),
            lambda v:v['workloads'].reverse(),lambda v:v['workloads'][0].update(id='k16'),
            lambda v:v['workloads'][0].update(parity=False),lambda v:v['workloads'][0].update(checks=True),
            lambda v:v['workloads'][0]['baseline'].update(min_ns=2),
            lambda v:v['workloads'][0]['baseline'].update(median_ns={'numerator':2,'denominator':2}),
            lambda v:v['workloads'][0].update(extra_median_ns={'numerator':-1,'denominator':1}),
            lambda v:v['workloads'][0].update(median_ratio=None),
            lambda v:v['workloads'][0]['baseline_snapshot'].update(passed_count=True),
            lambda v:v['workloads'][0]['wrapper_snapshot']['findings'][0].update(check_id='other')]
        m.validate(self.control,self.oracle)
        for change in mutations:
            value=deepcopy(self.control);change(value)
            with self.assertRaises(m.MeasurementError):m.validate(value,self.oracle)
        # Valid negative and zero-baseline statistics must survive the full parser.
        for control in self.oracle['statistics_controls']:
            value=deepcopy(self.control);w=value['workloads'][0]
            w['baseline']=m.statistics(control['baseline_raw_ns']);w['wrapper']=m.statistics(control['wrapper_raw_ns'])
            w['extra_median_ns']=control['extra_median_ns'];w['median_ratio']=control['median_ratio'];m.validate(value,self.oracle)

    def test_wrong_assertions_and_private_faults_fail_closed_without_context(self):
        for key in ('status','check_id'):
            wrong=deepcopy(self.oracle);wrong['workloads'][0]['expected_snapshot']['findings'][0][key]='unknown' if key=='status' else 'other'
            with self.assertRaises(m.MeasurementError) as error:m.measure(wrong,_timer=lambda:0)
            self.assertEqual(error.exception.code,'parity_failed');self.assertIsNone(error.exception.__context__)
        wrong=deepcopy(self.oracle);wrong['workloads'][0]['expected_snapshot']['passed_count']=0
        with self.assertRaises(m.MeasurementError) as error:m.measure(wrong,_timer=lambda:0)
        self.assertEqual(error.exception.code,'parity_failed')
        with patch.object(m.d,'evaluate_diagnostics',side_effect=ValueError('synthetic-private-sentinel')):
            with self.assertRaises(m.MeasurementError) as error:m.measure(self.oracle)
        self.assertEqual(str(error.exception),'Measurement rejected: invalid_schema')
        self.assertIsNone(error.exception.__context__);self.assertIsNone(error.exception.__cause__)


if __name__=='__main__':unittest.main()
