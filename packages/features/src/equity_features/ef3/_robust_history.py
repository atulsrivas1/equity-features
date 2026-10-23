"""Pure EF3 robust history (ef3-robust1): prior-only median, MAD, quantile and mid-rank, plus the declared-cohort rank.

Exact-rational statistics over the retained prior sample of the N governed sessions before the target (the target
never enters the sample), one correctly rounded float64 per published value, an exact int64 cohort rank. Declared
exclusion facts remove sessions from the sample and from the expected count; a gap, an absent, null, unknown or
future slot inside the window is never tolerated. No clock, I/O, storage, default window or default parameter.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata,
    SessionSpec, Status, ValueType, require_compatible_inputs,
)
from equity_features import __version__
from ._common import fail, integer
from ._robust_common import (
    Fact, SessionGrid, admit_series, admit_sessions, check_entity, check_features, check_policy, check_slots,
    evidence_row, fact_reasons, first_status, make_config, ordered, parameter_map, reduced_pair, reference_evidence,
)
from ._robust_roles import Population, admit_cohort, admit_population
from ._stats import mad, median, mid_rank, quantile, to_float

ROBUST_IDENTITY = "ef3.robust_history"
ROBUST_ALGORITHM = "ef3-robust-history-v1"
# The label names the whole convention set (median averaging the two middle values, raw MAD, type 7 quantile with an
# exact rational p, mid-rank percentile, competition cohort rank, prior-only window, exclusion and gap rules).
ROBUST_POLICY = "ef3-robust1"
MEDIAN, MAD, QUANTILE, PERCENTILE_RANK = "robust.median", "robust.mad", "robust.quantile", "robust.percentile_rank"
COHORT_PERCENTILE, COHORT_RANK = "cohort.percentile_rank", "cohort.rank"
HISTORY_FEATURES = (MAD, MEDIAN, PERCENTILE_RANK, QUANTILE)
COHORT_FEATURES = (COHORT_PERCENTILE, COHORT_RANK)
ROBUST_FEATURES = tuple(sorted(HISTORY_FEATURES + COHORT_FEATURES))
ROLES = ("series", "sessions", "population", "cohort_values")
FIELDS = ("volume", "open", "high", "low", "close")
_REQUIRED = frozenset({"policy_version", "field", "window", "min_history", "evidence_limit"})
_OPTIONAL = frozenset({"quantile_num", "quantile_den", "min_population"})


@dataclass(frozen=True)
class RobustHistorySettings:
    policy_version: str
    field: str
    window: int
    min_history: int
    quantile: tuple[int, int] | None
    min_population: int | None
    evidence_limit: int


def _check(policy: object, field: object, window: object, minimum: object, q_num: object, q_den: object,
           population: object, limit: object) -> RobustHistorySettings:
    check_policy(policy, ROBUST_POLICY)
    if type(field) is not str or field not in FIELDS:
        fail(ErrorCode.INVALID_CONFIG, "field must be volume, open, high, low or close")
    width = integer(window, 1, 4096)
    least = integer(minimum, 1, width)
    pair = None if q_num is None and q_den is None else reduced_pair(q_num, q_den, maximum_one=True, positive=False)
    members = None if population is None else integer(population, 1, 65536)
    assert type(policy) is str
    return RobustHistorySettings(policy, field, width, least, pair, members, integer(limit, 0, 10000))


def build_robust_history_config(*, policy_version: str | None = None, field: str | None = None,
                                window: int | None = None, min_history: int | None = None,
                                quantile_num: int | None = None, quantile_den: int | None = None,
                                min_population: int | None = None, session: SessionSpec,
                                availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit,
                                evidence_limit: int = 0) -> ConfigSpec:
    """Final ConfigSpec; the quantile pair is present exactly when robust.quantile is selected and min_population
    exactly when a cohort output is selected. Every parameter is explicit with no default."""
    settings = _check(policy_version, field, window, min_history, quantile_num, quantile_den, min_population,
                      evidence_limit)
    if (quantile_num is None) != (quantile_den is None):
        fail(ErrorCode.INVALID_CONFIG, "the quantile numerator and denominator come together")
    params = [Parameter("policy_version", settings.policy_version), Parameter("field", settings.field),
              Parameter("window", settings.window), Parameter("min_history", settings.min_history),
              Parameter("evidence_limit", settings.evidence_limit)]
    if settings.quantile is not None:
        params += [Parameter("quantile_num", settings.quantile[0]), Parameter("quantile_den", settings.quantile[1])]
    if settings.min_population is not None:
        params.append(Parameter("min_population", settings.min_population))
    return make_config(ROBUST_IDENTITY, ROBUST_ALGORITHM, tuple(params), settings.window, session, availability,
                       adjustment, price_unit)


def decode_robust_history_config(config: ConfigSpec) -> RobustHistorySettings:
    """Validate the closed robust-history envelope and return its settings."""
    values = parameter_map(config, ROBUST_IDENTITY, ROBUST_ALGORITHM, _REQUIRED, _OPTIONAL)
    if ("quantile_num" in values) != ("quantile_den" in values):
        fail(ErrorCode.INVALID_CONFIG, "the quantile numerator and denominator come together")
    settings = _check(values["policy_version"], values["field"], values["window"], values["min_history"],
                      values.get("quantile_num"), values.get("quantile_den"), values.get("min_population"),
                      values["evidence_limit"])
    assert config.price_unit is not None
    expected = build_robust_history_config(
        policy_version=settings.policy_version, field=settings.field, window=settings.window,
        min_history=settings.min_history,
        quantile_num=None if settings.quantile is None else settings.quantile[0],
        quantile_den=None if settings.quantile is None else settings.quantile[1],
        min_population=settings.min_population, session=config.session, availability=config.availability,
        adjustment=config.adjustment, price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical robust-history envelope")
    return settings


@dataclass(frozen=True)
class _Cell:
    value: float | int | None
    status: Status
    reasons: tuple[Reason, ...]
    expected: int | None
    observed: int
    witnesses: tuple[EvidenceRow, ...]


def _unit(settings: RobustHistorySettings) -> str:
    return "shares" if settings.field == "volume" else "currency/share"


def compute_robust_history(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                           config: ConfigSpec, *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef3-robust1 outputs; `batches` is the fixed (series, sessions, population, cohort_values) slots."""
    settings = decode_robust_history_config(config)
    entity = check_entity(entity, config)
    selected = check_features(features, ROBUST_FEATURES)
    use_history = any(feature in HISTORY_FEATURES for feature in selected)
    use_cohort = any(feature in COHORT_FEATURES for feature in selected)
    if (QUANTILE in selected) != (settings.quantile is not None):
        fail(ErrorCode.INVALID_CONFIG, "the quantile parameter is present exactly when robust.quantile is selected")
    if use_cohort != (settings.min_population is not None):
        fail(ErrorCode.INVALID_CONFIG, "min_population is present exactly when a cohort output is selected")
    slots = check_slots(batches, 4, (DataKind.DAILY, DataKind.REFERENCE, DataKind.REFERENCE, DataKind.DAILY))
    series_batch, sessions_batch, population_batch, cohort_batch = slots
    if use_history and use_cohort and series_batch is not None and cohort_batch is not None:
        require_compatible_inputs(series_batch, cohort_batch)
    knowledge = config.availability.knowledge_cutoff_ns
    assert config.price_unit is not None
    scale = Fraction(1, 10 ** config.price_unit.scale) if settings.field != "volume" else Fraction(1)
    cells: dict[str, _Cell] = {}
    used: dict[str, CanonicalBatch] = {}

    if use_history:
        grid: SessionGrid | None = None
        facts: dict[str, Fact] = {}
        if sessions_batch is not None:
            grid = admit_sessions(sessions_batch, config, entity, allow_excluded=True)
            used["sessions"] = sessions_batch
            if series_batch is not None:
                facts = admit_series(series_batch, config, entity, grid, settings.field)
                used["series"] = series_batch
        cells.update(_history(settings, selected, config, entity, grid, facts, knowledge, scale))
    if use_cohort:
        population: Population | None = None
        member_facts: dict[str, Fact] = {}
        if population_batch is not None:
            population = admit_population(population_batch, config, entity)
            used["population"] = population_batch
            if cohort_batch is not None:
                member_facts = admit_cohort(cohort_batch, config, population, settings.field)
                used["cohort_values"] = cohort_batch
        cells.update(_cohort(settings, selected, entity, population, member_facts, knowledge))

    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        cell = cells[feature]
        dtype = ValueType.INT64 if feature == COHORT_RANK else ValueType.FLOAT64
        unit = ("members" if feature == COHORT_RANK else _unit(settings) if feature in (MEDIAN, MAD, QUANTILE)
                else "fraction")
        columns.append(FeatureColumn(feature, ROBUST_ALGORITHM, dtype, unit, (entity,), (cell.value,)))
        quality.append(QualityRow(entity, feature, cell.status, cell.expected, cell.observed, cell.reasons))
        for row in cell.witnesses:
            if len(evidence) < settings.evidence_limit:
                evidence.append(row)
    bindings = tuple(sorted((InputBinding(role, batch.kind, batch.metadata) for role, batch in used.items()),
                            key=lambda binding: binding.role))
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
                              bindings, "python-exact", __version__, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))


