"""Shared DV1 configuration checks, one copy for all DV1 producers. Internal, synthetic, pre-release.

Contract stage order (identical in every producer): parameters (the producer's own shape check, before this module),
then units and adjustment (`check_units`), then labels, the market cutoff and the policy label (`check_tail`). The
currency form (RF22: three uppercase letters) is checked by every producer; the adjustment pair (RF21: raw with raw-v1,
or split with split-factors-v1) only by producers that carry an adjustment basis. The core spread producer has no
adjustment basis and calls `check_currency` only.
"""
from __future__ import annotations

from equity_feature_contracts import AdjustmentSpec, AvailabilitySpec, CanonicalBatch, ErrorCode, PriceUnit
from equity_features.ef3._common import DailyGrid, fail, label

# The two declared adjustment labels and the policy each one carries (the EF5 vocabulary).
ADJUSTMENTS = frozenset({("raw", "raw-v1"), ("split", "split-factors-v1")})


def check_currency(price_unit: object) -> PriceUnit:
    """RF22: an explicit PriceUnit with a three-letter uppercase currency, else INVALID_UNIT."""
    if (type(price_unit) is not PriceUnit or type(price_unit.currency) is not str or len(price_unit.currency) != 3
            or not all("A" <= c <= "Z" for c in price_unit.currency)):
        fail(ErrorCode.INVALID_UNIT, "an explicit PriceUnit with a three-letter uppercase currency is required")
    return price_unit


def check_adjustment_pair(adjustment: AdjustmentSpec) -> None:
    """RF21: the declared basis and its policy label form a declared pair, else UNSUPPORTED_ADJUSTMENT."""
    if (adjustment.basis, adjustment.policy_version) not in ADJUSTMENTS:
        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT,
             "declared basis must be unadjusted (raw-v1) or split_adjusted (split-factors-v1)")


def check_units(availability: object, adjustment: object,
                price_unit: object) -> tuple[AvailabilitySpec, AdjustmentSpec, PriceUnit]:
    """Daily-grid producers: concrete timing/action, currency form (RF22), adjustment pair (RF21), in that order."""
    if type(availability) is not AvailabilitySpec or type(adjustment) is not AdjustmentSpec:
        fail(ErrorCode.INVALID_CONFIG, "concrete timing/action required")
    unit = check_currency(price_unit)
    check_adjustment_pair(adjustment)
    return availability, adjustment, unit


def check_tail(grid: DailyGrid, availability: AvailabilitySpec, adjustment: AdjustmentSpec, price_unit: PriceUnit,
               policy: str, expected_policy: str, policy_message: str) -> None:
    """Daily-grid producers: labels, the market cutoff window, then the policy label (the version stage)."""
    for value in (adjustment.policy_version, adjustment.action_snapshot, adjustment.anchor, price_unit.currency):
        label(value)
    if availability.reconstruction_reason is not None:
        label(availability.reconstruction_reason)
    target = grid.target
    # A target session still forming at the market cutoff is a lost slot (future_market), not a refusal.
    if not target.open_ns <= availability.market_cutoff_ns <= grid.sessions[-1].close_ns:
        fail(ErrorCode.BOUNDS, "market cutoff must lie between the target session open and the last grid session close")
    if policy != expected_policy:
        fail(ErrorCode.INCOMPATIBLE_VERSION, policy_message)


def check_coverage_declared(batch: CanonicalBatch | None) -> None:
    """Shared admission (RF11): rows delivered with no per-slot coverage entry are never read as complete."""
    if batch is not None:
        if type(batch) is not CanonicalBatch:
            fail(ErrorCode.INVALID_SCHEMA, "concrete canonical batch required")
        if batch.row_count and not batch.metadata.interval_coverage:
            fail(ErrorCode.INVALID_SCHEMA, "coverage not declared")
