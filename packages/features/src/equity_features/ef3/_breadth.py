"""Pure EF3 declared-universe session breadth (ef3-breadth1): counts, fractions, volume sums and proximity.

The declared population is the set of selected members at the market cutoff C (`static_snapshot`: every declared member;
`ordered_history`: the members with a stint where start <= C < end). Every denominator is the declared size N, so a
missing member never shrinks it. Each member predicate is three valued; an output is available only when no member is
unknown for it (no partial or lower-bound count). Counts, sums and proximity run on exact integers and rationals; each
published float64 is one correctly rounded division of exact integers. No default, no state across calls.
"""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata,
    SessionSpec, Status, ValueType,
)
from equity_features import __version__
from ._breadth_common import (
    ANY_MODE, NONE_MODE, NONNEG_MODE, NO_REASONS, POSITIVE_MODE, VWAP_MODE, FactRow, Role, Tri, fact_rows,
    member_evidence, resolve, tri_and,
)
from ._common import fail, integer, label
from ._robust_common import (
    I64_MAX, check_entity, check_features, check_policy, check_slots, first_status, make_config, ordered,
    parameter_map, reduced_pair,
)
from ._stats import to_float

BREADTH_IDENTITY = "ef3.session_breadth"
BREADTH_ALGORITHM = "ef3-session-breadth-v1"
# The label names the whole convention set (declared denominator N, three valued members, strict above-VWAP,
# range based inclusive proximity, exact sign classes, whole-volume direction flips, zero denominators).
BREADTH_POLICY = "ef3-breadth1"
PROFILES = ("static_snapshot", "ordered_history")
STATIC_KIND = "ef3.population.member"
INTERVAL_KIND = "ef3.breadth.membership_interval"
PRA_AVAILABLE, PRA_UNAVAILABLE = "ef3.member.prior_reference.available", "ef3.member.prior_reference.unavailable"
VWAP_KIND, VWAP_UNAVAILABLE = "ef3.member.vwap", "ef3.member.vwap.unavailable"

ABOVE_VWAP = "breadth.session.above_vwap_fraction"
ADVANCE_DECLINE = "breadth.session.advance_decline_ratio"
ADVANCING = "breadth.session.advancing_count"
DECLINING = "breadth.session.declining_count"
DIRECTION_NET = "breadth.session.direction_net_count"
DOWN_VOLUME = "breadth.session.down_volume"
LATEST_EVENT = "breadth.session.latest_observed_member_event_ns"
NEAR_HIGH = "breadth.session.near_high_fraction"
NEAR_LOW = "breadth.session.near_low_fraction"
POSITIVE_MOMENTUM = "breadth.session.positive_momentum_fraction"
PRIOR_COVERAGE = "breadth.session.prior_reference_coverage_fraction"
PRIOR_ELIGIBLE = "breadth.session.prior_reference_eligible_count"
SELECTED_COUNT = "breadth.session.selected_member_count"
UNCHANGED = "breadth.session.unchanged_count"
UP_DOWN_RATIO = "breadth.session.up_down_volume_ratio"
UP_VOLUME = "breadth.session.up_volume"
BREADTH_FEATURES = (ABOVE_VWAP, ADVANCE_DECLINE, ADVANCING, DECLINING, DIRECTION_NET, DOWN_VOLUME, LATEST_EVENT,
                    NEAR_HIGH, NEAR_LOW, POSITIVE_MOMENTUM, PRIOR_COVERAGE, PRIOR_ELIGIBLE, SELECTED_COUNT, UNCHANGED,
                    UP_DOWN_RATIO, UP_VOLUME)
ROLES = ("population", "prior_reference_availability", "current_return", "cumulative_volume", "endpoint_price",
         "vwap", "momentum", "selected_high", "selected_low")
