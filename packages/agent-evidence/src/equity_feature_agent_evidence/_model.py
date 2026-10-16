"""Bounded immutable declarations, without authentication or execution authority."""
from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re
from typing import Callable, TypeAlias, TypeVar
from equity_feature_contracts import AvailabilitySpec
from equity_feature_evidence import ContentFingerprint, InputFingerprint

MAX_EVENT_BYTES = 16384
MAX_EVENT_NODES = 4096
MAX_EVENT_DEPTH = 12
I64_MIN = -(2**63)
I64_MAX = 2**63 - 1
GENESIS = '0' * 64
DOMAIN = 'equity-feature.agent-event'
SCHEMA_VERSION = '1'
CANONICALIZATION = 'agent-event-json-v1'
_CODES = ('invalid_schema', 'unsupported_version', 'duplicate', 'limit_exceeded',
          'invalid_reference', 'inconsistent_reference', 'inconsistent_content')


class AgentEvidenceError(ValueError):
    """Fixed payload-free error; code is a closed public string."""
    def __init__(self, code: str = 'invalid_schema') -> None:
        if type(code) is not str or code not in _CODES:
            code = 'invalid_schema'
        self.code = code
        super().__init__('Agent evidence rejected: ' + code)


def require(condition: bool, code: str = 'invalid_schema') -> None:
    if not condition:
        raise AgentEvidenceError(code)


class ActorKind(str, Enum):
    HUMAN = 'human'
    SOFTWARE = 'software'
    SYSTEM = 'system'
    UNKNOWN = 'unknown'


class EventKind(str, Enum):
    REQUEST = 'request'
    MODEL_DECLARATION = 'model_declaration'
    TOOL_CALL = 'tool_call'
    TOOL_RESULT = 'tool_result'
    FEATURE_READ = 'feature_read'
    DECISION = 'decision'
    HUMAN_REVIEW = 'human_review'
    CANCELLATION = 'cancellation'
    ERROR = 'error'
    CORRECTION = 'correction'


class DisclosureState(str, Enum):
    RETAINED_COMPLETE = 'retained_complete'
    TRUNCATED = 'truncated'
    REDACTED = 'redacted'
    NOT_SUPPLIED = 'not_supplied'
    UNKNOWN = 'unknown'


class ModelIdentityState(str, Enum):
    DECLARED = 'declared'
    REDACTED = 'redacted'
    NOT_SUPPLIED = 'not_supplied'
    UNKNOWN = 'unknown'


class PayloadKind(str, Enum):
    TOOL_RESULT = 'tool_result'
    DIAGNOSTIC_REPORT = 'diagnostic_report'
    EXPLANATION = 'explanation'
    ARTIFACT = 'artifact'
    EXECUTION_RECEIPT = 'execution_receipt'


class ToolOutcome(str, Enum):
    SUCCEEDED = 'succeeded'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    UNKNOWN = 'unknown'


class DecisionAction(str, Enum):
    OBSERVE = 'observe'
    DEFER = 'defer'
    REJECT = 'reject'
    ADMIT = 'admit'


class ReviewVerdict(str, Enum):
    APPROVED = 'approved'
    DENIED = 'denied'
    UNKNOWN = 'unknown'


class CancellationReason(str, Enum):
    REQUESTED = 'requested'
    DEADLINE = 'deadline'
    SHUTDOWN = 'shutdown'
    UNKNOWN = 'unknown'


class EventErrorCode(str, Enum):
    INVALID_INPUT = 'invalid_input'
    UNAUTHORIZED = 'unauthorized'
    UNAVAILABLE = 'unavailable'
    FAILED = 'failed'
    CANCELLED = 'cancelled'
    UNKNOWN = 'unknown'


class CorrectionOperation(str, Enum):
    AMEND = 'amend'
    REVOKE = 'revoke'


class PayloadCheckStatus(str, Enum):
    MATCHED_RETAINED = 'matched_retained'
    UNAVAILABLE = 'unavailable'


