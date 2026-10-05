"""Exact synthetic EQ-003 reference checks, not production package code."""
from copy import deepcopy
from fractions import Fraction as F
from pathlib import Path
import json
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
GOLD = json.loads((ROOT / 'tests/fixtures/quote_math/golden.json').read_text(encoding='utf-8'))
I64 = 2**63 - 1


def classify(row):
    b, a = row.get('bid'), row.get('ask')
    for p in (b, a):
        if p is not None and (type(p) is not int or not -I64-1 <= p <= I64):
            raise ValueError('malformed price representation')
    if b is None or a is None or b <= 0 or a <= 0:
        return 'invalid', None, None
    spread = a - b
    return ('crossed' if spread < 0 else 'locked' if spread == 0 else 'normal',
            F(spread), F(20000 * spread, a + b))


def admit(rows, start=0, end=12, scale=0):
    if type(start) is not int or type(end) is not int or not -I64-1 <= start < end <= I64:
        raise ValueError('target bounds')
    if end-start > I64:
        raise ValueError('duration representation overflow')
    if type(scale) is not int or not 0 <= scale <= 18:
        raise ValueError('scale')
    if rows is None:
        return None
    seen, previous, selected = set(), None, []
    for row in rows:
        if type(row['ts']) is not int or type(row['order']) is not int:
            raise ValueError('time/order representation')
        key = row['ts'], row['order']
        if not start <= row['ts'] < end or (previous is not None and key <= previous):
            raise ValueError('bounds/order')
        if not isinstance(row['id'], str) or not row['id'] or row['id'] in seen:
            raise ValueError('identity')
        seen.add(row['id']); previous = key
        if type(row.get('eligible', True)) is not bool:
            raise ValueError('eligibility')
        if row.get('eligible', True):
            classify(row)
            selected.append(row)
    return selected


def sampled(rows, start=0, end=12, scale=0, complete=True):
    selected = admit(rows, start, end, scale)
    if selected is None:
        return {'status': 'missing_input', 'value': None}
    counts = dict(total=0, normal=0, valid=0, locked=0, crossed=0, invalid=0)
    abs_values, bps_values = [], []
    for row in selected:
        kind, spread, bps = classify(row)
        counts['total'] += 1; counts[kind] += 1
        if kind in ('normal', 'locked'):
            counts['valid'] += 1
            abs_values.append(spread / 10**scale); bps_values.append(bps)
    n = counts['valid']
    value = {'counts': counts, 'mean_abs': sum(abs_values, F()) / n if n else None,
             'mean_bps': sum(bps_values, F()) / n if n else None}
    return {'status': 'available' if complete else 'incomplete_coverage',
            'spread_status': 'available' if n else 'not_applicable',
            'value': value if complete else None, 'observed': value}


def continuous(rows, start=0, end=12, scale=0, max_age=6,
               initial='unknown', seed=None, complete=True, kind='continuous'):
    if kind != 'continuous':
        raise ValueError('unsupported sampling')
    if type(max_age) is not int or not 0 < max_age <= I64:
        raise ValueError('max_age')
    selected = admit(rows, start, end, scale)
    if selected is None:
        return {'status': 'missing_input', 'value': None}
    if initial not in ('unknown', 'inactive'):
        raise ValueError('initial state')
    if seed is not None:
        if type(seed['ts']) is not int or not -I64-1 <= seed['ts'] < start:
            raise ValueError('seed bounds')
        if not seed.get('eligible', True):
            raise ValueError('excluded seed')
        if any(seed['id'] == row['id'] for row in rows):
            raise ValueError('duplicate seed')
        classify(seed)
    durations = dict(valid=0, normal=0, locked=0, crossed=0, invalid=0, expired=0, unknown=0)
    weighted_abs = weighted_bps = F()

    def segment(state, left, right):
        nonlocal weighted_abs, weighted_bps
        if right <= left:
            return
        if state is None:
            durations['unknown' if initial == 'unknown' else 'invalid'] += right-left
            return
        # Reference integers are unbounded: no wrapping at event_ns + max_age.
        expiry = state['ts'] + max_age
        fresh_end = max(left, min(right, expiry))
        duration = fresh_end-left
        kind, spread, bps = classify(state)
        durations[kind] += duration
        if kind in ('normal', 'locked'):
            durations['valid'] += duration
            weighted_abs += spread / 10**scale * duration
            weighted_bps += bps * duration
        durations['expired'] += right-fresh_end

    state, cursor = seed, start
    for row in selected:
        segment(state, cursor, row['ts'])
        state, cursor = row, row['ts']
    segment(state, cursor, end)
    valid = durations['valid']
    observed = {'durations': durations, 'mean_abs': weighted_abs/valid if valid else None,
                'mean_bps': weighted_bps/valid if valid else None,
                'valid_fraction': F(valid, end-start)}
    status = 'incomplete_coverage' if not complete or durations['unknown'] else 'available' if valid else 'not_applicable'
    return {'status': status, 'value': observed if status != 'incomplete_coverage' else None,
            'observed': observed}


