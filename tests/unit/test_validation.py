"""Independent semantic and exact transformation fixtures."""
from dataclasses import replace
from decimal import Decimal
import unittest
from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ContractError,
    Coverage, DataKind, ErrorCode, PriceUnit, Reason, SessionSpec, SourceBinding,
    checked_decimal128, checked_int64, checked_product, checked_sum,
    normalize_batch, quantize_float_prices, quote_state, require_compatible_inputs,
    validate_batch,
)

def batch(kind=DataKind.TRADE, **fields):
    n=len(next(iter(fields.values()))) if fields else 1
    common={"instrument_id":("A",)*n,"session_id":("S",)*n}
    if kind in (DataKind.TRADE,DataKind.QUOTE):common.update(event_ns=tuple(range(100,100+n)),order_key=tuple(range(n)),event_id=tuple("e"+str(i) for i in range(n)))
    if kind==DataKind.TRADE:common.update(eligible=(True,)*n,price=(100,)*n,size=(2,)*n)
    if kind in (DataKind.BAR,DataKind.DAILY):common.update(start_ns=tuple(100+10*i for i in range(n)),end_ns=tuple(110+10*i for i in range(n)),open=(100,)*n,high=(110,)*n,low=(90,)*n,close=(105,)*n,volume=(2,)*n)
    if kind==DataKind.REFERENCE:common.update(reference_id=tuple("r"+str(i) for i in range(n)),fact_kind=("membership",)*n,effective_start_ns=tuple(range(n)))
    common.update(fields)
    metadata=BatchMetadata("demo",SourceBinding("synthetic","snapshot","map1","input1"),Coverage(n,n,True),PriceUnit(2,"USD"),sampling="continuous" if kind==DataKind.QUOTE else "none")
    return CanonicalBatch(kind,tuple(Column(name,tuple(values)) for name,values in common.items()),metadata)

