"""Pre-code synthetic fixture export with independent math; no graph/tracer implementation."""
import dataclasses,hashlib,importlib,json,math,pathlib,pickle,sys
from dataclasses import replace
from decimal import Context,Decimal,localcontext,ROUND_HALF_EVEN,InvalidOperation,DivisionByZero,Overflow
from enum import Enum
from fractions import Fraction as F
import argparse
import importlib.metadata
ROOT=pathlib.Path(__file__).resolve().parents[3]
P=ROOT/'docs/stories'
W=ROOT
parser=argparse.ArgumentParser(description=__doc__)
parser.add_argument('--output',type=pathlib.Path,required=True)
args=parser.parse_args()
inputs=json.loads((ROOT/'docs/R18_INPUTS.json').read_bytes())
for distribution,version in inputs['distributions'].items():
    assert importlib.metadata.version(distribution)==version,distribution
for module in ['equity_feature_contracts','equity_features','equity_features_intraday',
               'equity_feature_io_contracts','equity_feature_io_sdk','equity_feature_workers']:
    assert pathlib.Path(importlib.import_module(module).__file__).resolve().is_relative_to(pathlib.Path(sys.prefix).resolve()),module
sys.path.insert(0,str(W/'tests/intraday'))
from test_preparation import supplied
from test_admission import split
from equity_features_intraday import build_intraday_config,compute_intraday
from equity_feature_workers import TaskManifest,InputManifest,encode_task
from equity_feature_workers.intraday import intraday_headers,intraday_history
from equity_feature_contracts import InputBinding,IntervalSpec,Column,ErrorCode
from equity_feature_io_sdk import encode_result
manual=json.loads((P/'EQ-142_INDEPENDENT_CASES_DRAFT.json').read_bytes())
type_registry={}
def wire(v):
    if isinstance(v,Enum):return {'enum':type(v).__name__,'value':v.value}
    if dataclasses.is_dataclass(v):
        name=type(v).__name__;type_registry[name]=type(v).__module__+'.'+name
        return {'type':name,'fields':{f.name:wire(getattr(v,f.name)) for f in dataclasses.fields(v)}}
    if type(v) is tuple:return {'tuple':[wire(x) for x in v]}
    if v is None or type(v) in (str,int,bool):return v
    raise TypeError('Unsupported fixture value '+type(v).__name__)
def sha(v):return hashlib.sha256(v).hexdigest()
def fixture(xs,missing=()):
    return supplied(closes=xs,highs=tuple(x+1 for x in xs),lows=tuple(x-1 for x in xs),missing=missing,absent=('high','low'))
def config(ctx,cfg,period=3,k=F(2),limit=10):
    return build_intraday_config(ctx,period=period,band_k=k,availability=cfg.availability,
                                adjustment=cfg.adjustment,price_unit=cfg.price_unit,evidence_limit=limit)
def task_for(batches,ctx,cfg,features,partition):
    inputs=tuple(InputManifest(f'bars:{i:03}',sha(pickle.dumps(b,protocol=5)),'revision1',
         'complete' if b.metadata.coverage.complete else 'partial',InputBinding(f'bars:{i:03}',b.kind,b.metadata))
         for i,b in enumerate(batches))
    return TaskManifest('eq142-canonical-fixtures','generation1',partition,'intraday',(ctx.instrument_id,),cfg,
        intraday_headers(features),inputs,tuple(IntervalSpec(s.session_id,s.open_ns,s.close_ns) for s in ctx.sessions),
        'eq142-fixture-destination','serialized_destination',len(batches),1048576,*intraday_history(cfg,features))
CTX=Context(prec=240,rounding=ROUND_HALF_EVEN,Emin=-999999,Emax=999999,capitals=1,clamp=0,
            flags=[],traps=[InvalidOperation,DivisionByZero,Overflow])
