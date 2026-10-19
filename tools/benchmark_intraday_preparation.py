"""Frozen EQ137 supplied-data baseline versus shared preparation; no worker claim."""
from __future__ import annotations
import argparse
import ctypes
import hashlib
import json
import math
import os
from pathlib import Path
import platform
import statistics
import subprocess
import sys
import time
from fractions import Fraction

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, Coverage,
    DataKind, InputScope, IntervalCoverage, PriceUnit, SessionSpec, SourceBinding,
)
from equity_features_intraday import IntradayContext, IntradayRun, build_intraday_config, prepare_intraday
from equity_features_intraday._prepare import validate_preparation

ROOT=Path(__file__).resolve().parents[1]
FAMILIES=('anchored_closes','true_ranges','price_moments','high_extrema','low_extrema','simple_returns')
CASES={
    'small':(1,256,20), 'large':(64,4096,20), 'skewed':(64,256,20),
    'long14':(1,4096,14), 'long20':(1,4096,20), 'long60':(1,4096,60),
}
GENERATOR='positive-scaled-integer-quadratic-v1'



def source_identity():
    import equity_feature_contracts
    import equity_features_intraday
    from importlib.metadata import version
    scopes=('packages/contracts','packages/intraday','tools/benchmark_intraday_preparation.py')
    paths=subprocess.check_output(['git','ls-files','--',*scopes],cwd=ROOT,encoding='utf-8').splitlines()
    assert paths and not subprocess.check_output(['git','status','--porcelain','--untracked-files=all','--',*scopes],cwd=ROOT)
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    sources={}
    for name in paths:
        body=(ROOT/name).read_bytes()
        git_body=subprocess.check_output(['git','show',head+':'+name],cwd=ROOT)
        assert body.replace(b'\r\n',b'\n')==git_body,('source differs from Git',name)
        sources[name]={'git_sha256':hashlib.sha256(git_body).hexdigest(),'materialized_sha256':hashlib.sha256(body).hexdigest()}
    origins={}
    for module,distribution,package in ((equity_feature_contracts,'equity-feature-contracts','contracts'),
                                       (equity_features_intraday,'equity-features-intraday','intraday')):
        expected=(ROOT/'packages'/package/'src'/module.__name__/'__init__.py').resolve()
        origin=Path(module.__file__).resolve()
        assert origin==expected,('unexpected benchmark import origin',module.__name__)
        root=origin.parent
        actual={p.relative_to(ROOT).as_posix() for p in root.rglob('*') if p.is_file() and '__pycache__' not in p.parts}
        wanted={name for name in paths if name.startswith(root.relative_to(ROOT).as_posix()+'/')}
        assert actual==wanted,('untracked/missing runtime module',module.__name__)
        origins[module.__name__]={'origin':origin.relative_to(ROOT).as_posix(),'version':version(distribution)}
    assert origins['equity_feature_contracts']['version']=='0.0.4a4'
    assert origins['equity_features_intraday']['version']=='0.1.0a1'
    return {'head':head,'source':sources,'libraries':origins,'runtime':'pinned source development environment; artifact installs qualified separately'}


