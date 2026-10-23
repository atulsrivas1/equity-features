"""Closed public dispatch over the four EF4 projection producers (routed by the configuration identity)."""
from __future__ import annotations

from equity_feature_contracts import CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, FeatureResult
from ..ef3._common import DailyGrid, fail
from ._bar_projection import BAR_IDENTITY, BarGrid, compute_bar_projection
from ._rate_projection import RATE_IDENTITY, compute_rate_projection
from ._relative_excess import RELATIVE_IDENTITY, compute_relative_excess
from ._session_projection import SESSION_IDENTITY, compute_session_projection


def compute_ef4_path_projections(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None],
                                 config: ConfigSpec, *, features: tuple[str, ...],
                                 grid: DailyGrid | BarGrid | None = None,
                                 entity: EntityKey | None = None) -> FeatureResult:
    """Route the complete selected request: grid producers take their grid, fact producers the result entity."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == SESSION_IDENTITY:
        if type(grid) is not DailyGrid:
            fail(ErrorCode.INVALID_CONFIG, "the daily grid is required")
        return compute_session_projection(batches, grid, config, features=features)
    if config.identity == BAR_IDENTITY:
        if type(grid) is not BarGrid:
            fail(ErrorCode.INVALID_CONFIG, "the bar grid is required")
        return compute_bar_projection(batches, grid, config, features=features)
    if config.identity in (RELATIVE_IDENTITY, RATE_IDENTITY):
        if type(entity) is not EntityKey:
            fail(ErrorCode.INVALID_CONFIG, "the result entity is required")
        compute = compute_relative_excess if config.identity == RELATIVE_IDENTITY else compute_rate_projection
        return compute(batches, config, entity=entity, features=features)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF4 projection producer is not implemented")