def bands(xs,k=F(2)):
    mean=sum(map(F,xs))/len(xs);var=sum((F(x)-mean)**2 for x in xs)/len(xs)
    with localcontext(CTX):
        dec=lambda x:Decimal(x.numerator)/Decimal(x.denominator)
        m=dec(mean);r=dec(k)*dec(var).sqrt()
        return {'intraday.band_middle':float(m),'intraday.band_lower':float(m-r),'intraday.band_upper':float(m+r),
                'intraday.band_width_ratio':float(2*r/m),'intraday.band_position':None if r==0 else float((dec(F(xs[-1]))-m+r)/(2*r))}
def expected_cells(i,selected):
    result={}
    for f in selected:
        status='available';expected=observed=3;reasons=[];value=None
        if f=='intraday.ema':
            value=11.0
            if i==5:status='incomplete_coverage';expected=5;observed=4;reasons=['governed_gap'];value=None
        elif f=='intraday.rsi':status='insufficient_history';expected=4;reasons=['insufficient_history']
        elif f=='intraday.atr':
            if i==2:status='missing_input';expected=4;observed=1;reasons=['absent_input','insufficient_history']
            elif i==3:status='insufficient_history';expected=2;observed=1;reasons=['insufficient_history']
            else:expected=observed=2;value=3.0
        elif i==6:status='incomplete_coverage';observed=2;reasons=['governed_gap']
        else:
            xs=(10,11,12) if i==5 else (11,11,11) if i==7 else (1,1,100) if i==8 else (2**60-1,2**60,2**60+1)
            value=bands(xs,F(1,10) if i==8 else F(2))[f]
            if value is None:status='not_applicable';reasons=['zero_denominator']
        result[f]={'value':value,'status':status,'expected':expected,'observed':observed,'reasons':reasons}
    return result

