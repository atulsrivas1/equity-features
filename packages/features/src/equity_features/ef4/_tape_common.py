"""Shared trade admission, knowledge flags and counts of the EF4 tape producers (ef4-tape1, ef4-notional1); pure, no I/O.

Both producers admit the trade batch exactly as the accepted `session.trade.*` family does (`_admit_trades`: batch kind,
unit, adjustment, scope policy, scope bounds, coverage count, one entity and session, then per row duplicate, order,
bounds and positive eligible price and size). Knowledge uses the accepted `AvailabilitySpec.knowledge_reason`, so in a
`reconstruction` config no knowledge reason is raised (DP-M1). Nothing is sorted, deduplicated or defaulted.
"""
from __future__ import annotations

from typing import Any, cast

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, EntityKey, ErrorCode, Reason,
)
from equity_features.ef3._common import fail, label
from equity_features.session.bars import _columns
from equity_features.session.trades import _admit_trades

I64_MAX = 2**63 - 1


def eligibility_policy(value: object) -> str:
    """The caller's eligibility policy label (the existing `eligibility_policy` Parameter)."""
    return label(value)


def admit_trades(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey, policy: str) -> dict[str, tuple[Any, ...]]:
    """The accepted trade admission, unchanged; returns the columns by name."""
    _admit_trades(batch, config, entity, policy)
    return cast(dict[str, tuple[Any, ...]], _columns(batch))


def knowledge_flags(columns: dict[str, tuple[Any, ...]], count: int, config: ConfigSpec) -> list[Reason | None]:
    """Per delivered row (eligible or not) the knowledge reason, None when the row is known (known_at == K is known)."""
    known = columns.get("known_at_ns")
    flags: list[Reason | None] = []
    for i in range(count):
        reason = config.availability.knowledge_reason(known[i] if known is not None else None)
        flags.append(Reason(reason) if reason is not None else None)
    return flags


def require_batch_capability(feature_id: str, capability: str, features: tuple[str, ...], supported: tuple[str, ...]) -> None:
    """Unknown feature first, then the capability (batch and the listed capabilities only)."""
    if feature_id not in features:
        fail(ErrorCode.UNKNOWN_FEATURE, "unknown EF4 tape feature")
    if capability not in supported:
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "output capability is not implemented in this package version")
