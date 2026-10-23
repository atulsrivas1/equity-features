"""Closed public dispatch over the EF3 robust history, volume-pace and mean-ratio producers (no daily grid)."""
from __future__ import annotations

from equity_feature_contracts import CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, FeatureResult
from ._common import fail
from ._mean import MEAN_IDENTITY, compute_volume_ratio_mean
from ._pace import PACE_IDENTITY, compute_volume_pace_robust
from ._robust_history import ROBUST_IDENTITY, compute_robust_history


def compute_ef3_robust(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None], config: ConfigSpec,
                       *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Route the complete selected request to its producer by the config identity."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == ROBUST_IDENTITY:
        return compute_robust_history(batches, config, entity=entity, features=features)
    if config.identity == PACE_IDENTITY:
        return compute_volume_pace_robust(batches, config, entity=entity, features=features)
    if config.identity == MEAN_IDENTITY:
        return compute_volume_ratio_mean(batches, config, entity=entity, features=features)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF3 producer is not implemented")
