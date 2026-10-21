"""Optional EF1 discovery; the accepted default registry remains unchanged."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    Capabilities, ConfigSpec, DataKind, InputRequirement, OutputField, ValueType,
)
from ._context import decode_ef1_context


@dataclass(frozen=True)
class EF1Definition:
    """Own non-transport metadata: existing FeatureDefinition restricts built-in IDs."""

    feature_id: str
    dtype: ValueType
    unit: str
    requirements: tuple[InputRequirement, ...]
    formula: str
    algorithm_version: str = "v1"
    schema_version: str = "1"
    capabilities: Capabilities = Capabilities(batch=True)

    @property
    def outputs(self) -> tuple[OutputField, ...]:
        return (OutputField("value", self.dtype.value, self.unit),)


def ef1_definitions(config: ConfigSpec) -> tuple[EF1Definition, ...]:
    """Describe the complete selected executable producer; unsupported producers fail."""
    context = decode_ef1_context(config)
    if context["producer"] == "clock":
        requirements = (InputRequirement("calendar_provenance", "canonical:1",
                        ("reference_id", "fact_kind", "effective_start_ns", "effective_end_ns",
                         "text", "known_at_ns"), DataKind.REFERENCE,
                        rule="actual causal finite supplied-calendar hash declaration"),)
        return (
            EF1Definition("session.clock.early_close", ValueType.BOOL, "boolean", requirements,
                          "actual_close < supplied_scheduled_close; equal to SessionSpec declaration"),
            EF1Definition("session.clock.phase", ValueType.STRING, "state", requirements,
                          "supplied half-open segment containing C, otherwise closed"),
            EF1Definition("session.clock.regular_elapsed_ns", ValueType.INT64, "ns", requirements,
                          "clamp(C-open,0,close-open)"),
            EF1Definition("session.clock.regular_fraction", ValueType.FLOAT64, "fraction", requirements,
                          "clamp(C-open,0,close-open)/(close-open)"),
            EF1Definition("session.clock.regular_remaining_ns", ValueType.INT64, "ns", requirements,
                          "close-open-clamp(C-open,0,close-open)"),
        )
    trades = context["selection"]["mode"] == "trades"
    primary = InputRequirement("trades" if trades else "bars", "canonical:1",
                               ("price", "size") if trades else ("volume", "actual_notional"),
                               DataKind.TRADE if trades else DataKind.BAR,
                               rule="exact supplied positive-duration anchor window; field-independent readiness")
    proof = InputRequirement("anchor_provenance", "canonical:1",
                             ("reference_id", "fact_kind", "effective_start_ns", "text", "known_at_ns"),
                             DataKind.REFERENCE, rule="actual causal supplied anchor hash declaration")
    requirements = (primary, proof)
    return (
        EF1Definition("session.anchor.notional", ValueType.DECIMAL128, "currency", requirements,
                      "N=sum(price_coefficient*shares) or actual_notional; coefficient at PriceUnit.scale"),
        EF1Definition("session.anchor.volume", ValueType.INT64, "shares", requirements, "V=sum(shares)"),
        EF1Definition("session.anchor.vwap", ValueType.FLOAT64, "currency/share", requirements,
                      "N/(V*10**PriceUnit.scale), undefined for V=0"),
    )
