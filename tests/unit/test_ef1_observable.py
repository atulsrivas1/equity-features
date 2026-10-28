"""Independent frozen full observable packets and adversarial admission controls.

The source JSON predates implementation. No output-generated oracle is used.
"""
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import unittest

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec,
    ContractError, Coverage, DataKind, EntityKey, ErrorCode, InputScope, IntervalCoverage,
    IntervalSpec, Parameter, PriceUnit, SessionSpec, SourceBinding, WindowSpec,
)
from equity_features.ef1 import build_ef1_config, compute_ef1, decode_ef1_context, ef1_definitions

SPEC_PATH = Path(__file__).resolve().parents[2] / "docs/ef1/OBSERVABLE_PUBLICATION_FIXTURES.json"
SPEC_BYTES = SPEC_PATH.read_bytes()
SPEC = json.loads(SPEC_BYTES)
PACKETS = {packet["id"]: packet for packet in SPEC["packets"]}


def configuration(packet):
    raw = packet["config"]
    session = dict(raw["session"])
    session["intervals"] = tuple(IntervalSpec(**row) for row in session["intervals"])
    window = dict(raw["window"])
    window["governed_sessions"] = tuple(window["governed_sessions"])
    return ConfigSpec(raw["identity"], raw["algorithm_version"],
        tuple(Parameter(**row) for row in raw["parameters"]), SessionSpec(**session), WindowSpec(**window),
        AvailabilitySpec(**raw["availability"]), AdjustmentSpec(**raw["adjustment"]),
        None if raw["price_unit"] is None else PriceUnit(**raw["price_unit"]), raw["schema_version"])


def metadata(raw):
    data = dict(raw)
    data["source"] = SourceBinding(**raw["source"])
    data["coverage"] = Coverage(**raw["coverage"])
    data["price_unit"] = None if raw["price_unit"] is None else PriceUnit(**raw["price_unit"])
    data["adjustment"] = AdjustmentSpec(**raw["adjustment"])
    data["scope"] = None if raw["scope"] is None else InputScope(**raw["scope"])
    data["interval_coverage"] = tuple(IntervalCoverage(row["name"], row["start_ns"], row["end_ns"],
                                                     Coverage(**row["coverage"])) for row in raw["interval_coverage"])
    return BatchMetadata(**data)


def inputs(packet):
    roles = SPEC["input_transport"]["slots"][packet["producer"]]
    supplied = {row["role"]: row["batch"] for row in packet["batches"]}
    if len(supplied) != len(packet["batches"]) or set(supplied) - set(roles):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "invalid packet role labels")
    return tuple(None if role not in supplied else CanonicalBatch(DataKind(supplied[role]["kind"]),
        tuple(Column(c["name"], tuple(c["values"])) for c in supplied[role]["columns"]),
        metadata(supplied[role]["metadata"])) for role in roles)


def projection(value):
    return json.loads(json.dumps(asdict(value), ensure_ascii=True))


def changed_batch(batch, **changes):
    return replace(batch, columns=tuple(Column(column.name, tuple(changes.get(column.name, column.values)))
                                       for column in batch.columns))


def empty_batch(batch):
    return replace(batch, columns=tuple(Column(column.name, ()) for column in batch.columns),
                   metadata=replace(batch.metadata, coverage=Coverage(0, 0, True)))


def evaluate(packet):
    config = configuration(packet)
    return compute_ef1(inputs(packet), config, entity=EntityKey(**packet.get("entity", {"instrument_id": "X", "session_id": config.session.session_id})))


def quality(result, name):
    return next(row for row in result.quality if row.feature_id.endswith("." + name))


def value(result, name):
    return next(row.values[0] for row in result.values if row.feature_id.endswith("." + name))


def canonical_mode(config, mode):
    return replace(config, availability=replace(config.availability, mode=mode,
        reconstruction_reason="explicit independent test" if mode == "reconstruction" else None))


