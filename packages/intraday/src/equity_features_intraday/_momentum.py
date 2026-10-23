"""Pure EF2 momentum and trend (ef2-conv1): MACD, DMI/ADX and stochastic/Williams %R.

One homogeneous family per config with any subset of its outputs selected. Every selected output owns its
dependency slots, counts and readiness, so an unrelated gap, null or missing column never blocks an output whose
own dependencies are ready. No clock, I/O, storage or default period. Reset epoch and full-history replay only.
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
from ._context import IntradayContext, fail
from ._momentum_config import MOMENTUM_ALGORITHM, MomentumSettings, decode_momentum_config
from ._momentum_math import (
    DmiResult, directional_moves, dmi_values, macd_values, rolling_extrema_runs,
    stochastic_values, williams_value,
)
from ._momentum_registry import (
    ADX, DX, MACD_LINE, MINUS_DI, MOMENTUM_FAMILY_FEATURES, PLUS_DI,
    STOCH_D, STOCH_K, WILLIAMS_R, describe_momentum, require_momentum_capability,
)
from ._prepare import OperandEvidence, arithmetic
from ._registry import PACKAGE_VERSION

_CLOSE = ("close",)
_HL = ("high", "low")
_HLC = ("high", "low", "close")


@dataclass(frozen=True)
class _View:
    """Readiness of one output's dependency slots (the R17 per-slot rule, owned by the output)."""
    reasons: frozenset[Reason]
    observed: int
    missing_column: bool
    evidence: tuple[OperandEvidence, ...]


def _assess(admitted: Admitted, fields: dict[int, tuple[str, ...]], evidence_limit: int) -> _View:
    reasons: set[Reason] = set()
    missing_column = False
    observed = 0
    evidence: list[OperandEvidence] = []
    for i, names in fields.items():
        fact = admitted.facts[i]
        ready = True
        if fact.input_id is not None and any(name not in fact.columns for name in names):
            missing_column = True
            reasons.add(Reason.ABSENT_INPUT)
            ready = False
        if fact.knowledge_reason is not None:
            reasons.add(fact.knowledge_reason)
            ready = False
        if fact.empty:
            reasons.update((Reason.OBSERVED_EMPTY, Reason.NO_ELIGIBLE_OBSERVATIONS))
            ready = False
        elif fact.row_index is None or fact.coverage is None:
            reasons.add(Reason.GOVERNED_GAP)
            ready = False
        else:
            if not fact.coverage.complete or fact.coverage.expected != 1 or fact.coverage.observed != 1:
                reasons.add(Reason.GOVERNED_GAP)
                ready = False
            for name in names:
                if name in fact.columns and (fact.close if name == "close" else
                                             fact.high if name == "high" else fact.low) is None:
                    reasons.add(Reason.NULL_FIELD)
                    ready = False
        if ready:
            observed += 1
        if (fact.row_index is not None and fact.input_id is not None and len(evidence) < evidence_limit
                and (ready or fact.knowledge_reason is not None)):
            evidence.append(OperandEvidence(i, fact.input_id, fact.slot.start_ns, fact.slot.end_ns,
                                            fact.known_at_ns, "consumed" if ready else "excluded",
                                            None if ready else fact.knowledge_reason))
    if admitted.observed_empty_delivery:
        reasons.add(Reason.OBSERVED_EMPTY)
    return _View(frozenset(reasons), observed, missing_column, tuple(evidence))


def _dependency(feature: str, settings: MomentumSettings, anchor: int,
                target: int) -> tuple[dict[int, tuple[str, ...]], int, bool]:
    """Dependency slots and fields, the minimum epoch slots (seed) and whether the output is a rolling window."""
    if settings.family == "macd":
        slow, signal = settings.period("slow_period"), settings.period("signal_period")
        seed = slow if feature == MACD_LINE else slow + signal - 1
        return {i: _CLOSE for i in range(anchor, target+1)}, seed, False
    if settings.family == "dmi":
        di, adx = settings.period("di_period"), settings.period("adx_period")
        seed = di + adx if feature == ADX else di + 1
        if target == anchor:
            return {anchor: _HLC}, seed, False
        fields = {i: _HLC for i in range(anchor, target)}
        fields[target] = _HL
        return fields, seed, False
    window, slowing, d_period = (settings.period("k_period"), settings.period("k_slowing"),
                                 settings.period("d_period"))
    span, closes = ((window, 1) if feature == WILLIAMS_R else
                    (window+slowing-1, slowing) if feature == STOCH_K else
                    (window+slowing+d_period-2, slowing+d_period-1))
    first = max(anchor, target-span+1)
    return {i: _HLC if i > target-closes else _HL for i in range(first, target+1)}, span, True


