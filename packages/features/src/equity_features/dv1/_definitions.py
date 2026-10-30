"""Optional DV1 discovery; the accepted default registry and the EF1 to EF5 discovery remain unchanged."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    Capabilities, ConfigSpec, DataKind, ErrorCode, InputRequirement, OutputField, ValueType,
)
from equity_features.ef3._common import CLOSE_FIELDS, DailyGrid, fail
from ._core_spread import CORE_ALGORITHM, CORE_FEATURES, CORE_FORMULA, CORE_IDENTITY, CORE_META, CORE_ROLE, decode_core_spread_config
from ._atr_simple_mean import (
    ATR_ALGORITHM, ATR_FEATURES, ATR_FORMULA, ATR_IDENTITY, ATR_MEAN, atr_requirements, decode_atr_simple_mean_config,
)
from ._window_extreme import (
    OFFSET_UNIT, WEXT_ALGORITHM, WEXT_FEATURES, WEXT_IDENTITY, WINDOW_HIGH, WINDOW_HIGH_OFFSET, WINDOW_LOW,
    WINDOW_LOW_OFFSET, decode_window_extreme_config, window_field,
)
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


# Window extremes: the description names the target-inclusive window so the id cannot be mistaken for history.prior_high/low.
_WINDOW_FORMULAS = {
    WINDOW_HIGH: "maximum daily high (intraday basis) or close (close basis) over the P most recent completed sessions "
                 "INCLUDING the target; exact integer comparison, one float64 rounding; not history.prior_high "
                 "(target excluded)",
    WINDOW_HIGH_OFFSET: "sessions before the target of the window maximum (0 = the target); the latest session wins a "
                        "tie; exact integer",
    WINDOW_LOW: "minimum daily low (intraday basis) or close (close basis) over the P most recent completed sessions "
                "INCLUDING the target; exact integer comparison, one float64 rounding; not history.prior_low "
                "(target excluded)",
    WINDOW_LOW_OFFSET: "sessions before the target of the window minimum (0 = the target); the latest session wins a "
                       "tie; exact integer",
}


_LEG_FIELDS = ("instrument_id", "session_id", "reference_id", "fact_kind", "effective_start_ns", "effective_end_ns", "text",
               "price", "known_at_ns")


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


def dv1_definitions(grid: DailyGrid | None, config: ConfigSpec) -> tuple[DV1Definition, ...]:
    """Describe the complete selected executable DV1 daily-grid producer (lexical feature order)."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == CORE_IDENTITY:
        decode_core_spread_config(config)
        legs = (InputRequirement(CORE_ROLE, "canonical:1", _LEG_FIELDS, DataKind.REFERENCE,
                                 rule="nullable ef4.leg.start|end facts, one start and one end witness per declared core "
                                      "fund; regular_open start = daily_bar_open of the exact session, end = same-session "
                                      "close"),)
        return tuple(DV1Definition(feature, CORE_META[feature][0], CORE_META[feature][1], legs, CORE_FORMULA[feature],
                                   CORE_ALGORITHM) for feature in CORE_FEATURES)
    if type(grid) is not DailyGrid:
        fail(ErrorCode.INVALID_CONFIG, "the daily grid is required")
    if config.identity == RLOG_IDENTITY:
        settings = decode_relative_log_config(grid, config)
        requirements = (
            _requirement("instrument", "nullable close-only BAR on the daily governed grid, instrument id of the grid"),
            _requirement("benchmark", f"nullable close-only BAR, instrument id {settings.benchmark_id}, "
                         "same namespace, unit and adjustment"),
        )
        return tuple(DV1Definition(feature, ValueType.FLOAT64, "fraction", requirements, _FORMULAS[feature],
                                   RLOG_ALGORITHM) for feature in RLOG_FEATURES)
    if config.identity == WEXT_IDENTITY:
        window_settings = decode_window_extreme_config(grid, config)
        definitions = []
        for feature in WEXT_FEATURES:
            field = window_field(feature, window_settings.extreme_basis)
            fields = ("instrument_id", "session_id", "start_ns", "end_ns", field, "known_at_ns")
            rule = (f"nullable {field}-only BAR on the daily governed grid, instrument id of the grid; "
                    f"{window_settings.period} sessions including the target, one declared adjustment basis")
            offset = feature in (WINDOW_HIGH_OFFSET, WINDOW_LOW_OFFSET)
            definitions.append(DV1Definition(
                feature, ValueType.INT64 if offset else ValueType.FLOAT64, OFFSET_UNIT if offset else "currency/share",
                (InputRequirement("daily", "canonical:1", fields, DataKind.BAR, rule=rule),), _WINDOW_FORMULAS[feature],
                WEXT_ALGORITHM))
        return tuple(definitions)
    if config.identity == ATR_IDENTITY:
        decode_atr_simple_mean_config(grid, config)
        assert config.price_unit is not None
        return (DV1Definition(ATR_MEAN, ValueType.FLOAT64, f"{config.price_unit.currency}/share", atr_requirements(),
                              ATR_FORMULA, ATR_ALGORITHM),)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "DV1 producer is not implemented")


def require_dv1_capability(feature_id: str, capability: str) -> None:
    """Batch only; update, restore and merge are unsupported."""
    if feature_id not in RLOG_FEATURES + WEXT_FEATURES + ATR_FEATURES + CORE_FEATURES:
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown DV1 feature")
    if capability != "batch":
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "output capability is not implemented in this package version")
