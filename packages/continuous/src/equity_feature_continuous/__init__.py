"""Opt-in pure supplied continuous contracts and exact finite batch kernels."""
from ._model import (ContinuousConfig, ContinuousInput, ContinuousResult, ConversionFact,
                     DeviationWitness, FeedFact, Leg, MetricValue, PriceObservation,
                     RoleReadiness, SelectedObservation)
from ._rational import Rational
from ._codec import (config_digest, config_from_json, from_json, input_digest,
                     input_from_json, result_digest, result_from_json, to_json)
from ._engine import compute_basis, compute_freeze, compute_reopen
from ._registry import ContinuousFeature, list_features, require_capability

__version__ = '0.1.0a2'
__all__ = ['ContinuousConfig', 'ContinuousInput', 'ContinuousResult', 'ConversionFact',
           'DeviationWitness', 'FeedFact', 'Leg', 'MetricValue', 'PriceObservation',
           'Rational', 'RoleReadiness', 'SelectedObservation', 'config_digest',
           'config_from_json', 'from_json', 'input_digest', 'input_from_json',
           'result_digest', 'result_from_json', 'to_json', 'ContinuousFeature',
           'compute_basis', 'compute_freeze', 'compute_reopen', 'list_features', 'require_capability']
