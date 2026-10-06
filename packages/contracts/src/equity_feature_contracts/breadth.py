"""Owned declared-universe and supplied breadth dependencies, schema1."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from .errors import ContractError, ErrorCode
from .history import HistoryContext, SMAReference
from .inputs import Coverage, DataKind, I64_MAX, I64_MIN, InputScope
from .relative import ReturnReference
from .results import EntityKey, FeatureResult, InputBinding, Reason, Status, ValueType
from .specs import ConfigSpec
from .volume import _digest


def _configuration(config: ConfigSpec, direction: bool) -> tuple[int, int]:
    if type(config) is not ConfigSpec or config.algorithm_version != "v1":
        raise ContractError(ErrorCode.INVALID_CONFIG, "owned v1 breadth configuration required")
    params = {p.name: p.value for p in config.parameters}
    n, limit = params.get("period"), params.get("evidence_limit", 0)
    if set(params)-{"period", "evidence_limit"} or type(n) is not int or not 1 <= n < I64_MAX or type(limit) is not int or not 0 <= limit <= I64_MAX:
        raise ContractError(ErrorCode.INVALID_CONFIG, "explicit bounded period/evidence required")
    if config.window.count != n+int(direction) or config.window.anchor != "completed_eod" or config.price_unit is None or not config.session.open_ns <= config.availability.market_cutoff_ns <= config.session.close_ns:
        raise ContractError(ErrorCode.INVALID_CONFIG, "completed close window/price metadata/cutoff required")
    policies = {"raw": "raw-v1", "split": "split-factors-v1", "total_return": "total-return-reinvest-v1"}
    if config.adjustment.policy_version != policies[config.adjustment.basis]:
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "unsupported breadth adjustment policy")
    return n, limit


@dataclass(frozen=True)
class DeclaredUniverseSpec:
    namespace: str
    session_id: str
    universe_id: str
    membership_identity: str
    effective_ns: int
    members: tuple[str, ...]
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported universe schema")
        if any(type(x) is not str or not x.strip() for x in (self.namespace, self.session_id, self.universe_id, self.membership_identity)) or type(self.members) not in (tuple, list) or any(type(x) is not str or not x.strip() for x in self.members):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "explicit universe identities and members required")
        object.__setattr__(self, "members", tuple(self.members))
        if len(set(self.members)) != len(self.members):
            raise ContractError(ErrorCode.DUPLICATE, "duplicate declared universe member")
        if type(self.effective_ns) is not int or not I64_MIN <= self.effective_ns <= I64_MAX:
            raise ContractError(ErrorCode.BOUNDS, "UTC int64 universe evaluation point required")

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class CompletedClose:
    entity: EntityKey
    coefficient: int | None
    known_at_ns: int | None
    source: InputBinding
    row_index: int
    interval: InputScope
    coverage: Coverage
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported completed close schema")
        if type(self.entity) is not EntityKey or type(self.source) is not InputBinding or type(self.interval) is not InputScope or type(self.coverage) is not Coverage:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned completed close certificate required")
        if self.coefficient is not None and (type(self.coefficient) is not int or not 1 <= self.coefficient <= I64_MAX):
            raise ContractError(ErrorCode.BOUNDS, "positive int64 close coefficient required")
        if self.known_at_ns is not None and (type(self.known_at_ns) is not int or not I64_MIN <= self.known_at_ns <= I64_MAX):
            raise ContractError(ErrorCode.BOUNDS, "exact int64 close knowledge required")
        if self.source.kind not in (DataKind.DAILY, DataKind.BAR) or self.source.metadata.price_unit is None or type(self.row_index) is not int or not 0 <= self.row_index < self.source.metadata.coverage.observed or self.coverage.expected != 1 or self.coverage.observed != 1:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "original daily/bar source row and price metadata required")
        scope = self.source.metadata.scope
        if scope is not None and (self.interval.start_ns < scope.start_ns or self.interval.end_ns > scope.end_ns or self.interval.eligibility_policy != scope.eligibility_policy or self.interval.include_opening_auction != scope.include_opening_auction or self.interval.include_closing_auction != scope.include_closing_auction):
            raise ContractError(ErrorCode.BOUNDS, "selected close scope must match original source scope")

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class SMAInput:
    reference: SMAReference
    config: ConfigSpec
    context: HistoryContext
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported SMA input schema")
        n, limit = _configuration(self.config, False)
        if type(self.reference) is not SMAReference or type(self.context) is not HistoryContext:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned SMA/context required")
        r, ctx, cfg = self.reference.result, self.context, self.config
        m, col, q = r.metadata, r.values[0], r.quality[0]
        if col.entities != (ctx.entity,) or cfg.session != next(s for s in ctx.sessions if s.session_id == ctx.entity.session_id) or cfg.window.governed_sessions != tuple(s.session_id for s in ctx.sessions) or m.namespace != cfg.session.namespace or m.session_id != ctx.entity.session_id or m.config_digest != cfg.digest or m.availability != cfg.availability or m.evidence_limit != limit or m.backend_id != "python-exact" or self.reference.price_unit != cfg.price_unit or q.expected != n:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "SMA actual config/entity/grid/metadata mismatch")
        contexts = [b for b in m.inputs if b.role == "history_context"]
        daily = [b for b in m.inputs if b.role == "daily_history"]
        if len(contexts) != 1 or contexts[0].kind != DataKind.REFERENCE or contexts[0].metadata.source.input_id != ctx.identity_digest or any(b.kind != DataKind.DAILY or b.metadata.price_unit != cfg.price_unit or b.metadata.adjustment != cfg.adjustment for b in daily):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "SMA exact context/source proof required")
        action = ctx.action_admission
        if action is None:
            if cfg.adjustment.basis != "raw":
                raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "adjusted SMA needs action proof")
        elif action.config_digest != cfg.digest or action.availability != cfg.availability or action.policy.adjustment != cfg.adjustment or (action.reference is not None and action.reference not in m.inputs):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "SMA actual action proof mismatch")
        selected = set(cfg.window.selected_sessions())
        if q.status == Status.AVAILABLE and (self.reference.denominator != n or len(daily) != 1 or daily[0].metadata.coverage.observed < n or not cfg.window.history_complete or cfg.session.close_ns > cfg.availability.market_cutoff_ns or any(not c.complete for s, c in zip(ctx.sessions, ctx.slot_coverage, strict=True) if s.session_id in selected) or (action is not None and action.status != Status.AVAILABLE)):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "available SMA contradicts completion/source/action proof")

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class MemberFeatures:
    entity: EntityKey
    return_reference: ReturnReference | None = None
    sma: SMAInput | None = None
    close: CompletedClose | None = None
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported member schema")
        if type(self.entity) is not EntityKey or (self.return_reference is not None and (type(self.return_reference) is not ReturnReference or self.return_reference.context.entity != self.entity)) or (self.sma is not None and (type(self.sma) is not SMAInput or self.sma.context.entity != self.entity)) or (self.close is not None and (type(self.close) is not CompletedClose or self.close.entity != self.entity)):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "owned member dependencies must bind actual entity")


@dataclass(frozen=True)
class BreadthSpec:
    entity: EntityKey
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1" or type(self.entity) is not EntityKey:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned aggregate entity schema1 required")

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class MemberExclusion:
    entity: EntityKey
    feature_id: str
    status: Status
    reasons: tuple[Reason, ...]
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported exclusion schema")
        if type(self.entity) is not EntityKey or self.feature_id not in ("breadth.direction_counts", "breadth.above_sma_fraction") or type(self.status) is not Status or self.status == Status.AVAILABLE or type(self.reasons) not in (tuple, list) or not self.reasons or any(type(x) is not Reason for x in self.reasons):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed unavailable member exclusion required")
        object.__setattr__(self, "reasons", tuple(self.reasons))


@dataclass(frozen=True)
class BreadthResult:
    result: FeatureResult
    exclusions: tuple[MemberExclusion, ...]
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1" or type(self.result) is not FeatureResult or type(self.exclusions) not in (tuple, list) or any(type(x) is not MemberExclusion for x in self.exclusions):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned breadth result/exclusions schema1 required")
        object.__setattr__(self, "exclusions", tuple(self.exclusions))
        if len(self.result.values) != 1 or self.result.values[0].feature_id not in ("breadth.direction_counts", "breadth.above_sma_fraction") or any(e.feature_id != self.result.values[0].feature_id or e.entity.session_id != self.result.metadata.session_id for e in self.exclusions):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "exclusions must match breadth feature/target")
        col = self.result.values[0]
        if len(col.entities) != 1 or col.algorithm_version != "v1" or col.dtype != (ValueType.BREADTH_COUNTS if col.feature_id == "breadth.direction_counts" else ValueType.BREADTH_FRACTION):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "single typed v1 aggregate breadth cell required")
        q = self.result.quality[0]
        if (q.status == Status.AVAILABLE and self.exclusions) or (q.status == Status.INCOMPLETE_COVERAGE and (q.expected is None or len(self.exclusions) != q.expected-q.observed)):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "breadth exclusions must account for incomplete population")
        if len({e.entity for e in self.exclusions}) != len(self.exclusions):
            raise ContractError(ErrorCode.DUPLICATE, "duplicate member exclusion")

