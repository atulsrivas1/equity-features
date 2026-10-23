"""Pure EF3 observed-population session breadth companion (ef3-obsbreadth1).

The roster defines the observed population (records with an event time before the market cutoff C, then the optional
group filter); there is no expected universe, so quality `expected` is a record count. A member qualifies when its
price coefficient reaches the caller price floor and its volume the caller volume floor (both inclusive) and advances
when it qualifies with a strictly positive change. Predicates are three valued with dominance (a known failure decides
without the other input). Fractions are one correctly rounded division of exact integers. No default, no state.
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
    ANY_MODE, NONE_MODE, NONNEG_MODE, NO_REASONS, POSITIVE_MODE, FactRow, Role, Tri, fact_rows, member_evidence,
    resolve, tri_and,
)
from ._common import fail, integer, label
from ._robust_common import (
    I64_MAX, check_entity, check_features, check_policy, check_slots, first_status, make_config, ordered,
    parameter_map, reduced_pair,
)
from ._stats import to_float

OBSERVED_IDENTITY = "ef3.observed_breadth"
OBSERVED_ALGORITHM = "ef3-observed-breadth-v1"
# The label names the whole convention set (roster population, inclusive floors, strict positive change, three
# valued members with dominance, observed zero is an observation, zero denominators).
OBSERVED_POLICY = "ef3-obsbreadth1"
SCOPES = ("cohort", "group")
ADVANCE_FRACTION = "breadth.observed.advance_fraction"
ADVANCING_COUNT = "breadth.observed.advancing_member_count"
NONADVANCING_COUNT = "breadth.observed.nonadvancing_member_count"
OBSERVED_COUNT = "breadth.observed.observed_member_count"
QUALIFYING_FRACTION = "breadth.observed.qualifying_fraction"
QUALIFYING_COUNT = "breadth.observed.qualifying_member_count"
UNKNOWN_COUNT = "breadth.observed.unknown_member_count"
OBSERVED_FEATURES = (ADVANCE_FRACTION, ADVANCING_COUNT, NONADVANCING_COUNT, OBSERVED_COUNT, QUALIFYING_FRACTION,
                     QUALIFYING_COUNT, UNKNOWN_COUNT)
ROLES = ("members", "change", "qualifier_price", "qualifier_volume")
_MEMBERS, _CHANGE, _PRICE, _VOLUME = ROLES
FEATURE_ROLES: dict[str, tuple[str, ...]] = {
    ADVANCE_FRACTION: ROLES, ADVANCING_COUNT: ROLES, NONADVANCING_COUNT: ROLES, OBSERVED_COUNT: (_MEMBERS,),
    QUALIFYING_FRACTION: (_MEMBERS, _PRICE, _VOLUME), QUALIFYING_COUNT: (_MEMBERS, _PRICE, _VOLUME),
    UNKNOWN_COUNT: ROLES,
}
FEATURE_META: dict[str, tuple[ValueType, str]] = {
    ADVANCE_FRACTION: (ValueType.FLOAT64, "fraction"), ADVANCING_COUNT: (ValueType.INT64, "members"),
    NONADVANCING_COUNT: (ValueType.INT64, "members"), OBSERVED_COUNT: (ValueType.INT64, "members"),
    QUALIFYING_FRACTION: (ValueType.FLOAT64, "fraction"), QUALIFYING_COUNT: (ValueType.INT64, "members"),
    UNKNOWN_COUNT: (ValueType.INT64, "members"),
}
MEMBER_KIND = "ef3.observed.member"
_KINDS: dict[str, dict[str, str]] = {
    _MEMBERS: {MEMBER_KIND: NONE_MODE},
    _CHANGE: {"ef3.observed.change": ANY_MODE},
    _PRICE: {"ef3.observed.qualifier_price": POSITIVE_MODE},
    _VOLUME: {"ef3.observed.qualifier_volume": NONNEG_MODE},
}
_REQUIRED = frozenset({"policy_version", "scope", "record_set_id", "floor_price_num", "floor_price_den",
                       "floor_volume", "evidence_limit"})
_OPTIONAL = frozenset({"group_label"})


@dataclass(frozen=True)
class ObservedBreadthSettings:
    policy_version: str
    scope: str
    group_label: str | None
    record_set_id: str
    floor_price: tuple[int, int]
    floor_volume: int
    evidence_limit: int


def _check(policy: object, scope: object, group_label: object, record_set_id: object, price_num: object,
           price_den: object, volume: object, limit: object) -> ObservedBreadthSettings:
    check_policy(policy, OBSERVED_POLICY)
    if type(scope) is not str or scope not in SCOPES:
        fail(ErrorCode.INVALID_CONFIG, "scope must be cohort or group")
    if (scope == "group") != (group_label is not None):
        fail(ErrorCode.INVALID_CONFIG, "a group label is supplied exactly when the scope is group")
    assert type(policy) is str
    return ObservedBreadthSettings(
        policy, scope, None if group_label is None else label(group_label), label(record_set_id),
        reduced_pair(price_num, price_den, maximum_one=False, positive=False), integer(volume, 0, I64_MAX),
        integer(limit, 0, 10000))


def build_observed_breadth_config(*, policy_version: str | None = None, scope: str | None = None,
                                  group_label: str | None = None, record_set_id: str | None = None,
                                  floor_price_num: int | None = None, floor_price_den: int | None = None,
                                  floor_volume: int | None = None, session: SessionSpec,
                                  availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit,
                                  evidence_limit: int = 0) -> ConfigSpec:
    """Final ConfigSpec; every parameter is explicit with no default (the floor price is a reduced rational >= 0)."""
    s = _check(policy_version, scope, group_label, record_set_id, floor_price_num, floor_price_den, floor_volume,
               evidence_limit)
    params = [Parameter("policy_version", s.policy_version), Parameter("scope", s.scope),
              Parameter("record_set_id", s.record_set_id), Parameter("floor_price_num", s.floor_price[0]),
              Parameter("floor_price_den", s.floor_price[1]), Parameter("floor_volume", s.floor_volume),
              Parameter("evidence_limit", s.evidence_limit)]
    if s.group_label is not None:
        params.append(Parameter("group_label", s.group_label))
    return make_config(OBSERVED_IDENTITY, OBSERVED_ALGORITHM, tuple(params), 1, session, availability, adjustment,
                       price_unit)


def decode_observed_breadth_config(config: ConfigSpec) -> ObservedBreadthSettings:
    """Validate the closed observed-breadth envelope and return its settings."""
    v = parameter_map(config, OBSERVED_IDENTITY, OBSERVED_ALGORITHM, _REQUIRED, _OPTIONAL)
    s = _check(v["policy_version"], v["scope"], v.get("group_label"), v["record_set_id"], v["floor_price_num"],
               v["floor_price_den"], v["floor_volume"], v["evidence_limit"])
    assert config.price_unit is not None
    expected = build_observed_breadth_config(
        policy_version=s.policy_version, scope=s.scope, group_label=s.group_label, record_set_id=s.record_set_id,
        floor_price_num=s.floor_price[0], floor_price_den=s.floor_price[1], floor_volume=s.floor_volume,
        session=config.session, availability=config.availability, adjustment=config.adjustment,
        price_unit=config.price_unit, evidence_limit=s.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical observed-breadth envelope")
    return s


@dataclass
class _Out:
    value: int | float | None
    reasons: frozenset[Reason]
    expected: int | None
    observed: int
    witnesses: list[EvidenceRow]


def compute_observed_breadth(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                             config: ConfigSpec, *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef3-obsbreadth1 outputs; `batches` is the fixed four nullable role slots."""
    settings = decode_observed_breadth_config(config)
    entity = check_entity(entity, config)
    selected = check_features(features, OBSERVED_FEATURES)
    slots = check_slots(batches, len(ROLES), (DataKind.REFERENCE,) * len(ROLES))
    needed = {role for feature in selected for role in FEATURE_ROLES[feature]}
    cutoff, knowledge = config.availability.market_cutoff_ns, config.availability.knowledge_cutoff_ns
    scale = config.price_unit.scale if config.price_unit is not None else 0
    roles: dict[str, Role] = {}
    for name, batch in zip(ROLES, slots):
        if batch is None or name not in needed:
            continue
        rows = fact_rows(batch, config, _KINDS[name], "ob1", ("t",))
        if any(parts[0] != settings.record_set_id for _, _, parts in rows):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "record set id differs from the configuration")
        roles[name] = Role(name, batch, batch.metadata.coverage.complete, {m: row for m, row, _ in rows})
    roster = roles.get(_MEMBERS)
    if roster is not None and roster.complete:
        for name, role in roles.items():
            if name != _MEMBERS and any(member not in roster.rows for member in role.rows):
                fail(ErrorCode.INCONSISTENT_IDENTITY, "fact row for a member that is not in the roster")

    findings: set[Reason] = set()
    members: list[str] = []
    if roster is None:
        findings.add(Reason.ABSENT_INPUT)
    else:
        if not roster.complete:
            findings.add(Reason.GOVERNED_GAP)
        for member, row in roster.rows.items():
            if row.start >= cutoff:
                continue
            if row.known_at is None:
                findings.add(Reason.UNKNOWN_AVAILABILITY)
            elif row.known_at > knowledge:
                findings.add(Reason.FUTURE_KNOWLEDGE)
            if settings.scope == "cohort" or row.text == settings.group_label:
                members.append(member)
    total = len(members)
    floor_num, floor_den = settings.floor_price
    memo: dict[tuple[str, str], tuple[FactRow | None, frozenset[Reason]]] = {}

    def cell(role: str, member: str) -> tuple[FactRow | None, frozenset[Reason]]:
        key = (role, member)
        if key not in memo:
            memo[key] = resolve(roles.get(role), member, cutoff, knowledge)
        return memo[key]

    def qualifies(member: str) -> Tri:
        prow, pwhy = cell(_PRICE, member)
        vrow, vwhy = cell(_VOLUME, member)
        price: Tri = (None, pwhy) if pwhy or prow is None or prow.price is None else (
            prow.price * floor_den >= floor_num * 10 ** scale, NO_REASONS)
        volume: Tri = (None, vwhy) if vwhy or vrow is None or vrow.price is None else (
            vrow.price >= settings.floor_volume, NO_REASONS)
        return tri_and(price, volume)

    def advancing(member: str) -> Tri:
        row, why = cell(_CHANGE, member)
        change: Tri = (None, why) if why or row is None or row.price is None else (row.price > 0, NO_REASONS)
        return tri_and(qualifies(member), change)

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

    def evaluate(feature: str) -> _Out:
        if findings:
            return _Out(None, frozenset(findings), None, 0, [])
        if feature == OBSERVED_COUNT:
            return _Out(total, NO_REASONS, total, total, [])
        qual, adv = run(qualifies), run(advancing)
        if feature == UNKNOWN_COUNT:
            unknown, _ = joint(qual, adv)
            return _Out(unknown, NO_REASONS, total, total, [])
        if feature == QUALIFYING_COUNT:
            return count(feature, qual, _PRICE)
        if feature == ADVANCING_COUNT:
            return count(feature, adv, _CHANGE)
        if feature == QUALIFYING_FRACTION:
            unknown, reasons = joint(qual)
            if unknown:
                return _Out(None, reasons, total, total - unknown, [])
            if total == 0:
                return _Out(None, frozenset({Reason.ZERO_DENOMINATOR}), 0, 0, [])
            return _Out(to_float(Fraction(sum(1 for f, _ in qual if f), total)), NO_REASONS, total, total, [])
        unknown, reasons = joint(qual, adv)
        if unknown:
            return _Out(None, reasons, total, total - unknown, [])
        q, a = sum(1 for f, _ in qual if f), sum(1 for f, _ in adv if f)
        if feature == NONADVANCING_COUNT:
            return _Out(q - a, NO_REASONS, total, total, [])
        if q == 0:
            return _Out(None, frozenset({Reason.ZERO_DENOMINATOR}), total, total, [])
        return _Out(to_float(Fraction(a, q)), NO_REASONS, total, total, [])

    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for feature in selected:
        out = evaluate(feature)
        status = Status.AVAILABLE if out.value is not None else first_status(out.reasons)
        dtype, unit = FEATURE_META[feature]
        columns.append(FeatureColumn(feature, OBSERVED_ALGORITHM, dtype, unit, (entity,), (out.value,)))
        quality.append(QualityRow(entity, feature, status, out.expected, out.observed,
                                  () if out.value is not None else ordered(out.reasons)))
        for witness in out.witnesses:
            if len(evidence) < settings.evidence_limit:
                evidence.append(witness)
    bindings = tuple(sorted((InputBinding(name, role.batch.kind, role.batch.metadata) for name, role in roles.items()),
                            key=lambda binding: binding.role))
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
                              bindings, "python-exact", __version__, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
