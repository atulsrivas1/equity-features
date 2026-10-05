# EQ-036 — pre-code draft

Prepared 2026-10-05 from the owner-authorized R2 package. Local preparation only;
no code, Ready status or accepted delivery claimed. Review live issue acceptance,
Project status, actual dependency receipts and the final prior-story API before pull.

## Scope, dependencies and effort

[EQ-036 #41](https://github.com/atulsrivas1/equity-features/issues/41) /5 /selected delivered families/results

## First action and frozen design

Explicit pure composition of caller-supplied accepted feature results; validate entity/session/version/config/availability/basis and supported optional families. Resolve typed orchestration without acquisition or hidden dependency calculation.

## Concrete API/version/numerical decision

compose_features accepts concrete tuple of named FamilyResult(result,context) and an explicit CompositionSpec, returning frozen FeatureBundle with retained independently typed FeatureResults and common compatible entity/session/C-K-E/unit/basis/algorithm references. Do not fabricate a common ConfigSpec digest across distinct actual family configurations; preserve each config/source identity. Reject duplicate family/feature keys, stale context and incompatible identities. Optional absent families are explicit and retained as absent; no acquisition/calculation, scheduling or incremental join engine.

All caller input is immutable owned typed in-memory data. Preserve frozen39 built-in
IDs and source-independent CanonicalBatch/ConfigSpec/FeatureResult boundaries.
No hidden calendar/reference/dependency lookup. Malformed representations/identity
mismatches raise ContractError; independent missing families retain typed null and
readiness. C/K/E, source/revision/action basis, supplied units/grid/anchor and consumed
membership remain explicit. Float64 tolerance is rtol/atol1e-12 in declared units;
independent exact/high-precision references establish arithmetic, not source truth.

## Independent actual API qualification

Compatible joins, missing optional families preserved, duplicate/incompatible identities/versions/cutoffs/modes, stale contexts, immutability and no source reads.

Tests must call actual production public APIs with independently derived synthetic
expected values; never only duplicate reference helpers. Preserve all123 reference
cases and repaired session regressions. Cover ownership, unavailable/null/zero,
duplicates/order, incompatibility, wide arithmetic and truthful mode discovery.

## Documentation and observable Done

Composition API/dependency graph/example; coherent typed feature bundle without generating missing dependencies.

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
