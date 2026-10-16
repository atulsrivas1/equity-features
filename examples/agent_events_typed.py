"""Strict public consumer: exact constructor unions and immutable result fields."""
from equity_feature_contracts import AvailabilitySpec
from equity_feature_evidence import ContentFingerprint, InputFingerprint
import equity_feature_agent_evidence as a


def typed(event: a.EventRecord, reference: a.EventReference, prior: list[a.EventRecord]) -> bytes:
    actor = a.ActorDeclaration(None, a.ActorKind.UNKNOWN)
    time = a.TimeDeclaration(None, None, None)
    context = a.DecisionContext('demo', 'S', AvailabilitySpec(1, 2, 3))
    arg = a.Argument('profile', 'synthetic')
    args = a.ArgumentSet(a.DisclosureState.RETAINED_COMPLETE, 1, [arg])
    entries: tuple[a.Argument, ...] = args.entries
    payload = a.PayloadReference(a.PayloadKind.EXECUTION_RECEIPT, None, 0, None, a.DisclosureState.NOT_SUPPLIED)
    configuration = ContentFingerprint('configuration', 'a' * 64, 1)
    inputs = [InputFingerprint('trades', 'input1', ContentFingerprint('canonical_batch', 'b' * 64, 1))]
    read = a.FeatureReadSubject(reference, payload, configuration, inputs, None, ['session.trade.count'], context)
    frozen_inputs: tuple[InputFingerprint, ...] = read.inputs
    ids: tuple[str, ...] = read.feature_ids
    decision = a.DecisionSubject(reference, [reference], a.DecisionAction.DEFER, 'research')
    refs: tuple[a.EventReference, ...] = decision.feature_reads
    subjects: tuple[a.Subject, ...] = (
        a.RequestSubject('r1', 'research', context),
        a.ModelSubject(None, None, None, a.ModelIdentityState.NOT_SUPPLIED),
        a.ToolCallSubject(reference, 'features.read', None, args),
        a.ToolResultSubject(reference, a.ToolOutcome.UNKNOWN, payload), read, decision,
        a.HumanReviewSubject(reference, a.ReviewVerdict.UNKNOWN, 'review1'),
        a.CancellationSubject(reference, a.CancellationReason.REQUESTED),
        a.ErrorSubject(None, a.EventErrorCode.UNKNOWN),
        a.CorrectionSubject(reference, a.CorrectionOperation.REVOKE, None, 'revision'))
    # This function demonstrates typing only: callers must supply role-correct refs.
    _ = entries, frozen_inputs, ids, refs, subjects, actor, time
    checked: a.ReferenceCheck = a.check_references(event, prior)
    copied = a.ReferenceCheck(list(checked.verified), checked.unresolved)
    good: tuple[a.EventReference, ...] = copied.verified
    unavailable: a.PayloadCheck = a.verify_payload(payload, None)
    resolved: bool = copied.fully_resolved
    matched: bool = unavailable.retained_matched
    digest: str = a.event_digest(event)
    ref: a.EventReference = a.event_reference(event)
    _ = good, resolved, matched, digest, ref
    parsed: a.EventRecord = a.decode_event(a.encode_event(event))
    return a.encode_event(parsed)
