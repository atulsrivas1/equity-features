"""Outer installed-consumer measurements; no clock or I/O inside calculations."""
from __future__ import annotations
import argparse
from dataclasses import asdict
from decimal import Decimal, InvalidOperation
from fractions import Fraction
import json
import math
import os
from pathlib import Path
import platform
import time
import equity_feature_conformance as c
import equity_feature_diagnostics as d
from equity_feature_contracts import AvailabilitySpec, EntityKey, ReferenceFact, SourceBinding

ORACLE=Path(__file__).resolve().parents[1]/'docs/stories/EQ-105_MEASUREMENT_ORACLE.json'
IDS=('k1','k16','k32','m512')
COUNTS=((1,0),(16,0),(32,0),(4,512))


class MeasurementError(ValueError):
    def __init__(self,code='invalid_schema'):
        self.code=code
        super().__init__('Measurement rejected: '+code)


def require(value,code='invalid_schema'):
    if not value:raise MeasurementError(code)


def exact(actual,expected):
    """JSON-shaped equality that does not accept bool as int or ignore keys."""
    require(type(actual) is type(expected))
    if type(expected) is dict:
        require(actual.keys()==expected.keys())
        for key in expected:exact(actual[key],expected[key])
    elif type(expected) is list:
        require(len(actual)==len(expected))
        for a,b in zip(actual,expected):exact(a,b)
    else:require(actual==expected)


def shape(value,keys):require(type(value) is dict and set(value)==set(keys))


def integer(value,low,high):require(type(value) is int and low<=value<=high)


def normalized(value):
    # asdict returns tuples for tuple fields; the private report uses JSON lists.
    return json.loads(json.dumps(asdict(value)))


def assertion(value):
    return c.DiagnosticSnapshot(c.ContextSnapshot(**value['context']),c.PolicySnapshot(**value['policy']),
        tuple(c.FindingSnapshot(**f) for f in value['findings']),value['requested_count'],value['passed_count'],
        value['failed_count'],value['unknown_count'],value['assessed_count'],value['unknown_prerequisite_count'],
        tuple(value['not_requested']),value['admission'],value['source_authenticated'],
        value['historical_acquisition_verified'],value['schema_version'])


def report_snapshot(report):
    ctx=report.context;p=report.policy
    return c.DiagnosticSnapshot(c.ContextSnapshot(ctx.namespace,ctx.entity.instrument_id,ctx.entity.session_id,
        ctx.availability.market_cutoff_ns,ctx.availability.knowledge_cutoff_ns,ctx.availability.evaluation_ns),
        c.PolicySnapshot(p.policy_id,p.mode,p.unknown_action),
        tuple(c.FindingSnapshot(f.check_id,f.subject_id,f.kind,f.content,f.status,f.severity,f.reasons,
            f.assessed,f.unknown_prerequisites,f.age_ns) for f in report.findings),
        report.requested_count,report.passed_count,report.failed_count,report.unknown_count,report.assessed_count,
        report.unknown_prerequisite_count,report.not_requested,report.admission,report.source_authenticated,
        report.historical_acquisition_verified,report.schema_version)


def requests(index):
    ctx=d.DecisionContext('demo',EntityKey('A','S'),AvailabilitySpec(100,100,120))
    policy=d.DiagnosticPolicy('case-policy','strict','deny')
    n,fact_count=COUNTS[index]
    if not fact_count:checks=tuple(d.KnowledgeCheck('k'+str(i),'s'+str(i),100) for i in range(n))
    else:
        ref=d.ReferenceDeclaration('demo',EntityKey('A','S'),'universe_membership',
            SourceBinding('synthetic','snapshot1','map1','reference1'),128,True)
        facts=tuple(ReferenceFact(i,'r'+str(i),'universe_membership',200,None,90,text='U') for i in range(128))
        checks=tuple(d.MembershipCheck('c'+str(i),'s'+str(i),'universe_membership','U',100,ref,facts,'historical') for i in range(4))
    return ctx,policy,checks


def ratio(value):return {'numerator':value.numerator,'denominator':value.denominator}


def statistics(raw):
    require(type(raw) is list and len(raw)==10)
    for value in raw:integer(value,0,2**63-1)
    ordered=sorted(raw)
    return {'raw_ns':list(raw),'min_ns':ordered[0],'median_ns':ratio(Fraction(ordered[4]+ordered[5],2)),'max_ns':ordered[-1]}


def fraction(value):
    shape(value,('numerator','denominator'))
    require(type(value['numerator']) is int and type(value['denominator']) is int and value['denominator']>0)
    require(math.gcd(value['numerator'],value['denominator'])==1)
    return Fraction(value['numerator'],value['denominator'])


def comparison(baseline,wrapper):
    b=fraction(baseline['median_ns']);w=fraction(wrapper['median_ns'])
    return ratio(w-b),None if b==0 else ratio(w/b)


def timed(call,timer=time.perf_counter_ns):
    # Validate raw reads after the second read but before subtraction. Validation,
    # snapshot mapping and parity assertions are outside the timed interval.
    start=timer();value=call();stop=timer()
    valid=type(start) is int and type(stop) is int and -2**63<=start<=2**63-1 and -2**63<=stop<=2**63-1
    require(valid,'invalid_measurement')
    elapsed=stop-start;require(0<=elapsed<=2**63-1,'invalid_measurement')
    return value,elapsed


def metadata():
    info=time.get_clock_info('perf_counter')
    return {'system':platform.system(),'release':platform.release(),'machine':platform.machine(),
        'python_implementation':platform.python_implementation(),'python_version':platform.python_version(),
        'cpu_count':os.cpu_count(),'backend':'pure_python','requested_threads':None,'timer':'perf_counter_ns',
        'timer_resolution_seconds':str(info.resolution),'timer_monotonic':info.monotonic}


