"""Pure EF3 intraday realized variance (ef3-rv1): uncentered sum of squared log returns over the reset epoch.

RV(t) = sum over consecutive governed bars a+1..t of ln(C_i / C_{i-1})**2; volatility = sqrt(A * RV). Every
logarithm is a Decimal120 evaluation of the exact close ratio. No clock, I/O, storage or default.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import (
    Context, Decimal, DecimalException, localcontext, ROUND_HALF_EVEN,
    InvalidOperation, DivisionByZero, Overflow, Underflow, Subnormal, Clamped, FloatOperation,
)
from math import isfinite
from typing import cast

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow, FeatureColumn,
    FeatureResult, QualityRow, Reason, ResultMetadata, Status, ValueType, validate_batch,
)
from ._admission import SlotFacts, admit
from ._context import IntradayContext, fail
from ._registry import PACKAGE_VERSION
from ._rv_config import REALIZED_VARIANCE_ALGORITHM, decode_realized_variance_config
from ._rv_registry import (
    REALIZED_VARIANCE, REALIZED_VOLATILITY, describe_realized_variance, require_realized_variance_capability,
)

# The first applicable reason fixes the status; every applicable reason is still reported (lexical order).
_PRECEDENCE = (Reason.ABSENT_INPUT, Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE, Reason.NULL_FIELD,
               Reason.INELIGIBLE, Reason.GOVERNED_GAP, Reason.INSUFFICIENT_HISTORY,
               Reason.NO_ELIGIBLE_OBSERVATIONS, Reason.ZERO_DENOMINATOR)
_STATUS = {Reason.GOVERNED_GAP: Status.INCOMPLETE_COVERAGE, Reason.INSUFFICIENT_HISTORY: Status.INSUFFICIENT_HISTORY,
           Reason.NO_ELIGIBLE_OBSERVATIONS: Status.NOT_APPLICABLE, Reason.ZERO_DENOMINATOR: Status.NOT_APPLICABLE}


@dataclass(frozen=True)
class _Slot:
    """Per-slot verdict: blocking reasons (empty when the slot is READY)."""
    reasons: frozenset[Reason]


def _status(reasons: set[Reason]) -> Status:
    first = next((reason for reason in _PRECEDENCE if reason in reasons), None)
    return Status.AVAILABLE if first is None else _STATUS.get(first, Status.MISSING_INPUT)


def _assess(fact: SlotFacts, knowledge_cutoff_ns: int) -> _Slot:
    """Classify one governed slot; knowledge is enforced on the original known_at in every availability mode."""
    if fact.row_index is None:
        coverage = fact.coverage
        if coverage is None:
            return _Slot(frozenset({Reason.ABSENT_INPUT}))
        # A coverage-proven empty slot has no close: no return, never zero flow and never forward filled.
        if coverage.complete and coverage.expected == 0:
            return _Slot(frozenset({Reason.NO_ELIGIBLE_OBSERVATIONS}))
        return _Slot(frozenset({Reason.GOVERNED_GAP}))
    reasons: set[Reason] = set()
    if fact.known_at_ns is None:
        reasons.add(Reason.UNKNOWN_AVAILABILITY)
    elif fact.known_at_ns > knowledge_cutoff_ns:
        reasons.add(Reason.FUTURE_KNOWLEDGE)
    coverage = fact.coverage
    if coverage is None or not coverage.complete or coverage.expected != 1 or coverage.observed != 1:
        reasons.add(Reason.GOVERNED_GAP)
    if "close" not in fact.columns:
        reasons.add(Reason.ABSENT_INPUT)
    elif fact.volume == 0:
        reasons.add(Reason.NO_ELIGIBLE_OBSERVATIONS)
    elif fact.close is None:
        reasons.add(Reason.NULL_FIELD)
    return _Slot(frozenset(reasons))


def _policy() -> Context:
    context = Context(prec=120, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
                      capitals=1, clamp=0, traps=[InvalidOperation, DivisionByZero, Overflow,
                      Underflow, Subnormal, Clamped, FloatOperation])
    context.clear_flags()
    return context


def _finite(value: Decimal) -> float:
    converted = float(value)
    if not isfinite(converted):
        fail("nonfinite realized-variance conversion", ErrorCode.OVERFLOW)
    return 0.0 if value == 0 else converted


def realized_values(closes: tuple[int, ...], factor: int | None) -> tuple[float, float | None]:
    """(RV, sqrt(A RV)) of an all-ready epoch of at least two closes.

    A step with an equal close contributes exactly 0 (decided on the integers); a flat epoch is therefore exactly +0.0.
    """
    try:
        with localcontext(_policy()):
            total = Decimal(0)
            for previous, current in zip(closes, closes[1:]):
                if current != previous:
                    step = (Decimal(current) / Decimal(previous)).ln()
                    total += step * step
            volatility = None if factor is None else _finite((Decimal(factor) * total).sqrt())
            return _finite(total), volatility
    except (DecimalException, OverflowError, ValueError):
        fail("realized-variance arithmetic outside declared numeric policy", ErrorCode.OVERFLOW)


def compute_realized_variance(batches: tuple[CanonicalBatch, ...] | None, context: IntradayContext,
                              config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef3-rv1 outputs over supplied BAR closes; deterministic, batch and full replay only."""
    settings = decode_realized_variance_config(context, config)
    if (type(features) is not tuple or not 1 <= len(features) <= len(describe_realized_variance())
            or any(type(feature) is not str for feature in features) or len(set(features)) != len(features)):
        fail("nonempty unique selected feature IDs required")
    known = {entry.feature_id for entry in describe_realized_variance()}
    if any(feature not in known for feature in features):
        fail("unknown selected realized-variance feature", ErrorCode.UNKNOWN_FEATURE)
    selected = tuple(sorted(features))
    for feature in selected:
        require_realized_variance_capability(feature, "batch")
    # The annualization factor is a caller parameter bound in the config exactly when volatility is selected.
    if (REALIZED_VOLATILITY in selected) != (settings.annualization_factor is not None):
        fail("annualization_factor is required exactly when intraday.realized_volatility is selected")
    if batches is not None and type(batches) is tuple:
        # Row-level semantics first, so a duplicated interval is DUPLICATE rather than a slot-bound overflow.
        for chunk in batches:
            if type(chunk) is CanonicalBatch:
                validate_batch(chunk, required_fields=())
    admitted = admit(batches, context, config) if batches is not None else None
    a, t = context.anchor_index, context.target_index
    expected = max(2, t-a+1)
    cutoff = config.availability.knowledge_cutoff_ns
    entity = EntityKey(context.instrument_id, config.session.session_id)
    reasons: set[Reason] = set()
    observed = 0
    if admitted is None:
        # An absent delivery stops at absent_input; consequent history reasons are suppressed.
        reasons.add(Reason.ABSENT_INPUT)
    else:
        for i in range(a, t+1):
            verdict = _assess(admitted.facts[i], cutoff)
            reasons.update(verdict.reasons)
            observed += not verdict.reasons
        if t == a:
            reasons.add(Reason.INSUFFICIENT_HISTORY)
    status = _status(reasons)
    results: dict[str, float | None] = {feature: None for feature in selected}
    if status == Status.AVAILABLE:
        assert admitted is not None
        closes = tuple(cast(int, admitted.facts[i].close) for i in range(a, t+1))
        variance, volatility = realized_values(closes, settings.annualization_factor)
        results[REALIZED_VARIANCE] = variance
        results[REALIZED_VOLATILITY] = volatility
    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    ordered = tuple(sorted(reasons, key=lambda reason: reason.value))
    for feature in selected:
        if status == Status.AVAILABLE:
            assert admitted is not None
            # Witnesses are the original rows only: anchor then target, truncated to the result-wide limit.
            for i in (a, t):
                fact = admitted.facts[i]
                if fact.row_index is None or fact.input_id is None or len(evidence) >= settings.evidence_limit:
                    continue
                evidence.append(EvidenceRow(entity, feature, fact.input_id,
                    f"bar:{fact.slot.start_ns}:{fact.slot.end_ns}", fact.slot.end_ns, fact.known_at_ns,
                    fact.slot.start_ns, fact.slot.end_ns, "consumed", None, "completed_interval"))
        columns.append(FeatureColumn(feature, REALIZED_VARIANCE_ALGORITHM, ValueType.FLOAT64, "fraction",
                                     (entity,), (results[feature],)))
        quality.append(QualityRow(entity, feature, status, expected, observed, ordered))
    metadata = ResultMetadata(config.session.namespace, config.session.session_id, config.availability,
                              config.digest, () if admitted is None else admitted.inputs,
                              "intraday.python", PACKAGE_VERSION, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
