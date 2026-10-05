"""Production quote APIs compared with independent exact arithmetic and state cases."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import unittest
from equity_feature_contracts import (BatchMetadata, CanonicalBatch, Column, ContractError,
    Coverage, DataKind, ErrorCode, InputScope, Parameter, PriceUnit, QuoteStateCounts,
    SampledSpread, SourceBinding, Status, builtin_registry)
from equity_feature_contracts.columnar import to_arrow_result
from equity_features.session import compute_quotes
from test_bars import ENTITY, config


def cfg(limit=4):return replace(config(),parameters=config().parameters+(Parameter('observation_limit',limit),))
def quotes(**changes):
    data=dict(instrument_id=('A',)*4,session_id=('S',)*4,event_ns=(110,120,130,140),order_key=(1,2,3,4),event_id=('q1','q2','q3','q4'),bid=(100,102,105,None),ask=(102,102,104,102),known_at_ns=(110,120,130,140))
    data.update(changes);data={k:v for k,v in data.items() if v is not None};n=len(data['instrument_id'])
    return CanonicalBatch(DataKind.QUOTE,tuple(Column(k,v) for k,v in data.items()),BatchMetadata('demo',SourceBinding('synthetic','s1','m1','quotes'),Coverage(n,n,True),PriceUnit(0,'USD'),sampling='trade_snapshot',scope=InputScope(100,200,'synthetic-v1')))
def calc(b=None,c=None):return compute_quotes(b,cfg() if c is None else c,entity=ENTITY)
def sample(r):return r.values[0].values[0]
def counts(r):return r.values[1].values[0]

def empty():
    b=quotes();return replace(b,columns=tuple(Column(c.name,()) for c in b.columns),metadata=replace(b.metadata,coverage=Coverage(0,0,True)))

class Quotes(unittest.TestCase):
    def error(self,code,fn):
        with self.assertRaises(ContractError) as caught:fn()
        self.assertEqual(caught.exception.code,code)

    def test_golden_exact_means_counts_diagnostics(self):
        r=calc(quotes());s=sample(r);n=counts(r)
        self.assertEqual(n,QuoteStateCounts(1,1,1,1));self.assertEqual((n.total,n.valid),(4,2))
        self.assertEqual(s.mean_spread,1.0);self.assertAlmostEqual(s.mean_bps,float(Fraction(10000,101)),delta=1e-12)
        self.assertEqual([x.state for x in s.rows],['normal','locked','crossed','invalid'])
        self.assertEqual(s.rows[2].spread,-1.0);self.assertIsNone(s.rows[3].bps)
        self.assertFalse(s.truncated);self.assertEqual(len(r.evidence),4)

    def test_mean_bps_is_not_ratio_of_means(self):
        r=calc(quotes(bid=(1,100,1000,10000),ask=(3,110,1100,10010)))
        expected=sum(Fraction(20000*(a-b),a+b) for b,a in zip((1,100,1000,10000),(3,110,1100,10010)))/4
        self.assertAlmostEqual(sample(r).mean_bps,float(expected),delta=1e-12)
        wrong=20000*sum((2,10,100,10))/sum((4,210,2100,20010))
        self.assertGreater(abs(sample(r).mean_bps-wrong),100)

    def test_locked_zero_is_valid(self):
        r=calc(quotes(bid=(100,)*4,ask=(100,)*4));self.assertEqual(counts(r).valid,4)
        self.assertEqual((sample(r).mean_spread,sample(r).mean_bps),(0.0,0.0));self.assertEqual(r.quality[0].status,Status.AVAILABLE)

    def test_all_crossed_retains_diagnostics_null_means(self):
        r=calc(quotes(bid=(101,)*4,ask=(100,)*4));self.assertEqual(counts(r).crossed,4)
        self.assertEqual(r.quality[0].status,Status.NOT_APPLICABLE);self.assertIsNone(sample(r).mean_spread)
        self.assertEqual(len(sample(r).rows),4);self.assertEqual(r.quality[1].status,Status.AVAILABLE)

    def test_null_and_nonpositive_count_as_invalid(self):
        r=calc(quotes(bid=(None,0,-1,100),ask=(100,100,100,0)));self.assertEqual(counts(r).invalid,4)
        self.assertTrue(all(x.spread is None for x in sample(r).rows));self.assertEqual(r.quality[0].status,Status.NOT_APPLICABLE)

    def test_optional_sizes_do_not_change_classification(self):
        r=calc(quotes(bid_size=(None,0,5,10),ask_size=(0,None,10,5)))
        self.assertEqual(counts(r),counts(calc(quotes())));self.assertEqual(sample(r),sample(calc(quotes())))

    def test_empty_covered_vs_missing_and_absent_sides(self):
        r=calc(empty());self.assertEqual(counts(r).total,0);self.assertEqual(sample(r).rows,())
        self.assertEqual(r.quality[0].status,Status.NOT_APPLICABLE);self.assertEqual(r.quality[1].status,Status.AVAILABLE)
        self.assertTrue(all(c.values[0] is None for c in calc().values))
        self.assertTrue(all(c.values[0] is None for c in calc(quotes(bid=None)).values))

    def test_sampling_labels_are_distinct_event_populations(self):
        b=quotes();a=calc(b);c=calc(replace(b,metadata=replace(b.metadata,sampling='continuous')))
        self.assertEqual(sample(a).mean_bps,sample(c).mean_bps)
        self.assertEqual(sample(a).sampling,'trade_snapshot');self.assertEqual(sample(c).sampling,'continuous')
        self.assertNotEqual(a.metadata.identity_digest,c.metadata.identity_digest)

    def test_bounded_optional_observations_and_provenance(self):
        r=calc(quotes(),cfg(2));s=sample(r);self.assertEqual([x.event_id for x in s.rows],['q1','q2'])
        self.assertTrue(s.truncated);self.assertEqual(len(r.evidence),2);self.assertEqual(s.total,4)
        r=calc(quotes(),cfg(0));self.assertEqual(sample(r).rows,());self.assertEqual(r.evidence,())
        self.assertEqual(sample(r).mean_bps,s.mean_bps)

    def test_invalid_observation_bounds(self):
        for bound in (-1,10001,True,1.0,'2'):
            self.error(ErrorCode.INVALID_CONFIG,lambda:calc(quotes(),cfg(bound)))
        self.error(ErrorCode.INVALID_CONFIG,lambda:calc(quotes(),config()))

    def test_coverage_knowledge_and_actual_population(self):
        b=quotes();r=calc(replace(b,metadata=replace(b.metadata,coverage=Coverage(5,4,False))))
        self.assertTrue(all(x.status==Status.INCOMPLETE_COVERAGE for x in r.quality));self.assertEqual(r.evidence,())
        self.assertTrue(all(c.values[0] is None for c in calc(quotes(known_at_ns=(110,120,130,999))).values))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:calc(replace(b,metadata=replace(b.metadata,coverage=Coverage(3,3,True)))))

    def test_order_duplicate_and_cutoff_errors(self):
        self.error(ErrorCode.DUPLICATE,lambda:calc(quotes(event_id=('q1','q1','q3','q4'))))
        self.error(ErrorCode.INVALID_ORDER,lambda:calc(quotes(event_ns=(120,110,130,140))))
        self.error(ErrorCode.DUPLICATE,lambda:calc(quotes(event_ns=(110,)*4,order_key=(1,1,2,3))))
        self.error(ErrorCode.BOUNDS,lambda:calc(quotes(event_ns=(110,120,130,200))))
        r=calc(quotes(event_ns=(110,)*4));self.assertEqual(counts(r).total,4)

    def test_scale_and_wide_half_sum(self):
        unit=PriceUnit(2,'USD');b=quotes();b=replace(b,metadata=replace(b.metadata,price_unit=unit))
        s=sample(calc(b,replace(cfg(),price_unit=unit)));self.assertEqual(s.mean_spread,.01)
        big=2**63-1;s=sample(calc(quotes(bid=(big-1,)*4,ask=(big,)*4)))
        self.assertEqual(s.mean_spread,1.0);self.assertAlmostEqual(s.mean_bps,float(Fraction(20000,2*big-1)),delta=1e-25)

    def test_compensated_mean_matches_exact_oracle_and_retained_bound(self):
        n=1000;bids=tuple(1 if i%2 else 2**62 for i in range(n));asks=tuple(x+1 for x in bids)
        b=quotes(instrument_id=('A',)*n,session_id=('S',)*n,event_ns=(110,)*n,order_key=tuple(range(n)),event_id=tuple(str(i) for i in range(n)),bid=bids,ask=asks,known_at_ns=(110,)*n)
        s=sample(calc(b,cfg(3)));oracle=sum(Fraction(20000,a+b) for a,b in zip(asks,bids))/n
        self.assertAlmostEqual(s.mean_bps,float(oracle),delta=1e-12);self.assertEqual(len(s.rows),3)

    def test_immutable_structures_and_quality_consistency(self):
        r=calc(quotes());s=sample(r);rows=list(s.rows);owned=replace(s,rows=rows);rows.clear();self.assertEqual(len(owned.rows),4)
        with self.assertRaises(FrozenInstanceError):owned.total=9
        self.error(ErrorCode.INVALID_SCHEMA,lambda:replace(s,valid=0))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,evidence=()))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,quality=(replace(r.quality[0],expected=5,observed=5),r.quality[1])))

    def test_arrow_structures_and_utc_ns(self):
        import pyarrow as pa
        tables=to_arrow_result(calc(quotes()))['values'];s=tables['session.quote.sampled_spread'].column('value').combine_chunks()
        self.assertEqual(s.field('valid').to_pylist(),[2]);self.assertEqual(s.field('mean_spread').to_pylist(),[1.0])
        self.assertEqual(s.field('rows').flatten().field('event_ns').cast(pa.int64()).to_pylist(),[110,120,130,140])
        self.assertEqual(tables['session.quote.state_counts'].column('value').combine_chunks().field('total').to_pylist(),[4])
        self.assertIsNone(to_arrow_result(calc(empty()))['values']['session.quote.sampled_spread'].column('value').combine_chunks().field('mean_bps').to_pylist()[0])

    def test_identity_basis_units_and_capabilities(self):
        b=quotes();self.error(ErrorCode.INVALID_UNIT,lambda:calc(replace(b,metadata=replace(b.metadata,price_unit=PriceUnit(1,'USD')))))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:calc(quotes(instrument_id=('B',)*4)))
        for feature in ('session.quote.sampled_spread','session.quote.state_counts'):
            builtin_registry().require_capability(feature,'batch')
            for mode in ('merge',):
                self.error(ErrorCode.UNSUPPORTED_CAPABILITY,lambda:builtin_registry().require_capability(feature,mode))

    def test_sampled_label_and_denominator_cannot_contradict_binding(self):
        r=calc(quotes());s=sample(r)
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,values=(replace(r.values[0],values=(replace(s,sampling='continuous'),)),r.values[1])))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,values=(replace(r.values[0],values=(replace(s,valid=3),)),r.values[1])))
