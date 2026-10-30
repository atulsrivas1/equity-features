"""Literal independent daily observations packets, frozen before implementation."""
from copy import deepcopy
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import unittest

from equity_feature_contracts import CanonicalBatch, Column, ConfigSpec, ContractError, DataKind, EntityKey
from equity_features.ef1 import build_ef1_config, compute_ef1, decode_ef1_context, ef1_definitions
from test_ef1_observable import metadata

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures/ef1_daily_observations.json"
FIXTURE_BYTES = FIXTURE.read_bytes()
PACK = json.loads(FIXTURE_BYTES)


def inputs(packet):
    return tuple(None if slot["batch"] is None else CanonicalBatch(DataKind(slot["batch"]["kind"]),
        tuple(Column(c["name"], tuple(c["values"])) for c in slot["batch"]["columns"]),
        metadata(slot["batch"]["metadata"])) for slot in packet["role_slots"])


def evaluate(packet):
    config = ConfigSpec.from_json(json.dumps(packet["config"]))
    return compute_ef1(inputs(packet), config, entity=EntityKey(**packet["entity"]))


class DailyPackets(unittest.TestCase):
    def test_frozen_original_synthetic_bytes(self):
        self.assertEqual(hashlib.sha256(FIXTURE_BYTES).hexdigest(), "50257a0d648809c7987ce49d710812afdd5f1ff6dd4ddf1c65c0fafb8c121f15")
        self.assertEqual(len(PACK["packets"]), 119)

    def test_all_complete_literals(self):
        for packet in PACK["packets"]:
            if packet.get("expected_result") is None:
                continue
            with self.subTest(packet=packet["id"]):
                result = evaluate(packet)
                self.assertEqual(json.loads(json.dumps(asdict(result))), packet["expected_result"])

    def test_all_stage_refusals(self):
        for packet in PACK["packets"]:
            if packet.get("expected_error") is None:
                continue
            with self.subTest(packet=packet["id"], stage=packet["expected_error"]["stage"]):
                with self.assertRaises(ContractError) as caught:
                    evaluate(packet)
                self.assertEqual(caught.exception.code.value, packet["expected_error"]["code"])

    def test_additive_config_discovery(self):
        packet = PACK["packets"][0]
        config = ConfigSpec.from_json(json.dumps(packet["config"]))
        built = build_ef1_config(json.loads(config.parameters[0].value), session=config.session,
            window=config.window, availability=config.availability, adjustment=config.adjustment, price_unit=config.price_unit)
        self.assertEqual(config, built)
        self.assertEqual(decode_ef1_context(config)["producer"], "daily_observations")
        self.assertEqual([d.feature_id.rsplit(".", 1)[1] for d in ef1_definitions(config)], ["high", "low", "open", "selected_observed_count"])

    def test_known_raw_minimum_suppresses_all_outputs_despite_common_gap(self):
        # Two causally proved admitted raw rows cannot meet minimum three.
        # A missing price capability cannot turn that known gate into a price
        # missing-input assessment. Numeric structural checks still run first.
        packet = deepcopy(next(p for p in PACK["packets"] if p["id"] == "V202-last-two"))
        context = json.loads(packet["config"]["parameters"][0]["value"])
        context["admission"]["minimum_admitted_history"] = 3
        packet["config"]["parameters"][0]["value"] = json.dumps(context, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
        packet["role_slots"][4]["batch"] = None
        result = evaluate(packet)
        self.assertEqual([c.values for c in result.values], [(None,)] * 4)
        self.assertEqual([(q.status.value, tuple(r.value for r in q.reasons), q.expected, q.observed) for q in result.quality],
            [("insufficient_history", ("insufficient_history",), 3, 3)] * 4)
        self.assertEqual(result.evidence, ())
        self.assertEqual([binding.role for binding in result.metadata.inputs],
            ["basis_provenance", "calendar_manifest", "calendar_slots", "observation_coverage", "raw_observations"])
        self.assertEqual({binding.role: asdict(binding.metadata) for binding in result.metadata.inputs},
            {slot["role"]: asdict(metadata(slot["batch"]["metadata"])) for slot in packet["role_slots"] if slot["batch"] is not None})

    def test_existing_basis_cannot_contradict_proved_absence(self):
        for missing_parents in (False, True):
            with self.subTest(missing_parents=missing_parents):
                packet = deepcopy(next(p for p in PACK["packets"] if p["id"] == "V202-last-two"))
                for slot in packet["role_slots"]:
                    if slot["role"] in ("raw_observations", "common_observations"):
                        if missing_parents:
                            slot["batch"] = None
                        else:
                            for column in slot["batch"]["columns"]:
                                column["values"] = []
                            slot["batch"]["metadata"]["coverage"] = {"expected": 0, "observed": 0, "complete": True}
                    elif slot["role"] == "observation_coverage":
                        for column in slot["batch"]["columns"]:
                            if column["name"] == "text":
                                column["values"] = [json.dumps({"state": "absent_in_snapshot", "raw_reference_id": None,
                                    "common_reference_id": None, "basis_reference_id": None}, sort_keys=True, separators=(",", ":"))] * 3
                with self.assertRaises(ContractError) as caught:
                    evaluate(packet)
                self.assertEqual(caught.exception.code.value, "inconsistent_identity")

    def test_declared_raw_ids_agree_without_physical_raw_role(self):
        for role in ("common_observations", "basis_provenance"):
            with self.subTest(role=role):
                packet = deepcopy(next(p for p in PACK["packets"] if p["id"] == "V318-raw_observations-none"))
                slot = next(s for s in packet["role_slots"] if s["role"] == role)
                column = next(c for c in slot["batch"]["columns"] if c["name"] == "text")
                payload = json.loads(column["values"][0])
                payload["raw_reference_id"] = "CONTRADICTORY-RAW-ID"
                column["values"][0] = json.dumps(payload, sort_keys=True, separators=(",", ":"))
                with self.assertRaises(ContractError) as caught:
                    evaluate(packet)
                self.assertEqual(caught.exception.code.value, "inconsistent_identity")

    def test_actual_empty_raw_parent_rejects_basis_without_coverage(self):
        packet = deepcopy(next(p for p in PACK["packets"] if p["id"] == "V202-last-two"))
        for slot in packet["role_slots"]:
            if slot["role"] in ("raw_observations", "common_observations"):
                for column in slot["batch"]["columns"]:
                    column["values"] = []
                slot["batch"]["metadata"]["coverage"] = {"expected": 0, "observed": 0, "complete": True}
            elif slot["role"] == "observation_coverage":
                slot["batch"] = None
        with self.assertRaises(ContractError) as caught:
            evaluate(packet)
        self.assertEqual(caught.exception.code.value, "inconsistent_identity")

    def test_duplicate_civil_dates_precede_later_join_refusals(self):
        for role in ("calendar_slots", "raw_observations", "common_observations"):
            with self.subTest(role=role):
                packet = deepcopy(next(p for p in PACK["packets"] if p["id"] == "V202-last-two"))
                slot = next(s for s in packet["role_slots"] if s["role"] == role)
                column = next(c for c in slot["batch"]["columns"] if c["name"] == "text")
                payload = json.loads(column["values"][1])
                payload["date"] = json.loads(column["values"][0])["date"]
                column["values"][1] = json.dumps(payload, sort_keys=True, separators=(",", ":"))
                with self.assertRaises(ContractError) as caught:
                    evaluate(packet)
                self.assertEqual(caught.exception.code.value, "duplicate")

    def test_civil_label_validation_does_not_infer_utc_day_bounds(self):
        packet = deepcopy(PACK["packets"][0])
        context = json.loads(packet["config"]["parameters"][0]["value"])
        # A valid civil label is independent of the actual UTC int64 instants.
        # Decoder acceptance establishes no timezone or actual calendar truth.
        context["calendar"]["history_start_date"] = "1677-09-20"
        packet["config"]["parameters"][0]["value"] = json.dumps(context, sort_keys=True, separators=(",", ":"))
        config = ConfigSpec.from_json(json.dumps(packet["config"]))
        self.assertEqual(decode_ef1_context(config)["calendar"]["history_start_date"], "1677-09-20")
        context["calendar"]["history_start_date"] = "1677-02-30"
        packet["config"]["parameters"][0]["value"] = json.dumps(context, sort_keys=True, separators=(",", ":"))
        with self.assertRaises(ContractError):
            decode_ef1_context(ConfigSpec.from_json(json.dumps(packet["config"])))


if __name__ == "__main__":
    unittest.main()
