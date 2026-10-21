"""Independent preimplementation full canonical period/phase packets and controls."""
from copy import deepcopy
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import unittest

from equity_feature_contracts import (
    AdjustmentSpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, ContractError,
    Coverage, DataKind, EntityKey, ErrorCode, InputScope, IntervalCoverage,
    PriceUnit, SourceBinding,
)
from equity_features.ef1 import build_ef1_config, compute_ef1, decode_ef1_context, ef1_definitions

SPEC_BYTES = (Path(__file__).resolve().parents[2] / "docs/ef1/PERIOD_PHASE_CONTRACT_PROPOSAL.json").read_bytes()
SPEC = json.loads(SPEC_BYTES)
PACKETS = {p["id"]: p for p in SPEC["canonical_fixture_packets"] + SPEC["canonical_case_packets"]}


def metadata(raw):
    m = dict(raw)
    m["source"] = SourceBinding(**m["source"])
    m["coverage"] = Coverage(**m["coverage"])
    m["adjustment"] = AdjustmentSpec(**m["adjustment"])
    m["price_unit"] = None if m["price_unit"] is None else PriceUnit(**m["price_unit"])
    m["scope"] = None if m["scope"] is None else InputScope(**m["scope"])
    m["interval_coverage"] = tuple(IntervalCoverage(v["name"], v["start_ns"], v["end_ns"], Coverage(**v["coverage"]))
                                    for v in m["interval_coverage"])
    return BatchMetadata(**m)


def inputs(packet):
    present = []
    for slot in packet["input_slots"]:
        raw = slot["batch"]
        if raw is not None:
            present.append(CanonicalBatch(DataKind(raw["kind"]),
                tuple(Column(name, tuple(row[i] for row in raw["rows"])) for i, name in enumerate(raw["column_order"])),
                metadata(raw["metadata"])))
    return tuple(present)


def configuration(packet):
    return ConfigSpec.from_json(json.dumps(packet["config"], ensure_ascii=True, sort_keys=True, separators=(",", ":")))


def projection(value):
    return json.loads(json.dumps(asdict(value), ensure_ascii=True))


def evaluate(packet):
    return compute_ef1(inputs(packet), configuration(packet), entity=EntityKey(**packet["entity"]))


