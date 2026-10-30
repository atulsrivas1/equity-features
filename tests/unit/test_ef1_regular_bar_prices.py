"""Complete independently frozen endpoint packets, with actual refusal stages."""
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import unittest
from collections import Counter
from equity_feature_contracts import validate_batch

from equity_feature_contracts import CanonicalBatch, Column, ConfigSpec, ContractError, DataKind, EntityKey
from equity_features.ef1 import build_ef1_config, compute_ef1, decode_ef1_context, ef1_definitions
from test_ef1_observable import metadata

ORACLE_PATH = Path(__file__).resolve().parents[2] / 'docs/ef1/regular_bar_prices/REGULAR_BAR_PRICES_ORACLE.json'
ORACLE_BYTES = ORACLE_PATH.read_bytes()
PACKETS = json.loads(ORACLE_BYTES)['packets']


def inputs(packet):
    return tuple(None if row['batch'] is None else CanonicalBatch(DataKind(row['batch']['kind']),
        tuple(Column(c['name'], tuple(c['values'])) for c in row['batch']['columns']),
        metadata(row['batch']['metadata'])) for row in packet['role_slots'])


def evaluate(packet):
    config = ConfigSpec.from_json(json.dumps(packet['config']))
    return compute_ef1(inputs(packet), config, entity=EntityKey(**packet['entity']))



class RegularBarPricePackets(unittest.TestCase):
    def test_immutable_oracle(self):
        self.assertEqual(hashlib.sha256(ORACLE_BYTES).hexdigest(), 'bd057b4042e1274ae46a8653debae90e275087f6448780f491c33a2a691bbaf0')
        self.assertEqual(len(PACKETS), 100)

    def test_complete_result_literals(self):
        self.assertEqual(sum(p.get('expected_result') is not None for p in PACKETS), 46)
        for packet in PACKETS:
            if packet.get('expected_result') is not None:
                with self.subTest(packet=packet['id']):
                    self.assertEqual(json.loads(json.dumps(asdict(evaluate(packet)))), packet['expected_result'])

    def test_refusals_at_actual_earliest_stage(self):
        observed = Counter()
        for packet in PACKETS:
            if packet.get('expected_error') is None:
                continue
            with self.subTest(packet=packet['id']):
                stage = 'Coverage_constructor' if packet['id'] == 'N11_complete_unknown_expected' else 'CanonicalBatch_constructor'
                try:
                    supplied = inputs(packet)
                    stage = 'canonical_validate_batch'
                    for batch in supplied:
                        if batch is not None:
                            validate_batch(batch, required_fields=())
                    stage = 'endpoint_config_decode'
                    config = ConfigSpec.from_json(json.dumps(packet['config']))
                    decode_ef1_context(config)
                    stage = 'endpoint_pure_semantic_or_geometry'
                    compute_ef1(supplied, config, entity=EntityKey(**packet['entity']))
                except ContractError as error:
                    self.assertEqual(error.code.value, packet['expected_error']['code'])
                    self.assertEqual(stage, packet['expected_error']['expected_earliest_stage'])
                    observed[stage] += 1
                else:
                    self.fail('expected refusal')
        self.assertEqual(observed, {'Coverage_constructor': 1, 'CanonicalBatch_constructor': 3,
            'canonical_validate_batch': 10, 'endpoint_config_decode': 3, 'endpoint_pure_semantic_or_geometry': 37})

    def test_additive_discovery_builder(self):
        config = ConfigSpec.from_json(json.dumps(PACKETS[0]['config']))
        self.assertEqual(decode_ef1_context(config)['producer'], 'regular_bar_prices')
        self.assertEqual(config, build_ef1_config(json.loads(config.parameters[0].value), session=config.session,
            window=config.window, availability=config.availability, price_unit=config.price_unit, adjustment=config.adjustment))
        self.assertEqual([x.feature_id for x in ef1_definitions(config)],
            ['session.close.calculated_price', 'session.regular.first_completed_bar_open'])

    def test_actual_pure_execution_denies_external_entrypoints(self):
        from test_purity_audit import denied_entrypoints
        requests = [(inputs(p), ConfigSpec.from_json(json.dumps(p['config'])),
                     EntityKey(**p['entity']), p['expected_result'])
                    for p in PACKETS if p.get('expected_result') is not None]
        # Materialize imports before entering the denied execution boundary.
        compute_ef1(requests[0][0], requests[0][1], entity=requests[0][2])
        with denied_entrypoints():
            results = [compute_ef1(batches, config, entity=entity) for batches, config, entity, _ in requests]
        for result, (_, _, _, expected) in zip(results, requests):
            self.assertEqual(json.loads(json.dumps(asdict(result))), expected)

    def test_fixed_slots_and_reference_family(self):
        from equity_feature_contracts import ErrorCode
        config = ConfigSpec.from_json(json.dumps(PACKETS[0]['config']))
        supplied = inputs(PACKETS[0])
        for bad in (supplied[:2], supplied + (None,), iter(supplied), (supplied[2], supplied[1], supplied[0])):
            with self.subTest(shape=type(bad).__name__):
                with self.assertRaises(ContractError) as caught:
                    compute_ef1(bad, config, entity=EntityKey(**PACKETS[0]['entity']))
                self.assertEqual(caught.exception.code, ErrorCode.INVALID_SCHEMA)

    def test_numeric_prices_excluded_from_membership_and_inputs_unchanged(self):
        from test_ef1_observable import changed_batch
        packet = PACKETS[0]
        config = ConfigSpec.from_json(json.dumps(packet['config']))
        supplied = inputs(packet)
        before = tuple(asdict(b) for b in supplied)
        bars = changed_batch(supplied[1], open=(150,) * supplied[1].row_count,
            close=(151,) * supplied[1].row_count, high=(152,) * supplied[1].row_count, low=(149,) * supplied[1].row_count)
        result = compute_ef1((supplied[0], bars, supplied[2]), config, entity=EntityKey(**packet['entity']))
        self.assertEqual([column.values for column in result.values], [(1.51,), (1.5,)])
        self.assertEqual(tuple(asdict(b) for b in supplied), before)

    def test_invalid_interior_ohlc_refuses_with_missing_both_proofs(self):
        from test_ef1_observable import changed_batch
        packet = next(p for p in PACKETS if p['id'] == 'R15_interior_price_future_irrelevant')
        supplied = inputs(packet)
        closes = list(next(c.values for c in supplied[1].columns if c.name == 'close'))
        closes[1] = None
        bars = changed_batch(supplied[1], close=closes)
        with self.assertRaises(ContractError) as caught:
            compute_ef1((None, bars, None), ConfigSpec.from_json(json.dumps(packet['config'])),
                        entity=EntityKey(**packet['entity']))
        self.assertEqual(caught.exception.code.value, 'invalid_schema')

    def test_legacy_gap_family_never_admitted_as_regular_proof(self):
        packet = PACKETS[0]
        supplied = inputs(packet)
        proof = replace(supplied[2], columns=tuple(Column(c.name, ('ef1.gap.population.v1',)
            if c.name == 'fact_kind' else c.values) for c in supplied[2].columns))
        with self.assertRaises(ContractError) as caught:
            compute_ef1((None, supplied[1], proof), ConfigSpec.from_json(json.dumps(packet['config'])),
                        entity=EntityKey(**packet['entity']))
        self.assertEqual(caught.exception.code.value, 'invalid_schema')
