# R27 — Volatility surfaces, tenors and comparisons

[Replan](../OPTION_DELIVERY_REPLAN.md). Existing epic [E35](https://github.com/atulsrivas1/equity-features/issues/540); milestone [31](https://github.com/atulsrivas1/equity-features/milestone/31). Planning only; Project owns live status. Preserve equity/R18 ownership and option implementation gates.

## Parallel layer contracts

Contract owner: EQ-194. Published reviewed release contracts, independent conformance fixtures and accepted implementation prerequisites; integration follows actual producer readiness.

| Track | Stories | Deliverables |
| --- | --- | --- |
| libraries | EQ-194, EQ-195, EQ-196, EQ-197 | Compute admitted option strips/surfaces, constant-tenor variance, skew/curvature/term structure, move scales and compatible historical/comparison statistics. |
| io | EQ-198 | Map quote/expiry frames, rates/dividends/classification, histories, group membership and separately supplied equity RV with exact method/time/basis identities. |
| workers | EQ-199 | Run independent expiry/strip/surface and ready target/history branches; join only actual operands and persist distinct unavailable states. |

## Integrated acceptance and demonstration

Release acceptance: EQ-200; integrated composition: EQ-200. No setup-only release; no API/product UI/public deployment gate.

A small expiry frame with direct versus worker/stored tenor/skew values, missing brackets and distinct daily/intraday RV conventions.

Compare independently expected results with direct calls, installed workers and stored readback. Include available, unavailable and invalid cases, timing/identity/provenance, supported modes, retries and sink conflicts. Freeze actual compatible package artifacts, applicable Windows/Linux checks and resource workloads before implementation. Required fresh independent review and CI remain mandatory. Demonstration is performed at implementation acceptance, not claimed by this planning packet.

## Story contracts

### EQ-194: Specify distinct volatility estimators and surface conventions

[#541](https://github.com/atulsrivas1/equity-features/issues/541). Layer: contracts/design. Provisional complexity: 3 points; not an estimate of days.

Separate existing equity SIMPLE-return RV, planned LOG-return RV and each implied estimator. Freeze selected option strip/model-IV/surface/tenor definitions, units, forward/strike/expiry selection, day count, sampling, interpolation, coverage and negative/invalid variance handling. Reuse EQ154/155 rather than duplicate RV/statistics.

Dependencies: EQ-182. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent convention-separation and interpolation/coverage references; unresolved model/expiry/basis choices explicit before Ready. No probability/forecast claim from descriptive measures.

### EQ-195: Implement admitted option strips and IV surfaces

[#542](https://github.com/atulsrivas1/equity-features/issues/542). Layer: pure calculation. Provisional complexity: 5 points; not an estimate of days.

Implement reviewed strip and selected surface outputs from supplied eligible quotes/model/expiry frames. Define finite support, forward/strike/delta selection, numerical stability and per-expiry readiness; preserve distinct estimator identities.

Dependencies: EQ-183, EQ-184, EQ-194. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent small chains and high-precision references, sparse/crossed/invalid inputs, strike/expiry boundaries, monotonicity/arbitrage checks only where specified, and full unavailable/evidence cases.

### EQ-196: Implement constant-tenor volatility, skew and move scales

[#543](https://github.com/atulsrivas1/equity-features/issues/543). Layer: pure calculation. Provisional complexity: 5 points; not an estimate of days.

Specify supported tenor interpolation and skew/term-structure/move scaling over admitted expiry outputs. Bind exact target/anchor clocks, bracketing/classifications and variance/time conventions; distinguish numerical scale from probability and current from frozen forecast evidence.

Dependencies: EQ-194, EQ-195. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent small expiry grids, exact-target/bracketing/zero-time/missing-classification cases, units and clock mismatch, pure supplied-expiry reuse and bounded target fan-out.

### EQ-197: Implement volatility histories and aligned comparison arithmetic

[#544](https://github.com/atulsrivas1/equity-features/issues/544). Layer: pure calculation. Provisional complexity: 5 points; not an estimate of days.

Reuse existing robust statistics and equity RV with compatible method/cohort/time/basis populations. Define selected IV-RV spreads/ratios, history changes, comparable ranks, group medians/competition ranks and event-residual arithmetic. Product scan thresholds/pressure policies remain separate.

Dependencies: EQ-194, EQ-196, EQ-154, EQ-155, EQ-168, EQ-173. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent sorted/group/time vectors, prior-only/target-exclusion/tie/zero-MAD/zero-RV cases, dated membership and event coverage; no claim that forward IV minus trailing RV is a horizon-matched forecast.

### EQ-198: Implement volatility frame, history and reference I-O

[#545](https://github.com/atulsrivas1/equity-features/issues/545). Layer: I/O. Provisional complexity: 5 points; not an estimate of days.

Provide selected quote/expiry/price/grid/history/event/group normalized frames and typed output mappings. Share compatible immutable preparations; preserve actual observation/knowledge/coverage and separate current/prior populations.

Dependencies: EQ-185, EQ-194. Delivery gates are separate from runtime operand dependencies.

Independent validation: Synthetic acquisition/normalization/sink/readback and comparable-history conformance, revision/clock/basis mismatches, bounded read/copy/cache evidence and explicit unsupported inputs.

### EQ-199: Implement independent volatility worker branches

[#546](https://github.com/atulsrivas1/equity-features/issues/546). Layer: workers. Provisional complexity: 5 points; not an estimate of days.

Schedule independently ready RV, strip/surface, tenor, history and comparison outputs. RV does not wait on IV; joins require only actual operands. Reuse verified histories/expiry populations across targets/products under shared resource limits.

Dependencies: EQ-195, EQ-196, EQ-197, EQ-198, EQ-144, EQ-145. Delivery gates are separate from runtime operand dependencies.

Independent validation: Direct/worker full-result parity, unrelated failure isolation, ordered history revisions and restart/readback; cold/warm/skewed workload throughput, peak memory and live latency where supported.

### EQ-200: Qualify volatility library and cross-layer release

[#547](https://github.com/atulsrivas1/equity-features/issues/547). Layer: release acceptance. Provisional complexity: 5 points; not an estimate of days.

Qualify exact estimator/API/I-O/worker/method combinations and preserve old equity volatility ownership/compatibility. Publish synthetic calculation/consumer examples and explicit unsupported conventions.

Dependencies: EQ-187, EQ-199. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent numerical/timing/coverage fixtures, both-platform installs/artifacts, measured current/alternative baselines with parity, separate final-head review and actual publication/readback.
