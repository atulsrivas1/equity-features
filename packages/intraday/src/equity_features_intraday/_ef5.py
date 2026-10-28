"""Pure EF5 price structures: candle geometry, swing structure and technical returns over supplied governed BAR slots.

Exact rational arithmetic over int64 price coefficients; each float64 output is the exact value correctly rounded once
(Python Fraction to float is round-to-nearest-even); bool and int64 outputs are exact. No clock, I/O, storage, clamp,
epsilon or default: a slot is READY only when it is on the grid, complete, known at the knowledge cutoff by its original
known_at, and carries the fields the output reads. Windows are strict (no shrinking, no bridging a hole).
"""
from __future__ import annotations

from fractions import Fraction
from typing import cast

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow, FeatureColumn, FeatureResult, QualityRow, Reason,
    ResultMetadata, Status, validate_batch,
)
from ._admission import Admitted, SlotFacts, admit
from ._context import IntradayContext, fail
from ._ef5_config import Ef5Settings, decode_ef5_config, span_check
from ._ef5_registry import describe_ef5, ef5_dtype, ef5_producer, require_ef5_capability
from ._registry import PACKAGE_VERSION

_PRECEDENCE = (Reason.ABSENT_INPUT, Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE, Reason.NULL_FIELD,
               Reason.INELIGIBLE, Reason.GOVERNED_GAP, Reason.FUTURE_MARKET, Reason.PARTIAL_UNIVERSE,
               Reason.INSUFFICIENT_HISTORY, Reason.NO_ELIGIBLE_OBSERVATIONS, Reason.EMPTY_UNIVERSE,
               Reason.ZERO_DENOMINATOR)
_STATUS = {Reason.GOVERNED_GAP: Status.INCOMPLETE_COVERAGE, Reason.FUTURE_MARKET: Status.INCOMPLETE_COVERAGE,
           Reason.INSUFFICIENT_HISTORY: Status.INSUFFICIENT_HISTORY,
           Reason.NO_ELIGIBLE_OBSERVATIONS: Status.NOT_APPLICABLE, Reason.ZERO_DENOMINATOR: Status.NOT_APPLICABLE}
_PAIR = ("candle.inside_bar", "candle.engulfing_bullish", "candle.engulfing_bearish")
_OHLC = ("open", "high", "low", "close")


def _status(reasons: set[Reason] | frozenset[Reason]) -> Status:
    first = next((reason for reason in _PRECEDENCE if reason in reasons), None)
    return Status.AVAILABLE if first is None else _STATUS.get(first, Status.MISSING_INPUT)


def _sgn(a: int, b: int) -> int:
    return (a > b) - (a < b)


def _span(feature: str, s: Ef5Settings) -> int | None:
    """Governed slots before the target an output reads; None when the output is undefined (session return, governed)."""
    if feature in _PAIR:
        return 1
    if feature.startswith("candle."):
        return 0
    if feature.endswith("confirmed"):
        return 2 * cast(int, s.swing_strength)
    if feature.startswith("structure."):
        return cast(int, s.lookback)
    if feature.endswith("session_return_fraction"):
        return None
    if feature.endswith("price_velocity_fraction_per_second"):
        return 1
    if feature.startswith("technical.momentum"):
        return 2
    return cast(int, s.trend_window) * cast(int, s.trend_count)


def _fields(feature: str, slot_is_first: bool, slot_is_target: bool) -> tuple[str, ...]:
    if feature.startswith("candle."):
        return _OHLC
    if feature.startswith("structure."):
        return ("high", "low")
    if feature.endswith("session_return_fraction"):
        return (("open",) if slot_is_first else ()) + (("close",) if slot_is_target else ())
    return ("close",)


def _cause(fact: SlotFacts, cutoff_ns: int, fields: tuple[str, ...]) -> Reason | None:
    """The single cause that makes one governed slot unusable for the fields (knowledge uses the original known_at)."""
    if fact.row_index is None:
        if fact.slot.end_ns > cutoff_ns:
            return Reason.FUTURE_MARKET
        coverage = fact.coverage
        if coverage is None:
            return Reason.ABSENT_INPUT
        if coverage.complete and coverage.expected == 0:
            return Reason.NO_ELIGIBLE_OBSERVATIONS
        return Reason.GOVERNED_GAP
    if fact.knowledge_reason is not None:
        return fact.knowledge_reason
    coverage = fact.coverage
    if coverage is None or not coverage.complete or coverage.expected != 1 or coverage.observed != 1:
        return Reason.GOVERNED_GAP
    if fact.volume == 0:
        return Reason.NO_ELIGIBLE_OBSERVATIONS
    values = {"open": fact.open_price, "high": fact.high, "low": fact.low, "close": fact.close}
    if any(values[name] is None for name in fields if name in fact.columns):
        return Reason.NULL_FIELD
    if any(name not in fact.columns for name in fields):
        return Reason.ABSENT_INPUT
    return None


