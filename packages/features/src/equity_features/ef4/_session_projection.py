"""Pure EF4 session projections (ef4-proj1): up/down session fractions, drawdown, max drawdown, distance from the
window low and the scalar close-versus-SMA comparison over the governed daily closes of one instrument.

Exact integer/rational arithmetic on the supplied positive scaled closes, one correctly rounded float64 per published
value; the SMA is this producer's own computation (no result edge). Each output has its own closure and independent
readiness. No clock, I/O, storage, default window or default parameter.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureResult, Parameter, PriceUnit, Reason, ValueType, validate_batch,
)
from ..ef3._common import (
    DailyGrid, admit_role, envelope, fail, integer, parameter_map, slot_reasons,
)
from ._proj_common import Cell, check_features, check_unit_basis, check_policy, finish, fraction_float

SESSION_IDENTITY = "ef4.session_projection"
SESSION_ALGORITHM = "ef4-session-projection-v1"
# The label names the whole convention set (strict up/down with ties in neither, denominator N, closes-only drawdown
# and distance on the N-close window, scalar SMA comparison with strict above); another convention is another label.
SESSION_POLICY = "ef4-proj1"
UP_FRACTION = "projection.up_session_fraction"
DOWN_FRACTION = "projection.down_session_fraction"
DRAWDOWN = "projection.drawdown_fraction"
MAX_DRAWDOWN = "projection.max_drawdown_fraction"
DISTANCE_FROM_LOW = "projection.distance_from_low_fraction"
CLOSE_VS_SMA = "projection.close_vs_sma_fraction"
CLOSE_ABOVE_SMA = "projection.close_above_sma"
SESSION_FEATURES = (CLOSE_ABOVE_SMA, CLOSE_VS_SMA, DISTANCE_FROM_LOW, DOWN_FRACTION, DRAWDOWN, MAX_DRAWDOWN,
                    UP_FRACTION)
SESSION_META: dict[str, tuple[ValueType, str]] = {
    feature: (ValueType.FLOAT64, "fraction") for feature in SESSION_FEATURES}
SESSION_META[CLOSE_ABOVE_SMA] = (ValueType.BOOL, "boolean")
_KEYS = frozenset({"policy_version", "window", "evidence_limit"})


@dataclass(frozen=True)
class SessionProjectionSettings:
    policy_version: str
    window: int
    evidence_limit: int


def _check(policy: object, window: object, limit: object,
           defer_version: bool = False) -> SessionProjectionSettings:
    width = integer(window, 1, 4096)
    evidence_limit = integer(limit, 0, 10000)
    if not (defer_version and type(policy) is str):
        check_policy(policy, SESSION_POLICY)
    assert type(policy) is str
    return SessionProjectionSettings(policy, width, evidence_limit)


def build_session_projection_config(grid: DailyGrid, *, policy_version: str | None = None, window: int | None = None,
                                    availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                                    price_unit: PriceUnit, evidence_limit: int | None = None) -> ConfigSpec:
    """Final ConfigSpec; every parameter is explicit with no default."""
    if type(grid) is not DailyGrid:
        fail(ErrorCode.INVALID_CONFIG, "concrete daily grid required")
    settings = _check(policy_version, window, evidence_limit)
    params = (Parameter("policy_version", settings.policy_version), Parameter("window", settings.window),
              Parameter("evidence_limit", settings.evidence_limit))
    return envelope(SESSION_IDENTITY, SESSION_ALGORITHM, params, grid, availability, adjustment, price_unit)


def decode_session_projection_config(grid: DailyGrid, config: ConfigSpec, *,
                                     defer_version: bool = False) -> SessionProjectionSettings:
    """Validate the closed session-projection envelope against the supplied grid and return its settings."""
    values = parameter_map(config, SESSION_IDENTITY, SESSION_ALGORITHM, _KEYS, grid)
    settings = _check(values["policy_version"], values["window"], values["evidence_limit"], defer_version)
    if defer_version and settings.policy_version != SESSION_POLICY:
        return settings
    assert config.price_unit is not None
    expected = build_session_projection_config(
        grid, policy_version=settings.policy_version, window=settings.window, availability=config.availability,
        adjustment=config.adjustment, price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical session-projection envelope")
    return settings


def _max_drawdown(window: list[int]) -> Fraction:
    """Largest (running peak - close) / running peak inside the window; exact."""
    best = Fraction(0)
    peak = window[0]
    for close in window:
        if close > peak:
            peak = close
        decline = Fraction(peak - close, peak)
        if decline > best:
            best = decline
    return best


def compute_session_projection(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                               grid: DailyGrid, config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef4-proj1 session outputs; `batches` is the fixed single nullable role (daily)."""
    if type(batches) not in (tuple, list) or len(batches) != 1:
        fail(ErrorCode.INVALID_SCHEMA, "the fixed single role (daily) is required")
    batch = batches[0]
    if batch is not None:
        if type(batch) is not CanonicalBatch:
            fail(ErrorCode.INVALID_SCHEMA, "an actual BAR batch is required for a close role")
        validate_batch(batch, availability=config.availability, required_fields=())  # shared tier first
        if batch.kind != DataKind.BAR:
            fail(ErrorCode.INVALID_SCHEMA, "an actual BAR batch is required for a close role")
        owners = {c.name: c.values for c in batch.columns}
        pairs = list(zip(owners["instrument_id"], owners["session_id"]))
        if len(set(pairs)) != len(pairs):
            fail(ErrorCode.DUPLICATE, "daily rows are unique per instrument and session")
    settings = decode_session_projection_config(grid, config, defer_version=True)
    selected = check_features(features, SESSION_FEATURES)
    check_unit_basis(batch, config)
    check_policy(settings.policy_version, SESSION_POLICY)
    daily = admit_role("daily", batch, grid.instrument_id, grid, config)
    t, window = grid.target_index, settings.window
    entity = EntityKey(grid.instrument_id, config.session.session_id)
    knowledge = config.availability.knowledge_cutoff_ns
    cells: dict[str, Cell] = {}
    for feature in selected:
        long = feature in (UP_FRACTION, DOWN_FRACTION)
        span = window + 1 if long else window
        first = t - span + 1
        reasons: set[Reason] = set()
        ready: dict[int, int] = {}
        for s in range(max(first, 0), t + 1):
            if not daily.present:
                reasons.add(Reason.ABSENT_INPUT)
                continue
            causes = slot_reasons(daily.facts[s], knowledge)
            reasons.update(causes)
            close = daily.facts[s].close
            if not causes and close is not None:
                ready[s] = close
        if first < 0:
            reasons.add(Reason.INSUFFICIENT_HISTORY)
        cell = Cell(None, reasons, span, len(ready))
        cells[feature] = cell
        if reasons:
            continue
        value: float | bool
        if long:
            series = [ready[s] for s in range(t - window, t + 1)]
            pairs = list(zip(series, series[1:]))
            moves = sum(1 for a, b in pairs if (b > a if feature == UP_FRACTION else b < a))
            value = fraction_float(Fraction(moves, window))
            order = [t] + list(range(t - window, t))
        else:
            closes = [ready[s] for s in range(t - window + 1, t + 1)]
            last = closes[-1]
            if feature == DRAWDOWN:
                value = fraction_float(Fraction(max(closes) - last, max(closes)))
            elif feature == MAX_DRAWDOWN:
                value = fraction_float(_max_drawdown(closes))
            elif feature == DISTANCE_FROM_LOW:
                value = fraction_float(Fraction(last - min(closes), min(closes)))
            elif feature == CLOSE_VS_SMA:
                value = fraction_float(Fraction(window * last, sum(closes)) - 1)
            else:
                value = window * last > sum(closes)
            order = [t] + list(range(t - window + 1, t))
        cell.value = value
        cell.witnesses = []
        for s in order:
            fact = daily.facts[s]
            assert fact.input_id is not None and fact.row_index is not None
            cell.witnesses.append(EvidenceRow(
                entity, feature, fact.input_id, f"slot:{s}", fact.slot.end_ns, fact.known_at_ns, fact.slot.start_ns,
                fact.slot.end_ns, "consumed", None, "completed_interval"))
    bindings = () if daily.binding is None else (daily.binding,)
    return finish(config, entity, SESSION_ALGORITHM, selected, SESSION_META, cells, bindings,
                  settings.evidence_limit)
