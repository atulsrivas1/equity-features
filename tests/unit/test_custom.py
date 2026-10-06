"""Public installed extension admission and independent consumer arithmetic."""
from dataclasses import replace
import json
import unittest
from equity_feature_contracts import (
    Capabilities, Column, ContractError, Coverage, EntityKey, ErrorCode, FeatureColumn, FeatureResult,
    InputRequirement, OutputField, Parameter, PriceUnit, QualityRow, Reason, Status, ValueType, builtin_registry,
)
from equity_features.custom import CustomDefinition, CustomInput, CustomRegistry, CustomRequest
from equity_feature_demo import FEATURE_ID, calculate, definition, fixture


class CustomTests(unittest.TestCase):
    def setUp(self):
        self.request = fixture()
        self.definition = definition()
        self.registry = CustomRegistry("demo").register(self.definition, calculate)

    def reject(self, code, action):
        with self.assertRaises(ContractError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def test_independent_golden_and_isolation(self):
        before = builtin_registry().to_json()
        result = self.registry.compute(FEATURE_ID, self.request)
        self.assertEqual(result.values[0].values, (5/100,))
        self.assertEqual(result.metadata.config_digest, self.request.config.digest)
        self.assertEqual(self.registry.get(FEATURE_ID), self.definition)
        self.assertEqual(CustomRegistry("demo").list_features(), ())
        self.assertEqual(builtin_registry().to_json(), before)
        self.assertEqual(len(builtin_registry().list_features(capability="batch")), 39)

    def test_duplicate_reserved_and_namespace(self):
        self.reject(ErrorCode.DUPLICATE, lambda: self.registry.register(self.definition, calculate))
        self.reject(ErrorCode.INCONSISTENT_IDENTITY, lambda: CustomRegistry("other").register(self.definition, calculate))
        builtin = builtin_registry().get("history.sma")
        # A reserved descriptor remains rejected even with all execution claims removed.
        builtin = replace(builtin, capabilities=Capabilities(), requirements=self.definition.definition.requirements, outputs=(OutputField(builtin.feature_id, "float64", "USD"),))
        reserved = replace(self.definition, definition=builtin)
        self.reject(ErrorCode.DUPLICATE, lambda: CustomRegistry("demo").register(reserved, calculate))

    def test_modes_reject_before_callback(self):
        def never(request):
            raise AssertionError("callback invoked")
        registry = CustomRegistry("demo").register(self.definition, never)
        for mode in ("update", "restore", "merge"):
            self.reject(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: registry.compute(FEATURE_ID, self.request, mode=mode))
        self.reject(ErrorCode.INVALID_CONFIG, lambda: registry.compute(FEATURE_ID, self.request, mode="unknown"))
        self.reject(ErrorCode.UNKNOWN_FEATURE, lambda: registry.compute("demo:absent", self.request))

    def test_definition_contracts(self):
        self.reject(ErrorCode.INVALID_SCHEMA, lambda: replace(self.definition, implementation_version=""))
        self.reject(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: replace(self.definition, capabilities=Capabilities(batch=True, update=True)))
        self.reject(ErrorCode.INVALID_CONFIG, lambda: replace(self.definition, parameter_types=(("x", "object"),)))
        self.reject(ErrorCode.DUPLICATE, lambda: replace(self.definition, parameter_types=(("x", "int"), ("x", "int"))))
        logical = replace(self.definition.definition, requirements=(InputRequirement("x", "result:1", ("values",)),))
        self.reject(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: replace(self.definition, definition=logical))
        metadata = json.loads(self.definition.to_json())
        self.assertEqual(metadata["capabilities"], {"batch": True, "update": False, "restore": False, "merge": False})
        self.assertNotIn("calculator", self.definition.to_json())

    def test_request_identity_schema_and_config(self):
        for config in (replace(self.request.config, identity="demo:other"), replace(self.request.config, algorithm_version="v1")):
            self.reject(ErrorCode.INCOMPATIBLE_VERSION, lambda: self.registry.compute(FEATURE_ID, replace(self.request, config=config)))
        config = replace(self.request.config, parameters=(Parameter("eligibility_policy", 1),))
        self.reject(ErrorCode.INVALID_CONFIG, lambda: self.registry.compute(FEATURE_ID, replace(self.request, config=config)))
        self.reject(ErrorCode.INVALID_SCHEMA, lambda: self.registry.compute(FEATURE_ID, replace(self.request, inputs=())))
        self.reject(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(self.request, entity=EntityKey("A", "other")))
        self.reject(ErrorCode.DUPLICATE, lambda: replace(self.request, inputs=self.request.inputs*2))
        self.reject(ErrorCode.INVALID_SCHEMA, lambda: self.registry.register(self.definition, None))
        self.reject(ErrorCode.INVALID_SCHEMA, lambda: CustomRegistry("demo", iter(())))

    def test_result_bindings(self):
        result = calculate(self.request)
        changes = (replace(result.metadata, backend_version="other"), replace(result.metadata, backend_id="other"),
                   replace(result.metadata, config_digest="0"*64), replace(result.metadata, inputs=()),
                   replace(result.metadata, availability=replace(result.metadata.availability, evaluation_ns=211)),
                   replace(result.metadata, math_policy_version="v2"), replace(result.metadata, evidence_limit=1))
        for metadata in changes:
            bad = replace(result, metadata=metadata)
            registry = CustomRegistry("demo").register(self.definition, lambda request: bad)
            self.reject(ErrorCode.INCONSISTENT_IDENTITY, lambda: registry.compute(FEATURE_ID, self.request))

    def test_result_column_admission(self):
        result = calculate(self.request)
        original = result.values[0]
        for column, code in ((replace(original, unit="USD"), ErrorCode.INVALID_SCHEMA),
                             (replace(original, algorithm_version="v9"), ErrorCode.INCONSISTENT_IDENTITY),
                             (replace(original, dtype=ValueType.INT64, values=(1,)), ErrorCode.INVALID_SCHEMA),
                             (replace(original, entities=(EntityKey("B", "S"),)), ErrorCode.INCONSISTENT_IDENTITY)):
            quality = replace(result.quality[0], entity=column.entities[0])
            bad = replace(result, values=(column,), quality=(quality,))
            registry = CustomRegistry("demo").register(self.definition, lambda request: bad)
            self.reject(code, lambda: registry.compute(FEATURE_ID, self.request))
        registry = CustomRegistry("demo").register(self.definition, lambda request: None)
        self.reject(ErrorCode.INVALID_SCHEMA, lambda: registry.compute(FEATURE_ID, self.request))

    def test_nullability_and_callback_exceptions(self):
        original = calculate(self.request)
        q = QualityRow(self.request.entity, FEATURE_ID, Status.MISSING_INPUT, 2, 2, (Reason.NULL_FIELD,))
        missing = replace(original, values=(replace(original.values[0], values=(None,)),), quality=(q,))
        strict = replace(self.definition, definition=replace(self.definition.definition,
                         outputs=(OutputField(FEATURE_ID, "float64", "fraction", False),)))
        registry = CustomRegistry("demo").register(strict, lambda request: missing)
        self.reject(ErrorCode.INVALID_SCHEMA, lambda: registry.compute(FEATURE_ID, self.request))
        def failure(request):
            raise RuntimeError("trusted caller error")
        with self.assertRaisesRegex(RuntimeError, "trusted caller error"):
            CustomRegistry("demo").register(self.definition, failure).compute(FEATURE_ID, self.request)

    def test_declared_input_unit_mismatch(self):
        config = replace(self.request.config, price_unit=PriceUnit(2, "USD"))
        self.reject(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.registry.compute(FEATURE_ID, replace(self.request, config=config)))

    def test_unavailable_missing_operand(self):
        batch = self.request.inputs[0].batch
        columns = tuple(replace(c, values=(None, 104)) if c.name == "high" else c for c in batch.columns)
        request = replace(self.request, inputs=(CustomInput("bars", replace(batch, columns=columns)),))
        self.reject(ErrorCode.INVALID_SCHEMA, lambda: self.registry.compute(FEATURE_ID, request))

    def test_incomplete_input_is_unavailable(self):
        batch = self.request.inputs[0].batch
        batch = replace(batch, metadata=replace(batch.metadata, coverage=Coverage(3, 2, False)))
        request = replace(self.request, inputs=(CustomInput("bars", batch),))
        result = self.registry.compute(FEATURE_ID, request)
        self.assertIsNone(result.values[0].values[0])
        self.assertEqual(result.quality[0].status, Status.INCOMPLETE_COVERAGE)

    def test_future_and_unknown_operand_are_unavailable(self):
        batch = self.request.inputs[0].batch
        for known in ((150, 211), (150, None)):
            columns = tuple(replace(c, values=known) if c.name == "known_at_ns" else c for c in batch.columns)
            request = replace(self.request, inputs=(CustomInput("bars", replace(batch, columns=columns)),))
            result = self.registry.compute(FEATURE_ID, request)
            self.assertIsNone(result.values[0].values[0])
            self.assertEqual(result.quality[0].status, Status.MISSING_INPUT)


if __name__ == "__main__":
    unittest.main()
