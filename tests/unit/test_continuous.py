"""Independent continuous integrals, expiry/initialization and conservation adversaries."""
from dataclasses import replace
from fractions import Fraction
import unittest
from equity_feature_contracts import (AvailabilitySpec, BatchMetadata, CanonicalBatch,
    Column, ContractError, Coverage, DataKind, ErrorCode, InputScope, Parameter,
    PriceUnit, QuoteDurations, Reason, SessionSpec, SourceBinding, Status,
    builtin_registry)
from equity_feature_contracts.columnar import to_arrow_result
from equity_features.session import compute_time_weighted
from test_bars import ENTITY, config
from test_quotes import quotes


def cfg(age=6,initial='unknown'):
    c=config();return replace(c,parameters=c.parameters+(Parameter('max_age_ns',age),Parameter('initial_state',initial)),session=SessionSpec('demo','S',100,112,'supplied'),availability=AvailabilitySpec(112,200,200))
def updates(**changes):
    b=quotes(event_ns=(100,103,107,109),known_at_ns=(100,103,107,109),**changes)
    return replace(b,metadata=replace(b.metadata,sampling='continuous',scope=InputScope(100,112,'synthetic-v1')))
def blank():
    b=updates();return replace(b,columns=tuple(Column(c.name,()) for c in b.columns),metadata=replace(b.metadata,coverage=Coverage(0,0,True)))
def one(event=103,bid=100,ask=102):
    b=updates();data={c.name:(c.values[0],) for c in b.columns};data.update(event_ns=(event,),bid=(bid,),ask=(ask,),known_at_ns=(event,))
    return replace(b,columns=tuple(Column(k,v) for k,v in data.items()),metadata=replace(b.metadata,coverage=Coverage(1,1,True)))
def seed(event=99,known=None,event_id='seed',bid=100,ask=102):
    return CanonicalBatch(DataKind.QUOTE,tuple(Column(k,(v,)) for k,v in dict(instrument_id='A',session_id='S',event_ns=event,order_key=0,event_id=event_id,known_at_ns=event if known is None else known,bid=bid,ask=ask).items()),BatchMetadata('demo',SourceBinding('synthetic','seed-s1','m1','seed-input'),Coverage(1,1,True),PriceUnit(0,'USD'),sampling='continuous',scope=InputScope(event,100,'synthetic-v1')))
def calc(b=None,c=None,s=None):return compute_time_weighted(b,cfg() if c is None else c,entity=ENTITY,seed=s)
def value(r):return r.values[0].values[0]

