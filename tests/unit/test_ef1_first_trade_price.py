"""Complete frozen first-trade literals; fixtures loaded before calculation denial."""
from collections import Counter
from dataclasses import asdict, replace
import hashlib
import json
from pathlib import Path
import unittest
import equity_feature_contracts as c
from equity_features.ef1 import build_ef1_config, compute_ef1, decode_ef1_context, ef1_definitions

ORACLE_BYTES = (Path(__file__).resolve().parents[2] / "docs/ef1/regular_first_trade_price/REGULAR_FIRST_TRADE_PRICE_ORACLE.json").read_bytes()
ORACLE = json.loads(ORACLE_BYTES)
OUTCOMES = ORACLE["outcome_cases"]
REFUSALS = ORACLE["refusal_cases"]


def inputs(request, stage=None):
    def mark(name):
        if stage is not None:
            stage[0] = name
    result = []
    for slot in request["role_slots"]:
        b = slot["batch"]
        if b is None:
            result.append(None)
            continue
        mark("transport_schema_admission")
        if b["schema_version"] != "1":
            raise c.ContractError(c.ErrorCode.INCOMPATIBLE_VERSION, "unsupported transport schema")
        d = b["metadata"]
        mark("Coverage_constructor")
        coverage = c.Coverage(**d["coverage"])
        intervals = tuple(c.IntervalCoverage(x["name"], x["start_ns"], x["end_ns"], c.Coverage(**x["coverage"])) for x in d["interval_coverage"])
        mark("PriceUnit_constructor")
        unit = None if d["price_unit"] is None else c.PriceUnit(**d["price_unit"])
        mark("BatchMetadata_constructor")
        meta = c.BatchMetadata(namespace=d["namespace"], source=c.SourceBinding(**d["source"]),
            coverage=coverage, price_unit=unit, adjustment=c.AdjustmentSpec(**d["adjustment"]),
            sampling=d["sampling"], quantity_unit=d["quantity_unit"], ordering=d["ordering"],
            duplicate_policy=d["duplicate_policy"], scope=None if d["scope"] is None else c.InputScope(**d["scope"]),
            interval_coverage=intervals)
        mark("CanonicalBatch_constructor")
        result.append(c.CanonicalBatch(c.DataKind(b["kind"]), tuple(c.Column(x["name"], tuple(x["values"])) for x in b["columns"]), meta))
    return tuple(result)


def evaluate(case):
    request = case["request"]
    return compute_ef1(inputs(request), c.ConfigSpec.from_json(json.dumps(request["config"])), entity=c.EntityKey(**request["entity"]))


class FirstTradePackets(unittest.TestCase):
    def test_immutable_complete_oracle(self):
        self.assertEqual(hashlib.sha256(ORACLE_BYTES).hexdigest(), "b57ac7221508310cdc812f718b19287c9e23604fddcab6a676cb4407bfdd9997")
        self.assertEqual((len(OUTCOMES), len(REFUSALS), len(ORACLE["worker_result_cases"])), (122, 159, 17))

    def test_complete_result_literals_and_exact_float(self):
        for case in OUTCOMES:
            with self.subTest(case=case["id"]):
                result = evaluate(case)
                self.assertEqual(json.loads(json.dumps(asdict(result))), case["expected_result"])
                value = result.values[0].values[0]
                self.assertEqual(None if value is None else value.hex(), case["expected_float_hex"])

    def test_refusals_actual_earliest_stage(self):
        observed = Counter()
        for case in REFUSALS:
            with self.subTest(case=case["id"]):
                request = case["request"]
                stage = ["ConfigSpec_constructor"]
                try:
                    config = c.ConfigSpec.from_json(json.dumps(request["config"]))
                    batches = inputs(request, stage)
                    stage[0] = "canonical_validate_batch"
                    for batch in batches:
                        if batch is not None:
                            c.validate_batch(batch, required_fields=())
                    stage[0] = "future_new_config_decode"
                    decode_ef1_context(config)
                    stage[0] = "future_new_pure_semantic"
                    compute_ef1(batches, config, entity=c.EntityKey(**request["entity"]))
                except c.ContractError as error:
                    self.assertEqual(error.code.value, case["expected_error"]["code"])
                    self.assertEqual(stage[0], case["expected_error"]["earliest_stage"])
                    observed[stage[0]] += 1
                else:
                    self.fail("expected refusal")
        self.assertEqual(observed, Counter(case["expected_error"]["earliest_stage"] for case in REFUSALS))

    def test_additive_builder_and_definition(self):
        config = c.ConfigSpec.from_json(json.dumps(OUTCOMES[0]["request"]["config"]))
        self.assertEqual(config, build_ef1_config(json.loads(config.parameters[0].value), session=config.session,
            window=config.window, availability=config.availability, price_unit=config.price_unit, adjustment=config.adjustment))
        definition, = ef1_definitions(config)
        self.assertEqual((definition.feature_id, definition.dtype.value, definition.unit),
            ("session.regular.first_trade_price", "float64", "currency/share"))
        self.assertEqual(tuple(r.role for r in definition.requirements), ("calendar_provenance", "trades", "population_proof"))

    def test_calculation_denies_external_entrypoints(self):
        from test_purity_audit import denied_entrypoints
        requests = [(inputs(x["request"]), c.ConfigSpec.from_json(json.dumps(x["request"]["config"])),
                     c.EntityKey(**x["request"]["entity"])) for x in OUTCOMES]
        compute_ef1(requests[0][0], requests[0][1], entity=requests[0][2])
        with denied_entrypoints():
            results = [compute_ef1(b, config, entity=e) for b, config, e in requests]
        for result, case in zip(results, OUTCOMES):
            self.assertEqual(json.loads(json.dumps(asdict(result))), case["expected_result"])

    def test_input_immutability_and_fixed_slots(self):
        request = OUTCOMES[0]["request"]
        batches = inputs(request)
        config = c.ConfigSpec.from_json(json.dumps(request["config"]))
        entity = c.EntityKey(**request["entity"])
        before = tuple(asdict(b) for b in batches)
        compute_ef1(batches, config, entity=entity)
        self.assertEqual(tuple(asdict(b) for b in batches), before)
        for bad in (batches[:2], batches + (None,), iter(batches)):
            with self.assertRaises(c.ContractError) as caught:
                compute_ef1(bad, config, entity=entity)
            self.assertEqual(caught.exception.code, c.ErrorCode.INVALID_SCHEMA)
