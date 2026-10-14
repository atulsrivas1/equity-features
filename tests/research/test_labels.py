"""Independent label goldens, runnable with contracts and labels alone."""
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
import math
from pathlib import Path
import unittest
from equity_feature_contracts import AvailabilitySpec
from equity_feature_labels import (BasisWitness, Entity, LabelConfig, LabelError, LabelOrigin,
    LabelRequest, PriceObservation, digest, encode, evaluate_label, origin_digest, path_content_digest)

FIXTURES = json.loads((Path(__file__).resolve().parents[2] / 'docs/stories/EQ-089_FIXTURES.json').read_text(encoding='utf-8'))
CASES = {c['id']: c for c in FIXTURES['label_cases']}
COMBINED = {'causal-signal-invariance', 'join-reject-future-known', 'join-admit-boundary'}


def maybe_int(value):
    return None if value is None else int(value)


def basis(fields):
    return BasisWitness(fields['basis'], fields['policy_version'], fields['action_snapshot'],
        fields['anchor_id'], fields['source_revision'], int(fields['effective_ns']), maybe_int(fields['known_at_ns']))


def request(case=None):
    """Materialize supplied fixture facts; never compute an expected return."""
    case = {} if case is None else case
    defaults = FIXTURES['label_defaults']
    ob = dict(defaults['origin_basis'])
    if 'origin_basis_known_at_ns' in case:
        ob['known_at_ns'] = case['origin_basis_known_at_ns']
    origin = LabelOrigin(Entity(**defaults['entity']), 'a' * 64, 'b' * 64, AvailabilitySpec(100, 100, 100),
        100, 100.0, maybe_int(case.get('origin_anchor_known_at_ns', '100')), 'origin-1', basis(ob))
    pb = dict(case.get('path_basis', defaults['path_basis']))
    for field in ('known_at_ns', 'effective_ns'):
        if 'path_basis_' + field in case:
            pb[field] = case['path_basis_' + field]
    if 'path_basis_kind' in case:
        pb['basis'] = case['path_basis_kind']
    path_basis = basis(pb)
    observations = []
    for raw in case.get('observations', defaults['observations']):
        stamp = int(raw['event_ns'])
        if str(stamp) == case.get('remove_event_ns'):
            continue
        price = float(raw['price'])
        if stamp == 100:
            if 'anchor_price' in case:
                price = float(case['anchor_price'])
            if 'anchor_price_hex' in case:
                price = float.fromhex(case['anchor_price_hex'])
        if stamp == 110:
            if 'endpoint_price' in case:
                price = float(case['endpoint_price'])
            if 'endpoint_price_hex' in case:
                price = float.fromhex(case['endpoint_price_hex'])
        known = case.get('endpoint_known_at_ns', raw['known_at_ns']) if stamp == 110 else raw['known_at_ns']
        observations.append(PriceObservation(stamp, price, maybe_int(known),
            case.get('path_source_revision', 'path-1'), origin_digest(origin), path_basis))
    if case.get('id') == 'duplicate-timestamp':
        observations.append(observations[-1])
    if case.get('id') == 'basis-mismatch':
        # A valid but different split witness; structural raw witness rules are tested separately.
        common = BasisWitness('split', 'split-v1', 'snapshot-1', 'anchor-1', 'basis-1', 100, 100)
        observations = [replace(row, basis=common) for row in observations]
        observations[-1] = replace(observations[-1], basis=replace(common, action_snapshot='snapshot-2'))
    a = case.get('availability', defaults['availability'])
    return LabelRequest(origin, AvailabilitySpec(int(a['market_cutoff_ns']), int(a['knowledge_cutoff_ns']), int(a['evaluation_ns'])),
        observations, LabelConfig(int(case.get('horizon_ns', '10'))))


