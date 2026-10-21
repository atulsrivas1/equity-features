"""Standalone original C01 schedule and actual supplied provenance; no external I/O."""
import hashlib
import json

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, Coverage,
    DataKind, EntityKey, SessionSpec, SourceBinding, WindowSpec,
)
from equity_features.ef1 import build_ef1_config, compute_ef1

calendar = {"calendar_id": "C01", "revision": "R1", "timezone": "UTC",
            "target_date": "2026-01-02", "sessions": [["S", "2026-01-02", 10, 30]],
            "segments": [["premarket", 0, 10], ["regular", 10, 30], ["postmarket", 30, 40]],
            "scheduled_close_ns": 40, "early_close": True}
definition_bytes = json.dumps(calendar, ensure_ascii=True, sort_keys=True, separators=(",", ":")).encode("ascii")
columns = {"instrument_id": ("X",), "session_id": ("S",),
           "reference_id": ("c1:" + hashlib.sha256(definition_bytes).hexdigest(),),
           "fact_kind": ("ef1.calendar.provenance",), "text": ("supplied_schedule",),
           "effective_start_ns": (0,), "effective_end_ns": (40,), "known_at_ns": (5,)}
proof = CanonicalBatch(DataKind.REFERENCE, tuple(Column(k, v) for k, v in columns.items()),
                       BatchMetadata("SYN", SourceBinding("F", "R1", "ef1-reference-map1", "cp"),
                                     Coverage(1, 1, True), None))
config = build_ef1_config({"version": "ef1-context1", "producer": "clock", "calendar": calendar, "selection": {}},
                          session=SessionSpec("SYN", "S", 10, 30, "UTC", scheduled_close_ns=40, early_close=True),
                          window=WindowSpec(1, "S", ("S",), "completed_eod"),
                          availability=AvailabilitySpec(20, 20, 20), price_unit=None,
                          adjustment=AdjustmentSpec())
result = compute_ef1((proof,), config, entity=EntityKey("X", "S"))
assert {c.feature_id.rsplit(".", 1)[1]: c.values[0] for c in result.values} == {
    "phase": "regular", "early_close": True, "regular_elapsed_ns": 10,
    "regular_remaining_ns": 10, "regular_fraction": 0.5}
