"""Own optional EF2 money-flow identities; the accepted R17 catalog and its digest stay untouched."""
from dataclasses import asdict
import hashlib
import json

from equity_feature_contracts import ErrorCode
from ._context import fail
from ._flow_config import MONEY_FLOW_ALGORITHM
from ._registry import PACKAGE_VERSION, IntradayFeature

OBV = "intraday.obv"
AD_LINE = "intraday.ad_line"
CMF = "intraday.cmf"

# Lexicographic by feature id. minimum_period is the mathematical floor; the CMF window N is caller supplied.
_CATALOG = (
    IntradayFeature(AD_LINE, MONEY_FLOW_ALGORITHM, "shares", 1, "anchored_money_flow", supports_batch=True),
    IntradayFeature(CMF, MONEY_FLOW_ALGORITHM, "fraction", 1, "windowed_money_flow", supports_batch=True),
    IntradayFeature(OBV, MONEY_FLOW_ALGORITHM, "shares", 1, "anchored_signed_volume", supports_batch=True),
)


def describe_money_flow() -> tuple[IntradayFeature, ...]:
    return _CATALOG


def money_flow_catalog_digest() -> str:
    payload = {"schema": "equity-features.money-flow-catalog.v1",
               "package_version": PACKAGE_VERSION,
               "entries": [asdict(entry) for entry in _CATALOG]}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":"), allow_nan=False).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def require_money_flow_capability(feature_id: str, capability: str) -> None:
    entry = next((entry for entry in _CATALOG if entry.feature_id == feature_id), None)
    if entry is None:
        fail("unknown money-flow feature", ErrorCode.UNKNOWN_FEATURE)
    supported = {"batch": entry.supports_batch, "update": entry.supports_update,
                 "restore": entry.supports_restore, "merge": entry.supports_merge}
    if capability not in supported or not supported[capability]:
        fail("output capability is not implemented in this package version", ErrorCode.UNSUPPORTED_CAPABILITY)
