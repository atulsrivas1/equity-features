"""Independent exact trade fixture and normalized eligibility/timing adversaries."""
from dataclasses import replace
from fractions import Fraction
import unittest
from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column,
    ContractError, Coverage, DataKind, ErrorCode, InputScope, PriceUnit, Reason,
    SourceBinding, Status, builtin_registry,
)
from equity_feature_contracts.columnar import to_arrow_result
from equity_features.session import compute_trades
from test_bars import ENTITY, config

def trades(**changes):
    data=dict(instrument_id=("A",)*3,session_id=("S",)*3,event_ns=(110,130,160),
        order_key=(1,2,3),event_id=("t1","t2","t3"),eligible=(True,)*3,
        price=(100,102,101),size=(2,3,5),known_at_ns=(110,130,210))
    data.update(changes);data={k:v for k,v in data.items() if v is not None}
    n=len(data['instrument_id'])
    meta=BatchMetadata("demo",SourceBinding("synthetic","s1","m1","trades"),Coverage(n,n,True),
        PriceUnit(0,"USD"),scope=InputScope(100,200,"synthetic-v1"))
    return CanonicalBatch(DataKind.TRADE,tuple(Column(k,v) for k,v in data.items()),meta)

def calc(b=None,c=None):return compute_trades(b,config() if c is None else c,entity=ENTITY)
def values(r):return {c.feature_id.rsplit('.',1)[1]:c.values[0] for c in r.values}
def quality(r):return {q.feature_id.rsplit('.',1)[1]:q for q in r.quality}

