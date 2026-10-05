"""Independent lifecycle fixtures, actual batch parity and bounded atomic state admission."""
from dataclasses import asdict, replace
from math import isclose
import unittest
from equity_feature_contracts import (
    Column, ContractError, Coverage, DataKind, ErrorCode, PrefixCoverage,
    StreamPopulation, Status,
)
from equity_features.incremental import SessionAccumulator
from equity_features.session import (compute_bars,compute_structure,compute_trades,
    compute_top_k,compute_quotes,compute_time_weighted)
from test_bars import ENTITY, batch, config, prior
from test_structure import fixture, cfg as structure_config
from test_trades import trades
from test_top_k import cfg as top_config
from test_quotes import quotes, cfg as quote_config
from test_continuous import updates, cfg as continuous_config, seed


def chunk(b, indices):
    return replace(b,columns=tuple(Column(c.name,tuple(c.values[i] for i in indices)) for c in b.columns),metadata=replace(b.metadata,coverage=Coverage(len(indices),len(indices),True),interval_coverage=()))
def certificate(b,c=None):return PrefixCoverage(b.metadata.scope.end_ns if c is None else c,b.metadata.coverage,b.metadata.interval_coverage)
def accumulator(family,b,c,**extra):return SessionAccumulator(family,c,entity=ENTITY,population=StreamPopulation.from_batch(b),**extra)

def semantic_equal(test,a,b):
    if isinstance(a,float):test.assertTrue(isclose(a,b,rel_tol=1e-12,abs_tol=1e-12),(a,b))
    elif isinstance(a,dict):
        test.assertEqual(set(a),set(b))
        for key in a:semantic_equal(test,a[key],b[key])
    elif isinstance(a,(list,tuple)):
        test.assertEqual(len(a),len(b))
        for x,y in zip(a,b):semantic_equal(test,x,y)
    else:test.assertEqual(a,b)

