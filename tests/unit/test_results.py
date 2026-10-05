"""Typed expected values and stable negative cases, no calculations claimed."""
from dataclasses import replace
from fractions import Fraction
import json
import unittest
import pyarrow as pa
from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, BreadthCounts, BreadthFraction,
    CanonicalBatch, Column, ConfigSpec, ContractError, Coverage, DataKind, EntityKey,
    ErrorCode, EvidenceRow, FeatureColumn, FeatureResult, InputBinding, PriceUnit,
    QualityRow, Reason, ResultMetadata, SourceBinding, Status, ValueType,
)
from equity_feature_contracts.columnar import from_arrow, from_numpy, to_arrow_result

ENTITY=EntityKey("A","S")

def meta():
    batch=BatchMetadata("demo",SourceBinding("synthetic","snapshot","map1","input1"),Coverage(1,1,True),PriceUnit(4,"USD"))
    return ResultMetadata("demo","S",AvailabilitySpec(200,210,210),"0"*64,(InputBinding("market",DataKind.TRADE,batch),),"caller:fixture","v1",2)

def result(value=0,status=Status.AVAILABLE,reason=(),dtype=ValueType.INT64,expected=1,observed=1):
    return FeatureResult((FeatureColumn("demo:count","v1",dtype,"shares",(ENTITY,),(value,)),), (QualityRow(ENTITY,"demo:count",status,expected,observed,reason),),meta())

def evidence(**changes):
    return replace(EvidenceRow(ENTITY,"demo:count","input1","row1",199,210),**changes)