def _history(settings: RobustHistorySettings, selected: tuple[str, ...], config: ConfigSpec, entity: EntityKey,
             grid: SessionGrid | None, facts: dict[str, Fact], knowledge: int,
             scale: Fraction) -> dict[str, _Cell]:
    wanted = [feature for feature in selected if feature in HISTORY_FEATURES]
    window = settings.window
    if grid is None:
        # No governed grid: nothing can be assessed (exclusions and the window are unknown).
        absent = (Reason.ABSENT_INPUT,)
        return {f: _Cell(None, Status.MISSING_INPUT, absent, window + (f == PERCENTILE_RANK), 0, ())
                for f in wanted}
    t = grid.target_index
    prior = grid.order[max(0, t - window):t]
    reasons: set[Reason] = set()
    excluded: list[str] = []
    retained: list[str] = []
    values: list[int] = []
    for session_id in prior:
        fact_of_exclusion = grid.excluded.get(session_id)
        if fact_of_exclusion is not None:
            if fact_of_exclusion.known_at_ns is None:
                reasons.add(Reason.UNKNOWN_AVAILABILITY)
            elif fact_of_exclusion.known_at_ns > knowledge:
                reasons.add(Reason.FUTURE_KNOWLEDGE)
            else:
                excluded.append(session_id)
            continue
        fact = facts.get(session_id, Fact())
        causes = fact_reasons(fact, knowledge)
        if causes:
            reasons |= causes
        else:
            assert fact.value is not None
            retained.append(session_id)
            values.append(fact.value)
    expected = window - len(excluded)
    if t < window or expected < settings.min_history:
        reasons.add(Reason.INSUFFICIENT_HISTORY)
    observed = len(retained)
    target_fact = facts.get(grid.order[t], Fact())
    target_reasons = fact_reasons(target_fact, knowledge)
    sample_ready = not reasons
    sample = sorted(Fraction(v) for v in values)
    cells: dict[str, _Cell] = {}
    sample_witnesses: list[EvidenceRow] = []
    if sample_ready:
        sample_witnesses = [evidence_row(entity, MEDIAN, facts[s], f"session:{s}") for s in retained]
        sample_witnesses += [reference_evidence(entity, MEDIAN, grid, s, f"excluded:{s}") for s in excluded]
    for feature in wanted:
        if feature == PERCENTILE_RANK:
            all_reasons = reasons | target_reasons
            count_expected, count_observed = expected + 1, observed + int(not target_reasons)
        else:
            all_reasons = set(reasons)
            count_expected, count_observed = expected, observed
        value: float | None = None
        witnesses: tuple[EvidenceRow, ...] = ()
        if not all_reasons:
            if feature == MEDIAN:
                value = to_float(median(sample) * scale)
            elif feature == MAD:
                value = to_float(mad(sample) * scale)
            elif feature == QUANTILE:
                assert settings.quantile is not None
                value = to_float(quantile(sample, Fraction(*settings.quantile)) * scale)
            else:
                assert target_fact.value is not None
                value = to_float(mid_rank(sample, Fraction(target_fact.value)))
            rows = [_retag(row, feature) for row in sample_witnesses]
            if feature == PERCENTILE_RANK:
                rows.insert(0, evidence_row(entity, feature, target_fact, f"session:{grid.order[t]}"))
            witnesses = tuple(rows)
        status = Status.AVAILABLE if value is not None else first_status(all_reasons)
        cells[feature] = _Cell(value, status, ordered(all_reasons), count_expected, count_observed, witnesses)
    return cells


