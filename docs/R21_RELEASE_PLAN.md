# R21 — Equity tape, quote and path analytics

Owner-requested planning, October 19, 2026. [Epic](https://github.com/atulsrivas1/equity-features/issues/469), [milestone](https://github.com/atulsrivas1/equity-features/milestone/25), [GOV-031](https://github.com/atulsrivas1/equity-features/issues/464). Current execution status belongs to the live Project. No date or implementation start is selected.

## EQ-158: Implement rolling trade windows and tick-rule signed volume

[Issue](https://github.com/atulsrivas1/equity-features/issues/492); 8 provisional complexity points; ownership: core.

Specify event ordering, timestamp ties, window endpoints, sign carry/seed, eligibility, volume/notional precision and late correction replay. These trade-sign proxies must not be represented as observed aggressor or dealer positions.

Dependencies: [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470), [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent tiny tapes with ties, unchanged prices, seed gaps, expiration and corrections; ordered-state and batch/replay parity plus hot-symbol throughput/memory cases.

## EQ-159: Implement microprice and selected quote dynamics

[Issue](https://github.com/atulsrivas1/equity-features/issues/493); 8 provisional complexity points; ownership: core + qualified input bindings.

Specify selected microprice/quote-change outputs, size/price units, crossed/locked/zero-size/invalid quotes, sampling and coverage. Trade-snapshot quotes cannot silently satisfy continuous quote requirements.

Dependencies: [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent price/size examples, gap/stale/invalid/crossed/zero-size coverage, ordered quote state, cutoff replay and unavailable-input cases; direct/worker and memory benchmarks.

## EQ-160: Implement VWAP slopes and selected path statistics

[Issue](https://github.com/atulsrivas1/equity-features/issues/494); 8 provisional complexity points; ownership: core.

Specify which bar/trade VWAP series and eligible population each slope/path output consumes, coordinate/time basis, anchor and sampling. Support supplied compatible series without forcing a trade-window recomputation.

Dependencies: [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471), [EQ-158](https://github.com/atulsrivas1/equity-features/issues/492).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent weighted-series and time-axis fixtures, irregular spacing, zero volume, missing intervals, origin-time availability and correction cases; demonstrate series preparation reuse.

## EQ-161: Implement path efficiency and choppiness measures

[Issue](https://github.com/atulsrivas1/equity-features/issues/495); 5 provisional complexity points; ownership: core.

Specify selected path-efficiency/choppiness formulas, range/ATR/return basis, window, gaps, zero denominators and log-domain validity. Direct operands are output-specific; no blanket context or scanner dependency.

Dependencies: [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471), [EQ-138](https://github.com/atulsrivas1/equity-features/issues/472).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent monotone/flat/oscillating OHLC fixtures, short histories, gap/zero-range and invalid-log cases, replay parity and shared preparation performance.

## EQ-162: Implement deterministic notional-ranked largest prints

[Issue](https://github.com/atulsrivas1/equity-features/issues/496); 5 provisional complexity points; ownership: core + worker bindings.

Specify eligible trade notional, exact units/precision, ranking, K, stable tie keys and partition merge rules. Existing size-ranked top-K remains separately named and compatible.

Dependencies: [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent trades whose size and notional rankings differ, equal-notional ties, boundaries, partition/merge and overflow cases; benchmark selection and transport without claiming equivalent rankings.

## EQ-163: Qualify and deliver tape, quote and path release

[Issue](https://github.com/atulsrivas1/equity-features/issues/497); 5 provisional complexity points; ownership: cross-repository acceptance.

Qualify selected equity outputs end-to-end with real declared input capabilities. Preserve source-independent calculations and previously accepted contracts; scanner/watchlist/strategy policies, options exposures and live feed deployment remain separate.

Dependencies: [EQ-158](https://github.com/atulsrivas1/equity-features/issues/492), [EQ-159](https://github.com/atulsrivas1/equity-features/issues/493), [EQ-160](https://github.com/atulsrivas1/equity-features/issues/494), [EQ-161](https://github.com/atulsrivas1/equity-features/issues/495), [EQ-162](https://github.com/atulsrivas1/equity-features/issues/496), [EQ-157](https://github.com/atulsrivas1/equity-features/issues/491).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent math/temporal and source capability fixtures, requested-output closure, bounded state and serial/parallel parity, representative both-platform benchmarks/install artifacts, final review and exact published release readback.

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
