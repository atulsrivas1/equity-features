"""EF5 price-structure configuration identities (ef5-candle1, ef5-structure1, ef5-technical1) over the R17 context.

One closed envelope per producer: every parameter, the adjustment label and the adjustment policy version are required
(no default anywhere), the shared AdjustmentSpec defaults are never read, and the label/policy pairing is normative:
`unadjusted` is the shared basis `raw` with policy `raw-v1`, `split_adjusted` is the shared basis `split` with policy
`split-factors-v1` and a declared action snapshot and anchor. Any other label (including the shared `total_return`)
is UNSUPPORTED_ADJUSTMENT. Currency is the three-letter uppercase rule of EF5 admission (not a shared rule).
"""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ConfigSpec, ErrorCode, Parameter, PriceUnit, WindowSpec,
)
from ._context import CONTEXT_SCHEMA, IntradayContext, fail, integer, label

SESSION_RESET = "session_reset"
GOVERNED_HISTORY = "governed_history"
EF5_PROFILES = (GOVERNED_HISTORY, SESSION_RESET)
# The epoch profile fixes the R17 context mode (session_reset: reset; governed_history: carry).
_MODE = {SESSION_RESET: "reset", GOVERNED_HISTORY: "carry"}
GOVERNED_SPAN_MAX = 63  # ruling E4: a governed_history span above 63 can never be available
# EF5 label -> (shared basis, normative policy version)
ADJUSTMENT_LABELS = {"unadjusted": ("raw", "raw-v1"), "split_adjusted": ("split", "split-factors-v1")}
_COMMON = ("policy_version", "epoch_profile", "evidence_limit", "adjustment", "adjustment_policy_version")


@dataclass(frozen=True)
class Producer:
    name: str
    identity: str
    algorithm: str
    policy: str
    params: tuple[str, ...]


PRODUCERS = {
    "candle": Producer("candle", "ef5.candle", "ef5-candle-v1", "ef5-candle1", ("doji_body_max_fraction",)),
    "structure": Producer("structure", "ef5.structure", "ef5-structure-v1", "ef5-structure1",
                          ("swing_strength", "lookback")),
    "technical": Producer("technical", "ef5.technical", "ef5-technical-v1", "ef5-technical1",
                          ("trend_window", "trend_count")),
}


@dataclass(frozen=True)
class Ef5Settings:
    producer: str
    policy_version: str
    epoch_profile: str
    evidence_limit: int
    adjustment_label: str
    adjustment_policy_version: str
    doji: tuple[int, int] | None = None
    swing_strength: int | None = None
    lookback: int | None = None
    trend_window: int | None = None
    trend_count: int | None = None


def _positive(text: str) -> int | None:
    """A plain positive decimal integer of at most 18 digits (no sign, no leading zero), else None."""
    if not 1 <= len(text) <= 18 or text[0] == "0" or any(c not in "0123456789" for c in text):
        return None
    return int(text)


def _currency(text: object) -> bool:
    return type(text) is str and len(text) == 3 and all("A" <= c <= "Z" for c in text)


def _unit(unit: object) -> None:
    if (type(unit) is not PriceUnit or type(unit.scale) is not int or not 0 <= unit.scale <= 18
            or not _currency(unit.currency)):
        fail("explicit price unit with scale 0..18 and a three-letter uppercase currency required",
             ErrorCode.INVALID_UNIT)


def _adjustment(label_text: object, policy: object) -> tuple[str, str]:
    """Label presence is INVALID_CONFIG; vocabulary and pairing faults are UNSUPPORTED_ADJUSTMENT."""
    if type(label_text) is not str:
        fail("adjustment label must be declared (unadjusted or split_adjusted)")
    if label_text not in ADJUSTMENT_LABELS:
        fail("adjustment label outside the v1 vocabulary", ErrorCode.UNSUPPORTED_ADJUSTMENT)
    if type(policy) is not str or policy != ADJUSTMENT_LABELS[label_text][1]:
        fail("adjustment_spec.policy_version must be declared and paired with the label",
             ErrorCode.UNSUPPORTED_ADJUSTMENT)
    return label_text, policy


