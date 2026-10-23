"""Closed public dispatch over the EF4 quote dynamics and VWAP path producers."""
from __future__ import annotations

from equity_feature_contracts import CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, FeatureResult
from ..ef3._common import fail
from ._quote import QUOTE_IDENTITY, compute_quote_dynamics
from ._vwap import VWAP_IDENTITY, compute_vwap_path


def compute_quote_vwap(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None], config: ConfigSpec,
                *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Route the complete selected request to its producer by the config identity."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == QUOTE_IDENTITY:
        return compute_quote_dynamics(batches, config, entity=entity, features=features)
    if config.identity == VWAP_IDENTITY:
        return compute_vwap_path(batches, config, entity=entity, features=features)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF4 producer is not implemented")
