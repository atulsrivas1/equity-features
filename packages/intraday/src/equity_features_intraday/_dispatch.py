"""Selected independent batch outputs over immutable compatible admitted facts."""
from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow, FeatureColumn,
    FeatureResult, QualityRow, Reason, ResultMetadata, Status, ValueType,
)
from ._context import IntradayContext, fail, validate_config
from ._bands import BAND_FEATURES, band_values
from ._indicators import indicator
from ._prepare import IntradayPreparation, prepare_intraday, validate_preparation
from ._registry import PACKAGE_VERSION, describe_intraday, require_intraday_capability


def compute_intraday(batches: tuple[CanonicalBatch, ...] | None, context: IntradayContext,
                     config: ConfigSpec, *, features: tuple[str, ...],
                     preparation: IntradayPreparation | None = None) -> FeatureResult:
    period, multiplier, evidence_limit = validate_config(context, config)
    if (type(features) is not tuple or not 1 <= len(features) <= len(describe_intraday())
            or any(type(feature) is not str for feature in features)
            or len(set(features)) != len(features)):
        fail("nonempty unique selected feature IDs required")
    known = {entry.feature_id: entry for entry in describe_intraday()}
    if any(feature not in known for feature in features):
        fail("unknown selected intraday feature", ErrorCode.UNKNOWN_FEATURE)
    for feature in sorted(features):
        require_intraday_capability(feature, "batch")
        if (period < known[feature].minimum_period
                or period > (4095 if feature in ("intraday.rsi", "intraday.atr") else 4096)):
            fail("period outside selected feature bounds")
    selected = tuple(sorted(features))
    requirements = tuple(sorted({"price_moments" if feature in BAND_FEATURES else
                                 "true_ranges" if feature == "intraday.atr" else
                                 "anchored_closes" for feature in selected}))
    if preparation is not None:
        validate_preparation(preparation, batches, context, config, requirements)
    elif batches is not None:
        preparation = prepare_intraday(batches, context, config, requirements=requirements)
    epoch_count = context.target_index-context.anchor_index+1
    entity = EntityKey(context.instrument_id, config.session.session_id)
    metadata = ResultMetadata(config.session.namespace, config.session.session_id,
                              config.availability, config.digest,
                              () if preparation is None else preparation.input_bindings,
                              "intraday.python", PACKAGE_VERSION, evidence_limit)
    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    selected_bands = tuple(feature for feature in selected if feature in BAND_FEATURES)
    bands: dict[str, float | None] = {}
    if preparation is not None and selected_bands:
        moments = preparation.operand("price_moments")
        if moments.status == Status.AVAILABLE:
            if moments.values is None:
                fail("available moments have no arithmetic values", ErrorCode.OVERFLOW)
            bands = band_values(moments.values, multiplier, selected_bands)
    for feature in selected:
        is_band = feature in BAND_FEATURES
        seed = period + (feature in ("intraday.rsi", "intraday.atr"))
        expected = period if is_band else max(seed, epoch_count)
        value: float | None = None
        reasons: tuple[Reason, ...]
        if preparation is None:
            status, observed, reasons = Status.MISSING_INPUT, 0, (Reason.ABSENT_INPUT,)
        else:
            view = preparation.operand("price_moments" if is_band else
                                       "true_ranges" if feature == "intraday.atr" else "anchored_closes")
            observed = view.observed
            reason_set = set(view.reasons)
            short = epoch_count < seed
            if short:
                reason_set.add(Reason.INSUFFICIENT_HISTORY)
            reasons = tuple(sorted(reason_set, key=lambda reason: reason.value))
            status = (Status.MISSING_INPUT if view.status == Status.MISSING_INPUT else
                      Status.INSUFFICIENT_HISTORY if short else view.status)
            if status == Status.AVAILABLE:
                if view.values is None:
                    fail("available operand has no arithmetic values", ErrorCode.OVERFLOW)
                value = bands[feature] if is_band else indicator(feature, view.values, period)
                if is_band and value is None:
                    status = Status.NOT_APPLICABLE
                    reasons = tuple(sorted((*reasons, Reason.ZERO_DENOMINATOR), key=lambda reason: reason.value))
            for row in view.evidence:
                if len(evidence) >= evidence_limit:
                    break
                evidence.append(EvidenceRow(entity, feature, row.input_id, f"slot:{row.slot_index}",
                    row.end_ns, row.known_at_ns, row.start_ns, row.end_ns,
                    row.use, row.reason, "completed_interval"))
        unit = known[feature].unit
        columns.append(FeatureColumn(feature, "intraday-v1", ValueType.FLOAT64, unit, (entity,), (value,)))
        quality.append(QualityRow(entity, feature, status, expected, observed, reasons))
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