# Independently hand-enumerated operand/output pairs; not imported from a graph builder.
PAIRS=[
 [('anchored_closes','intraday.ema')],
 [('anchored_closes','intraday.ema'),('anchored_closes','intraday.rsi')],
 [('anchored_closes','intraday.ema'),('true_ranges','intraday.atr')],
 [('true_ranges','intraday.atr')], [('true_ranges','intraday.atr')],
 [('anchored_closes','intraday.ema'),('price_moments','intraday.band_middle'),('price_moments','intraday.band_width_ratio'),('price_moments','intraday.band_position')],
 [('price_moments','intraday.band_middle')],
 [('price_moments','intraday.band_lower'),('price_moments','intraday.band_middle'),('price_moments','intraday.band_upper'),('price_moments','intraday.band_width_ratio'),('price_moments','intraday.band_position')],
 [('price_moments','intraday.band_position')],
 [('price_moments','intraday.band_middle'),('price_moments','intraday.band_lower'),('price_moments','intraday.band_upper'),('price_moments','intraday.band_width_ratio'),('price_moments','intraday.band_position')],
]
cases=[]
for i,original in enumerate(manual['cases'][:10]):
    if i<3:b,ctx,cfg=fixture((10,11,12))
    elif i==3:b,ctx,cfg=fixture((10,));cfg=config(ctx,cfg,period=1)
    elif i==4:
        b,ctx,cfg=supplied(closes=(10,11),highs=(11,12),lows=(9,9));a,z=split(b[0],1)
        b=(replace(a,columns=tuple(c for c in a.columns if c.name not in ('high','low'))),
           replace(z,columns=tuple(c for c in z.columns if c.name!='close')));cfg=config(ctx,cfg,period=1)
    elif i in (5,6):b,ctx,cfg=fixture((8,9,10,11,12),missing=(0,) if i==5 else (3,))
    elif i==7:b,ctx,cfg=fixture((11,11,11))
    elif i==8:b,ctx,cfg=fixture((1,1,100));cfg=config(ctx,cfg,k=F(1,10))
    else:b,ctx,cfg=fixture((2**60-1,2**60,2**60+1))
    selected=tuple(sorted(original['selected']));task=task_for(b,ctx,cfg,selected,'case'+str(i))
    expected=expected_cells(i,selected)
    # The independently generated expectations precede producer validation.
    actual=compute_intraday(b,ctx,cfg,features=selected);values={c.feature_id:c.values[0] for c in actual.values}
    for q in actual.quality:
        e=expected[q.feature_id]
        assert (q.status.value,q.expected,q.observed,[r.value for r in q.reasons])==(e['status'],e['expected'],e['observed'],e['reasons'])
        if e['value'] is None:assert values[q.feature_id] is None
        elif e['value']==0:assert values[q.feature_id]==0.0
        else:assert math.isclose(values[q.feature_id],e['value'],rel_tol=2e-15,abs_tol=0)
    slots={}
    if any(p[0]=='anchored_closes' for p in PAIRS[i]):slots['anchored_closes']={'close':list(range(ctx.anchor_index,ctx.target_index+1)),'high':[],'low':[]}
    if any(p[0]=='true_ranges' for p in PAIRS[i]):
        slots['true_ranges']={'close':[ctx.anchor_index] if ctx.target_index==ctx.anchor_index else list(range(ctx.anchor_index,ctx.target_index)),
                              'high':list(range(ctx.anchor_index+1,ctx.target_index+1)),
                              'low':list(range(ctx.anchor_index+1,ctx.target_index+1))}
    if any(p[0]=='price_moments' for p in PAIRS[i]):slots['price_moments']={'close':list(range(max(ctx.anchor_index,ctx.target_index-2),ctx.target_index+1)),'high':[],'low':[]}
    cases.append({'id':original['id'],'kind':'qualified_intraday_description','context_json':ctx.to_json(),
                  'task_json':encode_task(task).decode(),'task_sha256':task.task_sha256,'reuse_sha256':task.reuse_sha256,
                  'input_batches':wire(b),'original_observed_tuple_pickle_sha256':sha(pickle.dumps(b,protocol=5)),
                  'callback':{'module':'equity_feature_workers.intraday','export':'compute_intraday_inputs','relation':'actual_export_object'},
                  'expected_cells':expected,'expected_operand_output_reachability_pairs':PAIRS[i],'expected_required_slots':slots,
                  'forbidden_relation':'no_numerical_output_is_a_prerequisite_for_another_numerical_output',
                  'real_common_boundaries':['configuration','structural_admission','resource_admission','complete_result_join','publication_owner'],
                  'baseline_observed_parity':{'complete_result_sdk_sha256':sha(encode_result(actual)),
                      'result_bytes':len(encode_result(actual)),'evidence':[[e.feature_id,e.row_id] for e in actual.evidence]},
                  'parity_limit':'Full SDK hash is observed baseline parity only; expected_cells/operand pairs are independent mathematical/specification oracles.'})

b,ctx,cfg=supplied();base=task_for(b,ctx,cfg,('intraday.ema',),'structural')
invalid=replace(b[0],columns=tuple(Column(c.name,(11,8,13,15,15)) if c.name=='high' else c for c in b[0].columns))
cases.append({'id':manual['cases'][10]['id'],'kind':'common_invalid_input','context_json':ctx.to_json(),
 'task_json':encode_task(base).decode(),'input_batches':wire((invalid,)),
 'expected_error':{'class':'equity_feature_contracts.ContractError','code':ErrorCode.INVALID_SCHEMA.value},
 'graph_disposition':'Structural node remains a real requirement; no successful numerical output is asserted.'})
cases.append({'id':manual['cases'][11]['id'],'kind':'explicit_guarded_failure_injection','context_json':ctx.to_json(),
 'task_json':encode_task(task_for(b,ctx,cfg,('intraday.ema','intraday.band_middle'),'overflow')).decode(),'input_batches':wire(b),
 'fault_injection':{'target':'equity_features_intraday._dispatch.band_values','error_class':'equity_feature_contracts.ContractError','code':ErrorCode.OVERFLOW.value},
 'expected_error':{'class':'equity_feature_contracts.ContractError','code':ErrorCode.OVERFLOW.value,'whole_call':True},
 'limit':'Synthetic guard injection, not naturally overflowing admitted prices; never applied during measurements.'})
