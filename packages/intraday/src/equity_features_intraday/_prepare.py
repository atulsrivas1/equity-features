"""Exact bounded preparation with per-family fact/readiness ownership."""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import NoReturn, SupportsIndex, cast

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, ErrorCode, InputBinding, Reason, Status,
)
from ._admission import Admitted, SlotFacts, admit
from ._context import IntradayContext, fail, validate_config

REQUIREMENTS = frozenset({"anchored_closes", "true_ranges", "price_moments",
                          "high_extrema", "low_extrema", "simple_returns"})
PREPARATION_SCHEMA = "equity-features.intraday-preparation.v1"
_ISSUER = object()


@dataclass(frozen=True)
class OperandEvidence:
    slot_index: int
    input_id: str
    start_ns: int
    end_ns: int
    known_at_ns: int | None
    use: str
    reason: Reason | None


@dataclass(frozen=True)
class PreparedOperand:
    requirement: str
    dependency_slots: tuple[int, ...]
    units: tuple[str, ...]
    values: tuple[Fraction, ...] | None
    status: Status
    expected: int
    observed: int
    reasons: tuple[Reason, ...]
    evidence: tuple[OperandEvidence, ...]


@dataclass(frozen=True, init=False)
class IntradayPreparation:
    context_digest: str = ""
    config_digest: str = ""
    requirements: tuple[str, ...] = ()
    input_bindings: tuple[InputBinding, ...] = ()
    batches: tuple[CanonicalBatch, ...] = ()
    _views: tuple[PreparedOperand, ...] = ()
    _issuer: object | None = None
    schema_version: str = PREPARATION_SCHEMA

    def __init__(self) -> None:
        fail("use the reviewed preparation factory", ErrorCode.UNSUPPORTED_CAPABILITY)

    def __reduce_ex__(self, protocol: SupportsIndex) -> NoReturn:
        fail("preparation has no serialization/restore capability", ErrorCode.UNSUPPORTED_CAPABILITY)

    def operand(self, requirement: str) -> PreparedOperand:
        if self._issuer is not _ISSUER or self.schema_version != PREPARATION_SCHEMA:
            fail("unrecognized preparation producer/version", ErrorCode.INCOMPATIBLE_VERSION)
        if requirement not in self.requirements:
            fail("requested operand was not prepared", ErrorCode.UNSUPPORTED_CAPABILITY)
        return self._views[self.requirements.index(requirement)]


def dependency_fields(requirement: str, context: IntradayContext,
                      period: int) -> tuple[dict[int, tuple[str, ...]], int]:
    a, t = context.anchor_index, context.target_index
    if requirement == "anchored_closes":
        return {i: ("close",) for i in range(a, t+1)}, t-a+1
    if requirement == "true_ranges":
        if t == a:
            return {a: ("close",)}, 1
        fields = {a: ("close",), t: ("high", "low")}
        fields.update({i: ("close", "high", "low") for i in range(a+1, t)})
        return dict(sorted(fields.items())), t-a+1
    if requirement == "simple_returns":
        return {i: ("close",) for i in range(max(a, t-1), t+1)}, 2
    field = "high" if requirement == "high_extrema" else "low" if requirement == "low_extrema" else "close"
    return {i: (field,) for i in range(max(a, t-period+1), t+1)}, period


def price(fact: SlotFacts, field: str) -> int | None:
    if field == "close":
        return fact.close
    if field == "high":
        return fact.high
    if field == "low":
        return fact.low
    fail("unknown internal operand field")


def arithmetic(requirement: str, facts: tuple[SlotFacts, ...],
               context: IntradayContext, period: int, scale: int) -> tuple[Fraction, ...]:
    a, t = context.anchor_index, context.target_index
    divisor = 10**scale
    if requirement == "anchored_closes":
        return tuple(Fraction(cast(int, f.close), divisor) for f in facts[a:t+1])
    if requirement == "true_ranges":
        return tuple(Fraction(max(cast(int, facts[i].high)-cast(int, facts[i].low),
                                  abs(cast(int, facts[i].high)-cast(int, facts[i-1].close)),
                                  abs(cast(int, facts[i].low)-cast(int, facts[i-1].close))), divisor)
                     for i in range(a+1, t+1))
    if requirement == "simple_returns":
        return (Fraction(cast(int, facts[t].close), cast(int, facts[t-1].close))-1,)
    window = facts[t-period+1:t+1]
    if requirement == "high_extrema":
        return (Fraction(max(cast(int, f.high) for f in window), divisor),)
    if requirement == "low_extrema":
        return (Fraction(min(cast(int, f.low) for f in window), divisor),)
    origin = cast(int, window[0].close)
    delta_sum = sum(cast(int, f.close)-origin for f in window)
    square_sum = sum((cast(int, f.close)-origin)**2 for f in window)
    numerator = period*square_sum-delta_sum**2
    if numerator < 0 or abs(delta_sum) >= 2**75 or square_sum >= 2**138 or numerator >= 2**150:
        fail("moment arithmetic invariant violated", ErrorCode.OVERFLOW)
    mean = Fraction(origin*period+delta_sum, period*divisor)
    variance = Fraction(numerator, period**2*divisor**2)
    residual = Fraction(cast(int, facts[t].close), divisor)-mean
    return mean, variance, residual


