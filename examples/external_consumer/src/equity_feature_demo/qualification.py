"""Public synthetic qualification; trusted local code, not an extension sandbox."""
from dataclasses import asdict, dataclass, replace
from fractions import Fraction
import hashlib
import json
from typing import Callable, cast
from equity_feature_contracts import (
    Capabilities, Column, ContractError, EntityKey, ErrorCode, FeatureResult,
    InputRequirement, OutputField, Parameter, Reason, Status, ValueType, builtin_registry,
)
from equity_feature_contracts.adapter_kit import ConformanceCase, run_conformance
from equity_feature_contracts.adapters import SourceError, SourceErrorCode
from equity_feature_demo import FEATURE_ID, calculate, definition, fixture
from equity_feature_demo.adapter import InMemoryBarAdapter, NeverCancelled, adapter_fixture
from equity_features.custom import CustomInput, CustomRegistry, CustomRequest
from equity_features.session import compute_bars


@dataclass(frozen=True)
class QualificationOutcome:
    case_id: str
    group: str
    expected: str
    observed: str

    @property
    def passed(self) -> bool:
        return self.expected == self.observed


@dataclass(frozen=True)
class QualificationReport:
    schema: str
    consumer_version: str
    algorithm_version: str
    custom_golden: float
    builtin_golden: float
    builtin_catalog_before_sha256: str
    builtin_catalog_after_sha256: str
    cases: tuple[QualificationOutcome, ...]

    @property
    def passed(self) -> bool:
        return bool(self.cases) and all(case.passed for case in self.cases)

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"))


@dataclass(frozen=True)
class AlreadyCancelled:
    def is_cancelled(self) -> bool:
        return True