class LabelTests(unittest.TestCase):
    def error(self, code, call):
        with self.assertRaises(LabelError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(str(caught.exception), 'label ' + code)

    def test_published_numerical_and_state_requirements(self):
        self.assertEqual(len(CASES), 33)
        for name, case in CASES.items():
            if name in COMBINED or name == 'revision':
                continue
            with self.subTest(name=name):
                if 'expected_error' in case:
                    self.error(case['expected_error'], lambda: evaluate_label(request(case)))
                    continue
                req = request(case)
                out = evaluate_label(req)
                expected = case['expected']
                self.assertEqual(out.status, expected['status'])
                self.assertEqual(out.reasons, tuple(expected.get('reasons', ())))
                self.assertEqual(out.horizon_endpoint_ns, int(expected.get('horizon_endpoint_ns', 110)))
                if out.status != 'mature':
                    self.assertIsNone(out.value)
                    self.assertIsNone(out.label_known_at_ns)
                else:
                    self.assertEqual(out.label_known_at_ns, int(expected.get('label_known_at_ns', 110)))
                    if 'fraction' in expected:
                        n, d = map(int, expected['fraction'])
                        self.assertTrue(math.isclose(out.value, n / d, rel_tol=1e-12, abs_tol=1e-12))
                    else:
                        self.assertEqual(out.value.hex(), expected['rounded_float_hex'])
                self.assertEqual(evaluate_label(req), out)
                self.assertEqual(req.origin.anchor_price, 100.0)

    def test_revision_adjustment_and_complete_path_identity(self):
        raw, revised = request(), request(CASES['revision'])
        adjusted = request(CASES['later-adjusted-path'])
        for other in (revised, adjusted):
            self.assertEqual(raw.origin.identity_digest, other.origin.identity_digest)
            self.assertNotEqual(raw.identity_digest, other.identity_digest)
            self.assertNotEqual(path_content_digest(raw.observations), path_content_digest(other.observations))
            self.assertNotEqual(evaluate_label(raw).identity_digest, evaluate_label(other).identity_digest)
        interior = replace(raw.observations[0], event_ns=105, price=123.0, known_at_ns=None)
        extended = replace(raw, observations=(*raw.observations, interior))
        self.assertEqual(evaluate_label(raw).value, evaluate_label(extended).value)
        self.assertNotEqual(extended.identity_digest, raw.identity_digest)
        self.assertEqual(extended.identity_digest, replace(extended, observations=list(reversed(extended.observations))).identity_digest)
        self.assertEqual(path_content_digest(extended.observations), path_content_digest(list(reversed(extended.observations))))
        self.assertNotEqual(path_content_digest((interior,)), path_content_digest((replace(interior, price=124.0),)))

    def test_structural_precedence_and_exact_types(self):
        base = request()
        for price in (0.0, -1.0, math.inf, math.nan):
            self.error('bounds', lambda: replace(base, observations=(*base.observations,
                replace(base.observations[0], event_ns=200, price=price))))
        for horizon in (0, -1, 2**63):
            self.error('bounds', lambda: LabelConfig(horizon))
        for horizon in (True, 10.0, '10'):
            self.error('invalid_schema', lambda: LabelConfig(horizon))
        for value in (1, True, '1'):
            self.error('invalid_schema', lambda: replace(base.observations[0], price=value))
        self.error('duplicate', lambda: replace(base, observations=(*base.observations, replace(base.observations[0], price=12.0))))
        self.error('inconsistent_identity', lambda: replace(base, observations=(replace(base.observations[0], origin_anchor_digest='0' * 64),)))
        self.error('inconsistent_identity', lambda: replace(base, observations=(base.observations[0], replace(base.observations[1], source_revision='other'))))
        self.error('inconsistent_identity', lambda: replace(base.origin, anchor_known_at_ns=None))
        self.error('inconsistent_identity', lambda: replace(base.origin, anchor_event_ns=101))
        self.error('inconsistent_identity', lambda: replace(base.origin, anchor_basis=replace(base.origin.anchor_basis, effective_ns=101)))
        self.error('inconsistent_identity', lambda: replace(base, availability=AvailabilitySpec(99, 110, 110)))
        self.error('inconsistent_identity', lambda: replace(base, availability=AvailabilitySpec(110, 99, 110)))
        self.error('inconsistent_identity', lambda: replace(base.observations[0].basis, action_snapshot='other'))
        self.error('inconsistent_identity', lambda: BasisWitness('split', 'none', 'action', 'anchor', 'revision', 100, 100))
        self.error('unsupported_adjustment', lambda: replace(base.observations[0].basis, basis='total_return'))
        self.error('incompatible_version', lambda: LabelConfig(10, algorithm_version='other'))
        self.error('incompatible_version', lambda: replace(base, schema_version='other'))
        self.error('invalid_unit', lambda: replace(evaluate_label(base), unit='percent'))
        self.error('invalid_schema', lambda: evaluate_label(object()))

    def test_ownership_closed_encoding_and_identity_requirements(self):
        base = request()
        rows = list(base.observations)
        owned = replace(base, observations=rows)
        rows.clear()
        self.assertEqual(owned, base)
        with self.assertRaises(FrozenInstanceError):
            owned.config = LabelConfig(20)
        self.error('invalid_schema', lambda: replace(base, observations=iter(base.observations)))
        class Foreign: pass
        class EntitySubclass(Entity): pass
        self.error('invalid_schema', lambda: encode(Foreign()))
        self.error('invalid_schema', lambda: EntitySubclass('synthetic', 'A', 'S0'))
        self.error('invalid_schema', lambda: Entity('synthetic', '\ud800', 'S0'))
        for text in ('', ' ', 'A\n', '\x7f'):
            self.error('invalid_schema', lambda: Entity('synthetic', text, 'S0'))
        self.assertEqual(encode(9007199254740993), b'{"int":"9007199254740993"}')
        self.assertEqual(encode(1.0), b'{"float64":"0x1.0000000000000p+0"}')
        self.assertEqual(len({encode(1), encode(1.0), encode(True)}), 3)
        self.assertNotEqual(encode(0.0), encode(-0.0))
        body = encode(base.origin)
        expected = hashlib.sha256(b'label-origin:1\0' + body).hexdigest()
        self.assertEqual(origin_digest(base.origin), expected)
        self.assertNotEqual(expected, hashlib.sha256(b'label-request:1\0' + body).hexdigest())
        self.error('invalid_schema', lambda: digest('label-request:1', base.origin))
        self.error('incompatible_version', lambda: digest('strategy-result:1', base))
        cyclic = []; cyclic.append(cyclic)
        self.error('invalid_schema', lambda: encode(cyclic))
        self.assertEqual(json.loads(encode(evaluate_label(base)))['record'], 'LabelResult')
        err = LabelError('bounds')
        with self.assertRaises(AttributeError): err.code = 'other'
        with self.assertRaises(AttributeError): del err.code
        self.assertEqual(LabelError('unknown').code, 'invalid_schema')
        # Predicate-order belongs to independently optional strategies and is exercised
        # there and by the combined consumer; importing that sibling here is prohibited.


if __name__ == '__main__':
    unittest.main()
