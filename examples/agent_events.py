"""Pure supplied declarations; no clock/model/tool/ledger operation."""
import equity_feature_agent_evidence as a

request = a.EventRecord('demo:research', 1, 'demo:request',
    a.ActorDeclaration(None, a.ActorKind.UNKNOWN), a.TimeDeclaration(None, None, None),
    a.TimeDeclaration(100, 'caller-declared', 0), '0' * 64,
    a.RequestSubject('request-1', 'synthetic research', None))
model = a.EventRecord('demo:research', 2, 'demo:model',
    a.ActorDeclaration(None, a.ActorKind.SOFTWARE), a.TimeDeclaration(50, 'caller-declared', None),
    a.TimeDeclaration(100, 'caller-declared', 0), a.event_digest(request),
    a.ModelSubject(None, None, None, a.ModelIdentityState.NOT_SUPPLIED))
call = a.EventRecord('demo:research', 3, 'demo:call',
    a.ActorDeclaration('synthetic-agent', a.ActorKind.SOFTWARE), a.TimeDeclaration(None, None, None),
    a.TimeDeclaration(101, 'caller-declared', 0), a.event_digest(model),
    a.ToolCallSubject(a.event_reference(request), 'features.read', None,
                      a.ArgumentSet(a.DisclosureState.REDACTED, None, [])))
for event in (request, model, call):
    assert a.decode_event(a.encode_event(event)) == event
assert a.check_references(call, [request]).fully_resolved
assert not a.check_references(call, []).fully_resolved
missing = a.PayloadReference(a.PayloadKind.EXECUTION_RECEIPT, None, 0, None, a.DisclosureState.NOT_SUPPLIED)
assert not a.verify_payload(missing, None).retained_matched
print('Supplied event round trips and bounded references passed; identity, clock and missing receipt remain unauthenticated declarations.')
