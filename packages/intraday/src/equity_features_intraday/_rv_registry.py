"""Own optional EF3 realized-variance identities; the accepted R17 catalog and its digest stay untouched."""
from dataclasses import asdict
import hashlib
import json

from equity_feature_contracts import ErrorCode
from ._context import fail
from ._registry import PACKAGE_VERSION, IntradayFeature
from ._rv_config import REALIZED_VARIANCE_ALGORITHM

REALIZED_VARIANCE = "intraday.realized_variance"
REALIZED_VOLATILITY = "intraday.realized_volatility"

# Lexicographic by feature id. Both outputs need at least one return (two bars) in the anchored epoch.
_CATALOG = (
    IntradayFeature(REALIZED_VARIANCE, REALIZED_VARIANCE_ALGORITHM, "fraction", 2, "anchored_log_returns",
                    supports_batch=True),
    IntradayFeature(REALIZED_VOLATILITY, REALIZED_VARIANCE_ALGORITHM, "fraction", 2, "anchored_log_returns",
                    supports_batch=True),
)


def describe_realized_variance() -> tuple[IntradayFeature, ...]:
    return _CATALOG


def realized_variance_catalog_digest() -> str:
    payload = {"schema": "equity-features.realized-variance-catalog.v1",
               "package_version": PACKAGE_VERSION,
               "entries": [asdict(entry) for entry in _CATALOG]}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":"), allow_nan=False).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def require_realized_variance_capability(feature_id: str, capability: str) -> None:
    entry = next((entry for entry in _CATALOG if entry.feature_id == feature_id), None)
    if entry is None:
        fail("unknown realized-variance feature", ErrorCode.UNKNOWN_FEATURE)
    supported = {"batch": entry.supports_batch, "update": entry.supports_update,
                 "restore": entry.supports_restore, "merge": entry.supports_merge}
    if capability not in supported or not supported[capability]:
        fail("output capability is not implemented in this package version", ErrorCode.UNSUPPORTED_CAPABILITY)
