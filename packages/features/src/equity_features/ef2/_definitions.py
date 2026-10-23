"""Optional EF2 discovery; the accepted default registry and the EF1 discovery remain unchanged."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    Capabilities, ConfigSpec, DataKind, ErrorCode, InputRequirement, OutputField, ValueType,
)
from ._retracement import (
    FEATURE_ID, RETRACEMENT_ALGORITHM, RETRACEMENT_IDENTITY, ROLES, decode_retracement_config, fail,
)

_FIELDS = ("reference_id", "fact_kind", "effective_start_ns", "effective_end_ns", "text", "price",
           "factor_num", "factor_den", "known_at_ns")


@dataclass(frozen=True)
class EF2Definition:
    """Own discovery metadata for one selected EF2 producer output; batch capability only."""

    feature_id: str
    dtype: ValueType
    unit: str
    requirements: tuple[InputRequirement, ...]
    formula: str
    algorithm_version: str = RETRACEMENT_ALGORITHM
    schema_version: str = "1"
    capabilities: Capabilities = Capabilities(batch=True)

    @property
    def outputs(self) -> tuple[OutputField, ...]:
        return (OutputField("value", self.dtype.value, self.unit),)


def ef2_definitions(config: ConfigSpec) -> tuple[EF2Definition, ...]:
    """Describe the complete selected executable EF2 producer; unsupported producers fail."""
    if type(config) is not ConfigSpec or config.identity != RETRACEMENT_IDENTITY:
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF2 producer is not implemented")
    settings = decode_retracement_config(config)
    requirements = tuple(InputRequirement(role, "canonical:1", _FIELDS, DataKind.REFERENCE,
        rule="fixed nullable role; one exact integer-coefficient prior-window extremum row from the extrema owner")
        for role in ROLES)
    formula = ("(H - r*(H-L))/10**scale" if settings.direction == "from_high" else "(L + r*(H-L))/10**scale")
    return (EF2Definition(FEATURE_ID, ValueType.FLOAT64, "currency/share", requirements,
                          formula + "; r = ratio_num/ratio_den exact, one final binary64 rounding"),)


def require_ef2_capability(feature_id: str, capability: str) -> None:
    """Batch only; update, restore and merge are unsupported."""
    if feature_id != FEATURE_ID:
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown EF2 feature")
    if capability != "batch":
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "output capability is not implemented in this package version")
