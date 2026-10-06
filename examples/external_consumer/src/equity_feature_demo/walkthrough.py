"""Installed synthetic batch/stream/history/composition; no repository imports."""
from dataclasses import replace
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, CompositionSpec,
    ConfigSpec, Coverage, DataKind, EntityKey, FamilyResult, FeatureResult,
    HistoryContext, Parameter, PrefixCoverage, PriceUnit, ReturnReference,
    SessionSpec, SourceBinding, Status, StreamPopulation, WindowSpec,
)
from equity_features.composition import compose_features
from equity_features.history import compute_history
from equity_features.incremental import SessionAccumulator
from equity_features.session import compute_bars
from equity_feature_demo import fixture, main as custom_and_adapter


def values(result: FeatureResult) -> dict[str, object]:
    return {column.feature_id: column.values[0] for column in result.values}


def session_walkthrough() -> None:
    request = fixture()
    batch = request.inputs[0].batch
    config = replace(request.config, identity="walkthrough-bars", algorithm_version="v1")
    result = compute_bars(batch, config, entity=request.entity)
    actual = values(result)
    assert tuple(actual[name] for name in ("session.bar.open", "session.bar.high",
        "session.bar.low", "session.bar.close")) == (100.0, 104.0, 99.0, 103.0)
    assert actual["session.bar.volume"] == 500
    assert actual["session.bar.notional"] == 51200  # 20300+30900, original exact amounts.
    assert actual["session.price.range_fraction"] == 5/103
    absent = compute_bars(None, config, entity=request.entity)
    assert all(column.values == (None,) for column in absent.values)
    assert all(row.status == Status.MISSING_INPUT for row in absent.quality)

    def chunk(index: int) -> CanonicalBatch:
        return replace(batch, columns=tuple(Column(column.name, (column.values[index],))
            for column in batch.columns), metadata=replace(batch.metadata, coverage=Coverage(1, 1, True)))

    accumulator = SessionAccumulator("bars", config, entity=request.entity,
        population=StreamPopulation.from_batch(batch))
    accumulator.update(chunk(0), start_ordinal=0)
    prefix = accumulator.snapshot(PrefixCoverage(150, Coverage(1, 1, True)))
    assert values(prefix)["session.bar.close"] == 102.0
    assert prefix.metadata.availability.market_cutoff_ns == 150
    accumulator.update(chunk(1), start_ordinal=1)
    final = accumulator.finalize(PrefixCoverage(200, Coverage(2, 2, True)))
    assert values(final) == actual and final.quality == result.quality
    assert values(prefix)["session.bar.close"] == 102.0  # Returned prefix remains independent.
    print("Installed batch OHLC100/104/99/103; streamed prefix102/final parity; absent bars remain null.")


def historical_walkthrough() -> None:
    sessions = tuple(SessionSpec("demo", f"S{i}", 10*i+1, 10*i+10, "supplied") for i in range(3))
    context = HistoryContext(EntityKey("A", "S2"), "walkthrough-grid-v1", sessions, (Coverage(1, 1, True),)*3)
    unit = PriceUnit(0, "USD")
    timing = AvailabilitySpec(30, 35, 35)
    batch = CanonicalBatch(DataKind.DAILY, tuple(Column(name, data) for name, data in (
        ("instrument_id", ("A",)*3), ("session_id", ("S0", "S1", "S2")),
        ("start_ns", (1, 11, 21)), ("end_ns", (10, 20, 30)),
        ("close", (100, 110, 121)), ("known_at_ns", (10, 20, 30)),
    )), BatchMetadata("demo", SourceBinding("synthetic", "history1", "map1", "daily-A"),
        Coverage(3, 3, True), unit))

    def supplied(period: int) -> FamilyResult:
        config = ConfigSpec(f"walkthrough-h{period}", "v1", (Parameter("period", period),),
            sessions[-1], WindowSpec(period+1, "S2", ("S0", "S1", "S2"), "completed_eod"), timing, price_unit=unit)
        result = compute_history(batch, config, context=context, feature_ids=("history.return",))
        absent = compute_history(None, config, context=context, feature_ids=("history.return",))
        assert absent.values[0].values == (None,) and absent.quality[0].status == Status.MISSING_INPUT
        return FamilyResult(f"h{period}", result, config, companion=ReturnReference(result, config, context))

    short, long = supplied(1), supplied(2)
    assert short.result.values[0].values == (1/10,) and long.result.values[0].values == (21/100,)
    bundle = compose_features((short, long), spec=CompositionSpec("demo", sessions[-1], timing,
        ("h2", "missing", "h1")))
    assert bundle.components == (long, short) and bundle.missing_instances == ("missing",)
    assert bundle.components[0].result is long.result
    print("Installed history100/110/121 gives h1=1/10,h2=21/100; missing history/instance stay explicit.")


def main() -> None:
    session_walkthrough()
    historical_walkthrough()
    custom_and_adapter()


if __name__ == "__main__":
    main()
