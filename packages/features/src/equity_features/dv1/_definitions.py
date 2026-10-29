"""Optional DV1 discovery; the accepted default registry and the EF1 to EF5 discovery remain unchanged."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    Capabilities, ConfigSpec, DataKind, ErrorCode, InputRequirement, OutputField, ValueType,
)
from equity_features.ef3._common import CLOSE_FIELDS, DailyGrid, fail
from ._relative_log import (
    LOG_BETA, LOG_CORRELATION, RLOG_ALGORITHM, RLOG_FEATURES, RLOG_IDENTITY, decode_relative_log_config,
)

# Each description names the convention so the id cannot be mistaken for the simple-return variant.
_FORMULAS = {
    LOG_BETA: "LOG-return beta = Sxy / Syy over the joint pairs of x = ln(C_i,j / C_i,j-1) and y = ln(C_b,j / C_b,j-1) "
              "(centred sums, benchmark variance Syy); not the simple-return relative.beta; Decimal120 logarithms, one "
              "float64 rounding; benchmark ratios all equal is zero_denominator by exact comparison",
    LOG_CORRELATION: "LOG-return correlation = Sxy / sqrt(Sxx Syy) over the same log-return pairs; not the simple-return "
                     "relative.correlation; Decimal120, one float64 rounding; either series with equal ratios is "
                     "zero_denominator by exact comparison",
}


@dataclass(frozen=True)
class DV1Definition:
    """Own discovery metadata for one selected DV1 daily-grid producer output; batch capability only."""

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


def dv1_definitions(grid: DailyGrid, config: ConfigSpec) -> tuple[DV1Definition, ...]:
    """Describe the complete selected executable DV1 daily-grid producer (lexical feature order)."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == RLOG_IDENTITY:
        settings = decode_relative_log_config(grid, config)
        requirements = (
            _requirement("instrument", "nullable close-only BAR on the daily governed grid, instrument id of the grid"),
            _requirement("benchmark", f"nullable close-only BAR, instrument id {settings.benchmark_id}, "
                         "same namespace, unit and adjustment"),
        )
        return tuple(DV1Definition(feature, ValueType.FLOAT64, "fraction", requirements, _FORMULAS[feature],
                                   RLOG_ALGORITHM) for feature in RLOG_FEATURES)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "DV1 producer is not implemented")


def require_dv1_capability(feature_id: str, capability: str) -> None:
    """Batch only; update, restore and merge are unsupported."""
    if feature_id not in RLOG_FEATURES:
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown DV1 feature")
    if capability != "batch":
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "output capability is not implemented in this package version")
