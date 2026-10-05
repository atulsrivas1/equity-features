"""Synthetic exact EQ-004 mathematics references; not a production API."""
from copy import deepcopy
from decimal import Decimal, localcontext
from fractions import Fraction as F
from pathlib import Path
import json
import re
import unittest

ROOT=Path(__file__).resolve().parents[1]
GOLD=json.loads((ROOT/'tests/fixtures/history_math/golden.json').read_text(encoding='utf-8'))
I64=2**63-1


class Unready(Exception):
    def __init__(self,status): self.status=status


def history(rows,feature,n=3,scale=0,cutoff=60,anchor=0,annualization=1):
    supported={'return','sma','ema','rsi','atr','prior_high','prior_low','return_volatility'}
    if feature not in supported: raise ValueError('feature')
    if type(n) is not int or n < (2 if feature in ('rsi','return_volatility') else 1):
        raise ValueError('period')
    if type(scale) is not int or not 0<=scale<=18: raise ValueError('scale')
    if type(cutoff) is not int or not -I64-1<=cutoff<=I64: raise ValueError('cutoff')
    if type(anchor) is not int or anchor<0: raise ValueError('anchor')
    if type(annualization) is not int or annualization<1: raise ValueError('annualization')
    if rows is None: return dict(status='missing_input',value=None)
    if not rows: return dict(status='insufficient_history',value=None)
    previous_end=None
    for i,row in enumerate(rows):
        if row is None: continue
        if row['session']!=i or type(row['session']) is not int:
            raise ValueError('governed-grid identity/order')
        if type(row['end']) is not int or not -I64-1<=row['end']<=I64:
            raise ValueError('time representation')
        if previous_end is not None and row['end']<=previous_end:
            raise ValueError('session time order')
        previous_end=row['end']
        for field in ('close','high','low'):
            p=row.get(field)
            if p is not None and (type(p) is not int or not 0<p<=I64):
                raise ValueError('price representation')
        if row.get('high') is not None and row.get('low') is not None:
            if row['high']<row['low']: raise ValueError('range')
            if row.get('close') is not None and not row['low']<=row['close']<=row['high']:
                raise ValueError('OHLC')
    t=len(rows)-1
    def get(i,field):
        if i<0 or i>=len(rows): raise Unready('insufficient_history')
        row=rows[i]
        if row is None or not row.get('complete',True) or row['end']>cutoff:
            raise Unready('incomplete_coverage')
        if not row.get('available',True): raise Unready('missing_input')
        if field not in row: raise Unready('missing_input')
        if row[field] is None: raise Unready('incomplete_coverage')
        return F(row[field],10**scale)
    def seq(left,right,field='close'): return [get(i,field) for i in range(left,right+1)]
    try:
        if feature=='return':
            prices=seq(t-n,t)
            value=prices[-1]/prices[0]-1
        elif feature=='sma': value=sum(seq(t-n+1,t),F())/n
        elif feature in ('prior_high','prior_low'):
            values=seq(t-n,t-1,'high' if feature=='prior_high' else 'low')
            value=(max if feature=='prior_high' else min)(values)
        elif feature=='ema':
            if t-anchor+1<n: raise Unready('insufficient_history')
            prices=seq(anchor,t)
            value=sum(prices[:n],F())/n
            alpha=F(2,n+1)
            for price in prices[n:]: value=alpha*price+(1-alpha)*value
        elif feature=='rsi':
            if t-anchor<n: raise Unready('insufficient_history')
            prices=seq(anchor,t)
            changes=[b-a for a,b in zip(prices,prices[1:])]
            gains=[max(x,F()) for x in changes];losses=[max(-x,F()) for x in changes]
            gain=sum(gains[:n],F())/n;loss=sum(losses[:n],F())/n
            for g,l in zip(gains[n:],losses[n:]):
                gain=((n-1)*gain+g)/n;loss=((n-1)*loss+l)/n
            value=100*gain/(gain+loss) if gain+loss else F(50)
        elif feature=='atr':
            # anchor is the first TR-bearing session; previous close is mandatory.
            if t-anchor+1<n or anchor<1: raise Unready('insufficient_history')
            values=[]
            for i in range(anchor,t+1):
                high,low,previous=get(i,'high'),get(i,'low'),get(i-1,'close')
                values.append(max(high-low,abs(high-previous),abs(low-previous)))
            value=sum(values[:n],F())/n
            for v in values[n:]: value=((n-1)*value+v)/n
        else:
            prices=seq(t-n,t)
            returns=[b/a-1 for a,b in zip(prices,prices[1:])]
            mean=sum(returns,F())/n
            variance=sum(((x-mean)**2 for x in returns),F())/(n-1)
            with localcontext() as ctx:
                ctx.prec=60
                value=(Decimal(variance.numerator*annualization)/Decimal(variance.denominator)).sqrt()
            return dict(status='available',value=value,variance=variance,
                        scaled_variance=variance*annualization)
        return dict(status='available',value=value)
    except Unready as exc:
        return dict(status=exc.status,value=None)


