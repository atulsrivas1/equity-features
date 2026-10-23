"""Optional EF4 discovery (separate ef4 catalog); the accepted default registry, R17, EF1 to EF3 discovery and the
`describe_intraday` catalog digest are unchanged."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    Capabilities, ConfigSpec, DataKind, ErrorCode, InputRequirement, OutputField, ValueType,
)
from ..ef3._common import fail
from . import _quote as qd
from . import _vwap as vw

_REFERENCE = ("instrument_id", "session_id", "reference_id", "fact_kind", "effective_start_ns", "effective_end_ns",
              "text", "price", "factor_num", "factor_den", "known_at_ns")
_QUOTE = ("instrument_id", "session_id", "event_ns", "order_key", "event_id", "bid", "ask", "bid_size", "ask_size",
          "known_at_ns")
_TRADE = ("instrument_id", "session_id", "event_ns", "order_key", "event_id", "eligible", "price", "size",
          "known_at_ns")
_BAR = ("instrument_id", "session_id", "start_ns", "end_ns", "volume", "actual_notional", "known_at_ns")
_FORMULAS = {
    qd.MAX_SPREAD: "max over valid observations of s = a - b (earliest tie), published s / 10^scale",
    qd.MAX_MIDPOINT_BPS: "max over valid observations of its own 20000 (a - b) / (a + b) (earliest tie)",
    qd.MICRO_LAST: "(b Qa + a Qb) / (Qa + Qb) of the final admitted observation, published / 10^scale",
    qd.MICRO_OFFSET: "10000 (microprice - midpoint) / midpoint of the final admitted observation",
    qd.MICRO_MEAN: "equal-observation mean of the microprice over valid observations with both sizes positive",
    qd.CHANGE_BPS: "10000 (m_last - m_first) / m_first over the first and last valid observations (continuous)",
    qd.CHANGE_SPREAD: "s_last - s_first over the first and last valid observations (continuous)",
    qd.PAIR_COUNT: "adjacent valid-valid pairs in the admitted total order (continuous)",
    qd.CHANGE_COUNT: "adjacent valid-valid pairs whose midpoints differ (continuous)",
    vw.PATH_CHANGE: "10000 (W_n - W_1) / W_1 over the anchored cumulative VWAP path",
    vw.PATH_LAST: "W_n = sum(N) / sum(V) over all path points",
    vw.PATH_MAXIMUM: "max W_k (earliest tie)",
    vw.PATH_MINIMUM: "min W_k (earliest tie)",
    vw.POINT_COUNT: "number of path points (trades, or positive-volume windows)",
    vw.SLOPE_ENDPOINT: "(W_n - W_1) 10^9 / (x_n - x_1) per second",
    vw.SLOPE_OLS: "ordinary least squares slope of W_k on x_k, equal weights, per second",
}


@dataclass(frozen=True)
class QuoteVwapDefinition:
    """Own discovery metadata for one selected EF4 output; batch capability only."""

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


def _facts(role: str, rule: str) -> InputRequirement:
    return InputRequirement(role, "canonical:1", _REFERENCE, DataKind.REFERENCE, rule=rule)


def quote_vwap_definitions(config: ConfigSpec) -> tuple[QuoteVwapDefinition, ...]:
    """Describe the complete executable output set of one configured EF4 producer (lexical order)."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == qd.QUOTE_IDENTITY:
        s = qd.decode_quote_dynamics_config(config)
        requirements = (
            _facts("bounds", "exactly one ef4.interval.bounds fact: the declared half-open interval [S, E)"),
            InputRequirement("quotes", "canonical:1", _QUOTE, DataKind.QUOTE,
                             "continuous" if s.sampling == "continuous" else "sampled_or_continuous",
                             "nullable full bid/ask states in [S, E) before the market cutoff, with the declared "
                             "interval coverage; batch sampling equals the config sampling"))
        names = [f for f in qd.QUOTE_FEATURES if s.sampling == "continuous" or f not in qd.CONTINUOUS_ONLY]
        return tuple(QuoteVwapDefinition(f, qd.FEATURE_META[f][0], qd.FEATURE_META[f][1], requirements, _FORMULAS[f],
                                   qd.QUOTE_ALGORITHM) for f in names)
    if config.identity == vw.VWAP_IDENTITY:
        v = vw.decode_vwap_path_config(config)
        roles: list[InputRequirement] = [
            _facts("bounds", "exactly one ef4.interval.bounds fact: the declared interval and the VWAP anchor S")]
        if v.series_source == "trade":
            roles.append(InputRequirement("trades", "canonical:1", _TRADE, DataKind.TRADE,
                                          rule="nullable ordered trades in [S, E) with an eligibility flag"))
        else:
            roles.append(_facts("grid", f"B+1 ef4.window.edge facts, text {v.grid_version}, first S, last E"))
            roles.append(InputRequirement("bars", "canonical:1", _BAR, DataKind.BAR,
                                          rule="nullable one BAR row per grid slot with volume and actual notional"))
        if v.series_source == "prepared_window":
            roles.append(_facts("proof", f"exactly one ef4.series.proof fact, text {v.series_policy_id}"))
        return tuple(QuoteVwapDefinition(f, vw.FEATURE_META[f][0], vw.FEATURE_META[f][1], tuple(roles), _FORMULAS[f],
                                   vw.VWAP_ALGORITHM) for f in vw.VWAP_FEATURES)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF4 producer is not implemented")


def require_quote_vwap_capability(feature_id: str, capability: str) -> None:
    """Batch only; update, restore and merge are unsupported."""
    if feature_id not in qd.QUOTE_FEATURES + vw.VWAP_FEATURES:
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown EF4 feature")
    if capability != "batch":
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "output capability is not implemented in this package version")
