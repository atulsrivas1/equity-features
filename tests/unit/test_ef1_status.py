"""Hand-authored S01-S03 values and adversarial supplied-status declarations."""
from copy import deepcopy
from dataclasses import replace
import unittest

from equity_feature_contracts import (
    BatchMetadata, CanonicalBatch, Column, ContractError, Coverage, DataKind, ErrorCode,
    Reason, SourceBinding, Status, ValueType, builtin_registry,
)
from equity_features.ef1 import build_ef1_config, compute_ef1, decode_ef1_context, ef1_definitions
from test_ef1_clock import CALENDAR, ENTITY, config as clock_config, proof as calendar_proof, changed, view

S01 = (
    ("s1:t:ZQ:0000000000000000000:c2VlZA", "ef1.status.trading", 8, None, "active", 8),
    ("s1:t:ZQ:0000000000000000001:aGFsdA", "ef1.status.trading", 12, None, "halted", 12),
    ("s1:t:ZQ:0000000000000000002:cmVzdW1l", "ef1.status.trading", 16, None, "active", 16),
)
S02 = (("s1:s:ZQ:0000000000000000000:c2VlZA", "ef1.status.ssr", 5, None, "on", 5),)
S03 = (("s1:s:ZQ:0000000000000000000:YQ", "ef1.status.ssr", 5, None, "on", 5),
       ("s1:s:ZQ:0000000000000000001:Yg", "ef1.status.ssr", 5, None, "off", 5))


def config(cutoff=17, knowledge=None, *, dimension="trading", seed=S01[0][0], maximum=None, mode="known_at"):
    base = clock_config(cutoff, knowledge=cutoff if knowledge is None else knowledge)
    if mode == "reconstruction":
        base = replace(base, availability=replace(base.availability, mode=mode, reconstruction_reason="explicit supplied replay"))
    return build_ef1_config({"version": "ef1-context1", "producer": "status", "calendar": deepcopy(CALENDAR),
        "selection": {"dimension": dimension, "epoch": "e", "seed_reference_id": seed, "max_age_ns": maximum}},
        session=base.session, window=base.window, availability=base.availability,
        price_unit=None, adjustment=base.adjustment)


def reference(input_id, rows, *, complete=True):
    names = ("reference_id", "fact_kind", "effective_start_ns", "effective_end_ns", "text", "known_at_ns")
    data = {"instrument_id": ("X",) * len(rows), "session_id": ("S",) * len(rows)}
    data.update({name: tuple(row[i] for row in rows) for i, name in enumerate(names)})
    return CanonicalBatch(DataKind.REFERENCE, tuple(Column(k, v) for k, v in data.items()),
        BatchMetadata("SYN", SourceBinding("F", "R1", "ef1-reference-map1", input_id),
                      Coverage(len(rows) if complete else len(rows) + 1, len(rows), complete), None))


def inputs(*, rows=S01, dimension="t", prefix_end=20, validity_end=21):
    start = rows[0][2] if rows else 5
    return (calendar_proof(), reference("st", rows),
        reference("sp", (("p1:" + dimension + ":ZQ:c3Q:cHJlZg", "ef1.status.prefix_complete", start, prefix_end, dimension, 5),)),
        reference("sv", (("p1:" + dimension + ":ZQ:c3Q:dmFsaWQ", "ef1.status.validity", start, validity_end, dimension, 5),)))


