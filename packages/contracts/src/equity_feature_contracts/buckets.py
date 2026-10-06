"""Owned individual-volume-bucket context and supplied witnesses, schema1."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from fractions import Fraction
from .errors import ContractError, ErrorCode
from .inputs import Coverage, DataKind, I64_MAX, InputScope
from .policies import PolicyAdmission
from .results import EntityKey, FeatureResult, InputBinding, Status, ValueType
from .specs import ConfigSpec, SessionSpec
from .validation import checked_int64
from .volume import TargetVolume, _digest


@dataclass(frozen=True)
class VolumeBucket:
    name: str
    start_offset_ns: int
    end_offset_ns: int
    grid_version: str
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported bucket schema")
        if any(type(x) is not str or not x.strip() for x in (self.name, self.grid_version)):
            raise ContractError(ErrorCode.INVALID_CONFIG, "explicit bucket/grid identities required")
        if any(type(x) is not int for x in (self.start_offset_ns, self.end_offset_ns)) or not 0 <= self.start_offset_ns < self.end_offset_ns <= I64_MAX:
            raise ContractError(ErrorCode.BOUNDS, "positive bounded half-open bucket offsets required")

    def bounds(self, session: SessionSpec) -> tuple[int, int]:
        if type(session) is not SessionSpec:
            raise ContractError(ErrorCode.INVALID_CONFIG, "typed bucket session required")
        return checked_int64(session.open_ns+self.start_offset_ns), checked_int64(session.open_ns+self.end_offset_ns)


@dataclass(frozen=True)
class BucketContext:
    entity: EntityKey
    grid_version: str
    sessions: tuple[SessionSpec, ...]
    bucket: VolumeBucket
    slot_coverage: tuple[Coverage, ...]
    action_admission: PolicyAdmission | None = None
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported bucket context schema")
        if type(self.entity) is not EntityKey or type(self.bucket) is not VolumeBucket or type(self.grid_version) is not str or self.grid_version != self.bucket.grid_version:
            raise ContractError(ErrorCode.INVALID_CONFIG, "typed bucket and matching explicit grid required")
        if type(self.sessions) not in (tuple, list) or not self.sessions or any(type(s) is not SessionSpec for s in self.sessions):
            raise ContractError(ErrorCode.INVALID_CONFIG, "owned typed governed bucket sessions required")
        if type(self.slot_coverage) not in (tuple, list) or any(type(c) is not Coverage for c in self.slot_coverage):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned typed bucket certificates required")
        object.__setattr__(self, "sessions", tuple(self.sessions))
        object.__setattr__(self, "slot_coverage", tuple(self.slot_coverage))
        ids = tuple(s.session_id for s in self.sessions)
        if len(set(ids)) != len(ids):
            raise ContractError(ErrorCode.DUPLICATE, "duplicate bucket session ID")
        if self.entity.session_id not in ids or len(ids) != len(self.slot_coverage):
            raise ContractError(ErrorCode.INVALID_CONFIG, "target and one certificate per bucket slot required")
        if any(s.namespace != self.sessions[0].namespace for s in self.sessions):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "one bucket namespace required")
        if any(a.close_ns > b.open_ns for a, b in zip(self.sessions, self.sessions[1:])):
            raise ContractError(ErrorCode.INVALID_ORDER, "increasing nonoverlapping bucket sessions required")
        for session, coverage in zip(self.sessions, self.slot_coverage, strict=True):
            _, end = self.bucket.bounds(session)
            if coverage.expected != 1 or coverage.observed not in (0, 1):
                raise ContractError(ErrorCode.INVALID_CONFIG, "each bucket slot expects one supplied row")
            if end > session.close_ns and (coverage.observed != 0 or coverage.complete):
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "early-close bucket has no eligible complete observation")
        action = self.action_admission
        if action is not None and (type(action) is not PolicyAdmission or action.entity != self.entity or
                (action.reference is not None and action.reference.metadata.namespace != self.sessions[0].namespace)):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "bucket action target/namespace mismatch")

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))


def _configuration(config: ConfigSpec, context: BucketContext) -> tuple[int, int, str]:
    if type(config) is not ConfigSpec or type(context) is not BucketContext:
        raise ContractError(ErrorCode.INVALID_CONFIG, "typed bucket config/context required")
    if config.algorithm_version != "v1":
        raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported bucket algorithm")
    params = {p.name: p.value for p in config.parameters}
    if set(params)-{"period", "quantity_basis", "evidence_limit"}:
        raise ContractError(ErrorCode.INVALID_CONFIG, "unknown bucket parameter")
    period, limit, basis = params.get("period", 20), params.get("evidence_limit", 0), params.get("quantity_basis", "raw_shares")
    if type(period) is not int or not 1 <= period <= I64_MAX or type(limit) is not int or not 0 <= limit <= I64_MAX:
        raise ContractError(ErrorCode.INVALID_CONFIG, "bounded bucket period/evidence required")
    if type(basis) is not str or basis not in ("raw_shares", "split_shares"):
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "supported bucket quantity basis required")
    session = next(s for s in context.sessions if s.session_id == context.entity.session_id)
    if config.session != session or config.window.governed_sessions != tuple(s.session_id for s in context.sessions):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "exact bucket grid/session required")
    if config.price_unit is None or config.window.anchor != "prior_only" or config.window.count != period or not session.open_ns <= config.availability.market_cutoff_ns <= session.close_ns:
        raise ContractError(ErrorCode.INVALID_CONFIG, "bucket price metadata/prior count/target cutoff required")
    action = context.action_admission
    if action is None:
        if config.adjustment.basis != "raw" or config.adjustment.policy_version != "raw-v1" or basis != "raw_shares":
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "adjusted bucket quantities need supplied action admission")
    elif action.config_digest != config.digest or action.availability != config.availability or action.policy.adjustment != config.adjustment or action.policy.quantity_basis != basis:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "bucket action/config/quantity mismatch")
    return period, limit, basis


@dataclass(frozen=True)
class IntervalBaseline:
    result: FeatureResult
    config: ConfigSpec
    context: BucketContext
    numerator: int | None
    denominator: int | None
    quantity_basis: str
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported interval reference schema")
        period, limit, basis = _configuration(self.config, self.context)
        if self.quantity_basis != basis or type(self.result) is not FeatureResult or len(self.result.values) != 1 or len(self.result.quality) != 1:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "single owned matching interval baseline required")
        col, q, m = self.result.values[0], self.result.quality[0], self.result.metadata
        if col.feature_id != "baseline.interval_volume" or col.algorithm_version != "v1" or col.dtype != ValueType.FLOAT64 or col.unit != "shares" or col.entities != (self.context.entity,):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "single v1 bucket shares result required")
        if m.config_digest != self.config.digest or m.availability != self.config.availability or m.namespace != self.config.session.namespace or m.session_id != self.context.entity.session_id or m.evidence_limit != limit:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "bucket result config/timing mismatch")
        contexts = [x for x in m.inputs if x.role == "bucket_context"]
        bars = [x for x in m.inputs if x.role == "bucket_history"]
        if len(contexts) != 1 or contexts[0].kind != DataKind.REFERENCE or contexts[0].metadata.source.input_id != self.context.identity_digest:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "exact bucket context binding required")
        if any(x.kind != DataKind.BAR or x.metadata.price_unit != self.config.price_unit or x.metadata.adjustment != self.config.adjustment for x in bars):
            raise ContractError(ErrorCode.INVALID_UNIT, "bucket source unit/basis mismatch")
        if q.expected != period:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "required bucket denominator mismatch")
        if q.status != Status.AVAILABLE:
            if self.numerator is not None or self.denominator is not None:
                raise ContractError(ErrorCode.INVALID_SCHEMA, "unavailable bucket has no exact operands")
            return
        selected = set(self.config.window.selected_sessions())
        action = self.context.action_admission
        if not self.config.window.history_complete or any(not c.complete for s, c in zip(self.context.sessions, self.context.slot_coverage, strict=True) if s.session_id in selected) or (action is not None and action.status != Status.AVAILABLE):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "available bucket contradicts required coverage/action")
        if len(bars) != 1 or q.observed != period or type(self.denominator) is not int or self.denominator != period:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "available bucket source/count mismatch")
        if type(self.numerator) is not int or not 0 <= self.numerator < 10**38 or self.numerator > period*I64_MAX:
            raise ContractError(ErrorCode.OVERFLOW, "nonnegative checked bucket sum required")
        if col.values[0] != float(Fraction(self.numerator, period)):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "bucket exact/Float64 projection mismatch")

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class BucketVolume:
    entity: EntityKey
    volume: int | None
    known_at_ns: int | None
    source: InputBinding
    row_index: int
    interval: InputScope
    coverage: Coverage
    bucket: VolumeBucket
    quantity_basis: str
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported bucket volume schema")
        if type(self.bucket) is not VolumeBucket:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed target bucket required")
        # Reuse only source-row/scope/quantity admission, not daily endpoint semantics.
        TargetVolume(self.entity, self.volume, self.known_at_ns, self.source, self.row_index,
                     self.interval, self.coverage, "observed_prefix", self.quantity_basis)

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))
