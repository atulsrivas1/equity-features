"""EF2 momentum configuration identity (ef2-conv1): builder and closed decoder over the R17 context."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ConfigSpec, ErrorCode, Parameter, PriceUnit, WindowSpec,
)
from ._context import CONTEXT_SCHEMA, IntradayContext, fail, integer, label

MOMENTUM_IDENTITY = "intraday.momentum.v1"
MOMENTUM_ALGORITHM = "intraday-momentum-v1"
# The label names the whole convention group; a different choice is a new value and a new label.
MOMENTUM_CONVENTIONS = "ef2-conv1"
MAX_SLOTS = 4096

# Closed per-family period parameters in declaration order (the decoded settings keep this order).
MOMENTUM_PERIODS: dict[str, tuple[str, ...]] = {
    "macd": ("fast_period", "slow_period", "signal_period"),
    "dmi": ("di_period", "adx_period"),
    "stochastic": ("k_period", "k_slowing", "d_period"),
}
# Each convention parameter accepts exactly one value in v1.
MOMENTUM_CONVENTION_VALUES: dict[str, tuple[tuple[str, str], ...]] = {
    "macd": (("ema_seed", "sma_first_n"), ("ema_alpha", "two_over_n_plus_one"),
             ("signal_seed", "sma_first_n_macd"), ("macd_start", "slow_seed_bar"),
             ("numeric_policy", "r17_decimal120_v1")),
    "dmi": (("smoothing", "wilder_average_seeded_by_mean"), ("dm_rule", "strict_greater_zero_on_tie"),
            ("di_scale", "points_0_100"), ("undefined_di_dx", "not_applicable_zero_denominator"),
            ("adx_chain_start", "first_defined_dx"), ("numeric_policy", "r17_decimal120_v1")),
    "stochastic": (("raw_k", "close_location_in_window_including_current"), ("stoch_smoothing", "sma"),
                   ("zero_range", "undefined_not_applicable"),
                   ("oscillator_scale", "points_0_100_williams_minus100_0"),
                   ("numeric_policy", "r17_decimal120_v1")),
}


@dataclass(frozen=True)
class MomentumSettings:
    family: str
    periods: tuple[int, ...]
    evidence_limit: int

    def period(self, name: str) -> int:
        return self.periods[MOMENTUM_PERIODS[self.family].index(name)]


def _check_periods(family: str, values: tuple[int, ...]) -> None:
    """Bounds that need several parameters at once; every failure is INVALID_CONFIG."""
    if family == "macd":
        fast, slow, signal = values
        if not fast < slow or slow + signal - 1 > MAX_SLOTS:
            fail("macd needs fast_period < slow_period and slow_period + signal_period - 1 <= 4096")
    elif family == "dmi":
        if values[0] + values[1] > MAX_SLOTS:
            fail("dmi needs di_period + adx_period <= 4096")
    elif values[0] + values[1] + values[2] - 2 > MAX_SLOTS:
        fail("stochastic needs k_period + k_slowing + d_period - 2 <= 4096")


def _check_conventions(family: str, supplied: dict[str, object]) -> None:
    expected = dict(MOMENTUM_CONVENTION_VALUES[family])
    if set(supplied) != set(expected):
        fail("closed convention parameters required")
    if any(type(value) is not str for value in supplied.values()):
        fail("exact convention labels required")
    if any(supplied[name] != value for name, value in expected.items()):
        fail("unsupported convention value for ef2-conv1", ErrorCode.INCOMPATIBLE_VERSION)


def build_momentum_config(context: IntradayContext, *, family: str,
                          fast_period: int | None = None, slow_period: int | None = None,
                          signal_period: int | None = None, di_period: int | None = None,
                          adx_period: int | None = None, k_period: int | None = None,
                          k_slowing: int | None = None, d_period: int | None = None,
                          availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                          price_unit: PriceUnit, evidence_limit: int = 0,
                          conventions: dict[str, str] | None = None) -> ConfigSpec:
    """Final ConfigSpec for one homogeneous family request; exactly that family's periods, none defaulted.

    conventions defaults to the single ef2-conv1 value of each convention parameter; any other value is
    INCOMPATIBLE_VERSION.
    """
    if type(family) is not str or family not in MOMENTUM_PERIODS:
        fail("momentum family must be macd, dmi or stochastic")
    given = {"fast_period": fast_period, "slow_period": slow_period, "signal_period": signal_period,
             "di_period": di_period, "adx_period": adx_period, "k_period": k_period,
             "k_slowing": k_slowing, "d_period": d_period}
    names = MOMENTUM_PERIODS[family]
    if any((given[name] is not None) != (name in names) for name in given):
        fail("exactly the closed period parameters of the family are required")
    values = tuple(integer(given[name], 1, MAX_SLOTS, ErrorCode.INVALID_CONFIG) for name in names)
    return _envelope(context, family, values, availability, adjustment, price_unit, evidence_limit, conventions)


def _envelope(context: IntradayContext, family: str, values: tuple[int, ...], availability: AvailabilitySpec,
              adjustment: AdjustmentSpec, price_unit: PriceUnit, evidence_limit: int,
              conventions: dict[str, str] | None) -> ConfigSpec:
    if (type(context) is not IntradayContext or type(availability) is not AvailabilitySpec
            or type(adjustment) is not AdjustmentSpec or type(price_unit) is not PriceUnit):
        fail("concrete context/timing/action/unit required")
    if context.mode != "reset":
        fail("ef2-conv1 supports the anchored reset epoch only; carry is out of v1")
    names = MOMENTUM_PERIODS[family]
    _check_periods(family, values)
    integer(evidence_limit, 0, 10000, ErrorCode.INVALID_CONFIG)
    if conventions is not None and type(conventions) is not dict:
        fail("convention mapping required")
    supplied: dict[str, object] = dict(MOMENTUM_CONVENTION_VALUES[family] if conventions is None
                                       else conventions)
    _check_conventions(family, supplied)
    for value in (adjustment.policy_version, adjustment.action_snapshot, adjustment.anchor, price_unit.currency):
        label(value)
    if availability.reconstruction_reason is not None:
        label(availability.reconstruction_reason)
    slots = context.slots()
    target = next(s for s in context.sessions if s.session_id == slots[-1].session_id)
    if not slots[-1].end_ns <= availability.market_cutoff_ns <= target.close_ns:
        fail("target completion/cutoff outside actual session", ErrorCode.BOUNDS)
    text = context.to_json()
    chunks = tuple(text[i:i+4096] for i in range(0, len(text), 4096))
    params: tuple[Parameter, ...] = (Parameter("momentum_family", family),)
    params += tuple(Parameter(name, value) for name, value in zip(names, values))
    params += tuple(Parameter(name, value) for name, value in MOMENTUM_CONVENTION_VALUES[family])
    params += (Parameter("evidence_limit", evidence_limit), Parameter("context_schema", CONTEXT_SCHEMA),
               Parameter("context_sha256", context.digest), Parameter("context_chunks", len(chunks)))
    params += tuple(Parameter(f"context_{i:03}", chunk) for i, chunk in enumerate(chunks))
    return ConfigSpec(MOMENTUM_IDENTITY, MOMENTUM_ALGORITHM, params, target,
                      WindowSpec(len(context.sessions), target.session_id,
                                 tuple(s.session_id for s in context.sessions), "completed_eod"),
                      availability, adjustment, price_unit)


def decode_momentum_config(context: IntradayContext, config: ConfigSpec) -> MomentumSettings:
    """Validate the closed momentum envelope against the supplied context and return its settings."""
    if type(context) is not IntradayContext or type(config) is not ConfigSpec:
        fail("concrete intraday context/config required")
    if config.algorithm_version != MOMENTUM_ALGORITHM:
        fail("momentum algorithm version differs", ErrorCode.INCOMPATIBLE_VERSION)
    if config.identity != MOMENTUM_IDENTITY:
        fail("not a momentum configuration", ErrorCode.INCONSISTENT_IDENTITY)
    values = {p.name: p.value for p in config.parameters}
    count = integer(values.get("context_chunks"), 1, 16, ErrorCode.INVALID_CONFIG)
    family = values.get("momentum_family")
    if type(family) is not str or family not in MOMENTUM_PERIODS:
        fail("momentum family must be macd, dmi or stochastic")
    names = MOMENTUM_PERIODS[family]
    conventions = tuple(name for name, _ in MOMENTUM_CONVENTION_VALUES[family])
    required = ({"momentum_family", "evidence_limit", "context_schema", "context_sha256", "context_chunks"}
                | set(names) | set(conventions) | {f"context_{i:03}" for i in range(count)})
    if set(values) != required or len(values) != len(config.parameters):
        fail("closed momentum parameters required")
    periods = tuple(integer(values[name], 1, MAX_SLOTS, ErrorCode.INVALID_CONFIG) for name in names)
    _check_periods(family, periods)
    limit = integer(values["evidence_limit"], 0, 10000, ErrorCode.INVALID_CONFIG)
    _check_conventions(family, {name: values[name] for name in conventions})
    if values["context_schema"] != CONTEXT_SCHEMA:
        fail("context codec mismatch", ErrorCode.INCOMPATIBLE_VERSION)
    chunks: list[str] = []
    for i in range(count):
        text = values[f"context_{i:03}"]
        if type(text) is not str or not 1 <= len(text) <= 4096 or (i < count-1 and len(text) != 4096):
            fail("canonical bounded context chunks required")
        chunks.append(text)
    if IntradayContext.from_json("".join(chunks)) != context or values["context_sha256"] != context.digest:
        fail("context identity differs", ErrorCode.INCONSISTENT_IDENTITY)
    if config.price_unit is None:
        fail("explicit price unit required", ErrorCode.INVALID_UNIT)
    expected = _envelope(context, family, periods, config.availability, config.adjustment,
                         config.price_unit, limit, None)
    if config != expected:
        fail("configuration is not the final canonical momentum envelope", ErrorCode.INCONSISTENT_IDENTITY)
    return MomentumSettings(family, periods, limit)
