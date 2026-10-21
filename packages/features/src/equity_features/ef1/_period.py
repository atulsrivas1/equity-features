"""Pure bounded civil-period and supplied extended-phase interval aggregates."""
from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction
from typing import Any, cast

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow,
    FeatureColumn, FeatureResult, InputBinding, PriceUnit, QualityRow, Reason,
    ResultMetadata, Status, checked_decimal128, checked_int64, validate_batch,
)
from equity_features import __version__
from ._anchor import _columns, _ready, _reasons
from ._clock import _calendar_ready
from ._context import decode_ef1_context, fail, label
from ._definitions import ef1_definitions
from ._path import _causal, _witness

Columns = dict[str, tuple[Any, ...]]
Row = tuple[CanonicalBatch, Columns, int]
Slot = tuple[Any, ...]


def _structural(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey) -> Columns:
    """Validate every supplied field, including numerically unused DAILY fields."""
    meta = batch.metadata
    if meta.namespace != config.session.namespace or meta.coverage.observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "actual namespace/population binding mismatch")
    if meta.ordering != "declared" or meta.duplicate_policy != "reject":
        fail(ErrorCode.INVALID_ORDER, "ordered unique original canonical population required")
    for text in (meta.namespace, meta.source.source_id, meta.source.snapshot_id,
                 meta.source.mapping_version, meta.source.input_id):
        label(text)
    for interval in meta.interval_coverage:
        label(interval.name)
    for column in batch.columns:
        for value in column.values:
            if type(value) is str:
                label(value)
    columns = _columns(batch)
    if any(value != entity.instrument_id for value in columns["instrument_id"]):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "one requested instrument required")
    # No regular-session argument: extended BAR timestamps legitimately lie
    # outside regular trading hours; DAILY rows legitimately span prior slots.
    validate_batch(batch, required_fields=())
    if batch.kind in (DataKind.BAR, DataKind.DAILY):
        if meta.price_unit != config.price_unit:
            fail(ErrorCode.INVALID_UNIT, "period/phase market PriceUnit mismatch")
        if meta.adjustment != config.adjustment:
            fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "period/phase adjustment mismatch")
    return columns


def _scope(batch: CanonicalBatch, config: ConfigSpec, start: int, end: int,
           policy: str) -> None:
    scope = batch.metadata.scope
    if scope is None or (scope.start_ns, scope.end_ns, scope.eligibility_policy,
            scope.include_opening_auction, scope.include_closing_auction) != (
            start, end, policy, config.session.include_opening_auction,
            config.session.include_closing_auction):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact governed scope and auction construction required")


def _daily(batch: CanonicalBatch, columns: Columns, slots: tuple[Slot, ...],
           config: ConfigSpec, policy: str) -> tuple[Reason, ...]:
    if not slots:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "DAILY role forbidden without required governed slots")
    # Bounds precede population declaration checks: an extra target/future row
    # cannot become an apparently incomplete historical population.
    required = {row[0]: row for row in slots}
    delivered: set[str] = set()
    for i in range(batch.row_count):
        identity = columns["session_id"][i]
        if identity not in required:
            fail(ErrorCode.BOUNDS, "DAILY row outside required governed session slots")
        slot = required[identity]
        if (columns["start_ns"][i], columns["end_ns"][i]) != (slot[2], slot[3]):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "DAILY original interval differs from governed slot")
        if columns["end_ns"][i] > config.availability.market_cutoff_ns:
            fail(ErrorCode.BOUNDS, "forming/future DAILY row exceeds cutoff")
        delivered.add(identity)
    _scope(batch, config, slots[0][2], slots[-1][3], policy)
    whole = batch.metadata.coverage
    if whole.expected != len(slots):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "DAILY expected population must equal required slot count")
    intervals = batch.metadata.interval_coverage
    if len(intervals) != len(slots):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "every required DAILY slot needs exact interval coverage")
    complete = whole.complete
    for interval, slot in zip(intervals, slots):
        count = int(slot[0] in delivered)
        if (interval.name, interval.start_ns, interval.end_ns,
                interval.coverage.expected, interval.coverage.observed) != (slot[0], slot[2], slot[3], 1, count):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "DAILY interval coverage contradicts actual required slot")
        if whole.complete and not interval.coverage.complete:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "complete DAILY declaration contradicts incomplete slot")
        complete = complete and interval.coverage.complete
    return () if complete else (Reason.GOVERNED_GAP,)


