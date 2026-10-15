"""Public pure consumer: matching an unknown assertion is not safety."""
from equity_feature_contracts import AvailabilitySpec,EntityKey
from equity_feature_diagnostics import DecisionContext,DiagnosticPolicy,KnowledgeCheck
from equity_feature_conformance import (ContextSnapshot,PolicySnapshot,FindingSnapshot,
    DiagnosticSnapshot,check_diagnostics,compare_content,summarize)

expected=DiagnosticSnapshot(ContextSnapshot('demo','A','S',100,100,120),
    PolicySnapshot('example','strict','deny'),
    (FindingSnapshot('known','selected-trade','knowledge_time',None,'unknown','warning',
        ('missing_knowledge',),False,1,None),),
    1,0,0,1,0,1,('adjustment','declared_context','freshness','market_time','membership','revision'),
    'denied',False,False)
outcome=check_diagnostics('unknown-declaration',
    DecisionContext('demo',EntityKey('A','S'),AvailabilitySpec(100,100,120)),
    DiagnosticPolicy('example','strict','deny'),(KnowledgeCheck('known','selected-trade',None),),expected)
content=compare_content('missing-result',None,None,'unknown')
summary=summarize((outcome,content))
assert summary.all_matched and summary.unknown_cases==2
assert outcome.observed.admission=='denied' and outcome.remaining_unknown
print('Two expected unknown cases matched; evidence remains unknown and strict admission denied.')
