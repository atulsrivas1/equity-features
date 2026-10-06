"""Separately packaged trusted calculator using public installed APIs only."""
from dataclasses import replace
from typing import cast
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage,
    DataKind, EntityKey, FeatureColumn, FeatureDefinition, FeatureResult, InputRequirement,
    InputScope, OutputField, Parameter, PriceUnit, QualityRow, Reason, SessionSpec,
    SourceBinding, Status, ValueType, WindowSpec,
)
from equity_features.custom import CustomDefinition, CustomInput, CustomRegistry, CustomRequest
from equity_features.session import compute_bars

FEATURE_ID = "demo:range_over_open"


def definition() -> CustomDefinition:
    return CustomDefinition(FeatureDefinition(
        FEATURE_ID, "Supplied session range divided by open",
        (InputRequirement("bars", "canonical:1", ("open", "high", "low", "close", "volume"), DataKind.BAR),),
        (OutputField(FEATURE_ID, "float64", "fraction"),),
        "(max(high)-min(low))/first(open)", "complete supplied session bars",
        "Use built-in admitted OHLC at supplied C/K/E; no future/unknown knowledge",
        "Unavailable operands propagate; zero open is not_applicable/zero_denominator",
        "docs/api/CUSTOM_FEATURES.md", algorithm_version="v2"),
        "equity-feature-demo", "0.1.0", "eligibility_policy supplied to admitted built-in bars",
        (("eligibility_policy", "str"),))


def calculate(request: CustomRequest) -> FeatureResult:
    builtin = compute_bars(request.inputs[0].batch, replace(request.config, algorithm_version="v1"), entity=request.entity)
    columns = {x.feature_id: x for x in builtin.values}
    quality = {x.feature_id: x for x in builtin.quality}
    names = ("session.bar.open", "session.bar.high", "session.bar.low")
    bad = next((quality[name] for name in names if quality[name].status != Status.AVAILABLE), None)
    value = None
    if bad is not None:
        q = replace(bad, feature_id=FEATURE_ID)
    else:
        operands = tuple(columns[name].values[0] for name in names)
        assert all(type(x) is float for x in operands)
        opening, high, low = (cast(float, x) for x in operands)
        if opening == 0:
            q = QualityRow(request.entity, FEATURE_ID, Status.NOT_APPLICABLE,
                           quality[names[0]].expected, quality[names[0]].observed, (Reason.ZERO_DENOMINATOR,))
        else:
            value = (high-low)/opening
            q = replace(quality[names[0]], feature_id=FEATURE_ID)
    return FeatureResult((FeatureColumn(FEATURE_ID, "v2", ValueType.FLOAT64, "fraction", (request.entity,), (value,)),),
                         (q,), request.metadata(definition()))


def fixture() -> CustomRequest:
    unit = PriceUnit(0, "USD")
    config = ConfigSpec(FEATURE_ID, "v2", (Parameter("eligibility_policy", "example-v1"),),
        SessionSpec("demo", "S", 100, 200, "caller-supplied"),
        WindowSpec(1, "S", ("P", "S")), AvailabilitySpec(200, 210, 210), price_unit=unit)
    batch = CanonicalBatch(DataKind.BAR, tuple(Column(name, values) for name, values in (
        ("instrument_id", ("A", "A")), ("session_id", ("S", "S")),
        ("start_ns", (100, 150)), ("end_ns", (150, 200)), ("known_at_ns", (150, 210)),
        ("open", (100, 102)), ("high", (103, 104)), ("low", (99, 101)), ("close", (102, 103)),
        ("volume", (200, 300)), ("actual_notional", (20300, 30900)),
    )), BatchMetadata("demo", SourceBinding("synthetic", "snapshot1", "map1", "bars1"),
        Coverage(2, 2, True), unit, scope=InputScope(100, 200, "example-v1")))
    return CustomRequest((CustomInput("bars", batch),), config, EntityKey("A", "S"))


def main() -> None:
    request = fixture()
    registry = CustomRegistry("demo").register(definition(), calculate)
    assert registry.get(FEATURE_ID).definition.algorithm_version == "v2"
    result = registry.compute(FEATURE_ID, request)
    assert result.values[0].values == (0.05,)  # Independent 5/100 golden.
    builtin = compute_bars(request.inputs[0].batch, replace(request.config, algorithm_version="v1"), entity=request.entity)
    values = {x.feature_id: x.values[0] for x in builtin.values}
    assert values["session.price.range_fraction"] == 5/103
    assert len(registry.list_features()) == 1 and len(CustomRegistry("demo").list_features()) == 0
    print("Installed external custom range/open=0.05; unchanged built-in range/close=5/103 verified.")
