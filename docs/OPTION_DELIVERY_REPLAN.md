# Option delivery replan under the coordinator working agreement

October 20, 2026. [GOV036 #572](https://github.com/atulsrivas1/equity-features/issues/572) replans the option portion of the full matrix under the [coordinator agreement](COORDINATOR_WORKING_AGREEMENT.md), using the same feature-bearing three-layer delivery model as [equities](EQUITY_DELIVERY_REPLAN.md). It supersedes the delivery arrangement in the [GOV033/PR524 option proposal](https://github.com/atulsrivas1/equity-features/pull/524), preserving historical evidence and existing numbered issues rather than creating a competing option backlog. It does not change the equity release allocation or take ownership of EF1/R18.

[PR579](https://github.com/atulsrivas1/equity-features/pull/579) records source review and CI; the live Project owns execution status. The matrix defines capability coverage, including features, scanners, watchlists, strategies, scores, lifecycle and outcomes. Product names are consumer views. Every capability needs an appropriate library/module owner; shared mathematics is reused. This is a reviewed planning allocation. The 36 story contracts, five epics and five milestones were reconciled against the published independently reviewed source; new issues EQ214-219 are #573-578. Actual publication/lifecycle evidence is tracked on GOV036/PR579. Implementation stories remain Backlog. The original GOV036 prerequisite was verified EQ141/EQ146 acceptance and reviewed story prerequisites. The scoped owner amendment below supersedes EQ146 only for R25; later-release gates remain unchanged. All EF releases need not finish first.

## Owner repository correction and first-release preparation

After GOV036 publication, the owner selected separate option repositories and then selected R25. [GOV037 #581](https://github.com/atulsrivas1/equity-features/issues/581) records this successor decision and the [R25 preparation handoff](r25/PREPARATION.md). The old assumption of co-location in existing equity repositories is superseded. Repository baselines are documentation only; no new package/runtime is implemented or qualified. R18/EQ146 remains unaccepted. On October 20 the owner explicitly approved independent R25 admission, superseding its blanket EQ146 gate and removing EQ143/EQ144 only from EQ186. Accepted EQ141/R17 references, published planning, reviewed frozen contracts and R25-owned package/schema/executor compatibility, numerical, resource and integrated acceptance remain mandatory. Later-release prerequisites and active EF1/R18 ownership/resource windows are unchanged. The [working agreement amendment](COORDINATOR_WORKING_AGREEMENT.md#owner-amendment-independent-r25-admission--october-20-2026) records the boundary.

## Repository and library ownership

Use the three dedicated option repositories below. Existing equity calculation/contract and qualified I/O/worker components are versioned dependency references, not option code homes. Exact new packages/import names and compatibility are frozen before implementation; the newly created repositories currently contain reviewed documentation baselines only. Do not duplicate equity mathematics or silently move accepted APIs. Independent exact experimental dependency/artifact locks implement the agreed version policy.

| Repository | Responsibility and write boundary |
| --- | --- |
| [option-features](https://github.com/atulsrivas1/option-features) | Pure option contracts/calculations and separately optional option domain packages; selected qualified equity dependencies flow inward only. |
| [option-feature-io](https://github.com/atulsrivas1/option-feature-io) | Native option input conversion, codec and sinks; closed equity transport compatibility must be demonstrated, never assumed. |
| [option-feature-workers](https://github.com/atulsrivas1/option-feature-workers) | Option request/identity admission, bounded selected-output orchestration and serialized publication under reviewed contracts. |

Logical libraries remain option-features, option-specific microstructure extensions, volatility-features, exposure-features, option policies/strategy-context/lifecycle and outcomes. Their option-owned packages live in the option calculation repository. Generic equity calculations, events, policy engines and labels retain their existing owners and APIs; consume only compatible public packages. Low-level equity calculations never import option or strategy packages. Separately optional strategy consumers may depend on both, with no reverse edge from feature kernels. This changes repository allocation, not the existing numbered feature scope or release identities.

The accepted equity schema fixes quantities to shares; result codecs, DuckDB table layout and worker multi-input admission are closed. Reusing them unchanged for native option records would lose contract units or underlying identity. R25 explicitly prepares option-owned contracts or a reviewed shared extension, preserving old equity interfaces. No unchanged SDK/sink/worker compatibility is claimed by this repository decision.

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

Existing dependency lists are delivery/admission gates. [Allocation JSON](plans/option-delivery-replan.json) gives the effective planned graph and story-specific changes. EQ186/187 gain the explicit reference-feature producer; flow integration gains the activity producer. EQ210 becomes local composition and loses the optional service EQ084 gate; it retains separately mature outcome integration. R29 gains distinct strategy, I/O, worker and delayed-calculation stories. Only the owner-approved R25 blanket EQ146 gate and EQ186 EQ143/EQ144 delivery dependencies are removed; later-release equity dependencies remain unchanged. This does not waive a numerical operand or compatibility/resource acceptance requirement.

## Data flow and integration

Qualified source DuckDB or explicitly labelled synthetic input -> input adapter -> workers -> pure feature/policy libraries -> output sink -> a separate output DuckDB. Workers invoke adapters and libraries and pass canonical results to sinks. Source conversion and persistence remain outside pure libraries. Reuse the existing catalogue-backed Parquet route only where exact qualified option interfaces and source schema permit it; arbitrary DuckDB tables require a separately qualified mapping. Source paths/schema/rights/clock/coverage and output path/schema/run/provenance/repeat-write contracts are frozen before actual data operations. This planning reads no datasets and creates no database.

Use suitable owner-designated source data only after qualification; synthetic gaps stay labelled and do not invent observed liquidity, OI, coverage, freshness or known-at evidence. Distinguish supplied Greeks from calculated Greeks, missing from observed zero, metric readiness from full-grid completeness and calculation completion from publication visibility.

## Matrix coverage and scope changes

[Coverage accounting](OPTION_MATRIX_COVERAGE.md) and the private exact-identity ledger account for the pinned finite catalogue and all command roles. This is planning ownership, not an assertion that existing libraries implement them. All 30 existing EQ182-211 stories are retained once; six missing scopes are explicitly added: reference/liquidity/chain features, activity/execution baselines, strategy/context/meta composition, policy I/O, policy workers and delayed calibration. Their allocation and original acceptance criteria are in the JSON and per-release documents. Historical PR524 remains the predecessor and its unrelated equity/product discussion is not imported as option implementation scope.

Typed fields, aliases, metadata, wrappers and parameters are not separate mathematical features. The source ledger retains unresolved typed writes/dynamic dispatch and conservative unions; exact output-to-producer/dependency qualification remains EQ182 and the corresponding domain contract stories, with EQ211 final reconciliation. An unresolved or deferred capability cannot disappear or count as delivered full coverage. Record a numbered residual and explicit owner/scope decision where admission requires resolution; never silently exclude a matrix item to pass acceptance.

## Review and release gates

Coordinator review precedes any layer push; every PR has a fresh independent read-only reviewer distinct from its author, actual final-head coverage and applicable CI. Record reviewer identity/findings/rechecks and limitations. After integration, compare direct libraries, installed workers and stored readback against independently expected synthetic/licensed results, including values/null/status/quality/evidence/identity and missing/invalid/future/revised cases. Qualify actual supported wheel/sdist combinations on Windows/Linux, core-only optional dependency isolation and exact compatible artifacts before delivery claims.

Measure performance only for selected reproducible workloads with complete parity: compatible preparation reuse, kernel and end-to-end times, throughput/tails where supported, process-tree memory, copies/I/O and one bounded CPU/RAM/I/O/backend-thread owner. No universal fastest claim, forced process per library or invented SLA. The local browser demo shows actual computed/stored output, provenance and remaining gaps; it is not a production app.

Follow Backlog -> Ready -> In progress -> Code review -> Test -> Ready to release -> Released -> Done with actual evidence. Publication/package/operating boundaries remain unchanged. This planning authorizes no paid provider access, trading, notifications, public deployment, production writes or recurring jobs. API/SaaS stays optional and secondary.
