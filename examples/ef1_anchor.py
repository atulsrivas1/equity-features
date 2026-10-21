"""Original tiny supplied anchor example. Source-authored; not executed at this stage."""
import hashlib
import json

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, Coverage,
    DataKind, EntityKey, InputScope, PriceUnit, SessionSpec, SourceBinding, WindowSpec,
)
from equity_features.ef1 import build_ef1_config, compute_ef1


def main() -> None:
    unit = PriceUnit(2, "USD")
    definition = {"anchor_id": "example", "reset_id": "r1", "start_ns": 10,
                  "selection_policy_id": "supplied-v1", "revision": "R1"}
    context = {"version": "ef1-context1", "producer": "anchor", "calendar": None,
               "selection": {"mode": "trades", "definition": definition}}
    config = build_ef1_config(context, session=SessionSpec("SYN", "S", 10, 30, "UTC"),
                             window=WindowSpec(1, "S", ("S",), "completed_eod"),
                             availability=AvailabilitySpec(20, 20, 20),
                             price_unit=unit, adjustment=AdjustmentSpec())
    trade_rows = {"instrument_id": ("X", "X"), "session_id": ("S", "S"),
                  "event_ns": (10, 15), "order_key": (0, 1), "event_id": ("a", "b"),
                  "eligible": (True, True), "price": (1000, 1300), "size": (2, 1),
                  "known_at_ns": (10, 15)}
    market = CanonicalBatch(DataKind.TRADE, tuple(Column(k, v) for k, v in trade_rows.items()),
                            BatchMetadata("SYN", SourceBinding("synthetic", "R1", "example-v1", "trades"),
                                          Coverage(2, 2, True), unit,
                                          scope=InputScope(10, 20, "example-eligible-v1")))
    canonical = json.dumps(definition, ensure_ascii=True, sort_keys=True,
                           separators=(",", ":"), allow_nan=False).encode("ascii")
    proof_rows = {"instrument_id": ("X",), "session_id": ("S",),
                  "reference_id": ("a1:" + hashlib.sha256(canonical).hexdigest(),),
                  "fact_kind": ("ef1.anchor.provenance",), "text": ("supplied_anchor",),
                  "effective_start_ns": (10,), "known_at_ns": (10,)}
    proof = CanonicalBatch(DataKind.REFERENCE, tuple(Column(k, v) for k, v in proof_rows.items()),
                           BatchMetadata("SYN", SourceBinding("synthetic", "R1", "ef1-reference-map1", "proof"),
                                         Coverage(1, 1, True), None))
    result = compute_ef1((market, proof), config, entity=EntityKey("X", "S"))
    print({column.feature_id: column.values[0] for column in result.values})
    # Independent expected: notional coefficient3300, volume3, VWAP11.0.


if __name__ == "__main__":
    main()