class Continuous(unittest.TestCase):
    def error(self,code,fn):
        with self.assertRaises(ContractError) as caught:fn()
        self.assertEqual(caught.exception.code,code)

    def test_independent_golden_integral(self):
        r=calc(updates());v=value(r);d=v.durations
        self.assertEqual(d,QuoteDurations(3,4,2,3,0,0));self.assertEqual((d.total,d.valid),(12,7))
        self.assertAlmostEqual(v.mean_spread,float(Fraction(6,7)),delta=1e-12)
        self.assertAlmostEqual(v.mean_bps,float(Fraction(60000,707)),delta=1e-12)
        self.assertAlmostEqual(d.valid_fraction,7/12);self.assertEqual(r.quality[0].status,Status.AVAILABLE)

    def test_unknown_initial_duration_nulls_means(self):
        r=calc(one());v=value(r);self.assertEqual(v.durations,QuoteDurations(6,0,0,0,3,3))
        self.assertIsNone(v.mean_spread);self.assertIsNone(v.mean_bps);self.assertEqual(r.quality[0].status,Status.INCOMPLETE_COVERAGE)

    def test_inactive_initial_is_known_invalid(self):
        v=value(calc(one(),cfg(initial='inactive')))
        self.assertEqual(v.durations,QuoteDurations(6,0,0,3,3,0));self.assertEqual(v.mean_spread,2.0)

    def test_preopen_seed_uses_original_expiry(self):
        r=calc(blank(),cfg(initial='seed'),seed());v=value(r)
        self.assertEqual(v.durations,QuoteDurations(5,0,0,0,7,0));self.assertEqual(v.mean_spread,2.0)
        self.assertEqual(r.evidence[0].event_ns,99);self.assertEqual(r.evidence[0].use,'consumed')
        self.assertEqual({x.role for x in r.metadata.inputs},{'quotes','quote_seed'})

    def test_seed_expired_exactly_at_open(self):
        r=calc(blank(),cfg(initial='seed'),seed(94));self.assertEqual(value(r).durations.expired,12)
        self.assertEqual(r.quality[0].status,Status.NOT_APPLICABLE);self.assertIsNone(value(r).mean_spread)
        self.assertEqual(value(calc(blank(),cfg(initial='seed'),seed(90))).durations.expired,12)

    def test_unavailable_seed_is_unknown_not_consumed(self):
        r=calc(blank(),cfg(initial='seed'),seed(known=999));self.assertEqual(value(r).durations.unknown,12)
        self.assertEqual(r.quality[0].status,Status.INCOMPLETE_COVERAGE)
        self.assertEqual(r.evidence[0].use,'excluded');self.assertEqual(r.evidence[0].exclusion_reason,Reason.FUTURE_KNOWLEDGE)
        r=calc(blank(),cfg(initial='seed'));self.assertEqual(value(r).durations.unknown,12)
        self.assertIn(Reason.ABSENT_INPUT,r.quality[0].reasons)

    def test_first_update_at_open_eliminates_unknown_seed_time(self):
        r=calc(updates(),cfg(initial='seed'),seed(known=999))
        self.assertEqual(r.quality[0].status,Status.AVAILABLE);self.assertEqual(value(r).durations.unknown,0)
        self.assertEqual(value(r).mean_spread,value(calc(updates())).mean_spread)

    def test_observed_empty_initial_modes(self):
        r=calc(blank());self.assertEqual(value(r).durations.unknown,12);self.assertEqual(r.quality[0].status,Status.INCOMPLETE_COVERAGE)
        r=calc(blank(),cfg(initial='inactive'));self.assertEqual(value(r).durations.invalid,12);self.assertEqual(r.quality[0].status,Status.NOT_APPLICABLE)
        r=calc();self.assertIsNone(value(r));self.assertEqual(r.quality[0].status,Status.MISSING_INPUT)

    def test_short_age_splits_each_state_and_conserves(self):
        v=value(calc(updates(),cfg(age=1)));self.assertEqual(v.durations,QuoteDurations(1,1,1,1,8,0))
        self.assertEqual(v.mean_spread,1.0);self.assertAlmostEqual(v.mean_bps,10000/101)

    def test_equal_time_last_state_governs_positive_duration(self):
        b=updates();b=replace(b,columns=tuple(Column(c.name,(100,100,107,109) if c.name=='event_ns' else c.values) for c in b.columns))
        v=value(calc(b));self.assertEqual(v.durations,QuoteDurations(0,6,2,3,1,0));self.assertEqual(v.mean_spread,0.0)

    def test_invalid_crossed_replace_valid_without_carry(self):
        self.assertEqual(value(calc(updates())).durations.normal,3)
        v=value(calc(one(100,bid=None,ask=102),cfg(age=100)))
        self.assertEqual(v.durations.invalid,12);self.assertIsNone(v.mean_spread)
        v=value(calc(one(100,bid=105,ask=104),cfg(age=100)));self.assertEqual(v.durations.crossed,12)

    def test_locked_entire_window_has_available_zero(self):
        r=calc(one(100,102,102),cfg(age=100));self.assertEqual(value(r).durations.locked,12)
        self.assertEqual((value(r).mean_spread,value(r).mean_bps),(0.0,0.0));self.assertEqual(r.quality[0].status,Status.AVAILABLE)

    def test_incomplete_feed_never_certifies_carried_durations(self):
        b=updates();b=replace(b,metadata=replace(b.metadata,coverage=Coverage(5,4,False)))
        r=calc(b);self.assertIsNone(value(r));self.assertEqual(r.quality[0].status,Status.INCOMPLETE_COVERAGE);self.assertEqual(r.evidence,())

    def test_sampling_payload_and_future_target(self):
        b=updates();self.error(ErrorCode.UNSUPPORTED_SAMPLING,lambda:calc(replace(b,metadata=replace(b.metadata,sampling='trade_snapshot'))))
        b=replace(b,columns=tuple(c for c in b.columns if c.name!='bid'));self.assertIsNone(value(calc(b)))
        b=updates();b=replace(b,columns=tuple(Column(c.name,(100,103,107,999) if c.name=='known_at_ns' else c.values) for c in b.columns))
        self.assertEqual(calc(b).quality[0].status,Status.MISSING_INPUT);self.assertIsNone(value(calc(b)))
        self.error(ErrorCode.INVALID_SCHEMA,lambda:calc('not a batch'))

    def test_seed_duplicate_and_incompatible_evidence(self):
        self.error(ErrorCode.DUPLICATE,lambda:calc(updates(),cfg(initial='seed'),seed(event_id='q1')))
        s=seed();self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:calc(blank(),cfg(initial='seed'),replace(s,metadata=replace(s.metadata,source=SourceBinding('other','s1','m1','seed-input')))))
        self.error(ErrorCode.INVALID_UNIT,lambda:calc(blank(),cfg(initial='seed'),replace(s,metadata=replace(s.metadata,price_unit=PriceUnit(2,'USD')))))
        self.error(ErrorCode.INVALID_CONFIG,lambda:calc(blank(),cfg(initial='inactive'),s))
        s=replace(s,columns=tuple(Column(c.name,(100,) if c.name=='event_ns' else c.values) for c in s.columns))
        self.error(ErrorCode.BOUNDS,lambda:calc(blank(),cfg(initial='seed'),s))

    def test_max_age_requires_exact_positive_int64(self):
        for age in (0,-1,True,1.0,2**63):self.error(ErrorCode.INVALID_CONFIG,lambda:calc(updates(),cfg(age=age)))
        self.error(ErrorCode.INVALID_CONFIG,lambda:calc(updates(),cfg(initial='guess')))

    def test_early_close_cutoff_and_exact_expiry_boundary(self):
        c=cfg();c=replace(c,session=replace(c.session,scheduled_close_ns=120,early_close=True));self.assertEqual(value(calc(updates(),c)).durations.total,12)
        c=replace(cfg(age=3),availability=AvailabilitySpec(103,200,200));b=one(100);b=replace(b,metadata=replace(b.metadata,scope=InputScope(100,103,'synthetic-v1')))
        v=value(calc(b,c));self.assertEqual(v.durations.normal,3);self.assertEqual(v.durations.expired,0)
        b=updates();b=replace(b,columns=tuple(Column(c.name,(100,103,107,112) if c.name=='event_ns' else c.values) for c in b.columns))
        self.error(ErrorCode.BOUNDS,lambda:calc(b))

    def test_near_int64_expiry_is_wide_and_clipped(self):
        high=2**63-1;start=high-12;c=cfg(age=high,initial='seed')
        c=replace(c,session=SessionSpec('demo','S',start,high,'supplied'),availability=AvailabilitySpec(high,high,high))
        b=blank();b=replace(b,metadata=replace(b.metadata,scope=InputScope(start,high,'synthetic-v1')))
        s=seed();s=replace(s,columns=tuple(Column(x.name,(start-1,) if x.name in ('event_ns','known_at_ns') else x.values) for x in s.columns),metadata=replace(s.metadata,scope=InputScope(start-1,start,'synthetic-v1')))
        v=value(calc(b,c,s));self.assertEqual(v.durations.normal,12);self.assertEqual(v.mean_spread,2.0)

    def test_wide_weighted_products_and_duration_overflow(self):
        high=2**63-1;c=replace(cfg(age=high),session=SessionSpec('demo','S',0,high,'supplied'),availability=AvailabilitySpec(high,high,high))
        b=one(100);b=replace(b,columns=tuple(Column(x.name,(0,) if x.name in ('event_ns','known_at_ns') else (1,) if x.name=='bid' else (high,) if x.name=='ask' else x.values) for x in b.columns),metadata=replace(b.metadata,scope=InputScope(0,high,'synthetic-v1')))
        v=value(calc(b,c));self.assertEqual(v.durations.valid,high);self.assertEqual(v.mean_spread,float(high-1))
        c=replace(c,session=SessionSpec('demo','S',-(2**63),high,'supplied'))
        self.error(ErrorCode.OVERFLOW,lambda:calc(b,c))

    def test_typed_conservation_status_and_arrow(self):
        r=calc(updates());v=value(r);self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,values=(replace(r.values[0],values=(replace(v,durations=replace(v.durations,invalid=4)),)),)))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,quality=(replace(r.quality[0],status=Status.NOT_APPLICABLE,reasons=(Reason.ZERO_DENOMINATOR,)),)))
        cell=to_arrow_result(r)['values']['session.quote.time_weighted_spread'].column('value').combine_chunks()
        self.assertEqual(cell.field('durations').field('valid').to_pylist(),[7]);self.assertEqual(cell.field('durations').field('total').to_pylist(),[12])
        self.assertAlmostEqual(cell.field('mean_spread').to_pylist()[0],6/7)
        builtin_registry().require_capability('session.quote.time_weighted_spread','batch')
        for mode in ('update','restore','merge'):self.error(ErrorCode.UNSUPPORTED_CAPABILITY,lambda:builtin_registry().require_capability('session.quote.time_weighted_spread',mode))
    def test_weighted_mean_of_ratios_matches_exact_integral(self):
        bids=(1,100,1000,10000);asks=(3,110,1100,10010);dt=(3,4,2,3)
        v=value(calc(updates(bid=bids,ask=asks),cfg(age=100)))
        expected=sum(Fraction(20000*(a-b)*t,a+b) for a,b,t in zip(asks,bids,dt))/12
        self.assertEqual(v.mean_spread,23.0);self.assertAlmostEqual(v.mean_bps,float(expected),delta=1e-12)
        self.assertEqual(v.durations.normal,12)

    def test_fixed_reducer_retention_across_more_updates(self):
        from equity_features.session.continuous import _TimeReducer
        for n in (1,100,1000):
            state=_TimeReducer(0,10,0)
            for i in range(n):state.update(i,100,102)
            state.advance(n)
            self.assertEqual(len(state.duration),6);self.assertEqual(state.anchor,n-1)
            self.assertEqual(state.summary('unknown').durations.total,n)
            self.assertEqual(state.summary('unknown').mean_spread,2.0)

    def test_initialization_cannot_contradict_duration_or_seed_binding(self):
        unknown=value(calc(blank()))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(unknown,initial_state='inactive'))
        r=calc(blank(),cfg(initial='seed'),seed());v=value(r)
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,values=(replace(r.values[0],values=(replace(v,initial_state='unknown'),)),)))
