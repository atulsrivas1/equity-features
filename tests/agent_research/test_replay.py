"""Actual pure calculator/replay controls; selected only with features installed."""
from __future__ import annotations
from dataclasses import replace
from pathlib import Path
import sys
import unittest
from unittest.mock import patch

ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'examples'));sys.path.insert(0,str(Path(__file__).parent))
import agent_research as research
from independent_oracle import fixture
from test_consumer import reports
from equity_feature_contracts import EntityKey,CanonicalBatch,Column,Status,Reason
from equity_feature_evidence import canonical_content
from equity_features.session import compute_trades


class ReplayTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg,self.batch,self.expected=fixture();self.raw=reports()
    def run_replay(self,**kw: object) -> research.ReplayObservation:
        return research.replay(self.cfg,(('trades',self.batch),),self.expected,*self.raw,'session.trade.count=3',**kw)
    def test_C01_original_and_replay_complete_parity(self) -> None:
        actual=compute_trades(self.batch,self.cfg,entity=EntityKey('A','S'))
        self.assertEqual(canonical_content(actual),canonical_content(self.expected))
        with patch('equity_features.session.compute_trades',wraps=compute_trades) as calls:
            observed=self.run_replay()
        self.assertEqual((observed.status,observed.calculation_count),('matched',1));self.assertEqual(calls.call_count,1)
    def test_C02_wrong_narrative_independent_of_matched_replay(self) -> None:
        actual=research.replay(self.cfg,(('trades',self.batch),),self.expected,*self.raw,'session.trade.count=4')
        self.assertEqual((actual.status,actual.calculation_count),('matched',1))
        self.assertEqual(research.assess(self.cfg,(('trades',self.batch),),self.expected,*self.raw,'session.trade.count=4').decision,'REJECT')
    def test_C03_unsupported_narrative_replay_still_explicit(self) -> None:
        actual=research.replay(self.cfg,(('trades',self.batch),),self.expected,*self.raw,'free prose')
        self.assertEqual((actual.status,actual.calculation_count),('matched',1))
    def test_C04_to06_missing_reports_never_invoke_calculator(self) -> None:
        for index in range(3):
            raw=list(self.raw);raw[index]=None
            with self.subTest(index=index),patch('equity_features.session.compute_trades',wraps=compute_trades) as calls:
                actual=research.replay(self.cfg,(('trades',self.batch),),self.expected,*raw,'session.trade.count=3')
                self.assertEqual((actual.status,actual.calculation_count),('not_requested',0));self.assertEqual(calls.call_count,0)
    def test_C07_reference_only_bundle_unavailable_zero(self) -> None:
        with patch('equity_features.session.compute_trades',wraps=compute_trades) as calls:
            actual=research.replay(self.cfg,(),self.expected,*self.raw,'session.trade.count=3')
        self.assertEqual((actual.status,actual.calculation_count),('unavailable',0));self.assertEqual(calls.call_count,0)
    def test_C13_preentry_cancel_zero(self) -> None:
        with patch('equity_features.session.compute_trades',wraps=compute_trades) as calls:actual=self.run_replay(cancel_before_start=True)
        self.assertEqual((actual.status,actual.calculation_count),('cancelled_before_start',0));self.assertEqual(calls.call_count,0)
    def test_C14_future_known_actual_producer_not_filtered(self) -> None:
        cols=tuple(replace(x,values=(110,130,211)) if x.name=='known_at_ns' else x for x in self.batch.columns)
        batch=replace(self.batch,columns=cols)
        actual=compute_trades(batch,self.cfg,entity=EntityKey('A','S'))
        self.assertEqual(tuple(x.values[0] for x in actual.values),(None,)*5)
        self.assertTrue(all(x.status is Status.MISSING_INPUT and x.reasons==(Reason.FUTURE_KNOWLEDGE,) and x.expected==x.observed==3 for x in actual.quality))
        expected=research.fixture(True)[2];self.assertEqual(canonical_content(actual),canonical_content(expected))
        raw=research.expected_reports(True)
        assessment=research.assess(self.cfg,(('trades',batch),),actual,*raw,'session.trade.count=3')
        self.assertEqual((assessment.narrative_status,assessment.decision),('unavailable','DEFER'))
        with patch('equity_features.session.compute_trades',wraps=compute_trades) as calls:
            replayed=research.replay(self.cfg,(('trades',batch),),actual,*raw,'session.trade.count=3')
        self.assertEqual((replayed.status,replayed.calculation_count),('matched',1));self.assertEqual(calls.call_count,1)
    def test_C25_unsupported_registry_is_parser_refusal(self) -> None:
        import io,json,zipfile
        from equity_feature_bundles import PublicationDeclaration,write_bundle,read_bundle,BundleError
        from equity_feature_evidence import decode_receipt
        raw=write_bundle(decode_receipt(self.raw[0]),self.cfg,self.expected,(('trades',self.batch),),PublicationDeclaration('synthetic','Synthetic example','caller_owned'))
        source=zipfile.ZipFile(io.BytesIO(raw));out=io.BytesIO()
        with zipfile.ZipFile(out,'w') as target:
            for name in source.namelist():
                data=source.read(name)
                if name=='manifest.json':
                    v=json.loads(data);v['registry']='caller.plugin';data=json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=True).encode('ascii')
                target.writestr(name,data)
        with self.assertRaises(BundleError):read_bundle(out.getvalue())


if __name__=='__main__':unittest.main()
