"""Independent full synthetic composition literals, not generated expectations."""
import copy
import hashlib
import json
from pathlib import Path
import runpy
import unittest

from equity_feature_contracts import (AvailabilitySpec, ConfigSpec, ContractError,
    FeatureResult, IntervalSpec, ResultMetadata, SessionSpec, WindowSpec)
import equity_feature_continuous as c

ROOT = Path(__file__).resolve().parents[2]
RAW = (ROOT/'docs/stories/EQ115_SYNTHETIC_ORACLES.json').read_bytes()
PACKET = json.loads(RAW)


def pack(kind, payload):
    return json.dumps({'kind': kind, 'schema_version': '1', 'payload': payload},
                      sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                      allow_nan=False).encode()


class SuppliedWeek(unittest.TestCase):
    def test_twelve_full_independent_outputs_and_36_identities(self):
        functions = {'basis': c.compute_basis, 'freeze': c.compute_freeze, 'reopen': c.compute_reopen}
        self.assertEqual(len(PACKET['cases']), 12)
        for case in PACKET['cases']:
            with self.subTest(case=case['case_id']):
                raw = pack('continuous_input', case['input'])
                value = c.input_from_json(raw)
                config_raw = c.to_json(value.config)
                result = functions[value.config.operation](value)
                self.assertEqual(json.loads(c.to_json(result))['payload'], case['expected_result'])
                self.assertEqual(c.config_digest(value.config), case['config_digest'])
                self.assertEqual(c.input_digest(value), case['input_digest'])
                self.assertEqual(c.result_digest(result), case['expected_result_digest'])
                self.assertEqual(c.from_json(c.to_json(result)), result)
                self.assertEqual(c.to_json(value), raw)
                self.assertEqual(c.to_json(value.config), config_raw)

    def test_consumer_complete_receipt_and_tampered_expectations_refuse(self):
        example = runpy.run_path(str(ROOT/'examples/continuous_supplied_week.py'))
        digest = hashlib.sha256(RAW).hexdigest()
        receipt = example['evaluate'](PACKET, digest)
        self.assertEqual(receipt['cases'], [{'case_id': x['case_id'],
            'result_digest': x['expected_result_digest']} for x in PACKET['cases']])
        self.assertEqual((receipt['case_count'], receipt['fixture_sha256']), (12, digest))
        for mode in ('missing_case', 'input_digest', 'expected_result_digest', 'expected_payload'):
            changed = copy.deepcopy(PACKET)
            if mode == 'missing_case':
                changed['cases'].pop()
            elif mode == 'expected_payload':
                changed['cases'][0]['expected_result']['available_at_ns'] += 1
                changed['cases'][0]['expected_result_digest'] = hashlib.sha256(
                    pack('continuous_result', changed['cases'][0]['expected_result'])).hexdigest()
            else:
                changed['cases'][0][mode] = '0'*64
            with self.subTest(mode=mode), self.assertRaises(ValueError):
                example['evaluate'](changed, digest)
        self.assertEqual(json.loads(RAW), PACKET)

    def test_old_config_and_result_type_domains_remain_separate(self):
        case = PACKET['cases'][0]
        for kind, payload in [('continuous_config', case['input']['config']),
                              ('continuous_input', case['input']),
                              ('continuous_result', case['expected_result'])]:
            with self.subTest(kind=kind), self.assertRaises(ContractError) as caught:
                ConfigSpec.from_json(pack(kind, payload).decode())
            self.assertEqual(caught.exception.code.value, 'invalid_config')
        own = c.result_from_json(pack('continuous_result', case['expected_result']))
        with self.assertRaises(ContractError) as caught:
            FeatureResult((), (), own)
        self.assertEqual(caught.exception.code.value, 'invalid_schema')
        old_config = ConfigSpec('synthetic:old', 'v1', (),
            SessionSpec('demo', 'S1', 0, 10, 'supplied', (IntervalSpec('all', 0, 10),)),
            WindowSpec(1, 'S1', ('S1',)), AvailabilitySpec(10, 10, 10))
        old_metadata = ResultMetadata('demo', 'S1', AvailabilitySpec(10, 10, 10),
            old_config.digest, (), 'python', 'synthetic')
        old_result = FeatureResult((), (), old_metadata)
        for old in (old_config, old_result):
            with self.assertRaises(ContractError) as caught:
                c.to_json(old)
            self.assertEqual(caught.exception.code.value, 'invalid_schema')
