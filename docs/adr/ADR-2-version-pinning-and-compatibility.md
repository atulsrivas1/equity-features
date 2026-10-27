# ADR-2: Version pinning and compatibility policy

Status: proposed (decided, pending owner review). Date: 2026-10-27.

## Context: verified state

Read from every `pyproject.toml` in the three sibling repos (all on main, 2026-10-27). Everything is pinned with `==`, including the build backend (`setuptools==80.9.0`) and third-party libraries (`duckdb==1.5.6`, `pyarrow==20.0.0`, `numpy==2.2.6`).

Current versions: equity-features 0.0.4a5; contracts 0.0.4a4; evidence 0.1.0a2; explanations 0.1.0a2; io-contracts and io-sdk 0.1.0a2; duckdb 0.1.0a9; duckdb-sink 0.1.0a0; workers 0.1.0a15; service 0.1.0a3; intraday 0.1.0a3.

| Reported mismatch | Verdict | Evidence |
|---|---|---|
| workers pins equity-features==0.0.4a5 | Not a mismatch | features package is 0.0.4a5 |
| bundles pins core 0.0.4a4 | REAL | `bundles[replay]` pins `equity-features==0.0.4a4`; current is 0.0.4a5. Extra only, so the base install is unaffected, but the extra conflicts with workers |
| service pins workers a23 vs package a15 | REAL and unsatisfiable | `service[jobs]` pins `equity-feature-workers==0.1.0a23`; workers is 0.1.0a15, so that extra cannot install |
| duckdb a8 vs a9 | REAL | `service[duckdb]` pins `equity-feature-duckdb==0.1.0a8`; package is 0.1.0a9 (provenance correctly pins a9) |
| docs/COMPATIBILITY.md says a14 | REAL, partly historical | the R17 paragraph states workers 0.1.0a14; current is a15. The file keeps older checkpoints as history by design but has no current-state table |
| new finding: mcp[evidence] pins explanations 0.1.0a1 | REAL | package is `equity-feature-explanations` 0.1.0a2 |

All the real mismatches are in optional extras, which is why they went unnoticed: nothing installs every extra. Provenance's dependency on workers is covered in ADR-1.

## Decision

1. Policy by dependency kind:
   - Qualified release set (what we install and test together): exact `==` pins recorded in one lock file, as today.
   - Library-to-sibling-library metadata (core <- io <- workers): compatible ranges inside an epoch, for example `equity-feature-contracts>=0.0.4a4,<0.0.5`. Exact sibling pins turn every upstream bump into a three-repo cascade, which is the root cause of the mismatches.
   - Third-party runtime libraries (duckdb, pyarrow, numpy): exact in the lock file; in library metadata, exact until qualification proves a range.
   - Build backend pin stays exact (reproducible archives are a stated qualification property).
2. Single source of truth: `docs/COMPATIBILITY.md` gets a top "Current qualified set" table (distribution, version, repo, pins). A manual script `tools/check_pins.py` (run by hand, consistent with the no-automated-tests policy) reads all `pyproject.toml` files in the three repos and reports (a) any pin naming a version that is not the current version of that distribution, (b) any upward layer edge (ADR-1), (c) extras naming nonexistent versions, including extras. Run before each release and attach output to release evidence.
3. Fix the four real mismatches in the repos that own them, one small PR each: bundles `replay` to 0.0.4a5, service `jobs` to 0.1.0a15, service `duckdb` to 0.1.0a9, mcp `evidence` to explanations 0.1.0a2. This ADR PR does not edit those repos.
4. Stage the range change: land the checker, fix the four pins, then convert sibling pins to ranges one repo at a time with a fresh-install qualification run each.

## Consequences

Ranges let io and workers move independently inside an epoch, at the cost of qualifying range edges (lowest and highest) instead of one point. The lock file keeps exact reproducibility. Effort: checker half a day, pin fixes small, ranges medium per repo.
