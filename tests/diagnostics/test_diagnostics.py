"""Literal pre-code expectations and independent structural/immutable controls."""
import dataclasses
import json
from pathlib import Path
import unittest

from equity_feature_contracts import inputs as i, policies as p, results as r, specs as s
from equity_feature_evidence import ContentFingerprint
import equity_feature_diagnostics as d

# The installed qualification copies this literal accepted oracle beside tests.
ORACLE = Path(__file__).with_name('EQ-101_TRUTH_TABLE.json')
if not ORACLE.exists():
    ORACLE = Path(__file__).resolve().parents[2] / 'docs/stories/EQ-101_TRUTH_TABLE.json'


def context(C=100, K=100, E=120):
    return d.DecisionContext('demo', r.EntityKey('A', 'S'), s.AvailabilitySpec(C, K, E))


def ref(observed=1, complete=True, kind='universe_membership'):
    return d.ReferenceDeclaration('demo', r.EntityKey('A','S'), kind,
        i.SourceBinding('synthetic','snapshot1','map1','reference1'), observed, complete)


def member(facts=None, reference='default', selected='universe_membership', **kwargs):
    if facts is None: facts = (p.ReferenceFact(0,'r0',selected,0,None,100,text='U'),)
    if reference == 'default': reference = ref(len(facts), kind=selected)
    return d.MembershipCheck(kwargs.pop('check_id','m'), kwargs.pop('subject_id','member'),
        selected, kwargs.pop('scope','U'), kwargs.pop('query',50), reference,
        facts, kwargs.pop('history','historical'), **kwargs)


def map_case(case):
    """Input construction only. Never computes expected findings."""
    v=case['input']; tag=case['kind']; ident=case['id']
    ctx=context(**case.get('context',{}))
    if tag=='market_time':
        session=None if v['open'] is None or v['close'] is None else s.SessionSpec(
            'demo','S',v['open'],v['close'],'UTC',include_closing_auction=v['include_closing'])
        check=d.MarketCheck(ident,ident,session,v['time'],v['convention'],v['start'])
    elif tag=='knowledge_time': check=d.KnowledgeCheck(ident,ident,v['known'])
    elif tag=='declared_context':
        observed=None if v is None else s.AvailabilitySpec(v['C'],v['K'],v['E'],v['mode'],
            'fixture' if v['mode']=='reconstruction' else None)
        check=d.ContextCheck(ident,ident,observed)
    elif tag=='membership':
        reference=None if v['reference'] is None else ref(v['reference']['observed'],v['reference']['complete'],v['selected_kind'])
        facts=tuple(p.ReferenceFact(row,rid,v['selected_kind'],start,end,known,text=text)
                    for row,rid,start,end,known,text in v['facts'])
        check=member(facts,reference,v['selected_kind'],check_id=ident,subject_id=ident,
            scope=v['scope'],query=v['query'],history=v['history'])
    elif tag=='revision':
        expected=None if v['expected'] is None else d.RevisionIdentity(*v['expected'])
        observed=None if v['observed'] is None else d.RevisionIdentity(*v['observed'])
        check=d.RevisionCheck(ident,ident,expected,observed,v['start'],v['end'],v['query'],v['known'])
    elif tag=='adjustment':
        def policy(a):
            if a is None: return None
            fields=a.split('/')
            return p.ActionPolicy(i.AdjustmentSpec(*fields[:4]),0,*fields[4:])
        check=d.AdjustmentCheck(ident,ident,policy(v['expected']),policy(v['observed']),
            None if v['expected_unit'] is None else i.PriceUnit(*v['expected_unit']),
            None if v['observed_unit'] is None else i.PriceUnit(*v['observed_unit']))
    else: check=d.FreshnessCheck(ident,ident,v['basis'],v['target'],v['observed'],v['tolerance'])
    return ctx,check


