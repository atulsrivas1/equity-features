"""Independent synthetic contract fixtures; no providers or private data."""
from dataclasses import replace
import unittest
import numpy as np
import pyarrow as pa
from equity_feature_contracts import (
    AdjustmentSpec, BatchMetadata, CanonicalBatch, Column, Coverage, DataKind,
    DType, PriceUnit, SourceBinding, schema_for,
)
from equity_feature_contracts.columnar import from_arrow, to_arrow, from_numpy, to_numpy

def metadata(kind=DataKind.TRADE):
    return BatchMetadata("synthetic:instrument:v1", SourceBinding("synthetic", "snapshot-1", "map-1", "input-1"), Coverage(1, 1, True), PriceUnit(4, "USD"), sampling="continuous" if kind == DataKind.QUOTE else "none")

def fixture(kind=DataKind.TRADE, rows=1):
    values = {"instrument_id": "A", "session_id": "S", "event_ns": 1_700_000_000_000_000_001, "order_key": 1, "event_id": "e1", "eligible": True, "start_ns": 1, "end_ns": 2, "reference_id": "r1", "fact_kind": "membership", "effective_start_ns": 1}
    return CanonicalBatch(kind, tuple(Column(f.name, (values[f.name],)*rows) for f in schema_for(kind).fields if f.required), replace(metadata(kind), coverage=Coverage(rows, rows, True)))

def append(batch, name, values):
    return replace(batch, columns=batch.columns+(Column(name, tuple(values)),))

