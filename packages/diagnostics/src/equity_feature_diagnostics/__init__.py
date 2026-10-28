"""Optional pure diagnostics of supplied declarations; no source authentication."""
from ._model import (DecisionContext, DiagnosticPolicy, ReferenceDeclaration,
    RevisionIdentity, MarketCheck, KnowledgeCheck, ContextCheck, MembershipCheck,
    RevisionCheck, AdjustmentCheck, FreshnessCheck, CheckFinding, DiagnosticReport,
    Check, DiagnosticsError)
from ._evaluate import evaluate_diagnostics

__version__ = '0.1.0a2'
__all__ = ['DecisionContext', 'DiagnosticPolicy', 'ReferenceDeclaration',
    'RevisionIdentity', 'MarketCheck', 'KnowledgeCheck', 'ContextCheck',
    'MembershipCheck', 'RevisionCheck', 'AdjustmentCheck', 'FreshnessCheck',
    'CheckFinding', 'DiagnosticReport', 'Check', 'DiagnosticsError',
    'evaluate_diagnostics', '__version__']
