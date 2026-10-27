"""Shared admission, quality vocabulary and evidence helpers of the EF3 robust history, pace and mean producers.

Roles are fixed nullable slots. DAILY and BAR roles are admitted by the shared validators first and then by the
identity checks below; REFERENCE roles carry the `ef3.*` facts. Per-slot coverage entries are optional for a delivered
row and name the slot: `session:<session_id>` (daily series), `member:<instrument_id>` (cohort values) and
`bucket:<session_id>:<index>` (bars). No clock, I/O, storage, default window or default parameter.
"""
from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from collections.abc import Callable
from dataclasses import dataclass
from math import gcd
import re
from typing import Any

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, Coverage, DataKind, ErrorCode, EntityKey,
    EvidenceRow, Parameter, PriceUnit, Reason, SessionSpec, Status, WindowSpec, validate_batch,
)
from ._common import fail, label

I64_MAX = 2**63 - 1
MAX_GRID_SESSIONS = 8192
MAX_EDGES = 4097
BOUNDS_KIND = "ef3.session.bounds"
EXCLUDED_KIND = "ef3.session.excluded"
POPULATION_KIND = "ef3.population.member"
EDGE_KIND = "ef3.bucket.edge"
# The first applicable reason fixes the status; every applicable reason is still reported (lexical order).
PRECEDENCE = (Reason.ABSENT_INPUT, Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE, Reason.NULL_FIELD,
              Reason.INELIGIBLE, Reason.GOVERNED_GAP, Reason.FUTURE_MARKET, Reason.PARTIAL_UNIVERSE,
              Reason.INSUFFICIENT_HISTORY, Reason.NO_ELIGIBLE_OBSERVATIONS, Reason.EMPTY_UNIVERSE,
              Reason.ZERO_DENOMINATOR)
STATUS = {Reason.GOVERNED_GAP: Status.INCOMPLETE_COVERAGE, Reason.FUTURE_MARKET: Status.INCOMPLETE_COVERAGE,
          Reason.PARTIAL_UNIVERSE: Status.INCOMPLETE_COVERAGE, Reason.INSUFFICIENT_HISTORY: Status.INSUFFICIENT_HISTORY,
          Reason.NO_ELIGIBLE_OBSERVATIONS: Status.NOT_APPLICABLE, Reason.EMPTY_UNIVERSE: Status.NOT_APPLICABLE,
          Reason.ZERO_DENOMINATOR: Status.NOT_APPLICABLE}
_B64URL = re.compile("[A-Za-z0-9_-]+")


def first_status(reasons: set[Reason] | frozenset[Reason]) -> Status:
    first = next((reason for reason in PRECEDENCE if reason in reasons), None)
    return Status.AVAILABLE if first is None else STATUS.get(first, Status.MISSING_INPUT)


def ordered(reasons: set[Reason] | frozenset[Reason]) -> tuple[Reason, ...]:
    return tuple(sorted(reasons, key=lambda reason: reason.value))


def reduced_pair(num: object, den: object, *, maximum_one: bool, positive: bool) -> tuple[int, int]:
    """Caller rational as a reduced exact int64 pair; no float, bool or decimal text."""
    if type(num) is not int or type(den) is not int:
        fail(ErrorCode.INVALID_CONFIG, "exact integer rational pair required")
    if not 1 <= den <= I64_MAX:
        fail(ErrorCode.INVALID_CONFIG, "rational denominator outside 1..2^63-1")
    if num < 0 or (positive and num == 0):
        fail(ErrorCode.INVALID_CONFIG, "nonnegative quantile numerator or positive scale numerator required")
    if num > I64_MAX or (maximum_one and num > den):
        fail(ErrorCode.INVALID_CONFIG, "rational outside its admitted range")
    if gcd(num, den) != 1:
        fail(ErrorCode.INVALID_CONFIG, "reduced rational pair required (zero only as 0/1)")
    return num, den


def check_policy(value: object, expected: str) -> str:
    if type(value) is not str:
        fail(ErrorCode.INVALID_CONFIG, "exact policy label required")
    if value != expected:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported policy label")
    return value


