"""Pure EF2 money flow (ef2-mf1): OBV, accumulation/distribution line and Chaikin money flow.

Exact integer and rational arithmetic with one final rounding; no clock, I/O, storage or default.
Each selected output owns its operands, counts and readiness, so one unready slot or an unrelated
missing column never blocks an output whose own dependencies are ready.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow, FeatureColumn,
    FeatureResult, QualityRow, Reason, ResultMetadata, Status, ValueType,
)
from ._admission import SlotFacts, admit
from ._context import I64_MAX, I64_MIN, IntradayContext, fail
from ._flow_config import MONEY_FLOW_ALGORITHM, decode_money_flow_config
from ._flow_registry import AD_LINE, CMF, OBV, describe_money_flow, require_money_flow_capability
from ._registry import PACKAGE_VERSION

# The first applicable reason fixes the status; every applicable reason is still reported (lexical order).
_PRECEDENCE = (Reason.ABSENT_INPUT, Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE, Reason.NULL_FIELD,
               Reason.INELIGIBLE, Reason.GOVERNED_GAP, Reason.INSUFFICIENT_HISTORY,
               Reason.NO_ELIGIBLE_OBSERVATIONS, Reason.ZERO_DENOMINATOR)
_STATUS = {Reason.GOVERNED_GAP: Status.INCOMPLETE_COVERAGE, Reason.INSUFFICIENT_HISTORY: Status.INSUFFICIENT_HISTORY,
           Reason.NO_ELIGIBLE_OBSERVATIONS: Status.NOT_APPLICABLE, Reason.ZERO_DENOMINATOR: Status.NOT_APPLICABLE}
_OBV_FIELDS = ("close", "volume")
_FLOW_FIELDS = ("high", "low", "close", "volume")
_UNITS = {AD_LINE: "shares", CMF: "fraction", OBV: "shares"}


@dataclass(frozen=True)
class _Slot:
    """Per-slot verdict for one field set: blocking reasons, or a priced / proven-empty ready slot."""
    reasons: frozenset[Reason]
    empty: bool = False


def _status(reasons: set[Reason]) -> Status:
    first = next((reason for reason in _PRECEDENCE if reason in reasons), None)
    return Status.AVAILABLE if first is None else _STATUS.get(first, Status.MISSING_INPUT)


def _assess(fact: SlotFacts, fields: tuple[str, ...], knowledge_cutoff_ns: int) -> _Slot:
    """Classify one governed slot; knowledge is enforced on the original known_at in every availability mode."""
    if fact.row_index is None:
        coverage = fact.coverage
        if coverage is None:
            return _Slot(frozenset({Reason.ABSENT_INPUT}))
        # Only coverage-proven emptiness (complete, expected 0) is zero flow; any other missing slot is a gap.
        if coverage.complete and coverage.expected == 0:
            return _Slot(frozenset(), True)
        return _Slot(frozenset({Reason.GOVERNED_GAP}))
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
        return _Slot(frozenset(reasons))
    # A null volume is missing input, never assumed empty; volume 0 (null OHLC by the shared BAR rule) is empty.
    if fact.volume is None:
        reasons.add(Reason.NULL_FIELD)
        return _Slot(frozenset(reasons))
    if fact.volume == 0:
        return _Slot(frozenset(reasons), True)
    prices = {"close": fact.close, "high": fact.high, "low": fact.low}
    if any(prices[name] is None for name in fields if name != "volume"):
        reasons.add(Reason.NULL_FIELD)
    return _Slot(frozenset(reasons))


def _rational_sum(by_denominator: dict[int, int]) -> tuple[int, int]:
    """Exact sum of n/d terms as an unreduced (numerator, positive denominator) pair; pairwise, gcd-free."""
    terms = sorted(by_denominator.items(), key=lambda item: item[0])
    work = [(numerator, denominator) for denominator, numerator in terms]
    if not work:
        return 0, 1
    while len(work) > 1:
        merged = [(work[i][0]*work[i+1][1] + work[i+1][0]*work[i][1], work[i][1]*work[i+1][1])
                  for i in range(0, len(work)-1, 2)]
        if len(work) % 2:
            merged.append(work[-1])
        work = merged
    return work[0]


def _flow(facts: tuple[SlotFacts, ...], assessed: dict[int, _Slot], lo: int,
          hi: int) -> tuple[int, int, int]:
    """Exact money-flow volume sum as (numerator, denominator) and the volume sum over lo..hi."""
    terms: dict[int, int] = {}
    volume = 0
    for i in range(lo, hi+1):
        if assessed[i].empty:
            continue
        fact = facts[i]
        high, low, close, shares = (cast(int, fact.high), cast(int, fact.low),
                                    cast(int, fact.close), cast(int, fact.volume))
        volume += shares
        spread = high - low
        # Zero range: multiplier 0, but the volume above still counts in the CMF denominator.
        if spread > 0:
            terms[spread] = terms.get(spread, 0) + (2*close - high - low) * shares
    numerator, denominator = _rational_sum(terms)
    return numerator, denominator, volume


def _obv(facts: tuple[SlotFacts, ...], assessed: dict[int, _Slot], lo: int, hi: int) -> int:
    total = 0
    base: int | None = None
    for i in range(lo, hi+1):
        if assessed[i].empty:
            continue
        close, shares = cast(int, facts[i].close), cast(int, facts[i].volume)
        # The first priced bar of the epoch only supplies the base; ties add 0; empty slots are never the base.
        if base is not None and close != base:
            total += shares if close > base else -shares
        base = close
    return total


def compute_money_flow(batches: tuple[CanonicalBatch, ...] | None, context: IntradayContext,
                       config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef2-mf1 outputs over supplied BARs with volume; deterministic, batch and full replay only."""
    settings = decode_money_flow_config(context, config)
    if (type(features) is not tuple or not 1 <= len(features) <= len(describe_money_flow())
            or any(type(feature) is not str for feature in features) or len(set(features)) != len(features)):
        fail("nonempty unique selected feature IDs required")
    known = {entry.feature_id for entry in describe_money_flow()}
    if any(feature not in known for feature in features):
        fail("unknown selected money-flow feature", ErrorCode.UNKNOWN_FEATURE)
    selected = tuple(sorted(features))
    for feature in selected:
        require_money_flow_capability(feature, "batch")
    # The CMF window is a caller parameter bound in the config exactly when intraday.cmf is selected.
    if (CMF in selected) != (settings.cmf_period is not None):
        fail("cmf_period is required exactly when intraday.cmf is selected")
    admitted = admit(batches, context, config) if batches is not None else None
    a, t = context.anchor_index, context.target_index
    epoch = t-a+1
    period = settings.cmf_period
    cutoff = config.availability.knowledge_cutoff_ns
    entity = EntityKey(context.instrument_id, config.session.session_id)
    facts = None if admitted is None else admitted.facts
    assessments: dict[tuple[str, ...], dict[int, _Slot]] = {}

    def verdicts(fields: tuple[str, ...], lo: int) -> dict[int, _Slot]:
        if fields not in assessments:
            assessments[fields] = {}
        cache = assessments[fields]
        assert facts is not None
        for i in range(lo, t+1):
            if i not in cache:
                cache[i] = _assess(facts[i], fields, cutoff)
        return cache

    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        cmf = feature == CMF
        lo = max(a, t-cast(int, period)+1) if cmf else a
        expected = cast(int, period) if cmf else epoch
        fields = _OBV_FIELDS if feature == OBV else _FLOW_FIELDS
        value: int | float | None = None
        reasons: set[Reason] = set()
        observed = 0
        if facts is None:
            # An absent delivery stops at absent_input; consequent history reasons are suppressed.
            reasons.add(Reason.ABSENT_INPUT)
        else:
            assessed = verdicts(fields, lo)
            for i in range(lo, t+1):
                reasons.update(assessed[i].reasons)
                observed += not assessed[i].reasons
            if cmf and t-cast(int, period)+1 < a:
                reasons.add(Reason.INSUFFICIENT_HISTORY)
        status = _status(reasons)
        if status == Status.AVAILABLE:
            assert facts is not None
            if feature == OBV:
                value = _obv(facts, assessed, a, t)
                if not I64_MIN <= value <= I64_MAX:
                    fail("published OBV outside int64", ErrorCode.OVERFLOW)
            else:
                numerator, denominator, volume = _flow(facts, assessed, lo, t)
                if cmf and volume == 0:
                    reasons.add(Reason.ZERO_DENOMINATOR)
                    status = Status.NOT_APPLICABLE
                else:
                    # One correctly rounded binary64 conversion of the exact rational (round-half-even).
                    value = numerator / (denominator*volume if cmf else denominator)
        if status == Status.AVAILABLE:
            # Witnesses are the original rows only: anchor then target, or first then last window slot.
            for i in dict.fromkeys((lo, t)):
                fact = facts[i]  # type: ignore[index]
                if fact.row_index is None or fact.input_id is None or len(evidence) >= settings.evidence_limit:
                    continue
                evidence.append(EvidenceRow(entity, feature, fact.input_id, f"slot:{i}", fact.slot.end_ns,
                    fact.known_at_ns, fact.slot.start_ns, fact.slot.end_ns, "consumed", None, "completed_interval"))
        dtype = ValueType.INT64 if feature == OBV else ValueType.FLOAT64
        columns.append(FeatureColumn(feature, MONEY_FLOW_ALGORITHM, dtype, _UNITS[feature], (entity,), (value,)))
        ordered = tuple(sorted(reasons, key=lambda reason: reason.value))
        quality.append(QualityRow(entity, feature, status, expected, observed, ordered))
    metadata = ResultMetadata(config.session.namespace, config.session.session_id, config.availability,
                              config.digest, () if admitted is None else admitted.inputs,
                              "intraday.python", PACKAGE_VERSION, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
