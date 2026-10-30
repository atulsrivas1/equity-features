# Existing system audit (Release 0)

Internal, synthetic, pre-release. Architect, 2026-10-30. Decided, pending owner review; not accepted. Basis: core 685594e (this checkout); io 3c94be6 and workers 6c3123c read through the GitHub contents and tree API (branch main); paths below are inside those repos. All four ADRs are 'proposed, pending owner review'. States: current, stale (fix), missing. Retire/reuse/rewrite is a recommendation.

## Per area

| Area | State | Evidence | Action |
|---|---|---|---|
| ADR-1 layering, provenance in workers | implemented, unratified (ADR status is proposed, pending owner review) | workers `packages/provenance/pyproject.toml` (0.1.0a5); no `provenance` under core `packages/`; core `tools/check_boundary.py` | reuse |
| ADR-1 `docs/adr/ADR-1` text | stale (fix) | context still says provenance is in core and recommends moving it (`docs/adr/ADR-1-dependency-direction-and-provenance.md`) | mark implemented, keep status proposed |
| ADR-2 pinning | missing (not implemented) | every sibling pin is `==`: workers `packages/workers/pyproject.toml` pins `equity-features==0.0.4a7`; workers `packages/provenance/pyproject.toml` pins contracts, evidence, workers, io-contracts, io-sdk, duckdb exactly | PO/owner to rule; keep exact pins meanwhile |
| ADR-2 text, in full | stale (fix) | its whole verified-state section is out of date: version list (contracts a4, workers a15, io a2, duckdb a9, core a5) and all six mismatch rows (a15/a23/a8 etc.) predate current mains (core `tools/_versions.py`, io and workers `pyproject.toml` files). The policy decision itself is unratified | rewrite the context section from current files; keep status proposed |
| Pin consistency (sampled) | current | io `packages/io-contracts/pyproject.toml` and `packages/duckdb/pyproject.toml` pin contracts 0.0.4a6; io `packages/bundles/pyproject.toml` pins features 0.0.4a7; workers `packages/client/pyproject.toml` pins contracts 0.0.4a6 | none |
| `tools/_versions.py` SIBLINGS in core | stale (fix) | lists io-contracts a3, duckdb a11, workers a17, io commit 94217cf, workers 99b5fed; mains are io-contracts a5 (io `packages/io-contracts/pyproject.toml`), duckdb a12 (`packages/duckdb/pyproject.toml`), workers a18 (workers `packages/workers/pyproject.toml`), commits 3c94be6 and 6c3123c (GitHub commits API, branch main). Core re-pin PR is handoff step 2 | re-pin PR |
| `docs/COMPATIBILITY.md` | stale (fix) | newest sections are R17/EQ-era checkpoints; no current-state table for a6/a7 | add table (ADR-2 point 2) |
| ADR-3 capability matrix | missing | no `docs/matrix/` in core (checked in this checkout); matrix lives in the ignored `work/` (core `.gitignore`) | build per ADR-3 |
| ADR-4 entry-point discovery | missing | no `entry-points` table in any io or workers `pyproject.toml` (all 15 scanned); no `load_entry_points` in io `packages/io-sdk/src/equity_feature_io_sdk/factories.py` | build per ADR-4 |
| Registries, factories, sink protocol | current | `SourceRegistry`/`SinkRegistry` in io `packages/io-sdk/src/equity_feature_io_sdk/factories.py`; `ResultSink` in io `packages/io-contracts/src/equity_feature_io_contracts/publication.py` | reuse |
| Sinks (duckdb-sink, parquet) | current | io `packages/duckdb-sink/src/equity_feature_duckdb_sink/sink.py`, `packages/parquet/src/equity_feature_parquet/sink.py` | reuse |
| Source adapters (duckdb per family, files) | current for EF1-EF5; missing for DV1 | io `packages/duckdb/src/equity_feature_duckdb/price_structures.py` present; no `dv1` path in the io main file tree (522 files) | DV1 io lane |
| Workers per family | current EF1-EF5 (`equity_ef5.py`); missing DV1 | no `dv1` path in the workers main file tree (640 files); EF5 is `packages/workers/src/equity_feature_workers/equity_ef5.py` | DV1 workers lane |
| Catalogue pages (io `docs/contracts/catalogue/`) | current EF5; missing DV1 | io `docs/contracts/catalogue/ef5.candle`, `ef5.structure`, `ef5.technical` present; no `dv1` catalogue directory | handoff step 4 (io-contracts a5 -> a6) |
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
