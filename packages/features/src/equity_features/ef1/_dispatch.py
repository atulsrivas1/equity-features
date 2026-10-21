"""Closed public EF1 dispatch, preserving the existing anchor implementation."""
from __future__ import annotations

from typing import cast

from equity_feature_contracts import CanonicalBatch, ConfigSpec, EntityKey, FeatureResult
from ._anchor import compute_ef1 as compute_anchor
from ._clock import compute_clock
from ._status import compute_status
from ._reference import compute_reference
from ._path import compute_path_gap, compute_path_drive
from ._period import compute_period_phase
from ._observable import compute_observable
from ._context import decode_ef1_context


def compute_ef1(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None] | list[CanonicalBatch], config: ConfigSpec,
                *, entity: EntityKey) -> FeatureResult:
    """Return the complete selected producer with original actual input bindings."""
    context = decode_ef1_context(config)
    if context["producer"] == "regular_bar_prices":
        from ._regular_bar_prices import compute_regular_bar_prices
        return compute_regular_bar_prices(batches, config, entity=entity)
    if context["producer"] == "path_gap_endpoint":
        from ._gap_endpoint import compute_gap_endpoint
        return compute_gap_endpoint(batches, config, entity=entity)
    if context["producer"] == "daily_observations":
        from ._daily import compute_daily
        return compute_daily(batches, config, entity=entity)
    if context["producer"] in ("opening_trade", "opening_trade_seconds", "status_history"):
        return compute_observable(batches, config, entity=entity)
    if context["producer"] in ("reference_classification", "reference_action"):
        return compute_reference(batches, config, entity=entity)
    if context["producer"] == "status":
        return compute_status(batches, config, entity=entity)
    # Legacy producers retain their own concrete present-only validation.
    present = cast(tuple[CanonicalBatch, ...] | list[CanonicalBatch], batches)
    if context["producer"] in ("period", "extended"):
        return compute_period_phase(present, config, entity=entity)
    if context["producer"] == "clock":
        return compute_clock(present, config, entity=entity)
    if context["producer"] == "path_gap":
        return compute_path_gap(present, config, entity=entity)
    if context["producer"] == "path_drive":
        return compute_path_drive(present, config, entity=entity)
    return compute_anchor(present, config, entity=entity)
