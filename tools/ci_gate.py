"""Closed logical CI dependency gate; not a platform/security attestation."""
from __future__ import annotations

import json
import re
from typing import Any

import ci_scope

LEAVES = (
    "agent-evidence", "agent-ledger", "conformance", "continuous", "diagnostics",
    "evidence", "evidence-evaluation", "evidence-pilot", "explanations", "packages",
    "provenance", "quickstart", "r9", "r10", "research", "transport",
)
ROOTS = ("scope", "docs", *LEAVES)
WORKFLOWS = tuple(".github/workflows/" + n + ".yml" for n in ("qualification", "docs", *LEAVES))


def require(condition: bool) -> None:
    if not condition:
        raise ValueError("QUALIFICATION_REJECTED")


def reject_constant(value: str) -> Any:
    raise ValueError("QUALIFICATION_REJECTED")


def loads(raw: str | bytes) -> Any:
    return json.loads(raw, object_pairs_hook=ci_scope.unique_object, parse_constant=reject_constant)


def canonical(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False).encode("utf-8")


def classification(record: Any) -> None:
    require(type(record) is dict and set(record) == set(ci_scope.invalid()))
    require(record["schema"] == ci_scope.SCHEMA and record["valid"] is True)
    require(record["repository"] == ci_scope.REPOSITORY)
    require(record["event"] in ("push", "pull_request"))
    require(record["allowlist_sha256"] == ci_scope.ALLOWLIST_SHA256)
    for name in ("source_head", "checkout_head", "checkout_tree"):
        ci_scope.oid(record[name])
    if record["reason"] == "INITIAL_PUSH":
        require(record["decision"] == "FULL" and record["event"] == "push")
        require(all(record[k] is None for k in ("base", "diff_sha256", "changes_count")))
    else:
        ci_scope.oid(record["base"])
        require(type(record["diff_sha256"]) is str and re.fullmatch(r"[0-9a-f]{64}", record["diff_sha256"]) is not None)
        count = record["changes_count"]
        require(type(count) is int and count >= 0)
        require((record["reason"], record["decision"]) in (
            ("READERS_ONLY", "DOCS"), ("EMPTY_DIFF", "FULL"), ("NON_READER_CHANGE", "FULL"),
        ))
        require((count == 0) == (record["reason"] == "EMPTY_DIFF"))


def validate(needs: Any, expected: dict[str, Any]) -> dict[str, str]:
    """Require exact original results plus a freshly source-bound scope record."""
    classification(expected)
    require(type(needs) is dict and set(needs) == set(ROOTS))
    results: dict[str, str] = {}
    for name in ROOTS:
        entry = needs[name]
        require(type(entry) is dict and set(entry) == {"result", "outputs"})
        require(type(entry["result"]) is str and entry["result"] in ("success", "failure", "cancelled", "skipped"))
        require(type(entry["outputs"]) is dict)
        require(set(entry["outputs"]) == ({"record"} if name == "scope" else set()))
        results[name] = entry["result"]
    require(results["scope"] == results["docs"] == "success")
    raw = needs["scope"]["outputs"]["record"]
    require(type(raw) is str)
    actual = loads(raw)
    classification(actual)
    require(canonical(actual) == canonical(expected))
    wanted = "success" if expected["decision"] == "FULL" else "skipped"
    require(all(results[name] == wanted for name in LEAVES))
    return results
