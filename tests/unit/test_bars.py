"""Independent exact expectations and adversarial session bar admission."""
from dataclasses import replace
from fractions import Fraction
import unittest
from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column,
    ConfigSpec, ContractError, Coverage, DataKind, EntityKey, ErrorCode, InputScope,
    Parameter, PriceUnit, Reason, SessionSpec, SourceBinding, Status, WindowSpec,
    builtin_registry,
)
from equity_feature_contracts.columnar import from_arrow, to_arrow, to_arrow_result
from equity_features.session.bars import compute_bars

ENTITY = EntityKey("A","S")

def config(**changes):
    c = ConfigSpec("bars-demo","v1",(Parameter("eligibility_policy","synthetic-v1"),),
        SessionSpec("demo","S",100,200,"supplied"),WindowSpec(1,"S",("P","S","future")),
        AvailabilitySpec(200,210,210),price_unit=PriceUnit(0,"USD"))
    return replace(c,**changes)

def batch(**changes):
    data = dict(instrument_id=("A","A"),session_id=("S","S"),start_ns=(100,150),end_ns=(150,200),
        open=(100,102),high=(103,104),low=(99,101),close=(102,103),volume=(200,300),
        actual_notional=(20300,30900),known_at_ns=(150,210))
    data.update(changes)
    data={k:v for k,v in data.items() if v is not None}
    n=len(data["instrument_id"])
    meta = BatchMetadata("demo",SourceBinding("synthetic","s1","m1","bars"),Coverage(n,n,True),
        PriceUnit(0,"USD"),scope=InputScope(100,200,"synthetic-v1"))
    return CanonicalBatch(DataKind.BAR,tuple(Column(k,v) for k,v in data.items()),meta)

def prior(**changes):
    b = CanonicalBatch(DataKind.DAILY,tuple(Column(k,v) for k,v in dict(instrument_id=("A",),session_id=("P",),
        start_ns=(0,),end_ns=(100,),close=(98,),known_at_ns=(100,)).items()),
        BatchMetadata("demo",SourceBinding("synthetic","p1","m1","prior"),Coverage(1,1,True),
        PriceUnit(0,"USD"),scope=InputScope(0,100,"synthetic-v1")))
    data={c.name:c.values for c in b.columns};data.update(changes)
    return replace(b,columns=tuple(Column(k,v) for k,v in data.items() if v is not None))

def result(b=None,c=None,p=None):
    return compute_bars(b,config() if c is None else c,entity=ENTITY,prior_close=p)

def values(r): return {c.feature_id.rsplit(".",1)[1]:c.values[0] for c in r.values}
def qualities(r): return {q.feature_id.rsplit(".",1)[1]:q for q in r.quality}

