"""Qualified preparation is separate from the later EQ138/EQ139 output kernels."""
from equity_feature_contracts import CanonicalBatch, ConfigSpec, ErrorCode, FeatureResult
from ._context import IntradayContext, fail, validate_config
from ._prepare import IntradayPreparation
from ._registry import describe_intraday, require_intraday_capability


def compute_intraday(batches: tuple[CanonicalBatch, ...] | None, context: IntradayContext,
                     config: ConfigSpec, *, features: tuple[str, ...],
                     preparation: IntradayPreparation | None = None) -> FeatureResult:
    validate_config(context, config)
    if (type(features) is not tuple or not 1 <= len(features) <= len(describe_intraday())
            or any(type(feature) is not str for feature in features)
            or len(set(features)) != len(features)):
        fail("nonempty unique selected feature IDs required")
    known = {entry.feature_id for entry in describe_intraday()}
    if any(feature not in known for feature in features):
        fail("unknown selected intraday feature", ErrorCode.UNKNOWN_FEATURE)
    for feature in sorted(features):
        require_intraday_capability(feature, "batch")
    fail("no output kernels in preparation-only version", ErrorCode.UNSUPPORTED_CAPABILITY)