def label(value: str, *, empty: bool = False) -> None:
    require(type(value) is str)
    require(len(value) <= 256, 'limit_exceeded')
    require(empty or bool(value.strip()))
    require(not any(ord(c) < 32 or 127 <= ord(c) <= 159 or 0xD800 <= ord(c) <= 0xDFFF for c in value))
    require(len(value.encode('utf-8')) <= 1024, 'limit_exceeded')


def optional_label(value: str | None) -> None:
    if value is not None:
        label(value)


def integer(value: int, *, minimum: int = I64_MIN) -> None:
    require(type(value) is int)
    require(minimum <= value <= I64_MAX)


def identity(value: str) -> None:
    require(type(value) is str)
    require(len(value) <= 128, 'limit_exceeded')
    require(re.fullmatch(r'[A-Za-z][A-Za-z0-9_.-]{0,62}:[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', value) is not None)


def digest(value: str) -> None:
    require(type(value) is str)
    require(re.fullmatch('[0-9a-f]{64}', value) is not None)


T = TypeVar('T')


def sequence(value: list[T] | tuple[T, ...], member: type[T], limit: int,
             clone: Callable[[T], T]) -> tuple[T, ...]:
    require(type(value) in (list, tuple))
    require(len(value) <= limit, 'limit_exceeded')
    result = []
    for item in value:
        require(type(item) is member)
        result.append(clone(item))
    return tuple(result)


@dataclass(frozen=True)
class ActorDeclaration:
    actor_id: str | None
    kind: ActorKind

    def __post_init__(self) -> None:
        optional_label(self.actor_id); require(type(self.kind) is ActorKind)
        require(self.kind is not ActorKind.UNKNOWN or self.actor_id is None)


@dataclass(frozen=True)
class TimeDeclaration:
    at_ns: int | None
    clock_source: str | None
    uncertainty_ns: int | None

    def __post_init__(self) -> None:
        if self.at_ns is not None: integer(self.at_ns)
        optional_label(self.clock_source)
        if self.uncertainty_ns is not None: integer(self.uncertainty_ns, minimum=0)
        require(self.at_ns is not None or (self.clock_source is None and self.uncertainty_ns is None))


def copy_availability(value: AvailabilitySpec) -> AvailabilitySpec:
    require(type(value) is AvailabilitySpec)
    integer(value.market_cutoff_ns); integer(value.knowledge_cutoff_ns); integer(value.evaluation_ns)
    require(type(value.mode) is str and value.mode in ('known_at', 'reconstruction'))
    optional_label(value.reconstruction_reason)
    if value.mode == 'known_at':
        require(value.market_cutoff_ns <= value.evaluation_ns and value.knowledge_cutoff_ns <= value.evaluation_ns and value.reconstruction_reason is None)
    else:
        require(value.reconstruction_reason is not None)
    return AvailabilitySpec(value.market_cutoff_ns, value.knowledge_cutoff_ns, value.evaluation_ns, value.mode, value.reconstruction_reason)


@dataclass(frozen=True)
class DecisionContext:
    namespace: str
    session_id: str
    availability: AvailabilitySpec

    def __post_init__(self) -> None:
        label(self.namespace); label(self.session_id)
        object.__setattr__(self, 'availability', copy_availability(self.availability))


def copy_context(value: DecisionContext | None) -> DecisionContext | None:
    if value is None: return None
    require(type(value) is DecisionContext)
    return DecisionContext(value.namespace, value.session_id, value.availability)


@dataclass(frozen=True)
class EventReference:
    chain_id: str
    sequence: int
    event_id: str
    kind: EventKind
    digest: str

    def __post_init__(self) -> None:
        identity(self.chain_id); integer(self.sequence, minimum=1); identity(self.event_id)
        require(type(self.kind) is EventKind); digest(self.digest)


def copy_reference(value: EventReference, roles: tuple[EventKind, ...] = ()) -> EventReference:
    require(type(value) is EventReference)
    result = EventReference(value.chain_id, value.sequence, value.event_id, value.kind, value.digest)
    require(not roles or result.kind in roles, 'invalid_reference')
    return result


