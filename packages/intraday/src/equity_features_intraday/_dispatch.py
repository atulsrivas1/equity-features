"""Selected independent batch outputs over immutable compatible admitted facts."""
from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, EvidenceRow, FeatureColumn,
    FeatureResult, QualityRow, Reason, ResultMetadata, Status, ValueType,
)
from ._context import IntradayContext, fail, validate_config
from ._indicators import indicator
from ._prepare import IntradayPreparation, prepare_intraday, validate_preparation
from ._registry import PACKAGE_VERSION, describe_intraday, require_intraday_capability


def compute_intraday(batches: tuple[CanonicalBatch, ...] | None, context: IntradayContext,
                     config: ConfigSpec, *, features: tuple[str, ...],
                     preparation: IntradayPreparation | None = None) -> FeatureResult:
    period, _, evidence_limit = validate_config(context, config)
    if (type(features) is not tuple or not 1 <= len(features) <= len(describe_intraday())
            or any(type(feature) is not str for feature in features)
            or len(set(features)) != len(features)):
        fail("nonempty unique selected feature IDs required")
    known = {entry.feature_id for entry in describe_intraday()}
    if any(feature not in known for feature in features):
        fail("unknown selected intraday feature", ErrorCode.UNKNOWN_FEATURE)
    for feature in sorted(features):
        require_intraday_capability(feature, "batch")
        if (period < (2 if feature == "intraday.rsi" else 1)
                or period > (4096 if feature == "intraday.ema" else 4095)):
            fail("period outside selected indicator bounds")
    selected = tuple(sorted(features))
    requirements = tuple(sorted({"true_ranges" if feature == "intraday.atr" else
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
    for feature in selected:
        expected = max(period + (feature != "intraday.ema"), epoch_count)
        value: float | None = None
        reasons: tuple[Reason, ...]
        if preparation is None:
            status, observed, reasons = Status.MISSING_INPUT, 0, (Reason.ABSENT_INPUT,)
        else:
            view = preparation.operand("true_ranges" if feature == "intraday.atr" else "anchored_closes")
            observed = view.observed
            reason_set = set(view.reasons)
            short = epoch_count < period + (feature != "intraday.ema")
            if short:
                reason_set.add(Reason.INSUFFICIENT_HISTORY)
            reasons = tuple(sorted(reason_set, key=lambda reason: reason.value))
            status = (Status.MISSING_INPUT if view.status == Status.MISSING_INPUT else
                      Status.INSUFFICIENT_HISTORY if short else view.status)
            if status == Status.AVAILABLE:
                if view.values is None:
                    fail("available operand has no arithmetic values", ErrorCode.OVERFLOW)
                value = indicator(feature, view.values, period)
            for row in view.evidence:
                if len(evidence) >= evidence_limit:
                    break
                evidence.append(EvidenceRow(entity, feature, row.input_id, f"slot:{row.slot_index}",
                    row.end_ns, row.known_at_ns, row.start_ns, row.end_ns,
                    row.use, row.reason, "completed_interval"))
        unit = "RSI points" if feature == "intraday.rsi" else "currency/share"
        columns.append(FeatureColumn(feature, "intraday-v1", ValueType.FLOAT64, unit, (entity,), (value,)))
        quality.append(QualityRow(entity, feature, status, expected, observed, reasons))
    return FeatureResult(tuple(columns), tuple(quality), metadata, tuple(evidence))
