"""Pure EF4 bar projections (ef4-proj1): epoch-to-date up/down volume and actual dollar volume of one instrument.

A positive-volume bar is up when close > open, down when close < open and flat otherwise (flat volume is in the
denominators only); a proven-empty zero-volume bar is a READY observation contributing 0. Dollar volume is the
supplied actual notional only, never close * volume. Exact integer sums, one correctly rounded float64 per published
fraction; a published int64 or decimal128 sum outside its range is `OVERFLOW`. No clock, I/O, storage or default.

The reset-epoch bar delivery is described by a `BarGrid` (a local codec in the manner of the EF3 daily grid): one
instrument, one reset-epoch session, a fixed bar duration and the governed bar slots with a target slot index.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass
from fractions import Fraction
import hashlib
import json
from typing import cast

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, Coverage, DataKind, EntityKey, ErrorCode,
    EvidenceRow, FeatureResult, InputBinding, Parameter, PriceUnit, Reason, SessionSpec, ValueType, WindowSpec,
    validate_batch,
)
from ..ef3._common import fail, integer, label
from ._proj_common import (
    DEC128_LIMIT, I64_MAX, Cell, check_features, check_meta, check_unit_basis, check_policy, finish, fraction_float,
    knowledge_reason,
)

BAR_GRID_SCHEMA = "equity-features.ef4-bar-grid.v1"
MAX_BARS = 8192
BAR_IDENTITY = "ef4.bar_projection"
BAR_ALGORITHM = "ef4-bar-projection-v1"
# The label names the whole convention set (close versus open direction, flat in the denominators only, empty bars
# contribute 0, actual notional only, epoch-to-date strict population); another convention is another label.
BAR_POLICY = "ef4-proj1"
UP_VOLUME = "projection.up_volume"
DOWN_VOLUME = "projection.down_volume"
UP_VOLUME_FRACTION = "projection.up_volume_fraction"
UP_DOLLAR_VOLUME = "projection.up_dollar_volume"
DOWN_DOLLAR_VOLUME = "projection.down_dollar_volume"
UP_DOLLAR_FRACTION = "projection.up_dollar_volume_fraction"
BAR_FEATURES = (DOWN_DOLLAR_VOLUME, DOWN_VOLUME, UP_DOLLAR_VOLUME, UP_DOLLAR_FRACTION, UP_VOLUME,
                UP_VOLUME_FRACTION)
BAR_META: dict[str, tuple[ValueType, str]] = {
    UP_VOLUME: (ValueType.INT64, "shares"), DOWN_VOLUME: (ValueType.INT64, "shares"),
    UP_VOLUME_FRACTION: (ValueType.FLOAT64, "fraction"), UP_DOLLAR_VOLUME: (ValueType.DECIMAL128, "currency"),
    DOWN_DOLLAR_VOLUME: (ValueType.DECIMAL128, "currency"), UP_DOLLAR_FRACTION: (ValueType.FLOAT64, "fraction"),
}
_DOLLAR = frozenset({UP_DOLLAR_VOLUME, DOWN_DOLLAR_VOLUME, UP_DOLLAR_FRACTION})
_KEYS = frozenset({"policy_version", "evidence_limit"})


@dataclass(frozen=True)
class BarSlot:
    index: int
    start_ns: int
    end_ns: int


@dataclass(frozen=True)
class BarGrid:
    """Governed bar slots of one reset epoch: slot i is `[open + i * bar_ns, open + (i + 1) * bar_ns)`."""

    instrument_id: str
    calendar_id: str
    grid_id: str
    revision: str
    session: SessionSpec
    bar_ns: int
    bar_count: int
    target_index: int

    def __post_init__(self) -> None:
        for value in (self.instrument_id, self.calendar_id, self.grid_id, self.revision):
            label(value)
        if type(self.session) is not SessionSpec:
            fail(ErrorCode.INVALID_CONFIG, "a concrete reset-epoch session is required")
        label(self.session.namespace)
        label(self.session.session_id)
        integer(self.bar_ns, 1, 2**62)
        integer(self.bar_count, 1, MAX_BARS)
        integer(self.target_index, 0, self.bar_count - 1)
        if self.session.open_ns + self.bar_count * self.bar_ns > self.session.close_ns:
            fail(ErrorCode.BOUNDS, "the governed bar slots exceed the reset-epoch session")

    def slots(self) -> tuple[BarSlot, ...]:
        open_ns = self.session.open_ns
        return tuple(BarSlot(i, open_ns + i * self.bar_ns, open_ns + (i + 1) * self.bar_ns)
                     for i in range(self.bar_count))

    def to_json(self) -> str:
        return json.dumps({"schema": BAR_GRID_SCHEMA, **asdict(self)}, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False)

    @property
    def digest(self) -> str:
        return hashlib.sha256(self.to_json().encode("ascii")).hexdigest()

    @property
    def target(self) -> BarSlot:
        return self.slots()[self.target_index]


@dataclass(frozen=True)
class BarProjectionSettings:
    policy_version: str
    evidence_limit: int


def _check(policy: object, limit: object, defer_version: bool = False) -> BarProjectionSettings:
    evidence_limit = integer(limit, 0, 10000)
    if not (defer_version and type(policy) is str):
        check_policy(policy, BAR_POLICY)
    assert type(policy) is str
    return BarProjectionSettings(policy, evidence_limit)


def build_bar_projection_config(grid: BarGrid, *, policy_version: str | None = None,
                                availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit,
                                evidence_limit: int | None = None) -> ConfigSpec:
    """Final ConfigSpec: the reset-epoch session, the whole bar grid and an explicit unit and adjustment."""
    if type(grid) is not BarGrid:
        fail(ErrorCode.INVALID_CONFIG, "concrete bar grid required")
    settings = _check(policy_version, evidence_limit)
    if (type(availability) is not AvailabilitySpec or type(adjustment) is not AdjustmentSpec):
        fail(ErrorCode.INVALID_CONFIG, "concrete timing/action required")
    if type(price_unit) is not PriceUnit:
        fail(ErrorCode.INVALID_UNIT, "an explicit PriceUnit is required")
    for value in (adjustment.policy_version, adjustment.action_snapshot, adjustment.anchor, price_unit.currency):
        label(value)
    if availability.reconstruction_reason is not None:
        label(availability.reconstruction_reason)
    if not grid.target.end_ns <= availability.market_cutoff_ns <= grid.session.close_ns:
        fail(ErrorCode.BOUNDS, "market cutoff must follow the completed target bar")
    params = (Parameter("policy_version", settings.policy_version),
              Parameter("evidence_limit", settings.evidence_limit),
              Parameter("grid_schema", BAR_GRID_SCHEMA), Parameter("grid_sha256", grid.digest))
    session = grid.session
    return ConfigSpec(BAR_IDENTITY, BAR_ALGORITHM, params, session,
                      WindowSpec(grid.bar_count, session.session_id, (session.session_id,), "completed_eod"),
                      availability, adjustment, price_unit)


def decode_bar_projection_config(grid: BarGrid, config: ConfigSpec, *,
                                 defer_version: bool = False) -> BarProjectionSettings:
    """Validate the closed bar-projection envelope against the supplied grid and return its settings."""
    if type(grid) is not BarGrid or type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete bar grid/config required")
    if config.algorithm_version != BAR_ALGORITHM:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "algorithm version differs")
    if config.identity != BAR_IDENTITY:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "not this producer's configuration")
    values: dict[str, object] = {p.name: p.value for p in config.parameters}
    if set(values) != _KEYS | {"grid_schema", "grid_sha256"}:
        fail(ErrorCode.INVALID_CONFIG, "closed producer parameters required (there are no defaults)")
    if config.price_unit is None:
        fail(ErrorCode.INVALID_UNIT, "an explicit PriceUnit is required")
    settings = _check(values["policy_version"], values["evidence_limit"], defer_version)
    if defer_version and settings.policy_version != BAR_POLICY:
        return settings
    if values["grid_schema"] != BAR_GRID_SCHEMA:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "bar grid codec mismatch")
    if values["grid_sha256"] != grid.digest:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "bar grid identity differs")
    expected = build_bar_projection_config(
        grid, policy_version=settings.policy_version, availability=config.availability,
        adjustment=config.adjustment, price_unit=config.price_unit, evidence_limit=settings.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical bar-projection envelope")
    return settings


@dataclass(frozen=True)
class BarFact:
    """Per-slot supplied bar; `row_index is None` means no row for the slot."""

    slot: BarSlot
    coverage: Coverage | None = None
    columns: frozenset[str] = frozenset()
    input_id: str | None = None
    row_index: int | None = None
    open_px: int | None = None
    close: int | None = None
    volume: int | None = None
    notional: int | None = None
    known_at_ns: int | None = None


@dataclass(frozen=True)
class BarAdmission:
    facts: tuple[BarFact, ...]
    binding: InputBinding | None
    present: bool
    columns: frozenset[str]


def admit_bars(batch: CanonicalBatch | None, grid: BarGrid, config: ConfigSpec) -> BarAdmission:
    """Structural admission of the `bars` role on the governed bar grid; every contradiction refuses."""
    slots = grid.slots()
    if batch is None:
        return BarAdmission(tuple(BarFact(s) for s in slots), None, False, frozenset())
    if type(batch) is not CanonicalBatch or batch.kind != DataKind.BAR:
        fail(ErrorCode.INVALID_SCHEMA, "an actual BAR batch is required for the bars role")
    validate_batch(batch, availability=config.availability, required_fields=())
    if batch.row_count > len(slots) or len(batch.metadata.interval_coverage) > len(slots):
        fail(ErrorCode.BOUNDS, "delivery exceeds governed slot bound")
    meta = batch.metadata
    check_meta(batch, config, unit=True, adjustment=True)
    if meta.namespace != grid.session.namespace:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "input namespace differs from the grid")
    scope = meta.scope
    if scope is None or meta.sampling != "none":
        fail(ErrorCode.INVALID_SCHEMA, "explicit BAR scope and nonquote sampling required")
    if scope.start_ns < slots[0].start_ns or scope.end_ns > slots[-1].end_ns:
        fail(ErrorCode.BOUNDS, "input scope outside the governed grid")
    columns = {c.name: c.values for c in batch.columns}
    lookup = {(grid.session.session_id, s.start_ns, s.end_ns): s for s in slots}
    market_cutoff = config.availability.market_cutoff_ns
    rows: dict[int, int] = {}
    previous = -1
    for row in range(batch.row_count):
        if columns["instrument_id"][row] != grid.instrument_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "row instrument differs from the role instrument")
        start, end = cast(int, columns["start_ns"][row]), cast(int, columns["end_ns"][row])
        if end > market_cutoff:
            fail(ErrorCode.BOUNDS, "forming/future supplied bar")
        slot = lookup.get((cast(str, columns["session_id"][row]), start, end))
        if slot is None:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "row not on the governed bar grid")
        if not scope.start_ns <= start < end <= scope.end_ns:
            fail(ErrorCode.BOUNDS, "row outside its own input scope")
        if slot.index in rows:
            fail(ErrorCode.DUPLICATE, "duplicate governed slot")
        if slot.index <= previous:
            fail(ErrorCode.INVALID_ORDER, "rows are not in governed grid order")
        previous = slot.index
        rows[slot.index] = row
    present = frozenset(columns)
    by_name = {f"bar:{s.index}": s for s in slots}
    facts = [BarFact(s) for s in slots]
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
        if row_index is None:
            facts[slot_or_none.index] = BarFact(slot_or_none, coverage, present, meta.source.input_id)
            continue

        bound_index: int = row_index

        def cell(name: str, index: int = bound_index) -> int | None:
            return cast("int | None", columns[name][index]) if name in columns else None
        facts[slot_or_none.index] = BarFact(
            slot_or_none, coverage, present, meta.source.input_id, row_index, cell("open"), cell("close"),
            cell("volume"), cell("actual_notional"), cell("known_at_ns"))
    if not set(rows) <= covered:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "every supplied row needs exact per-slot coverage")
    if declared_observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "entry counts contradict actual delivery")
    if meta.coverage.complete and not all_complete:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "complete aggregate contradicts incomplete slot coverage")
    return BarAdmission(tuple(facts), InputBinding("bars", DataKind.BAR, meta), True, present)


def _bar_reasons(fact: BarFact, knowledge: int, money: bool) -> frozenset[Reason]:
    """Causes that make one bar not READY for the volume (or dollar) family; empty when READY."""
    if fact.row_index is None:
        return frozenset({Reason.ABSENT_INPUT if fact.coverage is None else Reason.GOVERNED_GAP})
    reasons: set[Reason] = set()
    cause = knowledge_reason(fact.known_at_ns, knowledge)
    if cause is not None:
        reasons.add(cause)
    coverage = fact.coverage
    if coverage is None or not coverage.complete or coverage.expected != 1 or coverage.observed != 1:
        reasons.add(Reason.GOVERNED_GAP)
    if "volume" not in fact.columns:
        reasons.add(Reason.ABSENT_INPUT)
    elif fact.volume is None:
        reasons.add(Reason.NULL_FIELD)
    elif fact.volume > 0:
        if "open" not in fact.columns or "close" not in fact.columns:
            reasons.add(Reason.ABSENT_INPUT)
        elif fact.open_px is None or fact.close is None:
            reasons.add(Reason.NULL_FIELD)
        if money and fact.notional is None:
            reasons.add(Reason.NULL_FIELD)
    return frozenset(reasons)


def compute_bar_projection(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                           grid: BarGrid, config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef4-proj1 bar outputs; `batches` is the fixed single nullable role (bars)."""
    if type(batches) not in (tuple, list) or len(batches) != 1:
        fail(ErrorCode.INVALID_SCHEMA, "the fixed single role (bars) is required")
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    batch = batches[0]
    if batch is not None:
        if type(batch) is not CanonicalBatch:
            fail(ErrorCode.INVALID_SCHEMA, "an actual BAR batch is required for the bars role")
        validate_batch(batch, availability=config.availability, required_fields=())  # shared tier first
        if batch.kind != DataKind.BAR:
            fail(ErrorCode.INVALID_SCHEMA, "an actual BAR batch is required for the bars role")
    settings = decode_bar_projection_config(grid, config, defer_version=True)
    selected = check_features(features, BAR_FEATURES)
    check_unit_basis(batch, config)
    check_policy(settings.policy_version, BAR_POLICY)
    bars = admit_bars(batch, grid, config)
    t = grid.target_index
    entity = EntityKey(grid.instrument_id, config.session.session_id)
    knowledge = config.availability.knowledge_cutoff_ns
    cells: dict[str, Cell] = {}
    for feature in selected:
        money = feature in _DOLLAR
        reasons: set[Reason] = set()
        ready: list[int] = []
        if not bars.present or (money and "actual_notional" not in bars.columns):
            reasons.add(Reason.ABSENT_INPUT)
        else:
            for i in range(t + 1):
                causes = _bar_reasons(bars.facts[i], knowledge, money)
                reasons.update(causes)
                if not causes:
                    ready.append(i)
        cell = Cell(None, reasons, t + 1, len(ready))
        cells[feature] = cell
        if reasons:
            continue
        total_volume = total_notional = up_volume = down_volume = up_notional = down_notional = 0
        for i in ready:
            fact = bars.facts[i]
            volume = cast(int, fact.volume)
            notional = fact.notional or 0
            total_volume += volume
            total_notional += notional
            if volume > 0 and cast(int, fact.close) > cast(int, fact.open_px):
                up_volume += volume
                up_notional += notional
            elif volume > 0 and cast(int, fact.close) < cast(int, fact.open_px):
                down_volume += volume
                down_notional += notional
        value: int | float
        if feature in (UP_VOLUME, DOWN_VOLUME):
            value = up_volume if feature == UP_VOLUME else down_volume
            if value > I64_MAX:
                fail(ErrorCode.OVERFLOW, "published volume sum outside int64")
        elif feature in (UP_DOLLAR_VOLUME, DOWN_DOLLAR_VOLUME):
            value = up_notional if feature == UP_DOLLAR_VOLUME else down_notional
            if value >= DEC128_LIMIT:
                fail(ErrorCode.OVERFLOW, "published dollar volume outside decimal128")
        elif feature == UP_VOLUME_FRACTION:
            if total_volume == 0:
                reasons.add(Reason.ZERO_DENOMINATOR)
                continue
            value = fraction_float(Fraction(up_volume, total_volume))
        else:
            if total_notional == 0:
                reasons.add(Reason.ZERO_DENOMINATOR)
                continue
            value = fraction_float(Fraction(up_notional, total_notional))
        cell.value = value
        cell.witnesses = []
        for i in [t] + list(range(t)):
            fact = bars.facts[i]
            assert fact.input_id is not None
            cell.witnesses.append(EvidenceRow(
                entity, feature, fact.input_id, f"bar:{i}", fact.slot.end_ns, fact.known_at_ns, fact.slot.start_ns,
                fact.slot.end_ns, "consumed", None, "completed_interval"))
    bindings = () if bars.binding is None else (bars.binding,)
    return finish(config, entity, BAR_ALGORITHM, selected, BAR_META, cells, bindings, settings.evidence_limit)
