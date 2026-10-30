"""Pure DV1 core spread (dv1-core1): `core.benchmark_return_range_fraction` and `core.benchmark_return_stdev_fraction`.

Each declared core fund k has an exact start price S_k and end price E_k (leg witnesses), so its simple return is
`r_k = E_k / S_k - 1`, derived from exact integers. The range output is `max r - min r` (the value the deprecated EF4
`core.benchmark_return_dispersion_fraction` publishes, which is a range and not a dispersion). The standard deviation
output is the POPULATION standard deviation with divisor K over the K declared funds: `sqrt((K sum r^2 - (sum r)^2) / K^2)`
as an exact rational variance whose root is exact when numerator and denominator are perfect squares, else a Decimal120
square root; each published value is one correctly rounded float64. Eligibility is the EF4 relative-excess rule
(per fund start and end facts present and known, end not after the market cutoff, endpoint age bound, one action snapshot);
a fund that fails leaves the population partial and BOTH values are withheld, never zero. The profile `regular_open` has
its start leg at the open of the regular-session DAILY BAR of the exact session (operand label `daily_bar_open`) and its
end leg at the close of the same session; a start leg of any other operand, session or profile does not count.
No clock, I/O, storage or default tolerance, age, window or fund list. The fact admission and the result assembly are the
EF4 helpers (`equity_features.ef4._legs`, `_proj_common`), imported not copied; the EF4 files are not edited.
Internal, synthetic, pre-release.
"""
from __future__ import annotations

from dataclasses import dataclass
from decimal import Context, Decimal, DecimalException, localcontext, MAX_EMAX, MIN_EMIN, ROUND_HALF_EVEN
from fractions import Fraction
from math import isfinite, isqrt

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode,
    FeatureResult, InputBinding, Parameter, PriceUnit, Reason, SessionSpec, ValueType,
)
from ..ef3._common import fail, integer, label
from ._config_check import check_currency
from ..ef3._robust_common import make_config, parameter_map
from ..ef4._legs import PROFILES, SLOTS, Leg, check_leg_bounds, check_legs
from ..ef4._proj_common import (
    MAX_NS, Cell, RefRow, check_features, check_meta, check_policy, finish, fraction_float, knowledge_reason,
    reference_rows, token, validate_reference,
)
from ..ef4._relative_excess import _core_ids, encode_core_ids

CORE_IDENTITY = "dv1.core_spread"
CORE_ALGORITHM = "dv1-core-spread-v1"
# The label names the whole convention set (simple returns of exact witnesses, profile-labelled start facts with one shared
# end fact, the regular_open operand daily_bar_open, EF4 eligibility, range as max minus min, population standard deviation
# with divisor K, partial populations withheld); another convention is another label.
CORE_POLICY = "dv1-core1"
CORE_RANGE = "core.benchmark_return_range_fraction"
CORE_STDEV = "core.benchmark_return_stdev_fraction"
CORE_FEATURES = (CORE_RANGE, CORE_STDEV)
CORE_META: dict[str, tuple[ValueType, str]] = {feature: (ValueType.FLOAT64, "fraction") for feature in CORE_FEATURES}
CORE_ROLE = "legs"
CORE_PROFILES = ("prior_close", "window_start", "regular_open")
OPERAND_DAILY_BAR_OPEN = "daily_bar_open"
CORE_FORMULA = {
    CORE_RANGE: ("RANGE of core returns max r - min r over the K declared funds, r = E / S - 1 (the value the deprecated "
                 "core.benchmark_return_dispersion_fraction publishes; a range, not a dispersion); regular_open start leg = "
                 "daily_bar_open of the exact session, end leg = same-session close; any fund missing withholds the "
                 "value; exact rational, one float64 rounding"),
    CORE_STDEV: ("POPULATION standard deviation (divisor K, not K - 1) of the core returns r = E / S - 1 over the K "
                 "declared funds: sqrt((K sum r^2 - (sum r)^2) / K^2); not the range; regular_open start leg = "
                 "daily_bar_open of the exact session, end leg = same-session close; any fund missing withholds the "
                 "value; exact when the variance is a rational square, else Decimal120 square root, one float64 rounding"),
}
_REQUIRED = frozenset({"policy_version", "core_benchmark_ids", "core_profile", "alignment_tolerance_ns",
                       "max_endpoint_age_ns", "evidence_limit"})