@dataclass(frozen=True)
class Argument:
    name: str
    value: None | bool | int | str

    def __post_init__(self) -> None:
        require(type(self.name) is str)
        require(len(self.name) <= 64, 'limit_exceeded')
        require(re.fullmatch('[a-z][a-z0-9_]{0,63}', self.name) is not None)
        require(type(self.value) in (type(None), bool, int, str))
        if type(self.value) is int: integer(self.value)
        elif type(self.value) is str: label(self.value, empty=True)


@dataclass(frozen=True, init=False)
class ArgumentSet:
    state: DisclosureState
    total_count: int | None
    entries: tuple[Argument, ...]

    def __init__(self, state: DisclosureState, total_count: int | None,
                 entries: list[Argument] | tuple[Argument, ...]) -> None:
        require(type(state) is DisclosureState)
        if total_count is not None: integer(total_count, minimum=0)
        copied = sequence(entries, Argument, 16, lambda x: Argument(x.name, x.value))
        require(len({x.name for x in copied}) == len(copied), 'duplicate')
        if state is DisclosureState.RETAINED_COMPLETE: require(total_count == len(copied))
        elif state is DisclosureState.TRUNCATED: require(total_count is not None and total_count > len(copied))
        elif state is DisclosureState.REDACTED: require(not copied)
        else: require(not copied and total_count is None)
        object.__setattr__(self, 'state', state); object.__setattr__(self, 'total_count', total_count)
        object.__setattr__(self, 'entries', copied)


@dataclass(frozen=True)
class PayloadReference:
    kind: PayloadKind
    digest: str | None
    retained_bytes: int
    full_bytes: int | None
    state: DisclosureState

    def __post_init__(self) -> None:
        require(type(self.kind) is PayloadKind)
        if self.digest is not None: digest(self.digest)
        integer(self.retained_bytes, minimum=0)
        if self.full_bytes is not None: integer(self.full_bytes, minimum=0)
        require(type(self.state) is DisclosureState)
        if self.state is DisclosureState.RETAINED_COMPLETE:
            require(self.digest is not None and self.full_bytes == self.retained_bytes)
        elif self.state is DisclosureState.TRUNCATED:
            require(self.digest is not None and self.full_bytes is not None and self.full_bytes > self.retained_bytes)
        else:
            require(self.digest is None and self.retained_bytes == 0)
            if self.state is not DisclosureState.REDACTED: require(self.full_bytes is None)


def copy_payload(value: PayloadReference) -> PayloadReference:
    require(type(value) is PayloadReference)
    return PayloadReference(value.kind, value.digest, value.retained_bytes, value.full_bytes, value.state)


def copy_fingerprint(value: ContentFingerprint, domain: str) -> ContentFingerprint:
    require(type(value) is ContentFingerprint)
    require(type(value.domain) is str and value.domain == domain)
    digest(value.digest); integer(value.byte_length, minimum=0)
    require(type(value.schema_version) is str)
    require(value.schema_version == '1', 'unsupported_version')
    require(type(value.canonicalization) is str)
    require(value.canonicalization == 'typed-json-v1', 'unsupported_version')
    require(type(value.algorithm) is str)
    require(value.algorithm == 'sha256', 'unsupported_version')
    return ContentFingerprint(value.domain, value.digest, value.byte_length, value.schema_version, value.canonicalization, value.algorithm)


@dataclass(frozen=True)
class RequestSubject:
    request_key: str
    objective: str
    context: DecisionContext | None

    def __post_init__(self) -> None:
        label(self.request_key); label(self.objective)
        object.__setattr__(self, 'context', copy_context(self.context))


@dataclass(frozen=True)
class ModelSubject:
    provider: str | None
    model: str | None
    version: str | None
    identity_state: ModelIdentityState

    def __post_init__(self) -> None:
        optional_label(self.provider); optional_label(self.model); optional_label(self.version)
        require(type(self.identity_state) is ModelIdentityState)
        if self.identity_state is ModelIdentityState.DECLARED: require(self.model is not None)
        else: require(self.provider is None and self.model is None and self.version is None)


