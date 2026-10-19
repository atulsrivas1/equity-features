"""Producer admission, exact independent moments, reset and correction fixtures."""
from dataclasses import replace
from fractions import Fraction as F
import unittest

from equity_feature_contracts import (
    AvailabilitySpec, CanonicalBatch, Column, ContractError, Coverage, ErrorCode,
    InputScope, IntervalCoverage, PriceUnit, SessionSpec,
)
from equity_features_intraday import IntradayContext, IntradayRun, build_intraday_config, prepare_intraday
from test_preparation import supplied


def make(batches,c,cfg,requirements=('price_moments',)):
    return prepare_intraday(batches,c,cfg,requirements=requirements)


def split(batch,cut):
    result=[]
    for j,(left,right) in enumerate(((0,cut),(cut,batch.row_count))):
        meta=replace(batch.metadata,source=replace(batch.metadata.source,input_id=f'chunk{j}'),
                     coverage=Coverage(right-left,right-left,True),
                     scope=replace(batch.metadata.scope,start_ns=left*10,end_ns=right*10),
                     interval_coverage=batch.metadata.interval_coverage[left:right])
        result.append(CanonicalBatch(batch.kind,tuple(Column(col.name,col.values[left:right]) for col in batch.columns),meta))
    return tuple(result)


class AdmissionTests(unittest.TestCase):
    def assert_code(self,code,operation):
        with self.assertRaises(ContractError) as caught: operation()
        self.assertEqual(caught.exception.code,code)

    def test_unit_identity_precedes_malformed_payload_semantics(self):
        batches,c,cfg=supplied()
        bad=replace(batches[0],metadata=replace(batches[0].metadata,price_unit=PriceUnit(0,'EUR')),
            columns=tuple(Column(col.name,(0,)+col.values[1:]) if col.name=='close' else col for col in batches[0].columns))
        self.assert_code(ErrorCode.INVALID_UNIT,lambda:make((bad,),c,cfg))

    def test_later_chunk_unit_or_snapshot_precedes_first_malformed_payload(self):
        batches,c,cfg=supplied()
        first,last=split(batches[0],2)
        first=replace(first,columns=tuple(Column(col.name,(0,)+col.values[1:]) if col.name=='close' else col for col in first.columns))
        variants=((replace(last.metadata,price_unit=PriceUnit(0,'EUR')),ErrorCode.INVALID_UNIT),
                  (replace(last.metadata,source=replace(last.metadata.source,snapshot_id='wrong')),ErrorCode.INCONSISTENT_IDENTITY))
        for metadata,code in variants:
            with self.subTest(code=code):
                self.assert_code(code,lambda:make((first,replace(last,metadata=metadata)),c,cfg))

    def test_all_payload_semantics_precede_cross_chunk_grid_admission(self):
        batches,c,cfg=supplied()
        first,last=split(batches[0],2)
        first=replace(first,columns=tuple(Column(col.name,(1,)+col.values[1:]) if col.name=='start_ns' else col for col in first.columns))
        last=replace(last,columns=tuple(Column(col.name,(0,)+col.values[1:]) if col.name=='close' else col for col in last.columns))
        self.assert_code(ErrorCode.INVALID_SCHEMA,lambda:make((first,last),c,cfg))

    def test_chunked_delivery_has_same_values_but_actual_distinct_provenance(self):
        batches,c,cfg=supplied()
        single=make(batches,c,cfg).operand('price_moments')
        chunks=split(batches[0],2)
        product=make(chunks,c,cfg)
        view=product.operand('price_moments')
        self.assertEqual((view.values,view.status,view.expected,view.observed),
                         (single.values,single.status,single.expected,single.observed))
        self.assertEqual(tuple(b.metadata.source.input_id for b in product.input_bindings),('chunk0','chunk1'))
        self.assertTrue(all(e.input_id=='chunk1' for e in view.evidence))

    def test_unrelated_old_chunk_missing_close_is_not_missing_current_window(self):
        batches,c,cfg=supplied()
        first,last=split(batches[0],2)
        first=replace(first,columns=tuple(col for col in first.columns if col.name!='close'))
        result=make((first,last),c,cfg,('price_moments','anchored_closes'))
        self.assertIsNotNone(result.operand('price_moments').values)
        self.assertEqual(result.operand('anchored_closes').status.value,'missing_input')

    def test_duplicate_input_identity_and_mixed_snapshot_rejected(self):
        batches,c,cfg=supplied()
        first,last=split(batches[0],2)
        for source,code in ((replace(last.metadata.source,input_id='chunk0'),ErrorCode.DUPLICATE),
                            (replace(last.metadata.source,snapshot_id='different'),ErrorCode.INCONSISTENT_IDENTITY)):
            changed=replace(last,metadata=replace(last.metadata,source=source))
            self.assert_code(code,lambda:make((first,changed),c,cfg))

    def test_overlapping_chunk_scopes_rejected_even_with_disjoint_rows(self):
        batches,c,cfg=supplied()
        first,last=split(batches[0],2)
        last=replace(last,metadata=replace(last.metadata,scope=replace(last.metadata.scope,start_ns=10)))
        self.assert_code(ErrorCode.INVALID_ORDER,lambda:make((first,last),c,cfg))

    def test_aggregate_counts_do_not_override_actual_rows(self):
        batches,c,cfg=supplied()
        bad=replace(batches[0],metadata=replace(batches[0].metadata,coverage=Coverage(5,4,False)))
        self.assert_code(ErrorCode.INCONSISTENT_IDENTITY,lambda:make((bad,),c,cfg))

    def test_wrong_slot_coverage_name_rejected(self):
        batches,c,cfg=supplied()
        intervals=list(batches[0].metadata.interval_coverage)
        intervals[0]=replace(intervals[0],name='slot:99')
        bad=replace(batches[0],metadata=replace(batches[0].metadata,interval_coverage=tuple(intervals)))
        self.assert_code(ErrorCode.INCONSISTENT_IDENTITY,lambda:make((bad,),c,cfg))

    def test_malformed_supplied_unrelated_field_is_global_error(self):
        batches,c,cfg=supplied()
        cols=tuple(Column(col.name,(-1,)+col.values[1:]) if col.name=='high' else col for col in batches[0].columns)
        bad=replace(batches[0],columns=cols)
        self.assert_code(ErrorCode.INVALID_SCHEMA,lambda:make((bad,),c,cfg))

    def test_cutoff_equality_allowed_but_earlier_cutoff_rejected(self):
        batches,c,cfg=supplied()
        self.assertIsNotNone(make(batches,c,cfg).operand('price_moments').values)
        self.assert_code(ErrorCode.BOUNDS,lambda:build_intraday_config(c,period=3,band_k=F(2),
            availability=AvailabilitySpec(49,60,60),adjustment=cfg.adjustment,price_unit=cfg.price_unit))

    def test_evidence_truncation_does_not_change_values_or_counts(self):
        batches,c,cfg=supplied()
        limited=build_intraday_config(c,period=3,band_k=F(2),availability=cfg.availability,
            adjustment=cfg.adjustment,price_unit=cfg.price_unit,evidence_limit=1)
        a,b=make(batches,c,cfg).operand('price_moments'),make(batches,c,limited).operand('price_moments')
        self.assertEqual((a.values,a.status,a.expected,a.observed),(b.values,b.status,b.expected,b.observed))
        self.assertEqual(len(b.evidence),1)
        self.assertEqual(b.evidence[0].slot_index,2)

    def test_pairwise_oracle_over_varied_windows_and_large_offsets(self):
        for n in range(1,9):
            for offset in (0,2**60):
                closes=tuple(offset+10+(i*i+7*i)%11 for i in range(n))
                highs=tuple(x+1 for x in closes);lows=tuple(x-1 for x in closes)
                batches,c,base=supplied(closes=closes,highs=highs,lows=lows)
                for period in range(1,n+1):
                    cfg=build_intraday_config(c,period=period,band_k=F(2),availability=base.availability,
                        adjustment=base.adjustment,price_unit=base.price_unit)
                    window=closes[-period:]
                    mean=sum(map(F,window))/period
                    # Pairwise squared differences: independent of centered sum implementation.
                    variance=sum((F(x)-y)**2 for x in window for y in window)/(2*period**2)
                    self.assertEqual(make(batches,c,cfg).operand('price_moments').values,
                                     (mean,variance,F(window[-1])-mean))

    def test_corrected_snapshot_rebuilds_without_mutating_old_facts(self):
        batches,c,cfg=supplied()
        before=make(batches,c,cfg)
        revised,c2,cfg2=supplied(closes=(10,12,11,14,14))
        revised=(replace(revised[0],metadata=replace(revised[0].metadata,
            source=replace(revised[0].metadata.source,snapshot_id='snap2'))),)
        c2=replace(c2,revision='revision2')
        cfg2=build_intraday_config(c2,period=3,band_k=F(2),availability=cfg.availability,
            adjustment=cfg.adjustment,price_unit=cfg.price_unit,evidence_limit=10)
        after=make(revised,c2,cfg2)
        self.assertEqual(before.operand('price_moments').values,(F(38,3),F(14,9),F(1,3)))
        self.assertEqual(after.operand('price_moments').values,(F(13),F(2),F(1)))
        self.assertNotEqual(before.context_digest,after.context_digest)

    def test_reset_and_carry_use_only_explicit_anchor_operands(self):
        batches,_,base=supplied()
        original=batches[0]
        sessions=(SessionSpec('synthetic','S0',0,20,'UTC'),SessionSpec('synthetic','S1',30,60,'UTC'))
        runs=(IntradayRun('S0',0,10,2),IntradayRun('S1',30,10,3))
        carry=IntradayContext('A','cal','grid','rev',sessions,runs,0,4,'carry')
        a,b=split(original,2)
        a=replace(a,columns=tuple(Column(col.name,('S0',)*2) if col.name=='session_id' else col for col in a.columns))
        shifted=[]
        for col in b.columns:
            values=('S1',)*3 if col.name=='session_id' else tuple(v+10 for v in col.values) if col.name in ('start_ns','end_ns','known_at_ns') else col.values
            shifted.append(Column(col.name,values))
        b=replace(b,columns=tuple(shifted),metadata=replace(b.metadata,scope=InputScope(30,60,'synthetic-v1'),
            interval_coverage=tuple(replace(i,start_ns=i.start_ns+10,end_ns=i.end_ns+10) for i in b.metadata.interval_coverage)))
        for ctx,expected in ((carry,(3,3,4,3)),(replace(carry,mode='reset',anchor_index=2),(4,3))):
            cfg=build_intraday_config(ctx,period=3,band_k=F(2),availability=AvailabilitySpec(60,60,60),
                adjustment=base.adjustment,price_unit=base.price_unit)
            product=make((a,b),ctx,cfg,('true_ranges',))
            self.assertEqual(product.operand('true_ranges').values,expected)


if __name__=='__main__':unittest.main()