def _check_identity(batches: tuple[CanonicalBatch, ...], config: ConfigSpec) -> None:
    """Identity stage: a chunk on another adjustment basis than the config is INCONSISTENT_IDENTITY."""
    for chunk in batches:
        if type(chunk) is CanonicalBatch and chunk.metadata.adjustment != config.adjustment:
            fail("input adjustment differs from the configuration", ErrorCode.INCONSISTENT_IDENTITY)


def _value(feature: str, s: Ef5Settings, facts: tuple[SlotFacts, ...], a: int, t: int,
           scale: int) -> tuple[object, int | None, Reason | None]:
    """(value, located swing slot, reason) of an output whose required slots are all READY."""
    def num(i: int, name: str) -> int:
        fact = facts[i]
        return cast(int, {"open": fact.open_price, "high": fact.high, "low": fact.low, "close": fact.close}[name])

    if feature.startswith("candle."):
        o, h, lo, c = (num(t, n) for n in _OHLC)
        rng, body = h - lo, abs(c - o)
        if feature in _PAIR:
            o1, h1, l1, c1 = (num(t-1, n) for n in _OHLC)
            if feature == "candle.inside_bar":
                return h < h1 and lo > l1, None, None
            cur_lo, cur_hi, pre_lo, pre_hi = min(o, c), max(o, c), min(o1, c1), max(o1, c1)
            covers = cur_lo <= pre_lo and cur_hi >= pre_hi and (cur_lo < pre_lo or cur_hi > pre_hi)
            if feature == "candle.engulfing_bullish":
                return c1 < o1 and c > o and covers, None, None
            return c1 > o1 and c < o and covers, None, None
        if rng == 0:
            return None, None, Reason.ZERO_DENOMINATOR
        if feature == "candle.doji":
            p, q = cast(tuple[int, int], s.doji)
            return body * q <= p * rng, None, None
        top = {"candle.body_fraction": body, "candle.upper_shadow_fraction": h - max(o, c),
               "candle.lower_shadow_fraction": min(o, c) - lo}[feature]
        return float(Fraction(top, rng)), None, None
    if feature.startswith("structure."):
        high = "high" in feature
        name = "high" if high else "low"
        k = cast(int, s.swing_strength)

        def is_swing(slot: int) -> bool:
            around = [num(i, name) for i in range(slot-k, slot+k+1) if i != slot]
            return num(slot, name) > max(around) if high else num(slot, name) < min(around)
        if feature.endswith("confirmed"):
            return is_swing(t-k), None, None
        for slot in range(t-k, t-cast(int, s.lookback)+k-1, -1):
            if is_swing(slot):
                return float(Fraction(num(slot, name), 10**scale)), slot, None
        return None, None, Reason.NO_ELIGIBLE_OBSERVATIONS

    def end(i: int) -> int:
        return facts[i].slot.end_ns

    def seconds(i: int) -> Fraction:
        return Fraction(end(i) - end(i-1), 10**9)

    def velocity(i: int) -> Fraction:
        return Fraction(num(i, "close") - num(i-1, "close"), num(i-1, "close")) / seconds(i)
    if feature.endswith("session_return_fraction"):
        return float(Fraction(num(t, "close") - num(a, "open"), num(a, "open"))), None, None
    if feature.endswith("price_velocity_fraction_per_second"):
        return float(velocity(t)), None, None
    if feature.startswith("technical.momentum"):
        return float((velocity(t) - velocity(t-1)) / seconds(t)), None, None
    n, m = cast(int, s.trend_window), cast(int, s.trend_count)
    marks = [num(t-j*n, "close") for j in range(m, -1, -1)]
    return sum(_sgn(b, x) for x, b in zip(marks, marks[1:])), None, None