class ResultContracts(unittest.TestCase):
    def assertCode(self,code,call):
        with self.assertRaises(ContractError) as caught:call()
        self.assertEqual(caught.exception.code,code)
    def test_available_observed_zero(self):
        r=result(0,expected=0,observed=0,reason=(Reason.OBSERVED_EMPTY,))
        self.assertEqual(r.values[0].values,(0,));self.assertEqual(r.quality[0].status,Status.AVAILABLE)
    def test_missing_is_null_not_zero(self):
        r=result(None,Status.MISSING_INPUT,(Reason.ABSENT_INPUT,),expected=None,observed=0)
        self.assertIsNone(r.values[0].values[0]);self.assertIsNone(r.quality[0].expected)
    def test_all_unavailable_statuses(self):
        for status,reason in ((Status.INSUFFICIENT_HISTORY,Reason.INSUFFICIENT_HISTORY),(Status.MISSING_INPUT,Reason.NULL_FIELD),(Status.INCOMPLETE_COVERAGE,Reason.GOVERNED_GAP),(Status.NOT_APPLICABLE,Reason.ZERO_DENOMINATOR)):
            with self.subTest(status=status):self.assertEqual(result(None,status,(reason,),expected=2,observed=1).quality[0].status,status)
    def test_unavailable_scalar_rejected(self):
        for status in Status:
            if status!=Status.AVAILABLE:self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:result(0,status,(Reason.ABSENT_INPUT,)))
    def test_available_null_rejected(self):
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:result(None))
    def test_status_requires_reason(self):
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:result(None,Status.MISSING_INPUT))
    def test_available_requires_declared_coverage(self):
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:result(1,expected=2,observed=1))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:result(1,expected=None))
    def test_partial_breadth_counts(self):
        value=BreadthCounts(1,1,1,4);r=result(value,Status.INCOMPLETE_COVERAGE,(Reason.PARTIAL_UNIVERSE,),ValueType.BREADTH_COUNTS,4,3)
        self.assertEqual(value.eligible,3);self.assertEqual(value.coverage,Fraction(3,4))
        self.assertEqual(r.values[0].values,(value,))
    def test_partial_breadth_fraction(self):
        value=BreadthFraction(1,3,4);r=result(value,Status.INCOMPLETE_COVERAGE,(Reason.PARTIAL_UNIVERSE,),ValueType.BREADTH_FRACTION,4,3)
        self.assertEqual(value.fraction,Fraction(1,3));self.assertEqual(value.coverage,Fraction(3,4))
        self.assertEqual(r.quality[0].observed,3)
    def test_breadth_complete_available(self):
        value=BreadthCounts(1,1,1,3);self.assertEqual(result(value,dtype=ValueType.BREADTH_COUNTS,expected=3,observed=3).values[0].values,(value,))
    def test_breadth_zero_eligible_is_null(self):
        self.assertCode(ErrorCode.BOUNDS,lambda:BreadthCounts(0,0,0,4))
        self.assertCode(ErrorCode.BOUNDS,lambda:BreadthFraction(0,0,4))
        self.assertIsNone(result(None,Status.INCOMPLETE_COVERAGE,(Reason.PARTIAL_UNIVERSE,),ValueType.BREADTH_COUNTS,4,0).values[0].values[0])
    def test_breadth_coverage_mismatch(self):
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:result(BreadthCounts(1,1,1,4),Status.INCOMPLETE_COVERAGE,(Reason.PARTIAL_UNIVERSE,),ValueType.BREADTH_COUNTS,4,2))
        self.assertCode(ErrorCode.BOUNDS,lambda:BreadthFraction(4,3,4))
    def test_independent_feature_quality(self):
        r=result();missing=FeatureColumn("demo:spread","v1",ValueType.FLOAT64,"bps",(ENTITY,),(None,))
        r=replace(r,values=r.values+(missing,),quality=r.quality+(QualityRow(ENTITY,"demo:spread",Status.MISSING_INPUT,None,0,(Reason.ABSENT_INPUT,)),))
        self.assertEqual(r.values[0].values,(0,));self.assertIsNone(r.values[1].values[0])
    def test_exact_scalar_types(self):
        for value,dtype in ((2**63-1,ValueType.INT64),(-(2**63),ValueType.INT64),(10**38-1,ValueType.DECIMAL128),(-10**38+1,ValueType.DECIMAL128),(0.0,ValueType.FLOAT64),(True,ValueType.BOOL),("value",ValueType.STRING)):
            self.assertEqual(result(value,dtype=dtype).values[0].values,(value,))
    def test_overflow_and_bool_integer(self):
        self.assertCode(ErrorCode.OVERFLOW,lambda:result(2**63))
        self.assertCode(ErrorCode.OVERFLOW,lambda:result(10**38,dtype=ValueType.DECIMAL128))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:result(True))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:result(1,dtype=ValueType.FLOAT64))
    def test_nonfinite_results_rejected(self):
        for value in (float("nan"),float("inf"),float("-inf")):
            self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:result(value,dtype=ValueType.FLOAT64))
    def test_key_alignment_and_duplicate(self):
        r=result()
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,quality=()))
        self.assertCode(ErrorCode.DUPLICATE,lambda:replace(r,quality=r.quality+r.quality))
        self.assertCode(ErrorCode.DUPLICATE,lambda:replace(r,values=r.values+r.values))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,metadata=replace(r.metadata,session_id="other")))
    def test_metadata_bindings(self):
        r=result();raw=json.loads(r.metadata_json());self.assertEqual(raw["metadata"]["inputs"][0]["metadata"]["source"]["snapshot_id"],"snapshot")
        self.assertEqual(raw["features"][0]["algorithm_version"],"v1");self.assertEqual(raw["metadata"]["availability"]["knowledge_cutoff_ns"],210)
        self.assertEqual(len(r.metadata.identity_digest),64)
    def test_identity_compatibility(self):
        r=result();r.require_same_identity(result(1))
        for other in (replace(r,metadata=replace(r.metadata,config_digest="1"*64)),replace(r,metadata=replace(r.metadata,backend_version="v2")),replace(r,values=(replace(r.values[0],algorithm_version="v2"),)),replace(r,metadata=replace(r.metadata,availability=AvailabilitySpec(200,209,210)))):
            self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:r.require_same_identity(other))
    def test_digest_and_namespace_binding_failures(self):
        m=meta();self.assertCode(ErrorCode.INVALID_CONFIG,lambda:replace(m,config_digest="not hash"))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(m,namespace="other"))
        self.assertCode(ErrorCode.DUPLICATE,lambda:replace(m,inputs=m.inputs+m.inputs))
        self.assertCode(ErrorCode.INCOMPATIBLE_VERSION,lambda:replace(m,schema_version="2"))
    def test_bound_evidence_with_exact_known_at(self):
        e=evidence();r=replace(result(),evidence=(e,));self.assertEqual(r.evidence[0].known_at_ns,210)
    def test_consumed_causal_unknown_future_rejected(self):
        for time in (None,211):self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(result(),evidence=(evidence(known_at_ns=time),)))
        self.assertCode(ErrorCode.BOUNDS,lambda:replace(result(),evidence=(evidence(event_ns=201),)))
    def test_excluded_unknown_future_preserved(self):
        for time,reason in ((None,Reason.UNKNOWN_AVAILABILITY),(211,Reason.FUTURE_KNOWLEDGE)):
            e=evidence(known_at_ns=time,use="excluded",exclusion_reason=reason)
            self.assertEqual(replace(result(),evidence=(e,)).evidence[0].known_at_ns,time)
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(result(),evidence=(evidence(use="excluded",exclusion_reason=Reason.FUTURE_KNOWLEDGE),)))
    def test_reconstruction_unknown_preserved(self):
        m=replace(meta(),availability=AvailabilitySpec(200,300,200,"reconstruction","caller revision"))
        r=replace(result(),metadata=m,evidence=(evidence(known_at_ns=None),));self.assertIsNone(r.evidence[0].known_at_ns)
    def test_evidence_bounds_and_identity(self):
        r=result();self.assertCode(ErrorCode.BOUNDS,lambda:replace(r,metadata=replace(r.metadata,evidence_limit=0),evidence=(evidence(),)))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,lambda:replace(r,evidence=(evidence(input_id="missing"),)))
        self.assertCode(ErrorCode.DUPLICATE,lambda:replace(r,evidence=(evidence(),evidence())))
        self.assertCode(ErrorCode.BOUNDS,lambda:evidence(event_ns=None))
    def test_result_ownership_and_no_lazy(self):
        r=result();values=list(r.values);copy=replace(r,values=values);values.clear();self.assertEqual(copy.values,r.values)
        def lazy():raise AssertionError("source executed");yield r.values[0]
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:replace(r,values=lazy()))
    def test_arrow_result_values_quality_evidence(self):
        r=replace(result(10**38-1,dtype=ValueType.DECIMAL128),evidence=(evidence(),))
        tables=to_arrow_result(r)
        self.assertEqual(int(tables["values"]["demo:count"]["value"][0].as_py()),10**38-1)
        self.assertEqual(tables["quality"]["status"].to_pylist(),["available"])
        self.assertEqual(tables["evidence"]["known_at_ns"].cast(pa.int64()).to_pylist(),[210])
        self.assertEqual(tables["evidence"].schema.metadata[b"equity.result"].decode(),r.metadata_json())
    def test_arrow_partial_breadth_and_empty_tables(self):
        r=result(BreadthFraction(1,3,4),Status.INCOMPLETE_COVERAGE,(Reason.PARTIAL_UNIVERSE,),ValueType.BREADTH_FRACTION,4,3)
        self.assertEqual(to_arrow_result(r)["values"]["demo:count"]["value"].to_pylist(),[{"above":1,"eligible":3,"expected":4}])
        empty=FeatureResult((),(),meta())
        tables=to_arrow_result(empty);self.assertEqual(tables["quality"].num_rows,0);self.assertEqual(tables["evidence"].num_rows,0)
    def test_empty_feature_column_and_malformed_numpy(self):
        empty=FeatureResult((FeatureColumn("demo:count","v1",ValueType.INT64,"count",(),()),),(),meta())
        self.assertEqual(to_arrow_result(empty)["values"]["demo:count"].schema.field("instrument_id").type,pa.string())
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:from_numpy(DataKind.TRADE,{"price":()},meta().inputs[0].metadata))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:Column([],()))
    def test_configuration_parse_has_stable_errors(self):
        self.assertCode(ErrorCode.INVALID_CONFIG,lambda:ConfigSpec.from_json("{"))
        from test_specs import config
        raw=json.loads(config().to_json());raw["parameters"]=[{"name":"p","value":{"float64":"not-hex"}}]
        self.assertCode(ErrorCode.INVALID_CONFIG,lambda:ConfigSpec.from_json(json.dumps(raw)))
    def test_market_evidence_boundary_exceptions(self):
        self.assertCode(ErrorCode.BOUNDS,lambda:replace(result(),evidence=(evidence(event_ns=200),)))
        closing=evidence(event_ns=200,boundary="closing_auction")
        self.assertEqual(replace(result(),evidence=(closing,)).evidence[0].boundary,"closing_auction")
        m=meta();quote=replace(m,inputs=(replace(m.inputs[0],kind=DataKind.QUOTE),))
        self.assertCode(ErrorCode.BOUNDS,lambda:replace(result(),metadata=quote,evidence=(closing,)))
        bar=replace(m,inputs=(replace(m.inputs[0],kind=DataKind.BAR),))
        self.assertEqual(replace(result(),metadata=bar,evidence=(evidence(event_ns=200,boundary="completed_interval"),)).evidence[0].event_ns,200)
    def test_existing_admission_typed_errors(self):
        self.assertCode(ErrorCode.INVALID_UNIT,lambda:PriceUnit(19,"USD"))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT,lambda:AdjustmentSpec("unsupported"))
        self.assertCode(ErrorCode.BOUNDS,lambda:AvailabilitySpec(True,0,0))
        b=BatchMetadata("demo",SourceBinding("s","snap","map","i"),Coverage(1,1,True),PriceUnit(4,"USD"))
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:CanonicalBatch(DataKind.TRADE,(),b))
        arrow=pa.record_batch([pa.array([1])],names=["price"])
        arrow=arrow.replace_schema_metadata({b"equity.inputs":b"invalid-json"})
        self.assertCode(ErrorCode.INVALID_SCHEMA,lambda:from_arrow(arrow))

if __name__ == "__main__":unittest.main()