def make_config(identity: str, algorithm: str, params: tuple[Parameter, ...], count: int, session: SessionSpec,
                availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit) -> ConfigSpec:
    """Final ConfigSpec: the target session, an explicit unit and one shared adjustment basis."""
    if (type(session) is not SessionSpec or type(availability) is not AvailabilitySpec
            or type(adjustment) is not AdjustmentSpec):
        fail(ErrorCode.INVALID_CONFIG, "concrete session/timing/action required")
    if type(price_unit) is not PriceUnit:
        fail(ErrorCode.INVALID_UNIT, "an explicit PriceUnit is required")
    for value in (adjustment.policy_version, adjustment.action_snapshot, adjustment.anchor, price_unit.currency):
        label(value)
    if availability.reconstruction_reason is not None:
        label(availability.reconstruction_reason)
    if availability.market_cutoff_ns < session.open_ns:
        fail(ErrorCode.BOUNDS, "market cutoff precedes the target session open")
    return ConfigSpec(identity, algorithm, params, session,
                      WindowSpec(count, session.session_id, (session.session_id,), "prior_only"),
                      availability, adjustment, price_unit)


def parameter_map(config: ConfigSpec, identity: str, algorithm: str, required: frozenset[str],
                  optional: frozenset[str]) -> dict[str, Any]:
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.algorithm_version != algorithm:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "algorithm version differs")
    if config.identity != identity:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "not this producer's configuration")
    values: dict[str, Any] = {p.name: p.value for p in config.parameters}
    if not required <= set(values) or not set(values) <= required | optional:
        fail(ErrorCode.INVALID_CONFIG, "closed producer parameters required (there are no defaults)")
    if config.price_unit is None:
        fail(ErrorCode.INVALID_UNIT, "an explicit PriceUnit is required")
    return values


def check_features(features: object, allowed: tuple[str, ...]) -> tuple[str, ...]:
    if (type(features) is not tuple or not 1 <= len(features) <= len(allowed)
            or any(type(feature) is not str for feature in features) or len(set(features)) != len(features)):
        fail(ErrorCode.INVALID_SCHEMA, "nonempty unique selected feature IDs required")
    if any(feature not in allowed for feature in features):
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown selected feature")
    return tuple(sorted(features))


def check_entity(entity: object, config: ConfigSpec) -> EntityKey:
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    return entity


def check_slots(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None], count: int,
                kinds: tuple[DataKind, ...]) -> list[CanonicalBatch | None]:
    if type(batches) not in (tuple, list) or len(batches) != count:
        fail(ErrorCode.INVALID_SCHEMA, "the fixed nullable role slots are required")
    slots: list[CanonicalBatch | None] = list(batches)
    for batch, kind in zip(slots, kinds):
        if batch is not None and (type(batch) is not CanonicalBatch or batch.kind != kind):
            fail(ErrorCode.INVALID_SCHEMA, "wrong slot kind")
    present = [batch for batch in slots if batch is not None]
    if len({batch.metadata.source.input_id for batch in present}) != len(present):
        fail(ErrorCode.DUPLICATE, "distinct actual role input IDs required")
    return slots


def _decode_part(part: str) -> str:
    if _B64URL.fullmatch(part) is None or len(part) % 4 == 1:
        fail(ErrorCode.INVALID_SCHEMA, "closed x1 reference grammar required")
    raw = urlsafe_b64decode(part + "=" * (-len(part) % 4))
    if urlsafe_b64encode(raw).rstrip(b"=").decode("ascii") != part:
        fail(ErrorCode.INVALID_SCHEMA, "reversible x1 reference grammar required")
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        fail(ErrorCode.INVALID_SCHEMA, "UTF8 x1 reference component required")
    if not text.strip() or any(ord(c) < 32 or ord(c) == 127 for c in text):
        fail(ErrorCode.INVALID_SCHEMA, "nonblank safe x1 reference component required")
    return text


