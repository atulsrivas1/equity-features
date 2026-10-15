"""Narrow public comparisons; no callbacks or retained borrowed request graphs."""
from __future__ import annotations
import equity_feature_diagnostics as d
from equity_feature_evidence import ContentFingerprint
from ._model import (ConformanceError,ContextSnapshot,PolicySnapshot,FindingSnapshot,
    DiagnosticSnapshot,DiagnosticOutcome,ContentOutcome,SuiteSummary,Outcome,
    require,label,copy_snapshot)


def check_diagnostics(case_id: str, context: d.DecisionContext, policy: d.DiagnosticPolicy,
                      checks: tuple[d.Check, ...], expected: DiagnosticSnapshot) -> DiagnosticOutcome:
    """Evaluate supplied declarations and compare with independent assertions."""
    try:
        label(case_id); assertion=copy_snapshot(expected)
        require(type(context) is d.DecisionContext and type(policy) is d.DiagnosticPolicy)
        require(type(checks) in (tuple,list)); require(1 <= len(checks) <= 32,'limit_exceeded')
        require(all(type(c) in (d.MarketCheck,d.KnowledgeCheck,d.ContextCheck,d.MembershipCheck,
                    d.RevisionCheck,d.AdjustmentCheck,d.FreshnessCheck) for c in checks))
        facts=0
        for c in checks:
            if type(c) is d.MembershipCheck:
                require(type(c.facts) in (tuple,list)); require(len(c.facts) <= 128,'limit_exceeded')
                facts+=len(c.facts)
        require(facts <= 512,'limit_exceeded')
        report=d.evaluate_diagnostics(context,policy,checks)
        r=report.context; p=report.policy
        observed=DiagnosticSnapshot(
            ContextSnapshot(r.namespace,r.entity.instrument_id,r.entity.session_id,
                r.availability.market_cutoff_ns,r.availability.knowledge_cutoff_ns,r.availability.evaluation_ns),
            PolicySnapshot(p.policy_id,p.mode,p.unknown_action),
            tuple(FindingSnapshot(f.check_id,f.subject_id,f.kind,f.content,f.status,f.severity,
                    f.reasons,f.assessed,f.unknown_prerequisites,f.age_ns) for f in report.findings),
            report.requested_count,report.passed_count,report.failed_count,report.unknown_count,
            report.assessed_count,report.unknown_prerequisite_count,report.not_requested,
            report.admission,report.source_authenticated,report.historical_acquisition_verified,report.schema_version)
        return DiagnosticOutcome(case_id,assertion,observed)
    except ConformanceError:
        raise
    except d.DiagnosticsError as exc:
        code=exc.code
    except Exception:
        code='invalid_schema'
    # Raise after leaving the handler so the original exception is not retained
    # as __context__, including for callers that inspect more than traceback text.
    raise ConformanceError(code)


def compare_content(case_id: str, before: ContentFingerprint | None,
                    after: ContentFingerprint | None, expected_relation: str) -> ContentOutcome:
    """Compare supplied scalar fingerprints; missing remains unknown."""
    try: return ContentOutcome(case_id,before,after,expected_relation)
    except ConformanceError: raise
    except Exception: pass
    raise ConformanceError()


def summarize(outcomes: tuple[Outcome, ...]) -> SuiteSummary:
    """Aggregate ordinary test records without authenticating their origin."""
    try: return SuiteSummary(outcomes)
    except ConformanceError: raise
    except Exception: pass
    raise ConformanceError()
