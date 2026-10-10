"""Independent owned EQ076 wire vectors; executable design, not endpoint tests."""
from copy import deepcopy
import json
from pathlib import Path
import struct
import sys
import unittest

from remote_transport_reference import WireError, command_digest, decode, verify_pair

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "docs/examples/remote"
sys.path.insert(0, str(ROOT / "packages/contracts/src"))
from equity_feature_contracts import (  # noqa: E402
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, ConfigSpec, Coverage,
    InputBinding, InputScope, PriceUnit, ResultMetadata, SourceBinding, DataKind,
    builtin_registry, BreadthCounts,
)


def fixture(name):
    return json.loads((FIXTURES / (name + ".json")).read_text(encoding="utf-8"))


def wire(value):
    return json.dumps(value, ensure_ascii=True, allow_nan=False).encode("ascii")


def decode_fixture_record(cell):
    """Owned test fixture only; explicit constructors, never a remote decoder."""
    if cell is None:
        return None
    tag = cell["type"]
    if tag == "int64":
        return int(cell["value"])
    if tag in ("string", "bool"):
        return cell["value"]
    if tag == "list":
        return tuple(decode_fixture_record(x) for x in cell["items"])
    constructors = {c.__name__: c for c in (
        SourceBinding, Coverage, PriceUnit, AdjustmentSpec, InputScope,
        BatchMetadata, AvailabilitySpec, InputBinding, ResultMetadata,
    )}
    fields = {k: decode_fixture_record(v) for k, v in cell["fields"].items()}
    if cell["name"] == "InputBinding":
        fields["kind"] = DataKind(fields["kind"])
    return constructors[cell["name"]](**fields)


