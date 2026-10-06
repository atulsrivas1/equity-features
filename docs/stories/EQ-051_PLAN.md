# EQ-051 — R4 pre-code plan

[Issue58](https://github.com/atulsrivas1/equity-features/issues/58), R4/E07.
Estimate: **8 provisional story points**, not a deadline. Prepared plan only;
no implementation, executed tests or delivery claimed.

## Start and dependencies

EQ049/050. Reinspect live acceptance and accepted public contracts before pulling.
One active implementation story. Follow [execution package](../R4_AUTONOMOUS_HANDOFF.md)
and [test strategy](../R4_TEST_STRATEGY.md); define concrete interfaces and independently
expected fixtures before source implementation.

## Design

Private read-only connections, bound filters, owned source populations, bounded batches/cancellation; choose tested DuckDB/backend pins.

## Open questions and source issues

Freeze exact API/configuration/backend pins and supported source populations when
pulled. Unknown precision/availability/eligibility/calendar/reference evidence stays
explicit. A consequential canonical schema/capability change needs a versioned
decision, regression evidence and review. Real instruments/dates/goldens must be
selected from inspected source support, not invented in this preparation.

## Required tests

Predicates, chunks/limits/order/cancellation/errors; measure SQL plus conversion/copy/native memory; optional install/read API.

Apply relevant accepted SDK, mathematical/time/action and package-isolation checks.
Keep synthetic DuckDB conformance and private real-data acceptance separate; record
actual executed results, source/installation identities and limitations. Original
or legacy derived output is not automatically an independent numerical golden.

## Documentation

Update relevant public API/mapping/install/limitations examples, issue/PR, review
and delivery receipt, changelog and SESSION_HANDOFF alongside implementation.
Private actual-source evidence remains outside public files without redistribution
rights. Final installed/artifact/CI/readback evidence precedes Done.

## Done outcome

Bounded historical acquisition; no scheduler/live feed. Neither a prepared plan nor a source merge establishes this outcome.

## EQ051 concrete pre-code design

Use optional version0.1.0a3, unchanged corepaira4/schema1/DuckDB1.5.6. ReadConfig owns namespace/source_id/calendar_version, caller supplied SessionSpecs and exact partition-session pairs, one resolved source and MappingPolicy. Freeze valid sessions/interval bounds; do not infer from file dates. Supported one source kind per adapter, historical/raw/ordinary half-open events or whole completed intervals, quotes trade_snapshot. No live/closing-auction inclusive/preopen seeds, continuous TBBO, reference acquisition or adjusted source support.

DuckDBHistoricalAdapter(config) capabilities/iter_batches and eager read(request, cancellation=None)->ReadResult(batches, metrics). The eager bounded population is mapped once; chunk source.mapping_version remains stable and each input_id binds request/ordinal/slice. Source coverage describes the selected supplied population only; provider completeness requires independent evidence. Whole selected population checked before yielding, rows+1/batches/files bounds, safe errors and cancellation before/query/fetch/map/between yields. Synchronous SQL/UDF work has no hard responsiveness/process-cap promise. Caller serializes iterator use.

Use original selected local Parquet for file_row_number original occurrence; optimized row number cannot be relabeled original. Preserve both lineage records/pins. One private local read-only catalog connection, static controlled projections, bound individual paths/instrument IDs/time limits. No catalog view execution/globs/remote files/extensions. Original time VARCHAR is parsed by pinned exact UTCns Python UDF with BIGINT output; no lossy timestamp cast. SQL predicate selection and deterministic time/file-index/physical-row ordering, final mapper semantic validation. Require original raw schema compatible and file paths exact; same-sized mutated files stability EQ053.

Metrics separately record SQL/fetch, canonical conversion, delivery copying, selected/delivered rows/cells/chunks/files and selected physical file byte lengths (not measured storage I/O). External standalone synthetic benchmark probes process native lifetime peak and elapsed/memory/copy costs; qualify numerical/identity parity before claims. No zero-copy/throughput guarantee.

Independent real DuckDB/Parquet fixtures cover two shards/tied equal payloads/physical occurrence, instrument/time pushdown and exact1ns boundaries, whole bars/UTCdaily, mapping binding across chunks, actual empty/missing partition, wrongsnapshot/kind/clock/sampling/unit/adjustment, stale original schema/count, limits/pre- and between-chunk cancellation/safe messages/private connection unchanged catalog and no core changes. Source read preserves known-at unknown/later. Documentation read/config/metrics, installed bothOS fixtures, final local review/artifacts/readback before Done. Governed calendar/history/references EQ052 and stability/acquisition receipts EQ053 remain later. Actual real numerical slice/goldens EQ055 remains unfrozen.

Preparation-only synthetic probe on installed DuckDB1.5.6/Windows verified bound original-path read_parquet(file_row_number=true,hive_partitioning=false), exact VARCHAR-to-BIGINT UTCns Python UDF and1ns half-open filter retaining original physical row1; read-only catalog bytes unchanged. One fixture is not story/nativeLinux/performance/real-source/conformance acceptance.

ReadResult should retain full bounded canonical population as well as envelopes/metrics for explicit calculation composition. Chunking occurs after mapping whole population: identical mapping_version/source coverage/schema, unique deterministic per-request/ordinal input IDs, source coverage distinct from delivery count. Default source coverage unknown/incomplete. An optional caller-owned CoverageAssertion binds exact request kind/instrument/session/scope/time and expected selected rows plus policy; only matching verified selected count may retain asserted complete, never provider truth or market interval completeness. Missing selected partitions produce a single missing envelope instead of publishing partial complete data. Calendar and bar construction scope are explicit caller inputs.


### Frozen interfaces and bounds

ReadConfig(catalog_path, resolved, mapping, namespace, source_id, calendar_version, sessions,
partition_sessions, scope, coverage_assertion=None, max_files=4096,
max_batch_rows=1024, threads=1, memory_limit_mb=256) owns typed records and exact
positive bounds. SessionSpecs are caller-governed, same namespace/unique IDs/
nonoverlapping actual bounds. Partition-to-session pairs are explicit unique exact
ISO dates covering the resolver selection; no file-date calendar inference. Scope
is caller-owned InputScope; no auctions/inclusive acquisition extension. Mapping
schema/unit/policy must agree with resolved selection/scope. No adjusted/live/ref
source support. Config limits control eager population/materialization; memory
setting is not a hard process cap.

CoverageAssertion(instruments,sessions,start_ns,end_ns,expected_rows,policy_id)
is an explicit caller assertion for exactly one requested population, not provider
truth. A matching actual selected count retains asserted complete; absent assertion
defaults Coverage(None,n,False). Conflicts fail; subsets do not inherit complete.
ReadResult(canonical,batches,metrics,mapping_report) owns full bounded canonical population and
chunk envelopes. ReadMetrics names SQL/fetch, mapping and delivery copy ns, rows,
files, cells/chunks and selected file bytes, explicitly not measured storage I/O.

Read SQL intersects request time/instrument/session predicates with supplied actual
session bounds, preserving half-open events or whole bar intervals. Bounded n+1
selection across explicit original local files, exact UTCns UDF, original physical
file row number, deterministic timestamp/file-index/row order. Global retained tie
keys distinguish equal-time occurrences; not exchange sequence proof. File schema/
path/declared bounds and input typing fail safely. Map once, then deterministic
request/ordinal/slice input IDs retain mapping version/coverage across envelopes.
Missing selected partition is terminal missing, no partial complete output.

Independent fixtures before code: original row index remains1 after excluding
physical row0 at end bound; tied equal payloads across two shards count separately;
1ns start/end boundary; excluded instrument/session rows; two valid minute bars
whole-boundary selection; UTCdaily24h; nonnull/null known-at untouched; wrong units/
snapshot/schema/sampling/adjustment; malformed original file time/type; all row/
file/chunk limits before yield; pre- and between-chunk cancellation; observed zero
selection versus missing partition; stable mapping across chunks passes existing
validate_delivery; original catalog bytes unchanged. External measured synthetic
workload verifies selected units/identity parity, SQL/conversion/copy times and
process lifetime native peaks with units/platform/toolchain recorded. No native
memory hard cap, midquery responsiveness, zero-copy or full-corpus claim.

Implementation refinement: ReadConfig requires catalog_path:Path as its first
argument. ResolvedSource intentionally holds no catalog path; caller supplies the
explicit existing absolute catalog for a private read_only=True connection. No
catalog view is executed and no imaginary in-memory read-only mode is promised.
EQ053 adds actual catalog/file stability receipt binding.

ReadResult also retains MappingReport (None for missing acquisition) so actual
price rounding and unmapped-field evidence remain observable, not lost behind
the bound canonical identity. Mapping timing includes sorting/column/occurrence
materialization and mapping; total external timing includes preflight overhead.


Clean installation refinement: optional adapter runtime includes NumPy2.2.6,
required by observed DuckDB1.5.6 Python UDF registration. Reuse existing governed
upstream pin/integrity provenance; corepair dependencies are unchanged. No extra
provider/backend or numerical behavior added. Final bothOS clean installed forms
verify exact dependency metadata and backend versions.
