"""One fixed-head EQ117 study per OS; no adaptive trials or successful-run selection.

Run only after source/instrumentation/installed qualification approval. This is
trusted local orchestration, not a process sandbox or hard cleanup guarantee.
"""
from __future__ import annotations
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import platform
import queue
import stat
import subprocess
import sys
import threading
import time
from typing import Any

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
LIMIT = 65536
REQUIRED_SOURCE = {'run_evidence_evaluation.py','evidence_evaluation_observer.py',
 'evidence_evaluation_producer.py','evidence_evaluation_instrumentation.py',
 'evidence_evaluation_worker.py','evidence_evaluation_scoring.py',
 'evidence_pilot.py','agent_research.py','EQ116_ORACLES.json'}
ACTIVE_ACTORS: list[Any] = []
PARTIAL_STATE: dict[str,Any] = {}


def encoded(value: Any) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False)+'\n').encode('ascii')


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def load(name: str) -> Any:
    spec = importlib.util.spec_from_file_location(name, HERE/(name+'.py'))
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec);sys.modules[name]=value;spec.loader.exec_module(value)
    return value


def retain_calculator_observation(row: dict[str,Any], trace: dict[str,Any]) -> None:
    """Known captured entries survive even when diagnosis/replay output failed."""
    count=trace['counts']['calculator_call']
    assert type(count)is int and count>=0
    row['calculator_calls']=count


class Actor:
    def __init__(self, arm: str, logs: Path, name: str, prefix: str) -> None:
        self.logs, self.name = logs, name
        self.queue: queue.Queue[bytes | None] = queue.Queue(maxsize=1)
        self.stderr = bytearray()
        self.overflow = False
        self.rows: list[dict[str, Any]] = []
        self.closed_result: bool | None = None
        env = dict(os.environ)
        for key in ('PYTHONPATH', 'PYTHONHOME', 'MYPYPATH'):env.pop(key, None)
        self.started = time.perf_counter_ns()
        self.process = subprocess.Popen([sys.executable, '-I', str(HERE/'evidence_evaluation_worker.py'), 'serve', arm],
            cwd=logs.parent, env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
            creationflags=subprocess.CREATE_NO_WINDOW if os.name == 'nt' else 0)
        def stdout() -> None:
            assert self.process.stdout is not None
            try:
                while True:
                    raw = self.process.stdout.readline(LIMIT+1)
                    if len(raw)>LIMIT:self.overflow=True
                    try:self.queue.put(raw[:LIMIT] if raw else None, timeout=2)
                    except queue.Full:self.overflow=True;return
                    if not raw:return
            finally:
                self.process.stdout.close()
        def stderr() -> None:
            assert self.process.stderr is not None
            try:
                while True:
                    raw=self.process.stderr.read(4096)
                    if not raw:break
                    room=LIMIT-len(self.stderr)
                    self.stderr.extend(raw[:max(0,room)])
                    if len(raw)>room:self.overflow=True
            finally:self.process.stderr.close()
        self.readers=[threading.Thread(target=stdout,daemon=True),threading.Thread(target=stderr,daemon=True)]
        try:
            for reader in self.readers:reader.start()
            hello_raw=self.receive();self.imported=time.perf_counter_ns()
            with (logs/(name+'.hello')).open('xb') as output:output.write(hello_raw)
            hello=json.loads(hello_raw)
            assert hello==dict(schema='eq117.worker.hello.v1',arm=arm,prefix=prefix,
                              executable=sys.executable,python=platform.python_version(),imports_completed=True)
        except BaseException:
            self.close()
            raise

    def receive(self) -> bytes:
        raw=self.queue.get(timeout=60)
        if raw is None or self.overflow or not raw.endswith(b'\n'):
            raise RuntimeError('worker_protocol')
        return raw

    def ask(self, seed: Path, root: Path, trial_id: str) -> bytes:
        assert self.process.stdin is not None and self.process.poll() is None
        raw=encoded(dict(seed=str(seed),root=str(root),trial_id=trial_id));assert len(raw)<=8192
        self.process.stdin.write(raw);self.process.stdin.flush()
        return self.receive()

    def close(self) -> bool:
        """Actual waits/EOF/reader joins are observed; unknown cleanup invalidates."""
        if self.closed_result is not None:return self.closed_result
        clean=True
        try:
            if self.process.stdin is not None and not self.process.stdin.closed:self.process.stdin.close()
        except BaseException:clean=False
        try:self.process.wait(timeout=60)
        except subprocess.TimeoutExpired:
            clean=False
            # Best effort on the owned launcher; no descendant-kill claim.
            try:self.process.terminate()
            except BaseException:pass
            try:self.process.wait(timeout=10)
            except BaseException:pass
        except BaseException:
            clean=False
            try:self.process.terminate()
            except BaseException:pass
            try:self.process.wait(timeout=10)
            except BaseException:pass
        for reader in self.readers:
            try:
                if reader.ident is not None:reader.join(timeout=10)
            except BaseException:clean=False
        clean=clean and all(not reader.is_alive() for reader in self.readers) and not self.overflow
        if all(not reader.is_alive() for reader in self.readers):
            for pipe in (self.process.stdout,self.process.stderr):
                try:
                    if pipe is not None and not pipe.closed:pipe.close()
                except BaseException:clean=False
        stderr=bytes(self.stderr)
        try:
            with (self.logs/(self.name+'.stderr')).open('xb') as output:output.write(stderr)
        except BaseException:clean=False
        try:actual_exit=self.process.poll()
        except BaseException:actual_exit=None;clean=False
        for row in self.rows:
            row['return_code']=actual_exit
            row['stderr_sha256']=sha(stderr)
            if not clean or actual_exit!=0 or stderr:
                row['status']='failed';row['error_code']='cleanup_unknown' if not clean else 'worker_error'
        self.closed_result=clean and actual_exit==0 and not stderr
        return self.closed_result


