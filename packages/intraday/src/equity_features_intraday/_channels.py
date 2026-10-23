"""Pure EF2 Ichimoku and price channels (ef2-v1): ichimoku, keltner, donchian, pivot_levels,
band_width_percentile and bollinger_keltner_squeeze.

One homogeneous producer per config; a call returns that producer's complete sorted header set unless a subset is
selected. Every header owns its closure slots, counts and readiness, so an unrelated gap, null or missing column never
blocks a header whose own closure is ready. No clock, I/O, storage or default period. Reset epoch and full-history
replay only; every output reads bars at or before the target slot.
"""
from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from typing import cast

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow, FeatureColumn,
    FeatureResult, QualityRow, Reason, ResultMetadata, Status, ValueType,
)
from ._admission import Admitted, admit
from ._channels_config import CHANNELS_ALGORITHM, ChannelsSettings, decode_channels_config
from ._channels_math import (
    exact_float, keltner_values, midpoint, percentile_rank, pivot_levels, rolling_extrema_at,
    rolling_high_at, rolling_low_at, rolling_moments_at, squeeze_values, width_keys,
)
from ._channels_registry import (
    CHANNELS_PRODUCER_FEATURES, DONCHIAN_PREFIX, ICHIMOKU_PREFIX, KELTNER_PREFIX, PERCENTILE, PIVOT_PREFIX,
    SQUEEZE_PREFIX, describe_channels, require_channels_capability,
)
from ._context import IntradayContext, fail
from ._momentum import _View, _assess
from ._prepare import arithmetic
from ._registry import PACKAGE_VERSION

_CLOSE = ("close",)
_HL = ("high", "low")
_HLC = ("high", "low", "close")


@dataclass(frozen=True)
class _Plan:
    """One header's closure: dependency slots and fields, the contract's expected count and the short-history rule."""
    fields: dict[int, tuple[str, ...]]
    expected: int
    short: bool
    absent: bool = False  # no preceding session for the pivots: missing_input / absent_input


def _window(first_limit: int, end: int, period: int, names: tuple[str, ...]) -> dict[int, tuple[str, ...]]:
    """The `period` slots ending at `end`, never reaching before the anchor (no shortening, no earlier bars)."""
    return {i: names for i in range(max(first_limit, end-period+1), end+1)}


def _chain_fields(anchor: int, target: int) -> dict[int, tuple[str, ...]]:
    """Keltner closure: close on a..t, high/low on a+1..t (the anchor high/low are not read)."""
    fields = {anchor: _CLOSE}
    fields.update({i: _HLC for i in range(anchor+1, target+1)})
    return fields


def _plan(feature: str, settings: ChannelsSettings, context: IntradayContext) -> _Plan:
    a, t = context.anchor_index, context.target_index
    n = t - a + 1
    producer = settings.producer
    if producer == "ichimoku":
        conversion, base, leading = (settings.param("conversion_period"), settings.param("base_period"),
                                     settings.param("leading_b_period"))
        d = settings.param("displacement")
        o = t - d
        name = feature[len(ICHIMOKU_PREFIX):]
        both = max(conversion, base)
        if name == "conversion_line":
            return _Plan(_window(a, t, conversion, _HL), conversion, n < conversion)
        if name == "base_line":
            return _Plan(_window(a, t, base, _HL), base, n < base)
        if name == "leading_span_a_observed":
            return _Plan(_window(a, t, both, _HL), both, n < both)
        if name == "leading_span_b_observed":
            return _Plan(_window(a, t, leading, _HL), leading, n < leading)
        if name == "leading_span_a_displayed":
            return _Plan(_window(a, o, both, _HL), both, n < both + d)
        if name == "leading_span_b_displayed":
            return _Plan(_window(a, o, leading, _HL), leading, n < leading + d)
        if name == "lagging_line_observed":
            return _Plan({t: _CLOSE}, 1, n < d + 1)
        return _Plan({o: _CLOSE} if o >= a else {}, 1, n < d + 1)
    if producer in ("keltner", "bollinger_keltner_squeeze"):
        seed = max(settings.param("ema_period"), settings.param("atr_period") + 1)
        if producer == "bollinger_keltner_squeeze":
            seed = max(seed, settings.param("band_period"))
        return _Plan(_chain_fields(a, t), max(seed, n), n < seed)
    if producer == "donchian":
        period = settings.param("period")
        name = feature[len(DONCHIAN_PREFIX):]
        names = _HL if name in ("middle", "width_ratio") else ("high",) if name == "upper" else ("low",)
        return _Plan(_window(a, t, period, names), period, n < period)
    if producer == "pivot_levels":
        slots = context.slots()
        order = [s.session_id for s in context.sessions]
        position = order.index(slots[-1].session_id)
        if position == 0:
            return _Plan({}, 1, False, True)
        prior = [s.index for s in slots if s.session_id == order[position-1]]
        fields = {i: _HL for i in prior}
        fields[prior[-1]] = _HLC
        return _Plan(fields, len(prior), False)
    period, population, minimum = (settings.param("band_period"), settings.param("population_size"),
                                   settings.param("min_population"))
    count = max(0, min(population, n - period))
    first = max(a, t - count - period + 1)
    return _Plan({i: _CLOSE for i in range(first, t+1)},
                 period + (count if count >= minimum else minimum), count < minimum)


