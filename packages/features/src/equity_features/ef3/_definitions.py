"""Optional EF3 discovery; the accepted default registry, the EF1 and EF2 discovery remain unchanged."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    Capabilities, ConfigSpec, DataKind, ErrorCode, InputRequirement, OutputField, ValueType,
)
from ._common import CLOSE_FIELDS, DailyGrid, fail
from ._logvol import (
    LOG_VOL, LOG_VOL_ALGORITHM, LOG_VOL_FEATURES, LOG_VOL_IDENTITY, decode_log_volatility_config,
)
from ._relative import (
    BETA, CORRELATION, RELATIVE_ALGORITHM, RELATIVE_FEATURES, RELATIVE_IDENTITY, RESIDUAL,
    decode_relative_stats_config,
)

_FORMULAS = {
    BETA: "beta = Sxy / Sxx over the joint valid simple-return pairs (benchmark variance Sxx); exact rationals, one rounding",
    CORRELATION: "rho = sign(Sxy) sqrt(Sxy^2 / (Sxx Syy)); exact when a perfect square, else Decimal120, one rounding",
    RESIDUAL: "r_instrument,t - beta r_benchmark,t with beta of the same window, no intercept; exact, one rounding",
    LOG_VOL: "sqrt(A s2), s2 the centered N-1 variance of ln(C_i / C_{i-1}) over N+1 closes; Decimal120",
}


@dataclass(frozen=True)
class EF3Definition:
    """Own discovery metadata for one selected EF3 daily-grid producer output; batch capability only."""

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


def _requirement(role: str, rule: str) -> InputRequirement:
    return InputRequirement(role, "canonical:1", CLOSE_FIELDS, DataKind.BAR, rule=rule)


def ef3_definitions(grid: DailyGrid, config: ConfigSpec) -> tuple[EF3Definition, ...]:
    """Describe the complete selected executable EF3 daily-grid producer (lexical feature order)."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == RELATIVE_IDENTITY:
        settings = decode_relative_stats_config(grid, config)
        requirements: tuple[InputRequirement, ...] = (
            _requirement("instrument", "nullable close-only BAR on the daily governed grid, instrument id of the grid"),
            _requirement("benchmark", f"nullable close-only BAR, instrument id {settings.benchmark_id}, "
                         "same namespace, unit and adjustment"),
        )
        return tuple(EF3Definition(feature, ValueType.FLOAT64, "fraction", requirements, _FORMULAS[feature],
                                   RELATIVE_ALGORITHM) for feature in RELATIVE_FEATURES)
    if config.identity == LOG_VOL_IDENTITY:
        decode_log_volatility_config(grid, config)
        requirements = (_requirement("daily", "nullable close-only BAR on the daily governed grid"),)
        return tuple(EF3Definition(feature, ValueType.FLOAT64, "fraction", requirements, _FORMULAS[feature],
                                   LOG_VOL_ALGORITHM) for feature in LOG_VOL_FEATURES)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF3 producer is not implemented")


def require_ef3_capability(feature_id: str, capability: str) -> None:
    """Batch only; update, restore and merge are unsupported."""
    if feature_id not in RELATIVE_FEATURES + LOG_VOL_FEATURES:
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown EF3 feature")
    if capability != "batch":
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "output capability is not implemented in this package version")