_PRA, _RET, _VOL, _EP, _VWAP, _MOM, _HI, _LO = ROLES[1:]
FEATURE_ROLES: dict[str, tuple[str, ...]] = {
    ABOVE_VWAP: ("population", _EP, _VWAP),
    ADVANCE_DECLINE: ("population", _PRA, _RET),
    ADVANCING: ("population", _PRA, _RET),
    DECLINING: ("population", _PRA, _RET),
    DIRECTION_NET: ("population", _PRA, _RET),
    DOWN_VOLUME: ("population", _PRA, _RET, _VOL),
    LATEST_EVENT: ("population", _EP),
    NEAR_HIGH: ("population", _EP, _HI, _LO),
    NEAR_LOW: ("population", _EP, _HI, _LO),
    POSITIVE_MOMENTUM: ("population", _MOM),
    PRIOR_COVERAGE: ("population", _PRA),
    PRIOR_ELIGIBLE: ("population", _PRA),
    SELECTED_COUNT: ("population",),
    UNCHANGED: ("population", _PRA, _RET),
    UP_DOWN_RATIO: ("population", _PRA, _RET, _VOL),
    UP_VOLUME: ("population", _PRA, _RET, _VOL),
}
FEATURE_META: dict[str, tuple[ValueType, str]] = {
    ABOVE_VWAP: (ValueType.FLOAT64, "fraction"), ADVANCE_DECLINE: (ValueType.FLOAT64, "ratio"),
    ADVANCING: (ValueType.INT64, "members"), DECLINING: (ValueType.INT64, "members"),
    DIRECTION_NET: (ValueType.INT64, "members"), DOWN_VOLUME: (ValueType.INT64, "shares"),
    LATEST_EVENT: (ValueType.INT64, "utc_ns"), NEAR_HIGH: (ValueType.FLOAT64, "fraction"),
    NEAR_LOW: (ValueType.FLOAT64, "fraction"), POSITIVE_MOMENTUM: (ValueType.FLOAT64, "fraction"),
    PRIOR_COVERAGE: (ValueType.FLOAT64, "fraction"), PRIOR_ELIGIBLE: (ValueType.INT64, "members"),
    SELECTED_COUNT: (ValueType.INT64, "members"), UNCHANGED: (ValueType.INT64, "members"),
    UP_DOWN_RATIO: (ValueType.FLOAT64, "ratio"), UP_VOLUME: (ValueType.INT64, "shares"),
}
_KINDS: dict[str, dict[str, str]] = {
    _PRA: {PRA_AVAILABLE: NONE_MODE, PRA_UNAVAILABLE: NONE_MODE},
    _RET: {"ef3.member.current_return": ANY_MODE},
    _VOL: {"ef3.member.cumulative_volume": NONNEG_MODE},
    _EP: {"ef3.member.endpoint_price": POSITIVE_MODE},
    _VWAP: {VWAP_KIND: VWAP_MODE, VWAP_UNAVAILABLE: NONE_MODE},
    _MOM: {"ef3.member.momentum": ANY_MODE},
    _HI: {"ef3.member.selected_high": POSITIVE_MODE},
    _LO: {"ef3.member.selected_low": POSITIVE_MODE},
}
_REQUIRED = frozenset({"policy_version", "membership_profile", "population_id", "population_revision",
                       "evidence_limit"})
_OPTIONAL = frozenset({"near_high_tol_num", "near_high_tol_den", "near_low_tol_num", "near_low_tol_den"})


@dataclass(frozen=True)
class SessionBreadthSettings:
    policy_version: str
    membership_profile: str
    population_id: str
    population_revision: str
    near_high: tuple[int, int] | None
    near_low: tuple[int, int] | None
    evidence_limit: int


def _pair(num: object, den: object) -> tuple[int, int] | None:
    if num is None and den is None:
        return None
    if num is None or den is None:
        fail(ErrorCode.INVALID_CONFIG, "a tolerance numerator and denominator come together")
    return reduced_pair(num, den, maximum_one=True, positive=False)


def _check(policy: object, profile: object, population_id: object, revision: object, high: tuple[object, object],
           low: tuple[object, object], limit: object) -> SessionBreadthSettings:
    check_policy(policy, BREADTH_POLICY)
    if type(profile) is not str or profile not in PROFILES:
        fail(ErrorCode.INVALID_CONFIG, "membership_profile must be static_snapshot or ordered_history")
    assert type(policy) is str
    return SessionBreadthSettings(policy, profile, label(population_id), label(revision), _pair(*high), _pair(*low),
                                  integer(limit, 0, 10000))


