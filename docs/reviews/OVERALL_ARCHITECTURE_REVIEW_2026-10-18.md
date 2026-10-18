# Overall calculation, architecture and parallel generation review

Audit date: October 18, 2026. [AUDIT001#453](https://github.com/atulsrivas1/equity-features/issues/453). This is a cross-release audit, not selection of R17 or an implementation change. The source-freeze review below precedes its own publication; live issue/PR acceptance governs current lifecycle. Accepted R0-R16 and deferred scopes retain their original boundaries.

## Verdict

**Keep the architecture. The inspected calculations and orchestration have credible correctness evidence; faster end-to-end generation remains an unfulfilled performance objective for the retained benchmark workloads.** No new actionable mathematical, purity, shared-state or worker correctness defect was established in the inspected paths. This bounded conclusion is not formal verification of every input, equation, callback, interleaving or dependency.

Independent calculations are supported now. Parallel thread/spawn-process execution is supported and its actual result parity passed fresh tests. More workers are not automatically faster: existing R5/R8 measurements support the conservative sequential default. The next engineering investment should demonstrate one useful local throughput improvement with complete parity, rather than adding another infrastructure layer or changing defaults without evidence.

## Exact reviewed source

| Repository | Published main inspected |
| --- | --- |
| equity-features | `0d4eb0c1af33507bc0e9f8961180f175edcd7b8b` |
| equity-feature-io | `18d86761aa3eebb7414e51e8fa2aba089717b5eb` |
| equity-feature-workers | `a69ae9cfeb62730fc78705b4752b94c6f9438275` |

Dedicated clean worktrees retained the original working copies. Three separate local automated reviewers inspected mathematics, architecture and workers/performance. They are not human reviewers and did not independently reinstall or rerun the benchmarks. Root executed the fresh source tests separately. [Structured source/evidence index](OVERALL_ARCHITECTURE_REVIEW_2026-10-18.json).

## Independence and architecture

The dependency direction is appropriate: adapters acquire and normalize supplied facts; pure kernels validate and calculate typed results; workers orchestrate; sinks publish. A local caller can calculate directly without a worker, service, MCP server, ledger or strategy package. Optional consumers should stay optional.

The inspected kernels build local reducer state and consume immutable typed batches/configuration. Result composition preserves validated family results instead of silently recalculating them. Batch, incremental and declared partition merge paths share semantic rules. Mutable accumulators have one stream owner; reuse caches, supervisors and publisher drains enforce their ownership rules. Caller callbacks and factories are trusted local code, not sandboxed or automatically pure/thread-safe.

The supervisor supports sequential, thread and spawn-process modes. Its conservative instrument-connected shards retain chronological histories. Explicit dependency/assembly/universe barriers prevent arbitrary splitting of history, carry state and breadth calculations. This is not a universal automatic feature DAG planner: callers still prepare admitted inputs and dependent stages.

Source references: [composition](https://github.com/atulsrivas1/equity-features/blob/0d4eb0c1af33507bc0e9f8961180f175edcd7b8b/packages/features/src/equity_features/composition.py), [partitioning and supervisor](https://github.com/atulsrivas1/equity-feature-workers/blob/a69ae9cfeb62730fc78705b4752b94c6f9438275/packages/workers/src/equity_feature_workers/supervisor.py#L159), [dependency barriers](https://github.com/atulsrivas1/equity-feature-workers/blob/a69ae9cfeb62730fc78705b4752b94c6f9438275/packages/workers/src/equity_feature_workers/barriers.py), [architecture review](AUDIT001_ARCHITECTURE.json), [worker review](AUDIT001_WORKER_PERFORMANCE.json).

## Calculation correctness assessment

The mathematical review inspected core session reductions, quote validity/time integration, historical initialization and recurrences, volatility, relative/breadth dependencies, temporal admission, numeric overflow and streaming state/merge rules. A supplemental review covers continuous-market public kernels and timing/readiness boundaries. Detailed source identities, inspected paths and limitations are in the reviewer reports.

Positive evidence includes integer/checked decimal accumulation and exact Fraction arithmetic before declared float projections; independent literal/Fraction/Decimal expected results; explicit missing/null/zero and incomplete-coverage behavior; governed history/knowledge cutoffs; original expiry anchors; exact SMA witnesses for breadth; and batch/update/state-restore/legal-merge parity. Shared reducer parity alone cannot validate the shared mathematics, so independent arithmetic fixtures matter.

An investigated extreme relative-return cancellation case is not a confirmed bug: the API explicitly subtracts supplied Float64 projections. Exact differences in unavailable original raw operands cannot be recovered from equal rounded projections. Retain this precision boundary rather than promising exact raw-price cancellation. Caller-supplied calendars, completeness, identities, known-at and adjustment evidence remain trust inputs.

[Mathematics review](AUDIT001_MATHEMATICS.json), [continuous supplement](AUDIT001_CONTINUOUS_MATHEMATICS.json), [relative dependency contract](../api/RELATIVE_RETURNS.md).

## Fresh executed validation

| Suite | Successful test methods | Executed scope |
| --- | ---: | --- |
| Core source unit suites | 638 | Formula/admission/precision/availability/state/equivalence/purity/custom/adapter fixtures; four build/resource/performance/installed-only modules excluded |
| Continuous contracts and kernels | 24 | Existing constructor/codec/kernel tests, including the 99 allocated independent kernel fixture cases |
| Worker supervisor and barriers | 58 | Actual thread/spawn-process parity, row conservation, ordering/warm-up, reuse, budgets, cancellation, immutable result transport, owned spill, dependency/universe barriers and both-sink publication |
| Total | 720 | All three corrected runs: zero failures, errors or skips |

These are test-method counts, not counts of independent formulas; individual methods contain multiple fixtures/subcases and purity checks. All runs used existing Windows CPython 3.12 and exact source imports, without a new install or build. No new Linux execution, artifact qualification, provider/production workload or speed benchmark is claimed. Earlier accepted both-OS qualification remains its own evidence.

The initial core harness run failed with five import/setup errors because it omitted example/demo source paths. The corrected external harness changed only paths; product source was unchanged. The failed run and a shell-parsing correction are retained, not relabeled passing. [Exact selected modules, counts, source origins, log/harness hashes and limitations](AUDIT001_VALIDATION.json).

## What the speed evidence actually shows

The worker reviewer independently recomputed all 24 grouped min/median/max statistics from the retained EQ088 72 measurements, excluding its eight references, and reconciled EQ066's 162 sample parity flags and EQ085's six pipeline medians. This is independent analysis of historical measurements, not new timing on the current source.

For the largest EQ088 population, 64 instruments and 16,384 supplied synthetic trade rows, the whole-pipeline medians were:

| Sink | Sequential 1 | Threads 2 | Threads 4 |
| --- | ---: | ---: | ---: |
| Parquet | 69.333 s | 72.574 s | 77.237 s |
| DuckDB | 205.460 s | 217.156 s | 214.957 s |

Wider modes were slower here and failed the frozen adoption rule. Some smaller/large configurations improved modestly, with overlapping ranges; no mode won across required workloads. R5 also found all 24 process-configuration medians slower than its measured sequential baseline. These fixed shared-host Windows observations are not current-head universal timings, production capacity or proof that a larger representative compute-heavy workload cannot benefit.

There are plausible costs to measure in current code: Python tuple materialization and Python-loop kernels; repeated validation/codec/hash work; process startup, pickle/copies and whole-shard results; coarse same-instrument serialization; acquisition before dispatch and serial publication/generation/catalog afterward. Static inspection does not establish their relative contribution. Logical byte/CPU declarations are not hard RSS/physical resource limits or configuration of arbitrary native libraries; cancellation joins running cooperative work rather than imposing a hard callback deadline.

[Original benchmark analysis and all timing limits](../stories/EQ-088_ANALYSIS.md), [R5 retained measurements](../R5_ACCEPTANCE.md), [independent raw-statistic reconciliation](AUDIT001_WORKER_PERFORMANCE.json).

## Recommended next direction, in order

1. **Establish the intended throughput target.** Fix instruments, sessions/history, input kinds/rows, feature families, source/sink, memory/output limits and a useful end-to-end target. Use synthetic/licensed admitted facts and an independent full-result/status/quality/evidence/identity oracle. No workload or target is invented by this review.
2. **Measure the existing simplest local pipeline.** Attribute acquisition, conversion, validation, calculation, serialization/IPC, publication, readback and generation/catalog separately and together. Use a compute-only comparison to distinguish kernel time from pipeline time. Preserve warm/cold/cache/platform boundaries and original failures.
3. **Optimize the dominant measured cost.** Candidates include feature fusion/input reuse per instrument, avoiding duplicate canonical conversion/encoding or repeated setup, and then process task granularity/native-thread budgets. Change only a proven bottleneck; preserve exact identities, Unicode rejection, receipt/recovery behavior and numerical parity. A vectorized/native implementation remains conditional on measured benefit.
4. **Adopt parallel configurations only for demonstrated workload classes.** Compare existing sequential/thread/process modes with startup/IPC, shard skew, dependency barriers, memory and serial publication included. Preserve ordered history and legal merge laws. Retain sequential fallback when concurrency loses.

A short direct-use recipe can make existing capabilities easier to use; assess existing quickstart/worker examples before creating another abstraction. No new scheduler, framework, service, evidence layer, provider or security platform is justified solely to obtain ordinary feature-generation speed. These are prioritized recommendations, not selected implementation stories or a new release grant.

## Coverage and delivery limits

No confirmed defect means none established by this bounded inspection and these tests; it does not mean every calculation or concurrent execution is proven correct. Deep review of every service/MCP/ledger/strategy/label/provider/security path and all filesystem interleavings is outside this audit. Numerical validity is distinct from data-source truth, research usefulness, profitable strategies and production admission.

Report publication changes only documentation and continuity. Package APIs, mathematics, dependencies, versions, runtime defaults, executors and output protocols remain unchanged. R16 acceptance, deferred provider/witness/security/research/combined-C1 scope and paused automation are preserved. No R17 implementation follows automatically. Findings remain an empty list; recommendations are not disguised bug findings. Final report review, required current checks, normal default-branch publication and live acceptance/readback are recorded on issue453.