class Trades(unittest.TestCase):
    def error(self,code,call):
        with self.assertRaises(ContractError) as caught:call()
        self.assertEqual(caught.exception.code,code)

    def test_five_exact_golden_aggregates(self):
        r=calc(trades());v=values(r)
        self.assertEqual(v['count'],3);self.assertEqual(v['volume'],10);self.assertEqual(v['notional'],1011)
        self.assertAlmostEqual(v['vwap'],101.1,delta=1e-12);self.assertAlmostEqual(v['mean_size'],float(Fraction(10,3)),delta=1e-12)
        self.assertTrue(all(q.status==Status.AVAILABLE for q in r.quality))
        self.assertEqual(r.metadata.config_digest,config().digest)
        self.assertEqual(r.metadata.inputs[0].metadata,trades().metadata)

    def test_eligibility_excludes_prints_without_changing_delivery_count(self):
        r=calc(trades(eligible=(True,False,True),price=(100,0,101),size=(2,0,5)))
        v=values(r);self.assertEqual(v['count'],2);self.assertEqual(v['volume'],7);self.assertEqual(v['notional'],705)
        self.assertAlmostEqual(v['vwap'],705/7);self.assertTrue(all(q.observed==3 and q.expected==3 for q in r.quality))

    def test_all_ineligible_is_observed_zero_population(self):
        r=calc(trades(eligible=(False,)*3,price=None,size=None));v=values(r)
        self.assertEqual((v['count'],v['volume'],v['notional']),(0,0,0))
        self.assertIsNone(v['vwap']);self.assertIsNone(v['mean_size'])
        self.assertEqual(quality(r)['vwap'].status,Status.NOT_APPLICABLE)

    def test_empty_observed_and_missing_differ(self):
        b=trades();b=replace(b,columns=tuple(Column(c.name,()) for c in b.columns),metadata=replace(b.metadata,coverage=Coverage(0,0,True)))
        self.assertEqual(values(calc(b))['count'],0)
        r=calc();self.assertTrue(all(x is None for x in values(r).values()));self.assertTrue(all(q.status==Status.MISSING_INPUT for q in r.quality))

    def test_absent_price_only_blocks_notional_and_vwap(self):
        r=calc(trades(price=None));v=values(r)
        self.assertEqual(v['count'],3);self.assertEqual(v['volume'],10);self.assertIsNone(v['notional']);self.assertIsNone(v['vwap'])
        self.assertAlmostEqual(v['mean_size'],10/3)

    def test_absent_size_preserves_only_count(self):
        v=values(calc(trades(size=None)));self.assertEqual(v['count'],3)
        self.assertTrue(all(v[x] is None for x in ('volume','notional','vwap','mean_size')))

    def test_eligible_null_nonpositive_payload_is_malformed(self):
        for changes in (dict(price=(100,None,101)),dict(size=(2,None,5)),dict(price=(100,0,101)),dict(size=(2,0,5))):
            self.error(ErrorCode.INVALID_SCHEMA,lambda:calc(trades(**changes)))
        self.error(ErrorCode.BOUNDS,lambda:calc(trades(eligible=(False,True,True),size=(-1,3,5))))

    def test_price_scale_preserves_exact_notional(self):
        unit=PriceUnit(2,'USD');b=trades();b=replace(b,metadata=replace(b.metadata,price_unit=unit))
        v=values(calc(b,config(price_unit=unit)));self.assertEqual(v['notional'],1011);self.assertAlmostEqual(v['vwap'],1.011)
        self.assertAlmostEqual(v['mean_size'],10/3)

    def test_wide_products_never_int64_wrap(self):
        big=2**62;v=values(calc(trades(price=(big,)*3,size=(2,)*3)))
        self.assertEqual(v['notional'],big*6);self.assertEqual(v['vwap'],float(big))

    def test_volume_overflow_is_typed_failure(self):
        self.error(ErrorCode.OVERFLOW,lambda:calc(trades(size=(2**63-1,1,1))))

    def test_equal_time_total_order_and_duplicate_errors(self):
        self.assertEqual(values(calc(trades(event_ns=(110,)*3)))['count'],3)
        self.error(ErrorCode.DUPLICATE,lambda:calc(trades(event_id=('same','same','t3'))))
        self.error(ErrorCode.DUPLICATE,lambda:calc(trades(event_ns=(110,)*3,order_key=(1,1,2))))
        self.error(ErrorCode.INVALID_ORDER,lambda:calc(trades(event_ns=(130,110,160))))

    def test_market_cutoff_and_ineligible_outside_target(self):
        self.error(ErrorCode.BOUNDS,lambda:calc(trades(event_ns=(110,130,200))))
        self.error(ErrorCode.BOUNDS,lambda:calc(trades(event_ns=(99,130,160),eligible=(False,True,True))))

    def test_closing_auction_requires_actual_explicit_policy(self):
        c=config();c=replace(c,session=replace(c.session,include_closing_auction=True))
        b=trades(event_ns=(110,130,200),condition=('none','none','closing_auction'))
        b=replace(b,metadata=replace(b.metadata,scope=replace(b.metadata.scope,include_closing_auction=True)))
        self.assertEqual(values(calc(b,c))['count'],3)
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:calc(b))

    def test_coverage_is_not_guessed_from_counts(self):
        b=trades();r=calc(replace(b,metadata=replace(b.metadata,coverage=Coverage(4,3,False))))
        self.assertTrue(all(x is None for x in values(r).values()));self.assertTrue(all(q.status==Status.INCOMPLETE_COVERAGE for q in r.quality))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:calc(replace(b,metadata=replace(b.metadata,coverage=Coverage(4,4,True)))))

    def test_unknown_and_future_knowledge_null_causal_values(self):
        for stamps,reason in (((110,130,None),Reason.UNKNOWN_AVAILABILITY),((110,130,211),Reason.FUTURE_KNOWLEDGE)):
            r=calc(trades(known_at_ns=stamps));self.assertTrue(all(x is None for x in values(r).values()))
            self.assertEqual(quality(r)['count'].reasons,(reason,))
        # Normalized false eligibility is still a supplied fact with causal delivery.
        r=calc(trades(eligible=(True,False,True),known_at_ns=(110,None,210)))
        self.assertIsNone(values(r)['count'])

    def test_reconstruction_preserves_distinct_identity(self):
        c=config(availability=AvailabilitySpec(200,210,210,'reconstruction','synthetic-replay'))
        r=calc(trades(known_at_ns=(None,300,210)),c);self.assertEqual(values(r)['count'],3)
        self.assertNotEqual(r.metadata.config_digest,config().digest)

    def test_units_basis_namespace_and_entity_checked(self):
        b=trades()
        for changes,code in ((dict(price_unit=PriceUnit(1,'USD')),ErrorCode.INVALID_UNIT),
                (dict(namespace='wrong'),ErrorCode.INCONSISTENT_IDENTITY),
                (dict(adjustment=AdjustmentSpec('split','p','a','S')),ErrorCode.UNSUPPORTED_ADJUSTMENT),
                (dict(scope=None),ErrorCode.INVALID_CONFIG)):
            self.error(code,lambda:calc(replace(b,metadata=replace(b.metadata,**changes))))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:calc(trades(instrument_id=('A','B','A'))))

    def test_arrow_values_match_registry_units_and_types(self):
        r=calc(trades());tables=to_arrow_result(r)['values']
        self.assertEqual(tables['session.trade.notional'].column('value').to_pylist(),[1011])
        for column in r.values:
            output=builtin_registry().get(column.feature_id).outputs[0]
            self.assertEqual(column.dtype.value,output.dtype);self.assertEqual(column.unit,output.unit)

if __name__=='__main__':unittest.main()
