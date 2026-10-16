"""Strict public caller; paths and events are trusted external owner inputs."""
import equity_feature_agent_evidence as a
import equity_feature_agent_ledger as l

def typed(store: l.Ledger, event: a.EventRecord, expected: l.Checkpoint) -> l.Checkpoint:
    wire: bytes = l.encode_checkpoint(expected)
    parsed: l.Checkpoint = l.decode_checkpoint(wire)
    result: l.Verification = store.verify(expected=parsed)
    status: l.AnchorStatus = result.anchor_status
    terminal: l.Checkpoint = store.append(event, expected=parsed)
    page: l.Page = store.export_page(after=parsed.sequence, through=terminal)
    values: tuple[a.EventRecord, ...] = page.events
    checked: l.PageVerification = l.verify_page(page, start=parsed, through=terminal)
    refs: tuple[a.EventReference, ...] = checked.unresolved
    reconciliation: l.Reconciliation = store.reconcile(event, expected_before=parsed)
    observed: a.EventReference | None = reconciliation.observed
    _ = status, values, refs, observed
    return terminal