def compute_channels(batches: tuple[CanonicalBatch, ...] | None, context: IntradayContext,
                     config: ConfigSpec, *, features: tuple[str, ...] | None = None) -> FeatureResult:
    """Selected ef2-v1 headers of one producer over supplied BARs; deterministic, batch and full replay only.

    features defaults to the producer's complete header set; a subset selects only those headers.
    """
    settings = decode_channels_config(context, config)
    owned = CHANNELS_PRODUCER_FEATURES[settings.producer]
    if features is None:
        features = owned
    if (type(features) is not tuple or not 1 <= len(features) <= len(owned)
            or any(type(feature) is not str for feature in features) or len(set(features)) != len(features)):
        fail("nonempty unique selected feature IDs required")
    known = {entry.feature_id for entry in describe_channels()}
    if any(feature not in known or feature not in owned for feature in features):
        fail("selected feature is unknown or belongs to another channels producer", ErrorCode.UNKNOWN_FEATURE)
    selected = tuple(sorted(features))
    for feature in selected:
        require_channels_capability(feature, "batch")
    admitted = admit(batches, context, config) if batches is not None else None
    a, t = context.anchor_index, context.target_index
    scale = cast(int, config.price_unit.scale)  # decode_channels_config proved the unit
    entity = EntityKey(context.instrument_id, config.session.session_id)
    status: dict[str, Status] = {}
    reasons: dict[str, set[Reason]] = {}
    expected: dict[str, int] = {}
    observed: dict[str, int] = {}
    views: dict[str, _View | None] = {}
    ready: list[str] = []
    for feature in selected:
        plan = _plan(feature, settings, context)
        expected[feature] = plan.expected
        if admitted is None or plan.absent:
            views[feature] = None
            status[feature], observed[feature] = Status.MISSING_INPUT, 0
            reasons[feature] = {Reason.ABSENT_INPUT}
            continue
        view = _assess(admitted, plan.fields, settings.evidence_limit)
        views[feature] = view
        observed[feature] = view.observed
        found = set(view.reasons)
        if plan.short:
            found.add(Reason.INSUFFICIENT_HISTORY)
        reasons[feature] = found
        status[feature] = (Status.MISSING_INPUT if view.missing_column else
                           Status.INSUFFICIENT_HISTORY if plan.short else
                           Status.INCOMPLETE_COVERAGE if view.reasons or view.observed != len(plan.fields) else
                           Status.AVAILABLE)
        if status[feature] == Status.AVAILABLE:
            ready.append(feature)
    values: dict[str, float | bool | None] = {}
    if ready:
        assert admitted is not None
        values.update(_values(settings, context, admitted, scale, tuple(ready)))
    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    units = {entry.feature_id: entry.unit for entry in describe_channels()}
    for feature in selected:
        value = values.get(feature) if status[feature] == Status.AVAILABLE else None
        view = views[feature]
        if view is not None and status[feature] != Status.MISSING_INPUT:
            for row in view.evidence:
                if len(evidence) >= settings.evidence_limit:
                    break
                evidence.append(EvidenceRow(entity, feature, row.input_id, f"slot:{row.slot_index}",
                    row.end_ns, row.known_at_ns, row.start_ns, row.end_ns,
                    row.use, row.reason, "completed_interval"))
        dtype = ValueType.BOOL if feature == SQUEEZE_PREFIX + "bollinger_inside_keltner" else ValueType.FLOAT64
        columns.append(FeatureColumn(feature, CHANNELS_ALGORITHM, dtype, units[feature], (entity,), (value,)))
        ordered = tuple(sorted(reasons[feature], key=lambda reason: reason.value))
        quality.append(QualityRow(entity, feature, status[feature], expected[feature], observed[feature], ordered))
    metadata = ResultMetadata(config.session.namespace, config.session.session_id, config.availability,
                              config.digest, () if admitted is None else admitted.inputs,
                              "intraday.python", PACKAGE_VERSION, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))


