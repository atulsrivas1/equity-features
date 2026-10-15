"""Literal pre-code oracle mapping, independent of observed evaluator outputs."""
import json
from pathlib import Path
import equity_feature_diagnostics as d
import equity_feature_conformance as c
from equity_feature_contracts import (EntityKey,AvailabilitySpec,SessionSpec,SourceBinding,
    ReferenceFact,ActionPolicy,AdjustmentSpec,PriceUnit)
from equity_feature_evidence import ContentFingerprint

ORACLE=Path(__file__).with_name('EQ-104_CONFORMANCE_ORACLE.json')
if not ORACLE.exists(): ORACLE=Path(__file__).resolve().parents[2]/'docs/stories/EQ-104_CONFORMANCE_ORACLE.json'
KINDS=('adjustment','declared_context','freshness','knowledge_time','market_time','membership','revision')


def oracle(): return json.loads(ORACLE.read_text(encoding='utf-8'))


def fp(symbol='a',domain='feature_result'):
    return ContentFingerprint(domain=domain,digest=symbol*64,byte_length=1)


def snapshot(findings,*,mode='strict',action='deny',admission='admitted'):
    # These are literal assertion semantics, not output from evaluate_diagnostics.
    return c.DiagnosticSnapshot(c.ContextSnapshot('demo','A','S',100,100,120),
        c.PolicySnapshot('case-policy',mode,action),tuple(findings),len(findings),
        sum(f.status=='passed' for f in findings),sum(f.status=='failed' for f in findings),
        sum(f.status=='unknown' for f in findings),sum(f.assessed for f in findings),
        sum(f.unknown_prerequisites for f in findings),
        tuple(k for k in KINDS if all(f.kind!=k for f in findings)),admission,False,False)


def expected(case):
    status,reasons,unknown,age,admission=case['expected'];mode,action=case.get('policy',('strict','deny'))
    f=c.FindingSnapshot('check','subject',case['kind'],None,status,
        {'passed':'info','failed':'error','unknown':'warning'}[status],tuple(reasons),unknown==0,unknown,age)
    return snapshot((f,),mode=mode,action=action,admission=admission)


def request(case):
    context=d.DecisionContext('demo',EntityKey('A','S'),AvailabilitySpec(100,100,120))
    mode,action=case.get('policy',('strict','deny'));policy=d.DiagnosticPolicy('case-policy',mode,action)
    v=case['input'];kind=case['kind'];args=('check','subject')
    if kind=='market_time':
        check=d.MarketCheck(*args,SessionSpec('demo','S',*v['session'],'synthetic'),
            v['observed'],v['convention'],v.get('start'))
    elif kind=='knowledge_time':check=d.KnowledgeCheck(*args,v['known'])
    elif kind=='declared_context':
        C,K,E,mode=v['availability'];check=d.ContextCheck(*args,
            AvailabilitySpec(C,K,E,mode,'fixture' if mode=='reconstruction' else None))
    elif kind=='membership':
        reference=d.ReferenceDeclaration('demo',EntityKey('A','S'),'universe_membership',
            SourceBinding('synthetic','snapshot1','map1','reference1'),v['observed'],v['complete'])
        facts=tuple(ReferenceFact(row,rid,'universe_membership',start,end,known,text=text)
            for row,rid,start,end,known,text in v['facts'])
        check=d.MembershipCheck(*args,'universe_membership','U',100,reference,facts,v['history'])
    elif kind=='revision':
        check=d.RevisionCheck(*args,d.RevisionIdentity(*v['expected']),d.RevisionIdentity(*v['observed']),
            v['start'],v['end'],100,v['known'])
    elif kind=='adjustment':
        policy=d.DiagnosticPolicy('case-policy',mode,action)
        raw=ActionPolicy(AdjustmentSpec(),0)
        check=d.AdjustmentCheck(*args,raw,raw,PriceUnit(v['expected_scale'],'USD'),PriceUnit(v['observed_scale'],'USD'))
    elif kind=='freshness':
        check=d.FreshnessCheck(*args,'reference_publication',v['target'],v['observed'],v['tolerance'])
    else:raise AssertionError('unreviewed oracle kind')
    return context,policy,(check,)


def run(case):return c.check_diagnostics(case['id'],*request(case),expected(case))
