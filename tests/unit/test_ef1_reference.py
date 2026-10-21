"""Independent frozen full reference packets and adversarial admission controls.

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

SPEC_PATH = Path(__file__).resolve().parents[2] / "docs/ef1/REFERENCE_CONTRACT_PROPOSAL.json"
SPEC_BYTES = SPEC_PATH.read_bytes()
SPEC = json.loads(SPEC_BYTES)
PACKETS = {packet["id"]: packet for packet in SPEC["canonical_literal_packets"]}


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
    return tuple(None if row["batch"] is None else CanonicalBatch(DataKind(row["batch"]["kind"]),
        tuple(Column(column["name"], tuple(column["values"])) for column in row["batch"]["columns"]),
        metadata(row["batch"]["metadata"])) for row in packet["role_slots"])


def projection(value):
    return json.loads(json.dumps(asdict(value), ensure_ascii=True))


def changed_batch(batch, **changes):
    return replace(batch, columns=tuple(Column(column.name, tuple(changes.get(column.name, column.values)))
                                       for column in batch.columns))


def empty_batch(batch):
    return replace(batch, columns=tuple(Column(column.name, ()) for column in batch.columns),
                   metadata=replace(batch.metadata, coverage=Coverage(0, 0, True)))


def packet(case="R01-CANONICAL"):
    return deepcopy(PACKETS[case])


def evaluate(source):
    return compute_ef1(inputs(source), configuration(source), entity=EntityKey(**source["entity"]))


class ReferencePackets(unittest.TestCase):
    def assert_packet(self, case):
        source = packet(case)
        original = deepcopy(source)
        config = configuration(source)
        self.assertEqual(config.to_json(), source["canonical_config_json"])
        self.assertEqual(config.digest, source["config_digest"])
        selection = json.loads(config.parameters[0].value)
        rebuilt = build_ef1_config(selection, session=config.session, window=config.window,
            availability=config.availability, price_unit=config.price_unit, adjustment=config.adjustment)
        self.assertEqual(rebuilt, config)
        actual_inputs = inputs(source)
        before = tuple(None if batch is None else projection(batch) for batch in actual_inputs)
        result = compute_ef1(actual_inputs, config, entity=EntityKey(**source["entity"]))
        self.assertEqual(projection(result), source["expected_result"])
        self.assertEqual(tuple(None if batch is None else projection(batch) for batch in actual_inputs), before)
        self.assertEqual(source, original)
        self.assertEqual(projection(compute_ef1(actual_inputs, config, entity=EntityKey(**source["entity"]))),
                         source["expected_result"])

    def error(self, code, call):
        with self.assertRaises(ContractError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)

    def test_frozen_packet_population_and_source_identity(self):
        self.assertEqual(len(PACKETS), 55)
        self.assertEqual(len(SPEC["negative_controls"]), 42)
        self.assertEqual(hashlib.sha256(SPEC_BYTES).hexdigest(),
                         "5160d91fc966137a1728c6c26dde15d6772ea35811efc4ea9832b2f7460a28f0")
    def test_packet_r01_canonical(self):
        self.assert_packet("R01-CANONICAL")

    def test_packet_r02_canonical(self):
        self.assert_packet("R02-CANONICAL")

    def test_packet_r01_late_proof_known_at(self):
        self.assert_packet("R01-late_proof-known_at")

    def test_packet_r01_null_proof_known_at(self):
        self.assert_packet("R01-null_proof-known_at")

    def test_packet_r01_blank_text_known_at(self):
        self.assert_packet("R01-blank_text-known_at")

    def test_packet_r01_partial_projection_known_at(self):
        self.assert_packet("R01-partial_projection-known_at")

    def test_packet_r01_current_only_known_at(self):
        self.assert_packet("R01-current_only-known_at")

    def test_packet_r01_late_proof_reconstruction(self):
        self.assert_packet("R01-late_proof-reconstruction")

    def test_packet_r01_null_proof_reconstruction(self):
        self.assert_packet("R01-null_proof-reconstruction")

    def test_packet_r01_blank_text_reconstruction(self):
        self.assert_packet("R01-blank_text-reconstruction")

    def test_packet_r01_partial_projection_reconstruction(self):
        self.assert_packet("R01-partial_projection-reconstruction")

    def test_packet_r01_current_only_reconstruction(self):
        self.assert_packet("R01-current_only-reconstruction")

    def test_packet_r01_missing_projection(self):
        self.assert_packet("R01-MISSING-PROJECTION")

    def test_packet_industry_canonical(self):
        self.assert_packet("INDUSTRY-CANONICAL")

    def test_packet_r03_canonical(self):
        self.assert_packet("R03-CANONICAL")

    def test_packet_action_late_proof_known_at(self):
        self.assert_packet("ACTION-late_proof-known_at")

    def test_packet_action_null_proof_known_at(self):
        self.assert_packet("ACTION-null_proof-known_at")

    def test_packet_action_source_policy_mismatch_known_at(self):
        self.assert_packet("ACTION-source_policy_mismatch-known_at")

    def test_packet_action_late_market_known_at(self):
        self.assert_packet("ACTION-late_market-known_at")

    def test_packet_action_null_market_known_at(self):
        self.assert_packet("ACTION-null_market-known_at")

    def test_packet_action_incomplete_market_known_at(self):
        self.assert_packet("ACTION-incomplete_market-known_at")

    def test_packet_action_missing_market_known_at(self):
        self.assert_packet("ACTION-missing_market-known_at")

    def test_packet_action_revision_mismatch_known_at(self):
        self.assert_packet("ACTION-revision_mismatch-known_at")

    def test_packet_action_late_factor_known_at(self):
        self.assert_packet("ACTION-late_factor-known_at")

    def test_packet_action_zero_actions_known_at(self):
        self.assert_packet("ACTION-zero_actions-known_at")

    def test_packet_action_late_proof_reconstruction(self):
        self.assert_packet("ACTION-late_proof-reconstruction")

    def test_packet_action_null_proof_reconstruction(self):
        self.assert_packet("ACTION-null_proof-reconstruction")

    def test_packet_action_source_policy_mismatch_reconstruction(self):
        self.assert_packet("ACTION-source_policy_mismatch-reconstruction")

    def test_packet_action_late_market_reconstruction(self):
        self.assert_packet("ACTION-late_market-reconstruction")

    def test_packet_action_null_market_reconstruction(self):
        self.assert_packet("ACTION-null_market-reconstruction")

    def test_packet_action_incomplete_market_reconstruction(self):
        self.assert_packet("ACTION-incomplete_market-reconstruction")

    def test_packet_action_missing_market_reconstruction(self):
        self.assert_packet("ACTION-missing_market-reconstruction")

    def test_packet_action_revision_mismatch_reconstruction(self):
        self.assert_packet("ACTION-revision_mismatch-reconstruction")

    def test_packet_action_late_factor_reconstruction(self):
        self.assert_packet("ACTION-late_factor-reconstruction")

    def test_packet_action_zero_actions_reconstruction(self):
        self.assert_packet("ACTION-zero_actions-reconstruction")

    def test_packet_class_late_fact_null_proof_known_at(self):
        self.assert_packet("CLASS-LATE-FACT-NULL-PROOF-known_at")

    def test_packet_class_late_fact_null_proof_reconstruction(self):
        self.assert_packet("CLASS-LATE-FACT-NULL-PROOF-reconstruction")

    def test_packet_class_expired_proof(self):
        self.assert_packet("CLASS-EXPIRED-PROOF")

    def test_packet_r03_caller_quantity_mismatch(self):
        self.assert_packet("R03-caller_quantity_mismatch")

    def test_packet_r03_caller_transformed_pass(self):
        self.assert_packet("R03-caller_transformed_pass")

    def test_packet_action_numeric_fields_absent_gate_only(self):
        self.assert_packet("ACTION-NUMERIC-FIELDS-ABSENT-GATE-ONLY")

    def test_packet_action_two_factor_cap12(self):
        self.assert_packet("ACTION-TWO-FACTOR-CAP12")

    def test_packet_universe_canonical(self):
        self.assert_packet("UNIVERSE-CANONICAL")

    def test_packet_r02_unknown_expected(self):
        self.assert_packet("R02-unknown_expected")

    def test_packet_r02_missing_facts(self):
        self.assert_packet("R02-missing_facts")

    def test_packet_raw_actual_r1_empty_known_at(self):
        self.assert_packet("RAW-ACTUAL-R1-empty-known_at")

    def test_packet_raw_actual_r1_factor_known_at(self):
        self.assert_packet("RAW-ACTUAL-R1-factor-known_at")

    def test_packet_raw_actual_r1_late_factor_known_at(self):
        self.assert_packet("RAW-ACTUAL-R1-late_factor-known_at")

    def test_packet_class_blank_plus_partial_projection_known_at(self):
        self.assert_packet("CLASS-BLANK-PLUS-PARTIAL-PROJECTION-known_at")

    def test_packet_raw_actual_r1_empty_reconstruction(self):
        self.assert_packet("RAW-ACTUAL-R1-empty-reconstruction")

    def test_packet_raw_actual_r1_factor_reconstruction(self):
        self.assert_packet("RAW-ACTUAL-R1-factor-reconstruction")

    def test_packet_raw_actual_r1_late_factor_reconstruction(self):
        self.assert_packet("RAW-ACTUAL-R1-late_factor-reconstruction")

    def test_packet_class_blank_plus_partial_projection_reconstruction(self):
        self.assert_packet("CLASS-BLANK-PLUS-PARTIAL-PROJECTION-reconstruction")

    def test_packet_class_blank_plus_incomplete_history_known_at(self):
        self.assert_packet("CLASS-BLANK-PLUS-INCOMPLETE-HISTORY-known_at")

    def test_packet_class_blank_plus_incomplete_history_reconstruction(self):
        self.assert_packet("CLASS-BLANK-PLUS-INCOMPLETE-HISTORY-reconstruction")

    def test_discovery_complete_action_market_alternatives(self):
        definitions = ef1_definitions(configuration(packet("R03-CANONICAL")))
        self.assertEqual(tuple(row.feature_id for row in definitions),
                         ("reference.gate.action_reason", "reference.gate.action_state"))
        for definition in definitions:
            self.assertEqual(len(definition.requirements), 5)
            self.assertNotIn("market", tuple(row.role for row in definition.requirements))
            self.assertEqual(len(definition.alternative_requirements), 3)
            self.assertEqual(tuple(rows[0].kind for rows in definition.alternative_requirements),
                             (DataKind.TRADE, DataKind.BAR, DataKind.DAILY))
            for rows in definition.alternative_requirements:
                self.assertEqual(tuple(row.role for row in rows),
                    ("market", "action_facts", "action_history", "action_projection", "source_representation", "source_quantity_basis"))
                self.assertEqual(rows[1:], definition.requirements)
                self.assertTrue(definition.capabilities.batch)
                self.assertFalse(definition.capabilities.update or definition.capabilities.restore or definition.capabilities.merge)

    def test_classification_discovery_has_no_alternatives(self):
        for definition in ef1_definitions(configuration(packet())):
            self.assertEqual(tuple(row.role for row in definition.requirements),
                             ("classification_facts", "classification_history", "classification_projection"))
            self.assertEqual(definition.alternative_requirements, ())

    def test_exact_nullable_slot_count(self):
        source = packet()
        config = configuration(source)
        batches = inputs(source)
        for wrong in ((), batches[:2], (*batches, None), iter(batches), (batches[0], object(), batches[2])):
            self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(wrong, config, entity=EntityKey("X", "S")))

    def test_all_absent_slots_preserve_absence(self):
        source = packet()
        result = compute_ef1((None, None, None), configuration(source), entity=EntityKey("X", "S"))
        self.assertEqual(result.metadata.inputs, ())
        self.assertEqual(result.evidence, ())
        self.assertEqual(result.quality[0].expected, None)
        self.assertEqual(result.quality[0].observed, 0)
        self.assertEqual(result.values[-1].values, ("unknown",))

    def test_wrong_slot_kind_rejected(self):
        source = packet("R03-CANONICAL")
        batches = inputs(source)
        wrong = (batches[1], batches[0], *batches[2:])
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(wrong, configuration(source), entity=EntityKey("X", "S")))

    def test_duplicate_actual_input_id_rejected(self):
        source = packet()
        batches = list(inputs(source))
        batches[1] = replace(batches[1], metadata=replace(batches[1].metadata,
            source=replace(batches[1].metadata.source, input_id="cl")))
        self.error(ErrorCode.DUPLICATE, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_overlapping_memberships_reject_before_late_knowledge(self):
        source = packet()
        batches = list(inputs(source))
        batches[0] = changed_batch(batches[0], effective_end_ns=(21, 40), known_at_ns=(5, 21))
        self.error(ErrorCode.DUPLICATE, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_duplicate_proofs_reject_before_knowledge(self):
        source = packet()
        batches = list(inputs(source))
        proof = batches[1]
        data = {column.name: (column.values[0], column.values[0]) for column in proof.columns}
        data["reference_id"] = ("h1:s:VQ:Y2w:YQ", "h1:s:VQ:Y2w:Yg")
        data["known_at_ns"] = (5, 21)
        batches[1] = replace(proof, columns=tuple(Column(name, values) for name, values in data.items()),
                             metadata=replace(proof.metadata, coverage=Coverage(2, 2, True)))
        self.error(ErrorCode.DUPLICATE, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_original_canonical_order_not_repaired(self):
        source = packet()
        batches = list(inputs(source))
        batches[0] = replace(batches[0], columns=tuple(Column(column.name, tuple(reversed(column.values)))
                                                     for column in batches[0].columns))
        self.error(ErrorCode.INVALID_ORDER, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_duplicate_original_reference_identity(self):
        source = packet()
        batches = list(inputs(source))
        batches[0] = changed_batch(batches[0], reference_id=("a", "a"))
        self.error(ErrorCode.DUPLICATE, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_selected_kind_filter_preserves_other_original_rows(self):
        source = packet()
        batches = list(inputs(source))
        batches[0] = changed_batch(batches[0], fact_kind=("industry_membership", "sector_membership"))
        result = compute_ef1(batches, configuration(source), entity=EntityKey("X", "S"))
        self.assertEqual(result.values[0].values, ("B",))
        self.assertEqual(result.quality[0].observed, 4)
        self.assertEqual(result.metadata.inputs[0].metadata, batches[0].metadata)

    def test_history_wrong_target_is_typed(self):
        source = packet()
        batches = list(inputs(source))
        batches[1] = changed_batch(batches[1], reference_id=("h1:s:VQ:b3RoZXI:aA",))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_history_wrong_scope_is_typed(self):
        source = packet()
        batches = list(inputs(source))
        batches[1] = changed_batch(batches[1], reference_id=("h1:s:Vg:Y2w:aA",))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_proof_relation_wrong_revision_is_typed(self):
        source = packet()
        batches = list(inputs(source))
        batches[1] = replace(batches[1], metadata=replace(batches[1].metadata,
            source=replace(batches[1].metadata.source, snapshot_id="R2")))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_empty_proof_wrong_source_is_not_hidden(self):
        source = packet()
        batches = list(inputs(source))
        batches[1] = empty_batch(batches[1])
        batches[1] = replace(batches[1], metadata=replace(batches[1].metadata,
            source=replace(batches[1].metadata.source, source_id="other")))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_missing_target_proofs_must_remain_coherent(self):
        source = packet()
        batches = list(inputs(source))
        batches[0] = None
        batches[1] = changed_batch(batches[1], reference_id=("h1:s:VQ:b3RoZXI:aA",))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_canonical_base64_padding_rejected(self):
        source = packet()
        batches = list(inputs(source))
        batches[1] = changed_batch(batches[1], reference_id=("h1:s:VQ=:Y2w:aA",))
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_reference_null_text_is_semantic_missingness(self):
        source = packet()
        batches = list(inputs(source))
        batches[0] = changed_batch(batches[0], text=("A", None))
        result = compute_ef1(batches, configuration(source), entity=EntityKey("X", "S"))
        self.assertEqual(result.values[0].values, (None,))
        self.assertEqual(result.values[1].values, ("missing_text",))
        self.assertEqual(tuple(reason.value for reason in result.quality[0].reasons), ("null_field",))

    def test_reference_nonblank_text_preserves_spacing(self):
        source = packet()
        batches = list(inputs(source))
        batches[0] = changed_batch(batches[0], text=("A", " B "))
        result = compute_ef1(batches, configuration(source), entity=EntityKey("X", "S"))
        self.assertEqual(result.values[0].values, (" B ",))

    def test_reference_unsafe_text_rejected_even_inactive(self):
        source = packet()
        for text in ("A\x00", "A\x7f", "\ud800", "x" * 129):
            batches = list(inputs(source))
            batches[0] = changed_batch(batches[0], text=(text, "B"))
            self.error(ErrorCode.BOUNDS, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_proof_numerical_fields_cannot_be_discarded(self):
        source = packet()
        batches = list(inputs(source))
        batches[1] = replace(batches[1], columns=(*batches[1].columns, Column("factor_num", (1,))))
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_null_unused_factor_columns_preserved_without_payload(self):
        source = packet()
        batches = list(inputs(source))
        batches[1] = replace(batches[1], columns=(*batches[1].columns,
            Column("factor_num", (None,)), Column("factor_den", (None,))))
        result = compute_ef1(batches, configuration(source), entity=EntityKey("X", "S"))
        self.assertEqual(projection(result), source["expected_result"])
        self.assertEqual(tuple(column.name for column in batches[1].columns)[-2:], ("factor_num", "factor_den"))
    def test_zero_factor_rejected_even_for_raw_policy(self):
        source = packet("RAW-ACTUAL-R1-factor-known_at")
        batches = list(inputs(source))
        batches[1] = changed_batch(batches[1], factor_num=(0,))
        self.error(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_finite_factor_end_rejected(self):
        source = packet("R03-CANONICAL")
        batches = list(inputs(source))
        batches[1] = changed_batch(batches[1], effective_end_ns=(21,))
        self.error(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_factor_text_cannot_be_discarded(self):
        source = packet("R03-CANONICAL")
        batches = list(inputs(source))
        batches[1] = replace(batches[1], columns=(*batches[1].columns, Column("text", ("hidden",))))
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_source_policy_mismatch_wins_unknown_history(self):
        source = packet("ACTION-source_policy_mismatch-known_at")
        batches = list(inputs(source))
        batches[2] = changed_batch(batches[2], text=("unknown",))
        result = compute_ef1(batches, configuration(source), entity=EntityKey("X", "S"))
        self.assertEqual(result.values[0].values, ("action_policy_mismatch",))
        self.assertEqual(result.values[1].values, ("failed",))

    def test_actual_adjustment_mismatch_is_diagnostic(self):
        source = packet("R03-CANONICAL")
        batches = list(inputs(source))
        batches[0] = replace(batches[0], metadata=replace(batches[0].metadata, adjustment=configuration(source).adjustment))
        result = compute_ef1(batches, configuration(source), entity=EntityKey("X", "S"))
        self.assertEqual(result.values[0].values, ("action_policy_mismatch",))

    def test_market_price_unit_mismatch_is_typed(self):
        source = packet("R03-CANONICAL")
        batches = list(inputs(source))
        batches[0] = replace(batches[0], metadata=replace(batches[0].metadata, price_unit=PriceUnit(1, "USD")))
        self.error(ErrorCode.INVALID_UNIT, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_market_scope_cannot_escape_requested_action_scope(self):
        source = packet("R03-CANONICAL")
        batches = list(inputs(source))
        batches[0] = replace(batches[0], metadata=replace(batches[0].metadata, scope=InputScope(-1, 20, "supplied_action")))
        self.error(ErrorCode.BOUNDS, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_market_scope_auction_declarations_match_config(self):
        source = packet("R03-CANONICAL")
        batches = list(inputs(source))
        batches[0] = replace(batches[0], metadata=replace(batches[0].metadata,
            scope=replace(batches[0].metadata.scope, include_opening_auction=True)))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_closing_trade_requires_source_proof_covering_actual_event_time(self):
        source = packet("R03-CANONICAL")
        base = configuration(source)
        context = json.loads(base.parameters[0].value)
        context["selection"]["scope_end_ns"] = 31
        config = build_ef1_config(context, session=replace(base.session, include_closing_auction=True),
            window=base.window, availability=AvailabilitySpec(30, 30, 30),
            price_unit=base.price_unit, adjustment=base.adjustment)
        batches = list(inputs(source))
        batches[0] = changed_batch(batches[0], event_ns=(30,), known_at_ns=(30,))
        batches[0] = replace(batches[0], columns=(*batches[0].columns, Column("condition", ("closing_auction",))),
            metadata=replace(batches[0].metadata, scope=InputScope(10, 30, "supplied_action", False, True)))
        for index in (2, 3):
            batches[index] = changed_batch(batches[index], effective_end_ns=(31,))
        for index in (4, 5):
            batches[index] = changed_batch(batches[index], effective_end_ns=(30,))
        result = compute_ef1(batches, config, entity=EntityKey("X", "S"))
        self.assertEqual(result.values[0].values, ("incomplete_reference",))
        self.assertEqual(result.values[1].values, ("unknown",))
        for index in (4, 5):
            batches[index] = changed_batch(batches[index], effective_end_ns=(31,))
        result = compute_ef1(batches, config, entity=EntityKey("X", "S"))
        self.assertEqual(result.values[1].values, ("passed",))
        # Filter the expired closing instant before duplicate arbitration.
        for index in (4, 5):
            proof = batches[index]
            data = {column.name: (column.values[0], column.values[0]) for column in proof.columns}
            data["reference_id"] = (data["reference_id"][0], "q1:bWs:eg")
            data["effective_end_ns"] = (30, 31)
            batches[index] = replace(proof, columns=tuple(Column(name, values) for name, values in data.items()),
                                     metadata=replace(proof.metadata, coverage=Coverage(2, 2, True)))
        result = compute_ef1(batches, config, entity=EntityKey("X", "S"))
        self.assertEqual(result.values[1].values, ("passed",))
        self.assertEqual(tuple(row.row_id for row in result.evidence if row.input_id in ("sr", "sq")),
                         ("q1:bWs:eg",) * 4)

    def test_action_bar_crossing_factor_boundary_rejected(self):
        source = packet("R03-CANONICAL")
        batches = list(inputs(source))
        market = batches[0]
        batches[0] = CanonicalBatch(DataKind.BAR,
            tuple(Column(name, (value,)) for name, value in (("instrument_id", "X"), ("session_id", "S"),
                ("start_ns", 10), ("end_ns", 20), ("known_at_ns", 10))), market.metadata)
        batches[1] = changed_batch(batches[1], effective_start_ns=(15,))
        self.error(ErrorCode.BOUNDS, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_action_daily_gate_without_optional_prices(self):
        source = packet("R03-CANONICAL")
        batches = list(inputs(source))
        market = batches[0]
        batches[0] = CanonicalBatch(DataKind.DAILY,
            tuple(Column(name, (value,)) for name, value in (("instrument_id", "X"), ("session_id", "S"),
                ("start_ns", 10), ("end_ns", 20), ("known_at_ns", 10))), market.metadata)
        result = compute_ef1(batches, configuration(source), entity=EntityKey("X", "S"))
        self.assertEqual(result.values[-1].values, ("passed",))
        self.assertEqual(batches[0].columns[-1].name, "known_at_ns")

    def test_action_missing_facts_do_not_become_complete_zero(self):
        source = packet("R03-CANONICAL")
        batches = list(inputs(source))
        batches[1] = None
        result = compute_ef1(batches, configuration(source), entity=EntityKey("X", "S"))
        self.assertEqual(result.values[0].values, ("absent_reference",))
        self.assertEqual(result.values[1].values, ("unknown",))
        self.assertNotIn("action_facts", tuple(binding.role for binding in result.metadata.inputs))

    def test_empty_action_requires_closed_projection(self):
        source = packet("ACTION-zero_actions-known_at")
        batches = list(inputs(source))
        batches[3] = None
        result = compute_ef1(batches, configuration(source), entity=EntityKey("X", "S"))
        self.assertEqual(result.values[0].values, ("incomplete_projection",))
        self.assertEqual(result.values[1].values, ("unknown",))

    def test_irrelevant_future_membership_is_not_consumed(self):
        source = packet()
        batches = list(inputs(source))
        facts = batches[0]
        data = {column.name: (*column.values, column.values[-1]) for column in facts.columns}
        data.update(reference_id=("a", "b", "c"), effective_start_ns=(0, 20, 40),
                    effective_end_ns=(20, 40, 60), known_at_ns=(5, 5, 99), text=("A", "B", "C"))
        batches[0] = replace(facts, columns=tuple(Column(name, values) for name, values in data.items()),
                             metadata=replace(facts.metadata, coverage=Coverage(3, 3, True)))
        result = compute_ef1(batches, configuration(source), entity=EntityKey("X", "S"))
        self.assertEqual(result.values[0].values, ("B",))
        self.assertEqual((result.quality[0].expected, result.quality[0].observed), (5, 5))
        self.assertNotIn("c", tuple(row.row_id for row in result.evidence))

    def test_reference_expected_count_overflow_rejected(self):
        source = packet()
        batches = list(inputs(source))
        batches[0] = replace(batches[0], metadata=replace(batches[0].metadata, coverage=Coverage(2**63 - 1, 2, False)))
        self.error(ErrorCode.OVERFLOW, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_reference_aggregate_work_bound_rejected(self):
        source = packet()
        batches = list(inputs(source))
        facts = batches[0]
        count = 4095
        data = {column.name: (column.values[0],) * count for column in facts.columns}
        data["reference_id"] = tuple("r" + str(index).zfill(4) for index in range(count))
        batches[0] = replace(facts, columns=tuple(Column(name, values) for name, values in data.items()),
                             metadata=replace(facts.metadata, coverage=Coverage(count, count, True)))
        self.error(ErrorCode.BOUNDS, lambda: compute_ef1(batches, configuration(source), entity=EntityKey("X", "S")))

    def test_future_effective_query_is_typed(self):
        source = packet()
        raw = json.loads(source["config"]["parameters"][0]["value"])
        raw["selection"]["effective_ns"] = 21
        config = configuration(source)
        self.error(ErrorCode.BOUNDS, lambda: build_ef1_config(raw, session=config.session, window=config.window,
            availability=config.availability, price_unit=config.price_unit, adjustment=config.adjustment))

    def test_action_policy_config_adjustment_must_match(self):
        config = configuration(packet("R03-CANONICAL"))
        config = replace(config, adjustment=AdjustmentSpec())
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: decode_ef1_context(config))

    def test_config_forbids_extra_payload_context(self):
        source = packet()
        config = configuration(source)
        context = json.loads(config.parameters[0].value)
        context["selection"]["text"] = "unbound acquired fact"
        self.error(ErrorCode.INVALID_CONFIG, lambda: build_ef1_config(context, session=config.session, window=config.window,
            availability=config.availability, price_unit=config.price_unit, adjustment=config.adjustment))

    def test_config_context_duplicate_keys_not_silently_selected(self):
        config = configuration(packet())
        text = config.parameters[0].value.replace('"effective_ns":20', '"effective_ns":20,"effective_ns":19')
        config = replace(config, parameters=(Parameter("ef1_context_json", text),))
        self.error(ErrorCode.DUPLICATE, lambda: decode_ef1_context(config))

    def test_config_bool_query_is_not_integer(self):
        source = packet()
        config = configuration(source)
        context = json.loads(config.parameters[0].value)
        context["selection"]["effective_ns"] = True
        self.error(ErrorCode.BOUNDS, lambda: build_ef1_config(context, session=config.session, window=config.window,
            availability=config.availability, price_unit=config.price_unit, adjustment=config.adjustment))


if __name__ == "__main__":
    unittest.main()