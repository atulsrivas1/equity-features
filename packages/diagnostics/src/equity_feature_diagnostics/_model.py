"""Bounded immutable supplied declarations, without acquisition authority."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias
from equity_feature_contracts import inputs as i, policies as p, results as r, specs as s
from equity_feature_evidence import ContentFingerprint

KINDS = ('adjustment', 'declared_context', 'freshness', 'knowledge_time',
         'market_time', 'membership', 'revision')
MEMBERSHIPS = ('universe_membership', 'sector_membership')
REASONS = ('market_bound', 'missing_market_fact', 'late_knowledge', 'missing_knowledge',
    'market_cutoff_mismatch', 'knowledge_cutoff_mismatch', 'evaluation_mismatch',
    'reconstruction_context', 'missing_context', 'future_effective_query',
    'membership_absent', 'membership_scope_mismatch', 'ambiguous_membership',
    'missing_reference', 'incomplete_reference', 'incomplete_projection',
    'historical_proof_unknown', 'missing_membership_text', 'revision_mismatch',
    'missing_revision_identity', 'missing_effective_start', 'outside_effective_interval',
    'adjustment_mismatch', 'missing_adjustment', 'future_observation',
    'stale_observation', 'missing_observation', 'missing_session')


class DiagnosticsError(ValueError):
    """Fixed code only; no caller payload in the public message."""
    def __init__(self, code: str = 'invalid_schema') -> None:
        if type(code) is not str or code not in ('invalid_schema', 'unsupported_version',
                'inconsistent_binding', 'duplicate', 'limit_exceeded'):
            code = 'invalid_schema'
        self.code = code
        super().__init__('Diagnostics rejected: ' + code)


def require(ok: bool, code: str = 'invalid_schema') -> None:
    if not ok:
        raise DiagnosticsError(code)


def label(value: str) -> None:
    require(type(value) is str)
    require(bool(value.strip()))
    require(len(value) <= 128, 'limit_exceeded')
    require(not any(ord(c) < 32 or 127 <= ord(c) <= 159 or 0xD800 <= ord(c) <= 0xDFFF for c in value))
    require(len(value.encode('utf-8')) <= 512, 'limit_exceeded')


def integer(value: int, nonnegative: bool = False) -> None:
    require(type(value) is int and (0 if nonnegative else i.I64_MIN) <= value <= i.I64_MAX)


def optional_ns(value: int | None) -> None:
    if value is not None:
        integer(value)


def entity(value: r.EntityKey) -> None:
    require(type(value) is r.EntityKey)
    label(value.instrument_id); label(value.session_id)


def availability(value: s.AvailabilitySpec, causal: bool = False) -> None:
    require(type(value) is s.AvailabilitySpec)
    for n in (value.market_cutoff_ns, value.knowledge_cutoff_ns, value.evaluation_ns):
        integer(n)
    require(type(value.mode) is str and value.mode in ('known_at', 'reconstruction'), 'unsupported_version')
    if value.mode == 'known_at':
        require(value.market_cutoff_ns <= value.evaluation_ns and value.knowledge_cutoff_ns <= value.evaluation_ns)
        require(value.reconstruction_reason is None)
    else:
        require(not causal)
        require(type(value.reconstruction_reason) is str)
        assert value.reconstruction_reason is not None
        label(value.reconstruction_reason)


def session(value: s.SessionSpec) -> None:
    require(type(value) is s.SessionSpec)
    for text in (value.namespace, value.session_id, value.timezone_label): label(text)
    integer(value.open_ns); integer(value.close_ns); require(value.open_ns < value.close_ns)
    require(type(value.intervals) in (tuple, list))
    require(len(value.intervals) <= 128, 'limit_exceeded')
    names: set[str] = set()
    for v in value.intervals:
        require(type(v) is s.IntervalSpec); label(v.name); integer(v.start_ns); integer(v.end_ns)
        require(value.open_ns <= v.start_ns < v.end_ns <= value.close_ns)
        require(v.name not in names, 'duplicate'); names.add(v.name)
    for flag in (value.early_close, value.include_opening_auction, value.include_closing_auction): require(type(flag) is bool)
    optional_ns(value.scheduled_close_ns)
    if value.scheduled_close_ns is None:
        require(not value.early_close)
    else:
        require(value.scheduled_close_ns >= value.close_ns and value.early_close == (value.close_ns < value.scheduled_close_ns))


def action(value: p.ActionPolicy) -> None:
    require(type(value) is p.ActionPolicy)
    require(type(value.schema_version) is str and value.schema_version == '1', 'unsupported_version')
    require(type(value.adjustment) is i.AdjustmentSpec)
    a = value.adjustment
    for text in (a.basis, a.policy_version, a.action_snapshot, a.anchor,
                 value.representation, value.quantity_basis, value.dividend_convention): label(text)
    versions = {'raw': 'raw-v1', 'split': 'split-factors-v1', 'total_return': 'total-return-reinvest-v1'}
    require(a.basis in versions and a.policy_version == versions[a.basis], 'unsupported_version')
    require(a.basis == 'raw' or (a.action_snapshot != 'none' and a.anchor != 'none'))
    require(value.representation in ('apply_factors', 'caller_transformed'))
    require(value.quantity_basis in ('raw_shares', 'split_shares') and (a.basis != 'raw' or value.quantity_basis == 'raw_shares'))
    require(value.dividend_convention == ('supplied_reinvestment_factors' if a.basis == 'total_return' else 'none'))
    integer(value.anchor_ns)


def unit(value: i.PriceUnit) -> None:
    require(type(value) is i.PriceUnit); integer(value.scale, True)
    require(value.scale <= 18); label(value.currency)


def content(value: ContentFingerprint | None) -> None:
    if value is None: return
    require(type(value) is ContentFingerprint)
    require(type(value.schema_version) is str and value.schema_version == '1', 'unsupported_version')
    require(type(value.canonicalization) is str and value.canonicalization == 'typed-json-v1', 'unsupported_version')
    require(type(value.algorithm) is str and value.algorithm == 'sha256', 'unsupported_version')
    require(type(value.domain) is str and value.domain in ('canonical_batch', 'feature_result', 'configuration'))
    require(type(value.digest) is str and len(value.digest) == 64 and all(c in '0123456789abcdef' for c in value.digest))
    integer(value.byte_length, True)


@dataclass(frozen=True)
class DecisionContext:
    namespace: str
    entity: r.EntityKey
    availability: s.AvailabilitySpec
    def __post_init__(self) -> None:
        label(self.namespace); entity(self.entity); availability(self.availability, True)


@dataclass(frozen=True)
class DiagnosticPolicy:
    policy_id: str
    mode: str
    unknown_action: str
    def __post_init__(self) -> None:
        label(self.policy_id)
        require(type(self.mode) is str and self.mode in ('advisory', 'strict'), 'unsupported_version')
        require(type(self.unknown_action) is str and self.unknown_action in ('allow', 'deny'), 'unsupported_version')


@dataclass(frozen=True)
class ReferenceDeclaration:
    namespace: str
    entity: r.EntityKey
    fact_kind: str
    source: i.SourceBinding
    observed: int
    complete: bool
    def __post_init__(self) -> None:
        label(self.namespace); entity(self.entity)
        require(type(self.fact_kind) is str and self.fact_kind in MEMBERSHIPS, 'unsupported_version')
        require(type(self.source) is i.SourceBinding)
        for v in (self.source.source_id, self.source.snapshot_id, self.source.mapping_version, self.source.input_id): label(v)
        integer(self.observed, True); require(type(self.complete) is bool)


@dataclass(frozen=True)
class RevisionIdentity:
    snapshot_id: str
    revision_id: str
    def __post_init__(self) -> None:
        label(self.snapshot_id); label(self.revision_id)


@dataclass(frozen=True, kw_only=True)
class _Check:
    content: ContentFingerprint | None = None


def common(check_id: str, subject_id: str, value: ContentFingerprint | None) -> None:
    label(check_id); label(subject_id); content(value)


@dataclass(frozen=True)
class MarketCheck(_Check):
    check_id: str
    subject_id: str
    session: s.SessionSpec | None
    observed_ns: int | None
    convention: str
    interval_start_ns: int | None
    @property
    def kind(self) -> str: return 'market_time'
    def __post_init__(self) -> None:
        common(self.check_id, self.subject_id, self.content)
        if self.session is not None: session(self.session)
        optional_ns(self.observed_ns); optional_ns(self.interval_start_ns)
        require(type(self.convention) is str and self.convention in ('ordinary_event', 'closing_auction', 'completed_interval'), 'unsupported_version')
        require(self.convention == 'completed_interval' or self.interval_start_ns is None)


@dataclass(frozen=True)
class KnowledgeCheck(_Check):
    check_id: str
    subject_id: str
    known_at_ns: int | None
    @property
    def kind(self) -> str: return 'knowledge_time'
    def __post_init__(self) -> None:
        common(self.check_id, self.subject_id, self.content); optional_ns(self.known_at_ns)


@dataclass(frozen=True)
class ContextCheck(_Check):
    check_id: str
    subject_id: str
    observed: s.AvailabilitySpec | None
    @property
    def kind(self) -> str: return 'declared_context'
    def __post_init__(self) -> None:
        common(self.check_id, self.subject_id, self.content)
        if self.observed is not None: availability(self.observed)


@dataclass(frozen=True)
class MembershipCheck(_Check):
    check_id: str
    subject_id: str
    selected_kind: str
    expected_scope: str
    effective_ns: int
    reference: ReferenceDeclaration | None
    facts: tuple[p.ReferenceFact, ...]
    history: str
    @property
    def kind(self) -> str: return 'membership'
    def __post_init__(self) -> None:
        common(self.check_id, self.subject_id, self.content)
        require(type(self.selected_kind) is str and self.selected_kind in MEMBERSHIPS, 'unsupported_version')
        label(self.expected_scope); integer(self.effective_ns)
        require(type(self.history) is str and self.history in ('historical', 'current_only', 'unknown'), 'unsupported_version')
        require(type(self.facts) in (tuple, list)); require(len(self.facts) <= 1024, 'limit_exceeded')
        if self.reference is not None:
            require(type(self.reference) is ReferenceDeclaration); self.reference.__post_init__()
            require(self.reference.fact_kind == self.selected_kind, 'inconsistent_binding')
        else: require(not self.facts, 'inconsistent_binding')
        ids: set[str] = set(); rows: set[int] = set()
        for f in self.facts:
            require(type(f) is p.ReferenceFact); label(f.reference_id); label(f.fact_kind)
            require(f.fact_kind == self.selected_kind, 'inconsistent_binding')
            integer(f.row_index, True); integer(f.effective_start_ns); optional_ns(f.effective_end_ns); optional_ns(f.known_at_ns)
            require(f.effective_end_ns is None or f.effective_end_ns > f.effective_start_ns)
            require(f.factor_num is None and f.factor_den is None)
            if f.text is not None: label(f.text)
            require(self.reference is not None and f.row_index < self.reference.observed, 'inconsistent_binding')
            require(f.reference_id not in ids and f.row_index not in rows, 'duplicate')
            ids.add(f.reference_id); rows.add(f.row_index)
        object.__setattr__(self, 'facts', tuple(self.facts))


@dataclass(frozen=True)
class RevisionCheck(_Check):
    check_id: str
    subject_id: str
    expected: RevisionIdentity | None
    observed: RevisionIdentity | None
    effective_start_ns: int | None
    effective_end_ns: int | None
    effective_ns: int
    known_at_ns: int | None
    @property
    def kind(self) -> str: return 'revision'
    def __post_init__(self) -> None:
        common(self.check_id, self.subject_id, self.content)
        for value in (self.expected, self.observed):
            if value is not None:
                require(type(value) is RevisionIdentity); value.__post_init__()
        for n in (self.effective_start_ns, self.effective_end_ns, self.known_at_ns): optional_ns(n)
        integer(self.effective_ns)
        require(self.effective_end_ns is None or self.effective_start_ns is None or self.effective_start_ns < self.effective_end_ns)


@dataclass(frozen=True)
class AdjustmentCheck(_Check):
    check_id: str
    subject_id: str
    expected: p.ActionPolicy | None
    observed: p.ActionPolicy | None
    expected_unit: i.PriceUnit | None
    observed_unit: i.PriceUnit | None
    @property
    def kind(self) -> str: return 'adjustment'
    def __post_init__(self) -> None:
        common(self.check_id, self.subject_id, self.content)
        for a in (self.expected, self.observed):
            if a is not None: action(a)
        for u in (self.expected_unit, self.observed_unit):
            if u is not None: unit(u)


@dataclass(frozen=True)
class FreshnessCheck(_Check):
    check_id: str
    subject_id: str
    age_basis: str
    target_ns: int
    observed_ns: int | None
    tolerance_ns: int
    @property
    def kind(self) -> str: return 'freshness'
    def __post_init__(self) -> None:
        common(self.check_id, self.subject_id, self.content)
        require(type(self.age_basis) is str and self.age_basis in ('market_observation', 'reference_publication', 'tool_read'), 'unsupported_version')
        integer(self.target_ns); optional_ns(self.observed_ns); integer(self.tolerance_ns, True)


Check: TypeAlias = MarketCheck | KnowledgeCheck | ContextCheck | MembershipCheck | RevisionCheck | AdjustmentCheck | FreshnessCheck
CHECK_TYPES = (MarketCheck, KnowledgeCheck, ContextCheck, MembershipCheck, RevisionCheck, AdjustmentCheck, FreshnessCheck)


@dataclass(frozen=True)
class CheckFinding:
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
        common(self.check_id, self.subject_id, self.content)
        require(type(self.kind) is str and self.kind in KINDS, 'unsupported_version')
        require(type(self.status) is str and self.status in ('passed', 'failed', 'unknown'))
        require(type(self.severity) is str and self.severity == {'passed':'info', 'failed':'error', 'unknown':'warning'}[self.status])
        integer(self.unknown_prerequisites, True)
        require(type(self.assessed) is bool and self.assessed == (self.unknown_prerequisites == 0))
        require(type(self.reasons) in (tuple, list)); require(len(self.reasons) <= 32, 'limit_exceeded')
        require(all(type(v) is str and v in REASONS for v in self.reasons))
        require(tuple(self.reasons) == tuple(sorted(set(self.reasons))))
        require((not self.reasons) == (self.status == 'passed'))
        require(self.status != 'unknown' or self.unknown_prerequisites > 0)
        require(self.status != 'passed' or self.assessed)
        if self.age_ns is not None:
            require(self.kind == 'freshness' and type(self.age_ns) is int and 0 <= self.age_ns <= 2**64-1)
        object.__setattr__(self, 'reasons', tuple(self.reasons))


@dataclass(frozen=True)
class DiagnosticReport:
    context: DecisionContext
    policy: DiagnosticPolicy
    findings: tuple[CheckFinding, ...]
    schema_version: str = '1'
    requested_count: int = field(init=False)
    passed_count: int = field(init=False)
    failed_count: int = field(init=False)
    unknown_count: int = field(init=False)
    assessed_count: int = field(init=False)
    unknown_prerequisite_count: int = field(init=False)
    not_requested: tuple[str, ...] = field(init=False)
    admission: str = field(init=False)
    source_authenticated: bool = field(default=False, init=False)
    historical_acquisition_verified: bool = field(default=False, init=False)
    def __post_init__(self) -> None:
        require(type(self.schema_version) is str and self.schema_version == '1', 'unsupported_version')
        require(type(self.context) is DecisionContext and type(self.policy) is DiagnosticPolicy)
        self.context.__post_init__(); self.policy.__post_init__()
        require(type(self.findings) in (tuple, list)); require(1 <= len(self.findings) <= 256, 'limit_exceeded')
        ids: set[str] = set(); subjects: set[tuple[str, str]] = set()
        for f in self.findings:
            require(type(f) is CheckFinding); f.__post_init__()
            require(f.check_id not in ids and (f.kind, f.subject_id) not in subjects, 'duplicate')
            ids.add(f.check_id); subjects.add((f.kind, f.subject_id))
        object.__setattr__(self, 'findings', tuple(self.findings))
        object.__setattr__(self, 'requested_count', len(self.findings))
        object.__setattr__(self, 'passed_count', sum(f.status == 'passed' for f in self.findings))
        object.__setattr__(self, 'failed_count', sum(f.status == 'failed' for f in self.findings))
        object.__setattr__(self, 'unknown_count', sum(f.status == 'unknown' for f in self.findings))
        object.__setattr__(self, 'assessed_count', sum(f.assessed for f in self.findings))
        object.__setattr__(self, 'unknown_prerequisite_count', sum(f.unknown_prerequisites for f in self.findings))
        object.__setattr__(self, 'not_requested', tuple(k for k in KINDS if all(f.kind != k for f in self.findings)))
        admission = 'not_applied' if self.policy.mode == 'advisory' else (
            'denied' if self.failed_count or (self.unknown_count and self.policy.unknown_action == 'deny') else 'admitted')
        object.__setattr__(self, 'admission', admission)
