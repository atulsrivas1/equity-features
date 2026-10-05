# EQ-032 — pre-code draft

Prepared 2026-10-05 from the owner-authorized R2 package. Local preparation only;
no code, Ready status or accepted delivery claimed. Review live issue acceptance,
Project status, actual dependency receipts and the final prior-story API before pull.

## Scope, dependencies and effort

[EQ-032 #37](https://github.com/atulsrivas1/equity-features/issues/37) /8 /031 and structure contracts

## First action and frozen design

Caller buckets bind exact offsets/grid version; historical entire bucket coverage and Ndenominator fixed. Define typed per-bucket input/output/quality, independent readiness and elapsed target boundaries.

## Concrete API/version/numerical decision

Introduce owned BucketSpec(name,open_offset_ns,end_offset_ns,grid_version), BucketContext and IntervalBaseline/IntervalBaselineRow typed result cells with per-bucket QualityRow. Canonical BAR rows bind exact bucket/session bounds with per-slot certificates. Scheduled grid buckets may exceed an actual early close: record excluded absence, never synthesize observations. Historical denominator is always N. Target relative calculation requires exact elapsed bucket and supplied complete target coverage. Extend ValueType/Arrow output admission with versioned typed list-of-struct, independent bucket readiness, no untyped parallel result dictionary.

All caller input is immutable owned typed in-memory data. Preserve frozen39 built-in
IDs and source-independent CanonicalBatch/ConfigSpec/FeatureResult boundaries.
No hidden calendar/reference/dependency lookup. Malformed representations/identity
mismatches raise ContractError; independent missing families retain typed null and
readiness. C/K/E, source/revision/action basis, supplied units/grid/anchor and consumed
membership remain explicit. Float64 tolerance is rtol/atol1e-12 in declared units;
independent exact/high-precision references establish arithmetic, not source truth.

## Independent actual API qualification

Historical[10,20,30] mean20; early-close bucket absent rather than0, observed2/expected3 remainsnull; other buckets ready, zero/missing/partial target, incompatible grids/durations/cutoffs.

Tests must call actual production public APIs with independently derived synthetic
expected values; never only duplicate reference helpers. Preserve all123 reference
cases and repaired session regressions. Cover ownership, unavailable/null/zero,
duplicates/order, incompatibility, wide arithmetic and truthful mode discovery.

## Documentation and observable Done

Bucket/grid API and synthetic early-close example; two IDs without observed-count denominator or cumulative reinterpretation.

Publish reviewed plan before implementation. Version/API/math/precision decisions,
guide, installed example, changelog, issue evidence and continuity accompany code.
No-impact decisions are explicit. Follow Backlog->Ready->In progress->Code review
->Test->Ready to release->Released->Done with actual evidence. Author self-review
plus required exact-head CI is accurately labeled; no independent human claimed.
Relevant local tests/types/import/boundary/registry/compatibility/license checks,
repeat archive builds/inspection/fresh wheel+sdist execution, gated merge, published
main bytes/main bothOS CI, actual downloaded bundles/manifests/hashes/content and
four fresh installed pairs precede release receipt and issue closure. Source merge
or plan publication alone is not completion. No stable/PyPI/tag/public channel.
