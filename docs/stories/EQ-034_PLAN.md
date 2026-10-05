# EQ-034 — pre-code draft

Prepared 2026-10-05 from the owner-authorized R2 package. Local preparation only;
no code, Ready status or accepted delivery claimed. Review live issue acceptance,
Project status, actual dependency receipts and the final prior-story API before pull.

## Scope, dependencies and effort

[EQ-034 #39](https://github.com/atulsrivas1/equity-features/issues/39) /5 /027,033

## First action and frozen design

Consume supplied admitted symbol/market/sector returns and effective membership; arithmetic return differences. Define exact alignment/identity checks and independent market/sector readiness.

## Concrete API/version/numerical decision

compute_relative accepts owned ReturnContext for symbol/market/sector FeatureResults plus supplied ClassificationAdmission for sector membership. ReturnContext pins exact start/end governed IDs, horizon, endpoint mode, namespace mapping, units/basis/policy/anchor/C-K-E, feature algorithm and config. Validate supplied accepted results against their contexts; no return calculation. Independently unavailable market/sector outputs retain reasons; reject stale membership/reference/action revisions and mismatches. Different instrument action snapshots bind separately under same compatible policy.

All caller input is immutable owned typed in-memory data. Preserve frozen39 built-in
IDs and source-independent CanonicalBatch/ConfigSpec/FeatureResult boundaries.
No hidden calendar/reference/dependency lookup. Malformed representations/identity
mismatches raise ContractError; independent missing families retain typed null and
readiness. C/K/E, source/revision/action basis, supplied units/grid/anchor and consumed
membership remain explicit. Float64 tolerance is rtol/atol1e-12 in declared units;
independent exact/high-precision references establish arithmetic, not source truth.

## Independent actual API qualification

100→110 vs200→210 gives1/20; wrong horizon/endpoints/namespace/currency/basis/C/K/E/mode/version, missing benchmark/membership and stale revision; no hidden recalculation.

Tests must call actual production public APIs with independently derived synthetic
expected values; never only duplicate reference helpers. Preserve all123 reference
cases and repaired session regressions. Cover ownership, unavailable/null/zero,
duplicates/order, incompatibility, wide arithmetic and truthful mode discovery.

## Documentation and observable Done

Relative API/reference alignment/evidence docs; two IDs with independent dependent readiness.

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