class HistoryReferences(unittest.TestCase):
    def test_eight_definition_coverage(self):
        scope=(ROOT/'docs/features/V1_SCOPE.md').read_text(encoding='utf-8')
        doc=(ROOT/'docs/features/HISTORICAL_FORMULAS.md').read_text(encoding='utf-8')
        ids=set(re.findall(r'^\| (history\.[a-z_]+) \|',scope,re.M))
        self.assertEqual(len(ids),8)
        self.assertEqual(ids,set(re.findall(r'^\| (history\.[a-z_]+) \|',doc,re.M)))

    def test_golden_nonrecursive(self):
        for feature in ('return','sma','prior_high','prior_low'):
            with self.subTest(feature=feature):
                self.assertEqual(history(GOLD['rows'],feature)['value'],F(GOLD['expected'][feature]))

    def test_golden_ema(self):
        self.assertEqual(history(GOLD['rows'],'ema')['value'],F(GOLD['expected']['ema']))

    def test_golden_rsi(self):
        self.assertEqual(history(GOLD['rows'],'rsi')['value'],F(GOLD['expected']['rsi']))

    def test_golden_atr(self):
        self.assertEqual(history(GOLD['rows'],'atr',anchor=1)['value'],F(GOLD['expected']['atr']))

    def test_golden_volatility(self):
        result=history(GOLD['rows'],'return_volatility')
        self.assertEqual(result['variance'],F(GOLD['expected']['variance']))
        expected=Decimal(GOLD['expected']['volatility'])
        self.assertLess(abs(result['value']-expected),Decimal('1e-12'))

    def test_seed_and_warmup_boundaries(self):
        rows=GOLD['rows']
        for feature in ('sma','ema'):
            self.assertEqual(history(rows[:2],feature)['status'],'insufficient_history')
            self.assertEqual(history(rows[:3],feature)['value'],105)
        for feature in ('rsi','return','return_volatility'):
            self.assertEqual(history(rows[:3],feature)['status'],'insufficient_history')
            self.assertEqual(history(rows[:4],feature)['status'],'available')
        self.assertEqual(history(rows[:3],'atr',anchor=1)['status'],'insufficient_history')
        self.assertEqual(history(rows[:4],'atr',anchor=1)['value'],13)

    def test_period_one_identities(self):
        rows=GOLD['rows']
        self.assertEqual(history(rows,'sma',n=1)['value'],130)
        self.assertEqual(history(rows,'ema',n=1)['value'],130)
        self.assertEqual(history(rows,'atr',n=1,anchor=1)['value'],18)

    def test_invalid_parameters(self):
        for n in (0,-1,True,1.5):
            with self.subTest(n=n),self.assertRaises(ValueError):history(GOLD['rows'],'sma',n=n)
        for feature in ('rsi','return_volatility'):
            with self.assertRaises(ValueError):history(GOLD['rows'],feature,n=1)
        for factor in (0,-1,True,1.5):
            with self.assertRaises(ValueError):history(GOLD['rows'],'return_volatility',annualization=factor)

    def test_rsi_one_direction_and_flat(self):
        for closes,expected in [([100,101,102,103],100),([100,99,98,97],0),([100]*4,50)]:
            rows=[dict(session=i,end=10*(i+1),close=p) for i,p in enumerate(closes)]
            self.assertEqual(history(rows,'rsi')['value'],expected)

    def test_flat_after_moves_preserves_rsi_ratio(self):
        rows=[dict(session=i,end=i+1,close=p) for i,p in enumerate([100,110,105,120]+[120]*300)]
        self.assertEqual(history(rows,'rsi',cutoff=1000)['value'],F(250,3))

    def test_prior_extrema_exclude_target(self):
        rows=deepcopy(GOLD['rows']);rows[-1].update(high=1000,low=1)
        self.assertEqual(history(rows,'prior_high')['value'],122)
        self.assertEqual(history(rows,'prior_low')['value'],103)

    def test_governed_missing_slot_not_compressed(self):
        rows=deepcopy(GOLD['rows']);rows[3]=None
        for feature in ('return','sma','ema','rsi','prior_high','atr','return_volatility'):
            self.assertEqual(history(rows,feature,anchor=1 if feature=='atr' else 0)['status'],'incomplete_coverage')
        compressed=[r for r in rows if r is not None]
        with self.assertRaises(ValueError):history(compressed,'sma')

    def test_rolling_recovery_not_recursive_restart(self):
        rows=deepcopy(GOLD['rows']);rows[1]=None
        self.assertEqual(history(rows,'sma')['value'],F(365,3))
        self.assertEqual(history(rows,'ema')['status'],'incomplete_coverage')
        self.assertEqual(history(rows,'rsi')['status'],'incomplete_coverage')
        self.assertEqual(history(rows,'ema',anchor=2)['status'],'available')

    def test_missing_high_does_not_break_close_features(self):
        rows=deepcopy(GOLD['rows']);del rows[3]['high']
        self.assertEqual(history(rows,'sma')['status'],'available')
        self.assertEqual(history(rows,'atr',anchor=1)['status'],'missing_input')
        self.assertEqual(history(rows,'prior_high')['status'],'missing_input')

    def test_null_completed_and_availability(self):
        for patch,status in [({'close':None},'incomplete_coverage'),({'complete':False},'incomplete_coverage'),({'available':False},'missing_input')]:
            rows=deepcopy(GOLD['rows']);rows[-1].update(patch)
            self.assertEqual(history(rows,'sma')['status'],status)

    def test_absent_empty_history(self):
        self.assertEqual(history(None,'sma')['status'],'missing_input')
        self.assertEqual(history([],'sma')['status'],'insufficient_history')

    def test_cutoff_excludes_unfinished_target(self):
        self.assertEqual(history(GOLD['rows'],'sma',cutoff=59)['status'],'incomplete_coverage')
        self.assertEqual(history(GOLD['rows'],'sma',cutoff=60)['status'],'available')
        self.assertEqual(history(GOLD['rows'],'prior_high',cutoff=50)['status'],'available')

    def test_invalid_prices_and_ranges(self):
        for price in (0,-1,True,1.1,float('nan'),I64+1):
            rows=deepcopy(GOLD['rows']);rows[0]['close']=price
            with self.subTest(price=price),self.assertRaises(ValueError):history(rows,'ema')
        rows=deepcopy(GOLD['rows']);rows[1]['high']=98
        with self.assertRaises(ValueError):history(rows,'sma')

    def test_zero_true_range_is_valid(self):
        rows=[dict(session=i,end=(i+1)*10,close=100,high=100,low=100) for i in range(4)]
        self.assertEqual(history(rows,'atr',anchor=1)['value'],0)

    def test_true_range_uses_previous_close(self):
        rows=[dict(session=0,end=10,close=100),dict(session=1,end=20,close=112,high=113,low=111)]
        self.assertEqual(history(rows,'atr',n=1,anchor=1)['value'],13)

    def test_volatility_centering_and_sample_denominator(self):
        rows=[dict(session=i,end=(i+1)*10,close=p) for i,p in enumerate([100,110,121,1331])]
        result=history(rows,'return_volatility')
        self.assertEqual(result['variance'],F(3267,100))
        self.assertNotEqual(result['variance'],F(3267,150))
        self.assertNotEqual(result['variance'],(F(1,100)+F(1,100)+100)/3)

    def test_volatility_annualization_explicit(self):
        a=history(GOLD['rows'],'return_volatility')
        b=history(GOLD['rows'],'return_volatility',annualization=252)
        self.assertEqual(b['scaled_variance'],a['variance']*252)
        self.assertNotEqual(a['value'],b['value'])

    def test_constant_returns_zero_volatility(self):
        rows=[dict(session=i,end=(i+1)*10,close=p) for i,p in enumerate([100,200,400,800])]
        self.assertEqual(history(rows,'return_volatility')['value'],0)

    def test_scale_and_wide_sums(self):
        rows=deepcopy(GOLD['rows'])
        for row in rows:
            for field in ('close','high','low'):row[field]*=100
        self.assertEqual(history(rows,'ema',scale=2)['value'],F(975,8))
        self.assertEqual(history(rows,'rsi',scale=2)['value'],F(4700,57))
        big=[dict(session=i,end=(i+1)*10,close=I64) for i in range(3)]
        self.assertEqual(history(big,'sma')['value'],I64)

    def test_anchor_changes_are_not_hidden(self):
        full=history(GOLD['rows'],'ema')['value']
        restarted=history(GOLD['rows'],'ema',anchor=2)['value']
        self.assertNotEqual(full,restarted)

    def test_recursive_recurrence_partition_carry(self):
        rows=GOLD['rows'];seed=history(rows[:4],'ema')['value']
        for row in rows[4:]:seed=F(1,2)*row['close']+F(1,2)*seed
        self.assertEqual(seed,history(rows,'ema')['value'])
        self.assertNotEqual((history(rows[:3],'ema')['value']+history(rows,'ema',anchor=3)['value'])/2,seed)

    def test_session_identity_and_time_order_validation(self):
        for index,field,value in [(1,'session',0),(1,'end',10),(0,'end',True),(0,'end',I64+1)]:
            rows=deepcopy(GOLD['rows']);rows[index][field]=value
            with self.subTest(field=field,value=value),self.assertRaises(ValueError):history(rows,'sma')

    def test_atr_previous_close_required_not_range_fallback(self):
        rows=deepcopy(GOLD['rows']);del rows[0]['close']
        self.assertEqual(history(rows,'atr',anchor=1)['status'],'missing_input')
        # Current close is context for next TR, not in the current TR equation.
        rows=deepcopy(GOLD['rows']);del rows[-1]['close']
        self.assertEqual(history(rows,'atr',anchor=1)['value'],F(122,9))

    def test_missing_price_slots_not_filled(self):
        rows=deepcopy(GOLD['rows']);rows[4]['close']=None
        for feature in ('sma','ema','rsi','return','return_volatility'):
            self.assertEqual(history(rows,feature)['status'],'incomplete_coverage')

    def test_extrema_ready_without_target_price(self):
        rows=deepcopy(GOLD['rows']);rows[-1]=None
        self.assertEqual(history(rows,'prior_high')['value'],122)
        self.assertEqual(history(rows,'prior_low')['value'],103)


if __name__=='__main__':unittest.main(verbosity=2)
