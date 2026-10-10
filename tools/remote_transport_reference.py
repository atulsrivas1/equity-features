"""EQ076 executable design reference, not an installed service or core codec.

Only owned JSON and local schemas are read. No dynamic Python deserialization,
network, grants, datasets or calculation callbacks. Downstream services must
implement and qualify this contract at their actual ingress/egress boundary.
"""
from __future__ import annotations

import hashlib
import json
import math
from pathlib import Path
import struct

from jsonschema import Draft202012Validator

SCHEMA = Path(__file__).resolve().parents[1] / "docs/schemas/remote-v1.schema.json"
I64_MIN, I64_MAX = -(1 << 63), (1 << 63) - 1
MAX_DEPTH, MAX_NODES = 32, 10_000


class WireError(ValueError):
    def __init__(self, code: str):
        self.code = code
        super().__init__(code)  # Never echo untrusted payloads or private paths.


def command_digest(payload: dict) -> str:
    """Wire identity is distinct from the unchanged canonical ConfigSpec digest."""
    command = {k: v for k, v in payload.items()
               if k not in ("command_digest", "idempotency_key")}
    text = json.dumps(command, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False)
    return hashlib.sha256(text.encode("ascii")).hexdigest()


def _integer(text: str, *, count: bool = False) -> int:
    value = int(text)
    if not (0 if count else I64_MIN) <= value <= I64_MAX:
        raise WireError("bounds")
    return value


def _walk(value, depth=0, counter=None, *, semantic=True):
    if counter is None:
        counter = [0]
    counter[0] += 1
    if counter[0] > MAX_NODES or depth > MAX_DEPTH:
        raise WireError("bounds")
    if isinstance(value, str) and any(0xD800 <= ord(c) <= 0xDFFF for c in value):
        raise WireError("invalid_json")
    if isinstance(value, dict):
        if semantic and value.get("type") == "int64":
            _integer(value["value"])
        elif semantic and value.get("type") == "float64":
            number = struct.unpack(">d", bytes.fromhex(value["bits"]))[0]
            if not math.isfinite(number):
                raise WireError("invalid_schema")
        elif semantic and value.get("type") == "decimal128":
            if type(value["scale"]) is not int:
                raise WireError("invalid_schema")
            if not -(10**38) < int(value["coefficient"]) < 10**38:
                raise WireError("bounds")
        for key, child in value.items():
            _walk(key, depth + 1, counter, semantic=semantic)
            _walk(child, depth + 1, counter, semantic=semantic)
    elif isinstance(value, list):
        for child in value:
            _walk(child, depth + 1, counter, semantic=semantic)


def _timing(context):
    a = context["availability"]
    c, k, e = (_integer(a[name]) for name in
               ("market_cutoff_ns", "knowledge_cutoff_ns", "evaluation_ns"))
    if a["mode"] == "known_at":
        if c > e or k > e or a["reconstruction_reason"] is not None:
            raise WireError("inconsistent_identity")
    elif a["reconstruction_reason"] is None:
        raise WireError("invalid_schema")
    features = [f["feature_id"] for f in context["features"]]
    if len(set(features)) != len(features):
        raise WireError("inconsistent_identity")


def _scope(scope):
    if _integer(scope["start_ns"]) >= _integer(scope["end_ns"]):
        raise WireError("bounds")


def _cell_type(cell):
    return None if cell is None else cell["type"]


def _columns(columns, quality=None):
    keys = set()
    names = set()
    for col in columns:
        name = col.get("feature_id", col.get("name"))
        if name in names:
            raise WireError("inconsistent_identity")
        names.add(name)
        dtype = col["dtype"]
        scalar = {"int64": "int64", "float64": "float64",
                  "decimal128": "decimal128", "string": "string", "bool": "bool"}
        for cell in col["values"]:
            if cell is not None and _cell_type(cell) != scalar.get(dtype, "record"):
                raise WireError("invalid_schema")
            records = {"breadth_counts": "BreadthCounts", "breadth_fraction": "BreadthFraction",
                       "time_weighted_spread": "TimeWeightedSpread", "quote_state_counts": "QuoteStateCounts",
                       "sampled_spread": "SampledSpread", "top_k_trades": "TopKTrades",
                       "interval_ohlcv": "IntervalOHLCV", "interval_volume_shares": "IntervalVolumeShares"}
            if cell is not None and dtype in records and cell["name"] != records[dtype]:
                raise WireError("invalid_schema")
        if quality is not None:
            if len(col["entities"]) != len(col["values"]):
                raise WireError("invalid_schema")
            for entity in col["entities"]:
                key = (entity["instrument_id"], entity["session_id"], name)
                if key in keys:
                    raise WireError("inconsistent_identity")
                keys.add(key)
    if quality is None:
        if len({len(c["values"]) for c in columns}) > 1:
            raise WireError("invalid_schema")
        return
    qkeys = set()
    for row in quality:
        entity = row["entity"]
        key = (entity["instrument_id"], entity["session_id"], row["feature_id"])
        if key in qkeys:
            raise WireError("inconsistent_identity")
        qkeys.add(key)
        observed = _integer(row["observed"], count=True)
        expected = None if row["expected"] is None else _integer(row["expected"], count=True)
        if expected is not None and observed > expected:
            raise WireError("bounds")
        if row["status"] == "available":
            if expected is None or expected != observed:
                raise WireError("inconsistent_identity")
        elif not row["reasons"]:
            raise WireError("invalid_schema")
    if qkeys != keys:
        raise WireError("inconsistent_identity")
    by_key = {(r["entity"]["instrument_id"], r["entity"]["session_id"], r["feature_id"]): r
              for r in quality}
    for col in columns:
        for entity, cell in zip(col["entities"], col["values"], strict=True):
            row = by_key[entity["instrument_id"], entity["session_id"], col["feature_id"]]
            if row["status"] == "available" and cell is None:
                raise WireError("invalid_schema")
            if row["status"] != "available" and cell is not None and col["dtype"] in (
                    "int64", "decimal128", "float64", "string", "bool"):
                raise WireError("invalid_schema")
    # Structured diagnostic exceptions and native identity admission require the
    # actual canonical validators; this design reference never constructs them.


