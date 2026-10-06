"""Synthetic supplied simple-return differences and explicit sector mapping."""
from fractions import Fraction
import math
from typing import cast
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage,
    DataKind, EntityKey, HistoryContext, Parameter, PriceUnit, RelativeSpec,
    ReturnReference, SectorBenchmark, SessionSpec, SourceBinding, Status, WindowSpec,
)
from equity_features.history import compute_history
from equity_features.policies import admit_classification
from equity_features.relative import compute_relative

sessions = (SessionSpec("synthetic", "S0", 1, 10, "supplied"), SessionSpec("synthetic", "S1", 11, 20, "supplied"))
unit = PriceUnit(0, "USD")
window = WindowSpec(2, "S1", ("S0", "S1"), "completed_eod")
availability = AvailabilitySpec(20, 25, 25)


def supplied(instrument: str, first: int, last: int) -> ReturnReference:
    context = HistoryContext(EntityKey(instrument, "S1"), "grid-v1", sessions, (Coverage(1, 1, True),)*2)
    config = ConfigSpec("return-"+instrument, "v1", (Parameter("period", 1), Parameter("evidence_limit", 2)),
                        sessions[-1], window, availability, price_unit=unit)
    batch = CanonicalBatch(DataKind.DAILY, (
        Column("instrument_id", (instrument,)*2), Column("session_id", ("S0", "S1")),
        Column("start_ns", (1, 11)), Column("end_ns", (10, 20)), Column("close", (first, last)),
        Column("known_at_ns", (10, 20))), BatchMetadata("synthetic",
        SourceBinding("fixture", "r1", "v1", "prices-"+instrument), Coverage(2, 2, True), unit))
    return ReturnReference(compute_history(batch, config, context=context, feature_ids=("history.return",)), config, context)


symbol, market, sector = supplied("A", 100, 110), supplied("M", 200, 210), supplied("T", 300, 321)
config = ConfigSpec("relative", "v1", (Parameter("period", 1), Parameter("evidence_limit", 12)),
                    sessions[-1], window, availability, price_unit=unit)
spec = RelativeSpec(symbol.context.entity, market.context.entity, SectorBenchmark("synthetic-sector", sector.context.entity), 11)
ids = ("relative.market_return", "relative.sector_return")
missing = compute_relative(symbol, market, sector, None, config, spec=spec, feature_ids=ids)
assert tuple(q.status for q in missing.quality) == (Status.AVAILABLE, Status.MISSING_INPUT)
references = CanonicalBatch(DataKind.REFERENCE, (
    Column("instrument_id", ("A",)), Column("session_id", ("S1",)), Column("reference_id", ("membership",)),
    Column("fact_kind", ("sector_membership",)), Column("effective_start_ns", (11,)),
    Column("text", ("synthetic-sector",)), Column("known_at_ns", (25,))),
    BatchMetadata("synthetic", SourceBinding("fixture", "r1", "v1", "membership"), Coverage(1, 1, True), None))
membership = admit_classification(references, config, entity=spec.entity, effective_ns=11, fact_kind="sector_membership")
result = compute_relative(symbol, market, sector, membership, config, spec=spec, feature_ids=ids)
assert all(q.status == Status.AVAILABLE for q in result.quality)
assert math.isclose(cast(float, result.values[0].values[0]), float(Fraction(1, 20)), rel_tol=1e-12, abs_tol=1e-12)
assert math.isclose(cast(float, result.values[1].values[0]), float(Fraction(3, 100)), rel_tol=1e-12, abs_tol=1e-12)
print("Supplied market spread1/20, sector spread3/100 and independent missing membership verified.")
