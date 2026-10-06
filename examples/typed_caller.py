"""Typed supplied-input caller; execute only after installing the external demo."""
from equity_feature_contracts import (
    CanonicalBatch, CompositionSpec, ConfigSpec, ContractError, EntityKey,
    ErrorCode, FamilyResult, FeatureBundle, FeatureDefinition, FeatureResult,
    HistoryContext, Status, builtin_registry,
)
from equity_feature_contracts.adapter_kit import ConformanceCase, ConformanceReport, run_conformance
from equity_feature_contracts.adapters import SourceError, SourceErrorCode
from equity_features.composition import compose_features
from equity_features.custom import CustomRegistry, CustomRequest
from equity_features.history import compute_history
from equity_features.session import compute_bars
from equity_feature_demo import calculate, definition, fixture


def session(batch: CanonicalBatch | None, config: ConfigSpec, entity: EntityKey) -> FeatureResult:
    return compute_bars(batch, config, entity=entity)


def history(batch: CanonicalBatch | None, config: ConfigSpec, context: HistoryContext) -> FeatureResult:
    return compute_history(batch, config, context=context, feature_ids=("history.return",))


def collection(components: tuple[FamilyResult, ...], spec: CompositionSpec) -> FeatureBundle:
    return compose_features(components, spec=spec)


def discovery() -> tuple[FeatureDefinition, ...]:
    return builtin_registry().list_features(capability="batch")


def custom(request: CustomRequest) -> FeatureResult:
    registry = CustomRegistry("demo").register(definition(), calculate)
    return registry.compute("demo:range_over_open", request)


def conformance(cases: tuple[ConformanceCase, ...]) -> ConformanceReport:
    return run_conformance(cases)


def main() -> None:
    request = fixture()
    result = custom(request)
    assert result.values[0].values == (0.05,)
    assert result.quality[0].status == Status.AVAILABLE
    assert len(discovery()) == 39
    # Typed errors describe invalid calls, while valid unavailable results retain null/quality.
    try:
        builtin_registry().get("demo:unknown")
    except ContractError as error:
        assert error.code == ErrorCode.UNKNOWN_FEATURE
    try:
        conformance(())
    except SourceError as error:
        assert error.code == SourceErrorCode.SCHEMA
    print("Installed typed public caller/custom/discovery and stable error codes verified.")


if __name__ == "__main__":
    main()
