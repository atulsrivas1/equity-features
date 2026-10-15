"""At/above conjunctive limits and fixed refusal, including no evaluator entry."""
from dataclasses import replace
import unittest
from unittest.mock import patch
import equity_feature_conformance as c
import equity_feature_diagnostics as d
from equity_feature_contracts import ReferenceFact
from conformance_fixture import oracle,request,expected,fp,snapshot


class Bounds(unittest.TestCase):
    def code(self,code,call):
        with self.assertRaises(c.ConformanceError) as caught:call()
        self.assertEqual(caught.exception.code,code)
        self.assertEqual(str(caught.exception),'Conformance rejected: '+code)
        self.assertTrue(caught.exception.__suppress_context__ or caught.exception.__context__ is None)

    def test_scalar_endpoints_types_shapes_and_domains(self):
        case=oracle()['diagnostic_cases'][2];a=expected(case);f=a.findings[0]
        c.ContextSnapshot('x'*128,'A','S',-2**63,2**63-1,0)
        c.ContextSnapshot('\U0001f600'*128,'A','S',0,0,0)
        c.FindingSnapshot('x','s','freshness',None,'unknown','warning',('missing_observation',),False,8,2**64-1)
        c.compare_content('max',replace(fp(),byte_length=2**63-1),replace(fp(),byte_length=2**63-1),'equal')
        for call in (lambda:replace(a.context,market_cutoff_ns=True),lambda:replace(a.context,market_cutoff_ns=2**63),
                lambda:replace(a,source_authenticated=1),lambda:replace(f,age_ns=2**64),
                lambda:replace(f,unknown_prerequisites=-1),lambda:replace(a,requested_count=True)):
            self.code('invalid_schema',call)
        self.code('limit_exceeded',lambda:replace(a.context,namespace='x'*129))
        self.code('limit_exceeded',lambda:replace(f,unknown_prerequisites=9))
        self.code('unsupported_version',lambda:replace(a,schema_version='2'))
        self.code('inconsistent_binding',lambda:c.compare_content('domain',fp(domain='canonical_batch'),fp(),'equal'))
        self.code('invalid_schema',lambda:replace(f,reasons=('unknown-reason',)))
        self.code('duplicate',lambda:replace(f,reasons=('late_knowledge','late_knowledge')))
        self.code('duplicate',lambda:replace(a,findings=(f,f)))
        class DerivedSnapshot(c.DiagnosticSnapshot):pass
        derived=DerivedSnapshot(a.context,a.policy,a.findings,a.requested_count,a.passed_count,
            a.failed_count,a.unknown_count,a.assessed_count,a.unknown_prerequisite_count,
            a.not_requested,a.admission,a.source_authenticated,a.historical_acquisition_verified)
        self.code('invalid_schema',lambda:c.check_diagnostics('subclass',*request(case),derived))
        class DerivedCheck(d.KnowledgeCheck):pass
        ctx,policy,_=request(case)
        self.code('invalid_schema',lambda:c.check_diagnostics('subclass-check',ctx,policy,(DerivedCheck('x','s',100),),a))

    def test_32check_boundary_and_preflight_before_evaluator(self):
        case=oracle()['diagnostic_cases'][2];ctx,policy,_=request(case);f=expected(case).findings[0]
        fs=tuple(replace(f,check_id='k'+str(i),subject_id='s'+str(i)) for i in range(32))
        checks=tuple(d.KnowledgeCheck(f.check_id,f.subject_id,100) for f in fs)
        a=snapshot(fs);self.assertTrue(c.check_diagnostics('at',ctx,policy,checks,a).matched)
        with patch.object(d,'evaluate_diagnostics',side_effect=AssertionError('must not enter')):
            self.code('limit_exceeded',lambda:c.check_diagnostics('above',ctx,policy,checks+(checks[0],),a))
            self.code('invalid_schema',lambda:c.check_diagnostics('lazy',ctx,policy,(x for x in checks),a))
            self.code('invalid_schema',lambda:c.check_diagnostics('foreign',ctx,policy,(object(),),a))
        self.code('limit_exceeded',lambda:replace(a,findings=fs+(replace(fs[0],check_id='extra'),)))
        self.code('limit_exceeded',lambda:replace(a,requested_count=33))
        self.code('limit_exceeded',lambda:replace(a,unknown_prerequisite_count=257))

    def test_membership_fact_and_total_limits(self):
        case=oracle()['diagnostic_cases'][10];ctx,policy,original=request(case);check=original[0]
        facts=tuple(ReferenceFact(i,'r'+str(i),'universe_membership',200,None,90,text='U') for i in range(128))
        reference=replace(check.reference,observed=128);checks=tuple(replace(check,check_id='c'+str(i),subject_id='s'+str(i),reference=reference,facts=facts) for i in range(4))
        f=c.FindingSnapshot('c0','s0','membership',None,'failed','error',('membership_absent',),True,0,None)
        a=snapshot(tuple(replace(f,check_id=x.check_id,subject_id=x.subject_id) for x in checks),admission='denied')
        self.assertTrue(c.check_diagnostics('at512',ctx,policy,checks,a).matched)
        with patch.object(d,'evaluate_diagnostics',side_effect=AssertionError('must not enter')):
            over=replace(checks[0],reference=replace(reference,observed=129),facts=facts+(ReferenceFact(128,'last','universe_membership',200,None,90,text='U'),))
            self.code('limit_exceeded',lambda:c.check_diagnostics('above128',ctx,policy,(over,),a))
            extra=replace(checks[0],check_id='extra',subject_id='extra')
            self.code('limit_exceeded',lambda:c.check_diagnostics('above512',ctx,policy,checks+(extra,),a))

    def test_summary_cardinality_and_aggregate_findings(self):
        base=expected(oracle()['diagnostic_cases'][2]);f=base.findings[0]
        a=snapshot(tuple(replace(f,check_id='c'+str(i),subject_id='s'+str(i)) for i in range(32)))
        outs=tuple(c.DiagnosticOutcome('case'+str(i),a,a) for i in range(8))
        self.assertEqual(c.summarize(outs).total,8)
        self.code('limit_exceeded',lambda:c.summarize(outs+(c.DiagnosticOutcome('extra',a,a),)))
        contents=tuple(c.compare_content('case'+str(i),None,None,'unknown') for i in range(32))
        self.assertEqual((c.summarize(contents).total,c.summarize(contents).unknown_cases),(32,32))
        self.code('limit_exceeded',lambda:c.summarize(contents+(c.compare_content('extra',None,None,'unknown'),)))
        self.code('limit_exceeded',lambda:c.summarize(()))
        self.code('duplicate',lambda:c.summarize((contents[0],contents[0])))
        self.code('invalid_schema',lambda:c.summarize((x for x in contents)))


if __name__=='__main__':unittest.main()