def validate(value):
    _walk(value, semantic=False)  # Resource/Unicode preflight before recursive schema evaluation.
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    if next(Draft202012Validator(schema).iter_errors(value), None) is not None:
        raise WireError("invalid_schema")
    _walk(value)
    kind, payload = value["kind"], value["payload"]
    if kind == "request":
        op = payload["operation"]
        if "scope" in payload:
            _scope(payload["scope"])
        if op == "calculate":
            _timing(payload["context"])
            if payload["command_digest"] != command_digest(payload):
                raise WireError("inconsistent_identity")
    elif kind == "result":
        _timing(payload["context"])
        _columns(payload["columns"], payload["quality"])
        if payload["metadata"]["name"] != "ResultMetadata":
            raise WireError("invalid_schema")
        executed = {f["feature_id"]: f["algorithm_version"] for f in payload["executed_features"]}
        if len(executed) != len(payload["executed_features"]):
            raise WireError("inconsistent_identity")
        for f in payload["context"]["features"]:
            if executed.get(f["feature_id"]) != f["algorithm_version"]:
                raise WireError("inconsistent_identity")
        for c in payload["columns"]:
            if executed.get(c["feature_id"]) != c["algorithm_version"]:
                raise WireError("inconsistent_identity")
        fields = payload["metadata"]["fields"]
        required = {"namespace", "session_id", "availability", "config_digest", "inputs",
                    "backend_id", "backend_version", "evidence_limit", "schema_version", "math_policy_version"}
        if set(fields) != required:
            raise WireError("invalid_schema")
        expected = {"namespace": payload["context"]["namespace"],
                    "config_digest": payload["context"]["config"]["digest"],
                    "backend_id": payload["backend_id"], "backend_version": payload["backend_version"],
                    "math_policy_version": payload["context"]["math_policy_version"], "schema_version": "1"}
        for key, expected_value in expected.items():
            if fields[key] != {"type": "string", "value": expected_value}:
                raise WireError("inconsistent_identity")
        availability = fields["availability"]
        a = payload["context"]["availability"]
        expected_a = {key: (None if v is None else {"type": "int64", "value": v}
                            if key.endswith("_ns") else {"type": "string", "value": v})
                      for key, v in a.items()}
        if availability != {"type": "record", "name": "AvailabilitySpec", "fields": expected_a}:
            raise WireError("inconsistent_identity")
    elif kind == "slice":
        _scope(payload["scope"])
        _columns(payload["columns"])
    elif kind == "job":
        state = payload["state"]
        if (state == "succeeded") != (payload["result_id"] is not None):
            raise WireError("inconsistent_identity")
        if (state == "failed") != (payload["error"] is not None):
            raise WireError("inconsistent_identity")
    return value


def _unique(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise WireError("invalid_json")
        result[key] = value
    return result


def _constant(_value):
    raise WireError("invalid_json")


def decode(data: bytes, *, request: bool):
    if type(data) is not bytes or type(request) is not bool:
        raise WireError("invalid_json")
    if len(data) > (16_384 if request else 262_144):
        raise WireError("bounds")
    try:
        text = data.decode("utf-8")
        # Bound container depth before invoking the general-purpose parser.
        depth, quoted, escape = 0, False, False
        for c in text:
            if quoted:
                if escape:
                    escape = False
                elif c == "\\":
                    escape = True
                elif c == '"':
                    quoted = False
            elif c == '"':
                quoted = True
            elif c in "[{":
                depth += 1
                if depth > MAX_DEPTH:
                    raise WireError("bounds")
            elif c in "]}":
                depth -= 1
        value = json.loads(text, object_pairs_hook=_unique, parse_constant=_constant)
    except (UnicodeError, json.JSONDecodeError, RecursionError):
        raise WireError("invalid_json") from None
    if type(value) is not dict:
        raise WireError("invalid_schema")
    if value.get("schema") != "equity.remote" or value.get("version") != "1.0":
        raise WireError("incompatible_version")
    if request != (value.get("kind") == "request"):
        raise WireError("invalid_schema")
    return validate(value)


def verify_pair(request, response):
    """Compare result provenance to the accepted request, without claiming rights."""
    validate(request)
    validate(response)
    if request["kind"] != "request" or request["payload"]["operation"] != "calculate":
        raise WireError("invalid_schema")
    if response["kind"] != "result" or response["request_id"] != request["request_id"]:
        raise WireError("inconsistent_identity")
    for key in ("context", "command_digest"):
        if response["payload"][key] != request["payload"][key]:
            raise WireError("inconsistent_identity")
    scope = request["payload"]["scope"]
    for column in response["payload"]["columns"]:
        for entity in column["entities"]:
            if entity != {"instrument_id": scope["instrument_id"], "session_id": scope["session_id"]}:
                raise WireError("inconsistent_identity")
    if response["payload"]["metadata"]["fields"]["session_id"] != {"type": "string", "value": scope["session_id"]}:
        raise WireError("inconsistent_identity")