altered=replace(b[0],columns=tuple(Column(c.name,c.values[:-1]+(14,)) if c.name=='close' else c for c in b[0].columns))
cases.append({'id':manual['cases'][12]['id'],'kind':'same_declared_identity_conflict','context_json':ctx.to_json(),
 'task_json':encode_task(base).decode(),'input_batches':wire(b),'conflicting_batches':wire((altered,)),
 'second_task_transform':{'partition_id':'other'},'declared_identity_policy':'Keep original InputManifest acquisition/revision/metadata labels for both; do not replace with changed actual hash.',
 'expected_error':{'class':'equity_feature_io_contracts.SinkError','code':'CONFLICT','boundaries':['existing_cache_put','existing_supervisor_reuse_check']},
 'duplicate_task_error':{'class':'equity_feature_io_contracts.SinkError','code':'CONFLICT'},
 'expected_cache_reference':'original caller tuple object, not a deep copy or new content certificate'})
cases.append({'id':manual['cases'][13]['id'],'kind':'callback_relations','context_json':ctx.to_json(),
 'task_json':encode_task(base).decode(),'input_batches':wire(b),
 'variants':[{'construction':'same actual exported builtin under another caller variable','expected_disposition':'qualified_intraday_description'},
             {'construction':'FunctionType copied code/globals/name, not identical to inspected export','expected_disposition':'conservative_unresolved'},
             {'construction':'top-level caller delegating wrapper','expected_disposition':'conservative_unresolved'},
             {'construction':'unknown top-level caller FunctionType','expected_disposition':'conservative_unresolved'},
             {'construction':'module export or relevant inspected alias changed after baseline binding','expected_error':'source_mismatch'}],
 'limit':'Exact expected fixture constructions for the new graph qualifier; existing WorkItem pickling may reject copied function first. Preserve original admission errors.'})
cases.append({'id':manual['cases'][14]['id'],'kind':'generic_population_job_boundaries','base_task_json':encode_task(base).decode(),
 'input_batches':wire(b),'callback_fixture':'top-level never_called; any execution raises AssertionError',
 'task_transforms':[{'partition_id':'population0','instruments':['A']},{'partition_id':'population1','instruments':['A','B']},
                    {'partition_id':'population2','instruments':['B','C']},{'partition_id':'population3','instruments':['D']}],
 'configured_workers':4,'expected_components':[[0,1,2],[3]],'expected_actual_partition_count':2,
 'expected_task_graph_disposition':'conservative_unresolved','job_barriers':['population_component_order','all_worker_terminal_outcomes_before_coordinator_publication','serialized_publication_owner'],
 'limit':'Generic manifest partition fixture; the actual single-symbol intraday callback cannot compute multi-symbol tasks.'})
all_features=tuple(sorted(['intraday.ema','intraday.rsi','intraday.atr','intraday.band_middle','intraday.band_lower','intraday.band_upper','intraday.band_width_ratio','intraday.band_position']))
cfg=config(ctx,cfg,limit=2);last=task_for(b,ctx,cfg,all_features,'all-eight')
all_values=bands((11,14,13));all_values.update({'intraday.ema':float(F(51,4)),'intraday.rsi':float(F(200,3)),'intraday.atr':float(F(29,9))})
last_expected={f:{'value':all_values[f],'status':'available','expected':3 if '.band_' in f else 5,
                  'observed':3 if '.band_' in f else 5,'reasons':[]} for f in all_features}
last_actual=compute_intraday(b,ctx,cfg,features=all_features)
for c in last_actual.values:assert math.isclose(c.values[0],last_expected[c.feature_id]['value'],rel_tol=2e-15,abs_tol=0)
cases.append({'id':manual['cases'][15]['id'],'kind':'complete_result_and_publication','context_json':ctx.to_json(),
 'task_json':encode_task(last).decode(),'input_batches':wire(b),'expected_cells':last_expected,
 'expected_evidence':[['intraday.atr','slot:0'],['intraday.atr','slot:1']],
 'expected_complete_selected_headers':list(all_features),'evidence_limit':2,
 'publication_fixture':'original SerializedMemorySink; exact complete in-memory commit/lookup/readback; no physical durability',
 'limits':{'task_and_output_bytes':1048576,'publisher_pending_bytes':8388608,'publisher_pending_tasks':16,'receipt_wire_bytes':400000,
           'sink_max_results':1,'sink_max_chunk_bytes':1048576,'sink_max_total_bytes':1048576,'sink_max_result_cells':100,'sink_max_evidence_rows':100}})