def _bars(batch: CanonicalBatch, columns: Columns, config: ConfigSpec,
          start: int, end: int, policy: str, interval_name: str) -> tuple[Reason, ...]:
    for i in range(batch.row_count):
        if columns["session_id"][i] != config.session.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "BAR must belong to exact target session")
        if columns["start_ns"][i] < start or columns["end_ns"][i] > end:
            fail(ErrorCode.BOUNDS, "BAR straddles exact completed governed prefix")
    _scope(batch, config, start, end, policy)
    intervals = batch.metadata.interval_coverage
    if len(intervals) != 1 or (intervals[0].name, intervals[0].start_ns, intervals[0].end_ns,
            intervals[0].coverage) != (interval_name, start, end, batch.metadata.coverage):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "BAR prefix interval and whole coverage must agree exactly")
    coverage = batch.metadata.coverage
    if coverage.expected is not None:
        checked_int64(coverage.expected)
    return () if coverage.complete else (Reason.GOVERNED_GAP,)


def _cell(row: Row, field: str) -> Any:
    _, columns, index = row
    return columns[field][index] if field in columns else None


def _missing(row: Row, field: str) -> tuple[Reason, ...]:
    return (Reason.NULL_FIELD if field in row[1] else Reason.ABSENT_INPUT,)


def _aggregate(rows: list[Row], common: tuple[Reason, ...]) -> tuple[
        dict[str, int], dict[str, tuple[Reason, ...]], dict[str, list[Row]], bool]:
    """Independent fields share delivery/knowledge, never inferred operands."""
    reasons = {name: common for name in ("open", "high", "low", "close", "volume", "notional")}
    values: dict[str, int] = {"volume": 0, "notional": 0}
    witnesses: dict[str, list[Row]] = {}
    price_rows: list[Row] = []
    for row in rows:
        quantity = _cell(row, "volume")
        if quantity is None:
            for name in ("open", "high", "low", "close", "volume"):
                reasons[name] = _reasons(reasons[name], _missing(row, "volume"))
        else:
            values["volume"] += quantity
            if quantity > 0:
                price_rows.append(row)
        if quantity != 0:
            amount = _cell(row, "actual_notional")
            if amount is None:
                reasons["notional"] = _reasons(reasons["notional"], _missing(row, "actual_notional"))
            else:
                values["notional"] += amount
    # Checked arithmetic is structural and cannot be hidden by missing proof.
    checked_int64(values["volume"])
    checked_decimal128(values["notional"])
    for name in ("open", "high", "low", "close"):
        required_rows = (price_rows[:1] if name == "open" else price_rows[-1:] if name == "close" else price_rows)
        for row in required_rows:
            if _cell(row, name) is None:
                reasons[name] = _reasons(reasons[name], _missing(row, name))
        usable = [row for row in required_rows if _cell(row, name) is not None]
        if usable:
            selected = (usable[0] if name == "open" else usable[-1] if name == "close" else
                        max(usable, key=lambda row: _cell(row, name)) if name == "high" else
                        min(usable, key=lambda row: _cell(row, name)))
            values[name] = _cell(selected, name)
            witnesses[name] = [selected]
    # Proved no-price depends on complete, causal delivered population and
    # known volume, not optional OHLC fields on rows known to have zero volume.
    no_price = not price_rows and not reasons["volume"]
    return values, reasons, witnesses, no_price


