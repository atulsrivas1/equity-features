# System design: map (Release 0)

Internal, synthetic, pre-release. Architect, 2026-10-30. Decided, pending owner review; the PO accepts. This file is a map to existing authorities. It links rather than restates; new content is marked NEW. Per-area state is in [EXISTING-SYSTEM-AUDIT.md](EXISTING-SYSTEM-AUDIT.md).

Verification basis: core main 685594e (this checkout); io 3c94be6 and workers 6c3123c read from `origin/main` via the GitHub API (local sibling checkouts are stale: io sits on branch `docs/ef4-c3-parquet-roundtrip`). **[not verified]** marks anything not opened.

## Authorities

| Topic | Authority (edit there, not here) |
|---|---|
| Layering core <- io <- workers, provenance placement | `docs/adr/ADR-1`; checked by `tools/check_boundary.py` |
| Pins, compatibility | `docs/adr/ADR-2`, `docs/COMPATIBILITY.md`, `docs/VERSIONING.md`, `tools/_versions.py`, each repo's `tools/verify_versions.py` |
| Capability matrix, compute location | `docs/adr/ADR-3` (target `docs/matrix/`, absent) |
| Adapter/sink registration | `docs/adr/ADR-4`; io `docs/api/FACTORIES.md`; core `docs/IO_FACTORIES.md` |
| Sink contract, publication records | `docs/IO_PUBLICATION_V1.md`, `docs/decisions/IO_PUBLICATION_V1.md`, `docs/IO_PUBLICATION_API.md` |
| io/workers split | `docs/IO_WORKER_ARCHITECTURE.md`, `docs/decisions/IO_REPOSITORY_SEPARATION.md`, `docs/PACKAGE_LAYOUT.md` |
| Feature contracts and refusals | `docs/ef1`..`ef5`, `docs/dv1` (frozen text); io catalogue `docs/contracts/catalogue/` |
| Live/intraday direction | `docs/decisions/LIVE_INTRADAY_ARCHITECTURE_DIRECTION.md` (Backlog) |
| Process and gates | `docs/playbook/ADOPTION.md`, `docs/COORDINATOR_WORKING_AGREEMENT.md` |
| Assumptions | `DECISIONS.md` (append-only) |

## Components

Versions live in each `pyproject.toml` (core `packages/*`, io and workers `packages/*` on main) and `tools/_versions.py`; they are not repeated here. Core: contracts, features (pure libraries, `ef1`..`ef4`, `dv1`), intraday (EF5), evidence and related. io: io-contracts (ports, records), io-sdk (registries, admission, conformance), adapters `duckdb` and `files`, sinks `duckdb-sink` and `parquet`, `acquisition`, `bundles`. workers: workers (manifests, planning, supervisor), provenance, service, client, mcp.

## Flow

source -> source adapter (io) -> workers (plan, TaskManifest, supervisor) -> library (core, pure) -> FeatureResult -> sink (io) -> CompletionReceipt -> provenance report. Adapters and sinks are the only conversion points; libraries never touch storage, clock or vendors. Data placement: inputs in the data-generating process's store behind an adapter or supplied by the caller; results in a sink; manifests and receipts in workers/provenance.

## Ports and mock/synthetic per port (NEW: no single table existed)

| Port | Protocol (io-contracts) | Real | Mock / synthetic |
|---|---|---|---|
| Source | `ComponentFactory` + `SourceCandidate.capabilities()` | `duckdb`, `files` | contract fixtures (`tools/contract_fixtures`), supplied batches, io `examples/factory_consumer` |
| Sink | `ResultSink` (`begin/write/commit/abort/lookup/read`) | `duckdb-sink`, `parquet` | in-memory test sink **[not verified]**; pass bar is `qualify_sink` |
| Credentials | `CredentialProvider.get` | none shipped | none needed |
| Transport | service job API, MCP | `service`, `mcp` | `tools/remote_transport_reference.py` |

## Pin discipline (NEW: one list, from DV1 practice)

1. One coordinated pre-release bump per chain, then a re-pin PR per downstream repo with its own three reviews. 2. Merge upstream first; re-pin after every squash merge. 3. Run every builder whose pin moves (core `SIBLINGS`/`SIBLING_COMMITS`; workers `WORKER_COMMIT`, `SERVICE_COMMIT`, `CLIENT_COMMIT`). 4. `verify_versions` in all three repos plus `tools/pre_merge_check.py`. 5. Frozen contract text is never edited; changes are a new contract version.

## Architecture review checks

Upward import edge; library touching storage, clock or vendor; conversion outside an adapter or sink; config able to cause import; sibling pin mismatch; edit of a frozen contract; capability row missing its field groups.
