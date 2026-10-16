"""Run only in genuinely calculator-absent fresh installed light forms."""
from pathlib import Path
import importlib.util
import sys
import unittest
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'examples'));sys.path.insert(0,str(Path(__file__).parent))
import agent_research as research
from independent_oracle import fixture
from test_consumer import reports


class LightTests(unittest.TestCase):
    def test_C12_genuine_absent_calculator_incompatible_zero(self) -> None:
        self.assertIsNone(importlib.util.find_spec('equity_features'))
        cfg,batch,result=fixture()
        observed=research.replay(cfg,(('trades',batch),),result,*reports(),'session.trade.count=3')
        self.assertEqual((observed.status,observed.calculation_count),('incompatible',0))
        self.assertNotIn('equity_features.session',sys.modules)


if __name__=='__main__':unittest.main()
