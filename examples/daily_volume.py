"""Synthetic prior-only volume baseline and explicitly supplied intraday prefix."""
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage,
    DataKind, EntityKey, HistoryContext, InputBinding, InputScope, Parameter, PriceUnit,
    SessionSpec, SourceBinding, Status, TargetVolume, WindowSpec,
)
from equity_features.volume import compute_daily_baseline, compute_relative_volume

sessions = tuple(SessionSpec("synthetic", f"S{i}", 10*i+1, 10*i+10, "supplied") for i in range(4))
ids = tuple(s.session_id for s in sessions)
unit = PriceUnit(0, "USD")  # Required canonical market metadata; no price fields consumed.
batch = CanonicalBatch(DataKind.DAILY, (
    Column("instrument_id", ("A",)*4), Column("session_id", ids),
    Column("start_ns", tuple(s.open_ns for s in sessions)),
    Column("end_ns", tuple(s.close_ns for s in sessions)),
    Column("volume", (100, 200, 300, 9000)), Column("known_at_ns", (10, 20, 30, 40))),
    BatchMetadata("synthetic", SourceBinding("fixture", "r1", "v1", "daily-volumes"), Coverage(4, 4, True), unit))
context = HistoryContext(EntityKey("A", "S3"), "grid-v1", sessions, (Coverage(1, 1, True),)*4)
config = ConfigSpec("prior-volume3", "v1", (Parameter("period", 3), Parameter("evidence_limit", 4)),
                    sessions[-1], WindowSpec(3, "S3", ids, "prior_only"), AvailabilitySpec(35, 40, 40), price_unit=unit)
baseline = compute_daily_baseline(batch, config, context=context)
assert (baseline.numerator, baseline.denominator) == (600, 3)
assert baseline.result.values[0].values == (200.0,)
source = InputBinding("target_volume", DataKind.BAR, BatchMetadata("synthetic",
                      SourceBinding("fixture", "r1", "v1", "prefix-volume"), Coverage(1, 1, True), unit))
prefix = TargetVolume(context.entity, 500, 35, source, 0, InputScope(31, 35, "all"),
                      Coverage(1, 1, True), "observed_prefix", "raw_shares")
ratio = compute_relative_volume(prefix, baseline, config, context=context)
assert ratio.values[0].values == (2.5,)
assert ratio.quality[0].status == Status.AVAILABLE
assert ratio.evidence[-1].event_ns == 35
print("Prior-only volume sum600/count3=200 and supplied observed-prefix ratio5/2 verified.")
