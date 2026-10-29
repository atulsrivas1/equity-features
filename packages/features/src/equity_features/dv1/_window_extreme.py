"""Pure DV1 window extremes with the date of the extreme (dv1-wext1): one daily series, one explicit basis.

The window is the `period` most recent completed sessions ending at and including the target session. On the intraday
basis `history.window_high` reads the daily highs and `history.window_low` the daily lows; on the close basis both read
the daily closes (the parameter is `extreme_basis`, not `basis`, because the result field `basis` echoes the adjustment
basis). The offset outputs count sessions before the target (0 is the target); the latest session wins every tie. All
comparisons are exact integer comparisons of price coefficients and each published price is one correctly rounded
float64 of coefficient / 10^scale. Readiness is per output field, so a null low never disturbs the high outputs. No
clock, I/O, storage, default period or default basis. `history.prior_high` and `history.prior_low` (target excluded)
are untouched. Internal, synthetic, pre-release.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from math import isfinite
from typing import cast

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow, FeatureColumn,
    FeatureResult, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata, ValueType, WindowSpec,
)
from equity_features import __version__
from equity_features.ef3._common import (
    CloseFact, DailyGrid, admit_role, fail, grid_parameters, integer, label, parameter_map,
)
from ._relative_log import _status

WEXT_IDENTITY = "dv1.window_extreme"
WEXT_ALGORITHM = "dv1-window-extreme-v1"
# The label names the whole convention set (window includes the target, explicit extreme basis, exact integer
# comparison, latest session wins ties, offsets in sessions, one float64 rounding per price).
WEXT_POLICY = "dv1-wext1"
WINDOW_HIGH = "history.window_high"
WINDOW_HIGH_OFFSET = "history.window_high_offset"
WINDOW_LOW = "history.window_low"
WINDOW_LOW_OFFSET = "history.window_low_offset"
WEXT_FEATURES = (WINDOW_HIGH, WINDOW_HIGH_OFFSET, WINDOW_LOW, WINDOW_LOW_OFFSET)
OFFSET_UNIT = "sessions"
EXTREME_BASES = ("intraday", "close")
_ADJUSTMENTS = frozenset({("raw", "raw-v1"), ("split", "split-factors-v1")})
_KEYS = frozenset({"policy_version", "period", "extreme_basis", "evidence_limit"})
# (is a high-side output, is an offset output)
_KIND = {WINDOW_HIGH: (True, False), WINDOW_HIGH_OFFSET: (True, True),
         WINDOW_LOW: (False, False), WINDOW_LOW_OFFSET: (False, True)}


@dataclass(frozen=True)
class WindowExtremeSettings:
    policy_version: str
    period: int
    extreme_basis: str
    evidence_limit: int


def window_field(feature: str, extreme_basis: str) -> str:
    """The supplied input field an output reads on the declared extreme basis."""
    if extreme_basis == "close":
        return "close"
    return "high" if _KIND[feature][0] else "low"


def _check(policy: object, period: object, basis: object, limit: object) -> WindowExtremeSettings:
    """Config-stage checks of the parameters (types, bounds, no default); the policy label is the version stage."""
    if type(policy) is not str:
        fail(ErrorCode.INVALID_CONFIG, "exact window-extreme policy label required")
    width = integer(period, 1, 4096)
    if type(basis) is not str or basis not in EXTREME_BASES:
        fail(ErrorCode.INVALID_CONFIG, "explicit extreme_basis intraday or close required (no default)")
    return WindowExtremeSettings(policy, width, basis, integer(limit, 0, 10000))


def build_window_extreme_config(grid: DailyGrid, *, policy_version: str | None = None, period: int | None = None,
                                extreme_basis: str | None = None, offset_unit: str | None = None,
                                availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit,
                                evidence_limit: int | None = None) -> ConfigSpec:
    """Final ConfigSpec for one instrument; every parameter is explicit with no default.

    `offset_unit` declares the unit of the two offset outputs and must be exactly `sessions`; a price unit offered
    there, or `sessions` offered as the price currency, is INVALID_UNIT.
    """
    if type(grid) is not DailyGrid:
        fail(ErrorCode.INVALID_CONFIG, "concrete daily grid required")
    settings = _check(policy_version, period, extreme_basis, evidence_limit)
    if type(availability) is not AvailabilitySpec or type(adjustment) is not AdjustmentSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete timing/action required")
    if (type(price_unit) is not PriceUnit or type(price_unit.currency) is not str or len(price_unit.currency) != 3
            or not all("A" <= c <= "Z" for c in price_unit.currency)):
        fail(ErrorCode.INVALID_UNIT, "an explicit PriceUnit with a three-letter uppercase currency is required")
    if (adjustment.basis, adjustment.policy_version) not in _ADJUSTMENTS:
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "declared basis must be unadjusted (raw-v1) or split_adjusted (split-factors-v1)")
    if offset_unit != OFFSET_UNIT:
        fail(ErrorCode.INVALID_UNIT, "the offset outputs are in the unit sessions")
    for value in (adjustment.policy_version, adjustment.action_snapshot, adjustment.anchor, price_unit.currency):
        label(value)
    if availability.reconstruction_reason is not None:
        label(availability.reconstruction_reason)
    target = grid.target
    # A target session still forming at the market cutoff is a lost slot (future_market), not a refusal.
    if not target.open_ns <= availability.market_cutoff_ns <= grid.sessions[-1].close_ns:
        fail(ErrorCode.BOUNDS, "market cutoff must lie between the target session open and the last grid session close")
    if settings.policy_version != WEXT_POLICY:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported window-extreme policy label")
    params = (Parameter("policy_version", settings.policy_version), Parameter("period", settings.period),
              Parameter("extreme_basis", settings.extreme_basis), Parameter("evidence_limit", settings.evidence_limit))
    return ConfigSpec(WEXT_IDENTITY, WEXT_ALGORITHM, params + grid_parameters(grid), target,
                      WindowSpec(len(grid.sessions), target.session_id, tuple(s.session_id for s in grid.sessions),
                                 "completed_eod"),
                      availability, adjustment, price_unit)


def decode_window_extreme_config(grid: DailyGrid, config: ConfigSpec) -> WindowExtremeSettings:
    """Validate the closed window-extreme envelope against the supplied grid and return its settings."""
    values = parameter_map(config, WEXT_IDENTITY, WEXT_ALGORITHM, _KEYS, grid)
    settings = _check(values["policy_version"], values["period"], values["extreme_basis"], values["evidence_limit"])
    assert config.price_unit is not None
    expected = build_window_extreme_config(
        grid, policy_version=settings.policy_version, period=settings.period, extreme_basis=settings.extreme_basis,
        offset_unit=OFFSET_UNIT, availability=config.availability, adjustment=config.adjustment,
        price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical window-extreme envelope")
    return settings


def _price(coefficient: int, scale: int) -> float:
    """One correctly rounded binary64 of coefficient / 10^scale."""
    converted = float(Fraction(coefficient, 10 ** scale))
    if not isfinite(converted):
        fail(ErrorCode.OVERFLOW, "window extreme outside binary64")
    return 0.0 if converted == 0.0 else converted


def _causes(fact: CloseFact, field: str, values: dict[str, tuple[object, ...]], market_cutoff_ns: int,
            knowledge_cutoff_ns: int) -> frozenset[Reason]:
    """Causes that make one slot not READY for `field` (empty when READY); a forming slot is future_market."""
    if fact.slot.end_ns > market_cutoff_ns:
        return frozenset({Reason.FUTURE_MARKET})
    if fact.row_index is None:
        return frozenset({Reason.ABSENT_INPUT if fact.coverage is None else Reason.GOVERNED_GAP})
    reasons: set[Reason] = set()
    if fact.known_at_ns is None:
        reasons.add(Reason.UNKNOWN_AVAILABILITY)
    elif fact.known_at_ns > knowledge_cutoff_ns:
        reasons.add(Reason.FUTURE_KNOWLEDGE)
    coverage = fact.coverage
    if coverage is None or not coverage.complete or coverage.expected != 1 or coverage.observed != 1:
        reasons.add(Reason.GOVERNED_GAP)
    if field not in values:
        reasons.add(Reason.ABSENT_INPUT)
    elif values[field][fact.row_index] is None:
        reasons.add(Reason.NULL_FIELD)
    return frozenset(reasons)


def extreme_of(series: list[int], high: bool) -> tuple[int, int]:
    """(coefficient, index) of the maximum (high) or minimum of `series`, oldest first; the latest index wins a tie."""
    best = 0
    for i in range(1, len(series)):
        if (series[i] >= series[best]) if high else (series[i] <= series[best]):
            best = i
    return series[best], best


def compute_window_extreme(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                           grid: DailyGrid, config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Selected dv1-wext1 outputs; `batches` is the single nullable daily role."""
    settings = decode_window_extreme_config(grid, config)
    if (type(features) is not tuple or not 1 <= len(features) <= len(WEXT_FEATURES)
            or any(type(feature) is not str for feature in features) or len(set(features)) != len(features)):
        fail(ErrorCode.INVALID_SCHEMA, "nonempty unique selected feature IDs required")
    if any(feature not in WEXT_FEATURES for feature in features):
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown selected window-extreme feature")
    selected = tuple(sorted(features))
    if type(batches) not in (tuple, list) or len(batches) != 1:
        fail(ErrorCode.INVALID_SCHEMA, "the single daily role is required")
    batch = batches[0]
    if batch is not None:
        if type(batch) is not CanonicalBatch:
            fail(ErrorCode.INVALID_SCHEMA, "concrete canonical batch required")
        if batch.row_count and not batch.metadata.interval_coverage:
            # Rows without any per-slot coverage declaration are never read as complete (fail closed, as EF5).
            fail(ErrorCode.INVALID_SCHEMA, "coverage not declared")
    daily = admit_role("daily", batch, grid.instrument_id, grid, config)
    columns: dict[str, tuple[object, ...]] = {} if batch is None else {c.name: tuple(c.values) for c in batch.columns}
    t = grid.target_index
    period = settings.period
    lo = max(t - period + 1, 0)
    in_grid = t - period + 1 >= 0
    assert config.price_unit is not None
    scale = config.price_unit.scale
    entity = EntityKey(grid.instrument_id, config.session.session_id)
    cutoff = config.availability.knowledge_cutoff_ns
    market = config.availability.market_cutoff_ns
    order = [t] + list(range(lo, t))
    out_columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        field = window_field(feature, settings.extreme_basis)
        high, is_offset = _KIND[feature]
        causes = {s: _causes(daily.facts[s], field, columns, market, cutoff) for s in range(lo, t + 1)}
        reasons = {reason for s in causes for reason in causes[s]}
        if not in_grid:
            reasons.add(Reason.INSUFFICIENT_HISTORY)
        ready = sum(1 for s in causes if not causes[s])
        value: float | int | None = None
        if not reasons:
            series = [cast(int, columns[field][cast(int, daily.facts[s].row_index)]) for s in range(lo, t + 1)]
            coefficient, index = extreme_of(series, high)
            value = (len(series) - 1 - index) if is_offset else _price(coefficient, scale)
            for s in order:
                fact = daily.facts[s]
                if fact.row_index is None or fact.input_id is None or len(evidence) >= settings.evidence_limit:
                    continue
                evidence.append(EvidenceRow(entity, feature, fact.input_id, f"slot:{s}", fact.slot.end_ns,
                                            fact.known_at_ns, fact.slot.start_ns, fact.slot.end_ns, "consumed", None,
                                            "completed_interval"))
        ordered = tuple(sorted(reasons, key=lambda reason: reason.value))
        out_columns.append(FeatureColumn(feature, WEXT_ALGORITHM, ValueType.INT64 if is_offset else ValueType.FLOAT64,
                                         OFFSET_UNIT if is_offset else "currency/share", (entity,), (value,)))
        quality.append(QualityRow(entity, feature, _status(reasons), period, ready, ordered))
    bindings = (daily.binding,) if daily.binding is not None else ()
    metadata = ResultMetadata(config.session.namespace, config.session.session_id, config.availability,
                              config.digest, bindings, "python-exact", __version__, settings.evidence_limit)
    return FeatureResult(tuple(out_columns), tuple(quality), metadata, tuple(evidence))