def load_oracle():
    value=json.loads(ORACLE.read_text(encoding='utf-8'))
    require(value['schema']=='eq105-measurement-oracle:1' and len(value['workloads'])==4)
    for i,v in enumerate(value['workloads']):
        require(v['id']==IDS[i] and (v['checks'],v['facts'])==COUNTS[i])
        exact(normalized(assertion(v['expected_snapshot'])),v['expected_snapshot'])
    return value


def _measure(oracle,timer):
    result={'schema':'r10-measurement:1','status':'completed','metadata':metadata(),'warmup_pairs':3,
        'sample_pairs':10,'pair_order':'baseline_then_wrapper','workloads':[]}
    for i,case in enumerate(oracle['workloads']):
        ctx,policy,checks=requests(i);expected=assertion(case['expected_snapshot'])
        original=(asdict(ctx),asdict(policy),tuple(asdict(v) for v in checks),asdict(expected))
        raw_b=[];raw_w=[]
        for pair in range(13):
            if pair<3:
                baseline=d.evaluate_diagnostics(ctx,policy,checks)
                wrapper=c.check_diagnostics(case['id'],ctx,policy,checks,expected)
            else:
                baseline,b=timed(lambda:d.evaluate_diagnostics(ctx,policy,checks),timer)
                wrapper,w=timed(lambda:c.check_diagnostics(case['id'],ctx,policy,checks,expected),timer)
                raw_b.append(b);raw_w.append(w)
            observed=normalized(report_snapshot(baseline));wrapped=normalized(wrapper.observed)
            try:
                exact(observed,case['expected_snapshot']);exact(wrapped,case['expected_snapshot'])
                exact(normalized(wrapper.expected),case['expected_snapshot'])
                require(wrapper.matched is True and wrapper.remaining_unknown is False)
                require(original==(asdict(ctx),asdict(policy),tuple(asdict(v) for v in checks),asdict(expected)))
            except MeasurementError:raise MeasurementError('parity_failed') from None
        b=statistics(raw_b);w=statistics(raw_w);extra,relative=comparison(b,w)
        result['workloads'].append({'id':case['id'],'checks':case['checks'],'facts':case['facts'],
            'baseline':b,'wrapper':w,'extra_median_ns':extra,'median_ratio':relative,
            'expected_snapshot':case['expected_snapshot'],'baseline_snapshot':observed,'wrapper_snapshot':wrapped,'parity':True})
    validate(result,oracle)
    return result


def measure(oracle=None,*,_timer=time.perf_counter_ns):
    """Private test clock injection is never exposed as a CLI/library option."""
    try:return _measure(load_oracle() if oracle is None else oracle,_timer)
    except MeasurementError as exc:code=exc.code
    except Exception:code='invalid_schema'
    raise MeasurementError(code)


def _validate(value,oracle):
    shape(value,('schema','status','metadata','warmup_pairs','sample_pairs','pair_order','workloads'))
    for key,expected in [('schema','r10-measurement:1'),('status','completed'),('warmup_pairs',3),('sample_pairs',10),('pair_order','baseline_then_wrapper')]:exact(value[key],expected)
    m=value['metadata'];shape(m,('system','release','machine','python_implementation','python_version','cpu_count','backend','requested_threads','timer','timer_resolution_seconds','timer_monotonic'))
    for key in ('system','release','machine','python_implementation','python_version','backend','timer','timer_resolution_seconds'):
        s=m[key];require(type(s) is str and bool(s) and len(s.encode('utf-8'))<=512 and not any(ord(ch)<32 or 127<=ord(ch)<=159 for ch in s))
    exact(m['backend'],'pure_python');exact(m['timer'],'perf_counter_ns');exact(m['requested_threads'],None);exact(m['timer_monotonic'],True)
    if m['cpu_count'] is not None:integer(m['cpu_count'],1,2**63-1)
    try:resolution=Decimal(m['timer_resolution_seconds']);require(resolution.is_finite() and resolution>0)
    except InvalidOperation:raise MeasurementError() from None
    require(type(value['workloads']) is list and len(value['workloads'])==4)
    for i,w in enumerate(value['workloads']):
        shape(w,('id','checks','facts','baseline','wrapper','extra_median_ns','median_ratio','expected_snapshot','baseline_snapshot','wrapper_snapshot','parity'))
        exact(w['id'],IDS[i]);exact(w['checks'],COUNTS[i][0]);exact(w['facts'],COUNTS[i][1]);exact(w['parity'],True)
        for key in ('baseline','wrapper'):
            shape(w[key],('raw_ns','min_ns','median_ns','max_ns'))
            require(fraction(w[key]['median_ns'])>=0)
            exact(w[key],statistics(w[key]['raw_ns']))
        extra,relative=comparison(w['baseline'],w['wrapper']);fraction(w['extra_median_ns'])
        if w['median_ratio'] is not None:require(fraction(w['median_ratio'])>=0)
        exact(w['extra_median_ns'],extra);exact(w['median_ratio'],relative)
        for key in ('expected_snapshot','baseline_snapshot','wrapper_snapshot'):exact(w[key],oracle['workloads'][i]['expected_snapshot'])


def validate(value,oracle=None):
    try:return _validate(value,load_oracle() if oracle is None else oracle)
    except MeasurementError as exc:code=exc.code
    except Exception:code='invalid_schema'
    raise MeasurementError(code)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True);args=parser.parse_args()
    require(not args.out.exists())
    result=measure();args.out.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    print('R10 measured four workloads:104 parity-checked calls,80 timed calls; fixed order, no performance threshold.')


if __name__=='__main__':
    try:main()
    except MeasurementError as exc:raise SystemExit('Measurement rejected: '+exc.code) from None