class PeriodPhasePackets(unittest.TestCase):
    def error(self, code, call):
        with self.assertRaises(ContractError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)

    def assert_packet(self, case):
        packet = deepcopy(PACKETS[case])
        original = deepcopy(packet)
        if packet["expected_result"] is None:
            self.error(ErrorCode(packet["expected_error"]["code"]), lambda: evaluate(packet))
        else:
            config = configuration(packet)
            canonical_context = json.loads(config.parameters[0].value)
            self.assertEqual(canonical_context, packet["context"])
            rebuilt = build_ef1_config(canonical_context, session=config.session, window=config.window,
                availability=config.availability, price_unit=config.price_unit, adjustment=config.adjustment)
            self.assertEqual(config, rebuilt)
            batches = inputs(packet)
            before = tuple(projection(batch) for batch in batches)
            entity = EntityKey(**packet["entity"])
            result = compute_ef1(batches, config, entity=entity)
            self.assertEqual(projection(result), packet["expected_result"])
            self.assertEqual(projection(compute_ef1(batches, config, entity=entity)), packet["expected_result"])
            self.assertEqual(tuple(projection(batch) for batch in batches), before)
        self.assertEqual(packet, original)

    def test_frozen_population_and_bytes(self):
        self.assertEqual(hashlib.sha256(SPEC_BYTES).hexdigest(), "b4c78f03b3c1ec5100740803d4b853920f9aa28cb58d73446dea6b3f403db09c")
        self.assertEqual(len(PACKETS), 62)
        self.assertEqual(sum(p["expected_result"] is not None for p in PACKETS.values()), 42)

    def test_complete_discovery_sets_and_roles(self):
        for name, count, roles in (("PERIOD_BASE", 9, ("calendar_provenance", "daily_history", "bars")),
                                   ("EXTENDED_BASE", 8, ("calendar_provenance", "bars", "prior_close"))):
            definitions = ef1_definitions(configuration(PACKETS[name]))
            self.assertEqual(len(definitions), count)
            self.assertEqual({d.feature_id for d in definitions}, {v["feature_id"] for v in PACKETS[name]["expected_result"]["values"]})
            self.assertTrue(all(tuple(r.role for r in d.requirements) == roles for d in definitions))
            self.assertTrue(all(d.capabilities.batch and not d.capabilities.update for d in definitions))

    def test_reordered_present_roles_reject(self):
        packet = PACKETS["PERIOD_BASE"]
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(tuple(reversed(inputs(packet))), configuration(packet), entity=EntityKey(**packet["entity"])))

    def test_duplicate_input_identity_reject(self):
        packet = PACKETS["PERIOD_BASE"]
        batches = list(inputs(packet))
        batches[-1] = replace(batches[-1], metadata=replace(batches[-1].metadata,
            source=replace(batches[-1].metadata.source, input_id=batches[0].metadata.source.input_id)))
        self.error(ErrorCode.DUPLICATE, lambda: compute_ef1(batches, configuration(packet), entity=EntityKey(**packet["entity"])))

    def test_null_is_not_present_empty_batch(self):
        packet = PACKETS["EXTENDED_BASE"]
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1((None,), configuration(packet), entity=EntityKey(**packet["entity"])))

    def test_wrong_target_entity_reject(self):
        packet = PACKETS["PERIOD_BASE"]
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(inputs(packet), configuration(packet), entity=EntityKey("X", "WRONG")))

    def test_detached_context_is_immutable(self):
        context = decode_ef1_context(configuration(PACKETS["PERIOD_BASE"]))
        with self.assertRaises(TypeError):
            context["selection"]["count"] = 2

    def test_original_contract_headers_retained(self):
        self.assertEqual(len(SPEC["original_headers"]), 17)
        self.assertEqual(len(SPEC["original_fixtures"]), 6)

    def test_wrong_civil_boundary_reject(self):
        packet = deepcopy(PACKETS["PERIOD_BASE"])
        context = packet["context"]
        context["selection"]["start_date"] = "2026-09-30"
        config = configuration(packet)
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: build_ef1_config(context,
            session=config.session, window=config.window, availability=config.availability,
            price_unit=config.price_unit, adjustment=config.adjustment))

    def test_boolean_period_count_reject(self):
        packet = deepcopy(PACKETS["PERIOD_BASE"])
        packet["context"]["selection"]["count"] = True
        config = configuration(packet)
        self.error(ErrorCode.BOUNDS, lambda: build_ef1_config(packet["context"],
            session=config.session, window=config.window, availability=config.availability,
            price_unit=config.price_unit, adjustment=config.adjustment))

    def test_missing_selected_phase_reject(self):
        packet = deepcopy(PACKETS["EXTENDED_BASE"])
        packet["context"]["calendar"]["segments"] = [["regular", 10, 30]]
        config = configuration(packet)
        self.error(ErrorCode.INVALID_CONFIG, lambda: build_ef1_config(packet["context"],
            session=config.session, window=config.window, availability=config.availability,
            price_unit=config.price_unit, adjustment=config.adjustment))

    def test_market_units_reject_even_with_missing_calendar(self):
        packet = PACKETS["PERIOD_BASE"]
        batches = list(inputs(packet))[1:]
        batches[0] = replace(batches[0], metadata=replace(batches[0].metadata, price_unit=PriceUnit(1, "USD")))
        self.error(ErrorCode.INVALID_UNIT, lambda: compute_ef1(batches,
            configuration(packet), entity=EntityKey(**packet["entity"])))

    def test_unused_nonboundary_ohlc_fields_do_not_gate_first_open_last_close(self):
        packet = PACKETS["PERIOD_BASE"]
        proof, daily, bars = inputs(packet)
        daily = replace(daily, columns=tuple(c for c in daily.columns if c.name != "close"))
        bars = replace(bars, columns=tuple(c for c in bars.columns if c.name != "open"))
        result = compute_ef1((proof, daily, bars), configuration(packet), entity=EntityKey(**packet["entity"]))
        self.assertEqual({v.feature_id.rsplit(".", 1)[1]: v.values[0] for v in result.values},
            {"open": 10.0, "high": 14.0, "low": 9.0, "close": 13.0, "volume": 5,
             "notional": 57, "open_close_return": 0.3, "scheduled_sessions": 2, "completed_sessions": 1})
        self.assertTrue(all(q.status == "available" and q.expected == q.observed == 2 and not q.reasons for q in result.quality))


def _packet_test(case):
    def test(self):
        self.assert_packet(case)
    test.__name__ = "test_packet_" + case.lower()
    return test


for _case in PACKETS:
    setattr(PeriodPhasePackets, "test_packet_" + _case.lower(), _packet_test(_case))


if __name__ == "__main__":
    unittest.main()
