"""Closed public dispatch over the EF4 tape window and notional top-K producers."""
from __future__ import annotations

from equity_feature_contracts import CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, FeatureResult
from equity_features.ef3._common import fail
from ._tape_topk import TOP_K_IDENTITY, compute_trade_top_k_notional
from ._tape_window import TAPE_IDENTITY, compute_tape_window


def compute_ef4_tape(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None], config: ConfigSpec,
                     *, entity: EntityKey, features: tuple[str, ...]) -> FeatureResult:
    """Route the complete selected request to its producer by the config identity."""
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete ConfigSpec required")
    if config.identity == TAPE_IDENTITY:
        return compute_tape_window(batches, config, entity=entity, features=features)
    if config.identity == TOP_K_IDENTITY:
        return compute_trade_top_k_notional(batches, config, entity=entity, features=features)
    fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF4 tape producer is not implemented")