def check_reference_id(reference_id: Any) -> str:
    """Closed grammar x1:B(id); returns the decoded id."""
    if type(reference_id) is not str or len(reference_id) > 256:
        fail(ErrorCode.INVALID_SCHEMA, "bounded x1 reference identity required")
    parts = reference_id.split(":")
    if len(parts) != 2 or parts[0] != "x1":
        fail(ErrorCode.INVALID_SCHEMA, "closed x1 reference grammar required")
    return _decode_part(parts[1])


def _check_meta(batch: CanonicalBatch, config: ConfigSpec) -> None:
    meta = batch.metadata
    if meta.namespace != config.session.namespace:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "input namespace differs from the target session")
    if meta.price_unit is not None and meta.price_unit != config.price_unit:
        fail(ErrorCode.INVALID_UNIT, "input currency/scale differs from the config unit")
    if meta.adjustment != config.adjustment:
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "input action basis differs from the config basis")
    for text in (meta.source.source_id, meta.source.snapshot_id, meta.source.mapping_version, meta.source.input_id):
        label(text, ErrorCode.INVALID_SCHEMA)
    if meta.ordering != "declared" or meta.duplicate_policy != "reject":
        fail(ErrorCode.INVALID_ORDER, "declared order and rejected duplicates required")
    if meta.coverage.observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "aggregate observed coverage differs from actual rows")
    if meta.scope is not None and meta.sampling != "none":
        fail(ErrorCode.INVALID_SCHEMA, "nonquote sampling required")


def columns_of(batch: CanonicalBatch) -> dict[str, tuple[Any, ...]]:
    return {c.name: c.values for c in batch.columns}


@dataclass(frozen=True)
class Fact:
    """One governed slot (a daily session, a cohort member or a bucket cell); `row_index is None` means no row."""

    input_id: str | None = None
    row_index: int | None = None
    coverage: Coverage | None = None
    has_column: bool = False
    value: int | None = None
    known_at_ns: int | None = None
    start_ns: int = 0
    end_ns: int = 0


def fact_reasons(fact: Fact, knowledge_cutoff_ns: int) -> frozenset[Reason]:
    """Causes that make one slot not READY (empty when READY); knowledge uses the original known_at in every mode."""
    if fact.row_index is None:
        return frozenset({Reason.ABSENT_INPUT if fact.coverage is None else Reason.GOVERNED_GAP})
    reasons: set[Reason] = set()
    if fact.known_at_ns is None:
        reasons.add(Reason.UNKNOWN_AVAILABILITY)
    elif fact.known_at_ns > knowledge_cutoff_ns:
        reasons.add(Reason.FUTURE_KNOWLEDGE)
    coverage = fact.coverage
    if coverage is not None and (not coverage.complete or coverage.expected != 1 or coverage.observed != 1):
        reasons.add(Reason.GOVERNED_GAP)
    if not fact.has_column:
        reasons.add(Reason.ABSENT_INPUT)
    elif fact.value is None:
        reasons.add(Reason.NULL_FIELD)
    return frozenset(reasons)


def knowledge_reasons(known_at_ns: int | None, knowledge_cutoff_ns: int) -> frozenset[Reason]:
    """Knowledge gate of one reference fact (E-A2): null is unknown_availability, later than K is future_knowledge,
    equal to K is available (the same rule the data rows, the exclusion facts and contract F already apply)."""
    if known_at_ns is None:
        return frozenset({Reason.UNKNOWN_AVAILABILITY})
    if known_at_ns > knowledge_cutoff_ns:
        return frozenset({Reason.FUTURE_KNOWLEDGE})
    return frozenset()


def bounds_reasons(grid: SessionGrid, window: tuple[str, ...], knowledge_cutoff_ns: int) -> frozenset[Reason]:
    """Knowledge of the session bounds facts a result uses: the target session and every session of the window
    (a declared exclusion removes a session from the sample, not its bounds from the grid)."""
    reasons: set[Reason] = set()
    for session_id in (*window, grid.order[grid.target_index]):
        reasons |= knowledge_reasons(grid.bounds_known_at[session_id], knowledge_cutoff_ns)
    return frozenset(reasons)


