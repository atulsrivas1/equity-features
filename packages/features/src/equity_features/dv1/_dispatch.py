"""Closed public DV1 dispatch over the DV1 daily-grid producers."""
from __future__ import annotations

from equity_feature_contracts import CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, FeatureResult
from equity_features.ef3._common import DailyGrid, fail
from ._atr_simple_mean import ATR_IDENTITY, compute_atr_simple_mean
from ._core_spread import CORE_IDENTITY, compute_core_spread
from ._relative_log import RLOG_IDENTITY, compute_relative_log
from ._window_extreme import WEXT_IDENTITY, compute_window_extreme


def compute_dv1(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None], grid: DailyGrid | None,
                config: ConfigSpec, *, features: tuple[str, ...], entity: EntityKey | None = None) -> FeatureResult:
    """Route the complete selected request to its producer (relative log statistics: two nullable role slots; window
    extremes and ATR: one daily role on the grid; core spread: the legs role and the result entity, no grid)."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == CORE_IDENTITY:
        if type(entity) is not EntityKey:
            fail(ErrorCode.INVALID_CONFIG, "the result entity is required")
        return compute_core_spread(batches, config, entity=entity, features=features)
    if config.identity == RLOG_IDENTITY:
        return compute_relative_log(batches, _grid(grid), config, features=features)
    if config.identity == WEXT_IDENTITY:
        return compute_window_extreme(batches, _grid(grid), config, features=features)
    if config.identity == ATR_IDENTITY:
        return compute_atr_simple_mean(batches, _grid(grid), config, features=features)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "DV1 producer is not implemented")


def _grid(grid: DailyGrid | None) -> DailyGrid:
    if type(grid) is not DailyGrid:
        fail(ErrorCode.INVALID_CONFIG, "the daily grid is required")
    return grid
