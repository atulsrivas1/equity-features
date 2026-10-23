"""Closed public EF2 dispatch."""
from __future__ import annotations

from equity_feature_contracts import CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, FeatureResult
from ._retracement import RETRACEMENT_IDENTITY, compute_retracement_level, fail


def compute_ef2(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None], config: ConfigSpec,
                *, entity: EntityKey) -> FeatureResult:
    """Return the complete selected producer with original actual input bindings."""
    if type(config) is not ConfigSpec or config.identity != RETRACEMENT_IDENTITY:
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF2 producer is not implemented")
    return compute_retracement_level(batches, config, entity=entity)
