"""Pure EF4 path efficiency and choppiness (ef4-path1) over the N+1 governed slots ending at the target bar.

Net displacement, path length, window range and the plain-sum true range are exact integer sums at the price scale;
the efficiency ratio is an exact rational; the log efficiency ratio and the choppiness fraction ln(TRS/WR)/ln(N) are
Decimal120 logarithms of exact integer ratios. Every published value is rounded once to float64. No clock, I/O,
storage, clamp, epsilon or default.
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
from ._admission import Admitted, SlotFacts, admit
from ._context import IntradayContext, fail
from ._path_config import PATH_EFFICIENCY_ALGORITHM, decode_path_efficiency_config
from ._path_registry import (
    PATH_CHOPPINESS_FRACTION, PATH_EFFICIENCY_RATIO, PATH_LENGTH, PATH_LOG_EFFICIENCY_RATIO, PATH_NET_DISPLACEMENT,
    PATH_TRUE_RANGE_SUM, PATH_WINDOW_RANGE, describe_path_efficiency, require_path_efficiency_capability,
)
from ._registry import PACKAGE_VERSION

# The first applicable reason fixes the status; every applicable reason is still reported (lexical order).
# ineligible, future_market, partial_universe and empty_universe are unreachable in this producer.
_PRECEDENCE = (Reason.ABSENT_INPUT, Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE, Reason.NULL_FIELD,
               Reason.GOVERNED_GAP, Reason.INSUFFICIENT_HISTORY, Reason.NO_ELIGIBLE_OBSERVATIONS,
               Reason.ZERO_DENOMINATOR)
_STATUS = {Reason.GOVERNED_GAP: Status.INCOMPLETE_COVERAGE, Reason.INSUFFICIENT_HISTORY: Status.INSUFFICIENT_HISTORY,
           Reason.NO_ELIGIBLE_OBSERVATIONS: Status.NOT_APPLICABLE, Reason.ZERO_DENOMINATOR: Status.NOT_APPLICABLE}
_CLOSE = ("close",)
_BAR = ("close", "high", "low")
_RANGE_GROUP = frozenset({PATH_CHOPPINESS_FRACTION, PATH_TRUE_RANGE_SUM, PATH_WINDOW_RANGE})


@dataclass(frozen=True)
class _Window:
    """Readiness of one operand group over the window: causes of the lost slots and the READY slot count."""
    reasons: frozenset[Reason]
    observed: int


def _status(reasons: set[Reason] | frozenset[Reason]) -> Status:
    first = next((reason for reason in _PRECEDENCE if reason in reasons), None)
    return Status.AVAILABLE if first is None else _STATUS.get(first, Status.MISSING_INPUT)


def _assess(fact: SlotFacts, knowledge_cutoff_ns: int, fields: tuple[str, ...]) -> frozenset[Reason]:
    """Causes that make one governed slot unusable for the fields; knowledge uses the original known_at in every mode."""
    if fact.row_index is None:
        coverage = fact.coverage
        if coverage is None:
            return frozenset({Reason.ABSENT_INPUT})
        # A coverage-proven empty slot has no price: no return, never a zero move and never forward filled.
        if coverage.complete and coverage.expected == 0:
            return frozenset({Reason.NO_ELIGIBLE_OBSERVATIONS})
        return frozenset({Reason.GOVERNED_GAP})
    reasons: set[Reason] = set()
    if fact.known_at_ns is None:
        reasons.add(Reason.UNKNOWN_AVAILABILITY)
    elif fact.known_at_ns > knowledge_cutoff_ns:
        reasons.add(Reason.FUTURE_KNOWLEDGE)
    coverage = fact.coverage
    if coverage is None or not coverage.complete or coverage.expected != 1 or coverage.observed != 1:
        reasons.add(Reason.GOVERNED_GAP)
    if any(name not in fact.columns for name in fields):
        reasons.add(Reason.ABSENT_INPUT)
    elif fact.volume == 0:
        reasons.add(Reason.NO_ELIGIBLE_OBSERVATIONS)
    else:
        values = {"close": fact.close, "high": fact.high, "low": fact.low}
        if any(values[name] is None for name in fields):
            reasons.add(Reason.NULL_FIELD)
    return frozenset(reasons)


def _window(admitted: Admitted, a: int, t: int, n: int, cutoff: int, ranged: bool) -> _Window:
    """Strict N+1 slot window t-N..t clipped at the epoch anchor; the base slot only ever needs its close."""
    reasons: set[Reason] = set()
    observed = 0
    for i in range(max(a, t-n), t+1):
        fields = _BAR if ranged and i > t-n else _CLOSE
        lost = _assess(admitted.facts[i], cutoff, fields)
        reasons.update(lost)
        observed += not lost
    if t-n < a:
        reasons.add(Reason.INSUFFICIENT_HISTORY)
    return _Window(frozenset(reasons), observed)


def _policy() -> Context:
    context = Context(prec=120, rounding=ROUND_HALF_EVEN, Emin=-999999, Emax=999999,
                      capitals=1, clamp=0, traps=[InvalidOperation, DivisionByZero, Overflow,
                      Underflow, Subnormal, Clamped, FloatOperation])
    context.clear_flags()
    return context


def _finite(value: Decimal) -> float:
    converted = float(value)
    if not isfinite(converted):
        fail("nonfinite path-efficiency conversion", ErrorCode.OVERFLOW)
    return 0.0 if value == 0 else converted


def _ratio(numerator: int, denominator: int) -> float:
    """One correctly rounded float64 of an exact integer ratio (Python int true division); zero is +0.0."""
    return 0.0 if numerator == 0 else numerator / denominator


def log_efficiency(closes: tuple[int, ...]) -> float:
    """|ln(C_t/C_b)| / sum |ln(C_i/C_(i-1))| from the exact close ratios; the caller guarantees a nonzero path."""
    if closes[-1] == closes[0]:
        return 0.0
    steps = [(previous, current) for previous, current in zip(closes, closes[1:]) if previous != current]
    # All moves in one direction: the sum of same-signed logarithms is exactly the net logarithm.
    if all(current > previous for previous, current in steps) or all(current < previous for previous, current in steps):
        return 1.0
    try:
        with localcontext(_policy()):
            net = abs((Decimal(closes[-1]) / Decimal(closes[0])).ln())
            path = Decimal(0)
            for previous, current in steps:
                path += abs((Decimal(current) / Decimal(previous)).ln())
            return _finite(net / path)
    except (DecimalException, OverflowError, ValueError):
        fail("path-efficiency arithmetic outside declared numeric policy", ErrorCode.OVERFLOW)


def choppiness(true_range_sum: int, window_range: int, n: int) -> float:
    """ln(TRS/WR) / ln(N) from the exact integer ratio (log1p-grade near 1); TRS = WR is exactly +0.0.

    Each true range lies inside the extended window range and the intervals chain through the closes, so
    1 <= TRS/WR <= N and the value is in [0, 1] without any clamp.
    """
    if true_range_sum == window_range:
        return 0.0
    try:
        with localcontext(_policy()):
            return _finite((Decimal(true_range_sum) / Decimal(window_range)).ln() / Decimal(n).ln())
    except (DecimalException, OverflowError, ValueError):
        fail("path-efficiency arithmetic outside declared numeric policy", ErrorCode.OVERFLOW)


def compute_path_efficiency(batches: tuple[CanonicalBatch, ...] | None, context: IntradayContext,
                            config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef4-path1 outputs over supplied BAR closes and ranges; deterministic, batch and full replay only."""
    if (type(features) is not tuple or not features or any(type(feature) is not str for feature in features)
            or len(set(features)) != len(features)):
        fail("nonempty unique selected feature IDs required")
    if batches is not None and type(batches) is tuple:
        # Shared row semantics first, so a repeated, unordered or incoherent bar is refused before config and identity.
        for chunk in batches:
            if type(chunk) is CanonicalBatch:
                validate_batch(chunk, required_fields=())
    known = {entry.feature_id for entry in describe_path_efficiency()}
    if any(feature not in known for feature in features):
        fail("unknown selected path-efficiency feature", ErrorCode.UNKNOWN_FEATURE)
    selected = tuple(sorted(features))
    for feature in selected:
        require_path_efficiency_capability(feature, "batch")
    settings = decode_path_efficiency_config(context, config)
    admitted = admit(batches, context, config) if batches is not None else None
    a, t, n = context.anchor_index, context.target_index, settings.window
    cutoff = config.availability.knowledge_cutoff_ns
    scale = 10**config.price_unit.scale if config.price_unit is not None else 1
    entity = EntityKey(context.instrument_id, config.session.session_id)
    windows: dict[bool, _Window] = {}
    for ranged in {feature in _RANGE_GROUP for feature in selected}:
        # An absent delivery stops at absent_input; consequent history reasons are suppressed.
        windows[ranged] = (_Window(frozenset({Reason.ABSENT_INPUT}), 0) if admitted is None
                           else _window(admitted, a, t, n, cutoff, ranged))
    values: dict[str, float | None] = {}
    reasons_of: dict[str, frozenset[Reason]] = {}
    for feature in selected:
        window = windows[feature in _RANGE_GROUP]
        reasons_of[feature] = window.reasons
        values[feature] = None
        if window.reasons or admitted is None:
            continue
        facts = admitted.facts
        closes = tuple(cast(int, facts[i].close) for i in range(t-n, t+1))
        path = sum(abs(current - previous) for previous, current in zip(closes, closes[1:]))
        if feature == PATH_NET_DISPLACEMENT:
            values[feature] = _ratio(closes[-1] - closes[0], scale)
        elif feature == PATH_LENGTH:
            values[feature] = _ratio(path, scale)
        elif feature == PATH_EFFICIENCY_RATIO:
            if path == 0:
                reasons_of[feature] = frozenset({Reason.ZERO_DENOMINATOR})
            else:
                values[feature] = _ratio(abs(closes[-1] - closes[0]), path)
        elif feature == PATH_LOG_EFFICIENCY_RATIO:
            if path == 0:
                reasons_of[feature] = frozenset({Reason.ZERO_DENOMINATOR})
            else:
                values[feature] = log_efficiency(closes)
        else:
            true_range = 0
            high = low = closes[0]
            for j, i in enumerate(range(t-n+1, t+1)):
                bar_high, bar_low = cast(int, facts[i].high), cast(int, facts[i].low)
                true_range += max(bar_high-bar_low, abs(bar_high-closes[j]), abs(bar_low-closes[j]))
                high, low = max(high, bar_high), min(low, bar_low)
            if feature == PATH_TRUE_RANGE_SUM:
                values[feature] = _ratio(true_range, scale)
            elif feature == PATH_WINDOW_RANGE:
                values[feature] = _ratio(high-low, scale)
            elif high == low:
                reasons_of[feature] = frozenset({Reason.ZERO_DENOMINATOR})
            else:
                values[feature] = choppiness(true_range, high-low, n)
    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        window = windows[feature in _RANGE_GROUP]
        status = _status(reasons_of[feature])
        if status == Status.AVAILABLE:
            assert admitted is not None
            # Witnesses are the original rows only: target, base, then the interior ascending (result-wide limit).
            for i in (t, t-n, *range(t-n+1, t)):
                fact = admitted.facts[i]
                if fact.row_index is None or fact.input_id is None or len(evidence) >= settings.evidence_limit:
                    continue
                evidence.append(EvidenceRow(entity, feature, fact.input_id,
                    f"slot:{fact.slot.index}", fact.slot.end_ns, fact.known_at_ns,
                    fact.slot.start_ns, fact.slot.end_ns, "consumed", None, "completed_interval"))
        unit = next(entry.unit for entry in describe_path_efficiency() if entry.feature_id == feature)
        columns.append(FeatureColumn(feature, PATH_EFFICIENCY_ALGORITHM, ValueType.FLOAT64, unit,
                                     (entity,), (values[feature],)))
        ordered = tuple(sorted(reasons_of[feature], key=lambda reason: reason.value))
        quality.append(QualityRow(entity, feature, status, n+1, window.observed, ordered))
    metadata = ResultMetadata(config.session.namespace, config.session.session_id, config.availability,
                              config.digest, () if admitted is None else admitted.inputs,
                              "intraday.python", PACKAGE_VERSION, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
