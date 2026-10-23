"""Pure EF3 daily centered log-return volatility (ef3-dlv1): sqrt(A * s2) of N natural-log close returns.

s2 is the centered sample variance (denominator N-1) of ln(C_i / C_{i-1}) over N+1 READY consecutive governed closes.
Every logarithm is a Decimal120 evaluation of the exact close ratio and the variance is two-pass. No clock, I/O,
storage or default. This is a distinct producer from the simple-return `history.return_volatility`.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Context, Decimal, DecimalException, localcontext, MAX_EMAX, MIN_EMIN, ROUND_HALF_EVEN
from math import isfinite

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow, FeatureColumn,
    FeatureResult, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata, Status, ValueType,
)
from equity_features import __version__
from ._common import DailyGrid, admit_role, envelope, fail, first_status, integer, parameter_map, slot_reasons

LOG_VOL_IDENTITY = "ef3.daily_log_volatility"
LOG_VOL_ALGORITHM = "ef3-daily-log-vol-v1"
# The label names the whole convention set (natural-log returns, centered, N-1, sqrt(A s2), strict N+1 closes).
LOG_VOL_POLICY = "ef3-dlv1"
LOG_VOL = "history.log_return_volatility"
LOG_VOL_FEATURES = (LOG_VOL,)
ROLES = ("daily",)
_KEYS = frozenset({"policy_version", "period", "annualization_factor", "evidence_limit"})
_I64_MAX = 2**63 - 1


@dataclass(frozen=True)
class LogVolatilitySettings:
    policy_version: str
    period: int
    annualization_factor: int
    evidence_limit: int


def _check(policy: object, period: object, factor: object, limit: object) -> LogVolatilitySettings:
    if type(policy) is not str:
        fail(ErrorCode.INVALID_CONFIG, "exact log-volatility policy label required")
    if policy != LOG_VOL_POLICY:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported log-volatility policy label")
    return LogVolatilitySettings(policy, integer(period, 2, 4096), integer(factor, 1, _I64_MAX),
                                 integer(limit, 0, 10000))


def build_log_volatility_config(grid: DailyGrid, *, policy_version: str | None = None, period: int | None = None,
                                annualization_factor: int | None = None, availability: AvailabilitySpec,
                                adjustment: AdjustmentSpec, price_unit: PriceUnit,
                                evidence_limit: int = 0) -> ConfigSpec:
    """Final ConfigSpec; period and annualization_factor are explicit (1 means unannualized), no defaults."""
    if type(grid) is not DailyGrid:
        fail(ErrorCode.INVALID_CONFIG, "concrete daily grid required")
    settings = _check(policy_version, period, annualization_factor, evidence_limit)
    params = (Parameter("policy_version", settings.policy_version), Parameter("period", settings.period),
              Parameter("annualization_factor", settings.annualization_factor),
              Parameter("evidence_limit", settings.evidence_limit))
    return envelope(LOG_VOL_IDENTITY, LOG_VOL_ALGORITHM, params, grid, availability, adjustment, price_unit)


def decode_log_volatility_config(grid: DailyGrid, config: ConfigSpec) -> LogVolatilitySettings:
    """Validate the closed log-volatility envelope against the supplied grid and return its settings."""
    values = parameter_map(config, LOG_VOL_IDENTITY, LOG_VOL_ALGORITHM, _KEYS, grid)
    settings = _check(values["policy_version"], values["period"], values["annualization_factor"],
                      values["evidence_limit"])
    assert config.price_unit is not None
    expected = build_log_volatility_config(
        grid, policy_version=settings.policy_version, period=settings.period,
        annualization_factor=settings.annualization_factor, availability=config.availability,
        adjustment=config.adjustment, price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical log-volatility envelope")
    return settings


def log_volatility(closes: tuple[int, ...], factor: int) -> float:
    """sqrt(A s2) of an all-ready window of N+1 closes (N >= 2 log returns).

    Equal close ratios, decided by integer cross-multiplication, give identical logarithms and a centered sum that is
    exactly zero; that case is published as +0.0 explicitly. Every other value is the unsnapped Decimal120 result.
    """
    first = (closes[1], closes[0])
    if all(closes[i] * first[1] == first[0] * closes[i - 1] for i in range(2, len(closes))):
        return 0.0
    context = Context(prec=120, rounding=ROUND_HALF_EVEN, Emin=MIN_EMIN, Emax=MAX_EMAX)
    try:
        with localcontext(context):
            logs = [(Decimal(c) / Decimal(p)).ln() for p, c in zip(closes, closes[1:])]
            count = len(logs)
            mean = sum(logs, Decimal(0)) / count
            variance = sum(((value - mean) ** 2 for value in logs), Decimal(0)) / (count - 1)
            result = (Decimal(factor) * variance).sqrt()
            converted = float(result)
    except (DecimalException, OverflowError, ValueError):
        fail(ErrorCode.OVERFLOW, "log-volatility arithmetic outside declared numeric policy")
    if not isfinite(converted):
        fail(ErrorCode.OVERFLOW, "nonfinite log-volatility conversion")
    return 0.0 if result == 0 else converted


def compute_log_volatility(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                           grid: DailyGrid, config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """The one `history.log_return_volatility` cell; `batches` is the fixed single nullable role (daily)."""
    settings = decode_log_volatility_config(grid, config)
    if (type(features) is not tuple or len(features) != 1 or type(features[0]) is not str):
        fail(ErrorCode.INVALID_SCHEMA, "exactly one selected feature ID required")
    if features[0] != LOG_VOL:
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown selected log-volatility feature")
    if type(batches) not in (tuple, list) or len(batches) != 1:
        fail(ErrorCode.INVALID_SCHEMA, "the fixed single role (daily) is required")
    daily = admit_role("daily", batches[0], grid.instrument_id, grid, config)
    t, period = grid.target_index, settings.period
    lo = max(t - period, 0)
    expected = period + 1
    entity = EntityKey(grid.instrument_id, config.session.session_id)
    cutoff = config.availability.knowledge_cutoff_ns
    reasons: set[Reason] = set()
    observed = 0
    if not daily.present:
        reasons.add(Reason.ABSENT_INPUT)
    else:
        for s in range(lo, t + 1):
            causes = slot_reasons(daily.facts[s], cutoff)
            reasons.update(causes)
            observed += not causes
        if t - period < 0:
            reasons.add(Reason.INSUFFICIENT_HISTORY)
    status = first_status(reasons)
    value: float | None = None
    evidence: list[EvidenceRow] = []
    if status == Status.AVAILABLE:
        closes = tuple(daily.facts[s].close for s in range(lo, t + 1))
        assert all(close is not None for close in closes)
        value = log_volatility(tuple(c for c in closes if c is not None), settings.annualization_factor)
        for s in (lo, t):
            fact = daily.facts[s]
            if fact.row_index is None or fact.input_id is None or len(evidence) >= settings.evidence_limit:
                continue
            evidence.append(EvidenceRow(entity, LOG_VOL, fact.input_id, f"slot:{fact.slot.index}",
                fact.slot.end_ns, fact.known_at_ns, fact.slot.start_ns, fact.slot.end_ns, "consumed", None,
                "completed_interval"))
    ordered = tuple(sorted(reasons, key=lambda reason: reason.value))
    column = FeatureColumn(LOG_VOL, LOG_VOL_ALGORITHM, ValueType.FLOAT64, "fraction", (entity,), (value,))
    row = QualityRow(entity, LOG_VOL, status, expected, observed, ordered)
    bindings = () if daily.binding is None else (daily.binding,)
    metadata = ResultMetadata(config.session.namespace, config.session.session_id, config.availability,
                              config.digest, bindings, "python-exact", __version__, settings.evidence_limit)
    return FeatureResult((column,), (row,), metadata, tuple(evidence))
