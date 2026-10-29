"""Closed public DV1 dispatch over the DV1 daily-grid producers."""
from __future__ import annotations

from equity_feature_contracts import CanonicalBatch, ConfigSpec, ErrorCode, FeatureResult
from equity_features.ef3._common import DailyGrid, fail
from ._relative_log import RLOG_IDENTITY, compute_relative_log
from ._window_extreme import WEXT_IDENTITY, compute_window_extreme


def compute_dv1(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None], grid: DailyGrid,
                config: ConfigSpec, *, features: tuple[str, ...]) -> FeatureResult:
    """Route the complete selected request to its producer (relative log statistics: two nullable role slots; window extremes: one)."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == RLOG_IDENTITY:
        return compute_relative_log(batches, grid, config, features=features)
    if config.identity == WEXT_IDENTITY:
        return compute_window_extreme(batches, grid, config, features=features)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "DV1 producer is not implemented")
