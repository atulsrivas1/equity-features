# EQ-035 — pre-code draft

Prepared 2026-10-05 from the owner-authorized R2 package. Local preparation only;
no code, Ready status or accepted delivery claimed. Review live issue acceptance,
Project status, actual dependency receipts and the final prior-story API before pull.

## Scope, dependencies and effort

[EQ-035 #40](https://github.com/atulsrivas1/equity-features/issues/40) /8 /027,028,033

## First action and frozen design

Immutable declared unique universe, exact compatible return/close/SMA membership. Typed partial breadth with expected/eligible counts and exclusions; preserve frozen structured partial semantics in result admission.

## Concrete API/version/numerical decision

Introduce frozen UniverseSpec(namespace,members,membership_identity,effective bounds,known_at_ns,revision) and MemberFeatureInput typed tuples. compute_breadth validates immutable unique declared universe, rejects extra/duplicate members and incompatible typed return/close/SMA contexts, then returns existing BreadthCounts/BreadthFraction cells in FeatureResult. Exact compatible rational/coefficient operands decide sign/equality; missing members never count unchanged. E/M and K/E stay exact properties and typed partial quality; E0 produces null cells, empty universe not_applicable. No event-stream accumulator.

All caller input is immutable owned typed in-memory data. Preserve frozen39 built-in
IDs and source-independent CanonicalBatch/ConfigSpec/FeatureResult boundaries.
No hidden calendar/reference/dependency lookup. Malformed representations/identity
mismatches raise ContractError; independent missing families retain typed null and
readiness. C/K/E, source/revision/action basis, supplied units/grid/anchor and consumed
membership remain explicit. Float64 tolerance is rtol/atol1e-12 in declared units;
independent exact/high-precision references establish arithmetic, not source truth.

## Independent actual API qualification

Universe4: +,-,0,missing→1/1/1,E3,M4; close>SMA gives1/3, equality excluded; empty/absent/E0, extra/duplicate members, mismatched basis/horizon/cutoff/version, future membership.

Tests must call actual production public APIs with independently derived synthetic
expected values; never only duplicate reference helpers. Preserve all123 reference
cases and repaired session regressions. Cover ownership, unavailable/null/zero,
duplicates/order, incompatibility, wide arithmetic and truthful mode discovery.

## Documentation and observable Done

Universe/breadth API and partial-result examples; two IDs without treating missing members as unchanged or denominatorM by default.

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
