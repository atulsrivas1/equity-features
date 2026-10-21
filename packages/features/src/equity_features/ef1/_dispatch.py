"""Closed public EF1 dispatch, preserving the existing anchor implementation."""
from __future__ import annotations

from typing import cast

from equity_feature_contracts import CanonicalBatch, ConfigSpec, EntityKey, FeatureResult
from ._anchor import compute_ef1 as compute_anchor
from ._clock import compute_clock
from ._status import compute_status
from ._context import decode_ef1_context


def compute_ef1(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None] | list[CanonicalBatch], config: ConfigSpec,
                *, entity: EntityKey) -> FeatureResult:
    """Return the complete selected producer with original actual input bindings."""
    context = decode_ef1_context(config)
    if context["producer"] == "status":
        return compute_status(batches, config, entity=entity)
    # Legacy producers retain their own concrete present-only validation.
    present = cast(tuple[CanonicalBatch, ...] | list[CanonicalBatch], batches)
    if context["producer"] == "clock":
        return compute_clock(present, config, entity=entity)
    return compute_anchor(present, config, entity=entity)