def _coverage_map(batch: CanonicalBatch, expected: Callable[[str], tuple[int, int] | None],
                  rows: dict[str, int]) -> dict[str, Coverage]:
    """Per-slot coverage entries must name an exact governed slot and agree with the delivered row."""
    result: dict[str, Coverage] = {}
    for entry in batch.metadata.interval_coverage:
        bounds = expected(entry.name)
        if bounds is None or (entry.start_ns, entry.end_ns) != bounds:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "coverage entry differs from an exact governed slot")
        coverage = entry.coverage
        if coverage.observed > 1 or (coverage.expected is not None and coverage.expected > 1):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "per-slot coverage cannot exceed one observation")
        if coverage.observed != int(entry.name in rows):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "per-slot observed coverage contradicts the row")
        result[entry.name] = coverage
    return result


def admit_market(batch: CanonicalBatch, kind: DataKind, config: ConfigSpec) -> dict[str, tuple[Any, ...]]:
    """Shared validators first (so DUPLICATE and INVALID_ORDER precede identity checks), then unit and basis."""
    validate_batch(batch, availability=config.availability, required_fields=())
    _check_meta(batch, config)
    if batch.metadata.price_unit is None:
        fail(ErrorCode.INVALID_UNIT, "market input requires the config price unit")
    return columns_of(batch)


@dataclass(frozen=True)
class ExcludedFact:
    known_at_ns: int | None
    reason_label: str


@dataclass(frozen=True)
class SessionGrid:
    """The governed grid of the `sessions` role: sessions in grid order with their exact actual bounds."""

    input_id: str
    order: tuple[str, ...]
    bounds: dict[str, tuple[int, int]]
    bounds_known_at: dict[str, int | None]
    excluded: dict[str, ExcludedFact]
    target_index: int


def admit_sessions(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey, *,
                   allow_excluded: bool) -> SessionGrid:
    """Admit the session bounds (and optional exclusion) facts; every contradiction refuses."""
    validate_batch(batch, required_fields=())
    _check_meta(batch, config)
    cols = columns_of(batch)
    order: list[str] = []
    bounds: dict[str, tuple[int, int]] = {}
    known: dict[str, int | None] = {}
    grid_ref: str | None = None
    pending: list[tuple[str, ExcludedFact, tuple[int, int | None]]] = []
    previous: tuple[int, int] | None = None
    snapshot = batch.metadata.source.snapshot_id
    for row in range(batch.row_count):
        if cols["instrument_id"][row] != entity.instrument_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "row instrument differs from the target entity")
        kind = cols["fact_kind"][row]
        reference_id = cols["reference_id"][row]
        check_reference_id(reference_id)
        for name in ("price", "factor_num", "factor_den"):
            if name in cols and cols[name][row] is not None:
                fail(ErrorCode.INVALID_SCHEMA, "EF3 facts carry no price or factor")
        session_id = label(cols["session_id"][row], ErrorCode.INVALID_SCHEMA)
        start = cols["effective_start_ns"][row]
        end = cols["effective_end_ns"][row] if "effective_end_ns" in cols else None
        known_at = cols["known_at_ns"][row] if "known_at_ns" in cols else None
        text = cols["text"][row] if "text" in cols else None
        if kind == BOUNDS_KIND:
            if end is None:
                fail(ErrorCode.INVALID_SCHEMA, "a session bounds fact carries its actual close")
            if text != snapshot:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "session bounds revision differs from the snapshot")
            if grid_ref is not None and reference_id != grid_ref:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "one governed grid id required across the role")
            grid_ref = reference_id
            if session_id in bounds:
                fail(ErrorCode.DUPLICATE, "duplicate session bounds fact")
            if previous is not None and (start <= previous[0] or start < previous[1]):
                fail(ErrorCode.INCONSISTENT_IDENTITY, "bounds facts must be strictly ordered and not overlap")
            if len(order) >= MAX_GRID_SESSIONS:
                fail(ErrorCode.BOUNDS, "too many governed sessions")
            previous = (start, end)
            order.append(session_id)
            bounds[session_id] = (start, end)
            known[session_id] = known_at
        elif kind == EXCLUDED_KIND:
            if not allow_excluded:
                fail(ErrorCode.INVALID_SCHEMA, "this producer admits only session bounds facts")
            if type(text) is not str or not text.strip():
                fail(ErrorCode.INVALID_SCHEMA, "an exclusion fact carries a nonempty reason label")
            pending.append((session_id, ExcludedFact(known_at, text), (start, end)))
        else:
            fail(ErrorCode.INVALID_SCHEMA, "unknown fact kind for this role")
    excluded: dict[str, ExcludedFact] = {}
    for session_id, fact, (start, end) in pending:
        if session_id not in bounds:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "exclusion fact for a session without a bounds fact")
        if (start, end) != bounds[session_id]:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "exclusion fact bounds differ from the session bounds fact")
        if session_id in excluded:
            fail(ErrorCode.DUPLICATE, "two exclusion facts for one session")
        if session_id == config.session.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "an exclusion fact on the target session is refused")
        excluded[session_id] = fact
    target = config.session.session_id
    if target not in bounds or bounds[target] != (config.session.open_ns, config.session.close_ns):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "the target session needs its exact bounds fact")
    return SessionGrid(batch.metadata.source.input_id, tuple(order), bounds, known, excluded, order.index(target))


