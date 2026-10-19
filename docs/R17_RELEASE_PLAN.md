## EQ137 delivery checkpoint — October 19, 2026

EQ136 is accepted Done. EQ137 is In progress in [PR500](https://github.com/atulsrivas1/equity-features/pull/500). [Measured preparation evidence](stories/EQ-137_BENCHMARK.md) and independently reviewed candidate Windows/Linux artifacts qualify exact source `c7a46d6`; final-head review/CI/artifacts, publication and main acceptance remain. The [session handoff](SESSION_HANDOFF.md) records exact proofs, remaining gates and resume steps. Scope/dependencies are unchanged; the live Project owns status. Finish R17 before the selected R18 handoff and execution. Earlier snapshots below retain their original dates and limits.

## EQ136 final review corrections and current gates — October 19, 2026

EQ136#470/PR499 is Code review. Full original contracts/references are reviewable;79author methods passed (24intraday,31daily,12CIgate,12policyprovenance). Separate review of74d independently passed78methods and80original synthetic mathematical crosschecks, but its ATRsingle-anchor quality finding required a successor: now warm-up observes close-only with expectedN+1, observed1, and has its own24th reference case. Config-bound evidence_limit, printable/limited source/config labels, explicit local compatible-preparation protocol and deterministic absent/empty reason precedence are concrete corrections. Current [author receipt](stories/EQ-136_AUTHOR_VALIDATION.json) binds exact changed bytes and preserves the prior receipt/failure. Renew exact-source separate review and current CI; older74d results are not automatically acceptance of these changed bytes.

GOV031 is accepted Closed/Done; EQ136 is specification-only, not a delivered kernel or accepted R17. Remaining priorities: finish EQ136 review/CI/publication/readback; admit EQ137 only from accepted contracts and reviewed concrete preparation/build plan; retain R17-first before R18 handoff/execution. Companion/package inspection notes are local preparation only, with no next-story code or Ready claim. Live Project owns actual status.

## Owner selects bounded R17 execution — October 19, 2026

The owner requested the R17 handoff and then work on R17. [Execution handoff](R17_AUTONOMOUS_HANDOFF.md), [inputs](R17_INPUTS.json), [test strategy](R17_TEST_STRATEGY.md) and [EQ136 initial pre-code proposal](stories/EQ-136_PLAN.md) now make the bounded mission concrete. This supersedes earlier preparation-only/no-start-selection text prospectively. GOV030/PR463 and GOV031/PR498 review/current-CI/publication prerequisites remain actual gates; no kernel, accepted math/new registry ID or measured performance result is claimed. Work on this preparation remains under GOV031; EQ136–141 stay Backlog until real Ready admission. New separate-review authorization for PR498/handoff/R17 is pending; earlier bounded grants do not imply it. Live Project remains status authority.

# R17 — Intraday equity foundations

Owner-requested planning, October 19, 2026. [Epic](https://github.com/atulsrivas1/equity-features/issues/465), [milestone](https://github.com/atulsrivas1/equity-features/milestone/21), [GOV-031](https://github.com/atulsrivas1/equity-features/issues/464). Current execution status belongs to the live Project. No date or implementation start is selected.

## EQ-136: Define intraday mathematics, capability and dependency contracts

[Issue](https://github.com/atulsrivas1/equity-features/issues/470); 5 provisional complexity points; ownership: core/contracts.

Freeze selected finalized-bar intervals, return/price bases, seeds, warm-up, missing/partial bars, session resets, adjustments, cutoff equality and correction/replay rules. Define per-output direct operands separately from upstream lineage; allocate new feature IDs only after specification review.

Dependencies: GOV-031/GOV030 planning publication and accepted R16 baseline.

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent tiny synthetic histories cover flat/rising/falling prices, short history, session boundaries, gaps, split-compatible revisions and seed alternatives. Existing daily semantics remain separately verified.

## EQ-137: Implement compatible rolling primitives and shared preparation

[Issue](https://github.com/atulsrivas1/equity-features/issues/471); 8 provisional complexity points; ownership: core.

Implement selected rolling price moments, extrema, return and true-range preparation with explicit identity and lifetime. Share compatible scans and intermediate values without coupling unrelated output readiness; numerical stability and legal state/merge behavior are explicit.

Dependencies: [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Compare against independent direct-window/high-precision expected results; test eviction, cancellation of old observations, restore/replay and unsupported merges. Measure fused versus separate preparation and peak memory.

## EQ-138: Implement interval-aware EMA, RSI and ATR

[Issue](https://github.com/atulsrivas1/equity-features/issues/472); 8 provisional complexity points; ownership: core.

Implement qualified intraday variants using supplied finalized bars. Independent EMA, RSI and ATR branches share admitted facts; recursive observations remain ordered per symbol, interval, configuration and revision. Advertise only implemented batch/update/restore/merge capabilities.

Dependencies: [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470), [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent seed and warm-up fixtures, missing/zero denominators, session/gap policies, batch versus legal update/replay parity; benchmark families separately and together.

## EQ-139: Implement rolling price bands

[Issue](https://github.com/atulsrivas1/equity-features/issues/473); 5 provisional complexity points; ownership: core.

Implement selected Bollinger-style price bands from rolling price moments with explicit variance convention, band parameters and zero-width policy. Price moments are not return volatility. Bands do not depend on RSI or ATR.

Dependencies: [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470), [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent mean/variance/band fixtures, constant values, numerical cancellation, short windows, large offsets and correction replay; quantify compatible preparation reuse.

## EQ-140: Wire qualified feature inputs and independent worker branches

[Issue](https://github.com/atulsrivas1/equity-features/issues/474); 5 provisional complexity points; ownership: workers + I/O contracts.

Bind the selected new APIs to supplied normalized inputs. Audit existing dispatcher gaps for structure, top-K, continuous quotes and prior-close arguments; wire only capabilities supported by admitted inputs, reporting explicit unsupported requirements. Keep acquisition outside calculations.

Dependencies: [EQ-138](https://github.com/atulsrivas1/equity-features/issues/472), [EQ-139](https://github.com/atulsrivas1/equity-features/issues/473).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Synthetic end-to-end source-to-result contract tests, prior-close unavailable versus supplied cases, required-input discovery, and branch isolation when an unrelated reference is absent. Compare all values/status/quality/evidence with direct APIs.

## EQ-141: Qualify and deliver intraday foundation release

[Issue](https://github.com/atulsrivas1/equity-features/issues/475); 5 provisional complexity points; ownership: cross-repository acceptance.

Freeze selected R17 outputs and artifact versions; establish direct and current-worker compute-only and end-to-end baselines before adopting acceleration. Verify original daily API compatibility and all selected story evidence.

Dependencies: [EQ-140](https://github.com/atulsrivas1/equity-features/issues/474).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Repeated small/large/skewed workloads, cold/warm paths, current Windows/Linux artifacts and clean installs, separate final-head review, published-source/artifact readback and documentation. No live feed/SLA claim.

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

## Specification-only gate applicability

EQ-136 delivers contracts, independent expected fixtures and the benchmark/adoption plan. Actual runtime benchmarks and installed-artifact gates apply to subsequent implementation changes; no benchmark of documentation or invented runtime result is required for this specification-only story. Record the no-impact disposition.
