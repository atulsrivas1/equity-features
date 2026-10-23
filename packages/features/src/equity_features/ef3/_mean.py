"""Pure EF3 mean-ratio companion (ef3-mean1): numerator and baseline mean daily volume and their ratio.

A separate producer from the median/MAD profiles. Each window ends at the prior session (`prior_only`) or at the
target (`current_inclusive`); only complete governed windows are admitted (no exclusions in v1, no shrunken
denominator); exact sums, one float64 rounding per published value. Overlap and any ordering of the two windows are
legal.
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
from ._common import fail, integer
from ._robust_common import (
    Fact, SessionGrid, admit_series, admit_sessions, check_entity, check_features, check_policy, check_slots,
    evidence_row, fact_reasons, first_status, make_config, ordered, parameter_map,
)
from ._stats import to_float

MEAN_IDENTITY = "ef3.volume_ratio_mean"
MEAN_ALGORITHM = "ef3-volume-ratio-mean-v1"
# The label names the whole convention set (sum / window length, ratio L sumS / (S sumL), complete windows,
# no exclusions, prior-only or current-inclusive window ends, zero baseline as zero denominator).
MEAN_POLICY = "ef3-mean1"
MEAN_BASELINE, MEAN_NUMERATOR, MEAN_RATIO = "mean.baseline", "mean.numerator", "mean.ratio"
MEAN_FEATURES = (MEAN_BASELINE, MEAN_NUMERATOR, MEAN_RATIO)
ROLES = ("series", "sessions")
INCLUSIONS = ("prior_only", "current_inclusive")
_KEYS = frozenset({"policy_version", "field", "numerator_window", "baseline_window", "numerator_inclusion",
                   "baseline_inclusion", "evidence_limit"})


@dataclass(frozen=True)
class MeanRatioSettings:
    policy_version: str
    field: str
    numerator_window: int
    baseline_window: int
    numerator_inclusion: str
    baseline_inclusion: str
    evidence_limit: int


def _check(policy: object, field: object, s: object, length: object, s_inclusion: object, l_inclusion: object,
           limit: object) -> MeanRatioSettings:
    check_policy(policy, MEAN_POLICY)
    if type(field) is not str or field != "volume":
        fail(ErrorCode.INVALID_CONFIG, "the mean companion admits only the volume field in v1")
    numerator = integer(s, 1, 4096)
    baseline = integer(length, 1, 4096)
    for inclusion in (s_inclusion, l_inclusion):
        if type(inclusion) is not str or inclusion not in INCLUSIONS:
            fail(ErrorCode.INVALID_CONFIG, "inclusion must be prior_only or current_inclusive")
    assert type(policy) is str and type(s_inclusion) is str and type(l_inclusion) is str
    return MeanRatioSettings(policy, "volume", numerator, baseline, s_inclusion, l_inclusion,
                             integer(limit, 0, 10000))


def build_mean_ratio_config(*, policy_version: str | None = None, field: str | None = None,
                            numerator_window: int | None = None, baseline_window: int | None = None,
                            numerator_inclusion: str | None = None, baseline_inclusion: str | None = None,
                            session: SessionSpec, availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                            price_unit: PriceUnit, evidence_limit: int = 0) -> ConfigSpec:
    """Final ConfigSpec; every parameter is explicit with no default."""
    settings = _check(policy_version, field, numerator_window, baseline_window, numerator_inclusion,
                      baseline_inclusion, evidence_limit)
    params = (Parameter("policy_version", settings.policy_version), Parameter("field", settings.field),
              Parameter("numerator_window", settings.numerator_window),
              Parameter("baseline_window", settings.baseline_window),
              Parameter("numerator_inclusion", settings.numerator_inclusion),
              Parameter("baseline_inclusion", settings.baseline_inclusion),
              Parameter("evidence_limit", settings.evidence_limit))
    return make_config(MEAN_IDENTITY, MEAN_ALGORITHM, params, max(settings.numerator_window, settings.baseline_window),
                       session, availability, adjustment, price_unit)


def decode_mean_ratio_config(config: ConfigSpec) -> MeanRatioSettings:
    """Validate the closed mean-ratio envelope and return its settings."""
    values = parameter_map(config, MEAN_IDENTITY, MEAN_ALGORITHM, _KEYS, frozenset())
    settings = _check(values["policy_version"], values["field"], values["numerator_window"],
                      values["baseline_window"], values["numerator_inclusion"], values["baseline_inclusion"],
                      values["evidence_limit"])
    assert config.price_unit is not None
    expected = build_mean_ratio_config(
        policy_version=settings.policy_version, field=settings.field, numerator_window=settings.numerator_window,
        baseline_window=settings.baseline_window, numerator_inclusion=settings.numerator_inclusion,
        baseline_inclusion=settings.baseline_inclusion, session=config.session, availability=config.availability,
        adjustment=config.adjustment, price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical mean-ratio envelope")
    return settings


@dataclass(frozen=True)
class _Window:
    sessions: tuple[str, ...]
    reasons: frozenset[Reason]
    total: int
    observed: int
    length: int

    @property
    def ready(self) -> bool:
        return not self.reasons


def _window(grid: SessionGrid | None, facts: dict[str, Fact], length: int, inclusion: str,
            knowledge: int) -> _Window:
    if grid is None:
        return _Window((), frozenset({Reason.ABSENT_INPUT}), 0, 0, length)
    end = grid.target_index - (inclusion == "prior_only")
    first = end - length + 1
    sessions = grid.order[max(first, 0):end + 1]
    reasons: set[Reason] = set()
    total = observed = 0
    for session_id in sessions:
        fact = facts.get(session_id, Fact())
        causes = fact_reasons(fact, knowledge)
        reasons |= causes
        if not causes:
            assert fact.value is not None
            total += fact.value
            observed += 1
    if first < 0:
        reasons.add(Reason.INSUFFICIENT_HISTORY)
    return _Window(sessions, frozenset(reasons), total, observed, length)


def compute_volume_ratio_mean(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                              config: ConfigSpec, *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef3-mean1 outputs; `batches` is the fixed (series, sessions) slots."""
    settings = decode_mean_ratio_config(config)
    entity = check_entity(entity, config)
    selected = check_features(features, MEAN_FEATURES)
    slots = check_slots(batches, 2, (DataKind.DAILY, DataKind.REFERENCE))
    series_batch, sessions_batch = slots
    knowledge = config.availability.knowledge_cutoff_ns
    used: dict[str, CanonicalBatch] = {}
    grid: SessionGrid | None = None
    facts: dict[str, Fact] = {}
    if sessions_batch is not None:
        grid = admit_sessions(sessions_batch, config, entity, allow_excluded=False)
        used["sessions"] = sessions_batch
        if series_batch is not None:
            facts = admit_series(series_batch, config, entity, grid, settings.field)
            used["series"] = series_batch
    numerator = _window(grid, facts, settings.numerator_window, settings.numerator_inclusion, knowledge)
    baseline = _window(grid, facts, settings.baseline_window, settings.baseline_inclusion, knowledge)

    def rows(feature: str, windows: tuple[_Window, ...]) -> list[EvidenceRow]:
        seen: set[str] = set()
        result: list[EvidenceRow] = []
        for window in windows:
            for session_id in window.sessions:
                if session_id not in seen:
                    seen.add(session_id)
                    result.append(evidence_row(entity, feature, facts[session_id], f"session:{session_id}"))
        return result

    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        value: float | None = None
        witnesses: list[EvidenceRow] = []
        if feature == MEAN_RATIO:
            reasons = set(numerator.reasons | baseline.reasons)
            count = (2, int(numerator.ready) + int(baseline.ready))
            if numerator.ready and baseline.ready:
                if baseline.total == 0:
                    reasons.add(Reason.ZERO_DENOMINATOR)
                else:
                    value = to_float(Fraction(baseline.length * numerator.total, numerator.length * baseline.total))
                    witnesses = rows(feature, (numerator, baseline))
        else:
            window = numerator if feature == MEAN_NUMERATOR else baseline
            reasons = set(window.reasons)
            count = (window.length, window.observed)
            if window.ready:
                value = to_float(Fraction(window.total, window.length))
                witnesses = rows(feature, (window,))
        status = Status.AVAILABLE if value is not None else first_status(reasons)
        columns.append(FeatureColumn(feature, MEAN_ALGORITHM, ValueType.FLOAT64,
                                     "fraction" if feature == MEAN_RATIO else "shares", (entity,), (value,)))
        quality.append(QualityRow(entity, feature, status, count[0], count[1], ordered(reasons)))
        for row in witnesses:
            if len(evidence) < settings.evidence_limit:
                evidence.append(row)
    bindings = tuple(sorted((InputBinding(role, batch.kind, batch.metadata) for role, batch in used.items()),
                            key=lambda binding: binding.role))
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
                              bindings, "python-exact", __version__, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