def admit_series(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey, grid: SessionGrid,
                 field: str) -> dict[str, Fact]:
    """Daily rows of the target instrument on the governed grid; returns the per-session facts."""
    cols = admit_market(batch, DataKind.DAILY, config)
    input_id = batch.metadata.source.input_id
    rows: dict[str, int] = {}
    for row in range(batch.row_count):
        if cols["instrument_id"][row] != entity.instrument_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "series instrument differs from the target entity")
        session_id = cols["session_id"][row]
        if session_id not in grid.bounds or (cols["start_ns"][row], cols["end_ns"][row]) != grid.bounds[session_id]:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "series row without an exact session bounds fact")
        rows[f"session:{session_id}"] = row
    coverage = _coverage_map(batch, lambda name: grid.bounds.get(name[8:]) if name.startswith("session:") else None, rows)
    facts: dict[str, Fact] = {}
    for session_id, (start, end) in grid.bounds.items():
        key = f"session:{session_id}"
        row_index = rows.get(key)
        if row_index is None:
            facts[session_id] = Fact(input_id, None, coverage.get(key), False, None, None, start, end)
        else:
            facts[session_id] = Fact(
                input_id, row_index, coverage.get(key), field in cols,
                cols[field][row_index] if field in cols else None,
                cols["known_at_ns"][row_index] if "known_at_ns" in cols else None, start, end)
    return facts


def evidence_row(entity: EntityKey, feature: str, fact: Fact, row_id: str, event_ns: int | None = None,
                 start_ns: int | None = None, known_at_ns: int | None = None) -> EvidenceRow:
    assert fact.input_id is not None
    return EvidenceRow(entity, feature, fact.input_id, row_id, fact.end_ns if event_ns is None else event_ns,
                       fact.known_at_ns if known_at_ns is None else known_at_ns,
                       fact.start_ns if start_ns is None else start_ns, fact.end_ns, "consumed", None,
                       "completed_interval")


def reference_evidence(entity: EntityKey, feature: str, grid: SessionGrid, session_id: str,
                       row_id: str) -> EvidenceRow:
    """Exclusion / ineligible session witness bound to the REFERENCE `sessions` role (ordinary boundary: the
    shared FeatureResult validator admits a completed_interval boundary only for BAR and DAILY inputs)."""
    start, end = grid.bounds[session_id]
    fact = grid.excluded.get(session_id)
    known_at = fact.known_at_ns if fact is not None else grid.bounds_known_at[session_id]
    return EvidenceRow(entity, feature, grid.input_id, row_id, end, known_at, start, end, "excluded",
                       Reason.INELIGIBLE, "ordinary")