class Bars(unittest.TestCase):
    def error(self,code,call):
        with self.assertRaises(ContractError) as caught: call()
        self.assertEqual(caught.exception.code,code)

    def test_twelve_exact_golden_results(self):
        r=result(batch(),p=prior());v=values(r)
        expected=dict(open=100,high=104,low=99,close=103,volume=500,notional=51200,
            close_weighted_price=Fraction(513,5),open_close_return=Fraction(3,100),range_fraction=Fraction(5,103),
            close_location=Fraction(4,5),overnight_gap=Fraction(1,49),close_close_return=Fraction(5,98))
        self.assertEqual(set(v),set(expected))
        for key,value in expected.items():
            if key in ("volume","notional"):self.assertEqual(v[key],value)
            else:self.assertAlmostEqual(v[key],float(value),delta=1e-12+abs(float(value))*1e-12)
        self.assertTrue(all(q.status==Status.AVAILABLE for q in r.quality))
        self.assertEqual(r.metadata.config_digest,config().digest)
        self.assertEqual(r.metadata.inputs[0].metadata,batch().metadata)
        self.assertEqual(r.metadata.availability,config().availability)

    def test_actual_notional_is_not_close_volume_proxy(self):
        v=values(result(batch()));self.assertEqual(v['notional'],51200)
        self.assertNotEqual(v['notional'],v['close_weighted_price']*v['volume'])

    def test_scale_and_exact_decimal_output(self):
        unit=PriceUnit(2,"USD");b=batch();b=replace(b,metadata=replace(b.metadata,price_unit=unit))
        p=prior();p=replace(p,metadata=replace(p.metadata,price_unit=unit))
        v=values(result(b,config(price_unit=unit),p))
        self.assertEqual(v['open'],1.0);self.assertEqual(v['notional'],51200)
        self.assertAlmostEqual(v['close_weighted_price'],1.026)
        self.assertAlmostEqual(v['close_close_return'],5/98)

    def test_absent_batch_all_missing(self):
        r=result();self.assertTrue(all(v is None for v in values(r).values()))
        self.assertTrue(all(q.status==Status.MISSING_INPUT for q in r.quality))

    def test_observed_empty_has_zero_totals(self):
        b=batch();b=replace(b,columns=tuple(Column(c.name,()) for c in b.columns),metadata=replace(b.metadata,coverage=Coverage(0,0,True)))
        v=values(result(b));q=qualities(result(b))
        self.assertEqual(v['volume'],0);self.assertEqual(v['notional'],0)
        self.assertEqual(q['open'].status,Status.NOT_APPLICABLE);self.assertEqual(q['volume'].status,Status.AVAILABLE)

    def test_zero_volume_does_not_invent_prices(self):
        b=batch(open=(None,None),high=(None,None),low=(None,None),close=(None,None),volume=(0,0),actual_notional=None)
        r=result(b);self.assertEqual(values(r)['notional'],0)
        self.assertEqual(qualities(r)['close_weighted_price'].reasons,(Reason.NO_ELIGIBLE_OBSERVATIONS,))

    def test_zero_intervals_do_not_poison_price_readiness(self):
        r=result(batch(open=(None,102),high=(None,104),low=(None,101),close=(None,103),volume=(0,300),actual_notional=(None,30900)))
        self.assertEqual(values(r)['open'],102.0);self.assertEqual(values(r)['notional'],30900)

    def test_flat_range_is_undefined_location(self):
        r=result(batch(open=(100,100),high=(100,100),low=(100,100),close=(100,100),actual_notional=(20000,30000)))
        self.assertEqual(values(r)['range_fraction'],0.0);self.assertIsNone(values(r)['close_location'])
        self.assertEqual(qualities(r)['close_location'].reasons,(Reason.ZERO_DENOMINATOR,))

    def test_missing_notional_independent_of_proxy(self):
        for field in (None,(20300,None)):
            r=result(batch(actual_notional=field));self.assertIsNone(values(r)['notional'])
            self.assertEqual(values(r)['close_weighted_price'],102.6);self.assertEqual(values(r)['volume'],500)

    def test_missing_high_does_not_erase_open_close(self):
        r=result(batch(high=None));self.assertIsNone(values(r)['high']);self.assertEqual(values(r)['open'],100.0)
        self.assertIsNone(values(r)['range_fraction']);self.assertEqual(values(r)['open_close_return'],.03)

    def test_missing_volume_prevents_price_population(self):
        for field in (None,(200,None)):
            r=result(batch(volume=field));self.assertTrue(all(v is None for v in values(r).values()))

    def test_positive_volume_null_price_is_malformed(self):
        self.error(ErrorCode.INVALID_SCHEMA,lambda:result(batch(close=(102,None))))

    def test_missing_prior_affects_only_two_returns(self):
        r=result(batch());self.assertEqual(sum(q.status==Status.AVAILABLE for q in r.quality),10)
        self.assertEqual(qualities(r)['overnight_gap'].reasons,(Reason.ABSENT_INPUT,))

    def test_prior_unknown_future_or_null_independent(self):
        for changes,reason in ((dict(known_at_ns=(None,)),Reason.UNKNOWN_AVAILABILITY),(dict(known_at_ns=(211,)),Reason.FUTURE_KNOWLEDGE),(dict(close=(None,)),Reason.NULL_FIELD)):
            r=result(batch(),p=prior(**changes));self.assertEqual(values(r)['volume'],500)
            self.assertEqual(qualities(r)['overnight_gap'].reasons,(reason,))

    def test_prior_positive_and_governed_slot(self):
        self.error(ErrorCode.INVALID_SCHEMA,lambda:result(batch(),p=prior(close=(0,))))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:result(batch(),p=prior(session_id=("future",))))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:result(batch(),p=prior(instrument_id=("B",))))

    def test_unit_basis_and_namespace_rejected(self):
        b=batch()
        for changes,code in ((dict(price_unit=PriceUnit(1,"USD")),ErrorCode.INVALID_UNIT),
                (dict(price_unit=PriceUnit(0,"EUR")),ErrorCode.INVALID_UNIT),
                (dict(namespace="other"),ErrorCode.INCONSISTENT_IDENTITY),
                (dict(adjustment=AdjustmentSpec("split","p","a","S")),ErrorCode.UNSUPPORTED_ADJUSTMENT)):
            self.error(code,lambda:result(replace(b,metadata=replace(b.metadata,**changes))))
            p=prior();self.error(code,lambda:result(b,p=replace(p,metadata=replace(p.metadata,**changes))))

    def test_mixed_target_entities_rejected(self):
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:result(batch(instrument_id=("A","B"))))
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:result(batch(session_id=("S","other"))))

    def test_exact_scope_and_policy_required(self):
        b=batch()
        for scope,code in ((None,ErrorCode.INVALID_CONFIG),(InputScope(100,200,"wrong"),ErrorCode.INVALID_CONFIG),
                (InputScope(101,200,"synthetic-v1"),ErrorCode.INCONSISTENT_IDENTITY),
                (InputScope(100,200,"synthetic-v1",True),ErrorCode.INCONSISTENT_IDENTITY)):
            self.error(code,lambda:result(replace(b,metadata=replace(b.metadata,scope=scope))))

    def test_partial_delivery_nulls_all(self):
        b=batch();b=replace(b,metadata=replace(b.metadata,coverage=Coverage(3,2,False)))
        r=result(b);self.assertTrue(all(v is None for v in values(r).values()))
        self.assertTrue(all(q.status==Status.INCOMPLETE_COVERAGE for q in r.quality))

    def test_rowcount_cannot_certify_another_population(self):
        b=batch();self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:result(replace(b,metadata=replace(b.metadata,coverage=Coverage(3,3,True)))))

    def test_market_cutoff_and_partial_target(self):
        c=config(availability=AvailabilitySpec(150,210,210));b=batch()
        self.error(ErrorCode.INCONSISTENT_IDENTITY,lambda:result(b,c))
        b=replace(b,columns=tuple(Column(x.name,x.values[:1]) for x in b.columns),metadata=replace(b.metadata,coverage=Coverage(1,1,True),scope=InputScope(100,150,"synthetic-v1")))
        r=result(b,c);self.assertEqual(values(r)['volume'],200)
        self.assertEqual(r.metadata.availability.market_cutoff_ns,150)

    def test_knowledge_is_not_inferred_from_market_time(self):
        for stamps,reason in (((150,211),Reason.FUTURE_KNOWLEDGE),((150,None),Reason.UNKNOWN_AVAILABILITY)):
            r=result(batch(known_at_ns=stamps));self.assertTrue(all(v is None for v in values(r).values()))
            self.assertEqual(qualities(r)['volume'].reasons,(reason,))

    def test_reconstruction_is_distinct_and_retains_unknown(self):
        c=config(availability=AvailabilitySpec(200,210,210,"reconstruction","synthetic-replay"))
        r=result(batch(known_at_ns=(None,300)),c,prior(known_at_ns=(None,)))
        self.assertEqual(values(r)['close_close_return'],5/98)
        self.assertNotEqual(c.digest,config().digest)
        self.assertEqual(r.metadata.inputs[0].metadata.source.input_id,"bars")

    def test_overlap_and_future_bar_errors(self):
        self.error(ErrorCode.INVALID_ORDER,lambda:result(batch(start_ns=(100,149))))
        self.error(ErrorCode.BOUNDS,lambda:result(batch(end_ns=(150,201))))

    def test_int64_volume_overflow_before_wrap(self):
        self.error(ErrorCode.OVERFLOW,lambda:result(batch(volume=(2**63-1,1),actual_notional=None)))

    def test_wide_exact_products_supported(self):
        big=2**62
        b=batch(open=(big,big),high=(big,big),low=(big,big),close=(big,big),volume=(2,2),actual_notional=(big*2,big*2))
        v=values(result(b));self.assertEqual(v['notional'],big*4);self.assertEqual(v['close_weighted_price'],float(big))

    def test_large_population_fails_before_any_wrap(self):
        big=2**63-1
        b=batch(open=(big,big),high=(big,big),low=(big,big),close=(big,big),volume=(big//2,big//2),actual_notional=(big*(big//2),big*(big//2)))
        # Two permitted products fit decimal128 here; a third crosses its bound.
        data={c.name:c.values+(c.values[-1],) for c in b.columns}
        data['start_ns']=(100,130,160);data['end_ns']=(130,160,200)
        b=replace(b,columns=tuple(Column(k,v) for k,v in data.items()),metadata=replace(b.metadata,coverage=Coverage(3,3,True)))
        # Volume overflows first, so direct decimal128 overflow is also independently
        # exercised by checked arithmetic in existing test_validation fixtures.
        self.error(ErrorCode.OVERFLOW,lambda:result(b))

    def test_arrow_scope_roundtrip_and_output_metadata(self):
        b=batch();self.assertEqual(from_arrow(to_arrow(b)),b)
        r=result(b,p=prior());tables=to_arrow_result(r)
        self.assertEqual(tables['values']['session.bar.notional'].column('value').to_pylist(),[51200])
        for c in r.values:
            d=builtin_registry().get(c.feature_id)
            self.assertEqual(c.dtype.value,d.outputs[0].dtype);self.assertEqual(c.unit,d.outputs[0].unit)

    def test_config_unknown_parameters_rejected(self):
        self.error(ErrorCode.INVALID_CONFIG,lambda:result(batch(),config(parameters=())))
        self.error(ErrorCode.INVALID_CONFIG,lambda:result(batch(),config(parameters=(Parameter('eligibility_policy','synthetic-v1'),Parameter('unknown',1)))))

if __name__ == '__main__':unittest.main()
