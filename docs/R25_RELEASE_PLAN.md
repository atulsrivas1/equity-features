# R25 — Option contracts, pricing and feature foundations

Owner-requested future planning, October19,2026. [Epic](https://github.com/atulsrivas1/equity-features/issues/526), [milestone](https://github.com/atulsrivas1/equity-features/milestone/29), [governance](https://github.com/atulsrivas1/equity-features/issues/525). Planned Backlog/unassigned/no due date; live Project owns status.

## EQ-182: Specify option facts, model boundaries and library ownership

[Issue](https://github.com/atulsrivas1/equity-features/issues/527); layer: contracts/design. Dependencies: EQ-012, EQ-013, EQ-014, EQ-016.

Reconcile option and mixed source candidates/finite product definitions into source-safe output and dependency manifests. Define option identity, exercise/settlement, expiry/time conventions, price/size/currency/multiplier units, underlying alignment, rates/dividends, quote eligibility, revisions and known-at. Select the initial model/exercise scope explicitly before Ready. Keep supplied model facts separate from calculated outputs. Assign every admitted gap a concrete story; decide modules versus distributions from consumers, preserving existing APIs.

Validation: Independent contract/timestamp/multiplier/exercise counterexamples, no orphan admitted definitions and compatibility review; unresolved conventions remain blocked, not defaults.

## EQ-183: Implement admitted contract pricing and Greek calculations

[Issue](https://github.com/atulsrivas1/equity-features/issues/528); layer: pure calculation. Dependencies: EQ-182.

Specify and implement only the reviewed pricing/model/exercise profiles and selected Greeks. Define discount/carry/time bases, dimensions, scaling, limits, expiry/zero-volatility and unsupported-input behavior. Share compatible model intermediates; supplied Greek facts need not invoke the model.

Validation: Independent analytic/high-precision or independently implemented fixtures and finite-difference crosschecks with declared error budgets, edge limits, input ownership and bounded batch memory.

## EQ-184: Implement bounded implied-volatility inversion

[Issue](https://github.com/atulsrivas1/equity-features/issues/529); layer: pure calculation. Dependencies: EQ-182, EQ-183.

Define admissible quotes/price bounds, model-specific IV roots, bracketing, tolerances, convergence budgets, ambiguous/nonexistent roots, expiry and null/status. Reuse pricing operands without changing selected model semantics.

Validation: Independent known-price/volatility pairs and invalid/near-boundary/poor-conditioning cases; residual and solver-budget evidence, exact statuses and measured baseline parity.

## EQ-185: Implement option and model-reference I-O contracts and conformance

[Issue](https://github.com/atulsrivas1/equity-features/issues/530); layer: I/O. Dependencies: EQ-182, EQ-125.

Define explicitly supplied/file/synthetic option trade/quote/definition, rates/dividends/model/OI/position reference and output-sink contracts using existing SDK/receipt/version boundaries. Preserve source identity, clocks, action/multiplier and declared coverage. Provider entitlement and actual provider acquisition stay in separately selected adapter scope.

Validation: Independent synthetic source/sink conformance, missing/stale/revised references, normalized-unit/precision/error fixtures, bounded reads and complete receipt/readback; no private/provider call required.

## EQ-186: Wire independent option compute worker branches

[Issue](https://github.com/atulsrivas1/equity-features/issues/531); layer: workers. Dependencies: EQ-183, EQ-184, EQ-185, EQ-143, EQ-144.

Expose selected pricing/Greek/IV requests over admitted supplied facts and existing I/O. Schedule independently ready contract/metric branches under one resource owner; IV-only inputs cannot block a supplied-Greek or different ready output. Bound task/batch size, backend threads, copies, in-flight memory and sink ownership.

Validation: Direct versus installed-worker full-result/quality/evidence parity, unrelated-missing-input isolation, retry/recovery/readback and repeated budget-constrained kernel/end-to-end workloads.

## EQ-187: Qualify option foundation library and cross-layer release

[Issue](https://github.com/atulsrivas1/equity-features/issues/532); layer: release acceptance. Dependencies: EQ-183, EQ-184, EQ-185, EQ-186.

Qualify exact supported model/contract/API/I-O/worker combinations, package/module boundaries, independent consumer examples and immutable release evidence. Existing equity APIs and pure dependency boundaries remain intact.

Validation: Both-platform clean wheel/sdist installs, independent numerical/causal/error fixtures, artifact/source closure, separate final-head review and actual publication/readback; finite supported model scope stated.

## Release gates


## Mandatory acceptance and boundaries

- [ ] Original mathematics, dimensions/units, timing/knowledge, initialization, model/eligibility/coverage and edge cases frozen with independent expected fixtures before Ready. Detailed private code/formulas/thresholds require established rights; raw source-derived ledgers stay local.
- [ ] Source-independent supplied-fact kernels; acquisition/credentials/storage in I/O, dependency scheduling/resource/persistence in workers, policy in consumers. Existing equity calculations/events/labels/scanners reused where semantically compatible.
- [ ] Supported batch/update/restore/merge/replay capabilities explicit; result/null/status/quality/evidence/identity parity and independent positive/negative/adversarial fixtures. No invented support from a registry declaration.
- [ ] Minimize repeated reads/copies/calculations; share compatible immutable inputs/intermediates with exact identity and bounded lifetime. Preserve actual per-output dependencies and ordered state. One coordinated CPU/RAM/I/O/backend-thread budget across products; configurable limits and an explicit full-machine option within real constraints. No mandatory process/service per library.
- [ ] Measure defined cold/warm/small/large/skewed workloads against credible current/serial/alternative baselines with parity; report kernel versus total time, throughput, memory/copies/I-O and live p50/p95/p99/freshness where supported. No universal fastest or invented SLA.
- [ ] Documentation, mathematical/API/discovery/examples/decisions/compatibility, required separate final-head review, applicable CI/installed both-platform artifacts and actual publication/readback accompany the story. Only actual accepted release scope becomes Done.

Future Backlog, unassigned, no due date or runtime selection. Current equity R17/R18 sequence and R22-R24 draft plan are preserved. Dependency lists are admission gates, not global runtime barriers. Release numbers are planning order, not a fabricated mathematical dependence between volatility/exposure branches. No provider spending/private data operation, live-feed/SLA, hosted deployment, notification sending, registry/admin/destructive/recurring scope or future review authorization is granted by this plan. Existing deferred provider/LIVE/SEC stories remain authoritative.

All selected children accepted; every admitted output/worker/product definition tied to accepted scope or separately numbered residual before final coverage acceptance.
