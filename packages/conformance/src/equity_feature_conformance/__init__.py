"""Optional pure external tests of supplied declarations; matching is not safety."""
from ._model import (ConformanceError,ContextSnapshot,PolicySnapshot,FindingSnapshot,
    DiagnosticSnapshot,DiagnosticOutcome,ContentOutcome,SuiteSummary,Outcome)
from ._run import check_diagnostics,compare_content,summarize

__version__ = '0.1.0a2'
__all__ = ['ConformanceError','ContextSnapshot','PolicySnapshot','FindingSnapshot',
    'DiagnosticSnapshot','DiagnosticOutcome','ContentOutcome','SuiteSummary','Outcome',
    'check_diagnostics','compare_content','summarize','__version__']
