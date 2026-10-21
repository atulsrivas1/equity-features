# R29 — Option scanners, watchlists, strategies and complete coverage

[Replan](../OPTION_DELIVERY_REPLAN.md). Existing epic [E37](https://github.com/atulsrivas1/equity-features/issues/555); milestone [33](https://github.com/atulsrivas1/equity-features/milestone/33). Planning only; Project owns live status. Preserve equity/R18 ownership and option implementation gates.

## Parallel layer contracts

Contract owner: EQ-207. Published reviewed release contracts, independent conformance fixtures and accepted implementation prerequisites; integration follows actual producer readiness.

| Track | Stories | Deliverables |
| --- | --- | --- |
| libraries | EQ-207, EQ-208, EQ-209, EQ-216, EQ-219 | Compose versioned scanner/watchlist, exposure-level, volatility-context, strategy/meta-score and lifecycle policies; compute separately mature descriptive outcomes. |
| io | EQ-217 | Map immutable feature/policy frames, weights, groups, watchlist memberships and ordered history; persist results and delayed labels with exact provenance. |
| workers | EQ-218 | Evaluate selected ready policies/strategies and ordered lifecycle transitions under the shared runtime; independently execute mature outcome branches. |

## Integrated acceptance and demonstration

Release acceptance: EQ-211; integrated composition: EQ-210. No setup-only release; no API/product UI/public deployment gate.

Show matching/nonmatching/unavailable policies, a strategy and watchlist transition, pending/mature outcomes and the coverage report from actual local stored results.

Compare independently expected results with direct calls, installed workers and stored readback. Include available, unavailable and invalid cases, timing/identity/provenance, supported modes, retries and sink conflicts. Freeze actual compatible package artifacts, applicable Windows/Linux checks and resource workloads before implementation. Required fresh independent review and CI remain mandatory. Demonstration is performed at implementation acceptance, not claimed by this planning packet.

## Story contracts

### EQ-207: Implement option flow scanner and watchlist policies

[#556](https://github.com/atulsrivas1/equity-features/issues/556). Layer: product policy/integration. Provisional complexity: 5 points; not an estimate of days.

Reconcile every selected flow screen/rollup/tracker definition to exact primitive, evidence, policy version and worker. Implement original allowed activity/execution/concentration/group/divergence interpretations without embedding thresholds in generic kernels. Link pure outcomes on the delayed path; unselected source variants receive numbered dispositions. Include option scanner generations, flow screens, option watchlists and option watchlist-membership evidence. Product brands do not determine reusable library boundaries.

Dependencies: EQ-193, EQ-176, EQ-177, EQ-178, EQ-215. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent positive/negative/unavailable policy cases, origin-time/partial-population and catalogue-identity checks, direct-to-product parity and all admitted outputs mapped; no legacy parity from familiar names.

### EQ-208: Plan and implement admitted option exposure level and change policies

[#557](https://github.com/atulsrivas1/equity-features/issues/557). Layer: product policy/integration. Provisional complexity: 5 points; not an estimate of days.

Bind shared exposure grids/changes to explicit node filters, level selection, proximity, projection and candidate/alert lifecycle policies. Require declared policy-specific completeness while preserving independently ready numerical metrics.

Dependencies: EQ-206, EQ-177, EQ-178. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent level/filter/tie/partial-grid/clock scenarios, lifecycle/replay and policy-specific unavailable status; catalogue completeness and full input/output/evidence binding.

### EQ-209: Plan and implement admitted volatility scan and context policies

[#558](https://github.com/atulsrivas1/equity-features/issues/558). Layer: product policy/integration. Provisional complexity: 5 points; not an estimate of days.

Bind volatility outputs to selected pricing pressure/anomaly, preset scans, relative/group context and frozen forecast consumers. Keep numeric estimators distinct from product weighting/thresholds and policy admission; map every admitted finite definition and retain explicit residual scope.

Dependencies: EQ-200, EQ-176, EQ-177. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent policy/weight/rank/group examples, unavailable components, exact source-frame joins and catalogue/producer checks; descriptive scales and forecasts retain their distinct claims.

### EQ-210: Qualify local option policy projections and delayed outcomes

[#559](https://github.com/atulsrivas1/equity-features/issues/559). Layer: I/O/workers/product delivery. Provisional complexity: 5 points; not an estimate of days.

Qualify local library-to-I/O-to-worker composition of policy projections and separately mature outcomes. Use existing sinks/receipts; no API, service, hosted UI or notification dependency. Preserve original evidence, distinct completion/publication receipts and unchanged origin data. Optional service/tool bindings stay outside this release gate.

Dependencies: EQ-207, EQ-208, EQ-209, EQ-174, EQ-179, EQ-218, EQ-219. Delivery gates are separate from runtime operand dependencies.

Independent validation: Synthetic installed end-to-end request-to-verified-projection and delayed-outcome replay, scope isolation/error/expiry/fault cases, chronological leakage controls and resource budgets shared across all products.

### EQ-211: Accept full option matrix library and cross-layer coverage

[#560](https://github.com/atulsrivas1/equity-features/issues/560). Layer: release acceptance. Provisional complexity: 5 points; not an estimate of days.

Account for every option/mixed matrix capability and command role against its appropriate library/module, canonical adapter, worker route and accepted story. Track equity/shared producer reuse, aliases, non-calculation support and unresolved dynamic bindings explicitly. A deferred or unresolved capability remains visible and prevents an unqualified full-coverage claim; catalogue counts do not establish numerical parity.

Dependencies: EQ-187, EQ-193, EQ-200, EQ-206, EQ-210, EQ-181, EQ-216, EQ-217, EQ-218, EQ-219. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent no-orphan/consumer/source-rights audit, full result/status/quality/evidence parity, both-platform exact artifacts, shared-machine mixed workloads and measured end-to-end time/memory/latency against credible alternatives, required review/CI/publication/readback.

### EQ-216: Implement option strategy, context and meta-score composition

[#575](https://github.com/atulsrivas1/equity-features/issues/575). Layer: policy calculation. Provisional complexity: 5 points; not an estimate of days.

Reconcile option/mixed strategy profiles, direction/expiry lanes, component gates, normalized evidence, configurable weights, tape summaries and meta scores. Implement original versioned pure composition in the optional strategies package; reuse equity-owned producers and select exact operand closure per strategy. Descriptive scores are not trading recommendations or profitability claims.

Dependencies: EQ-193, EQ-200, EQ-206, EQ-177. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent component/weight/gate/population/tie vectors, missing optional versus required evidence, chronological eligibility and cross-policy identity cases; no future label dependency in origin-time computation.

### EQ-217: Map option policies, strategies and watchlist state to canonical storage

[#576](https://github.com/atulsrivas1/equity-features/issues/576). Layer: I/O. Provisional complexity: 5 points; not an estimate of days.

Extend existing I/O SDK for immutable option feature/policy frames, strategy/context inputs, watchlist memberships and supplied ordered lifecycle/history. Convert and persist versioned canonical outputs into the separate output DuckDB; preserve real/synthetic/unavailable provenance and repeat-write/revision rules.

Dependencies: EQ-182, EQ-176, EQ-177, EQ-178. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent conversion and readback fixtures, compatible policy versions, missing inputs, stale/future frames, membership history, exact precision and deterministic repeat-write/conflict tests.

### EQ-218: Execute bounded option policies, strategies and watchlist lifecycles

[#577](https://github.com/atulsrivas1/equity-features/issues/577). Layer: workers. Provisional complexity: 5 points; not an estimate of days.

Compose ready selected policy/strategy branches and ordered watchlist/lifecycle transitions using the shared worker runtime. Preserve per-output readiness, one bounded resource owner, deterministic retry/cancellation and serialized sink ownership. No service or API required for local execution.

Dependencies: EQ-207, EQ-208, EQ-209, EQ-216, EQ-217, EQ-178. Delivery gates are separate from runtime operand dependencies.

Independent validation: Direct-library versus worker versus stored full-result parity, independent readiness, ordered correction/replay, recovery/fault and bounded-memory cases; local browser readback of actual stored results.

### EQ-219: Implement option move outcomes and descriptive calibration

[#578](https://github.com/atulsrivas1/equity-features/issues/578). Layer: delayed calculation. Provisional complexity: 5 points; not an estimate of days.

Freeze origin-time forecast/scale evidence and define admitted mature realized-fraction, sigma-observation and descriptive calibration arithmetic over supplied observations. Extend the optional labels package; preserve pending/mature states, observation resolution, embargo and revisions. No inferred horizon matching or model accuracy from a descriptive scale.

Dependencies: EQ-174, EQ-196. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent pending/mature, zero-scale, partial-path, revision and exact-time vectors; unchanged origin feature bytes, delayed data never reachable from origin-time policy DAG.