def build_session_breadth_config(*, policy_version: str | None = None, membership_profile: str | None = None,
                                 population_id: str | None = None, population_revision: str | None = None,
                                 near_high_tol_num: int | None = None, near_high_tol_den: int | None = None,
                                 near_low_tol_num: int | None = None, near_low_tol_den: int | None = None,
                                 session: SessionSpec, availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                                 price_unit: PriceUnit, evidence_limit: int = 0) -> ConfigSpec:
    """Final ConfigSpec; the tolerance pairs are present exactly when their fraction output is selected."""
    s = _check(policy_version, membership_profile, population_id, population_revision,
               (near_high_tol_num, near_high_tol_den), (near_low_tol_num, near_low_tol_den), evidence_limit)
    params = [Parameter("policy_version", s.policy_version), Parameter("membership_profile", s.membership_profile),
              Parameter("population_id", s.population_id), Parameter("population_revision", s.population_revision),
              Parameter("evidence_limit", s.evidence_limit)]
    if s.near_high is not None:
        params += [Parameter("near_high_tol_num", s.near_high[0]), Parameter("near_high_tol_den", s.near_high[1])]
    if s.near_low is not None:
        params += [Parameter("near_low_tol_num", s.near_low[0]), Parameter("near_low_tol_den", s.near_low[1])]
    return make_config(BREADTH_IDENTITY, BREADTH_ALGORITHM, tuple(params), 1, session, availability, adjustment,
                       price_unit)


def decode_session_breadth_config(config: ConfigSpec) -> SessionBreadthSettings:
    """Validate the closed session-breadth envelope and return its settings."""
    v = parameter_map(config, BREADTH_IDENTITY, BREADTH_ALGORITHM, _REQUIRED, _OPTIONAL)
    s = _check(v["policy_version"], v["membership_profile"], v["population_id"], v["population_revision"],
               (v.get("near_high_tol_num"), v.get("near_high_tol_den")),
               (v.get("near_low_tol_num"), v.get("near_low_tol_den")), v["evidence_limit"])
    assert config.price_unit is not None
    expected = build_session_breadth_config(
        policy_version=s.policy_version, membership_profile=s.membership_profile, population_id=s.population_id,
        population_revision=s.population_revision,
        near_high_tol_num=None if s.near_high is None else s.near_high[0],
        near_high_tol_den=None if s.near_high is None else s.near_high[1],
        near_low_tol_num=None if s.near_low is None else s.near_low[0],
        near_low_tol_den=None if s.near_low is None else s.near_low[1], session=config.session,
        availability=config.availability, adjustment=config.adjustment, price_unit=config.price_unit,
        evidence_limit=s.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical session-breadth envelope")
    return s


@dataclass(frozen=True)
class Population:
    """The declared population: every member named by a row, the members in P at C (row order) and the findings."""

    input_id: str
    complete: bool
    declared: frozenset[str]
    members: tuple[str, ...]
    reasons: frozenset[Reason]


def _admit_population(batch: CanonicalBatch, config: ConfigSpec, settings: SessionBreadthSettings,
                      cutoff: int, knowledge: int) -> Population:
    static = settings.membership_profile == "static_snapshot"
    kind = STATIC_KIND if static else INTERVAL_KIND
    rows = (fact_rows(batch, config, {kind: NONE_MODE}, "x1", ("t",)) if static
            else fact_rows(batch, config, {kind: NONE_MODE}, "bh1", ("t", "t", "d6")))
    snapshot = batch.metadata.source.snapshot_id
    session = config.session
    stints: dict[str, list[FactRow]] = {}
    for member, row, parts in rows:
        if parts[0] != settings.population_id or (not static and parts[1] != settings.population_revision):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "population reference differs from the configured population")
        if row.text != snapshot:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "population revision differs from the snapshot")
        if static and (row.start, row.end) != (session.open_ns, session.close_ns):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "population effective bounds differ from the target session")
        for other in stints.get(member, []):
            if (row.end is None or other.start < row.end) and (other.end is None or row.start < other.end):
                fail(ErrorCode.DUPLICATE, "two stints of one member overlap")
        stints.setdefault(member, []).append(row)
    reasons: set[Reason] = set()
    if not batch.metadata.coverage.complete:
        reasons.add(Reason.GOVERNED_GAP)
    members: list[str] = []
    for member, row, _ in rows:
        if static or (row.start <= cutoff and (row.end is None or cutoff < row.end)):
            members.append(member)
            if row.known_at is None:
                reasons.add(Reason.UNKNOWN_AVAILABILITY)
            elif row.known_at > knowledge:
                reasons.add(Reason.FUTURE_KNOWLEDGE)
    return Population(batch.metadata.source.input_id, batch.metadata.coverage.complete, frozenset(stints),
                      tuple(members), frozenset(reasons))


