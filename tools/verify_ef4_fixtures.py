"""Gate for the EF4 frozen-contract fixtures (contracts G tape, H quote/VWAP, I1 path efficiency, I2 projections).

Runs the three stdlib fixture expanders in `tools/contract_fixtures/` as subprocesses, requires exit status 0 and the
documented success line, and requires the fixture and refusal counts they report to equal the counts declared in each
contract JSON (`fixture_counts`). It then pins the known_at semantics the contracts define (null known_at is
`unknown_availability`, known_at > K is `future_knowledge`, known_at == K is available) against the expanders'
own readiness helpers, and requires every contract to carry fixtures that exercise both quality reasons.
Run from a source checkout: `python tools/verify_ef4_fixtures.py`; exit status 0 only if everything holds.
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
DOCS = ROOT / "docs" / "ef4"
HELPERS = ROOT / "tools" / "contract_fixtures"
K = 100


def contract(name: str) -> dict[str, Any]:
    return json.loads((DOCS / f"{name}_CONTRACT_PROPOSAL.json").read_text(encoding="utf-8"))


def run(script: str) -> tuple[int, str]:
    done = subprocess.run([sys.executable, "-I", str(HELPERS / script)], cwd=ROOT, capture_output=True, text=True,
                          check=False)
    return done.returncode, done.stdout + done.stderr


def load(script: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(script[:-3], HELPERS / script)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def numbers(pattern: str, text: str) -> list[int] | None:
    found = re.search(pattern, text)
    return [int(g) for g in found.groups()] if found else None


def expect(problems: list[str], label: str, got: Any, want: Any) -> None:
    if got != want:
        problems.append(f"{label}: got {got!r} want {want!r}")


def check_expanders(problems: list[str]) -> None:
    g, h, i1, i2 = (contract(n) for n in ("TAPE", "QUOTE_VWAP", "PATH_EFFICIENCY", "PATH_PROJECTIONS"))
    for script, tail in (("ef4g_fixture_expand.py", "OK: every fixture recomputed and matched"),
                         ("ef4h_fixture_expand.py", "ALL FIXTURES MATCH THE INDEPENDENT RECOMPUTE"),
                         ("ef4i_fixture_expand.py", "ALL FIXTURES AND REFUSALS RECOMPUTED AND MATCHED")):
        code, out = run(script)
        expect(problems, f"{script} exit status", code, 0)
        if tail not in out:
            problems.append(f"{script}: success line {tail!r} missing")
        if script.startswith("ef4g"):
            c = g["fixture_counts"]
            want = [c["window_result"], c["topk_result"], c["merge_result"], c["generator"], c["refusal"]]
            expect(problems, "G window/topk/merge/generator/refusal",
                   numbers(r"window=(\d+) topk=(\d+) merge=(\d+) generator=(\d+) refusal=(\d+)", out), want)
        elif script.startswith("ef4h"):
            c = h["fixture_counts"]
            expect(problems, "H quote/vwap/refusal",
                   numbers(r"quote fixtures (\d+), vwap fixtures (\d+), refusal fixtures (\d+) "
                           r"\(recipes applied and verified: \d+\)", out), [c["quote_result"], c["vwap_result"], c["refusal"]])
            applied = numbers(r"refusal fixtures \d+ \(recipes applied and verified: (\d+)\)", out)
            expect(problems, "H refusal recipes applied", applied, [c["refusal"]])
        else:
            a, b = i1["fixture_counts"], i2["fixture_counts"]
            expect(problems, "I1 result/refusal", numbers(r"I1 path efficiency: (\d+) result fixtures \(\d+ outputs\), "
                                                           r"(\d+) refusal", out), [a["path_result"], a["refusal"]])
            results = sum(v for k, v in b.items() if k != "refusal")
            expect(problems, "I2 result/refusal", numbers(r"I2 projections: (\d+) result fixtures \(\d+ outputs\), "
                                                           r"(\d+) refusal", out), [results, b["refusal"]])


def check_known_at_rules(problems: list[str]) -> None:
    gm, hm, im = load("ef4g_fixture_expand.py"), load("ef4h_fixture_expand.py"), load("ef4i_fixture_expand.py")
    probes = ((None, "unknown_availability"), (K + 1, "future_knowledge"), (K, None), (K - 1, None))
    for ka, want in probes:
        expect(problems, f"G know_reason({ka})", gm.know_reason(ka, K), want)
        expect(problems, f"H knowledge_reason({ka})", hm.knowledge_reason(ka, K), want)
        expect(problems, f"I classify_slot({ka})", im.classify_slot({"row": [1], "ka": ka}, K)[0], want)
        expect(problems, f"I fact_state({ka})", im.fact_state({"ka": ka}, K), want)
    expect(problems, "G reconstruction mode ignores known_at", gm.know_reason(None, K, "reconstruction"), None)


def check_reason_coverage(problems: list[str]) -> None:
    for name in ("TAPE", "QUOTE_VWAP", "PATH_EFFICIENCY", "PATH_PROJECTIONS"):
        doc = contract(name)
        fixtures = [f for key, rows in doc.items() if key.endswith("_fixtures") and key != "refusal_fixtures"
                    and isinstance(rows, list) for f in rows if isinstance(f, dict)]
        for reason in ("unknown_availability", "future_knowledge"):
            hits = sum(reason in json.dumps(f) for f in fixtures)
            if not hits:
                problems.append(f"{name}: no result fixture exercises {reason}")


def check_errata(problems: list[str]) -> None:
    """The additive errata recipes (E1, E2, E4): the frozen contract refusal counts stay and the errata list is whole.

    Frozen refusal censuses: tape 75, quote/VWAP 80, path efficiency 39, projections 114; plus 11 errata recipes that
    `verify_ef4_errata.py` runs against the library (it is run by the pre-merge command with the other verify scripts).
    """
    errata = json.loads((DOCS / "EF4_ERRATA_RECIPES.json").read_text(encoding="utf-8"))
    frozen = {"tape_refusal": contract("TAPE")["fixture_counts"]["refusal"],
              "quote_vwap_refusal": contract("QUOTE_VWAP")["fixture_counts"]["refusal"],
              "path_refusal": contract("PATH_EFFICIENCY")["fixture_counts"]["refusal"],
              "projections_refusal": contract("PATH_PROJECTIONS")["fixture_counts"]["refusal"]}
    expect(problems, "frozen refusal counts", frozen, errata["contract_counts_unchanged"])
    ids = [r["id"] for r in errata["recipes"]]
    expect(problems, "errata recipe count", errata["recipe_count"], len(ids))
    expect(problems, "errata ids unique", len(set(ids)), len(ids))
    expect(problems, "errata recipes", len(ids), 11)


def main() -> int:
    problems: list[str] = []
    check_expanders(problems)
    check_errata(problems)
    check_known_at_rules(problems)
    check_reason_coverage(problems)
    for line in problems:
        print("MISMATCH", line)
    print("EF4 fixtures (G, H, I1, I2): " + ("all expanders matched, known_at rules hold" if not problems
                                              else f"{len(problems)} problem(s)"))
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
