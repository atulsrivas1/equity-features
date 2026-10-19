# R18 — Dependency-driven execution and resource efficiency

Owner-requested planning, October 19, 2026. [Epic](https://github.com/atulsrivas1/equity-features/issues/466), [milestone](https://github.com/atulsrivas1/equity-features/milestone/22), [GOV-031](https://github.com/atulsrivas1/equity-features/issues/464). Current execution status belongs to the live Project. No date or implementation start is selected.

## EQ-142: Qualify exact output DAGs and execution baselines

[Issue](https://github.com/atulsrivas1/equity-features/issues/476); 5 provisional complexity points; ownership: workers.

Specialize selected outputs into operand/state/coverage nodes; distinguish configuration gates and publication ownership. Baseline sequential/thread/process modes, stage costs, queue/lock waits, copying, startup and sink bottlenecks. Reject unresolved dynamic/alias paths from scheduler refinement until qualified.

Dependencies: [EQ-141](https://github.com/atulsrivas1/equity-features/issues/475).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent dependency counterexamples, cycle checks, blocked-unrelated-branch cases and repeatable full-result parity; freeze representative workload and performance adoption rule before measurement.

## EQ-143: Reuse compatible inputs and fuse shared calculation work

[Issue](https://github.com/atulsrivas1/equity-features/issues/477); 8 provisional complexity points; ownership: core + workers + I/O.

Remove a demonstrated repeated admission, conversion, scan or serialization cost. Reuse only exact symbol/population/interval/window/cutoff/source/configuration/revision identities; immutable ownership and bounded lifetimes are explicit.

Dependencies: [EQ-142](https://github.com/atulsrivas1/equity-features/issues/476).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: A/B end-to-end timing, independent output oracle, incompatible-identity rejection, bounded cache/queue memory, error/retry/cancel and stale-input cases; retain fallback if improvement is not demonstrated.

## EQ-144: Schedule independent ready branches with ordered state ownership

[Issue](https://github.com/atulsrivas1/equity-features/issues/478); 8 provisional complexity points; ownership: workers.

Refine only proven coarse serialization: independent same-symbol feature families can run once their own operands are ready. Preserve recurrence and mutation order inside each state key, actual universe joins and publication commit authority. Use tasks large enough to amortize transport.

Dependencies: [EQ-142](https://github.com/atulsrivas1/equity-features/issues/476), [EQ-143](https://github.com/atulsrivas1/equity-features/issues/477).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Execution traces prove independent overlap and true dependency order; skew, missing benchmark, shared alias, cancellation/replay and deterministic result/status parity cases. No persistent live scheduler duplication of LIVE-002.

## EQ-145: Qualify adaptive bounded resource profiles

[Issue](https://github.com/atulsrivas1/equity-features/issues/479); 8 provisional complexity points; ownership: workers + I/O.

Use one job-wide CPU/native-thread/memory/I/O budget, explicit OS/other-job reserves, backpressure and admission. Detect actual available capacity at run time; benchmark supported concurrency levels before considering wider limits. Report declared reservations versus observed or enforced limits honestly.

Dependencies: [EQ-143](https://github.com/atulsrivas1/equity-features/issues/477), [EQ-144](https://github.com/atulsrivas1/equity-features/issues/478).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Scaling curves and repeat distributions, peak parent/child RSS and copies, nested-thread oversubscription, memory pressure, queue saturation, sink contention, cancellation and low-resource fallback. CPU utilization alone is not acceptance.

## EQ-146: Qualify and deliver measured parallel execution

[Issue](https://github.com/atulsrivas1/equity-features/issues/480); 5 provisional complexity points; ownership: cross-repository acceptance.

Adopt only changes meeting predeclared correctness, wall-time and resource criteria; document workload-specific winning and losing profiles. Preserve existing source-independent APIs and baseline fallback; publish reproducible synthetic benchmark instructions.

Dependencies: [EQ-145](https://github.com/atulsrivas1/equity-features/issues/479).

First action: freeze and review the original mathematical/pre-code contract, exact operand/state/coverage dependencies, independent fixtures, capability matrix and measurement adoption rule.

Validation and accepted result: Independent numerical/status/quality/evidence parity, critical-path and end-to-end latency/throughput measurements, both-platform installed artifacts, final review, publication/readback and complete R18 evidence. No universal fastest claim.

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