@dataclass(frozen=True)
class ToolCallSubject:
    request: EventReference
    tool_name: str
    tool_version: str | None
    arguments: ArgumentSet

    def __post_init__(self) -> None:
        object.__setattr__(self, 'request', copy_reference(self.request, (EventKind.REQUEST,)))
        label(self.tool_name); optional_label(self.tool_version)
        require(type(self.arguments) is ArgumentSet)
        object.__setattr__(self, 'arguments', ArgumentSet(self.arguments.state, self.arguments.total_count, self.arguments.entries))


@dataclass(frozen=True)
class ToolResultSubject:
    call: EventReference
    outcome: ToolOutcome
    payload: PayloadReference

    def __post_init__(self) -> None:
        object.__setattr__(self, 'call', copy_reference(self.call, (EventKind.TOOL_CALL,)))
        require(type(self.outcome) is ToolOutcome)
        object.__setattr__(self, 'payload', copy_payload(self.payload))


@dataclass(frozen=True, init=False)
class FeatureReadSubject:
    result: EventReference
    receipt: PayloadReference
    configuration: ContentFingerprint | None
    inputs: tuple[InputFingerprint, ...]
    output: ContentFingerprint | None
    feature_ids: tuple[str, ...]
    context: DecisionContext | None

    def __init__(self, result: EventReference, receipt: PayloadReference,
                 configuration: ContentFingerprint | None,
                 inputs: list[InputFingerprint] | tuple[InputFingerprint, ...],
                 output: ContentFingerprint | None, feature_ids: list[str] | tuple[str, ...],
                 context: DecisionContext | None) -> None:
        result = copy_reference(result, (EventKind.TOOL_RESULT,)); receipt = copy_payload(receipt)
        require(receipt.kind is PayloadKind.EXECUTION_RECEIPT)
        if configuration is not None: configuration = copy_fingerprint(configuration, 'configuration')
        def copy_input(x: InputFingerprint) -> InputFingerprint:
            label(x.role); label(x.input_id)
            return InputFingerprint(x.role, x.input_id, copy_fingerprint(x.content, 'canonical_batch'))
        copied = sequence(inputs, InputFingerprint, 16, copy_input)
        require(len({x.role for x in copied}) == len(copied) and len({x.input_id for x in copied}) == len(copied), 'duplicate')
        if output is not None: output = copy_fingerprint(output, 'feature_result')
        def copy_feature(feature: str) -> str:
            label(feature); return feature
        features = sequence(feature_ids, str, 32, copy_feature)
        require(len(set(features)) == len(features), 'duplicate')
        context = copy_context(context)
        object.__setattr__(self, 'result', result); object.__setattr__(self, 'receipt', receipt)
        object.__setattr__(self, 'configuration', configuration); object.__setattr__(self, 'inputs', tuple(copied))
        object.__setattr__(self, 'output', output); object.__setattr__(self, 'feature_ids', features)
        object.__setattr__(self, 'context', context)


@dataclass(frozen=True, init=False)
class DecisionSubject:
    request: EventReference
    feature_reads: tuple[EventReference, ...]
    action: DecisionAction
    reason_code: str

    def __init__(self, request: EventReference, feature_reads: list[EventReference] | tuple[EventReference, ...],
                 action: DecisionAction, reason_code: str) -> None:
        request = copy_reference(request, (EventKind.REQUEST,))
        refs = sequence(feature_reads, EventReference, 16, lambda x: copy_reference(x, (EventKind.FEATURE_READ,)))
        require(len({x.event_id for x in refs}) == len(refs), 'duplicate')
        require(type(action) is DecisionAction); label(reason_code)
        object.__setattr__(self, 'request', request); object.__setattr__(self, 'feature_reads', refs)
        object.__setattr__(self, 'action', action); object.__setattr__(self, 'reason_code', reason_code)


