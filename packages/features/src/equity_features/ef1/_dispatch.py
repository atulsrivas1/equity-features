"""Closed public EF1 dispatch, preserving the existing anchor implementation."""
from __future__ import annotations

from equity_feature_contracts import CanonicalBatch, ConfigSpec, EntityKey, FeatureResult
from ._anchor import compute_ef1 as compute_anchor
from ._clock import compute_clock
from ._context import decode_ef1_context


def compute_ef1(batches: tuple[CanonicalBatch, ...] | list[CanonicalBatch], config: ConfigSpec,
                *, entity: EntityKey) -> FeatureResult:
    """Return the complete selected producer with original actual input bindings."""
    context = decode_ef1_context(config)
    if context["producer"] == "clock":
        return compute_clock(batches, config, entity=entity)
    return compute_anchor(batches, config, entity=entity)
