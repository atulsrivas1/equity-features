"""Pure/SQLite source controls; no subprocess, sockets, native or calculator."""
from __future__ import annotations
from dataclasses import replace
import hashlib
import importlib.util
import json
from pathlib import Path
import sys
import tempfile
import unittest
from typing import Any

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'examples'))
sys.path.insert(0,str(Path(__file__).parent))
import agent_research as research
from independent_oracle import fixture,literal_oracle,canonical,independent_chain
import equity_feature_contracts as c
import equity_feature_agent_evidence as a
import equity_feature_agent_ledger as l
from equity_feature_evidence import (canonical_content,make_content_receipt,encode_receipt,EnvironmentDeclaration,
    PackageVersion,ExecutionClaim,EvidenceDisclosure)
from equity_feature_explanations import explain_result,encode_explanation


def reports() -> tuple[bytes,bytes,bytes]:
    cfg,batch,result=fixture()
    receipt=make_content_receipt(result,cfg,(('trades',batch),),
        EnvironmentDeclaration('CPython','3.12','synthetic-qualification',(
            PackageVersion('equity-feature-contracts','0.0.4a4'),PackageVersion('equity-features','0.0.4a4'))),
        ExecutionClaim(),EvidenceDisclosure('not_supplied',0))
    explanation=encode_explanation(explain_result(result,receipt,cfg,entity=c.EntityKey('A','S'),
        feature_id='session.trade.count',evidence_limit=16))
    fp=receipt.output
    diagnostic=canonical(dict(representation='equity.mcp.diagnostics.v1',schema_version='1',report=dict(
        schema_version='1',context=dict(namespace='demo',entity=dict(instrument_id='A',session_id='S'),
            availability=dict(market_cutoff_ns='200',knowledge_cutoff_ns='210',evaluation_ns='210',mode='known_at',reconstruction_reason=None)),
        policy=dict(policy_id='synthetic-advisory',mode='advisory',unknown_action='deny'),
        findings=[dict(check_id='observation',subject_id='synthetic-output',kind='freshness',
            content=dict(domain='feature_result',digest=fp.digest,byte_length=str(fp.byte_length),
                schema_version='1',canonicalization='typed-json-v1',algorithm='sha256'),
            status='unknown',severity='warning',reasons=['missing_observation'],assessed=False,unknown_prerequisites='1',age_ns=None)],
        requested_count=1,passed_count=0,failed_count=0,unknown_count=1,assessed_count=0,unknown_prerequisite_count='1',
        not_requested=['adjustment','declared_context','knowledge_time','market_time','membership','revision'],
        admission='not_applied',source_authenticated=False,historical_acquisition_verified=False),
        associations=[dict(check_id='observation',role='output',input_role=None,input_id=None)],input_content_verified=False))
    return encode_receipt(receipt),explanation,diagnostic


def summary_wire() -> bytes:
    return canonical(dict(ok=True,payload=dict(representation='complete_transported_producer',reference='A'*43,data=literal_oracle()['producer']['complete_producer_payload'])))


class ConsumerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.cfg,self.batch,self.result=fixture()
        self.raw=reports()
    def assess(self,*,inputs: Any=None,reports: Any=None,narrative: str='session.trade.count=3',cfg: Any=None,result: Any=None) -> research.Assessment:
        return research.assess(self.cfg if cfg is None else cfg,(('trades',self.batch),) if inputs is None else inputs,
            self.result if result is None else result,*(self.raw if reports is None else reports),narrative)
    def refusal(self,**kw: Any) -> None:
        with self.assertRaises(research.ResearchExampleError) as caught:self.assess(**kw)
        self.assertNotIn('synthetic-output',str(caught.exception))
    def test_independent_literal_fixture_and_cardinality(self) -> None:
        data=literal_oracle()
        self.assertEqual(self.cfg.window.governed_sessions,('P','S'))
        for key,value in (('configuration',self.cfg),('batch',self.batch)):
            raw=canonical(data[key]['value'])
            self.assertEqual(canonical_content(value),raw)
            self.assertEqual(len(raw),data[key]['bytes'])
            self.assertEqual(hashlib.sha256(raw).hexdigest(),data[key]['sha256'])
        actual=research.fixture()
        self.assertEqual(tuple(canonical_content(x) for x in actual),tuple(canonical_content(x) for x in (self.cfg,self.batch,self.result)))
        self.assertEqual(tuple(x.values[0] for x in self.result.values),(3,10,1011,101.1,10/3))
        self.assertEqual(research.expected_reports(),self.raw)
    def test_C01_unknown_diagnostic_always_defers(self) -> None:
        value=self.assess()
        self.assertEqual((value.narrative_status,value.decision,value.reason_code),('matched','DEFER','diagnostic_not_admitted'))
        self.assertEqual((value.expected_input_count,value.verified_input_count,value.input_content_status),(1,1,'complete'))
        self.assertFalse(value.source_authenticated or value.execution_verified)
    def test_C02_wrong_narrative_rejected(self) -> None:
        self.assertEqual(self.assess(narrative='session.trade.count=4').decision,'REJECT')
    def test_C03_unsupported_prose_deferred(self) -> None:
        for text in ('buy now','session.trade.count=03','session.trade.count=+3','session.trade.count=true','session.trade.count=3.0',' session.trade.count=3'):
            with self.subTest(text=text):
                observed=self.assess(narrative=text)
                self.assertEqual((observed.narrative_status,observed.decision),('unsupported','DEFER'))
    def test_C04_missing_receipt(self) -> None:
        r=self.assess(reports=(None,*self.raw[1:]))
        self.assertEqual((r.receipt_status,r.explanation_status,r.narrative_status),('unavailable','verified','unavailable'))
    def test_C05_missing_explanation(self) -> None:
        r=self.assess(reports=(self.raw[0],None,self.raw[2]));self.assertEqual((r.explanation_status,r.decision),('unavailable','DEFER'))
    def test_C06_missing_diagnostics(self) -> None:
        r=self.assess(reports=(*self.raw[:2],None));self.assertEqual((r.diagnostics_status,r.diagnostic_admission),('unavailable','unavailable'))
    def test_C07_missing_retained_input(self) -> None:
        r=self.assess(inputs=())
        self.assertEqual((r.narrative_status,r.input_content_status,r.verified_input_count,r.reason_code),('matched','missing',0,'incomplete_evidence'))
        self.assertEqual((r.receipt_status,r.explanation_status,r.diagnostics_status),('verified',)*3)
    def test_C08_changed_input_same_metadata(self) -> None:
        cols=tuple(replace(x,values=(100,103,101)) if x.name=='price' else x for x in self.batch.columns)
        self.refusal(inputs=(('trades',replace(self.batch,columns=cols)),))
    def test_C09_changed_result_same_metadata(self) -> None:
        cols=(replace(self.result.values[0],values=(4,)),)+self.result.values[1:]
        self.refusal(result=replace(self.result,values=cols))
    def test_C10_changed_configuration(self) -> None:
        self.refusal(cfg=replace(self.cfg,identity='wrong'))
    def test_C11_wrong_receipt_binding(self) -> None:
        value=json.loads(self.raw[0]);value['output']['digest']='0'*64
        self.refusal(reports=(canonical(value),*self.raw[1:]))
    def test_C18_changed_report_bytes(self) -> None:
        self.refusal(reports=(self.raw[0],self.raw[1]+b' ',self.raw[2]))
    def test_C22_model_unknown_never_admitted(self) -> None:
        self.assertEqual(self.assess().decision,'DEFER')
        self.assertEqual(research.ResearchObservation(self.assess(),research.ReplayObservation('not_requested',0),research.LedgerObservation('unavailable','unavailable','missing')).model_status,'not_supplied')
    def test_C23_oversized_report(self) -> None:
        self.refusal(reports=(b'x'*32769,*self.raw[1:]))
    def test_C26_wrong_explanation_focus(self) -> None:
        value=json.loads(self.raw[1]);value['feature_id']='session.trade.volume'
        self.refusal(reports=(self.raw[0],canonical(value),self.raw[2]))
    def test_C27_wrong_explanation_context(self) -> None:
        value=json.loads(self.raw[1]);value['entity']['instrument_id']='B'
        self.refusal(reports=(self.raw[0],canonical(value),self.raw[2]))
    def test_C28_wrong_explanation_summary(self) -> None:
        value=json.loads(self.raw[1]);value['inputs'][0]['content_verified']=True
        self.refusal(reports=(self.raw[0],canonical(value),self.raw[2]))
    def test_C29_wrong_diagnostic_context(self) -> None:
        value=json.loads(self.raw[2]);value['report']['context']['availability']['evaluation_ns']='211'
        self.refusal(reports=(*self.raw[:2],canonical(value)))
    def test_C30_wrong_diagnostic_association(self) -> None:
        value=json.loads(self.raw[2]);value['associations'][0]['role']='configuration'
        self.refusal(reports=(*self.raw[:2],canonical(value)))
    def test_C31_derived_diagnostic_counts_and_admission(self) -> None:
        for name,new in (('unknown_count',0),('admission','admitted'),('extra',False)):
            value=json.loads(self.raw[2]);value['report'][name]=new
            with self.subTest(name=name):self.refusal(reports=(*self.raw[:2],canonical(value)))
    def test_C32_present_empty_not_missing(self) -> None:
        for index in range(3):
            raw=list(self.raw);raw[index]=b''
            with self.subTest(index=index):self.refusal(reports=tuple(raw))
    def test_C33_graph_bounds_before_fingerprints(self) -> None:
        cfg=object.__new__(c.ConfigSpec)
        for name in research._FIELDS[c.ConfigSpec]:object.__setattr__(cfg,name,getattr(self.cfg,name))
        object.__setattr__(cfg,'parameters',(c.Parameter('x',1),)*65)
        self.refusal(cfg=cfg)
    def test_C34_forged_nested_type_no_callback(self) -> None:
        class Trap:
            def __repr__(self) -> str:raise AssertionError('repr called')
            def __str__(self) -> str:raise AssertionError('str called')
            def __iter__(self) -> Any:raise AssertionError('iter called')
        cfg=object.__new__(c.ConfigSpec)
        for name in research._FIELDS[c.ConfigSpec]:object.__setattr__(cfg,name,getattr(self.cfg,name))
        object.__setattr__(cfg,'session',Trap())
        self.refusal(cfg=cfg)
    def test_C35_missing_input_wrong_present_report(self) -> None:
        wrong=json.loads(self.raw[1]);wrong['entity']['instrument_id']='B'
        for explanation in (b'{}',canonical(wrong)):
            with self.subTest(explanation=explanation):
                self.refusal(inputs=(),reports=(self.raw[0],explanation,self.raw[2]))
        self.refusal(inputs=(),reports=(*self.raw[:2],b'{}'))
    def test_missing_receipt_does_not_hide_corrupt_other_report(self) -> None:
        self.refusal(reports=(None,b'{}',self.raw[2]))
    def test_duplicate_unknown_input_role_refuses(self) -> None:
        self.refusal(inputs=(('trades',self.batch),('trades',self.batch)))
        self.refusal(inputs=(('unknown',self.batch),))
    def test_exact_narrative_nonascii_and_bounds(self) -> None:
        self.refusal(narrative='x'*129)
        self.refusal(narrative='\u00e9')
    def test_C24_unknown_tool_refuses(self) -> None:
        with self.assertRaises(research.ResearchExampleError):research.history((('caller_code',b'{}','succeeded'),),self.assess(),self.cfg,(('trades',self.batch),),self.result,self.raw[0])
    def test_all32calls_68events_independent_chain_before_append(self) -> None:
        calls=tuple(('equity_result_summary',summary_wire(),'succeeded') for _ in range(32))
        events=research.history(calls,self.assess(),self.cfg,(('trades',self.batch),),self.result,self.raw[0])
        self.assertEqual(len(events),68)
        wires,digest=independent_chain(events)
        self.assertEqual(wires,tuple(a.encode_event(x) for x in events))
        self.assertEqual(digest,a.event_digest(events[-1]))
        with tempfile.TemporaryDirectory(prefix='eq109-source-ledger-') as folder:
            path=str(Path(folder).resolve()/'events.sqlite');store=l.Ledger.create(path,'demo:research')
            try:terminal=research.record(store,events,store.head())
            finally:store.close()
            self.assertEqual(terminal,l.Checkpoint('demo:research',68,digest))
            reopened=l.Ledger.open(path)
            try:
                self.assertEqual(research.inspect_ledger(reopened,terminal,wires,retained_payloads=(summary_wire(),*self.raw),required_reports=self.assess().retained_payload_digests),research.LedgerObservation('verified','matched','complete'))
                self.assertEqual(research.inspect_ledger(reopened,None,wires,retained_payloads=(),required_reports=self.assess().retained_payload_digests),research.LedgerObservation('verified','not_supplied','missing'))
            finally:reopened.close()
    def test_C19_anchor_not_supplied_C20_removed_suffix_C21_valid_prefix(self) -> None:
        calls=(('equity_result_summary',summary_wire(),'succeeded'),)
        events=research.history(calls,self.assess(),self.cfg,(('trades',self.batch),),self.result,self.raw[0]);wires,digest=independent_chain(events)
        terminal=l.Checkpoint('demo:research',len(events),digest)
        with tempfile.TemporaryDirectory(prefix='eq109-prefix-') as folder:
            store=l.Ledger.create(str(Path(folder).resolve()/'events.sqlite'),'demo:research')
            try:
                research.record(store,events[:-1],store.head())
                self.assertIs(store.verify(expected=terminal).anchor_status,l.AnchorStatus.NOT_COVERED)
                with self.assertRaises(research.ResearchExampleError):research.inspect_ledger(store,terminal,wires,retained_payloads=(summary_wire(),*self.raw),required_reports=self.assess().retained_payload_digests)
                observed=research.inspect_ledger(store,None,wires[:-1],retained_payloads=(),required_reports=self.assess().retained_payload_digests)
                self.assertEqual(observed.anchor,'not_supplied')
            finally:store.close()
    def test_record_stale_checkpoint_no_automatic_replay(self) -> None:
        events=research.history((('equity_result_summary',summary_wire(),'succeeded'),),self.assess(),self.cfg,(('trades',self.batch),),self.result,self.raw[0])
        with tempfile.TemporaryDirectory(prefix='eq109-cas-') as folder:
            store=l.Ledger.create(str(Path(folder).resolve()/'events.sqlite'),'demo:research')
            try:
                before=store.head();research.record(store,events[:1],before)
                with self.assertRaises(l.LedgerError):research.record(store,events[:1],before)
                self.assertEqual(store.head().sequence,1)
            finally:store.close()


    def test_SRC01_unknown_metaclass_never_compared_or_hashed(self) -> None:
        class Meta(type):
            def __eq__(self,other: object) -> bool:raise AssertionError('metaclass eq callback')
            def __hash__(self) -> int:raise AssertionError('metaclass hash callback')
        class Unknown(metaclass=Meta):pass
        self.refusal(cfg=Unknown())
    def test_SRC01_missing_known_field_closed_error(self) -> None:
        self.refusal(cfg=object.__new__(c.ConfigSpec))
    def test_SRC02_arbitrary_or_changed_summary_refuses(self) -> None:
        for raw in (b'not-a-public-result-summary',b'{}',summary_wire()+b' '):
            with self.subTest(raw=raw[:20]),self.assertRaises(research.ResearchExampleError):
                research.history((('equity_result_summary',raw,'succeeded'),),self.assess(),self.cfg,(('trades',self.batch),),self.result,self.raw[0])
        value=json.loads(summary_wire());value['payload']['data']['backend_id']='forged'
        with self.assertRaises(research.ResearchExampleError):
            research.history((('equity_result_summary',canonical(value),'succeeded'),),self.assess(),self.cfg,(('trades',self.batch),),self.result,self.raw[0])
    def test_SRC02_changed_typed_producer_cannot_reuse_valid_summary(self) -> None:
        result=replace(self.result,values=(replace(self.result.values[0],values=(4,)),)+self.result.values[1:])
        with self.assertRaises(research.ResearchExampleError):
            research.history((('equity_result_summary',summary_wire(),'succeeded'),),self.assess(),self.cfg,(('trades',self.batch),),result,self.raw[0])
    def test_SRC03_retention_requires_actual_referenced_bytes(self) -> None:
        events=research.history((('equity_result_summary',summary_wire(),'succeeded'),),self.assess(),self.cfg,(('trades',self.batch),),self.result,self.raw[0])
        wires,digest=independent_chain(events)
        with tempfile.TemporaryDirectory(prefix='eq109-retention-') as folder:
            store=l.Ledger.create(str(Path(folder).resolve()/'events.sqlite'),'demo:research')
            try:
                terminal=research.record(store,events,store.head())
                for payloads in ((),(summary_wire(),),(summary_wire(),self.raw[0]),(summary_wire(),self.raw[0],self.raw[1],b'changed')):
                    with self.subTest(count=len(payloads)):
                        observed=research.inspect_ledger(store,terminal,wires,payloads,self.assess().retained_payload_digests)
                        self.assertEqual(observed.payload_retention,'missing')
                observed=research.inspect_ledger(store,terminal,wires,(summary_wire(),*self.raw),self.assess().retained_payload_digests)
                self.assertEqual(observed.payload_retention,'complete')
            finally:store.close()


    def test_SRC04_malformed_history_inputs_closed_error(self) -> None:
        for supplied in ((('trades',),),((1,self.batch),),((('trades',self.batch),)*2),()):
            if supplied==():continue
            with self.subTest(length=len(supplied)),self.assertRaises(research.ResearchExampleError):
                research.history((('equity_result_summary',summary_wire(),'succeeded'),),self.assess(),self.cfg,supplied,self.result,self.raw[0])
    def test_SRC05_report_kind_digest_cannot_alias_receipt(self) -> None:
        events=research.history((('equity_result_summary',summary_wire(),'succeeded'),),self.assess(),self.cfg,(('trades',self.batch),),self.result,self.raw[0])
        wires,digest=independent_chain(events)
        with tempfile.TemporaryDirectory(prefix='eq109-report-alias-') as folder:
            store=l.Ledger.create(str(Path(folder).resolve()/'events.sqlite'),'demo:research')
            try:
                terminal=research.record(store,events,store.head())
                alias=tuple((kind,hashlib.sha256(self.raw[0]).hexdigest()) for kind in ('receipt','explanation','diagnostics'))
                with self.assertRaises(research.ResearchExampleError):research.inspect_ledger(store,terminal,wires,(summary_wire(),self.raw[0]),alias)
            finally:store.close()


if __name__=='__main__':unittest.main()
