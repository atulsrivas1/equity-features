"""Pure EF4 relative excess (ef4-rel1): current-endpoint and rolling-window excess returns against declared primary,
secondary and sector benchmarks, and the core-benchmark direction agreement and return dispersion.

A leg has an exact start price S and end price E, so the simple return is `E / S - 1`, derived here from exact witnesses
(a pre-rounded float return is never accepted). The excess is the arithmetic spread `r_instrument - r_benchmark`, one
correctly rounded float64 per published value. Explicit alignment tolerance and endpoint age; an endpoint after the
market cutoff is `future_market` and is never replaced by an earlier known row. No clock, I/O, storage, default
tolerance, age, window or benchmark.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
import json

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow, FeatureResult,
    DataKind, InputBinding, Parameter, PriceUnit, Reason, SessionSpec, ValueType,
)
from ..ef3._common import fail, integer, label
from ..ef3._robust_common import make_config, parameter_map
from ._legs import PROFILES, Leg, check_leg_bounds, check_legs, parse_legs
from ._proj_common import (
    MAX_NS, Cell, RefRow, check_features, check_meta, check_policy, finish, fraction_float, knowledge_reason,
    reference_rows, validate_reference,
)

RELATIVE_IDENTITY = "ef4.relative_excess"
RELATIVE_ALGORITHM = "ef4-relative-excess-v1"
# The label names the whole convention set (arithmetic spread of exact simple returns, profile-labelled start facts
# with one shared end fact, explicit alignment and age, per-leg action snapshot, causal sector membership, core
# agreement by the largest direction class and dispersion by the range); another convention is another label.
RELATIVE_POLICY = "ef4-rel1"
MEMBERSHIP_KIND = "ef4.sector.membership"
ROLES = ("legs", "membership")
CORE_AGREEMENT = "core.benchmark_direction_agreement_fraction"
CORE_DISPERSION = "core.benchmark_return_dispersion_fraction"
_EXCESS = {f"relative.session.{role}.{what}_excess_fraction": (role, profile)
           for role in ("primary", "secondary", "sector")
           for what, profile in (("prior_close", "prior_close"), ("window", "window_start"))}
RELATIVE_FEATURES = tuple(sorted(list(_EXCESS) + [CORE_AGREEMENT, CORE_DISPERSION]))
RELATIVE_META: dict[str, tuple[ValueType, str]] = {f: (ValueType.FLOAT64, "fraction") for f in RELATIVE_FEATURES}
_REQUIRED = frozenset({"policy_version", "alignment_tolerance_ns", "max_endpoint_age_ns", "evidence_limit"})
_OPTIONAL = frozenset({"primary_benchmark_id", "secondary_benchmark_id", "sector_benchmark_id", "window_ns",
                       "core_benchmark_ids", "core_profile"})
CORE_PROFILES = ("prior_close", "window_start")


@dataclass(frozen=True)
class RelativeExcessSettings:
    policy_version: str
    alignment_tolerance_ns: int
    max_endpoint_age_ns: int
    evidence_limit: int
    primary_benchmark_id: str | None
    secondary_benchmark_id: str | None
    sector_benchmark_id: str | None
    window_ns: int | None
    core_benchmark_ids: tuple[str, ...] | None
    core_profile: str | None


def encode_core_ids(ids: tuple[str, ...] | list[str]) -> str:
    """Canonical compact JSON text of the ordered core benchmark ids (the scalar parameter value)."""
    return json.dumps(list(ids), separators=(",", ":"), ensure_ascii=True)


def _core_ids(value: object) -> tuple[str, ...]:
    if type(value) is tuple or type(value) is list:
        ids = list(value)
    elif type(value) is str:
        try:
            decoded = json.loads(value)
        except ValueError:
            fail(ErrorCode.INVALID_CONFIG, "canonical JSON core benchmark id list required")
        if type(decoded) is not list or encode_core_ids(decoded) != value:
            fail(ErrorCode.INVALID_CONFIG, "canonical JSON core benchmark id list required")
        ids = decoded
    else:
        fail(ErrorCode.INVALID_CONFIG, "a list of 2..16 distinct core benchmark ids is required")
    if not 2 <= len(ids) <= 16 or len(set(ids)) != len(ids):
        fail(ErrorCode.INVALID_CONFIG, "2..16 distinct core benchmark ids are required")
    return tuple(label(i) for i in ids)


def _check(policy: object, tolerance: object, age: object, limit: object, primary: object, secondary: object,
           sector: object, window: object, core_ids: object, core_profile: object,
           defer_version: bool = False) -> RelativeExcessSettings:
    tol = integer(tolerance, 0, MAX_NS)
    max_age = integer(age, 0, MAX_NS)
    evidence_limit = integer(limit, 0, 10000)
    ids = [None if v is None else label(v) for v in (primary, secondary, sector)]
    width = None if window is None else integer(window, 1, MAX_NS)
    core = None if core_ids is None else _core_ids(core_ids)
    profile: str | None = None
    if core_profile is not None:
        if type(core_profile) is not str or core_profile not in CORE_PROFILES:
            fail(ErrorCode.INVALID_CONFIG, "core_profile must be prior_close or window_start")
        profile = core_profile
    if (core is None) != (profile is None):
        fail(ErrorCode.INVALID_CONFIG, "core_benchmark_ids and core_profile come together")
    if not (defer_version and type(policy) is str):
        check_policy(policy, RELATIVE_POLICY)
    assert type(policy) is str
    return RelativeExcessSettings(policy, tol, max_age, evidence_limit, ids[0], ids[1], ids[2], width, core, profile)


def build_relative_excess_config(*, policy_version: str | None = None, primary_benchmark_id: str | None = None,
                                 secondary_benchmark_id: str | None = None, sector_benchmark_id: str | None = None,
                                 alignment_tolerance_ns: int | None = None, max_endpoint_age_ns: int | None = None,
                                 window_ns: int | None = None,
                                 core_benchmark_ids: tuple[str, ...] | list[str] | None = None,
                                 core_profile: str | None = None, session: SessionSpec,
                                 availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit,
                                 evidence_limit: int | None = None) -> ConfigSpec:
    """Final ConfigSpec; a benchmark id, the window and the core pair are present exactly when their outputs are
    selected, and there is no default tolerance, age, window or benchmark."""
    s = _check(policy_version, alignment_tolerance_ns, max_endpoint_age_ns, evidence_limit, primary_benchmark_id,
               secondary_benchmark_id, sector_benchmark_id, window_ns, core_benchmark_ids, core_profile)
    bound = [b for b in (s.primary_benchmark_id, s.secondary_benchmark_id, s.sector_benchmark_id) if b is not None]
    if len(set(bound)) != len(bound):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "two benchmark roles are bound to one instrument")
    params = [Parameter("policy_version", s.policy_version),
              Parameter("alignment_tolerance_ns", s.alignment_tolerance_ns),
              Parameter("max_endpoint_age_ns", s.max_endpoint_age_ns), Parameter("evidence_limit", s.evidence_limit)]
    for name, value in (("primary_benchmark_id", s.primary_benchmark_id),
                        ("secondary_benchmark_id", s.secondary_benchmark_id),
                        ("sector_benchmark_id", s.sector_benchmark_id), ("window_ns", s.window_ns),
                        ("core_profile", s.core_profile)):
        if value is not None:
            params.append(Parameter(name, value))
    if s.core_benchmark_ids is not None:
        params.append(Parameter("core_benchmark_ids", encode_core_ids(s.core_benchmark_ids)))
    return make_config(RELATIVE_IDENTITY, RELATIVE_ALGORITHM, tuple(params), 1, session, availability, adjustment,
                       price_unit)


def decode_relative_excess_config(config: ConfigSpec, *, defer_version: bool = False) -> RelativeExcessSettings:
    """Validate the closed relative-excess envelope and return its settings."""
    v = parameter_map(config, RELATIVE_IDENTITY, RELATIVE_ALGORITHM, _REQUIRED, _OPTIONAL)
    s = _check(v["policy_version"], v["alignment_tolerance_ns"], v["max_endpoint_age_ns"], v["evidence_limit"],
               v.get("primary_benchmark_id"), v.get("secondary_benchmark_id"), v.get("sector_benchmark_id"),
               v.get("window_ns"), v.get("core_benchmark_ids"), v.get("core_profile"), defer_version)
    if defer_version and s.policy_version != RELATIVE_POLICY:
        return s
    assert config.price_unit is not None
    expected = build_relative_excess_config(
        policy_version=s.policy_version, primary_benchmark_id=s.primary_benchmark_id,
        secondary_benchmark_id=s.secondary_benchmark_id, sector_benchmark_id=s.sector_benchmark_id,
        alignment_tolerance_ns=s.alignment_tolerance_ns, max_endpoint_age_ns=s.max_endpoint_age_ns,
        window_ns=s.window_ns, core_benchmark_ids=s.core_benchmark_ids, core_profile=s.core_profile,
        session=config.session, availability=config.availability, adjustment=config.adjustment,
        price_unit=config.price_unit, evidence_limit=s.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical relative-excess envelope")
    return s


def check_selection(settings: RelativeExcessSettings, selected: tuple[str, ...]) -> None:
    """Optional parameters are present exactly when an output that needs them is selected."""
    core = CORE_AGREEMENT in selected or CORE_DISPERSION in selected
    window = (any(_EXCESS[f][1] == "window_start" for f in selected if f in _EXCESS)
              or (core and settings.core_profile == "window_start"))
    wanted = {
        "primary": any(_EXCESS[f][0] == "primary" for f in selected if f in _EXCESS),
        "secondary": any(_EXCESS[f][0] == "secondary" for f in selected if f in _EXCESS),
        "sector": any(_EXCESS[f][0] == "sector" for f in selected if f in _EXCESS),
    }
    have = {"primary": settings.primary_benchmark_id is not None,
            "secondary": settings.secondary_benchmark_id is not None,
            "sector": settings.sector_benchmark_id is not None}
    if (wanted != have or window != (settings.window_ns is not None)
            or core != (settings.core_benchmark_ids is not None) or core != (settings.core_profile is not None)):
        fail(ErrorCode.INVALID_CONFIG, "optional parameters must be present exactly when their outputs are selected")


@dataclass(frozen=True)
class Member:
    instrument: str
    bound: str
    effective_from: int
    known_at: int | None
    row: int


def _members(rows: list[RefRow]) -> list[Member]:
    members: list[Member] = []
    for row in rows:
        if row.end is not None:
            fail(ErrorCode.INVALID_SCHEMA, "a sector membership is open-ended in v1 (no effective end)")
        if row.price is not None:
            fail(ErrorCode.INVALID_SCHEMA, "a sector membership carries no price")
        members.append(Member(row.instrument, label(row.text, ErrorCode.INVALID_SCHEMA), row.start, row.known_at,
                              row.row))
    return members


def _unknown(known_at: int | None, knowledge: int) -> Reason | None:
    return knowledge_reason(known_at, knowledge)


def _leg_ok(s: Leg, e: Leg, profile: str, settings: RelativeExcessSettings, cutoff: int) -> bool:
    """One leg is individually compatible: same action snapshot, phase, matched window and a fresh endpoint."""
    if s.act != e.act:
        return False
    if profile == "prior_close":
        if s.session == e.session:
            return False
    else:
        assert settings.window_ns is not None
        if s.session != e.session or abs((e.t - s.t) - settings.window_ns) > settings.alignment_tolerance_ns:
            return False
    return not (e.t <= cutoff and cutoff - e.t > settings.max_endpoint_age_ns)


def compute_relative_excess(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                            config: ConfigSpec, *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef4-rel1 outputs; `batches` is the fixed (legs, membership) slots, each nullable."""
    if type(batches) not in (tuple, list) or len(batches) != 2:
        fail(ErrorCode.INVALID_SCHEMA, "the fixed roles (legs, membership) are required")
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    legs_batch, member_batch = batches
    sector_wanted = (type(features) is tuple
                     and any(type(f) is str and f.startswith("relative.session.sector.") for f in features))
    leg_rows: list[RefRow] = []
    member_rows: list[RefRow] = []
    for batch, kind in ((legs_batch, "legs"), (member_batch, "membership")):
        if batch is None or (kind == "membership" and not sector_wanted):
            continue
        rows = reference_rows(batch, frozenset({"ef4.leg.start", "ef4.leg.end"} if kind == "legs"
                                               else {MEMBERSHIP_KIND}))
        if kind == "legs":
            leg_rows = rows
        else:
            member_rows = rows
    legs = parse_legs(leg_rows, PROFILES, frozenset({"A"}))
    members = _members(member_rows)
    for batch, active in ((legs_batch, True), (member_batch, sector_wanted)):
        if batch is not None and active:
            validate_reference(batch)
    settings = decode_relative_excess_config(config, defer_version=True)
    selected = check_features(features, RELATIVE_FEATURES)
    check_selection(settings, selected)
    if legs_batch is not None:
        check_meta(legs_batch, config, unit=True, adjustment=True)
    if member_batch is not None and sector_wanted:
        check_meta(member_batch, config, unit=False, adjustment=False)
    check_policy(settings.policy_version, RELATIVE_POLICY)
    if legs_batch is not None and member_batch is not None and sector_wanted and (
            legs_batch.metadata.source.input_id == member_batch.metadata.source.input_id):
        fail(ErrorCode.DUPLICATE, "distinct actual role input IDs required")
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    target = entity.instrument_id
    bound = [b for b in (settings.primary_benchmark_id, settings.secondary_benchmark_id,
                         settings.sector_benchmark_id) if b is not None]
    core_ids = settings.core_benchmark_ids or ()
    if target in bound or target in core_ids:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "a benchmark must differ from the target instrument")
    check_legs(legs, frozenset([target, *bound, *core_ids]))
    if len(members) > 1:
        fail(ErrorCode.DUPLICATE, "at most one sector membership fact for the target instrument")
    if members and members[0].instrument != target:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "the membership fact belongs to the target instrument")
    check_leg_bounds(legs)
    membership = members[0] if members else None
    legs_input = "" if legs_batch is None else legs_batch.metadata.source.input_id
    member_input = "" if member_batch is None else member_batch.metadata.source.input_id
    starts = {(leg.instrument, leg.profile): leg for leg in legs if leg.is_start}
    ends = {leg.instrument: leg for leg in legs if not leg.is_start}
    cutoff, knowledge = config.availability.market_cutoff_ns, config.availability.knowledge_cutoff_ns
    cells: dict[str, Cell] = {}

    def leg_evidence(feature: str, leg: Leg, which: str) -> EvidenceRow:
        return leg.evidence(entity, feature, legs_input, f"leg:{leg.instrument}:{which}")

    for feature in selected:
        if feature in _EXCESS:
            role, profile = _EXCESS[feature]
            benchmark = {"primary": settings.primary_benchmark_id, "secondary": settings.secondary_benchmark_id,
                         "sector": settings.sector_benchmark_id}[role]
            assert benchmark is not None
            facts: list[Leg | Member | None] = [starts.get((target, profile)), ends.get(target),
                                                starts.get((benchmark, profile)), ends.get(benchmark)]
            if role == "sector":
                facts.append(membership)
            missing: set[Reason] = set()
            known = 0
            for fact in facts:
                if fact is None:
                    missing.add(Reason.ABSENT_INPUT)
                    continue
                cause = _unknown(fact.known_at, knowledge)
                if cause is None:
                    known += 1
                else:
                    missing.add(cause)
            cell = Cell(None, missing, len(facts), known)
            cells[feature] = cell
            if missing:
                continue
            xs, xe, bs, be = (facts[0], facts[1], facts[2], facts[3])
            assert isinstance(xs, Leg) and isinstance(xe, Leg) and isinstance(bs, Leg) and isinstance(be, Leg)
            why = cell.reasons
            assert why is not None
            if xe.t > cutoff or be.t > cutoff:
                why.add(Reason.FUTURE_MARKET)
            if not _leg_ok(xs, xe, profile, settings, cutoff) or not _leg_ok(bs, be, profile, settings, cutoff):
                why.add(Reason.INELIGIBLE)
            tolerance = settings.alignment_tolerance_ns
            if abs(xe.t - be.t) > tolerance:
                why.add(Reason.INELIGIBLE)
            if profile == "prior_close":
                if xs.session != bs.session or xe.session != be.session:
                    why.add(Reason.INELIGIBLE)
            elif xe.session != be.session or abs(xs.t - bs.t) > tolerance:
                why.add(Reason.INELIGIBLE)
            if role == "sector":
                assert isinstance(facts[4], Member)
                if facts[4].bound != benchmark or facts[4].effective_from > xe.t:
                    why.add(Reason.INELIGIBLE)
            if why:
                continue
            cell.value = fraction_float((Fraction(xe.price, xs.price) - 1) - (Fraction(be.price, bs.price) - 1))
            cell.witnesses = [leg_evidence(feature, xs, "start"), leg_evidence(feature, xe, "end"),
                              leg_evidence(feature, bs, "start"), leg_evidence(feature, be, "end")]
            if role == "sector":
                assert isinstance(facts[4], Member)
                cell.witnesses.append(EvidenceRow(entity, feature, member_input, f"membership:{target}",
                                                  facts[4].effective_from, facts[4].known_at,
                                                  facts[4].effective_from, None, "consumed", None, "ordinary"))
            continue
        assert settings.core_benchmark_ids is not None and settings.core_profile is not None
        profile = settings.core_profile
        eligible: list[tuple[str, Leg, Leg]] = []
        for benchmark_id in settings.core_benchmark_ids:
            s_leg, e_leg = starts.get((benchmark_id, profile)), ends.get(benchmark_id)
            if s_leg is None or e_leg is None:
                continue
            if _unknown(s_leg.known_at, knowledge) or _unknown(e_leg.known_at, knowledge):
                continue
            if e_leg.t > cutoff or not _leg_ok(s_leg, e_leg, profile, settings, cutoff):
                continue
            eligible.append((benchmark_id, s_leg, e_leg))
        total = len(settings.core_benchmark_ids)
        cell = Cell(None, set(), total, len(eligible))
        cells[feature] = cell
        assert cell.reasons is not None
        if len(eligible) != total:
            cell.reasons.add(Reason.PARTIAL_UNIVERSE)
            continue
        tolerance = settings.alignment_tolerance_ns
        end_times = [e.t for _, _, e in eligible]
        start_times = [s.t for _, s, _ in eligible]
        misaligned = max(end_times) - min(end_times) > tolerance
        if profile == "prior_close":
            misaligned = (misaligned or len({s.session for _, s, _ in eligible}) > 1
                          or len({e.session for _, _, e in eligible}) > 1)
        else:
            misaligned = (misaligned or max(start_times) - min(start_times) > tolerance
                          or len({e.session for _, _, e in eligible}) > 1)
        if misaligned:
            cell.reasons.add(Reason.INELIGIBLE)
            continue
        returns = [Fraction(e.price, s.price) - 1 for _, s, e in eligible]
        if feature == CORE_AGREEMENT:
            classes = [sum(1 for r in returns if r > 0), sum(1 for r in returns if r < 0),
                       sum(1 for r in returns if r == 0)]
            cell.value = fraction_float(Fraction(max(classes), len(returns)))
        else:
            cell.value = fraction_float(max(returns) - min(returns))
        cell.witnesses = []
        for benchmark_id, s_leg, e_leg in eligible:
            cell.witnesses += [leg_evidence(feature, s_leg, "start"), leg_evidence(feature, e_leg, "end")]
    bindings: list[InputBinding] = []
    if legs_batch is not None:
        bindings.append(InputBinding("legs", DataKind.REFERENCE, legs_batch.metadata))
    if member_batch is not None and sector_wanted:
        bindings.append(InputBinding("membership", DataKind.REFERENCE, member_batch.metadata))
    return finish(config, entity, RELATIVE_ALGORITHM, selected, RELATIVE_META, cells, tuple(bindings),
                  settings.evidence_limit)
