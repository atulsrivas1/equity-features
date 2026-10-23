"""Pure EF4 rate projection (ef4-rate1): trailing trade, share-volume and notional rates of an exact declared window,
the raw sampled endpoint return and the difference of the rates of two equal-duration windows.

Rates divide by the declared window duration, never by the span of observed events. An observed zero is an available
`+0.0`; an absent operand is `absent_input`, never zero. The tape operands (`ef4.tape.count|volume|notional`) are
consumed by documented name only (their carrier is provisional until contract G is accepted). Exact rational
arithmetic, one correctly rounded float64 per published value. No clock, I/O, storage or default.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureResult, InputBinding, Parameter, PriceUnit, Reason, SessionSpec, ValueType,
)
from ..ef3._common import fail, integer, label
from ..ef3._robust_common import make_config, parameter_map
from ._legs import Leg, check_leg_bounds, check_legs, parse_legs
from ._proj_common import (
    DEC128_LIMIT, I64_MAX, MAX_NS, Cell, RefRow, canonical_decimal, check_features, check_meta, check_policy,
    finish, fraction_float, knowledge_reason, reference_rows,
)

RATE_IDENTITY = "ef4.rate_projection"
RATE_ALGORITHM = "ef4-rate-projection-v1"
# The label names the whole convention set (declared-window denominator, observed zero is a value, an absent operand is
# not zero, window-start and end witnesses of one session, difference of rates of equal-duration windows).
RATE_POLICY = "ef4-rate1"
ROLES = ("tape", "legs")
TRADE_RATE = "rate.window.trade_rate"
NOTIONAL_RATE = "rate.window.notional_rate"
SHARE_VOLUME_RATE = "rate.window.share_volume_rate"
RAW_RETURN = "rate.window.raw_return_fraction"
RATE_DIFFERENCE = "rate.window.return_rate_difference"
RATE_FEATURES = (NOTIONAL_RATE, RAW_RETURN, RATE_DIFFERENCE, SHARE_VOLUME_RATE, TRADE_RATE)
RATE_META: dict[str, tuple[ValueType, str]] = {
    TRADE_RATE: (ValueType.FLOAT64, "trades_per_second"), NOTIONAL_RATE: (ValueType.FLOAT64, "currency_per_second"),
    SHARE_VOLUME_RATE: (ValueType.FLOAT64, "shares/s"), RAW_RETURN: (ValueType.FLOAT64, "fraction"),
    RATE_DIFFERENCE: (ValueType.FLOAT64, "fraction_per_second"),
}
_TAPE = {TRADE_RATE: "count", NOTIONAL_RATE: "notional", SHARE_VOLUME_RATE: "volume"}
TAPE_KINDS = {"ef4.tape.count": "count", "ef4.tape.volume": "volume", "ef4.tape.notional": "notional"}
ADJACENCIES = ("adjacent", "disjoint")
_REQUIRED = frozenset({"policy_version", "window_ns", "max_endpoint_age_ns", "evidence_limit"})
_OPTIONAL = frozenset({"alignment_tolerance_ns", "adjacency"})


@dataclass(frozen=True)
class RateProjectionSettings:
    policy_version: str
    window_ns: int
    max_endpoint_age_ns: int
    evidence_limit: int
    alignment_tolerance_ns: int | None
    adjacency: str | None


def _check(policy: object, window: object, age: object, limit: object, tolerance: object,
           adjacency: object, defer_version: bool = False) -> RateProjectionSettings:
    width = integer(window, 1, MAX_NS)
    max_age = integer(age, 0, MAX_NS)
    evidence_limit = integer(limit, 0, 10000)
    tol = None if tolerance is None else integer(tolerance, 0, MAX_NS)
    side: str | None = None
    if adjacency is not None:
        if type(adjacency) is not str or adjacency not in ADJACENCIES:
            fail(ErrorCode.INVALID_CONFIG, "adjacency must be adjacent or disjoint")
        side = adjacency
    if not (defer_version and type(policy) is str):
        check_policy(policy, RATE_POLICY)
    assert type(policy) is str
    return RateProjectionSettings(policy, width, max_age, evidence_limit, tol, side)


def build_rate_projection_config(*, policy_version: str | None = None, window_ns: int | None = None,
                                 max_endpoint_age_ns: int | None = None, alignment_tolerance_ns: int | None = None,
                                 adjacency: str | None = None, session: SessionSpec,
                                 availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit,
                                 evidence_limit: int | None = None) -> ConfigSpec:
    """Final ConfigSpec; the tolerance and adjacency are present exactly when their outputs are selected."""
    s = _check(policy_version, window_ns, max_endpoint_age_ns, evidence_limit, alignment_tolerance_ns, adjacency)
    params = [Parameter("policy_version", s.policy_version), Parameter("window_ns", s.window_ns),
              Parameter("max_endpoint_age_ns", s.max_endpoint_age_ns), Parameter("evidence_limit", s.evidence_limit)]
    if s.alignment_tolerance_ns is not None:
        params.append(Parameter("alignment_tolerance_ns", s.alignment_tolerance_ns))
    if s.adjacency is not None:
        params.append(Parameter("adjacency", s.adjacency))
    return make_config(RATE_IDENTITY, RATE_ALGORITHM, tuple(params), 1, session, availability, adjustment, price_unit)


def decode_rate_projection_config(config: ConfigSpec, *, defer_version: bool = False) -> RateProjectionSettings:
    """Validate the closed rate-projection envelope and return its settings."""
    v = parameter_map(config, RATE_IDENTITY, RATE_ALGORITHM, _REQUIRED, _OPTIONAL)
    s = _check(v["policy_version"], v["window_ns"], v["max_endpoint_age_ns"], v["evidence_limit"],
               v.get("alignment_tolerance_ns"), v.get("adjacency"), defer_version)
    if defer_version and s.policy_version != RATE_POLICY:
        return s
    assert config.price_unit is not None
    expected = build_rate_projection_config(
        policy_version=s.policy_version, window_ns=s.window_ns, max_endpoint_age_ns=s.max_endpoint_age_ns,
        alignment_tolerance_ns=s.alignment_tolerance_ns, adjacency=s.adjacency, session=config.session,
        availability=config.availability, adjustment=config.adjustment, price_unit=config.price_unit,
        evidence_limit=s.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical rate-projection envelope")
    return s


def check_selection(settings: RateProjectionSettings, selected: tuple[str, ...]) -> None:
    returns = RAW_RETURN in selected or RATE_DIFFERENCE in selected
    if (returns != (settings.alignment_tolerance_ns is not None)
            or (RATE_DIFFERENCE in selected) != (settings.adjacency is not None)):
        fail(ErrorCode.INVALID_CONFIG, "optional parameters must be present exactly when their outputs are selected")


@dataclass(frozen=True)
class TapeFact:
    kind: str
    start: int
    end: int
    value: int
    known_at: int | None


def _tape(rows: list[RefRow], config: ConfigSpec) -> list[tuple[TapeFact, RefRow]]:
    facts: list[tuple[TapeFact, RefRow]] = []
    for row in rows:
        if row.end is None:
            fail(ErrorCode.INVALID_SCHEMA, "a tape operand carries its window end")
        if row.price is not None:
            fail(ErrorCode.INVALID_SCHEMA, "a tape operand carries no price")
        kind = TAPE_KINDS[row.kind]
        value = canonical_decimal(row.text, DEC128_LIMIT if kind == "notional" else I64_MAX + 1)
        facts.append((TapeFact(kind, row.start, row.end, value, row.known_at), row))
    return facts


def compute_rate_projection(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                            config: ConfigSpec, *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef4-rate1 outputs; `batches` is the fixed (tape, legs) slots, each nullable."""
    if type(batches) not in (tuple, list) or len(batches) != 2:
        fail(ErrorCode.INVALID_SCHEMA, "the fixed roles (tape, legs) are required")
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    tape_batch, legs_batch = batches
    names = [f for f in features if type(f) is str] if type(features) is tuple else []
    tape_wanted = any(f in _TAPE for f in names)
    legs_wanted = RAW_RETURN in names or RATE_DIFFERENCE in names
    tape_rows = reference_rows(tape_batch, frozenset(TAPE_KINDS)) if tape_batch is not None and tape_wanted else []
    leg_rows = (reference_rows(legs_batch, frozenset({"ef4.leg.start", "ef4.leg.end"}))
                if legs_batch is not None and legs_wanted else [])
    tape = _tape(tape_rows, config)
    legs = parse_legs(leg_rows, frozenset({"window_start"}), frozenset({"A", "B"}))
    settings = decode_rate_projection_config(config, defer_version=True)
    selected = check_features(features, RATE_FEATURES)
    check_selection(settings, selected)
    has_notional = any(fact.kind == "notional" for fact, _ in tape)
    if tape_batch is not None and tape_wanted:
        check_meta(tape_batch, config, unit=has_notional, adjustment=True)
        if has_notional and tape_batch.metadata.price_unit is None:
            fail(ErrorCode.INVALID_UNIT, "a notional operand declares the PriceUnit")
    if legs_batch is not None and legs_wanted:
        check_meta(legs_batch, config, unit=True, adjustment=True)
    check_policy(settings.policy_version, RATE_POLICY)
    if (tape_batch is not None and legs_batch is not None and tape_wanted and legs_wanted
            and tape_batch.metadata.source.input_id == legs_batch.metadata.source.input_id):
        fail(ErrorCode.DUPLICATE, "distinct actual role input IDs required")
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    target = entity.instrument_id
    seen: set[str] = set()
    for fact, row in tape:
        if row.instrument != target or row.session != entity.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "a tape operand belongs to the target instrument and session")
        if fact.kind in seen:
            fail(ErrorCode.DUPLICATE, "two tape operands of one kind")
        seen.add(fact.kind)
    check_legs(legs, frozenset([target]))
    check_leg_bounds(legs)
    tape_by_kind = {fact.kind: fact for fact, _ in tape}
    cutoff, knowledge = config.availability.market_cutoff_ns, config.availability.knowledge_cutoff_ns
    window = settings.window_ns
    seconds = Fraction(window, 10**9)
    scale = config.price_unit.scale if config.price_unit is not None else 0
    tape_input = "" if tape_batch is None else tape_batch.metadata.source.input_id
    legs_input = "" if legs_batch is None else legs_batch.metadata.source.input_id
    starts = {(leg.instrument, leg.slot): leg for leg in legs if leg.is_start}
    ends = {(leg.instrument, leg.slot): leg for leg in legs if not leg.is_start}
    cells: dict[str, Cell] = {}
    for feature in selected:
        if feature in _TAPE:
            kind = _TAPE[feature]
            fact = tape_by_kind.get(kind)
            if fact is None:
                cells[feature] = Cell(None, {Reason.ABSENT_INPUT}, 1, 0)
                continue
            cause = knowledge_reason(fact.known_at, knowledge)
            if cause is not None:
                cells[feature] = Cell(None, {cause}, 1, 0)
                continue
            why: set[Reason] = set()
            if fact.end > cutoff:
                why.add(Reason.FUTURE_MARKET)
            if fact.end - fact.start != window:
                why.add(Reason.INELIGIBLE)
            if fact.end <= cutoff and cutoff - fact.end > settings.max_endpoint_age_ns:
                why.add(Reason.INELIGIBLE)
            cell = Cell(None, why, 1, 1)
            cells[feature] = cell
            if why:
                continue
            amount = Fraction(fact.value, 10**scale) if kind == "notional" else Fraction(fact.value)
            cell.value = fraction_float(amount / seconds)
            cell.witnesses = [EvidenceRow(entity, feature, tape_input, f"tape:{kind}", fact.end, fact.known_at,
                                          fact.start, fact.end, "consumed", None, "ordinary")]
            continue
        slots = ("A",) if feature == RAW_RETURN else ("A", "B")
        pairs = [(starts.get((target, slot)), ends.get((target, slot))) for slot in slots]
        miss: set[Reason] = set()
        known = 0
        for pair in pairs:
            for leg in pair:
                if leg is None:
                    miss.add(Reason.ABSENT_INPUT)
                    continue
                cause = knowledge_reason(leg.known_at, knowledge)
                if cause is None:
                    known += 1
                else:
                    miss.add(cause)
        cell = Cell(None, miss, 2 * len(slots), known)
        cells[feature] = cell
        if miss:
            continue
        assert settings.alignment_tolerance_ns is not None
        tolerance = settings.alignment_tolerance_ns
        causes = cell.reasons if cell.reasons is not None else set()
        legs_pairs: list[tuple[Leg, Leg]] = []
        for n, (s_leg, e_leg) in enumerate(pairs):
            assert s_leg is not None and e_leg is not None
            legs_pairs.append((s_leg, e_leg))
            if e_leg.t > cutoff:
                causes.add(Reason.FUTURE_MARKET)
            if (s_leg.act != e_leg.act or s_leg.session != e_leg.session
                    or abs((e_leg.t - s_leg.t) - window) > tolerance):
                causes.add(Reason.INELIGIBLE)
            if n == 0 and e_leg.t <= cutoff and cutoff - e_leg.t > settings.max_endpoint_age_ns:
                causes.add(Reason.INELIGIBLE)
        if feature == RATE_DIFFERENCE:
            (start_a, _), (_, end_b) = legs_pairs
            if settings.adjacency == "adjacent":
                if abs(start_a.t - end_b.t) > tolerance:
                    causes.add(Reason.INELIGIBLE)
            elif end_b.t - start_a.t > tolerance:
                causes.add(Reason.INELIGIBLE)
        if causes:
            continue
        returns = [Fraction(e.price, s.price) - 1 for s, e in legs_pairs]
        witnesses: list[EvidenceRow] = []
        for slot, (s_leg, e_leg) in zip(slots, legs_pairs):
            witnesses.append(s_leg.evidence(entity, feature, legs_input, f"leg:{target}:start:{slot}"))
            witnesses.append(e_leg.evidence(entity, feature, legs_input, f"leg:{target}:end:{slot}"))
        cell.witnesses = witnesses
        if feature == RAW_RETURN:
            cell.value = fraction_float(returns[0])
        else:
            cell.value = fraction_float(returns[0] / seconds - returns[1] / seconds)
    bindings: list[InputBinding] = []
    if tape_batch is not None and tape_wanted:
        bindings.append(InputBinding("tape", DataKind.REFERENCE, tape_batch.metadata))
    if legs_batch is not None and legs_wanted:
        bindings.append(InputBinding("legs", DataKind.REFERENCE, legs_batch.metadata))
    return finish(config, entity, RATE_ALGORITHM, selected, RATE_META, cells, tuple(bindings),
                  settings.evidence_limit)
