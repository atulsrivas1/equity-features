"""PROPOSED and UNEXECUTED: SDK carriage of a synthetic expected literal only.

This example never calls the unimplemented first-trade producer and never
calculates its expected result. Run only in an explicitly qualified compatible
environment; no runtime validation is claimed by this source file.
"""
from dataclasses import asdict
import json
from pathlib import Path

import equity_feature_contracts as c
import equity_feature_io_sdk as sdk


def metadata(d):
    return c.BatchMetadata(
        namespace=d["namespace"], source=c.SourceBinding(**d["source"]),
        coverage=c.Coverage(**d["coverage"]),
        price_unit=None if d["price_unit"] is None else c.PriceUnit(**d["price_unit"]),
        adjustment=c.AdjustmentSpec(**d["adjustment"]), sampling=d["sampling"],
        quantity_unit=d["quantity_unit"], ordering=d["ordering"],
        duplicate_policy=d["duplicate_policy"],
        scope=None if d["scope"] is None else c.InputScope(**d["scope"]),
        interval_coverage=tuple(c.IntervalCoverage(
            name=x["name"], start_ns=x["start_ns"], end_ns=x["end_ns"],
            coverage=c.Coverage(**x["coverage"])) for x in d["interval_coverage"]),
    )


def main():
    literal = json.loads(Path(__file__).with_name("SAMPLE_EXPECTED_RESULT.json").read_text(encoding="utf-8"))
    rm = literal["metadata"]
    md = c.ResultMetadata(
        namespace=rm["namespace"], session_id=rm["session_id"],
        availability=c.AvailabilitySpec(**rm["availability"]),
        config_digest=rm["config_digest"],
        inputs=tuple(c.InputBinding(x["role"], c.DataKind(x["kind"]),
            metadata(x["metadata"]), x["schema_version"]) for x in rm["inputs"]),
        backend_id=rm["backend_id"], backend_version=rm["backend_version"],
        evidence_limit=rm["evidence_limit"], schema_version=rm["schema_version"],
        math_policy_version=rm["math_policy_version"],
    )
    result = c.FeatureResult(
        values=tuple(c.FeatureColumn(x["feature_id"], x["algorithm_version"],
            c.ValueType(x["dtype"]), x["unit"],
            tuple(c.EntityKey(**e) for e in x["entities"]), tuple(x["values"]),
            x["schema_version"]) for x in literal["values"]),
        quality=tuple(c.QualityRow(c.EntityKey(**x["entity"]), x["feature_id"],
            c.Status(x["status"]), x["expected"], x["observed"],
            tuple(c.Reason(r) for r in x["reasons"])) for x in literal["quality"]),
        metadata=md,
        evidence=tuple(c.EvidenceRow(**{**x, "entity": c.EntityKey(**x["entity"]),
            "exclusion_reason": None if x["exclusion_reason"] is None else
            c.Reason(x["exclusion_reason"])}) for x in literal["evidence"]),
    )
    wire = sdk.encode_result(result)
    decoded = sdk.decode_result(wire)
    compact = lambda x: json.dumps(x, sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)
    assert compact(asdict(decoded)) == compact(literal)
    assert sdk.encode_result(decoded) == wire
    print("Synthetic expected literal SDK roundtrip passed; producer mathematics was not executed.")


if __name__ == "__main__":
    main()