def _values(settings: ChannelsSettings, context: IntradayContext, admitted: Admitted, scale: int,
            ready: tuple[str, ...]) -> dict[str, float | bool | None]:
    """Values of the ready headers (every closure slot already proved ready by the caller)."""
    facts = admitted.facts
    a, t = context.anchor_index, context.target_index
    divisor = 10**scale
    producer = settings.producer
    result: dict[str, float | bool | None] = {}
    if producer == "ichimoku":
        conversion, base, leading = (settings.param("conversion_period"), settings.param("base_period"),
                                     settings.param("leading_b_period"))
        o = t - settings.param("displacement")
        for feature in ready:
            name = feature[len(ICHIMOKU_PREFIX):]
            end = o if name.endswith("displayed") else t
            if name == "conversion_line":
                result[feature] = exact_float(midpoint(rolling_extrema_at(facts, t, conversion), scale))
            elif name == "base_line":
                result[feature] = exact_float(midpoint(rolling_extrema_at(facts, t, base), scale))
            elif name.startswith("leading_span_a"):
                result[feature] = exact_float((midpoint(rolling_extrema_at(facts, end, conversion), scale)
                                               + midpoint(rolling_extrema_at(facts, end, base), scale)) / 2)
            elif name.startswith("leading_span_b"):
                result[feature] = exact_float(midpoint(rolling_extrema_at(facts, end, leading), scale))
            else:
                slot = t if name == "lagging_line_observed" else o
                result[feature] = exact_float(Fraction(cast(int, facts[slot].close), divisor))
    elif producer == "donchian":
        period = settings.param("period")
        for feature in ready:
            name = feature[len(DONCHIAN_PREFIX):]
            # Upper and lower have independent readiness: read only the field(s) the header owns.
            high = rolling_high_at(facts, t, period) if name != "lower" else 0
            low = rolling_low_at(facts, t, period) if name != "upper" else 0
            result[feature] = exact_float(
                Fraction(high, divisor) if name == "upper" else Fraction(low, divisor) if name == "lower" else
                Fraction(high + low, 2*divisor) if name == "middle" else Fraction(2*(high-low), high+low))
    elif producer == "pivot_levels":
        slots = context.slots()
        order = [s.session_id for s in context.sessions]
        prior = [s.index for s in slots if s.session_id == order[order.index(slots[-1].session_id)-1]]
        levels = pivot_levels(max(cast(int, facts[i].high) for i in prior),
                              min(cast(int, facts[i].low) for i in prior),
                              cast(int, facts[prior[-1]].close), scale)
        for feature in ready:
            result[feature] = exact_float(levels[feature[len(PIVOT_PREFIX):]])
    elif producer == "band_width_percentile":
        period, population = settings.param("band_period"), settings.param("population_size")
        keys = width_keys(facts, t - min(population, t-a+1-period), t, period)
        result[PERCENTILE] = exact_float(percentile_rank(keys[:-1], keys[-1]))
    else:
        closes = cast(tuple[Fraction, ...], arithmetic("anchored_closes", facts, context, 1, scale))
        true_ranges = arithmetic("true_ranges", facts, context, 1, scale)
        ema, atr = settings.param("ema_period"), settings.param("atr_period")
        multiplier = settings.multiplier("atr_multiplier")
        if producer == "keltner":
            cells = keltner_values(closes, true_ranges, ema, atr, multiplier,
                                   tuple(feature[len(KELTNER_PREFIX):] for feature in ready))
            result.update({KELTNER_PREFIX + name: value for name, value in cells.items()})
        else:
            period = settings.param("band_period")
            mean, variance = rolling_moments_at(facts, t, period, scale)
            names = {"bollinger_inside_keltner": "inside", "lower_gap": "lower_gap", "upper_gap": "upper_gap"}
            squeezed = squeeze_values(closes, true_ranges, ema, atr, multiplier, mean, variance,
                                      settings.multiplier("band_k"),
                                      tuple(names[feature[len(SQUEEZE_PREFIX):]] for feature in ready))
            result.update({feature: squeezed[names[feature[len(SQUEEZE_PREFIX):]]] for feature in ready})
    return result
