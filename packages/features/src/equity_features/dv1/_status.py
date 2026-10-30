"""Shared DV1 status resolution (one copy for the daily-grid producers). Internal, synthetic, pre-release.

The first applicable reason in the precedence fixes the status; every applicable reason is still reported by the caller
(lexical order). Reasons outside the table map to `missing_input`.
"""
from __future__ import annotations

from equity_feature_contracts import Reason, Status

PRECEDENCE = (Reason.ABSENT_INPUT, Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE, Reason.NULL_FIELD,
              Reason.INELIGIBLE, Reason.GOVERNED_GAP, Reason.FUTURE_MARKET, Reason.PARTIAL_UNIVERSE,
              Reason.INSUFFICIENT_HISTORY, Reason.NO_ELIGIBLE_OBSERVATIONS, Reason.ZERO_DENOMINATOR)
STATUS = {Reason.GOVERNED_GAP: Status.INCOMPLETE_COVERAGE, Reason.FUTURE_MARKET: Status.INCOMPLETE_COVERAGE,
          Reason.PARTIAL_UNIVERSE: Status.INCOMPLETE_COVERAGE, Reason.INSUFFICIENT_HISTORY: Status.INSUFFICIENT_HISTORY,
          Reason.NO_ELIGIBLE_OBSERVATIONS: Status.NOT_APPLICABLE, Reason.ZERO_DENOMINATOR: Status.NOT_APPLICABLE}


def status_of(reasons: set[Reason]) -> Status:
    first = next((reason for reason in PRECEDENCE if reason in reasons), None)
    return Status.AVAILABLE if first is None else STATUS.get(first, Status.MISSING_INPUT)
