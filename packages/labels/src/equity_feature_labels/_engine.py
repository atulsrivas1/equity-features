"""Maturity precedes arithmetic; inputs are supplied facts only."""
from __future__ import annotations
import math
from ._model import LabelRequest, LabelResult, require
from ._codec import path_content_digest


def evaluate_label(request: LabelRequest) -> LabelResult:
    require(type(request) is LabelRequest)
    t0 = request.origin.anchor_event_ns
    t1 = t0 + request.config.horizon_ns
    status = 'pending'
    reasons: tuple[str, ...] = ()
    value: float | None = None
    known: int | None = None
    endpoints = {row.event_ns: row for row in request.observations if row.event_ns in (t0, t1)}
    if t1 > request.availability.market_cutoff_ns:
        reasons = ('horizon_not_elapsed',)
    elif t0 not in endpoints or t1 not in endpoints:
        status = 'incomplete'
        reasons = tuple(reason for stamp, reason in ((t0, 'missing_anchor_endpoint'),
            (t1, 'missing_horizon_endpoint')) if stamp not in endpoints)
    else:
        anchor, end = endpoints[t0], endpoints[t1]
        stamps = (anchor.known_at_ns, end.known_at_ns, anchor.basis.known_at_ns)
        reasons = (('unknown_availability',) if None in stamps else ()) + (
            ('future_knowledge',) if any(s is not None and s > request.availability.knowledge_cutoff_ns for s in stamps) else ())
        if not reasons:
            if anchor.basis.effective_ns > t1:
                reasons = ('basis_not_effective',)
            else:
                quotient = end.price / anchor.price
                require(math.isfinite(quotient), 'numerical_bounds')
                require(quotient != 0.0, 'precision_bounds')
                value = quotient - 1.0
                require(math.isfinite(value), 'numerical_bounds')
                known = max(s for s in stamps if s is not None)
                status = 'mature'
    return LabelResult(request.origin.entity, request.origin.identity_digest, request.config.identity_digest,
        request.identity_digest, path_content_digest(request.observations), request.availability, t1,
        status, reasons, value, known)