def main() -> int:
    assert len(sys.argv)==3
    root=Path(sys.argv[1]).resolve();context_path=Path(sys.argv[2]).resolve()
    assert not root.exists() and context_path.is_file()
    context_raw=context_path.read_bytes();assert len(context_raw)<=65536
    context=json.loads(context_raw)
    assert context['study_id'].isascii() and 0<len(context['study_id'])<=128
    assert context['system']==platform.system() in ('Windows','Linux') and context['prefix']==sys.prefix
    assert context['python']==platform.python_version()
    assert os.environ.get('GITHUB_RUN_ATTEMPT','1')=='1'
    def closure() -> None:
        assert type(context['source_map']) is dict and set(context['source_map'])==REQUIRED_SOURCE
        for name,h in context['source_map'].items():
            assert Path(name).name==name and type(h)is str and len(h)==64 and sha((HERE/name).read_bytes())==h
    closure()
    scorer=load('evidence_evaluation_scoring')
    assert context['proposal_sha256']==scorer.PROPOSAL_SHA256 and context['owner_accepted'] is True
    oracle=scorer.load_oracle((HERE/'EQ116_ORACLES.json').read_bytes())
    # This producer has controlled expected data; the worker observer does not.
    producer=load('evidence_evaluation_producer')
    root.mkdir();logs=root/'logs';logs.mkdir();seeds=root/'producer-seeds';seeds.mkdir();arms=root/'arms';arms.mkdir()
    with (root/'context.json').open('xb') as output:output.write(context_raw)
    rows=[];warm={};pair=None;seed=None;common=None;input_hash=None;stopped=False;actors=ACTIVE_ACTORS
    preparations=[]
    PARTIAL_STATE.update(root=root,rows=rows,preparations=preparations)
    script_hash=sha(encoded(context['source_map']));environment_id=sha(encoded(context['environment']))
    for slot in scorer.schedule():
        row=dict.fromkeys(scorer.RAW_FIELDS,None)
        row.update(slot,run_id=context['study_id'],proposal_sha256=scorer.PROPOSAL_SHA256,
            runner_source_map_sha256=script_hash,environment_id=environment_id,
            installed_map_sha256=context['installed_map_sha256'],os=platform.system(),python=platform.python_version(),
            status='not_run',error_code='not_run_after_failure')
        rows.append(row)
    # Retained full denominator before any actor starts; replaced after each slot.
    def checkpoint():
        (root/'observations.partial.jsonl').write_bytes(b''.join(encoded(row) for row in rows))
        (root/'preparations.partial.json').write_bytes(encoded(preparations))
    checkpoint()
    for number,row in enumerate(rows,1):
        slot={k:row[k] for k in ('case_id','arm','repetition','process_state','arm_position')}
        current=(slot['repetition'],slot['case_id'])
        if stopped:
            continue
        actor=None
        try:
            closure()
            if pair!=current:
                pair=current;seed=seeds/('%02d-%s'%current)
                preparation={}
                preparations.append(dict(repetition=slot['repetition'],case_id=slot['case_id'],audit=preparation))
                checkpoint()
                common=producer.prepare(seed,slot['case_id'],audit=preparation)
                input_hash=sha(encoded(common['seed_map']))
                with (seed/'preparation.json').open('xb') as output:output.write(encoded(common))
            assert seed is not None and common is not None and input_hash is not None
            row['input_map_sha256']=input_hash
            for suffix,key in (('_start_ns','start_ns'),('_end_ns','end_ns'),('_ns','duration_ns')):
                row['common_fixture_compute'+suffix]=common[key]
            if slot['process_state']=='PROCESS_WARM':
                if slot['arm'] not in warm:
                    warm[slot['arm']]=Actor(slot['arm'],logs,'warm-'+slot['arm'],sys.prefix);actors.append(warm[slot['arm']])
                actor=warm[slot['arm']]
            else:
                actor=Actor(slot['arm'],logs,'%03d-cold'%number,sys.prefix);actors.append(actor)
            actor.rows.append(row)
            row.update(launch_import_start_ns=actor.started,launch_import_end_ns=actor.imported,
                       launch_import_ns=actor.imported-actor.started)
            destination=arms/('%03d'%number)
            raw=actor.ask(seed,destination,'%03d'%number)
            with (logs/('%03d.stdout'%number)).open('xb') as output:output.write(raw)
            value=json.loads(raw)
            assert value['schema']=='eq117.worker.result.v1' and value['trial_id']=='%03d'%number
            assert value['status'] in ('valid','failed')
            row.update(status=value['status'],error_code=value['error_code'],diagnosis=value['diagnosis'],
                       operation_trace=value['operation_trace'],stdout_sha256=sha(raw),
                       transient_peak_bytes=value['transient_peak_bytes'])
            retain_calculator_observation(row,value['operation_trace'])
            sequence=value['operation_events']
            assert sequence is not None and sha(json.dumps(sequence,separators=(',',':')).encode('ascii'))==value['operation_trace']['sequence_sha256']
            counts=[0]*len(scorer.OPERATIONS);api_counts=dict.fromkeys(scorer.API_CATEGORIES,0)
            for category,api,count in sequence:
                assert type(category)is int and 0<=category<len(scorer.OPERATIONS) and type(api)is int and 0<=api<len(value['operation_trace']['api_name_order'])
                assert type(count)is int and count>0;counts[category]+=count
                api_name=value['operation_trace']['api_name_order'][api]
                assert scorer.API_CATEGORIES[api_name]==scorer.OPERATIONS[category];api_counts[api_name]+=count
            assert dict(zip(scorer.OPERATIONS,counts,strict=True))==value['operation_trace']['counts']
            assert api_counts==value['operation_trace']['api_calls']
            for stage in ('record','export','read_verify_replay'):
                start,end=(value['endpoints'][stage+suffix] for suffix in ('_start_ns','_end_ns'))
                row[stage+'_start_ns']=start;row[stage+'_end_ns']=end
                row[stage+'_ns']=None if start is None or end is None else end-start
            if value['diagnosis'] is not None:
                diagnosis=value['diagnosis']
                for target,source in (('anchor_status','anchor'),('retention','retention'),('model_identity','model_identity'),
                    ('narrative_status','narrative_status'),('replay_status','replay_status'),
                    ('declared_strict_admission','declared_strict_admission'),('recomputed_strict_admission','recomputed_strict_admission'),
                    ('recomputed_strict_reason','recomputed_strict_reason')):row[target]=diagnosis[source]
                assert row['calculator_calls']==row['operation_trace']['counts']['calculator_call']
                assert row['calculator_calls']==diagnosis['calculator_calls']
            files=value['closed_files']
            actual={p.name:dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in destination.iterdir()
                    if stat.S_ISREG(p.lstat().st_mode)}
            assert len(actual)==len(list(destination.iterdir())) and actual==files
            row['closed_file_bytes']=sum(x['bytes'] for x in files.values());row['file_count']=len(files)
            assert {p.name:dict(bytes=p.stat().st_size,sha256=sha(p.read_bytes())) for p in seed.iterdir() if p.name!='preparation.json'}==common['seed_map']
            if row['status']!='valid':stopped=True
        except BaseException:
            row['status']='failed';row['error_code']='protocol_error';stopped=True
        finally:
            if actor is not None and slot['process_state']=='PROCESS_COLD':
                if not actor.close():stopped=True
            checkpoint()
    for actor in warm.values():
        if not actor.close():stopped=True
    # Equal source/case input facts remain attached even if later slots never ran.
    for repetition in range(1,11):
        for case in scorer.CASES:
            pairrows=[x for x in rows if x['repetition']==repetition and x['case_id']==case]
            attempted=next((x for x in pairrows if x['input_map_sha256'] is not None),None)
            if attempted is not None:
                for row in pairrows:
                    if row['input_map_sha256'] is None:
                        row['input_map_sha256']=attempted['input_map_sha256']
                        for suffix in ('_start_ns','_end_ns','_ns'):row['common_fixture_compute'+suffix]=attempted['common_fixture_compute'+suffix]
    for row in rows:
        if len(encoded(row))>16384:
            # Full original diagnosis/trace remains in its bounded stdout file.
            row.update(status='failed',error_code='capture_limit',diagnosis=None,operation_trace=None)
            stopped=True
        assert len(encoded(row))<=16384
    raw=b''.join(encoded(row) for row in rows)
    captured=len(raw)+len(context_raw)+sum(p.stat().st_size for p in logs.iterdir())
    # Half of the accepted aggregate64MiB capture budget per OS.
    with (root/'observations.jsonl').open('xb') as output:output.write(raw)
    assert captured<=33554432
    summary=scorer.score(rows,oracle,(platform.system(),))
    summary.update(study_id=context['study_id'],source_head=context['source_head'],proposal_sha256=scorer.PROPOSAL_SHA256,
        source_map_sha256=script_hash,context_sha256=sha(context_raw),raw_observations_sha256=sha(raw),
        raw_observation_and_log_bytes=captured,stopped_after_error=stopped,
        shared_preparations=sum(x['audit'].get('completed') is True for x in preparations),
        shared_initial_calculator_calls=sum(x['audit'].get('calculator_entries',0) for x in preparations),
        shared_calculator_returns=sum(x['audit'].get('calculator_returns',0) for x in preparations),
        shared_calculator_errors=sum(x['audit'].get('calculator_errors',0) for x in preparations),
        shared_preparation_states=preparations,
        actor_closure=[dict(name=a.name,actual_return_code=a.process.poll(),readers_joined=all(not t.is_alive() for t in a.readers),stderr_overflow=a.overflow) for a in actors],
        launch_import_scope='parent-clock actual process start to HELLO; warm session duration is a shared reference in its40rows, not40launches')
    with (root/'summary.json').open('xb') as output:output.write(encoded(summary))
    closure()
    return 2 if stopped else 0


if __name__=='__main__':
    try:
        try:code=main()
        finally:
            # Covers checkpoint, scorer, capture-limit and final-source failures too.
            for actor in ACTIVE_ACTORS:actor.close()
            if PARTIAL_STATE:
                (PARTIAL_STATE['root']/'observations.partial.jsonl').write_bytes(
                    b''.join(encoded(row) for row in PARTIAL_STATE['rows']))
                (PARTIAL_STATE['root']/'preparations.partial.json').write_bytes(encoded(PARTIAL_STATE['preparations']))
    except BaseException:
        # Preserve partial denominator and logs even if scoring or final closure fails.
        if len(sys.argv)==3:
            target=Path(sys.argv[1])
            if target.is_dir():
                marker=target/'FAILED.json'
                if not marker.exists():marker.write_bytes(encoded(dict(status='failed',complete=False,reason='controller_failure')))
        raise
    raise SystemExit(code)