class SuppliedStatus(unittest.TestCase):
    def error(self, code, call):
        with self.assertRaises(ContractError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)

    def check(self, result, dimension, state, age, reason="none", quality=None):
        self.assertEqual(view(result), {dimension + "_state": state, dimension + "_age_ns": age,
            "admission_state": "ready" if reason == "none" else "unavailable", "admission_reason": reason})
        assessments = [q for q in result.quality if q.feature_id.rsplit(".", 1)[1].startswith("admission_")]
        self.assertTrue(all(q.status == Status.AVAILABLE and (q.expected, q.observed, q.reasons) == (1, 1, ())
                            for q in assessments))
        if quality is not None:
            facts = [q for q in result.quality if q not in assessments]
            self.assertTrue(all((q.status, q.reasons) == quality for q in facts))

    def test_s01_literal_cutoff_and_causal_knowledge(self):
        for cutoff, knowledge, state, age, reason in ((16, 16, "halted", 4, "none"),
                (17, 17, "active", 1, "none"), (17, 15, None, None, "future_knowledge")):
            result = compute_ef1(inputs(), config(cutoff, knowledge), entity=ENTITY)
            self.check(result, "trading", state, age, reason)

    def test_s02_no_default_expiry_explicit_max_equality_and_prefix_endpoint(self):
        batches = inputs(rows=S02, dimension="s", prefix_end=16, validity_end=17)
        for cutoff, maximum, state, age, reason in ((16, None, "on", 11, "none"),
                (16, 10, None, 11, "stale_state"), (15, 10, "on", 10, "none"),
                (17, None, None, None, "incomplete_status_prefix")):
            result = compute_ef1(batches, config(cutoff, dimension="ssr", seed=S02[0][0], maximum=maximum), entity=ENTITY)
            self.check(result, "ssr", state, age, reason)
            if reason == "stale_state":
                facts = {q.feature_id.rsplit(".", 1)[1]: q for q in result.quality}
                self.assertEqual((facts["ssr_state"].status, facts["ssr_state"].reasons),
                                 (Status.MISSING_INPUT, (Reason.INELIGIBLE,)))
                self.assertEqual(facts["ssr_age_ns"].status, Status.AVAILABLE)
            elif reason == "incomplete_status_prefix":
                self.assertTrue(all(q.status == Status.INCOMPLETE_COVERAGE and q.reasons == (Reason.GOVERNED_GAP,)
                    for q in result.quality if not q.feature_id.rsplit(".", 1)[1].startswith("admission_")))
                self.assertEqual(result.evidence, ())
        self.check(compute_ef1(inputs(rows=S02, dimension="s", validity_end=17),
            config(17, dimension="ssr", seed=S02[0][0]), entity=ENTITY), "ssr", None, None,
            "outside_effective_interval", (Status.MISSING_INPUT, (Reason.INELIGIBLE,)))

    def test_s03_sequence_tie_and_duplicate_semantic_sequence(self):
        c = config(6, dimension="ssr", seed=S03[0][0])
        result = compute_ef1(inputs(rows=S03, dimension="s"), c, entity=ENTITY)
        self.check(result, "ssr", "off", 1)
        self.assertEqual({e.row_id for e in result.evidence}, {S03[1][0]})
        self.assertEqual(len(result.evidence), 2)
        bad = (S03[0], ("s1:s:ZQ:0000000000000000000:Yg",) + S03[1][1:])
        self.error(ErrorCode.DUPLICATE, lambda: compute_ef1(inputs(rows=bad, dimension="s"), c, entity=ENTITY))

    def test_required_earlier_unknown_transition_blocks_later_resume_in_all_modes(self):
        for mode in ("known_at", "reconstruction"):
            for known, reason in ((None, Reason.UNKNOWN_AVAILABILITY), (18, Reason.FUTURE_KNOWLEDGE)):
                rows = (S01[0], S01[1][:-1] + (known,), S01[2])
                result = compute_ef1(inputs(rows=rows), config(mode=mode), entity=ENTITY)
                self.check(result, "trading", None, None, reason.value, (Status.MISSING_INPUT, (reason,)))
                self.assertEqual(result.metadata.availability.mode, mode)

    def test_irrelevant_future_effective_event_does_not_need_knowledge(self):
        rows = S01[:2] + (S01[2][:-1] + (None,),)
        self.check(compute_ef1(inputs(rows=rows), config(16), entity=ENTITY), "trading", "halted", 4)

    def test_calendar_and_both_status_proofs_require_original_knowledge_in_reconstruction(self):
        for index in (0, 2, 3):
            for known, reason in ((None, Reason.UNKNOWN_AVAILABILITY), (18, Reason.FUTURE_KNOWLEDGE)):
                batches = list(inputs())
                batches[index] = changed(batches[index], known_at_ns=(known,))
                self.check(compute_ef1(batches, config(mode="reconstruction"), entity=ENTITY),
                    "trading", None, None, reason.value, (Status.MISSING_INPUT, (reason,)))

    def test_missing_seed_role_and_incomplete_population_do_not_infer_state(self):
        self.check(compute_ef1((None,) * 4, config(), entity=ENTITY), "trading", None, None, "absent_input")
        self.check(compute_ef1(inputs(), config(seed=None), entity=ENTITY), "trading", None, None, "absent_input")
        for index in range(4):
            batches = list(inputs())
            b = batches[index]
            batches[index] = replace(b, metadata=replace(b.metadata, coverage=Coverage(b.row_count + 1, b.row_count, False)))
            self.check(compute_ef1(batches, config(), entity=ENTITY), "trading", None, None,
                       "incomplete_status_prefix", (Status.INCOMPLETE_COVERAGE, (Reason.GOVERNED_GAP,)))

    def test_binding_identity_headers_and_recursive_detachment(self):
        c, batches = config(), inputs()
        result = compute_ef1(batches, c, entity=ENTITY)
        self.assertEqual(c.identity, "ef1.status")
        self.assertEqual(result.metadata.config_digest, c.digest)
        self.assertEqual(result.metadata.availability, c.availability)
        self.assertEqual(tuple(b.role for b in result.metadata.inputs),
            ("calendar_provenance", "status_prefix", "status_states", "status_validity"))
        self.assertEqual({b.role: b.metadata for b in result.metadata.inputs},
            dict(zip(("calendar_provenance", "status_states", "status_prefix", "status_validity"),
                     (b.metadata for b in batches))))
        definitions = ef1_definitions(c)
        self.assertEqual([(d.feature_id.rsplit(".", 1)[1], d.dtype, d.unit) for d in definitions],
            [("admission_reason", ValueType.STRING, "reason"), ("admission_state", ValueType.STRING, "state"),
             ("trading_age_ns", ValueType.INT64, "ns"), ("trading_state", ValueType.STRING, "state")])
        self.assertTrue(all(tuple(r.role for r in d.requirements) ==
            ("calendar_provenance", "status_states", "status_prefix", "status_validity") for d in definitions))
        with self.assertRaises(TypeError):
            decode_ef1_context(c)["calendar"]["sessions"][0][0] = "changed"
        self.assertEqual(len(builtin_registry().list_features()), 39)

    def test_b01_wrong_target_source_revision_and_mapping(self):
        for index, batch in ((2, changed(inputs()[2], reference_id=("p1:t:ZQ:b3RoZXI:cHJlZg",))),
                (2, replace(inputs()[2], metadata=replace(inputs()[2].metadata,
                    source=SourceBinding("OTHER", "R1", "ef1-reference-map1", "sp")))),
                (3, replace(inputs()[3], metadata=replace(inputs()[3].metadata,
                    source=SourceBinding("F", "R2", "ef1-reference-map1", "sv"))))):
            batches = list(inputs())
            batches[index] = batch
            self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(batches, config(), entity=ENTITY))

    def test_canonical_encoding_seq_epoch_text_and_role_order_controls(self):
        for reference_id in ("s1:t:ZQ:1:YQ", "s1:t:ZQ:-000000000000000001:YQ",
                "s1:t:ZQ:9223372036854775808:YQ", "s1:t:ZQ=:0000000000000000000:YQ",
                "s1:t:Zh:0000000000000000000:YQ", "s1:t:ZQ:0000000000000000000:_w"):
            rows = ((reference_id,) + S01[0][1:],)
            self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(inputs(rows=rows), config(), entity=ENTITY))
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(tuple(reversed(inputs())), config(), entity=ENTITY))
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(inputs() + inputs()[:1], config(), entity=ENTITY))
        self.error(ErrorCode.BOUNDS, lambda: config(maximum=-1))
        self.error(ErrorCode.BOUNDS, lambda: config(maximum=True))

    def test_quoting_is_an_independent_dimension_and_exact_four_header_set(self):
        rows = (("s1:q:ZQ:0000000000000000000:c2VlZA", "ef1.status.quoting", 5, None, "enabled", 5),)
        result = compute_ef1(inputs(rows=rows, dimension="q"),
            config(16, dimension="quoting", seed=rows[0][0]), entity=ENTITY)
        self.check(result, "quoting", "enabled", 11)
        self.assertFalse(any("trading" in c.feature_id or "ssr" in c.feature_id for c in result.values))

    def test_explicit_missing_and_typed_empty_role_slots_are_not_shifted(self):
        for index in range(4):
            batches = list(inputs())
            batches[index] = None
            self.check(compute_ef1(batches, config(), entity=ENTITY), "trading", None, None, "absent_input")
            batches[index] = reference(("cp", "st", "sp", "sv")[index], ())
            self.check(compute_ef1(batches, config(), entity=ENTITY), "trading", None, None, "absent_input")
        for invalid in ((), inputs()[:3], iter(inputs()), (None,) * 5):
            self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(invalid, config(), entity=ENTITY))

    def test_finite_state_expiry_nulls_state_and_age(self):
        rows = (S01[0][:3] + (17,) + S01[0][4:],)
        self.check(compute_ef1(inputs(rows=rows), config(17), entity=ENTITY), "trading", None, None,
                   "outside_effective_interval", (Status.MISSING_INPUT, (Reason.INELIGIBLE,)))

    def test_all_applicable_knowledge_reasons_survive_in_lexical_order(self):
        rows = (S01[0][:-1] + (None,), S01[1][:-1] + (18,), S01[2])
        self.check(compute_ef1(inputs(rows=rows), config(), entity=ENTITY), "trading", None, None,
            "unknown_availability", (Status.MISSING_INPUT, (Reason.FUTURE_KNOWLEDGE, Reason.UNKNOWN_AVAILABILITY)))

    def test_reference_work_bound_rejects_before_unbounded_preparation(self):
        batches = list(inputs())
        rows = tuple(("s1:t:ZQ:" + str(i).zfill(19) + ":YQ", "ef1.status.trading", 8, None, "active", 8)
                     for i in range(4097))
        batches[1] = reference("st", rows)
        self.error(ErrorCode.BOUNDS, lambda: compute_ef1(batches, config(), entity=ENTITY))

    def test_sequence_gaps_are_not_synthetic_missing_messages(self):
        rows = S01[:2] + (("s1:t:ZQ:0000000000000000009:cmVzdW1l",) + S01[2][1:],)
        self.check(compute_ef1(inputs(rows=rows), config(), entity=ENTITY), "trading", "active", 1)

    def test_no_interval_stitching_and_ambiguous_full_scope_proofs_reject(self):
        batches = list(inputs())
        batches[2] = reference("sp", (
            ("p1:t:ZQ:c3Q:YQ", "ef1.status.prefix_complete", 8, 12, "t", 8),
            ("p1:t:ZQ:c3Q:Yg", "ef1.status.prefix_complete", 12, 20, "t", 8)))
        self.check(compute_ef1(batches, config(), entity=ENTITY), "trading", None, None,
            "incomplete_status_prefix", (Status.INCOMPLETE_COVERAGE, (Reason.GOVERNED_GAP,)))
        batches[2] = reference("sp", (
            ("p1:t:ZQ:c3Q:YQ", "ef1.status.prefix_complete", 8, 20, "t", 8),
            ("p1:t:ZQ:c3Q:Yg", "ef1.status.prefix_complete", 8, 21, "t", 8)))
        self.error(ErrorCode.DUPLICATE, lambda: compute_ef1(batches, config(), entity=ENTITY))

    def test_context_seed_is_not_a_carrier_for_acquired_event_values(self):
        c = config()
        from equity_feature_contracts import Parameter
        text = c.parameters[0].value.replace('"max_age_ns":null', '"known_at_ns":8,"max_age_ns":null')
        self.error(ErrorCode.INVALID_CONFIG, lambda: decode_ef1_context(
            replace(c, parameters=(Parameter("ef1_context_json", text),))))

    def test_selected_original_witnesses_and_max_age_exclusion(self):
        for cutoff, known, identity, time in ((16, 16, S01[1][0], 12), (17, 17, S01[2][0], 16)):
            result = compute_ef1(inputs(), config(cutoff, known), entity=ENTITY)
            self.assertEqual(len(result.evidence), 2)
            for evidence in result.evidence:
                self.assertEqual((evidence.entity, evidence.input_id, evidence.row_id, evidence.event_ns,
                    evidence.known_at_ns, evidence.effective_start_ns, evidence.effective_end_ns,
                    evidence.use, evidence.exclusion_reason),
                    (ENTITY, "st", identity, time, time, time, None, "consumed", None))
            self.assertEqual({e.feature_id for e in result.evidence},
                {"session.status.trading_state", "session.status.trading_age_ns"})
        result = compute_ef1(inputs(rows=S02, dimension="s"),
            config(16, dimension="ssr", seed=S02[0][0], maximum=10), entity=ENTITY)
        witnesses = {e.feature_id.rsplit(".", 1)[1]: e for e in result.evidence}
        self.assertEqual((witnesses["ssr_state"].use, witnesses["ssr_state"].exclusion_reason),
                         ("excluded", Reason.INELIGIBLE))
        self.assertEqual((witnesses["ssr_age_ns"].use, witnesses["ssr_age_ns"].row_id,
            witnesses["ssr_age_ns"].event_ns), ("consumed", S02[0][0], 5))
        self.assertEqual(compute_ef1(inputs(), config(17, 15), entity=ENTITY).evidence, ())

    def test_all_dimensions_unknown_and_late_required_transition_in_each_mode(self):
        for dimension, code, texts in (("trading", "t", ("active", "halted")),
                ("quoting", "q", ("enabled", "disabled")), ("ssr", "s", ("on", "off"))):
            seed = "s1:" + code + ":ZQ:0000000000000000000:YQ"
            transition = "s1:" + code + ":ZQ:0000000000000000001:Yg"
            for mode in ("known_at", "reconstruction"):
                for knowledge, reason in ((None, Reason.UNKNOWN_AVAILABILITY), (18, Reason.FUTURE_KNOWLEDGE)):
                    rows = ((seed, "ef1.status." + dimension, 5, None, texts[0], 5),
                            (transition, "ef1.status." + dimension, 12, None, texts[1], knowledge))
                    result = compute_ef1(inputs(rows=rows, dimension=code),
                        config(dimension=dimension, seed=seed, mode=mode), entity=ENTITY)
                    self.check(result, dimension, None, None, reason.value, (Status.MISSING_INPUT, (reason,)))
                    self.assertEqual(result.evidence, ())

    def test_absent_states_still_require_coherent_actual_proof_declarations(self):
        batches = list(inputs())
        batches[1] = None
        self.check(compute_ef1(batches, config(), entity=ENTITY), "trading", None, None, "absent_input")
        for bad in (changed(inputs()[3], reference_id=("p1:t:ZQ:b3RoZXI:dmFsaWQ",)),
                replace(inputs()[3], metadata=replace(inputs()[3].metadata,
                    source=SourceBinding("OTHER", "R1", "ef1-reference-map1", "sv"))),
                replace(inputs()[3], metadata=replace(inputs()[3].metadata,
                    source=SourceBinding("F", "R2", "ef1-reference-map1", "sv")))):
            batches[3] = bad
            self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(batches, config(), entity=ENTITY))

    def test_wrong_populated_slots_and_late_overlapping_certificate_reject(self):
        batches = list(inputs())
        batches[1], batches[2] = batches[2], batches[1]
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(batches, config(), entity=ENTITY))
        batches = list(inputs())
        batches[3] = reference("sv", (
            ("p1:t:ZQ:c3Q:YQ", "ef1.status.validity", 8, 20, "t", 8),
            ("p1:t:ZQ:c3Q:Yg", "ef1.status.validity", 8, 21, "t", 18)))
        self.error(ErrorCode.DUPLICATE, lambda: compute_ef1(batches, config(), entity=ENTITY))
        # Wrong-target rows still reject when a prefix gap prevents semantic validity.
        batches = list(inputs(prefix_end=16))
        batches[3] = changed(batches[3], reference_id=("p1:t:ZQ:b3RoZXI:dmFsaWQ",))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(batches, config(), entity=ENTITY))

    def test_aggregate_reference_row_boundary_and_unknown_expected_population(self):
        for count in (4093, 4094):
            rows = (S01[0],) + tuple(("s1:t:ZQ:" + str(i).zfill(19) + ":YQ",
                "ef1.status.trading", 8, None, "active", 8) for i in range(1, count))
            if count == 4093:
                result = compute_ef1(inputs(rows=rows), config(), entity=ENTITY)
                self.check(result, "trading", "active", 9)
                self.assertTrue(all((q.expected, q.observed) == (4096, 4096)
                    for q in result.quality if not q.feature_id.rsplit(".", 1)[1].startswith("admission_")))
            else:
                self.error(ErrorCode.BOUNDS, lambda: compute_ef1(inputs(rows=rows), config(), entity=ENTITY))
        batches = list(inputs())
        batches[1] = replace(batches[1], metadata=replace(batches[1].metadata, coverage=Coverage(None, 3, False)))
        result = compute_ef1(batches, config(), entity=ENTITY)
        self.assertTrue(all(q.expected is None for q in result.quality
            if not q.feature_id.rsplit(".", 1)[1].startswith("admission_")))

    def test_age_overflow_is_typed(self):
        rows = (S01[0][:2] + (-(2**63), None, "active", -(2**63)),)
        self.error(ErrorCode.OVERFLOW, lambda: compute_ef1(inputs(rows=rows), config(), entity=ENTITY))

    def test_proved_prefix_preserves_independent_validity_knowledge_and_state_expiry(self):
        rows = (S01[0][:3] + (17,) + S01[0][4:],)
        batches = list(inputs(rows=rows))
        batches[3] = changed(batches[3], known_at_ns=(None,))
        self.check(compute_ef1(batches, config(), entity=ENTITY), "trading", None, None,
            "unknown_availability", (Status.MISSING_INPUT, (Reason.INELIGIBLE, Reason.UNKNOWN_AVAILABILITY)))

    def test_applicable_validity_knowledge_survives_unavailable_required_transition(self):
        # Independent S01 mutations: neither prerequisite failure may hide the
        # other original knowledge failure, including under reconstruction.
        for mode in ("known_at", "reconstruction"):
            for halt_known, validity_known in ((None, 18), (18, None)):
                rows = (S01[0], S01[1][:-1] + (halt_known,), S01[2])
                batches = list(inputs(rows=rows))
                batches[3] = changed(batches[3], known_at_ns=(validity_known,))
                result = compute_ef1(batches, config(mode=mode), entity=ENTITY)
                self.check(result, "trading", None, None, "unknown_availability",
                    (Status.MISSING_INPUT, (Reason.FUTURE_KNOWLEDGE, Reason.UNKNOWN_AVAILABILITY)))
                self.assertEqual(result.evidence, ())


if __name__ == "__main__":
    unittest.main()
