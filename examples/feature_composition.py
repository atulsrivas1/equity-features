"""Synthetic supplied-instance composition; missing dependencies stay explicit."""
from fractions import Fraction
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage,
    DataKind, EntityKey, HistoryContext, Parameter, PriceUnit, ReturnReference,
    SessionSpec, SourceBinding, WindowSpec,
)
from equity_feature_contracts.composition import CompositionSpec, FamilyResult
from equity_features.composition import compose_features
from equity_features.history import compute_history

sessions = tuple(SessionSpec("synthetic", f"S{i}", 10*i+1, 10*i+10, "supplied") for i in range(3))
context = HistoryContext(EntityKey("A", "S2"), "grid-v1", sessions, (Coverage(1, 1, True),)*3)
unit = PriceUnit(0, "USD")
timing = AvailabilitySpec(30, 35, 35)
batch = CanonicalBatch(DataKind.DAILY, (
    Column("instrument_id", ("A",)*3), Column("session_id", ("S0", "S1", "S2")),
    Column("start_ns", (1, 11, 21)), Column("end_ns", (10, 20, 30)),
    Column("close", (100, 110, 121)), Column("known_at_ns", (10, 20, 30)),
), BatchMetadata("synthetic", SourceBinding("synthetic", "r1", "v1", "prices-A"), Coverage(3, 3, True), unit))


def supplied(period: int) -> FamilyResult:
    config = ConfigSpec(f"return-h{period}", "v1", (Parameter("period", period), Parameter("evidence_limit", 3)),
                        sessions[-1], WindowSpec(period+1, "S2", ("S0", "S1", "S2"), "completed_eod"),
                        timing, price_unit=unit)
    result = compute_history(batch, config, context=context, feature_ids=("history.return",))
    return FamilyResult(f"h{period}", result, config, companion=ReturnReference(result, config, context))


short, long = supplied(1), supplied(2)
spec = CompositionSpec("synthetic", sessions[-1], timing, ("h2", "optional", "h1"))
bundle = compose_features((short, long), spec=spec)
assert bundle.components == (long, short) and bundle.missing_instances == ("optional",)
assert long.result.values[0].values[0] == float(Fraction(21, 100))
assert short.result.values[0].values[0] == float(Fraction(1, 10))
assert bundle.components[0].result is long.result
assert long.config.digest != short.config.digest
print("Supplied instances h1=1/10, h2=21/100 and explicit missing family verified.")