class DiagnosticsTests(unittest.TestCase):
    def evaluate(self,*checks,ctx=None,mode='advisory',unknown='deny'):
        return d.evaluate_diagnostics(ctx or context(), d.DiagnosticPolicy('policy',mode,unknown),checks)

    def reject(self, code, call):
        with self.assertRaises(d.DiagnosticsError) as caught: call()
        self.assertEqual(caught.exception.code,code)
        self.assertEqual(str(caught.exception),'Diagnostics rejected: '+code)
        self.assertIsNone(caught.exception.__cause__)

    def test_literal_38_checks(self):
        data=json.loads(ORACLE.read_bytes());self.assertEqual(len(data['cases']),38)
        for case in data['cases']:
            with self.subTest(case=case['id']):
                ctx,check=map_case(case);report=self.evaluate(check,ctx=ctx);f=report.findings[0]
                self.assertEqual({'status':f.status,'reasons':list(f.reasons),'assessed':f.assessed,
                    'unknown_prerequisites':f.unknown_prerequisites,'age_ns':f.age_ns},case['expected'])
                self.assertEqual((f.check_id,f.subject_id,f.kind,f.content),(case['id'],case['id'],case['kind'],None))
                self.assertEqual(f.severity,{'passed':'info','failed':'error','unknown':'warning'}[f.status])
                self.assertFalse(report.source_authenticated);self.assertFalse(report.historical_acquisition_verified)

    def test_literal_six_aggregates(self):
        data=json.loads(ORACLE.read_bytes());cases={c['id']:c for c in data['cases']}
        for a in data['admission_cases']:
            with self.subTest(case=a['id']):
                checks=tuple(map_case(cases[k])[1] for k in a['case_ids'])
                q=self.evaluate(*checks,mode=a['mode'],unknown=a['unknown_action'])
                self.assertEqual({'admission':q.admission,'requested':q.requested_count,
                    'passed':q.passed_count,'failed':q.failed_count,'unknown':q.unknown_count,
                    'assessed':q.assessed_count,'unknown_prerequisites':q.unknown_prerequisite_count},a['expected'])
                self.assertEqual(q.not_requested,tuple(sorted(set(('market_time','knowledge_time','declared_context','membership','revision','adjustment','freshness'))-{c.kind for c in checks})))

    def test_all18_structural_refusals(self):
        good=member();fact=good.facts[0];ses=s.SessionSpec('demo','S',0,200,'UTC')
        huge=lambda n:tuple(p.ReferenceFact(k,'r'+str(k),'universe_membership',0,None,0,text='U') for k in range(n))
        cases={
          'mixed_membership_kind':lambda:member((dataclasses.replace(fact,fact_kind='sector_membership'),)),
          'wrong_reference_kind':lambda:member(reference=ref(kind='sector_membership')),
          'wrong_session_namespace':lambda:self.evaluate(d.MarketCheck('x','x',dataclasses.replace(ses,namespace='other'),1,'ordinary_event',None)),
          'wrong_session_id':lambda:self.evaluate(d.MarketCheck('x','x',dataclasses.replace(ses,session_id='other'),1,'ordinary_event',None)),
          'duplicate_check_id':lambda:self.evaluate(d.KnowledgeCheck('x','a',0),d.KnowledgeCheck('x','b',0)),
          'duplicate_kind_subject':lambda:self.evaluate(d.KnowledgeCheck('x','a',0),d.KnowledgeCheck('y','a',0)),
          'missing_reference_with_facts':lambda:member(reference=None),
          'duplicate_reference_id':lambda:member((fact,dataclasses.replace(fact,row_index=1))),
          'duplicate_reference_row':lambda:member((fact,dataclasses.replace(fact,reference_id='r1'))),
          'row_index_outside_population':lambda:member((dataclasses.replace(fact,row_index=1),)),
          'bool_as_int':lambda:d.KnowledgeCheck('x','x',True),
          'unknown_version':lambda:d.DiagnosticReport(context(),d.DiagnosticPolicy('p','advisory','deny'),self.evaluate(good).findings,'2'),
          'unknown_kind':lambda:d.MembershipCheck('x','x','unsupported_membership_kind','U',0,None,(),'historical'),
          'oversized_nested_identity':lambda:member(reference=dataclasses.replace(ref(),source=i.SourceBinding('a'*129,'s','m','i'))),
          'too_many_checks':lambda:self.evaluate(*(d.KnowledgeCheck(str(k),str(k),0) for k in range(257))),
          'too_many_facts':lambda:member(huge(1025)),
          'aggregate_fact_limit':lambda:self.evaluate(*(member(huge(820),check_id=str(k),subject_id=str(k)) for k in range(5))),
          'unsupported_borrowed_record':lambda:d.DecisionContext('demo',object(),s.AvailabilitySpec(0,0,0)),
        }
        expected=json.loads(ORACLE.read_bytes())['required_structural_refusals']
        self.assertEqual(set(cases),set(expected))
        for name,call in cases.items():
            with self.subTest(case=name):self.reject(expected[name],call)

    def test_both_kinds_projection_and_extreme_declared_population(self):
        for kind in ('universe_membership','sector_membership'):
            self.assertEqual(self.evaluate(member(selected=kind)).passed_count,1)
        q=self.evaluate(member((),ref(i.I64_MAX)))
        self.assertEqual(q.findings[0].reasons,('incomplete_projection',))
        self.assertEqual(q.unknown_count,1)
        self.assertEqual(self.evaluate(member((),ref(0))).findings[0].reasons,('membership_absent',))

    def test_list_detachment_and_frozen_derived_report(self):
        facts=[p.ReferenceFact(0,'r','universe_membership',0,None,0,text='U')]
        check=member(facts);facts.clear();self.assertEqual(len(check.facts),1)
        requests=[check];report=d.evaluate_diagnostics(context(),d.DiagnosticPolicy('p','strict','deny'),requests)
        requests.clear();self.assertEqual(report.requested_count,1);self.assertEqual(report.admission,'admitted')
        with self.assertRaises(dataclasses.FrozenInstanceError):report.passed_count=99
        with self.assertRaises(dataclasses.FrozenInstanceError):report.findings[0].status='failed'
        with self.assertRaises(TypeError):d.DiagnosticReport(context(),report.policy,report.findings,passed_count=99)
        original=dataclasses.asdict(report)
        self.evaluate(d.KnowledgeCheck('k','late',101));self.assertEqual(dataclasses.asdict(report),original)

    def test_content_preserved_without_authentication(self):
        content=ContentFingerprint('canonical_batch','a'*64,123)
        q=self.evaluate(d.KnowledgeCheck('k','cited',101,content=content))
        self.assertEqual(q.findings[0].content,content);self.assertFalse(q.source_authenticated)

    def test_exact_request_types_and_nonfocused_abort(self):
        self.reject('invalid_schema',lambda:d.evaluate_diagnostics(context(),d.DiagnosticPolicy('p','strict','deny'),iter(())))
        class Sub(d.KnowledgeCheck):pass
        self.reject('invalid_schema',lambda:self.evaluate(Sub('x','x',0)))
        bad=d.KnowledgeCheck('bad','bad',0);object.__setattr__(bad,'known_at_ns',True)
        self.reject('invalid_schema',lambda:self.evaluate(d.KnowledgeCheck('good','good',0),bad))
        borrowed=r.EntityKey('A','S');object.__setattr__(borrowed,'instrument_id','private\nsecret')
        self.reject('invalid_schema',lambda:d.DecisionContext('demo',borrowed,s.AvailabilitySpec(0,0,0)))

    def test_limits_at_and_above(self):
        self.assertEqual(self.evaluate(*(d.KnowledgeCheck(str(k),str(k),0) for k in range(256))).passed_count,256)
        self.evaluate(d.KnowledgeCheck('a'*128,'b'*128,i.I64_MIN))
        self.reject('limit_exceeded',lambda:d.KnowledgeCheck('a'*129,'b',0))
        self.reject('invalid_schema',lambda:d.KnowledgeCheck('x','x',i.I64_MAX+1))
        facts=tuple(p.ReferenceFact(k,'r'+str(k),'universe_membership',k,k+1,0,text='U') for k in range(1024))
        checks=tuple(member(facts,check_id=str(k),subject_id=str(k),query=50) for k in range(4))
        self.assertEqual(self.evaluate(*checks).passed_count,4)
        intervals=tuple(s.IntervalSpec(str(k),k,k+1) for k in range(128))
        ses=s.SessionSpec('demo','S',0,200,'UTC',intervals)
        self.evaluate(d.MarketCheck('s','s',ses,1,'ordinary_event',None))
        too=s.SessionSpec('demo','S',0,200,'UTC',intervals+(s.IntervalSpec('extra',128,129),))
        self.reject('limit_exceeded',lambda:d.MarketCheck('s','s',too,1,'ordinary_event',None))

    def test_deep_nested_bounds_and_borrowed_versions(self):
        self.reject('limit_exceeded',lambda:d.AdjustmentCheck('a','a',None,None,i.PriceUnit(0,'x'*129),None))
        self.reject('limit_exceeded',lambda:member((p.ReferenceFact(0,'r','universe_membership',0,None,0,text='x'*129),)))
        a=p.ActionPolicy(i.AdjustmentSpec(),0);object.__setattr__(a,'schema_version','9')
        self.reject('unsupported_version',lambda:d.AdjustmentCheck('a','a',a,None,None,None))
        a=p.ActionPolicy(i.AdjustmentSpec(),0);object.__setattr__(a,'anchor_ns',True)
        self.reject('invalid_schema',lambda:d.AdjustmentCheck('a','a',a,None,None,None))

    def test_addition_delisting_and_revision_half_open(self):
        # One complete population retains an ended constituent and its replacement.
        facts=(p.ReferenceFact(0,'old','universe_membership',0,50,20,text='OLD'),
               p.ReferenceFact(1,'new','universe_membership',50,None,50,text='NEW'))
        q=self.evaluate(member(facts,scope='OLD',query=49),
            member(facts,scope='NEW',query=50,check_id='new',subject_id='new'))
        self.assertEqual(tuple(f.status for f in q.findings),('passed','passed'))
        self.assertEqual(self.evaluate(member(facts,scope='OLD',query=50)).findings[0].reasons,('membership_scope_mismatch',))
        identity=d.RevisionIdentity('snap','r1')
        self.assertEqual(self.evaluate(d.RevisionCheck('r','r',identity,identity,0,50,50,101)).findings[0].reasons,
                         ('late_knowledge','outside_effective_interval'))

    def test_missing_active_fields_count_once_with_visible_overlap(self):
        facts=(p.ReferenceFact(0,'a','sector_membership',0,None,None,text=None),
               p.ReferenceFact(1,'b','sector_membership',0,None,None,text=None))
        f=self.evaluate(member(facts,selected='sector_membership')).findings[0]
        self.assertEqual((f.status,f.assessed,f.unknown_prerequisites),('failed',False,2))
        self.assertEqual(f.reasons,('ambiguous_membership','missing_knowledge','missing_membership_text'))

    def test_request_context_causal_and_member_identity(self):
        self.reject('invalid_schema',lambda:d.DecisionContext('demo',r.EntityKey('A','S'),s.AvailabilitySpec(100,100,120,'reconstruction','fixture')))
        wrong=dataclasses.replace(ref(),entity=r.EntityKey('B','S'))
        self.reject('inconsistent_binding',lambda:self.evaluate(member(reference=wrong)))
        wrong=dataclasses.replace(ref(),namespace='another')
        self.reject('inconsistent_binding',lambda:self.evaluate(member(reference=wrong)))

    def test_finding_reason_bound_and_exact_age(self):
        f=self.evaluate(d.FreshnessCheck('age','age','tool_read',i.I64_MAX,i.I64_MIN,i.I64_MAX)).findings[0]
        self.assertEqual((f.status,f.age_ns),('failed',2**64-1))
        self.reject('limit_exceeded',lambda:dataclasses.replace(f,reasons=('stale_observation',)*33))
        # Closed reasons currently have fewer than32 distinct values; a synthetic
        # 32-reason success would be an invalid positive, not a boundary proof.


if __name__=='__main__':unittest.main()
