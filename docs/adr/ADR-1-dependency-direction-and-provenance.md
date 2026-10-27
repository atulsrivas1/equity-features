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

Rule: package dependencies follow core <- io <- workers. Add a manual boundary check (script under `tools/`, run by hand per the no-automated-tests policy) that parses every `pyproject.toml` and import statement across the three repos and fails on an upward edge.

## Migration steps and effort

1. (S) In workers: add `packages/provenance` by moving the source unchanged, keeping distribution name `equity-feature-provenance` and import name `equity_feature_provenance` so downstream users change nothing.
2. (S) Trim its pins to what it consumes. Make duckdb and duckdb-sink an extra (`[duckdb]`) if the binding path allows optional sink use; otherwise keep as hard deps.
3. (S) In core: delete `packages/provenance`; add a tombstone note in `docs/CHANGELOG.md` and `docs/INSTALLING.md` pointing to the new home. Do not publish a stub that re-imports workers.
4. (S) Fix links in docs that mention provenance (`docs/api/ACQUISITION_PLANNING.md`, `DUCKDB_CONFORMANCE.md`, `DUCKDB_EVIDENCE.md`).
5. (S) Manual verification: fresh venv, install core, then io, then workers plus provenance; run the existing provenance synthetic example; confirm core installs with no io or workers present.
6. (XS) Add the boundary check and record its run.

Total effort: about 1.5 to 2 days including verification and independent review. Risk: external users pinned to the old repo layout; mitigated by unchanged distribution and import names. History: plain copy with a pointer to the original commit in the first workers commit message (or a filtered subtree if the owner wants history).

## Consequences

Core and io become releasable without workers. The workers repo gains one package and release cadence.
