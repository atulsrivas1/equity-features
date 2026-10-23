#!/usr/bin/env python3
"""Quiet parallel batch runner (stdlib only).

Runs shell commands from a file (one per line; blank lines and lines starting
with '#' are skipped) with N workers. Per-command output goes to a log file;
nothing is printed per command. One final summary is printed; exit code is
non-zero if any command failed or timed out.

Usage:
  python tools/run_batch.py --cmd-file cmds.txt --log-dir logs [--workers 4]
        [--timeout 600] [--heartbeat-file hb.txt] [--cwd DIR]
  python tools/run_batch.py cmds.txt --log-dir logs

Log files: <log-dir>/<NNNN>.log (NNNN = 1-based line order among commands),
first line is the command. Heartbeat file is rewritten with 'done/total'
every ~3 seconds (for peeking, not streaming).
"""
import argparse
import os
import subprocess
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor


def kill_tree(proc):
    try:
        if os.name == "nt":
            subprocess.run(["taskkill", "/F", "/T", "/PID", str(proc.pid)],
                           stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            import signal
            os.killpg(proc.pid, signal.SIGKILL)
    except Exception:
        proc.kill()


def run_one(idx, cmd, log_dir, timeout, cwd):
    path = os.path.join(log_dir, f"{idx:04d}.log")
    start = time.time()
    status, code = "pass", 0
    with open(path, "w", encoding="utf-8", newline="\n") as log:
        log.write(f"$ {cmd}\n")
        log.flush()
        kw = {} if os.name == "nt" else {"start_new_session": True}
        try:
            proc = subprocess.Popen(cmd, shell=True, cwd=cwd, stdout=log, stderr=subprocess.STDOUT,
                                    stdin=subprocess.DEVNULL, **kw)
        except OSError as e:
            log.write(f"[run_batch] failed to start: {e}\n")
            return idx, cmd, "fail", -1, path, 0.0
        try:
            code = proc.wait(timeout=timeout)
            if code != 0:
                status = "fail"
        except subprocess.TimeoutExpired:
            kill_tree(proc)
            proc.wait()
            status, code = "timeout", -1
            log.write(f"\n[run_batch] TIMEOUT after {timeout}s\n")
        log.write(f"\n[run_batch] exit={code} status={status}\n")
    return idx, cmd, status, code, path, time.time() - start


def tail(path, n=5):
    try:
        with open(path, encoding="utf-8", errors="replace") as fh:
            lines = [l.rstrip("\n") for l in fh]
    except OSError:
        return ["(log unreadable)"]
    return [l for l in lines if l.strip()][-n:]


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("cmds", nargs="?", help="command file (alternative to --cmd-file)")
    ap.add_argument("--cmd-file")
    ap.add_argument("--log-dir", required=True)
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--timeout", type=float, default=600.0, help="seconds per command (default 600)")
    ap.add_argument("--heartbeat-file")
    ap.add_argument("--cwd", help="working directory for the commands")
    a = ap.parse_args()
    src = a.cmd_file or a.cmds
    if not src:
        ap.error("give a command file (positional or --cmd-file)")
    with open(src, encoding="utf-8") as fh:
        cmds = [l.strip() for l in fh if l.strip() and not l.lstrip().startswith("#")]
    os.makedirs(a.log_dir, exist_ok=True)
    total = len(cmds)
    done = [0]
    lock = threading.Lock()
    stop = threading.Event()

    def beat():
        if a.heartbeat_file:
            tmp = a.heartbeat_file + ".tmp"
            with open(tmp, "w", newline="\n") as fh:
                fh.write(f"{done[0]}/{total}\n")
            os.replace(tmp, a.heartbeat_file)

    def beater():
        while not stop.wait(3):
            beat()

    beat()
    th = threading.Thread(target=beater, daemon=True)
    th.start()
    results = []

    def job(i):
        r = run_one(i + 1, cmds[i], a.log_dir, a.timeout, a.cwd)
        with lock:
            done[0] += 1
            results.append(r)
        return r

    t0 = time.time()
    with ThreadPoolExecutor(max_workers=max(1, a.workers)) as ex:
        list(ex.map(job, range(total)))
    stop.set()
    th.join()
    beat()
    results.sort()
    npass = sum(r[2] == "pass" for r in results)
    nfail = sum(r[2] == "fail" for r in results)
    nto = sum(r[2] == "timeout" for r in results)
    print(f"run_batch: total={total} pass={npass} fail={nfail} timeout={nto} "
          f"elapsed={time.time() - t0:.1f}s logs={os.path.abspath(a.log_dir)}")
    for idx, cmd, status, code, path, secs in results:
        if status != "pass":
            print(f"--- {status.upper()} #{idx} exit={code} {secs:.1f}s: {cmd}")
            print(f"    log: {path}")
            for line in tail(path):
                print(f"    | {line}")
    return 0 if nfail == 0 and nto == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
