# R4.1 autonomous repository separation and I/O execution

Prepared under [GOV-015 #289](https://github.com/atulsrivas1/equity-features/issues/289)
at the owner's October 6, 2026 request to prepare the release handoff and assign a
new session. This is execution preparation, not implementation or release acceptance.

## Mission and authorization

Complete [R4.1 milestone15](https://github.com/atulsrivas1/equity-features/milestone/15):
[E18 #276](https://github.com/atulsrivas1/equity-features/issues/276) and
[E19 #277](https://github.com/atulsrivas1/equity-features/issues/277), EQ-121 through
EQ-130 (#278 through #287). Deliver independently installable, extensible sources
and sinks before R5 worker implementation. The owner explicitly requests a new
execution session to perform this bounded release autonomously.

Within EQ-121, create public `atulsrivas1/equity-feature-io` and
`atulsrivas1/equity-feature-workers`, with Apache-2.0 and the same relevant work,
privacy, review and delivery agreements. Verify name/access availability first;
do not reuse an existing repository with unrelated contents. The worker repository
is a typed/buildable skeleton in this release; commands, scheduling and historical
generation are R5 scope. Move the optional DuckDB implementation through reviewed
EQ-122 changes, preserving accepted behavior and history. Routine API/package
choices within the accepted architecture do not require repeated permission.

Start implementation only after GOV-014 #275 and this GOV-015 handoff are verified
Closed/Project Done and their actual merged main content is fetched. Read current issue/Project
ownership before every pull. Use one active implementation story, short-lived
`codex/` branches, pre-code plans, public PRs and the exact lifecycle:
Backlog -> Ready -> In progress -> Code review -> Test -> Ready to release ->
Released -> Done. Do not close a merely merged implementation awaiting artifacts
or move blocked work to Ready. Keep explicit prerequisites and failure evidence.

Do not implement R5 workers, R6 providers, remote/MCP services or unrelated
products. Do not change formulas, core input/schema meanings, supported numerical
modes or historical availability to ease extraction. No source dataset deletion,
history rewriting, lake
cleanup, historical regeneration, paid provider fetch, account/profile changes,
deployment, stable tags or public package registry publication is authorized here.
Use the experimental CI artifact channel, disclose finite retention and verify
actual publication. A registry release or different distribution channel remains
a separate owner decision; do not make it an invented prerequisite for ordinary
experimental artifact delivery.

## Required context and accepted baseline

Read AGENTS.md, [project knowledge](PROJECT_KNOWLEDGE.md),
[public development](PUBLIC_DEVELOPMENT.md), [delivery policy](DELIVERY_POLICY.md),
[current continuity](SESSION_HANDOFF.md), [backlog](BACKLOG.md),
[architecture](IO_WORKER_ARCHITECTURE.md),
[decision](decisions/IO_REPOSITORY_SEPARATION.md),
[all ten story plans](R4_1_DELIVERY_PLAN.md), [review policy](CODE_REVIEW.md),
[knowledge workflow](knowledge/BACKLOG_WORKFLOW.md),
[lessons](knowledge/LESSONS.md), [R4 acceptance](R4_ACCEPTANCE.md),
[build delivery](BUILD_DELIVERY.md), [compatibility](COMPATIBILITY.md),
[package layout](PACKAGE_LAYOUT.md), and the relevant API/formula/timing contracts.
The live [Project](https://github.com/users/atulsrivas1/projects/2) is status authority.

Observed planning baseline: R4 accepted main `74ac28dcacc373105ff1a9bff97a69baabdee588`;
GOV-014 / PR288 merged `a44e48de9f52b61166af47d030718b2fb623372d`, separately reviewed
final `d99c61e2d6684a6ff5ec2f7f5ae607c6d990f374`,
[review](https://github.com/atulsrivas1/equity-features/pull/288#issuecomment-6027806164).
Actual main [documentation](https://github.com/atulsrivas1/equity-features/actions/runs/37550251108),
[Foundation](https://github.com/atulsrivas1/equity-features/actions/runs/37550251079) and
[optional adapter](https://github.com/atulsrivas1/equity-features/actions/runs/37550251096)
all succeeded; published tree and all 19 changed files matched reviewed source.
GOV-014 is Closed/Done. Ten R4.1 stories and both epics were open/Backlog, 60
provisional points; R5 explicitly depends on EQ-130. Recheck this live at execution.

Current experimental contracts/features pair `0.0.4a4`, consumer `0.4.0` and optional
`equity-feature-duckdb` `0.1.0a7` remain accepted. CPython 3.12 x64 Windows/Linux,
DuckDB 1.5.6, NumPy 2.2.6 and the actual supported dependency pins apply until
explicitly qualified changes. There are 39 built-ins, 23 session update/restore IDs,
22 conditional merges; all 16 R2 IDs and custom features remain batch-only.
R4 synthetic acceptance used 94 optional tests per installed form, 30 SDK outcomes
and 16 independent numerical checks; representative private acceptance used four
Windows installed forms, each 68 numeric/status/unit/source checks, 9 successful
acquisitions and 3 blocked cases. These are historical receipts, not new-session
executed results or guarantees for arbitrary data/platforms.

## Architecture and cross-repository authority

| Component | Responsibility and invariant |
| --- | --- |
| `equity-features` repository | Canonical contracts and pure calculations. Keep existing pure acquisition protocols/imports compatible. No fetching, credentials, file/database writes, scheduling or outward I/O/worker dependency. |
| `equity-feature-io` repository | Independently installable I/O contracts, SDK/factories, sources and sinks. New I/O contracts depend inward on canonical contracts; no duplicate schema or circular dependency. Backend dependencies stay optional per implementation. |
| `equity-feature-workers` repository | R4.1 skeleton only; R5 later owns tasks, claims/retry policy, partitioning, checkpoints, orchestration and catalog selection. |
| Source adapter | Acquires and normalizes bounded inputs with identity/precision/coverage/known-at evidence; source declarations are not truth or entitlement certification. |
| Output sink | Converts standard results and publication envelope into backend storage; preserves nulls, units, quality and all evidence; owns retry-safe storage commit and receipt. |
| Consumer/factory SDK | Supports directly supplied instances or explicit per-run registries and validated configuration. No import-time discovery/registration or untrusted executable/module loading. |

Keep EQ-121 through EQ-130, original epic links, milestone15 and Project2 as the
single canonical release/story authority in this repository. Companion PRs link
the full canonical issue URL and record their component delivery evidence; do
not use auto-closing keywords that close a cross-repository story before release.
Do not duplicate story lifecycle in a second issue/Project or silently transfer
accepted issue/history. Companion contribution/AGENTS docs explain this rule.
Core retains the roadmap/accepted receipts; I/O owns current implementation/API
docs after extraction, with explicit redirects/migration links instead of deleting
historical qualification. The workers skeleton links the future R5 authority.

For every final component PR, record the actual reviewer/head and applicable CI;
at story acceptance bind all contributing component commits/artifacts and the
core planning/readback record. Maintain compatible version ranges and a tested
component matrix. A green component build alone does not qualify the composed
system, private source authority or the whole R4.1 release.

## Story order and concrete plans

Points are provisional complexity, not days or promised release dates. Default
execution order below is sequential; before every implementation publish a
concrete pre-code plan, independently expected fixtures, signatures/configuration,
version effects and unresolved choices using the linked baseline plan.

| Story / canonical issue / points | Prerequisites | Deliverable and next boundary |
| --- | --- | --- |
| [EQ-121 #278](https://github.com/atulsrivas1/equity-features/issues/278),5 | Verified GOV-014/GOV-015 publication and repo access | Companion repositories, governance, package names/layout and independently buildable skeletons. No worker commands. |
| [EQ-122 #279](https://github.com/atulsrivas1/equity-features/issues/279),8 | EQ-121 | Extract accepted DuckDB implementation/tests/harness with preserved distribution/import and mathematical/source meanings; migration/deprecation and installed compatibility evidence. |
| [EQ-123 #280](https://github.com/atulsrivas1/equity-features/issues/280),5 | EQ-121 | Freeze separate source/sink/factory interfaces, logical content identity/serialization, receipt, capabilities, errors and publication traces before implementation. |
| [EQ-124 #281](https://github.com/atulsrivas1/equity-features/issues/281),5 | EQ-123 | Explicit direct injection and validated source/sink factory registries; compatibility/capability checks, credentials kept outside public config/results. |
| [EQ-125 #282](https://github.com/atulsrivas1/equity-features/issues/282),8 | EQ-123 | Typed sink lifecycle/contracts and reusable independent conformance kit: begin/write/commit/abort/status lookup and failure/conflict semantics. |
| [EQ-126 #283](https://github.com/atulsrivas1/equity-features/issues/283),8 | EQ-125 | Bounded immutable Parquet generations, staging/completion manifest/qualified readers and explicit filesystem assumptions. |
| [EQ-127 #284](https://github.com/atulsrivas1/equity-features/issues/284),8 | EQ-125 | Transactional DuckDB result sink, explicit output destination/serialized writer, identity/receipt/rollback/read visibility. |
| [EQ-128 #285](https://github.com/atulsrivas1/equity-features/issues/285),5 | EQ-124/125/126 | Independently packaged synthetic source/sink examples from installed public APIs, direct injection and factories, typing/conformance and failures. |
| [EQ-129 #286](https://github.com/atulsrivas1/equity-features/issues/286),5 | EQ-122/124/126/127/128 | Core-without-I/O independence and declared installed component compatibility matrix; preserve R4 constraints and qualify changed source behavior. |
| [EQ-130 #287](https://github.com/atulsrivas1/equity-features/issues/287),3 | EQ-129 and all other release story acceptance | Ten-story release audit, actual artifacts/reviews/CI/migration/extension acceptance and post-release readback; explicit R5 readiness handoff, then STOP. |

The [delivery plan](R4_1_DELIVERY_PLAN.md) contains each story's start, design,
open questions, tests, documentation and Done state. Refine it as evidence appears;
do not replace a dependency with an invented test count or mark planning as code.
EQ-123 owns unresolved wire/envelope/canonical digest details. EQ-126/127 qualify
actual platform/concurrency/transaction semantics. PostgreSQL and other sinks are
future/custom examples, not additional initial implementations.

## Review and test gates

Separate local Codex review is already owner-authorized for bounded R4.1 and its
preparation. Use a separate reviewer for actual final component heads, semantic
docs/contracts and affected callers. Record identity, response, executed checks,
findings/disposition and limitations. Relevant later changes require renewed
final-head coverage. Hosted review remains unavailable/unverified; author
self-review, a request or CI alone does not satisfy this gate. This authorization
does not silently extend to R5 or count as human review.

Use [R4.1 test strategy](R4_1_TEST_STRATEGY.md). Key independent gates are preserved
R4 source/precision/timing behavior, exact output round trips, every evidence table,
same-key same-content receipt replay, different-content conflict, partial writes,
commit uncertainty/status lookup, crash/rollback, cancellation, corruption, writer
contention and unsupported capability/version rejection. Freeze expected outcomes
before implementation; conformance is not universal durability certification.

Build wheel/sdist artifacts reproducibly and qualify fresh supported-platform
installations, including core without optional I/O/worker dependencies and separately
installed custom components. Record actual native producer and execution platform,
versions, archive hashes, scope/results and explicit unsupported combinations.
Never substitute an editable/source checkout for installed acceptance or claim a
Linux-produced package installed on Windows is native Linux private testing.

Private R4 source material remains in a local companion. Public examples are
synthetic or explicitly licensed. Preserve unknown known-at, missing eligibility,
TBBO trade-snapshot sampling, UTC daily versus RTH distinctions and scale4
`binary64_exact`/half-even quantization; do not claim original provider coefficient
recovery. Reuse accepted private goldens only with verified source/fixture bindings
and current installed artifact provenance. If extraction changes source behavior,
rerun relevant private acquisition and numerical qualification and record limits.
Input stores stay read-only; output tests use separate disposable destinations.
No paid rows, private paths, secrets or raw receipts enter public docs/artifacts.

## Bootstrap, progress and completion

The parent publishes/readbacks the reviewed handoff, then creates the execution
session with bootstrap authority while GOV-015 awaits assignment acceptance.
Before GOV-015 Done, the new session may fetch/inspect current main, read agreements
and live ownership, and run isolated baseline validation. It must not implement
EQ-121, create companion repositories or change implementation-story status yet.
The parent verifies assignment and closes GOV-015; the child then refreshes actual
Closed/Project Done evidence before the first story pull. This avoids a dispatch/
acceptance dependency cycle. Assignment and implementation readiness are distinct.

Use the dedicated private checkout specified in the local dispatch prompt. Fetch
current main, preserve unrelated checkouts, and configure
Atul Srivastava <102820540+atulsrivas1@users.noreply.github.com> for author and local
committer. Verify published attribution; no Codex co-author trailers. Inspect live
Project/milestones/open PRs, dependencies, companion name/access and active owners.
Run relevant baseline unit/reference/typing/import/registry/license/build checks
under the supported environment; distinguish reused historical evidence from
actual execution. Verify current accepted artifacts/expiry rather than assume
permanent hosting. Verify GOV-015 Done and begin EQ-121 after documented readiness, then pull continuously
within R4.1; no mandatory sprint or automatic reminder.

Maintain current continuity and evidence in each affected repository alongside
each story: API/config/examples/migration/changelog/build/acceptance docs, public
issue/PR, current Project stage and exact resume action. Core SESSION_HANDOFF.md
links component records and release owner; companion records carry concrete code
and artifact fingerprints. If blocked, retain stage and exact dependency, advance
independent authorized preparation, and report the required action when no useful
dependency-ready work remains. Do not poll forever or broaden scope.

Close R4.1 only after all ten canonical stories are actually Done, E18/E19 accepted,
milestone15 zero-open/closed, final separate review/CI/install/publication/readback
evidence and explicit limitations. Delivery is experimental artifact publication,
not stable production or private full-corpus admission. Record the R5 prerequisite
as satisfied and identify the next dependency-ready story, but stop before R5
implementation or launching a new R5 session. Return a concise final handoff with
actual delivered versions/components, evidence links and remaining limitations.

## Kickoff prompt

Complete bounded R4.1 autonomously using this handoff, the architecture, all ten
plans, test strategy, current work agreements and live Project. Bootstrap a
dedicated current-main checkout under the dispatch authority above; parent records
assignment and closes GOV-015. Refresh actual GOV-014/GOV-015 published/Done
evidence before implementation, then start EQ-121.
Create the authorized companion repositories, extract the compatible R4 adapter,
deliver separate extensible I/O/factory/sink contracts, Parquet/DuckDB sinks and
independently installed custom examples. Keep core calculations pure and canonical
issues authoritative across component PRs. Require real lifecycle, separate local
final-head reviews, meaningful independent tests, installed artifacts and same-story
documentation/publication verification. Preserve private sources/history and
accepted precision/PIT limits. Complete EQ-130 release acceptance, then STOP before
R5, providers, remote services, stable registry publication or historical generation.
