"""Run the first independently frozen synthetic regular-BAR request from source.

Fixture loading is example-only; the pure library performs no acquisition.
Run from the repository with contracts/features source paths on PYTHONPATH.
"""
from dataclasses import asdict
import json
from pathlib import Path

from equity_feature_contracts import (
    AdjustmentSpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage,
    DataKind, EntityKey, InputScope, IntervalCoverage, PriceUnit, SourceBinding,
)
from equity_features.ef1 import compute_ef1


def main() -> None:
    packet = json.loads((Path(__file__).resolve().parents[1] /
        "docs/ef1/regular_bar_prices/REGULAR_BAR_PRICES_ORACLE.json").read_text())["packets"][0]
    batches = []
    for slot in packet["role_slots"]:
        raw = slot["batch"]
        if raw is None:
            batches.append(None)
            continue
        meta = dict(raw["metadata"])
        meta["source"] = SourceBinding(**meta["source"])
        meta["coverage"] = Coverage(**meta["coverage"])
        meta["price_unit"] = None if meta["price_unit"] is None else PriceUnit(**meta["price_unit"])
        meta["adjustment"] = AdjustmentSpec(**meta["adjustment"])
        meta["scope"] = None if meta["scope"] is None else InputScope(**meta["scope"])
        meta["interval_coverage"] = tuple(IntervalCoverage(row["name"], row["start_ns"], row["end_ns"],
            Coverage(**row["coverage"])) for row in meta["interval_coverage"])
        batches.append(CanonicalBatch(DataKind(raw["kind"]),
            tuple(Column(col["name"], tuple(col["values"])) for col in raw["columns"]), BatchMetadata(**meta)))
    result = compute_ef1(batches, ConfigSpec.from_json(json.dumps(packet["config"])), entity=EntityKey(**packet["entity"]))
    literal = json.loads(json.dumps(asdict(result)))
    assert literal == packet["expected_result"]
    print(json.dumps(literal, sort_keys=True))


if __name__ == "__main__":
    main()
