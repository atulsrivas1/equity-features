"""EF2 Ichimoku and price-channel configuration identities (ef2-v1): builder and closed decoder over the R17 context."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ConfigSpec, ErrorCode, Parameter, PriceUnit, WindowSpec,
)
from ._context import CONTEXT_SCHEMA, IntradayContext, fail, integer, label

CHANNELS_ALGORITHM = "ef2-channels-v1"
CHANNELS_CONTRACT_VERSION = "ef2-v1"
MAX_SLOTS = 4096
MAX_ATR_PERIOD = 4095  # R17 caps ATR at 4095 (_dispatch.py)
MAX_MULTIPLIER = 1_000_000
_I64 = (-(2**63), 2**63-1)

# Closed operation parameters per homogeneous producer in declaration order (decoded settings keep this order).
CHANNELS_PARAMETERS: dict[str, tuple[str, ...]] = {
    "ichimoku": ("conversion_period", "base_period", "leading_b_period", "displacement"),
    "keltner": ("ema_period", "atr_period", "atr_multiplier_num", "atr_multiplier_den"),
    "donchian": ("period",),
    "pivot_levels": (),
    "band_width_percentile": ("band_period", "band_k_num", "band_k_den", "population_size", "min_population"),
    "bollinger_keltner_squeeze": ("band_period", "band_k_num", "band_k_den", "ema_period", "atr_period",
                                  "atr_multiplier_num", "atr_multiplier_den"),
}
# The convention label names the whole set of choices for that producer; a different choice is a new label.
CHANNELS_CONVENTIONS: dict[str, str] = {
    "ichimoku": "ef2-ichimoku-conv1",
    "keltner": "ef2-keltner-conv1",
    "donchian": "ef2-donchian-conv1",
    "pivot_levels": "ef2-pivot-conv1",
    "band_width_percentile": "ef2-bandpct-conv1",
    "bollinger_keltner_squeeze": "ef2-squeeze-conv1",
}
CHANNELS_IDENTITIES: dict[str, str] = {name: f"ef2.{name}" for name in CHANNELS_PARAMETERS}
_PRODUCER_BY_IDENTITY = {identity: name for name, identity in CHANNELS_IDENTITIES.items()}

# (minimum, maximum) per integer parameter; min_population is additionally bounded by population_size.
_BOUNDS: dict[str, tuple[int, int]] = {
    "conversion_period": (1, MAX_SLOTS), "base_period": (1, MAX_SLOTS), "leading_b_period": (1, MAX_SLOTS),
    "displacement": (1, MAX_SLOTS), "ema_period": (1, MAX_SLOTS), "atr_period": (1, MAX_ATR_PERIOD),
    "period": (1, MAX_SLOTS), "band_period": (2, MAX_SLOTS), "population_size": (1, MAX_SLOTS),
    "min_population": (1, MAX_SLOTS),
    "atr_multiplier_num": (1, MAX_MULTIPLIER), "atr_multiplier_den": (1, MAX_MULTIPLIER),
    "band_k_num": (1, MAX_MULTIPLIER), "band_k_den": (1, MAX_MULTIPLIER),
}
_FRACTIONS = (("atr_multiplier_num", "atr_multiplier_den"), ("band_k_num", "band_k_den"))


@dataclass(frozen=True)
class ChannelsSettings:
    producer: str
    values: tuple[int, ...]
    evidence_limit: int

    def param(self, name: str) -> int:
        return self.values[CHANNELS_PARAMETERS[self.producer].index(name)]

    def multiplier(self, prefix: str) -> Fraction:
        """The reduced rational `<prefix>_num/<prefix>_den` (prefix atr_multiplier or band_k)."""
        return Fraction(self.param(f"{prefix}_num"), self.param(f"{prefix}_den"))


def _check_values(producer: str, values: tuple[int, ...]) -> None:
    """Bounds and cross-parameter rules; every failure is INVALID_CONFIG."""
    names = CHANNELS_PARAMETERS[producer]
    for name, value in zip(names, values):
        low, high = _BOUNDS[name]
        integer(value, low, high, ErrorCode.INVALID_CONFIG)
    given = dict(zip(names, values))
    for numerator, denominator in _FRACTIONS:
        if numerator in given:
            reduced = Fraction(given[numerator], given[denominator])
            if (reduced.numerator, reduced.denominator) != (given[numerator], given[denominator]):
                fail("multiplier must use its reduced canonical fraction")
    if "min_population" in given and given["min_population"] > given["population_size"]:
        fail("min_population must be within 1..population_size")


def _check_convention(producer: str, supplied: object) -> None:
    if type(supplied) is not str:
        fail("exact convention label required")
    if supplied != CHANNELS_CONVENTIONS[producer]:
        fail("unsupported convention_version for this producer", ErrorCode.INCOMPATIBLE_VERSION)


def build_channels_config(context: IntradayContext, *, producer: str,
                          conversion_period: int | None = None, base_period: int | None = None,
                          leading_b_period: int | None = None, displacement: int | None = None,
                          ema_period: int | None = None, atr_period: int | None = None,
                          atr_multiplier_num: int | None = None, atr_multiplier_den: int | None = None,
                          period: int | None = None, band_period: int | None = None,
                          band_k_num: int | None = None, band_k_den: int | None = None,
                          population_size: int | None = None, min_population: int | None = None,
                          availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                          price_unit: PriceUnit, evidence_limit: int = 0,
                          convention_version: str | None = None) -> ConfigSpec:
    """Final ConfigSpec for one producer; exactly that producer's operation parameters, none defaulted.

    convention_version defaults to the producer's single ef2-v1 label; any other value is INCOMPATIBLE_VERSION.
    """
    if type(producer) is not str or producer not in CHANNELS_PARAMETERS:
        fail("producer must be ichimoku, keltner, donchian, pivot_levels, band_width_percentile "
             "or bollinger_keltner_squeeze")
    given = {"conversion_period": conversion_period, "base_period": base_period,
             "leading_b_period": leading_b_period, "displacement": displacement, "ema_period": ema_period,
             "atr_period": atr_period, "atr_multiplier_num": atr_multiplier_num,
             "atr_multiplier_den": atr_multiplier_den, "period": period, "band_period": band_period,
             "band_k_num": band_k_num, "band_k_den": band_k_den, "population_size": population_size,
             "min_population": min_population}
    names = CHANNELS_PARAMETERS[producer]
    if any((given[name] is not None) != (name in names) for name in given):
        fail("exactly the closed operation parameters of the producer are required")
    values = tuple(integer(given[name], *_I64, ErrorCode.INVALID_CONFIG) for name in names)
    return _envelope(context, producer, values, availability, adjustment, price_unit, evidence_limit,
                     CHANNELS_CONVENTIONS[producer] if convention_version is None else convention_version)


def _envelope(context: IntradayContext, producer: str, values: tuple[int, ...], availability: AvailabilitySpec,
              adjustment: AdjustmentSpec, price_unit: PriceUnit, evidence_limit: int,
              convention: object) -> ConfigSpec:
    if (type(context) is not IntradayContext or type(availability) is not AvailabilitySpec
            or type(adjustment) is not AdjustmentSpec or type(price_unit) is not PriceUnit):
        fail("concrete context/timing/action/unit required")
    if context.mode != "reset":
        fail("ef2-v1 supports the anchored reset epoch only; carry is out of v1")
    names = CHANNELS_PARAMETERS[producer]
    _check_values(producer, values)
    integer(evidence_limit, 0, 10000, ErrorCode.INVALID_CONFIG)
    _check_convention(producer, convention)
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
    params: tuple[Parameter, ...] = tuple(Parameter(name, value) for name, value in zip(names, values))
    params += (Parameter("convention_version", CHANNELS_CONVENTIONS[producer]),
               Parameter("evidence_limit", evidence_limit), Parameter("context_schema", CONTEXT_SCHEMA),
               Parameter("context_sha256", context.digest), Parameter("context_chunks", len(chunks)))
    params += tuple(Parameter(f"context_{i:03}", chunk) for i, chunk in enumerate(chunks))
    return ConfigSpec(CHANNELS_IDENTITIES[producer], CHANNELS_ALGORITHM, params, target,
                      WindowSpec(len(context.sessions), target.session_id,
                                 tuple(s.session_id for s in context.sessions), "completed_eod"),
                      availability, adjustment, price_unit)


def decode_channels_config(context: IntradayContext, config: ConfigSpec) -> ChannelsSettings:
    """Validate the closed channels envelope against the supplied context and return its settings."""
    if type(context) is not IntradayContext or type(config) is not ConfigSpec:
        fail("concrete intraday context/config required")
    if context.mode != "reset":
        fail("ef2-v1 supports the anchored reset epoch only; carry is out of v1")
    if config.algorithm_version != CHANNELS_ALGORITHM:
        fail("channels algorithm version differs", ErrorCode.INCOMPATIBLE_VERSION)
    producer = _PRODUCER_BY_IDENTITY.get(config.identity)
    if producer is None:
        fail("not a channels configuration", ErrorCode.INCONSISTENT_IDENTITY)
    values = {p.name: p.value for p in config.parameters}
    count = integer(values.get("context_chunks"), 1, 16, ErrorCode.INVALID_CONFIG)
    names = CHANNELS_PARAMETERS[producer]
    required = ({"convention_version", "evidence_limit", "context_schema", "context_sha256", "context_chunks"}
                | set(names) | {f"context_{i:03}" for i in range(count)})
    if set(values) != required or len(values) != len(config.parameters):
        fail("closed channels parameters required")
    operation = tuple(integer(values[name], *_I64, ErrorCode.INVALID_CONFIG) for name in names)
    _check_values(producer, operation)
    limit = integer(values["evidence_limit"], 0, 10000, ErrorCode.INVALID_CONFIG)
    _check_convention(producer, values["convention_version"])
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
    expected = _envelope(context, producer, operation, config.availability, config.adjustment,
                         config.price_unit, limit, values["convention_version"])
    if config != expected:
        fail("configuration is not the final canonical channels envelope", ErrorCode.INCONSISTENT_IDENTITY)
    return ChannelsSettings(producer, operation, limit)
