"""EF2 money-flow configuration identity (ef2-mf1): builder and closed decoder over the R17 context."""
from __future__ import annotations

from dataclasses import dataclass

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ConfigSpec, ErrorCode, Parameter, PriceUnit, WindowSpec,
)
from ._context import CONTEXT_SCHEMA, IntradayContext, fail, integer, label

MONEY_FLOW_IDENTITY = "ef2.money_flow"
MONEY_FLOW_ALGORITHM = "ef2-money-flow-v1"
# A label names the whole convention set (OBV seed and ties, zero-range multiplier, empty slots,
# CMF window and zero denominator). A different convention is a different label, never a silent change.
MONEY_FLOW_POLICY = "ef2-mf1"


@dataclass(frozen=True)
class MoneyFlowSettings:
    policy_version: str
    cmf_period: int | None
    evidence_limit: int


def build_money_flow_config(context: IntradayContext, *, policy_version: str, cmf_period: int | None,
                            availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                            price_unit: PriceUnit, evidence_limit: int = 0) -> ConfigSpec:
    """Final ConfigSpec for one money-flow request; cmf_period is present exactly when intraday.cmf is selected."""
    if (type(context) is not IntradayContext or type(availability) is not AvailabilitySpec
            or type(adjustment) is not AdjustmentSpec or type(price_unit) is not PriceUnit):
        fail("concrete context/timing/action/unit required")
    if type(policy_version) is not str:
        fail("exact money-flow policy label required")
    if policy_version != MONEY_FLOW_POLICY:
        fail("unsupported money-flow policy label", ErrorCode.INCOMPATIBLE_VERSION)
    if context.mode != "reset":
        fail("ef2-mf1 supports the anchored reset epoch only; carry is out of v1")
    if cmf_period is not None:
        integer(cmf_period, 1, 4096, ErrorCode.INVALID_CONFIG)
    integer(evidence_limit, 0, 10000, ErrorCode.INVALID_CONFIG)
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
    params: tuple[Parameter, ...] = (Parameter("policy_version", policy_version),
              Parameter("evidence_limit", evidence_limit), Parameter("context_schema", CONTEXT_SCHEMA),
              Parameter("context_sha256", context.digest), Parameter("context_chunks", len(chunks)))
    if cmf_period is not None:
        params += (Parameter("cmf_period", cmf_period),)
    params += tuple(Parameter(f"context_{i:03}", chunk) for i, chunk in enumerate(chunks))
    return ConfigSpec(MONEY_FLOW_IDENTITY, MONEY_FLOW_ALGORITHM, params, target,
                      WindowSpec(len(context.sessions), target.session_id,
                                 tuple(s.session_id for s in context.sessions), "completed_eod"),
                      availability, adjustment, price_unit)


def decode_money_flow_config(context: IntradayContext, config: ConfigSpec) -> MoneyFlowSettings:
    """Validate the closed money-flow envelope against the supplied context and return its settings."""
    if type(context) is not IntradayContext or type(config) is not ConfigSpec:
        fail("concrete intraday context/config required")
    if config.algorithm_version != MONEY_FLOW_ALGORITHM:
        fail("money-flow algorithm version differs", ErrorCode.INCOMPATIBLE_VERSION)
    if config.identity != MONEY_FLOW_IDENTITY:
        fail("not a money-flow configuration", ErrorCode.INCONSISTENT_IDENTITY)
    values = {p.name: p.value for p in config.parameters}
    count = integer(values.get("context_chunks"), 1, 16, ErrorCode.INVALID_CONFIG)
    required = ({"policy_version", "evidence_limit", "context_schema", "context_sha256", "context_chunks"}
                | {f"context_{i:03}" for i in range(count)} | ({"cmf_period"} & set(values)))
    if set(values) != required:
        fail("closed money-flow parameters required")
    policy = values["policy_version"]
    if type(policy) is not str:
        fail("exact money-flow policy label required")
    if policy != MONEY_FLOW_POLICY:
        fail("unsupported money-flow policy label", ErrorCode.INCOMPATIBLE_VERSION)
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
    period = values.get("cmf_period")
    if "cmf_period" in values:
        integer(period, 1, 4096, ErrorCode.INVALID_CONFIG)
    limit = integer(values["evidence_limit"], 0, 10000, ErrorCode.INVALID_CONFIG)
    if config.price_unit is None:
        fail("explicit price unit required", ErrorCode.INVALID_UNIT)
    expected = build_money_flow_config(context, policy_version=policy,
                                       cmf_period=period if type(period) is int else None,
                                       availability=config.availability, adjustment=config.adjustment,
                                       price_unit=config.price_unit, evidence_limit=limit)
    if config != expected:
        fail("configuration is not the final canonical money-flow envelope", ErrorCode.INCONSISTENT_IDENTITY)
    return MoneyFlowSettings(policy, period if type(period) is int else None, limit)
