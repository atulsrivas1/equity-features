"""Synthetic independent scanner goldens; no native backends or alternative calculator."""
from dataclasses import FrozenInstanceError, replace
import hashlib
import json
from pathlib import Path
import unittest

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, ConfigSpec, Coverage, DataKind,
    EntityKey, EvidenceRow, FeatureColumn, FeatureResult, InputBinding, InputScope,
    Parameter, PriceUnit, QualityRow, Reason, ResultMetadata, SessionSpec, SourceBinding,
    Status, ValueType, WindowSpec,
)
from equity_feature_strategies import (
    Entity, FeatureRequirement, Predicate, Ranking, StrategyConfig, StrategyError,
    StrategyRequest, digest, encode, feature_result_digest, input_semantic_digest, scan,
)

FIXTURES = json.loads((Path(__file__).resolve().parents[2] / 'docs/stories/EQ-089_FIXTURES.json').read_text(encoding='utf-8'))
CASES = {case['id']: case for case in FIXTURES['strategy_cases']}
C = 'session.trade.count'
V = 'session.trade.volume'
TYPES = {C: (ValueType.INT64, 'trades'), V: (ValueType.INT64, 'shares'),
         'history.return': (ValueType.FLOAT64, 'fraction'),
         'baseline.relative_volume': (ValueType.FLOAT64, 'fraction'),
         'session.price.open_close_return': (ValueType.FLOAT64, 'fraction')}
A = AvailabilitySpec(100, 100, 100)
META = BatchMetadata('synthetic', SourceBinding('synthetic-fixture', 'snapshot-1', 'mapping-1', 'input-1'),
    Coverage(1, 1, True), PriceUnit(0, 'USD'), scope=InputScope(0, 100, 'fixture-v1'))


def result(cells, *, metadata=META, config='0' * 64, availability=A, session='S0', algorithm='v1', evidence=()):
    """Constructor adapter only: expected scan outputs never calculated here."""
    columns, quality = [], []
    for feature, entries in cells.items():
        dtype, unit = TYPES.get(feature, (ValueType.INT64, 'trades'))
        entities = tuple(EntityKey(entity, session) for entity, _ in entries)
        values = tuple(value for _, value in entries)
        columns.append(FeatureColumn(feature, algorithm, dtype, unit, entities, values))
        for entity, value in zip(entities, values):
            quality.append(QualityRow(entity, feature, Status.MISSING_INPUT if value is None else Status.AVAILABLE,
                1, 0 if value is None else 1, (Reason.ABSENT_INPUT,) if value is None else ()))
    return FeatureResult(tuple(columns), tuple(quality), ResultMetadata('synthetic', session, availability,
        config, (InputBinding('observations', DataKind.TRADE, metadata),), 'synthetic-fixture', 'fixture-v1', 10), evidence)


BASELINE = result({})


def requirement(feature=C, config='0' * 64):
    dtype, unit = TYPES[feature]
    return FeatureRequirement(feature, '1', 'v1', dtype, unit, config, input_semantic_digest(BASELINE))


def configuration(*, top_k=2, predicates=None, ranking=None):
    return StrategyConfig((Predicate(requirement(), 'ge', 2),) if predicates is None else predicates,
        Ranking(requirement(V), 'descending') if ranking is None else ranking, top_k)


def request(universe=('A',), results=None, config=None, availability=A):
    return StrategyRequest('synthetic', 'S0', availability,
        [Entity('synthetic', name, 'S0') for name in universe],
        [result({C: [('A', 2)], V: [('A', 5)]})] if results is None else results,
        configuration() if config is None else config)


def materialize(case_id):
    case = CASES[case_id]
    base = dict(CASES[case.get('base_case', case_id)])
    base.update(case)
    cells = {}
    for feature, field in ((C, 'count'), (V, 'volume')):
        entries = [(row['entity'], None if row[field] is None else int(row[field]))
                   for row in base.get('cells', []) if field in row]
        if entries:
            cells[feature] = entries
    predicates = [] if base.get('predicates') == [] else [Predicate(requirement(), base.get('operator', 'ge'), 2)]
    return request(base.get('universe', ['A']), [result(cells)] if cells else [],
        configuration(top_k=int(base.get('top_k', 2)), predicates=predicates))