class Incremental(unittest.TestCase):
    def error(self,code,fn):
        with self.assertRaises(ContractError) as caught:fn()
        self.assertEqual(caught.exception.code,code)

    def same(self,a,b):semantic_equal(self,asdict(a),asdict(b))

    def test_all_six_families_chunked_final_equal_batch(self):
        cases=(('bars',batch(),config(),compute_bars,{'prior_close':prior()}),
            ('structure',fixture(),structure_config(),compute_structure,{}),
            ('trades',trades(),config(),compute_trades,{}),
            ('top_k',trades(),top_config(),compute_top_k,{}),
            ('quotes',quotes(),quote_config(),compute_quotes,{}),
            ('continuous',updates(),continuous_config(),compute_time_weighted,{}))
        for family,b,c,fn,extra in cases:
            with self.subTest(family=family):
                a=accumulator(family,b,c,**extra)
                for i in range(b.row_count):a.update(chunk(b,[i]),start_ordinal=i)
                self.same(a.finalize(certificate(b)),fn(b,c,entity=ENTITY,**extra))

    def test_trade_prefix_causality_and_independent_golden(self):
        b=trades();c=config();a=accumulator('trades',b,c)
        a.update(chunk(b,[0]),start_ordinal=0)
        r=a.snapshot(PrefixCoverage(120,Coverage(1,1,True)))
        v={x.feature_id.rsplit('.',1)[1]:x.values[0] for x in r.values}
        self.assertEqual((v['count'],v['volume'],v['notional'],v['vwap']),(1,2,200,100.))
        scoped=chunk(b,[0]);scoped=replace(scoped,metadata=replace(scoped.metadata,scope=replace(scoped.metadata.scope,end_ns=120)))
        self.same(r,compute_trades(scoped,replace(c,availability=replace(c.availability,market_cutoff_ns=120)),entity=ENTITY))
        a.update(chunk(b,[1,2]),start_ordinal=1);self.same(a.finalize(certificate(b)),compute_trades(b,c,entity=ENTITY))

    def test_continuous_snapshots_do_not_restart_anchor(self):
        b=updates();c=continuous_config();a=accumulator('continuous',b,c)
        a.update(chunk(b,[0]),start_ordinal=0);a.snapshot(PrefixCoverage(101,Coverage(1,1,True)))
        a.update(chunk(b,[1]),start_ordinal=1);r=a.snapshot(PrefixCoverage(105,Coverage(2,2,True)))
        self.assertEqual(r.values[0].values[0].durations.normal,3)
        self.assertEqual(r.values[0].values[0].durations.locked,2)
        a.update(chunk(b,[2,3]),start_ordinal=2);self.same(a.finalize(certificate(b)),compute_time_weighted(b,c,entity=ENTITY))

    def test_structure_prefix_window_and_full_denominator(self):
        b=fixture();c=structure_config();a=accumulator('structure',b,c)
        a.update(chunk(b,[0]),start_ordinal=0)
        r=a.snapshot(PrefixCoverage(150,Coverage(1,1,True),(b.metadata.interval_coverage[0],)))
        self.assertEqual(r.values[0].values[0].rows[0].volume,200)
        self.assertEqual(r.values[1].values[0].rows[0].share,1.0)
        self.assertEqual(r.values[0].values[0].rows[1].quality.status,Status.INCOMPLETE_COVERAGE)
        a.update(chunk(b,[1]),start_ordinal=1);self.same(a.finalize(certificate(b)),compute_structure(b,c,entity=ENTITY))

    def test_seed_continuation_matches_original_preopen_age(self):
        b=updates();c=continuous_config(initial='seed');s=seed();a=accumulator('continuous',b,c,seed=s)
        for i in range(4):a.update(chunk(b,[i]),start_ordinal=i)
        self.same(a.finalize(certificate(b)),compute_time_weighted(b,c,entity=ENTITY,seed=s))

    def test_wrong_ordinal_and_reused_span_do_not_mutate(self):
        b=trades();a=accumulator('trades',b,config());before=asdict(a._state)
        for ordinal in (1,-1,True):self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:a.update(chunk(b,[0]),start_ordinal=ordinal))
        self.assertEqual(asdict(a._state),before)
        a.update(chunk(b,[0]),start_ordinal=0);before=asdict(a._state)
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:a.update(chunk(b,[0]),start_ordinal=0));self.assertEqual(asdict(a._state),before)

    def test_wrong_source_and_schema_do_not_mutate(self):
        b=trades();a=accumulator('trades',b,config());piece=chunk(b,[0]);before=asdict(a._state)
        wrong=replace(piece,metadata=replace(piece.metadata,source=replace(piece.metadata.source,snapshot_id='other')))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:a.update(wrong,start_ordinal=0))
        wrong=replace(piece,columns=tuple(x for x in piece.columns if x.name!='price'))
        self.error(ErrorCode.INVALID_SCHEMA,lambda:a.update(wrong,start_ordinal=0));self.assertEqual(asdict(a._state),before)

    def test_cross_chunk_order_and_bar_overlap(self):
        b=trades();a=accumulator('trades',b,config());a.update(chunk(b,[1]),start_ordinal=0)
        before=asdict(a._state);self.error(ErrorCode.INVALID_ORDER,lambda:a.update(chunk(b,[0]),start_ordinal=1));self.assertEqual(asdict(a._state),before)
        b=batch();a=accumulator('bars',b,config());a.update(chunk(b,[0]),start_ordinal=0)
        self.error(ErrorCode.DUPLICATE,lambda:a.update(chunk(b,[0]),start_ordinal=1))

    def test_equal_time_across_chunks_requires_increasing_tie_key(self):
        b=trades(event_ns=(110,)*3);a=accumulator('trades',b,config())
        for i in range(3):a.update(chunk(b,[i]),start_ordinal=i)
        self.assertEqual(a.finalize(certificate(b)).values[0].values[0],3)
        a=accumulator('trades',b,config());a.update(chunk(b,[1]),start_ordinal=0)
        self.error(ErrorCode.INVALID_ORDER,lambda:a.update(chunk(b,[0]),start_ordinal=1))

    def test_known_retained_id_and_seed_overlap_reject(self):
        b=trades();a=accumulator('top_k',b,top_config());a.update(chunk(b,[0]),start_ordinal=0)
        piece=chunk(b,[1]);piece=replace(piece,columns=tuple(Column(x.name,('t1',) if x.name=='event_id' else x.values) for x in piece.columns))
        self.error(ErrorCode.DUPLICATE,lambda:a.update(piece,start_ordinal=1))
        b=updates();a=accumulator('continuous',b,continuous_config(initial='seed'),seed=seed(event_id='later'))
        piece=chunk(b,[0]);piece=replace(piece,columns=tuple(Column(x.name,('later',) if x.name=='event_id' else x.values) for x in piece.columns))
        self.error(ErrorCode.DUPLICATE,lambda:a.update(piece,start_ordinal=0))

    def test_earlier_snapshot_after_consumption_or_advance_rejects(self):
        b=trades();a=accumulator('trades',b,config());a.update(chunk(b,[0,1]),start_ordinal=0)
        self.error(ErrorCode.BOUNDS,lambda:a.snapshot(PrefixCoverage(130,Coverage(2,2,True))))
        a.snapshot(PrefixCoverage(140,Coverage(2,2,True)));before=asdict(a._state)
        self.error(ErrorCode.BOUNDS,lambda:a.snapshot(PrefixCoverage(135,Coverage(2,2,True))));self.assertEqual(asdict(a._state),before)

    def test_late_event_after_snapshot_requires_replay(self):
        b=trades();a=accumulator('trades',b,config());a.update(chunk(b,[0]),start_ordinal=0)
        a.snapshot(PrefixCoverage(140,Coverage(None,1,False)));before=asdict(a._state)
        self.error(ErrorCode.BOUNDS,lambda:a.update(chunk(b,[1]),start_ordinal=1));self.assertEqual(asdict(a._state),before)

    def test_invalid_certificate_count_cutoff_and_final_expectation(self):
        b=trades();a=accumulator('trades',b,config());a.update(chunk(b,[0]),start_ordinal=0);before=asdict(a._state)
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:a.snapshot(PrefixCoverage(120,Coverage(2,2,True))))
        self.error(ErrorCode.BOUNDS,lambda:a.snapshot(PrefixCoverage(201,Coverage(1,1,True))))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:a.snapshot(PrefixCoverage(200,Coverage(1,1,True))))
        self.assertEqual(asdict(a._state),before)

    def test_known_past_gap_never_becomes_complete_without_replay(self):
        b=trades();a=accumulator('trades',b,config());a.update(chunk(b,[0]),start_ordinal=0)
        r=a.snapshot(PrefixCoverage(120,Coverage(2,1,False)));self.assertTrue(all(q.status==Status.INCOMPLETE_COVERAGE for q in r.quality))
        a.update(chunk(b,[1,2]),start_ordinal=1)
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:a.snapshot(certificate(b)))

    def test_incomplete_chunk_is_recorded_not_promoted(self):
        b=trades();a=accumulator('trades',b,config());piece=chunk(b,[0]);piece=replace(piece,metadata=replace(piece.metadata,coverage=Coverage(2,1,False)))
        a.update(piece,start_ordinal=0)
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:a.snapshot(PrefixCoverage(120,Coverage(1,1,True))))
        r=a.snapshot(PrefixCoverage(120,Coverage(None,1,False)));self.assertEqual(r.quality[0].status,Status.INCOMPLETE_COVERAGE)

    def test_unproved_prefix_can_be_certified_when_facts_unchanged(self):
        b=trades();a=accumulator('trades',b,config());a.update(chunk(b,[0]),start_ordinal=0)
        a.snapshot(PrefixCoverage(120,Coverage(None,1,False)))
        self.assertEqual(a.snapshot(PrefixCoverage(120,Coverage(1,1,True))).values[0].values[0],1)

    def test_finalize_single_use_and_sealed_certificate(self):
        b=trades();a=accumulator('trades',b,config());a.update(b,start_ordinal=0);cert=certificate(b)
        r=a.finalize(cert);self.same(r,a.snapshot(cert))
        self.error(ErrorCode.BOUNDS,lambda:a.finalize(cert));self.error(ErrorCode.BOUNDS,lambda:a.update(chunk(b,[]),start_ordinal=3))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:a.snapshot(PrefixCoverage(200,Coverage(None,3,False))))

    def test_empty_declared_populations_match_batch(self):
        b=chunk(trades(),[]);a=accumulator('trades',b,config());self.same(a.finalize(certificate(b)),compute_trades(b,config(),entity=ENTITY))
        b=chunk(quotes(),[]);a=accumulator('quotes',b,quote_config());self.same(a.finalize(certificate(b)),compute_quotes(b,quote_config(),entity=ENTITY))
        b=chunk(updates(),[]);a=accumulator('continuous',b,continuous_config());self.same(a.finalize(certificate(b)),compute_time_weighted(b,continuous_config(),entity=ENTITY))

    def test_missing_payload_and_nulls_match_batch(self):
        for b,family,c,fn in ((trades(price=None),'trades',config(),compute_trades),(batch(close=None),'bars',config(),compute_bars),(quotes(bid=None),'quotes',quote_config(),compute_quotes)):
            a=accumulator(family,b,c)
            for i in range(b.row_count):a.update(chunk(b,[i]),start_ordinal=i)
            self.same(a.finalize(certificate(b)),fn(b,c,entity=ENTITY))

    def test_future_knowledge_never_leaks(self):
        b=trades(known_at_ns=(110,130,999));a=accumulator('trades',b,config())
        for i in range(3):a.update(chunk(b,[i]),start_ordinal=i)
        r=a.finalize(certificate(b));self.assertTrue(all(x.values[0] is None for x in r.values));self.same(r,compute_trades(b,config(),entity=ENTITY))

    def test_overflow_marker_preserves_unproved_unavailable_output(self):
        b=trades(size=(2**63-1,1,1));a=accumulator('trades',b,config());a.update(b,start_ordinal=0)
        self.error(ErrorCode.OVERFLOW,lambda:a.snapshot(certificate(b)))
        before=asdict(a._state);r=a.snapshot(PrefixCoverage(200,Coverage(3,3,False)))
        self.assertTrue(all(x.values[0] is None for x in r.values));self.assertTrue(a._state.trades.volume.overflow)
        self.assertEqual(before['bound'],100)

    def test_structure_straddle_rejects_atomically(self):
        b=batch(start_ns=(100,140),end_ns=(140,200));a=accumulator('structure',b,structure_config());before=asdict(a._state)
        self.error(ErrorCode.BOUNDS,lambda:a.update(b,start_ordinal=0));self.assertEqual(asdict(a._state),before)

    def test_structure_certificate_mismatch_and_independent_window_coverage(self):
        b=fixture();a=accumulator('structure',b,structure_config());a.update(chunk(b,[0,1]),start_ordinal=0)
        wrong=replace(b.metadata.interval_coverage[0],coverage=Coverage(2,2,True))
        before=asdict(a._state);self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:a.snapshot(PrefixCoverage(200,Coverage(2,2,True),(wrong,))))
        self.assertEqual(asdict(a._state),before)
        r=a.snapshot(PrefixCoverage(200,Coverage(2,2,False),b.metadata.interval_coverage))
        self.assertEqual(r.values[0].values[0].rows[0].volume,200);self.assertIsNone(r.values[1].values[0].rows[0].share)

    def test_interval_chunk_certificate_must_be_actual(self):
        b=fixture();a=accumulator('structure',b,structure_config());piece=chunk(b,[0]);piece=replace(piece,metadata=replace(piece.metadata,interval_coverage=(b.metadata.interval_coverage[1],)))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:a.update(piece,start_ordinal=0))

    def test_returned_snapshot_ownership_survives_updates(self):
        b=trades();a=accumulator('top_k',b,top_config());a.update(chunk(b,[0]),start_ordinal=0)
        old=a.snapshot(PrefixCoverage(120,Coverage(1,1,True)));saved=asdict(old)
        a.update(chunk(b,[1,2]),start_ordinal=1);a.finalize(certificate(b));self.assertEqual(asdict(old),saved)

    def test_operational_source_contract_types_and_declared_count(self):
        b=trades();self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:StreamPopulation.from_batch(replace(b,metadata=replace(b.metadata,coverage=Coverage(4,3,False)))))
        self.error(ErrorCode.INVALID_SCHEMA,lambda:replace(StreamPopulation.from_batch(b),identity_policy='unchecked'))
        self.error(ErrorCode.INVALID_SCHEMA,lambda:SessionAccumulator('bars',config(),entity=ENTITY,population=StreamPopulation.from_batch(b)))
        self.error(ErrorCode.INVALID_CONFIG,lambda:accumulator('trades',b,config(),prior_close=prior()))
        a=accumulator('trades',b,config());a.update(b,start_ordinal=0)
        extra=chunk(b,[0]);extra=replace(extra,columns=tuple(Column(x.name,(170,) if x.name=='event_ns' else (4,) if x.name=='order_key' else ('extra',) if x.name=='event_id' else x.values) for x in extra.columns))
        self.error(ErrorCode.BOUNDS,lambda:a.update(extra,start_ordinal=3))

    def test_fixed_retention_with_many_trade_chunks_and_bounded_topk(self):
        for n in (10,100,1000):
            b=trades(instrument_id=('A',)*n,session_id=('S',)*n,event_ns=(110,)*n,order_key=tuple(range(n)),event_id=tuple(str(i) for i in range(n)),eligible=(True,)*n,price=(100,)*n,size=tuple(range(1,n+1)),known_at_ns=(110,)*n)
            a=accumulator('top_k',b,top_config(3))
            for i in range(n):a.update(chunk(b,[i]),start_ordinal=i)
            self.assertEqual(len(a._state.top.rows),3);self.assertEqual(len(a.finalize(certificate(b)).metadata.inputs),1)
            self.assertEqual([x.size for x in a._state.top.rows],[n,n-1,n-2])

    def test_malformed_supplied_payload_rejects_without_partial_update(self):
        b=trades();a=accumulator('trades',b,config());before=asdict(a._state)
        bad=replace(b,columns=tuple(Column(x.name,(100,None,101) if x.name=='price' else x.values) for x in b.columns))
        self.error(ErrorCode.INVALID_SCHEMA,lambda:a.update(bad,start_ordinal=0));self.assertEqual(asdict(a._state),before)

    def test_closing_trade_auction_inclusive_final_bound(self):
        b=trades(event_ns=(110,130,200),condition=('none','none','closing_auction'))
        b=replace(b,metadata=replace(b.metadata,scope=replace(b.metadata.scope,include_closing_auction=True)))
        c=config();c=replace(c,session=replace(c.session,include_closing_auction=True))
        a=accumulator('trades',b,c)
        a.update(chunk(b,[0,1]),start_ordinal=0);a.snapshot(PrefixCoverage(150,Coverage(2,2,True)))
        a.update(chunk(b,[2]),start_ordinal=2);self.same(a.finalize(certificate(b)),compute_trades(b,c,entity=ENTITY))

    def test_structure_price_unavailable_does_not_block_volume_share(self):
        b=fixture(close=None);a=accumulator('structure',b,structure_config())
        a.update(chunk(b,[0]),start_ordinal=0);a.update(chunk(b,[1]),start_ordinal=1)
        r=a.finalize(certificate(b));self.same(r,compute_structure(b,structure_config(),entity=ENTITY))
        self.assertEqual(r.values[1].values[0].rows[0].share,.4)
        self.assertEqual(r.values[0].values[0].rows[0].quality.status,Status.MISSING_INPUT)

    def test_fixed_quote_retention_and_binding_after_many_chunks(self):
        n=1000;b=quotes(instrument_id=('A',)*n,session_id=('S',)*n,event_ns=(110,)*n,order_key=tuple(range(n)),event_id=tuple(str(i) for i in range(n)),bid=(100,)*n,ask=(102,)*n,known_at_ns=(110,)*n)
        a=accumulator('quotes',b,quote_config(3))
        for i in range(n):a.update(chunk(b,[i]),start_ordinal=i)
        r=a.finalize(certificate(b));self.assertEqual(len(a._state.quotes.rows),3);self.assertEqual(len(r.metadata.inputs),1)
        self.assertEqual([x.event_id for x in r.values[0].values[0].rows],['0','1','2'])
        self.same(r,compute_quotes(b,quote_config(3),entity=ENTITY))
