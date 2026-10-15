"""Pure receipt-bound explanations; no source or execution authentication."""
from ._explain import (ExplanationError, ExplanationFinding, InputSummary,
    EvidenceReference, Explanation, explain_result, encode_explanation)

__all__ = ['ExplanationError', 'ExplanationFinding', 'InputSummary',
    'EvidenceReference', 'Explanation', 'explain_result', 'encode_explanation']
