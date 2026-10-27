"""Pure EF3 robust volume pace (ef3-pace1): prior-only same-bucket median and MAD baselines, ratio and robust z.

The evaluation bucket is the last bucket of the supplied grid that has fully elapsed at the market cutoff and lies
inside the actual target session. The baseline is the retained prior sample of the N governed sessions before the
target (the target never enters it); declared exclusions and sessions that closed before the end of the evaluation
bucket are removed, never zero and never a gap. Exact rationals, one float64 rounding per published value.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata,
    SessionSpec, Status, ValueType,
)
from equity_features import __version__
from ._common import fail, integer, label
from ._robust_common import (
    Fact, SessionGrid, admit_sessions, bounds_reasons, check_entity, check_features, check_policy, check_slots, fact_reasons,
    first_status, knowledge_reasons, make_config, ordered, parameter_map, reduced_pair, reference_evidence,
)
from ._robust_roles import Edges, admit_bars, admit_edges
from ._stats import mad, median, to_float

PACE_IDENTITY = "ef3.volume_pace_robust"
PACE_ALGORITHM = "ef3-volume-pace-robust-v1"
# The label names the whole convention set (profiles, evaluation bucket, structural ineligibility, exclusion rules,
# raw MAD, ratio y/M, z (y-M)/(k D), zero denominators).
PACE_POLICY = "ef3-pace1"
BASELINE_MEDIAN, BASELINE_MAD, RATIO, ROBUST_Z = (
    "pace.baseline_median", "pace.baseline_mad", "pace.ratio", "pace.robust_z")
PACE_FEATURES = (BASELINE_MAD, BASELINE_MEDIAN, RATIO, ROBUST_Z)
ROLES = ("grid", "sessions", "bars")
PROFILES = ("cumulative", "bucket")
_REQUIRED = frozenset({"policy_version", "profile", "window", "min_history", "grid_version", "evidence_limit"})
_OPTIONAL = frozenset({"scale_num", "scale_den"})


@dataclass(frozen=True)
class PaceSettings:
    policy_version: str
    profile: str
    window: int
    min_history: int
    grid_version: str
    scale: tuple[int, int] | None
    evidence_limit: int


def _check(policy: object, profile: object, window: object, minimum: object, grid_version: object, s_num: object,
           s_den: object, limit: object) -> PaceSettings:
    check_policy(policy, PACE_POLICY)
    if type(profile) is not str or profile not in PROFILES:
        fail(ErrorCode.INVALID_CONFIG, "profile must be cumulative or bucket")
    width = integer(window, 1, 4096)
    least = integer(minimum, 1, width)
    version = label(grid_version)
    pair = None if s_num is None and s_den is None else reduced_pair(s_num, s_den, maximum_one=False, positive=True)
    assert type(policy) is str
    return PaceSettings(policy, profile, width, least, version, pair, integer(limit, 0, 10000))


def build_pace_config(*, policy_version: str | None = None, profile: str | None = None, window: int | None = None,
                      min_history: int | None = None, grid_version: str | None = None,
                      scale_num: int | None = None, scale_den: int | None = None, session: SessionSpec,
                      availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit,
                      evidence_limit: int = 0) -> ConfigSpec:
    """Final ConfigSpec; the scale pair k = scale_num/scale_den is present exactly when pace.robust_z is selected."""
    settings = _check(policy_version, profile, window, min_history, grid_version, scale_num, scale_den,
                      evidence_limit)
    if (scale_num is None) != (scale_den is None):
        fail(ErrorCode.INVALID_CONFIG, "the scale numerator and denominator come together")
    params = [Parameter("policy_version", settings.policy_version), Parameter("profile", settings.profile),
              Parameter("window", settings.window), Parameter("min_history", settings.min_history),
              Parameter("grid_version", settings.grid_version), Parameter("evidence_limit", settings.evidence_limit)]
    if settings.scale is not None:
        params += [Parameter("scale_num", settings.scale[0]), Parameter("scale_den", settings.scale[1])]
    return make_config(PACE_IDENTITY, PACE_ALGORITHM, tuple(params), settings.window, session, availability,
                       adjustment, price_unit)


def decode_pace_config(config: ConfigSpec) -> PaceSettings:
    """Validate the closed volume-pace envelope and return its settings."""
    values = parameter_map(config, PACE_IDENTITY, PACE_ALGORITHM, _REQUIRED, _OPTIONAL)
    if ("scale_num" in values) != ("scale_den" in values):
        fail(ErrorCode.INVALID_CONFIG, "the scale numerator and denominator come together")
    settings = _check(values["policy_version"], values["profile"], values["window"], values["min_history"],
                      values["grid_version"], values.get("scale_num"), values.get("scale_den"),
                      values["evidence_limit"])
    assert config.price_unit is not None
    expected = build_pace_config(
        policy_version=settings.policy_version, profile=settings.profile, window=settings.window,
        min_history=settings.min_history, grid_version=settings.grid_version,
        scale_num=None if settings.scale is None else settings.scale[0],
        scale_den=None if settings.scale is None else settings.scale[1], session=config.session,
        availability=config.availability, adjustment=config.adjustment, price_unit=config.price_unit,
        evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical volume-pace envelope")
    return settings


@dataclass(frozen=True)
class _Operand:
    """One session's operand over the evaluation buckets: ready value or its causes, plus the aggregate witness."""

    value: int | None
    reasons: frozenset[Reason]
    known_at_ns: int | None
    start_ns: int
    end_ns: int


