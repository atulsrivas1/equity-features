"""Complete independently frozen endpoint packets, with actual refusal stages."""
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import unittest

from equity_feature_contracts import CanonicalBatch, Column, ConfigSpec, ContractError, DataKind, EntityKey
from equity_features.ef1 import build_ef1_config, compute_ef1, decode_ef1_context, ef1_definitions
from test_ef1_observable import metadata

ORACLE_PATH = Path(__file__).resolve().parents[2] / 'docs/ef1/gap_endpoint/GAP_ENDPOINT_ORACLE.json'
ORACLE_BYTES = ORACLE_PATH.read_bytes()
CAUSAL_PATH = ORACLE_PATH.with_name('GAP_ENDPOINT_ORACLE_CAUSAL_V4.json')
CAUSAL_BYTES = CAUSAL_PATH.read_bytes()
PACKETS = json.loads(CAUSAL_BYTES)['packets']


def inputs(packet):
    return tuple(None if row['batch'] is None else CanonicalBatch(DataKind(row['batch']['kind']),
        tuple(Column(c['name'], tuple(c['values'])) for c in row['batch']['columns']),
        metadata(row['batch']['metadata'])) for row in packet['role_slots'])


def evaluate(packet):
    config = ConfigSpec.from_json(json.dumps(packet['config']))
    return compute_ef1(inputs(packet), config, entity=EntityKey(**packet['entity']))


class GapEndpointPackets(unittest.TestCase):
    def test_immutable_oracle(self):
        self.assertEqual(hashlib.sha256(ORACLE_BYTES).hexdigest(), '22d23e4c57fe1382c25b30aba50bde70eff002d85a9a4dc27f96b13df6b210b2')
        self.assertEqual(hashlib.sha256(CAUSAL_BYTES).hexdigest(), '8ff3cce116c71dbe50c8e3e8d455dd4203acddfcc9604bbc092aa85e2ca2b781')
        self.assertEqual(len(PACKETS), 114)

    def test_complete_result_literals(self):
        self.assertEqual(sum(p.get('expected_result') is not None for p in PACKETS), 71)
        for packet in PACKETS:
            if packet.get('expected_result') is not None:
                with self.subTest(packet=packet['id']):
                    self.assertEqual(json.loads(json.dumps(asdict(evaluate(packet)))), packet['expected_result'])

    def test_refusals(self):
        self.assertEqual(sum(p.get('expected_error') is not None for p in PACKETS), 43)
        for packet in PACKETS:
            if packet.get('expected_error') is not None:
                with self.subTest(packet=packet['id'], earliest=packet['expected_error']['expected_earliest_stage']):
                    if packet['id'] == 'E30_unknown_expected':
                        with self.assertRaises(ContractError) as caught:
                            inputs(packet)
                    else:
                        supplied = inputs(packet)
                        with self.assertRaises(ContractError) as caught:
                            config = ConfigSpec.from_json(json.dumps(packet['config']))
                            compute_ef1(supplied, config, entity=EntityKey(**packet['entity']))
                    self.assertEqual(caught.exception.code.value, packet['expected_error']['code'])

    def test_additive_discovery_builder(self):
        config = ConfigSpec.from_json(json.dumps(PACKETS[0]['config']))
        self.assertEqual(decode_ef1_context(config)['producer'], 'path_gap_endpoint')
        self.assertEqual(config, build_ef1_config(json.loads(config.parameters[0].value), session=config.session,
            window=config.window, availability=config.availability, price_unit=config.price_unit, adjustment=config.adjustment))
        self.assertEqual([x.feature_id for x in ef1_definitions(config)], ['session.gap_endpoint.current_fill_fraction', 'session.gap_endpoint.opening_gap_fraction'])

    def test_actual_pure_execution_denies_external_entrypoints(self):
        from test_purity_audit import denied_entrypoints
        config = ConfigSpec.from_json(json.dumps(PACKETS[0]['config']))
        supplied = inputs(PACKETS[0])
        entity = EntityKey(**PACKETS[0]['entity'])
        with denied_entrypoints():
            result = compute_ef1(supplied, config, entity=entity)
        self.assertEqual(json.loads(json.dumps(asdict(result))), PACKETS[0]['expected_result'])

    def test_fixed_slots_never_inferred_from_kind(self):
        from equity_feature_contracts import ErrorCode
        config = ConfigSpec.from_json(json.dumps(PACKETS[0]['config']))
        supplied = inputs(PACKETS[0])
        for bad in (supplied[:3], supplied + (None,), iter(supplied)):
            with self.subTest(shape=type(bad).__name__):
                with self.assertRaises(ContractError) as caught:
                    compute_ef1(bad, config, entity=EntityKey(**PACKETS[0]['entity']))
                self.assertEqual(caught.exception.code, ErrorCode.INVALID_SCHEMA)
