"""Fixed synthetic research consumer, outside numerical/MCP packages.

This source example recognizes one three-row fixture and its explicit late-known
variant. It demonstrates supplied-content consistency, never source or execution
authentication. SQLite and replay are explicit outer operations.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
import math
import re
from typing import Any, Literal

import equity_feature_contracts as c
from equity_feature_contracts import inputs as ci, results as cr, specs as cs
from equity_feature_evidence import (
    EnvironmentDeclaration, PackageVersion, ExecutionClaim, EvidenceDisclosure,
    canonical_content, make_content_receipt, encode_receipt, decode_receipt,
    fingerprint_result,
)
from equity_feature_explanations import explain_result, encode_explanation


class ResearchExampleError(ValueError):
    """Payload-free errors; caller objects and private causes are not rendered."""
    def __init__(self, code: str = 'invalid_input') -> None:
        self.code = code if type(code) is str and code in ('invalid_input', 'inconsistent_evidence', 'limit_exceeded', 'unsupported') else 'invalid_input'
        super().__init__('Synthetic research example rejected: ' + self.code)


def _require(ok: bool, code: str = 'invalid_input') -> None:
    if not ok:
        raise ResearchExampleError(code) from None


@dataclass(frozen=True)
class Assessment:
    narrative_status: Literal['matched', 'mismatch', 'unavailable', 'unsupported']
    configuration_status: Literal['verified']
    output_status: Literal['verified']
    receipt_status: Literal['verified', 'unavailable']
    explanation_status: Literal['verified', 'unavailable']
    diagnostics_status: Literal['verified', 'unavailable']
    expected_input_count: Literal[1]
    verified_input_count: Literal[0, 1]
    input_content_status: Literal['complete', 'missing']
    diagnostic_admission: Literal['not_applied', 'unavailable']
    decision: Literal['DEFER', 'REJECT']
    reason_code: Literal['incomplete_evidence', 'diagnostic_not_admitted', 'mismatch']
    retained_payload_digests: tuple[tuple[str, str], ...]
    source_authenticated: Literal[False] = False
    execution_verified: Literal[False] = False


@dataclass(frozen=True)
class ReplayObservation:
    status: str
    calculation_count: int


@dataclass(frozen=True)
class LedgerObservation:
    consistency: Literal['verified', 'unavailable']
    anchor: Literal['matched', 'not_supplied', 'not_covered', 'mismatch', 'unavailable']
    payload_retention: Literal['complete', 'missing']


@dataclass(frozen=True)
class ResearchObservation:
    assessment: Assessment
    replay: ReplayObservation
    ledger: LedgerObservation
    model_status: Literal['not_supplied'] = 'not_supplied'


# Explicit public-class field allowlist. No caller introspection or generic
# dataclass traversal happens before exact-type admission and graph limits.
_FIELDS: dict[type[Any], tuple[str, ...]] = {
    ci.CanonicalBatch: ('kind','columns','metadata'),
    ci.Column: ('name','values'),
    ci.BatchMetadata: ('namespace','source','coverage','price_unit','adjustment','sampling','quantity_unit','ordering','duplicate_policy','scope','interval_coverage'),
    ci.SourceBinding: ('source_id','snapshot_id','mapping_version','input_id'),
    ci.Coverage: ('expected','observed','complete'),
    ci.PriceUnit: ('scale','currency'),
    ci.AdjustmentSpec: ('basis','policy_version','action_snapshot','anchor'),
    ci.InputScope: ('start_ns','end_ns','eligibility_policy','include_opening_auction','include_closing_auction'),
    ci.IntervalCoverage: ('name','start_ns','end_ns','coverage'),
    cs.ConfigSpec: ('identity','algorithm_version','parameters','session','window','availability','adjustment','price_unit','schema_version'),
    cs.Parameter: ('name','value'),
    cs.SessionSpec: ('namespace','session_id','open_ns','close_ns','timezone_label','intervals','scheduled_close_ns','early_close','include_opening_auction','include_closing_auction'),
    cs.IntervalSpec: ('name','start_ns','end_ns'),
    cs.WindowSpec: ('count','target_session_id','governed_sessions','anchor'),
    cs.AvailabilitySpec: ('market_cutoff_ns','knowledge_cutoff_ns','evaluation_ns','mode','reconstruction_reason'),
    cr.FeatureResult: ('values','quality','metadata','evidence'),
    cr.FeatureColumn: ('feature_id','algorithm_version','dtype','unit','entities','values','schema_version'),
    cr.EntityKey: ('instrument_id','session_id'),
    cr.QualityRow: ('entity','feature_id','status','expected','observed','reasons'),
    cr.ResultMetadata: ('namespace','session_id','availability','config_digest','inputs','backend_id','backend_version','evidence_limit','schema_version','math_policy_version'),
    cr.InputBinding: ('role','kind','metadata','schema_version'),
    cr.EvidenceRow: ('entity','feature_id','input_id','row_id','event_ns','known_at_ns','effective_start_ns','effective_end_ns','use','exclusion_reason','boundary'),
}
_ENUMS = (ci.DataKind, cr.ValueType, cr.Status, cr.Reason)


def _copy_roots(roots: tuple[object, ...]) -> tuple[Any, ...]:
    """Bound graph before constructors, equality, conversion or hashing.

    Local Python is trusted; this does not sandbox concurrent mutation or code.
    Reject unknown types without repr/str/eq/iterator calls.
    """
    nodes = 0
    ancestors: set[int] = set()

    def copy(value: Any, depth: int) -> Any:
        nonlocal nodes
        nodes += 1
        _require(nodes <= 4096 and depth <= 16, 'limit_exceeded')
        kind = type(value)
        if value is None or kind is bool:
            return value
        if kind is int:
            _require(-(2**127) <= value < 2**127, 'limit_exceeded')
            return value
        if kind is float:
            _require(math.isfinite(value))
            return value
        if kind is str:
            _require(len(value) <= 128, 'limit_exceeded')
            _require(value.isascii())
            return value
        if any(kind is known for known in _ENUMS):
            return value
        fields=next((names for known,names in _FIELDS.items() if kind is known),None)
        _require(kind is tuple or fields is not None)
        _require(id(value) not in ancestors)
        ancestors.add(id(value))
        try:
            if kind is tuple:
                _require(len(value) <= 64, 'limit_exceeded')
                return tuple(copy(item, depth + 1) for item in value)
            assert fields is not None
            children = tuple(copy(getattr(value, name), depth + 1) for name in fields)
            return kind(**dict(zip(fields, children, strict=True)))
        except (c.ContractError,AttributeError,TypeError):
            raise ResearchExampleError() from None
        finally:
            ancestors.remove(id(value))

    return tuple(copy(root, 0) for root in roots)


def fixture(future_known: bool = False) -> tuple[c.ConfigSpec, c.CanonicalBatch, c.FeatureResult]:
    """Literal independent expected data; no calculator invocation or source I/O.

    The same complete values/configuration are frozen in EQ-109_ORACLES.json.
    Actual producers are compared to these facts outside their calculation.
    """
    _require(type(future_known) is bool)
    cfg = c.ConfigSpec('synthetic-bars','v1',(c.Parameter('eligibility_policy','example-v1'),),
        c.SessionSpec('demo','S',100,200,'caller-supplied'),c.WindowSpec(1,'S',('P','S')),
        c.AvailabilitySpec(200,210,210),price_unit=c.PriceUnit(0,'USD'))
    batch = c.CanonicalBatch(c.DataKind.TRADE,tuple(c.Column(name, values) for name,values in (
        ('instrument_id',('A',)*3),('session_id',('S',)*3),('event_ns',(110,130,160)),
        ('order_key',(1,2,3)),('event_id',('t1','t2','t3')),('eligible',(True,)*3),
        ('price',(100,102,101)),('size',(2,3,5)),('known_at_ns',(110,130,211 if future_known else 210)),
    )),c.BatchMetadata('demo',c.SourceBinding('synthetic','snapshot1','map1','trades'),
        c.Coverage(3,3,True),c.PriceUnit(0,'USD'),scope=c.InputScope(100,200,'example-v1')))
    descriptions = (
        ('session.trade.count',c.ValueType.INT64,'trades',3),
        ('session.trade.volume',c.ValueType.INT64,'shares',10),
        ('session.trade.notional',c.ValueType.DECIMAL128,'currency coefficient / 10^price_scale',1011),
        ('session.trade.vwap',c.ValueType.FLOAT64,'currency/share',101.1),
        ('session.trade.mean_size',c.ValueType.FLOAT64,'shares/trade',10/3),
    )
    entity = c.EntityKey('A','S')
    values = tuple(c.FeatureColumn(fid,'v1',dtype,unit,(entity,),(None if future_known else number,))
                   for fid,dtype,unit,number in descriptions)
    quality = tuple(c.QualityRow(entity,fid,c.Status.MISSING_INPUT if future_known else c.Status.AVAILABLE,
        3,3,(c.Reason.FUTURE_KNOWLEDGE,) if future_known else ()) for fid,_,_,_ in descriptions)
    metadata = c.ResultMetadata('demo','S',cfg.availability,cfg.digest,
        (c.InputBinding('trades',batch.kind,batch.metadata),),'python-exact','0.0.4a4')
    return cfg,batch,c.FeatureResult(values,quality,metadata)


def _expected_receipt(cfg: c.ConfigSpec, batch: c.CanonicalBatch, result: c.FeatureResult) -> Any:
    return make_content_receipt(result,cfg,(('trades',batch),),
        EnvironmentDeclaration('CPython','3.12','synthetic-qualification',(
            PackageVersion('equity-feature-contracts','0.0.4a4'),PackageVersion('equity-features','0.0.4a4'))),
        ExecutionClaim(),EvidenceDisclosure('not_supplied',0))


def _json(value: object) -> bytes:
    return json.dumps(value,ensure_ascii=True,sort_keys=True,separators=(',',':'),allow_nan=False).encode('ascii')


def expected_reports(future_known: bool = False) -> tuple[bytes, bytes, bytes]:
    """Fixed expected owner projections, independent of received report bytes."""
    cfg,batch,result = fixture(future_known)
    receipt = _expected_receipt(cfg,batch,result)
    explanation = encode_explanation(explain_result(result,receipt,cfg,entity=c.EntityKey('A','S'),
        feature_id='session.trade.count',evidence_limit=16))
    fp = receipt.output
    fingerprint = dict(domain=fp.domain,digest=fp.digest,byte_length=str(fp.byte_length),
        schema_version=fp.schema_version,canonicalization=fp.canonicalization,algorithm=fp.algorithm)
    report = dict(schema_version='1',context=dict(namespace='demo',entity=dict(instrument_id='A',session_id='S'),
        availability=dict(market_cutoff_ns='200',knowledge_cutoff_ns='210',evaluation_ns='210',mode='known_at',reconstruction_reason=None)),
        policy=dict(policy_id='synthetic-advisory',mode='advisory',unknown_action='deny'),
        findings=[dict(check_id='observation',subject_id='synthetic-output',kind='freshness',content=fingerprint,
            status='unknown',severity='warning',reasons=['missing_observation'],assessed=False,unknown_prerequisites='1',age_ns=None)],
        requested_count=1,passed_count=0,failed_count=0,unknown_count=1,assessed_count=0,unknown_prerequisite_count='1',
        not_requested=['adjustment','declared_context','knowledge_time','market_time','membership','revision'],
        admission='not_applied',source_authenticated=False,historical_acquisition_verified=False)
    diagnostic = _json(dict(representation='equity.mcp.diagnostics.v1',schema_version='1',report=report,
        associations=[dict(check_id='observation',role='output',input_role=None,input_id=None)],input_content_verified=False))
    return encode_receipt(receipt),explanation,diagnostic


def _shape(cfg: Any, inputs: Any, result: Any) -> None:
    _require(type(cfg) is c.ConfigSpec and type(result) is c.FeatureResult)
    _require(len(cfg.parameters)==1 and len(cfg.session.intervals)==0
        and cfg.window.governed_sessions==('P','S'))
    _require(len(result.values)==5 and len(result.quality)==5 and len(result.evidence)<=16
        and len(result.metadata.inputs)==1)
    for column in result.values:
        _require(len(column.entities)==1 and len(column.values)==1)
    for _,batch in inputs:
        _require(type(batch) is c.CanonicalBatch and len(batch.columns)<=16
            and len(batch.metadata.interval_coverage)==0)
        for column in batch.columns:
            _require(len(column.values)==3)


def assess(configuration: c.ConfigSpec, inputs: tuple[tuple[str,c.CanonicalBatch],...],
           producer: c.FeatureResult, receipt: bytes | None, explanation: bytes | None,
           diagnostics: bytes | None, narrative: str) -> Assessment:
    """Validate all present content before classifying this fixed narrative."""
    reports = (receipt,explanation,diagnostics)
    _require(all(type(x) is bytes or x is None for x in reports))
    _require(all(x is None or len(x)<=32768 for x in reports), 'limit_exceeded')
    _require(sum(len(x) for x in reports if x is not None)<=65536, 'limit_exceeded')
    _require(type(narrative) is str)
    _require(len(narrative)<=128,'limit_exceeded')
    _require(narrative.isascii())
    _require(type(inputs) is tuple and len(inputs)<=1)
    for pair in inputs:
        _require(type(pair) is tuple and len(pair)==2 and type(pair[0]) is str)
        _require(pair[0]=='trades')
    cfg, supplied, result = _copy_roots((configuration,inputs,producer))
    _shape(cfg,supplied,result)
    raw = (canonical_content(cfg),canonical_content(result))+tuple(canonical_content(x) for _,x in supplied)
    _require(all(len(x)<=16384 for x in raw) and sum(map(len,raw))<=49152, 'limit_exceeded')
    selected: bool | None = None
    for future in (False,True):
        want_cfg,want_batch,want_result = fixture(future)
        if raw[0]==canonical_content(want_cfg) and raw[1]==canonical_content(want_result):
            if supplied:
                _require(raw[2]==canonical_content(want_batch),'inconsistent_evidence')
            selected=future
            break
    _require(selected is not None,'inconsistent_evidence')
    expected = expected_reports(bool(selected))
    if receipt is not None:
        try:
            _require(encode_receipt(decode_receipt(receipt))==receipt,'inconsistent_evidence')
        except ValueError:
            raise ResearchExampleError('inconsistent_evidence') from None
    for actual,wanted in zip(reports,expected,strict=True):
        _require(actual is None or actual==wanted,'inconsistent_evidence')
    complete_reports = all(x is not None for x in reports)
    state: Literal['matched','mismatch','unavailable','unsupported']
    if not complete_reports or selected:
        state='unavailable'
    elif re.fullmatch(r'session\.trade\.count=(0|[1-9][0-9]*)',narrative) is None:
        state='unsupported'
    else:
        state='matched' if narrative=='session.trade.count=3' else 'mismatch'
    decision: Literal['DEFER','REJECT'] = 'REJECT' if state=='mismatch' else 'DEFER'
    reason: Literal['mismatch','incomplete_evidence','diagnostic_not_admitted']
    reason='mismatch' if decision=='REJECT' else 'incomplete_evidence' if not supplied or state in ('unavailable','unsupported') else 'diagnostic_not_admitted'
    return Assessment(state,'verified','verified','verified' if receipt is not None else 'unavailable',
        'verified' if explanation is not None else 'unavailable','verified' if diagnostics is not None else 'unavailable',
        1,1 if supplied else 0,'complete' if supplied else 'missing','not_applied' if diagnostics is not None else 'unavailable',
        decision,reason,tuple(sorted((kind,hashlib.sha256(x).hexdigest()) for kind,x in zip(('receipt','explanation','diagnostics'),reports,strict=True) if x is not None)))


def replay(configuration: c.ConfigSpec, inputs: tuple[tuple[str,c.CanonicalBatch],...], producer: c.FeatureResult,
           receipt: bytes | None, explanation: bytes | None, diagnostics: bytes | None,
           narrative: str, *, cancel_before_start: bool = False) -> ReplayObservation:
    """Explicit one-calculator replay; absent evidence is never reconstructed."""
    assessment=assess(configuration,inputs,producer,receipt,explanation,diagnostics,narrative)
    _require(type(cancel_before_start) is bool)
    if 'unavailable' in (assessment.receipt_status,assessment.explanation_status,assessment.diagnostics_status):
        return ReplayObservation('not_requested',0)
    from equity_feature_bundles import PublicationDeclaration,write_bundle,read_bundle
    from equity_feature_bundles.replay import replay_bundle
    assert receipt is not None
    cfg,supplied,result=_copy_roots((configuration,inputs,producer))
    bundle=read_bundle(write_bundle(decode_receipt(receipt),cfg,result,supplied,
        PublicationDeclaration('synthetic','Fixed caller-created synthetic research example','caller_owned')))
    actual=replay_bundle(bundle,cancel_before_start=cancel_before_start)
    return ReplayObservation(actual.status,actual.calculation_count)


def record(store: Any, records: tuple[Any,...], expected_before: Any) -> Any:
    """One CAS append per event; uncertain outcomes require manual reconciliation."""
    from equity_feature_agent_ledger import Ledger,Checkpoint
    from equity_feature_agent_evidence import EventRecord,encode_event
    _require(type(store) is Ledger and type(expected_before) is Checkpoint)
    _require(type(records) is tuple and len(records)<=68,'limit_exceeded')
    _require(all(type(x) is EventRecord for x in records))
    head=expected_before
    for event in records:
        _require(len(encode_event(event))<=16384,'limit_exceeded')
        head=store.append(event,expected=head)
    return head


# Fixed complete public producer fixture, not a reconstructed transport receipt.
_PRODUCER = {'backend_id': 'python-exact',
 'backend_version': '0.0.4a4',
 'columns': [{'algorithm_version': 'v1',
              'dtype': 'int64',
              'entities': [{'instrument_id': 'A', 'session_id': 'S'}],
              'feature_id': 'session.trade.count',
              'schema_version': '1',
              'unit': 'trades',
              'values': [{'type': 'int64', 'value': '3'}]},
             {'algorithm_version': 'v1',
              'dtype': 'int64',
              'entities': [{'instrument_id': 'A', 'session_id': 'S'}],
              'feature_id': 'session.trade.volume',
              'schema_version': '1',
              'unit': 'shares',
              'values': [{'type': 'int64', 'value': '10'}]},
             {'algorithm_version': 'v1',
              'dtype': 'decimal128',
              'entities': [{'instrument_id': 'A', 'session_id': 'S'}],
              'feature_id': 'session.trade.notional',
              'schema_version': '1',
              'unit': 'currency coefficient / 10^price_scale',
              'values': [{'coefficient': '1011', 'scale': 0, 'type': 'decimal128'}]},
             {'algorithm_version': 'v1',
              'dtype': 'float64',
              'entities': [{'instrument_id': 'A', 'session_id': 'S'}],
              'feature_id': 'session.trade.vwap',
              'schema_version': '1',
              'unit': 'currency/share',
              'values': [{'bits': '4059466666666666', 'type': 'float64'}]},
             {'algorithm_version': 'v1',
              'dtype': 'float64',
              'entities': [{'instrument_id': 'A', 'session_id': 'S'}],
              'feature_id': 'session.trade.mean_size',
              'schema_version': '1',
              'unit': 'shares/trade',
              'values': [{'bits': '400aaaaaaaaaaaab', 'type': 'float64'}]}],
 'command_digest': '94abf5050a221fe5a47bd2727ee465b23f9910d044dd3dd4d26929fed49537c3',
 'context': {'availability': {'evaluation_ns': '210',
                              'knowledge_cutoff_ns': '210',
                              'market_cutoff_ns': '200',
                              'mode': 'known_at',
                              'reconstruction_reason': None},
             'config': {'algorithm_version': 'v1',
                        'config_id': 'synthetic-bars',
                        'digest': 'ddc1b3b90e8d3333f31c268228e472aa440029f3f6ba7d72745d2f0096c3c931',
                        'revision': 'owned-config-v1',
                        'schema_version': '1'},
             'dataset': {'dataset_id': 'owned.trades',
                         'input_id': 'trades',
                         'mapping_version': 'map1',
                         'revision': 'owned-v1',
                         'snapshot_id': 'snapshot1',
                         'source_id': 'synthetic'},
             'features': [{'algorithm_version': 'v1', 'feature_id': 'session.trade.volume'}],
             'math_policy_version': 'v1',
             'namespace': 'demo',
             'registry_snapshot': '89cf8b68c6e854a1fa4139ce264353cf8000445743c05673bdf8fefeb4b69086'},
 'evidence': [],
 'executed_features': [{'algorithm_version': 'v1', 'feature_id': 'session.trade.count'},
                       {'algorithm_version': 'v1', 'feature_id': 'session.trade.volume'},
                       {'algorithm_version': 'v1', 'feature_id': 'session.trade.notional'},
                       {'algorithm_version': 'v1', 'feature_id': 'session.trade.vwap'},
                       {'algorithm_version': 'v1', 'feature_id': 'session.trade.mean_size'}],
 'metadata': {'fields': {'availability': {'fields': {'evaluation_ns': {'type': 'int64',
                                                                       'value': '210'},
                                                     'knowledge_cutoff_ns': {'type': 'int64',
                                                                             'value': '210'},
                                                     'market_cutoff_ns': {'type': 'int64',
                                                                          'value': '200'},
                                                     'mode': {'type': 'string',
                                                              'value': 'known_at'},
                                                     'reconstruction_reason': None},
                                          'name': 'AvailabilitySpec',
                                          'type': 'record'},
                         'backend_id': {'type': 'string', 'value': 'python-exact'},
                         'backend_version': {'type': 'string', 'value': '0.0.4a4'},
                         'config_digest': {'type': 'string',
                                           'value': 'ddc1b3b90e8d3333f31c268228e472aa440029f3f6ba7d72745d2f0096c3c931'},
                         'evidence_limit': {'type': 'int64', 'value': '0'},
                         'inputs': {'items': [{'fields': {'kind': {'type': 'string',
                                                                   'value': 'trade'},
                                                          'metadata': {'fields': {'adjustment': {'fields': {'action_snapshot': {'type': 'string',
                                                                                                                                'value': 'none'},
                                                                                                            'anchor': {'type': 'string',
                                                                                                                       'value': 'none'},
                                                                                                            'basis': {'type': 'string',
                                                                                                                      'value': 'raw'},
                                                                                                            'policy_version': {'type': 'string',
                                                                                                                               'value': 'raw-v1'}},
                                                                                                 'name': 'AdjustmentSpec',
                                                                                                 'type': 'record'},
                                                                                  'coverage': {'fields': {'complete': {'type': 'bool',
                                                                                                                       'value': True},
                                                                                                          'expected': {'type': 'int64',
                                                                                                                       'value': '3'},
                                                                                                          'observed': {'type': 'int64',
                                                                                                                       'value': '3'}},
                                                                                               'name': 'Coverage',
                                                                                               'type': 'record'},
                                                                                  'duplicate_policy': {'type': 'string',
                                                                                                       'value': 'reject'},
                                                                                  'interval_coverage': {'items': [],
                                                                                                        'type': 'list'},
                                                                                  'namespace': {'type': 'string',
                                                                                                'value': 'demo'},
                                                                                  'ordering': {'type': 'string',
                                                                                               'value': 'declared'},
                                                                                  'price_unit': {'fields': {'currency': {'type': 'string',
                                                                                                                         'value': 'USD'},
                                                                                                            'scale': {'type': 'int64',
                                                                                                                      'value': '0'}},
                                                                                                 'name': 'PriceUnit',
                                                                                                 'type': 'record'},
                                                                                  'quantity_unit': {'type': 'string',
                                                                                                    'value': 'shares'},
                                                                                  'sampling': {'type': 'string',
                                                                                               'value': 'none'},
                                                                                  'scope': {'fields': {'eligibility_policy': {'type': 'string',
                                                                                                                              'value': 'example-v1'},
                                                                                                       'end_ns': {'type': 'int64',
                                                                                                                  'value': '200'},
                                                                                                       'include_closing_auction': {'type': 'bool',
                                                                                                                                   'value': False},
                                                                                                       'include_opening_auction': {'type': 'bool',
                                                                                                                                   'value': False},
                                                                                                       'start_ns': {'type': 'int64',
                                                                                                                    'value': '100'}},
                                                                                            'name': 'InputScope',
                                                                                            'type': 'record'},
                                                                                  'source': {'fields': {'input_id': {'type': 'string',
                                                                                                                     'value': 'trades'},
                                                                                                        'mapping_version': {'type': 'string',
                                                                                                                            'value': 'map1'},
                                                                                                        'snapshot_id': {'type': 'string',
                                                                                                                        'value': 'snapshot1'},
                                                                                                        'source_id': {'type': 'string',
                                                                                                                      'value': 'synthetic'}},
                                                                                             'name': 'SourceBinding',
                                                                                             'type': 'record'}},
                                                                       'name': 'BatchMetadata',
                                                                       'type': 'record'},
                                                          'role': {'type': 'string',
                                                                   'value': 'trades'},
                                                          'schema_version': {'type': 'string',
                                                                             'value': '1'}},
                                               'name': 'InputBinding',
                                               'type': 'record'}],
                                    'type': 'list'},
                         'math_policy_version': {'type': 'string', 'value': 'v1'},
                         'namespace': {'type': 'string', 'value': 'demo'},
                         'schema_version': {'type': 'string', 'value': '1'},
                         'session_id': {'type': 'string', 'value': 'S'}},
              'name': 'ResultMetadata',
              'type': 'record'},
 'next_cursor': None,
 'quality': [{'entity': {'instrument_id': 'A', 'session_id': 'S'},
              'expected': '3',
              'feature_id': 'session.trade.count',
              'observed': '3',
              'reasons': [],
              'status': 'available'},
             {'entity': {'instrument_id': 'A', 'session_id': 'S'},
              'expected': '3',
              'feature_id': 'session.trade.volume',
              'observed': '3',
              'reasons': [],
              'status': 'available'},
             {'entity': {'instrument_id': 'A', 'session_id': 'S'},
              'expected': '3',
              'feature_id': 'session.trade.notional',
              'observed': '3',
              'reasons': [],
              'status': 'available'},
             {'entity': {'instrument_id': 'A', 'session_id': 'S'},
              'expected': '3',
              'feature_id': 'session.trade.vwap',
              'observed': '3',
              'reasons': [],
              'status': 'available'},
             {'entity': {'instrument_id': 'A', 'session_id': 'S'},
              'expected': '3',
              'feature_id': 'session.trade.mean_size',
              'observed': '3',
              'reasons': [],
              'status': 'available'}]}

def _public_wire(raw: bytes) -> Any:
    # Lexical depth before json.loads; no arbitrary callbacks or over-depth parse.
    _require(type(raw) is bytes and len(raw)<=65536,'limit_exceeded')
    quoted=escaped=False
    depth=0
    for byte in raw:
        _require(32<=byte<=126,'inconsistent_evidence')
        if quoted:
            if escaped:escaped=False
            elif byte==92:escaped=True
            elif byte==34:quoted=False
        elif byte==34:quoted=True
        elif byte in (91,123):
            depth+=1;_require(depth<=20,'limit_exceeded')
        elif byte in (93,125):depth-=1
    try:
        value=json.loads(raw)
        _require(_json(value)==raw,'inconsistent_evidence')
    except (ValueError,RecursionError,OverflowError):
        raise ResearchExampleError('inconsistent_evidence') from None
    _require(type(value) is dict and type(value.get('ok')) is bool,'inconsistent_evidence')
    return value


def _summary_bound(value: Any) -> None:
    _require(set(value)=={'ok','payload'} and value['ok'] is True,'inconsistent_evidence')
    payload=value['payload']
    _require(type(payload) is dict and set(payload)=={'representation','reference','data'},'inconsistent_evidence')
    _require(payload['representation']=='complete_transported_producer' and type(payload['reference']) is str,'inconsistent_evidence')
    _require(re.fullmatch('[A-Za-z0-9_-]{43}',payload['reference']) is not None,'inconsistent_evidence')
    _require(_json(payload['data'])==_json(_PRODUCER),'inconsistent_evidence')


# Calls are supplied by the external orchestration after actual public operations;
# this function neither dispatches tools nor reconstructs unobserved responses.
_TOOL_NAMES = ('equity_discover', 'equity_slice', 'equity_calculate', 'equity_job_status', 'equity_job_cancel', 'equity_result_summary', 'equity_artifact_reference', 'equity_receipt', 'equity_explanation', 'equity_diagnostics', 'equity_evidence_read', 'equity_evidence_capabilities')


def history(calls: tuple[tuple[str,bytes,str],...], assessment: Assessment,
            configuration: c.ConfigSpec, inputs: tuple[tuple[str,c.CanonicalBatch],...],
            producer: c.FeatureResult, receipt: bytes | None) -> tuple[Any,...]:
    """Record every observed call/chunk pair; no model or human approval claim."""
    import equity_feature_agent_evidence as a
    from equity_feature_evidence import fingerprint_config,fingerprint_batch,InputFingerprint
    _require(type(calls) is tuple and 1<=len(calls)<=32,'limit_exceeded')
    _require(type(assessment) is Assessment)
    _require(assessment.decision in ('DEFER','REJECT'))
    _require(receipt is None or type(receipt) is bytes)
    _require(receipt is None or len(receipt)<=32768,'limit_exceeded')
    _require(type(inputs) is tuple and len(inputs)<=1)
    for input_pair in inputs:
        _require(type(input_pair) is tuple and len(input_pair)==2 and type(input_pair[0]) is str and input_pair[0]=='trades' and type(input_pair[1]) is c.CanonicalBatch)
    cfg,supplied,result=_copy_roots((configuration,inputs,producer))
    _shape(cfg,supplied,result)
    fixed_cfg,fixed_batch,fixed_result=fixture()
    _require(canonical_content(cfg)==canonical_content(fixed_cfg) and canonical_content(result)==canonical_content(fixed_result),'inconsistent_evidence')
    for role,batch in supplied:
        _require(role=='trades' and canonical_content(batch)==canonical_content(fixed_batch),'inconsistent_evidence')
    _require(receipt is None or receipt==expected_reports()[0],'inconsistent_evidence')
    for pair in calls:
        _require(type(pair) is tuple and len(pair)==3 and type(pair[0]) is str and type(pair[1]) is bytes and type(pair[2]) is str)
        _require(pair[0] in _TOOL_NAMES and pair[2] in ('succeeded','failed','cancelled','unknown'))
        _require(len(pair[1])<=65536,'limit_exceeded')
    _require(sum(len(pair[1]) for pair in calls)<=1048576,'limit_exceeded')
    events: list[Any]=[]
    actor=a.ActorDeclaration('synthetic-agent',a.ActorKind.SOFTWARE)
    absent=a.TimeDeclaration(None,None,None)
    context=a.DecisionContext('demo','S',cfg.availability)
    def add(subject: Any) -> Any:
        prev='0'*64 if not events else a.event_digest(events[-1])
        value=a.EventRecord('demo:research',len(events)+1,'demo:event-'+str(len(events)+1),
            actor,absent,absent,prev,subject)
        events.append(value)
        return a.event_reference(value)
    request=add(a.RequestSubject('synthetic-request','check fixed count against retained evidence',context))
    add(a.ModelSubject(None,None,None,a.ModelIdentityState.NOT_SUPPLIED))
    result_ref=None
    for name,raw,outcome in calls:
        value=_public_wire(raw)
        _require((outcome=='succeeded')==value['ok'],'inconsistent_evidence')
        if name=='equity_result_summary' and outcome=='succeeded':
            _summary_bound(value)
        call=add(a.ToolCallSubject(request,name,None,a.ArgumentSet(a.DisclosureState.REDACTED,None,())))
        observed=add(a.ToolResultSubject(call,a.ToolOutcome(outcome),
            a.PayloadReference(a.PayloadKind.TOOL_RESULT,hashlib.sha256(raw).hexdigest(),len(raw),len(raw),a.DisclosureState.RETAINED_COMPLETE)))
        if name=='equity_result_summary' and outcome=='succeeded':
            result_ref=observed
    _require(result_ref is not None,'inconsistent_evidence')
    assert result_ref is not None
    retained=a.PayloadReference(a.PayloadKind.EXECUTION_RECEIPT,
        None if receipt is None else hashlib.sha256(receipt).hexdigest(),0 if receipt is None else len(receipt),
        None if receipt is None else len(receipt),a.DisclosureState.NOT_SUPPLIED if receipt is None else a.DisclosureState.RETAINED_COMPLETE)
    read=add(a.FeatureReadSubject(result_ref,retained,fingerprint_config(cfg),
        tuple(InputFingerprint(role,b.metadata.source.input_id,fingerprint_batch(b)) for role,b in supplied),
        fingerprint_result(result),('session.trade.count',),context))
    add(a.DecisionSubject(request,(read,),a.DecisionAction.DEFER if assessment.decision=='DEFER' else a.DecisionAction.REJECT,assessment.reason_code))
    return tuple(events)


def inspect_ledger(store: Any, terminal: Any | None, expected_wires: tuple[bytes,...],
                   retained_payloads: tuple[bytes,...],
                   required_reports: tuple[tuple[str,str],...]) -> LedgerObservation:
    """Check actual referenced bytes and full chain against external context.

    required_reports is the assessment's explicit digest tuple; missing required
    report kinds remain missing even if all event wires have been retained.
    """
    import equity_feature_agent_ledger as l
    import equity_feature_agent_evidence as a
    _require(type(store) is l.Ledger and (terminal is None or type(terminal) is l.Checkpoint))
    _require(type(expected_wires) is tuple and len(expected_wires)<=68,'limit_exceeded')
    _require(all(type(x) is bytes and len(x)<=16384 for x in expected_wires))
    _require(type(retained_payloads) is tuple and len(retained_payloads)<=72,'limit_exceeded')
    _require(all(type(x) is bytes and len(x)<=65536 for x in retained_payloads))
    _require(sum(len(x) for x in retained_payloads)<=1048576,'limit_exceeded')
    _require(type(required_reports) is tuple and len(required_reports)<=3)
    for pair in required_reports:
        _require(type(pair) is tuple and len(pair)==2 and all(type(x) is str for x in pair))
        _require(pair[0] in ('receipt','explanation','diagnostics') and re.fullmatch('[0-9a-f]{64}',pair[1]) is not None)
    _require(len({x[0] for x in required_reports})==len(required_reports))
    expected_report_digests={kind:hashlib.sha256(raw).hexdigest() for kind,raw in zip(('receipt','explanation','diagnostics'),expected_reports(),strict=True)}
    _require(all(digest==expected_report_digests[kind] for kind,digest in required_reports),'inconsistent_evidence')
    retained={hashlib.sha256(raw).hexdigest():raw for raw in retained_payloads}
    complete=set(x[0] for x in required_reports)=={'receipt','explanation','diagnostics'}
    complete=complete and all(digest in retained for _,digest in required_reports)
    verified=store.verify(expected=terminal)
    through=verified.head
    checkpoint=l.Checkpoint(through.chain_id,0,'0'*64)
    actual: list[bytes]=[]
    while checkpoint.sequence<through.sequence:
        page=store.export_page(after=checkpoint.sequence,through=through,limit=64)
        checked=l.verify_page(page,start=checkpoint,through=through)
        _require(page.after.sequence>checkpoint.sequence,'inconsistent_evidence')
        for event in page.events:
            actual.append(a.encode_event(event))
            subject=event.subject
            reference=subject.payload if type(subject) is a.ToolResultSubject else subject.receipt if type(subject) is a.FeatureReadSubject else None
            if reference is not None:
                raw=retained.get(reference.digest) if reference.digest is not None else None
                matched=a.verify_payload(reference,raw).retained_matched
                complete=complete and matched and reference.state is a.DisclosureState.RETAINED_COMPLETE
        checkpoint=page.after
        _require(len(actual)<=68,'limit_exceeded')
        _require(checked.reached_terminal==(checkpoint==through),'inconsistent_evidence')
    _require(tuple(actual)==expected_wires,'inconsistent_evidence')
    if verified.anchor_status is l.AnchorStatus.MATCHED_TERMINAL:
        anchor: Literal['matched','not_supplied','not_covered','mismatch','unavailable']='matched'
    elif verified.anchor_status is l.AnchorStatus.NOT_SUPPLIED:
        anchor='not_supplied'
    elif verified.anchor_status is l.AnchorStatus.NOT_COVERED:
        anchor='not_covered'
    else:
        anchor='mismatch'
    return LedgerObservation('verified',anchor,'complete' if complete else 'missing')
