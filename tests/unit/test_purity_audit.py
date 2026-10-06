"""Execution audit reuses independent fixtures; Python guards are not a sandbox."""
import builtins
from contextlib import ExitStack, contextmanager
from dataclasses import fields, is_dataclass
import importlib
import io
import multiprocessing.process
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
from types import SimpleNamespace
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
ARROW_CASES = frozenset({
    'test_bars.Bars.test_arrow_scope_roundtrip_and_output_metadata',
    'test_continuous.Continuous.test_typed_conservation_status_and_arrow',
    'test_inputs.InputContracts.test_absent_null_zero_distinct',
    'test_inputs.InputContracts.test_all_five_schemas',
    'test_inputs.InputContracts.test_arrow_concrete_only',
    'test_inputs.InputContracts.test_arrow_nullability_rejected',
    'test_inputs.InputContracts.test_arrow_table_roundtrip',
    'test_inputs.InputContracts.test_arrow_wrong_time_unit',
    'test_inputs.InputContracts.test_arrow_wrong_timezone',
    'test_inputs.InputContracts.test_empty_observed_retains_metadata',
    'test_inputs.InputContracts.test_exact_timestamp_extremes',
    'test_inputs.InputContracts.test_int64_price_extremes',
    'test_inputs.InputContracts.test_known_at_null_preserved',
    'test_inputs.InputContracts.test_quote_null_and_crossed_preserved',
    'test_inputs.InputContracts.test_wide_decimal_exact',
    'test_quotes.Quotes.test_arrow_structures_and_utc_ns',
    'test_r1_audit.R1Audit.test_exact_above_binary64_integer_notional_survives_merge_restore_arrow',
    'test_r1_audit.R1Audit.test_independent_early_close_window_goldens_quality_arrow',
    'test_results.ResultContracts.test_arrow_partial_breadth_and_empty_tables',
    'test_results.ResultContracts.test_arrow_result_values_quality_evidence',
    'test_results.ResultContracts.test_empty_feature_column_and_malformed_numpy',
    'test_results.ResultContracts.test_exact_cutoff_exclusion_preserves_diagnostic_knowledge_and_arrow',
    'test_results.ResultContracts.test_existing_admission_typed_errors',
    'test_structure.Structure.test_arrow_nested_rows_and_scope_roundtrip',
    'test_top_k.TopK.test_arrow_exact_timestamps_payload_and_bound',
    'test_trades.Trades.test_arrow_values_match_registry_units_and_types',
})

EXCLUDED = {'test_purity_audit', 'test_distribution_isolation',
            'test_benchmark_evidence', 'test_resource_behavior'}


def deny(*args, **kwargs):
    raise AssertionError('external Python entrypoint denied during calculation audit')


@contextmanager
def denied_entrypoints(arrow_reads=None):
    original_environment_getitem = os._Environ.__getitem__
    def environment_getitem(mapping, key):
        if arrow_reads is not None and key == 'PYARROW_IGNORE_TIMEZONE':
            arrow_reads.append(key)
            return original_environment_getitem(mapping, key)
        return deny()
    targets = [(builtins, 'open'), (io, 'open'), (os, 'open'), (os, 'getenv'),
               (os._Environ, '__getitem__'), (socket, 'socket'),
               (socket, 'create_connection'), (threading.Thread, 'start'),
               (multiprocessing.process.BaseProcess, 'start'), (subprocess, 'Popen')]
    targets += [(time, name) for name in ('time', 'time_ns', 'perf_counter',
                 'perf_counter_ns', 'monotonic', 'monotonic_ns')]
    with ExitStack() as stack:
        for owner, name in targets:
            stack.enter_context(patch.object(owner, name, deny))
        stack.enter_context(patch.object(os._Environ, '__getitem__', environment_getitem))
        yield


def data(value):
    """Represent owned declarative data, not code/import machinery/native state."""
    if value is None or isinstance(value, (bool, int, float, str, bytes)):
        return repr(value)
    if isinstance(value, (tuple, list)):
        return (type(value).__name__, tuple(data(v) for v in value))
    if isinstance(value, (set, frozenset)):
        return (type(value).__name__, tuple(sorted(repr(data(v)) for v in value)))
    if isinstance(value, dict):
        return ('dict', tuple(sorted((repr(data(k)), data(v)) for k, v in value.items())))
    if is_dataclass(value) and not isinstance(value, type):
        return (type(value).__qualname__, tuple((f.name, data(getattr(value, f.name))) for f in fields(value)))
    return ('excluded', type(value).__module__, type(value).__qualname__)


