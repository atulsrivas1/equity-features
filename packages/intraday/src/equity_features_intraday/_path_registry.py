"""Own optional EF4 path-efficiency identities; the accepted R17 catalog and its digest stay untouched."""
from dataclasses import asdict
import hashlib
import json

from equity_feature_contracts import ErrorCode
from ._context import fail
from ._path_config import PATH_EFFICIENCY_ALGORITHM
from ._registry import PACKAGE_VERSION, IntradayFeature

PATH_CHOPPINESS_FRACTION = "path.choppiness_fraction"
PATH_EFFICIENCY_RATIO = "path.efficiency_ratio"
PATH_LOG_EFFICIENCY_RATIO = "path.log_efficiency_ratio"
PATH_NET_DISPLACEMENT = "path.net_displacement"
PATH_LENGTH = "path.path_length"
PATH_TRUE_RANGE_SUM = "path.true_range_sum"
PATH_WINDOW_RANGE = "path.window_range"

# Lexicographic by feature id. The window is N+1 governed slots with N >= 2, so three slots is the least any
# configuration can need; the operand family names the readiness closure of the output.
_CATALOG = (
    IntradayFeature(PATH_CHOPPINESS_FRACTION, PATH_EFFICIENCY_ALGORITHM, "fraction", 3, "range_and_true_range",
                    supports_batch=True),
    IntradayFeature(PATH_EFFICIENCY_RATIO, PATH_EFFICIENCY_ALGORITHM, "fraction", 3, "closes", supports_batch=True),
    IntradayFeature(PATH_LOG_EFFICIENCY_RATIO, PATH_EFFICIENCY_ALGORITHM, "fraction", 3, "closes_log",
                    supports_batch=True),
    IntradayFeature(PATH_NET_DISPLACEMENT, PATH_EFFICIENCY_ALGORITHM, "currency/share", 3, "closes",
                    supports_batch=True),
    IntradayFeature(PATH_LENGTH, PATH_EFFICIENCY_ALGORITHM, "currency/share", 3, "closes", supports_batch=True),
    IntradayFeature(PATH_TRUE_RANGE_SUM, PATH_EFFICIENCY_ALGORITHM, "currency/share", 3, "range_and_true_range",
                    supports_batch=True),
    IntradayFeature(PATH_WINDOW_RANGE, PATH_EFFICIENCY_ALGORITHM, "currency/share", 3, "range_and_true_range",
                    supports_batch=True),
)


def describe_path_efficiency() -> tuple[IntradayFeature, ...]:
    return _CATALOG


def path_efficiency_catalog_digest() -> str:
    payload = {"schema": "equity-features.path-efficiency-catalog.v1",
               "package_version": PACKAGE_VERSION,
               "entries": [asdict(entry) for entry in _CATALOG]}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":"), allow_nan=False).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def require_path_efficiency_capability(feature_id: str, capability: str) -> None:
    entry = next((entry for entry in _CATALOG if entry.feature_id == feature_id), None)
    if entry is None:
        fail("unknown path-efficiency feature", ErrorCode.UNKNOWN_FEATURE)
    supported = {"batch": entry.supports_batch, "update": entry.supports_update,
                 "restore": entry.supports_restore, "merge": entry.supports_merge}
    if capability not in supported or not supported[capability]:
        fail("output capability is not implemented in this package version", ErrorCode.UNSUPPORTED_CAPABILITY)
