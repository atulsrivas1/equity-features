"""Outer synthetic producer example using the accepted R9 fixture verbatim."""
import hashlib
from pathlib import Path
import runpy
import tempfile
import equity_feature_agent_ledger as l
from equity_feature_evidence import canonical_content, encode_receipt, fingerprint_config, fingerprint_result, fingerprint_batch, InputFingerprint, verify_receipt_content
import equity_feature_agent_evidence as a


def original_chain() -> tuple[tuple[a.EventRecord, ...], tuple[bytes, ...]]:
    # Fixed owned example source; libraries imported by it must be installed.
    original = runpy.run_path(str(Path(__file__).with_name('evidence_content.py')))
    config, batch, result, receipt = (original[n] for n in ('config', 'batch', 'result', 'receipt'))
    before = tuple(canonical_content(x) for x in (config, batch, result)) + (encode_receipt(receipt),)
    assert verify_receipt_content(receipt, config, (('trades', batch),), result)
    actor = a.ActorDeclaration('synthetic-agent', a.ActorKind.SOFTWARE)
    absent = a.TimeDeclaration(None, None, None)
    recorded = a.TimeDeclaration(1000, 'caller-declared', 0)
    context = a.DecisionContext(config.session.namespace, config.session.session_id, config.availability)
    first = a.EventRecord('demo:producer', 1, 'demo:request', actor, absent, recorded, '0' * 64,
                           a.RequestSubject('r1', 'synthetic feature research', context))
    call = a.EventRecord('demo:producer', 2, 'demo:call', actor, absent, recorded, a.event_digest(first),
                          a.ToolCallSubject(a.event_reference(first), 'features.read', None,
                                            a.ArgumentSet(a.DisclosureState.RETAINED_COMPLETE, 1, [a.Argument('profile', 'synthetic-trades')])))
    payload = a.PayloadReference(a.PayloadKind.TOOL_RESULT, hashlib.sha256(before[2]).hexdigest(), len(before[2]), len(before[2]), a.DisclosureState.RETAINED_COMPLETE)
    response = a.EventRecord('demo:producer', 3, 'demo:result', actor, absent, recorded, a.event_digest(call),
                              a.ToolResultSubject(a.event_reference(call), a.ToolOutcome.SUCCEEDED, payload))
    receipt_ref = a.PayloadReference(a.PayloadKind.EXECUTION_RECEIPT, hashlib.sha256(before[3]).hexdigest(), len(before[3]), len(before[3]), a.DisclosureState.RETAINED_COMPLETE)
    read = a.EventRecord('demo:producer', 4, 'demo:read', actor, absent, recorded, a.event_digest(response),
                         a.FeatureReadSubject(a.event_reference(response), receipt_ref, fingerprint_config(config),
                                              [InputFingerprint('trades', batch.metadata.source.input_id, fingerprint_batch(batch))],
                                              fingerprint_result(result), [x.feature_id for x in result.values], context))
    assert a.check_references(read, [first, call, response]).fully_resolved
    assert a.verify_payload(receipt_ref, before[3]).retained_matched
    assert a.verify_payload(payload, before[2]).retained_matched
    assert a.decode_event(a.encode_event(read)) == read
    after = tuple(canonical_content(x) for x in (config, batch, result)) + (encode_receipt(receipt),)
    assert before == after
    print('Actual public producer/full result-quality-source-receipt parity retained; event declarations add no authentication or receipt transport.')
    return (first, call, response, read), before

def demonstrate() -> tuple[l.Checkpoint, tuple[bytes, ...]]:
    events, original = original_chain()
    wires = tuple(a.encode_event(e) for e in events)
    with tempfile.TemporaryDirectory(prefix='eq107-producer-') as folder:
        root = Path(folder).resolve()
        assert root.parent == Path(tempfile.gettempdir()).resolve()
        assert root.name.startswith('eq107-producer-')
        path = str(root/'events.sqlite')
        store = l.Ledger.create(path, 'demo:producer')
        try:
            for event in events: store.append(event, expected=store.head())
            terminal = store.head()
        finally: store.close()
        reopened = l.Ledger.open(path)
        try:
            assert reopened.verify(expected=terminal).anchor_status is l.AnchorStatus.MATCHED_TERMINAL
            page = reopened.export_page(after=0, through=terminal)
            assert tuple(a.encode_event(e) for e in page.events) == wires
            assert l.verify_page(page, start=l.Checkpoint('demo:producer', 0, '0'*64), through=terminal).reached_terminal
            assert a.verify_payload(page.events[-1].subject.receipt, original[3]).retained_matched
            assert a.verify_payload(page.events[-2].subject.payload, original[2]).retained_matched
            assert tuple(a.encode_event(e) for e in events) == wires
        finally: reopened.close()
    return terminal, original

if __name__ == '__main__': demonstrate()