def module_data():
    result = {}
    for name, module in sorted(sys.modules.items()):
        if name == 'equity_features' or name.startswith('equity_features.') or name == 'equity_feature_contracts' or name.startswith('equity_feature_contracts.'):
            result[name] = {key: data(value) for key, value in vars(module).items()
                            if (not key.startswith('__') or key in ('__all__', '__version__'))
                            and not callable(value) and not isinstance(value, type(sys))}
    return result


def calculation_suite():
    # All imports/fixture loading/backend initialization happen before denial.
    import numpy
    import pyarrow
    import pyarrow.compute
    for package in ('contracts', 'features'):
        src = ROOT / 'packages' / package / 'src'
        for path in sorted(src.rglob('*.py')):
            parts = path.relative_to(src).with_suffix('').parts
            name = '.'.join(parts[:-1] if parts[-1] == '__init__' else parts)
            importlib.import_module(name)
    sys.path.insert(0, str(ROOT / 'tests' / 'unit'))
    try:
        suites = [unittest.defaultTestLoader.loadTestsFromModule(importlib.import_module(path.stem))
                  for path in sorted((ROOT / 'tests' / 'unit').glob('test_*.py'))
                  if path.stem not in EXCLUDED]
    finally:
        sys.path.pop(0)
    return unittest.TestSuite(suites)


class PurityAuditTests(unittest.TestCase):
    def test_positive_controls_reject_external_entrypoints(self):
        probes = [lambda: builtins.open('audit-nonexistent'), lambda: io.open('audit-nonexistent'),
                  lambda: os.open('audit-nonexistent', os.O_RDONLY),
                  lambda: os.getenv('AUDIT_SYNTHETIC'), lambda: os.environ.get('AUDIT_SYNTHETIC'),
                  lambda: socket.socket(), lambda: socket.create_connection(('localhost', 1)),
                  lambda: threading.Thread(target=lambda: None).start(),
                  lambda: multiprocessing.process.BaseProcess().start(),
                  lambda: subprocess.Popen(['audit-nonexistent'])]
        probes += [lambda name=name: getattr(time, name)() for name in ('time', 'time_ns', 'perf_counter',
                    'perf_counter_ns', 'monotonic', 'monotonic_ns')]
        with denied_entrypoints():
            for probe in probes:
                with self.assertRaisesRegex(AssertionError, 'entrypoint denied'):
                    probe()

    def test_independent_calculation_fixtures_without_external_entrypoints(self):
        suite = calculation_suite()
        expected = suite.countTestCases()
        self.assertEqual(expected, 619)
        before = module_data()
        self.assertEqual(len(before), 43)
        bridge_cases = set()
        reads = []
        class AuditResult(unittest.TestResult):
            def startTest(self, test):
                reads.clear()
                super().startTest(test)
            def stopTest(self, test):
                if reads:
                    bridge_cases.add(test.id())
                super().stopTest(test)
        result = AuditResult()
        # CPython3.12 unittest measures case duration. Disable only the runner's
        # timing facade; the actual time module remains denied to calculations.
        with patch.object(unittest.case, 'time', SimpleNamespace(perf_counter=lambda: 0.0)):
            with denied_entrypoints(arrow_reads=reads):
                suite.run(result)
        self.assertEqual(result.testsRun, expected)
        self.assertEqual(result.skipped, [])
        self.assertFalse(result.errors, str(result.errors[:1]))
        self.assertFalse(result.failures, str(result.failures[:1]))
        self.assertEqual(module_data(), before)
        self.assertEqual(bridge_cases, ARROW_CASES)

    def test_strict_canonical_fixtures_and_owned_data_mutation_detector(self):
        def flatten(suite):
            for test in suite:
                if isinstance(test, unittest.TestSuite):
                    yield from flatten(test)
                else:
                    yield test
        suite = unittest.TestSuite(test for test in flatten(calculation_suite())
                                   if test.id() not in ARROW_CASES)
        self.assertEqual(suite.countTestCases(), 593)
        before = module_data()
        result = unittest.TestResult()
        with patch.object(unittest.case, 'time', SimpleNamespace(perf_counter=lambda: 0.0)):
            with denied_entrypoints():
                suite.run(result)
        self.assertEqual(result.testsRun, 593)
        self.assertEqual(result.skipped, [])
        self.assertFalse(result.errors, str(result.errors[:1]))
        self.assertFalse(result.failures, str(result.failures[:1]))
        self.assertEqual(module_data(), before)
        # Positive control: declared mutable module data must change the snapshot.
        import equity_feature_contracts.registry as registry
        with patch.object(registry, 'audit_positive_control', {'value': 1}, create=True):
            initial = module_data()
            registry.audit_positive_control['value'] = 2
            self.assertNotEqual(module_data(), initial)
        self.assertEqual(module_data(), before)


if __name__ == '__main__':
    unittest.main()
