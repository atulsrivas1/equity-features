# EQ-049 — Pinned catalog/source resolution

[Issue56](https://github.com/atulsrivas1/equity-features/issues/56), R4/E07.
Estimate: **5 provisional story points**, reflecting generation/overlap resolution,
identity evidence, malformed catalogs and integration fixtures. No deadline implied.
Dependencies: accepted package release R3. Design starts after live prerequisite
readback; implementation and delivery remain pending.

## Start and boundary

Inspect accepted adapter protocols and actual catalog metadata read-only. Define
an optional adapter distribution outside contracts/calculations. The resolver
accepts caller-configured catalog locations, source family, one explicit generation
and bounded requested sessions. No autodiscovery of drives, latest-generation
fallback, provider access, output publication or historical job launch.

This story resolves source populations and evidence; canonical row mapping belongs
to EQ050 and batch acquisition to EQ051. Follow [R4 test strategy](../R4_TEST_STRATEGY.md).
No change to feature mathematics or existing canonical schema is planned.

## Proposed design to freeze before implementation

Use immutable selection and resolved-source records in the optional adapter.
Selection declares catalog identity, family, layer, snapshot/generation and requested
sessions. Resolution returns the exact selected partition population, original
and optimized identities where evidenced, schema identity, substitutions and
source admission state. Represent missing and observed-empty separately.

Accept one generation explicitly; reject ambiguous selections. Resolve overlapping
curated/prepared populations by the declared policy, never UNION both implicitly.
Missing provenance or hash evidence remains unknown/unverified, not fabricated.
Detect stale/malformed pins and schema conflicts with typed source errors before
claiming a complete acquisition. Stable per-file original row occurrence binding
does not itself prove provider execution uniqueness or exchange ordering.

Require caller-controlled, read-only catalog access and validated SQL identifiers
with bound selection values. Bound metadata result cardinality and requested
session count. Treat caller-owned local catalogs as trusted configuration, not an
untrusted remote SQL sandbox. Query/copy/resource behavior is measured in EQ051.

## Open decisions and source limits

Freeze exact public type names, source error mapping, metadata limits and optional
distribution name after inspecting the accepted source contract. Some legacy
catalogs do not embed original SHA256; define explicit external receipt binding
without treating paths/sizes as equivalent hashes. Preserve dataset substitutions
as first-class lineage. File-date availability and calendar completeness must not
be inferred. Actual-schema support and normalization choices belong to EQ050.

## Required tests

Temporary synthetic catalog/Parquet fixtures for an explicit valid generation;
ambiguous and missing selection; overlap without double counting; substitutions;
missing versus empty partitions; malformed schema/identifiers; changed file/receipt
pins; unknown admission/provenance; bounded metadata requests; read-only behavior.
Independently assert selected original identities and retained evidence. Existing
pure packages must still import and run without DuckDB installed.

Actual catalog inspection can inform this story, but does not substitute for EQ055
adapter-delivered real-row and numerical integration evidence. Keep paid data and
private infrastructure out of committed fixtures and documentation.

## Documentation and end state

Document the optional resolver API, selection policy, pin/receipt meanings, typed
errors, limits and unavailable capabilities. Keep issue/PR, source-mapping guide,
dependency boundaries and continuity current. Done means reviewed, tested and
installed/published source-resolution behavior with actual acceptance evidence;
not a complete R4 adapter, calculation proof or full-corpus admission.

## EQ049 concrete execution decisions — October 6, 2026

Prerequisite readback: R2/R3 milestones closed and EQ048/095 Done. Separate handoff review covered adc3837 with 633 local Windows units, strict49, mathematical references, policy and published-blob checks. Actual R3 downloaded twelve inner archives match both manifests; the Windows wheel consumer qualification/walkthrough runs outside source without DuckDB. Linux execution evidence is native CI, not local emulation. GOV013 publication acceptance is checked before pulling implementation.

The optional distribution is `equity-feature-duckdb`, import `equity_feature_duckdb`, starting experimental0.1.0a1. It depends inward only on contracts0.0.4a4 and DuckDB1.5.6; it does not make features depend on an adapter or alter core versions/math/schema. CPython3.12 Windows/Linux are the qualification targets. DuckDB is a tested pin rather than a broad compatibility promise. Pure packages retain their existing import/run gate with DuckDB forbidden.

Public frozen records and call:

- `CatalogConfig(path, expected_sha256=None, max_sessions=366, max_files=4096, max_hash_bytes=1073741824)`: explicit absolute caller-owned local catalog path; optional catalog content pin; positive validated limits. No drive discovery or latest fallback.
- `SourceSelection(layer, snapshot, dataset, source_schema, sessions, expected_schema_sha256=None)`: curated/prepared; one explicit snapshot/dataset and trades/tbbo/ohlcv-1m/ohlcv-1d; concrete unique ISO dates. Dates are partition selections, not governed trading sessions.
- `FilePin(original_path, original_sha256=None, optimized_sha256=None, receipt_id=None)`: external caller-supplied receipt assertions bound by exact original path; any asserted content hash is independently checked against that selected file. Receipt identity is not authentication. No hash is inferred from path/size/parity/provenance.
- `resolve_source(config, selection, *, pins=(), cancellation=None) -> ResolvedSource`: owned immutable selected partitions, missing dates, declared zero-row dates, original/optimized paths/sizes/hashes, schema signature identity, substitutions and unchanged admission text; actual catalog SHA256 and deterministic selection digest. It resolves metadata, not canonical row acquisition or completeness.

Read-only private connection with static catalog identifiers and bound selection values. Require exactly one catalog.datasets route. Query only that layer/snapshot/dataset/source_schema and requested dates with max_files+1 rejection. Reject ambiguous routes, duplicate selected paths, conflicting schema signatures, malformed/null metadata and unsafe view identifiers. Never union a curated overlap into a prepared population. Multiple explicit files per requested date are allowed within the bound; sort by date/original path for deterministic receipt identity without claiming market-event order.

Check physical selected original/optimized presence and declared byte lengths; stream any asserted hashes in fixed chunks under cumulative max_hash_bytes, including catalog hashing. Catalog digest before/after resolution rejects changed catalogs. File checks are bounded observations, not a lock on mutable external files; EQ053 owns acquisition stability binding. Missing partitions remain explicit; a zero-row catalog entry is declared empty pending row qualification. Known-at, eligibility, precision, execution uniqueness, calendars and PIT remain unknown until separately qualified.

Safe fixed SourceError messages omit local paths/source exception text. SCHEMA for malformed records/identifiers/pin mismatch/ambiguity/conflicts; UNAVAILABLE for absent route/catalog/selected physical files; LIMIT for sessions/files/hash budget; CANCELLED for explicit cancellation checked between metadata/file/hash operations; TRANSPORT for other catalog I/O. No network/credential/live/scheduler/publication support. DuckDB read-only does not imply an untrusted-SQL sandbox; only owned static metadata queries are issued.

Independent synthetic tests create actual temporary DuckDB catalogs plus explicit files: exact selected generation despite overlapping curated rows; two routes/zero routes; multiple disjoint shards versus duplicate paths; missing date versus declared-empty entry; daily substitution preservation; schema signature conflict/stale schema pin; correct and wrong original/optimized hashes/unknown hashes; changed catalog pin; matching-size rewritten file; unknown admission text; invalid ISO dates/null/boolean/negative counts and SQL identifier payloads; bound sessions/files/hash bytes; pre-cancellation and cancellation during hashing; source database remains unchanged/read-only; core distribution bytes/dependencies unchanged. Expected selected paths/counts/hashes come from independently authored fixture bytes and metadata, not adapter output.

Update resolver API/source mapping, installation/compatibility/build channel, package design, README/changelog, issue/PR, delivery receipt and handoff with this story. Repeat-build/inspect actual adapter wheel/sdist, clean installed public resolver checks on Windows and native Linux CI, final-head separate local review, main artifact download/hash/installation/readback precede Done. No EQ050–056 source scope or R4 acceptance is claimed by resolver delivery.
