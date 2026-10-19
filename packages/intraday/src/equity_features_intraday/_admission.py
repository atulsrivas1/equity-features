"""Supplied BAR admission; per-slot facts preserve independent field readiness."""
from __future__ import annotations

from bisect import bisect_left, bisect_right
from dataclasses import dataclass
from typing import cast

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, Coverage, DataKind, ErrorCode, InputBinding,
    Reason, SessionSpec, validate_batch,
)
from ._context import IntradayContext, Slot, fail, label


@dataclass(frozen=True)
class SlotFacts:
    slot: Slot
    coverage: Coverage | None = None
    columns: frozenset[str] = frozenset()
    input_id: str | None = None
    row_index: int | None = None
    close: int | None = None
    high: int | None = None
    low: int | None = None
    known_at_ns: int | None = None
    knowledge_reason: Reason | None = None
    empty: bool = False


@dataclass(frozen=True)
class Admitted:
    facts: tuple[SlotFacts, ...]
    inputs: tuple[InputBinding, ...]
    observed_empty_delivery: bool


def validate_envelopes(batches: tuple[CanonicalBatch, ...], context: IntradayContext,
                       config: ConfigSpec, slot_count: int) -> tuple[SessionSpec, ...]:
    """Finish every chunk's limits/unit/identity phase before payload semantics."""
    seen_ids: set[str] = set()
    source_identity: tuple[str, str, str] | None = None
    policy: str | None = None
    governed: list[SessionSpec] = []
    for batch in batches:
        if batch.kind != DataKind.BAR:
            fail("intraday requires actual BAR inputs", ErrorCode.INVALID_SCHEMA)
        if batch.row_count > slot_count or len(batch.metadata.interval_coverage) > slot_count:
            fail("delivery exceeds governed slot bound", ErrorCode.BOUNDS)
        meta = batch.metadata
        if meta.namespace != context.sessions[0].namespace:
            fail("input namespace differs", ErrorCode.INCONSISTENT_IDENTITY)
        if meta.price_unit != config.price_unit:
            fail("input currency/scale differs", ErrorCode.INVALID_UNIT)
        if meta.adjustment != config.adjustment:
            fail("input action basis differs", ErrorCode.UNSUPPORTED_ADJUSTMENT)
        for value in (meta.source.source_id, meta.source.snapshot_id,
                      meta.source.mapping_version, meta.source.input_id):
            label(value)
        identity = (meta.source.source_id, meta.source.snapshot_id, meta.source.mapping_version)
        if source_identity is not None and source_identity != identity:
            fail("chunks need compatible source/snapshot/mapping", ErrorCode.INCONSISTENT_IDENTITY)
        source_identity = identity
        if meta.source.input_id in seen_ids:
            fail("input IDs must distinguish original chunks", ErrorCode.DUPLICATE)
        seen_ids.add(meta.source.input_id)
        scope = meta.scope
        if scope is None or meta.sampling != "none":
            fail("explicit BAR scope and nonquote sampling required")
        label(scope.eligibility_policy)
        if policy is not None and scope.eligibility_policy != policy:
            fail("chunk eligibility policy differs", ErrorCode.INCONSISTENT_IDENTITY)
        policy = scope.eligibility_policy
        sessions = [s for s in context.sessions
                    if s.open_ns <= scope.start_ns < scope.end_ns <= s.close_ns]
        if len(sessions) != 1:
            fail("chunk scope must belong to one actual session", ErrorCode.BOUNDS)
        session = sessions[0]
        if (scope.include_opening_auction, scope.include_closing_auction) != (
                session.include_opening_auction, session.include_closing_auction):
            fail("scope/session auction policy differs", ErrorCode.INCONSISTENT_IDENTITY)
        governed.append(session)
    return tuple(governed)


