"""Pure experimental feature consumers; no feature recomputation or future labels."""
from ._model import (Entity, FeatureRequirement, Predicate, Ranking, StrategyConfig, StrategyRequest,
    PredicateDisposition, StrategyRow, StrategyResult, InputSemantic, IntervalSemantic, StrategyError)
from ._codec import encode, digest, feature_result_digest, input_semantic_digest
from ._engine import scan

__version__ = '0.1.0a1'
__all__ = ['__version__', 'Entity', 'FeatureRequirement', 'Predicate', 'Ranking', 'StrategyConfig',
    'StrategyRequest', 'PredicateDisposition', 'StrategyRow', 'StrategyResult', 'InputSemantic',
    'IntervalSemantic', 'StrategyError', 'scan', 'encode', 'digest', 'feature_result_digest', 'input_semantic_digest']
