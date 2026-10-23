"""Optional EF3 breadth discovery; the accepted default registry, R17, EF1, EF2 and the other EF3 discovery are unchanged."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    Capabilities, ConfigSpec, DataKind, ErrorCode, InputRequirement, OutputField, ValueType,
)
from . import _adaptive as ad
from . import _breadth as br
from . import _observed as ob
from ._common import fail

_REFERENCE = ("instrument_id", "session_id", "reference_id", "fact_kind", "effective_start_ns", "effective_end_ns",
              "text", "price", "factor_num", "factor_den", "known_at_ns")
_ROLE_RULES = {
    "population": "nullable ef3.population.member (static_snapshot) or ef3.breadth.membership_interval facts",
    "prior_reference_availability": "nullable ef3.member.prior_reference.available|unavailable facts",
    "current_return": "nullable ef3.member.current_return facts (sign only, price column)",
    "cumulative_volume": "nullable ef3.member.cumulative_volume facts (shares, price column)",
    "endpoint_price": "nullable ef3.member.endpoint_price facts (positive coefficient)",
    "vwap": "nullable ef3.member.vwap (exact notional over volume) or ef3.member.vwap.unavailable facts",
    "momentum": "nullable ef3.member.momentum facts (sign only)",
    "selected_high": "nullable ef3.member.selected_high facts",
    "selected_low": "nullable ef3.member.selected_low facts",
    "members": "nullable ef3.observed.member roster facts (text is the group label)",
    "change": "nullable ef3.observed.change facts (sign only)",
    "qualifier_price": "nullable ef3.observed.qualifier_price facts",
    "qualifier_volume": "nullable ef3.observed.qualifier_volume facts (shares)",
    "observations": "nullable ef3.adaptive.rate facts (raw rate in shares per second)",
}
_FORMULAS = {
    br.ABOVE_VWAP: "#(endpoint > vwap, strict, exact) / N",
    br.ADVANCE_DECLINE: "A / D (zero D is zero_denominator)",
    br.ADVANCING: "#(prior available and return > 0)",
    br.DECLINING: "#(prior available and return < 0)",
    br.DIRECTION_NET: "A - D",
    br.DOWN_VOLUME: "sum of cumulative volume over declining members",
    br.LATEST_EVENT: "maximum member endpoint event time (or C-1 when saturated)",
    br.NEAR_HIGH: "#(H - E <= t (H - L)) / N, inclusive, H = L not near",
    br.NEAR_LOW: "#(E - L <= t (H - L)) / N, inclusive, H = L not near",
    br.POSITIVE_MOMENTUM: "#(momentum > 0) / N",
    br.PRIOR_COVERAGE: "#(prior reference available) / N",
    br.PRIOR_ELIGIBLE: "#(prior reference available)",
    br.SELECTED_COUNT: "N declared members at the market cutoff",
    br.UNCHANGED: "#(prior available and return = 0)",
    br.UP_DOWN_RATIO: "up volume / down volume (zero down is zero_denominator)",
    br.UP_VOLUME: "sum of cumulative volume over advancing members",
    ob.ADVANCE_FRACTION: "advancing / qualifying",
    ob.ADVANCING_COUNT: "#(qualifies and change > 0)",
    ob.NONADVANCING_COUNT: "qualifying - advancing",
    ob.OBSERVED_COUNT: "records observed before the cutoff in scope",
    ob.QUALIFYING_FRACTION: "qualifying / observed",
    ob.QUALIFYING_COUNT: "#(price >= floor price and volume >= floor volume)",
    ob.UNKNOWN_COUNT: "#(members whose qualification or advance is unknown)",
    ad.ACCELERATION_COUNT: "scorable observations with a defined relative acceleration",
    ad.BASELINE_AVAILABLE: "observations >= W",
    ad.BASELINE_RATE: "B_n with B_1 = r_1, B_k = (tau B_(k-1) + d_k r_k) / (tau + d_k)",
    ad.LATEST_EVENT: "event time of the last in-scope observation",
    ad.OBSERVATION_COUNT: "known in-scope observations",
    ad.PEAK_ACCELERATION: "max over scorable k of (r_k - r_(k-1)) 1e9 / (d_k B_(k-1))",
    ad.PEAK_ACCELERATION_NS: "event time of the earliest observation attaining the peak acceleration",
    ad.PEAK_RATE: "max over scorable k of r_k / B_(k-1)",
    ad.PEAK_RATE_NS: "event time of the earliest observation attaining the peak relative rate",
    ad.SCORED_COUNT: "scorable observations with a defined relative rate",
}


@dataclass(frozen=True)
class EF3BreadthDefinition:
    """Own discovery metadata for one selected EF3 breadth or adaptive volume output; batch capability only."""

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


def _reqs(roles: tuple[str, ...]) -> tuple[InputRequirement, ...]:
    return tuple(InputRequirement(role, "canonical:1", _REFERENCE, DataKind.REFERENCE, rule=_ROLE_RULES[role])
                 for role in roles)


def ef3_breadth_definitions(config: ConfigSpec) -> tuple[EF3BreadthDefinition, ...]:
    """Describe the complete executable output set of one configured EF3 breadth producer (lexical order)."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == br.BREADTH_IDENTITY:
        s = br.decode_session_breadth_config(config)
        names = [f for f in br.BREADTH_FEATURES if (f != br.NEAR_HIGH or s.near_high is not None)
                 and (f != br.NEAR_LOW or s.near_low is not None)]
        return tuple(EF3BreadthDefinition(f, br.FEATURE_META[f][0], br.FEATURE_META[f][1],
                                          _reqs(br.FEATURE_ROLES[f]), _FORMULAS[f], br.BREADTH_ALGORITHM)
                     for f in names)
    if config.identity == ob.OBSERVED_IDENTITY:
        ob.decode_observed_breadth_config(config)
        return tuple(EF3BreadthDefinition(f, ob.FEATURE_META[f][0], ob.FEATURE_META[f][1],
                                          _reqs(ob.FEATURE_ROLES[f]), _FORMULAS[f], ob.OBSERVED_ALGORITHM)
                     for f in ob.OBSERVED_FEATURES)
    if config.identity == ad.ADAPTIVE_IDENTITY:
        ad.decode_adaptive_volume_config(config)
        return tuple(EF3BreadthDefinition(f, ad.FEATURE_META[f][0], ad.FEATURE_META[f][1],
                                          _reqs(("observations",)), _FORMULAS[f], ad.ADAPTIVE_ALGORITHM)
                     for f in ad.ADAPTIVE_FEATURES)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF3 producer is not implemented")


def require_ef3_breadth_capability(feature_id: str, capability: str) -> None:
    """Batch only; update, restore and merge are unsupported."""
    if feature_id not in br.BREADTH_FEATURES + ob.OBSERVED_FEATURES + ad.ADAPTIVE_FEATURES:
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown EF3 breadth feature")
    if capability != "batch":
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "output capability is not implemented in this package version")
