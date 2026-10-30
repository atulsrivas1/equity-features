"""Pure DV1 simple-mean average true range (dv1-atrs1): `history.atr_simple_mean`.

TR_i = max(H_i - L_i, |H_i - C_(i-1)|, |L_i - C_(i-1)|); the value is the plain arithmetic mean of the N most recent
true ranges ending at AND INCLUDING the target session (N true ranges, N + 1 closes), as one exact rational rounded once
to float64. It is not the Wilder recursion of the shipped `history.atr` (which is untouched): there is no
initialization anchor, no smoothing and no inclusion parameter. Strict readiness: every closure slot must be READY, with
no skipping and no zero fill; an unavailable value is never zero. No clock, I/O, storage or default period. The
daily-grid admission and slot vocabulary are the EF3 helpers (`equity_features.ef3._common`), imported not copied.
Internal, synthetic, pre-release.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputRequirement, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata, Status,
    ValueType, WindowSpec,
)
from equity_features import __version__
from ._config_check import check_coverage_declared, check_tail, check_units
from ._status import status_of
from equity_features.ef3._common import (
    CloseFact, DailyGrid, admit_role, fail, grid_parameters, integer, label, parameter_map,
)

ATR_IDENTITY = "dv1.atr_simple_mean"
ATR_ALGORITHM = "dv1-atr-simple-mean-v1"
# The label names the whole convention set (target-inclusive N true ranges, simple mean, strict readiness, exact
# rational arithmetic, one float64 rounding, no initialization anchor and no inclusion parameter).
ATR_POLICY = "dv1-atrs1"
ATR_MEAN = "history.atr_simple_mean"
ATR_FEATURES = (ATR_MEAN,)
ATR_ROLE = "daily"
ATR_FIELDS = ("instrument_id", "session_id", "start_ns", "end_ns", "high", "low", "close", "known_at_ns")
ATR_FORMULA = ("SIMPLE mean (not the Wilder recursion of history.atr) of the N most recent true ranges "
               "TR = max(H - L, |H - C_prev|, |L - C_prev|) ending at and including the target session (N true ranges, "
               "N + 1 closes: oldest close only, middle high/low/close, target high/low); no initialization anchor, "
               "no inclusion parameter; strict: any closure slot not READY is unavailable, never skipped or zero "
               "filled; exact rational, one float64 rounding")
_KEYS = frozenset({"policy_version", "period", "evidence_limit"})


@dataclass(frozen=True)
class AtrSimpleMeanSettings:
    policy_version: str
    period: int
    evidence_limit: int


def atr_requirements() -> tuple[InputRequirement, ...]:
    """The single required daily role: high, low and close (the oldest closure slot needs only its close)."""
    return (InputRequirement(ATR_ROLE, "canonical:1", ATR_FIELDS, DataKind.BAR,
                             rule="nullable high/low/close BAR on the daily governed grid, instrument id of the grid; "
                                  "oldest closure session needs close only, the target needs high and low only"),)


def _shape(policy: object, period: object, limit: object) -> AtrSimpleMeanSettings:
    """Config-stage shape of the closed parameters; the policy label itself is a later (version) stage."""
    if type(policy) is not str:
        fail(ErrorCode.INVALID_CONFIG, "exact simple-mean ATR policy label required")
    return AtrSimpleMeanSettings(policy, integer(period, 1, 4096), integer(limit, 0, 10000))


def build_atr_simple_mean_config(grid: DailyGrid, *, policy_version: str | None, period: int | None,
                                 availability: AvailabilitySpec | None, adjustment: AdjustmentSpec | None,
                                 price_unit: PriceUnit | None, evidence_limit: int | None) -> ConfigSpec:
    """Final ConfigSpec for one instrument; every parameter is explicit with no default."""
    if type(grid) is not DailyGrid:
        fail(ErrorCode.INVALID_CONFIG, "concrete daily grid required")
    settings = _shape(policy_version, period, evidence_limit)
    availability, adjustment, price_unit = check_units(availability, adjustment, price_unit)
    check_tail(grid, availability, adjustment, price_unit, settings.policy_version, ATR_POLICY,
               "unsupported simple-mean ATR policy label")
    target = grid.target
    params = (Parameter("policy_version", settings.policy_version), Parameter("period", settings.period),
              Parameter("evidence_limit", settings.evidence_limit))
    return ConfigSpec(ATR_IDENTITY, ATR_ALGORITHM, params + grid_parameters(grid), target,
                      WindowSpec(len(grid.sessions), target.session_id, tuple(s.session_id for s in grid.sessions),
                                 "completed_eod"),
                      availability, adjustment, price_unit)


def decode_atr_simple_mean_config(grid: DailyGrid, config: ConfigSpec) -> AtrSimpleMeanSettings:
    """Validate the closed simple-mean ATR envelope against the supplied grid and return its settings."""
    values = parameter_map(config, ATR_IDENTITY, ATR_ALGORITHM, _KEYS, grid)
    settings = _shape(values["policy_version"], values["period"], values["evidence_limit"])
    expected = build_atr_simple_mean_config(
        grid, policy_version=settings.policy_version, period=settings.period, availability=config.availability,
        adjustment=config.adjustment, price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical simple-mean ATR envelope")
    return settings


def _need(slot: int, target: int, period: int) -> tuple[str, ...]:
    """Fields a closure slot must supply: oldest close only, target high/low only, middle high/low/close."""
    if slot == target - period:
        return ("close",)
    if slot == target:
        return ("high", "low")
    return ("high", "low", "close")


def _causes(fact: CloseFact, need: tuple[str, ...], columns: dict[str, tuple[object, ...]], market_cutoff_ns: int,
            knowledge_cutoff_ns: int) -> set[Reason]:
    """Causes that make one closure slot not READY (empty when READY); knowledge uses the original known_at."""
    if fact.slot.end_ns > market_cutoff_ns:
        return {Reason.FUTURE_MARKET}
    if fact.row_index is None:
        return {Reason.ABSENT_INPUT if fact.coverage is None else Reason.GOVERNED_GAP}
    reasons: set[Reason] = set()
    if fact.known_at_ns is None:
        reasons.add(Reason.UNKNOWN_AVAILABILITY)
    elif fact.known_at_ns > knowledge_cutoff_ns:
        reasons.add(Reason.FUTURE_KNOWLEDGE)
    coverage = fact.coverage
    if coverage is None or not coverage.complete or coverage.expected != 1 or coverage.observed != 1:
        reasons.add(Reason.GOVERNED_GAP)
    for name in need:
        if name not in fact.columns:
            reasons.add(Reason.ABSENT_INPUT)
        elif columns[name][fact.row_index] is None:
            reasons.add(Reason.NULL_FIELD)
    return reasons


def _mean_true_range(highs: dict[int, int], lows: dict[int, int], closes: dict[int, int], first: int, target: int,
                     scale: int) -> float:
    """Exact (sum of TR over slots first..target) / (count * 10^scale), rounded once to float64."""
    total = 0
    for slot in range(first, target + 1):
        high, low, previous = highs[slot], lows[slot], closes[slot - 1]
        total += max(high - low, abs(high - previous), abs(low - previous))
    try:
        return float(Fraction(total, (target - first + 1) * 10 ** scale))
    except OverflowError:
        fail(ErrorCode.OVERFLOW, "simple-mean ATR outside binary64")


def compute_atr_simple_mean(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                            grid: DailyGrid, config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Selected dv1-atrs1 output; `batches` is the single nullable daily role carrying high, low and close."""
    settings = decode_atr_simple_mean_config(grid, config)
    if (type(features) is not tuple or not 1 <= len(features) <= len(ATR_FEATURES)
            or any(type(feature) is not str for feature in features) or len(set(features)) != len(features)):
        fail(ErrorCode.INVALID_SCHEMA, "nonempty unique selected feature IDs required")
    if any(feature not in ATR_FEATURES for feature in features):
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown selected simple-mean ATR feature")
    if type(batches) not in (tuple, list) or len(batches) != 1:
        fail(ErrorCode.INVALID_SCHEMA, "exactly one daily role is required")
    batch = batches[0]
    check_coverage_declared(batch)
    admission = admit_role(ATR_ROLE, batch, grid.instrument_id, grid, config)
    columns: dict[str, tuple[object, ...]] = {}
    if batch is not None:
        columns = {c.name: tuple(c.values) for c in batch.columns}
    assert config.price_unit is not None
    scale = config.price_unit.scale
    t = grid.target_index
    period = settings.period
    first = t - period
    in_grid = first >= 0
    knowledge = config.availability.knowledge_cutoff_ns
    market = config.availability.market_cutoff_ns
    reasons: set[Reason] = set()
    ready: list[int] = []
    for slot in range(max(first, 0), t + 1):
        causes = _causes(admission.facts[slot], _need(slot, t, period), columns, market, knowledge)
        reasons.update(causes)
        if not causes:
            ready.append(slot)
    if not in_grid:
        reasons.add(Reason.INSUFFICIENT_HISTORY)
    entity = EntityKey(grid.instrument_id, config.session.session_id)
    value: float | None = None
    if in_grid and len(ready) == period + 1:
        def cell(name: str, slot: int) -> int:
            row = admission.facts[slot].row_index
            assert row is not None
            raw = columns[name][row]
            assert type(raw) is int
            return raw
        highs = {s: cell("high", s) for s in range(first + 1, t + 1)}
        lows = {s: cell("low", s) for s in range(first + 1, t + 1)}
        closes = {s: cell("close", s) for s in range(first, t)}
        value = _mean_true_range(highs, lows, closes, first + 1, t, scale)
    evidence: list[EvidenceRow] = []
    if value is not None:
        # Target slot first, then the remaining closure slots ascending.
        for slot in [t] + list(range(first, t)):
            fact = admission.facts[slot]
            if fact.input_id is None or len(evidence) >= settings.evidence_limit:
                continue
            evidence.append(EvidenceRow(entity, ATR_MEAN, fact.input_id, f"slot:{slot}", fact.slot.end_ns,
                                        fact.known_at_ns, fact.slot.start_ns, fact.slot.end_ns, "consumed", None,
                                        "completed_interval"))
    status = Status.AVAILABLE if value is not None else status_of(reasons)
    ordered = tuple(sorted(reasons, key=lambda reason: reason.value)) if value is None else ()
    unit = f"{config.price_unit.currency}/share"
    result_columns = (FeatureColumn(ATR_MEAN, ATR_ALGORITHM, ValueType.FLOAT64, unit, (entity,), (value,)),)
    quality = (QualityRow(entity, ATR_MEAN, status, period + 1, len(ready), ordered),)
    bindings = (admission.binding,) if admission.binding is not None else ()
    metadata = ResultMetadata(config.session.namespace, config.session.session_id, config.availability, config.digest,
                              bindings, "python-exact", __version__, settings.evidence_limit)
    return FeatureResult(result_columns, quality, metadata, tuple(evidence))
