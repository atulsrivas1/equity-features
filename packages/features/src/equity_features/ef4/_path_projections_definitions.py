"""Optional EF4 projection discovery (own catalog); the accepted default registry, R17, EF1, EF2 and EF3 discovery
and every catalog digest are unchanged."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    Capabilities, ConfigSpec, DataKind, ErrorCode, InputRequirement, OutputField, ValueType,
)
from ..ef3._common import CLOSE_FIELDS, DailyGrid, fail
from . import _bar_projection as bp
from . import _rate_projection as rp
from . import _relative_excess as rx
from . import _session_projection as sp

_BAR_FIELDS = ("instrument_id", "session_id", "start_ns", "end_ns", "open", "close", "volume", "actual_notional",
               "known_at_ns")
_REFERENCE = ("instrument_id", "session_id", "reference_id", "fact_kind", "effective_start_ns", "effective_end_ns",
              "text", "price", "known_at_ns")
_FORMULAS = {
    sp.UP_FRACTION: "#(C_i > C_(i-1), i in t-N+1..t) / N over N+1 closes",
    sp.DOWN_FRACTION: "#(C_i < C_(i-1), i in t-N+1..t) / N over N+1 closes",
    sp.DRAWDOWN: "(M - C_t) / M over the N closes ending at t",
    sp.MAX_DRAWDOWN: "largest (R_i - C_i) / R_i, R_i the running maximum of the N closes",
    sp.DISTANCE_FROM_LOW: "(C_t - m) / m over the N closes ending at t",
    sp.CLOSE_VS_SMA: "N C_t / S - 1, S the sum of the N closes",
    sp.CLOSE_ABOVE_SMA: "N C_t > S, strict",
    bp.UP_VOLUME: "sum of volume over epoch bars with close > open",
    bp.DOWN_VOLUME: "sum of volume over epoch bars with close < open",
    bp.UP_VOLUME_FRACTION: "up volume / total volume (zero total is zero_denominator)",
    bp.UP_DOLLAR_VOLUME: "sum of actual notional over up bars (decimal128 coefficient)",
    bp.DOWN_DOLLAR_VOLUME: "sum of actual notional over down bars (decimal128 coefficient)",
    bp.UP_DOLLAR_FRACTION: "up notional / total notional (zero total is zero_denominator)",
    rx.CORE_AGREEMENT: "max(#r>0, #r<0, #r=0) / K over the core benchmark returns",
    rx.CORE_DISPERSION: ("RANGE of core returns (deprecated name), not dispersion; max r_k - min r_k over the core benchmark returns; "
                         "use core.benchmark_return_range_fraction (same value) or core.benchmark_return_stdev_fraction"),
    rp.TRADE_RATE: "count / (window_ns / 1e9)",
    rp.NOTIONAL_RATE: "(notional / 10^scale) / (window_ns / 1e9)",
    rp.SHARE_VOLUME_RATE: "volume / (window_ns / 1e9)",
    rp.RAW_RETURN: "E / S - 1 from the window_start and end witnesses",
    rp.RATE_DIFFERENCE: "(r_A - r_B) / (window_ns / 1e9)",
}


@dataclass(frozen=True)
class EF4PathProjectionsDefinition:
    """Own discovery metadata for one selected EF4 projection output; batch capability only."""

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


def _reqs(items: tuple[tuple[str, DataKind, tuple[str, ...], str], ...]) -> tuple[InputRequirement, ...]:
    return tuple(InputRequirement(role, "canonical:1", fields, kind, rule=rule) for role, kind, fields, rule in items)


def ef4_path_projections_definitions(config: ConfigSpec, *, grid: DailyGrid | bp.BarGrid | None = None,
                                     ) -> tuple[EF4PathProjectionsDefinition, ...]:
    """Describe the complete executable output set of one configured EF4 projection producer (lexical order)."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == sp.SESSION_IDENTITY:
        if type(grid) is not DailyGrid:
            fail(ErrorCode.INVALID_CONFIG, "the daily grid of the configuration is required")
        sp.decode_session_projection_config(grid, config)
        req = _reqs((("daily", DataKind.BAR, CLOSE_FIELDS, "nullable close-only BAR on the daily governed grid"),))
        return tuple(EF4PathProjectionsDefinition(f, sp.SESSION_META[f][0], sp.SESSION_META[f][1], req,
                                                  _FORMULAS[f], sp.SESSION_ALGORITHM) for f in sp.SESSION_FEATURES)
    if config.identity == bp.BAR_IDENTITY:
        if type(grid) is not bp.BarGrid:
            fail(ErrorCode.INVALID_CONFIG, "the bar grid of the configuration is required")
        bp.decode_bar_projection_config(grid, config)
        req = _reqs((("bars", DataKind.BAR, _BAR_FIELDS, "nullable BAR delivery of the reset epoch on the bar grid"),))
        return tuple(EF4PathProjectionsDefinition(f, bp.BAR_META[f][0], bp.BAR_META[f][1], req, _FORMULAS[f],
                                                  bp.BAR_ALGORITHM) for f in bp.BAR_FEATURES)
    if config.identity == rx.RELATIVE_IDENTITY:
        s = rx.decode_relative_excess_config(config)
        names = [f for f in rx.RELATIVE_FEATURES if _relative_configured(f, s)]
        req = _reqs((("legs", DataKind.REFERENCE, _REFERENCE, "nullable ef4.leg.start|end facts"),
                     ("membership", DataKind.REFERENCE, _REFERENCE,
                      "nullable ef4.sector.membership fact (sector outputs only)")))
        return tuple(EF4PathProjectionsDefinition(f, rx.RELATIVE_META[f][0], rx.RELATIVE_META[f][1], req,
                                                  _FORMULAS.get(f, "r_instrument - r_benchmark, r = E / S - 1"),
                                                  rx.RELATIVE_ALGORITHM) for f in names)
    if config.identity == rp.RATE_IDENTITY:
        s2 = rp.decode_rate_projection_config(config)
        names = [f for f in rp.RATE_FEATURES
                 if (f not in (rp.RAW_RETURN, rp.RATE_DIFFERENCE) or s2.alignment_tolerance_ns is not None)
                 and (f != rp.RATE_DIFFERENCE or s2.adjacency is not None)]
        req = _reqs((("tape", DataKind.REFERENCE, _REFERENCE, "nullable ef4.tape.count|volume|notional facts"),
                     ("legs", DataKind.REFERENCE, _REFERENCE, "nullable ef4.leg.start|end facts (window_start)")))
        return tuple(EF4PathProjectionsDefinition(f, rp.RATE_META[f][0], rp.RATE_META[f][1], req, _FORMULAS[f],
                                                  rp.RATE_ALGORITHM) for f in names)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF4 projection producer is not implemented")


def _relative_configured(feature: str, s: rx.RelativeExcessSettings) -> bool:
    if feature.startswith("core."):
        return s.core_benchmark_ids is not None
    role = feature.split(".")[2]
    present = {"primary": s.primary_benchmark_id, "secondary": s.secondary_benchmark_id,
               "sector": s.sector_benchmark_id}[role] is not None
    return present and (s.window_ns is not None or "prior_close" in feature)


def require_ef4_path_projections_capability(feature_id: str, capability: str) -> None:
    """Batch only; update, restore and merge are unsupported."""
    if feature_id not in (sp.SESSION_FEATURES + bp.BAR_FEATURES + rx.RELATIVE_FEATURES + rp.RATE_FEATURES):
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown EF4 projection feature")
    if capability != "batch":
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "output capability is not implemented in this package version")