for case in cases:
    if 'input_batches' in case:
        value_bytes=(json.dumps(case['input_batches'],sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
        case['canonical_value_body_sha256']=sha(b'eq142-typed-batch-values1\0'+value_bytes)
    if 'conflicting_batches' in case:
        value_bytes=(json.dumps(case['conflicting_batches'],sort_keys=True,separators=(',',':'),ensure_ascii=True,allow_nan=False)+'\n').encode('ascii')
        case['conflicting_canonical_value_body_sha256']=sha(b'eq142-typed-batch-values1\0'+value_bytes)
packet={'schema':'eq142-canonical-independent-fixtures:1','stage':'PRECODE_PROPOSAL_NOT_READY_OR_GRAPH_IMPLEMENTATION',
 'source':{'canonical_docs_head':'fbb3d30efbe37d9f0c56728787209764dde68ba8',
           'package_build_sources':{'core':'b1f5445eb9799b73753e413669b94166997fc468','worker':'231349aaf2bf1b9ec21f45807382ca9c6522520c','io':'18d86761aa3eebb7414e51e8fa2aba089717b5eb'}},
 'oracle':{'method':'Independent centered Fraction population moments/direct Decimal240 expressions; explicit first-seed/simple rational values; accepted API status/count/reasons; hand-enumerated operand edges.',
           'decimal_context':{'prec':240,'rounding':'ROUND_HALF_EVEN','Emin':-999999,'Emax':999999,'capitals':1,'clamp':0,
                              'flags':[],'traps':['InvalidOperation','DivisionByZero','Overflow']},
           'tolerance':{'relative':2e-15,'absolute':0,'zero_and_unavailable':'exact'},
           'generator_sha256_lf':sha(pathlib.Path(__file__).read_bytes().replace(b'\r\n',b'\n')),
           'not_oracles':['producer-generated graph','same scheduler twice','observed SDK parity hash alone']},
 'typed_batch_wire':{'tuple_marker':'tuple','dataclass_marker':'type/fields','enum_marker':'enum/value',
                     'closed_type_registry':dict(sorted(type_registry.items())),'closed_enums':['DataKind'],
                     'canonical_value_digest':'SHA256(b"eq142-typed-batch-values1\\0" + ASCII JSON(input_batches, sorted keys, separators comma/colon, ensure_ascii=true, allow_nan=false) + LF)',
                     'identity_limit':'Value records do not preserve Python aliasing, object interning or pickle memoization. Original observed tuple/batch pickle hashes are diagnostics only, not guaranteed reconstructed bytes.',
                     'declared_acquisition_policy':'Retain original task JSON InputManifest declared acquisition identities; no claim of fresh reconstructed-body pickle rehash/seal. Canonical value digest is a fixture-integrity identity, not a new production reuse authority.'},
 'cases':cases,'limits':['This exporter validates independent tiny producer expectations, not the unimplemented graph/tracer.',
                        'Canonical input/task bodies and independently authored expectations remain subject to separate final public-packet Ready review.',
                        'Existing finite Windows baseline source/version/origin proof applies; no new package, Linux, workload timing or release acceptance.']}
raw=(json.dumps(packet,indent=2,ensure_ascii=True,allow_nan=False)+'\n').encode()
out=args.output.resolve();assert not out.exists(),'Preserve prior output; choose a new path.';out.write_bytes(raw)
print(json.dumps({'result':'AUTHOR_CANONICAL16_FIXTURE_PROPOSAL_GENERATED_NOT_READY','cases':len(cases),'bytes':len(raw),'sha256':sha(raw),'types':len(type_registry)}))
