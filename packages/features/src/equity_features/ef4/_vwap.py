"""Pure EF4 anchored VWAP path (ef4-vwap1): cumulative VWAP, its extrema, change and two per-second slopes.

The path is the anchored cumulative VWAP `W_k = sum(N_i) / sum(V_i)` over the first k points of the declared interval
`[S, E)`, reset at the anchor S. A point is `(x, N, V)`: for the trade source each eligible trade `(event_ns, price size,
size)`; for the bar and prepared_window sources each positive-volume window `(end_ns, actual_notional, volume)` (never
close times volume). The time axis is UTC wall-clock nanoseconds; slopes are per second (the exact factor 10^9). The
endpoint slope is `(W_n - W_1) / (x_n - x_1)` and the OLS slope regresses `W_k` on `x_k` with equal point weights. Every
sum is exact; each published float64 is one correctly rounded rational. No state, default window or minimum.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, FeatureResult,
    Parameter, PriceUnit, Reason, SessionSpec, ValueType,
)
from ..ef3._common import fail, label
from ..ef3._robust_common import check_entity, columns_of
from ._common import (
    EDGE_KIND, PROOF_KIND, SEC, SOURCES, Interval, Out, Witness, admit_bounds, admit_facts, assemble, bindings_of,
    check_closed, check_kinds, check_limit, check_meta, check_roles, declared_coverage, knowledge_reason, make_config,
    parameter_values, shared_validation, unavailable,
)

VWAP_IDENTITY = "ef4.vwap_path"
VWAP_ALGORITHM = "ef4-vwap-path-v1"
# The label names the whole convention set (series source, anchor, operand, time axis, estimators, missingness mapping,
# zero-volume rule, rounding).
VWAP_POLICY = "ef4-vwap1"
PATH_CHANGE = "vwap.path.change_bps"
PATH_LAST = "vwap.path.last"
PATH_MAXIMUM = "vwap.path.maximum"
PATH_MINIMUM = "vwap.path.minimum"
POINT_COUNT = "vwap.path.point_count"
SLOPE_ENDPOINT = "vwap.slope.endpoint"
SLOPE_OLS = "vwap.slope.ols"
VWAP_FEATURES = (PATH_CHANGE, PATH_LAST, PATH_MAXIMUM, PATH_MINIMUM, POINT_COUNT, SLOPE_ENDPOINT, SLOPE_OLS)
FEATURE_META: dict[str, tuple[ValueType, str]] = {
    PATH_CHANGE: (ValueType.FLOAT64, "bps"), PATH_LAST: (ValueType.FLOAT64, "currency/share"),
    PATH_MAXIMUM: (ValueType.FLOAT64, "currency/share"), PATH_MINIMUM: (ValueType.FLOAT64, "currency/share"),
    POINT_COUNT: (ValueType.INT64, "points"), SLOPE_ENDPOINT: (ValueType.FLOAT64, "currency/share/second"),
    SLOPE_OLS: (ValueType.FLOAT64, "currency/share/second"),
}
_REQUIRED = frozenset({"policy_version", "series_source", "evidence_limit"})
_OPTIONAL = frozenset({"grid_version", "series_policy_id"})
_OHLC = ("open", "high", "low", "close")


@dataclass(frozen=True)
class VwapPathSettings:
    policy_version: str
    series_source: str
    grid_version: str | None
    series_policy_id: str | None
    evidence_limit: int


def _check(policy: object, source: object, grid_version: object, series_policy_id: object,
           limit: object) -> VwapPathSettings:
    if type(policy) is not str:
        fail(ErrorCode.INVALID_CONFIG, "exact policy label required")
    if policy != VWAP_POLICY:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported policy label")
    if source not in SOURCES:
        fail(ErrorCode.INVALID_CONFIG, "series_source must be trade, bar or prepared_window")
    assert type(source) is str
    if source == "trade":
        if grid_version is not None:
            fail(ErrorCode.INVALID_CONFIG, "grid_version only with a bar or prepared_window source")
    else:
        label(grid_version)
    if source == "prepared_window":
        label(series_policy_id)
    elif series_policy_id is not None:
        fail(ErrorCode.INVALID_CONFIG, "series_policy_id only with the prepared_window source")
    return VwapPathSettings(policy, source, None if grid_version is None else str(grid_version),
                            None if series_policy_id is None else str(series_policy_id), check_limit(limit))


def build_vwap_path_config(*, policy_version: str | None = None, series_source: str | None = None,
                           grid_version: str | None = None, series_policy_id: str | None = None,
                           session: SessionSpec, availability: AvailabilitySpec, adjustment: AdjustmentSpec,
                           price_unit: PriceUnit, evidence_limit: int | None = None) -> ConfigSpec:
    """Final ConfigSpec; every parameter is explicit with no default."""
    s = _check(policy_version, series_source, grid_version, series_policy_id, evidence_limit)
    params = [Parameter("policy_version", s.policy_version), Parameter("series_source", s.series_source),
              Parameter("evidence_limit", s.evidence_limit)]
    if s.grid_version is not None:
        params.append(Parameter("grid_version", s.grid_version))
    if s.series_policy_id is not None:
        params.append(Parameter("series_policy_id", s.series_policy_id))
    return make_config(VWAP_IDENTITY, VWAP_ALGORITHM, tuple(params), session, availability, adjustment, price_unit)


def _decode(config: ConfigSpec, features: tuple[str, ...] | None) -> tuple[VwapPathSettings, tuple[str, ...]]:
    values, selected = parameter_values(config, VWAP_IDENTITY, VWAP_ALGORITHM, VWAP_POLICY, features, VWAP_FEATURES)
    check_closed(values, _REQUIRED, _OPTIONAL)
    s = _check(values["policy_version"], values["series_source"], values.get("grid_version"),
               values.get("series_policy_id"), values["evidence_limit"])
    assert config.price_unit is not None
    expected = build_vwap_path_config(
        policy_version=s.policy_version, series_source=s.series_source, grid_version=s.grid_version,
        series_policy_id=s.series_policy_id, session=config.session, availability=config.availability,
        adjustment=config.adjustment, price_unit=config.price_unit, evidence_limit=s.evidence_limit)
    if config != expected:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "configuration is not the final canonical VWAP-path envelope")
    return s, selected


def decode_vwap_path_config(config: ConfigSpec) -> VwapPathSettings:
    """Validate the closed VWAP-path envelope and return its settings."""
    return _decode(config, None)[0]


@dataclass(frozen=True)
class _Point:
    x: int
    notional: int | None
    volume: int
    witness: Witness


@dataclass
class _Series:
    """Per-slot causes `(count outputs, price outputs)`, the path points and batch level causes."""

    slots: list[tuple[list[Reason], list[Reason]]]
    points: list[_Point]
    batch: list[Reason]
    input_id: str


def _trade_series(trades: CanonicalBatch, config: ConfigSpec, entity: EntityKey,
                  interval: Interval) -> _Series | None:
    check_meta(trades, config, market=True)
    cols = columns_of(trades)
    knowledge = config.availability.knowledge_cutoff_ns
    input_id = trades.metadata.source.input_id
    for i in range(trades.row_count):
        if cols["instrument_id"][i] != entity.instrument_id or cols["session_id"][i] != config.session.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "trade identity differs from the target entity and session")
        if cols["event_ns"][i] < interval.start:
            fail(ErrorCode.BOUNDS, "trade before the anchor")
        if cols["event_ns"][i] >= interval.end:
            fail(ErrorCode.BOUNDS, "trade at or after the interval end")
    coverage = declared_coverage(trades, interval.start, interval.end)
    if trades.row_count == 0 and coverage == "undeclared":
        return None  # emptiness cannot be proven: an absent delivery
    series = _Series([], [], [Reason.GOVERNED_GAP] if coverage == "incomplete" else [], input_id)
    for i in range(trades.row_count):
        if cols["eligible"][i] is not True:
            continue  # an ineligible trade is not an operand: its price, size and knowledge are never read
        known_at = cols["known_at_ns"][i] if "known_at_ns" in cols else None
        price = cols["price"][i] if "price" in cols else None
        size = cols["size"][i] if "size" in cols else None
        counted: list[Reason] = []
        priced: list[Reason] = []
        reason = knowledge_reason(known_at, knowledge)
        if reason is not None:
            counted.append(reason)
            priced.append(reason)
        if size is None:
            counted.append(Reason.NULL_FIELD)
            priced.append(Reason.NULL_FIELD)
        if price is None:
            priced.append(Reason.NULL_FIELD)
        series.slots.append((counted, priced))
        if size is not None:
            event_ns = cols["event_ns"][i]
            series.points.append(_Point(event_ns, None if price is None else price * size, size,
                                        Witness(input_id, f"trade:{cols['event_id'][i]}", event_ns, known_at)))
    return series


def _bar_series(grid: CanonicalBatch, bars: CanonicalBatch, config: ConfigSpec, entity: EntityKey,
                interval: Interval, settings: VwapPathSettings) -> tuple[_Series, list[Reason]]:
    edges_facts = admit_facts(grid, config, entity, EDGE_KIND, end_null=True)
    if any(f.text != settings.grid_version for f in edges_facts):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "grid text differs from the configured grid_version")
    edges = [f.start for f in edges_facts]
    if not edges or edges[0] != interval.start:
        fail(ErrorCode.BOUNDS, "the first grid edge must equal the interval start")
    if edges[-1] != interval.end:
        fail(ErrorCode.BOUNDS, "the last grid edge must equal the interval end")
    if any(a >= b for a, b in zip(edges, edges[1:])):
        fail(ErrorCode.BOUNDS, "grid edges must strictly increase")
    edge_reasons = [r for r in (knowledge_reason(f.known_at, config.availability.knowledge_cutoff_ns)
                                for f in edges_facts) if r is not None]
    check_meta(bars, config, market=True)
    if interval.end > config.availability.market_cutoff_ns:
        fail(ErrorCode.BOUNDS, "bar sources need the interval end at or before the market cutoff")
    cols = columns_of(bars)
    slot_of = {(a, b): k for k, (a, b) in enumerate(zip(edges, edges[1:]))}
    row_of: dict[int, int] = {}
    ohlc = any(name in cols for name in _OHLC)
    for i in range(bars.row_count):
        if cols["instrument_id"][i] != entity.instrument_id or cols["session_id"][i] != config.session.session_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "bar identity differs from the target entity and session")
        slot = slot_of.get((cols["start_ns"][i], cols["end_ns"][i]))
        if slot is None:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "bar does not equal a grid slot")
        row_of[slot] = i
        volume = cols["volume"][i] if "volume" in cols else None
        notional = cols["actual_notional"][i] if "actual_notional" in cols else None
        if not ohlc and volume is not None and volume > 0 and notional is not None and notional <= 0:
            fail(ErrorCode.INVALID_SCHEMA, "a positive-volume bar needs a positive actual notional")
    declared: set[int] = set()
    incomplete: set[int] = set()
    for entry in bars.metadata.interval_coverage:
        slot = slot_of.get((entry.start_ns, entry.end_ns))
        if slot is None:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "coverage entry differs from an exact grid slot")
        if slot in declared:
            fail(ErrorCode.DUPLICATE, "two coverage entries for one slot")
        declared.add(slot)
        if entry.coverage.observed != int(slot in row_of) or (entry.coverage.expected or 0) > 1:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "slot coverage contradicts the delivered row")
        if not entry.coverage.complete:
            incomplete.add(slot)
            if bars.metadata.coverage.complete:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "complete aggregate contradicts incomplete slot coverage")
    input_id = bars.metadata.source.input_id
    knowledge = config.availability.knowledge_cutoff_ns
    series = _Series([], [], [], input_id)
    for k in range(len(edges) - 1):
        start, end = edges[k], edges[k + 1]
        row_i = row_of.get(k)
        if row_i is None:
            gap_reason = Reason.GOVERNED_GAP if k in declared else Reason.ABSENT_INPUT
            series.slots.append(([gap_reason], [gap_reason]))
            continue
        volume = cols["volume"][row_i] if "volume" in cols else None
        notional = cols["actual_notional"][row_i] if "actual_notional" in cols else None
        known_at = cols["known_at_ns"][row_i] if "known_at_ns" in cols else None
        counted: list[Reason] = []
        priced: list[Reason] = []
        if k in incomplete:
            counted.append(Reason.GOVERNED_GAP)
            priced.append(Reason.GOVERNED_GAP)
        # A zero-volume window is ready without reading its knowledge or notional; a null volume reads its knowledge.
        knowledge_cause = None if volume == 0 else knowledge_reason(known_at, knowledge)
        if knowledge_cause is not None:
            counted.append(knowledge_cause)
            priced.append(knowledge_cause)
        if volume is None:
            counted.append(Reason.NULL_FIELD)
            priced.append(Reason.NULL_FIELD)
        elif volume > 0 and notional is None:
            priced.append(Reason.NULL_FIELD)
        series.slots.append((counted, priced))
        if volume is not None and volume > 0:
            series.points.append(_Point(end, notional, volume,
                                        Witness(input_id, f"bar:{start}:{end}", end, known_at, start, end,
                                                "completed_interval")))
    return series, edge_reasons


def compute_vwap_path(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                      config: ConfigSpec, *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef4-vwap1 outputs; `batches` is the fixed slots `(bounds, grid, trades, bars, proof)`, all but bounds
    nullable."""
    settings, selected = _decode(config, features)
    entity = check_entity(entity, config)
    slots = check_roles(batches, 5)
    bounds_batch, grid, trades, bars, proof = slots
    shared_validation(slots, (0, 1, 4, 2, 3), config)
    check_kinds(slots, (DataKind.REFERENCE, DataKind.REFERENCE, DataKind.TRADE, DataKind.BAR, DataKind.REFERENCE))
    interval = admit_bounds(bounds_batch, config, entity)
    source = settings.series_source
    wanted = {"trade": (False, True, False, False), "bar": (True, False, True, False),
              "prepared_window": (True, False, True, True)}[source]
    for batch, needed in zip((grid, trades, bars, proof), wanted):
        if batch is not None and not needed:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "a role is delivered that the series source does not read")
    cutoff, knowledge = config.availability.market_cutoff_ns, config.availability.knowledge_cutoff_ns
    bindings = bindings_of((("bounds", bounds_batch), ("grid", grid), ("trades", trades), ("bars", bars),
                            ("proof", proof)))
    series: _Series | None = None
    edge_reasons: list[Reason] = []
    if source == "trade":
        if trades is not None:
            series = _trade_series(trades, config, entity, interval)
    elif grid is not None and bars is not None:
        series, edge_reasons = _bar_series(grid, bars, config, entity, interval, settings)
    proof_reason: Reason | None = None
    if source == "prepared_window":
        if proof is None:
            proof_reason = Reason.ABSENT_INPUT
        else:
            facts = admit_facts(proof, config, entity, PROOF_KIND, end_null=False)
            if len(facts) != 1:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "exactly one series proof fact is required")
            if facts[0].text != settings.series_policy_id:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "proof text differs from the configured series_policy_id")
            if (facts[0].start, facts[0].end) != (interval.start, interval.end):
                fail(ErrorCode.INCONSISTENT_IDENTITY, "proof bounds differ from the declared interval")
            proof_reason = knowledge_reason(facts[0].known_at, knowledge)
    if series is None:
        outs = {f: unavailable({Reason.ABSENT_INPUT}, 0, 0) for f in selected}
        return assemble(config, entity, selected, outs, FEATURE_META, VWAP_ALGORITHM, settings.evidence_limit,
                        bindings)
    anchor_reason = knowledge_reason(interval.known_at, knowledge)
    unready = [r for r in [anchor_reason, proof_reason, *edge_reasons] if r is not None]
    points = series.points
    n = len(points)
    nslots = len(series.slots)
    cum_n = cum_v = 0
    path: list[Fraction] = []
    for p in points:
        cum_v += p.volume
        cum_n += p.notional or 0  # a null notional blocks every priced output, so the path is read only when complete
        path.append(Fraction(cum_n, cum_v))
    witnesses = [p.witness for p in points]
    assert config.price_unit is not None
    scale = Fraction(10**config.price_unit.scale)

    def evaluate(feature: str) -> Out:
        priced = feature != POINT_COUNT
        reasons: set[Reason] = set(unready) | set(series.batch)
        unready_slots = 0
        for counted, with_price in series.slots:
            causes = with_price if priced else counted
            if causes:
                reasons.update(causes)
                unready_slots += 1
        if cutoff < interval.end:
            reasons.add(Reason.FUTURE_MARKET)
        if reasons:
            return unavailable(reasons, nslots, 0 if unready else nslots - unready_slots)

        def result(value: Fraction | int, rows: list[Witness]) -> Out:
            return Out(value, frozenset(), nslots, nslots, list(rows))

        if feature == POINT_COUNT:
            return result(n, witnesses)
        if n == 0:
            return unavailable({Reason.NO_ELIGIBLE_OBSERVATIONS}, nslots, nslots)
        if feature == PATH_LAST:
            return result(path[-1] / scale, witnesses)
        if feature == PATH_MAXIMUM:
            top = max(path)
            return result(top / scale, witnesses[:path.index(top) + 1])
        if feature == PATH_MINIMUM:
            low = min(path)
            return result(low / scale, witnesses[:path.index(low) + 1])
        if n < 2:
            return unavailable({Reason.INSUFFICIENT_HISTORY}, 2, 1)
        if feature == PATH_CHANGE:
            return result(Fraction(10000) * (path[-1] - path[0]) / path[0], witnesses)
        xs = [p.x for p in points]
        if feature == SLOPE_ENDPOINT:
            span = xs[-1] - xs[0]
            if span == 0:
                return unavailable({Reason.ZERO_DENOMINATOR}, nslots, nslots)
            return result((path[-1] - path[0]) / scale * SEC / span, witnesses)
        sx, sxx = sum(xs), sum(x * x for x in xs)
        sw = sum(path, Fraction(0))
        sxw = sum((x * w for x, w in zip(xs, path)), Fraction(0))
        den = n * sxx - sx * sx
        if den == 0:
            return unavailable({Reason.ZERO_DENOMINATOR}, nslots, nslots)
        return result((n * sxw - sx * sw) / den / scale * SEC, witnesses)

    outs = {f: evaluate(f) for f in selected}
    return assemble(config, entity, selected, outs, FEATURE_META, VWAP_ALGORITHM, settings.evidence_limit, bindings)
