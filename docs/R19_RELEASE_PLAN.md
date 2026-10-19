# R19 — Trend, momentum and money-flow features

Owner-requested planning, October 19, 2026. [Epic](https://github.com/atulsrivas1/equity-features/issues/467), [milestone](https://github.com/atulsrivas1/equity-features/milestone/23), [GOV-031](https://github.com/atulsrivas1/equity-features/issues/464). Current execution status belongs to the live Project. No date or implementation start is selected.

## EQ-147: Implement MACD line, signal and histogram

[Issue](https://github.com/atulsrivas1/equity-features/issues/481); 5 provisional complexity points; ownership: core.

Specify fast/slow EMA and signal seeds, periods and availability. Fast and slow chains are independent; signal depends on ordered MACD observations. Reuse compatible EMA preparation without a whole-indicator barrier.

Dependencies: [EQ-138](https://github.com/atulsrivas1/equity-features/issues/472).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent hand-calculated seeds and line/signal/histogram fixtures, insufficient history, corrections and legal state parity; direct/fused and worker performance cases.

## EQ-148: Implement directional movement, DMI and ADX

[Issue](https://github.com/atulsrivas1/equity-features/issues/482); 8 provisional complexity points; ownership: core.

Specify directional movement ties, true range, smoothing, DX/ADX initialization and zero-denominator availability. Share compatible true range; ADX follows its actual DMI/DX observations.

Dependencies: [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471), [EQ-138](https://github.com/atulsrivas1/equity-features/issues/472).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent OHLC fixtures including inside/outside bars, ties, flat prices and warm-up; replay/state equivalence, compatibility isolation and repeated timing.

## EQ-149: Implement stochastic oscillators and Williams percent R

[Issue](https://github.com/atulsrivas1/equity-features/issues/483); 5 provisional complexity points; ownership: core.

Specify rolling high/low populations, close location, smoothing stages and zero-range handling. Reuse compatible extrema; independent selected oscillators need not wait on unrelated indicators.

Dependencies: [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent extrema/oscillator fixtures, ties, zero ranges, evictions, gaps and smoothing warm-up; compare shared versus independent preparation.

## EQ-150: Implement OBV, accumulation/distribution and Chaikin money flow

[Issue](https://github.com/atulsrivas1/equity-features/issues/484); 8 provisional complexity points; ownership: core.

Specify signed OBV ties/initialization, close-location weighting, zero-range bars, rolling denominators and exact volume units. Share admitted bars and compatible money-flow preparation with independent result readiness.

Dependencies: [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470), [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent synthetic volume/price fixtures, zero volume/range, warm-up, revision replay, precision and order cases; benchmark combined families and direct outputs.

## EQ-151: Implement explicitly aligned Ichimoku components

[Issue](https://github.com/atulsrivas1/equity-features/issues/485); 8 provisional complexity points; ownership: core.

Specify conversion/base/leading/lagging components, periods, displacement and observation versus display timestamps. A displayed shifted value cannot imply future information was available at origin time.

Dependencies: [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent timestamp-index fixtures, short history, gaps, displaced arrays, cutoff/availability and lookahead counterexamples; measure extrema reuse and output size.

## EQ-152: Qualify and deliver advanced indicator release

[Issue](https://github.com/atulsrivas1/equity-features/issues/486); 5 provisional complexity points; ownership: cross-repository acceptance.

Reconcile every selected indicator with public discovery/specifications and actual supported worker bindings. Publish independent dependency diagrams, capability matrix and synthetic examples; preserve R17/R18 behavior.

Dependencies: [EQ-147](https://github.com/atulsrivas1/equity-features/issues/481), [EQ-148](https://github.com/atulsrivas1/equity-features/issues/482), [EQ-149](https://github.com/atulsrivas1/equity-features/issues/483), [EQ-150](https://github.com/atulsrivas1/equity-features/issues/484), [EQ-151](https://github.com/atulsrivas1/equity-features/issues/485), [EQ-146](https://github.com/atulsrivas1/equity-features/issues/480).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent math/temporal fixtures, serial/parallel and state parity where supported, repeated workload timing/memory, both-platform clean installs, final review and exact release/publication readback.

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
