"""Gate for the EF5 price-structures contract fixtures (candle, structure, technical, known_at KA-set).

Runs the independent stdlib expander `tools/contract_fixtures/ef5_fixture_expand.py` as a subprocess, requires exit
status 0 and its success line, and requires the fixture and refusal counts it reports to equal both the counts pinned
in this file and the counts declared in the contract JSON (`fixture_counts`). It then pins the known_at semantics
(null is `unknown_availability`, later than K is `future_knowledge`, equal to K is available), requires every pattern
output to have a positive, a negative and an unavailable fixture, requires the fail-closed drivers (undeclared
coverage, missing known_at, future known_at, missing context) to exist and to refuse, and requires every contract
header to carry an E9 slash-style unit. Run from a source checkout: `python tools/verify_ef5_fixtures.py`;
exit status 0 only if everything holds.
"""
from __future__ import annotations

import importlib.util
import json
import re
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "ef5" / "PRICE_STRUCTURES_CONTRACT_PROPOSAL.json"
HELPER = ROOT / "tools" / "contract_fixtures" / "ef5_fixture_expand.py"
K = 100
# Pinned counts: a change to a fixture list must change these numbers in the same PR.
PINNED = {"candle_result": 23, "structure_result": 16, "technical_result": 18, "ka_result": 27, "refusal": 49}
PINNED_HEADERS = 15
PINNED_REFUSAL_CODES = 12
LISTS = ("candle_fixtures", "structure_fixtures", "technical_fixtures", "ka_fixtures")
UNIT = re.compile(r"^(boolean|currency/share|fraction|fraction/s|fraction/s\^2|windows)$")


def expect(problems: list[str], label: str, got: Any, want: Any) -> None:
    if got != want:
        problems.append(f"{label}: got {got!r} want {want!r}")


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("ef5_fixture_expand", HELPER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def check_expander(problems: list[str], doc: dict[str, Any]) -> None:
    done = subprocess.run([sys.executable, "-I", str(HELPER)], cwd=ROOT, capture_output=True, text=True, check=False)
    out = done.stdout + done.stderr
    expect(problems, "expander exit status", done.returncode, 0)
    if "ALL FIXTURES AND REFUSALS RECOMPUTED AND MATCHED" not in out:
        problems.append("expander success line missing")
    found = re.search(r"candle=(\d+) structure=(\d+) technical=(\d+) ka=(\d+) refusal=(\d+) \((\d+) outputs recomputed; "
                      r"(\d+) distinct refusal codes\)", out)
    got = [int(g) for g in found.groups()] if found else None
    want = [PINNED[k] for k in ("candle_result", "structure_result", "technical_result", "ka_result", "refusal")]
    expect(problems, "expander counts vs pinned", got[:5] if got else None, want)
    expect(problems, "contract fixture_counts vs pinned", doc["fixture_counts"], PINNED)
    expect(problems, "distinct refusal codes", got[6] if got else None, PINNED_REFUSAL_CODES)
    expect(problems, "header count", len(doc["headers"]), PINNED_HEADERS)


def check_known_at_rules(problems: list[str]) -> None:
    mod = load()
    for ka, want in ((None, "unknown_availability"), (K + 1, "future_knowledge"), (K, None), (K - 1, None)):
        expect(problems, f"know_reason({ka})", mod.know_reason(ka, K), want)
        expect(problems, f"classify_slot({ka})", mod.classify_slot({"row": [1, 1, 1, 1, 1], "ka": ka}, K)[0], want)
    expect(problems, "forming bar", mod.classify_slot("forming", K)[0], "future_market")


def check_pattern_coverage(problems: list[str], doc: dict[str, Any]) -> None:
    bools = {h["id"] for h in doc["headers"] if h["dtype"] == "bool"}
    seen: dict[str, set[str]] = {h["id"]: set() for h in doc["headers"]}
    for key in LISTS:
        for fx in doc[key]:
            for name, res in fx["expected"].items():
                if res["status"] != "available":
                    seen[name].add("unavailable")
                elif name in bools:
                    seen[name].add("positive" if res["value"]["bool"] else "negative")
                else:
                    seen[name].add("positive")
    for name, kinds in seen.items():
        need = {"positive", "unavailable"} | ({"negative"} if name in bools else set())
        if not need <= kinds:
            problems.append(f"{name}: fixtures missing kinds {sorted(need - kinds)}")
    reasons = json.dumps([fx["expected"] for key in LISTS for fx in doc[key]])
    for reason in ("unknown_availability", "future_knowledge", "insufficient_history", "zero_denominator",
                   "governed_gap", "future_market", "absent_input", "null_field", "no_eligible_observations"):
        if f'"{reason}"' not in reasons:
            problems.append(f"no fixture exercises {reason}")


def check_fail_closed(problems: list[str], doc: dict[str, Any]) -> None:
    drivers = doc["fail_closed_drivers"]
    for key in ("undeclared_coverage", "missing_known_at", "future_known_at", "missing_context", "missing_adjustment"):
        if not drivers[key]:
            problems.append(f"fail-closed driver {key} is empty")
    refusals = {r["id"]: r for r in doc["refusal_fixtures"]}
    for rid in drivers["undeclared_coverage"] + drivers["missing_context"] + drivers["missing_adjustment"] \
            + drivers["missing_parameters"]:
        if rid not in refusals:
            problems.append(f"fail-closed driver {rid} is not a refusal fixture")
    ka = {fx["id"]: fx for fx in doc["ka_fixtures"]}
    for fid in drivers["missing_known_at"] + drivers["future_known_at"]:
        res = ka[fid]["expected"]
        if not any(r["status"] == "missing_input" and r["value"] is None and not r["witnesses"] for r in res.values()):
            problems.append(f"{fid}: known_at driver yields no null-valued missing_input output")
    for fx in (f for key in LISTS for f in doc[key]):
        for name, res in fx["expected"].items():
            if (res["status"] == "available") != (res["value"] is not None):
                problems.append(f"{fx['id']} {name}: value null exactly when not available is violated")
            if res["status"] == "available" and res["expected"] != res["observed"]:
                problems.append(f"{fx['id']} {name}: available with observed != expected")


def check_units(problems: list[str], doc: dict[str, Any]) -> None:
    for h in doc["headers"]:
        if not UNIT.match(h["unit"]):
            problems.append(f"{h['id']}: unit {h['unit']!r} is not an E9 slash-style unit")
        if "_per_" in h["unit"]:
            problems.append(f"{h['id']}: underscore unit form on a new header")


def main() -> int:
    doc = json.loads(CONTRACT.read_text(encoding="utf-8"))
    problems: list[str] = []
    check_expander(problems, doc)
    check_known_at_rules(problems)
    check_pattern_coverage(problems, doc)
    check_fail_closed(problems, doc)
    check_units(problems, doc)
    for line in problems:
        print("MISMATCH", line)
    print("EF5 fixtures (candle, structure, technical, known_at set): "
          + ("expander matched, counts pinned, known_at and fail-closed rules hold" if not problems
             else f"{len(problems)} problem(s)"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
