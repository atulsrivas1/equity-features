"""Pure assessment of caller-supplied evidence; no implicit consumption proof."""
from __future__ import annotations

from ._model import (Check, CHECK_TYPES, DecisionContext, DiagnosticPolicy,
    CheckFinding, DiagnosticReport, MarketCheck, KnowledgeCheck, ContextCheck,
    MembershipCheck, RevisionCheck, AdjustmentCheck, FreshnessCheck, require)


def evaluate_diagnostics(context: DecisionContext, policy: DiagnosticPolicy,
                         checks: tuple[Check, ...]) -> DiagnosticReport:
    """Validate the complete bounded request, then retain every visible finding."""
    require(type(context) is DecisionContext and type(policy) is DiagnosticPolicy)
    context.__post_init__(); policy.__post_init__()
    require(type(checks) in (tuple, list))
    require(1 <= len(checks) <= 256, 'limit_exceeded')
    # Count the full input before validating individual fact contents or findings.
    require(all(type(c) in CHECK_TYPES for c in checks))
    total = 0
    for c in checks:
        if type(c) is MembershipCheck:
            require(type(c.facts) in (tuple, list))
            total += len(c.facts)
    require(total <= 4096, 'limit_exceeded')
    ids: set[str] = set(); subjects: set[tuple[str, str]] = set()
    for c in checks:
        c.__post_init__()
        require(c.check_id not in ids and (c.kind, c.subject_id) not in subjects, 'duplicate')
        ids.add(c.check_id); subjects.add((c.kind, c.subject_id))
        if type(c) is MarketCheck and c.session is not None:
            require(c.session.namespace == context.namespace and c.session.session_id == context.entity.session_id, 'inconsistent_binding')
        if type(c) is MembershipCheck and c.reference is not None:
            require(c.reference.namespace == context.namespace and c.reference.entity == context.entity, 'inconsistent_binding')
    return DiagnosticReport(context, policy, tuple(_assess(context, c) for c in checks))


def _assess(context: DecisionContext, c: Check) -> CheckFinding:
    failures: set[str] = set(); unknowns: list[str] = []; age = None
    C = context.availability.market_cutoff_ns
    K = context.availability.knowledge_cutoff_ns
    E = context.availability.evaluation_ns
    if type(c) is MarketCheck:
        t, start, session = c.observed_ns, c.interval_start_ns, c.session
        if session is None: unknowns.append('missing_session')
        if t is None: unknowns.append('missing_market_fact')
        if c.convention == 'completed_interval':
            if start is None: unknowns.append('missing_market_fact')
            if ((t is not None and t > C) or (start is not None and start >= C)
                    or (t is not None and start is not None and start >= t)):
                failures.add('market_bound')
            if session is not None:
                if t is not None and not session.open_ns < t <= session.close_ns: failures.add('market_bound')
                if start is not None and not session.open_ns <= start < session.close_ns: failures.add('market_bound')
        elif c.convention == 'closing_auction':
            if t is not None and t != C: failures.add('market_bound')
            if session is not None and (not session.include_closing_auction or session.close_ns != C): failures.add('market_bound')
        else:
            if t is not None and t >= C: failures.add('market_bound')
            if session is not None and t is not None and not session.open_ns <= t < session.close_ns: failures.add('market_bound')
    elif type(c) is KnowledgeCheck:
        if c.known_at_ns is None: unknowns.append('missing_knowledge')
        elif c.known_at_ns > K: failures.add('late_knowledge')
    elif type(c) is ContextCheck:
        if c.observed is None: unknowns.append('missing_context')
        else:
            if c.observed.market_cutoff_ns != C: failures.add('market_cutoff_mismatch')
            if c.observed.knowledge_cutoff_ns != K: failures.add('knowledge_cutoff_mismatch')
            if c.observed.evaluation_ns != E: failures.add('evaluation_mismatch')
            if c.observed.mode != 'known_at': failures.add('reconstruction_context')
    elif type(c) is MembershipCheck:
        if c.effective_ns > C: failures.add('future_effective_query')
        full = False
        if c.reference is None: unknowns.append('missing_reference')
        else:
            if not c.reference.complete: unknowns.append('incomplete_reference')
            # Validation already proved unique in-range indices. Equal cardinality
            # proves coverage without allocating proportional to declared observed.
            full = len(c.facts) == c.reference.observed
            if not full: unknowns.append('incomplete_projection')
        if c.history != 'historical': unknowns.append('historical_proof_unknown')
        active = tuple(f for f in c.facts if f.effective_start_ns <= c.effective_ns
                       and (f.effective_end_ns is None or c.effective_ns < f.effective_end_ns))
        if len(active) > 1: failures.add('ambiguous_membership')
        if not active and c.reference is not None and c.reference.complete and full and c.history == 'historical':
            failures.add('membership_absent')
        if any(f.text is None for f in active): unknowns.append('missing_membership_text')
        if any(f.known_at_ns is None for f in active): unknowns.append('missing_knowledge')
        if any(f.text is not None and f.text != c.expected_scope for f in active): failures.add('membership_scope_mismatch')
        if any(f.known_at_ns is not None and f.known_at_ns > K for f in active): failures.add('late_knowledge')
    elif type(c) is RevisionCheck:
        if c.effective_ns > C: failures.add('future_effective_query')
        if c.expected is None: unknowns.append('missing_revision_identity')
        if c.observed is None: unknowns.append('missing_revision_identity')
        if c.expected is not None and c.observed is not None and c.expected != c.observed: failures.add('revision_mismatch')
        if c.effective_start_ns is None: unknowns.append('missing_effective_start')
        elif c.effective_ns < c.effective_start_ns: failures.add('outside_effective_interval')
        if c.effective_end_ns is not None and c.effective_ns >= c.effective_end_ns: failures.add('outside_effective_interval')
        if c.known_at_ns is None: unknowns.append('missing_knowledge')
        elif c.known_at_ns > K: failures.add('late_knowledge')
    elif type(c) is AdjustmentCheck:
        if c.expected is None: unknowns.append('missing_adjustment')
        if c.observed is None: unknowns.append('missing_adjustment')
        if c.expected_unit is None: unknowns.append('missing_adjustment')
        if c.observed_unit is None: unknowns.append('missing_adjustment')
        if c.expected is not None and c.observed is not None and c.expected != c.observed: failures.add('adjustment_mismatch')
        if c.expected_unit is not None and c.observed_unit is not None and c.expected_unit != c.observed_unit: failures.add('adjustment_mismatch')
    elif type(c) is FreshnessCheck:
        if c.observed_ns is None: unknowns.append('missing_observation')
        elif c.observed_ns > c.target_ns: failures.add('future_observation')
        else:
            age = c.target_ns - c.observed_ns
            if age > c.tolerance_ns: failures.add('stale_observation')
    status = 'failed' if failures else ('unknown' if unknowns else 'passed')
    return CheckFinding(c.check_id, c.subject_id, c.kind, c.content, status,
        {'passed':'info', 'failed':'error', 'unknown':'warning'}[status],
        tuple(sorted(failures | set(unknowns))), not unknowns, len(unknowns), age)
