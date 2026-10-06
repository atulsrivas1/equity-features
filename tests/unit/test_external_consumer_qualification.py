"""External driver: hand goldens and a deliberately wrong trusted callback."""
from dataclasses import replace
from fractions import Fraction
import json
import unittest
from unittest.mock import patch
import equity_feature_demo.qualification as qualification

EXPECTED = {'custom_hand_golden': ('positive', 'pass'), 'distinct_builtin_hand_golden': ('positive', 'pass'), 'discovery_and_registry_isolation': ('positive', 'pass'), 'typed_identity_unit_quality': ('positive', 'pass'), 'config_input_implementation_binding': ('positive', 'pass'), 'explicit_empty_complete_evidence': ('positive', 'pass'), 'supported_config_identity_change': ('positive', 'pass'), 'nonpositive_bar_input': ('contract_error', 'invalid_schema'), 'unavailable_input_quality': ('positive', 'pass'), 'duplicate_registration': ('contract_error', 'duplicate'), 'namespace_mismatch': ('contract_error', 'inconsistent_identity'), 'reserved_builtin_collision': ('contract_error', 'duplicate'), 'missing_role': ('contract_error', 'invalid_schema'), 'incompatible_algorithm': ('contract_error', 'incompatible_version'), 'incompatible_config_identity': ('contract_error', 'incompatible_version'), 'invalid_parameter_type': ('contract_error', 'invalid_config'), 'unsupported_definition_mode': ('contract_error', 'unsupported_capability'), 'unsupported_input_schema': ('contract_error', 'unsupported_capability'), 'unsupported_update': ('contract_error', 'unsupported_capability'), 'unsupported_restore': ('contract_error', 'unsupported_capability'), 'unsupported_merge': ('contract_error', 'unsupported_capability'), 'unknown_mode': ('contract_error', 'invalid_config'), 'unknown_feature': ('contract_error', 'unknown_feature'), 'bad_output_unit': ('contract_error', 'invalid_schema'), 'bad_output_type': ('contract_error', 'invalid_schema'), 'bad_output_algorithm': ('contract_error', 'inconsistent_identity'), 'incompatible_callback_implementation': ('contract_error', 'inconsistent_identity'), 'bad_result_config_binding': ('contract_error', 'inconsistent_identity'), 'bad_result_input_binding': ('contract_error', 'inconsistent_identity'), 'bad_result_schema': ('contract_error', 'invalid_schema'), 'bad_result_entity': ('contract_error', 'inconsistent_identity'), 'adapter_custom_binding_and_golden': ('positive', 'pass'), 'actual_bounded_chunks': ('positive', 'pass'), 'missing_source_not_fabricated': ('positive', 'pass'), 'adapter_snapshot_mismatch': ('source_error', 'unsupported_capability'), 'adapter_row_limit': ('source_error', 'resource_limit'), 'adapter_chunk_limit': ('source_error', 'resource_limit'), 'adapter_cancel_before': ('source_error', 'cancelled'), 'adapter_source_binding_mismatch': ('source_error', 'schema_mismatch'), 'adapter_malformed_ohlc': ('source_error', 'schema_mismatch'), 'adapter_source_bounds': ('source_error', 'schema_mismatch'), 'actual_adapter_conformance': ('positive', 'pass'), 'request_and_builtin_invariance': ('positive', 'pass')}

class ExternalConsumerQualification(unittest.TestCase):
    def test_actual_public_contract_matrix_and_independent_goldens(self):
        report = qualification.qualify()
        self.assertTrue(report.passed)
        self.assertEqual(report.custom_golden, float(Fraction(5, 100)))
        self.assertEqual(report.builtin_golden, float(Fraction(5, 103)))
        self.assertNotEqual(report.custom_golden, report.builtin_golden)
        self.assertEqual(len(report.cases), len(EXPECTED))
        self.assertEqual({c.case_id: (c.group, c.expected) for c in report.cases}, EXPECTED)
        self.assertEqual(report.builtin_catalog_before_sha256, report.builtin_catalog_after_sha256)
        self.assertEqual(json.loads(report.to_json())['consumer_version'], '0.4.0')

    def test_plausible_wrong_callback_cannot_report_numerical_success(self):
        original = qualification.calculate
        def wrong(request):
            result = original(request)
            return replace(result, values=(replace(result.values[0], values=(0.06,)),))
        with patch.object(qualification, 'calculate', wrong):
            with self.assertRaisesRegex(AssertionError, 'custom_hand_golden'):
                qualification.qualify()
