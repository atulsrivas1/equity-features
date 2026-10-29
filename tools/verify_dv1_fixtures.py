"""Gate for the DV1 definition-variants contract fixtures (log beta/correlation, simple-mean ATR, core spread,
range over open, window extremes). Status of the contract: draft, not frozen.

Runs the independent stdlib expander `tools/contract_fixtures/dv1_fixture_expand.py` as a subprocess, requires exit
status 0 and its success line, and requires the fixture and refusal counts it reports to equal both the counts pinned
in this file and the counts declared in the contract JSON (`fixture_counts`). It then requires every header to carry
an input contract and an output contract, an E9 slash-style unit, every output id to have a positive, an unavailable
and a wrong-convention fixture (signed outputs also a negative one), the wrong-convention fixtures that the PO rulings
name (simple vs log, Wilder vs simple mean, close vs open range, range vs stdev, window length 253/252, high vs close
basis, tie rule, regular_open operand), the fail-closed drivers, the known_at semantics, the EF4 equality fixtures for
the deprecated range id, and the posture wording (draft, internal, synthetic, pre-release; no performance claim), and that no EF1-EF5 file except the 4-line EF4 erratum differs from origin/main.
Run from a source checkout: `python tools/verify_dv1_fixtures.py`; exit status 0 only if everything holds.
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
CONTRACT = ROOT / "docs" / "dv1" / "DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json"
CONTRACT_MD = ROOT / "docs" / "dv1" / "DEFINITION_VARIANTS_CONTRACT_PROPOSAL.md"
HELPER = ROOT / "tools" / "contract_fixtures" / "dv1_fixture_expand.py"
# Pinned counts: a change to a fixture list must change these numbers in the same PR.
PINNED = {"atr_result": 20, "window_result": 25, "relative_log_result": 23, "core_spread_result": 21,
          "range_over_open_result": 11, "refusal": 72}
PINNED_HEADERS = 10
PINNED_REFUSAL_CODES = 12
PINNED_RIVAL_CHECKS = 66
LISTS = ("atr_fixtures", "window_fixtures", "relative_log_fixtures", "core_spread_fixtures", "range_over_open_fixtures")
UNIT = re.compile(r"^(currency/share|fraction|sessions)$")
SIGNED = {"relative.log_return_beta", "relative.log_return_correlation"}
REQUIRED_CONVENTIONS = {"simple_return_beta", "simple_return_correlation", "wilder_atr", "prior_only_mean", "hl_range_only_mean",
                        "close_denominator", "range_instead_of_stdev", "stdev_instead_of_range", "first_trade_operand",
                        "first_bar_open_operand", "prior_close_basis", "period_252", "period_253", "close_basis", "intraday_basis",
                        "earliest_wins", "daily_bar_open_operand"}
BANNED = re.compile(r"\b(faster|speed-?up|speedup|throughput|latency gain|performance gain)\b", re.I)


def expect(problems: list[str], label: str, got: Any, want: Any) -> None:
    if got != want:
        problems.append(f"{label}: got {got!r} want {want!r}")


def load() -> ModuleType:
    spec = importlib.util.spec_from_file_location("dv1_fixture_expand", HELPER)
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
    found = re.search(r"atr=(\d+) window=(\d+) relative_log=(\d+) core=(\d+) range_over_open=(\d+) refusal=(\d+) "
                      r"\((\d+) outputs recomputed; (\d+) distinct refusal codes; (\d+) rival/cross checks\)", out)
    got = [int(g) for g in found.groups()] if found else None
    want = [PINNED[k] for k in ("atr_result", "window_result", "relative_log_result", "core_spread_result",
                                "range_over_open_result", "refusal")]
    expect(problems, "expander counts vs pinned", got[:6] if got else None, want)
    expect(problems, "contract fixture_counts vs pinned", doc["fixture_counts"], PINNED)
    expect(problems, "distinct refusal codes", got[7] if got else None, PINNED_REFUSAL_CODES)
    expect(problems, "rival and cross checks", got[8] if got else None, PINNED_RIVAL_CHECKS)
    expect(problems, "header count", len(doc["headers"]), PINNED_HEADERS)


def check_known_at_rules(problems: list[str]) -> None:
    mod = load()
    row = [1, 1, 1]
    for ka, want in ((None, "unknown_availability"), (101, "future_knowledge"), (100, None), (99, None)):
        expect(problems, f"cause(ka={ka})", mod.cause({"row": row, "ka": ka}, (0,)), want)
    expect(problems, "forming slot", mod.cause("forming", (0,)), "future_market")
    expect(problems, "null needed field", mod.cause([1, None, 1], (1,)), "null_field")
    expect(problems, "null unneeded field", mod.cause([1, None, 1], (0, 2)), None)


def check_contracts(problems: list[str], doc: dict[str, Any]) -> None:
    md = CONTRACT_MD.read_text(encoding="utf-8")
    for h in doc["headers"]:
        if not UNIT.match(h["unit"]):
            problems.append(f"{h['id']}: unit {h['unit']!r} is not an E9 slash-style unit")
        sides = (("input_contract", ("fields", "grain", "adjustment", "session", "history_depth", "min_samples", "adapter_must")),
                 ("output_contract", ("value_type", "unit", "basis_echo", "unavailable_rules", "refusals")))
        for side, keys in sides:
            block = h.get(side) or {}
            for key in keys:
                if not str(block.get(key, "")).strip():
                    problems.append(f"{h['id']}: {side}.{key} is empty")
        if h["id"] not in md:
            problems.append(f"{h['id']} missing from the contract md")
    if BANNED.search(json.dumps(doc) + md):
        problems.append("performance wording found in the contract")
    if not doc["status"].startswith("draft, NOT frozen"):
        problems.append("status is not draft / not frozen")
    if "internal, synthetic, pre-release" not in doc["status"] + md:
        problems.append("posture wording 'internal, synthetic, pre-release' missing")


def check_coverage(problems: list[str], doc: dict[str, Any]) -> None:
    seen: dict[str, set[str]] = {h["id"]: set() for h in doc["headers"]}
    conventions: set[str] = set()
    for key in LISTS:
        for fx in doc[key]:
            for w in fx.get("wrong_convention", []):
                conventions.add(w["convention"])
                seen[w["output"]].add("wrong_convention")
            for name, res in fx["expected"].items():
                if res["status"] != "available":
                    seen[name].add("unavailable")
                else:
                    seen[name].add("positive")
                    if name in SIGNED and res["value"]["float64"] < 0:
                        seen[name].add("negative")
    for name, kinds in seen.items():
        need = {"positive", "unavailable", "wrong_convention"} | ({"negative"} if name in SIGNED else set())
        if not need <= kinds:
            problems.append(f"{name}: fixtures missing kinds {sorted(need - kinds)}")
    missing = REQUIRED_CONVENTIONS - conventions
    if missing:
        problems.append(f"wrong-convention fixtures missing for {sorted(missing)}")
    reasons = json.dumps([fx["expected"] for key in LISTS for fx in doc[key]])
    for reason in ("unknown_availability", "future_knowledge", "insufficient_history", "zero_denominator", "governed_gap",
                   "future_market", "absent_input", "null_field", "no_eligible_observations", "partial_universe", "ineligible"):
        if f'"{reason}"' not in reasons:
            problems.append(f"no fixture exercises {reason}")
    for fx in (f for key in LISTS for f in doc[key]):
        for name, res in fx["expected"].items():
            if (res["status"] == "available") != (res["value"] is not None):
                problems.append(f"{fx['id']} {name}: value null exactly when not available is violated")
            if res["status"] != "available" and (not res["reasons"] or res["witnesses"]):
                problems.append(f"{fx['id']} {name}: unavailable needs a reason and no witnesses")
            v = res["value"]
            if v and "acceptance" in v and v["acceptance"] == "tolerance":
                problems.append(f"{fx['id']} {name}: tolerance acceptance is not allowed in DV1")


def check_fail_closed(problems: list[str], doc: dict[str, Any]) -> None:
    drivers = doc["fail_closed_drivers"]
    refusals = {r["id"]: r for r in doc["refusal_fixtures"]}
    for key in ("undeclared_coverage", "missing_parameters", "missing_adjustment"):
        if not drivers[key]:
            problems.append(f"fail-closed driver {key} is empty")
        for rid in drivers[key]:
            if rid not in refusals:
                problems.append(f"fail-closed driver {rid} is not a refusal fixture")
            elif key != "undeclared_coverage" and refusals[rid]["error_code"] != "INVALID_CONFIG":
                problems.append(f"fail-closed driver {rid} is not INVALID_CONFIG")
    ids = {fx["id"]: fx for key in LISTS for fx in doc[key]}
    for fid in drivers["known_at"]:
        if not any(r["status"] != "available" and r["value"] is None for r in ids[fid]["expected"].values()):
            problems.append(f"{fid}: known_at driver yields no unavailable output")


def check_deprecation(problems: list[str], doc: dict[str, Any]) -> None:
    dep = doc["deprecation"]
    if "RANGE of core returns (deprecated name)" not in dep["wording"]:
        problems.append("deprecation wording missing")
    for fid in dep["equal_value_fixtures"]:
        fx = next(f for f in doc["core_spread_fixtures"] if f["id"] == fid)
        if "ef4_reference" not in fx:
            problems.append(f"{fid}: no EF4 reference")
    errata = (ROOT / "docs" / "ef4" / "EF4_ERRATA.md").read_text(encoding="utf-8")
    if "core.benchmark_return_dispersion_fraction" not in errata or "deprecated" not in errata:
        problems.append("EF4 errata entry for the deprecated id missing")


def check_frozen_files(problems: list[str]) -> None:
    """No EF1-EF5 file other than the 4-line EF4 erratum differs from origin/main (skipped without git or origin/main)."""
    def git(*args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=False)
    if git("rev-parse", "--verify", "origin/main").returncode != 0:
        print("SKIP frozen-file check: no origin/main in this checkout")
        return
    changed = git("diff", "--name-only", "origin/main", "--", "docs/ef1", "docs/ef2", "docs/ef3", "docs/ef4", "docs/ef5").stdout.split()
    extra = [f for f in changed if f != "docs/ef4/EF4_ERRATA.md"]
    if extra:
        problems.append(f"frozen EF1-EF5 files differ from origin/main: {extra}")
    if "docs/ef4/EF4_ERRATA.md" in changed:
        stat = git("diff", "--numstat", "origin/main", "--", "docs/ef4/EF4_ERRATA.md").stdout.split()
        if stat[:2] != ["4", "0"]:
            problems.append(f"EF4_ERRATA.md must be a 4-line addition only, got {stat[:2]}")


def main() -> int:
    doc = json.loads(CONTRACT.read_text(encoding="utf-8"))
    problems: list[str] = []
    check_expander(problems, doc)
    check_known_at_rules(problems)
    check_contracts(problems, doc)
    check_coverage(problems, doc)
    check_fail_closed(problems, doc)
    check_deprecation(problems, doc)
    check_frozen_files(problems)
    for line in problems:
        print("MISMATCH", line)
    print("DV1 fixtures (log beta/correlation, simple-mean ATR, core spread, range over open, window extremes): "
          + ("expander matched, counts pinned, input/output contracts and wrong-convention coverage hold" if not problems
             else f"{len(problems)} problem(s)"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
