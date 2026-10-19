# Equity feature expansion and measured execution roadmap

Owner-requested planning, October 19, 2026. [GOV-031](https://github.com/atulsrivas1/equity-features/issues/464); [live Project](https://github.com/users/atulsrivas1/projects/2). The owner requested releases, epics and stories following the equity feature gap discussion, then emphasized correctness, performance, independence, parallelism and efficient use of available resources. This selects planning scope R17–R21; it does not start implementations or select live feed operations. Earlier no-R17-selection statements remain historical.

The six requirements are release gates: correct independently verified mathematics; calculations independent of data sources; independent readiness for unrelated features; dependency-correct parallel work; efficient use of available CPU/memory/I/O within explicit reserves and bounds; and measured direct/end-to-end performance with full result parity. More workers or higher CPU usage alone do not qualify. No timing, speed ranking, due date or capacity guarantee is invented.

## Releases and epics

| Release | Outcome / epic | Stories | Planning dependency |
| --- | --- | --- | --- |
| [R17](https://github.com/atulsrivas1/equity-features/milestone/21) | [R17 — Intraday equity foundations](https://github.com/atulsrivas1/equity-features/issues/465) | EQ-136–EQ-141 | GOV-031/GOV030 publication and accepted R16 baseline |
| [R18](https://github.com/atulsrivas1/equity-features/milestone/22) | [R18 — Dependency-driven execution and resource efficiency](https://github.com/atulsrivas1/equity-features/issues/466) | EQ-142–EQ-146 | Exact story dependencies; earlier release acceptance at combined delivery gate |
| [R19](https://github.com/atulsrivas1/equity-features/milestone/23) | [R19 — Trend, momentum and money-flow features](https://github.com/atulsrivas1/equity-features/issues/467) | EQ-147–EQ-152 | Exact story dependencies; earlier release acceptance at combined delivery gate |
| [R20](https://github.com/atulsrivas1/equity-features/milestone/24) | [R20 — Relative statistics, realized volatility and robust anomalies](https://github.com/atulsrivas1/equity-features/issues/468) | EQ-153–EQ-157 | Exact story dependencies; earlier release acceptance at combined delivery gate |
| [R21](https://github.com/atulsrivas1/equity-features/milestone/25) | [R21 — Equity tape, quote and path analytics](https://github.com/atulsrivas1/equity-features/issues/469) | EQ-158–EQ-163 | Exact story dependencies; earlier release acceptance at combined delivery gate |

Release order is planning/delivery order, not a runtime barrier. Within each calculation job, only actual required operands, state order, coverage and publication ownership constrain work. Later pure-kernel story specifications may be prepared independently where their listed prerequisites allow, but one active implementation story remains the default.

## Implementation order and first slice

1. Establish interval, initialization, availability and direct dependency contracts before kernels. This prevents incorrect daily-to-intraday substitution and false serial edges.
2. Deliver reusable preparation and independent EMA/RSI/ATR/band branches, with direct/current-worker baselines and actual input bindings. Parameter changes alone are not new kernels.
3. Use the baseline to remove demonstrated repeated scans/copies or coarse serialization, then qualify resource profiles. Add later families through the same exact-output, independent-oracle and measurement gates.

Every implementation story must publish a concrete reviewed pre-code contract before Ready, including open formula choices and independent fixtures. Numerical identity, supported batch/update/restore/merge/replay behavior, requested-output closure, resource lifetime, documentation and benchmark adoption criteria are mandatory. Final release acceptance stories audit child evidence rather than replace it.

## Resource and parallelism contract

Use a single admission policy across source preparation, calculations, transport and publication. Detect usable capacity at admission, account for OS/other-job reserves and native/backend thread pools, and bound memory, in-flight work and queues. Declare reservations, observations and enforced limits separately. Share immutable compatible inputs using exact source/configuration/revision/cutoff identities. Keep recursive state ordered within its identity; dispatch independent symbols or sufficiently large independent families when ready. Preserve legal sink ownership and backpressure.

Measure wall time and full-pipeline throughput/latency first, plus core-seconds/utilization, peak parent+child memory, copies/IPC, queue/lock waits, output transport and cold/warm startup. Freeze workload, full-result parity checks and adoption threshold before measuring. Compare supported concurrency levels; preserve a fallback when wider execution loses. No automatic use of all memory, unbounded fan-out, hard-enforcement claim or fastest-library claim follows.

## Repository and overlap boundaries

Canonical scope and issue IDs live in equity-features. Pure contracts/calculations belong here; adapter/input/sink changes belong in equity-feature-io, and dispatch/resources/publication changes in equity-feature-workers. Actual companion PRs must link the canonical issue; do not create duplicate feature stories in each repository. New IDs are not registry implementations: the accepted 39-ID built-in catalog stays unchanged until separately reviewed feature specifications and releases extend it.

GOV030 #462 / PR463 remain the independent dependency inventory/planning delivery, with their own current review/CI/publication gates. This roadmap does not supersede or close them. Source-derived detailed comparison material stays local; public issues contain original generic requirements, not copied proprietary code/formulas or thresholds. Independent fixtures use synthetic or explicitly licensed data.

Existing E24 #456 and LIVE-001–004 #457–460 keep the persistent live orchestration/feed/replay/trader-delivery scope. R18 is bounded execution of the selected supplied-input workloads; it neither duplicates LIVE-002 nor activates a live feed/SLA/deployment. Providers, optional witnesses, SEC-001, research/combined-C1 coordination, paused automation and all other deferred work retain their existing ownership/state. Options exposures/surfaces, scanner/watchlist/strategy policies and forward labels are excluded from this equity-kernel roadmap.

## Delivery and review

All five epics and 28 implementation/acceptance stories are initially Backlog/unassigned, with no due dates. GOV-031 is the planning delivery only. The live Project owns current status. Use Backlog -> Ready -> In progress -> Code review -> Test -> Ready to release -> Released -> Done with documented entry/exit evidence. New planning allocations do not reopen accepted releases or mark any feature implemented.

Separate final-head review under docs/CODE_REVIEW.md, applicable CI, publication to the default branch and actual readback remain required for GOV-031. Existing bounded GOV030/R16 local-review grants are not treated as blanket authorization for these new releases. No separate review or numerical/benchmark result is claimed by author checks. Implementation later requires actual prerequisite acceptance and the applicable review arrangement.

## Story plans and machine-readable allocation

- [R17 detailed story plans](R17_RELEASE_PLAN.md).
- [R18 detailed story plans](R18_RELEASE_PLAN.md).
- [R19 detailed story plans](R19_RELEASE_PLAN.md).
- [R20 detailed story plans](R20_RELEASE_PLAN.md).
- [R21 detailed story plans](R21_RELEASE_PLAN.md).

[EQUITY_EXPANSION_ROADMAP.json](EQUITY_EXPANSION_ROADMAP.json) records exact issue, release, points, ownership and dependency allocations. Points are provisional complexity, not days.

[Author validation](stories/GOV-031_AUTHOR_VALIDATION.json) records allocation/dependency/link/Project readback and gate checks. The necessary planning-count extension and narrowly normalized workflow-equivalence test preserve the original immutable CI baseline; no routing, package job, registry or calculation behavior changes. Separate review and delivery gates remain pending.
