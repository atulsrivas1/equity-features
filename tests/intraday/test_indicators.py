"""Original expanded-weight rational oracles; no production recurrence as oracle."""
from dataclasses import replace
from decimal import getcontext, setcontext, ROUND_DOWN
from fractions import Fraction as F
import math
import unittest

from equity_feature_contracts import (
    AvailabilitySpec, Column, ContractError, ErrorCode, InputScope, Reason, SessionSpec, Status,
)
from equity_features_intraday import (
    IntradayContext, IntradayRun, build_intraday_config, compute_intraday, prepare_intraday,
)
from test_admission import split
from test_preparation import supplied

FEATURES = ('intraday.atr', 'intraday.ema', 'intraday.rsi')


def fixture(closes=(10,12,11,14,13), period=3, **kwargs):
    if 'highs' not in kwargs:
        kwargs['highs'] = tuple(x+2 if x is not None else None for x in closes)
    if 'lows' not in kwargs:
        kwargs['lows'] = tuple(max(1,x-2) if x is not None else None for x in closes)
    b,c,cfg = supplied(closes=closes, **kwargs)
    cfg = replace(cfg,parameters=tuple(replace(p,value=period) if p.name=='period' else p
                                      for p in cfg.parameters))
    return b,c,cfg


def weighted(values, n, alpha):
    """Expanded seed and geometric weights; deliberately no recursive state."""
    tail = len(values)-n
    return (sum(values[:n],F())/n * (1-alpha)**tail +
            sum((alpha*(1-alpha)**(tail-j-1)*x for j,x in enumerate(values[n:])),F()))


def oracle(closes,n,highs,lows,scale=0):
    closes=tuple(map(F,closes)); divisor=10**scale
    delta=tuple(b-a for a,b in zip(closes,closes[1:]))
    gain=weighted(tuple(max(x,F()) for x in delta),n,F(1,n))
    loss=weighted(tuple(max(-x,F()) for x in delta),n,F(1,n))
    tr=tuple(max(highs[i]-lows[i],abs(highs[i]-closes[i-1]),abs(lows[i]-closes[i-1]))
             for i in range(1,len(closes)))
    return {'intraday.ema':weighted(closes,n,F(2,n+1))/divisor,
            'intraday.rsi':F(50) if gain==loss==0 else 100*gain/(gain+loss),
            'intraday.atr':weighted(tr,n,F(1,n))/divisor}


def run(facts, features=FEATURES, preparation=None):
    return compute_intraday(*facts,features=features,preparation=preparation)