def _check(producer: Producer, values: dict[str, object]) -> Ef5Settings:
    """Shape and range faults are INVALID_CONFIG; adjustment faults UNSUPPORTED_ADJUSTMENT; the label is checked last."""
    if set(values) != set(_COMMON) | set(producer.params):
        fail("closed parameter set required (no defaults, no extras)")
    profile = values["epoch_profile"]
    if type(profile) is not str or profile not in EF5_PROFILES:
        fail("epoch_profile must be session_reset or governed_history")
    limit = integer(values["evidence_limit"], 0, 10000, ErrorCode.INVALID_CONFIG)
    extra: dict[str, object] = {}
    if producer.name == "candle":
        text = values["doji_body_max_fraction"]
        parts = text.split("/") if type(text) is str else []
        p, q = (_positive(part) for part in parts) if len(parts) == 2 else (None, None)
        if p is None or q is None or p > q:
            fail("doji_body_max_fraction must be p/q with 1 <= p <= q")
        extra["doji"] = (p, q)
    elif producer.name == "structure":
        k = integer(values["swing_strength"], 1, 64, ErrorCode.INVALID_CONFIG)
        extra["swing_strength"] = k
        extra["lookback"] = integer(values["lookback"], 2 * k, 4096, ErrorCode.INVALID_CONFIG)
    else:
        extra["trend_window"] = integer(values["trend_window"], 1, 1024, ErrorCode.INVALID_CONFIG)
        extra["trend_count"] = integer(values["trend_count"], 1, 256, ErrorCode.INVALID_CONFIG)
    adjustment_label, policy = _adjustment(values["adjustment"], values["adjustment_policy_version"])
    version = values["policy_version"]
    if type(version) is not str:
        fail("exact policy label required")
    return Ef5Settings(producer.name, version, profile, limit, adjustment_label, policy, **extra)  # type: ignore[arg-type]


def _version(producer: Producer, settings: Ef5Settings) -> None:
    if settings.policy_version != producer.policy:
        fail("unsupported EF5 policy label", ErrorCode.INCOMPATIBLE_VERSION)


def _values(settings: Ef5Settings) -> dict[str, object]:
    values: dict[str, object] = {
        "policy_version": settings.policy_version, "epoch_profile": settings.epoch_profile,
        "evidence_limit": settings.evidence_limit, "adjustment": settings.adjustment_label,
        "adjustment_policy_version": settings.adjustment_policy_version}
    if settings.producer == "candle":
        assert settings.doji is not None
        values["doji_body_max_fraction"] = f"{settings.doji[0]}/{settings.doji[1]}"
    elif settings.producer == "structure":
        values["swing_strength"], values["lookback"] = settings.swing_strength, settings.lookback
    else:
        values["trend_window"], values["trend_count"] = settings.trend_window, settings.trend_count
    return values


def _shared_adjustment(settings: Ef5Settings, adjustment: AdjustmentSpec) -> None:
    basis, policy = ADJUSTMENT_LABELS[settings.adjustment_label]
    if adjustment.basis != basis or adjustment.policy_version != policy:
        fail("AdjustmentSpec differs from the declared label and policy", ErrorCode.UNSUPPORTED_ADJUSTMENT)