class QuoteReferences(unittest.TestCase):
    def test_three_scoped_definitions(self):
        scope = (ROOT/'docs/features/V1_SCOPE.md').read_text(encoding='utf-8')
        ids = re.findall(r'^\| (session\.quote\.[a-z_]+) \|', scope, re.M)
        doc = (ROOT/'docs/features/QUOTE_FORMULAS.md').read_text(encoding='utf-8')
        self.assertEqual(len(ids), 3)
        self.assertEqual(set(ids), set(re.findall(r'^\| (session\.quote\.[a-z_]+) \|', doc, re.M)))

    def test_sampled_golden(self):
        value = sampled(GOLD['rows'])['value']
        self.assertEqual(value['counts'], GOLD['sampled']['counts'])
        self.assertEqual(value['mean_abs'], F(GOLD['sampled']['mean_abs']))
        self.assertEqual(value['mean_bps'], F(GOLD['sampled']['mean_bps']))

    def test_continuous_golden(self):
        value = continuous(GOLD['rows'], initial='inactive')['value']
        self.assertEqual(value['durations'], GOLD['continuous']['durations'])
        for key in ('mean_abs', 'mean_bps', 'valid_fraction'):
            self.assertEqual(value[key], F(GOLD['continuous'][key]))

    def test_sampling_not_time_weighting(self):
        rows = [dict(id='a',ts=0,order=0,bid=100,ask=102),dict(id='b',ts=1,order=0,bid=100,ask=104)]
        self.assertEqual(sampled(rows)['value']['mean_abs'], 3)
        self.assertEqual(continuous(rows,max_age=20)['value']['mean_abs'], F(23,6))

    def test_bps_mean_not_ratio_of_means(self):
        rows = [dict(id='a',ts=0,order=0,bid=1,ask=3),dict(id='b',ts=1,order=0,bid=99,ask=101)]
        self.assertEqual(sampled(rows)['value']['mean_bps'], 5100)
        self.assertNotEqual(5100, F(20000,51))

    def test_locked_valid_zero(self):
        row = dict(id='a',ts=0,order=0,bid=100,ask=100)
        result=sampled([row])['value']
        self.assertEqual(result['mean_abs'],0);self.assertEqual(result['counts']['valid'],1)

    def test_crossed_signed_evidence_not_mean(self):
        row=dict(id='a',ts=0,order=0,bid=105,ask=104)
        self.assertEqual(classify(row),('crossed',F(-1),F(-20000,209)))
        self.assertIsNone(sampled([row])['value']['mean_abs'])

    def test_missing_nonpositive_sides(self):
        for bid,ask in [(None,102),(0,102),(-1,102),(100,None),(100,0)]:
            with self.subTest(bid=bid,ask=ask):
                self.assertEqual(sampled([dict(id='a',ts=0,order=0,bid=bid,ask=ask)])['value']['counts']['invalid'],1)

    def test_malformed_numeric_representation(self):
        for price in [float('nan'),float('inf'),1.1,True,I64+1]:
            with self.subTest(price=price),self.assertRaises(ValueError):
                sampled([dict(id='a',ts=0,order=0,bid=price,ask=102)])

    def test_missing_empty_and_incomplete(self):
        self.assertEqual(sampled(None)['status'],'missing_input')
        self.assertEqual(sampled([])['value']['counts']['total'],0)
        self.assertEqual(sampled([])['spread_status'],'not_applicable')
        self.assertIsNone(sampled(GOLD['rows'],complete=False)['value'])

    def test_equal_timestamps_last_state_no_duration(self):
        rows=[dict(id='a',ts=0,order=0,bid=100,ask=102),dict(id='b',ts=0,order=1,bid=100,ask=100)]
        self.assertEqual(sampled(rows)['value']['counts']['total'],2)
        self.assertEqual(continuous(rows)['value']['mean_abs'],0)
        self.assertEqual(continuous(rows)['value']['durations']['valid'],6)

    def test_cutoff_open_and_order_errors(self):
        row=dict(id='a',ts=0,order=0,bid=100,ask=102)
        self.assertEqual(sampled([row])['value']['counts']['total'],1)
        for ts in [-1,12]:
            with self.subTest(ts=ts),self.assertRaises(ValueError):sampled([{**row,'ts':ts}])
        with self.assertRaises(ValueError):sampled(list(reversed(GOLD['rows'])))
        with self.assertRaises(ValueError):sampled([row,row])
        with self.assertRaises(ValueError):sampled([row,{**row,'id':'b'}])

    def test_unknown_left_boundary(self):
        rows=[dict(id='a',ts=3,order=0,bid=100,ask=102)]
        result=continuous(rows)
        self.assertEqual(result['status'],'incomplete_coverage')
        self.assertIsNone(result['value']);self.assertEqual(result['observed']['durations']['unknown'],3)

    def test_known_inactive_left_boundary(self):
        rows=[dict(id='a',ts=3,order=0,bid=100,ask=102)]
        result=continuous(rows,initial='inactive')
        self.assertEqual(result['status'],'available')
        self.assertEqual(result['value']['durations']['invalid'],3)

    def test_seed_age_not_restarted(self):
        seed=dict(id='seed',ts=-4,order=0,bid=100,ask=102)
        result=continuous([],seed=seed)['value']
        self.assertEqual(result['durations']['valid'],2)
        self.assertEqual(result['durations']['expired'],10)
        self.assertEqual(sampled([])['value']['counts']['total'],0)
        with self.assertRaises(ValueError):continuous([],seed={**seed,'ts':0})

    def test_invalid_update_breaks_previous_quote(self):
        rows=[dict(id='a',ts=0,order=0,bid=100,ask=102),dict(id='b',ts=2,order=0,bid=None,ask=102)]
        value=continuous(rows,max_age=20)['value']
        self.assertEqual(value['durations']['valid'],2);self.assertEqual(value['durations']['invalid'],10)

    def test_excluded_update_does_not_refresh(self):
        rows=[dict(id='a',ts=0,order=0,bid=100,ask=102),dict(id='b',ts=4,order=0,bid=100,ask=102,eligible=False)]
        value=continuous(rows)['value']
        self.assertEqual(value['durations']['valid'],6);self.assertEqual(value['durations']['expired'],6)

    def test_cannot_time_weight_trade_samples(self):
        with self.assertRaises(ValueError):continuous([],kind='trade_associated')

    def test_age_configuration(self):
        for age in [0,-1,True,1.5,I64+1]:
            with self.subTest(age=age),self.assertRaises(ValueError):continuous([],max_age=age)

    def test_price_scale_and_wide_midpoint(self):
        rows=[dict(id='a',ts=0,order=0,bid=10000,ask=10200)]
        value=sampled(rows,scale=2)['value']
        self.assertEqual(value['mean_abs'],2);self.assertEqual(value['mean_bps'],F(20000,101))
        big=dict(id='b',ts=0,order=0,bid=I64-1,ask=I64)
        self.assertEqual(classify(big)[2],F(20000,2*I64-1))

    def test_duration_conservation(self):
        d=continuous(GOLD['rows'])['value']['durations']
        self.assertEqual(sum(d[k] for k in ['normal','locked','crossed','invalid','expired','unknown']),12)
        self.assertEqual(d['valid'],d['normal']+d['locked'])

    def test_partition_boundary_uses_carry_and_totals(self):
        rows=GOLD['rows'];full=continuous(rows)['value']
        a=continuous(rows[:2],end=6)['value']
        b=continuous(rows[2:],start=6,seed=rows[1])['value']
        d=a['durations']['valid']+b['durations']['valid']
        self.assertEqual((a['mean_abs']*a['durations']['valid']+b['mean_abs']*b['durations']['valid'])/d,full['mean_abs'])
        self.assertNotEqual((a['mean_abs']+b['mean_abs'])/2,full['mean_abs'])

    def test_partial_cutoff(self):
        value=continuous(GOLD['rows'][:2],end=5)['value']
        self.assertEqual(value['durations']['valid'],5)
        self.assertEqual(value['mean_abs'],F(6,5))
        with self.assertRaises(ValueError):continuous(GOLD['rows'],end=5)

    def test_continuous_delivery_gap_and_absent_input(self):
        result=continuous(GOLD['rows'],complete=False)
        self.assertEqual(result['status'],'incomplete_coverage')
        self.assertIsNone(result['value'])
        self.assertEqual(result['observed']['durations']['valid'],7)
        self.assertEqual(continuous(None)['status'],'missing_input')

    def test_no_valid_time_distinct_from_unknown(self):
        inactive=continuous([],initial='inactive')
        self.assertEqual(inactive['status'],'not_applicable')
        self.assertEqual(inactive['value']['durations']['invalid'],12)
        self.assertIsNone(inactive['value']['mean_abs'])
        self.assertEqual(continuous([])['status'],'incomplete_coverage')
        seed=dict(id='s',ts=-10,order=0,bid=100,ask=102)
        expired=continuous([],seed=seed)
        self.assertEqual(expired['status'],'not_applicable')
        self.assertEqual(expired['value']['durations']['expired'],12)

    def test_int64_expiry_and_duration_boundaries(self):
        row=dict(id='a',ts=I64-3,order=0,bid=100,ask=102)
        value=continuous([row],start=I64-3,end=I64,max_age=6)['value']
        self.assertEqual(value['durations']['valid'],3)
        self.assertEqual(value['mean_abs'],2)
        with self.assertRaises(ValueError):sampled([],start=-I64-1,end=I64)


if __name__ == '__main__':
    unittest.main(verbosity=2)