class IndicatorTests(unittest.TestCase):
    def assert_close(self,value,expected):
        ref=float(expected)
        self.assertLessEqual(abs(value-ref),max(8*math.ulp(ref),1e-12*abs(ref)))

    def test_original_expanded_rational_cases(self):
        for n in (2,3,7,20):
            for length in (n+1,n+5,n+17):
                for origin,scale in ((10,0),(2**60,0),(10**18,18)):
                    closes=tuple(origin+(i*i+3*i)%7 for i in range(length))
                    highs=tuple(x+2 for x in closes);lows=tuple(x-2 for x in closes)
                    expected=oracle(closes,n,highs,lows,scale)
                    result=run(fixture(closes,n,highs=highs,lows=lows,scale=scale))
                    for column in result.values:
                        with self.subTest(n=n,length=length,scale=scale,feature=column.feature_id):
                            self.assert_close(column.values[0],expected[column.feature_id])

    def test_flat_up_down_extremes(self):
        for closes,expected in (((10,)*8,50), (tuple(range(10,18)),100), (tuple(range(18,10,-1)),0)):
            result=run(fixture(closes),features=('intraday.rsi',))
            self.assertEqual(result.values[0].values,(float(expected),))
            if expected==0:self.assertEqual(math.copysign(1,result.values[0].values[0]),1)

    def test_long_flat_tail_preserves_non_neutral_ratio(self):
        closes=(10,12,11)+(11,)*4093
        result=run(fixture(closes,2,absent=('high','low')),features=('intraday.rsi',))
        self.assert_close(result.values[0].values[0],F(200,3))
        self.assertNotEqual(result.values[0].values[0],50)

    def test_hostile_global_decimal_context_unchanged(self):
        original=getcontext().copy()
        try:
            getcontext().prec=2;getcontext().rounding=ROUND_DOWN
            getcontext().Emin=-9;getcontext().Emax=9
            snapshot=getcontext().copy()
            result=run(fixture())
            self.assertEqual(getcontext().prec,snapshot.prec)
            self.assertEqual(getcontext().rounding,snapshot.rounding)
            self.assertEqual(getcontext().flags,snapshot.flags)
            self.assertEqual(getcontext().traps,snapshot.traps)
            self.assertEqual((getcontext().Emin,getcontext().Emax),(-9,9))
            expected=oracle((10,12,11,14,13),3,(12,14,13,16,15),(8,10,9,12,11))
            for col in result.values:self.assert_close(col.values[0],expected[col.feature_id])
        finally:setcontext(original)

    def test_three_closes_ema_ready_rsi_atr_not_yet(self):
        result=run(fixture((10,12,11)))
        by={q.feature_id:q for q in result.quality}
        self.assertEqual(by['intraday.ema'].status,Status.AVAILABLE)
        for name in ('intraday.rsi','intraday.atr'):
            self.assertEqual(by[name].status,Status.INSUFFICIENT_HISTORY)
            self.assertEqual((by[name].expected,by[name].observed),(4,3))

    def test_single_anchor_and_period_one(self):
        result=run(fixture((10,),1),features=('intraday.ema','intraday.atr'))
        self.assertEqual(result.values[1].values,(10.0,))
        self.assertEqual((result.quality[0].status,result.quality[0].expected,result.quality[0].observed),
                         (Status.INSUFFICIENT_HISTORY,2,1))
        result=run(fixture((10,12),1),features=('intraday.ema','intraday.atr'))
        self.assertEqual(tuple(c.values[0] for c in result.values),(4.0,12.0))

    def test_unrelated_high_low_and_target_close_independence(self):
        result=run(fixture(absent=('high','low')))
        self.assertEqual(tuple(q.status for q in result.quality),
                         (Status.MISSING_INPUT,Status.AVAILABLE,Status.AVAILABLE))
        facts=fixture((10,12,11,14,None),highs=(12,14,13,16,15),lows=(8,10,9,12,11))
        result=run(facts)
        self.assertEqual(tuple(q.status for q in result.quality),
                         (Status.AVAILABLE,Status.INCOMPLETE_COVERAGE,Status.INCOMPLETE_COVERAGE))

    def test_absent_delivery_and_empty_delivery_distinct(self):
        b,c,cfg=fixture((10,12))
        absent=run((None,c,cfg));empty=run(((),c,cfg))
        for q in absent.quality:
            self.assertEqual((q.status,q.observed,q.reasons),
                             (Status.MISSING_INPUT,0,(Reason.ABSENT_INPUT,)))
        for q in empty.quality:
            self.assertEqual(q.status,Status.INSUFFICIENT_HISTORY)
            self.assertIn(Reason.OBSERVED_EMPTY,q.reasons)
            self.assertIn(Reason.GOVERNED_GAP,q.reasons)
        self.assertFalse(absent.metadata.inputs)

    def test_gap_and_knowledge_exclusions_keep_full_counts(self):
        for kwargs,reason in (({'missing':(0,)},Reason.GOVERNED_GAP),
                              ({'unknown':(0,)},Reason.UNKNOWN_AVAILABILITY),
                              ({'future':(0,)},Reason.FUTURE_KNOWLEDGE)):
            result=run(fixture(**kwargs))
            for q in result.quality:
                self.assertEqual((q.status,q.expected,q.observed),(Status.INCOMPLETE_COVERAGE,5,4))
                self.assertIn(reason,q.reasons)
            for e in result.evidence:
                if e.row_id=='slot:0':self.assertEqual(e.use,'excluded')

    def test_shared_selected_and_superset_full_result_parity(self):
        for kwargs in ({},{'absent':('high','low')},{'future':(0,)},{'missing':(0,)}):
            facts=fixture(**kwargs);b,c,cfg=facts
            shared=prepare_intraday(*facts,requirements=('anchored_closes','true_ranges','price_moments'))
            for selected in (FEATURES,('intraday.ema',),('intraday.rsi',),('intraday.atr',)):
                self.assertEqual(run(facts,selected),run((tuple(b),c,cfg),selected,shared))

    def test_individual_values_and_global_evidence_limit(self):
        for limit in (0,2,7,15):
            b,c,cfg=fixture();cfg=replace(cfg,parameters=tuple(replace(p,value=limit)
                           if p.name=='evidence_limit' else p for p in cfg.parameters));facts=b,c,cfg
            result=run(facts)
            expected=[(feature,f'slot:{i}') for feature in FEATURES for i in range(5)][:limit]
            self.assertEqual([(e.feature_id,e.row_id) for e in result.evidence],expected)
            for col,q in zip(result.values,result.quality):
                single=run(facts,(col.feature_id,))
                self.assertEqual(single.values,(col,));self.assertEqual(single.quality,(q,))
                self.assertEqual(single.metadata,result.metadata)
                for e in single.evidence:
                    self.assertEqual((e.event_ns,e.effective_start_ns,e.effective_end_ns,e.boundary),
                                     ((int(e.row_id[5:])+1)*10,int(e.row_id[5:])*10,(int(e.row_id[5:])+1)*10,'completed_interval'))

    def test_preparation_identity_and_missing_family_rejections(self):
        facts=fixture();b,c,cfg=facts
        shared=prepare_intraday(*facts,requirements=('anchored_closes',))
        for other,selected,code in (((None,c,cfg),('intraday.ema',),ErrorCode.INCONSISTENT_IDENTITY),
                                    ((tuple(replace(x) for x in b),c,cfg),('intraday.ema',),ErrorCode.INCONSISTENT_IDENTITY),
                                    (facts,('intraday.atr',),ErrorCode.UNSUPPORTED_CAPABILITY)):
            with self.assertRaises(ContractError) as caught:run(other,selected,shared)
            self.assertEqual(caught.exception.code,code)

    def test_selected_period_limits(self):
        for n,feature in ((1,'intraday.rsi'),(4096,'intraday.rsi'),(4096,'intraday.atr')):
            with self.assertRaises(ContractError) as caught:run(fixture(period=n),(feature,))
            self.assertEqual(caught.exception.code,ErrorCode.INVALID_CONFIG)
        self.assertEqual(run(fixture(period=4096),('intraday.ema',)).quality[0].expected,4096)

    def test_maximum_seed_bounds_large_scaled_coefficients(self):
        closes=(2**63-1,)*4096
        result=run(fixture(closes,4095,absent=('high','low'),scale=18),('intraday.rsi','intraday.ema'))
        self.assertEqual(result.values[1].values,(50.0,))
        self.assert_close(result.values[0].values[0],F(2**63-1,10**18))

    def test_corrected_snapshot_does_not_mutate_original(self):
        facts=fixture();original=run(facts)
        b,c,cfg=fixture((10,12,11,14,14));c=replace(c,revision='corrected')
        cfg=build_intraday_config(c,period=3,band_k=F(2),availability=cfg.availability,
            adjustment=cfg.adjustment,price_unit=cfg.price_unit,evidence_limit=10)
        b=tuple(replace(batch,metadata=replace(batch.metadata,source=replace(batch.metadata.source,
            snapshot_id='corrected'))) for batch in b)
        corrected=run((b,c,cfg))
        self.assertNotEqual(original.values,corrected.values)
        self.assertNotEqual(original.metadata.identity_digest,corrected.metadata.identity_digest)
        self.assertEqual(original,run(fixture()))

    def test_explicit_reset_and_carry_across_actual_sessions(self):
        batches,_,base=fixture()
        sessions=(SessionSpec('synthetic','S0',0,20,'UTC'),SessionSpec('synthetic','S1',30,60,'UTC'))
        runs=(IntradayRun('S0',0,10,2),IntradayRun('S1',30,10,3))
        carry=IntradayContext('A','cal','grid','revision',sessions,runs,0,4,'carry')
        a,b=split(batches[0],2)
        a=replace(a,columns=tuple(Column(col.name,('S0',)*2) if col.name=='session_id' else col for col in a.columns))
        b=replace(b,columns=tuple(Column(col.name,('S1',)*3 if col.name=='session_id' else
                  tuple(v+10 for v in col.values) if col.name in ('start_ns','end_ns','known_at_ns') else col.values)
                  for col in b.columns),metadata=replace(b.metadata,scope=InputScope(30,60,'synthetic-v1'),
                  interval_coverage=tuple(replace(i,start_ns=i.start_ns+10,end_ns=i.end_ns+10)
                                          for i in b.metadata.interval_coverage)))
        expected=oracle((10,12,11,14,13),2,(12,14,13,16,15),(8,10,9,12,11))
        for ctx in (carry,replace(carry,mode='reset',anchor_index=2)):
            cfg=build_intraday_config(ctx,period=2,band_k=F(2),availability=AvailabilitySpec(60,60,60),
                                     adjustment=base.adjustment,price_unit=base.price_unit)
            result=run(((a,b),ctx,cfg))
            wanted=expected if ctx.mode=='carry' else oracle((11,14,13),2,(13,16,15),(9,12,11))
            for col in result.values:self.assert_close(col.values[0],wanted[col.feature_id])
            self.assertEqual(result.metadata.session_id,'S1')


if __name__=='__main__':unittest.main()
