"""Independent boundary/timing and canonical identity fixtures."""
from dataclasses import replace
import json
import unittest
from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ConfigSpec, IntervalSpec, Parameter,
    PriceUnit, SessionSpec, WindowSpec,
)

def config():
    return ConfigSpec("synthetic:baseline", "v1", (Parameter("z", 1.5),Parameter("a", 20)),
        SessionSpec("demo", "S3", 100, 200, "caller-label", (IntervalSpec("opening",100,120),)),
        WindowSpec(2, "S3", ("S1","S2","S3","S4")), AvailabilitySpec(200,210,210), price_unit=PriceUnit(4,"USD"))

class SuppliedSpecifications(unittest.TestCase):
    def test_half_open_interval(self):
        x=IntervalSpec("open",100,120)
        self.assertTrue(x.contains(100));self.assertTrue(x.contains(119));self.assertFalse(x.contains(120))
    def test_exact_ns_extremes(self):
        x=IntervalSpec("wide",-(2**63),2**63-1)
        self.assertTrue(x.contains(2**63-2));self.assertFalse(x.contains(2**63-1))
    def test_bad_time_types_and_bounds(self):
        for bad in (True,1.0,2**63,-(2**63)-1):
            with self.subTest(bad=bad),self.assertRaises(ValueError):IntervalSpec("bad",bad,1)
        for end in (99,100):
            with self.assertRaises(ValueError):IntervalSpec("bad",100,end)
    def test_session_actual_early_close(self):
        s=SessionSpec("demo","S",100,150,"America/New_York",(IntervalSpec("closing",140,150),),200,True)
        self.assertTrue(s.early_close);self.assertEqual(s.close_ns,150)
        with self.assertRaises(ValueError):replace(s,intervals=(IntervalSpec("bad",140,151),))
    def test_early_close_evidence_required(self):
        s=config().session
        with self.assertRaises(ValueError):replace(s,early_close=True)
        with self.assertRaises(ValueError):replace(s,scheduled_close_ns=250)
        with self.assertRaises(ValueError):replace(s,scheduled_close_ns=199)
    def test_duplicate_interval_names(self):
        s=config().session
        with self.assertRaises(ValueError):replace(s,intervals=s.intervals+s.intervals)
    def test_no_timezone_discovery(self):
        self.assertEqual(replace(config().session,timezone_label="opaque-caller-zone").timezone_label,"opaque-caller-zone")
    def test_ordinary_cutoff_and_close(self):
        s=config().session
        self.assertTrue(s.admits_event(149,150));self.assertFalse(s.admits_event(150,150))
        self.assertFalse(s.admits_event(200,200));self.assertFalse(s.admits_event(200,210))
    def test_explicit_auction_rules(self):
        s=replace(config().session,include_opening_auction=True,include_closing_auction=True)
        self.assertTrue(s.admits_event(100,101,auction="opening"))
        self.assertTrue(s.admits_event(200,200,auction="closing"))
        self.assertFalse(s.admits_event(200,201,auction="closing"))
        self.assertFalse(config().session.admits_event(200,200,auction="closing"))
        self.assertFalse(s.admits_event(200,200,quote=True))
        with self.assertRaises(ValueError):s.admits_event(200,200,quote=True,auction="closing")
    def test_causal_cutoffs_inclusive(self):
        a=AvailabilitySpec(200,210,210)
        self.assertIsNone(a.knowledge_reason(210))
        self.assertEqual(a.knowledge_reason(211),"future_knowledge")
        self.assertEqual(a.knowledge_reason(None),"unknown_availability")
    def test_future_cutoffs_rejected(self):
        for c,k,e in ((201,200,200),(200,201,200)):
            with self.assertRaises(ValueError):AvailabilitySpec(c,k,e)
    def test_reconstruction_explicit_and_distinct(self):
        a=AvailabilitySpec(200,300,200,"reconstruction","later revision")
        self.assertIsNone(a.knowledge_reason(None));self.assertIsNone(a.knowledge_reason(400))
        c=replace(config(),availability=a)
        self.assertNotEqual(c.digest,config().digest)
        self.assertEqual(ConfigSpec.from_json(c.to_json()),c)
        with self.assertRaises(ValueError):AvailabilitySpec(200,300,200,"reconstruction")
        with self.assertRaises(ValueError):AvailabilitySpec(200,200,200,reconstruction_reason="not causal")
    def test_prior_only_governed_window(self):
        w=config().window
        self.assertEqual(w.selected_sessions(),("S1","S2"));self.assertTrue(w.history_complete)
    def test_completed_eod_window(self):
        self.assertEqual(replace(config().window,anchor="completed_eod").selected_sessions(),("S2","S3"))
    def test_insufficient_governed_history(self):
        w=replace(config().window,count=3)
        self.assertEqual(w.selected_sessions(),("S1","S2"));self.assertFalse(w.history_complete)
    def test_governed_missing_slot_retained(self):
        w=WindowSpec(2,"target",("first","missing","target"))
        self.assertEqual(w.selected_sessions(),("first","missing"))
    def test_bad_window(self):
        w=config().window
        for changes in ({"count":True},{"count":0},{"anchor":"calendar_days"},{"target_session_id":"unknown"},{"governed_sessions":("S3","S3")}):
            with self.subTest(changes=changes),self.assertRaises(ValueError):replace(w,**changes)
    def test_defensive_ownership(self):
        slots=["S1","S2"];w=WindowSpec(1,"S2",slots);slots[0]="mutated";self.assertEqual(w.selected_sessions(),("S1",))
        params=[Parameter("p",1)];c=replace(config(),parameters=params);params.clear();self.assertEqual(c.parameters,(Parameter("p",1),))
    def test_lazy_sequences_rejected_before_iteration(self):
        def lazy():raise AssertionError("source executed");yield "S3"
        with self.assertRaises(ValueError):WindowSpec(1,"S3",lazy())
        with self.assertRaises(ValueError):replace(config(),parameters=lazy())
    def test_parameter_admission(self):
        for bad in (float("nan"),float("inf"),float("-inf"),[],{}):
            with self.subTest(bad=bad),self.assertRaises(ValueError):Parameter("p",bad)
        with self.assertRaises(ValueError):replace(config(),parameters=(Parameter("p",1),Parameter("p",2)))
    def test_canonical_parameter_order(self):
        c=config();reverse=replace(c,parameters=tuple(reversed(c.parameters)))
        self.assertEqual(c.to_json(),reverse.to_json());self.assertEqual(c.digest,reverse.digest)
        self.assertEqual(json.loads(c.to_json())["parameters"],[{"name":"a","value":20},{"name":"z","value":{"float64":"0x1.8000000000000p+0"}}])
        self.assertEqual(c.digest,"d8ff9ddb56cf26be7e9550874f8891f4db5d3ee38ed3b6a7ac9a100a5fa9d8fc")
    def test_complete_round_trip(self):
        c=config();parsed=ConfigSpec.from_json(c.to_json())
        self.assertEqual(parsed.to_json(),c.to_json());self.assertEqual(parsed.digest,c.digest)
    def test_finite_float_signed_zero(self):
        for value in (-0.0,0.0,1.1,1e300,1e-300):
            c=replace(config(),parameters=(Parameter("p",value),));parsed=ConfigSpec.from_json(c.to_json())
            self.assertEqual(parsed.parameters[0].value.hex(),value.hex())
        self.assertNotEqual(replace(config(),parameters=(Parameter("p",-0.0),)).digest,replace(config(),parameters=(Parameter("p",0.0),)).digest)
    def test_digest_binds_every_identity(self):
        c=config()
        mutations=(replace(c,identity="other"),replace(c,algorithm_version="v2"),replace(c,session=replace(c.session,namespace="other")),replace(c,session=replace(c.session,close_ns=201)),replace(c,window=replace(c.window,count=1)),replace(c,availability=replace(c.availability,knowledge_cutoff_ns=209)),replace(c,adjustment=AdjustmentSpec("split","v1","actions","S3")),replace(c,price_unit=PriceUnit(3,"USD")),replace(c,parameters=(Parameter("a",21),)))
        for mutation in mutations:self.assertNotEqual(c.digest,mutation.digest)
    def test_target_mismatch_rejected(self):
        with self.assertRaises(ValueError):replace(config(),session=replace(config().session,session_id="other"))
    def test_unknown_versions_and_fields(self):
        c=config()
        for changes in ({"schema_version":"2"},{"unexpected":True}):
            raw=json.loads(c.to_json());raw.update(changes)
            with self.assertRaises(ValueError):ConfigSpec.from_json(json.dumps(raw))
        raw=json.loads(c.to_json());raw["session"]["unexpected"]=True
        with self.assertRaises(ValueError):ConfigSpec.from_json(json.dumps(raw))
    def test_json_duplicates_and_nonfinite(self):
        with self.assertRaises(ValueError):ConfigSpec.from_json('{"schema_version":"1","schema_version":"2"}')
        with self.assertRaises(ValueError):ConfigSpec.from_json('{"p":NaN}')
        raw=json.loads(config().to_json());raw["parameters"]=[{"name":"p","value":{"float64":"inf"}}]
        with self.assertRaises(ValueError):ConfigSpec.from_json(json.dumps(raw))

if __name__ == "__main__":unittest.main()
