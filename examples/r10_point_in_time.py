"""Pure installed consumer: a matched assertion can describe failure or unknown."""
from equity_feature_contracts import AvailabilitySpec,EntityKey,SessionSpec
import equity_feature_diagnostics as d
import equity_feature_conformance as c


def example() -> c.SuiteSummary:
    ctx=d.DecisionContext('demo',EntityKey('A','S'),AvailabilitySpec(100,100,120))
    policy=d.DiagnosticPolicy('consumer','strict','deny')
    checks=(d.KnowledgeCheck('known','cited-row',101),
        d.FreshnessCheck('fresh','reference','reference_publication',100,None,10),
        d.MarketCheck('market','interval',SessionSpec('demo','S',0,200,'synthetic'),101,'completed_interval',None))
    expected=c.DiagnosticSnapshot(c.ContextSnapshot('demo','A','S',100,100,120),
        c.PolicySnapshot('consumer','strict','deny'),(
            c.FindingSnapshot('known','cited-row','knowledge_time',None,'failed','error',('late_knowledge',),True,0,None),
            c.FindingSnapshot('fresh','reference','freshness',None,'unknown','warning',('missing_observation',),False,1,None),
            c.FindingSnapshot('market','interval','market_time',None,'failed','error',('market_bound','missing_market_fact'),False,1,None)),
        3,0,2,1,1,2,('adjustment','declared_context','membership','revision'),'denied',False,False)
    outcome=c.check_diagnostics('consumer',ctx,policy,checks,expected)
    summary=c.summarize((outcome,))
    assert summary.all_matched and summary.unknown_cases==1 and outcome.remaining_unknown
    assert outcome.observed.admission=='denied' and outcome.observed.unknown_prerequisite_count==2
    return summary


if __name__=='__main__':
    report=example();outcome=report.outcomes[0]
    assert isinstance(outcome,c.DiagnosticOutcome)
    print('Expected observations matched:2failed,1unknown;2missing prerequisites; strict admission denied.')
    print('Not requested: '+','.join(outcome.observed.not_requested)+'. Matching assertions are not safety or execution authority.')
