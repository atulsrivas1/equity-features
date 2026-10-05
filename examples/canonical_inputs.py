"""Synthetic installed-artifact example, no source access."""
from equity_feature_contracts import (
    BatchMetadata, CanonicalBatch, Column, Coverage, DataKind,
    PriceUnit, SourceBinding,
)
meta = BatchMetadata("demo:instrument:v1",
    SourceBinding("synthetic", "snapshot1", "map1", "input1"),
    Coverage(1, 1, True), PriceUnit(4, "USD"))
trade = CanonicalBatch(DataKind.TRADE, (
    Column("instrument_id", ("A",)), Column("session_id", ("S",)),
    Column("event_ns", (1700000000000000001,)), Column("order_key", (1,)),
    Column("event_id", ("e1",)), Column("eligible", (True,)),
    Column("price", (1234500,)), Column("size", (10,)),
    Column("known_at_ns", (None,)),
), meta)

from equity_feature_contracts.columnar import from_arrow, to_arrow
assert from_arrow(to_arrow(trade)) == trade
assert trade.column("price").values == (1234500,)
print("Canonical synthetic input and exact Arrow round trip verified")

from equity_feature_contracts import (
    AvailabilitySpec, ConfigSpec, Parameter, SessionSpec, WindowSpec,
)
config = ConfigSpec("demo:volume-baseline", "v1", (Parameter("window", 2),),
    SessionSpec("demo", "S3", 100, 200, "caller-zone"),
    WindowSpec(2, "S3", ("S1", "missing", "S3", "future")),
    AvailabilitySpec(200, 210, 210))
assert config.window.selected_sessions() == ("S1", "missing")
assert config.availability.knowledge_reason(None) == "unknown_availability"
assert ConfigSpec.from_json(config.to_json()) == config
assert len(config.digest) == 64

print("Supplied specifications and canonical configuration verified",config.digest)

from equity_feature_contracts import (
    EntityKey, EvidenceRow, FeatureColumn, FeatureResult, InputBinding,
    QualityRow, Reason, ResultMetadata, Status, ValueType,
)
from equity_feature_contracts.columnar import to_arrow_result
stamp = trade.column("event_ns").values[0]
result_config = ConfigSpec("demo:trade-count", "v1", (),
    SessionSpec(meta.namespace, "S", stamp - 100, stamp + 100, "caller-zone"),
    WindowSpec(2, "S", ("P1", "P2", "S")), AvailabilitySpec(stamp+1,stamp+2,stamp+2))
entity = EntityKey("A", "S")
result_metadata = ResultMetadata(meta.namespace, "S", result_config.availability,
    result_config.digest, (InputBinding("trades", DataKind.TRADE, meta),),
    "caller:synthetic", "v1", 1)
supplied_result = FeatureResult(
    (FeatureColumn("demo:trade-count", "v1", ValueType.INT64, "count", (entity,), (None,)),),
    (QualityRow(entity,"demo:trade-count",Status.MISSING_INPUT,1,0,(Reason.UNKNOWN_AVAILABILITY,)),),
    result_metadata,
    (EvidenceRow(entity,"demo:trade-count",meta.source.input_id,"e1",stamp,None,
        use="excluded",exclusion_reason=Reason.UNKNOWN_AVAILABILITY),))
arrow_result = to_arrow_result(supplied_result)
assert arrow_result["quality"]["status"].to_pylist() == ["missing_input"]
assert supplied_result.values[0].values == (None,)
print("Typed supplied result, unavailable scalar and excluded evidence verified")

from equity_feature_contracts import validate_batch, normalize_batch, quantize_float_prices
report = validate_batch(trade, session=result_config.session,
    availability=result_config.availability)
assert report.knowledge_exclusions[0].reason == Reason.UNKNOWN_AVAILABILITY
scaled = normalize_batch(trade, price_unit=PriceUnit(5,"USD"))
assert scaled.batch.column("price").values == (12345000,)
assert scaled.batch.metadata.source.input_id != trade.metadata.source.input_id
assert trade.column("price").values == (1234500,)
quantized = quantize_float_prices((0.1,None), unit=PriceUnit(4,"USD"),
    interpretation="decimal_repr", rounding="exact")
assert quantized.values == (1000,None)
print("Semantic validation and explicit owned normalization verified")

from dataclasses import replace
from equity_features.registry import builtin_registry, Registry
catalog = builtin_registry()
assert len(catalog.list_features()) == 39
assert len(catalog.list_features(capability="batch")) == 23
assert len(catalog.list_features(capability="update")) == 23
assert len(catalog.list_features(capability="restore")) == 23
assert len(catalog.list_features(capability="merge")) == 22
prototype = catalog.get("history.sma")
research = Registry("research")
scoped = research.with_definition(replace(prototype, feature_id="research:sma_metadata", planned_release="R3"))
assert len(research.list_features()) == 39 and len(scoped.list_features()) == 40
assert Registry.from_json(scoped.to_json()) == scoped
print("39-ID discovery and immutable caller-scoped metadata registration verified")
