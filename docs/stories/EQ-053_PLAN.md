# EQ-053 — R4 pre-code plan

[Issue60](https://github.com/atulsrivas1/equity-features/issues/60), R4/E07.
Estimate: **5 provisional story points**, not a deadline. Prepared plan only;
no implementation, executed tests or delivery claimed.

## Start and dependencies

EQ049–052 evidence boundaries. Reinspect live acceptance and accepted public contracts before pulling.
One active implementation story. Follow [execution package](../R4_AUTONOMOUS_HANDOFF.md)
and [test strategy](../R4_TEST_STRATEGY.md); define concrete interfaces and independently
expected fixtures before source implementation.

## Design

Bind source snapshots, receipts, normalization/schema versions, substitutions, original/optimized identity and admission; reuse contracts for later EQ103.

### Concrete pull — October6,2026, before source

EQ049–052 are Closed/ProjectDone. EQ052 finalmaincd8377f passed separate source/
receipt reviews6025190664/6025336786, actual24archives/current20reports/fourfresh
forms and Released6025430699/postrelease readback. No active PR; pull053only.
Optional version becomes0.1.0a5; corepaira4/consumer0.4.0, schema1/math/runtime pins
DuckDB1.5.6/NumPy2.2.6 remain unchanged. No provider download or source rewrite.

Add frozen VerificationPolicy(max_hash_bytes=1073741824, max_files=4096,
require_original_pins=False) to ReadConfig, with positive exact integer bounds
and exact Boolean. No size-only bypass: every selected original is SHA256-read
before and after bounded acquisition; original expected pins are enforced whenever
supplied. Strict caller mode requires every selected original pin. Unknown pins
are recorded as observed read-window evidence, never invented prior admission.
Optimized files are never queried; only supplied optimized pins are hash-checked
before/after, otherwise their declared identity remains unverified. Existing resolver
reinspection verifies actual route/partition metadata/receipt IDs and catalog hash
against the retained resolution. Detect stale same-sized catalog/original content,
tampered resolution digest, schema/snapshot/receipt metadata mixing and missing files.
All hashes share an explicit cumulative byte budget (including resolver's two
catalog reads and final catalog read), cancellation and safe SourceError boundary.

Add immutable FileEvidence(partition, observed_original_sha256,
verified_optimized_sha256) and AcquisitionReceipt(schema/version, request/config/
resolved identities, catalog hash, owned files/missing dates, source binding,
canonical schema1, MappingReport or explicit absence, source coverage, availability,
calendar version, disposition/rows, pin strength, hash byte count, identity digest).
ReadResult.receipt is present on successful actual reads and terminal missing input.
Input evidence identity binds full request/config mapping/sessions/scope/caller
coverage/version and actual observed source bytes before canonical mapping. Upgrade
source mapping prefix to original-read2; retained-map1 extends it using actual
columns/conversion reports. Final receipt digest binds input evidence, normalization
report and full-population output source/coverage, without a circular output binding.
Original occurrence tokens bind observed original content plus resolver/path/row;
stable subset reads preserve occurrences for unchanged source. Chunk sizes may change
delivery/request identities but never original physical occurrence identity.

Hash equality proves matching local observations at checked points, not atomic
snapshot isolation, absence of transient change/reversion, provider truth, original
exchange IDs, rights, precision recovery, rewrite parity, calendar authority or PIT.
Catalog declarations/substitutions/legacy admission remain unchanged assertions.
Receipts contain private local paths and metadata: do not publish raw real receipts.
No new execution-receipt schema in pure packages; future EQ103 can consume this
versioned optional acquisition evidence rather than duplicate a catalog.

ReadMetrics gains verification_ns and verification_hash_bytes (default zero for
compatible manual construction). External total read includes verification; existing
SQL/map/copy phases retain their meanings. User-space hashed bytes are not physical
storage I/O or exclusive memory allocations. Current synthetic quick measurements
must bind the new harness/report/runtime; previous a3 costs remain dated provenance.

Independent actual Parquet tests: hand-computed SHA256s/budget totals; unpinned versus
all-original-pinned receipts; exact retained schema/normalization/availability and
legacy substitution fields; equal-size stale catalog/original mutation rejection;
valid same-sized original mutation before an unpinned read produces new receipt and
occurrence identity (no prior-pin claim); mutation during read is rejected before
any envelope; optimized unpinned bytes remain unverified versus supplied pin mismatch;
missing files/pin/digest/metadata mixing; exact budget boundary/one-byte short;
cancellation while hashing; owned missing/empty receipts and repeat/chunk/subset
identity behavior. Reuse actual fixture module without duplicate test collection.
Run full optional/strict6/pure boundary/current Foundation checks, separate final
review and bothOS actual wheel/sdist CI, fresh downloaded fourforms, actual main
archives/reports, receipt/publication/Releasedpostread before Done.

## Open questions and source issues

Freeze exact API/configuration/backend pins and supported source populations when
pulled. Unknown precision/availability/eligibility/calendar/reference evidence stays
explicit. A consequential canonical schema/capability change needs a versioned
decision, regression evidence and review. Real instruments/dates/goldens must be
selected from inspected source support, not invented in this preparation.

## Required tests

Changed/stale/missing pins, schema/snapshot mixing, unknown provenance/availability; receipt semantics and limits.

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

Bounded acquisition evidence, no provider-truth or PIT certification by hashes. Neither a prepared plan nor a source merge establishes this outcome.