_OPTIONAL = frozenset({"window_ns"})
_LEG_KINDS = frozenset({"ef4.leg.start", "ef4.leg.end"})
# Closed ordered leg text: start `profile[;slot][;op];rev;act`, end `[slot;]rev;act` (`op` is the operand label).
_START_KEYS = frozenset({("profile", "rev", "act"), ("profile", "slot", "rev", "act"), ("profile", "op", "rev", "act"),
                         ("profile", "slot", "op", "rev", "act")})
_END_KEYS = frozenset({("rev", "act"), ("slot", "rev", "act")})


@dataclass(frozen=True)
class CoreSpreadSettings:
    policy_version: str
    core_benchmark_ids: tuple[str, ...]
    core_profile: str
    alignment_tolerance_ns: int
    max_endpoint_age_ns: int
    window_ns: int | None
    evidence_limit: int


def _shape(policy: object, core_ids: object, profile: object, tolerance: object, age: object, window: object,
           limit: object) -> CoreSpreadSettings:
    """Config-stage shape of the closed parameters; the policy label itself is a later (version) stage."""
    if type(policy) is not str:
        fail(ErrorCode.INVALID_CONFIG, "exact core spread policy label required")
    ids = _core_ids(core_ids)
    if type(profile) is not str or profile not in CORE_PROFILES:
        fail(ErrorCode.INVALID_CONFIG, "core_profile must be prior_close, window_start or regular_open")
    tol = integer(tolerance, 0, MAX_NS)
    max_age = integer(age, 0, MAX_NS)
    evidence_limit = integer(limit, 0, 10000)
    if (profile == "window_start") != (window is not None):
        fail(ErrorCode.INVALID_CONFIG, "window_ns is present exactly when core_profile is window_start")
    width = None if window is None else integer(window, 1, MAX_NS)
    return CoreSpreadSettings(policy, ids, profile, tol, max_age, width, evidence_limit)


def build_core_spread_config(*, policy_version: str | None, core_benchmark_ids: tuple[str, ...] | list[str] | None,
                             core_profile: str | None, alignment_tolerance_ns: int | None,
                             max_endpoint_age_ns: int | None, window_ns: int | None, session: SessionSpec | None,
                             availability: AvailabilitySpec | None, price_unit: PriceUnit | None,
                             evidence_limit: int | None) -> ConfigSpec:
    """Final ConfigSpec; every parameter is explicit with no default. The producer has no adjustment basis."""
    settings = _shape(policy_version, core_benchmark_ids, core_profile, alignment_tolerance_ns, max_endpoint_age_ns,
                      window_ns, evidence_limit)
    if type(session) is not SessionSpec or type(availability) is not AvailabilitySpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete session/timing required")
    price_unit = check_currency(price_unit)
    label(price_unit.currency)
    if availability.reconstruction_reason is not None:
        label(availability.reconstruction_reason)
    # The cutoff may fall inside the target session; a fact after it is simply not eligible (future_market, not a refusal).
    if availability.market_cutoff_ns < session.open_ns:
        fail(ErrorCode.BOUNDS, "market cutoff precedes the target session open")
    if settings.policy_version != CORE_POLICY:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported core spread policy label")
    params = [Parameter("policy_version", settings.policy_version),
              Parameter("core_benchmark_ids", encode_core_ids(settings.core_benchmark_ids)),
              Parameter("core_profile", settings.core_profile),
              Parameter("alignment_tolerance_ns", settings.alignment_tolerance_ns),
              Parameter("max_endpoint_age_ns", settings.max_endpoint_age_ns),
              Parameter("evidence_limit", settings.evidence_limit)]
    if settings.window_ns is not None:
        params.append(Parameter("window_ns", settings.window_ns))
    return make_config(CORE_IDENTITY, CORE_ALGORITHM, tuple(params), 1, session, availability, AdjustmentSpec(),
                       price_unit)