class InputContracts(unittest.TestCase):
    def test_all_five_schemas(self):
        for kind in DataKind:
            with self.subTest(kind=kind):
                batch=fixture(kind)
                self.assertEqual(batch.row_count, 1)
                self.assertEqual(from_arrow(to_arrow(batch)), batch)
                self.assertEqual(from_numpy(kind, to_numpy(batch), batch.metadata), batch)
    def test_empty_observed_retains_metadata(self):
        empty=fixture(rows=0)
        self.assertEqual(empty.row_count,0)
        self.assertTrue(empty.metadata.coverage.complete)
        self.assertEqual(from_arrow(to_arrow(empty)),empty)
    def test_absent_null_zero_distinct(self):
        absent=fixture();null=append(absent,"price",[None]);zero=append(absent,"price",[0])
        self.assertIsNone(absent.column("price"))
        self.assertEqual(null.column("price").values,(None,))
        self.assertEqual(zero.column("price").values,(0,))
        for b in (absent,null,zero):
            self.assertEqual(from_arrow(to_arrow(b)),b)
            self.assertEqual(from_numpy(b.kind,to_numpy(b),b.metadata),b)
    def test_exact_timestamp_extremes(self):
        for value in (-(2**63),2**63-1,1_700_000_000_000_000_001):
            b=replace(fixture(),columns=tuple(Column(c.name,(value,)) if c.name=="event_ns" else c for c in fixture().columns))
            self.assertEqual(from_arrow(to_arrow(b)),b)
            self.assertEqual(from_numpy(b.kind,to_numpy(b),b.metadata),b)
    def test_int64_price_extremes(self):
        for value in (-(2**63),2**63-1):
            b=append(fixture(),"price",[value]);self.assertEqual(from_arrow(to_arrow(b)),b)
    def test_integer_overflow_rejected(self):
        for value in (-(2**63)-1,2**63,True,1.0,"100"):
            with self.subTest(value=value),self.assertRaises(ValueError):append(fixture(),"price",[value])
    def test_null_identity_rejected(self):
        with self.assertRaises(ValueError):replace(fixture(),columns=tuple(Column(c.name,(None,)) if c.name=="event_id" else c for c in fixture().columns))
    def test_missing_eligibility_rejected(self):
        with self.assertRaises(ValueError):replace(fixture(),columns=tuple(c for c in fixture().columns if c.name!="eligible"))
    def test_unknown_column_rejected(self):
        with self.assertRaises(ValueError):append(fixture(),"ticker",["A"])
    def test_duplicate_column_rejected(self):
        with self.assertRaises(ValueError):replace(fixture(),columns=fixture().columns+(fixture().columns[0],))
    def test_length_mismatch_rejected(self):
        with self.assertRaises(ValueError):append(fixture(),"price",[1,2])
    def test_wide_decimal_exact(self):
        for value in (10**38-1,-10**38+1):
            b=append(fixture(DataKind.BAR),"actual_notional",[value]);self.assertEqual(from_arrow(to_arrow(b)),b)
            with self.assertRaises(ValueError):to_numpy(b)
        with self.assertRaises(ValueError):append(fixture(DataKind.BAR),"actual_notional",[10**38])
    def test_arrow_wrong_time_unit(self):
        a=to_arrow(fixture());i=a.schema.get_field_index("event_ns")
        a=a.set_column(i,pa.field("event_ns",pa.timestamp("us",tz="UTC"),nullable=False),pa.array([1],type=pa.timestamp("us",tz="UTC")))
        with self.assertRaises(ValueError):from_arrow(a)
    def test_arrow_wrong_timezone(self):
        a=to_arrow(fixture());i=a.schema.get_field_index("event_ns")
        a=a.set_column(i,pa.field("event_ns",pa.timestamp("ns"),nullable=False),pa.array([1],type=pa.timestamp("ns")))
        with self.assertRaises(ValueError):from_arrow(a)
    def test_arrow_table_roundtrip(self):
        b=fixture();self.assertEqual(from_arrow(pa.Table.from_batches([to_arrow(b)])),b)
    def test_arrow_concrete_only(self):
        with self.assertRaises(ValueError):from_arrow(object())
        with self.assertRaises(ValueError):from_arrow(pa.record_batch([pa.array([1])],names=["price"]))
    def test_numpy_float_and_unsigned_rejected(self):
        for dtype in (np.float64,np.uint64):
            cols=to_numpy(fixture());cols["event_ns"]=(np.array([1],dtype=dtype),np.array([True]))
            with self.assertRaises(ValueError):from_numpy(DataKind.TRADE,cols,metadata())
    def test_numpy_bad_mask_rejected(self):
        cols=to_numpy(fixture());cols["event_ns"]=(np.array([1],dtype=np.int64),np.array([1],dtype=np.int64))
        with self.assertRaises(ValueError):from_numpy(DataKind.TRADE,cols,metadata())
    def test_owned_numpy_copy(self):
        b=fixture();cols=to_numpy(b);owned=from_numpy(b.kind,cols,b.metadata);cols["event_ns"][0][0]=0
        self.assertEqual(owned,b)
        self.assertEqual(b.column("event_ns").values,(1_700_000_000_000_000_001,))
    def test_column_detaches_list(self):
        values=[1];c=Column("price",values);values[0]=2;self.assertEqual(c.values,(1,))
    def test_lazy_iterable_never_executed(self):
        touched=[]
        def lazy():
            touched.append(True)
            yield 1
        with self.assertRaises(ValueError):Column("price",lazy())
        with self.assertRaises(ValueError):CanonicalBatch(DataKind.TRADE,lazy(),metadata())
        self.assertEqual(touched,[])
    def test_explicit_kind_and_typed_metadata(self):
        with self.assertRaises(ValueError):replace(fixture(),kind="trade")
        with self.assertRaises(ValueError):replace(metadata(),source={})
    def test_arrow_nullability_rejected(self):
        a=to_arrow(fixture());i=a.schema.get_field_index("event_ns")
        a=a.set_column(i,pa.field("event_ns",pa.timestamp("ns",tz="UTC"),nullable=True),a.column(i))
        with self.assertRaises(ValueError):from_arrow(a)
    def test_units_sampling_and_adjustment(self):
        for scale in (-1,19,True):
            with self.assertRaises(ValueError):PriceUnit(scale,"USD")
        with self.assertRaises(ValueError):replace(metadata(),sampling="mystery")
        with self.assertRaises(ValueError):replace(fixture(DataKind.QUOTE),metadata=metadata())
        with self.assertRaises(ValueError):replace(fixture(),metadata=replace(metadata(),price_unit=None))
        with self.assertRaises(ValueError):AdjustmentSpec("split")
        with self.assertRaises(ValueError):AdjustmentSpec("unknown")
        self.assertEqual(AdjustmentSpec("split","v1","actions-1","S").basis,"split")
    def test_source_and_coverage_requirements(self):
        with self.assertRaises(ValueError):SourceBinding("", "s", "m", "i")
        with self.assertRaises(ValueError):Coverage(None,0,True)
        with self.assertRaises(ValueError):Coverage(0,1,False)
        self.assertEqual(Coverage(None,0,False).expected,None)
    def test_quote_null_and_crossed_preserved(self):
        b=append(append(fixture(DataKind.QUOTE),"bid",[11]),"ask",[10])
        self.assertEqual(from_arrow(to_arrow(b)),b)
        self.assertEqual(from_arrow(to_arrow(append(fixture(DataKind.QUOTE),"bid",[None]))).column("bid").values,(None,))
    def test_known_at_null_preserved(self):
        b=append(fixture(),"known_at_ns",[None]);self.assertEqual(from_arrow(to_arrow(b)),b)
        self.assertEqual(schema_for(DataKind.TRADE).field("known_at_ns").dtype,DType.UTC_NS)

if __name__ == "__main__":unittest.main()
