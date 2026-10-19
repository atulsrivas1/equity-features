# R17 autonomous execution handoff

Owner direction, October 19, 2026: prepare the R17 handoff, then work on R17. This selects bounded R17 execution once its real prerequisites/review gates pass; earlier preparation-only statements are historical. No new chat, schedule or R18 implementation is requested. [Epic E25](https://github.com/atulsrivas1/equity-features/issues/465), [milestone21](https://github.com/atulsrivas1/equity-features/milestone/21), [GOV-031](https://github.com/atulsrivas1/equity-features/issues/464), [planning PR498](https://github.com/atulsrivas1/equity-features/pull/498).

Start with AGENTS.md, PROJECT_KNOWLEDGE.md, SESSION_HANDOFF.md, PUBLIC_DEVELOPMENT.md, DELIVERY_POLICY.md, knowledge/BACKLOG_WORKFLOW.md and live issue/Project evidence. Read [release plans](R17_RELEASE_PLAN.md), [inputs](R17_INPUTS.json), [test strategy](R17_TEST_STRATEGY.md), [initial contract proposal](stories/EQ-136_PLAN.md) and [existing historical math](features/HISTORICAL_FORMULAS.md). Chat memory and old green receipts do not establish current acceptance.

## Mission and boundaries

Deliver source-independent intraday foundations: explicit finalized-bar/interval/initialization contracts; compatible reusable rolling preparation; independent EMA, RSI, ATR and price-band outputs; qualified input/worker bindings; and reproducible correctness/performance/release evidence. Correctness, independent readiness, dependency-correct parallel work and bounded efficient use of available resources are mandatory. Do not promise a speed ranking or allocate all free memory. Use original specifications and synthetic/licensed fixtures; comparison-derived private material stays local.

Pure calculations do not fetch, read databases/files, consult wall time, schedule or publish. Calculation changes live in equity-features; normalized I/O changes in equity-feature-io; dispatch/resources/publication in equity-feature-workers. Canonical EQ-136–141 remain in this repository and companion PRs must link them. The current source pins in R17_INPUTS are inspection starting points, not accepted R17 artifacts. Do not repin automatically if a repository changes; inspect relevant delta and renew evidence.

## Admission and review

GOV030#462/PR463 and GOV031#464/PR498 publication/readback are actual prerequisites of EQ136; at handoff preparation both PRs were draft/open. R16's closed milestone is not substituted for those publication gates. Author planning tests do not replace final-head separate review. No R17 story is Ready simply because its issue exists or the owner requested execution.

The owner has selected R17 work, but existing GOV030/R16 bounded local-review grants are not treated as a new grant for PR498 or R17. Under [CODE_REVIEW.md](CODE_REVIEW.md), obtain a supported separate review or explicit bounded alternative-review authorization, then record actual reviewer/head/checks/findings/limits. Prepare the concrete packet first; permission is not a passed review. A useful single bounded grant covers PR498's planning packet, this handoff, EQ136–141, necessary companion qualification changes and final R17 delivery. It grants no R18–R21 implementation or operating scope.

Until the review/publication prerequisites pass, continue independent planning, source/caller inspection and synthetic reference preparation under GOV031. Do not silently skip gates, leave active implementation in Backlog, merge an unreviewed head, or label the mathematical proposal accepted. Complete prerequisite planning deliveries through the exact lifecycle using actual current evidence.

## Continuous pull order

| Story | Issue | Complexity | First action / accepted end state |
| --- | --- | --- | --- |
| EQ136 | [#470](https://github.com/atulsrivas1/equity-features/issues/470) | 5 | Freeze original interval/math/output/state/availability contract and independent expected fixtures. Review and publish it; no runtime benchmark is required for a specification-only change. |
| EQ137 | [#471](https://github.com/atulsrivas1/equity-features/issues/471) | 8 | Implement only accepted compatible rolling preparation. Verify independent direct-window results, precision, eviction and bounded memory before exposing reuse. |
| EQ138 | [#472](https://github.com/atulsrivas1/equity-features/issues/472) | 8 | Implement EMA/RSI/ATR as independent branches over admitted closes/OHLC. Preserve actual recurrence order, warm-up, corrections and declared capability parity. |
| EQ139 | [#473](https://github.com/atulsrivas1/equity-features/issues/473) | 5 | Implement price moments/bands with cell-specific availability. No RSI/ATR prerequisites; zero band width does not invalidate valid middle/upper/lower cells. |
| EQ140 | [#474](https://github.com/atulsrivas1/equity-features/issues/474) | 5 | Qualify actual source/input bindings and dispatcher support. Missing unrelated fields/references must not block a compatible output; no new provider or live input grant. |
| EQ141 | [#475](https://github.com/atulsrivas1/equity-features/issues/475) | 5 | Audit every child and release the exact qualified cross-repository artifact set with direct/worker baselines, both-platform installed evidence and actual publication/readback. |

Points are provisional complexity, not dates. Follow each story's exact dependencies in the allocation JSON; EQ139 can be mathematically independent of EQ138 even though continuous pulling normally completes one implementation story at a time. Ready each story only after accepted dependencies and a concrete reviewed pre-code packet, then Ready -> In progress with actual ownership. Use short-lived codex/ branches and linked draft PRs early. Record Code review -> Test -> Ready to release -> Released -> Done only from actual evidence; rework returns to the appropriate stage.

## Practical implementation constraints

1. Select requested outputs, then compute their exact prerequisite closure. Share a source-compatible immutable bar view and equivalent moments/TR where useful. Do not model one task per scalar or add a SMA -> EMA -> RSI -> ATR chain.
2. State ownership includes instrument, grid/interval, price/action basis, anchor/session mode, algorithm/period, cutoff and source revision. Consecutive observations in a recurrence are ordered. Parallelize sufficiently large independent families/symbols; unresolved aliases or dynamic producers block refinement of that path, not unrelated admitted calculations.
3. Introduce no new executor or resource default merely to implement kernels. Reuse the current supported worker modes and budget contracts. Preparation, IPC, native threads, queues and sink publication count in one CPU/memory/I/O budget; distinguish declared, observed and enforced limits.
4. Observe performance while implementing, not after all features are built. Freeze expected outputs and workload/adoption criteria before timings. Preserve slower runs and a qualified fallback; correctness/availability/evidence parity precede optimization adoption. R18 owns wider scheduler/resource refinements, not this foundation release.
5. Current daily APIs and their accepted 39-ID registry remain compatible. Candidate intraday IDs are proposals until EQ136 freezes them. Do not relabel daily bars, introduce silent new math, or claim update/restore/merge because a general extension interface exists.

## Stop and final delivery

Stop after verified R17 acceptance; do not start R18, live-provider delivery, scanner/strategy policies, options Greeks/surfaces, paid/private acquisition, hosting, stable registry publication, account/protection administration, automation or destructive cleanup. Existing E24/LIVE001–004, provider/research/security/witness deferrals and paused automation retain their scope.

Release evidence must identify exact core/I/O/worker heads and public artifact versions, current applicable candidate/main checks, clean installed Windows/Linux results, independent review, numerical/state/temporal fixtures, benchmark workload/configuration and repeated results, limitations and actual Git/publication readback. A merged implementation waiting for release is Ready to release. Close E25 only after every selected child is Done and the declared user channel has been verified. Update backlog, API/math/examples/decisions/release notes and handoff in each story.

## Copyable kickoff

Continue owner-selected R17 only. Read this handoff, linked contract/test/input records and live Project. Preserve unrelated work. Recheck GOV030/GOV031 review/current CI/publication prerequisites and the applicable separate-review authorization; finish those gates before admitting EQ136. Prepare/review exact mathematics and independent fixtures before kernels. Pull EQ136–141 by satisfied dependencies, one active implementation story at a time, keeping pure calculations, independent readiness, bounded efficient resource use and measured full-result parity. Record actual review/CI/installed artifacts/publication evidence and exact lifecycle; do not invent progress, benchmark results or deadlines. Stop after verified R17 delivery.
