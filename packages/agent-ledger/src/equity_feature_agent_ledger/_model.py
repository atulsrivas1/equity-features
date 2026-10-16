"""Bounded immutable ledger declarations; construction does not authenticate history."""
from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
import json
import re
from equity_feature_agent_evidence import (
    AgentEvidenceError, EventRecord, EventReference, encode_event, decode_event,
)

GENESIS = '0' * 64
MAX_EVENTS = 4096
MAX_BYTES = 33554432
_CODES = ('invalid_schema', 'unsupported_version', 'limit_exceeded',
          'inconsistent_chain', 'inconsistent_reference', 'duplicate',
          'stale_checkpoint', 'busy', 'storage_error', 'outcome_unknown', 'closed')


class LedgerError(ValueError):
    """Closed payload-free public error; private causes are not safe log text."""
    def __init__(self, code: str = 'invalid_schema') -> None:
        self.code = code if type(code) is str and code in _CODES else 'invalid_schema'
        super().__init__('Agent ledger rejected: ' + self.code)


def require(condition: bool, code: str = 'invalid_schema') -> None:
    if not condition:
        raise LedgerError(code)


def namespace(value: str) -> None:
    require(type(value) is str)
    require(len(value) <= 128, 'limit_exceeded')
    require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,62}:[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', value) is not None)


def integer(value: int, maximum: int) -> None:
    require(type(value) is int and value >= 0)
    require(value <= maximum, 'limit_exceeded')


@dataclass(frozen=True)
class Checkpoint:
    chain_id: str
    sequence: int
    head_hash: str

    def __post_init__(self) -> None:
        namespace(self.chain_id)
        integer(self.sequence, MAX_EVENTS)
        require(type(self.head_hash) is str and re.fullmatch('[0-9a-f]{64}', self.head_hash) is not None)
        require(self.sequence != 0 or self.head_hash == GENESIS, 'inconsistent_chain')


def checkpoint(value: Checkpoint) -> Checkpoint:
    require(type(value) is Checkpoint)
    return Checkpoint(value.chain_id, value.sequence, value.head_hash)


def event(value: EventRecord) -> EventRecord:
    require(type(value) is EventRecord)
    try:
        return decode_event(encode_event(value))
    except AgentEvidenceError as exc:
        code = {'invalid_reference': 'inconsistent_reference'}.get(exc.code, exc.code)
        raise LedgerError(code if code in _CODES else 'invalid_schema') from exc


def reference(value: EventReference) -> EventReference:
    require(type(value) is EventReference)
    try:
        return EventReference(value.chain_id, value.sequence, value.event_id, value.kind, value.digest)
    except AgentEvidenceError as exc:
        raise LedgerError({'invalid_reference': 'inconsistent_reference'}.get(exc.code, exc.code)) from exc


class AnchorStatus(str, Enum):
    NOT_SUPPLIED = 'not_supplied'
    MATCHED_TERMINAL = 'matched_terminal'
    MATCHED_PREFIX = 'matched_prefix'
    MISMATCH = 'mismatch'
    NOT_COVERED = 'not_covered'


class ReconciliationStatus(str, Enum):
    FOUND_EXACT = 'found_exact'
    ABSENT_AT_UNCHANGED_HEAD = 'absent_at_unchanged_head'
    CONFLICT = 'conflict'
    BASE_NOT_COVERED = 'base_not_covered'


@dataclass(frozen=True)
class Verification:
    head: Checkpoint
    anchor_status: AnchorStatus
    verified_events: int
    canonical_event_bytes: int

    def __post_init__(self) -> None:
        object.__setattr__(self, 'head', checkpoint(self.head))
        require(type(self.anchor_status) is AnchorStatus)
        integer(self.verified_events, MAX_EVENTS)
        integer(self.canonical_event_bytes, MAX_BYTES)
        require(self.verified_events == self.head.sequence, 'inconsistent_chain')
        if self.verified_events == 0:
            require(self.canonical_event_bytes == 0, 'inconsistent_chain')
        else:
            require(self.verified_events <= self.canonical_event_bytes <= min(self.verified_events * 16384, MAX_BYTES), 'inconsistent_chain')
        require(self.anchor_status is not AnchorStatus.MATCHED_PREFIX or self.head.sequence > 0)


@dataclass(frozen=True, init=False)
class Page:
    before: Checkpoint
    after: Checkpoint
    through: Checkpoint
    events: tuple[EventRecord, ...]

    def __init__(self, before: Checkpoint, after: Checkpoint, through: Checkpoint,
                 events: list[EventRecord] | tuple[EventRecord, ...]) -> None:
        object.__setattr__(self, 'before', checkpoint(before))
        object.__setattr__(self, 'after', checkpoint(after))
        object.__setattr__(self, 'through', checkpoint(through))
        require(type(events) in (list, tuple))
        require(len(events) <= 64, 'limit_exceeded')
        copied = tuple(event(x) for x in events)
        require(sum(len(encode_event(x)) for x in copied) <= 1048576, 'limit_exceeded')
        object.__setattr__(self, 'events', copied)


@dataclass(frozen=True, init=False)
class PageVerification:
    after: Checkpoint
    reached_terminal: bool
    resolved: tuple[EventReference, ...]
    unresolved: tuple[EventReference, ...]
    prior_global_uniqueness: str
    prior_membership: str

    def __init__(self, after: Checkpoint, reached_terminal: bool,
                 resolved: list[EventReference] | tuple[EventReference, ...],
                 unresolved: list[EventReference] | tuple[EventReference, ...],
                 prior_global_uniqueness: str = 'not_verified', prior_membership: str = 'not_verified') -> None:
        object.__setattr__(self, 'after', checkpoint(after))
        require(type(reached_terminal) is bool)
        require(type(resolved) in (list, tuple) and type(unresolved) in (list, tuple))
        require(len(resolved) + len(unresolved) <= 1024, 'limit_exceeded')
        groups = (tuple(reference(x) for x in resolved), tuple(reference(x) for x in unresolved))
        require(type(prior_global_uniqueness) is str and prior_global_uniqueness == 'not_verified')
        require(type(prior_membership) is str and prior_membership == 'not_verified')
        ids: dict[str, tuple[EventReference, int]] = {}
        seqs: dict[int, tuple[EventReference, int]] = {}
        for group, refs in enumerate(groups):
            for ref in refs:
                require(ref.chain_id == self.after.chain_id and 1 <= ref.sequence < self.after.sequence, 'inconsistent_reference')
                first, second = ids.get(ref.event_id), seqs.get(ref.sequence)
                if first is not None or second is not None:
                    require(first == second == (ref, group), 'inconsistent_reference')
                    raise LedgerError('duplicate')
                ids[ref.event_id] = (ref, group); seqs[ref.sequence] = (ref, group)
        object.__setattr__(self, 'reached_terminal', reached_terminal)
        object.__setattr__(self, 'resolved', groups[0])
        object.__setattr__(self, 'unresolved', groups[1])
        object.__setattr__(self, 'prior_global_uniqueness', prior_global_uniqueness)
        object.__setattr__(self, 'prior_membership', prior_membership)


@dataclass(frozen=True)
class Reconciliation:
    status: ReconciliationStatus
    head: Checkpoint
    observed: EventReference | None = None

    def __post_init__(self) -> None:
        require(type(self.status) is ReconciliationStatus)
        object.__setattr__(self, 'head', checkpoint(self.head))
        if self.observed is not None:
            object.__setattr__(self, 'observed', reference(self.observed))
        require(self.status is not ReconciliationStatus.FOUND_EXACT or self.observed is not None)
        require(self.status not in (ReconciliationStatus.ABSENT_AT_UNCHANGED_HEAD, ReconciliationStatus.BASE_NOT_COVERED) or self.observed is None)
        if self.observed is not None:
            require(self.observed.chain_id == self.head.chain_id and 1 <= self.observed.sequence <= self.head.sequence, 'inconsistent_reference')
            require(self.observed.sequence != self.head.sequence or self.observed.digest == self.head.head_hash, 'inconsistent_reference')


def encode_checkpoint(value: Checkpoint) -> bytes:
    value = checkpoint(value)
    return json.dumps({'domain': 'equity-feature.agent-checkpoint', 'schema_version': '1',
                       'canonicalization': 'agent-checkpoint-json-v1', 'chain_id': value.chain_id,
                       'sequence': value.sequence, 'head_hash': value.head_hash},
                      sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode('ascii')


def _pairs(items: list[tuple[str, object]]) -> dict[str, object]:
    out: dict[str, object] = {}
    for key, value in items:
        require(key not in out)
        out[key] = value
    return out


def decode_checkpoint(content: bytes) -> Checkpoint:
    require(type(content) is bytes)
    require(len(content) <= 1024, 'limit_exceeded')
    try:
        obj = json.loads(content.decode('ascii'), object_pairs_hook=_pairs)
    except (ValueError, UnicodeError, RecursionError) as exc:
        if isinstance(exc, LedgerError):
            raise
        raise LedgerError() from exc
    require(type(obj) is dict and set(obj) == {'domain', 'schema_version', 'canonicalization', 'chain_id', 'sequence', 'head_hash'})
    require(obj['domain'] == 'equity-feature.agent-checkpoint')
    require(obj['schema_version'] == '1' and obj['canonicalization'] == 'agent-checkpoint-json-v1', 'unsupported_version')
    value = Checkpoint(obj['chain_id'], obj['sequence'], obj['head_hash'])
    require(encode_checkpoint(value) == content)
    return value
