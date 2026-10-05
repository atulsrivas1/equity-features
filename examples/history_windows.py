"""Synthetic governed horizon return and target-excluding prior extrema."""
from fractions import Fraction
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Cell, Column, ConfigSpec,
    Coverage, DataKind, EntityKey, HistoryContext, Parameter, PriceUnit, SessionSpec,
    SourceBinding, Status, WindowSpec,
)
from equity_features.history import compute_history

sessions = tuple(SessionSpec("demo", f"S{i}", 10*i+1, 10*i+10, "supplied") for i in range(6))
entity = EntityKey("A", "S5")
context = HistoryContext(entity, "synthetic-grid-v1", sessions, (Coverage(1, 1, True),)*6)
unit = PriceUnit(0, "USD")
fields: dict[str, tuple[Cell, ...]] = {
    "instrument_id": ("A",)*6, "session_id": tuple(s.session_id for s in sessions),
    "start_ns": tuple(s.open_ns for s in sessions), "end_ns": tuple(s.close_ns for s in sessions),
    "close": (100, 110, 105, 120, 115, 130), "high": (102, 112, 111, 122, 121, 132),
    "low": (98, 99, 103, 104, 113, 114), "known_at_ns": tuple(s.close_ns for s in sessions),
}
batch = CanonicalBatch(DataKind.DAILY, tuple(Column(name, values) for name, values in fields.items()),
                       BatchMetadata("demo", SourceBinding("synthetic", "history-r1", "v1", "prices"),
                                     Coverage(6, 6, True), unit))
ids = tuple(s.session_id for s in sessions)
returns_config = ConfigSpec("horizon3", "v1", (Parameter("period", 3),), sessions[-1],
                            WindowSpec(4, "S5", ids, "completed_eod"), AvailabilitySpec(60, 60, 60), price_unit=unit)
returns = compute_history(batch, returns_config, context=context, feature_ids=("history.return",))
assert returns.quality[0].status == Status.AVAILABLE
assert returns.values[0].values == (float(Fraction(5, 21)),)
prior_config = ConfigSpec("prior3", "v1", (Parameter("period", 3),), sessions[-1],
                          WindowSpec(3, "S5", ids, "prior_only"), AvailabilitySpec(51, 60, 60), price_unit=unit)
extrema = compute_history(batch, prior_config, context=context,
                          feature_ids=("history.prior_high", "history.prior_low"))
assert all(q.status == Status.AVAILABLE for q in extrema.quality)
assert tuple(c.values for c in extrema.values) == ((122.0,), (103.0,))
print("Governed h3 return5/21 and prior high122/low103 before target close verified.")