class SemanticValidation(unittest.TestCase):
    def assertCode(self,code,call):
        with self.assertRaises(ContractError) as caught:call()
        self.assertEqual(caught.exception.code,code)
    def test_sorted_trade_and_owned_report(self):
        report=validate_batch(batch(event_ns=(100,101),known_at_ns=(100,101)))
        self.assertEqual(report.row_count,2);self.assertTrue(report.supplied_fields_ready)
    def test_unsorted_never_silently_sorts(self):
        b=batch(event_ns=(101,100));self.assertCode(ErrorCode.INVALID_ORDER,lambda:validate_batch(b))
        self.assertEqual(b.column("event_ns").values,(101,100))
    def test_equal_time_supplied_order(self):
        b=batch(event_ns=(100,100),order_key=(1,2));self.assertEqual(validate_batch(b).row_count,2)
        self.assertCode(ErrorCode.DUPLICATE,lambda:validate_batch(batch(event_ns=(100,100),order_key=(1,1))))
    def test_duplicate_event_id(self):
        self.assertCode(ErrorCode.DUPLICATE,lambda:validate_batch(batch(event_ns=(100,101),event_id=("same","same"))))
    def test_per_partition_interleaving(self):
        b=batch(event_ns=(100,50,101),instrument_id=("A","B","A"))
        self.assertEqual(validate_batch(b).row_count,3)
    def test_missing_optional_payload_report(self):
        b=batch();b=replace(b,columns=tuple(c for c in b.columns if c.name!="price"))
        report=validate_batch(b);self.assertEqual(report.missing_fields,("price",));self.assertFalse(report.supplied_fields_ready)
    def test_eligible_trade_validity(self):
        for fields in ({"price":(0,)},{"price":(None,)},{"size":(0,)},{"size":(-1,)}):
            self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:validate_batch(batch(**fields)))
    def test_ineligible_rows_preserved(self):
        b=batch(eligible=(False,),price=(None,),size=(0,));self.assertEqual(validate_batch(b).row_count,1)
        self.assertEqual(b.column("eligible").values,(False,))
    def test_all_quote_states_preserved(self):
        b=batch(DataKind.QUOTE,bid=(100,102,105,None),ask=(102,102,104,102))
        self.assertEqual(validate_batch(b).quote_states,("normal","locked","crossed","invalid"))
        self.assertEqual(b.row_count,4);self.assertEqual(quote_state(0,1),"invalid")
    def test_quote_negative_size_invalid(self):
        self.assertCode(ErrorCode.BOUNDS,lambda:validate_batch(batch(DataKind.QUOTE,bid=(100,),ask=(101,),bid_size=(-1,))))
    def test_session_cutoff_auctions(self):
        s=SessionSpec("demo","S",100,200,"supplied",include_opening_auction=True,include_closing_auction=True)
        self.assertEqual(validate_batch(batch(event_ns=(200,),condition=("closing_auction",)),session=s,availability=AvailabilitySpec(200,210,210)).row_count,1)
        self.assertCode(ErrorCode.BOUNDS,lambda:validate_batch(batch(event_ns=(200,)),session=s))
        self.assertCode(ErrorCode.BOUNDS,lambda:validate_batch(batch(event_ns=(100,),condition=("opening_auction",)),session=replace(s,include_opening_auction=False)))
        self.assertCode(ErrorCode.BOUNDS,lambda:validate_batch(batch(),session=s,availability=AvailabilitySpec(201,210,210)))
    def test_session_namespace_mismatch(self):
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:validate_batch(batch(),session=SessionSpec("other","S",100,200,"zone")))
    def test_knowledge_exclusion_never_filters(self):
        b=batch(known_at_ns=(None,211,210));r=validate_batch(b,availability=AvailabilitySpec(200,210,210))
        self.assertEqual([(x.row_index,x.reason) for x in r.knowledge_exclusions],[(0,Reason.UNKNOWN_AVAILABILITY),(1,Reason.FUTURE_KNOWLEDGE)])
        self.assertEqual(b.row_count,3)
        recon=AvailabilitySpec(200,300,200,"reconstruction","later revision")
        self.assertEqual(validate_batch(b,availability=recon).knowledge_exclusions,())
    def test_close_only_daily_positive_without_volume(self):
        def close_only(value):
            b=batch(DataKind.DAILY,close=(value,))
            return replace(b,columns=tuple(c for c in b.columns if c.name not in ("open","high","low","volume")))
        for value in (0,-1):self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:validate_batch(close_only(value),required_fields=("close",)))
        self.assertTrue(validate_batch(close_only(105),required_fields=("close",)).supplied_fields_ready)
        self.assertFalse(validate_batch(close_only(None),required_fields=("close",)).supplied_fields_ready)
    def test_daily_ohlc_coherence_without_volume(self):
        b=batch(DataKind.DAILY,close=(111,));b=replace(b,columns=tuple(c for c in b.columns if c.name!="volume"))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:validate_batch(b,required_fields=("close",)))
    def test_bar_negative_price_with_unknown_volume(self):
        b=batch(DataKind.BAR,close=(-1,),volume=(None,))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:validate_batch(b))
    def test_valid_bar_exact_notional(self):
        self.assertTrue(validate_batch(batch(DataKind.BAR,actual_notional=(200,))).supplied_fields_ready)
        for notional in (179,221):self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:validate_batch(batch(DataKind.BAR,actual_notional=(notional,))))
    def test_bar_ohlc_coherence_and_missing(self):
        for changes in ({"low":(111,)},{"open":(111,)},{"close":(None,)}):
            self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:validate_batch(batch(DataKind.BAR,**changes)))
        b=batch(DataKind.BAR);b=replace(b,columns=tuple(c for c in b.columns if c.name!="close"))
        self.assertEqual(validate_batch(b).missing_fields,("close",))
    def test_zero_volume_null_ohlc(self):
        b=batch(DataKind.BAR,volume=(0,),open=(None,),high=(None,),low=(None,),close=(None,),actual_notional=(0,))
        self.assertEqual(validate_batch(b).row_count,1)
        self.assertTrue(validate_batch(b,required_fields=("volume",)).supplied_fields_ready)
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:validate_batch(batch(DataKind.BAR,volume=(0,))))
    def test_overlap_duplicate_and_forming_bars(self):
        self.assertCode(ErrorCode.INVALID_ORDER,lambda:validate_batch(batch(DataKind.BAR,start_ns=(100,105),end_ns=(110,115))))
        self.assertCode(ErrorCode.DUPLICATE,lambda:validate_batch(batch(DataKind.BAR,start_ns=(100,100),end_ns=(110,110))))
        self.assertCode(ErrorCode.BOUNDS,lambda:validate_batch(batch(DataKind.BAR),availability=AvailabilitySpec(109,200,200)))
    def test_daily_order_uses_time_not_session_label(self):
        b=batch(DataKind.DAILY,start_ns=(100,110),end_ns=(110,120),session_id=("Z","A"))
        self.assertEqual(validate_batch(b).row_count,2)
        self.assertCode(ErrorCode.DUPLICATE,lambda:validate_batch(batch(DataKind.DAILY,start_ns=(100,110),end_ns=(110,120))))
    def test_reference_bounds_factors_duplicates_order(self):
        self.assertCode(ErrorCode.BOUNDS,lambda:validate_batch(batch(DataKind.REFERENCE,effective_start_ns=(10,),effective_end_ns=(10,))))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT,lambda:validate_batch(batch(DataKind.REFERENCE,factor_num=(2,),factor_den=(0,))))
        self.assertCode(ErrorCode.DUPLICATE,lambda:validate_batch(batch(DataKind.REFERENCE,reference_id=("same","same"))))
        self.assertCode(ErrorCode.INVALID_ORDER,lambda:validate_batch(batch(DataKind.REFERENCE,effective_start_ns=(2,1))))
    def test_checked_wide_products_and_sums(self):
        self.assertEqual(checked_product(2**62,2),2**63)
        self.assertCode(ErrorCode.OVERFLOW,lambda:checked_product(2**62,2,representation="int64"))
        self.assertCode(ErrorCode.OVERFLOW,lambda:checked_sum((2**63-1,1)))
        self.assertEqual(checked_sum((10**30,10**30),representation="decimal128"),2*10**30)
        self.assertCode(ErrorCode.OVERFLOW,lambda:checked_sum((10**38-1,1),representation="decimal128"))
        self.assertCode(ErrorCode.OVERFLOW,lambda:checked_sum((2**64,-2**64)))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:checked_int64(True))
    def test_coverage_count_overflow(self):
        self.assertCode(ErrorCode.OVERFLOW,lambda:Coverage(None,2**63,False))
        self.assertCode(ErrorCode.OVERFLOW,lambda:Coverage(2**63,0,False))
    def test_int64_and_wide_limits(self):
        self.assertEqual(checked_int64(-(2**63)),-(2**63));self.assertEqual(checked_decimal128(10**38-1),10**38-1)
        self.assertCode(ErrorCode.OVERFLOW,lambda:checked_decimal128(10**38))
    def test_compatible_units_basis_and_namespace(self):
        a=batch();require_compatible_inputs(a,a)
        self.assertCode(ErrorCode.INVALID_UNIT,lambda:require_compatible_inputs(a,replace(a,metadata=replace(a.metadata,price_unit=PriceUnit(3,"USD")))))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:require_compatible_inputs(a,replace(a,metadata=replace(a.metadata,namespace="other"))))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT,lambda:require_compatible_inputs(a,replace(a,metadata=replace(a.metadata,adjustment=AdjustmentSpec("split","v1","actions","S")))))
    def test_explicit_sort_identity_mapping(self):
        b=batch(event_ns=(101,100),price=(101,100));n=normalize_batch(b,sort=True)
        self.assertEqual(n.batch.column("event_ns").values,(100,101));self.assertEqual(n.report.original_row_indices,(1,0));self.assertTrue(n.report.sorted)
        self.assertNotEqual(n.batch.metadata.source.input_id,b.metadata.source.input_id)
        self.assertEqual(n.batch.metadata.source.snapshot_id,b.metadata.source.snapshot_id)
        self.assertEqual(b.column("event_ns").values,(101,100))
    def test_explicit_identical_dedup_only(self):
        b=batch(event_ns=(100,100),order_key=(0,0),event_id=("same","same"))
        self.assertCode(ErrorCode.DUPLICATE,lambda:normalize_batch(b))
        n=normalize_batch(b,deduplicate="identical");self.assertEqual(n.batch.row_count,1);self.assertEqual(n.report.discarded_row_indices,(1,))
        conflict=batch(event_ns=(100,100),order_key=(0,0),event_id=("same","same"),price=(100,101))
        self.assertCode(ErrorCode.DUPLICATE,lambda:normalize_batch(conflict,deduplicate="identical"))
    def test_exact_rescale_and_notional(self):
        b=batch(DataKind.BAR,actual_notional=(200,));n=normalize_batch(b,price_unit=PriceUnit(3,"USD"))
        self.assertEqual(n.batch.column("open").values,(1000,));self.assertEqual(n.batch.column("actual_notional").values,(2000,))
        self.assertEqual(n.batch.column("volume").values,(2,));self.assertEqual(n.report.rounded_cells,0)
        self.assertEqual(n.report.original_price_unit,PriceUnit(2,"USD"))
    def test_lossy_rescale_requires_policy(self):
        b=batch(price=(105,));self.assertCode(ErrorCode.INVALID_UNIT,lambda:normalize_batch(b,price_unit=PriceUnit(1,"USD")))
        n=normalize_batch(b,price_unit=PriceUnit(1,"USD"),rounding="half_even")
        self.assertEqual(n.batch.column("price").values,(10,));self.assertEqual(n.report.rounded_cells,1)
        self.assertEqual(normalize_batch(batch(price=(115,)),price_unit=PriceUnit(1,"USD"),rounding="half_even").batch.column("price").values,(12,))
    def test_rescale_overflow_and_currency(self):
        self.assertCode(ErrorCode.OVERFLOW,lambda:normalize_batch(batch(price=(2**63-1,)),price_unit=PriceUnit(3,"USD")))
        self.assertCode(ErrorCode.INVALID_UNIT,lambda:normalize_batch(batch(),price_unit=PriceUnit(2,"EUR")))
    def test_normalization_owned_idempotent(self):
        b=batch();n=normalize_batch(b,sort=True);self.assertIsNot(n.batch,b)
        self.assertEqual(n.batch,b);self.assertEqual(n.report.output_input_id,b.metadata.source.input_id)
        changed=normalize_batch(batch(event_ns=(101,100)),sort=True).batch
        self.assertEqual(normalize_batch(changed,sort=True).batch.metadata.source.input_id,changed.metadata.source.input_id)
    def test_float_interpretation_is_explicit(self):
        unit=PriceUnit(2,"USD")
        self.assertCode(ErrorCode.INVALID_UNIT,lambda:quantize_float_prices((0.1,),unit=unit,interpretation="binary64_exact",rounding="exact"))
        self.assertEqual(quantize_float_prices((0.1,None),unit=unit,interpretation="decimal_repr",rounding="exact").values,(10,None))
    def test_float_half_even_positive_negative(self):
        q=quantize_float_prices((1.25,1.35,-1.25,-1.35),unit=PriceUnit(1,"USD"),interpretation="decimal_repr",rounding="half_even")
        self.assertEqual(q.values,(12,14,-12,-14));self.assertEqual(q.rounded_cells,4)
    def test_float_nonfinite_and_overflow(self):
        for value in (float("nan"),float("inf"),True,1):
            self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:quantize_float_prices((value,),unit=PriceUnit(2,"USD"),interpretation="decimal_repr",rounding="half_even"))
        self.assertCode(ErrorCode.OVERFLOW,lambda:quantize_float_prices((1e30,),unit=PriceUnit(2,"USD"),interpretation="decimal_repr",rounding="half_even"))
    def test_empty_and_no_lazy_helpers(self):
        empty=batch(event_ns=());self.assertEqual(validate_batch(empty).row_count,0);self.assertEqual(normalize_batch(empty).batch.row_count,0)
        def lazy():raise AssertionError("source executed");yield 1
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:checked_sum(lazy()))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:quantize_float_prices(lazy(),unit=PriceUnit(2,"USD"),interpretation="decimal_repr",rounding="exact"))

if __name__ == "__main__":unittest.main()