class ObservablePackets(unittest.TestCase):
    def test_frozen_bytes(self):
        self.assertEqual(hashlib.sha256(SPEC_BYTES).hexdigest(), "8404a1871c7841abbca8551e6c6b31e52dc3c4fd0a16eefead826d38bac9c3aa")

    def test_packet_stage_accounting(self):
        self.assertEqual(sum(p.get("expected_result") is not None for p in PACKETS.values()),58)
        self.assertEqual(sum("expected_error" in p for p in PACKETS.values()),31)
        self.assertIsNotNone(PACKETS["X15-evidence-bound"]["candidate_result"])
        self.assertEqual(PACKETS["X13-task-byte-bound"]["expected_error"]["code"],"bounds")

    def test_error_admission_stages(self):
        for case,p in PACKETS.items():
            if "expected_error" not in p or case in ("X13-task-byte-bound","X15-evidence-bound"):
                continue
            if case=="X10-timestamp-int64-overflow":
                with self.assertRaises(ContractError) as caught:inputs(p)
                self.assertEqual(caught.exception.code,ErrorCode.OVERFLOW)
            else:
                configuration(p);inputs(p)  # All other28 refuse only at pure semantic admission.

    def test_public_builder_and_definitions(self):
        for p in PACKETS.values():
            if p.get("expected_result") is None:
                continue
            c=configuration(p)
            rebuilt=build_ef1_config(json.loads(c.parameters[0].value), session=c.session, window=c.window,
                availability=c.availability, price_unit=c.price_unit, adjustment=c.adjustment)
            self.assertEqual(c,rebuilt)
            self.assertEqual([d.feature_id for d in ef1_definitions(c)],[d["feature_id"] for d in p["expected_result"]["values"]])
            self.assertTrue(all(d.algorithm_version=="observable-v2" for d in ef1_definitions(c)))

    def test_all_missing_nullable_roles(self):
        for case in ("O01-first","H01-one-record-three-dimensions"):
            c=configuration(PACKETS[case]);r=compute_ef1((None,)*(5 if "status_history" in c.identity else 4),c,entity=EntityKey("X","S"))
            q=next(q for q in r.quality if not q.feature_id.endswith(("admission_reason","admission_state")))
            self.assertEqual((q.status,q.expected,q.observed,q.reasons),("missing_input",None,0,("absent_input",)))
            self.assertEqual(r.metadata.inputs,())

    def test_exact_nullable_transport(self):
        p=PACKETS["O01-first"];c=configuration(p);bs=inputs(p)
        for bad in (iter(bs),bs[:-1],(*bs,None),(*bs[:-1],object()),(bs[3],*bs[1:])):
            with self.subTest(container=type(bad).__name__),self.assertRaises(ContractError) as caught:
                compute_ef1(bad,c,entity=EntityKey("X","S"))
            self.assertEqual(caught.exception.code,ErrorCode.INVALID_SCHEMA)

    def test_duplicate_unknown_wrapper_labels(self):
        for role in ("calendar_provenance","unknown"):
            p=deepcopy(PACKETS["O01-first"]);p["batches"].append({"role":role,"batch":p["batches"][0]["batch"]})
            with self.assertRaises(ContractError) as caught: inputs(p)
            self.assertEqual(caught.exception.code,ErrorCode.INVALID_SCHEMA)

    def test_population_metadata_observed_is_actual(self):
        p=PACKETS["H01-one-record-three-dimensions"];bs=list(inputs(p));bs[1]=replace(bs[1],metadata=replace(bs[1].metadata,coverage=Coverage(2,2,True)))
        with self.assertRaises(ContractError) as caught: compute_ef1(tuple(bs),configuration(p),entity=EntityKey("X","S"))
        self.assertEqual(caught.exception.code,ErrorCode.INCONSISTENT_IDENTITY)

    def test_wrong_family_proof(self):
        p=PACKETS["O01-first"];bs=list(inputs(p));bs[1]=changed_batch(bs[1],fact_kind=("ef1.observable.history_prefix",))
        with self.assertRaises(ContractError) as caught: compute_ef1(tuple(bs),configuration(p),entity=EntityKey("X","S"))
        self.assertEqual(caught.exception.code,ErrorCode.INVALID_SCHEMA)

    def test_history_knowledge_strict_in_both_modes(self):
        p=PACKETS["H01-one-record-three-dimensions"]
        for mode in ("known_at","reconstruction"):
            for stamp,reason in ((None,"unknown_availability"),(21,"future_knowledge")):
                c=canonical_mode(configuration(p),mode);bs=list(inputs(p));bs[1]=changed_batch(bs[1],known_at_ns=(stamp,))
                r=compute_ef1(tuple(bs),c,entity=EntityKey("X","S"))
                for name in ("event_count","halt_observed","resume_observed","ssr_on_observed"):
                    self.assertIsNone(value(r,name));self.assertIn(reason,quality(r,name).reasons)
                self.assertFalse(any(e.input_id==bs[1].metadata.source.input_id for e in r.evidence))

    def test_history_proofs_strict_in_both_modes(self):
        p=PACKETS["H01-one-record-three-dimensions"]
        for mode in ("known_at","reconstruction"):
            for slot in (0,2,4):
                c=canonical_mode(configuration(p),mode);bs=list(inputs(p));bs[slot]=changed_batch(bs[slot],known_at_ns=(21,))
                r=compute_ef1(tuple(bs),c,entity=EntityKey("X","S"))
                self.assertIsNone(value(r,"event_count"));self.assertIn("future_knowledge",quality(r,"event_count").reasons)
                self.assertFalse(any(e.input_id==bs[slot].metadata.source.input_id for e in r.evidence))

    def test_seed_knowledge_only_dependent_resume(self):
        p=PACKETS["H13-seed-derived-resume"]
        for mode in ("known_at","reconstruction"):
            for stamp,reason in ((None,"unknown_availability"),(21,"future_knowledge")):
                c=canonical_mode(configuration(p),mode);bs=list(inputs(p));bs[3]=changed_batch(bs[3],known_at_ns=(stamp,))
                r=compute_ef1(tuple(bs),c,entity=EntityKey("X","S"))
                self.assertEqual(value(r,"event_count"),1);self.assertEqual(value(r,"halt_observed"),False)
                self.assertIsNone(value(r,"resume_observed"));self.assertIn(reason,quality(r,"resume_observed").reasons)
                self.assertFalse(any(e.input_id==bs[3].metadata.source.input_id for e in r.evidence))

    def test_count_checked_addition(self):
        p=PACKETS["H06-complete-empty-no-seed"];bs=list(inputs(p));bs[2]=changed_batch(bs[2],text=("pv2~9223372036854775807~partial",))
        with self.assertRaises(ContractError) as caught: compute_ef1(tuple(bs),configuration(p),entity=EntityKey("X","S"))
        self.assertEqual(caught.exception.code,ErrorCode.OVERFLOW)

    def test_independent_outputs_and_initial_relation(self):
        for case,count,halt,resume,ssr in (("H02-initial-not-resume",1,False,False,False),("H03-explicit-resume-no-seed",1,False,True,False),
                ("H04-local-pair-no-seed",2,True,True,False),("H09-ssr-unknown-independent",1,False,False,None),
                ("H08-ssr-on-then-off",2,False,False,True)):
            r=evaluate(PACKETS[case]);self.assertEqual(tuple(value(r,n) for n in ("event_count","halt_observed","resume_observed","ssr_on_observed")),(count,halt,resume,ssr))

    def test_unknown_action_without_active_is_not_resume(self):
        p=PACKETS["H03-explicit-resume-no-seed"];bs=list(inputs(p));c=configuration(p)
        bs[1]=changed_batch(bs[1],text=("ov2~65535~00000~00000~--~--~--~u",))
        r=compute_ef1(tuple(bs),c,entity=EntityKey("X","S"))
        self.assertEqual(value(r,"event_count"),1);self.assertFalse(value(r,"halt_observed"));self.assertFalse(value(r,"resume_observed"))
        self.assertIsNone(value(r,"ssr_on_observed"))

    def test_unknown_action_does_not_erase_explicit_positive(self):
        p=PACKETS["H08-ssr-on-then-off"];bs=list(inputs(p));c=configuration(p)
        bs[1]=changed_batch(bs[1],text=("ov2~00004~00000~00000~--~--~--~u","ov2~65535~00000~00000~--~--~--~u"))
        action_map=dict(json.loads(c.parameters[0].value)["selection"]["action_map"])
        explicit=next(raw for raw,meaning in action_map.items() if meaning=="resume")
        bs[1]=changed_batch(bs[1],text=(f"ov2~{explicit:05d}~00000~00000~--~--~--~u","ov2~65535~00000~00000~--~--~--~u"))
        r=compute_ef1(tuple(bs),c,entity=EntityKey("X","S"))
        self.assertEqual(value(r,"event_count"),2);self.assertTrue(value(r,"resume_observed"))
        self.assertEqual(quality(r,"resume_observed").status,"available")

    def test_unneeded_seed_does_not_affect_independent_outputs(self):
        p=PACKETS["H13-seed-derived-resume"];bs=list(inputs(p));c=configuration(p)
        bs[1]=changed_batch(bs[1],text=("ov2~00001~00000~00000~--~--~30~u",))
        bs[3]=changed_batch(bs[3],known_at_ns=(21,))
        r=compute_ef1(tuple(bs),c,entity=EntityKey("X","S"))
        self.assertEqual(value(r,"event_count"),1);self.assertTrue(value(r,"halt_observed"))
        self.assertFalse(value(r,"resume_observed"));self.assertEqual(quality(r,"resume_observed").status,"available")

    def test_irrelevant_prefix_retains_missing_boundary_seed_dependency(self):
        p=PACKETS["H08-ssr-on-then-off"]
        for mode in ("known_at","reconstruction"):
            bs=list(inputs(p));c=canonical_mode(configuration(p),mode)
            bs[1]=changed_batch(bs[1],text=("ov2~00005~00000~00000~--~--~30~u","ov2~00002~00000~00000~--~--~30~u"))
            r=compute_ef1(tuple(bs),c,entity=EntityKey("X","S"));q=quality(r,"resume_observed")
            self.assertEqual((q.status,q.expected,q.observed,q.reasons),("missing_input",6,5,("missing_action_evidence",)))
            self.assertIsNone(value(r,"resume_observed"));self.assertEqual(value(r,"event_count"),2)
            self.assertEqual((quality(r,"event_count").expected,quality(r,"event_count").observed),(5,5))
            self.assertEqual({e.input_id for e in r.evidence if e.feature_id.endswith(".resume_observed")},{"calendar","capability","prefix"})

    def test_unknown_prefix_resets_boundary_seed_dependency(self):
        p=PACKETS["H08-ssr-on-then-off"]
        for mode in ("known_at","reconstruction"):
            for seed in (None,inputs(PACKETS["H13-seed-derived-resume"])[3]):
                bs=list(inputs(p));c=canonical_mode(configuration(p),mode);bs[3]=seed
                bs[1]=changed_batch(bs[1],text=("ov2~65535~00000~00000~--~--~30~u","ov2~00002~00000~00000~--~--~30~u"))
                r=compute_ef1(tuple(bs),c,entity=EntityKey("X","S"));q=quality(r,"resume_observed")
                self.assertEqual((q.status,q.expected,q.observed,q.reasons),("missing_input",5,5,("missing_action_evidence",)))
                self.assertIsNone(value(r,"resume_observed"))
                self.assertFalse(any(e.input_id=="seed" for e in r.evidence))

    def test_irrelevant_prefix_seed_payload_and_knowledge_dependencies(self):
        p=PACKETS["H08-ssr-on-then-off"];seed=inputs(PACKETS["H13-seed-derived-resume"])[3]
        for mode in ("known_at","reconstruction"):
            for state,known,want,observed,reasons in (("clear",1,False,6,()),("interrupted",1,True,6,()),
                    ("unknown",1,None,6,("missing_action_evidence",)),
                    ("interrupted",None,None,5,("missing_action_evidence","unknown_availability")),
                    ("interrupted",21,None,5,("future_knowledge","missing_action_evidence"))):
                bs=list(inputs(p));c=canonical_mode(configuration(p),mode)
                bs[1]=changed_batch(bs[1],text=("ov2~00005~00000~00000~--~--~30~u","ov2~00002~00000~00000~--~--~30~u"))
                bs[3]=changed_batch(seed,text=(state,),known_at_ns=(known,))
                r=compute_ef1(tuple(bs),c,entity=EntityKey("X","S"));q=quality(r,"resume_observed")
                self.assertEqual(value(r,"resume_observed"),want)
                self.assertEqual((q.expected,q.observed,q.reasons),(6,observed,reasons))
                self.assertEqual(value(r,"event_count"),2);self.assertEqual(quality(r,"event_count").status,"available")
                self.assertEqual((quality(r,"event_count").expected,quality(r,"event_count").observed),(5,5))
                self.assertFalse(any(e.known_at_ns is None or e.known_at_ns>20 for e in r.evidence))

    def test_missing_known_at_column_is_unknown(self):
        p=PACKETS["O01-first"];bs=list(inputs(p));c=configuration(p)
        bs[3]=replace(bs[3],columns=tuple(col for col in bs[3].columns if col.name!="known_at_ns"))
        r=compute_ef1(tuple(bs),c,entity=EntityKey("X","S"))
        self.assertIsNone(value(r,"observed"));self.assertIn("unknown_availability",quality(r,"observed").reasons)

    def test_unknown_config_fields_and_legacy_version_refused(self):
        p=PACKETS["O01-first"];c=configuration(p);raw=json.loads(c.parameters[0].value)
        for key,datum in (("unknown",True),("version","ef1-context1")):
            context=deepcopy(raw);context[key]=datum
            changed=replace(c,parameters=(Parameter("ef1_context_json",json.dumps(context,sort_keys=True,separators=(",",":"))),))
            with self.assertRaises(ContractError):decode_ef1_context(changed)

    def test_false_prefix_hash_stays_false(self):
        p=PACKETS["E16-false-prefix-target"]
        self.assertIn("0"*64,next(c["values"][0] for b in p["batches"] if b["role"]=="market_prefix" for c in b["batch"]["columns"] if c["name"]=="reference_id"))

    def test_zero_prefix_identical_empty_roles(self):
        one=PACKETS["T01-zero-prefix-empty-market-prefix-refusal"];two=PACKETS["T02-zero-prefix-empty-source-capability-retained"]
        self.assertEqual(one["batches"][1]["batch"],two["batches"][1]["batch"])
        with self.assertRaises(ContractError) as caught:evaluate(one)
        self.assertEqual(caught.exception.code,ErrorCode.BOUNDS)
        self.assertEqual(projection(evaluate(two)),two["expected_result"])


def make_success(case):
    def test(self):
        p=deepcopy(PACKETS[case]);before=deepcopy(p)
        result=evaluate(p)
        self.assertEqual(projection(result),p["expected_result"])
        self.assertEqual(projection(evaluate(p)),p["expected_result"])
        self.assertEqual(p,before)
    return test


def make_error(case):
    def test(self):
        p=deepcopy(PACKETS[case])
        with self.assertRaises(ContractError) as caught:evaluate(p)
        self.assertEqual(caught.exception.code.value,p["expected_error"]["code"])
    return test


for _case,_packet in PACKETS.items():
    if _packet.get("expected_result") is not None:
        setattr(ObservablePackets,"test_packet_"+_case.replace("-","_"),make_success(_case))
    elif _case not in ("X13-task-byte-bound","X15-evidence-bound"):
        setattr(ObservablePackets,"test_refusal_"+_case.replace("-","_"),make_error(_case))

if __name__ == "__main__":unittest.main()
