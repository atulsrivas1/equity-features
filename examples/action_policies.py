"""Synthetic exact split and independent point-in-time sector admission."""
from equity_feature_contracts import (
    ActionPolicy, AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch,
    Cell, Column, ConfigSpec, Coverage, DataKind, EntityKey, PriceUnit, SessionSpec,
    SourceBinding, Status, WindowSpec,
)
from equity_features.policies import admit_classification, apply_action_policy

unit = PriceUnit(2, "USD")
adjustment = AdjustmentSpec("split", "split-factors-v1", "actions-r1", "S2")
policy = ActionPolicy(adjustment, 200, quantity_basis="split_shares")
config = ConfigSpec("synthetic-policy", "v1", (), SessionSpec("demo", "S2", 100, 200, "supplied"),
                    WindowSpec(2, "S2", ("S1", "S2"), "completed_eod"),
                    AvailabilitySpec(200, 210, 210), adjustment, unit)
entity = EntityKey("A", "S2")
price_fields: dict[str, tuple[Cell, ...]] = {
    "instrument_id": ("A", "A"), "session_id": ("S1", "S2"), "start_ns": (0, 100),
    "end_ns": (100, 200), "close": (10000, 5000), "volume": (10, 20),
    "actual_notional": (100000, 100000), "known_at_ns": (210, 210),
}
prices = CanonicalBatch(DataKind.DAILY, tuple(Column(name, values) for name, values in price_fields.items()),
                       BatchMetadata("demo", SourceBinding("synthetic", "prices-r1", "v1", "prices"),
                         Coverage(2, 2, True), unit))
reference_fields: dict[str, tuple[Cell, ...]] = {
    "instrument_id": ("A", "A"), "session_id": ("S2", "S2"),
    "reference_id": ("sector", "split"), "fact_kind": ("sector_membership", "split_factor"),
    "effective_start_ns": (100, 100), "factor_num": (None, 1), "factor_den": (None, 2),
    "text": ("synthetic-sector", None), "known_at_ns": (210, 210),
}
references = CanonicalBatch(DataKind.REFERENCE, tuple(Column(name, values) for name, values in reference_fields.items()),
                           BatchMetadata("demo", SourceBinding("synthetic", "actions-r1", "v1", "references"),
                         Coverage(2, 2, True), None))
application = apply_action_policy(prices, references, policy, config, entity=entity)
assert application.status == Status.AVAILABLE and application.batch is not None
close = application.batch.column("close")
volume = application.batch.column("volume")
notional = application.batch.column("actual_notional")
assert close is not None and close.values == (5000, 5000)
assert volume is not None and volume.values == (20, 20)
assert notional is not None and notional.values == (100000, 100000)
classification = admit_classification(references, config, entity=entity, effective_ns=100,
                                      fact_kind="sector_membership")
assert classification.text == "synthetic-sector"
print("Exact supplied split, unchanged notional and point-in-time classification verified.")
