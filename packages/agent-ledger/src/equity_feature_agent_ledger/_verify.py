"""Supplied-chain and contiguous-page checks using only public event operations."""
from __future__ import annotations
from typing import Iterable
from equity_feature_agent_evidence import (
    EventRecord, EventReference, EventKind, event_reference, encode_event,
    ToolCallSubject, ToolResultSubject, FeatureReadSubject, DecisionSubject,
    HumanReviewSubject, CancellationSubject, ErrorSubject, CorrectionSubject,
)
from . import _model as m


def references(value: EventRecord) -> tuple[EventReference, ...]:
    s = value.subject
    if type(s) is ToolCallSubject: return (s.request,)
    if type(s) is ToolResultSubject: return (s.call,)
    if type(s) is FeatureReadSubject: return (s.result,)
    if type(s) is DecisionSubject: return (s.request, *s.feature_reads)
    if type(s) is HumanReviewSubject: return (s.decision,)
    if type(s) is CancellationSubject: return (s.target,)
    if type(s) is ErrorSubject: return () if s.target is None else (s.target,)
    if type(s) is CorrectionSubject: return (s.target,) if s.replacement is None else (s.target, s.replacement)
    return ()


def _anchor(head: m.Checkpoint, expected: m.Checkpoint | None,
            hashes: dict[int, str]) -> m.AnchorStatus:
    if expected is None: return m.AnchorStatus.NOT_SUPPLIED
    if expected.chain_id != head.chain_id: return m.AnchorStatus.MISMATCH
    if expected.sequence > head.sequence: return m.AnchorStatus.NOT_COVERED
    if hashes[expected.sequence] != expected.head_hash: return m.AnchorStatus.MISMATCH
    return m.AnchorStatus.MATCHED_TERMINAL if expected.sequence == head.sequence else m.AnchorStatus.MATCHED_PREFIX


def scan(events: Iterable[EventRecord], chain_id: str,
         expected: m.Checkpoint | None = None) -> m.Verification:
    m.namespace(chain_id)
    if expected is not None: expected = m.checkpoint(expected)
    ids: dict[str, EventReference] = {}; seqs: dict[int, EventReference] = {}
    hashes = {0: m.GENESIS}; total = 0; head = m.Checkpoint(chain_id, 0, m.GENESIS)
    for source in events:
        m.require(head.sequence < m.MAX_EVENTS, 'limit_exceeded')
        value = m.event(source)
        m.require(value.chain_id == chain_id and value.sequence == head.sequence + 1 and value.previous_hash == head.head_hash, 'inconsistent_chain')
        m.require(value.event_id not in ids, 'duplicate')
        for ref in references(value):
            m.require(ids.get(ref.event_id) == seqs.get(ref.sequence) == ref, 'inconsistent_reference')
        total += len(encode_event(value)); m.require(total <= m.MAX_BYTES, 'limit_exceeded')
        own = event_reference(value); ids[value.event_id] = own; seqs[value.sequence] = own
        hashes[value.sequence] = own.digest; head = m.Checkpoint(chain_id, value.sequence, own.digest)
    return m.Verification(head, _anchor(head, expected, hashes), head.sequence, total)


def verify_events(events: list[EventRecord] | tuple[EventRecord, ...], *, chain_id: str,
                  expected: m.Checkpoint | None = None) -> m.Verification:
    m.require(type(events) in (list, tuple)); m.require(len(events) <= m.MAX_EVENTS, 'limit_exceeded')
    return scan(events, chain_id, expected)


def verify_page(page: m.Page, *, start: m.Checkpoint, through: m.Checkpoint,
                prior: list[EventRecord] | tuple[EventRecord, ...] = ()) -> m.PageVerification:
    m.require(type(page) is m.Page)
    page = m.Page(page.before, page.after, page.through, page.events)
    start = m.checkpoint(start); through = m.checkpoint(through)
    m.require(page.before == start and page.through == through, 'inconsistent_chain')
    m.require(start.chain_id == through.chain_id and start.sequence <= through.sequence, 'inconsistent_chain')
    m.require(type(prior) in (list, tuple)); m.require(len(prior) <= 64, 'limit_exceeded')
    ids: dict[str, EventReference] = {}; seqs: dict[int, EventReference] = {}; total = 0
    for source in prior:
        value = m.event(source)
        m.require(value.chain_id == start.chain_id and value.sequence <= start.sequence, 'inconsistent_reference')
        m.require(value.event_id not in ids and value.sequence not in seqs, 'duplicate')
        total += len(encode_event(value)); m.require(total <= 1048576, 'limit_exceeded')
        ref = event_reference(value); ids[value.event_id] = ref; seqs[value.sequence] = ref
    resolved: list[EventReference] = []; unresolved: list[EventReference] = []
    seen: set[EventReference] = set(); cited_ids: dict[str, EventReference] = {}; cited_seqs: dict[int, EventReference] = {}
    current = start
    m.require(bool(page.events) or start == through)
    for value in page.events:
        m.require(value.chain_id == start.chain_id and value.sequence == current.sequence + 1 and value.previous_hash == current.head_hash and value.sequence <= through.sequence, 'inconsistent_chain')
        m.require(value.event_id not in ids and value.sequence not in seqs, 'duplicate')
        for ref in references(value):
            for known in (cited_ids.get(ref.event_id), cited_seqs.get(ref.sequence)):
                m.require(known is None or known == ref, 'inconsistent_reference')
            first, second = ids.get(ref.event_id), seqs.get(ref.sequence)
            if first is None and second is None:
                target = unresolved
            else:
                m.require(first == second == ref, 'inconsistent_reference'); target = resolved
            if ref not in seen:
                target.append(ref); seen.add(ref)
            cited_ids[ref.event_id] = ref; cited_seqs[ref.sequence] = ref
        own = event_reference(value)
        for cited in (cited_ids.get(own.event_id), cited_seqs.get(own.sequence)):
            m.require(cited is None or cited == own, 'inconsistent_reference')
        ids[value.event_id] = own; seqs[value.sequence] = own
        current = m.Checkpoint(start.chain_id, value.sequence, own.digest)
    m.require(current == page.after, 'inconsistent_chain')
    if current.sequence == through.sequence:
        m.require(current == through, 'inconsistent_chain')
    return m.PageVerification(current, current == through, resolved, unresolved)