class ScannerGoldens(unittest.TestCase):
    def error(self, code, call):
        with self.assertRaises(StrategyError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)
        self.assertEqual(str(caught.exception), 'strategy ' + code)

    def test_published_numeric_and_availability_goldens(self):
        ids = ('scan-tie-coverage', 'false-plus-ranking-missing', 'no-predicates', 'strict-boundary',
               'zero-k', 'oversized-k', 'empty', 'all-missing', 'exact-int-order')
        for case_id in ids:
            with self.subTest(case=case_id):
                actual = scan(materialize(case_id))
                expected = CASES[case_id]['expected']
                for field in ('expected', 'eligible', 'matching', 'coverage_numerator', 'coverage_denominator', 'readiness'):
                    if field in expected:
                        self.assertEqual(getattr(actual, field), int(expected[field]) if field != 'readiness' else expected[field])
                for field in ('ranked', 'selected'):
                    if field in expected:
                        self.assertEqual([e.instrument_id for e in getattr(actual, field)], expected[field])
                if 'row_statuses' in expected:
                    self.assertEqual([r.status for r in actual.rows], expected['row_statuses'])
                    self.assertEqual([r.rank for r in actual.rows], [None if x is None else int(x) for x in expected['ranks']])
                if 'status' in expected:
                    self.assertEqual(actual.rows[0].status, expected['status'])
                for field, name in (('predicate_state', 'state'), ('predicate_reason', 'reason')):
                    if field in expected:
                        self.assertEqual(getattr(actual.rows[0].predicate_dispositions[0], name), expected[field])
                if 'ranking_reason' in expected:
                    self.assertEqual(actual.rows[0].ranking_reason, expected['ranking_reason'])

    def test_published_structural_errors(self):
        self.error('bounds', lambda: configuration(top_k=-1))
        self.error('invalid_schema', lambda: configuration(top_k=True))
        self.error('duplicate', lambda: request(('A', 'A')))
        r = request().feature_results[0]
        for other in (r, result({C: [('A', 3)], V: [('A', 7)]})):
            self.error('duplicate', lambda: request(results=[r, other]))
        self.error('inconsistent_identity', lambda: request(results=[result({C: [('B', 2)]})]))
        self.error('invalid_unit', lambda: replace(requirement(), unit='shares'))
        self.error('incompatible_version', lambda: request(results=[result({C: [('A', 2)]}, algorithm='v2')]))
        self.error('inconsistent_identity', lambda: request(results=[result({}, availability=AvailabilitySpec(100, 101, 101))]))
        self.error('inconsistent_identity', lambda: request(results=[result({}, session='S1')]))
        self.error('invalid_config', lambda: request(results=[], availability=AvailabilitySpec(100, 100, 100, 'reconstruction', 'fixture')))
        self.error('unsupported_feature', lambda: request(results=[result({'label.forward_price_return': [('A', 2)]})]))

    def test_permutation_normalizes_all_presentations(self):
        original = materialize('scan-tie-coverage')
        r = original.feature_results[0]
        evidence = tuple(EvidenceRow(EntityKey(name, 'S0'), C, 'input-1', 'row-' + name, 10, 10) for name in ('A', 'B'))
        r = replace(r, evidence=evidence)
        original = replace(original, feature_results=[r])
        permuted = replace(r, values=[replace(c, entities=c.entities[::-1], values=c.values[::-1]) for c in r.values[::-1]],
            quality=r.quality[::-1], evidence=r.evidence[::-1])
        other = replace(original, universe=original.universe[::-1], feature_results=[permuted])
        self.assertEqual(encode(original), encode(other))
        self.assertEqual(encode(scan(original)), encode(scan(other)))
        # Separately permute a true multi-result input.
        split = [replace(r, values=(c,), quality=tuple(q for q in r.quality if q.feature_id == c.feature_id),
            evidence=tuple(e for e in r.evidence if e.feature_id == c.feature_id)) for c in r.values]
        left = replace(original, feature_results=split)
        right = replace(left, feature_results=split[::-1])
        self.assertEqual(left.identity_digest, right.identity_digest)
        self.assertEqual(scan(left).identity_digest, scan(right).identity_digest)

    def test_content_values_quality_evidence_and_source_revisions(self):
        original = materialize('scan-tie-coverage')
        r = original.feature_results[0]
        changed_values = replace(r, values=tuple(replace(c, values=tuple(3 if e.instrument_id == 'E' else v
            for e, v in zip(c.entities, c.values))) if c.feature_id == V else c for c in r.values))
        changed_quality = replace(r, quality=tuple(replace(q, expected=2, observed=2) if q.entity.instrument_id == 'A' else q for q in r.quality))
        changed_evidence = replace(r, evidence=(EvidenceRow(EntityKey('A', 'S0'), C, 'input-1', 'row-A', 10, 10),))
        revision = replace(META, source=replace(META.source, snapshot_id='snapshot-2', input_id='input-2'))
        changed_source = replace(r, metadata=replace(r.metadata, inputs=(InputBinding('observations', DataKind.TRADE, revision),)))
        for changed in (changed_values, changed_quality, changed_evidence, changed_source):
            with self.subTest(change=feature_result_digest(changed)):
                req = replace(original, feature_results=[changed])
                self.assertNotEqual(feature_result_digest(r), feature_result_digest(changed))
                self.assertNotEqual(original.identity_digest, req.identity_digest)
                self.assertNotEqual(scan(original).identity_digest, scan(req).identity_digest)
                self.assertEqual(scan(original).selected, scan(req).selected)
                self.assertEqual(input_semantic_digest(r), input_semantic_digest(changed))
        self.assertEqual(r.metadata.identity_digest, changed_values.metadata.identity_digest)

    def test_real_config_horizon_and_baseline_mismatches(self):
        def cfg(period):
            return ConfigSpec('fixture-history', 'v1', (Parameter('period', period),),
                SessionSpec('synthetic', 'S0', 0, 100, 'supplied'), WindowSpec(1, 'S0', ('prior', 'S0')),
                A, price_unit=PriceUnit(0, 'USD'))
        for feature, expected_period, wrong_period in (('history.return', 1, 252), ('baseline.relative_volume', 20, 5)):
            expected, wrong = cfg(expected_period).digest, cfg(wrong_period).digest
            self.assertNotEqual(expected, wrong)
            config = configuration(predicates=[], ranking=Ranking(requirement(feature, expected), 'descending'))
            right = result({feature: [('A', .1)]}, config=expected)
            bad = result({feature: [('B', .2)]}, config=wrong)
            self.error('inconsistent_identity', lambda: request(('A', 'B'), [right, bad], config))
            self.error('inconsistent_identity', lambda: request(('B',), [bad], config))
        first = requirement('history.return', cfg(1).digest)
        second = requirement('history.return', cfg(252).digest)
        self.error('invalid_config', lambda: configuration(predicates=[Predicate(first, 'ge', .0), Predicate(second, 'ge', .0)]))

    def test_semantic_adjustment_and_eligibility_mismatches_even_when_missing(self):
        changes = (replace(META, adjustment=AdjustmentSpec('split', 'split-v1', 'actions', 'anchor')),
                   replace(META, scope=replace(META.scope, eligibility_policy='different')),
                   replace(META, scope=replace(META.scope, include_opening_auction=True)))
        for metadata in changes:
            for scalar in (2, None):
                self.error('inconsistent_identity', lambda: request(results=[result({C: [('A', scalar)]}, metadata=metadata)]))
                # A valid raw entity cannot mask a later entity's incompatible basis/policy.
                good = result({C: [('A', 2)]})
                bad = result({C: [('B', scalar)]}, metadata=metadata)
                self.error('inconsistent_identity', lambda: request(('A', 'B'), [good, bad]))

    def test_all_operators_float_thresholds_and_ascending_ties(self):
        feature = 'session.price.open_close_return'
        supplied = result({feature: [('B', .5), ('A', .5), ('C', -.5)]})
        for op, ranked in (('lt', ['C']), ('le', ['C', 'A', 'B']), ('eq', ['A', 'B']),
                           ('ge', ['A', 'B']), ('gt', [])):
            config = configuration(predicates=[Predicate(requirement(feature), op, .5)],
                ranking=Ranking(requirement(feature), 'ascending'))
            actual = scan(request(('C', 'B', 'A'), [supplied], config))
            self.assertEqual([e.instrument_id for e in actual.ranked], ranked)
        self.error('invalid_config', lambda: Predicate(requirement(feature), 'ge', 1))
        self.error('invalid_schema', lambda: Predicate(requirement(), 'ge', True))

    def test_absent_entity_status_family_and_retained_ranking(self):
        r = result({C: [('A', None)], V: [('A', 5)]})
        for status in (Status.INSUFFICIENT_HISTORY, Status.INCOMPLETE_COVERAGE, Status.NOT_APPLICABLE, Status.MISSING_INPUT):
            q = tuple(replace(q, status=status) if q.feature_id == C else q for q in r.quality)
            actual = scan(request(('A', 'B'), [replace(r, quality=q)]))
            self.assertEqual(actual.rows[0].predicate_dispositions[0].reason, status.value)
            self.assertEqual(actual.rows[0].ranking_value, 5)
            self.assertEqual(actual.rows[1].ranking_reason, 'absent_entity')

    def test_ownership_closed_encoder_and_error_immutability(self):
        req = request()
        universe, results, predicates = list(req.universe), list(req.feature_results), list(req.config.predicates)
        owned = replace(req, universe=universe, feature_results=results, config=replace(req.config, predicates=predicates))
        before = encode(owned)
        universe.clear(); results.clear(); predicates.clear()
        self.assertEqual(encode(owned), before)
        with self.assertRaises(FrozenInstanceError):
            owned.namespace = 'changed'
        error = StrategyError('invalid_schema')
        with self.assertRaises(AttributeError):
            error.code = 'bounds'
        with self.assertRaises(AttributeError):
            del error._StrategyError__code
        cycle = []; cycle.append(cycle)
        for unknown in (object(), {'unrecognized': 1}, cycle, float('nan'), '\ud800'):
            self.error('invalid_schema', lambda: encode(unknown))
        self.error('incompatible_version', lambda: digest('label-result:1', req))
        self.assertEqual(encode((True, None, 9007199254740993, -.0)),
            b'[true,null,{"int":"9007199254740993"},{"float64":"-0x0.0p+0"}]')
        self.assertEqual(req.identity_digest, hashlib.sha256(b'strategy-request:1\0' + encode(req)).hexdigest())

    def test_identity_tags_signed_zero_domains_and_rule_order(self):
        self.assertEqual(len({encode(True), encode(1), encode(1.)}), 3)
        self.assertEqual(encode(1.), b'{"float64":"0x1.0000000000000p+0"}')
        self.assertNotEqual(encode(.0), encode(-.0))
        feature = 'history.return'
        supplied = result({feature: [('B', -.0), ('A', .0)]})
        config = configuration(predicates=[], ranking=Ranking(requirement(feature), 'descending'))
        self.assertEqual([e.instrument_id for e in scan(request(('B', 'A'), [supplied], config)).ranked], ['A', 'B'])
        p, q = Predicate(requirement(), 'ge', 2), Predicate(requirement(V), 'gt', 0)
        first = request(config=configuration(predicates=[p, q]))
        second = replace(first, config=configuration(predicates=[q, p]))
        self.assertNotEqual(first.config.identity_digest, second.config.identity_digest)
        self.assertNotEqual(first.identity_digest, second.identity_digest)
        self.assertEqual(scan(first).selected, scan(second).selected)
        data = encode(first)
        self.assertNotEqual(hashlib.sha256(b'strategy-request:1\0' + data).digest(),
            hashlib.sha256(b'strategy-result:1\0' + data).digest())


if __name__ == '__main__':
    unittest.main()