def compute_momentum(batches: tuple[CanonicalBatch, ...] | None, context: IntradayContext,
                     config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Selected ef2-conv1 outputs of one family over supplied BARs; deterministic, batch and full replay only."""
    settings = decode_momentum_config(context, config)
    owned = MOMENTUM_FAMILY_FEATURES[settings.family]
    if (type(features) is not tuple or not 1 <= len(features) <= len(owned)
            or any(type(feature) is not str for feature in features) or len(set(features)) != len(features)):
        fail("nonempty unique selected feature IDs required")
    known = {entry.feature_id for entry in describe_momentum()}
    if any(feature not in known or feature not in owned for feature in features):
        fail("selected feature is unknown or belongs to another momentum family", ErrorCode.UNKNOWN_FEATURE)
    selected = tuple(sorted(features))
    for feature in selected:
        require_momentum_capability(feature, "batch")
    admitted = admit(batches, context, config) if batches is not None else None
    a, t = context.anchor_index, context.target_index
    epoch = t-a+1
    scale = cast(int, config.price_unit.scale)  # decode_momentum_config proved the unit
    entity = EntityKey(context.instrument_id, config.session.session_id)
    status: dict[str, Status] = {}
    reasons: dict[str, set[Reason]] = {}
    expected: dict[str, int] = {}
    observed: dict[str, int] = {}
    views: dict[str, _View | None] = {}
    seeds: dict[str, int] = {}
    ready: list[str] = []
    for feature in selected:
        fields, seed, rolling = _dependency(feature, settings, a, t)
        seeds[feature] = seed
        expected[feature] = seed if rolling else max(seed, epoch)
        if admitted is None:
            views[feature] = None
            status[feature], observed[feature] = Status.MISSING_INPUT, 0
            reasons[feature] = {Reason.ABSENT_INPUT}
            continue
        view = _assess(admitted, fields, settings.evidence_limit)
        views[feature] = view
        observed[feature] = view.observed
        found = set(view.reasons)
        short = epoch < seed
        if short:
            found.add(Reason.INSUFFICIENT_HISTORY)
        reasons[feature] = found
        status[feature] = (Status.MISSING_INPUT if view.missing_column else
                           Status.INSUFFICIENT_HISTORY if short else
                           Status.INCOMPLETE_COVERAGE if view.reasons or view.observed != len(fields) else
                           Status.AVAILABLE)
        if status[feature] == Status.AVAILABLE:
            ready.append(feature)
    values: dict[str, float | None] = {}
    if ready:
        assert admitted is not None
        facts = admitted.facts
        if settings.family == "macd":
            closes = cast(tuple[Fraction, ...], arithmetic("anchored_closes", facts, context, 1, scale))
            values.update(macd_values(closes, settings.period("fast_period"), settings.period("slow_period"),
                                      settings.period("signal_period"), tuple(ready)))
        elif settings.family == "dmi":
            di, adx = settings.period("di_period"), settings.period("adx_period")
            result: DmiResult = dmi_values(arithmetic("true_ranges", facts, context, 1, scale),
                                           directional_moves(facts, a, t, scale), di, adx, ADX in ready)
            values.update({PLUS_DI: result.plus_di, MINUS_DI: result.minus_di, DX: result.dx})
            if ADX in ready:
                if not result.dx_defined:
                    values[ADX] = None
                elif epoch - cast(int, result.first_dx) < adx:
                    # Data-dependent warm-up: fewer than adx_period defined DX values exist.
                    status[ADX] = Status.INSUFFICIENT_HISTORY
                    reasons[ADX].add(Reason.INSUFFICIENT_HISTORY)
                    expected[ADX] = cast(int, result.first_dx) + adx
                else:
                    values[ADX] = result.adx
        else:
            window, slowing, d_period = (settings.period("k_period"), settings.period("k_slowing"),
                                         settings.period("d_period"))
            for feature in ready:
                if feature == WILLIAMS_R:
                    values[feature] = williams_value(rolling_extrema_runs(facts, t, window, 1, scale)[-1])
                elif feature == STOCH_K:
                    values[feature] = stochastic_values(
                        rolling_extrema_runs(facts, t, window, slowing, scale), slowing, None)
                else:
                    values[feature] = stochastic_values(
                        rolling_extrema_runs(facts, t, window, slowing+d_period-1, scale), slowing, d_period)
    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    units = {entry.feature_id: entry.unit for entry in describe_momentum()}
    for feature in selected:
        value: float | None = None
        if status[feature] == Status.AVAILABLE:
            value = values[feature]
            if value is None:
                status[feature] = Status.NOT_APPLICABLE
                reasons[feature].add(Reason.ZERO_DENOMINATOR)
        view = views[feature]
        if view is not None and status[feature] != Status.MISSING_INPUT:
            for row in view.evidence:
                if len(evidence) >= settings.evidence_limit:
                    break
                evidence.append(EvidenceRow(entity, feature, row.input_id, f"slot:{row.slot_index}",
                    row.end_ns, row.known_at_ns, row.start_ns, row.end_ns,
                    row.use, row.reason, "completed_interval"))
        columns.append(FeatureColumn(feature, MOMENTUM_ALGORITHM, ValueType.FLOAT64, units[feature],
                                     (entity,), (value,)))
        ordered = tuple(sorted(reasons[feature], key=lambda reason: reason.value))
        quality.append(QualityRow(entity, feature, status[feature], expected[feature], observed[feature], ordered))
    metadata = ResultMetadata(config.session.namespace, config.session.session_id, config.availability,
                              config.digest, () if admitted is None else admitted.inputs,
                              "intraday.python", PACKAGE_VERSION, settings.evidence_limit)
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
