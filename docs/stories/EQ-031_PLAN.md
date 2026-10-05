# EQ-031 — pre-code draft

Prepared 2026-10-05 from the owner-authorized R2 package. Local preparation only;
no code, Ready status or accepted delivery claimed. Review live issue acceptance,
Project status, actual dependency receipts and the final prior-story API before pull.

## Scope, dependencies and effort

[EQ-031 #36](https://github.com/atulsrivas1/equity-features/issues/36) /5 /027, context formulas

## First action and frozen design

PriorNvolume mean excludes target; supplied compatible target divided by baseline. Resolve target intraday completeness identity and typed baseline dependency.

## Concrete API/version/numerical decision

compute_daily_baseline accepts canonical daily batch, ConfigSpec and HistoryContext and returns FeatureResult. compute_relative_volume accepts caller-supplied canonical target volume and typed accepted baseline/context; it never computes a missing baseline. Default N20 selects prior-only slots. Matching target entity/grid/N/quantity basis/action policy/cutoffs/config identities are required. Target may be intraday only with explicit scope/completeness; baseline is not a forecast. Scalar unavailable results stay null; baseline0 available and ratio0/0 not_applicable.

All caller input is immutable owned typed in-memory data. Preserve frozen39 built-in
IDs and source-independent CanonicalBatch/ConfigSpec/FeatureResult boundaries.
No hidden calendar/reference/dependency lookup. Malformed representations/identity
mismatches raise ContractError; independent missing families retain typed null and
readiness. C/K/E, source/revision/action basis, supplied units/grid/anchor and consumed
membership remain explicit. Float64 tolerance is rtol/atol1e-12 in declared units;
independent exact/high-precision references establish arithmetic, not source truth.

## Independent actual API qualification

Prior[100,200,300] mean200 andtarget500 ratio5/2; target/future mutation, missing slot, insufficient history, coveredzero baseline, absent target and unit/basis/config mismatch.

Tests must call actual production public APIs with independently derived synthetic
expected values; never only duplicate reference helpers. Preserve all123 reference
cases and repaired session regressions. Cover ownership, unavailable/null/zero,
duplicates/order, incompatibility, wide arithmetic and truthful mode discovery.

## Documentation and observable Done

Daily baseline/relative-volume API and causal example; two IDs with explicit unavailable/zero-denominator behavior.

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
