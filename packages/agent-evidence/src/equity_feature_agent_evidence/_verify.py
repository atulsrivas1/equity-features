"""Bounded supplied identity checks, without history or authenticity inference."""
from __future__ import annotations
import hashlib
from . import _model as m
from ._codec import encode_validated


def event_digest(event: m.EventRecord) -> str:
    return hashlib.sha256(encode_validated(m.copy_event(event))).hexdigest()


def event_reference(event: m.EventRecord) -> m.EventReference:
    event = m.copy_event(event)
    return m.EventReference(event.chain_id, event.sequence, event.event_id, event.kind,
                            hashlib.sha256(encode_validated(event)).hexdigest())


def verify_payload(reference: m.PayloadReference, content: bytes | None) -> m.PayloadCheck:
    reference = m.copy_payload(reference)
    m.require(content is None or type(content) is bytes)
    if content is not None: m.require(len(content) <= 65536, 'limit_exceeded')
    if content is None or reference.state not in (m.DisclosureState.RETAINED_COMPLETE, m.DisclosureState.TRUNCATED):
        return m.PayloadCheck(m.PayloadCheckStatus.UNAVAILABLE, reference.state, 0)
    m.require(len(content) == reference.retained_bytes and hashlib.sha256(content).hexdigest() == reference.digest, 'inconsistent_content')
    return m.PayloadCheck(m.PayloadCheckStatus.MATCHED_RETAINED, reference.state, len(content))


def check_references(event: m.EventRecord, retained_events: list[m.EventRecord] | tuple[m.EventRecord, ...]) -> m.ReferenceCheck:
    event = m.copy_event(event)
    def prior(value: m.EventRecord) -> m.EventRecord:
        value = m.copy_event(value)
        m.require(value.chain_id == event.chain_id and value.sequence < event.sequence, 'invalid_reference')
        return value
    values = m.sequence(retained_events, m.EventRecord, 64, prior)
    by_id: dict[str, m.EventReference] = {}
    by_sequence: dict[int, m.EventReference] = {}
    total = 0
    for value in values:
        m.require(value.event_id not in by_id and value.sequence not in by_sequence, 'duplicate')
        raw = encode_validated(value); total += len(raw)
        m.require(total <= 1048576, 'limit_exceeded')
        ref = m.EventReference(value.chain_id, value.sequence, value.event_id, value.kind, hashlib.sha256(raw).hexdigest())
        by_id[value.event_id] = ref; by_sequence[value.sequence] = ref
    good = []; missing = []
    for ref in m.references(event.subject):
        first = by_id.get(ref.event_id); second = by_sequence.get(ref.sequence)
        if first is None and second is None: missing.append(ref)
        else:
            m.require(first is not None and second is not None and first == second and first == ref, 'inconsistent_reference')
            good.append(ref)
    return m.ReferenceCheck(good, missing)
