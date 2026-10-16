"""Public constructor/codec checks against pre-implementation independent literals.

These checks do not execute any cross-venue calculation kernel.
"""
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import unittest
from unittest.mock import patch

from equity_feature_contracts import AdjustmentSpec, ContractError, ErrorCode, IntervalSpec
import equity_feature_continuous as c

ROOT = Path(__file__).resolve().parents[2]
FIXTURES = json.loads((ROOT/'docs/stories/EQ112_FIXTURES.json').read_bytes())
ADMISSION = json.loads((ROOT/'docs/stories/EQ113_ADMISSION_FIXTURES.json').read_bytes())
CONFIG_ERRORS = {
    'unsupported_reconstruction', 'unsupported_duration_weighting',
    'freeze_empty_unsupported_weighting_still_error', 'basis_anchor_required',
    'basis_unused_reopen_refused', 'basis_anchor_at_window_end_refused',
    'freeze_unused_anchor_refused', 'freeze_unused_reopen_refused',
    'reopen_boundary_required', 'reopen_unused_anchor_refused',
    'reopen_boundary_at_window_start_refused', 'reopen_boundary_at_window_end_refused',
}


def pack(kind, payload):
    return json.dumps(dict(kind=kind, schema_version='1', payload=payload), sort_keys=True,
                      separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode()


class ContinuousContracts(unittest.TestCase):
    def error(self, code, function, *args, **kwargs):
        with self.assertRaises(ContractError) as caught:
            function(*args, **kwargs)
        self.assertEqual(caught.exception.code.value, code)
        return caught.exception

    def base(self):
        return c.input_from_json(pack('continuous_input', FIXTURES['cases'][0]['input']))

    def test_all_99_literal_input_admissions_and_67_digests(self):
        table = {row['case_id']: row for row in ADMISSION['records']}
        self.assertEqual(len(table), 99)
        successes = errors = 0
        for case in FIXTURES['cases']:
            with self.subTest(case=case['case_id']):
                expected = table[case['case_id']]
                raw = pack('continuous_input', case['input'])
                if expected['input_admitted']:
                    value = c.input_from_json(raw)
                    self.assertEqual(c.to_json(value), raw)
                    self.assertEqual(c.input_digest(value), case['input_digest'])
                    self.assertEqual(value.identity_digest, case['input_digest'])
                    self.assertEqual(c.from_json(raw), value)
                    successes += 1
                else:
                    self.error(expected['input_error_code'], c.input_from_json, raw)
                    errors += 1
        self.assertEqual((successes, errors), (67, 32))

    def test_all_99_config_admissions_and_87_digests(self):
        successes = errors = 0
        for case in FIXTURES['cases']:
            with self.subTest(case=case['case_id']):
                raw = pack('continuous_config', case['input']['config'])
                if case['case_id'] in CONFIG_ERRORS:
                    self.error(case['expected_error']['error_code'], c.config_from_json, raw)
                    errors += 1
                else:
                    value = c.config_from_json(raw)
                    self.assertEqual(c.to_json(value), raw)
                    self.assertEqual(c.config_digest(value), case['config_digest'])
                    self.assertEqual(value.identity_digest, case['config_digest'])
                    successes += 1
        self.assertEqual((successes, errors), (87, 12))

    def test_all_65_full_literal_result_codecs_and_digests_not_kernels(self):
        successes = 0
        for case in FIXTURES['cases']:
            if case['expected_error'] is not None:
                continue
            with self.subTest(case=case['case_id']):
                raw = pack('continuous_result', case['expected_result'])
                value = c.result_from_json(raw)
                self.assertEqual(c.to_json(value), raw)
                self.assertEqual(c.result_digest(value), case['expected_result_digest'])
                self.assertEqual(value.identity_digest, case['expected_result_digest'])
                self.assertEqual(hashlib.sha256(raw).hexdigest(), case['expected_result_digest'])
                successes += 1
        self.assertEqual(successes, 65)

    def test_rational_independent_constructor_boundaries(self):
        for case in FIXTURES['rational_cases']:
            with self.subTest(case=case['id']):
                if 'error_code' in case:
                    self.error(case['error_code'], c.Rational, *case['input'])
                else:
                    value = c.Rational(*case['input'])
                    self.assertEqual([value.numerator, value.denominator], case['expected'])
        self.assertEqual(c.Rational(2, 2), c.Rational(1, 1))
        self.error('invalid_schema', c.Rational, True, 1)
        self.error('invalid_schema', c.Rational, 1, False)
        self.error('bounds', c.Rational, 1, 0)
        self.error('bounds', c.Rational, 1, -1)

    def test_frozen_and_detached_concrete_collections(self):
        original = self.base()
        rows = list(original.continuous.observations)
        leg = replace(original.continuous, observations=rows)
        rows.clear()
        self.assertEqual(len(leg.observations), 1)
        feeds = list(original.feed_facts)
        snapshot = replace(original, continuous=leg, feed_facts=feeds)
        before = c.to_json(snapshot)
        feeds.clear()
        self.assertEqual(c.to_json(snapshot), before)
        self.assertIs(type(snapshot.feed_facts), tuple)
        with self.assertRaises(FrozenInstanceError):
            snapshot.config = original.config
        with self.assertRaises(FrozenInstanceError):
            snapshot.continuous.observations[0].price = 1

    def test_caller_iterators_and_subclasses_never_admitted(self):
        original = self.base()
        calls = []
        class Iterator:
            def __iter__(self):
                calls.append('iterated')
                raise AssertionError('caller iterator ran')
        class String(str):
            def strip(self):
                calls.append('stripped')
                raise AssertionError('caller string callback ran')
        self.error('invalid_schema', replace, original.continuous, observations=Iterator())
        self.error('invalid_schema', replace, original, feed_facts=Iterator())
        self.error('invalid_schema', c.PriceObservation, String('private-synthetic'), 1, 0, 1, 1)
        self.assertEqual(calls, [])

    def test_literal_row_fact_and_topk_limits(self):
        value = self.base()
        self.error('bounds', replace, value.continuous,
                   observations=[value.continuous.observations[0]]*4097)
        self.error('bounds', replace, value, feed_facts=[value.feed_facts[0]]*257)
        self.error('bounds', replace, value, conversion_facts=[value.conversion_facts[0]]*257)
        self.error('invalid_config', replace, value.config, top_k=0)
        self.error('invalid_config', replace, value.config, top_k=33)

    def test_identifier_utf8_bounds_and_fixed_errors(self):
        self.assertEqual(c.PriceObservation('e'*128, 1, 0, 1, 1).observation_id, 'e'*128)
        exc = self.error('bounds', c.PriceObservation, 'e'*129, 1, 0, 1, 1)
        self.assertNotIn('e'*129, str(exc))
        self.error('bounds', c.PriceObservation, '\u00e9'*65, 1, 0, 1, 1)
        self.error('invalid_schema', c.PriceObservation, '\ud800', 1, 0, 1, 1)
        self.error('invalid_schema', c.PriceObservation, 'row', 1, True, 1, 1)
        self.error('invalid_schema', c.PriceObservation, 'row', 1, 0, True, 1)

    def test_duplicate_unknown_trailing_nonfinite_closed_json(self):
        raw = pack('continuous_input', FIXTURES['cases'][0]['input'])
        self.error('invalid_schema', c.input_from_json, raw+b'{}')
        self.error('invalid_schema', c.from_json, raw.replace(b'"schema_version":"1"', b'"schema_version":"1","schema_version":"1"', 1))
        root = json.loads(raw); root['unknown'] = 1
        self.error('invalid_schema', c.from_json, json.dumps(root).encode())
        root = json.loads(raw); root['payload']['continuous']['observations'][0]['price'] = float('nan')
        self.error('invalid_schema', c.from_json, json.dumps(root).encode())
        for bad in [b'null', b'[]', b'1', b'"text"', b'\xff', b'{', b'NaN', b'Infinity']:
            self.error('invalid_schema', c.from_json, bad)

    def test_wrong_kind_version_and_old_core_coercion(self):
        value = self.base(); raw = c.to_json(value)
        self.error('invalid_schema', c.config_from_json, raw)
        self.error('invalid_schema', c.result_from_json, raw)
        root = json.loads(raw); root['kind'] = 'feature_result'
        self.error('invalid_schema', c.from_json, json.dumps(root).encode())
        root = json.loads(raw); root['schema_version'] = '2'
        self.error('incompatible_version', c.from_json, json.dumps(root).encode())
        self.error('invalid_schema', c.to_json, IntervalSpec('old-core', 1, 2))
        self.error('invalid_schema', c.from_json, raw.decode())
        self.assertIn('compute_basis', c.__all__)
        self.assertTrue(callable(c.compute_basis))

    def test_typed_byte_limits_precede_json_parser(self):
        for decoder, size in [(c.config_from_json, 65536), (c.input_from_json, 16777216),
                              (c.result_from_json, 1048576)]:
            with self.subTest(decoder=decoder.__name__), patch('json.loads', side_effect=AssertionError('parser ran')):
                self.error('bounds', decoder, b' '*(size+1))

    def test_wire_rational_and_digest_literal_negatives(self):
        payload = json.loads(json.dumps(FIXTURES['cases'][0]['expected_result']))
        payload['metrics'][0]['value'] = {'numerator': 2, 'denominator': 2}
        self.error('invalid_schema', c.result_from_json, pack('continuous_result', payload))
        payload = json.loads(json.dumps(FIXTURES['cases'][0]['expected_result']))
        payload['config_digest'] = 'a'*64+'\n'
        self.error('invalid_schema', c.result_from_json, pack('continuous_result', payload))

    def test_role_and_result_structural_contradictions(self):
        self.error('invalid_schema', c.RoleReadiness, 'continuous', 'ready', ['null_price'], [])
        self.error('invalid_schema', c.RoleReadiness, 'continuous', 'blocked', [], ['/continuous/observations/0'])
        self.error('invalid_schema', c.RoleReadiness, 'continuous', 'unavailable', ['null_price', 'null_price'], [])
        self.error('invalid_schema', c.RoleReadiness, 'continuous', 'ready', [], ['/continuous/observations/00'])
        payload = json.loads(json.dumps(FIXTURES['cases'][0]['expected_result']))
        payload['status'] = 'missing_input'
        self.error('invalid_schema', c.result_from_json, pack('continuous_result', payload))

    def test_composite_error_order_precedes_later_collections(self):
        base = FIXTURES['cases'][0]['input']
        p = json.loads(json.dumps(base))
        p['reference']['price_unit']['currency'] = 'EUR'
        p['feed_facts'] = False
        with self.subTest(case='leg_identity_before_feed_collection'):
            self.error('invalid_unit', c.input_from_json, pack('continuous_input', p))
        p = json.loads(json.dumps(base))
        extra = json.loads(json.dumps(p['feed_facts'][0]))
        extra['fact_id'] = 'overlapping-domain'
        p['feed_facts'].append(extra)
        p['conversion_facts'][0]['continuous_units_denominator'] = 0
        with self.subTest(case='feed_overlap_before_conversion_fields'):
            self.error('invalid_schema', c.input_from_json, pack('continuous_input', p))

    def test_trimmed_identities_on_direct_and_wire_boundaries(self):
        for value in (' padded', 'padded ', '\tpadded', 'padded\n'):
            self.error('invalid_schema', c.PriceObservation, value, 99, 0, 100, 99)
            for path in (('config', 'identity'), ('continuous', 'instrument_id'),
                         ('continuous', 'feed_id')):
                payload = json.loads(json.dumps(FIXTURES['cases'][0]['input']))
                payload[path[0]][path[1]] = value
                self.error('invalid_schema', c.input_from_json, pack('continuous_input', payload))

    def test_selected_result_cap_order_and_population(self):
        literal = FIXTURES['cases'][0]['expected_result']
        for selections in ([], list(reversed(literal['selected'])),
                           [literal['selected'][1]],
                           [literal['selected'][0], {'role': 'continuous', 'observation_id': 'extra'}, literal['selected'][1]]):
            payload = json.loads(json.dumps(literal)); payload['selected'] = selections
            self.error('invalid_schema', c.result_from_json, pack('continuous_result', payload))
        payload = json.loads(json.dumps(literal))
        payload['selected'] = [{'role': 'continuous', 'observation_id': str(i)} for i in range(4098)]
        self.error('bounds', c.result_from_json, pack('continuous_result', payload))
        result = c.result_from_json(pack('continuous_result', literal))
        self.error('bounds', replace, result, selected=[c.SelectedObservation('continuous', str(i)) for i in range(4098)])
        object.__setattr__(result, 'selected', tuple(reversed(result.selected)))
        self.error('invalid_schema', c.to_json, result)
        freeze = next(case['expected_result'] for case in FIXTURES['cases'] if case['case_id'] == 'freeze_count_weighted_all_samples')
        for mutate in ('population', 'witness'):
            payload = json.loads(json.dumps(freeze))
            if mutate == 'population': payload['population_count'] = 2
            else: payload['top_k'][0]['reference_id'] = 'not-selected'
            self.error('invalid_schema', c.result_from_json, pack('continuous_result', payload))

    def test_nested_role_scalar_validation_precedes_aggregate_equality(self):
        calls = []
        class String(str):
            def __eq__(self, other):
                calls.append('compared')
                raise AssertionError('nested caller comparison ran')
            __hash__ = str.__hash__
        result = c.result_from_json(pack('continuous_result', FIXTURES['cases'][0]['expected_result']))
        object.__setattr__(result.roles[0], 'role', String('continuous_coverage'))
        self.error('invalid_schema', c.to_json, result)
        self.assertEqual(calls, [])

    def test_unavailable_freeze_retains_exact_population_on_every_boundary(self):
        literal = next(case['expected_result'] for case in FIXTURES['cases'] if case['case_id'] == 'freeze_unknown_population_not_filtered')
        payload = json.loads(json.dumps(literal)); payload['population_count'] = None
        self.error('invalid_schema', c.result_from_json, pack('continuous_result', payload))
        result = c.result_from_json(pack('continuous_result', literal))
        self.error('invalid_schema', replace, result, population_count=None)
        object.__setattr__(result, 'population_count', None)
        self.error('invalid_schema', c.to_json, result)

    def test_reused_adjustment_scalar_cannot_run_comparison_callback(self):
        calls = []
        class String(str):
            enabled = False
            def __eq__(self, other):
                if self.enabled:
                    calls.append('compared')
                    raise AssertionError('supplied comparison callback ran')
                return str.__eq__(self, other)
            __hash__ = str.__hash__
        adjustment = AdjustmentSpec(basis=String('raw'))
        String.enabled = True
        self.error('invalid_schema', replace, self.base().continuous, adjustment=adjustment)
        self.assertEqual(calls, [])


if __name__ == '__main__':
    unittest.main()
