"""EQ117 qualification controls; these are not scheduled study observations."""
from __future__ import annotations
import copy
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

HERE = Path(__file__).resolve().parent
# Builder copies this test beside the fixed helper files outside the checkout.
def load(name):
    spec = importlib.util.spec_from_file_location(name, HERE / (name + '.py'))
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module

observer = load('evidence_evaluation_observer')
producer = load('evidence_evaluation_producer')
scorer = load('evidence_evaluation_scoring')
instrumentation = load('evidence_evaluation_instrumentation')
oracle = scorer.load_oracle((HERE/'EQ116_ORACLES.json').read_bytes())


class Qualification(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory(prefix='eq117-qualification-')
        self.root = Path(self.directory.name)

    def tearDown(self):
        self.directory.cleanup()

    def recorded(self, case, arm, suffix=''):
        seed = self.root/('private-'+case+suffix)
        producer.prepare(seed, case)
        visible = self.root/('opaque-'+suffix+arm)
        producer.record(seed, visible, arm, 'opaque-qualification')
        producer.export(visible, arm)
        return visible

    def test_full_independent_diagnoses_both_arms(self):
        for case in scorer.CASES:
            for arm in scorer.ARMS:
                with self.subTest(case=case, arm=arm):
                    root = self.recorded(case, arm, case+arm)
                    actual = observer.observe(root, arm)
                    self.assertTrue(scorer.exact(actual, scorer.expected(case, oracle)))

    def test_missing_corrupt_never_enter_calculator(self):
        from equity_features import session
        for case in ('P05', 'P07'):
            for arm in scorer.ARMS:
                root = self.recorded(case, arm, case+arm)
                with patch.object(session, 'compute_trades', side_effect=AssertionError('forbidden')) as compute:
                    result = observer.observe(root, arm)
                    self.assertEqual(result['calculator_calls'], 0)
                    compute.assert_not_called()

    def test_actual_replay_restores_entry(self):
        from equity_features import session
        root = self.recorded('P01', 'ordinary_log')
        original = session.compute_trades
        self.assertEqual(observer.observe(root, 'ordinary_log')['calculator_calls'], 1)
        self.assertIs(session.compute_trades, original)
        audit={}
        def failed_calculator(*args,**kwargs):
            raise RuntimeError('synthetic qualification entry failure')
        with patch.object(producer,'compute_trades',failed_calculator):
            with self.assertRaises(RuntimeError):
                producer.prepare(self.root/'failed-shared-preparation','P01',audit=audit)
        self.assertEqual(audit,dict(calculator_entries=1,calculator_returns=0,calculator_errors=1,completed=False))
        self.assertFalse((self.root/'failed-shared-preparation').exists())
        self.assertIsNone(sys.getprofile())

    def test_foreign_baseline_context_rejected(self):
        root = self.recorded('P01', 'ordinary_log')
        path = root/'plain-log.json'
        value = json.loads(path.read_bytes())
        # A retained event changed without the corresponding terminal declaration.
        value[0]['facts']['context'] = {'foreign': True}
        path.write_bytes(observer.encoded(value))
        with self.assertRaises((AssertionError, ValueError, KeyError, TypeError)):
            observer.observe(root, 'ordinary_log')

    def test_scorer_distinguishes_json_numeric_types(self):
        wanted = scorer.expected('P01', oracle)
        altered = copy.deepcopy(wanted)
        def change(value):
            if type(value) is dict:
                for key, item in value.items():
                    if type(item) is int:
                        value[key] = float(item)
                        return True
                    if change(item): return True
            if type(value) is list:
                return any(change(item) for item in value)
            return False
        self.assertTrue(change(altered))
        self.assertFalse(scorer.exact(wanted, altered))
        self.assertFalse(scorer.exact(0, False))

    def test_schedule_keeps_all_slots_and_counterbalance(self):
        slots = scorer.schedule()
        self.assertEqual(len(slots), 160)
        self.assertEqual(len({(s['case_id'],s['arm'],s['repetition']) for s in slots}),160)
        for case in scorer.CASES:
            first = [s for s in slots if s['case_id']==case and s['arm_position']==1]
            self.assertEqual(sum(s['arm']==scorer.ARMS[0] for s in first),5)
            self.assertEqual(sum(s['process_state']=='PROCESS_COLD' for s in first),5)

    def test_trace_counts_nested_public_boundaries(self):
        trace = instrumentation.OperationTrace()
        trace.start()
        try:
            json.loads(json.dumps({'a': 1}))
        finally:
            trace.stop()
        summary = trace.summary()
        self.assertGreaterEqual(summary['counts']['json_encode'],1)
        self.assertGreaterEqual(summary['counts']['json_decode'],1)
        self.assertEqual(summary['total'],sum(summary['counts'].values()))
        self.assertIsNone(sys.getprofile())
        compressed=instrumentation.OperationTrace()
        for _ in range(16385):compressed._add('json_encode','json.dumps')
        self.assertEqual(compressed.summary()['total'],16385)
        self.assertEqual(len(compressed.sequence),1)
        alternating=instrumentation.OperationTrace()
        for i in range(instrumentation.MAX_RUNS):
            alternating._add('json_decode' if i%2 else 'json_encode','json.loads' if i%2 else 'json.dumps')
        before=alternating.summary()
        with self.assertRaises(instrumentation.TraceLimitError):alternating._add('json_encode','json.dumps')
        self.assertEqual(alternating.summary(),before)

    def test_worker_handshake_and_actual_eof_exit(self):
        command=[sys.executable,'-I',str(HERE/'evidence_evaluation_worker.py'),'serve','ordinary_log']
        source_paths=getattr(sys,'_eq117_source_paths',None)
        if source_paths is not None:
            # Explicit source-only qualification, never an installed-origin claim.
            code='import sys,json,runpy;sys.dont_write_bytecode=True;sys.path[:0]=json.loads(sys.argv[1]);sys.argv=sys.argv[2:];runpy.run_path(sys.argv[0],run_name="__main__")'
            command=[sys.executable,'-I','-c',code,json.dumps(source_paths),*command[2:]]
        process = subprocess.Popen(command,stdin=subprocess.PIPE,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        try:
            stdout, stderr = process.communicate(b'',timeout=30)
            self.assertEqual(process.returncode,0)
            self.assertEqual(stderr,b'')
            hello = json.loads(stdout)
            self.assertEqual(hello['schema'],'eq117.worker.hello.v1')
            self.assertEqual(hello['prefix'],sys.prefix)
            self.assertTrue(hello['imports_completed'])
        finally:
            if process.poll() is None:
                process.kill();process.wait(timeout=10)

    def test_worker_endpoint_arithmetic_with_injected_clock(self):
        from types import SimpleNamespace
        worker = load('evidence_evaluation_worker')
        for case in scorer.CASES:
            seed = self.root/('private-'+case)
            producer.prepare(seed,case)
            for arm in scorer.ARMS:
                with self.subTest(case=case,arm=arm):
                    ticks = iter((10,20,30,45,50,75))
                    output = io.BytesIO()
                    with patch.object(sys,'stdout',SimpleNamespace(buffer=output)):
                        result=worker.trial(seed,self.root/('visible-'+case+arm),arm,'qualification-fake-clock',
                                            clock=lambda:next(ticks),actual_cli_invocations=0)
                    self.assertEqual(result['status'],'valid',output.getvalue().decode('ascii'))
                    self.assertEqual(result['endpoints'],dict(record_start_ns=10,record_end_ns=20,
                        export_start_ns=30,export_end_ns=45,read_verify_replay_start_ns=50,read_verify_replay_end_ns=75))
                    self.assertEqual(result['operation_trace']['cli_invocations'],0)
                    self.assertTrue(scorer.exact(result['diagnosis'],scorer.expected(case,oracle)))
                    self.assertEqual(json.loads(output.getvalue()),result)
        actual_observe=worker.observer.observe
        def fail_after_entry(directory,arm):
            actual_observe(directory,arm)
            raise RuntimeError('synthetic post-entry observation failure')
        ticks=iter((10,20,30,45,50,75));output=io.BytesIO()
        with patch.object(worker.observer,'observe',fail_after_entry),patch.object(sys,'stdout',SimpleNamespace(buffer=output)):
            failed=worker.trial(seed,self.root/'failed-after-calculator','ordinary_log','qualification-failure',
                                clock=lambda:next(ticks),actual_cli_invocations=0)
        self.assertEqual(failed['status'],'failed')
        self.assertIsNone(failed['diagnosis'])
        self.assertEqual(failed['operation_trace']['counts']['calculator_call'],1)
        driver=load('run_evidence_evaluation');row={}
        driver.retain_calculator_observation(row,failed['operation_trace'])
        self.assertEqual(row['calculator_calls'],1)


if __name__=='__main__':
    result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(Qualification))
    raise SystemExit(not(result.testsRun==9 and result.wasSuccessful() and not result.skipped))
