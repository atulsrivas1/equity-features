"""Pure EF4 tape producer `ef4.tape_window_sign` (ef4-tape1): rolling trade window totals and tick-rule signed volume.

The window is `[C - W, C)`. The tick sign runs over the whole epoch (the eligible prints from the session open up to C
in the supplied `(event_ns, order_key)` order): `s_i = 0` without a reference, `+1` / `-1` on a price change and the
previous sign on an unchanged price; the reference is the seed `(price, sign)` when one is supplied. Expiry affects only
the totals. Every sum is an exact integer (checked int64 volumes, decimal128 notional coefficients); the only float is
`tape.tick.imbalance`, one correctly rounded division. These are tick-rule proxies, not aggressor or dealer positions.
Readiness is static per output (DP-T12); there is no default, no state and no clock.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata, SessionSpec,
    Status, ValueType, checked_decimal128, checked_int64, require_compatible_inputs, validate_batch,
)
from equity_features import __version__
from equity_features.ef3._common import fail, integer
from equity_features.ef3._robust_common import (
    _check_meta, check_entity, check_features, check_policy, check_reference_id, check_slots, columns_of, first_status,
    make_config, ordered, parameter_map,
)
from equity_features.ef3._stats import to_float
from ._tape_common import I64_MAX, admit_trades, eligibility_policy, knowledge_flags

TAPE_IDENTITY = "ef4.tape_window_sign"
TAPE_ALGORITHM = "ef4-tape-window-v1"
# The label names the whole convention set (window endpoints, order, tick sign with carry, seed rule, eligibility,
# expiry, static readiness closure, rounding).
TAPE_POLICY = "ef4-tape1"
SEED_POLICIES = ("none", "supplied")
SEED_KIND = "ef4.tick.seed"
COUNT = "tape.window.count"
VOLUME = "tape.window.volume"
NOTIONAL = "tape.window.notional"
UP = "tape.tick.up_volume"
DOWN = "tape.tick.down_volume"
NEUTRAL = "tape.tick.neutral_volume"
NET_VOLUME = "tape.tick.net_volume"
NET_NOTIONAL = "tape.tick.net_notional"
IMBALANCE = "tape.tick.imbalance"
TAPE_FEATURES = tuple(sorted((COUNT, DOWN, IMBALANCE, NET_NOTIONAL, NET_VOLUME, NEUTRAL, NOTIONAL, UP, VOLUME)))
_MONEY = "currency coefficient / 10^price_scale"
FEATURE_META: dict[str, tuple[ValueType, str]] = {
    COUNT: (ValueType.INT64, "trades"), VOLUME: (ValueType.INT64, "shares"), NOTIONAL: (ValueType.DECIMAL128, _MONEY),
    UP: (ValueType.INT64, "shares"), DOWN: (ValueType.INT64, "shares"), NEUTRAL: (ValueType.INT64, "shares"),
    NET_VOLUME: (ValueType.INT64, "shares"), NET_NOTIONAL: (ValueType.DECIMAL128, _MONEY),
    IMBALANCE: (ValueType.FLOAT64, "fraction"),
}
WINDOW_CLASS = (COUNT, VOLUME, NOTIONAL)
ROLES = ("trades", "seed")
_REQUIRED = frozenset({"policy_version", "window_ns", "seed_policy", "evidence_limit", "eligibility_policy"})
_SIGNS = {"+": 1, "-": -1, "0": 0}


@dataclass(frozen=True)
class TapeWindowSettings:
    policy_version: str
    window_ns: int
    seed_policy: str
    evidence_limit: int
    eligibility_policy: str


def _check(policy: object, window: object, seed_policy: object, limit: object, eligibility: object) -> TapeWindowSettings:
    window_ns = integer(window, 1, I64_MAX)
    if type(seed_policy) is not str or seed_policy not in SEED_POLICIES:
        fail(ErrorCode.INVALID_CONFIG, "seed_policy must be none or supplied")
    evidence_limit = integer(limit, 0, 10000)
    policy_label = eligibility_policy(eligibility)
    check_policy(policy, TAPE_POLICY)
    assert type(policy) is str
    return TapeWindowSettings(policy, window_ns, seed_policy, evidence_limit, policy_label)


def build_tape_window_config(*, policy_version: str | None = None, window_ns: int | None = None,
                             seed_policy: str | None = None, evidence_limit: int | None = None,
                             eligibility_policy: str | None = None, session: SessionSpec,
                             availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                             price_unit: PriceUnit) -> ConfigSpec:
    """Final ConfigSpec; every parameter is explicit with no default. Opening and closing auction inclusion must be false."""
    s = _check(policy_version, window_ns, seed_policy, evidence_limit, eligibility_policy)
    if type(session) is SessionSpec and (session.include_opening_auction or session.include_closing_auction):
        fail(ErrorCode.INVALID_CONFIG, "the tape window producer refuses auction inclusion")
    params = (Parameter("policy_version", s.policy_version), Parameter("window_ns", s.window_ns),
              Parameter("seed_policy", s.seed_policy), Parameter("evidence_limit", s.evidence_limit),
              Parameter("eligibility_policy", s.eligibility_policy))
    return make_config(TAPE_IDENTITY, TAPE_ALGORITHM, params, 1, session, availability, adjustment, price_unit)


def decode_tape_window_config(config: ConfigSpec) -> TapeWindowSettings:
    """Validate the closed tape-window envelope and return its settings."""
    v = parameter_map(config, TAPE_IDENTITY, TAPE_ALGORITHM, _REQUIRED, frozenset())
    s = _check(v["policy_version"], v["window_ns"], v["seed_policy"], v["evidence_limit"], v["eligibility_policy"])
    assert config.price_unit is not None
    expected = build_tape_window_config(
        policy_version=s.policy_version, window_ns=s.window_ns, seed_policy=s.seed_policy,
        evidence_limit=s.evidence_limit, eligibility_policy=s.eligibility_policy, session=config.session,
        availability=config.availability, adjustment=config.adjustment, price_unit=config.price_unit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical tape-window envelope")
    return s


@dataclass(frozen=True)
class _Seed:
    reference_id: str
    price: int
    sign: int
    start_ns: int
    end_ns: int
    known_at: int | None
    input_id: str


def _admit_seed(batch: CanonicalBatch, trades: CanonicalBatch | None, config: ConfigSpec, entity: EntityKey) -> _Seed:
    """The one `ef4.tick.seed` fact: shared validators first, then the kind, price, sign, identity and bounds rules."""
    _check_meta(batch, config)
    if trades is not None:
        require_compatible_inputs(trades, batch)
    validate_batch(batch, required_fields=())
    cols = columns_of(batch)
    for i in range(batch.row_count):
        if cols["fact_kind"][i] != SEED_KIND:
            fail(ErrorCode.INVALID_SCHEMA, "only ef4.tick.seed facts are accepted in the seed role")
        check_reference_id(cols["reference_id"][i])
        price = cols["price"][i] if "price" in cols else None
        if type(price) is not int or price <= 0:
            fail(ErrorCode.INVALID_SCHEMA, "the seed carries a positive price coefficient")
        text = cols["text"][i] if "text" in cols else None
        if type(text) is not str or text not in _SIGNS:
            fail(ErrorCode.INVALID_SCHEMA, "the seed sign is exactly +, - or 0")
        for name in ("factor_num", "factor_den"):
            if name in cols and cols[name][i] is not None:
                fail(ErrorCode.INVALID_SCHEMA, "the seed carries no rational factor")
        if cols["instrument_id"][i] != entity.instrument_id or cols["session_id"][i] != entity.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "the seed belongs to the target entity and session")
        start = cols["effective_start_ns"][i]
        end = cols["effective_end_ns"][i] if "effective_end_ns" in cols else None
        if type(end) is not int:
            fail(ErrorCode.INVALID_SCHEMA, "the seed carries the session open as its effective end")
        if start >= config.session.open_ns:
            fail(ErrorCode.BOUNDS, "the seed print precedes the session open")
        if end != config.session.open_ns:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "the seed is effective until the session open")
    if batch.row_count != 1:
        fail(ErrorCode.INVALID_SCHEMA, "exactly one seed fact is required")
    return _Seed(cols["reference_id"][0], cols["price"][0], _SIGNS[cols["text"][0]], cols["effective_start_ns"][0],
                 cols["effective_end_ns"][0], cols["known_at_ns"][0] if "known_at_ns" in cols else None,
                 batch.metadata.source.input_id)


@dataclass
class _Sums:
    count: int = 0
    volume: int = 0
    notional: int = 0
    up: int = 0
    down: int = 0
    neutral: int = 0
    net_notional: int = 0


def compute_tape_window(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None], config: ConfigSpec,
                        *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef4-tape1 outputs; `batches` is the fixed nullable slots `(trades, seed)`."""
    selected = check_features(features, TAPE_FEATURES)
    settings = decode_tape_window_config(config)
    entity = check_entity(entity, config)
    trades, seed_batch = check_slots(batches, len(ROLES), (DataKind.TRADE, DataKind.REFERENCE))
    if settings.seed_policy == "none" and seed_batch is not None:
        fail(ErrorCode.INVALID_CONFIG, "a seed fact is supplied while seed_policy is none")
    columns = admit_trades(trades, config, entity, settings.eligibility_policy) if trades is not None else {}
    seed = _admit_seed(seed_batch, trades, config, entity) if seed_batch is not None else None
    cutoff, open_ns = config.availability.market_cutoff_ns, config.session.open_ns
    low = cutoff - settings.window_ns
    supplied = settings.seed_policy == "supplied"
    limit = settings.evidence_limit
    n = trades.row_count if trades is not None else 0
    flags = knowledge_flags(columns, n, config)
    has_price, has_size = "price" in columns, "size" in columns
    sums = _Sums()
    first = n
    witnesses: list[int] = []
    if trades is not None:
        stamps, eligible = columns["event_ns"], columns["eligible"]
        first = next((i for i in range(n) if stamps[i] >= low), n)
        reference = seed.price if seed is not None else None
        carried = seed.sign if seed is not None else 0
        for i in range(n):
            if eligible[i] is not True:
                continue
            sign = 0
            price = columns["price"][i] if has_price else None
            if price is not None:
                sign = 0 if reference is None else 1 if price > reference else -1 if price < reference else carried
                reference, carried = price, sign
            if i < first:
                continue
            sums.count += 1
            if len(witnesses) < limit:
                witnesses.append(i)
            if has_size:
                size = columns["size"][i]
                sums.volume += size
                if price is not None:
                    sums.notional += price * size
                    sums.net_notional += sign * price * size
                if sign > 0:
                    sums.up += size
                elif sign < 0:
                    sums.down += size
                else:
                    sums.neutral += size
    cov = trades.metadata.coverage if trades is not None else None
    gap = cov is not None and (not cov.complete or cov.expected != n)
    window_unready = sum(1 for flag in flags[first:] if flag is not None)
    window_reasons = {flag for flag in flags[first:] if flag is not None}
    all_unready = sum(1 for flag in flags if flag is not None)
    all_reasons = {flag for flag in flags if flag is not None}
    seed_reason = None if seed is None else config.availability.knowledge_reason(seed.known_at)

    def evaluate(feature: str) -> tuple[int | float | None, set[Reason], int | None, int, list[EvidenceRow]]:
        if cov is None:
            return None, {Reason.ABSENT_INPUT}, 0, 0, []
        tick = feature not in WINDOW_CLASS
        absent = (feature not in (COUNT, VOLUME) and not has_price) or (feature != COUNT and not has_size)
        reasons: set[Reason] = {Reason.ABSENT_INPUT} if absent else set()
        reasons |= all_reasons if tick else window_reasons
        unready = all_unready if tick else window_unready
        slot = tick and supplied
        ready = 0
        if slot:
            if seed is None:
                reasons.add(Reason.ABSENT_INPUT)
            elif seed_reason is not None:
                reasons.add(Reason(seed_reason))
            else:
                ready = 1
        if gap:
            reasons.add(Reason.GOVERNED_GAP)
        if low < open_ns:
            reasons.add(Reason.INSUFFICIENT_HISTORY)
        expected = None if cov.expected is None else cov.expected + int(slot)
        observed = 0 if absent else n - unready + ready
        if reasons:
            return None, reasons, expected, observed, []
        net = sums.up - sums.down
        value: int | float | None
        if feature == COUNT:
            value = sums.count
        elif feature == VOLUME:
            value = checked_int64(sums.volume)
        elif feature == NOTIONAL:
            value = checked_decimal128(sums.notional)
        elif feature == UP:
            value = checked_int64(sums.up)
        elif feature == DOWN:
            value = checked_int64(sums.down)
        elif feature == NEUTRAL:
            value = checked_int64(sums.neutral)
        elif feature == NET_VOLUME:
            value = checked_int64(net)
        elif feature == NET_NOTIONAL:
            value = checked_decimal128(sums.net_notional)
        else:
            checked_int64(sums.volume)
            if sums.volume == 0:
                return None, {Reason.ZERO_DENOMINATOR}, expected, observed, []
            value = to_float(Fraction(net, sums.volume))
        rows: list[EvidenceRow] = []
        if slot and seed is not None and seed_batch is not None:
            rows.append(EvidenceRow(entity, feature, seed.input_id, f"seed:{seed.reference_id}", seed.start_ns,
                                    seed.known_at, seed.start_ns, seed.end_ns, "consumed", None, "ordinary"))
        assert trades is not None
        for i in witnesses:
            rows.append(EvidenceRow(entity, feature, trades.metadata.source.input_id, f"trade:{columns['event_id'][i]}",
                                    columns["event_ns"][i],
                                    columns["known_at_ns"][i] if "known_at_ns" in columns else None,
                                    None, None, "consumed", None, "ordinary"))
        return value, set(), expected, observed, rows[:limit]

    values: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        value, reasons, expected, observed, rows = evaluate(feature)
        dtype, unit = FEATURE_META[feature]
        status = Status.AVAILABLE if not reasons else first_status(reasons)
        values.append(FeatureColumn(feature, TAPE_ALGORITHM, dtype, unit, (entity,), (value,)))
        quality.append(QualityRow(entity, feature, status, expected, observed, ordered(reasons)))
        evidence.extend(rows)
    bindings = []
    if trades is not None:
        bindings.append(InputBinding("trades", DataKind.TRADE, trades.metadata))
    if seed_batch is not None:
        bindings.append(InputBinding("seed", DataKind.REFERENCE, seed_batch.metadata))
    # The bound is per output (DP-T15): each available output lists at most evidence_limit witnesses.
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
                              tuple(bindings), "python-exact", __version__, limit * len(TAPE_FEATURES))
    return FeatureResult(tuple(values), tuple(quality), metadata, tuple(evidence))