@dataclass(frozen=True)
class HumanReviewSubject:
    decision: EventReference
    verdict: ReviewVerdict
    review_key: str

    def __post_init__(self) -> None:
        object.__setattr__(self, 'decision', copy_reference(self.decision, (EventKind.DECISION,)))
        require(type(self.verdict) is ReviewVerdict); label(self.review_key)


@dataclass(frozen=True)
class CancellationSubject:
    target: EventReference
    reason: CancellationReason

    def __post_init__(self) -> None:
        object.__setattr__(self, 'target', copy_reference(self.target, (EventKind.REQUEST, EventKind.TOOL_CALL, EventKind.DECISION)))
        require(type(self.reason) is CancellationReason)


@dataclass(frozen=True)
class ErrorSubject:
    target: EventReference | None
    code: EventErrorCode

    def __post_init__(self) -> None:
        if self.target is not None: object.__setattr__(self, 'target', copy_reference(self.target))
        require(type(self.code) is EventErrorCode)


@dataclass(frozen=True)
class CorrectionSubject:
    target: EventReference
    operation: CorrectionOperation
    replacement: EventReference | None
    reason_code: str

    def __post_init__(self) -> None:
        object.__setattr__(self, 'target', copy_reference(self.target))
        require(self.target.kind is not EventKind.CORRECTION, 'invalid_reference')
        require(type(self.operation) is CorrectionOperation)
        if self.replacement is not None: object.__setattr__(self, 'replacement', copy_reference(self.replacement))
        label(self.reason_code)
        if self.operation is CorrectionOperation.AMEND:
            require(self.replacement is not None, 'invalid_reference')
            assert self.replacement is not None
            require(self.replacement.kind is self.target.kind and self.replacement.event_id != self.target.event_id, 'invalid_reference')
        else: require(self.replacement is None, 'invalid_reference')


Subject: TypeAlias = RequestSubject | ModelSubject | ToolCallSubject | ToolResultSubject | FeatureReadSubject | DecisionSubject | HumanReviewSubject | CancellationSubject | ErrorSubject | CorrectionSubject
_KINDS = {RequestSubject: EventKind.REQUEST, ModelSubject: EventKind.MODEL_DECLARATION,
          ToolCallSubject: EventKind.TOOL_CALL, ToolResultSubject: EventKind.TOOL_RESULT,
          FeatureReadSubject: EventKind.FEATURE_READ, DecisionSubject: EventKind.DECISION,
          HumanReviewSubject: EventKind.HUMAN_REVIEW, CancellationSubject: EventKind.CANCELLATION,
          ErrorSubject: EventKind.ERROR, CorrectionSubject: EventKind.CORRECTION}


def copy_subject(value: Subject) -> Subject:
    require(type(value) in _KINDS)
    if isinstance(value, RequestSubject): return RequestSubject(value.request_key, value.objective, value.context)
    if isinstance(value, ModelSubject): return ModelSubject(value.provider, value.model, value.version, value.identity_state)
    if isinstance(value, ToolCallSubject): return ToolCallSubject(value.request, value.tool_name, value.tool_version, value.arguments)
    if isinstance(value, ToolResultSubject): return ToolResultSubject(value.call, value.outcome, value.payload)
    if isinstance(value, FeatureReadSubject): return FeatureReadSubject(value.result, value.receipt, value.configuration, value.inputs, value.output, value.feature_ids, value.context)
    if isinstance(value, DecisionSubject): return DecisionSubject(value.request, value.feature_reads, value.action, value.reason_code)
    if isinstance(value, HumanReviewSubject): return HumanReviewSubject(value.decision, value.verdict, value.review_key)
    if isinstance(value, CancellationSubject): return CancellationSubject(value.target, value.reason)
    if isinstance(value, ErrorSubject): return ErrorSubject(value.target, value.code)
    assert isinstance(value, CorrectionSubject)
    return CorrectionSubject(value.target, value.operation, value.replacement, value.reason_code)


