"""Verify a fixed delivered three-wheel quickstart, without rebuilding packages.

Run from the reviewed checkout using CPython3.12 x64 and existing gh read access.
Timeouts are cooperative subprocess controls, not a physical containment claim.
"""
from pathlib import Path, PurePosixPath
import base64
import csv
from datetime import datetime, timezone
import email.parser
import hashlib
import io
import json
import os
import platform
import re
import struct
import subprocess
import sys
import time
import zipfile

ROOT = Path(__file__).resolve().parents[1]
INPUTS = ROOT / "docs/stories/EQ-132_INPUTS.json"
REPO = "atulsrivas1/equity-features"
LIMIT = 2 * 1024 * 1024


def require(condition, message):
    if not condition:
        raise ValueError(message)


def sha(raw):
    return hashlib.sha256(raw).hexdigest()


def read_json(path):
    return json.loads(Path(path).read_bytes())


def validate_platform(system, implementation, version, bits, machine=None):
    machine = platform.machine() if machine is None else machine
    require(system in ("Windows", "Linux") and implementation == "cpython"
            and tuple(version) == (3, 12) and bits == 64 and machine.casefold() in ("amd64", "x86_64"),
            "supported runtime is CPython3.12 x64 Windows/Linux")


def validate_artifact(current, expected, now):
    for key in ("id", "name", "size_in_bytes", "digest", "expires_at", "workflow_run"):
        require(current[key] == expected[key], "artifact metadata drift: " + key)
    require(current["expired"] is False and 0 < current["size_in_bytes"] < LIMIT,
            "artifact unavailable or oversized")
    expiry = datetime.fromisoformat(current["expires_at"].replace("Z", "+00:00"))
    require(now < expiry, "retained artifact expired; do not substitute latest or rebuild")


def zip_files(raw, expected):
    require(0 < len(raw) < LIMIT, "archive size refused")
    with zipfile.ZipFile(io.BytesIO(raw)) as archive:
        entries = archive.infolist()
        require(len(entries) <= 64 and len({x.filename for x in entries}) == len(entries),
                "duplicate or excessive ZIP entries")
        require(sum(x.file_size for x in entries) <= 4 * LIMIT, "expanded archive refused")
        result = {}
        for item in entries:
            path = PurePosixPath(item.filename)
            require(not item.is_dir() and not path.is_absolute() and ".." not in path.parts
                    and "\\" not in item.filename and ":" not in item.filename
                    and item.file_size < LIMIT and not item.flag_bits & 1
                    and (item.external_attr >> 16) & 0o170000 in (0, 0o100000),
                    "non-regular or unsafe ZIP entry")
            data = archive.read(item)
            result[item.filename] = data
        actual = {p: {"sha256": sha(v), "bytes": len(v)} for p, v in result.items()}
        require(actual == expected, "complete archive entry map drift")
        return result


def validate_wheel(raw, expected):
    require(sha(raw) == expected["sha256"] and len(raw) == expected["bytes"], "wheel identity drift")
    files = zip_files(raw, expected["entries"])
    name = next(p for p in files if p.endswith(".dist-info/METADATA"))
    message = email.parser.BytesParser().parsebytes(files[name])
    observed = {"name": message["Name"], "version": message["Version"],
        "requires_python": message["Requires-Python"], "requires_dist": message.get_all("Requires-Dist", []),
        "license_expression": message["License-Expression"]}
    require(observed == expected["metadata"] and observed["license_expression"] == "Apache-2.0",
            "wheel metadata/dependency/license drift")
    record = next(p for p in files if p.endswith(".dist-info/RECORD"))
    rows = list(csv.reader(io.StringIO(files[record].decode("utf-8"))))
    require(len(rows) == len(files) and {x[0] for x in rows} == set(files), "RECORD names drift")
    for path, digest, size in rows:
        if path == record:
            require(digest == size == "", "RECORD self entry must be empty")
        else:
            wanted = "sha256=" + base64.urlsafe_b64encode(hashlib.sha256(files[path]).digest()).decode().rstrip("=")
            require(digest == wanted and size == str(len(files[path])), "RECORD payload drift")
    for path, binding in expected["source_bindings"].items():
        require(sha(files[path]) == binding["wheel_raw_sha256"], "raw source payload drift")
        require(sha(files[path].replace(b"\r\n", b"\n")) == binding["LF_equivalent_sha256"],
                "declared source representation drift")
    return files


def validate_stdout(raw, lines):
    require(raw.replace(b"\r\n", b"\n") == ("\n".join(lines) + "\n").encode(),
            "complete four-line output mismatch")


