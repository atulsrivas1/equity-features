"""Explicit trusted local batch extensions; no executable discovery or serialization."""
from __future__ import annotations

from dataclasses import dataclass, fields, replace
import json
from typing import Any, Callable, Protocol, cast

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, BreadthCounts, BreadthFraction,
    CanonicalBatch, Capabilities, ConfigSpec, ContractError, Coverage, EntityKey, ErrorCode,
    EvidenceRow, FeatureColumn, InputScope, IntervalCoverage, IntervalOHLCV, IntervalOHLCVRow,
    IntervalSpec, IntervalVolumeShareRow, IntervalVolumeShares, PriceUnit, QualityRow,
    QuoteDurations, QuoteObservation, QuoteStateCounts, Reason, SampledSpread, SourceBinding,
    Status, TimeWeightedSpread, TopKTradeRow, TopKTrades, ValueType, DataKind,
    FeatureDefinition, FeatureResult, InputBinding, Registry, ResultMetadata,
    validate_batch,
)


_RESULT_COMPONENTS = (
    FeatureResult, FeatureColumn, QualityRow, EntityKey, ResultMetadata, InputBinding,
    AvailabilitySpec, BatchMetadata, SourceBinding, Coverage, PriceUnit, AdjustmentSpec,
    InputScope, IntervalCoverage, IntervalSpec, BreadthCounts, BreadthFraction,
    IntervalOHLCV, IntervalOHLCVRow, IntervalVolumeShares, IntervalVolumeShareRow,
    TopKTrades, TopKTradeRow, QuoteStateCounts, QuoteObservation, SampledSpread,
    QuoteDurations, TimeWeightedSpread,
)


def _readmit(value: object, depth: int = 0) -> object:
    """Reconstruct only owned result contract types, including every nested component."""
    if depth > 32:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "cyclic/overdeep result component")
    cls = type(value)
    if value is None or cls in (str, int, float, bool, Status, Reason, ValueType, DataKind):
        return value
    if cls in (tuple, list):
        return tuple(_readmit(x, depth + 1) for x in cast(tuple[object, ...], value))
    if cls not in _RESULT_COMPONENTS:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "unsupported nested result component")
    try:
        constructor = cast(Callable[..., object], cls)
        return constructor(**{f.name: _readmit(value.__dict__[f.name], depth + 1) for f in fields(cast(Any, cls))})
    except ContractError:
        raise
    except (TypeError, ValueError, AttributeError, KeyError, OverflowError) as error:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "malformed nested result component") from error


@dataclass(frozen=True)
class CustomDefinition:
    """Discovery metadata and actual supported modes for one trusted calculator."""

    definition: FeatureDefinition
    implementation_id: str
    implementation_version: str
    config_rule: str
    parameter_types: tuple[tuple[str, str], ...] = ()
    capabilities: Capabilities = Capabilities(batch=True)

    def __post_init__(self) -> None:
        if type(self.definition) is not FeatureDefinition:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed custom definition required")
        for value in (self.implementation_id, self.implementation_version, self.config_rule):
            if type(value) is not str or not value.strip():
                raise ContractError(ErrorCode.INVALID_SCHEMA, "implementation/config metadata required")
        if self.definition.capabilities != Capabilities():
            raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY, "built-in metadata cannot certify custom execution")
        if type(self.capabilities) is not Capabilities or self.capabilities != Capabilities(batch=True):
            raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY, "custom execution currently supports batch only")
        if any(r.schema_id != "canonical:1" for r in self.definition.requirements):
            raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY, "custom inputs currently support canonical:1 only")
        if len(self.definition.outputs) != 1 or self.definition.outputs[0].name != self.definition.feature_id:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "one output named by the custom feature ID required")
        if self.definition.outputs[0].dtype == "evidence:1":
            raise ContractError(ErrorCode.INVALID_SCHEMA, "evidence is not a value column")
        if type(self.parameter_types) not in (tuple, list):
            raise ContractError(ErrorCode.INVALID_CONFIG, "concrete parameter schema required")
        for item in self.parameter_types:
            if (type(item) is not tuple or len(item) != 2 or type(item[0]) is not str
                    or not item[0].strip() or item[1] not in ("int", "float", "str", "bool")):
                raise ContractError(ErrorCode.INVALID_CONFIG, "named primitive parameter types required")
        if len({x[0] for x in self.parameter_types}) != len(self.parameter_types):
            raise ContractError(ErrorCode.DUPLICATE, "duplicate parameter name")
        object.__setattr__(self, "parameter_types", tuple(sorted(self.parameter_types)))

    def to_json(self) -> str:
        """Metadata only; this text cannot recreate an executable registration."""
        return json.dumps({"definition": json.loads(self.definition.to_json()),
                           "implementation_id": self.implementation_id,
                           "implementation_version": self.implementation_version,
                           "config_rule": self.config_rule, "parameter_types": self.parameter_types,
                           "capabilities": {"batch": True, "update": False, "restore": False, "merge": False}},
                          sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class CustomInput:
    role: str
    batch: CanonicalBatch

    def __post_init__(self) -> None:
        if type(self.role) is not str or not self.role.strip() or type(self.batch) is not CanonicalBatch:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "named concrete canonical input required")


