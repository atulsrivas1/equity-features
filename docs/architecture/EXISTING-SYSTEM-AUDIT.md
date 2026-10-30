# Existing system audit (Release 0)

Internal, synthetic, pre-release. Architect, 2026-10-30. Decided, pending owner review; not accepted. Basis as in [SYSTEM-DESIGN.md](SYSTEM-DESIGN.md): core 685594e, io 3c94be6, workers 6c3123c (origin/main). States: current, stale (fix), missing. Retire/reuse/rewrite is a recommendation.

## Per area

| Area | State | Evidence | Action |
|---|---|---|---|
| ADR-1 layering, provenance in workers | current | `provenance` 0.1.0a5 is in workers; absent from core packages; `tools/check_boundary.py` exists | reuse |
| ADR-1 `docs/adr/ADR-1` text | stale (fix) | still says provenance is in core and recommends moving it | mark implemented |
| ADR-2 pinning | missing (not implemented) | every sibling pin on all three mains is `==` (e.g. workers pins `equity-features==0.0.4a7`, provenance pins six siblings exactly) | PO/owner to rule; keep exact pins meanwhile |
| ADR-2 listed mismatches | stale (fix) | the a15/a23/a8 mismatches no longer match current versions; the sampled pins on main agree | refresh the table |
| Pin consistency (sampled) | current | io, workers pins on main agree with core 0.0.4a6/a7 | none |
| `tools/_versions.py` SIBLINGS in core | stale (fix) | lists io-contracts a3, duckdb a11, workers a17, io commit 94217cf, workers 99b5fed; mains are a5, a12, a18, 3c94be6, 6c3123c. Core re-pin PR is handoff step 2 | re-pin PR |
| `docs/COMPATIBILITY.md` | stale (fix) | newest sections are R17/EQ-era checkpoints; no current-state table for a6/a7 | add table (ADR-2 point 2) |
| ADR-3 capability matrix | missing | `docs/matrix/` absent; matrix lives in git-ignored `work/` | build per ADR-3 |
| ADR-4 entry-point discovery | missing | no entry-points table in any io/workers `pyproject.toml`; `load_entry_points` not found | build per ADR-4 |
| Registries, factories, sink protocol | current | io-sdk `SourceRegistry`/`SinkRegistry`, `ResultSink` in io-contracts | reuse |
| Sinks (duckdb-sink, parquet) | current | packages present | reuse |
| Source adapters (duckdb per family, files) | current for EF1-EF5; missing for DV1 | `price_structures.py` present; no dv1 adapter module found in io | DV1 io lane |
| Workers per family | current EF1-EF5 (`equity_ef5.py`); missing DV1 | no dv1 worker module found | DV1 workers lane |
| Catalogue pages (io `docs/contracts/catalogue/`) | current EF5; missing DV1 | `ef5.*` present, no dv1 | handoff step 4 (io-contracts a5 -> a6) |
| Coverage table CV1-CV6 | missing | only CV0 seed in core `docs/plans/design-coverage-map.json` | handoff step 5 |
| DV1 core library | current, closeout open | `packages/features/.../dv1`, `docs/dv1/`; manifest flip, freeze text, second-author recompute pending (handoff) | finish C4 |
| EF5 | current (library, io, workers) | core `docs/ef5/` frozen 2026-10-29; services/MCP exposure `ef5.*` missing | backlog |
| Core `docs/` size and history | stale | 100+ files, many release-era plans (R1-R26) and snapshots | do not edit; index only, retire nothing without PO |
| Local sibling checkouts | stale | io on a feature branch; workers pre-bump | developers use fresh worktrees |
| `STATUS.md` | stale | newest entry 2026-10-24 (EF4) | coordinator refresh |
| Release gate tooling | current | `tools/pre_merge_check.py`, `check_boundary`, `verify_*` | reuse |
| Live/continuous intraday | current as Backlog | direction decision only | none |

## Open contract items E1-E9 (status only; owner decides)

Source: DECISIONS.md 2026-10-27/28, `docs/ef4/EF4_ERRATA.md`. All nine are "applied, pending owner ratification"; none is owner-confirmed. PO-1..PO-7 (EF5) are PO-ruled and likewise pending owner ratification.

| Item | Status |
|---|---|
| E1 TopKTrades order check, notional cells | applied; same-version notional cells accepted with compatibility note; owner pending |
| E2 coverage form, undeclared coverage | applied; tape adapter fails closed (INVALID_SCHEMA), library half via `governed_gap` (DP-T12); owner pending |
| E3 REFERENCE evidence boundary | applied; owner pending |
| E4 `governed_history` N <= 63 | applied; owner pending |
| E5 I1 path efficiency hosted in `intraday` | applied; owner preference pending |
| E6 refusal label errata (RF18, RF35) | errata table in `EF4_ERRATA.md`; frozen files unedited; owner pending |
| E7 tape per-output `evidence_limit` | applied; owner pending |
| E8 top-K merge shared config | nine tape refusal recipes library-only, no worker path; owner pending |
| E9 unit spellings | slash style canonical; four aliases rejected on new headers; migration of 5 headers deferred to a contract-version boundary; the DV1 bump (a6) may have been that boundary: **not verified** |

## Not verified

Core packages other than `features`/`intraday` internals; whether the in-memory sink exists in io-sdk; the E9 migration state after the a6 bump; remote client notional-cell decode fix; workers `provenance` behavior.