def capacity():
    result={'os':platform.platform(),'python':platform.python_version(),
            'logical_cpus':os.cpu_count(),'processor':platform.processor(),
            'native_threads_per_worker':1,'workers':1,
            'limits':'One pure Python process. Affinity is permitted capacity, not CPU reservation; memory uses OS peak working set/RSS, not physical enforcement.'}
    if os.name=='nt':
        class Memory(ctypes.Structure):
            _fields_=[('length',ctypes.c_ulong),('load',ctypes.c_ulong)]+[(n,ctypes.c_ulonglong) for n in ('total','available','total_page','available_page','total_virtual','available_virtual','extended')]
        memory=Memory();memory.length=ctypes.sizeof(memory)
        assert ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(memory))
        result.update(total_memory_bytes=memory.total,available_memory_bytes=memory.available)
        kernel=ctypes.windll.kernel32
        kernel.GetCurrentProcess.restype=ctypes.c_void_p
        process=kernel.GetCurrentProcess()
        proc_mask=ctypes.c_size_t();system_mask=ctypes.c_size_t()
        assert kernel.GetProcessAffinityMask(ctypes.c_void_p(process),ctypes.byref(proc_mask),ctypes.byref(system_mask))
        result['affinity_mask']=int(proc_mask.value)
        result['affinity_logical_cpus']=int(proc_mask.value).bit_count()
        result['affinity_limit']='Windows current process group mask; multi-group scheduling is not measured.'
        command='Get-CimInstance Win32_Processor | Select-Object Name,NumberOfCores,NumberOfLogicalProcessors | ConvertTo-Json -Compress'
        result['cpu_inventory']=json.loads(subprocess.check_output(['powershell','-NoProfile','-Command',command],encoding='utf-8'))
        result['physical_cores']=sum(cpu['NumberOfCores'] for cpu in (result['cpu_inventory'] if isinstance(result['cpu_inventory'],list) else [result['cpu_inventory']]))
    else:
        result['affinity_logical_cpus']=len(os.sched_getaffinity(0))
        result['affinity']=sorted(os.sched_getaffinity(0))
        memory={key:int(value.split()[0])*1024 for key,value in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines()) if key in ('MemTotal','MemAvailable')}
        result.update(total_memory_bytes=memory['MemTotal'],available_memory_bytes=memory['MemAvailable'])
        result['physical_cores']=None
        result['physical_core_limit']='Physical topology not collected on this OS; no topology scaling claim.'
    result['memory_budget_bytes']=min(1024**3,result['available_memory_bytes']//4)
    return result


def peak_memory():
    if os.name=='nt':
        class Counters(ctypes.Structure):
            _fields_=[('cb',ctypes.c_ulong),('page_faults',ctypes.c_ulong)]+[(n,ctypes.c_size_t) for n in ('peak_working_set','working_set','peak_paged_pool','paged_pool','peak_nonpaged_pool','nonpaged_pool','pagefile','peak_pagefile')]
        counters=Counters();counters.cb=ctypes.sizeof(counters)
        kernel=ctypes.windll.kernel32;kernel.GetCurrentProcess.restype=ctypes.c_void_p
        assert ctypes.windll.psapi.GetProcessMemoryInfo(ctypes.c_void_p(kernel.GetCurrentProcess()),ctypes.byref(counters),counters.cb)
        return int(counters.peak_working_set)
    import resource
    return resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024


def inputs(case):
    symbols,slots,period=CASES[case]
    result=[]
    for symbol in range(symbols):
        n=4096 if case=='skewed' and symbol==symbols-1 else slots
        instrument=f'SYN{symbol:03}'
        context=IntradayContext(instrument,'synthetic-calendar','ten-ns-grid','revision1',
            (SessionSpec('synthetic','S',0,n*10,'UTC'),),(IntradayRun('S',0,10,n),),0,n-1,'reset')
        config=build_intraday_config(context,period=period,band_k=Fraction(2),
            availability=AvailabilitySpec(n*10,n*10,n*10),adjustment=AdjustmentSpec(),price_unit=PriceUnit(4,'USD'),evidence_limit=16)
        closes=tuple(1000000+(symbol*17+i*13+i*i)%101 for i in range(n))
        batch=CanonicalBatch(DataKind.BAR,(
            Column('instrument_id',(instrument,)*n),Column('session_id',('S',)*n),
            Column('start_ns',tuple(i*10 for i in range(n))),Column('end_ns',tuple((i+1)*10 for i in range(n))),
            Column('known_at_ns',tuple((i+1)*10 for i in range(n))),Column('close',closes),
            Column('high',tuple(c+5 for c in closes)),Column('low',tuple(c-5 for c in closes))),
            BatchMetadata('synthetic',SourceBinding('synthetic',f'snap{symbol}','map1',f'input{symbol}'),Coverage(n,n,True),
                PriceUnit(4,'USD'),scope=InputScope(0,n*10,'synthetic-v1'),
                interval_coverage=tuple(IntervalCoverage(f'slot:{i}',i*10,(i+1)*10,Coverage(1,1,True)) for i in range(n))))
        result.append(((batch,),context,config))
    return result


def projection(preparation,family):
    return (preparation.context_digest,preparation.config_digest,preparation.input_bindings,preparation.operand(family))


def execute(supplied,mode):
    digest=hashlib.sha256()
    for batches,context,config in supplied:
        shared=prepare_intraday(batches,context,config,requirements=FAMILIES) if mode=='shared' else None
        for family in FAMILIES:
            preparation=shared if shared is not None else prepare_intraday(batches,context,config,requirements=(family,))
            # Include actual compatible-reuse checks and full projection inspection.
            validate_preparation(preparation,batches,context,config,(family,))
            digest.update(repr(projection(preparation,family)).encode('ascii'))
    return digest.hexdigest()


def verify_quality_parity():
    # Independent tiny arithmetic is in producer tests. This gate checks complete
    # P projection for absent H/L, governed gaps, correction and zero variance.
    supplied=inputs('small')
    batches,context,config=supplied[0]
    variants=[batches]
    variants.append((CanonicalBatch(DataKind.BAR,tuple(c for c in batches[0].columns if c.name not in ('high','low')),batches[0].metadata),))
    from dataclasses import replace
    batch=batches[0]
    variants.append((replace(batch,columns=tuple(Column(c.name,tuple(v for i,v in enumerate(c.values) if i!=0)) for c in batch.columns),
        metadata=replace(batch.metadata,coverage=Coverage(256,255,False),interval_coverage=(replace(batch.metadata.interval_coverage[0],coverage=Coverage(1,0,False)),)+batch.metadata.interval_coverage[1:])),))
    variants.append((replace(batch,columns=tuple(Column(c.name,(1000000,)*256) if c.name=='close' else Column(c.name,(1000005,)*256) if c.name=='high' else Column(c.name,(999995,)*256) if c.name=='low' else c for c in batch.columns)),))
    revised=replace(batch,columns=tuple(Column(c.name,c.values[:-1]+(c.values[-1]+1,)) if c.name=='close' else c for c in batch.columns),
        metadata=replace(batch.metadata,source=replace(batch.metadata.source,snapshot_id='corrected')))
    variants.append((revised,))
    for index,variant in enumerate(variants):
        view_context=context if index<4 else replace(context,revision='revision2')
        view_config=config if index<4 else build_intraday_config(view_context,period=20,band_k=Fraction(2),availability=config.availability,adjustment=config.adjustment,price_unit=config.price_unit,evidence_limit=16)
        shared=prepare_intraday(variant,view_context,view_config,requirements=FAMILIES)
        for family in FAMILIES:
            single=prepare_intraday(variant,view_context,view_config,requirements=(family,))
            assert projection(single,family)==projection(shared,family)
    return {'full_projection_cases':len(variants),'families_each':len(FAMILIES),'passed':True,
            'limits':'Preparation parity only; no FeatureResult or worker equivalence claim.'}


def measure(case,mode):
    identity=source_identity()
    results=[]
    for repeat in range(9):
        try:
            cpu=time.process_time();start=time.perf_counter()
            construction_start=time.perf_counter();supplied=inputs(case)
            construction=time.perf_counter()-construction_start
            calculation_start=time.perf_counter();digest=execute(supplied,mode)
            calculation=time.perf_counter()-calculation_start
            elapsed=time.perf_counter()-start;core=time.process_time()-cpu
            sample={'wall_seconds':elapsed,'construction_seconds':construction,'admission_preparation_identity_inspection_seconds':calculation,
                    'core_seconds':core,'peak_process_bytes':peak_memory(),'projection_sha256':digest}
            del supplied
            if repeat>=2:results.append(sample)
        except BaseException as error:
            return {'case':case,'mode':mode,'samples':results,'status':'failed',
                    'failed_repeat':repeat,'failure_type':type(error).__name__,'source_identity':identity}
    try:
        assert len({r['projection_sha256'] for r in results})==1
        assert source_identity()==identity,'benchmark source changed during measurement'
    except BaseException as error:
        return {'case':case,'mode':mode,'samples':results,'status':'failed',
                'failed_phase':'post-measurement closure','failure_type':type(error).__name__,'source_identity':identity}
    return {'case':case,'mode':mode,'samples':results,'warmups':2,'source_identity':identity,'status':'completed',
        'stages':'Construct immutable supplied inputs, admission/preparation, actual reuse identity checks and full projection inspection. No worker/startup/IPC/queue or external source/sink.',
        'queue_bytes':0,'ipc_bytes':0,'worker_children':0,'native_compute_threads':0}


def summary(measurement):
    samples=measurement['samples'];walls=[s['wall_seconds'] for s in samples]
    quartiles=statistics.quantiles(walls,n=4,method='inclusive')
    return {'median_seconds':statistics.median(walls),'iqr_seconds':quartiles[2]-quartiles[0],
        'p95_seconds':sorted(walls)[math.ceil(.95*len(walls))-1],
        'median_core_seconds':statistics.median(s['core_seconds'] for s in samples),
        'peak_process_bytes':max(s['peak_process_bytes'] for s in samples)}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',type=Path)
    parser.add_argument('--child',choices=CASES);parser.add_argument('--mode',choices=('separate','shared'))
    args=parser.parse_args()
    if args.child:
        print(json.dumps(measure(args.child,args.mode),sort_keys=True));return
    assert args.output is not None,'explicit output path required'
    baseline_path=args.output.with_suffix('.baseline.json')
    assert args.output.resolve()!=baseline_path.resolve(),'distinct output paths required'
    assert not args.output.exists() and not baseline_path.exists(),'preserve earlier benchmark evidence'
    head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()
    assert not subprocess.check_output(['git','status','--porcelain','--',str(Path(__file__).relative_to(ROOT)),'packages/intraday','tools/benchmark_intraday_preparation.py'],cwd=ROOT)
    identity=source_identity()
    report={'schema':'equity-features.eq137-preparation-benchmark.v1','source_commit':head,
        'source_identity':identity,'generator':GENERATOR,'cases':CASES,'capacity':capacity(),'quality_parity':verify_quality_parity(),
        'rule':'A first. B median improvement >=max(5%,3*IQR(A)/median(A)); full P parity; peakRSS<=min(1GiB,25%initial free) and<=1.25A; median coreseconds<=1.25A; small latency p95<=1.10A.',
        'baseline':{},'thresholds':{},'candidate':{},'decisions':{},'status':'running'}
    def save():args.output.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n',encoding='utf-8')
    def child(case,mode):
        started=time.perf_counter()
        process=subprocess.run([sys.executable,'-I','-B',__file__,'--child',case,'--mode',mode],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
        if process.returncode:
            report['failure']={'case':case,'mode':mode,'child_exit':process.returncode,'stderr_sha256':hashlib.sha256(process.stderr).hexdigest()}
            save();raise RuntimeError('child rejected benchmark')
        value=json.loads(process.stdout)
        if value.get('status')!='completed':
            report['failure']=value;save();raise RuntimeError('child benchmark failed')
        value['subprocess_total_seconds']=time.perf_counter()-started
        value['parent_peak_bytes']=peak_memory()
        value['aggregate_peak_bound_bytes']=value['parent_peak_bytes']+max(s['peak_process_bytes'] for s in value['samples'])
        assert value['source_identity']==identity and source_identity()==identity,'parent/child source binding differs'
        value['summary']=summary(value)
        return value
    with args.output.open('x',encoding='utf-8') as initial:
        json.dump(report,initial,sort_keys=True,indent=2)
    try:
        # Freeze all baselines and margins before observing any candidate timing.
        for case in CASES:
            value=child(case,'separate');report['baseline'][case]=value
            report['thresholds'][case]=max(.05,3*value['summary']['iqr_seconds']/value['summary']['median_seconds']);save()
        baseline_bytes=args.output.read_bytes()
        report['frozen_baseline_sha256']=hashlib.sha256(baseline_bytes).hexdigest()
        with baseline_path.open('xb') as frozen:
            frozen.write(baseline_bytes)
        save()
        for case in CASES:
            value=child(case,'shared');report['candidate'][case]=value
            a=report['baseline'][case];b=value;sa=a['summary'];sb=b['summary']
            parity=a['samples'][0]['projection_sha256']==b['samples'][0]['projection_sha256']
            improvement=1-sb['median_seconds']/sa['median_seconds']
            conditions={'full_projection_parity':parity,'improvement':improvement>=report['thresholds'][case],
                'absolute_memory_budget':b['aggregate_peak_bound_bytes']<=report['capacity']['memory_budget_bytes'],
                'relative_memory':b['aggregate_peak_bound_bytes']<=1.25*a['aggregate_peak_bound_bytes'],
                'core_seconds':sb['median_core_seconds']<=1.25*sa['median_core_seconds'],
                'small_latency':case!='small' or sb['p95_seconds']<=1.10*sa['p95_seconds']}
            report['decisions'][case]={'conditions':conditions,'observed_median_improvement':improvement,
                'adopt_shared_for_case':all(conditions.values()),'fallback':'separate calls remain supported'};save()
            assert parity,'full P parity failed; no adoption'
        assert subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip()==head
    except BaseException as error:
        report['status']='failed';report['failure_type']=type(error).__name__;save()
        raise
    report['status']='completed';save()


if __name__=='__main__':main()