@dataclass
class _Out:
    value: int | float | None
    reasons: frozenset[Reason]
    expected: int | None
    observed: int
    witnesses: list[EvidenceRow]


def compute_session_breadth(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                            config: ConfigSpec, *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef3-breadth1 outputs; `batches` is the fixed nine nullable role slots."""
    settings = decode_session_breadth_config(config)
    entity = check_entity(entity, config)
    selected = check_features(features, BREADTH_FEATURES)
    if ((NEAR_HIGH in selected) != (settings.near_high is not None)
            or (NEAR_LOW in selected) != (settings.near_low is not None)):
        fail(ErrorCode.INVALID_CONFIG, "a tolerance is supplied exactly when its fraction output is selected")
    slots = check_slots(batches, len(ROLES), (DataKind.REFERENCE,) * len(ROLES))
    needed = {role for feature in selected for role in FEATURE_ROLES[feature]}
    cutoff, knowledge = config.availability.market_cutoff_ns, config.availability.knowledge_cutoff_ns
    population: Population | None = None
    roles: dict[str, Role] = {}
    snapshots: set[str] = set()
    if slots[0] is not None:
        population = _admit_population(slots[0], config, settings, cutoff, knowledge)
        snapshots.add(slots[0].metadata.source.snapshot_id)
    for name, batch in zip(ROLES[1:], slots[1:]):
        if batch is None or name not in needed:
            continue
        rows = fact_rows(batch, config, _KINDS[name], "bf1", ("t",))
        if any(parts[0] != settings.population_id for _, _, parts in rows):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "fact population id differs from the configuration")
        roles[name] = Role(name, batch, batch.metadata.coverage.complete, {m: row for m, row, _ in rows})
        snapshots.add(batch.metadata.source.snapshot_id)
    if len(snapshots) > 1:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "fact roles carry different snapshot ids")
    if population is not None and population.complete:
        for role in roles.values():
            if any(member not in population.declared for member in role.rows):
                fail(ErrorCode.INCONSISTENT_IDENTITY, "fact row for a member that is not declared")
    pra, ret = roles.get(_PRA), roles.get(_RET)
    if pra is not None and ret is not None:
        for member, row in pra.rows.items():
            other = ret.rows.get(member)
            if row.kind == PRA_UNAVAILABLE and other is not None and other.price is not None:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "a current return for a member declared prior-unavailable")

    members: tuple[str, ...] = () if population is None else population.members
    total = len(members)
    memo: dict[tuple[str, str], tuple[FactRow | None, frozenset[Reason]]] = {}

    def cell(role: str, member: str) -> tuple[FactRow | None, frozenset[Reason]]:
        key = (role, member)
        if key not in memo:
            memo[key] = resolve(roles.get(role), member, cutoff, knowledge)
        return memo[key]

    def prior(member: str) -> Tri:
        row, why = cell(_PRA, member)
        if why or row is None:
            return None, why
        return row.kind == PRA_AVAILABLE, NO_REASONS

    def direction(member: str, sign: int) -> Tri:
        available = prior(member)
        if available[0] is False:
            return False, NO_REASONS
        row, why = cell(_RET, member)
        if why or row is None or row.price is None:
            return tri_and(available, (None, why))
        if (row.price > 0) - (row.price < 0) != sign:
            return False, NO_REASONS
        return tri_and(available, (True, NO_REASONS))

    def above(member: str) -> Tri:
        vrow, vwhy = cell(_VWAP, member)
        if not vwhy and vrow is not None and vrow.kind == VWAP_UNAVAILABLE:
            return False, NO_REASONS
        erow, ewhy = cell(_EP, member)
        if vwhy or ewhy or vrow is None or erow is None or vrow.price is None or erow.price is None:
            return None, vwhy | ewhy
        assert vrow.num is not None and vrow.den is not None
        return erow.price * vrow.den > vrow.price * vrow.num, NO_REASONS

    def positive(member: str) -> Tri:
        row, why = cell(_MOM, member)
        if why or row is None or row.price is None:
            return None, why
        return row.price > 0, NO_REASONS

    def near(member: str, high: bool) -> Tri:
        hrow, hwhy = cell(_HI, member)
        lrow, lwhy = cell(_LO, member)
        erow, ewhy = cell(_EP, member)
        if hwhy or lwhy or hrow is None or lrow is None or hrow.price is None or lrow.price is None:
            return None, hwhy | lwhy | ewhy
        top, bottom = hrow.price, lrow.price
        if top == bottom:
            return False, NO_REASONS
        if top < bottom:
            return None, frozenset({Reason.INELIGIBLE})
        if ewhy or erow is None or erow.price is None:
            return None, ewhy
        end = erow.price
        if not bottom <= end <= top:
            return None, frozenset({Reason.INELIGIBLE})
        tolerance = settings.near_high if high else settings.near_low
        assert tolerance is not None
        gap = top - end if high else end - bottom
        return gap * tolerance[1] <= tolerance[0] * (top - bottom), NO_REASONS

    def run(predicate: Callable[[str], Tri]) -> list[Tri]:
        return [predicate(m) for m in members]

    def joint(*lists: list[Tri]) -> tuple[int, frozenset[Reason]]:
        unknown = 0
        reasons: frozenset[Reason] = NO_REASONS
        for index in range(total):
            bad = [lst[index][1] for lst in lists if lst[index][0] is None]
            if bad:
                unknown += 1
                reasons = reasons.union(*bad)
        return unknown, reasons

    def witnesses(feature: str, flags: list[Tri], role: str) -> list[EvidenceRow]:
        chosen = [m for m, (flag, _) in zip(members, flags) if flag is True][:settings.evidence_limit]
        return [member_evidence(entity, feature, roles[role], m) for m in chosen]

    def count(feature: str, flags: list[Tri], role: str) -> _Out:
        unknown, reasons = joint(flags)
        if unknown:
            return _Out(None, reasons, total, total - unknown, [])
        return _Out(sum(1 for flag, _ in flags if flag), NO_REASONS, total, total, witnesses(feature, flags, role))

    def fraction(flags: list[Tri]) -> _Out:
        unknown, reasons = joint(flags)
        if unknown:
            return _Out(None, reasons, total, total - unknown, [])
        return _Out(to_float(Fraction(sum(1 for flag, _ in flags if flag), total)), NO_REASONS, total, total, [])

    def contributions(sign: int) -> tuple[list[Tri], list[int | None], list[frozenset[Reason]]]:
        flags = run(lambda m: direction(m, sign))
        amounts: list[int | None] = []
        whys: list[frozenset[Reason]] = []
        for member, (flag, why) in zip(members, flags):
            row, vwhy = cell(_VOL, member)
            if flag is False:
                amounts.append(0)
                whys.append(NO_REASONS)
            elif flag is True and not vwhy and row is not None:
                amounts.append(row.price)
                whys.append(NO_REASONS)
            else:
                amounts.append(None)
                whys.append(why | vwhy)
        return flags, amounts, whys

    def volume(feature: str, sign: int) -> _Out:
        flags, amounts, whys = contributions(sign)
        bad = [w for amount, w in zip(amounts, whys) if amount is None]
        if bad:
            return _Out(None, NO_REASONS.union(*bad), total, total - len(bad), [])
        value = sum(a for a in amounts if a is not None)
        if value > I64_MAX:
            fail(ErrorCode.OVERFLOW, "published share volume exceeds int64")
        return _Out(value, NO_REASONS, total, total, witnesses(feature, flags, _VOL))

    def volume_ratio() -> _Out:
        _, up_amounts, up_whys = contributions(1)
        _, down_amounts, down_whys = contributions(-1)
        reasons: frozenset[Reason] = NO_REASONS
        unknown = 0
        for u, d, uw, dw in zip(up_amounts, down_amounts, up_whys, down_whys):
            if u is None or d is None:
                unknown += 1
                reasons |= (uw if u is None else NO_REASONS) | (dw if d is None else NO_REASONS)
        if unknown:
            return _Out(None, reasons, total, total - unknown, [])
        up = sum(a for a in up_amounts if a is not None)
        down = sum(a for a in down_amounts if a is not None)
        if down == 0:
            return _Out(None, frozenset({Reason.ZERO_DENOMINATOR}), total, total, [])
        return _Out(to_float(Fraction(up, down)), NO_REASONS, total, total, [])

    def ratio_of_counts() -> _Out:
        adv, dec = run(lambda m: direction(m, 1)), run(lambda m: direction(m, -1))
        unknown, reasons = joint(adv, dec)
        if unknown:
            return _Out(None, reasons, total, total - unknown, [])
        a, d = sum(1 for f, _ in adv if f), sum(1 for f, _ in dec if f)
        if d == 0:
            return _Out(None, frozenset({Reason.ZERO_DENOMINATOR}), total, total, [])
        return _Out(to_float(Fraction(a, d)), NO_REASONS, total, total, [])

    def net() -> _Out:
        adv, dec = run(lambda m: direction(m, 1)), run(lambda m: direction(m, -1))
        unknown, reasons = joint(adv, dec)
        if unknown:
            return _Out(None, reasons, total, total - unknown, [])
        return _Out(sum(1 for f, _ in adv if f) - sum(1 for f, _ in dec if f), NO_REASONS, total, total, [])

    def latest() -> _Out:
        times: list[int | None] = []
        reasons: frozenset[Reason] = NO_REASONS
        for member in members:
            row, why = cell(_EP, member)
            if why or row is None:
                times.append(None)
                reasons |= why
            else:
                times.append(row.start)
        known = [t for t in times if t is not None]
        peak = max(known) if known else None
        if peak is None or (len(known) != total and peak != cutoff - 1):
            return _Out(None, reasons, total, len(known), [])
        holder = next(m for m, t in zip(members, times) if t == peak)
        evidence = [member_evidence(entity, LATEST_EVENT, roles[_EP], holder)][:settings.evidence_limit]
        size = total if len(known) == total else 1
        return _Out(peak, NO_REASONS, size, size, evidence)

    def evaluate(feature: str) -> _Out:
        if population is None:
            return _Out(None, frozenset({Reason.ABSENT_INPUT}), None, 0, [])
        found = set(population.reasons)
        if found:
            return _Out(None, frozenset(found), None, 0, [])
        if total == 0:
            return _Out(None, frozenset({Reason.EMPTY_UNIVERSE}), 0, 0, [])
        if feature == SELECTED_COUNT:
            return _Out(total, NO_REASONS, total, total, [])
        if feature == PRIOR_ELIGIBLE:
            return count(feature, run(prior), _PRA)
        if feature == PRIOR_COVERAGE:
            return fraction(run(prior))
        if feature == ADVANCING:
            return count(feature, run(lambda m: direction(m, 1)), _RET)
        if feature == DECLINING:
            return count(feature, run(lambda m: direction(m, -1)), _RET)
        if feature == UNCHANGED:
            return count(feature, run(lambda m: direction(m, 0)), _RET)
        if feature == DIRECTION_NET:
            return net()
        if feature == ADVANCE_DECLINE:
            return ratio_of_counts()
        if feature == UP_VOLUME:
            return volume(feature, 1)
        if feature == DOWN_VOLUME:
            return volume(feature, -1)
        if feature == UP_DOWN_RATIO:
            return volume_ratio()
        if feature == ABOVE_VWAP:
            flags = run(above)
            out = fraction(flags)
            if out.value is not None:
                out.witnesses = witnesses(feature, flags, _EP)
            return out
        if feature == POSITIVE_MOMENTUM:
            flags = run(positive)
            out = fraction(flags)
            if out.value is not None:
                out.witnesses = witnesses(feature, flags, _MOM)
            return out
        if feature in (NEAR_HIGH, NEAR_LOW):
            flags = run(lambda m: near(m, feature == NEAR_HIGH))
            out = fraction(flags)
            if out.value is not None:
                out.witnesses = witnesses(feature, flags, _EP)
            return out
        return latest()

    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        out = evaluate(feature)
        reasons = set(out.reasons)
        if out.value is None and not reasons:
            reasons = {Reason.ABSENT_INPUT}
        status = Status.AVAILABLE if out.value is not None else first_status(reasons)
        dtype, unit = FEATURE_META[feature]
        columns.append(FeatureColumn(feature, BREADTH_ALGORITHM, dtype, unit, (entity,), (out.value,)))
        quality.append(QualityRow(entity, feature, status, out.expected, out.observed,
                                  () if out.value is not None else ordered(reasons)))
        for witness in out.witnesses:
            if len(evidence) < settings.evidence_limit:
                evidence.append(witness)
    used: dict[str, CanonicalBatch] = {name: role.batch for name, role in roles.items()}
    if slots[0] is not None:
        used["population"] = slots[0]
    bindings = tuple(sorted((InputBinding(role, batch.kind, batch.metadata) for role, batch in used.items()),
                            key=lambda binding: binding.role))
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
                              bindings, "python-exact", __version__, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
