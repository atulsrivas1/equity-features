"""Optional EF3 robust discovery; the accepted default registry, R17, EF1, EF2 and the EF3 daily-grid discovery are unchanged."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    Capabilities, ConfigSpec, DataKind, ErrorCode, InputRequirement, OutputField, ValueType,
)
from ._common import fail
from ._mean import (
    MEAN_ALGORITHM, MEAN_BASELINE, MEAN_FEATURES, MEAN_IDENTITY, MEAN_NUMERATOR, MEAN_RATIO, decode_mean_ratio_config,
)
from ._pace import (
    BASELINE_MAD, BASELINE_MEDIAN, PACE_ALGORITHM, PACE_FEATURES, PACE_IDENTITY, RATIO, ROBUST_Z, decode_pace_config,
)
from ._robust_history import (
    COHORT_FEATURES, COHORT_PERCENTILE, COHORT_RANK, HISTORY_FEATURES, MAD, MEDIAN, PERCENTILE_RANK, QUANTILE,
    ROBUST_ALGORITHM, ROBUST_IDENTITY, decode_robust_history_config,
)

_DAILY = ("instrument_id", "session_id", "start_ns", "end_ns", "known_at_ns")
_BAR = ("instrument_id", "session_id", "start_ns", "end_ns", "volume", "known_at_ns")
_REFERENCE = ("instrument_id", "session_id", "reference_id", "fact_kind", "effective_start_ns", "effective_end_ns",
              "text", "known_at_ns")
_FORMULAS = {
    MEDIAN: "median of the retained prior sample (even n averages the two middle values); exact, one rounding",
    MAD: "median(|x - median|) of the retained prior sample, raw (scale constant 1); exact, one rounding",
    QUANTILE: "Hyndman-Fan type 7, h = (n-1) p with exact rational p; exact, one rounding",
    PERCENTILE_RANK: "(L + E/2) / n of the target against the prior sample (ties count half)",
    COHORT_PERCENTILE: "(L + E/2) / n over all eligible declared members including the target",
    COHORT_RANK: "1 + #{members with a larger value} (competition rank, 1 is the largest)",
    BASELINE_MEDIAN: "median of the retained prior same-bucket (or cumulative-through-bucket) volumes",
    BASELINE_MAD: "raw MAD of the retained prior same-bucket (or cumulative-through-bucket) volumes",
    RATIO: "y / M with y the current observation and M the baseline median",
    ROBUST_Z: "(y - M) / (k D) with k = scale_num/scale_den and D the baseline MAD",
    MEAN_NUMERATOR: "sum over the S-session window / S",
    MEAN_BASELINE: "sum over the L-session window / L",
    MEAN_RATIO: "(L sumS) / (S sumL)",
}
_UNITS = {COHORT_PERCENTILE: "fraction", PERCENTILE_RANK: "fraction", COHORT_RANK: "members",
          BASELINE_MEDIAN: "shares", BASELINE_MAD: "shares", RATIO: "fraction", ROBUST_Z: "fraction",
          MEAN_NUMERATOR: "shares", MEAN_BASELINE: "shares", MEAN_RATIO: "fraction"}


@dataclass(frozen=True)
class EF3RobustDefinition:
    """Own discovery metadata for one selected EF3 robust producer output; batch capability only."""

    feature_id: str
    dtype: ValueType
    unit: str
    requirements: tuple[InputRequirement, ...]
    formula: str
    algorithm_version: str
    schema_version: str = "1"
    capabilities: Capabilities = Capabilities(batch=True)

    @property
    def outputs(self) -> tuple[OutputField, ...]:
        return (OutputField("value", self.dtype.value, self.unit),)


def _req(role: str, kind: DataKind, fields: tuple[str, ...], rule: str) -> InputRequirement:
    return InputRequirement(role, "canonical:1", fields, kind, rule=rule)


def ef3_robust_definitions(config: ConfigSpec) -> tuple[EF3RobustDefinition, ...]:
    """Describe the complete executable output set of one configured EF3 robust producer (lexical order)."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == ROBUST_IDENTITY:
        settings = decode_robust_history_config(config)
        unit = "shares" if settings.field == "volume" else "currency/share"
        reqs = (_req("series", DataKind.DAILY, _DAILY + (settings.field,), "nullable daily rows of the governed grid"),
                _req("sessions", DataKind.REFERENCE, _REFERENCE, "nullable ef3.session.bounds / excluded facts"))
        cohort = (_req("population", DataKind.REFERENCE, _REFERENCE, "nullable ef3.population.member facts"),
                  _req("cohort_values", DataKind.DAILY, _DAILY + (settings.field,), "nullable one row per member"))
        names = [f for f in HISTORY_FEATURES if f != QUANTILE or settings.quantile is not None]
        out = [EF3RobustDefinition(f, ValueType.FLOAT64, unit if f in (MEDIAN, MAD, QUANTILE) else "fraction",
                                   reqs, _FORMULAS[f], ROBUST_ALGORITHM) for f in names]
        if settings.min_population is not None:
            out += [EF3RobustDefinition(f, ValueType.INT64 if f == COHORT_RANK else ValueType.FLOAT64, _UNITS[f],
                                        cohort, _FORMULAS[f], ROBUST_ALGORITHM) for f in COHORT_FEATURES]
        return tuple(sorted(out, key=lambda d: d.feature_id))
    if config.identity == PACE_IDENTITY:
        pace = decode_pace_config(config)
        pace_reqs = (_req("grid", DataKind.REFERENCE, _REFERENCE, "nullable ef3.bucket.edge facts"),
                     _req("sessions", DataKind.REFERENCE, _REFERENCE, "nullable ef3.session.bounds / excluded facts"),
                     _req("bars", DataKind.BAR, _BAR, "nullable one BAR row per session per grid bucket"))
        return tuple(EF3RobustDefinition(f, ValueType.FLOAT64, _UNITS[f], pace_reqs, _FORMULAS[f], PACE_ALGORITHM)
                     for f in PACE_FEATURES if f != ROBUST_Z or pace.scale is not None)
    if config.identity == MEAN_IDENTITY:
        decode_mean_ratio_config(config)
        reqs = (_req("series", DataKind.DAILY, _DAILY + ("volume",), "nullable daily volume rows"),
                _req("sessions", DataKind.REFERENCE, _REFERENCE, "nullable ef3.session.bounds facts only"))
        return tuple(EF3RobustDefinition(f, ValueType.FLOAT64, _UNITS[f], reqs, _FORMULAS[f], MEAN_ALGORITHM)
                     for f in MEAN_FEATURES)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF3 producer is not implemented")


def require_ef3_robust_capability(feature_id: str, capability: str) -> None:
    """Batch only; update, restore and merge are unsupported."""
    if feature_id not in HISTORY_FEATURES + COHORT_FEATURES + PACE_FEATURES + MEAN_FEATURES:
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown EF3 robust feature")
    if capability != "batch":
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "output capability is not implemented in this package version")
