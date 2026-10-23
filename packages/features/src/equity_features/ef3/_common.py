"""Shared EF3 daily-grid context, close-only BAR admission and quality vocabulary; pure, no I/O.

The daily governed grid follows the R17 conventions (one slot per governed session with exact `[open, close)`
bounds, per-slot coverage named `slot:<index>`, explicit price unit and adjustment) but is a local codec because
`equity-features` does not depend on `equity-features-intraday`.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import NoReturn, cast

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, ConfigSpec, ContractError, Coverage,
    DataKind, ErrorCode, InputBinding, Parameter, PriceUnit, Reason, SessionSpec, Status, WindowSpec,
    validate_batch,
)

GRID_SCHEMA = "equity-features.ef3-daily-grid.v1"
MAX_SESSIONS = 8192
I64_MIN = -(2**63)
I64_MAX = 2**63 - 1
# The first applicable reason fixes the status; every applicable reason is still reported (lexical order).
PRECEDENCE = (Reason.ABSENT_INPUT, Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE, Reason.NULL_FIELD,
              Reason.INELIGIBLE, Reason.GOVERNED_GAP, Reason.INSUFFICIENT_HISTORY,
              Reason.NO_ELIGIBLE_OBSERVATIONS, Reason.ZERO_DENOMINATOR)
STATUS = {Reason.GOVERNED_GAP: Status.INCOMPLETE_COVERAGE, Reason.INSUFFICIENT_HISTORY: Status.INSUFFICIENT_HISTORY,
          Reason.NO_ELIGIBLE_OBSERVATIONS: Status.NOT_APPLICABLE, Reason.ZERO_DENOMINATOR: Status.NOT_APPLICABLE}
CLOSE_FIELDS = ("instrument_id", "session_id", "start_ns", "end_ns", "close", "known_at_ns")


def fail(code: ErrorCode, message: str) -> NoReturn:
    raise ContractError(code, message)


def label(value: object, code: ErrorCode = ErrorCode.INVALID_CONFIG, limit: int = 128) -> str:
    """Bounded nonblank printable ASCII identity."""
    if (type(value) is not str or not value.strip() or len(value) > limit
            or any(not 32 <= ord(c) <= 126 for c in value)):
        fail(code, "bounded nonblank printable ASCII label required")
    return value


def integer(value: object, minimum: int, maximum: int, code: ErrorCode = ErrorCode.INVALID_CONFIG) -> int:
    """Exact integer (never bool or float) within inclusive bounds."""
    if type(value) is not int or not minimum <= value <= maximum:
        fail(code, f"exact integer in {minimum}..{maximum} required")
    return value


def first_status(reasons: set[Reason]) -> Status:
    first = next((reason for reason in PRECEDENCE if reason in reasons), None)
    return Status.AVAILABLE if first is None else STATUS.get(first, Status.MISSING_INPUT)


@dataclass(frozen=True)
class DailySlot:
    index: int
    session_id: str
    start_ns: int
    end_ns: int


@dataclass(frozen=True)
class DailyGrid:
    """Governed daily grid: one slot per actual session in order, plus the target slot index."""

    instrument_id: str
    calendar_id: str
    grid_id: str
    revision: str
    sessions: tuple[SessionSpec, ...]
    target_index: int

    def __post_init__(self) -> None:
        for value in (self.instrument_id, self.calendar_id, self.grid_id, self.revision):
            label(value)
        if (type(self.sessions) not in (tuple, list) or not 1 <= len(self.sessions) <= MAX_SESSIONS
                or any(type(s) is not SessionSpec for s in self.sessions)):
            fail(ErrorCode.INVALID_CONFIG, f"1..{MAX_SESSIONS} concrete actual sessions required")
        object.__setattr__(self, "sessions", tuple(self.sessions))
        for session in self.sessions:
            label(session.namespace)
            label(session.session_id)
            label(session.timezone_label, limit=64)
            if session.intervals:
                fail(ErrorCode.INVALID_CONFIG, "daily slots are whole sessions; session intervals must be empty")
        if len({s.namespace for s in self.sessions}) != 1:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "one session namespace required")
        if len({s.session_id for s in self.sessions}) != len(self.sessions):
            fail(ErrorCode.DUPLICATE, "duplicate governed session")
        if any(a.close_ns > b.open_ns for a, b in zip(self.sessions, self.sessions[1:])):
            fail(ErrorCode.INVALID_ORDER, "actual sessions overlap or are unordered")
        integer(self.target_index, 0, len(self.sessions) - 1)

    def slots(self) -> tuple[DailySlot, ...]:
        return tuple(DailySlot(i, s.session_id, s.open_ns, s.close_ns) for i, s in enumerate(self.sessions))

    def to_json(self) -> str:
        return json.dumps({"schema": GRID_SCHEMA, **asdict(self)}, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.to_json().encode("ascii")).hexdigest()

    @property
    def target(self) -> SessionSpec:
        return self.sessions[self.target_index]


def grid_parameters(grid: DailyGrid) -> tuple[Parameter, ...]:
    return Parameter("grid_schema", GRID_SCHEMA), Parameter("grid_sha256", grid.digest)


def check_grid_parameters(values: dict[str, object], grid: DailyGrid) -> None:
    if values["grid_schema"] != GRID_SCHEMA:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "daily grid codec mismatch")
    if values["grid_sha256"] != grid.digest:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "daily grid identity differs")


def envelope(identity: str, algorithm: str, parameters: tuple[Parameter, ...], grid: DailyGrid,
             availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit) -> ConfigSpec:
    """Final ConfigSpec: the target session, the whole governed grid and an explicit unit and adjustment."""
    if (type(grid) is not DailyGrid or type(availability) is not AvailabilitySpec
            or type(adjustment) is not AdjustmentSpec):
        fail(ErrorCode.INVALID_CONFIG, "concrete grid/timing/action required")
    if type(price_unit) is not PriceUnit:
        fail(ErrorCode.INVALID_UNIT, "an explicit PriceUnit is required")
    for value in (adjustment.policy_version, adjustment.action_snapshot, adjustment.anchor, price_unit.currency):
        label(value)
    if availability.reconstruction_reason is not None:
        label(availability.reconstruction_reason)
    target = grid.target
    if not target.close_ns <= availability.market_cutoff_ns <= grid.sessions[-1].close_ns:
        fail(ErrorCode.BOUNDS, "market cutoff must follow the completed target session")
    return ConfigSpec(identity, algorithm, parameters + grid_parameters(grid), target,
                      WindowSpec(len(grid.sessions), target.session_id,
                                 tuple(s.session_id for s in grid.sessions), "completed_eod"),
                      availability, adjustment, price_unit)


def parameter_map(config: ConfigSpec, identity: str, algorithm: str, keys: frozenset[str],
                  grid: DailyGrid) -> dict[str, object]:
    """Closed decode envelope shared by the daily producers."""
    if type(grid) is not DailyGrid or type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete daily grid/config required")
    if config.algorithm_version != algorithm:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "algorithm version differs")
    if config.identity != identity:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "not this producer's configuration")
    values: dict[str, object] = {p.name: p.value for p in config.parameters}
    if set(values) != keys | {"grid_schema", "grid_sha256"}:
        fail(ErrorCode.INVALID_CONFIG, "closed producer parameters required (there are no defaults)")
    check_grid_parameters(values, grid)
    if config.price_unit is None:
        fail(ErrorCode.INVALID_UNIT, "an explicit PriceUnit is required")
    return values


@dataclass(frozen=True)
class CloseFact:
    """Per-slot supplied close fact; `row_index is None` means no row for the slot."""
    slot: DailySlot
    coverage: Coverage | None = None
    columns: frozenset[str] = frozenset()
    input_id: str | None = None
    row_index: int | None = None
    close: int | None = None
    known_at_ns: int | None = None


@dataclass(frozen=True)
class RoleAdmission:
    facts: tuple[CloseFact, ...]
    binding: InputBinding | None
    present: bool


def absent_role(grid: DailyGrid) -> RoleAdmission:
    return RoleAdmission(tuple(CloseFact(s) for s in grid.slots()), None, False)


def admit_role(role: str, batch: CanonicalBatch | None, instrument_id: str, grid: DailyGrid,
               config: ConfigSpec) -> RoleAdmission:
    """Structural admission of one close-only BAR role on the daily grid; every contradiction refuses."""
    if batch is None:
        return absent_role(grid)
    if type(batch) is not CanonicalBatch or batch.kind != DataKind.BAR:
        fail(ErrorCode.INVALID_SCHEMA, "an actual BAR batch is required for a close role")
    # Row-level semantics first, so a duplicated interval is DUPLICATE rather than a slot-bound overflow.
    validate_batch(batch, required_fields=())
    slots = grid.slots()
    meta: BatchMetadata = batch.metadata
    if batch.row_count > len(slots) or len(meta.interval_coverage) > len(slots):
        fail(ErrorCode.BOUNDS, "delivery exceeds governed slot bound")
    if meta.namespace != grid.sessions[0].namespace:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "input namespace differs from the grid")
    if meta.price_unit != config.price_unit:
        fail(ErrorCode.INVALID_UNIT, "input currency/scale differs from the config unit")
    if meta.adjustment != config.adjustment:
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "input action basis differs from the config basis")
    for text in (meta.source.source_id, meta.source.snapshot_id, meta.source.mapping_version, meta.source.input_id):
        label(text, ErrorCode.INVALID_SCHEMA)
    scope = meta.scope
    if scope is None or meta.sampling != "none":
        fail(ErrorCode.INVALID_SCHEMA, "explicit BAR scope and nonquote sampling required")
    if meta.ordering != "declared" or meta.duplicate_policy != "reject":
        fail(ErrorCode.INVALID_ORDER, "declared order and rejected duplicates required")
    if scope.start_ns < slots[0].start_ns or scope.end_ns > slots[-1].end_ns:
        fail(ErrorCode.BOUNDS, "input scope outside the governed grid")
    if meta.coverage.observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "aggregate observed coverage differs from actual rows")
    columns = {c.name: c.values for c in batch.columns}
    lookup = {(s.session_id, s.start_ns, s.end_ns): s for s in slots}
    market_cutoff = config.availability.market_cutoff_ns
    rows: dict[int, int] = {}
    previous = -1
    for row in range(batch.row_count):
        if columns["instrument_id"][row] != instrument_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "row instrument differs from the role instrument")
        start, end = cast(int, columns["start_ns"][row]), cast(int, columns["end_ns"][row])
        if end > market_cutoff:
            fail(ErrorCode.BOUNDS, "forming/future supplied bar")
        slot = lookup.get((cast(str, columns["session_id"][row]), start, end))
        if slot is None:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "row not on the governed daily grid")
        if not scope.start_ns <= start < end <= scope.end_ns:
            fail(ErrorCode.BOUNDS, "row outside its own input scope")
        if slot.index in rows:
            fail(ErrorCode.DUPLICATE, "duplicate governed slot")
        if slot.index <= previous:
            fail(ErrorCode.INVALID_ORDER, "rows are not in governed grid order")
        previous = slot.index
        rows[slot.index] = row
    present = frozenset(columns)
    by_name = {f"slot:{s.index}": s for s in slots}
    facts = [CloseFact(s) for s in slots]
    declared_observed = 0
    all_complete = True
    covered: set[int] = set()
    for interval in meta.interval_coverage:
        slot_or_none = by_name.get(interval.name)
        if slot_or_none is None or (interval.start_ns, interval.end_ns) != (slot_or_none.start_ns, slot_or_none.end_ns):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "coverage entry differs from the exact governed slot")
        covered.add(slot_or_none.index)
        coverage = interval.coverage
        if coverage.observed > 1 or (coverage.expected is not None and coverage.expected > 1):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "per-slot coverage cannot exceed one observation")
        row_index = rows.get(slot_or_none.index)
        if coverage.observed != int(row_index is not None):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "per-slot observed coverage contradicts the row")
        declared_observed += coverage.observed
        all_complete = all_complete and coverage.complete
        close = None if row_index is None or "close" not in columns else cast(int | None, columns["close"][row_index])
        known = (None if row_index is None or "known_at_ns" not in columns
                 else cast(int | None, columns["known_at_ns"][row_index]))
        facts[slot_or_none.index] = CloseFact(slot_or_none, coverage, present, meta.source.input_id, row_index,
                                              close, known)
    if not set(rows) <= covered:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "every supplied row needs exact per-slot coverage")
    if declared_observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "entry counts contradict actual delivery")
    if meta.coverage.complete and not all_complete:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "complete aggregate contradicts incomplete slot coverage")
    return RoleAdmission(tuple(facts), InputBinding(role, DataKind.BAR, meta), True)


def slot_reasons(fact: CloseFact, knowledge_cutoff_ns: int) -> frozenset[Reason]:
    """Causes that make one slot not READY (empty when READY); knowledge uses the original known_at in every mode."""
    if fact.row_index is None:
        # No row: no coverage is an absent slot, declared coverage without the row is a governed gap.
        return frozenset({Reason.ABSENT_INPUT if fact.coverage is None else Reason.GOVERNED_GAP})
    reasons: set[Reason] = set()
    if fact.known_at_ns is None:
        reasons.add(Reason.UNKNOWN_AVAILABILITY)
    elif fact.known_at_ns > knowledge_cutoff_ns:
        reasons.add(Reason.FUTURE_KNOWLEDGE)
    coverage = fact.coverage
    if coverage is None or not coverage.complete or coverage.expected != 1 or coverage.observed != 1:
        reasons.add(Reason.GOVERNED_GAP)
    if "close" not in fact.columns:
        reasons.add(Reason.ABSENT_INPUT)
    elif fact.close is None:
        reasons.add(Reason.NULL_FIELD)
    return frozenset(reasons)
