"""Original context identity, exact time and closed codec counterexamples."""
from dataclasses import replace
from fractions import Fraction
import json
import unittest

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ContractError, ErrorCode, Parameter,
    PriceUnit, SessionSpec,
)
from equity_features_intraday import IntradayContext, IntradayRun, build_intraday_config
from equity_features_intraday._context import validate_config


def context():
    return IntradayContext('A','calendar-v1','grid-v1','revision1',
                           (SessionSpec('synthetic','S',0,100,'UTC'),),
                           (IntradayRun('S',0,10,5),),0,4,'reset')


def config(ctx=None, **kwargs):
    return build_intraday_config(ctx or context(), period=3, band_k=Fraction(2),
                                 availability=AvailabilitySpec(50,60,60),
                                 adjustment=AdjustmentSpec(), price_unit=PriceUnit(4,'USD'),
                                 **kwargs)


class ContextTests(unittest.TestCase):
    def test_exact_grid_and_canonical_round_trip(self):
        c = context()
        self.assertEqual([(s.index,s.start_ns,s.end_ns) for s in c.slots()],
                         [(0,0,10),(1,10,20),(2,20,30),(3,30,40),(4,40,50)])
        self.assertEqual(IntradayContext.from_json(c.to_json()), c)
        self.assertEqual(len(c.digest),64)

    def test_distinct_endpoint_and_revision_identity(self):
        c = context()
        other = replace(c,runs=(IntradayRun('S',0,10,4),),target_index=3)
        self.assertNotEqual(config(c).digest, config(other).digest)
        self.assertNotEqual(c.digest, replace(c,revision='revision2').digest)

    def test_real_session_envelope_is_not_bar_count(self):
        c = context()
        cfg = config(c)
        self.assertEqual(cfg.window.governed_sessions,('S',))
        self.assertEqual(cfg.window.count,1)
        self.assertEqual(dict((p.name,p.value) for p in cfg.parameters)['period'],3)
        self.assertEqual((cfg.session.open_ns,cfg.session.close_ns),(0,100))
        self.assertLess(cfg.availability.market_cutoff_ns,cfg.session.close_ns)
        self.assertEqual(validate_config(c,cfg),(3,Fraction(2),0))

    def test_evidence_limit_bound_before_calculation(self):
        a,b = config(evidence_limit=0),config(evidence_limit=10)
        self.assertNotEqual(a.digest,b.digest)
        self.assertEqual(validate_config(context(),b)[2],10)

    def test_reset_and_carry_have_explicit_different_anchor(self):
        sessions=(SessionSpec('synthetic','S0',0,30,'UTC'),SessionSpec('synthetic','S1',40,70,'UTC'))
        runs=(IntradayRun('S0',0,10,3),IntradayRun('S1',40,10,3))
        carry=IntradayContext('A','cal','grid','rev',sessions,runs,0,5,'carry')
        reset=replace(carry,anchor_index=3,mode='reset')
        self.assertNotEqual(carry.digest,reset.digest)
        with self.assertRaises(ContractError):replace(carry,mode='reset')

    def test_no_silent_sort_overlap_or_session_alias(self):
        c=context()
        for runs in ((IntradayRun('S',10,10,2),IntradayRun('S',0,10,1)),
                     (IntradayRun('other',0,10,5),),
                     (IntradayRun('S',90,10,5),)):
            with self.subTest(runs=runs),self.assertRaises(ContractError):replace(c,runs=runs)

    def test_bool_period_index_count_rejected(self):
        with self.assertRaises(ContractError):IntradayRun('S',0,10,True)
        with self.assertRaises(ContractError):replace(context(),anchor_index=False)
        with self.assertRaises(ContractError):
            build_intraday_config(context(),period=True,band_k=Fraction(2),
                                  availability=AvailabilitySpec(50,60,60),
                                  adjustment=AdjustmentSpec(),price_unit=PriceUnit(0,'USD'))

    def test_noncanonical_and_unknown_json_rejected(self):
        text=context().to_json()
        wrong=[text+' ',text.replace('"mode":"reset"','"mode":"reset","unknown":1'),
               text.replace('"mode":"reset"','"mode":"reset","mode":"carry"'),
               text.replace('"anchor_index":0','"anchor_index":false')]
        for value in wrong:
            with self.subTest(value=value[-60:]),self.assertRaises(ContractError):
                IntradayContext.from_json(value)

    def test_unbounded_or_deep_parser_input_rejected(self):
        for value in (' '*65537,'['*1200+']'*1200):
            with self.assertRaises(ContractError):IntradayContext.from_json(value)

    def test_printable_identity_admission(self):
        for name in ('S\n1','S\x7f','é',' '):
            with self.subTest(name=name),self.assertRaises(ContractError):
                replace(context(),revision=name)

    def test_integer_ns_overflow_rejected(self):
        with self.assertRaises(ContractError):IntradayRun('S',2**63-2,2,1)

    def test_source_context_and_config_tamper_rejected(self):
        cfg=config()
        values={p.name:p.value for p in cfg.parameters}
        values['context_sha256']='0'*64
        tamper=replace(cfg,parameters=tuple(Parameter(k,v) for k,v in values.items()))
        with self.assertRaises(ContractError):validate_config(context(),tamper)
        with self.assertRaises(ContractError):validate_config(replace(context(),revision='new'),cfg)

    def test_context_chunking_and_canonical_splitting(self):
        sessions=tuple(SessionSpec('synthetic',f'S{i:02}',i*100,(i+1)*100,'UTC') for i in range(30))
        runs=tuple(IntradayRun(s.session_id,s.open_ns,10,10) for s in sessions)
        c=IntradayContext('A','cal','grid','rev',sessions,runs,0,299,'carry')
        cfg=build_intraday_config(c,period=20,band_k=Fraction(2),
                                  availability=AvailabilitySpec(3000,3000,3000),
                                  adjustment=AdjustmentSpec(),price_unit=PriceUnit(4,'USD'))
        chunks=[p.value for p in cfg.parameters if p.name.startswith('context_') and p.name[8:].isdigit()]
        self.assertGreater(len(chunks),1)
        self.assertTrue(all(len(s)==4096 for s in chunks[:-1]))
        self.assertEqual(validate_config(c,cfg)[0],20)

    def test_first_finalized_slot_and_cutoff_equality(self):
        c=replace(context(),runs=(IntradayRun('S',0,10,1),),target_index=0)
        cfg=build_intraday_config(c,period=1,band_k=Fraction(2),
                                  availability=AvailabilitySpec(10,10,10),
                                  adjustment=AdjustmentSpec(),price_unit=PriceUnit(0,'USD'))
        self.assertEqual(validate_config(c,cfg)[0],1)
        with self.assertRaises(ContractError) as caught:
            build_intraday_config(c,period=1,band_k=Fraction(2),
                                   availability=AvailabilitySpec(9,10,10),
                                   adjustment=AdjustmentSpec(),price_unit=PriceUnit(0,'USD'))
        self.assertEqual(caught.exception.code,ErrorCode.BOUNDS)


if __name__=='__main__':unittest.main()
