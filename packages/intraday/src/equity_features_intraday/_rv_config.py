"""EF3 intraday realized-variance configuration identity (ef3-rv1): builder and closed decoder over the R17 context."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ConfigSpec, ErrorCode, Parameter, PriceUnit, WindowSpec,
)
from ._context import CONTEXT_SCHEMA, IntradayContext, fail, integer, label

REALIZED_VARIANCE_IDENTITY = "ef3.intraday_realized_variance"
REALIZED_VARIANCE_ALGORITHM = "ef3-realized-variance-v1"
# A label names the whole convention set (uncentered sum of squared log returns, reset epoch with the first bar
# as base only, strict completeness, one return minimum, variance unannualized, volatility sqrt(A RV)).
# A different convention is a different label, never a silent change.
REALIZED_VARIANCE_POLICY = "ef3-rv1"
REALIZED_VARIANCE_SAMPLING = "every_governed_slot"
_I64_MAX = 2**63-1


@dataclass(frozen=True)
class RealizedVarianceSettings:
    policy_version: str
    sampling: str
    annualization_factor: int | None
    evidence_limit: int


def _check(policy: object, sampling: object, factor: object, limit: object) -> RealizedVarianceSettings:
    if type(policy) is not str:
        fail("exact realized-variance policy label required")
    if policy != REALIZED_VARIANCE_POLICY:
        fail("unsupported realized-variance policy label", ErrorCode.INCOMPATIBLE_VERSION)
    if type(sampling) is not str:
        fail("exact sampling convention required (there is no default)")
    if sampling != REALIZED_VARIANCE_SAMPLING:
        fail("only every_governed_slot sampling is supported; no resampling or subsampling",
             ErrorCode.UNSUPPORTED_SAMPLING)
    annualization = None if factor is None else integer(factor, 1, _I64_MAX, ErrorCode.INVALID_CONFIG)
    return RealizedVarianceSettings(policy, sampling, annualization,
                                    integer(limit, 0, 10000, ErrorCode.INVALID_CONFIG))


def build_realized_variance_config(context: IntradayContext, *, policy_version: str | None = None,
                                   sampling: str | None = None, annualization_factor: int | None = None,
                                   availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                                   price_unit: PriceUnit, evidence_limit: int = 0) -> ConfigSpec:
    """Final ConfigSpec; annualization_factor is present exactly when intraday.realized_volatility is selected."""
    if (type(context) is not IntradayContext or type(availability) is not AvailabilitySpec
            or type(adjustment) is not AdjustmentSpec or type(price_unit) is not PriceUnit):
        fail("concrete context/timing/action/unit required")
    settings = _check(policy_version, sampling, annualization_factor, evidence_limit)
    if context.mode != "reset":
        fail("ef3-rv1 supports the anchored reset epoch only; carry is out of v1")
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
    params: tuple[Parameter, ...] = (Parameter("policy_version", settings.policy_version),
              Parameter("sampling", settings.sampling), Parameter("evidence_limit", settings.evidence_limit),
              Parameter("context_schema", CONTEXT_SCHEMA), Parameter("context_sha256", context.digest),
              Parameter("context_chunks", len(chunks)))
    if settings.annualization_factor is not None:
        params += (Parameter("annualization_factor", settings.annualization_factor),)
    params += tuple(Parameter(f"context_{i:03}", chunk) for i, chunk in enumerate(chunks))
    return ConfigSpec(REALIZED_VARIANCE_IDENTITY, REALIZED_VARIANCE_ALGORITHM, params, target,
                      WindowSpec(len(context.sessions), target.session_id,
                                 tuple(s.session_id for s in context.sessions), "completed_eod"),
                      availability, adjustment, price_unit)


def decode_realized_variance_config(context: IntradayContext, config: ConfigSpec) -> RealizedVarianceSettings:
    """Validate the closed realized-variance envelope against the supplied context and return its settings."""
    if type(context) is not IntradayContext or type(config) is not ConfigSpec:
        fail("concrete intraday context/config required")
    if config.algorithm_version != REALIZED_VARIANCE_ALGORITHM:
        fail("realized-variance algorithm version differs", ErrorCode.INCOMPATIBLE_VERSION)
    if config.identity != REALIZED_VARIANCE_IDENTITY:
        fail("not a realized-variance configuration", ErrorCode.INCONSISTENT_IDENTITY)
    values = {p.name: p.value for p in config.parameters}
    count = integer(values.get("context_chunks"), 1, 16, ErrorCode.INVALID_CONFIG)
    required = ({"policy_version", "sampling", "evidence_limit", "context_schema", "context_sha256",
                 "context_chunks"} | {f"context_{i:03}" for i in range(count)}
                | ({"annualization_factor"} & set(values)))
    if set(values) != required:
        fail("closed realized-variance parameters required")
    settings = _check(values["policy_version"], values["sampling"], values.get("annualization_factor"),
                      values["evidence_limit"])
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
    expected = build_realized_variance_config(
        context, policy_version=settings.policy_version, sampling=settings.sampling,
        annualization_factor=settings.annualization_factor, availability=config.availability,
        adjustment=config.adjustment, price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail("configuration is not the final canonical realized-variance envelope", ErrorCode.INCONSISTENT_IDENTITY)
    return settings
