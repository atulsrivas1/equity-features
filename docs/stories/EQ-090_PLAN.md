# EQ090 scanner/ranking implementation readiness proposal

Local preparation only, October14,2026. [EQ090 #102](https://github.com/atulsrivas1/equity-features/issues/102), E12#100, R8 milestone9; provisional eight complexity points. Blocked on accepted EQ089 contracts and verified Atul Project access. No code, tests, release, Ready transition or acceptance.

## Concrete proposed deliverable

Implement the optional pure equity-feature-strategies distribution under packages/strategies, 0.1.0a1/Python3.12 as proposed in [EQ089 exact schemas](EQ-089_SCHEMA_PROPOSAL.md). The public entry point is scan(request:StrategyRequest)->StrategyResult; constructors/types and encode/digest helpers follow those exact contracts. It consumes valid supplied core FeatureResult objects and never imports equity_features or recomputes numerical features. No feature acquisition, files/database access, wall clock, job scheduling, output publication, orders or portfolio state.

Implement closed feature/config/semantic-input admission before predicates, then complete per-entity predicate/ranking availability, explicit unavailable/nonmatching/matching rows, exact numeric ordering with stable entity ties, top-k watchlist, complete coverage counters and provenance/content identities. A feature ID/version/unit match alone is insufficient: expected calculation and input-semantic digests must agree across required cells. Keep core contracts/features dependencies unchanged and do not add label inputs to the core feature schema.

## First actions after accepted contracts

1. Verify actual EQ089 acceptance/final contract identities and current clean canonical main; refresh Project assignment/dependencies. Publish exact branch/points/contract/fixture pins and this packet to #102 before Ready and assigned In progress.
2. Freeze the public API/export names, package version/build inputs and supported Python/contract bounds in the linked design draft. Build one standalone optional distribution with no mandatory columnar or label dependency.
3. Materialize the hand-derived [strategy fixtures](EQ-089_FIXTURES.json) using actual independent valid core constructors. Expected selections/statuses/identities come from the published rules and goldens, never the production scanner. Keep immutable input snapshots and verify caller list mutation cannot change admitted request state.
4. Implement admission and deterministic selection, then full content identity/encoding. Separate source tests, independent review, formal acceptance and release evidence.

## Meaningful verification

Required cases cover threshold equality, false plus unavailable precedence, ties/ascending/descending ordering, no predicates, k0/koversized/invalidbool/negative, empty/single/allmissing/partial universe, exact int64 beyond binary64 precision, all supported scalar feature families, duplicate and outside-universe cells, incompatible versions/units/cutoffs/namespace/session and unsupported label/structured inputs. Mixed history horizons, baseline windows, adjustments and eligibility policies must reject even when feature IDs or units agree. Same semantics with a revised source snapshot preserves numeric selection but changes content/request identities.

Permuting universe/result/column/entity/quality/evidence presentation preserves normalized request and result bytes. Reordering semantic predicates changes config identity. Full payload/quality/evidence/source changes affect identities; metadata-only hashes cannot substitute. Identical observed prefixes with arbitrary future label/path/basis inputs leave the strategy result unchanged because labels cannot enter this API. Validate strict error/status schemas and exact exports with meaningful type/boundary checks.

## Same-story documentation and delivery

Publish API/config/identity/readiness/error examples using synthetic facts, import/ownership rules, fixture expectations, issue/PR acceptance, changelog, scoped lesson and handoff. Explicitly document raw deterministic screening without trading/profitability claims. Separate local reviewer covers exact final implementation/contracts/callers/findings, with renewed coverage after material changes.

Formal Test requires relevant independent fixtures, typing/import/boundary/publicdocs checks and actual fresh supported bothOS wheel/sdist qualification for this distribution; record source-tree fallback rejection and archive/source/RECORD/sdist identity. Default-branch current checks/artifacts/public UTF8/Atul attribution and release evidence precede Released then actual Done/issue closure. EQ092 still owns final cross-distribution synthetic consumer and aggregate compatibility/causality acceptance; component success cannot close it. No build/runtime verification has occurred for this proposal.
