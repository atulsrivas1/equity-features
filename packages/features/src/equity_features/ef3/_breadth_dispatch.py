"""Closed public dispatch over the EF3 session breadth, observed breadth and adaptive volume producers."""
from __future__ import annotations

from equity_feature_contracts import CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, FeatureResult
from ._adaptive import ADAPTIVE_IDENTITY, compute_adaptive_volume
from ._breadth import BREADTH_IDENTITY, compute_session_breadth
from ._common import fail
from ._observed import OBSERVED_IDENTITY, compute_observed_breadth


def compute_ef3_breadth(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None], config: ConfigSpec,
                        *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Route the complete selected request to its producer by the config identity."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == BREADTH_IDENTITY:
        return compute_session_breadth(batches, config, entity=entity, features=features)
    if config.identity == OBSERVED_IDENTITY:
        return compute_observed_breadth(batches, config, entity=entity, features=features)
    if config.identity == ADAPTIVE_IDENTITY:
        return compute_adaptive_volume(batches, config, entity=entity, features=features)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF3 producer is not implemented")
