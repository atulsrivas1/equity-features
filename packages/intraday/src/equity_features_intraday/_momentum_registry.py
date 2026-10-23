"""Own optional EF2 momentum identities; the accepted R17 catalog and its digest stay untouched."""
from dataclasses import asdict
import hashlib
import json

from equity_feature_contracts import ErrorCode
from ._context import fail
from ._momentum_config import MOMENTUM_ALGORITHM
from ._registry import PACKAGE_VERSION, IntradayFeature

MACD_LINE = "intraday.macd_line"
MACD_SIGNAL = "intraday.macd_signal"
MACD_HISTOGRAM = "intraday.macd_histogram"
PLUS_DI = "intraday.plus_di"
MINUS_DI = "intraday.minus_di"
DX = "intraday.dx"
ADX = "intraday.adx"
STOCH_K = "intraday.stoch_k"
STOCH_D = "intraday.stoch_d"
WILLIAMS_R = "intraday.williams_r"

# Output IDs per homogeneous family (lexicographic); a config selects any subset of one family.
MOMENTUM_FAMILY_FEATURES: dict[str, tuple[str, ...]] = {
    "macd": (MACD_HISTOGRAM, MACD_LINE, MACD_SIGNAL),
    "dmi": (ADX, DX, MINUS_DI, PLUS_DI),
    "stochastic": (STOCH_D, STOCH_K, WILLIAMS_R),
}

# Lexicographic by feature id. minimum_period is the mathematical floor over all legal parameters; the
# periods themselves are caller supplied and bound in the config (no defaults).
_CATALOG = (
    IntradayFeature(ADX, MOMENTUM_ALGORITHM, "DMI points", 2, "dx_observations", supports_batch=True),
    IntradayFeature(DX, MOMENTUM_ALGORITHM, "DMI points", 2, "directional_moves", supports_batch=True),
    IntradayFeature(MACD_HISTOGRAM, MOMENTUM_ALGORITHM, "currency/share", 2, "macd_observations",
                    supports_batch=True),
    IntradayFeature(MACD_LINE, MOMENTUM_ALGORITHM, "currency/share", 2, "anchored_closes",
                    supports_batch=True),
    IntradayFeature(MACD_SIGNAL, MOMENTUM_ALGORITHM, "currency/share", 2, "macd_observations",
                    supports_batch=True),
    IntradayFeature(MINUS_DI, MOMENTUM_ALGORITHM, "DMI points", 2, "directional_moves", supports_batch=True),
    IntradayFeature(PLUS_DI, MOMENTUM_ALGORITHM, "DMI points", 2, "directional_moves", supports_batch=True),
    IntradayFeature(STOCH_D, MOMENTUM_ALGORITHM, "stochastic points", 1, "rolling_extrema_runs",
                    supports_batch=True),
    IntradayFeature(STOCH_K, MOMENTUM_ALGORITHM, "stochastic points", 1, "rolling_extrema_runs",
                    supports_batch=True),
    IntradayFeature(WILLIAMS_R, MOMENTUM_ALGORITHM, "Williams %R points", 1, "rolling_extrema_runs",
                    supports_batch=True),
)


def describe_momentum() -> tuple[IntradayFeature, ...]:
    return _CATALOG


def momentum_catalog_digest() -> str:
    payload = {"schema": "equity-features.momentum-catalog.v1",
               "package_version": PACKAGE_VERSION,
               "entries": [asdict(entry) for entry in _CATALOG]}
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=True,
                     separators=(",", ":"), allow_nan=False).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def require_momentum_capability(feature_id: str, capability: str) -> None:
    entry = next((entry for entry in _CATALOG if entry.feature_id == feature_id), None)
    if entry is None:
        fail("unknown momentum feature", ErrorCode.UNKNOWN_FEATURE)
    supported = {"batch": entry.supports_batch, "update": entry.supports_update,
                 "restore": entry.supports_restore, "merge": entry.supports_merge}
    if capability not in supported or not supported[capability]:
        fail("output capability is not implemented in this package version", ErrorCode.UNSUPPORTED_CAPABILITY)
