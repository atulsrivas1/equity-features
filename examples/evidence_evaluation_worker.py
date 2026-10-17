"""Fixed EQ117 worker protocol. Import helpers by exact sibling paths under -I."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path
import platform
import sys
import time
from typing import Any, Callable

sys.dont_write_bytecode = True


def module(name: str) -> Any:
    path = Path(__file__).with_name(name + '.py')
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec is not None and spec.loader is not None
    value = importlib.util.module_from_spec(spec)
    sys.modules[name] = value
    spec.loader.exec_module(value)
    return value


observer = module('evidence_evaluation_observer')
producer = module('evidence_evaluation_producer')
instrumentation = module('evidence_evaluation_instrumentation')
# Both cold and warm actors import the same fixed helpers once before HELLO.
producer.pilot_module()


def trial(seed: Path, root: Path, arm: str, trial_id: str, *, clock: Callable[[], int] = time.perf_counter_ns,
          actual_cli_invocations: int = 1) -> dict[str, Any]:
    trace = instrumentation.OperationTrace()
    endpoints: dict[str, int | None] = {}
    diagnosis: dict[str, Any] | None = None
    status, error = 'valid', None
    trace.start()
    try:
        for name, action in (
            ('record', lambda: producer.record(seed, root, arm, trial_id)),
            ('export', lambda: producer.export(root, arm)),
            ('read_verify_replay', lambda: observer.observe(root, arm))):
            endpoints[name + '_start_ns'] = clock()
            try:
                result = action()
                if name == 'read_verify_replay':
                    diagnosis = result
            finally:
                endpoints[name + '_end_ns'] = clock()
    except BaseException:
        # Preserve the owned root and raw partial observations; never retry.
        status, error = 'failed', 'observation_error'
    finally:
        trace.stop()
    summary = trace.summary()
    summary['cli_invocations'] = actual_cli_invocations
    if diagnosis is not None and diagnosis['calculator_calls'] != summary['counts']['calculator_call']:
        status, error = 'failed', 'calculator_count_mismatch'
    for name in ('record', 'export', 'read_verify_replay'):
        endpoints.setdefault(name + '_start_ns', None)
        endpoints.setdefault(name + '_end_ns', None)
    files = {}
    if root.exists():
        for path in root.iterdir():
            if not path.is_file() or path.is_symlink():
                status, error = 'failed', 'invalid_file'
                continue
            raw = path.read_bytes()
            files[path.name] = dict(bytes=len(raw), sha256=observer.digest(raw))
    out = dict(schema='eq117.worker.result.v1', trial_id=trial_id, status=status, error_code=error,
        diagnosis=diagnosis, endpoints=endpoints, operation_trace=summary,
        operation_events=trace.sequence, closed_files=files,
        transient_peak_bytes=None, transient_peak_reason='not_safely_observed')
    raw = observer.encoded(out)
    if len(raw) > 65536:
        # This is a failed logical capture, never a complete operation trace claim.
        out = dict(schema='eq117.worker.result.v1', trial_id=trial_id, status='failed',
            error_code='capture_limit', diagnosis=None, endpoints=endpoints,
            operation_trace=summary, operation_events=None, closed_files=files,
            transient_peak_bytes=None, transient_peak_reason='not_safely_observed')
        raw = observer.encoded(out)
    if len(raw) > 65536:
        raise ValueError('capture_limit')
    sys.stdout.buffer.write(raw)
    sys.stdout.buffer.flush()
    return out


def main() -> int:
    if len(sys.argv) != 3 or sys.argv[1] != 'serve' or sys.argv[2] not in observer.ARMS:
        return 2
    arm = sys.argv[2]
    hello = dict(schema='eq117.worker.hello.v1', arm=arm, prefix=sys.prefix,
                 executable=sys.executable, python=platform.python_version(), imports_completed=True)
    sys.stdout.buffer.write(observer.encoded(hello))
    sys.stdout.buffer.flush()
    first = True
    while True:
        raw = sys.stdin.buffer.readline(8193)
        if not raw:
            return 0
        if len(raw) > 8192:
            return 2
        request = observer.shape(observer.parsed(raw), {'seed', 'root', 'trial_id'})
        if not all(type(v) is str and len(v) <= 4096 for v in request.values()):
            return 2
        out = trial(Path(request['seed']), Path(request['root']), arm, request['trial_id'],
                    actual_cli_invocations=int(first))
        first = False
        if out['status'] != 'valid':
            return 1


if __name__ == '__main__':
    raise SystemExit(main())
