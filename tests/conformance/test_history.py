"""Actual public future-slot invariance and a contaminated selected-slot control."""
from fractions import Fraction
import unittest
from equity_feature_evidence import canonical_content,fingerprint_batch,fingerprint_result
from equity_feature_conformance import compare_content,summarize
from history_fixture import history_fixture,compute


class History(unittest.TestCase):
    def test_actual_unused_future_full_content_invariance(self):
        batch,context,config=history_fixture();original=(canonical_content(batch),context.identity_digest,config.digest)
        result=compute(batch,context,config);raw=canonical_content(result);anchor=fingerprint_result(result)
        self.assertEqual(result.values[0].values,(float(Fraction(5,21)),))
        self.assertEqual((result.quality[0].status.value,result.quality[0].expected,result.quality[0].observed),('available',4,4))
        changed,other_context,other_config=history_fixture(future_close=12345,future_known=999)
        self.assertNotEqual(fingerprint_batch(batch),fingerprint_batch(changed))
        self.assertEqual((context,config),(other_context,other_config))
        observed=compute(changed,other_context,other_config)
        out=compare_content('unused-future-slot',anchor,fingerprint_result(observed),'equal')
        self.assertTrue(out.matched);self.assertEqual(canonical_content(observed),raw)
        self.assertEqual(original,(canonical_content(batch),context.identity_digest,config.digest))
        self.assertEqual(fingerprint_result(result),anchor)

    def test_selected_contamination_changes_output_and_wrong_expectation_fails(self):
        batch,context,config=history_fixture();baseline=compute(batch,context,config)
        changed,ctx,cfg=history_fixture(target_close=140);observed=compute(changed,ctx,cfg)
        self.assertEqual(observed.values[0].values,(float(Fraction(1,3)),))
        self.assertEqual(baseline.quality,observed.quality)
        a,b=fingerprint_result(baseline),fingerprint_result(observed)
        right=compare_content('contamination-observed',a,b,'different')
        wrong=compare_content('deliberately-wrong-invariance',a,b,'equal')
        self.assertTrue(right.matched);self.assertFalse(wrong.matched)
        self.assertEqual((summarize((right,wrong)).matched_count,summarize((right,wrong)).mismatched_count),(1,1))


if __name__=='__main__':unittest.main()
