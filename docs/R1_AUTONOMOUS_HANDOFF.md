# R1 autonomous execution package

Prepared 2026-10-05 under [GOV-008 #143](https://github.com/atulsrivas1/equity-features/issues/143).
The owner requested a package for a new development chat. This document prepares
that mission; publishing it does not start a chat or calculation implementation.

## Mission and authority

Complete [R1 — Core session packages](https://github.com/atulsrivas1/equity-features/milestone/2):
the two linked prerequisite defects, then EQ-017–026, including implementation,
tests, documentation, issue/Project lifecycle, linked PRs and verified experimental
delivery. Use the [public Project](https://github.com/users/atulsrivas1/projects/2).
Live issue acceptance and Project states remain authoritative.

When the owner starts the execution chat with the kickoff prompt below, routine
implementation, documented technical choices, issue/Project updates, branches,
PRs and merges after existing gates are authorized. Pull continuously, one active
story at a time; no sprint approval, invented deadlines or repeated proceed requests.
Do not implement R2 or later, publish to a public package registry, add concrete
storage/provider adapters or workers, access private/paid data, activate deferred
GOV-005/PR120, change account/profile settings, integrate another product, or
create automations. New feature meaning/scope, destructive actions and changed
public commitments require owner input. Report a genuine blocker explicitly.

## Start here

1. Read [AGENTS.md](../AGENTS.md), [workflow](PUBLIC_DEVELOPMENT.md),
   [delivery policy](DELIVERY_POLICY.md), [continuity](SESSION_HANDOFF.md),
   [package design](PACKAGE_DESIGN.md), [backlog](BACKLOG.md),
   [R0 acceptance](R0_ACCEPTANCE.md), and the live milestone/issues/Project.
2. Inspect checkout status, current HEAD/default branch and open PRs. Work in the
   existing equity-features repository. Preserve unrelated edits; check for concurrent
   changes before every story. Never reset somebody else's work or trust cached status.
3. Read [V1 scope](features/V1_SCOPE.md), [session formulas](features/SESSION_FORMULAS.md),
   [quote formulas](features/QUOTE_FORMULAS.md), [timing policy](features/TIMING_ADJUSTMENT_POLICY.md),
   and all implemented [input](contracts/INPUTS.md), [spec](contracts/SPECS.md),
   [result](contracts/RESULTS.md), [validation](contracts/VALIDATION.md),
   [registry](contracts/REGISTRY.md) and [adapter](contracts/ADAPTERS.md) contracts.
4. Establish the pinned development environment using requirements-dev.txt and
   [compatibility](COMPATIBILITY.md)/[package layout](PACKAGE_LAYOUT.md). Verify
   baseline checks before beginning the first prerequisite. Do not install an
   unrelated latest dependency or use private market data to make tests pass.

Reviewed baseline: main `8f363cbccc91ae32363b856701888f855467aea4`, both
distributions `0.0.1a6`. All 16 R0 EQ stories are closed/Done; R0 milestone closed.
The independent follow-up review reran 170 unit tests, 123 reference cases, strict
typing on 14 source files, boundary/import/registry/license/compatibility checks,
repeat builds and clean wheel/sdist pair installations with both examples. Latest
main Windows/Linux CI succeeded; local Windows artifact hashes matched the
delivery receipt. R0 is a contracts/specification foundation, not a kernel release.
These are dated observations; verify actual live state when resuming.

## Required R0 follow-up repairs

Resolve and verify these before EQ-017. The R0 execution chat was observed actively
repairing both findings in [PR146](https://github.com/atulsrivas1/equity-features/pull/146)
while this package was prepared. Inspect live linked PRs,
default-branch publication, tests and delivery first. Reuse accepted fixes and record
them on #144/#145; do not redo them or race another chat. If repairs remain active,
wait for their gates while completing independent plans. If no repair is delivered
and ownership is available, the execution mission includes implementing the fix.
Accepted R0 reports remain historical evidence; do not
erase them, pretend the defects are already fixed, or reopen unrelated accepted work.
Both subsequent fixes are assigned to R1 explicitly so milestone completion cannot
omit them. Keep their original story/epic references without falsely re-closing epics.

| Prerequisite / provisional points | Reproduction and design | Tests and documentation | Done outcome |
| --- | --- | --- | --- |
| [BUG-001 #144](https://github.com/atulsrivas1/equity-features/issues/144) / 3 | In results.py, FUTURE_MARKET exclusion rejects event_ns<=C although ordinary trade/quote consumption requires event_ns<C. Existing test_results helpers with C=200 reject an excluded event at 200 with FUTURE_MARKET; 201 succeeds. Align exclusions with kind/boundary semantics. | Trade/quote below, at and above C; keep ordinary consumption at C forbidden; preserve closing-auction and completed-bar endpoints; reject contradictory reasons. Update result reference, issue evidence and continuity. | Correct diagnostic evidence, regression coverage, verified versioned delivery; relates to EQ-013 #16. |
| [BUG-002 #145](https://github.com/atulsrivas1/equity-features/issues/145) / 5 | violations() currently accepts np.genfromtxt, pa.input_stream and imported genfromtxt aliases. Scanner-only probes accessed no files; shipped code has no such calls. Use a reviewed backend API surface with alias/qualified-path handling. | Negative backend I/O/alias/path fixtures, positive in-memory array/conversion cases, existing boundary/isolation gates and both OS CI. Update BUILD_DELIVERY.md and limitations. | Prohibited backend reads fail CI; guard remains a development policy, not a sandbox; relates to EQ-009 #11. |

## Architecture and interface evolution

Keep two distributions: equity-feature-contracts / equity_feature_contracts and
equity-features / equity_features. Contracts depend inward on stdlib; optional
columnar bridges and calculation backends remain explicit. Feature code receives
owned in-memory data and supplied configuration; no files, databases, APIs,
credentials, wall clocks, scheduling, multiprocessing or output persistence inside
calculations. Caller owns acquisition, threading and source admission. Public
fixtures/examples remain synthetic or explicitly licensed.

Use existing CanonicalBatch, ConfigSpec and FeatureResult rather than a parallel
untyped API. Proposed modules are session.bars, session.trades, session.quotes and
incremental, with a small explicit orchestration entry point if necessary. Freeze
the concrete callable signatures in EQ-017's plan before coding; export only actual
implemented behavior. Family calls may accept caller-supplied compatible prior-close,
interval or quote-seed evidence explicitly, without fetching/calculating dependencies.
Missing one enrichment must not invalidate unrelated available features.

Preserve UTCns int64, exact scaled price coefficients/currency, stable event IDs
and tie order, supplied calendar/session/auction policies, missing/null/empty/zero
distinctions, C/K/E and reconstruction identities, adjustment basis and bounded
evidence. Never silently sort/deduplicate, invent coverage, fill gaps, quantize,
derive real notional from close*volume, or admit future knowledge.

R0 contains intentional temporary restrictions that R1 must evolve through linked,
versioned contract changes, tests and docs:

- Capabilities currently rejects every true execution flag; registry discovery and
  verify_registry.py enforce all flags false. Advertise batch/update/restore/merge
  only for accepted implementations; retain false flags for every unimplemented R2
  and custom feature. Update checks without removing the requirement-to-implementation
  invariant. Reserved 39 IDs and existing formula meaning remain stable.
- Interval OHLCV, sampled observation arrays/state-count summaries and top-K evidence
  need typed structured outputs. FeatureColumn currently has only scalar/breadth
  types. Choose documented typed tables/structures, preserving key, quality,
  provenance, schema and Arrow interoperability; do not hide structures in JSON
  strings, invented scalar IDs or untyped dictionaries. Exact representation is a
  story-owned design choice; migrations and registry output metadata must agree.
- Extend config deliberately for quote expiry/seed policy, K, evidence limits and
  per-family requirements if existing scalar parameters cannot express them safely.
  Canonical serialization/digests must include all numerical and admission choices.
  No broad R3 custom execution or general composition API is needed.
- Keep stdlib import isolation meaningful: optional numerical modules must not load
  backends during dependency-light discovery. Update runtime pins/extras and CI only
  with qualified evidence. Existing qualified baseline is CPython3.12 x64 on
  Windows/Linux, NumPy2.2.6/PyArrow20.0.0.

Build a simple checked implementation first. Python exact-integer reference
reductions are useful for correctness; numerical hot paths should use justified
columnar kernels without int64 product/sum wrapping. Float64 outputs require
documented absolute/relative tolerances derived from arithmetic, not arbitrary
tolerances hiding defects. Record copying/materialization costs. No unmeasured
performance claim, premature Rust rewrite or automatic parallelism. Broad benchmark
qualification remains R3; R1 still needs bounded-state evidence and correctness.

## Story plans and pull order

Points are provisional Fibonacci effort estimates, not time commitments. Confirm
or revise each in its story plan and Project when pulling. Total: 76 R1 story points
plus 8 prerequisite points; estimates do not imply a release date. Before code,
create docs/stories/EQ-NNN_PLAN.md (and a corresponding BUG plan) mapping live
acceptance to prerequisites, first action, design, open decisions, independent tests,
documentation, points and observable done state. Resolve routine choices autonomously
with recorded reasoning; ask only for consequential scope/public-commitment changes.

Default sequence: verify/reuse or complete BUG-001 and BUG-002, then EQ-017–026. Sequential completion keeps ownership
simple even where branches could be independent. Prerequisites below are additional
implementation guidance, not a replacement for live acceptance criteria.

| Story / points / prerequisites | First action and design | Open decisions to settle | Required tests | Documentation and done state |
| --- | --- | --- | --- | --- |
| [EQ-017 #21](https://github.com/atulsrivas1/equity-features/issues/21) / 8 / both bugs, R0 | Map 12 bar/price IDs to EQ-002 references. Define bars API, compatible supplied prior-close evidence and typed results; implement exact reductions and independent readiness. | Actual versus proxy price/notional representation, output scales/tolerances, input coverage scope and prior-close binding; capability evolution. | Hand-calculated OHLCV, actual notional versus proxy, ranges/returns/gaps, positive prior close, null/zero/missing/empty, incompatible units/basis/identity, integer overflow, C/K/E boundaries. | Plan, bar API/example, contract migration and registry capabilities, changelog/continuity. 12 IDs callable with truthful quality and verified artifacts. |
| [EQ-018 #22](https://github.com/atulsrivas1/equity-features/issues/22) / 5 / EQ-017 | Implement two structure IDs using supplied intervals and whole completed bars; reuse bar reductions and explicit typed keyed structures. | Structured output schema; incomplete interval versus full-session denominator coverage; interval overlap and bar-straddling error policy following formulas. | Early close, auctions, exact boundaries, empty/zero intervals, nonaligned whole-bar windows, missing buckets, no time leakage and independent volume share. | Interval API/config/result examples, decision and registry metadata. Both IDs supported without proration or invented coverage. |
| [EQ-019 #23](https://github.com/atulsrivas1/equity-features/issues/23) / 8 / EQ-017 contracts | Map five aggregate IDs; reduce eligible supplied trades with checked counts/volume/products/notional, then ratios. | Exact notional/output scaling, independent readiness when payload fields absent; accumulator representation suitable for later updates. | Independent count/volume/notional/VWAP/mean-size fixtures, ineligible prints, no eligible observations versus missing source, duplicate/order/tie errors and overflow before wrap. | Trades API/example, units/tolerances and capability metadata. Five IDs accepted, no bar-derived VWAP substitution. |
| [EQ-020 #24](https://github.com/atulsrivas1/equity-features/issues/24) / 5 / EQ-019 | Implement bounded top-K by size and accepted stable global tie key; preserve source/event provenance and legal disjoint reduction design. | K bounds, evidence-limit interaction, identity overlap detection and rank serialization/merge prerequisites; bounded summary cannot alone prove all populations disjoint. | K=1, ties, K larger than eligible count, invalid K, repartitioning, overlap/duplicate rejection and bounded retained state. | Top-K API/evidence schema, merge preconditions and examples. One ID with deterministic, bounded evidence. |
| [EQ-021 #25](https://github.com/atulsrivas1/equity-features/issues/25) / 8 / EQ-017 contract evolution | Implement sampled-spread and state-count IDs from EQ-003; keep sampled versus continuous input identity explicit. | Typed observation/summary schema and exact distribution materialization bound; exact quantiles are batch results, not an unbounded stream promise. | Normal/locked/crossed/invalid, midpoint-bps/absolute spread independent expectations, zero valid samples, null sizes, equal-time order, sampling labels, missing versus empty, masks and precision. | Sampled quote API, distribution ownership/copy costs, streaming limitations and registry metadata. Two IDs callable without continuous-coverage claims. |
| [EQ-022 #26](https://github.com/atulsrivas1/equity-features/issues/26) / 13 / EQ-021 | Implement one continuous time-weighted spread ID with supplied seed/inactive/unknown initial state, expiry and exact duration accounting. | Concrete supplied seed contract/config; weighted float tolerance and duration overflow policy; duration coverage result structure. Preserve EQ-003 semantics. | Hand-integrated durations, pre-open seeds, expired seeds, unknown/inactive starts, invalid transitions, equal-time updates, expiry/cutoff/session endpoints, zero valid duration, sampled rejection and duration conservation. | Continuous quote API/state diagram/example, eligibility/coverage and config migration. One ID with explicit valid/invalid/expired/unknown duration and no carry over gaps. |
| [EQ-023 #27](https://github.com/atulsrivas1/equity-features/issues/27) / 8 / EQ-017–022 | Reuse numerical/admission reductions in explicit bounded update/snapshot/finalize objects for supported modes. | Supported-feature matrix, cutoff advancement and late-correction replay policy; provenance/coverage across chunks without unbounded input-binding growth. Batch exact sampled quantiles remain unsupported incrementally unless bounded exact semantics are established. | Multiple chunks, order across boundaries, wrong session/config/source, no earlier snapshots after later ingestion, repeated finalization policy, future mutations, bounded state scaling and unsupported capability errors. | Lifecycle API/example and capability matrix. Actual supported streaming modes match documented semantics; no source polling. |
| [EQ-024 #28](https://github.com/atulsrivas1/equity-features/issues/28) / 8 / EQ-023 | Define immutable versioned in-memory snapshots of necessary sums/compensation/order/seed/expiry/top-K and provenance, then restore. | Float serialization, state schema/version compatibility, alias ownership and sufficient replay/continuation identity. No files/pickle/code execution. | Mid-session export/restore/continue parity, caller mutation isolation, corrupted/truncated/incompatible config/schema/math/backend/source state, integer/float edges and bounded representation. | State contract/migration/errors and executable example. Restored supported state has the same numerical/evidence behavior and rejects incompatible identity. |
| [EQ-025 #29](https://github.com/atulsrivas1/equity-features/issues/29) / 5 / EQ-023–024 | Build deterministic repartitioning tests for batch/update/restore and only mathematically legal merges. | Disjointness proof responsibility, ordered bar merge and nonmergeable quote temporal state; exact versus float parity contract. | Chunk sizes 1/small/large, uneven partitions, skew/ties, cross-boundary events, duplicate/overlap/cutoff/config rejection, merge-order tests for associative reducers; reject arbitrary ordered-state merge. | Parity matrix and supported merge proofs/limitations. Every advertised mode has independent equivalence evidence. |
| [EQ-026 #30](https://github.com/atulsrivas1/equity-features/issues/30) / 8 / EQ-017–025 | Audit all 23 R1 IDs against frozen formulas and independent oracle cases; close uncovered edges rather than duplicating implementation. | Remaining test gaps, tolerated float behavior, complete public acceptance matrix and known limitations. | Ties/nulls/empty/missing/zero, malformed prints/quotes, auctions/early close, int64/decimal limits, no future leakage, adjustments/identity, both OS installed packages and examples; all R0 regressions preserved. | R1 acceptance report, release notes, reproducible validation index and final handoff. Ten stories plus prerequisite fixes accepted with actual verified delivery; no R2 or stable-registry claim. |

## Tests, review, release and durable memory

Baseline commands (use the selected pinned interpreter; pytest is not required):

```text
python -m unittest discover -s tests/unit
python tools/verify_session_examples.py
python tools/verify_quote_examples.py
python tools/verify_history_examples.py
python tools/verify_context_examples.py
python tools/verify_timing_examples.py
python tools/verify_imports.py
python tools/verify_compatibility.py
python tools/verify_release_policy.py
python tools/verify_registry.py
python tools/check_boundary.py
python -m mypy --strict packages/contracts/src packages/features/src examples/in_memory_adapter.py
python tools/build_foundation.py
```

Extend unit/typing/build/example gates for new modules and actual installed kernels.
Keep planning checks from .github/workflows/docs.yml and both workflows green.
Existing 123 reference cases are independent specification evidence; production
tests must invoke production APIs and compare to hand-derived/exact oracles.
Do not increase fixture counts merely to claim progress. Existing tests evolve
only with documented contract changes, never by weakening checks to suit code.

For each item:

1. Establish dependency/acceptance readiness, plan and actual live status; use a
   short-lived codex/ branch and linked draft PR. Attach every created PR to the chat.
2. Update API/formula/decision/examples, issue checklist/evidence and continuity
   alongside implementation. Preserve mathematical definitions and expose intentional
   representation/API version changes with explicit migrations.
3. Follow Backlog -> Ready -> In progress -> Code review -> Test -> Ready to release
   -> Released -> Done. Review the diff and fix findings before formal acceptance.
   Owner-deferred PR120 remains untouched. Author self-review plus CI remains the
   agreed policy; do not claim another reviewer or bot ran.
4. Wait for required checks on the exact final PR head, then merge according to
   repository policy. Verify published main bytes and post-merge CI. Source merge
   alone does not complete an implementation story.
5. Continue the [declared experimental CI artifact channel](BUILD_DELIVERY.md).
   Version APIs honestly; maintain exact cross-distribution dependencies and update
   hardcoded version/build/import/example checks together. The artifact name may
   retain foundation for compatibility, but metadata/docs must identify actual R1
   capabilities. Download main bundles; inspect manifests/commit/archive content and
   SHA256, clean-install both wheel/sdist pairs, run installed tests and examples.
   Record OS/runtime, artifact URLs, actual expiry and rebuild path. No PyPI/tagged
   stable/public registry release is authorized. Do not overwrite published version
   meaning silently. Keep Ready to release if actual delivery remains unverified.
6. Record commands/results, decisions, failed attempts and checked recoveries,
   reviewer limitations, release identity and next action in SESSION_HANDOFF.md.
   Close an item only at verified Done. Reconcile epic checklists honestly: E04
   can finish after its ten children; E03 still has R3 EQ-093. Bugs relate to older
   epics without authorizing unrelated later work.

## Exit and stop boundary

Publish docs/R1_ACCEPTANCE.md linking the 23 IDs to implementations, fixtures,
capability/mode support and each accepted story/fix. Include exact source/version,
typing/reference/unit/parity evidence, both OS CI, actual downloaded artifacts,
clean-install execution, review identity, precision/copy/bounded-state limits and
remaining unsupported behavior. There is no fixed test-count target or speed claim.

Close R1 milestone only after all ten EQ stories and both prerequisite defects meet
acceptance/delivery; verify its live contents before closing. Update E04 only when
all its children are delivered. Identify EQ-027's actual dependency readiness,
leave R2 implementation unstarted, and stop. Do not execute the entire roadmap.
On interruption, preserve committed reviewable work, actual statuses, failures,
remaining gates and exact resume commands; do not claim completion because time
or context ran out. No autonomous follow-up scheduler is required by this package.

## Copyable kickoff prompt

> Complete equity-features R1 autonomously in the existing repository. First read
> AGENTS.md, docs/R1_AUTONOMOUS_HANDOFF.md, docs/SESSION_HANDOFF.md, the workflow,
> delivery policy, design/backlog, formula/contracts and live GitHub milestone/issues/
> Project. First verify/reuse or complete BUG-001 #144 and BUG-002 #145; the R0
> repair chat may already have delivered them, so do not duplicate active work.
> Then complete EQ-017–026 one
> item at a time. The handoff defines provisional points, design/open decisions,
> tests, documentation, exit outcomes and delivery gates. You are authorized to
> implement, document, manage issue/Project states and create/merge linked PRs
> after existing review/test/delivery gates. Preserve completed R0 evidence,
> unrelated work and deferred PR120. Keep calculations source-independent,
> synthetic examples, exact units/timestamps and causal/coverage semantics.
> Evolve R0 capability/structured-result contracts explicitly rather than bypassing
> them. Deliver and verify experimental main wheels/sdists and installed behavior
> before Done; no public registry publication, private/paid data, account changes,
> concrete adapters/workers, other-product integration, automations or R2+ work.
> Maintain durable evidence/decisions/failures/resume steps. Continue without
> repeated proceed requests. Stop after verified R1 acceptance or a genuine blocker
> requiring owner input; report truthful results and limitations.
