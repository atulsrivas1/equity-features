"""Independent direct-window values, field isolation and ownership cases."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction as F
import pickle
import unittest

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column,
    ContractError, Coverage, DataKind, ErrorCode, InputScope, IntervalCoverage,
    PriceUnit, Reason, SourceBinding, Status,
)
from equity_features_intraday import IntradayPreparation, build_intraday_config, prepare_intraday
from equity_features_intraday._prepare import REQUIREMENTS, validate_preparation
from test_context import context


def supplied(*, closes=(10,12,11,14,13), highs=(11,13,13,15,15), lows=(9,10,10,11,12),
             missing=(), absent=(), unknown=(), future=(), scale=0, omit_coverage=()):
    n=len(closes)
    c=replace(context(),sessions=(replace(context().sessions[0],close_ns=max(100,n*10)),),
              runs=(replace(context().runs[0],count=n),),target_index=n-1)
    cfg=build_intraday_config(c,period=3,band_k=F(2),availability=AvailabilitySpec(n*10,max(60,n*10),max(60,n*10)),
                              adjustment=AdjustmentSpec(),price_unit=PriceUnit(scale,'USD'),evidence_limit=10)
    selected=[i for i in range(n) if i not in missing]
    cols=[Column('instrument_id',tuple('A' for i in selected)),Column('session_id',tuple('S' for i in selected)),
          Column('start_ns',tuple(i*10 for i in selected)),Column('end_ns',tuple((i+1)*10 for i in selected))]
    for name,values in [('close',closes),('high',highs),('low',lows)]:
        if name not in absent:
            cols.append(Column(name,tuple(values[i] for i in selected)))
    cols.append(Column('known_at_ns',tuple(None if i in unknown else max(60,n*10)+1 if i in future else (i+1)*10 for i in selected)))
    intervals=tuple(IntervalCoverage(f'slot:{i}',i*10,(i+1)*10,Coverage(1,int(i not in missing),i not in missing))
                    for i in range(n) if i not in omit_coverage)
    meta=BatchMetadata('synthetic',SourceBinding('synthetic','snap1','map1','input1'),
                       Coverage(n,len(selected),not missing),PriceUnit(scale,'USD'),
                       scope=InputScope(0,n*10,'synthetic-v1'),interval_coverage=intervals)
    return (CanonicalBatch(DataKind.BAR,tuple(cols),meta),),c,cfg


def prepared(requirements=tuple(sorted(REQUIREMENTS)),**kwargs):
    batches,c,cfg=supplied(**kwargs)
    return prepare_intraday(batches,c,cfg,requirements=requirements)


class PreparationTests(unittest.TestCase):
    def test_original_exact_all_family_values(self):
        p=prepared()
        expected={'anchored_closes':(10,12,11,14,13),'true_ranges':(3,3,4,3),
                  'price_moments':(F(38,3),F(14,9),F(1,3)),
                  'high_extrema':(15,),'low_extrema':(10,),'simple_returns':(F(-1,14),)}
        for name,values in expected.items():
            with self.subTest(family=name):
                view=p.operand(name)
                self.assertEqual(view.values,values)
                self.assertEqual(view.status,Status.AVAILABLE)
                self.assertEqual(view.expected,view.observed)
                self.assertFalse(view.reasons)

    def test_close_only_missing_high_low_remains_independent(self):
        p=prepared(absent=('high','low'))
        for name in ('anchored_closes','price_moments','simple_returns'):
            self.assertEqual(p.operand(name).status,Status.AVAILABLE)
        for name in ('true_ranges','high_extrema','low_extrema'):
            self.assertEqual(p.operand(name).status,Status.MISSING_INPUT)
            self.assertIn(Reason.ABSENT_INPUT,p.operand(name).reasons)

    def test_atr_facts_do_not_read_target_close(self):
        p=prepared(closes=(10,12,11,14,None))
        self.assertEqual(p.operand('true_ranges').values,(3,3,4,3))
        self.assertEqual(p.operand('true_ranges').status,Status.AVAILABLE)
        self.assertEqual(p.operand('anchored_closes').status,Status.INCOMPLETE_COVERAGE)

    def test_out_of_window_gap_does_not_block_finite_families(self):
        p=prepared(missing=(0,),omit_coverage=(0,))
        for name in ('price_moments','high_extrema','low_extrema','simple_returns'):
            self.assertEqual(p.operand(name).status,Status.AVAILABLE)
        for name in ('anchored_closes','true_ranges'):
            self.assertEqual(p.operand(name).status,Status.INCOMPLETE_COVERAGE)

    def test_unknown_old_knowledge_is_not_global_barrier(self):
        p=prepared(unknown=(0,))
        self.assertEqual(p.operand('price_moments').status,Status.AVAILABLE)
        view=p.operand('anchored_closes')
        self.assertIn(Reason.UNKNOWN_AVAILABILITY,view.reasons)
        self.assertEqual(view.evidence[0].use,'excluded')

    def test_future_known_target_blocks_its_actual_families(self):
        p=prepared(future=(4,))
        for name in p.requirements:
            self.assertEqual(p.operand(name).status,Status.INCOMPLETE_COVERAGE)
            self.assertIn(Reason.FUTURE_KNOWLEDGE,p.operand(name).reasons)

    def test_exact_scale_units_and_dimensionless_return(self):
        p=prepared(scale=4)
        self.assertEqual(p.operand('price_moments').values,(F(19,15000),F(7,450000000),F(1,30000)))
        self.assertEqual(p.operand('simple_returns').values,(F(-1,14),))
        self.assertEqual(p.operand('price_moments').units,('currency/share','(currency/share)^2','currency/share'))

    def test_facts_do_not_apply_either_indicator_warmup(self):
        p=prepared(closes=(10,),highs=(None,),lows=(None,),absent=('high','low'))
        self.assertEqual(p.operand('anchored_closes').values,(10,))
        tr=p.operand('true_ranges')
        self.assertEqual(tr.values,())
        self.assertEqual((tr.status,tr.expected,tr.observed),(Status.AVAILABLE,1,1))
        self.assertEqual(p.operand('price_moments').status,Status.INSUFFICIENT_HISTORY)
        self.assertEqual(p.operand('simple_returns').expected,2)

    def test_same_complete_family_projection_for_shared_and_separate(self):
        batches,c,cfg=supplied()
        shared=prepare_intraday(batches,c,cfg,requirements=tuple(sorted(REQUIREMENTS)))
        for name in shared.requirements:
            single=prepare_intraday(batches,c,cfg,requirements=(name,))
            self.assertEqual((single.context_digest,single.config_digest,single.input_bindings,single.operand(name)),
                             (shared.context_digest,shared.config_digest,shared.input_bindings,shared.operand(name)))

    def test_partial_preparation_rejects_missing_family(self):
        p=prepared(('price_moments',))
        with self.assertRaises(ContractError) as caught:p.operand('true_ranges')
        self.assertEqual(caught.exception.code,ErrorCode.UNSUPPORTED_CAPABILITY)

    def test_no_public_constructor_restore_pickle_or_mutable_alias(self):
        p=prepared()
        with self.assertRaises(ContractError):IntradayPreparation()
        with self.assertRaises(ContractError):pickle.dumps(p)
        with self.assertRaises(FrozenInstanceError):p.context_digest='tampered'
        with self.assertRaises(FrozenInstanceError):p.operand('price_moments').expected=0

    def test_exact_original_objects_required_for_reuse(self):
        batches,c,cfg=supplied()
        p=prepare_intraday(batches,c,cfg,requirements=('price_moments',))
        validate_preparation(p,tuple(list(batches)),c,cfg,('price_moments',))
        copied=(replace(batches[0]),)
        with self.assertRaises(ContractError):validate_preparation(p,copied,c,cfg,('price_moments',))
        with self.assertRaises(ContractError):validate_preparation(p,None,c,cfg,('price_moments',))
        with self.assertRaises(ContractError):validate_preparation(p,batches,replace(c,revision='rev2'),cfg,('price_moments',))

    def test_large_offset_exact_moments(self):
        m=2**63-2
        p=prepared(('price_moments',),closes=(m-1,m,m+1),highs=(m,m+1,m+1),lows=(m-2,m-1,m))
        self.assertEqual(p.operand('price_moments').values,(F(m),F(2,3),F(1)))

    def test_complete_coverage_cannot_hide_a_missing_entry(self):
        batches,c,cfg=supplied(omit_coverage=(0,))
        with self.assertRaises(ContractError):
            prepare_intraday(batches,c,cfg,requirements=('anchored_closes',))

    def test_actual_empty_delivery_is_not_zero_prices(self):
        _,c,cfg=supplied()
        p=prepare_intraday((),c,cfg,requirements=('price_moments',))
        view=p.operand('price_moments')
        self.assertEqual(view.status,Status.INCOMPLETE_COVERAGE)
        self.assertIsNone(view.values)
        self.assertIn(Reason.OBSERVED_EMPTY,view.reasons)


if __name__=='__main__':unittest.main()
