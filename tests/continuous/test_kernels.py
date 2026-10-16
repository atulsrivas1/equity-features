"""Actual public kernels against independent pre-implementation full literals."""
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import unittest

from equity_feature_contracts import ContractError
import equity_feature_continuous as c

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = json.loads((ROOT/'docs/stories/EQ112_FIXTURES.json').read_bytes())
MANIFEST = json.loads((ROOT/'docs/stories/EQ114_CASE_MANIFEST.json').read_bytes())


def pack(kind, payload):
    return json.dumps(dict(kind=kind, schema_version='1', payload=payload), sort_keys=True,
                      separators=(',', ':'), ensure_ascii=True).encode()


class ContinuousKernels(unittest.TestCase):
    def error(self, code, function, *args, **kwargs):
        with self.assertRaises(ContractError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code.value, code)

    def test_all_99_allocated_independent_cases_and_input_preservation(self):
        functions = {'compute_basis': c.compute_basis, 'compute_freeze': c.compute_freeze,
                     'compute_reopen': c.compute_reopen}
        counts = {'full_result': 0, 'structural_error': 0, 'arithmetic_overflow': 0}
        self.assertEqual(len(MANIFEST['records']), 99)
        for case, allocation in zip(FIXTURES['cases'], MANIFEST['records']):
            with self.subTest(case=case['case_id']):
                self.assertEqual(allocation['case_id'], case['case_id'])
                canonical = json.dumps(case, sort_keys=True, separators=(',', ':'), ensure_ascii=True).encode()
                self.assertEqual(hashlib.sha256(canonical).hexdigest(), allocation['fixture_case_sha256'])
                raw = pack('continuous_input', case['input'])
                expected = allocation['expectation']; counts[expected] += 1
                if expected == 'structural_error':
                    self.error(allocation['error_code'], c.input_from_json, raw)
                    continue
                value = c.input_from_json(raw)
                config_before = c.to_json(value.config)
                function = functions[allocation['function']]
                if expected == 'arithmetic_overflow':
                    self.error('overflow', function, value)
                else:
                    result = function(value)
                    self.assertIs(type(result), c.ContinuousResult)
                    self.assertEqual(json.loads(c.to_json(result))['payload'], case['expected_result'])
                    self.assertEqual(c.result_digest(result), case['expected_result_digest'])
                    self.assertEqual(result.identity_digest, case['expected_result_digest'])
                    self.assertEqual(c.from_json(c.to_json(result)), result)
                self.assertEqual(c.to_json(value), raw)
                self.assertEqual(c.to_json(value.config), config_before)
                self.assertEqual(c.input_digest(value), case['input_digest'])
        self.assertEqual(counts, {'full_result': 65, 'structural_error': 32, 'arithmetic_overflow': 2})

    def test_exact_dispatch_and_structural_revalidation_precede_operation(self):
        basis = c.input_from_json(pack('continuous_input', FIXTURES['cases'][0]['input']))
        freeze_case = next(x for x in FIXTURES['cases'] if x['case_id']=='freeze_count_weighted_all_samples')
        freeze = c.input_from_json(pack('continuous_input', freeze_case['input']))
        self.error('invalid_config', c.compute_basis, freeze)
        self.error('invalid_config', c.compute_freeze, basis)
        self.error('invalid_config', c.compute_reopen, basis)
        calls = []
        class Callback:
            def __eq__(self, other):
                calls.append('comparison')
                raise AssertionError('caller callback ran')
        for function in (c.compute_basis, c.compute_freeze, c.compute_reopen):
            self.error('invalid_schema', function, Callback())
        corrupted = replace(basis.config)
        object.__setattr__(corrupted, 'operation', Callback())
        snapshot = replace(basis)
        object.__setattr__(snapshot, 'config', corrupted)
        self.error('invalid_schema', c.compute_freeze, snapshot)
        self.assertEqual(calls, [])

    def test_own_six_feature_metadata_is_exact_immutable_and_batch_only(self):
        records = c.list_features()
        expected = (
            ('cross_venue.basis', 'basis', 'reference_currency_per_reference_quantity'),
            ('cross_venue.premium', 'basis', 'ratio'),
            ('cross_venue.freeze_max_abs', 'freeze', 'reference_currency_per_reference_quantity'),
            ('cross_venue.freeze_mean_abs', 'freeze', 'reference_currency_per_reference_quantity'),
            ('cross_venue.reopen_gap', 'reopen', 'reference_currency_per_reference_quantity'),
            ('cross_venue.reopen_premium', 'reopen', 'ratio'))
        self.assertIs(type(records), tuple)
        self.assertIs(c.list_features(), records)
        self.assertEqual(tuple((r.id, r.operation, r.unit) for r in records), expected)
        for record in records:
            self.assertIs(type(record), c.ContinuousFeature)
            self.assertEqual((record.algorithm_version, record.batch, record.update, record.merge, record.restore),
                             ('1', True, False, False, False))
            self.assertIsNone(c.require_capability(record.id, 'batch'))
            for mode in ('update', 'merge', 'restore', 'streaming', ''):
                self.error('unsupported_capability', c.require_capability, record.id, mode)
            with self.assertRaises(FrozenInstanceError):
                record.batch = False
            self.error('unsupported_capability', replace, record, unit='ratio' if record.unit!='ratio' else 'percent')
            self.error('unsupported_capability', replace, record, batch=False)
            self.error('invalid_schema', replace, record, batch=1)
        self.error('unsupported_capability', c.require_capability, 'old.unknown', 'batch')
        self.error('invalid_schema', c.require_capability, 1, 'batch')
        self.error('invalid_schema', c.require_capability, records[0].id, True)

    def test_complete_admitted_input_oversize_result_refuses_before_return(self):
        raw = (ROOT/'docs/stories/EQ114_OVERSIZE_INPUT.json').read_bytes()
        self.assertEqual(len(raw), 1885760)
        self.assertEqual(hashlib.sha256(raw).hexdigest(), 'f0bec7b0d8ee164168e8586ee259c1739b47ba110a70ebe0cf8af45d28db1a2f')
        value = c.input_from_json(raw)
        self.assertEqual(len(value.continuous.observations), 4096)
        self.assertTrue(all(len(row.observation_id.encode('utf-8'))==128 for row in value.continuous.observations))
        self.assertEqual(4096*376, 1540096)
        self.assertGreater(1540096, 1048576)
        self.error('bounds', c.compute_freeze, value)
        self.assertEqual(c.to_json(value), raw)

    def test_empty_freeze_old_held_reference_keeps_population_blocked(self):
        case = next(x for x in FIXTURES['cases'] if x['case_id']=='freeze_complete_empty_no_conversion_consumed')
        value = c.input_from_json(pack('continuous_input', case['input']))
        value = replace(value, config=replace(value.config, max_reference_age_ns=0, max_mismatch_ns=0))
        result = c.compute_freeze(value)
        self.assertEqual(result.status, 'missing_input')
        self.assertEqual(result.population_count, 0)
        population, reference = result.roles[2:4]
        self.assertEqual((population.status, population.reasons, population.proofs), ('blocked', (), ()))
        self.assertEqual((reference.status, reference.reasons), ('unavailable', ('stale_observation', 'mismatch')))
        self.assertIsNone(result.available_at_ns)
        self.assertEqual(tuple(metric.value for metric in result.metrics), (None, None))
        self.assertEqual(result.top_k, ())
