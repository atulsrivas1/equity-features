# R27 — Volatility surfaces, tenors and comparisons

Owner-requested future planning, October19,2026. [Epic](https://github.com/atulsrivas1/equity-features/issues/540), [milestone](https://github.com/atulsrivas1/equity-features/milestone/31), [governance](https://github.com/atulsrivas1/equity-features/issues/525). Planned Backlog/unassigned/no due date; live Project owns status.

## EQ-194: Specify distinct volatility estimators and surface conventions

[Issue](https://github.com/atulsrivas1/equity-features/issues/541); layer: contracts/design. Dependencies: EQ-182.

Separate existing equity SIMPLE-return RV, planned LOG-return RV and each implied estimator. Freeze selected option strip/model-IV/surface/tenor definitions, units, forward/strike/expiry selection, day count, sampling, interpolation, coverage and negative/invalid variance handling. Reuse EQ154/155 rather than duplicate RV/statistics.

Validation: Independent convention-separation and interpolation/coverage references; unresolved model/expiry/basis choices explicit before Ready. No probability/forecast claim from descriptive measures.

## EQ-195: Implement admitted option strips and IV surfaces

[Issue](https://github.com/atulsrivas1/equity-features/issues/542); layer: pure calculation. Dependencies: EQ-183, EQ-184, EQ-194.

Implement reviewed strip and selected surface outputs from supplied eligible quotes/model/expiry frames. Define finite support, forward/strike/delta selection, numerical stability and per-expiry readiness; preserve distinct estimator identities.

Validation: Independent small chains and high-precision references, sparse/crossed/invalid inputs, strike/expiry boundaries, monotonicity/arbitrage checks only where specified, and full unavailable/evidence cases.

## EQ-196: Implement constant-tenor volatility, skew and move scales

[Issue](https://github.com/atulsrivas1/equity-features/issues/543); layer: pure calculation. Dependencies: EQ-194, EQ-195.

Specify supported tenor interpolation and skew/term-structure/move scaling over admitted expiry outputs. Bind exact target/anchor clocks, bracketing/classifications and variance/time conventions; distinguish numerical scale from probability and current from frozen forecast evidence.

Validation: Independent small expiry grids, exact-target/bracketing/zero-time/missing-classification cases, units and clock mismatch, pure supplied-expiry reuse and bounded target fan-out.

## EQ-197: Implement volatility histories and aligned comparison arithmetic

[Issue](https://github.com/atulsrivas1/equity-features/issues/544); layer: pure calculation. Dependencies: EQ-194, EQ-196, EQ-154, EQ-155, EQ-168, EQ-173.

Reuse existing robust statistics and equity RV with compatible method/cohort/time/basis populations. Define selected IV-RV spreads/ratios, history changes, comparable ranks, group medians/competition ranks and event-residual arithmetic. Product scan thresholds/pressure policies remain separate.

Validation: Independent sorted/group/time vectors, prior-only/target-exclusion/tie/zero-MAD/zero-RV cases, dated membership and event coverage; no claim that forward IV minus trailing RV is a horizon-matched forecast.

## EQ-198: Implement volatility frame, history and reference I-O

[Issue](https://github.com/atulsrivas1/equity-features/issues/545); layer: I/O. Dependencies: EQ-185, EQ-194.

Provide selected quote/expiry/price/grid/history/event/group normalized frames and typed output mappings. Share compatible immutable preparations; preserve actual observation/knowledge/coverage and separate current/prior populations.

Validation: Synthetic acquisition/normalization/sink/readback and comparable-history conformance, revision/clock/basis mismatches, bounded read/copy/cache evidence and explicit unsupported inputs.

## EQ-199: Implement independent volatility worker branches

[Issue](https://github.com/atulsrivas1/equity-features/issues/546); layer: workers. Dependencies: EQ-195, EQ-196, EQ-197, EQ-198, EQ-144, EQ-145.

Schedule independently ready RV, strip/surface, tenor, history and comparison outputs. RV does not wait on IV; joins require only actual operands. Reuse verified histories/expiry populations across targets/products under shared resource limits.

Validation: Direct/worker full-result parity, unrelated failure isolation, ordered history revisions and restart/readback; cold/warm/skewed workload throughput, peak memory and live latency where supported.

## EQ-200: Qualify volatility library and cross-layer release

[Issue](https://github.com/atulsrivas1/equity-features/issues/547); layer: release acceptance. Dependencies: EQ-187, EQ-199.

Qualify exact estimator/API/I-O/worker/method combinations and preserve old equity volatility ownership/compatibility. Publish synthetic calculation/consumer examples and explicit unsupported conventions.

Validation: Independent numerical/timing/coverage fixtures, both-platform installs/artifacts, measured current/alternative baselines with parity, separate final-head review and actual publication/readback.

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
