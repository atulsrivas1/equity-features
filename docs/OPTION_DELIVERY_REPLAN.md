# Option delivery replan under the coordinator working agreement

October 20, 2026. [GOV036 #572](https://github.com/atulsrivas1/equity-features/issues/572) replans the option portion of the full matrix under the [coordinator agreement](COORDINATOR_WORKING_AGREEMENT.md), using the same feature-bearing three-layer delivery model as [equities](EQUITY_DELIVERY_REPLAN.md). It supersedes the delivery arrangement in the [GOV033/PR524 option proposal](https://github.com/atulsrivas1/equity-features/pull/524), preserving historical evidence and existing numbered issues rather than creating a competing option backlog. It does not change the equity release allocation or take ownership of EF1/R18.

The matrix defines capability coverage, including features, scanners, watchlists, strategies, scores, lifecycle and outcomes. Product names are consumer views. Every capability needs an appropriate library/module owner; shared mathematics is reused. This document is a planning proposal until its independent review, CI, publication and tracker reconciliation pass. Implementation stories remain Backlog. Verified EQ141/EQ146 acceptance and reviewed story prerequisites still precede option implementation; all EF releases need not finish first.

## Repository and library ownership

Use the existing three repositories. Repository names do not limit supported asset classes. Separate library ownership does not require a separate repository. These new pure package paths are planning decisions; no packages, repositories or registry names are created by this document. EQ182 freezes exact distribution/import names and inward contract dependencies before implementation, preserving existing installations/APIs. Existing accepted APIs are never silently moved.

| Repository | Responsibility and write boundary |
| --- | --- |
| [equity-features](https://github.com/atulsrivas1/equity-features) | Canonical roadmap and pure option, microstructure, volatility and exposure packages; existing optional strategies/labels; no acquisition/storage/orchestration in calculations. |
| [equity-feature-io](https://github.com/atulsrivas1/equity-feature-io) | Option input/reference conversion, shared SDK contracts and result sinks; reuse qualified DuckDB adapter/sink components. |
| [equity-feature-workers](https://github.com/atulsrivas1/equity-feature-workers) | Bounded selected-output execution, compatible shared preparation, ordered state and serialized persistence. |

| Library | Planned package or existing home | Capability ownership |
| --- | --- | --- |
| option-features | packages/option-features (planned) | Contract/reference, pricing/Greeks, bounded IV inversion, liquidity/chain evidence and option-specific activity primitives. |
| market-microstructure | packages/microstructure (planned) | Shared execution, quote alignment, flow/concentration and cross-asset alignment; reuse qualified equity primitives without relocating accepted APIs. |
| volatility-features | packages/volatility (planned) | Strips/surfaces/tenors, skew/curvature/term structure, move scales and compatible histories/comparisons. Equity RV remains equity-owned and reused under exact conventions. |
| exposure-features | packages/exposure (planned) | Declared contributions, grids, numerical changes and explicit counterfactuals. |
| market-screeners, strategy-context, signal-lifecycle | packages/strategies (existing optional package) | Versioned scans, watchlist membership, strategy profiles, component/meta scores, level filters and deterministic lifecycle policies. |
| outcome-labels | packages/labels (existing optional package) | Separately mature move observations, realized fractions and descriptive calibration. |

## Feature releases

Retain R25-R29 and E33-E37 identities; their delivery contracts are replanned below. Setup/mocks are inside feature tracks. Every release requires all three layers, independent fixtures, exact dependency/artifact pins, integration and an actual local browser demonstration of computed/stored results. No product UI, public deployment or API is a release requirement.

| Release | Feature outcome | Epic | Acceptance |
| --- | --- | --- | --- |
| [R25](options/R25_DELIVERY_PLAN.md) | Option reference, pricing, Greeks and implied volatility | [E33](https://github.com/atulsrivas1/equity-features/issues/526) | EQ-187 |
| [R26](options/R26_DELIVERY_PLAN.md) | Option flow, activity and execution | [E34](https://github.com/atulsrivas1/equity-features/issues/533) | EQ-193 |
| [R27](options/R27_DELIVERY_PLAN.md) | Volatility surfaces, tenors and comparisons | [E35](https://github.com/atulsrivas1/equity-features/issues/540) | EQ-200 |
| [R28](options/R28_DELIVERY_PLAN.md) | Option exposure contributions, grids and changes | [E36](https://github.com/atulsrivas1/equity-features/issues/548) | EQ-206 |
| [R29](options/R29_DELIVERY_PLAN.md) | Option scanners, watchlists, strategies and complete coverage | [E37](https://github.com/atulsrivas1/equity-features/issues/555) | EQ-211 |

## Contracts, dependencies and parallel work

The coordinator prepares and reviews exact release contracts and independent conformance fixtures first. Freeze selected output identities, formulas, units, timing/known-at, initialization, model/exercise/settlement, reference and population admission, missingness/errors and actual supported batch/update/restore/merge/replay modes. Distribution/API dependency versions, request/result schemas, source/sink mapping, repeat-write policy and resource ownership are part of each handoff. Unresolved semantics block the affected output before Ready.

After prerequisites and contract review, use three fresh layer workers with explicit repository/path write boundaries and minimal shared context. I/O and worker implementations can use conformance fixtures while calculation implementation proceeds. Integration waits for actual compatible producers. Do not convert final acceptance dependencies into a requirement for serial authoring, or remove true numerical/state dependencies to claim parallel execution. Contract defects return to the coordinator; workers do not redefine shared boundaries.

R26 flow, R27 volatility and R28 exposure are distinct branches using compatible R25 foundations. No R26-to-R27-to-R28 whole-product runtime barrier is implied by numbering. GEX from supplied gamma does not wait for VEX-only model inputs or an IV solver. Pure equity RV has no option-strip dependency. Ordered signs/recurrences/history corrections, declared populations, target brackets and sink commits retain their true barriers. R29 origin-time scans do not wait for mature labels. EQ211 final full-coverage acceptance includes equity producer and delayed-outcome receipts.

Existing dependency lists are delivery/admission gates. [Allocation JSON](plans/option-delivery-replan.json) gives the effective planned graph and story-specific changes. EQ186/187 gain the explicit reference-feature producer; flow integration gains the activity producer. EQ210 becomes local composition and loses the optional service EQ084 gate; it retains separately mature outcome integration. R29 gains distinct strategy, I/O, worker and delayed-calculation stories. No equity dependency is waived.

## Data flow and integration

Qualified source DuckDB or explicitly labelled synthetic input -> input adapter -> workers -> pure feature/policy libraries -> output sink -> a separate output DuckDB. Workers invoke adapters and libraries and pass canonical results to sinks. Source conversion and persistence remain outside pure libraries. Reuse the existing catalogue-backed Parquet route where suitable; arbitrary DuckDB tables require a separately qualified mapping. Source paths/schema/rights/clock/coverage and output path/schema/run/provenance/repeat-write contracts are frozen before actual data operations. This planning reads no datasets and creates no database.

Use suitable owner-designated source data only after qualification; synthetic gaps stay labelled and do not invent observed liquidity, OI, coverage, freshness or known-at evidence. Distinguish supplied Greeks from calculated Greeks, missing from observed zero, metric readiness from full-grid completeness and calculation completion from publication visibility.

## Matrix coverage and scope changes

[Coverage accounting](OPTION_MATRIX_COVERAGE.md) and the private exact-identity ledger account for the pinned finite catalogue and all command roles. This is planning ownership, not an assertion that existing libraries implement them. All 30 existing EQ182-211 stories are retained once; six missing scopes are explicitly added: reference/liquidity/chain features, activity/execution baselines, strategy/context/meta composition, policy I/O, policy workers and delayed calibration. Their allocation and original acceptance criteria are in the JSON and per-release documents. Historical PR524 remains the predecessor and its unrelated equity/product discussion is not imported as option implementation scope.

Typed fields, aliases, metadata, wrappers and parameters are not separate mathematical features. The source ledger retains unresolved typed writes/dynamic dispatch and conservative unions; exact output-to-producer/dependency qualification remains EQ182 and the corresponding domain contract stories, with EQ211 final reconciliation. An unresolved or deferred capability cannot disappear or count as delivered full coverage. Record a numbered residual and explicit owner/scope decision where admission requires resolution; never silently exclude a matrix item to pass acceptance.

## Review and release gates

Coordinator review precedes any layer push; every PR has a fresh independent read-only reviewer distinct from its author, actual final-head coverage and applicable CI. Record reviewer identity/findings/rechecks and limitations. After integration, compare direct libraries, installed workers and stored readback against independently expected synthetic/licensed results, including values/null/status/quality/evidence/identity and missing/invalid/future/revised cases. Qualify actual supported wheel/sdist combinations on Windows/Linux, core-only optional dependency isolation and exact compatible artifacts before delivery claims.

Measure performance only for selected reproducible workloads with complete parity: compatible preparation reuse, kernel and end-to-end times, throughput/tails where supported, process-tree memory, copies/I/O and one bounded CPU/RAM/I/O/backend-thread owner. No universal fastest claim, forced process per library or invented SLA. The local browser demo shows actual computed/stored output, provenance and remaining gaps; it is not a production app.

Follow Backlog -> Ready -> In progress -> Code review -> Test -> Ready to release -> Released -> Done with actual evidence. Publication/package/operating boundaries remain unchanged. This planning authorizes no paid provider access, trading, notifications, public deployment, production writes or recurring jobs. API/SaaS stays optional and secondary.