def build_ef5_config(producer: str, context: IntradayContext, *, availability: AvailabilitySpec,
                     adjustment: AdjustmentSpec, price_unit: PriceUnit | None,
                     policy_version: object = None, epoch_profile: object = None, evidence_limit: object = None,
                     adjustment_label: object = None, adjustment_policy_version: object = None,
                     **parameters: object) -> ConfigSpec:
    """Final ConfigSpec for one EF5 producer; every value has no default (None is a missing declaration)."""
    spec = PRODUCERS.get(producer)
    if spec is None:
        fail("unknown EF5 producer", ErrorCode.UNKNOWN_FEATURE)
    if (type(context) is not IntradayContext or type(availability) is not AvailabilitySpec
            or type(adjustment) is not AdjustmentSpec):
        fail("concrete context, timing and action required")
    _unit(price_unit)
    assert price_unit is not None
    values: dict[str, object] = {
        "policy_version": policy_version, "epoch_profile": epoch_profile, "evidence_limit": evidence_limit,
        "adjustment": adjustment_label, "adjustment_policy_version": adjustment_policy_version}
    values.update({name: parameters.pop(name, None) for name in spec.params})
    values.update(parameters)  # any surplus name fails the closed-set check
    settings = _check(spec, values)
    _shared_adjustment(settings, adjustment)
    _version(spec, settings)
    if context.mode != _MODE[settings.epoch_profile]:
        fail("epoch_profile and R17 context mode disagree (session_reset: reset; governed_history: carry)")
    slots = context.slots()
    if settings.epoch_profile == GOVERNED_HISTORY and len(slots) != len(context.sessions):
        fail("governed_history needs one governed slot per session")
    for value in (adjustment.policy_version, adjustment.action_snapshot, adjustment.anchor, price_unit.currency):
        label(value)
    if availability.reconstruction_reason is not None:
        label(availability.reconstruction_reason)
    target = next(s for s in context.sessions if s.session_id == slots[-1].session_id)
    # A target bar may still be forming at the market cutoff (future_market); no earlier bar may be.
    if not slots[-1].start_ns <= availability.market_cutoff_ns <= target.close_ns:
        fail("market cutoff outside the target slot and session", ErrorCode.BOUNDS)
    text = context.to_json()
    chunks = tuple(text[i:i+4096] for i in range(0, len(text), 4096))
    ordered = (*_COMMON, *spec.params)
    params: tuple[Parameter, ...] = tuple(Parameter(name, _values(settings)[name]) for name in ordered) + (  # type: ignore[arg-type]
        Parameter("context_schema", CONTEXT_SCHEMA), Parameter("context_sha256", context.digest),
        Parameter("context_chunks", len(chunks)))
    params += tuple(Parameter(f"context_{i:03}", chunk) for i, chunk in enumerate(chunks))
    return ConfigSpec(spec.identity, spec.algorithm, params, target,
                      WindowSpec(len(context.sessions), target.session_id,
                                 tuple(s.session_id for s in context.sessions), "completed_eod"),
                      availability, adjustment, price_unit)


def decode_ef5_config(producer: str, context: IntradayContext, config: ConfigSpec) -> Ef5Settings:
    """Validate the closed envelope against the supplied context and return the settings."""
    spec = PRODUCERS.get(producer)
    if spec is None:
        fail("unknown EF5 producer", ErrorCode.UNKNOWN_FEATURE)
    if type(context) is not IntradayContext or type(config) is not ConfigSpec:
        fail("concrete intraday context/config required")
    if config.algorithm_version != spec.algorithm:
        fail("EF5 algorithm version differs", ErrorCode.INCOMPATIBLE_VERSION)
    if config.identity != spec.identity:
        fail("not this EF5 producer's configuration", ErrorCode.INCONSISTENT_IDENTITY)
    named = {p.name: p.value for p in config.parameters}
    count = integer(named.get("context_chunks"), 1, 16, ErrorCode.INVALID_CONFIG)
    context_keys = {"context_schema", "context_sha256", "context_chunks"} | {f"context_{i:03}" for i in range(count)}
    values: dict[str, object] = {k: v for k, v in named.items() if k not in context_keys}
    if set(named) < context_keys:
        fail("closed EF5 parameters required")
    settings = _check(spec, values)
    _unit(config.price_unit)
    _shared_adjustment(settings, config.adjustment)
    _version(spec, settings)
    if named["context_schema"] != CONTEXT_SCHEMA:
        fail("context codec mismatch", ErrorCode.INCOMPATIBLE_VERSION)
    chunks: list[str] = []
    for i in range(count):
        text = named[f"context_{i:03}"]
        if type(text) is not str or not 1 <= len(text) <= 4096 or (i < count-1 and len(text) != 4096):
            fail("canonical bounded context chunks required")
        chunks.append(text)
    if IntradayContext.from_json("".join(chunks)) != context or named["context_sha256"] != context.digest:
        fail("context identity differs", ErrorCode.INCONSISTENT_IDENTITY)
    expected = build_ef5_config(
        producer, context, availability=config.availability, adjustment=config.adjustment,
        price_unit=config.price_unit, **{("adjustment_label" if k == "adjustment" else k): v
                                         for k, v in _values(settings).items()})
    if config != expected:
        fail("configuration is not the final canonical EF5 envelope", ErrorCode.INCONSISTENT_IDENTITY)
    return settings


def span_check(settings: Ef5Settings, spans: dict[str, int | None]) -> None:
    """Ruling E4: under governed_history a selected output whose span exceeds 63 (or is undefined) is INVALID_CONFIG."""
    if settings.epoch_profile != GOVERNED_HISTORY:
        return
    for span in spans.values():
        if span is None or span > GOVERNED_SPAN_MAX:
            fail("governed_history span above 63 or undefined for the selected output")