def compute_period_phase(batches: tuple[CanonicalBatch, ...] | list[CanonicalBatch],
                         config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    context = decode_ef1_context(config)
    period = context["producer"] == "period"
    if context["producer"] not in ("period", "extended"):
        fail(ErrorCode.INVALID_CONFIG, "wrong period/phase producer")
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    label(entity.session_id)
    roles = ((DataKind.REFERENCE, "calendar_provenance"),
             (DataKind.DAILY, "daily_history"), (DataKind.BAR, "bars")) if period else (
             (DataKind.REFERENCE, "calendar_provenance"), (DataKind.BAR, "bars"), (DataKind.DAILY, "prior_close"))
    if type(batches) not in (tuple, list) or len(batches) > 3:
        fail(ErrorCode.INVALID_SCHEMA, "bounded concrete present-role subsequence required")
    selected: dict[str, CanonicalBatch] = {}
    columns: dict[str, Columns] = {}
    previous = -1
    for batch in batches:
        if type(batch) is not CanonicalBatch:
            fail(ErrorCode.INVALID_SCHEMA, "actual present CanonicalBatch required")
        position = next((i for i, (kind, _) in enumerate(roles) if batch.kind == kind), -1)
        if position < 0:
            fail(ErrorCode.UNSUPPORTED_CAPABILITY, "period/phase accepts supplied BAR/DAILY and calendar REFERENCE only")
        if position <= previous:
            fail(ErrorCode.INVALID_SCHEMA, "wrong/duplicate/reordered period/phase role")
        previous = position
        role = roles[position][1]
        selected[role] = batch
        columns[role] = _structural(batch, config, entity)
    if len({batch.metadata.source.input_id for batch in batches}) != len(batches):
        fail(ErrorCode.DUPLICATE, "distinct original input bindings required")
    calendar = context["calendar"]
    cutoff = config.availability.market_cutoff_ns
    bars = selected.get("bars")
    daily_role = "daily_history" if period else "prior_close"
    daily = selected.get(daily_role)
    coverage_reasons: tuple[Reason, ...] = ()
    rows: list[Row] = []
    before_phase = False
    if period:
        selection = context["selection"]
        members = tuple(row for row in calendar["sessions"]
                        if selection["start_date"] <= row[1] < selection["end_date_exclusive"])
        prior_complete = selection["inclusion"] == "prior_complete"
        daily_slots = members if prior_complete else tuple(row for row in members if row[1] < calendar["target_date"])
        bar_required = not prior_complete and any(row[0] == entity.session_id for row in members) and cutoff > config.session.open_ns
        start, end = config.session.open_ns, min(cutoff, config.session.close_ns)
    else:
        members = ()
        daily_slots = (calendar["sessions"][0],)
        _, start, phase_end = next(row for row in calendar["segments"] if row[0] == context["selection"]["phase"])
        end = min(cutoff, phase_end)
        bar_required = cutoff > start
        before_phase = cutoff < start
    policy = "supplied_period" if period else "supplied_phase"
    if bars is not None:
        if not bar_required:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "BAR role forbidden without a positive requested prefix")
        coverage_reasons = _bars(bars, columns["bars"], config, start, end, policy,
                                 "period_prefix" if period else "phase_prefix")
    elif bar_required:
        coverage_reasons = (Reason.ABSENT_INPUT,)
    if daily is not None:
        if not period and not bar_required:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "prior DAILY role forbidden at/before phase start")
        daily_coverage = _daily(daily, columns[daily_role], daily_slots, config, policy)
        if period:
            coverage_reasons = _reasons(coverage_reasons, daily_coverage)
    elif period and daily_slots:
        coverage_reasons = _reasons(coverage_reasons, (Reason.ABSENT_INPUT,))
    if period and daily is not None:
        rows.extend((daily, columns[daily_role], i) for i in range(daily.row_count))
    if bars is not None:
        rows.extend((bars, columns["bars"], i) for i in range(bars.row_count))
    for row in rows:
        coverage_reasons = _reasons(coverage_reasons, _causal(_cell(row, "known_at_ns"), config))
    _, calendar_reasons = _calendar_ready(selected.get("calendar_provenance"), config, context, entity)
    # Compute counts and arithmetic even when an unrelated readiness gate fails.
    bar_expected = (None if bars is None else bars.metadata.coverage.expected) if bar_required else 0
    expected = None if bar_expected is None else checked_int64(bar_expected + (len(daily_slots) if period else 0))
    observed = checked_int64(len(rows))
    values, field_reasons, witnesses, no_price = _aggregate(rows, _reasons(coverage_reasons, calendar_reasons))
    field_reasons["open_close_return"] = _reasons(field_reasons["open"], field_reasons["close"])
    if "open" in values and "close" in values:
        witnesses["open_close_return"] = witnesses["open"] + witnesses["close"]
    prior_expected, prior_observed = expected, observed
    if not period:
        # Only a complete causal no-price phase proves the denominator unused.
        unused_prior = not bar_required or no_price
        prior_reasons = field_reasons["close"]
        if not unused_prior:
            prior_expected = None if expected is None else checked_int64(expected + 1)
            prior_observed = checked_int64(observed + (daily.row_count if daily is not None else 0))
            if daily is None:
                prior_reasons = _reasons(prior_reasons, (Reason.ABSENT_INPUT,))
            else:
                prior_reasons = _reasons(prior_reasons, daily_coverage)
                if daily.row_count:
                    prior_row = (daily, columns[daily_role], 0)
                    prior_reasons = _reasons(prior_reasons, _causal(_cell(prior_row, "known_at_ns"), config))
                    prior_close = _cell(prior_row, "close")
                    if prior_close is None:
                        prior_reasons = _reasons(prior_reasons, _missing(prior_row, "close"))
                    else:
                        values["prior_close"] = prior_close
                        if "close" in witnesses:
                            witnesses["prior_close_return"] = witnesses["close"] + [prior_row]
                else:
                    prior_reasons = _reasons(prior_reasons, (Reason.ABSENT_INPUT,))
        field_reasons["prior_close_return"] = prior_reasons
    output: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: dict[tuple[str, str, str], EvidenceRow] = {}
    for definition in ef1_definitions(config):
        name = definition.feature_id.rsplit(".", 1)[1]
        value: int | float | None = None
        field_expected, field_observed = expected, observed
        if name in ("scheduled_sessions", "completed_sessions"):
            status, reasons = _ready(calendar_reasons)
            field_expected = len(members)
            field_observed = len(members) if status == Status.AVAILABLE else 0
            if status == Status.AVAILABLE:
                value = checked_int64(len(members) if name == "scheduled_sessions" else sum(row[3] <= cutoff for row in members))
        else:
            status, reasons = _ready(field_reasons[name])
            if name == "prior_close_return":
                field_expected, field_observed = prior_expected, prior_observed
            if status == Status.AVAILABLE:
                if not period and before_phase or name not in ("volume", "notional") and no_price:
                    status, reasons = Status.NOT_APPLICABLE, (Reason.NO_ELIGIBLE_OBSERVATIONS,)
                elif name in ("volume", "notional"):
                    value = values[name]
                elif name.endswith("return"):
                    denominator = values["open" if name == "open_close_return" else "prior_close"]
                    if denominator == 0:
                        status, reasons = Status.NOT_APPLICABLE, (Reason.ZERO_DENOMINATOR,)
                    else:
                        value = float(Fraction(values["close"] - denominator, denominator))
                else:
                    value = float(Fraction(values[name], 10 ** cast(PriceUnit, config.price_unit).scale))
        output.append(FeatureColumn(definition.feature_id, "v1", definition.dtype, definition.unit, (entity,), (value,)))
        quality.append(QualityRow(entity, definition.feature_id, status, field_expected, field_observed, reasons))
        if status == Status.AVAILABLE:
            for batch, _, index in witnesses.get(name, []):
                witness = _witness(batch, index, entity, definition.feature_id)
                evidence[(witness.feature_id, witness.input_id, witness.row_id)] = witness
    bindings = tuple(InputBinding(role, batch.kind, batch.metadata) for role, batch in selected.items())
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability,
        config.digest, bindings, "python-exact", __version__, evidence_limit=6 if period else 8)
    return FeatureResult(tuple(output), tuple(quality), metadata,
                         tuple(evidence[key] for key in sorted(evidence)))
