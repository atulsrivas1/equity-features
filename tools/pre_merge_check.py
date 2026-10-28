"""One documented pre-merge command for the core repo (no CI exists; this is run by hand).

Runs, with the current interpreter and from the core root: check_boundary, check_equity_delivery_replan, and every
tools/verify_*.py (including verify_ef4_fixtures). Prints PASS/FAIL/SKIP per check and exits 0 only if nothing failed.
It then prints, without running them, the manual commands for the sibling repos (io check_extraction and mypy, the
workers EF4 refusal drivers), which need the sibling checkouts and an environment with the io and workers packages.
Use the pinned venv from CONTRIBUTING.md (requirements-dev.txt plus the editable core packages).

SKIPs: three checks need an installed (non-editable) environment, the io wheels or jsonschema (checklist 2.2) and run
only with --installed. verify_quickstart refuses to overwrite its scratch folder work/eq132-quickstart-Windows (by
design), so it is skipped when that folder exists; delete the ignored folder to rerun it.
Usage: python tools/pre_merge_check.py [--only SUBSTRING] [--installed]
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TOOLS = ROOT / "tools"
INSTALLED_ONLY = {"verify_public_typing.py", "verify_remote_transport.py", "verify_supplied_worker_examples.py"}
QUICKSTART_SCRATCH = ROOT / "work" / "eq132-quickstart-Windows"

MANUAL = r"""Manual checks (not run here; run in the sibling repos with the same pinned interpreter; record results in the PR):
  io      : python tools/check_extraction.py --core-root <core>     (in ..\equity-feature-io)
  io      : python -m mypy --strict packages/duckdb/src               (in ..\equity-feature-io; examples/ has 2 known errors)
  workers : set EF4G_HARNESS, EF4H_HARNESS, EF4I_HARNESS to core tools/contract_fixtures/*, then in ..\equity-feature-workers:
            python examples/ef4_tape.py --refusals             (baseline 73/75: RF18 and RF35 ruled E6; the 9 merge refusals are library-only, E8)
            python examples/ef4_quote_vwap.py --refusals       (baseline 80/80)
            python examples/ef4_path_efficiency.py --refusals  (baseline 39/39)
            python examples/ef4_projections.py --refusals      (baseline 114/114)
            result fixtures: each driver with --case <id> --output-db <abs> --html <abs>
  Release acceptance (not per PR): docs/qa/RELEASE_ACCEPTANCE_CHECKLIST.md."""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--only", default="", help="run only checks whose name contains this text")
    parser.add_argument("--installed", action="store_true", help="also run the checks needing installed wheels, io wheels, jsonschema")
    args = parser.parse_args()
    checks = ["check_boundary.py", "check_equity_delivery_replan.py"] + sorted(p.name for p in TOOLS.glob("verify_*.py"))
    results: list[tuple[str, bool]] = []
    for name in checks:
        if args.only and args.only not in name:
            continue
        if name in INSTALLED_ONLY and not args.installed:
            print(f"SKIP  {name}  (needs installed wheels / io wheels / jsonschema; use --installed)")
            continue
        if name == "verify_quickstart.py" and QUICKSTART_SCRATCH.exists():
            print(f"SKIP  {name}  (refuses to overwrite {QUICKSTART_SCRATCH.relative_to(ROOT)}; delete it to rerun)")
            continue
        proc = subprocess.run([sys.executable, str(TOOLS / name)], cwd=ROOT, capture_output=True, text=True)
        ok = proc.returncode == 0
        results.append((name, ok))
        print(f"{'PASS' if ok else 'FAIL'}  {name}")
        if not ok:
            print("\n".join("      " + line for line in (proc.stdout + proc.stderr).strip().splitlines()[-15:]))
    failed = [n for n, ok in results if not ok]
    print(f"\n{len(results) - len(failed)} of {len(results)} automated checks passed.\n")
    print(MANUAL)
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
