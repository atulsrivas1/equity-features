"""Independent chunk/replay equivalence and conditional legal partition merge."""
from dataclasses import asdict,replace
import unittest
from equity_feature_contracts import Column, ContractError, Coverage, DataKind, PartitionSpan, PrefixCoverage, StreamPopulation
from equity_features.incremental import SessionAccumulator
from equity_features.session import compute_bars,compute_structure,compute_trades,compute_top_k,compute_quotes,compute_time_weighted
from test_incremental import accumulator,chunk,certificate,semantic_equal,ENTITY,batch,config,prior,fixture,structure_config,trades,top_config,quotes,quote_config,updates,continuous_config
from test_state import restore

CASES=(('bars',batch,config,compute_bars),('structure',fixture,structure_config,compute_structure),('trades',trades,config,compute_trades),('top_k',trades,top_config,compute_top_k),('quotes',quotes,quote_config,compute_quotes))

def part(family,b,c,start,end,**extra):
    a=accumulator(family,b,c,**extra);a.update(chunk(b,list(range(start,end))),start_ordinal=0);return a

def merge(a,b,start,split,end):return a.merge_partitions(b,left=PartitionSpan(start,split),right=PartitionSpan(split,end))

class Equivalence(unittest.TestCase):
    def same(self,a,b):semantic_equal(self,asdict(a),asdict(b))
    def reject(self,a,b,left,right):
        x=a.export_state();y=b.export_state()
        with self.assertRaises(ContractError):a.merge_partitions(b,left=left,right=right)
        self.assertEqual(a.export_state(),x);self.assertEqual(b.export_state(),y)

    def test_all_legal_families_every_partition_both_argument_orders(self):
        for family,bf,cf,fn in CASES:
            b=bf();c=cf()
            for split in range(1,b.row_count):
                with self.subTest(family=family,split=split):
                    a=part(family,b,c,0,split);r=part(family,b,c,split,b.row_count);x=a.export_state();y=r.export_state()
                    forward=merge(a,r,0,split,b.row_count)
                    reverse=r.merge_partitions(a,left=PartitionSpan(split,b.row_count),right=PartitionSpan(0,split))
                    self.same(forward.finalize(certificate(b)),fn(b,c,entity=ENTITY));self.same(reverse.finalize(certificate(b)),fn(b,c,entity=ENTITY))
                    self.assertEqual(a.export_state(),x);self.assertEqual(r.export_state(),y)

    def test_all_six_families_chunk_sizes_and_restored_replay(self):
        for family,bf,cf,fn in CASES+(('continuous',updates,continuous_config,compute_time_weighted),):
            b=bf();c=cf()
            for size in (1,2,7,10000):
                with self.subTest(family=family,size=size):
                    a=accumulator(family,b,c)
                    for start in range(0,b.row_count,size):
                        a.update(chunk(b,list(range(start,min(start+size,b.row_count)))),start_ordinal=start);a=restore(a)
                    self.same(a.finalize(certificate(b)),fn(b,c,entity=ENTITY))

    def test_balanced_merge_tree_and_restore(self):
        b=quotes();c=quote_config();n=b.row_count;mid=n//2
        def tree(lo,hi):
            if hi-lo==1:return part('quotes',b,c,lo,hi)
            split=(lo+hi)//2
            return restore(merge(tree(lo,split),tree(split,hi),lo,split,hi))
        self.same(tree(0,n).finalize(certificate(b)),compute_quotes(b,c,entity=ENTITY))

    def test_merged_prefix_can_update_remaining_contiguous_delivery(self):
        b=trades();c=config();a=merge(part('trades',b,c,0,1),part('trades',b,c,1,2),0,1,2)
        a.update(chunk(b,[2]),start_ordinal=2)
        v={x.feature_id.rsplit('.',1)[1]:x.values[0] for x in a.finalize(certificate(b)).values}
        self.assertEqual((v['count'],v['volume'],v['notional']),(3,10,1011))

    def test_prior_close_binding_and_independent_bar_golden(self):
        b=batch();c=config();n=b.row_count
        a=merge(part('bars',b,c,0,1,prior_close=prior()),part('bars',b,c,1,n,prior_close=prior()),0,1,n)
        self.same(a.finalize(certificate(b)),compute_bars(b,c,entity=ENTITY,prior_close=prior()))

    def test_top_rank_equal_times_ties_and_first_observation_order(self):
        b=trades(event_ns=(110,110,110),order_key=(1,2,3),size=(5,5,5));c=top_config();a=merge(part('top_k',b,c,0,1),part('top_k',b,c,1,3),0,1,3)
        self.assertEqual(tuple(x.order_key for x in a.finalize(certificate(b)).values[0].values[0].rows),(1,2))
        b=quotes();c=quote_config();a=merge(part('quotes',b,c,0,1),part('quotes',b,c,1,b.row_count),0,1,b.row_count)
        self.assertEqual(tuple(x.event_id for x in a._state.quotes.rows),tuple(b.column('event_id').values[:a._state.quotes.limit]))

    def test_zero_null_missing_noncausal_and_ineligible_parity(self):
        for family,b,c,fn in (('bars',batch(volume=(0,0),open=(None,None),high=(None,None),low=(None,None),close=(None,None),actual_notional=(0,0)),config(),compute_bars),('trades',trades(eligible=(False,False,False)),config(),compute_trades),('quotes',quotes(bid=(None,100,103,100)),quote_config(),compute_quotes)):
            a=merge(part(family,b,c,0,1),part(family,b,c,1,b.row_count),0,1,b.row_count);self.same(a.finalize(certificate(b)),fn(b,c,entity=ENTITY))
        b=quotes();b=replace(b,columns=tuple(x for x in b.columns if x.name!='ask'));a=merge(part('quotes',b,quote_config(),0,1),part('quotes',b,quote_config(),1,b.row_count),0,1,b.row_count)
        self.same(a.finalize(certificate(b)),compute_quotes(b,quote_config(),entity=ENTITY))

    def test_cross_partition_checked_overflow_flags_no_wrap(self):
        from equity_feature_contracts.inputs import I64_MAX
        b=trades(size=(I64_MAX,1,1));c=config();a=merge(part('trades',b,c,0,1),part('trades',b,c,1,3),0,1,3)
        self.assertTrue(a._state.trades.volume.overflow);self.assertEqual(a._state.trades.volume.value,0)
        with self.assertRaises(ContractError):a.finalize(certificate(b))
        restore(a)

    def test_partition_span_types_counts_overlap_gap_and_bounds_reject(self):
        for vals in ((True,1),(-1,1),(1,1),(2,1),(0,2**63)):
            with self.assertRaises(ContractError):PartitionSpan(*vals)
        b=trades();a=part('trades',b,config(),0,1);r=part('trades',b,config(),1,3)
        for left,right in ((PartitionSpan(0,2),PartitionSpan(2,3)),(PartitionSpan(0,1),PartitionSpan(0,2)),(PartitionSpan(0,1),PartitionSpan(2,4))):self.reject(a,r,left,right)

    def test_source_config_and_enrichment_mismatch_reject(self):
        b=trades();a=part('trades',b,config(),0,1);r=part('trades',b,replace(config(),identity='other'),1,3)
        self.reject(a,r,PartitionSpan(0,1),PartitionSpan(1,3))
        b2=replace(b,metadata=replace(b.metadata,source=replace(b.metadata.source,snapshot_id='other')));r=part('trades',b2,config(),1,3);self.reject(a,r,PartitionSpan(0,1),PartitionSpan(1,3))
        b=batch();a=part('bars',b,config(),0,1,prior_close=prior());r=part('bars',b,config(),1,b.row_count);self.reject(a,r,PartitionSpan(0,1),PartitionSpan(1,b.row_count))

    def test_market_order_overlap_and_false_ordinals_reject(self):
        b=trades();a=part('trades',b,config(),1,3);r=part('trades',b,config(),0,1)
        self.reject(a,r,PartitionSpan(0,2),PartitionSpan(2,3))
        b=batch();a=part('bars',b,config(),0,1);r=part('bars',b,config(),0,1);self.reject(a,r,PartitionSpan(0,1),PartitionSpan(1,2))

    def test_retained_duplicate_and_identical_state_reuse_reject(self):
        b=trades(event_id=('same','same','third'));pop=StreamPopulation(b.kind,tuple(c.name for c in b.columns),b.metadata)
        a=SessionAccumulator('top_k',top_config(),entity=ENTITY,population=pop);a.update(chunk(b,[0]),start_ordinal=0)
        r=SessionAccumulator('top_k',top_config(),entity=ENTITY,population=pop);r.update(chunk(b,[1,2]),start_ordinal=0)
        self.reject(a,r,PartitionSpan(0,1),PartitionSpan(1,3))
        b=trades();a=part('trades',b,config(),0,1);self.reject(a,a,PartitionSpan(0,1),PartitionSpan(1,2))

    def test_advanced_and_sealed_partitions_reject(self):
        b=trades();a=part('trades',b,config(),0,1);r=part('trades',b,config(),1,3);a.snapshot(PrefixCoverage(120,Coverage(1,1,True)))
        self.reject(a,r,PartitionSpan(0,1),PartitionSpan(1,3))
        b=trades();pop=replace(StreamPopulation.from_batch(b),metadata=replace(b.metadata,coverage=Coverage(None,3,False)))
        a=SessionAccumulator('trades',config(),entity=ENTITY,population=pop);a.update(chunk(b,[0]),start_ordinal=0);a.finalize(PrefixCoverage(200,Coverage(None,1,False)))
        r=SessionAccumulator('trades',config(),entity=ENTITY,population=pop);r.update(chunk(b,[1,2]),start_ordinal=0);self.reject(a,r,PartitionSpan(0,1),PartitionSpan(1,3))

    def test_continuous_merge_unsupported_and_chunk_replay_supported(self):
        b=updates();a=part('continuous',b,continuous_config(),0,1);r=part('continuous',b,continuous_config(),1,b.row_count)
        self.reject(a,r,PartitionSpan(0,1),PartitionSpan(1,b.row_count))

    def test_incomplete_chunk_gap_propagates_without_false_completeness(self):
        b=trades();a=accumulator('trades',b,config());x=chunk(b,[0]);a.update(replace(x,metadata=replace(x.metadata,coverage=Coverage(1,1,False))),start_ordinal=0)
        r=part('trades',b,config(),1,3);merged=merge(a,r,0,1,3)
        with self.assertRaises(ContractError):merged.finalize(certificate(b))
        result=merged.finalize(PrefixCoverage(200,Coverage(3,3,False)));self.assertTrue(all(x.values[0] is None for x in result.values))

    def test_large_uneven_skewed_quote_partitions_preserve_counts_and_tolerance(self):
        n=1000;base=quotes();data=dict(instrument_id=('A',)*n,session_id=('S',)*n,event_ns=tuple(110+i//20 for i in range(n)),order_key=tuple(range(n)),event_id=tuple(f'q{i}' for i in range(n)),known_at_ns=tuple(110+i//20 for i in range(n)),bid=tuple(None if i%7==0 else 100+i%17 for i in range(n)),ask=tuple(99 if i%13==0 else 100+i%17+i%4 for i in range(n)))
        b=replace(base,columns=tuple(Column(k,v) for k,v in data.items()),metadata=replace(base.metadata,coverage=Coverage(n,n,True)))
        c=quote_config();expected=compute_quotes(b,c,entity=ENTITY)
        a=part('quotes',b,c,0,7);start=7
        for end in (19,78,79,499,900,n):
            a=merge(a,part('quotes',b,c,start,end),0,start,end);start=end
            a=restore(a)
        self.same(a.finalize(certificate(b)),expected)
        self.assertLessEqual(len(a._state.quotes.rows),a._state.quotes.limit)
        self.assertEqual(sum(a._state.quotes.counts.values()),n)

    def test_independent_window_missing_price_and_future_knowledge_merge(self):
        b=fixture();b=replace(b,columns=tuple(c for c in b.columns if c.name!='close'));c=structure_config()
        a=merge(part('structure',b,c,0,1),part('structure',b,c,1,b.row_count),0,1,b.row_count)
        self.same(a.finalize(certificate(b)),compute_structure(b,c,entity=ENTITY))
        b=quotes();b=replace(b,columns=tuple(Column(x.name,(300,)*b.row_count) if x.name=='known_at_ns' else x for x in b.columns))
        a=merge(part('quotes',b,quote_config(),0,1),part('quotes',b,quote_config(),1,b.row_count),0,1,b.row_count)
        self.same(a.finalize(certificate(b)),compute_quotes(b,quote_config(),entity=ENTITY))

if __name__=='__main__':unittest.main()
