"""Original EQ136 Fraction/Decimal oracle; not a production kernel or API.

Expanded smoothing weights intentionally avoid the implementation's iterative
recurrences. Tiny hand-derived goldens and algebraic invariants qualify the
specification, not optimized code, transport, source truth or performance.
"""
from decimal import Decimal, localcontext
from fractions import Fraction as F
import json
import math
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
GOLD = json.loads((ROOT / 'tests/fixtures/intraday_math/golden.json').read_text(encoding='utf-8'))
PROPOSAL = json.loads((ROOT / 'docs/stories/EQ-136_FIXTURES.json').read_text(encoding='utf-8'))


def weighted(values, period, alpha):
    """Closed form from seed plus expanded powers, not a state update."""
    if len(values) < period:
        return None
    seed = sum(values[:period], F()) / period
    tail = values[period:]
    q = 1 - alpha
    return seed * q**len(tail) + sum(
        (alpha * x * q**(len(tail)-1-i) for i, x in enumerate(tail)), F())


def ema(closes, period, anchor=0):
    return weighted([F(x) for x in closes[anchor:]], period, F(2, period+1))


def rsi(closes, period, anchor=0):
    changes = [F(b-a) for a, b in zip(closes[anchor:], closes[anchor+1:])]
    gains = weighted([max(x, F()) for x in changes], period, F(1, period))
    losses = weighted([max(-x, F()) for x in changes], period, F(1, period))
    if gains is None or losses is None:
        return None
    return 100*gains/(gains+losses) if gains+losses else F(50)


def true_ranges(closes, highs, lows, anchor=0):
    return [F(max(highs[i]-lows[i], abs(highs[i]-closes[i-1]),
                  abs(lows[i]-closes[i-1]))) for i in range(anchor+1, len(closes))]


def atr(closes, highs, lows, period, anchor=0):
    return weighted(true_ranges(closes, highs, lows, anchor), period, F(1, period))


def moments(closes, period, anchor=0):
    if len(closes)-anchor < period:
        return None
    window = [F(x) for x in closes[-period:]]
    mu = sum(window, F()) / period
    return mu, sum(((x-mu)**2 for x in window), F()) / period


def decimal(x):
    x = F(x)
    return Decimal(x.numerator)/Decimal(x.denominator)


def bands(closes, period, k=F(2), anchor=0, scale=0):
    mu, variance = moments(closes, period, anchor)
    with localcontext() as ctx:
        ctx.prec = 120
        radius = decimal(k)*decimal(variance).sqrt()
        middle = decimal(mu)
        # Center target in exact rational arithmetic before Decimal conversion.
        centered = decimal(F(closes[-1])-mu)
        divisor = Decimal(10)**scale
        return dict(middle=middle/divisor, upper=(middle+radius)/divisor,
                    lower=(middle-radius)/divisor,
                    width=2*radius/middle,
                    position=Decimal('0.5')+centered/(2*radius) if radius else None)


def operand_slots(feature, anchor, target, period):
    if feature == 'atr':
        # An epoch with no TR yet still observes its close anchor for warm-up.
        return {anchor} | set(range(anchor, target)), set(range(anchor+1, target+1))
    if feature == 'bands':
        return set(range(max(anchor, target-period+1), target+1)), set()
    if feature in ('ema', 'rsi'):
        return set(range(anchor, target+1)), set()
    raise ValueError('unknown reference family')


