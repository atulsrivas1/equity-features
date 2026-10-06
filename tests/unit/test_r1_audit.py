"""Independent cross-mode rational/early-close/auction/seed edge qualification."""
from dataclasses import replace
from fractions import Fraction
import unittest
from equity_feature_contracts import Coverage, InputScope, IntervalCoverage, IntervalSpec, PartitionSpan, PrefixCoverage, PriceUnit, Status, builtin_registry, ContractError
from equity_feature_contracts.columnar import to_arrow_result
from equity_features.session import compute_bars,compute_structure,compute_trades,compute_top_k,compute_quotes,compute_time_weighted
from test_incremental import accumulator,chunk,certificate,ENTITY,batch,config,trades,top_config,quotes,quote_config,updates,continuous_config
from test_continuous import seed,one
from test_state import restore
from test_equivalence import part,merge

class R1Audit(unittest.TestCase):
    def early(self,structure=False):
        windows=(IntervalSpec('first',100,120),IntervalSpec('last',120,140))
        b=batch(start_ns=(100,120),end_ns=(120,140),open=(100,110),high=(105,120),low=(99,108),close=(103,115),volume=(2,3),actual_notional=(201,345),known_at_ns=(120,140))
        c=config();c=replace(c,session=replace(c.session,close_ns=140,early_close=True,scheduled_close_ns=200,intervals=windows if structure else ()),availability=replace(c.availability,market_cutoff_ns=140))
        b=replace(b,metadata=replace(b.metadata,scope=InputScope(100,140,'synthetic-v1'),interval_coverage=tuple(IntervalCoverage(x.name,x.start_ns,x.end_ns,Coverage(1,1,True)) for x in windows) if structure else ()))
        return b,c

    def test_independent_early_close_bar_goldens_across_restore_merge(self):
        b,c=self.early();a=restore(merge(part('bars',b,c,0,1),part('bars',b,c,1,2),0,1,2));r=a.finalize(certificate(b))
        v={x.feature_id.rsplit('.',1)[1]:x.values[0] for x in r.values}
        self.assertEqual((v['open'],v['high'],v['low'],v['close'],v['volume'],v['notional']),(100.,120.,99.,115.,5,546))
        self.assertEqual(v['close_weighted_price'],float(Fraction(551,5)))
        self.assertEqual(v['open_close_return'],.15);self.assertEqual(v['range_fraction'],float(Fraction(21,115)));self.assertEqual(v['close_location'],float(Fraction(16,21)))
        self.assertEqual(r,compute_bars(b,c,entity=ENTITY));self.assertEqual(r.metadata.availability.market_cutoff_ns,140)

    def test_independent_early_close_window_goldens_quality_arrow(self):
        b,c=self.early(True);a=restore(merge(part('structure',b,c,0,1),part('structure',b,c,1,2),0,1,2));r=a.finalize(certificate(b))
        self.assertEqual([x.volume for x in r.values[0].values[0].rows],[2,3]);self.assertEqual([x.share for x in r.values[1].values[0].rows],[.4,.6])
        self.assertTrue(all(q.status==Status.AVAILABLE for q in r.quality));self.assertEqual(r,compute_structure(b,c,entity=ENTITY))
        self.assertEqual(to_arrow_result(r)['values']['session.structure.interval_ohlcv'].num_rows,1)

    def test_closing_auction_exact_final_cutoff_merged_evidence(self):
        b=trades(event_ns=(110,130,200),condition=('none','none','closing_auction'));c=top_config();c=replace(c,session=replace(c.session,include_closing_auction=True))
        b=replace(b,metadata=replace(b.metadata,scope=replace(b.metadata.scope,include_closing_auction=True)))
        a=restore(merge(part('top_k',b,c,0,2),part('top_k',b,c,2,3),0,2,3));r=a.finalize(certificate(b));self.assertEqual(r,compute_top_k(b,c,entity=ENTITY))
        self.assertTrue(any(x.event_ns==200 and x.boundary=='closing_auction' for x in r.evidence))
        ordinary=trades(event_ns=(110,130,200));ordinary=replace(ordinary,metadata=b.metadata)
        with self.assertRaises(ContractError):part('top_k',ordinary,c,2,3)

    def test_exact_above_binary64_integer_notional_survives_merge_restore_arrow(self):
        p=2**53+1;b=trades(price=(p,100,101),size=(3,4,4),eligible=(True,False,False));c=config()
        a=restore(merge(part('trades',b,c,0,1),part('trades',b,c,1,3),0,1,3));r=a.finalize(certificate(b))
        v={x.feature_id.rsplit('.',1)[1]:x.values[0] for x in r.values};self.assertEqual((v['count'],v['volume'],v['notional']),(1,3,3*p));self.assertEqual(r,compute_trades(b,c,entity=ENTITY))
        table=to_arrow_result(r)['values'];value=table['session.trade.notional'].column('value').to_pylist()[0];self.assertEqual(int(value),3*p)

    def test_independent_scaled_sampled_quote_rational_denominator_after_merge(self):
        b=quotes(bid=(10000,10100,10300,None),ask=(10003,10100,10200,10100));c=quote_config();c=replace(c,price_unit=PriceUnit(2,'USD'));b=replace(b,metadata=replace(b.metadata,price_unit=c.price_unit))
        a=restore(merge(part('quotes',b,c,0,1),part('quotes',b,c,1,4),0,1,4));r=a.finalize(certificate(b));v=r.values[0].values[0];counts=r.values[1].values[0]
        self.assertEqual((counts.normal,counts.locked,counts.crossed,counts.invalid),(1,1,1,1));self.assertEqual(v.valid,2);self.assertEqual(v.mean_spread,.015)
        self.assertAlmostEqual(v.mean_bps,float(Fraction(30000,20003)),places=12);self.assertEqual(v.rows[2].spread,-1.)
        self.assertEqual(r,compute_quotes(b,c,entity=ENTITY))

    def test_seed_original_expiry_across_empty_prefix_restore_and_later_update(self):
        b=one(event=107,bid=100,ask=102);c=continuous_config(age=4,initial='seed')
        a=accumulator('continuous',b,c,seed=seed(event=99,bid=100,ask=102));a.snapshot(PrefixCoverage(102,Coverage(0,0,True)));a=restore(a);a.update(b,start_ordinal=0);r=a.finalize(certificate(b));v=r.values[0].values[0]
        self.assertEqual((v.durations.normal,v.durations.expired,v.durations.unknown),(7,5,0));self.assertEqual(v.mean_spread,2.);self.assertEqual(v.mean_bps,float(Fraction(20000,101)))
        self.assertEqual(r,compute_time_weighted(b,c,entity=ENTITY,seed=seed(event=99,bid=100,ask=102)))

    def test_inventory_has_no_unimplemented_or_arbitrary_continuous_modes(self):
        registry=builtin_registry();self.assertEqual(len(registry.list_features(family='session',capability='batch')),23);self.assertEqual(len(registry.list_features(capability='update')),23);self.assertEqual(len(registry.list_features(capability='restore')),23);self.assertEqual(len(registry.list_features(capability='merge')),22)
        self.assertFalse(registry.get('session.quote.time_weighted_spread').capabilities.merge)
        for d in registry.list_features():
            if d.planned_release!='R1':
                self.assertFalse(any((d.capabilities.update,d.capabilities.restore,d.capabilities.merge)))
                if d.feature_id not in ('history.return','history.prior_high','history.prior_low','history.sma','history.ema','history.rsi','history.atr','history.return_volatility','baseline.daily_volume','baseline.relative_volume','baseline.interval_volume','baseline.interval_relative_volume'):self.assertFalse(d.capabilities.batch)

if __name__=='__main__':unittest.main()
