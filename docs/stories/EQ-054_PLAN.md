# EQ-054 — R4 pre-code plan

[Issue61](https://github.com/atulsrivas1/equity-features/issues/61), R4/E07.
Estimate: **5 provisional story points**, not a deadline. Prepared plan only;
no implementation, executed tests or delivery claimed.

## Start and dependencies

EQ043 plus EQ049–053. Reinspect live acceptance and accepted public contracts before pulling.
One active implementation story. Follow [execution package](../R4_AUTONOMOUS_HANDOFF.md)
and [test strategy](../R4_TEST_STRATEGY.md); define concrete interfaces and independently
expected fixtures before source implementation.

## Design

Existing SDK against actual installed DuckDB adapter, public synthetic DuckDB/Parquet fixtures; independent expectations.

### Concrete pull — October6,2026, before source

EQ049–053 are Closed/ProjectDone. EQ053 finalmain185859d passed separate source/
receipt reviews6025684027/6025840016, allCI/actual24archive equality/current20reports/
fourfresh90case forms, Released6025925692/postread. Original P2budgetrace resolved,
old8ade checks excluded. Pull054only;055private scope/goldens/056R4 remain planned.

Add standalone public examples/duckdb_conformance.py, using fictional caller
identities and temporary actual DuckDB catalog plus original/optimized Parquet.
run_suite(require_installed=False) returns a sanitized synthetic report. CLI
--installed --output PATH requires site-packages imports for both pure packages,
optional adapter and native backend, then executes actual bounded adapter calls.
The accepted pure run_conformance receives actual returned envelopes or actual
captured safe SourceErrorCodes; supplied expected codes remain independently fixed.
Unexpected exceptions fail execution. No synthetic in-memory adapter substitutes
for DuckDB. Captured errors describe their actually exercised stage; deliberately
mutated delivered envelopes are labeled SDK rejection probes, not adapter output.

Freeze thirty cases spanning all four supported source schemas: valid tied/identical
trade occurrences and nanosecond selection/empty/unknown and future knowledge;
snapshot/namespace/unit/identity/missing-file/missing-partition/stale catalog/pin/
row/chunk/hash limits/cancellation; trade eligibility absence; TBBO trade_snapshot
versus unsupported continuous; minute and UTCdaily whole intervals versus partial
cutoffs; explicit curated/prepared overlap route selection; actual delivered
ordinal/final/coverage mutations rejected by SDK. Each report retains named actual
expected/observed outcomes and stage, no source paths/credentials/private data.
Prior90 resolver/mapping/reader/governance/evidence tests remain independent
DuckDB-specific edge coverage, including holidays/DST/earlyclose/reference timing.

Independent numerical goldens from actual admitted delivered populations:
trades price100/102/102, size2/3/3, distinct tied executions -> count3/volume8/
notional81200 coefficient at scale2/VWAP101.5/mean8/3; minute bars
(open10,high12,low9,close11,volume3) and (11,14,10,12,5) -> open10/high14/low9/
close12/volume8/close-weighted proxy93/8=11.625, actual notional unavailable;
three UTCdaily closes10/20/30 -> SMA3=20/anchored EMA3 seed20. Explicit synthetic
selected-population certificates and supplied known-at admit available results;
unknown/later known-at stay present and yield causal unavailable quality.
Check units/status/source binding as well as values; absolute/relative tolerance
1e-12 only for nonexact float ratios. No new formulas/source truth or provider PIT.

Optional version0.1.0a6 identifies expanded installation qualification; acquisition1
records actual adapter versiona6, original-read2/retained-map1 unchanged. Pure
corepaira4/consumer0.4.0/schema/math/modes/dependencies and DuckDB1.5.6/NumPy2.2.6 pins
unchanged. Add two integration tests for actual suite/independent outcomes and
installed-location enforcement; strict-check standalone example too. Existing
optional repeat builder executes installed standalone example for both forms,
retaining conformance-<system>-<form>.json with source/harness/producer/runtime/
actual input archive identities and expected/observed outcomes. Each native bundle
now has six reports; actual combined optional/Foundation report count becomes24.

Current source review/typing/independent fixtures/purity/docs and bothOS actual
wheel/sdist CI, fourfresh downloaded form installations, current harness/report/
archive/publication/receipt review/Releasedpostread remain beforeDone. Public API/
installation/executable fixture guide/changelog/qualification matrix/lesson/handoff
accompany implementation. Raw real sources are absent; EQ055 must separately freeze
and qualify actual private instruments/sessions/goldens before final R4 acceptance.

## Open questions and source issues

Freeze exact API/configuration/backend pins and supported source populations when
pulled. Unknown precision/availability/eligibility/calendar/reference evidence stays
explicit. A consequential canonical schema/capability change needs a versioned
decision, regression evidence and review. Real instruments/dates/goldens must be
selected from inspected source support, not invented in this preparation.

## Required tests

[Test matrix](../R4_TEST_STRATEGY.md), bothOS clean wheel/sdist conformance, limits/cancellation, core isolation; executable fixture guide.

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

Actual DuckDB conformance and synthetic integration, not an in-memory substitute. Neither a prepared plan nor a source merge establishes this outcome.