def prepare_view(requirement: str, admitted: Admitted, context: IntradayContext,
                 period: int, scale: int, evidence_limit: int) -> PreparedOperand:
    fields, expected = dependency_fields(requirement, context, period)
    reasons: set[Reason] = set()
    missing_column = False
    observed = 0
    evidence: list[OperandEvidence] = []
    for i, names in fields.items():
        fact = admitted.facts[i]
        ready = True
        absent = fact.input_id is not None and any(name not in fact.columns for name in names)
        if absent:
            missing_column = True
            reasons.add(Reason.ABSENT_INPUT)
            ready = False
        if fact.knowledge_reason is not None:
            reasons.add(fact.knowledge_reason)
            ready = False
        if fact.empty:
            reasons.update((Reason.OBSERVED_EMPTY, Reason.NO_ELIGIBLE_OBSERVATIONS))
            ready = False
        elif fact.row_index is None or fact.coverage is None:
            reasons.add(Reason.GOVERNED_GAP)
            ready = False
        else:
            if not fact.coverage.complete or fact.coverage.expected != 1 or fact.coverage.observed != 1:
                reasons.add(Reason.GOVERNED_GAP)
                ready = False
            if any(name in fact.columns and price(fact, name) is None for name in names):
                reasons.add(Reason.NULL_FIELD)
                ready = False
        if ready:
            observed += 1
        if (fact.row_index is not None and fact.input_id is not None and len(evidence) < evidence_limit
                and (ready or fact.knowledge_reason is not None)):
            evidence.append(OperandEvidence(i, fact.input_id, fact.slot.start_ns, fact.slot.end_ns,
                                            fact.known_at_ns, "consumed" if ready else "excluded",
                                            None if ready else fact.knowledge_reason))
    if admitted.observed_empty_delivery:
        reasons.add(Reason.OBSERVED_EMPTY)
    short = len(fields) < expected
    if short:
        reasons.add(Reason.INSUFFICIENT_HISTORY)
    status = (Status.MISSING_INPUT if missing_column else Status.INSUFFICIENT_HISTORY if short else
              Status.INCOMPLETE_COVERAGE if reasons or observed != expected else Status.AVAILABLE)
    units = (("fraction",) if requirement == "simple_returns" else
             ("currency/share", "(currency/share)^2", "currency/share") if requirement == "price_moments" else
             ("currency/share",))
    values = arithmetic(requirement, admitted.facts, context, period, scale) if status == Status.AVAILABLE else None
    return PreparedOperand(requirement, tuple(fields), units, values, status, expected, observed,
                           tuple(sorted(reasons, key=lambda r: r.value)), tuple(evidence))


def prepare_intraday(batches: tuple[CanonicalBatch, ...], context: IntradayContext,
                     config: ConfigSpec, *, requirements: tuple[str, ...]) -> IntradayPreparation:
    period, _, evidence_limit = validate_config(context, config)
    if (type(requirements) is not tuple or not 1 <= len(requirements) <= len(REQUIREMENTS)
            or any(type(r) is not str or r not in REQUIREMENTS for r in requirements)
            or len(set(requirements)) != len(requirements)):
        fail("nonempty unique closed preparation requirements required")
    ordered = tuple(sorted(requirements))
    admitted = admit(batches, context, config)
    if config.price_unit is None:
        fail("explicit configured price unit required", ErrorCode.INVALID_UNIT)
    views = tuple(prepare_view(r, admitted, context, period, config.price_unit.scale, evidence_limit) for r in ordered)
    result = object.__new__(IntradayPreparation)
    object.__setattr__(result, "context_digest", context.digest)
    object.__setattr__(result, "config_digest", config.digest)
    object.__setattr__(result, "requirements", ordered)
    object.__setattr__(result, "input_bindings", admitted.inputs)
    object.__setattr__(result, "batches", batches)
    object.__setattr__(result, "_views", views)
    object.__setattr__(result, "_issuer", _ISSUER)
    object.__setattr__(result, "schema_version", PREPARATION_SCHEMA)
    return result


def validate_preparation(preparation: IntradayPreparation, batches: tuple[CanonicalBatch, ...] | None,
                         context: IntradayContext, config: ConfigSpec,
                         requirements: tuple[str, ...]) -> None:
    if type(preparation) is not IntradayPreparation:
        fail("concrete preparation factory product required", ErrorCode.INVALID_SCHEMA)
    if preparation._issuer is not _ISSUER or preparation.schema_version != PREPARATION_SCHEMA:
        fail("unrecognized preparation producer/version", ErrorCode.INCOMPATIBLE_VERSION)
    if (batches is None or type(batches) is not tuple or len(batches) != len(preparation.batches)
            or any(a is not b for a, b in zip(batches, preparation.batches))
            or preparation.context_digest != context.digest or preparation.config_digest != config.digest):
        fail("prepared facts/config/context/source identity differs", ErrorCode.INCONSISTENT_IDENTITY)
    if not set(requirements) <= set(preparation.requirements):
        fail("required family was not prepared", ErrorCode.UNSUPPORTED_CAPABILITY)
