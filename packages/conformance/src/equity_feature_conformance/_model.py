"""Owned scalar assertions and observations; test records carry no authority."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import TypeAlias
from equity_feature_evidence import ContentFingerprint

KINDS = ('adjustment', 'declared_context', 'freshness', 'knowledge_time',
         'market_time', 'membership', 'revision')
REASONS = ('market_bound', 'missing_market_fact', 'late_knowledge', 'missing_knowledge',
    'market_cutoff_mismatch', 'knowledge_cutoff_mismatch', 'evaluation_mismatch',
    'reconstruction_context', 'missing_context', 'future_effective_query',
    'membership_absent', 'membership_scope_mismatch', 'ambiguous_membership',
    'missing_reference', 'incomplete_reference', 'incomplete_projection',
    'historical_proof_unknown', 'missing_membership_text', 'revision_mismatch',
    'missing_revision_identity', 'missing_effective_start', 'outside_effective_interval',
    'adjustment_mismatch', 'missing_adjustment', 'future_observation',
    'stale_observation', 'missing_observation', 'missing_session')


class ConformanceError(ValueError):
    """Fixed classification only; no caller data or underlying exception text."""
    def __init__(self, code: str = 'invalid_schema') -> None:
        if type(code) is not str or code not in ('invalid_schema','unsupported_version',
                'inconsistent_binding','duplicate','limit_exceeded'):
            code = 'invalid_schema'
        self.code = code
        super().__init__('Conformance rejected: ' + code)


def require(ok: bool, code: str = 'invalid_schema') -> None:
    if not ok: raise ConformanceError(code)


def label(value: str) -> None:
    require(type(value) is str)
    require(len(value) <= 128, 'limit_exceeded')
    require(bool(value.strip()) and not any(ord(c) < 32 or 127 <= ord(c) <= 159
                                          or 0xD800 <= ord(c) <= 0xDFFF for c in value))
    require(len(value.encode('utf-8')) <= 512, 'limit_exceeded')


def number(value: int, minimum: int, maximum: int, *, cardinal: bool = False) -> None:
    require(type(value) is int and value >= minimum)
    require(value <= maximum, 'limit_exceeded' if cardinal else 'invalid_schema')


def fingerprint(value: ContentFingerprint | None, *, result_only: bool = False) -> ContentFingerprint | None:
    if value is None: return None
    require(type(value) is ContentFingerprint)
    require(type(value.schema_version) is str and value.schema_version == '1', 'unsupported_version')
    require(type(value.algorithm) is str and value.algorithm == 'sha256', 'unsupported_version')
    require(type(value.canonicalization) is str and value.canonicalization == 'typed-json-v1', 'unsupported_version')
    require(type(value.domain) is str and value.domain in ('canonical_batch','feature_result','configuration'), 'inconsistent_binding')
    if result_only: require(value.domain == 'feature_result', 'inconsistent_binding')
    require(type(value.digest) is str and len(value.digest) == 64 and all(c in '0123456789abcdef' for c in value.digest))
    number(value.byte_length, 0, 2**63-1)
    return ContentFingerprint(domain=value.domain, digest=value.digest, byte_length=value.byte_length,
        algorithm=value.algorithm, canonicalization=value.canonicalization, schema_version=value.schema_version)


@dataclass(frozen=True)
class ContextSnapshot:
    namespace: str
    instrument_id: str
    session_id: str
    market_cutoff_ns: int
    knowledge_cutoff_ns: int
    evaluation_ns: int
    def __post_init__(self) -> None:
        for s in (self.namespace,self.instrument_id,self.session_id): label(s)
        for n in (self.market_cutoff_ns,self.knowledge_cutoff_ns,self.evaluation_ns): number(n,-2**63,2**63-1)


@dataclass(frozen=True)
class PolicySnapshot:
    policy_id: str
    mode: str
    unknown_action: str
    def __post_init__(self) -> None:
        label(self.policy_id)
        require(type(self.mode) is str and self.mode in ('advisory','strict'))
        require(type(self.unknown_action) is str and self.unknown_action in ('allow','deny'))


def copy_context(v: ContextSnapshot) -> ContextSnapshot:
    require(type(v) is ContextSnapshot)
    return ContextSnapshot(v.namespace,v.instrument_id,v.session_id,v.market_cutoff_ns,v.knowledge_cutoff_ns,v.evaluation_ns)


def copy_policy(v: PolicySnapshot) -> PolicySnapshot:
    require(type(v) is PolicySnapshot)
    return PolicySnapshot(v.policy_id,v.mode,v.unknown_action)


@dataclass(frozen=True)
class FindingSnapshot:
    check_id: str
    subject_id: str
    kind: str
    content: ContentFingerprint | None
    status: str
    severity: str
    reasons: tuple[str, ...]
    assessed: bool
    unknown_prerequisites: int
    age_ns: int | None
    def __post_init__(self) -> None:
        label(self.check_id); label(self.subject_id)
        require(type(self.kind) is str and self.kind in KINDS)
        require(type(self.status) is str and self.status in ('passed','failed','unknown'))
        require(type(self.severity) is str and self.severity in ('info','error','warning'))
        require(type(self.assessed) is bool)
        number(self.unknown_prerequisites,0,8,cardinal=True)
        if self.age_ns is not None: number(self.age_ns,0,2**64-1)
        require(type(self.reasons) in (tuple,list)); require(len(self.reasons) <= 32,'limit_exceeded')
        require(all(type(v) is str and v in REASONS for v in self.reasons))
        require(len(set(self.reasons)) == len(self.reasons),'duplicate')
        require(tuple(self.reasons) == tuple(sorted(self.reasons)))
        object.__setattr__(self,'reasons',tuple(self.reasons))
        object.__setattr__(self,'content',fingerprint(self.content))


def copy_finding(v: FindingSnapshot) -> FindingSnapshot:
    require(type(v) is FindingSnapshot)
    return FindingSnapshot(v.check_id,v.subject_id,v.kind,v.content,v.status,v.severity,
        v.reasons,v.assessed,v.unknown_prerequisites,v.age_ns)


@dataclass(frozen=True)
class DiagnosticSnapshot:
    context: ContextSnapshot
    policy: PolicySnapshot
    findings: tuple[FindingSnapshot, ...]
    requested_count: int
    passed_count: int
    failed_count: int
    unknown_count: int
    assessed_count: int
    unknown_prerequisite_count: int
    not_requested: tuple[str, ...]
    admission: str
    source_authenticated: bool
    historical_acquisition_verified: bool
    schema_version: str = '1'
    def __post_init__(self) -> None:
        require(type(self.schema_version) is str and self.schema_version == '1','unsupported_version')
        require(type(self.findings) in (tuple,list)); require(len(self.findings) <= 32,'limit_exceeded')
        require(type(self.not_requested) in (tuple,list)); require(len(self.not_requested) <= 7,'limit_exceeded')
        require(all(type(v) is str and v in KINDS for v in self.not_requested))
        require(len(set(self.not_requested)) == len(self.not_requested),'duplicate')
        require(tuple(self.not_requested) == tuple(k for k in KINDS if k in self.not_requested))
        for n in (self.requested_count,self.passed_count,self.failed_count,self.unknown_count,self.assessed_count):
            number(n,0,32,cardinal=True)
        number(self.unknown_prerequisite_count,0,256,cardinal=True)
        require(type(self.admission) is str and self.admission in ('admitted','denied','not_applied'))
        require(type(self.source_authenticated) is bool and type(self.historical_acquisition_verified) is bool)
        fs=tuple(copy_finding(v) for v in self.findings)
        require(len({v.check_id for v in fs}) == len(fs),'duplicate')
        object.__setattr__(self,'context',copy_context(self.context))
        object.__setattr__(self,'policy',copy_policy(self.policy))
        object.__setattr__(self,'findings',fs)
        object.__setattr__(self,'not_requested',tuple(self.not_requested))


def copy_snapshot(v: DiagnosticSnapshot) -> DiagnosticSnapshot:
    require(type(v) is DiagnosticSnapshot)
    return DiagnosticSnapshot(v.context,v.policy,v.findings,v.requested_count,v.passed_count,
        v.failed_count,v.unknown_count,v.assessed_count,v.unknown_prerequisite_count,
        v.not_requested,v.admission,v.source_authenticated,v.historical_acquisition_verified,v.schema_version)


def differences(a: DiagnosticSnapshot, b: DiagnosticSnapshot) -> tuple[str, ...]:
    return tuple(n for n,bad in (
        ('context',a.context!=b.context),('policy',a.policy!=b.policy),
        ('findings',a.findings!=b.findings),('requested_count',a.requested_count!=b.requested_count),
        ('passed_count',a.passed_count!=b.passed_count),('failed_count',a.failed_count!=b.failed_count),
        ('unknown_count',a.unknown_count!=b.unknown_count),('assessed_count',a.assessed_count!=b.assessed_count),
        ('unknown_prerequisite_count',a.unknown_prerequisite_count!=b.unknown_prerequisite_count),
        ('not_requested',a.not_requested!=b.not_requested),('admission',a.admission!=b.admission),
        ('source_authenticated',a.source_authenticated!=b.source_authenticated),
        ('historical_acquisition_verified',a.historical_acquisition_verified!=b.historical_acquisition_verified),
        ('schema_version',a.schema_version!=b.schema_version)) if bad)


@dataclass(frozen=True)
class DiagnosticOutcome:
    case_id: str
    expected: DiagnosticSnapshot
    observed: DiagnosticSnapshot
    matched: bool = field(init=False)
    mismatch_fields: tuple[str, ...] = field(init=False)
    remaining_unknown: bool = field(init=False)
    def __post_init__(self) -> None:
        label(self.case_id)
        a,b=copy_snapshot(self.expected),copy_snapshot(self.observed)
        ds=differences(a,b)
        object.__setattr__(self,'expected',a); object.__setattr__(self,'observed',b)
        object.__setattr__(self,'matched',not ds); object.__setattr__(self,'mismatch_fields',ds)
        object.__setattr__(self,'remaining_unknown',b.unknown_prerequisite_count>0)


@dataclass(frozen=True)
class ContentOutcome:
    case_id: str
    before: ContentFingerprint | None
    after: ContentFingerprint | None
    expected_relation: str
    observed_relation: str = field(init=False)
    matched: bool = field(init=False)
    remaining_unknown: bool = field(init=False)
    def __post_init__(self) -> None:
        label(self.case_id)
        require(type(self.expected_relation) is str and self.expected_relation in ('equal','different','unknown'))
        a,b=fingerprint(self.before,result_only=True),fingerprint(self.after,result_only=True)
        observed='unknown' if a is None or b is None else ('equal' if a==b else 'different')
        object.__setattr__(self,'before',a); object.__setattr__(self,'after',b)
        object.__setattr__(self,'observed_relation',observed)
        object.__setattr__(self,'matched',self.expected_relation==observed)
        object.__setattr__(self,'remaining_unknown',observed=='unknown')


Outcome: TypeAlias = DiagnosticOutcome | ContentOutcome


@dataclass(frozen=True)
class SuiteSummary:
    outcomes: tuple[Outcome, ...]
    total: int = field(init=False)
    matched_count: int = field(init=False)
    mismatched_count: int = field(init=False)
    unknown_cases: int = field(init=False)
    all_matched: bool = field(init=False)
    def __post_init__(self) -> None:
        require(type(self.outcomes) in (tuple,list)); require(1 <= len(self.outcomes) <= 32,'limit_exceeded')
        require(all(type(v) in (DiagnosticOutcome,ContentOutcome) for v in self.outcomes))
        total=0
        for v in self.outcomes:
            if type(v) is DiagnosticOutcome:
                require(type(v.observed) is DiagnosticSnapshot and type(v.observed.findings) in (tuple,list))
                total+=len(v.observed.findings)
        require(total <= 256,'limit_exceeded')
        copied: list[Outcome] = []
        for v in self.outcomes:
            if isinstance(v,DiagnosticOutcome): copied.append(DiagnosticOutcome(v.case_id,v.expected,v.observed))
            else: copied.append(ContentOutcome(v.case_id,v.before,v.after,v.expected_relation))
        require(len({v.case_id for v in copied}) == len(copied),'duplicate')
        object.__setattr__(self,'outcomes',tuple(copied)); object.__setattr__(self,'total',len(copied))
        matched=sum(v.matched for v in copied)
        object.__setattr__(self,'matched_count',matched)
        object.__setattr__(self,'mismatched_count',len(copied)-matched)
        object.__setattr__(self,'unknown_cases',sum(v.remaining_unknown for v in copied))
        object.__setattr__(self,'all_matched',matched==len(copied))
