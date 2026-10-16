"""Opt-in pure supplied continuous data contracts; kernels are a later capability."""
from ._model import (ContinuousConfig, ContinuousInput, ContinuousResult, ConversionFact,
                     DeviationWitness, FeedFact, Leg, MetricValue, PriceObservation,
                     RoleReadiness, SelectedObservation)
from ._rational import Rational
from ._codec import (config_digest, config_from_json, from_json, input_digest,
                     input_from_json, result_digest, result_from_json, to_json)

__version__ = '0.1.0a1'
__all__ = ['ContinuousConfig', 'ContinuousInput', 'ContinuousResult', 'ConversionFact',
           'DeviationWitness', 'FeedFact', 'Leg', 'MetricValue', 'PriceObservation',
           'Rational', 'RoleReadiness', 'SelectedObservation', 'config_digest',
           'config_from_json', 'from_json', 'input_digest', 'input_from_json',
           'result_digest', 'result_from_json', 'to_json']
