"""Synthetic declared-universe breadth; no dependency acquisition."""
from dataclasses import replace
from fractions import Fraction
from equity_feature_contracts import (
    BatchMetadata, BreadthCounts, BreadthFraction, BreadthSpec, CanonicalBatch, Column,
    CompletedClose, ConfigSpec, Coverage, DataKind, DeclaredUniverseSpec, EntityKey,
    HistoryContext, InputBinding, InputScope, MemberFeatures, Parameter, PriceUnit,
    ReturnReference, SMAInput, SessionSpec, SourceBinding, Status, WindowSpec, AvailabilitySpec,
)
from equity_features.breadth import compute_above_sma_breadth, compute_direction_breadth
from equity_features.history import compute_history, compute_sma_reference

sessions = (SessionSpec("synthetic", "S0", 1, 10, "supplied"), SessionSpec("synthetic", "S1", 11, 20, "supplied"))
base = ConfigSpec("breadth", "v1", (Parameter("period", 1), Parameter("evidence_limit", 20)), sessions[1],
                  WindowSpec(2, "S1", ("S0", "S1"), "completed_eod"), AvailabilitySpec(20, 25, 25), price_unit=PriceUnit(0, "USD"))
universe = DeclaredUniverseSpec("synthetic", "S1", "U", "synthetic-membership-r1", 11, ("a", "b", "c", "d"))
spec = BreadthSpec(EntityKey("U", "S1"))
direction_members = []
above_members = []
for name, last, close in (("a", 110, 11), ("b", 95, 9), ("c", 100, 10)):
    entity = EntityKey(name, "S1")
    context = HistoryContext(entity, "grid-v1", sessions, (Coverage(1, 1, True),)*2)
    def batch(prices: tuple[int, int], source_id: str) -> CanonicalBatch:
        return CanonicalBatch(DataKind.DAILY, (Column("instrument_id", (name, name)), Column("session_id", ("S0", "S1")),
            Column("start_ns", (1, 11)), Column("end_ns", (10, 20)), Column("close", prices), Column("known_at_ns", (10, 20))),
            BatchMetadata("synthetic", SourceBinding("example", "r1", "v1", source_id), Coverage(2, 2, True), base.price_unit))
    return_config = replace(base, identity="return-"+name)
    result = compute_history(batch((100, last), "return-prices-"+name), return_config, context=context, feature_ids=("history.return",))
    direction_members.append(MemberFeatures(entity, return_reference=ReturnReference(result, return_config, context)))
    sma_config = replace(base, identity="sma-"+name, parameters=(Parameter("period", 2), Parameter("evidence_limit", 20)))
    sma_batch = batch((9, 11), "sma-prices-"+name)
    sma = SMAInput(compute_sma_reference(sma_batch, sma_config, context=context), sma_config, context)
    close_source = InputBinding("completed_close", DataKind.DAILY, replace(sma_batch.metadata, source=SourceBinding("example", "r1", "v1", "close-"+name)))
    target = CompletedClose(entity, close, 20, close_source, 1, InputScope(11, 20, "supplied"), Coverage(1, 1, True))
    above_members.append(MemberFeatures(entity, sma=sma, close=target))
direction = compute_direction_breadth(tuple(direction_members), base, universe=universe, spec=spec)
above_config = replace(base, identity="above", parameters=(Parameter("period", 2), Parameter("evidence_limit", 20)))
above = compute_above_sma_breadth(tuple(above_members), above_config, universe=universe, spec=spec)
counts = direction.result.values[0].values[0]
fraction = above.result.values[0].values[0]
assert counts == BreadthCounts(1, 1, 1, 4) and isinstance(counts, BreadthCounts) and counts.coverage == Fraction(3, 4)
assert fraction == BreadthFraction(1, 3, 4) and isinstance(fraction, BreadthFraction) and fraction.fraction == Fraction(1, 3)
assert direction.result.quality[0].status == above.result.quality[0].status == Status.INCOMPLETE_COVERAGE
assert direction.exclusions[0].entity == above.exclusions[0].entity == EntityKey("d", "S1")
print("Declared U direction1/1/1 coverage3/4 and above-SMA1/3 with missing member exclusion verified.")
