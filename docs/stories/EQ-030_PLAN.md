# EQ-030 — pre-code draft

Prepared 2026-10-05 from the owner-authorized R2 package. Local preparation only;
no code, Ready status or accepted delivery claimed. Review live issue acceptance,
Project status, actual dependency receipts and the final prior-story API before pull.

## Scope, dependencies and effort

[EQ-030 #35](https://github.com/atulsrivas1/equity-features/issues/35) /8 /027

## First action and frozen design

Centered sample deviation of Nsimple returns from N+1closes, explicit Adefault1. Choose stable checked algorithm and document any bounded roundoff clamp with evidence.

## Concrete API/version/numerical decision

Extend compute_history for history.return_volatility. Use N>=2 simple returns from N+1 closes and explicit positive integer A(default1). Compute centered deviations with exact transient rational values for a finite window, then a high-precision square root and final Float64; retain no growing recursive fractions. Document arithmetic cost and no throughput claim. A supported finite-window accumulator retains at most N+1 exact closes and certificates. Registry modes require actual chunk/restored qualification.

All caller input is immutable owned typed in-memory data. Preserve frozen39 built-in
IDs and source-independent CanonicalBatch/ConfigSpec/FeatureResult boundaries.
No hidden calendar/reference/dependency lookup. Malformed representations/identity
mismatches raise ContractError; independent missing families retain typed null and
readiness. C/K/E, source/revision/action basis, supplied units/grid/anchor and consumed
membership remain explicit. Float64 tolerance is rtol/atol1e-12 in declared units;
independent exact/high-precision references establish arithmetic, not source truth.

## Independent actual API qualification

High-precision independent variance476449/44791488, centered-versus-RMS, sample-versus-population, flat0, scaling, near-equal large prices, gaps/minimum history, supported parity.

Tests must call actual production public APIs with independently derived synthetic
expected values; never only duplicate reference helpers. Preserve all123 reference
cases and repaired session regressions. Cover ownership, unavailable/null/zero,
duplicates/order, incompatibility, wide arithmetic and truthful mode discovery.

## Documentation and observable Done

Volatility conventions/units/tolerance and example; one ID without log-return or implicit252annualization.

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
