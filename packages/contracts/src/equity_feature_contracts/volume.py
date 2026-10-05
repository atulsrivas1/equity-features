"""Owned supplied daily-volume dependencies, schema1; no source authentication."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
from .errors import ContractError, ErrorCode
from .history import HistoryContext
from .inputs import Coverage, DataKind, InputScope, I64_MAX, I64_MIN
from .results import EntityKey, FeatureResult, InputBinding, Status, ValueType
from .specs import ConfigSpec


def _configuration(config: ConfigSpec, context: HistoryContext) -> tuple[int, int, str]:
    if type(config) is not ConfigSpec or type(context) is not HistoryContext:
        raise ContractError(ErrorCode.INVALID_CONFIG, "typed volume config/context required")
    if config.algorithm_version != "v1":
        raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported volume algorithm")
    params = {p.name: p.value for p in config.parameters}
    if set(params)-{"period", "quantity_basis", "evidence_limit"}:
        raise ContractError(ErrorCode.INVALID_CONFIG, "unknown volume parameter")
    period, limit, basis = params.get("period", 20), params.get("evidence_limit", 0), params.get("quantity_basis", "raw_shares")
    if type(period) is not int or not 1 <= period <= I64_MAX or type(limit) is not int or not 0 <= limit <= I64_MAX:
        raise ContractError(ErrorCode.INVALID_CONFIG, "bounded integer period/evidence required")
    if type(basis) is not str or basis not in ("raw_shares", "split_shares"):
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "explicit supported quantity basis required")
    target = next(s for s in context.sessions if s.session_id == context.entity.session_id)
    if config.session != target or config.window.governed_sessions != tuple(s.session_id for s in context.sessions):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "exact volume grid/target required")
    if config.price_unit is None or config.window.count != period or config.window.anchor != "prior_only" or not target.open_ns <= config.availability.market_cutoff_ns <= target.close_ns:
        raise ContractError(ErrorCode.INVALID_CONFIG, "prior-only period/window and target cutoff required")
    action = context.action_admission
    if action is None:
        if config.adjustment.basis != "raw" or config.adjustment.policy_version != "raw-v1" or basis != "raw_shares":
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "adjusted volume requires supplied action admission")
    elif action.config_digest != config.digest or action.availability != config.availability or action.policy.adjustment != config.adjustment or action.policy.quantity_basis != basis:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "volume action/config/quantity basis mismatch")
    return period, limit, basis


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


@dataclass(frozen=True)
class VolumeBaseline:
    result: FeatureResult
    config: ConfigSpec
    context: HistoryContext
    numerator: int | None
    denominator: int | None
    quantity_basis: str
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported volume reference schema")
        period, limit, basis = _configuration(self.config, self.context)
        if self.quantity_basis != basis or type(self.result) is not FeatureResult:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed matching volume reference required")
        r = self.result
        if len(r.values) != 1 or len(r.quality) != 1:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "single volume baseline required")
        col, quality, meta = r.values[0], r.quality[0], r.metadata
        if col.feature_id != "baseline.daily_volume" or col.algorithm_version != "v1" or col.dtype != ValueType.FLOAT64 or col.unit != "shares" or col.entities != (self.context.entity,):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "single v1 shares volume baseline required")
        if meta.config_digest != self.config.digest or meta.availability != self.config.availability or meta.session_id != self.context.entity.session_id or meta.namespace != self.config.session.namespace or meta.evidence_limit != limit:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "volume reference config/timing mismatch")
        ctx = [b for b in meta.inputs if b.role == "history_context"]
        daily = [b for b in meta.inputs if b.role == "daily_history"]
        if len(ctx) != 1 or ctx[0].kind != DataKind.REFERENCE or ctx[0].metadata.source.input_id != self.context.identity_digest:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "exact volume history context binding required")
        if any(b.kind != DataKind.DAILY or b.metadata.price_unit != self.config.price_unit or b.metadata.adjustment != self.config.adjustment for b in daily):
            raise ContractError(ErrorCode.INVALID_UNIT, "volume source unit/basis mismatch")
        if quality.expected != period:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "baseline required count mismatch")
        if quality.status != Status.AVAILABLE:
            if self.numerator is not None or self.denominator is not None:
                raise ContractError(ErrorCode.INVALID_SCHEMA, "unavailable volume has no exact operands")
            return
        selected = set(self.config.window.selected_sessions())
        if not self.config.window.history_complete or any(not c.complete for s, c in zip(self.context.sessions, self.context.slot_coverage, strict=True) if s.session_id in selected):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "available volume needs complete governed prior slots")
        action = self.context.action_admission
        if action is not None and action.status != Status.AVAILABLE:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "available volume contradicts action admission")
        if len(daily) != 1 or quality.observed != period or self.denominator != period or type(self.denominator) is not int:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "available volume operand/source/count mismatch")
        if type(self.numerator) is not int or not 0 <= self.numerator < 10**38 or self.numerator > period*I64_MAX:
            raise ContractError(ErrorCode.OVERFLOW, "nonnegative decimal128 volume sum required")
        if col.values[0] != float(Fraction(self.numerator, period)):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "exact volume/Float64 projection mismatch")

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class TargetVolume:
    entity: EntityKey
    volume: int | None
    known_at_ns: int | None
    source: InputBinding
    row_index: int
    interval: InputScope
    coverage: Coverage
    endpoint_mode: str
    quantity_basis: str
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported target volume schema")
        if type(self.entity) is not EntityKey or type(self.source) is not InputBinding or type(self.interval) is not InputScope or type(self.coverage) is not Coverage:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned typed target volume certificate required")
        if self.volume is not None and (type(self.volume) is not int or not 0 <= self.volume <= I64_MAX):
            raise ContractError(ErrorCode.BOUNDS, "nonnegative int64 target volume required")
        if self.known_at_ns is not None and (type(self.known_at_ns) is not int or not I64_MIN <= self.known_at_ns <= I64_MAX):
            raise ContractError(ErrorCode.BOUNDS, "exact int64 known-at required")
        if type(self.row_index) is not int or not 0 <= self.row_index < self.source.metadata.coverage.observed:
            raise ContractError(ErrorCode.BOUNDS, "original delivered row index required")
        if self.coverage.expected != 1 or self.coverage.observed != 1:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "supplied target is exactly one actual source row")
        if self.endpoint_mode not in ("completed_eod", "observed_prefix") or self.source.kind not in (DataKind.BAR, DataKind.DAILY) or (self.endpoint_mode == "observed_prefix" and self.source.kind != DataKind.BAR):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "explicit full daily/bar or observed bar prefix required")
        if self.quantity_basis not in ("raw_shares", "split_shares"):
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "supported target quantity basis required")
        scope = self.source.metadata.scope
        if scope is not None and (self.interval.start_ns < scope.start_ns or self.interval.end_ns > scope.end_ns or self.interval.eligibility_policy != scope.eligibility_policy or self.interval.include_opening_auction != scope.include_opening_auction or self.interval.include_closing_auction != scope.include_closing_auction):
            raise ContractError(ErrorCode.BOUNDS, "target scope must agree with original source scope")

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))