def references(value: Subject) -> tuple[EventReference, ...]:
    if isinstance(value, (RequestSubject, ModelSubject)): return ()
    if isinstance(value, ToolCallSubject): return (value.request,)
    if isinstance(value, ToolResultSubject): return (value.call,)
    if isinstance(value, FeatureReadSubject): return (value.result,)
    if isinstance(value, DecisionSubject): return (value.request, *value.feature_reads)
    if isinstance(value, HumanReviewSubject): return (value.decision,)
    if isinstance(value, CancellationSubject): return (value.target,)
    if isinstance(value, ErrorSubject): return () if value.target is None else (value.target,)
    return (value.target,) if value.replacement is None else (value.target, value.replacement)


@dataclass(frozen=True)
class EventRecord:
    chain_id: str
    sequence: int
    event_id: str
    actor: ActorDeclaration
    occurred: TimeDeclaration
    recorded: TimeDeclaration
    previous_hash: str
    subject: Subject

    def __post_init__(self) -> None:
        identity(self.chain_id); integer(self.sequence, minimum=1); identity(self.event_id)
        require(type(self.actor) is ActorDeclaration)
        object.__setattr__(self, 'actor', ActorDeclaration(self.actor.actor_id, self.actor.kind))
        for name, value in (('occurred', self.occurred), ('recorded', self.recorded)):
            require(type(value) is TimeDeclaration)
            object.__setattr__(self, name, TimeDeclaration(value.at_ns, value.clock_source, value.uncertainty_ns))
        digest(self.previous_hash)
        require(self.sequence != 1 or self.previous_hash == GENESIS, 'invalid_reference')
        object.__setattr__(self, 'subject', copy_subject(self.subject))
        refs = references(self.subject)
        require(len(refs) <= 16, 'limit_exceeded')
        require(len({x.event_id for x in refs}) == len(refs), 'duplicate')
        for ref in refs:
            require(ref.chain_id == self.chain_id and ref.sequence < self.sequence and ref.event_id != self.event_id, 'invalid_reference')
        from ._codec import encode_validated
        encode_validated(self)

    @property
    def kind(self) -> EventKind:
        require(type(self.subject) in _KINDS)
        return _KINDS[type(self.subject)]


def copy_event(value: EventRecord) -> EventRecord:
    require(type(value) is EventRecord)
    return EventRecord(value.chain_id, value.sequence, value.event_id, value.actor, value.occurred, value.recorded, value.previous_hash, value.subject)


@dataclass(frozen=True)
class PayloadCheck:
    status: PayloadCheckStatus
    disclosure: DisclosureState
    retained_bytes: int

    def __post_init__(self) -> None:
        require(type(self.status) is PayloadCheckStatus); require(type(self.disclosure) is DisclosureState)
        integer(self.retained_bytes, minimum=0)
        if self.status is PayloadCheckStatus.UNAVAILABLE: require(self.retained_bytes == 0)
        else: require(self.disclosure in (DisclosureState.RETAINED_COMPLETE, DisclosureState.TRUNCATED))

    @property
    def retained_matched(self) -> bool:
        return self.status is PayloadCheckStatus.MATCHED_RETAINED


@dataclass(frozen=True, init=False)
class ReferenceCheck:
    verified: tuple[EventReference, ...]
    unresolved: tuple[EventReference, ...]

    def __init__(self, verified: list[EventReference] | tuple[EventReference, ...],
                 unresolved: list[EventReference] | tuple[EventReference, ...]) -> None:
        good = sequence(verified, EventReference, 16, copy_reference)
        missing = sequence(unresolved, EventReference, 16, copy_reference)
        require(len(good) + len(missing) <= 16, 'limit_exceeded')
        require(len({x.event_id for x in (*good, *missing)}) == len(good) + len(missing), 'duplicate')
        object.__setattr__(self, 'verified', good); object.__setattr__(self, 'unresolved', missing)

    @property
    def fully_resolved(self) -> bool:
        return not self.unresolved
