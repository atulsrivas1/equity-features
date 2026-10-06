"""Independent benchmark admission/checker cases; no speed threshold."""
from dataclasses import replace
import importlib.util
from pathlib import Path
import unittest

spec=importlib.util.spec_from_file_location('benchmark_evidence',Path(__file__).resolve().parents[2]/'benchmarks/run_baseline.py')
benchmark=importlib.util.module_from_spec(spec)
spec.loader.exec_module(benchmark)


class BenchmarkEvidenceTests(unittest.TestCase):
    def test_seeded_fixture_and_independent_totals(self):
        from equity_features.session import compute_trades
        batch,config,entity,prices,sizes,digest=benchmark.trade_fixture(8,41001,False)
        self.assertEqual(prices,(109,128,148,161,189,108,185,136))
        self.assertEqual(sizes,(69,31,90,34,66,6,36,30))
        self.assertEqual(digest,'5dd8ec9c212ab78831081ba6fc5c3be5a1cc224617b60acfac96d0ed82a9b908')
        self.assertEqual(benchmark.trade_fixture(8,41001,False)[-1],digest)
        self.assertNotEqual(benchmark.trade_fixture(8,41002,False)[-1],digest)
        golden=benchmark.verify_trades(compute_trades(batch,config,entity=entity),prices,sizes)
        self.assertEqual((golden['session.trade.count'],golden['session.trade.volume'],golden['session.trade.notional']),(8,362,54145))

    def test_incorrect_result_prevents_benchmark_acceptance(self):
        from equity_features.session import compute_trades
        batch,config,entity,prices,sizes,_=benchmark.trade_fixture(8,41001,False)
        result=compute_trades(batch,config,entity=entity)
        wrong=replace(result,values=(replace(result.values[0],values=(9,)),)+result.values[1:])
        with self.assertRaises(AssertionError):benchmark.verify_trades(wrong,prices,sizes)

    def test_native_memory_unit_and_lifetime_monotonicity(self):
        import sys
        first,method=benchmark.peak_bytes(); second,_=benchmark.peak_bytes()
        self.assertGreater(first,0);self.assertGreaterEqual(second,first)
        self.assertEqual(method,'Windows PeakWorkingSetSize bytes' if sys.platform=='win32' else 'Linux ru_maxrss KiB times1024')


if __name__=='__main__':unittest.main()
