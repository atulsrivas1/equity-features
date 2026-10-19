"""Original centered/pairwise oracles and independent band readiness/identity cases."""
from dataclasses import replace
from decimal import Context, Decimal, ROUND_DOWN, ROUND_HALF_EVEN, getcontext, localcontext, setcontext
from fractions import Fraction as F
from itertools import combinations
import hashlib
import json
import math
from pathlib import Path
import unittest

from equity_feature_contracts import (
    AvailabilitySpec, Column, ContractError, ErrorCode, InputScope, Reason, SessionSpec, Status,
)
from equity_features_intraday import (
    IntradayContext, IntradayRun, build_intraday_config, compute_intraday, prepare_intraday,
)
from test_admission import split
from test_indicators import fixture


BANDS = tuple('intraday.band_'+name for name in ('lower','middle','position','upper','width_ratio'))
ORDER = ('intraday.band_middle','intraday.band_upper','intraday.band_lower',
         'intraday.band_width_ratio','intraday.band_position')
ALL = tuple(sorted((*BANDS,'intraday.atr','intraday.ema','intraday.rsi')))


def facts(closes=(10,12,11,14,13), n=3, k=F(2), **kwargs):
    kwargs.setdefault('absent',('high','low'))
    b,c,cfg=fixture(closes=closes,period=n,**kwargs)
    cfg=replace(cfg,parameters=tuple(replace(p,value=k.numerator if p.name=='k_num' else k.denominator)
        if p.name in ('k_num','k_den') else p for p in cfg.parameters))
    return b,c,cfg


def oracle(prices,k,scale=0):
    xs=tuple(F(x,10**scale) for x in prices);n=len(xs)
    mean=sum(xs,F())/n
    variance=sum(((x-mean)**2 for x in xs),F())/n
    if n <= 20:
        assert variance==sum(((a-b)**2 for a in xs for b in xs),F())/(2*n*n)
    radius2=k*k*variance
    rn,rd=math.isqrt(radius2.numerator),math.isqrt(radius2.denominator)
    exact=F(rn,rd) if rn*rn==radius2.numerator and rd*rd==radius2.denominator else None
    def dec(x):return Decimal(x.numerator)/Decimal(x.denominator)
    with localcontext(Context(prec=300,rounding=ROUND_HALF_EVEN,Emin=-999999,Emax=999999)):
        if exact is not None:
            values=(mean,mean+exact,mean-exact,2*exact/mean,
                    None if variance==0 else (xs[-1]-(mean-exact))/(2*exact))
            return dict(zip(ORDER,(None if x is None else 0.0 if x==0 else float(dec(x)) for x in values)))
        radius=dec(radius2).sqrt();center=dec(mean)
        # Independent direct expressions at 300digits, not production rationalizations.
        return dict(zip(ORDER,map(float,(center,center+radius,center-radius,2*radius/center,
                                             (dec(xs[-1])-(center-radius))/(2*radius)))))


