"""Own optional EF2 channel identities; the accepted R17 catalog and its digest stay untouched."""
from dataclasses import asdict
import hashlib
import json

from equity_feature_contracts import ErrorCode
from ._context import fail
from ._channels_config import CHANNELS_ALGORITHM
from ._registry import PACKAGE_VERSION, IntradayFeature

ICHIMOKU_PREFIX = "trend.ichimoku."
KELTNER_PREFIX = "channel.keltner."
DONCHIAN_PREFIX = "channel.donchian."
PIVOT_PREFIX = "channel.pivot."
PERCENTILE = "channel.band_width.percentile"
SQUEEZE_PREFIX = "channel.squeeze."

# Output IDs per homogeneous producer (lexicographic); a call returns that producer's complete set unless a
# subset is selected.
CHANNELS_PRODUCER_FEATURES: dict[str, tuple[str, ...]] = {
    "ichimoku": tuple(ICHIMOKU_PREFIX + name for name in (
        "base_line", "conversion_line", "lagging_line_observed", "lagging_line_reference_close",
        "leading_span_a_displayed", "leading_span_a_observed", "leading_span_b_displayed",
        "leading_span_b_observed")),
    "keltner": tuple(KELTNER_PREFIX + name for name in ("lower", "middle", "upper", "width_ratio")),
    "donchian": tuple(DONCHIAN_PREFIX + name for name in ("lower", "middle", "upper", "width_ratio")),
    "pivot_levels": tuple(PIVOT_PREFIX + name for name in (
        "point", "resistance_1", "resistance_2", "support_1", "support_2")),
    "band_width_percentile": (PERCENTILE,),
    "bollinger_keltner_squeeze": tuple(SQUEEZE_PREFIX + name for name in (
        "bollinger_inside_keltner", "lower_gap", "upper_gap")),
}

_PRICE = "currency/share"
_FRACTION = "fraction"


def _entry(feature_id: str, unit: str, minimum: int, operand: str) -> IntradayFeature:
    return IntradayFeature(feature_id, CHANNELS_ALGORITHM, unit, minimum, operand, supports_batch=True)


# minimum_period is the mathematical floor over all legal parameters; the periods themselves are caller supplied
# and bound in the config (no defaults). operand_family names the additive internal operand family.
_CATALOG = tuple(sorted((
    *(_entry(ICHIMOKU_PREFIX + name, _PRICE, 1, "rolling_extrema_at") for name in (
        "base_line", "conversion_line", "leading_span_a_displayed", "leading_span_a_observed",
        "leading_span_b_displayed", "leading_span_b_observed")),
    _entry(ICHIMOKU_PREFIX + "lagging_line_observed", _PRICE, 1, "anchored_closes"),
    _entry(ICHIMOKU_PREFIX + "lagging_line_reference_close", _PRICE, 1, "anchored_closes"),
    *(_entry(KELTNER_PREFIX + name, _FRACTION if name == "width_ratio" else _PRICE, 2, "ema_atr_decimal")
      for name in ("lower", "middle", "upper", "width_ratio")),
    *(_entry(DONCHIAN_PREFIX + name, _FRACTION if name == "width_ratio" else _PRICE, 1, "rolling_extrema_at")
      for name in ("lower", "middle", "upper", "width_ratio")),
    *(_entry(PIVOT_PREFIX + name, _PRICE, 1, "prior_session_bars")
      for name in ("point", "resistance_1", "resistance_2", "support_1", "support_2")),
    _entry(PERCENTILE, _FRACTION, 3, "rolling_moments_at"),
    _entry(SQUEEZE_PREFIX + "bollinger_inside_keltner", "boolean", 2, "ema_atr_decimal"),
    _entry(SQUEEZE_PREFIX + "lower_gap", _PRICE, 2, "ema_atr_decimal"),
    _entry(SQUEEZE_PREFIX + "upper_gap", _PRICE, 2, "ema_atr_decimal"),
), key=lambda feature: feature.feature_id))


def describe_channels() -> tuple[IntradayFeature, ...]:
    return _CATALOG


def channels_catalog_digest() -> str:
    payload = {"schema": "equity-features.channels-catalog.v1",
               "package_version": PACKAGE_VERSION,
               "entries": [asdict(entry) for entry in _CATALOG]}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":"), allow_nan=False).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def require_channels_capability(feature_id: str, capability: str) -> None:
    entry = next((entry for entry in _CATALOG if entry.feature_id == feature_id), None)
    if entry is None:
        fail("unknown channels feature", ErrorCode.UNKNOWN_FEATURE)
    supported = {"batch": entry.supports_batch, "update": entry.supports_update,
                 "restore": entry.supports_restore, "merge": entry.supports_merge}
    if capability not in supported or not supported[capability]:
        fail("output capability is not implemented in this package version", ErrorCode.UNSUPPORTED_CAPABILITY)