def admit(batches: tuple[CanonicalBatch, ...], context: IntradayContext,
          config: ConfigSpec) -> Admitted:
    if type(batches) is not tuple:
        fail("concrete owned canonical tuple required", ErrorCode.INVALID_SCHEMA)
    if len(batches) > 4096:
        fail("at most 4096 input chunks supported", ErrorCode.BOUNDS)
    if any(type(b) is not CanonicalBatch for b in batches):
        fail("concrete canonical chunks required", ErrorCode.INVALID_SCHEMA)
    slots = context.slots()
    facts = [SlotFacts(s) for s in slots]
    lookup = {(s.session_id, s.start_ns, s.end_ns): s for s in slots}
    by_name = {f"slot:{s.index}": s for s in slots}
    session_slots: dict[str, list[Slot]] = {}
    for governed_slot in slots:
        session_slots.setdefault(governed_slot.session_id, []).append(governed_slot)
    starts = {key: tuple(s.start_ns for s in group) for key, group in session_slots.items()}
    ends = {key: tuple(s.end_ns for s in group) for key, group in session_slots.items()}
    inputs: list[InputBinding] = []
    seen_rows: set[int] = set()
    seen_coverage: set[int] = set()
    previous_scope_end: int | None = None
    previous_row = -1
    empty_delivery = not batches
    if batches:
        empty_delivery = all(b.row_count == 0 and b.metadata.coverage.complete
                             and b.metadata.coverage.expected == 0 for b in batches)
    governed = validate_envelopes(batches, context, config, len(slots))
    for batch in batches:
        validate_batch(batch, required_fields=())
    for chunk, batch in enumerate(batches):
        meta = batch.metadata
        scope = meta.scope
        if scope is None:
            fail("validated scope missing", ErrorCode.INCONSISTENT_IDENTITY)
        session = governed[chunk]
        if meta.coverage.observed != batch.row_count:
            fail("aggregate observed coverage differs from actual rows", ErrorCode.INCONSISTENT_IDENTITY)
        columns = {c.name: c.values for c in batch.columns}
        present = frozenset(columns)
        rows: dict[int, int] = {}
        def number(name: str, row: int) -> int | None:
            column = columns.get(name)
            return None if column is None else cast(int | None, column[row])
        for row in range(batch.row_count):
            if (columns["instrument_id"][row] != context.instrument_id
                    or columns["session_id"][row] != session.session_id):
                fail("row instrument/session differs", ErrorCode.INCONSISTENT_IDENTITY)
            start, end = cast(int, number("start_ns", row)), cast(int, number("end_ns", row))
            if end > config.availability.market_cutoff_ns:
                fail("forming/future supplied bar", ErrorCode.BOUNDS)
            slot = lookup.get((session.session_id, start, end))
            if slot is None:
                fail("row not on governed grid", ErrorCode.INCONSISTENT_IDENTITY)
            if not scope.start_ns <= start < end <= scope.end_ns:
                fail("row outside its own chunk scope", ErrorCode.BOUNDS)
            if slot.index in seen_rows:
                fail("duplicate slot across chunks", ErrorCode.DUPLICATE)
            if slot.index <= previous_row:
                fail("chunks/rows are unordered", ErrorCode.INVALID_ORDER)
            previous_row = slot.index
            seen_rows.add(slot.index)
            rows[slot.index] = row
        declared_observed = 0
        declared_expected = 0
        all_expected_known = True
        all_complete = True
        local_coverage: set[int] = set()
        for interval in meta.interval_coverage:
            slot = by_name.get(interval.name)
            if slot is None or (interval.start_ns, interval.end_ns) != (slot.start_ns, slot.end_ns):
                fail("coverage entry differs from exact governed slot", ErrorCode.INCONSISTENT_IDENTITY)
            if slot.session_id != session.session_id:
                fail("coverage belongs to another session", ErrorCode.INCONSISTENT_IDENTITY)
            if slot.index in seen_coverage:
                fail("duplicate coverage ownership across chunks", ErrorCode.DUPLICATE)
            seen_coverage.add(slot.index)
            local_coverage.add(slot.index)
            coverage = interval.coverage
            if coverage.observed > 1 or (coverage.expected is not None and coverage.expected > 1):
                fail("per-slot coverage cannot exceed one observation", ErrorCode.INCONSISTENT_IDENTITY)
            row_index = rows.get(slot.index)
            if coverage.observed != int(row_index is not None):
                fail("per-slot observed coverage contradicts row", ErrorCode.INCONSISTENT_IDENTITY)
            declared_observed += coverage.observed
            if coverage.expected is None:
                all_expected_known = False
            else:
                declared_expected += coverage.expected
            all_complete = all_complete and coverage.complete
            empty = coverage.expected == 0 and coverage.complete
            known = None if row_index is None else number("known_at_ns", row_index)
            knowledge = None if row_index is None else config.availability.knowledge_reason(known)
            facts[slot.index] = SlotFacts(
                slot, coverage, present, meta.source.input_id, row_index,
                None if row_index is None else number("close", row_index),
                None if row_index is None else number("high", row_index),
                None if row_index is None else number("low", row_index), known,
                None if knowledge is None else Reason(knowledge),
                empty or (row_index is not None and number("volume", row_index) == 0),
            )
        if not set(rows) <= local_coverage:
            fail("every supplied row needs exact per-slot coverage", ErrorCode.INCONSISTENT_IDENTITY)
        if declared_observed != batch.row_count:
            fail("entry counts contradict actual delivery", ErrorCode.INCONSISTENT_IDENTITY)
        if meta.coverage.expected is not None and meta.coverage.expected < declared_expected:
            fail("aggregate expected below declared slot coverage", ErrorCode.INCONSISTENT_IDENTITY)
        left = bisect_left(starts[session.session_id], scope.start_ns)
        right = bisect_right(ends[session.session_id], scope.end_ns)
        scope_slots = {s.index for s in session_slots[session.session_id][left:right]}
        if meta.coverage.complete and not all_complete:
            fail("complete aggregate contradicts incomplete slot coverage", ErrorCode.INCONSISTENT_IDENTITY)
        if (all_expected_known and local_coverage == scope_slots and meta.coverage.expected is not None
                and meta.coverage.expected != declared_expected):
            fail("aggregate/declared expected counts differ", ErrorCode.INCONSISTENT_IDENTITY)
        if previous_scope_end is not None and scope.start_ns < previous_scope_end:
            fail("chunk scopes overlap or are unordered", ErrorCode.INVALID_ORDER)
        previous_scope_end = scope.end_ns
        inputs.append(InputBinding(f"bars:{chunk:03}", DataKind.BAR, meta))
    return Admitted(tuple(facts), tuple(inputs), empty_delivery)
