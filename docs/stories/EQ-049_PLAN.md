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
