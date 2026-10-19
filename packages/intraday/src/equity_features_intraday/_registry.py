"""Own optional batch identities; public state operations remain unsupported."""
from dataclasses import asdict, dataclass
import hashlib
import json

from equity_feature_contracts import ErrorCode
from ._context import ALGORITHM, fail

PACKAGE_VERSION = "0.1.0a3"


@dataclass(frozen=True)
class IntradayFeature:
    feature_id: str
    algorithm_version: str
    unit: str
    minimum_period: int
    operand_family: str
    supports_batch: bool = False
    supports_update: bool = False
    supports_restore: bool = False
    supports_merge: bool = False


_CATALOG = tuple(sorted((
    IntradayFeature("intraday.ema", ALGORITHM, "currency/share", 1, "anchored_closes", supports_batch=True),
    IntradayFeature("intraday.rsi", ALGORITHM, "RSI points", 2, "anchored_closes", supports_batch=True),
    IntradayFeature("intraday.atr", ALGORITHM, "currency/share", 1, "anchored_true_ranges", supports_batch=True),
    *(IntradayFeature(f"intraday.band_{name}", ALGORITHM,
                      "fraction" if name in ("width_ratio", "position") else "currency/share",
                      2, "rolling_price_moments", supports_batch=True)
      for name in ("middle", "upper", "lower", "width_ratio", "position")),
), key=lambda feature: feature.feature_id))


def describe_intraday() -> tuple[IntradayFeature, ...]:
    return _CATALOG


def intraday_catalog_digest() -> str:
    payload = {"schema": "equity-features.intraday-catalog.v1",
               "package_version": PACKAGE_VERSION,
               "entries": [asdict(entry) for entry in _CATALOG]}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":"), allow_nan=False).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def require_intraday_capability(feature_id: str, capability: str) -> None:
    entry = next((entry for entry in _CATALOG if entry.feature_id == feature_id), None)
    if entry is None:
        fail("unknown intraday feature", ErrorCode.UNKNOWN_FEATURE)
    supported = {"batch": entry.supports_batch, "update": entry.supports_update,
                 "restore": entry.supports_restore, "merge": entry.supports_merge}
    if capability not in supported or not supported[capability]:
        fail("output capability is not implemented in this package version", ErrorCode.UNSUPPORTED_CAPABILITY)