class TransportVectors(unittest.TestCase):
    def error(self, code, value, *, request=False):
        data = value if type(value) is bytes else wire(value)
        with self.assertRaises(WireError) as caught:
            decode(data, request=request)
        self.assertEqual(caught.exception.code, code)

    def cell(self, dtype, value):
        response = fixture("slice_response")
        response["payload"]["columns"] = [
            {"name": "owned", "dtype": dtype, "unit": "owned", "values": [value]}]
        return response

    def test_seven_frozen_envelopes(self):
        for name in ("calculate", "result", "slice_request", "slice_response",
                     "job", "error", "discovery"):
            with self.subTest(name=name):
                f = fixture(name)
                self.assertEqual(decode(wire(f), request=f["kind"] == "request"), f)
        verify_pair(fixture("calculate"), fixture("result"))

    def test_native_config_registry_and_full_metadata(self):
        c = ConfigSpec.from_json((FIXTURES / "approved-config.json").read_text(encoding="utf-8"))
        context = fixture("calculate")["payload"]["context"]
        self.assertEqual(c.digest, context["config"]["digest"])
        self.assertEqual(c.availability.market_cutoff_ns, 9007199254740993)
        self.assertEqual(context["registry_snapshot"], json.loads(builtin_registry().to_json())["builtin_digest"])
        self.assertEqual(builtin_registry().get("session.trade.count").algorithm_version, "v1")
        metadata = decode_fixture_record(fixture("result")["payload"]["metadata"])
        self.assertEqual(metadata.config_digest, c.digest)
        self.assertEqual(metadata.availability, c.availability)
        self.assertEqual(metadata.namespace, c.session.namespace)
        self.assertEqual(metadata.inputs[0].metadata.price_unit, c.price_unit)
        self.assertEqual(metadata.inputs[0].metadata.source.input_id, context["dataset"]["input_id"])

    def test_int64_extrema_and_javascript_boundary(self):
        for literal, expected in (("-9223372036854775808", -(2**63)),
                                  ("9223372036854775807", 2**63-1),
                                  ("9007199254740993", 2**53+1), ("0", 0)):
            with self.subTest(literal=literal):
                v = decode(wire(self.cell("int64", {"type": "int64", "value": literal})), request=False)
                self.assertEqual(int(v["payload"]["columns"][0]["values"][0]["value"]), expected)

    def test_one_nanosecond_and_unknown_not_zero(self):
        data = decode(wire(fixture("slice_response")), request=False)["payload"]["columns"]
        self.assertEqual(int(data[0]["values"][1]["value"]) - int(data[0]["values"][0]["value"]), 1)
        self.assertIsNone(data[1]["values"][0])
        self.assertEqual(data[1]["values"][1], {"type": "int64", "value": "0"})

    def test_finite_binary64_exact_bits(self):
        for bits, expected in (("8000000000000000", -0.0),
                               ("0000000000000001", float.fromhex("0x0.0000000000001p-1022")),
                               ("3ff0000000000000", 1.0),
                               ("7fefffffffffffff", float.fromhex("0x1.fffffffffffffp+1023"))):
            with self.subTest(bits=bits):
                value = decode(wire(self.cell("float64", {"type": "float64", "bits": bits})), request=False)
                actual = value["payload"]["columns"][0]["values"][0]["bits"]
                self.assertEqual(bytes.fromhex(actual), struct.pack(">d", expected))

    def test_decimal128_precision_and_scale(self):
        for coefficient, scale in (("9"*38, 0), ("-"+"9"*38, 38), ("1", -38)):
            value = {"type": "decimal128", "coefficient": coefficient, "scale": scale}
            result = decode(wire(self.cell("decimal128", value)), request=False)
            self.assertEqual(result["payload"]["columns"][0]["values"][0], value)

    def test_bad_integer_representations_and_overflow(self):
        for literal in (1, True, "01", "-0", "+1", "1.0", "1e2", " 1", "\u0661"):
            with self.subTest(literal=literal):
                self.error("invalid_schema", self.cell("int64", {"type": "int64", "value": literal}))
        for literal in ("9223372036854775808", "-9223372036854775809"):
            self.error("bounds", self.cell("int64", {"type": "int64", "value": literal}))

    def test_nonfinite_bit_patterns(self):
        for bits in ("7ff0000000000000", "fff0000000000000", "7ff8000000000001"):
            self.error("invalid_schema", self.cell("float64", {"type": "float64", "bits": bits}))

    def test_strict_json_ingress(self):
        for data in (b'{"a":1,"a":2}', b'{"a":NaN}', b'{"a":Infinity}', b'\xff', b'\xef\xbb\xbf{}'):
            self.error("invalid_json", data)
        f = fixture("slice_response")
        f["request_id"] = "\ud800"
        self.error("invalid_json", f)
        self.error("invalid_json", self.cell("string", {"type": "string", "value": "\ud800"}))
        self.error("bounds", b"["*33+b"0"+b"]"*33)
        self.error("bounds", b" "*262145)
        self.error("bounds", b" "*16385, request=True)

    def test_unknown_fields_versions_and_direction(self):
        f = fixture("calculate")
        for key in ("pickle", "sql", "path", "callable"):
            bad = deepcopy(f); bad["payload"][key] = "untrusted"
            self.error("invalid_schema", bad, request=True)
        for version in ("1.1", "2.0", 1):
            bad = deepcopy(f); bad["version"] = version
            self.error("incompatible_version", bad, request=True)
        self.error("invalid_schema", fixture("result"), request=True)

    def test_command_changes_and_idempotency_exclusion(self):
        f = fixture("calculate")
        bad = deepcopy(f);bad["payload"]["context"]["dataset"]["revision"] = "changed"
        self.error("inconsistent_identity", bad, request=True)
        bad = deepcopy(f);bad["payload"]["idempotency_key"] = "another-key"
        self.assertEqual(command_digest(bad["payload"]), f["payload"]["command_digest"])
        self.assertEqual(decode(wire(bad), request=True), bad)
        r = fixture("result");r["payload"]["context"]["config"]["revision"] = "changed"
        with self.assertRaises(WireError):verify_pair(f, r)

    def test_scope_and_causal_boundaries(self):
        for value in ("9007199254740992", "9007199254740991"):
            f = fixture("slice_request");f["payload"]["scope"]["end_ns"] = value
            self.error("bounds", f, request=True)
        f = fixture("calculate");a = f["payload"]["context"]["availability"]
        a["evaluation_ns"] = "9007199254740992"
        self.error("inconsistent_identity", f, request=True)
        f = fixture("calculate");f["payload"]["context"]["availability"]["mode"] = "reconstruction"
        self.error("invalid_schema", f, request=True)

    def test_quality_is_not_a_transport_failure(self):
        f = fixture("result");q = f["payload"]["quality"][0]
        q.update(status="missing_input", expected=None, observed="0", reasons=["absent_input"])
        f["payload"]["columns"][0]["values"] = [None]
        self.assertEqual(decode(wire(f), request=False), f)
        q["reasons"] = [];self.error("invalid_schema", f)
        f = fixture("result");f["payload"]["quality"][0]["observed"] = "2"
        self.error("bounds", f)
        f = fixture("result");f["payload"]["columns"][0]["values"] = [None]
        self.error("invalid_schema", f)
        f = fixture("result");f["payload"]["quality"] = []
        self.error("inconsistent_identity", f)

    def test_job_and_error_vocabularies(self):
        f = fixture("job");f["payload"]["state"] = "succeeded"
        self.error("inconsistent_identity", f)
        f = fixture("job");f["payload"]["state"] = "failed"
        self.error("inconsistent_identity", f)
        f["payload"]["error"] = {"category": "internal", "code": "internal_error", "retryable": False}
        self.assertEqual(decode(wire(f), request=False), f)
        f = fixture("error");f["payload"]["category"] = "authentication"
        self.error("invalid_schema", f)

    def test_record_algorithm_and_metadata_identity(self):
        f = fixture("result");f["payload"]["columns"][0]["algorithm_version"] = "changed"
        self.error("inconsistent_identity", f)
        f = fixture("result");f["payload"]["metadata"]["fields"]["backend_version"]["value"] = "changed"
        self.error("inconsistent_identity", f)
        f = fixture("result");f["payload"]["metadata"]["fields"].pop("inputs")
        self.error("invalid_schema", f)
        f = fixture("result");f["payload"]["metadata"]["name"] = "os.system"
        self.error("invalid_schema", f)
        r = fixture("result")
        for target in (r["payload"]["columns"][0]["entities"][0], r["payload"]["quality"][0]["entity"]):
            target["instrument_id"] = "foreign:ONE"
        with self.assertRaises(WireError):verify_pair(fixture("calculate"), r)

    def test_decimal_bounds_and_structured_literal(self):
        for coefficient, scale in (("1"+"0"*38, 0), ("1", 39), ("1", True), ("1", 1.0), ("-0", 0)):
            self.error("invalid_schema", self.cell("decimal128", {
                "type": "decimal128", "coefficient": coefficient, "scale": scale}))
        # A standalone owned typed cell, not a fabricated calculated result.
        from jsonschema import Draft202012Validator
        schema = json.loads((ROOT / "docs/schemas/remote-v1.schema.json").read_text(encoding="utf-8"))
        cell = {"type": "record", "name": "BreadthCounts", "fields": {
            name: {"type": "int64", "value": value} for name, value in
            (("advancing", "2"), ("declining", "1"), ("unchanged", "0"), ("expected", "3"))}}
        Draft202012Validator({"$ref": "#/$defs/cell", "$defs": schema["$defs"]}).validate(cell)
        self.assertEqual(json.loads(wire(cell)), cell)
        native = BreadthCounts(2, 1, 0, 3)
        self.assertEqual(native.eligible, 3)
        self.assertEqual(int(cell["fields"]["advancing"]["value"]), native.advancing)

    def test_node_cap_precedes_schema_recursion(self):
        cell = {"type": "list", "items": [
            {"type": "list", "items": [None]*100} for _ in range(100)]}
        f = self.cell("int64", cell)
        self.assertLess(len(wire(f)), 262144)
        self.error("bounds", f)

    def test_trailing_newline_regressions(self):
        for dtype, cell in (("int64", {"type": "int64", "value": "1\n"}),
                            ("float64", {"type": "float64", "bits": "3ff0000000000000\n"}),
                            ("decimal128", {"type": "decimal128", "coefficient": "1\n", "scale": 0})):
            self.error("invalid_schema", self.cell(dtype, cell))
        f = fixture("calculate")
        for target, key in ((f, "request_id"), (f["payload"], "command_digest"),
                            (f["payload"]["context"]["config"], "digest"),
                            (f["payload"]["context"]["dataset"], "revision")):
            original = target[key];target[key] += "\n"
            self.error("invalid_schema", f, request=True)
            target[key] = original


if __name__ == "__main__":
    unittest.main(verbosity=2)
