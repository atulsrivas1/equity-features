# R18 correctness and performance qualification

This is the proposed protocol for [GOV034](https://github.com/atulsrivas1/equity-features/issues/564) and existing EQ142–146. No R18 workload, benchmark or implementation is claimed. Each actual executable head and concrete harness requires separate review before timing and current artifact qualification before delivery.

## Correctness before optimization

Use the original R17 independent rational/Decimal/golden fixtures and accepted readiness/precision/quality/identity cases, plus new independently specified graph/ownership counterexamples in [EQ142](stories/EQ-142_PLAN.md). Full result comparison includes values, null validity, statuses, reasons, quality counts, deterministic evidence, headers, C/K/E, source/config/algorithm/revision and publication identity. Direct/SDK committed output parity is separate from independent numerical correctness. A shared implementation is not its own only oracle.

Verify exact selected prerequisite closure, cycle/alias rejection, no false unrelated edge, and actual state/universe/publication ordering. Missing, observed empty and unavailable remain distinct. Unknown callbacks retain conservative behavior. Test incompatible scope, mutation/lifetime, cancellation/retry/replay, source correction, limits, transport failure, pending-after-commit and low-resource paths. No new rollback, persistence or update/restore/merge capability is inferred.

## EQ142 baseline and exclusive costs

Use synthetic deterministic admitted inputs at the frozen R17 definitions: small1×256, balanced16×1024 and skew15×256+1×1024, N20/all-eight, plus focused independently ready families and exact compatible/incompatible task selections. Reuse existing fixture definitions only after current full-byte admission and full-result oracle pass; retain rejected1536/2048/4096 transport cases as admission controls, not admitted throughput. Record exact generator/config/input/expected hashes, actual task composition and shard count. More configured workers cannot create extra independent components.

Baseline sequential/thread/process modes and supported degrees1/2/4/8 only when current OS/runtime and admission permit. Capture admitted compute and cold full source→admission→transport→compute→complete SDK publication→lookup/readback paths separately. Warmed direct calls, within-run pools and a hypothetical persistent worker are distinct; advertise only actually executed modes. Cross-platform installed qualification does not establish cross-platform speed.

Instrument development harnesses outside pure calculations. Name every span's owner, clock, thread/process, parent span and inclusive/exclusive policy. Count actual admission/hash/canonicalization/encoding traversals, input/result bytes, allocations/copies where observable, IPC, startup/shutdown, queue/lock waits, result joining, and publication/lookup. Distinguish counts, estimates and measurements. Exclusive intervals on one timeline must not double-count nested work; process spans must not be summed into wall makespan. Retain critical-path trace relationships and residual/unobserved time explicitly.

Qualify instrumentation with deterministic counterexamples and trace closure, plus repeated instrumented versus uninstrumented A/A controls. Freeze acceptable overhead from that control before using attributed timings; do not subtract guessed overhead or change the tolerance after observing an optimization. If instrumentation materially changes execution, report it and obtain a lighter qualified baseline. No default/profile change follows from EQ142's observations alone.

## Freeze adoption before any optimized B

For each later accepted comparison, freeze case definitions, source/import origins, dependency/runtime versions, full expected result hashes, capacity/reserves, degrees, measurement classes, ordering, seed and failure policy. Use at least two warmups and seven retained samples per case/mode, preserve raw warmups/retained samples, and complete all A observations and noise thresholds before B. Retain the same instrument/collector semantics across A/B. No concurrent local builds/tests during timing.

Retain R17's conservative comparison rule unless a prospectively reviewed change is explicitly justified before timing: wall median reduction strictly exceeds max(5%,3×inclusive-IQR(A)/median(A)); B median whole-job CPU≤1.25×A; observed aggregate memory≤both the predeclared absolute budget and1.25×A; small-case p95≤1.10×A. Freeze the precise quantile method in the executable protocol. Full correctness/parity and every declared admission/resource condition must pass. A lower descriptive median alone is a nonwin. A no-win result retains baseline fallback; do not retune thresholds after B.

For supported resource profiles capture current allowed CPU capacity/OS restrictions, native-thread totals, actual free memory and explicit parent/OS/other-job reserves, queue/input/result/IPC/publication bounds and available backend capacity. Account for terminated children in job CPU; sampled RSS may miss peaks and is not physical enforcement. Record actual available, declared reserved, observed and enforced resources separately. Use scaling curves and tail distributions, not CPU utilization as the adoption criterion. If required evidence cannot be collected, reject that profile rather than inventing a resource pass.

## Delivery

Every source/config/harness change renews affected review, fixtures, strict typing, boundary tests, meaningful resource/admission tests, current CI and applicable both-platform clean wheel/SDist/base/combined-extra qualification. Preserve source/archive/rebuild/install/typing/core provenance and exact skip ledgers. Changed package execution cannot reuse old artifacts merely because the version label matches. Main publication must match reviewed trees and attribution; current artifact access/digests/expiry and separate final acceptance precede Released/Done. Audit every assigned milestone22 issue, including GOV034, before final E26/milestone closure.

Keep failed builds, rejected resource profiles, partial measurements and source-mismatch receipts with their original identities. Report exact workload/hardware/source applicability and finite channel limits. No universal fastest, live latency SLA, persistent worker, stable registry or physical durability claim follows from these synthetic tests.
