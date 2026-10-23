"""Pure EF4 quote dynamics (ef4-quote1): maximum spread and midpoint bps, size-tilted microprice, first-to-last change.

Over the admitted quote observations of the declared interval `[S, E)` (full bid/ask states in the total order
`(event_ns, order_key, event_id)`): an observation is invalid (a null or nonpositive side), normal (a > b), locked
(a = b) or crossed (a < b); valid is normal or locked. A valid observation has the cash spread `s = a - b`, the exact
midpoint `m = (a + b) / 2` and its own basis points `z = 10000 s / m`; with both sizes positive its microprice is
`(b Qa + a Qb) / (Qa + Qb)`. Everything runs on exact integers and `Fraction`s and every published float64 is one
correctly rounded rational. No seed, staleness limit, size or time weighting across observations, and no state.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, FeatureResult,
    Parameter, PriceUnit, Reason, SessionSpec, ValueType,
)
from ..ef3._common import fail
from ..ef3._robust_common import check_entity, columns_of
from ._common import (
    SAMPLINGS, Out, Witness, admit_bounds, assemble, bindings_of, check_closed, check_limit, check_meta, check_roles,
    declared_coverage, knowledge_reason, make_config, parameter_values, shared_validation, unavailable,
)

QUOTE_IDENTITY = "ef4.quote_dynamics"
QUOTE_ALGORITHM = "ef4-quote-dynamics-v1"
# The label names the whole convention set (classification, size rule, microprice, change rule, tie rule, interval and
# cutoff rule, missingness mapping, rounding).
QUOTE_POLICY = "ef4-quote1"
MAX_SPREAD = "quote.sampled.maximum_spread"
MAX_MIDPOINT_BPS = "quote.sampled.maximum_midpoint_bps"
MICRO_LAST = "quote.microprice.last"
MICRO_OFFSET = "quote.microprice.last_offset_bps"
MICRO_MEAN = "quote.microprice.mean"
CHANGE_BPS = "quote.change.midpoint_bps"
CHANGE_SPREAD = "quote.change.spread"
PAIR_COUNT = "quote.change.pair_count"
CHANGE_COUNT = "quote.change.midpoint_change_count"
QUOTE_FEATURES = (CHANGE_BPS, CHANGE_COUNT, PAIR_COUNT, CHANGE_SPREAD, MICRO_LAST, MICRO_OFFSET, MICRO_MEAN,
                  MAX_MIDPOINT_BPS, MAX_SPREAD)
FEATURE_META: dict[str, tuple[ValueType, str]] = {
    MAX_SPREAD: (ValueType.FLOAT64, "currency/share"), MAX_MIDPOINT_BPS: (ValueType.FLOAT64, "bps"),
    MICRO_LAST: (ValueType.FLOAT64, "currency/share"), MICRO_OFFSET: (ValueType.FLOAT64, "bps"),
    MICRO_MEAN: (ValueType.FLOAT64, "currency/share"), CHANGE_BPS: (ValueType.FLOAT64, "bps"),
    CHANGE_SPREAD: (ValueType.FLOAT64, "currency/share"), PAIR_COUNT: (ValueType.INT64, "pairs"),
    CHANGE_COUNT: (ValueType.INT64, "pairs"),
}
CONTINUOUS_ONLY = frozenset({CHANGE_BPS, CHANGE_SPREAD, PAIR_COUNT, CHANGE_COUNT})
_REQUIRED = frozenset({"policy_version", "sampling", "evidence_limit"})
_BPS = Fraction(10000)


@dataclass(frozen=True)
class QuoteDynamicsSettings:
    policy_version: str
    sampling: str
    evidence_limit: int


def _check(policy: object, sampling: object, limit: object) -> QuoteDynamicsSettings:
    if type(policy) is not str:
        fail(ErrorCode.INVALID_CONFIG, "exact policy label required")
    if policy != QUOTE_POLICY:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported policy label")
    if sampling not in SAMPLINGS:
        fail(ErrorCode.INVALID_CONFIG, "sampling must be trade_snapshot or continuous")
    assert type(sampling) is str
    return QuoteDynamicsSettings(policy, sampling, check_limit(limit))


def build_quote_dynamics_config(*, policy_version: str | None = None, sampling: str | None = None,
                                session: SessionSpec, availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                                price_unit: PriceUnit, evidence_limit: int | None = None) -> ConfigSpec:
    """Final ConfigSpec; every parameter is explicit with no default."""
    s = _check(policy_version, sampling, evidence_limit)
    params = (Parameter("policy_version", s.policy_version), Parameter("sampling", s.sampling),
              Parameter("evidence_limit", s.evidence_limit))
    return make_config(QUOTE_IDENTITY, QUOTE_ALGORITHM, params, session, availability, adjustment, price_unit)


def _decode(config: ConfigSpec, features: tuple[str, ...] | None) -> tuple[QuoteDynamicsSettings, tuple[str, ...]]:
    values, selected = parameter_values(config, QUOTE_IDENTITY, QUOTE_ALGORITHM, QUOTE_POLICY, features,
                                        QUOTE_FEATURES)
    check_closed(values, _REQUIRED, frozenset())
    s = _check(values["policy_version"], values["sampling"], values["evidence_limit"])
    assert config.price_unit is not None
    expected = build_quote_dynamics_config(
        policy_version=s.policy_version, sampling=s.sampling, session=config.session,
        availability=config.availability, adjustment=config.adjustment, price_unit=config.price_unit,
        evidence_limit=s.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical quote-dynamics envelope")
    return s, selected


def decode_quote_dynamics_config(config: ConfigSpec) -> QuoteDynamicsSettings:
    """Validate the closed quote-dynamics envelope and return its settings."""
    return _decode(config, None)[0]


@dataclass(frozen=True)
class _Obs:
    row_id: str
    event_ns: int
    known_at: int | None
    reason: Reason | None
    valid: bool
    bid_size: int | None
    ask_size: int | None
    s: Fraction = Fraction(0)
    m: Fraction = Fraction(0)
    z: Fraction = Fraction(0)
    mp: Fraction | None = None

    def witness(self, input_id: str) -> Witness:
        return Witness(input_id, self.row_id, self.event_ns, self.known_at)


def _observation(row_id: str, event_ns: int, known_at: int | None, reason: Reason | None, bid: int | None,
                 ask: int | None, bid_size: int | None, ask_size: int | None) -> _Obs:
    if bid is None or ask is None or bid <= 0 or ask <= 0 or bid > ask:
        return _Obs(row_id, event_ns, known_at, reason, False, bid_size, ask_size)
    s, m = Fraction(ask - bid), Fraction(ask + bid, 2)
    mp = None
    if bid_size is not None and ask_size is not None and bid_size > 0 and ask_size > 0:
        mp = Fraction(bid * ask_size + ask * bid_size, ask_size + bid_size)
    return _Obs(row_id, event_ns, known_at, reason, True, bid_size, ask_size, s, m, _BPS * s / m, mp)


def compute_quote_dynamics(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                           config: ConfigSpec, *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef4-quote1 outputs; `batches` is the fixed slots `(bounds, quotes)`, quotes nullable."""
    settings, selected = _decode(config, features)
    entity = check_entity(entity, config)
    slots = check_roles(batches, (DataKind.REFERENCE, DataKind.QUOTE))
    shared_validation(slots, (0, 1), config)
    interval = admit_bounds(slots[0], config, entity)
    quotes = slots[1]
    if settings.sampling == "trade_snapshot" and any(f in CONTINUOUS_ONLY for f in selected):
        fail(ErrorCode.UNSUPPORTED_SAMPLING, "change outputs need continuous sampling")
    cutoff, knowledge = config.availability.market_cutoff_ns, config.availability.knowledge_cutoff_ns
    observations: list[_Obs] = []
    coverage = "undeclared"
    input_id = ""
    if quotes is not None:
        check_meta(quotes, config, market=True)
        if quotes.metadata.sampling != settings.sampling:
            fail(ErrorCode.UNSUPPORTED_SAMPLING, "config sampling differs from the quote batch sampling")
        cols = columns_of(quotes)
        input_id = quotes.metadata.source.input_id
        for i in range(quotes.row_count):
            if cols["instrument_id"][i] != entity.instrument_id or cols["session_id"][i] != config.session.session_id:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "quote identity differs from the target entity and session")
            if cols["event_ns"][i] < interval.start:
                fail(ErrorCode.BOUNDS, "quote before the interval start")
            if cols["event_ns"][i] >= interval.end:
                fail(ErrorCode.BOUNDS, "quote at or after the interval end")
        coverage = declared_coverage(quotes, interval.start, interval.end)
        for i in range(quotes.row_count):
            known_at = cols["known_at_ns"][i] if "known_at_ns" in cols else None
            observations.append(_observation(
                f"quote:{cols['event_id'][i]}", cols["event_ns"][i], known_at, knowledge_reason(known_at, knowledge),
                cols["bid"][i] if "bid" in cols else None, cols["ask"][i] if "ask" in cols else None,
                cols["bid_size"][i] if "bid_size" in cols else None,
                cols["ask_size"][i] if "ask_size" in cols else None))
    bindings = bindings_of((("bounds", slots[0]), ("quotes", quotes)))
    n = len(observations)
    if quotes is None or (n == 0 and coverage == "undeclared"):
        outs = {f: unavailable({Reason.ABSENT_INPUT}, 0, 0) for f in selected}
        return assemble(config, entity, selected, outs, FEATURE_META, QUOTE_ALGORITHM, settings.evidence_limit,
                        bindings)
    bounds_reason = knowledge_reason(interval.known_at, knowledge)
    assert config.price_unit is not None
    scale = Fraction(10**config.price_unit.scale)
    valid = [o for o in observations if o.valid]
    sized = [o for o in valid if o.mp is not None]
    final = observations[-1] if observations else None
    pairs = [(a, b) for a, b in zip(observations, observations[1:]) if a.valid and b.valid]

    def evaluate(feature: str) -> Out:
        reasons: set[Reason] = set()
        bad: set[int] = set()
        if bounds_reason is not None:
            reasons.add(bounds_reason)
        for i, o in enumerate(observations):
            if o.reason is not None:
                reasons.add(o.reason)
                bad.add(i)
        if feature == MICRO_MEAN:
            need = [i for i, o in enumerate(observations) if o.valid]
        elif feature in (MICRO_LAST, MICRO_OFFSET):
            need = [n - 1] if final is not None and final.valid else []
        else:
            need = []
        for i in need:
            if observations[i].bid_size is None or observations[i].ask_size is None:
                reasons.add(Reason.NULL_FIELD)
                bad.add(i)
        if coverage == "incomplete":
            reasons.add(Reason.GOVERNED_GAP)
        if cutoff < interval.end:
            reasons.add(Reason.FUTURE_MARKET)
        if reasons:
            return unavailable(reasons, n, 0 if bounds_reason is not None else n - len(bad))
        none = unavailable({Reason.NO_ELIGIBLE_OBSERVATIONS}, n, n)

        def result(value: Fraction | int, witnesses: list[_Obs]) -> Out:
            return Out(value, frozenset(), n, n, [w.witness(input_id) for w in witnesses])

        if feature == MAX_SPREAD:
            if not valid:
                return none
            best = max(o.s for o in valid)
            return result(best / scale, [next(o for o in valid if o.s == best)])
        if feature == MAX_MIDPOINT_BPS:
            if not valid:
                return none
            best = max(o.z for o in valid)
            return result(best, [next(o for o in valid if o.z == best)])
        if feature in (MICRO_LAST, MICRO_OFFSET):
            if final is None or final.mp is None:
                return none
            if feature == MICRO_LAST:
                return result(final.mp / scale, [final])
            return result(_BPS * (final.mp - final.m) / final.m, [final])
        if feature == MICRO_MEAN:
            if not sized:
                return none
            assert all(o.mp is not None for o in sized)
            return result(sum((o.mp for o in sized if o.mp is not None), Fraction(0)) / len(sized) / scale, sized)
        if feature in (CHANGE_BPS, CHANGE_SPREAD):
            if len(valid) >= 2:
                first, last = valid[0], valid[-1]
                value = _BPS * (last.m - first.m) / first.m if feature == CHANGE_BPS else (last.s - first.s) / scale
                return result(value, [first, last])
            if len(valid) == 1:
                return unavailable({Reason.INSUFFICIENT_HISTORY}, 2, 1)
            return none
        counted = pairs if feature == PAIR_COUNT else [(a, b) for a, b in pairs if a.m != b.m]
        rows: list[_Obs] = []
        seen: set[str] = set()
        for a, b in counted:
            for o in (a, b):
                if o.row_id not in seen:
                    seen.add(o.row_id)
                    rows.append(o)
        return result(len(counted), rows)

    outs = {f: evaluate(f) for f in selected}
    return assemble(config, entity, selected, outs, FEATURE_META, QUOTE_ALGORITHM, settings.evidence_limit, bindings)