class IntradayReferences(unittest.TestCase):
    def test_hand_derived_rational_cases(self):
        self.assertEqual(GOLD['schema'], 'equity-features.intraday-math-goldens.v1')
        for case in GOLD['cases']:
            c, n, a = case['closes'], case['period'], case['anchor']
            actual = dict(ema=ema(c, n, a),
                          atr=atr(c, case['highs'], case['lows'], n, a))
            if 'rsi' in case:
                actual['rsi'] = rsi(c, n, a)
            if 'mean' in case:
                actual['mean'], actual['variance'] = moments(c, n, a)
            for name, value in actual.items():
                with self.subTest(case=case['name'], output=name):
                    self.assertEqual(value, None if case[name] is None else F(case[name]))

    def test_original_proposal_ema_seed_and_updates(self):
        c, n, e = PROPOSAL['closes'], PROPOSAL['period'], PROPOSAL['expected']['ema']
        self.assertEqual(ema(c[:3], n), F(e['seed_fraction']))
        for t in (3, 4):
            self.assertEqual(ema(c[:t+1], n), F(e[f'at_index_{t}']))

    def test_original_proposal_rsi(self):
        c, n, e = PROPOSAL['closes'], PROPOSAL['period'], PROPOSAL['expected']['rsi']
        self.assertEqual(sum((max(F(b-a), F()) for a,b in zip(c[:3], c[1:4])), F())/n, F(e['seed_gain']))
        self.assertEqual(sum((max(F(a-b), F()) for a,b in zip(c[:3], c[1:4])), F())/n, F(e['seed_loss']))
        for t in (3, 4):
            self.assertEqual(rsi(c[:t+1], n), F(e[f'at_index_{t}']))

    def test_original_proposal_atr(self):
        c, h, lo, n = (PROPOSAL[x] for x in ('closes', 'highs', 'lows', 'period'))
        e = PROPOSAL['expected']['atr']
        self.assertEqual(true_ranges(c, h, lo), e['true_ranges_indices_1_to_4'])
        self.assertEqual(atr(c[:4], h[:4], lo[:4], n), F(e['seed_fraction']))
        self.assertEqual(atr(c, h, lo, n), F(e['at_index_4']))

    def test_original_band_algebra(self):
        b = bands([10,12,11,14,13], 3)
        with localcontext() as ctx:
            ctx.prec = 120
            root = Decimal(14).sqrt()
            # Independently simplified symbolic formulas in the published toy.
            tol = Decimal('1e-115')
            self.assertLess(abs(b['upper']-(38+2*root)/3), tol)
            self.assertLess(abs(b['lower']-(38-2*root)/3), tol)
            self.assertLess(abs(b['width']-2*root/19), tol)
            self.assertLess(abs(b['position']-(1+2*root)/(4*root)), tol)

    def test_first_eligible_and_seed_boundaries(self):
        for n in (2,3,14):
            c = list(range(100, 100+n+1))
            self.assertIsNone(ema(c[:n-1], n))
            self.assertIsNotNone(ema(c[:n], n))
            self.assertIsNone(rsi(c[:n], n))
            self.assertEqual(rsi(c[:n+1], n), 100)
            h, lo = [x+1 for x in c], [x-1 for x in c]
            self.assertIsNone(atr(c[:n], h[:n], lo[:n], n))
            self.assertEqual(atr(c, h, lo, n), 2)

    def test_flat_rsi_not_empty(self):
        self.assertIsNone(rsi([10,10,10], 3))
        self.assertEqual(rsi([10]*4, 3), 50)

    def test_flat_tail_preserves_non_neutral_ratio(self):
        c = [10,12,11,14]
        value = rsi(c, 3)
        self.assertEqual(value, F(250,3))
        self.assertEqual(rsi(c+[14]*1200, 3), value)

    def test_atr_target_close_is_not_operand(self):
        c, h, lo = [10,12,11,14,13], [11,13,13,15,15], [9,10,10,11,12]
        expected = atr(c, h, lo, 3)
        c[-1] = None
        self.assertEqual(atr(c, h, lo, 3), expected)

    def test_atr_initial_high_low_are_not_operands(self):
        self.assertEqual(atr([10,12,11,14,13], [None,13,13,15,15],
                             [None,10,10,11,12], 3), F(29,9))

    def test_previous_close_not_replaced_with_range(self):
        self.assertEqual(true_ranges([100,110], [None,112], [None,109]), [12])
        self.assertNotEqual(atr([100,110], [None,112], [None,109], 1), 3)

    def test_direct_operand_goldens(self):
        for case in GOLD['operand_cases']:
            with self.subTest(feature=case['feature']):
                c, hl = operand_slots(case['feature'], case['anchor'], case['target'], case['period'])
                self.assertEqual(sorted(c), case['closes'])
                self.assertEqual(sorted(hl), case['high_low'])

    def test_single_anchor_atr_warmup_observes_close_only(self):
        c, hl = operand_slots('atr', 0, 0, 1)
        self.assertEqual(c, {0})
        self.assertEqual(hl, set())
        self.assertEqual(len(c|hl), 1)  # observed1 against required N+1=2
        self.assertIsNone(atr([10], [None], [None], 1))

    def test_old_gap_recovers_only_finite_window(self):
        for family in ('ema','rsi','atr','bands'):
            c, hl = operand_slots(family, 0, 4, 3)
            self.assertEqual(0 in c|hl, family != 'bands')

    def test_large_offset_preserves_variance(self):
        center = 2**60
        self.assertEqual(moments([center-1,center,center+1], 3), (F(center), F(2,3)))

    def test_equal_rounded_bounds_do_not_zero_width(self):
        b = bands([2**60-1,2**60,2**60+1], 3)
        self.assertEqual(float(b['upper']), float(b['lower']))
        self.assertGreater(float(b['width']), 0)
        self.assertGreater(float(b['position']), .8)
        self.assertLess(float(b['position']), .81)

    def test_zero_variance_cell_independence(self):
        b = bands([9,9,9], 3)
        self.assertEqual((b['middle'],b['upper'],b['lower']), (9,9,9))
        self.assertEqual(b['width'], 0)
        self.assertIsNone(b['position'])

    def test_negative_lower_and_unclamped_position(self):
        self.assertEqual(bands([1,9], 2)['lower'], -3)
        self.assertEqual(bands([1,9], 2, F(1,10))['position'], Decimal('5.5'))

    def test_exact_zero_lower(self):
        self.assertEqual(bands([1,3], 2)['lower'], 0)

    def test_scaled_units_and_dimensionless_ratios(self):
        c = [10,12,11,14,13]
        a, b = bands(c, 3), bands(c, 3, scale=4)
        with localcontext() as ctx:
            ctx.prec = 120
            for key in ('middle','upper','lower'):
                self.assertEqual(a[key].scaleb(-4), b[key])
        for key in ('width','position'):
            self.assertEqual(a[key], b[key])

    def test_numerator_wider_than_decimal128(self):
        c = [2**63-1,2**63-2,2**63-3]*1000
        self.assertGreater(sum(x*x for x in c), 10**38)
        self.assertEqual(moments(c, len(c))[1], F(2,3))

    def test_knowledge_and_completed_interval_truth_table(self):
        for row in GOLD['cutoff_cases']:
            with self.subTest(case=row['name']):
                self.assertEqual(row['end'] <= row['C'], row['market_ok'])
                reason = ('unknown_availability' if row['known'] is None else
                          'future_knowledge' if row['known'] > row['K'] else None)
                self.assertEqual(reason, row['knowledge_reason'])

    def test_relative_tolerance_cannot_erase_tiny_width(self):
        r = float(bands([2**60-1,2**60,2**60+1], 3)['width'])
        tolerance = max(8*math.ulp(r), 1e-12*abs(r))
        self.assertGreater(abs(r-0.0), tolerance)

    def test_reset_does_not_consume_previous_epoch(self):
        a, b = ema([10,11,12,20,21],2,3), ema([1000,1,999,20,21],2,3)
        self.assertEqual(a, F(41,2))
        self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
