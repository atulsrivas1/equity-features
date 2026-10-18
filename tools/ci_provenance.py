"""Produce a routing-policy sidecar before independent final run acceptance.

No product imports, network, package execution or physical-resource claims.
Contract: docs/stories/CI-002_CONTRACT.json.
"""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import ci_gate
import ci_scope

SCHEMA = "equity-features.ci-policy.v1"
STAGE = "GATE_EVALUATED_NOT_FINAL_RUN_ACCEPTANCE"
BOUNDARIES = "Existing GitHub Actions/runtime refs, interpreter and package/native dependency qualification remain baseline boundaries; no full host/physical or source-binary platform attestation."


def positive(raw: Any) -> int:
    ci_gate.require(type(raw) is str and re.fullmatch(r"[1-9][0-9]*", raw) is not None)
    return int(raw)


def inventory(root: Path, head: str) -> dict[str, dict[str, Any]]:
    """Hash every immutable regular blob, including binary files, exactly once."""
    ci_scope.oid(head)
    raw = ci_scope.git(root, "ls-tree", "-r", "-z", "--full-tree", head)
    ci_gate.require(raw.endswith(b"\0"))
    entries: dict[str, tuple[str, str]] = {}
    for entry in raw[:-1].split(b"\0"):
        match = re.fullmatch(rb"(100644|100755) blob ([0-9a-f]{40})\t(.+)", entry, re.S)
        ci_gate.require(match is not None)
        assert match is not None
        mode, oid, path = match.groups()
        name = path.decode("utf-8", errors="strict")
        ci_gate.require(not name.startswith("/") and "\\" not in name and ":" not in name)
        ci_gate.require(all(p not in ("", ".", "..") for p in name.split("/")))
        ci_gate.require(not any(ord(c) < 32 or ord(c) == 127 for c in name) and name not in entries)
        entries[name] = (mode.decode("ascii"), oid.decode("ascii"))
    ids = sorted({oid for _, oid in entries.values()})
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_")}
    env.update(GIT_NO_REPLACE_OBJECTS="1", GIT_OPTIONAL_LOCKS="0")
    done = subprocess.run(["git", "--no-pager", "cat-file", "--batch"], cwd=root, env=env,
                          input=("\n".join(ids) + "\n").encode("ascii"), stdout=subprocess.PIPE,
                          stderr=subprocess.DEVNULL, check=False)
    ci_gate.require(done.returncode == 0)
    data = done.stdout
    offset = 0
    hashes: dict[str, tuple[int, str]] = {}
    for oid in ids:
        end = data.find(b"\n", offset)
        ci_gate.require(end >= offset)
        fields = data[offset:end].split(b" ")
        ci_gate.require(len(fields) == 3 and fields[:2] == [oid.encode("ascii"), b"blob"])
        ci_gate.require(re.fullmatch(rb"0|[1-9][0-9]*", fields[2]) is not None)
        size = int(fields[2]); offset = end + 1
        blob = data[offset:offset + size]; offset += size
        ci_gate.require(len(blob) == size and data[offset:offset + 1] == b"\n"); offset += 1
        ci_gate.require(hashlib.sha1(b"blob " + str(size).encode() + b"\0" + blob).hexdigest() == oid)
        hashes[oid] = (size, hashlib.sha256(blob).hexdigest())
    ci_gate.require(offset == len(data))
    return {name: {"git_oid": oid, "kind": "blob", "mode": mode, "bytes": hashes[oid][0],
                   "sha256": hashes[oid][1]} for name, (mode, oid) in sorted(entries.items())}


def build(root: Path, context: dict[str, str], event: Any, needs: Any) -> dict[str, Any]:
    expected = ci_scope.classify(root, event, context)
    results = ci_gate.validate(needs, expected)
    head = expected["checkout_head"]
    source = inventory(root, head)
    actual_workflows = {p for p in source if p.startswith(".github/workflows/") and p.endswith((".yml", ".yaml"))}
    ci_gate.require(actual_workflows == set(ci_gate.WORKFLOWS))
    for module in (ci_scope, ci_gate, sys.modules[__name__]):
        path = Path(module.__file__).resolve()
        relative = "tools/" + path.name
        ci_gate.require(path == (root / relative).resolve() and relative in source)
        data = path.read_bytes()
        ci_gate.require(len(data) == source[relative]["bytes"] and hashlib.sha256(data).hexdigest() == source[relative]["sha256"])
    workflow = ".github/workflows/qualification.yml"
    workflow_sha = ci_scope.oid(context.get("GITHUB_WORKFLOW_SHA"))
    ci_gate.require(ci_scope.resolved(root, workflow_sha, "commit") == workflow_sha)
    workflow_ref = ci_scope.REPOSITORY + "/" + workflow + "@" + context["GITHUB_REF"]
    ci_gate.require(context.get("GITHUB_WORKFLOW_REF") == workflow_ref)
    for path in ci_gate.WORKFLOWS:
        blob = ci_scope.git(root, "cat-file", "blob", workflow_sha + ":" + path)
        ci_gate.require(hashlib.sha256(blob).hexdigest() == source[path]["sha256"] and len(blob) == source[path]["bytes"])
    ci_gate.require(ci_scope.resolved(root, "HEAD", "commit") == head)
    return dict(schema=SCHEMA, stage=STAGE, repository=ci_scope.REPOSITORY,
                event=expected["event"], run_id=positive(context.get("GITHUB_RUN_ID")),
                run_attempt=positive(context.get("GITHUB_RUN_ATTEMPT")), ref=context["GITHUB_REF"],
                checkout_head=head, checkout_tree=expected["checkout_tree"],
                workflow_ref=workflow_ref, workflow_sha=workflow_sha, classification=expected,
                logical_results=results, source_map_sha256=hashlib.sha256(ci_gate.canonical(source)).hexdigest(),
                declared_external_boundaries=BOUNDARIES, gate_qualified=True, source_map=source)


def error(context: dict[str, str]) -> dict[str, Any]:
    def optional(name: str) -> int | None:
        try:
            return positive(context.get(name))
        except ValueError:
            return None
    return dict(schema="equity-features.ci-policy-error.v1", gate_qualified=False,
                reason="QUALIFICATION_REJECTED", run_id=optional("GITHUB_RUN_ID"),
                run_attempt=optional("GITHUB_RUN_ATTEMPT"))


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    target = root / "dist/ci/policy/qualification.json"
    context = dict(os.environ)
    try:
        ci_gate.require(len(sys.argv) == 1 and not target.exists())
        event = ci_gate.loads(Path(context["GITHUB_EVENT_PATH"]).read_bytes())
        needs = ci_gate.loads(context["CI_NEEDS"])
        record = build(root, context, event, needs)
        code = 0
    except Exception:
        record = error(context)
        code = 1
    try:
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("xb") as output:
            output.write((json.dumps(record, ensure_ascii=True, sort_keys=True, indent=2) + "\n").encode("utf-8"))
    except OSError:
        return 1
    return code


if __name__ == "__main__":
    raise SystemExit(main())
