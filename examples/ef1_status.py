"""Synthetic supplied current state; all provenance is explicit canonical input."""
import hashlib
import json

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, Coverage,
    DataKind, EntityKey, SessionSpec, SourceBinding, WindowSpec,
)
from equity_features.ef1 import build_ef1_config, compute_ef1

calendar = {"calendar_id": "synthetic", "revision": "R1", "timezone": "UTC",
    "target_date": "2026-01-02", "sessions": [["S", "2026-01-02", 10, 30]],
    "segments": [["regular", 10, 30]], "scheduled_close_ns": 30, "early_close": False}
config = build_ef1_config({"version": "ef1-context1", "producer": "status", "calendar": calendar,
    "selection": {"dimension": "trading", "epoch": "e",
        "seed_reference_id": "s1:t:ZQ:0000000000000000000:c2VlZA", "max_age_ns": None}},
    session=SessionSpec("SYN", "S", 10, 30, "UTC", scheduled_close_ns=30),
    window=WindowSpec(1, "S", ("S",), "completed_eod"), availability=AvailabilitySpec(17, 17, 20),
    price_unit=None, adjustment=AdjustmentSpec())


def reference(input_id, rows):
    names = ("reference_id", "fact_kind", "effective_start_ns", "effective_end_ns", "text", "known_at_ns")
    values = {"instrument_id": ("X",) * len(rows), "session_id": ("S",) * len(rows)}
    values.update({name: tuple(row[index] for row in rows) for index, name in enumerate(names)})
    return CanonicalBatch(DataKind.REFERENCE, tuple(Column(k, v) for k, v in values.items()),
        BatchMetadata("SYN", SourceBinding("synthetic", "R1", "ef1-reference-map1", input_id),
                      Coverage(len(rows), len(rows), True), None))


calendar_id = "c1:" + hashlib.sha256(json.dumps(calendar, ensure_ascii=True, sort_keys=True,
    separators=(",", ":")).encode("ascii")).hexdigest()
inputs = (
    reference("cp", ((calendar_id, "ef1.calendar.provenance", 10, 30, "supplied_schedule", 5),)),
    reference("st", (("s1:t:ZQ:0000000000000000000:c2VlZA", "ef1.status.trading", 8, None, "active", 8),
        ("s1:t:ZQ:0000000000000000001:aGFsdA", "ef1.status.trading", 12, None, "halted", 12),
        ("s1:t:ZQ:0000000000000000002:cmVzdW1l", "ef1.status.trading", 16, None, "active", 16))),
    reference("sp", (("p1:t:ZQ:c3Q:cHJlZg", "ef1.status.prefix_complete", 8, 20, "t", 8),)),
    reference("sv", (("p1:t:ZQ:c3Q:dmFsaWQ", "ef1.status.validity", 8, 21, "t", 8),)),
)
result = compute_ef1(inputs, config, entity=EntityKey("X", "S"))
for column in result.values:
    print(column.feature_id, column.values[0])
# Independent expected values: admission_reason=none, admission_state=ready,
# trading_age_ns=1, trading_state=active. Source authoring is not an execution receipt.
