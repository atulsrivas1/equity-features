"""Owned supplied return and explicit benchmark identities, schema1."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from .errors import ContractError, ErrorCode
from .history import HistoryContext
from .inputs import DataKind, I64_MAX, I64_MIN
from .results import EntityKey, FeatureResult, Status, ValueType
from .specs import ConfigSpec
from .volume import _digest


def _configuration(config: ConfigSpec) -> tuple[int, int]:
    if type(config) is not ConfigSpec:
        raise ContractError(ErrorCode.INVALID_CONFIG, "owned relative configuration required")
    if config.algorithm_version != "v1":
        raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported simple-return algorithm")
    versions = {"raw": "raw-v1", "split": "split-factors-v1", "total_return": "total-return-reinvest-v1"}
    if config.adjustment.policy_version != versions[config.adjustment.basis]:
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "unsupported return adjustment policy")
    params = {p.name: p.value for p in config.parameters}
    if set(params)-{"period", "evidence_limit"} or "period" not in params:
        raise ContractError(ErrorCode.INVALID_CONFIG, "explicit horizon and optional evidence limit required")
    period, limit = params["period"], params.get("evidence_limit", 0)
    if type(period) is not int or not 1 <= period < I64_MAX or type(limit) is not int or not 0 <= limit <= I64_MAX:
        raise ContractError(ErrorCode.INVALID_CONFIG, "bounded horizon/evidence required")
    if config.price_unit is None or config.window.count != period+1 or config.window.anchor != "completed_eod" or not config.session.open_ns <= config.availability.market_cutoff_ns <= config.session.close_ns:
        raise ContractError(ErrorCode.INVALID_CONFIG, "compatible completed close window/price metadata/cutoff required")
    return period, limit


@dataclass(frozen=True)
class ReturnReference:
    result: FeatureResult
    config: ConfigSpec
    context: HistoryContext
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported return reference schema")
        period, limit = _configuration(self.config)
        if type(self.context) is not HistoryContext or type(self.result) is not FeatureResult:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned return result/history context required")
        ctx, cfg, r = self.context, self.config, self.result
        session = next(s for s in ctx.sessions if s.session_id == ctx.entity.session_id)
        if cfg.session != session or cfg.window.governed_sessions != tuple(s.session_id for s in ctx.sessions):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "return config must match exact governed target/grid")
        if len(r.values) != 1 or len(r.quality) != 1:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "single simple return required")
        col, q, m = r.values[0], r.quality[0], r.metadata
        if col.feature_id != "history.return" or col.algorithm_version != "v1" or col.dtype != ValueType.FLOAT64 or col.unit != "fraction" or col.entities != (ctx.entity,):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "single v1 simple-return fraction required")
        if m.config_digest != cfg.digest or m.availability != cfg.availability or m.namespace != session.namespace or m.session_id != ctx.entity.session_id or m.evidence_limit != limit or m.backend_id != "python-exact":
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "return config/timing/backend identity mismatch")
        contexts = [b for b in m.inputs if b.role == "history_context"]
        daily = [b for b in m.inputs if b.role == "daily_history"]
        if len(contexts) != 1 or contexts[0].kind != DataKind.REFERENCE or contexts[0].metadata.source.input_id != ctx.identity_digest:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "exact return history binding required")
        if any(b.kind != DataKind.DAILY or b.metadata.price_unit != cfg.price_unit or b.metadata.adjustment != cfg.adjustment for b in daily):
            raise ContractError(ErrorCode.INVALID_UNIT, "return source price unit/basis mismatch")
        action = ctx.action_admission
        if action is None:
            if cfg.adjustment.basis != "raw" or cfg.adjustment.policy_version != "raw-v1":
                raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "adjusted return reference needs action admission")
        elif action.config_digest != cfg.digest or action.availability != cfg.availability or action.policy.adjustment != cfg.adjustment:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "return action/config mismatch")
        elif action.reference is not None and action.reference not in m.inputs:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "return action source binding missing")
        if q.expected != period+1:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "return horizon/quality mismatch")
        if q.status == Status.AVAILABLE:
            value = col.values[0]
            if type(value) is not float or not -1.0 <= value <= float(I64_MAX-1):
                raise ContractError(ErrorCode.BOUNDS, "simple-return projection outside positive int64 price bounds")
            selected = set(cfg.window.selected_sessions())
            if len(daily) != 1 or daily[0].metadata.coverage.observed < period+1 or not cfg.window.history_complete or session.close_ns > cfg.availability.market_cutoff_ns or any(not c.complete for s, c in zip(ctx.sessions, ctx.slot_coverage, strict=True) if s.session_id in selected) or (action is not None and action.status != Status.AVAILABLE):
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "available return contradicts horizon/source/completion/action proof")

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class SectorBenchmark:
    sector_id: str
    entity: EntityKey
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported sector benchmark schema")
        if type(self.sector_id) is not str or not self.sector_id.strip() or type(self.entity) is not EntityKey:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "explicit sector ID and benchmark entity required")


@dataclass(frozen=True)
class RelativeSpec:
    entity: EntityKey
    market_benchmark: EntityKey | None = None
    sector_benchmark: SectorBenchmark | None = None
    membership_effective_ns: int | None = None
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported relative specification schema")
        if type(self.entity) is not EntityKey or (self.market_benchmark is not None and type(self.market_benchmark) is not EntityKey) or (self.sector_benchmark is not None and type(self.sector_benchmark) is not SectorBenchmark):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed symbol/benchmark identities required")
        if self.membership_effective_ns is not None and (type(self.membership_effective_ns) is not int or not I64_MIN <= self.membership_effective_ns <= I64_MAX):
            raise ContractError(ErrorCode.BOUNDS, "explicit membership effective UTCns required")
        benchmarks = [self.market_benchmark, self.sector_benchmark.entity if self.sector_benchmark is not None else None]
        if any(b is not None and b.session_id != self.entity.session_id for b in benchmarks):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "benchmark target session must match symbol")

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))
