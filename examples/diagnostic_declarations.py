"""Installed pure consumer; source and history remain caller declarations."""
from equity_feature_contracts import EntityKey, AvailabilitySpec, SourceBinding, ReferenceFact
from equity_feature_diagnostics import (DecisionContext, DiagnosticPolicy, KnowledgeCheck,
    MembershipCheck, ReferenceDeclaration, RevisionCheck, RevisionIdentity,
    DiagnosticReport, evaluate_diagnostics)

context = DecisionContext('demo', EntityKey('A','S'), AvailabilitySpec(100,100,120))
strict = DiagnosticPolicy('synthetic-strict','strict','allow')
reference = ReferenceDeclaration('demo',context.entity,'universe_membership',
    SourceBinding('synthetic','snap1','map1','input1'),1,True)
facts = (ReferenceFact(0,'r0','universe_membership',0,None,100,text='U'),)
report: DiagnosticReport = evaluate_diagnostics(context,strict,(
    MembershipCheck('historical','historical','universe_membership','U',50,reference,facts,'historical'),
    MembershipCheck('current','current','universe_membership','U',50,reference,facts,'current_only'),
    KnowledgeCheck('later','cited-row',101),
    RevisionCheck('revision','cited-revision',RevisionIdentity('snap1','v1'),RevisionIdentity('snap1','v1'),0,None,50,101),
))
assert tuple(f.status for f in report.findings) == ('passed','unknown','failed','failed')
assert (report.passed_count,report.unknown_count,report.failed_count)==(1,1,2)
assert report.admission == 'denied'
assert not report.source_authenticated and not report.historical_acquisition_verified
print('Supplied historical/current-only/late-knowledge findings retained; source truth unverified.')
