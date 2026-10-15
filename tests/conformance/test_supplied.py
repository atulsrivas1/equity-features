"""Independent literal assertions, wrong-expectation and ordinary-data controls."""
from dataclasses import asdict,replace
import unittest
from unittest.mock import patch
import equity_feature_conformance as c
import equity_feature_diagnostics as d
from conformance_fixture import oracle,request,expected,run,fp,snapshot


class Supplied(unittest.TestCase):
    def test_all24_literal_scenarios_preserve_unknowns(self):
        cases=oracle()['diagnostic_cases'];self.assertEqual(len(cases),24)
        outcomes=[]
        for case in cases:
            with self.subTest(case=case['id']):
                args=request(case);before=asdict(args[0]),asdict(args[1]),tuple(asdict(x) for x in args[2])
                out=c.check_diagnostics(case['id'],*args,expected(case));self.assertTrue(out.matched,out.mismatch_fields)
                self.assertEqual(out.observed,expected(case));self.assertEqual(before,(asdict(args[0]),asdict(args[1]),tuple(asdict(x) for x in args[2])))
                outcomes.append(out)
        summary=c.summarize(tuple(outcomes));self.assertTrue(summary.all_matched)
        self.assertEqual((summary.total,summary.matched_count,summary.mismatched_count,summary.unknown_cases),(24,24,0,6))
        partial=next(o for o in outcomes if o.case_id=='late-current-visible-failure')
        self.assertEqual(partial.observed.failed_count,1);self.assertTrue(partial.remaining_unknown)

    def test_full_snapshot_wrong_assertions_mismatch_without_repair(self):
        case=oracle()['diagnostic_cases'][2];a=expected(case);f=a.findings[0]
        mutations=[replace(a,context=replace(a.context,namespace='other')),
            replace(a,policy=replace(a.policy,policy_id='other')),
            replace(a,findings=()),replace(a,requested_count=2),replace(a,passed_count=0),
            replace(a,failed_count=1),replace(a,unknown_count=1),replace(a,assessed_count=0),
            replace(a,unknown_prerequisite_count=1),replace(a,not_requested=()),
            replace(a,admission='denied'),replace(a,source_authenticated=True),
            replace(a,historical_acquisition_verified=True)]
        for change in (dict(check_id='other'),dict(subject_id='other'),dict(kind='freshness'),
                dict(content=fp(domain='canonical_batch')),dict(status='failed'),dict(severity='warning'),
                dict(reasons=('late_knowledge',)),dict(assessed=False),dict(unknown_prerequisites=1),dict(age_ns=1)):
            mutations.append(replace(a,findings=(replace(f,**change),)))
        for wrong in mutations:
            out=c.check_diagnostics('wrong',*request(case),wrong)
            self.assertFalse(out.matched);self.assertTrue(out.mismatch_fields)
            self.assertEqual(out.observed,a);self.assertEqual(out.expected,wrong)

    def test_order_and_missing_extra_expected_findings_are_not_zip_prefix(self):
        base=expected(oracle()['diagnostic_cases'][2]);f=base.findings[0]
        fs=(replace(f,check_id='ka',subject_id='sa'),replace(f,check_id='kb',subject_id='sb'))
        assertion=snapshot(fs)
        ctx,policy,_=request(oracle()['diagnostic_cases'][2])
        checks=(d.KnowledgeCheck('ka','sa',100),d.KnowledgeCheck('kb','sb',100))
        self.assertTrue(c.check_diagnostics('ordered',ctx,policy,checks,assertion).matched)
        for wrong in (replace(assertion,findings=tuple(reversed(fs))),replace(assertion,findings=fs[:1]),
                replace(assertion,findings=fs+(replace(f,check_id='kc',subject_id='sc'),))):
            self.assertFalse(c.check_diagnostics('bad-inventory',ctx,policy,checks,wrong).matched)

    def test_six_content_relations_and_missing_not_equal(self):
        outs=[]
        for case in oracle()['content_cases']:
            out=c.compare_content(case['id'],None if case['before'] is None else fp(case['before']),
                None if case['after'] is None else fp(case['after']),case['expected'])
            self.assertEqual(out.matched,case.get('matched',True));outs.append(out)
        summary=c.summarize(tuple(outs));self.assertEqual((summary.total,summary.matched_count,summary.mismatched_count,summary.unknown_cases),(6,5,1,3))
        self.assertFalse(summary.all_matched);self.assertEqual(outs[4].observed_relation,'unknown')

    def test_cited_batch_fingerprint_and_owned_detachment(self):
        case=oracle()['diagnostic_cases'][2];ctx,policy,checks=request(case);content=fp(domain='canonical_batch')
        check=replace(checks[0],content=content);a=expected(case);a=replace(a,findings=(replace(a.findings[0],content=content),))
        out=c.check_diagnostics('detached',ctx,policy,(check,),a);self.assertTrue(out.matched)
        frozen=asdict(out)
        object.__setattr__(content,'digest','b'*64);object.__setattr__(a.findings[0].content,'digest','c'*64)
        object.__setattr__(ctx.entity,'instrument_id','changed')
        self.assertEqual(asdict(out),frozen)
        summary=c.summarize((out,));object.__setattr__(out.observed.context,'namespace','changed')
        self.assertEqual(summary.outcomes[0].observed.context.namespace,'demo')

    def test_summary_recomputes_mutated_derived_flags_no_origin_claim(self):
        out=c.compare_content('declared',fp(),fp('b'),'equal');self.assertFalse(out.matched)
        object.__setattr__(out,'matched',True);object.__setattr__(out,'remaining_unknown',True)
        summary=c.summarize((out,));self.assertFalse(summary.all_matched)
        self.assertEqual((summary.mismatched_count,summary.unknown_cases),(1,0))
        # A locally constructed outcome remains data; the summary does not attest execution.
        declared=c.ContentOutcome('ordinary-data',fp(),fp(),'equal')
        self.assertTrue(c.summarize((declared,)).all_matched)

    def test_normalized_errors_retain_neither_payload_nor_context(self):
        case=oracle()['diagnostic_cases'][2]
        for error,code in ((ValueError('synthetic-private-sentinel'),'invalid_schema'),(d.DiagnosticsError('duplicate'),'duplicate')):
            with patch.object(d,'evaluate_diagnostics',side_effect=error):
                with self.assertRaises(c.ConformanceError) as caught:
                    c.check_diagnostics('fixed-errors',*request(case),expected(case))
            self.assertEqual(caught.exception.code,code)
            self.assertNotIn('synthetic-private-sentinel',str(caught.exception))
            self.assertIsNone(caught.exception.__context__)
            self.assertIsNone(caught.exception.__cause__)


if __name__=='__main__':unittest.main()
