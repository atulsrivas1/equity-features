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

    def test_C25_unsupported_registry_refuses_without_calculator(self) -> None:
        import io,json,zipfile
        from equity_feature_bundles import PublicationDeclaration,write_bundle,read_bundle,BundleError
        from equity_feature_evidence import decode_receipt
        cfg,batch,result=fixture()
        raw=write_bundle(decode_receipt(reports()[0]),cfg,result,(('trades',batch),),PublicationDeclaration('synthetic','Synthetic example','caller_owned'))
        out=io.BytesIO()
        with zipfile.ZipFile(io.BytesIO(raw)) as source,zipfile.ZipFile(out,'w') as target:
            for name in source.namelist():
                data=source.read(name)
                if name=='manifest.json':
                    value=json.loads(data);value['registry']='caller.plugin'
                    data=json.dumps(value,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
                target.writestr(name,data)
        with self.assertRaises(BundleError):read_bundle(out.getvalue())
        self.assertIsNone(importlib.util.find_spec('equity_features'))


if __name__=='__main__':unittest.main()