@dataclass(frozen=True)
class CustomRequest:
    inputs: tuple[CustomInput, ...]
    config: ConfigSpec
    entity: EntityKey

    def __post_init__(self) -> None:
        if (type(self.inputs) not in (tuple, list) or any(type(x) is not CustomInput for x in self.inputs)
                or type(self.config) is not ConfigSpec or type(self.entity) is not EntityKey):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete typed custom request required")
        object.__setattr__(self, "inputs", tuple(sorted(self.inputs, key=lambda x: x.role)))
        if len({x.role for x in self.inputs}) != len(self.inputs):
            raise ContractError(ErrorCode.DUPLICATE, "duplicate input role")
        if self.entity.session_id != self.config.session.session_id:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "entity/config session mismatch")

    def metadata(self, definition: CustomDefinition) -> ResultMetadata:
        return ResultMetadata(self.config.session.namespace, self.entity.session_id,
                              self.config.availability, self.config.digest,
                              tuple(InputBinding(x.role, x.batch.kind, x.batch.metadata) for x in self.inputs),
                              definition.implementation_id, definition.implementation_version)


class BatchCalculator(Protocol):
    """Caller-owned trusted Python callback; its exceptions propagate unchanged."""

    def __call__(self, request: CustomRequest, /) -> FeatureResult: ...


@dataclass(frozen=True)
class CustomRegistration:
    definition: CustomDefinition
    calculator: BatchCalculator

    def __post_init__(self) -> None:
        if type(self.definition) is not CustomDefinition or not callable(self.calculator):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed definition and explicit callable required")


@dataclass(frozen=True)
class CustomRegistry:
    namespace: str
    registrations: tuple[CustomRegistration, ...] = ()

    def __post_init__(self) -> None:
        if (type(self.registrations) not in (tuple, list)
                or any(type(x) is not CustomRegistration for x in self.registrations)):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete registrations required")
        # Reuse the accepted namespace/reserved-ID/duplicate contract without changing it.
        Registry(self.namespace, tuple(x.definition.definition for x in self.registrations))
        object.__setattr__(self, "registrations", tuple(sorted(
            self.registrations, key=lambda x: x.definition.definition.feature_id)))

    def register(self, definition: CustomDefinition, calculator: BatchCalculator) -> CustomRegistry:
        return replace(self, registrations=self.registrations + (CustomRegistration(definition, calculator),))

    def list_features(self) -> tuple[CustomDefinition, ...]:
        return tuple(x.definition for x in self.registrations)

    def get(self, feature_id: str) -> CustomDefinition:
        return self._registration(feature_id).definition

    def _registration(self, feature_id: str) -> CustomRegistration:
        for item in self.registrations:
            if item.definition.definition.feature_id == feature_id:
                return item
        raise ContractError(ErrorCode.UNKNOWN_FEATURE, "unknown registered custom feature")

    def compute(self, feature_id: str, request: CustomRequest, *, mode: str = "batch") -> FeatureResult:
        registration = self._registration(feature_id)
        if mode not in ("batch", "update", "restore", "merge"):
            raise ContractError(ErrorCode.INVALID_CONFIG, "unknown execution mode")
        if mode != "batch":
            raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY, "custom execution supports batch only")
        if type(request) is not CustomRequest:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed custom request required")
        custom = registration.definition
        definition = FeatureDefinition.from_json(custom.definition.to_json())
        config = request.config
        if config.identity != feature_id or config.algorithm_version != definition.algorithm_version:
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "custom configuration identity/version mismatch")
        actual_types = tuple((p.name, type(p.value).__name__) for p in config.parameters)
        if actual_types != custom.parameter_types:
            raise ContractError(ErrorCode.INVALID_CONFIG, "configuration parameter schema mismatch")
        requirements = {r.role: r for r in definition.requirements}
        if set(requirements) != {x.role for x in request.inputs}:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "custom input roles mismatch")
        for item in request.inputs:
            requirement = requirements[item.role]
            if item.batch.kind != requirement.kind:
                raise ContractError(ErrorCode.INVALID_SCHEMA, "custom input kind mismatch")
            if requirement.sampling == "continuous" and item.batch.metadata.sampling != "continuous":
                raise ContractError(ErrorCode.UNSUPPORTED_SAMPLING, "continuous custom input required")
            if config.price_unit is not None and item.batch.metadata.price_unit != config.price_unit:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "custom input/config price unit mismatch")
            validate_batch(item.batch, session=config.session, availability=config.availability,
                           required_fields=requirement.fields)
        expected_entity = cast(EntityKey, _readmit(request.entity))
        expected_metadata = cast(ResultMetadata, _readmit(request.metadata(custom)))
        result = registration.calculator(request)
        if type(result) is not FeatureResult:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "custom callback must return FeatureResult")
        # Copy and re-admit every owned component, including structured cells and bindings.
        result = cast(FeatureResult, _readmit(result))
        if result.metadata != expected_metadata:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "custom result request/implementation bindings mismatch")
        if len(result.values) != 1:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "custom result requires one declared column")
        column = result.values[0]
        output = definition.outputs[0]
        if (column.feature_id != feature_id or column.algorithm_version != definition.algorithm_version
                or column.schema_version != definition.schema_version or column.entities != (expected_entity,)):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "custom column identity/version/entity mismatch")
        if column.dtype.value != output.dtype or column.unit != output.unit:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "custom output type/unit mismatch")
        if not output.nullable and any(x is None for x in column.values):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "custom output forbids null values")
        return result
