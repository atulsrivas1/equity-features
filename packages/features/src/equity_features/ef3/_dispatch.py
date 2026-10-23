"""Closed public EF3 dispatch over the daily-grid producers."""
from __future__ import annotations

from equity_feature_contracts import CanonicalBatch, ConfigSpec, ErrorCode, FeatureResult
from ._common import DailyGrid, fail
from ._logvol import LOG_VOL_IDENTITY, compute_log_volatility
from ._relative import RELATIVE_IDENTITY, compute_relative_stats


def compute_ef3(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None], grid: DailyGrid,
                config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Route the complete selected request to its producer: two role slots for relative statistics, one for log volatility."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == RELATIVE_IDENTITY:
        return compute_relative_stats(batches, grid, config, features=features)
    if config.identity == LOG_VOL_IDENTITY:
        return compute_log_volatility(batches, grid, config, features=features)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF3 producer is not implemented")