def qualify() -> QualificationReport:
    """Run actual public SDK/consumer checks with independently supplied goldens."""
    outcomes: list[QualificationOutcome] = []
    def positive(case_id: str, condition: bool) -> None:
        if not condition:
            raise AssertionError("qualification failed: " + case_id)
        outcomes.append(QualificationOutcome(case_id, "positive", "pass", "pass"))
    def contract(case_id: str, expected: ErrorCode, action: Callable[[], object]) -> None:
        try:
            action()
        except ContractError as error:
            if error.code != expected:
                raise AssertionError((case_id, expected, error.code)) from error
            outcomes.append(QualificationOutcome(case_id, "contract_error", expected.value, error.code.value))
        else:
            raise AssertionError("expected contract rejection: " + case_id)

    original_catalog = builtin_registry().to_json()
    request = fixture()
    original_request = fixture()
    empty_registry = CustomRegistry("demo")
    registry = empty_registry.register(definition(), calculate)
    result = registry.compute(FEATURE_ID, request)
    builtin = compute_bars(request.inputs[0].batch, replace(request.config, algorithm_version="v1"), entity=request.entity)
    builtin_values = {column.feature_id: column.values[0] for column in builtin.values}
    custom_golden = float(Fraction(5, 100))
    builtin_golden = float(Fraction(5, 103))
    positive("custom_hand_golden", result.values[0].values == (custom_golden,))
    positive("distinct_builtin_hand_golden", builtin_values["session.price.range_fraction"] == builtin_golden)
    positive("discovery_and_registry_isolation", registry.get(FEATURE_ID) == definition()
             and registry.list_features() == (definition(),) and empty_registry.list_features() == ()
             and CustomRegistry("demo").list_features() == ())
    column = result.values[0]
    positive("typed_identity_unit_quality", column.feature_id == FEATURE_ID and column.algorithm_version == "v2"
             and column.dtype == ValueType.FLOAT64 and column.unit == "fraction" and column.entities == (request.entity,)
             and result.quality[0].status == Status.AVAILABLE and result.quality[0].expected == 2
             and result.quality[0].observed == 2)
    positive("config_input_implementation_binding", result.metadata == request.metadata(definition())
             and result.metadata.backend_version == "0.4.0")
    # The complete example declares no additional diagnostic EvidenceRow samples.
    positive("explicit_empty_complete_evidence", result.evidence == ())
    source_batch = request.inputs[0].batch
    scope = source_batch.metadata.scope
    assert scope is not None
    alternate = replace(request, config=replace(request.config,
        parameters=(Parameter("eligibility_policy", "alternate-v1"),)),
        inputs=(CustomInput("bars", replace(source_batch, metadata=replace(source_batch.metadata,
            scope=replace(scope, eligibility_policy="alternate-v1")))),))
    alternate_result = registry.compute(FEATURE_ID, alternate)
    positive("supported_config_identity_change", alternate.config.digest != request.config.digest
             and alternate_result.metadata.config_digest == alternate.config.digest
             and alternate_result.values[0].values == (custom_golden,)
             and alternate_result.values[0].algorithm_version == "v2")
    zero_batch = replace(source_batch, columns=tuple(replace(c, values=(0, c.values[1]))
                         if c.name in ("open", "low") else c for c in source_batch.columns))
    contract("nonpositive_bar_input", ErrorCode.INVALID_SCHEMA,
             lambda: registry.compute(FEATURE_ID, replace(request, inputs=(CustomInput("bars", zero_batch),))))
    null_batch = replace(source_batch, columns=tuple(replace(c, values=(None, None))
                         if c.name == "known_at_ns" else c for c in source_batch.columns))
    missing = registry.compute(FEATURE_ID, replace(request, inputs=(CustomInput("bars", null_batch),)))
    positive("unavailable_input_quality", missing.values[0].values == (None,)
             and missing.quality[0].status == Status.MISSING_INPUT and Reason.UNKNOWN_AVAILABILITY in missing.quality[0].reasons)

    contract("duplicate_registration", ErrorCode.DUPLICATE, lambda: registry.register(definition(), calculate))
    contract("namespace_mismatch", ErrorCode.INCONSISTENT_IDENTITY, lambda: CustomRegistry("other").register(definition(), calculate))
    reserved = replace(definition(), definition=replace(builtin_registry().get("history.sma"),
        capabilities=Capabilities(), requirements=definition().definition.requirements,
        outputs=(OutputField("history.sma", "float64", "fraction"),)))
    contract("reserved_builtin_collision", ErrorCode.DUPLICATE, lambda: empty_registry.register(reserved, calculate))
    contract("missing_role", ErrorCode.INVALID_SCHEMA, lambda: registry.compute(FEATURE_ID, replace(request, inputs=())))
    contract("incompatible_algorithm", ErrorCode.INCOMPATIBLE_VERSION,
             lambda: registry.compute(FEATURE_ID, replace(request, config=replace(request.config, algorithm_version="v1"))))
    contract("incompatible_config_identity", ErrorCode.INCOMPATIBLE_VERSION,
             lambda: registry.compute(FEATURE_ID, replace(request, config=replace(request.config, identity="demo:other"))))
    contract("invalid_parameter_type", ErrorCode.INVALID_CONFIG,
             lambda: registry.compute(FEATURE_ID, replace(request, config=replace(request.config,
                 parameters=(Parameter("eligibility_policy", 1),)))))
    contract("unsupported_definition_mode", ErrorCode.UNSUPPORTED_CAPABILITY,
             lambda: replace(definition(), capabilities=Capabilities(batch=True, update=True)))
    contract("unsupported_input_schema", ErrorCode.UNSUPPORTED_CAPABILITY,
             lambda: replace(definition(), definition=replace(definition().definition,
                 requirements=(InputRequirement("bars", "result:1", ("values",)),))))
    def unsupported_mode(mode: str) -> None:
        contract("unsupported_" + mode, ErrorCode.UNSUPPORTED_CAPABILITY,
                 lambda: registry.compute(FEATURE_ID, request, mode=mode))
    for mode in ("update", "restore", "merge"):
        unsupported_mode(mode)
    contract("unknown_mode", ErrorCode.INVALID_CONFIG, lambda: registry.compute(FEATURE_ID, request, mode="unknown"))
    contract("unknown_feature", ErrorCode.UNKNOWN_FEATURE, lambda: registry.compute("demo:absent", request))

    def returned(case_id: str, expected: ErrorCode, bad: FeatureResult) -> None:
        def callback(supplied: CustomRequest) -> FeatureResult:
            return bad
        contract(case_id, expected, lambda: empty_registry.register(definition(), callback).compute(FEATURE_ID, request))
    returned("bad_output_unit", ErrorCode.INVALID_SCHEMA, replace(result, values=(replace(column, unit="USD"),)))
    returned("bad_output_type", ErrorCode.INVALID_SCHEMA,
             replace(result, values=(replace(column, dtype=ValueType.INT64, values=(1,)),)))
    returned("bad_output_algorithm", ErrorCode.INCONSISTENT_IDENTITY,
             replace(result, values=(replace(column, algorithm_version="v9"),)))
    returned("incompatible_callback_implementation", ErrorCode.INCONSISTENT_IDENTITY,
             replace(result, metadata=replace(result.metadata, backend_version="0.3.0")))
    returned("bad_result_config_binding", ErrorCode.INCONSISTENT_IDENTITY,
             replace(result, metadata=replace(result.metadata, config_digest="0" * 64)))
    returned("bad_result_input_binding", ErrorCode.INCONSISTENT_IDENTITY,
             replace(result, metadata=replace(result.metadata, inputs=())))
    returned("bad_result_schema", ErrorCode.INVALID_SCHEMA, cast(FeatureResult, None))
    bad_entity = EntityKey("B", "S")
    returned("bad_result_entity", ErrorCode.INCONSISTENT_IDENTITY,
             replace(result, values=(replace(column, entities=(bad_entity,)),),
                 quality=(replace(result.quality[0], entity=bad_entity),)))

    adapter, acquisition = adapter_fixture()
    deliveries = tuple(adapter.iter_batches(acquisition, NeverCancelled()))
    assert len(deliveries) == 1 and deliveries[0].batch is not None
    supplied = replace(request, inputs=(CustomInput("bars", deliveries[0].batch),))
    combined = registry.compute(FEATURE_ID, supplied)
    positive("adapter_custom_binding_and_golden", combined.values[0].values == (custom_golden,)
             and combined.metadata.inputs[0].metadata.source == deliveries[0].source)
    cases = [ConformanceCase("whole", acquisition, adapter.capabilities(), deliveries)]
    chunk_request = replace(acquisition, request_id="chunked", max_batch_rows=1)
    chunks = tuple(adapter.iter_batches(chunk_request, NeverCancelled()))
    positive("actual_bounded_chunks", len(chunks) == 2 and [x.ordinal for x in chunks] == [0, 1]
             and [x.final for x in chunks] == [False, True])
    cases.append(ConformanceCase("chunks", chunk_request, adapter.capabilities(), chunks))
    absent_adapter = replace(adapter, data=None)
    absent = tuple(absent_adapter.iter_batches(acquisition, NeverCancelled()))
    positive("missing_source_not_fabricated", len(absent) == 1 and absent[0].batch is None
             and absent[0].disposition == "missing" and not absent[0].source_coverage.complete)
    cases.append(ConformanceCase("missing", acquisition, absent_adapter.capabilities(), absent))
    def source(case_id: str, expected: SourceErrorCode, action: Callable[[], object]) -> None:
        try:
            action()
        except SourceError as error:
            if error.code != expected:
                raise AssertionError((case_id, expected, error.code)) from error
            outcomes.append(QualificationOutcome(case_id, "source_error", expected.value, error.code.value))
            cases.append(ConformanceCase(case_id, acquisition, adapter.capabilities(), (), expected, error.code))
        else:
            raise AssertionError("expected source rejection: " + case_id)
    source("adapter_snapshot_mismatch", SourceErrorCode.UNSUPPORTED,
           lambda: tuple(adapter.iter_batches(replace(acquisition, snapshot_id="other"), NeverCancelled())))
    source("adapter_row_limit", SourceErrorCode.LIMIT,
           lambda: tuple(adapter.iter_batches(replace(acquisition, max_rows=1, max_batch_rows=1), NeverCancelled())))
    source("adapter_chunk_limit", SourceErrorCode.LIMIT,
           lambda: tuple(adapter.iter_batches(replace(acquisition, max_batch_rows=1, max_batches=1), NeverCancelled())))
    source("adapter_cancel_before", SourceErrorCode.CANCELLED,
           lambda: tuple(adapter.iter_batches(acquisition, AlreadyCancelled())))
    bad_data = replace(source_batch, metadata=replace(source_batch.metadata,
        source=replace(source_batch.metadata.source, snapshot_id="other")))
    source("adapter_source_binding_mismatch", SourceErrorCode.SCHEMA,
           lambda: InMemoryBarAdapter(adapter.source, bad_data))
    malformed = replace(source_batch, columns=tuple(replace(c, values=(999, c.values[1]))
                        if c.name == "low" else c for c in source_batch.columns))
    source("adapter_malformed_ohlc", SourceErrorCode.SCHEMA,
           lambda: InMemoryBarAdapter(adapter.source, malformed))
    source("adapter_source_bounds", SourceErrorCode.SCHEMA,
           lambda: replace(adapter, start_ns=101))
    positive("actual_adapter_conformance", run_conformance(tuple(cases)).passed)
    positive("request_and_builtin_invariance", request == original_request
             and builtin_registry().to_json() == original_catalog
             and compute_bars(request.inputs[0].batch, replace(request.config, algorithm_version="v1"),
                 entity=request.entity) == builtin)
    def digest(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()
    return QualificationReport("external-qualification1", definition().implementation_version, "v2",
        custom_golden, builtin_golden, digest(original_catalog), digest(builtin_registry().to_json()), tuple(outcomes))


def main() -> None:
    report = qualify()
    assert report.passed
    print(report.to_json())


if __name__ == "__main__":
    main()