def _operand(facts: dict[tuple[str, int], Fact], session_id: str, open_ns: int, offsets: tuple[int, ...], b: int,
             profile: str, knowledge: int) -> _Operand:
    first = 0 if profile == "cumulative" else b
    reasons: set[Reason] = set()
    total = 0
    known: int | None = None
    for c in range(first, b + 1):
        fact = facts.get((session_id, c), Fact())
        causes = fact_reasons(fact, knowledge)
        reasons |= causes
        if not causes:
            assert fact.value is not None and fact.known_at_ns is not None
            total += fact.value
            known = fact.known_at_ns if known is None else max(known, fact.known_at_ns)
    return _Operand(None if reasons else total, frozenset(reasons), known, open_ns + offsets[first],
                    open_ns + offsets[b + 1])


def _witness(entity: EntityKey, feature: str, input_id: str, row_id: str, operand: _Operand) -> EvidenceRow:
    return EvidenceRow(entity, feature, input_id, row_id, operand.end_ns, operand.known_at_ns, operand.start_ns,
                       operand.end_ns, "consumed", None, "completed_interval")


def compute_volume_pace_robust(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                               config: ConfigSpec, *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef3-pace1 outputs; `batches` is the fixed (grid, sessions, bars) slots."""
    settings = decode_pace_config(config)
    entity = check_entity(entity, config)
    selected = check_features(features, PACE_FEATURES)
    if (ROBUST_Z in selected) != (settings.scale is not None):
        fail(ErrorCode.INVALID_CONFIG, "the scale parameter is present exactly when pace.robust_z is selected")
    slots = check_slots(batches, 3, (DataKind.REFERENCE, DataKind.REFERENCE, DataKind.BAR))
    grid_batch, sessions_batch, bars_batch = slots
    knowledge = config.availability.knowledge_cutoff_ns
    window = settings.window
    used: dict[str, CanonicalBatch] = {}
    offsets: tuple[int, ...] | None = None
    edges: Edges | None = None
    grid: SessionGrid | None = None
    if grid_batch is not None:
        edges = admit_edges(grid_batch, config, entity, settings.grid_version)
        offsets = edges.offsets
        used["grid"] = grid_batch
    if sessions_batch is not None:
        grid = admit_sessions(sessions_batch, config, entity, allow_excluded=True)
        used["sessions"] = sessions_batch
    facts: dict[tuple[str, int], Fact] = {}
    if offsets is not None and grid is not None and bars_batch is not None:
        facts = admit_bars(bars_batch, config, entity, grid, offsets)
        used["bars"] = bars_batch

    reasons_base: set[Reason] = set()
    n_expected: int | None = window
    n_observed = 0
    base_ready = False
    sample: list[Fraction] = []
    retained: list[str] = []
    excluded: list[str] = []
    ineligible: list[str] = []
    operands: dict[str, _Operand] = {}
    current: _Operand | None = None
    t = -1
    if offsets is None or grid is None:
        reasons_base.add(Reason.ABSENT_INPUT)
    else:
        session = config.session
        t = grid.target_index
        prior = grid.order[max(0, t - window):t]
        assert edges is not None
        reasons_base |= bounds_reasons(grid, prior, knowledge)
        for known_at in edges.known_at:
            reasons_base |= knowledge_reasons(known_at, knowledge)
        known_excluded = [s for s in prior if s in grid.excluded and _known(grid.excluded[s].known_at_ns, knowledge)]
        lim = min(session.close_ns, config.availability.market_cutoff_ns) - session.open_ns
        fits = [c for c in range(len(offsets) - 1) if offsets[c + 1] <= lim]
        if not fits:
            n_expected = window - len(known_excluded)
            reasons_base.add(Reason.INELIGIBLE if offsets[1] > session.close_ns - session.open_ns
                             else Reason.FUTURE_MARKET)
        else:
            b = fits[-1]
            for session_id in prior:
                fact_of_exclusion = grid.excluded.get(session_id)
                if fact_of_exclusion is not None:
                    if fact_of_exclusion.known_at_ns is None:
                        reasons_base.add(Reason.UNKNOWN_AVAILABILITY)
                    elif fact_of_exclusion.known_at_ns > knowledge:
                        reasons_base.add(Reason.FUTURE_KNOWLEDGE)
                    else:
                        excluded.append(session_id)
                    continue
                open_ns, close_ns = grid.bounds[session_id]
                if close_ns - open_ns < offsets[b + 1]:
                    ineligible.append(session_id)
                    continue
                operand = _operand(facts, session_id, open_ns, offsets, b, settings.profile, knowledge)
                if operand.reasons:
                    reasons_base |= operand.reasons
                else:
                    retained.append(session_id)
                    operands[session_id] = operand
                    assert operand.value is not None
                    sample.append(Fraction(operand.value))
            n_expected = window - len(excluded) - len(ineligible)
            n_observed = len(retained)
            if t < window or n_expected < settings.min_history:
                reasons_base.add(Reason.INSUFFICIENT_HISTORY)
            base_ready = not reasons_base
            current = _operand(facts, grid.order[t], session.open_ns, offsets, b, settings.profile, knowledge)

    sample.sort()
    median_value = mad_value = None
    if base_ready:
        median_value, mad_value = median(sample), mad(sample)
    input_id = bars_batch.metadata.source.input_id if bars_batch is not None else None
    cur_ready = current is not None and not current.reasons
    cur_reasons = frozenset() if current is None else current.reasons

    def baseline_rows(feature: str) -> list[EvidenceRow]:
        assert input_id is not None and grid is not None
        rows = [_witness(entity, feature, input_id, f"session:{s}", operands[s]) for s in retained]
        rows += [reference_evidence(entity, feature, grid, s, f"excluded:{s}") for s in excluded]
        rows += [reference_evidence(entity, feature, grid, s, f"ineligible:{s}") for s in ineligible]
        return rows

    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        value: float | None = None
        rows: list[EvidenceRow] = []
        if feature in (BASELINE_MEDIAN, BASELINE_MAD):
            reasons = set(reasons_base)
            count = (n_expected, n_observed)
            if base_ready:
                assert median_value is not None and mad_value is not None
                value = to_float(median_value if feature == BASELINE_MEDIAN else mad_value)
                rows = baseline_rows(feature)
        else:
            reasons = set(reasons_base) | set(cur_reasons)
            count = (2, int(base_ready) + int(cur_ready))
            if base_ready and cur_ready:
                assert median_value is not None and mad_value is not None and current is not None
                assert current.value is not None
                y = Fraction(current.value)
                if feature == RATIO:
                    if median_value == 0:
                        reasons.add(Reason.ZERO_DENOMINATOR)
                    else:
                        value = to_float(y / median_value)
                else:
                    assert settings.scale is not None
                    if mad_value == 0:
                        reasons.add(Reason.ZERO_DENOMINATOR)
                    else:
                        value = to_float((y - median_value) * settings.scale[1] / (settings.scale[0] * mad_value))
                if value is not None:
                    assert input_id is not None and grid is not None
                    rows = [_witness(entity, feature, input_id, f"target:{grid.order[t]}", current)]
                    rows += baseline_rows(feature)
        status = Status.AVAILABLE if value is not None else first_status(reasons)
        columns.append(FeatureColumn(feature, PACE_ALGORITHM, ValueType.FLOAT64,
                                     "fraction" if feature in (RATIO, ROBUST_Z) else "shares", (entity,), (value,)))
        quality.append(QualityRow(entity, feature, status, count[0], count[1], ordered(reasons)))
        for row in rows:
            if len(evidence) < settings.evidence_limit:
                evidence.append(row)
    bindings = tuple(sorted((InputBinding(role, batch.kind, batch.metadata) for role, batch in used.items()),
                            key=lambda binding: binding.role))
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
                              bindings, "python-exact", __version__, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))


def _known(known_at_ns: int | None, knowledge: int) -> bool:
    return known_at_ns is not None and known_at_ns <= knowledge