def _retag(row: EvidenceRow, feature: str) -> EvidenceRow:
    return EvidenceRow(row.entity, feature, row.input_id, row.row_id, row.event_ns, row.known_at_ns,
                       row.effective_start_ns, row.effective_end_ns, row.use, row.exclusion_reason, row.boundary)


def _cohort(settings: RobustHistorySettings, selected: tuple[str, ...], entity: EntityKey,
            population: Population | None, facts: dict[str, Fact], knowledge: int) -> dict[str, _Cell]:
    wanted = [feature for feature in selected if feature in COHORT_FEATURES]
    if population is None:
        return {f: _Cell(None, Status.MISSING_INPUT, (Reason.ABSENT_INPUT,), None, 0, ()) for f in wanted}
    assert settings.min_population is not None
    members = population.members
    declared = len(members)
    ready = {m: not fact_reasons(facts.get(m, Fact()), knowledge) for m in members}
    reasons: set[Reason] = set(fact_reasons(facts.get(entity.instrument_id, Fact()), knowledge))
    if any(not ok for m, ok in ready.items() if m != entity.instrument_id):
        reasons.add(Reason.PARTIAL_UNIVERSE)
    if declared < settings.min_population:
        reasons.add(Reason.INSUFFICIENT_HISTORY)
    eligible = [m for m in members if ready[m]]
    cells: dict[str, _Cell] = {}
    for feature in wanted:
        value: float | int | None = None
        witnesses: tuple[EvidenceRow, ...] = ()
        if not reasons:
            ranked = [Fraction(value_of) for m in members if (value_of := facts[m].value) is not None]
            target_value = facts[entity.instrument_id].value
            assert target_value is not None
            if feature == COHORT_RANK:
                value = 1 + sum(1 for v in ranked if v > target_value)
            else:
                value = to_float(mid_rank(ranked, Fraction(target_value)))
            witnesses = tuple(evidence_row(entity, feature, facts[m], f"member:{m}") for m in eligible)
        status = Status.AVAILABLE if value is not None else first_status(reasons)
        cells[feature] = _Cell(value, status, ordered(reasons), declared, len(eligible), witnesses)
    return cells
