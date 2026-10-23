"""Optional EF4 tape discovery (own catalog); the accepted default registry, R17, EF1, EF2 and EF3 are unchanged.

Discovery here is separate from `describe_intraday()` and the core session registry, so no existing catalog digest or
accepted header changes. The window producer is batch only; the notional top-K is batch and conditional merge.
"""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    Capabilities, ConfigSpec, DataKind, ErrorCode, InputRequirement, OutputField, ValueType,
)
from equity_features.ef3._common import fail
from . import _tape_topk as tk
from . import _tape_window as tw
from ._tape_common import require_batch_capability

_TRADE_FIELDS = ("instrument_id", "session_id", "event_ns", "order_key", "event_id", "eligible", "price", "size",
                 "condition", "known_at_ns")
_REFERENCE_FIELDS = ("instrument_id", "session_id", "reference_id", "fact_kind", "effective_start_ns",
                     "effective_end_ns", "text", "price", "factor_num", "factor_den", "known_at_ns")
_FORMULAS = {
    tw.COUNT: "#(eligible prints in [C - W, C))",
    tw.VOLUME: "sum of sizes of the eligible prints in [C - W, C)",
    tw.NOTIONAL: "sum of price * size over the eligible prints in [C - W, C)",
    tw.UP: "sum of sizes of in-window prints with tick sign +1",
    tw.DOWN: "sum of sizes of in-window prints with tick sign -1",
    tw.NEUTRAL: "sum of sizes of in-window prints with tick sign 0",
    tw.NET_VOLUME: "up_volume - down_volume",
    tw.NET_NOTIONAL: "sum of sign * price * size over the in-window prints",
    tw.IMBALANCE: "net_volume / window volume (zero volume is zero_denominator); one rounding",
    tk.TOP_K_FEATURE: "first min(K, n) eligible prints by (-price * size, event_ns, order_key, event_id)",
}


@dataclass(frozen=True)
class EF4TapeDefinition:
    """Own discovery metadata for one selected EF4 tape output."""

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


def _trades() -> InputRequirement:
    return InputRequirement("trades", "canonical:1", _TRADE_FIELDS, DataKind.TRADE,
                            rule="nullable ordered TRADE rows of the target entity and session in [open, C)")


def _seed() -> InputRequirement:
    return InputRequirement("seed", "canonical:1", _REFERENCE_FIELDS, DataKind.REFERENCE,
                            rule="nullable ef4.tick.seed fact, delivered exactly when seed_policy is supplied")


def ef4_tape_definitions(config: ConfigSpec) -> tuple[EF4TapeDefinition, ...]:
    """Describe the complete executable output set of one configured EF4 tape producer (lexical order)."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == tw.TAPE_IDENTITY:
        tw.decode_tape_window_config(config)
        return tuple(EF4TapeDefinition(
            f, tw.FEATURE_META[f][0], tw.FEATURE_META[f][1],
            (_trades(),) if f in tw.WINDOW_CLASS else (_trades(), _seed()), _FORMULAS[f], tw.TAPE_ALGORITHM)
            for f in tw.TAPE_FEATURES)
    if config.identity == tk.TOP_K_IDENTITY:
        tk.decode_notional_top_k_config(config)
        return (EF4TapeDefinition(tk.TOP_K_FEATURE, ValueType.TOP_K_TRADES, tk.TOP_K_UNIT, (_trades(),),
                                  _FORMULAS[tk.TOP_K_FEATURE], tk.TOP_K_ALGORITHM,
                                  capabilities=Capabilities(batch=True, merge=True)),)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF4 tape producer is not implemented")


def require_ef4_tape_capability(feature_id: str, capability: str) -> None:
    """Window outputs: batch only. Notional top-K: batch and merge; update and restore are unsupported."""
    if feature_id in tk.TOP_K_FEATURES:
        require_batch_capability(feature_id, capability, tk.TOP_K_FEATURES, ("batch", "merge"))
    else:
        require_batch_capability(feature_id, capability, tw.TAPE_FEATURES, ("batch",))