class BandTests(unittest.TestCase):
    def assert_cells(self,result,expected):
        quality={q.feature_id:q for q in result.quality}
        for col in result.values:
            feature=col.feature_id;actual=col.values[0];ref=expected[feature]
            self.assertEqual(col.algorithm_version,'intraday-v1')
            self.assertEqual(col.unit,'fraction' if feature in ORDER[3:] else 'currency/share')
            if ref is None:
                self.assertIsNone(actual)
                self.assertEqual(quality[feature].status,Status.NOT_APPLICABLE)
                self.assertEqual(quality[feature].reasons,(Reason.ZERO_DENOMINATOR,))
            else:
                self.assertIsNotNone(actual);self.assertTrue(math.isfinite(actual))
                self.assertLessEqual(abs(actual-ref),max(8*math.ulp(ref),1e-12*abs(ref)))
                if ref==0:self.assertEqual(math.copysign(1,actual),1.0)
                self.assertEqual(quality[feature].status,Status.AVAILABLE)
                self.assertEqual(quality[feature].reasons,())

    def test_thirteen_fixed_original_goldens_and_independent_centered_oracle(self):
        root=Path(__file__).resolve().parents[1]/'fixtures/intraday_bands'
        value=json.loads((root/'GOLDENS.json').read_bytes())
        self.assertEqual(value['generator_sha256_lf'],hashlib.sha256(
            (root/'generate_original.py').read_bytes().replace(b'\r\n',b'\n')).hexdigest())
        self.assertEqual(len(value['cases']),13)
        for row in value['cases']:
            with self.subTest(case=row['id']):
                k=F(row['k']);expected=dict(zip(ORDER,row['outputs_middle_upper_lower_width_position']))
                self.assertEqual(oracle(row['prices'],k,row['scale']),expected)
                result=compute_intraday(*facts(tuple(row['prices']),row['period'],k,scale=row['scale']),features=BANDS)
                self.assert_cells(result,expected)
                self.assertTrue(all((q.expected,q.observed)==(row['period'],row['period']) for q in result.quality))

    def test_original_centered_windows_and_multiplier_extremes(self):
        for n in (2,3,7,20):
            for origin,scale in ((10,0),(2**60,0),(10**18,18)):
                prices=tuple(origin+(i*i+3*i)%11 for i in range(n+4))
                for k in (F(1,1000000),F(4,3),F(1000000)):
                    with self.subTest(n=n,scale=scale,k=k):
                        result=compute_intraday(*facts(prices,n,k,scale=scale),features=BANDS)
                        self.assert_cells(result,oracle(prices[-n:],k,scale))
                        self.assertTrue(all((q.expected,q.observed)==(n,n) for q in result.quality))

    def test_all_thirty_one_nonempty_band_subsets_and_superset_reuse(self):
        f=facts();expected=oracle((11,14,13),F(2))
        prepared=prepare_intraday(*f,requirements=('price_moments','anchored_closes'))
        for size in range(1,6):
            for selected in combinations(BANDS,size):
                direct=compute_intraday(*f,features=selected)
                self.assertEqual(direct,compute_intraday(*f,features=selected,preparation=prepared))
                self.assert_cells(direct,expected)

    def test_absence_empty_null_gap_and_knowledge_have_independent_quality(self):
        f=facts();b,c,cfg=f
        for supplied,status,observed,reasons in (
            (None,Status.MISSING_INPUT,0,{Reason.ABSENT_INPUT}),
            ((),Status.INCOMPLETE_COVERAGE,0,{Reason.GOVERNED_GAP,Reason.OBSERVED_EMPTY}),
        ):
            result=compute_intraday(supplied,c,cfg,features=BANDS)
            for q in result.quality:
                self.assertEqual((q.status,q.expected,q.observed),(status,3,observed))
                self.assertEqual(set(q.reasons),reasons)
        for kwargs,status,observed,reasons in (
            ({'absent':('close','high','low')},Status.MISSING_INPUT,0,{Reason.ABSENT_INPUT}),
            ({'closes':(10,12,None,14,13)},Status.INCOMPLETE_COVERAGE,2,{Reason.NULL_FIELD}),
            ({'missing':(3,)},Status.INCOMPLETE_COVERAGE,2,{Reason.GOVERNED_GAP}),
            ({'unknown':(3,)},Status.INCOMPLETE_COVERAGE,2,{Reason.UNKNOWN_AVAILABILITY}),
            ({'future':(4,)},Status.INCOMPLETE_COVERAGE,2,{Reason.FUTURE_KNOWLEDGE}),
        ):
            result=compute_intraday(*facts(**kwargs),features=BANDS)
            for q in result.quality:
                self.assertEqual((q.status,q.expected,q.observed),(status,3,observed))
                self.assertEqual(set(q.reasons),reasons)

    def test_feature_warmup_precedence_and_absent_delivery_short_circuit(self):
        for kwargs,status,observed,reasons in (
            ({},Status.INSUFFICIENT_HISTORY,2,{Reason.INSUFFICIENT_HISTORY}),
            ({'absent':('close','high','low')},Status.MISSING_INPUT,0,{Reason.ABSENT_INPUT,Reason.INSUFFICIENT_HISTORY}),
        ):
            f=facts((10,12),3,**kwargs)
            result=compute_intraday(*f,features=BANDS)
            for q in result.quality:
                self.assertEqual((q.status,q.expected,q.observed),(status,3,observed))
                self.assertEqual(set(q.reasons),reasons)
            absent=compute_intraday(None,f[1],f[2],features=BANDS)
            self.assertTrue(all(q.reasons==(Reason.ABSENT_INPUT,) and q.expected==3 for q in absent.quality))

    def test_out_of_window_gap_and_knowledge_do_not_block_bands(self):
        for kwargs in ({'missing':(0,)},{'unknown':(0,)},{'future':(0,)}):
            f=facts(**kwargs)
            result=compute_intraday(*f,features=(*BANDS,'intraday.ema'))
            band_result=compute_intraday(*f,features=BANDS)
            self.assert_cells(band_result,oracle((11,14,13),F(2)))
            q={x.feature_id:x for x in result.quality}
            self.assertTrue(all(q[feature].status==Status.AVAILABLE for feature in BANDS))
            self.assertEqual(q['intraday.ema'].status,Status.INCOMPLETE_COVERAGE)

    def test_missing_target_close_preserves_atr(self):
        b,c,cfg=facts(absent=())
        chunks=split(b[0],4)
        chunks=(chunks[0],replace(chunks[1],columns=tuple(x for x in chunks[1].columns if x.name!='close')))
        result=compute_intraday(chunks,c,cfg,features=ALL)
        quality={q.feature_id:q for q in result.quality}
        self.assertEqual(quality['intraday.atr'].status,Status.AVAILABLE)
        for feature in (*BANDS,'intraday.ema','intraday.rsi'):
            self.assertEqual(quality[feature].status,Status.MISSING_INPUT)
            self.assertEqual(quality[feature].reasons,(Reason.ABSENT_INPUT,))

    def test_observed_empty_slot_retains_two_empty_reasons_without_null(self):
        b,c,cfg=facts(absent=())
        batch=replace(b[0],columns=tuple(Column(col.name,col.values[:3]+(None,)+col.values[4:])
            if col.name in ('close','high','low') else col for col in b[0].columns)
            +(Column('volume',(1,1,1,0,1)),))
        result=compute_intraday((batch,),c,cfg,features=BANDS)
        for q in result.quality:
            self.assertEqual((q.status,q.expected,q.observed),(Status.INCOMPLETE_COVERAGE,3,2))
            self.assertEqual(set(q.reasons),{Reason.OBSERVED_EMPTY,Reason.NO_ELIGIBLE_OBSERVATIONS})

    def test_mixed_all_eight_result_identity_and_once_global_evidence(self):
        for limit in (0,1,4,16,100):
            b,c,cfg=facts(absent=())
            cfg=replace(cfg,parameters=tuple(replace(p,value=limit) if p.name=='evidence_limit' else p for p in cfg.parameters))
            prepared=prepare_intraday(b,c,cfg,requirements=('anchored_closes','price_moments','true_ranges'))
            result=compute_intraday(b,c,cfg,features=tuple(reversed(ALL)))
            self.assertEqual(result,compute_intraday(b,c,cfg,features=ALL,preparation=prepared))
            expected=[(feature,f'slot:{i}') for feature in ALL for i in (range(2,5) if feature in BANDS else range(5))][:limit]
            self.assertEqual([(e.feature_id,e.row_id) for e in result.evidence],expected)
            self.assertEqual(result.metadata.backend_version,'0.1.0a3')
            self.assertEqual(result.metadata.config_digest,cfg.digest)
            for col,q in zip(result.values,result.quality):
                single=compute_intraday(b,c,cfg,features=(col.feature_id,))
                self.assertEqual((single.values,single.quality,single.metadata),((col,),(q,),result.metadata))
                for e in single.evidence:
                    i=int(e.row_id[5:])
                    self.assertEqual((e.event_ns,e.known_at_ns,e.effective_start_ns,e.effective_end_ns,e.boundary),
                                     ((i+1)*10,(i+1)*10,i*10,(i+1)*10,'completed_interval'))

    def test_maximum_period_scale_int64_and_minimum_period_admission(self):
        prices=tuple(2**63-4096+i for i in range(4096))
        result=compute_intraday(*facts(prices,4096,F(1000000),scale=18),features=BANDS)
        self.assert_cells(result,oracle(prices,F(1000000),18))
        self.assertTrue(all((q.expected,q.observed)==(4096,4096) for q in result.quality))
        with self.assertRaises(ContractError) as caught:
            compute_intraday(*facts(n=1),features=('intraday.band_middle',))
        self.assertEqual(caught.exception.code,ErrorCode.INVALID_CONFIG)

    def test_hostile_global_decimal_context_is_unchanged(self):
        f=facts((1,7),2,F(4,3));expected=oracle((1,7),F(4,3));old=getcontext().copy()
        try:
            current=getcontext();current.prec=1;current.rounding=ROUND_DOWN
            for signal in current.traps:current.traps[signal]=True
            current.clear_flags();before=current.copy()
            result=compute_intraday(*f,features=BANDS)
            after=getcontext().copy()
            self.assertEqual((after.prec,after.rounding,dict(after.traps),dict(after.flags)),
                             (before.prec,before.rounding,dict(before.traps),dict(before.flags)))
        finally:setcontext(old)
        self.assert_cells(result,expected)

    def test_band_preparation_original_identity_and_missing_family_rejections(self):
        b,c,cfg=facts();prepared=prepare_intraday(b,c,cfg,requirements=('price_moments',))
        for supplied in (None,tuple(replace(x) for x in b)):
            with self.assertRaises(ContractError) as caught:
                compute_intraday(supplied,c,cfg,features=BANDS,preparation=prepared)
            self.assertEqual(caught.exception.code,ErrorCode.INCONSISTENT_IDENTITY)
        other=prepare_intraday(b,c,cfg,requirements=('anchored_closes',))
        with self.assertRaises(ContractError) as caught:
            compute_intraday(b,c,cfg,features=BANDS,preparation=other)
        self.assertEqual(caught.exception.code,ErrorCode.UNSUPPORTED_CAPABILITY)

    def test_corrected_revision_replays_and_preserves_old_result(self):
        b,c,cfg=facts();original=compute_intraday(b,c,cfg,features=BANDS)
        frozen=original.values
        corrected=tuple(replace(batch,columns=tuple(Column(col.name,col.values[:-1]+(14,)) if col.name=='close' else col
                         for col in batch.columns),metadata=replace(batch.metadata,
                         source=replace(batch.metadata.source,snapshot_id='corrected'))) for batch in b)
        c=replace(c,revision='corrected')
        cfg=build_intraday_config(c,period=3,band_k=F(2),availability=cfg.availability,
                                 adjustment=cfg.adjustment,price_unit=cfg.price_unit,evidence_limit=10)
        new=compute_intraday(corrected,c,cfg,features=BANDS)
        self.assert_cells(new,oracle((11,14,14),F(2)))
        self.assertEqual(original.values,frozen)
        self.assertNotEqual(new.values,original.values)
        self.assertNotEqual(new.metadata,original.metadata)

    def test_real_session_reset_limits_band_window_without_invented_history(self):
        batches,_,base=facts()
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
        for n in (3,4):
            for ctx in (carry,replace(carry,mode='reset',anchor_index=2)):
                cfg=build_intraday_config(ctx,period=n,band_k=F(2),availability=AvailabilitySpec(60,60,60),
                                         adjustment=base.adjustment,price_unit=base.price_unit)
                result=compute_intraday((a,b),ctx,cfg,features=BANDS)
                if ctx.mode=='reset' and n==4:
                    self.assertTrue(all((q.status,q.expected,q.observed)==(Status.INSUFFICIENT_HISTORY,4,3)
                                        and q.reasons==(Reason.INSUFFICIENT_HISTORY,) for q in result.quality))
                    self.assertTrue(all(col.values==(None,) for col in result.values))
                else:
                    self.assert_cells(result,oracle((10,12,11,14,13)[-n:],F(2)))
                self.assertEqual(result.metadata.session_id,'S1')