def compute_ef5(producer: str, batches: tuple[CanonicalBatch, ...] | None, context: IntradayContext,
                config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Selected EF5 outputs of one producer over supplied BAR slots; deterministic, batch and full replay only."""
    if (type(features) is not tuple or not features or any(type(feature) is not str for feature in features)
            or len(set(features)) != len(features)):
        fail("nonempty unique selected feature IDs required")
    if context is None:
        fail("structural context (governed grid) not delivered", ErrorCode.INVALID_SCHEMA)
    if batches is not None and type(batches) is tuple:
        # Shared row semantics first, so a repeated, unordered or incoherent bar is refused before config and identity.
        for chunk in batches:
            if type(chunk) is CanonicalBatch:
                # Contract: a negative volume is INVALID_SCHEMA (the generic validator would say BOUNDS).
                volume = next((c.values for c in chunk.columns if c.name == "volume"), ())
                if any(type(v) is int and v < 0 for v in volume):
                    fail("negative volume", ErrorCode.INVALID_SCHEMA)
                validate_batch(chunk, required_fields=())
                if chunk.row_count and not chunk.metadata.interval_coverage:
                    fail("rows delivered with coverage not declared (no default-to-complete)", ErrorCode.INVALID_SCHEMA)
    known = {entry.feature_id for entry in describe_ef5()}
    if any(feature not in known or ef5_producer(feature) != producer for feature in features):
        fail("unknown selected EF5 feature for this producer", ErrorCode.UNKNOWN_FEATURE)
    selected = tuple(sorted(features))
    for feature in selected:
        require_ef5_capability(feature, "batch")
    settings = decode_ef5_config(producer, context, config)
    span_check(settings, {feature: _span(feature, settings) for feature in selected})
    if batches is not None and type(batches) is tuple:
        _check_identity(batches, config)
    admitted: Admitted | None = admit(batches, context, config) if batches is not None else None
    a, t = context.anchor_index, context.target_index
    cutoff = config.availability.market_cutoff_ns
    scale = config.price_unit.scale if config.price_unit is not None else 0
    entity = EntityKey(context.instrument_id, config.session.session_id)
    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        span = _span(feature, settings)
        need = [a, t] if span is None and t != a else [a] if span is None else list(range(t-span, t+1))
        reasons: set[Reason] = set()
        ready: list[int] = []
        for i in need:
            if i < a:
                continue
            if admitted is None:
                reasons.add(Reason.ABSENT_INPUT)
                continue
            cause = _cause(admitted.facts[i], cutoff, _fields(feature, i == a, i == t))
            if cause is None:
                ready.append(i)
            else:
                reasons.add(cause)
        if need[0] < a:
            reasons.add(Reason.INSUFFICIENT_HISTORY)
        value: object = None
        located: int | None = None
        if not reasons:
            assert admitted is not None
            value, located, extra = _value(feature, settings, admitted.facts, a, t, scale)
            if extra is not None:
                reasons.add(extra)
        status = _status(reasons)
        if status == Status.AVAILABLE:
            assert admitted is not None
            order = [t] + [i for i in ready if i != t]
            if located is not None:
                order = [located, t] + [i for i in ready if i not in (located, t)]
            for i in order:
                fact = admitted.facts[i]
                if fact.row_index is None or fact.input_id is None or len(evidence) >= settings.evidence_limit:
                    continue
                evidence.append(EvidenceRow(entity, feature, fact.input_id, f"slot:{fact.slot.index}",
                                            fact.slot.end_ns, fact.known_at_ns, fact.slot.start_ns, fact.slot.end_ns,
                                            "consumed", None, "completed_interval"))
        else:
            value = None
        unit = next(entry.unit for entry in describe_ef5() if entry.feature_id == feature)
        algorithm = next(entry.algorithm_version for entry in describe_ef5() if entry.feature_id == feature)
        columns.append(FeatureColumn(feature, algorithm, ef5_dtype(feature), unit, (entity,), (value,)))  # type: ignore[arg-type]
        ordered = tuple(sorted(reasons, key=lambda reason: reason.value))
        quality.append(QualityRow(entity, feature, status, len(need), len(ready), ordered))
    metadata = ResultMetadata(config.session.namespace, config.session.session_id, config.availability,
                              config.digest, () if admitted is None else admitted.inputs,
                              "intraday.python", PACKAGE_VERSION, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
