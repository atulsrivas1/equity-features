"""EF4 path-efficiency configuration identity (ef4-path1): builder and closed decoder over the R17 context."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ConfigSpec, ErrorCode, Parameter, PriceUnit, WindowSpec,
)
from ._context import CONTEXT_SCHEMA, IntradayContext, fail, integer, label

PATH_EFFICIENCY_IDENTITY = "ef4.path_efficiency"
PATH_EFFICIENCY_ALGORITHM = "ef4-path-efficiency-v1"
# A label names the whole convention set (N returns from N+1 governed slots, strict window, price and log return
# basis, window range with the base close, plain-sum true range with the predecessor close, choppiness
# ln(TRS/WR)/ln(N), exact zero tests, missingness mapping, rounding). A different convention is a different label.
PATH_EFFICIENCY_POLICY = "ef4-path1"
PATH_SESSION_RESET = "session_reset"
PATH_GOVERNED_HISTORY = "governed_history"
PATH_EFFICIENCY_PROFILES = (PATH_GOVERNED_HISTORY, PATH_SESSION_RESET)
PATH_WINDOW_MAX = 4096
# The epoch profile fixes the R17 context mode: the target session resets (reset); a supplied governed daily grid
# is one epoch from its anchor (carry in the R17 context vocabulary; no value ever crosses a session boundary).
_MODE = {PATH_SESSION_RESET: "reset", PATH_GOVERNED_HISTORY: "carry"}


@dataclass(frozen=True)
class PathEfficiencySettings:
    policy_version: str
    window: int
    epoch_profile: str
    evidence_limit: int


def _check(policy: object, window: object, profile: object, limit: object) -> PathEfficiencySettings:
    """Every shape and range fault is INVALID_CONFIG; only a well-formed unsupported label is INCOMPATIBLE_VERSION."""
    n = integer(window, 2, PATH_WINDOW_MAX, ErrorCode.INVALID_CONFIG)
    if type(profile) is not str or profile not in PATH_EFFICIENCY_PROFILES:
        fail("epoch_profile must be session_reset or governed_history (there is no default and no carry)")
    cap = integer(limit, 0, 10000, ErrorCode.INVALID_CONFIG)
    if type(policy) is not str:
        fail("exact path-efficiency policy label required")
    return PathEfficiencySettings(policy, n, profile, cap)


def _version(settings: PathEfficiencySettings) -> None:
    """The label is the last config-stage check, after shape, range and unit faults."""
    if settings.policy_version != PATH_EFFICIENCY_POLICY:
        fail("unsupported path-efficiency policy label", ErrorCode.INCOMPATIBLE_VERSION)


def build_path_efficiency_config(context: IntradayContext, *, policy_version: str | None = None,
                                 window: int | None = None, epoch_profile: str | None = None,
                                 availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                                 price_unit: PriceUnit, evidence_limit: int | None = None) -> ConfigSpec:
    """Final ConfigSpec; policy_version, window, epoch_profile and evidence_limit have no default."""
    if price_unit is None:
        fail("explicit price unit required", ErrorCode.INVALID_UNIT)
    if (type(context) is not IntradayContext or type(availability) is not AvailabilitySpec
            or type(adjustment) is not AdjustmentSpec or type(price_unit) is not PriceUnit):
        fail("concrete context/timing/action/unit required")
    settings = _check(policy_version, window, epoch_profile, evidence_limit)
    _version(settings)
    if context.mode != _MODE[settings.epoch_profile]:
        fail("epoch_profile and R17 context mode disagree (session_reset: reset; governed_history: carry)")
    if context.mode == "carry" and len(context.slots()) != len(context.sessions):
        fail("governed_history needs one governed slot per session")
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
    params: tuple[Parameter, ...] = (
        Parameter("policy_version", settings.policy_version), Parameter("window", settings.window),
        Parameter("epoch_profile", settings.epoch_profile), Parameter("evidence_limit", settings.evidence_limit),
        Parameter("context_schema", CONTEXT_SCHEMA), Parameter("context_sha256", context.digest),
        Parameter("context_chunks", len(chunks)))
    params += tuple(Parameter(f"context_{i:03}", chunk) for i, chunk in enumerate(chunks))
    return ConfigSpec(PATH_EFFICIENCY_IDENTITY, PATH_EFFICIENCY_ALGORITHM, params, target,
                      WindowSpec(len(context.sessions), target.session_id,
                                 tuple(s.session_id for s in context.sessions), "completed_eod"),
                      availability, adjustment, price_unit)


def decode_path_efficiency_config(context: IntradayContext, config: ConfigSpec) -> PathEfficiencySettings:
    """Validate the closed path-efficiency envelope against the supplied context and return its settings."""
    if type(context) is not IntradayContext or type(config) is not ConfigSpec:
        fail("concrete intraday context/config required")
    if config.algorithm_version != PATH_EFFICIENCY_ALGORITHM:
        fail("path-efficiency algorithm version differs", ErrorCode.INCOMPATIBLE_VERSION)
    if config.identity != PATH_EFFICIENCY_IDENTITY:
        fail("not a path-efficiency configuration", ErrorCode.INCONSISTENT_IDENTITY)
    values = {p.name: p.value for p in config.parameters}
    count = integer(values.get("context_chunks"), 1, 16, ErrorCode.INVALID_CONFIG)
    required = {"policy_version", "window", "epoch_profile", "evidence_limit", "context_schema", "context_sha256",
                "context_chunks"} | {f"context_{i:03}" for i in range(count)}
    if set(values) != required:
        fail("closed path-efficiency parameters required")
    settings = _check(values["policy_version"], values["window"], values["epoch_profile"], values["evidence_limit"])
    if config.price_unit is None:
        fail("explicit price unit required", ErrorCode.INVALID_UNIT)
    _version(settings)
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
    expected = build_path_efficiency_config(
        context, policy_version=settings.policy_version, window=settings.window, epoch_profile=settings.epoch_profile,
        availability=config.availability, adjustment=config.adjustment, price_unit=config.price_unit,
        evidence_limit=settings.evidence_limit)
    if config != expected:
        fail("configuration is not the final canonical path-efficiency envelope", ErrorCode.INCONSISTENT_IDENTITY)
    return settings