def unchanged_core(before, after):
    require(before["core"] == after["core"] and before["core_sha256"] == after["core_sha256"],
            "installed core changed")


def new_work(root, system):
    root = Path(root)
    parent = root / "work"
    target = parent / ("eq132-quickstart-" + system)
    for path in (parent, *parent.parents):
        require(not path.is_symlink() and not (hasattr(path, "is_junction") and path.is_junction()),
                "symlinked/junction parent refused")
    require(not os.path.lexists(target), "work destination exists; retain it, do not overwrite or auto-delete")
    parent.mkdir(exist_ok=True)
    target.mkdir()
    return target


class Replay:
    def __init__(self, root=ROOT):
        self.root = Path(root)
        self.inputs = read_json(self.root / "docs/stories/EQ-132_INPUTS.json")
        validate_platform(platform.system(), sys.implementation.name, sys.version_info[:2], struct.calcsize("P") * 8)
        require(not sys.flags.optimize, "assertions-enabled Python required")
        self.system = platform.system()
        self.selected = next(a for a in self.inputs["artifacts"] if a["manifest"]["system"] == self.system)
        self.work = new_work(self.root, self.system)
        for directory in ("raw-private", "logs", "wheelhouse", "run"):
            (self.work / directory).mkdir()
        self.steps = []
        self.start = time.monotonic()
        self.report = {"schema": "eq132.quickstart-replay.v1", "status": "RUNNING",
            "system": self.system, "machine": platform.machine(), "parent_python": platform.python_version(),
            "inputs_sha256": sha((self.root / "docs/stories/EQ-132_INPUTS.json").read_bytes()),
            "accepted_package_main": self.inputs["accepted_main"],
            "verifier_sha256": sha(Path(__file__).read_bytes()),
            "probe_sha256": sha((self.root / "tools/quickstart_probe.py").read_bytes()),
            "steps": self.steps, "timing_scope": "Automated maintainer replay; existing Python/gh/auth/checkout excluded. No novice five-minute claim."}

    def public(self, text):
        # Actual absolute paths remain in ignored local raw-private logs only.
        for original, replacement in ((str(self.work), "$WORK"), (str(self.root), "$CHECKOUT"),
                                      (str(Path(sys.executable)), "$PYTHON")):
            for variant in (original, original.replace("\\", "/"), original.replace("\\", "\\\\")):
                text = re.sub(re.escape(variant), lambda _: replacement, text,
                              flags=re.IGNORECASE if self.system == "Windows" else 0)
        return text

    def run(self, label, args, timeout, cwd=None, binary=False):
        number = len(self.steps) + 1
        out = self.work / "raw-private" / (f"{number:02}-{label}.out")
        err = self.work / "raw-private" / (f"{number:02}-{label}.err")
        step = {"label": label, "command": [self.public(str(x)) for x in args],
                "cwd": self.public(str(cwd or self.work / "run")), "timeout_seconds": timeout}
        self.steps.append(step)
        start = time.monotonic()
        try:
            with out.open("xb") as stdout, err.open("xb") as stderr:
                proc = subprocess.run([str(x) for x in args], cwd=cwd or self.work / "run",
                    stdin=subprocess.DEVNULL, stdout=stdout, stderr=stderr, timeout=timeout)
            step["returncode"] = proc.returncode
            require(proc.returncode == 0, "command failed: " + label)
        except subprocess.TimeoutExpired:
            step["timed_out"] = True
            raise
        finally:
            step["elapsed_seconds"] = time.monotonic() - start
            for kind, path in (("stdout", out), ("stderr", err)):
                if path.exists():
                    require(path.stat().st_size <= LIMIT, "command output exceeded acceptance cap")
                    data = path.read_bytes()
                    step[kind + "_bytes"] = len(data)
                    if not (binary and kind == "stdout"):
                        public = self.public(data.decode("utf-8"))
                        (self.work / "logs" / f"{number:02}-{label}-{kind}.txt").write_bytes(public.encode())
        return out.read_bytes()

    def api(self, label, endpoint):
        return json.loads(self.run(label, ["gh", "api", "repos/" + REPO + "/" + endpoint], 180))

    def probe(self, label, phase):
        return json.loads(self.run(label, [self.py, "-I", "-B", self.root / "tools/quickstart_probe.py",
            phase, self.root / "docs/stories/EQ-132_INPUTS.json"], 60))

    def execute(self):
        selected = self.selected
        artifact = selected["artifact"]
        actual = self.api("artifact-metadata", f'actions/artifacts/{artifact["id"]}')
        validate_artifact(actual, artifact, datetime.now(timezone.utc))
        binding = selected["delivery_job_binding"]
        run = self.api("accepted-run", f'actions/runs/{binding["run"]}')
        require(run["head_sha"] == self.inputs["accepted_main"] and run["head_branch"] == "main"
            and run["event"] == "push" and run["status"] == "completed" and run["conclusion"] == "success"
            and run["run_attempt"] == 1 and run["workflow_id"] == binding["registered_workflow_id"]
            and run["repository"]["full_name"] == REPO, "accepted workflow run binding drift")
        jobs = self.api("accepted-job", f'actions/runs/{binding["run"]}/attempts/1/jobs?per_page=100')
        require(jobs["total_count"] == len(jobs["jobs"]) == 2, "Foundation job set drift")
        job = next(j for j in jobs["jobs"] if j["id"] == binding["job"])
        require(job["name"] == binding["name"] and job["head_sha"] == self.inputs["accepted_main"]
            and job["status"] == "completed" and job["conclusion"] == "success", "Foundation job binding drift")
        raw = self.run("download", ["gh", "api", f'repos/{REPO}/actions/artifacts/{artifact["id"]}/zip'], 180, binary=True)
        require(len(raw) == artifact["size_in_bytes"] and "sha256:" + sha(raw) == artifact["digest"],
                "delivered ZIP identity drift")
        start = time.monotonic()
        files = zip_files(raw, selected["files"])
        require(json.loads(files["manifest.json"]) == selected["manifest"], "Foundation manifest drift")
        for name, wheel in selected["selected_wheels"].items():
            validate_wheel(files[name], wheel)
            (self.work / "wheelhouse" / name).write_bytes(files[name])
        self.report["archive_verification_seconds"] = time.monotonic() - start
        self.report["artifact"] = artifact
        self.report["source_map"] = self.inputs["effective_source_map"]
        self.report["wheel_maps"] = selected["selected_wheels"]
        self.run("create-venv", [sys.executable, "-I", "-B", "-m", "venv", self.work / "env"], 60)
        self.py = self.work / "env" / ("Scripts/python.exe" if self.system == "Windows" else "bin/python")
        wheels = self.work / "wheelhouse"
        core = [wheels / n for n in selected["selected_wheels"] if not n.startswith("equity_feature_demo-")]
        consumer = [wheels / n for n in selected["selected_wheels"] if n.startswith("equity_feature_demo-")]
        require(len(core) == 2 and len(consumer) == 1, "exact three-wheel selection required")
        install = [self.py, "-I", "-B", "-m", "pip", "--isolated", "install", "--no-index", "--no-deps", "--no-compile"]
        self.run("install-core", install + core, 120)
        before = self.probe("core-before", "core")
        self.run("install-consumer", install + consumer, 120)
        installed = self.probe("installed", "full")
        unchanged_core(before, installed)
        self.run("pip-check", [self.py, "-I", "-B", "-m", "pip", "check"], 120)
        stdout = self.run("walkthrough", [self.py, "-I", "-B", "-m", "equity_feature_demo.walkthrough"], 60)
        validate_stdout(stdout, self.inputs["independent_expected"]["stdout_lines"])
        results = self.probe("independent-results", "results")
        qualification = json.loads(self.run("public-qualification",
            [self.py, "-I", "-B", "-m", "equity_feature_demo.qualification"], 60))
        baseline = json.loads(files[f"consumer-{self.system}-whl.json"])["qualification"]
        require(len(baseline["cases"]) == 43 and qualification == baseline,
                "complete immutable public qualification object mismatch")
        after = self.probe("core-after", "full")
        unchanged_core(before, after)
        require(installed == after, "installed payload changed during replay")
        self.report.update({"status": "PASSED", "runtime": after, "before_core": before,
            "independent_results": results, "walkthrough_stdout": stdout.replace(b"\r\n", b"\n").decode(),
            "qualification": qualification, "qualification_cases": 43, "installed_payload_unchanged": True})

    def save(self):
        self.report["elapsed_seconds"] = time.monotonic() - self.start
        (self.work / "report.json").write_bytes((json.dumps(self.report, indent=2) + "\n").encode())


def main():
    replay = Replay()
    try:
        replay.execute()
    except Exception as error:
        replay.report.update({"status": "FAILED", "failure_type": type(error).__name__,
                              "failure": replay.public(str(error)), "cleanup_claimed": False})
        raise
    finally:
        replay.save()
    print(replay.report["walkthrough_stdout"], end="")
    print("Quickstart PASSED; three delivered wheels, four output lines and 43 qualification cases verified.")
    print("See work/eq132-quickstart-" + replay.system + "/report.json for actual scoped timings and provenance.")


if __name__ == "__main__":
    main()
