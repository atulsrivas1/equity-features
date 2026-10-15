from dataclasses import asdict
import unittest
from release_fixture import consumer,measurement as m
import equity_feature_diagnostics as d
import equity_feature_conformance as c


class Consumer(unittest.TestCase):
    def test_three_observations_preserve_partial_unknown_and_not_requested(self):
        summary=consumer();out=summary.outcomes[0]
        self.assertTrue(summary.all_matched);self.assertEqual(summary.unknown_cases,1)
        self.assertEqual((out.observed.failed_count,out.observed.unknown_count,out.observed.assessed_count,out.observed.unknown_prerequisite_count),(2,1,1,2))
        self.assertEqual(out.observed.not_requested,('adjustment','declared_context','membership','revision'))
        self.assertEqual(out.observed.admission,'denied');self.assertFalse(out.observed.source_authenticated)

    def test_all_four_literal_workloads_full_snapshots_and_input_parity(self):
        oracle=m.load_oracle()
        for i,case in enumerate(oracle['workloads']):
            with self.subTest(case=case['id']):
                ctx,policy,checks=m.requests(i);expected=m.assertion(case['expected_snapshot'])
                before=asdict(ctx),asdict(policy),tuple(asdict(x) for x in checks),asdict(expected)
                baseline=d.evaluate_diagnostics(ctx,policy,checks)
                out=c.check_diagnostics(case['id'],ctx,policy,checks,expected)
                self.assertEqual(m.normalized(m.report_snapshot(baseline)),case['expected_snapshot'])
                self.assertEqual(m.normalized(out.observed),case['expected_snapshot']);self.assertTrue(out.matched)
                self.assertEqual(before,(asdict(ctx),asdict(policy),tuple(asdict(x) for x in checks),asdict(expected)))
        self.assertEqual(oracle['workloads'][3]['expected_snapshot']['findings'][0]['reasons'],['membership_absent'])


if __name__=='__main__':unittest.main()
