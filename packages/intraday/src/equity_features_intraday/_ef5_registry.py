"""Own optional EF5 price-structure identities; the accepted R17 catalog and its digest stay untouched."""
from dataclasses import asdict
import hashlib
import json

from equity_feature_contracts import ErrorCode, ValueType
from ._context import fail
from ._registry import PACKAGE_VERSION, IntradayFeature

CANDLE_ALGORITHM = "ef5-candle-v1"
STRUCTURE_ALGORITHM = "ef5-structure-v1"
TECHNICAL_ALGORITHM = "ef5-technical-v1"

# Lexicographic by feature id. minimum_period is the fewest governed slots an output can need; the operand family
# names the readiness closure. dtype and producer are fixed per header (contract headers table).
_ROWS = (
    ("candle.body_fraction", CANDLE_ALGORITHM, "fraction", 1, "bar", ValueType.FLOAT64, "candle"),
    ("candle.doji", CANDLE_ALGORITHM, "boolean", 1, "bar", ValueType.BOOL, "candle"),
    ("candle.engulfing_bearish", CANDLE_ALGORITHM, "boolean", 2, "bar_pair", ValueType.BOOL, "candle"),
    ("candle.engulfing_bullish", CANDLE_ALGORITHM, "boolean", 2, "bar_pair", ValueType.BOOL, "candle"),
    ("candle.inside_bar", CANDLE_ALGORITHM, "boolean", 2, "bar_pair", ValueType.BOOL, "candle"),
    ("candle.lower_shadow_fraction", CANDLE_ALGORITHM, "fraction", 1, "bar", ValueType.FLOAT64, "candle"),
    ("candle.upper_shadow_fraction", CANDLE_ALGORITHM, "fraction", 1, "bar", ValueType.FLOAT64, "candle"),
    ("structure.last_swing_high_price", STRUCTURE_ALGORITHM, "currency/share", 3, "ranges_lookback",
     ValueType.FLOAT64, "structure"),
    ("structure.last_swing_low_price", STRUCTURE_ALGORITHM, "currency/share", 3, "ranges_lookback",
     ValueType.FLOAT64, "structure"),
    ("structure.swing_high_confirmed", STRUCTURE_ALGORITHM, "boolean", 3, "ranges_neighbourhood",
     ValueType.BOOL, "structure"),
    ("structure.swing_low_confirmed", STRUCTURE_ALGORITHM, "boolean", 3, "ranges_neighbourhood",
     ValueType.BOOL, "structure"),
    ("technical.momentum_acceleration_fraction_per_second_squared", TECHNICAL_ALGORITHM, "fraction/s^2", 3,
     "closes", ValueType.FLOAT64, "technical"),
    ("technical.price_velocity_fraction_per_second", TECHNICAL_ALGORITHM, "fraction/s", 2, "closes",
     ValueType.FLOAT64, "technical"),
    ("technical.session_return_fraction", TECHNICAL_ALGORITHM, "fraction", 1, "open_and_close",
     ValueType.FLOAT64, "technical"),
    ("technical.signed_trend_window_count", TECHNICAL_ALGORITHM, "windows", 2, "closes", ValueType.INT64,
     "technical"),
)
_CATALOG = tuple(IntradayFeature(f, algo, unit, minimum, family, supports_batch=True)
                 for f, algo, unit, minimum, family, _, _ in _ROWS)
_DTYPE = {row[0]: row[5] for row in _ROWS}
_PRODUCER = {row[0]: row[6] for row in _ROWS}


def describe_ef5() -> tuple[IntradayFeature, ...]:
    return _CATALOG


def ef5_dtype(feature_id: str) -> ValueType:
    return _DTYPE[feature_id]


def ef5_producer(feature_id: str) -> str:
    return _PRODUCER[feature_id]


def ef5_catalog_digest() -> str:
    payload = {"schema": "equity-features.ef5-catalog.v1", "package_version": PACKAGE_VERSION,
               "entries": [asdict(entry) | {"dtype": _DTYPE[entry.feature_id].value} for entry in _CATALOG]}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def require_ef5_capability(feature_id: str, capability: str) -> None:
    entry = next((entry for entry in _CATALOG if entry.feature_id == feature_id), None)
    if entry is None:
        fail("unknown EF5 feature", ErrorCode.UNKNOWN_FEATURE)
    supported = {"batch": entry.supports_batch, "update": entry.supports_update,
                 "restore": entry.supports_restore, "merge": entry.supports_merge}
    if capability not in supported or not supported[capability]:
        fail("output capability is not implemented in this package version", ErrorCode.UNSUPPORTED_CAPABILITY)
