# R20 — Relative statistics, realized volatility and robust anomalies

Owner-requested planning, October 19, 2026. [Epic](https://github.com/atulsrivas1/equity-features/issues/468), [milestone](https://github.com/atulsrivas1/equity-features/milestone/24), [GOV-031](https://github.com/atulsrivas1/equity-features/issues/464). Current execution status belongs to the live Project. No date or implementation start is selected.

## EQ-153: Implement correlation, beta and residual returns

[Issue](https://github.com/atulsrivas1/equity-features/issues/487); 8 provisional complexity points; ownership: core.

Specify aligned instrument/benchmark return witnesses, return basis, sample population, covariance convention, minimum coverage, zero benchmark variance and beta-adjusted residual semantics. Join only the requested pair.

Dependencies: [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470), [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent small-array correlation/beta/residual results, missing/asynchronous witnesses, constant benchmark, cutoff revisions and population mismatch; pairwise parallel scaling and shared preparation timing.

## EQ-154: Implement separately specified daily and intraday log-return RV

[Issue](https://github.com/atulsrivas1/equity-features/issues/488); 8 provisional complexity points; ownership: core.

Specify daily centered log-return and intraday regular-session realized-variance families separately: sampling, annualization, overnight exclusion, session calendars and early closes. Preserve existing simple-return volatility as a distinct API.

Dependencies: [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470), [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent log-return arithmetic, centered versus uncentered and simple versus log counterexamples, incomplete grids, early closes, zero/nonpositive prices, coverage and annualization; performance/parity for window reuse.

## EQ-155: Implement robust historical summaries and ranks

[Issue](https://github.com/atulsrivas1/equity-features/issues/489); 8 provisional complexity points; ownership: core.

Specify prior-only median, MAD, percentile/quantile convention, ties, minimum history, zero MAD, cohort and cutoff availability. Choose exact/approximate algorithms explicitly; approximation requires a separate accepted error contract.

Dependencies: [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent sorted-array expectations, ties, zero dispersion, missing values, target exclusion, revisions and deterministic ranks; measure time/memory across history sizes.

## EQ-156: Implement robust volume pace and anomaly normalization

[Issue](https://github.com/atulsrivas1/equity-features/issues/490); 8 provisional complexity points; ownership: core + worker bindings.

Combine compatible current volume observations with prior-only same-bucket/session robust baselines. Specify elapsed coverage, excluded sessions, irregular/early-close buckets, zero baseline and availability. Do not replace median/MAD with mean ratios.

Dependencies: [EQ-155](https://github.com/atulsrivas1/equity-features/issues/489), [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent bucket alignment and prior-only fixtures, lookahead/target-contamination counterexamples, missing buckets and clock boundaries; current and prior prep overlap with result parity and memory measurements.

## EQ-157: Qualify and deliver relative and robust statistics

[Issue](https://github.com/atulsrivas1/equity-features/issues/491); 5 provisional complexity points; ownership: cross-repository acceptance.

Qualify selected pairwise, RV and robust outputs with actual worker capabilities, examples and discoverable semantic distinctions. Options IV surfaces, option-relative policies and product scanners are excluded.

Dependencies: [EQ-153](https://github.com/atulsrivas1/equity-features/issues/487), [EQ-154](https://github.com/atulsrivas1/equity-features/issues/488), [EQ-155](https://github.com/atulsrivas1/equity-features/issues/489), [EQ-156](https://github.com/atulsrivas1/equity-features/issues/490), [EQ-152](https://github.com/atulsrivas1/equity-features/issues/486).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent numerical/causal validation, branch-isolation and requested-output closure cases, repeated representative benchmarks, both-platform installed artifacts, final review, versioned release and public readback.

## Cross-cutting acceptance — mandatory

- [ ] Freeze original mathematics, units, timing, initialization, coverage, edge cases and exact direct dependencies before code; define unresolved choices and complete required review before Ready.
- [ ] Keep calculations source-independent: supplied facts only; no acquisition, credentials, file/database access, scheduling or publication inside kernels.
- [ ] Preserve independent feature readiness and ordered state correctness; unrelated missing inputs cannot block valid selected outputs. Declare actual batch/update/restore/merge/replay capabilities.
- [ ] Validate with independent synthetic/licensed fixtures, full values/nulls/status/quality/evidence/identity parity and applicable temporal/revision/state tests. No shared optimized implementation as the only oracle.
- [ ] Measure direct and end-to-end work using frozen workloads, repeat distributions, wall time, throughput/latency, CPU/core-seconds, aggregate memory, copies and queue/I/O costs. Freeze an adoption rule before timing; reject changes that fail correctness or declared resource bounds. Task granularity and shared work matter more than worker count.
- [ ] Update formula/API/discovery/examples/decision and release documentation with the story; document no-impact decisions. Complete applicable final-head separate review, CI, both-platform installed/artifact checks and actual publication/readback before Released/Done.

## Lifecycle and boundaries

Planned Backlog, unassigned; points are provisional complexity, not days. Dependency acceptance and a concrete reviewed pre-code plan precede Ready. No dates, promised speed/SLA, provider/private data operation, deployment, automation or package publication is authorized by creating this issue. Existing closed releases retain their evidence. LIVE-001–004/E24 remain deferred and are reused for any future persistent live delivery; this scope does not duplicate them. Detailed comparison-source code/formulas remain local; implement from original specifications and independent fixtures.

All story acceptance applies individually; the final release story audits the combined result and cannot replace missing child evidence. Batch-only implementations remain honest where update/merge cannot be qualified.