def decode_core_spread_config(config: ConfigSpec, *, defer_version: bool = False) -> CoreSpreadSettings:
    """Validate the closed core spread envelope and return its settings (`defer_version` leaves the label to a later stage)."""
    values = parameter_map(config, CORE_IDENTITY, CORE_ALGORITHM, _REQUIRED, _OPTIONAL)
    settings = _shape(values["policy_version"], values["core_benchmark_ids"], values["core_profile"],
                      values["alignment_tolerance_ns"], values["max_endpoint_age_ns"], values.get("window_ns"),
                      values["evidence_limit"])
    if defer_version and settings.policy_version != CORE_POLICY:
        return settings
    expected = build_core_spread_config(
        policy_version=settings.policy_version, core_benchmark_ids=settings.core_benchmark_ids,
        core_profile=settings.core_profile, alignment_tolerance_ns=settings.alignment_tolerance_ns,
        max_endpoint_age_ns=settings.max_endpoint_age_ns, window_ns=settings.window_ns, session=config.session,
        availability=config.availability, price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical core spread envelope")
    return settings


def _parse_legs(rows: list[RefRow]) -> tuple[list[Leg], dict[int, str]]:
    """Wire admission of the leg facts: no end time, positive price, closed key=value text with closed vocabularies.

    Returns the legs and the operand label of each start leg that carries one (by fact row)."""
    legs: list[Leg] = []
    operands: dict[int, str] = {}
    for row in rows:
        if row.end is not None:
            fail(ErrorCode.INVALID_SCHEMA, "a leg witness is a point in time (no effective end)")
        if row.price is None or row.price <= 0:
            fail(ErrorCode.INVALID_SCHEMA, "a leg carries a positive price coefficient")
        if type(row.text) is not str:
            fail(ErrorCode.INVALID_SCHEMA, "a leg fact carries its profile, slot, operand, revision and action text")
        fields: list[tuple[str, str]] = []
        for part in row.text.split(";"):
            key, separator, value = part.partition("=")
            if not separator:
                fail(ErrorCode.INVALID_SCHEMA, "closed key=value leg text grammar required")
            fields.append((key, token(value)))
        keys = tuple(key for key, _ in fields)
        if keys not in (_START_KEYS if row.kind == "ef4.leg.start" else _END_KEYS):
            fail(ErrorCode.INVALID_SCHEMA, "closed ordered leg text grammar required")
        text = dict(fields)
        profile = text.get("profile")
        if profile is not None and profile not in PROFILES:
            fail(ErrorCode.INVALID_SCHEMA, "unknown or unsupported start profile")
        slot = text.get("slot", "A")
        if slot not in SLOTS or slot != "A":
            fail(ErrorCode.INVALID_SCHEMA, "unknown or unsupported slot")
        if "op" in text:
            operands[row.row] = text["op"]
        legs.append(Leg(row.instrument, row.kind, row.session, row.start, row.price, profile, slot, text["rev"],
                        text["act"], row.known_at, row.reference_id, row.row))
    return legs, operands


def _population_sd(returns: list[Fraction]) -> float:
    """Population standard deviation (divisor K) of exact returns, one correctly rounded float64."""
    k = len(returns)
    total = sum(returns, Fraction(0))
    squares = sum((r * r for r in returns), Fraction(0))
    variance = (k * squares - total * total) / (k * k)
    if variance == 0:
        return 0.0
    numerator, denominator = variance.numerator, variance.denominator
    root_n, root_d = isqrt(numerator), isqrt(denominator)
    if root_n * root_n == numerator and root_d * root_d == denominator:
        return fraction_float(Fraction(root_n, root_d))
    context = Context(prec=120, rounding=ROUND_HALF_EVEN, Emin=MIN_EMIN, Emax=MAX_EMAX)
    try:
        with localcontext(context):
            converted = float((Decimal(numerator) / Decimal(denominator)).sqrt())
    except (DecimalException, OverflowError, ValueError):
        fail(ErrorCode.OVERFLOW, "core standard deviation arithmetic outside declared numeric policy")
    if not isfinite(converted):
        fail(ErrorCode.OVERFLOW, "core standard deviation outside binary64")
    return converted


def _leg_ok(start: Leg, end: Leg, settings: CoreSpreadSettings, operand: str | None, cutoff: int) -> bool:
    """One fund is individually eligible: one action snapshot, the profile's phase and operand, a fresh endpoint."""
    if start.act != end.act or end.t > cutoff or cutoff - end.t > settings.max_endpoint_age_ns:
        return False
    if settings.core_profile == "prior_close":
        return start.session != end.session
    if settings.core_profile == "window_start":
        assert settings.window_ns is not None
        return (start.session == end.session
                and abs((end.t - start.t) - settings.window_ns) <= settings.alignment_tolerance_ns)
    # regular_open: the official daily-bar open of the exact session; any other operand label (or none) does not count.
    return start.session == end.session and operand == OPERAND_DAILY_BAR_OPEN


def compute_core_spread(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None], config: ConfigSpec,
                        *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected dv1-core1 outputs; `batches` is the single nullable role `legs` (REFERENCE leg facts)."""
    if type(batches) not in (tuple, list) or len(batches) != 1:
        fail(ErrorCode.INVALID_SCHEMA, "exactly one role (legs) is required")
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    legs_batch = batches[0]
    legs: list[Leg] = []
    operands: dict[int, str] = {}
    if legs_batch is not None:
        legs, operands = _parse_legs(reference_rows(legs_batch, _LEG_KINDS))
        validate_reference(legs_batch)
    settings = decode_core_spread_config(config, defer_version=True)
    selected = check_features(features, CORE_FEATURES)
    if legs_batch is not None:
        check_meta(legs_batch, config, unit=True, adjustment=False)
    check_policy(settings.policy_version, CORE_POLICY)
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact result entity required")
    label(entity.instrument_id)
    check_legs(legs, frozenset(settings.core_benchmark_ids))
    check_leg_bounds(legs)
    input_id = "" if legs_batch is None else legs_batch.metadata.source.input_id
    starts = {(leg.instrument, leg.profile): leg for leg in legs if leg.is_start}
    ends = {leg.instrument: leg for leg in legs if not leg.is_start}
    cutoff, knowledge = config.availability.market_cutoff_ns, config.availability.knowledge_cutoff_ns
    total = len(settings.core_benchmark_ids)
    reasons: set[Reason] = set()
    eligible: list[tuple[int, Leg, Leg]] = []
    if not legs:
        reasons.add(Reason.ABSENT_INPUT)
    else:
        for position, fund in enumerate(settings.core_benchmark_ids):
            start, end = starts.get((fund, settings.core_profile)), ends.get(fund)
            if start is None or end is None:
                continue
            if knowledge_reason(start.known_at, knowledge) is not None or knowledge_reason(end.known_at, knowledge) is not None:
                continue
            if _leg_ok(start, end, settings, operands.get(start.row), cutoff):
                eligible.append((position, start, end))
        if len(eligible) != total:
            reasons.add(Reason.PARTIAL_UNIVERSE)
        else:
            tolerance = settings.alignment_tolerance_ns
            end_times = [end.t for _, _, end in eligible]
            start_times = [start.t for _, start, _ in eligible]
            misaligned = max(end_times) - min(end_times) > tolerance or len({end.session for _, _, end in eligible}) > 1
            if settings.core_profile == "window_start":
                misaligned = misaligned or max(start_times) - min(start_times) > tolerance
            elif len({start.session for _, start, _ in eligible}) > 1:
                misaligned = True
            if misaligned:
                reasons.add(Reason.INELIGIBLE)
    returns = [Fraction(end.price, start.price) - 1 for _, start, end in eligible] if not reasons else []
    cells: dict[str, Cell] = {}
    for feature in selected:
        cell = Cell(None, set(reasons), total, len(eligible))
        if not reasons:
            cell.value = fraction_float(max(returns) - min(returns)) if feature == CORE_RANGE else _population_sd(returns)
            cell.witnesses = []
            for position, start, end in eligible:
                # Row id slot:<index> in declared order: fund k start is slot 2k, its end slot 2k + 1.
                cell.witnesses.append(start.evidence(entity, feature, input_id, f"slot:{2 * position}"))
                cell.witnesses.append(end.evidence(entity, feature, input_id, f"slot:{2 * position + 1}"))
        cells[feature] = cell
    bindings = () if legs_batch is None else (InputBinding(CORE_ROLE, DataKind.REFERENCE, legs_batch.metadata),)
    return finish(config, entity, CORE_ALGORITHM, selected, CORE_META, cells, bindings, settings.evidence_limit)
