# ADR-1: Dependency direction and where provenance lives

Status: proposed (decided, pending owner review). Date: 2026-10-27.

## Context

Intended layering is `core (equity-features repo) <- io (equity-feature-io) <- workers (equity-feature-workers)`: a lower layer never imports a higher one.

Verified in `packages/provenance/pyproject.toml` (equity-feature-provenance 0.1.0a2, in the core repo): it pins and imports `equity-feature-workers==0.1.0a15`, `equity-feature-io-contracts==0.1.0a2`, `equity-feature-io-sdk==0.1.0a2`, `equity-feature-duckdb==0.1.0a9` and `equity-feature-duckdb-sink==0.1.0a0`. Imports in `_bind.py` and `_model.py` include `DuckDBSink`, `GenerationStore`, `TaskManifest`, `OutputManifest`, `AcquisitionReceipt`, `FeatureHeader` and `descriptor`.

This is a cycle at repo level: workers 0.1.0a15 pins `equity-features==0.0.4a5` (core), and core's provenance pins workers. A core bump forces a workers bump, which forces a provenance bump back in core.

Provenance (bind receipts, task manifests and acquisition receipts into a verifiable report) is inherently a cross-layer join, so it belongs with the highest layer it needs.

## Options

1. Leave in core. Rejected: keeps the inversion and the release cycle.
2. Move to the io repo. Rejected: it imports `equity_feature_workers`, and io must not depend on workers.
3. Move to the workers repo as `packages/provenance` (recommended). Workers already depends on core and io-sdk and owns the manifests provenance consumes.
4. Split: keep model types in core, move binding (`_bind`, `_preflight`) to workers. More precise but more churn; only worth it if a consumer needs the report types without workers.

## Decision

Option 3 now; revisit option 4 only if a consumer needs report types without workers.

Rule: package dependencies follow core <- io <- workers. Add a manual boundary check (script under `tools/`, run by hand per the policy of adding no new automated tests) that parses every `pyproject.toml` and import statement across the three repos and fails on an upward edge.

## Migration steps and effort

1. (S) In workers: add `packages/provenance` by moving the source unchanged, keeping distribution name `equity-feature-provenance` and import name `equity_feature_provenance` so downstream users change nothing.
2. (S) Trim its pins to what it consumes. Make duckdb and duckdb-sink an extra (`[duckdb]`) if the binding path allows optional sink use; otherwise keep as hard deps.
3. (S) In core: delete `packages/provenance`; add a tombstone note in `docs/CHANGELOG.md` and `docs/INSTALLING.md` pointing to the new home. Do not publish a stub that re-imports workers.
4. (S) Move or rewrite the remaining core consumers (found by grep of `provenance` in the core repo; each is a disposition, not an assumption):
   - `tests/provenance/*` (`native_fixture.py`, `provenance_fixture.py`, `test_bounds.py`, `test_native.py`, `test_supplied.py`): move to workers with the package (they import provenance, workers and io).
   - `examples/provenance_readback.py`: move to workers (it inserts `tests/provenance` on `sys.path` and calls `bind_supplied_provenance` / `verify_live_generation`).
   - `examples/conformance_pipeline.py`, `tests/conformance/test_pipeline.py` and `tests/conformance/native_composition.py`: these use provenance together with conformance, so they are cross-layer. Move to workers (conformance is a core package and stays an allowed downward dependency). Core keeps conformance tests that need only core.
   - `tools/build_provenance.py`, `tools/build_conformance.py`, `tools/build_r10.py`, `tools/ci_gate.py`, `tools/verify_quickstart.py`, `tools/check_boundary.py`: audit each reference; provenance build logic moves to workers, core builders drop provenance from the installed set or keep it only as an absence check.
   - `tools/build_agent_evidence.py` and `tools/build_agent_ledger.py`: verified they only list `equity_feature_provenance` among modules asserted absent in a clean environment (`find_spec(...) is None`); they do not need provenance, so no upward dependency exists. They need only the list entry kept (still correct after the move).
   - Other `examples/ef1_*.py`, `examples/session_top_k.py` and `tests/unit/test_ef1_*`, `tests/intraday/test_admission.py`, `test_quotes.py`: grep hits to review; expected to be incidental wording, rewritten only if they import provenance.
   - Fix doc links (`docs/api/ACQUISITION_PLANNING.md`, `DUCKDB_CONFORMANCE.md`, `DUCKDB_EVIDENCE.md`).
5. (S) Manual verification. Core: fresh venv, install core packages only (contracts, features, evidence, diagnostics, conformance, agent-evidence, agent-ledger), run the remaining core examples and tools, and assert `equity_feature_provenance`, `equity_feature_workers` and io modules are absent. This passes only after step 4 removes `examples/conformance_pipeline.py` and `tests/conformance/test_pipeline.py` from core, since they import provenance today. Then install io, then workers plus provenance, and run the moved provenance examples and tests.
6. (XS) Add the boundary check and record its run; it must also scan `examples/`, `tests/` and `tools/`, not only package metadata.

Total effort: about 2 to 3 days (consumer moves add about a day) including verification and independent review. Risk: external users pinned to the old repo layout; mitigated by unchanged distribution and import names. History: plain copy with a pointer to the original commit in the first workers commit message (or a filtered subtree if the owner wants history).

## Consequences

Core and io become releasable without workers. The workers repo gains one package and release cadence.
