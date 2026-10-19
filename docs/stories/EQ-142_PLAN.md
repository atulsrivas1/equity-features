# EQ142 pre-code plan: exact dependencies and current cost baseline

[Issue #476](https://github.com/atulsrivas1/equity-features/issues/476), [E26](https://github.com/atulsrivas1/equity-features/issues/466), R18. This is a proposal in GOV034's handoff packet, not Ready, implementation, accepted graph semantics or a measured bottleneck. Required predecessors are accepted EQ141/R17, published GOV034 and actual reviewed current inputs. [Execution map](../R18_EXECUTION_MAP.md) records current source facts; [test strategy](../R18_TEST_STRATEGY.md) supplies the prospective measurement gates.

## Deliverable and scope

Produce a source-bound selected-output dependency/ownership specification, independently expected counterexample fixtures and an executable development baseline/trace tool for existing worker modes. Qualify actual stage costs, critical-path relations and byte/traversal counts without adopting a cache, widening default resources, splitting tasks or changing publication order. Any instrumentation must be opt-in with preserved public behavior and bounded overhead; final concrete API/schema/harness choices require review before code and timings. This story establishes evidence for EQ143–145, not their implementation.

## Freeze the graph before code

Represent nodes with explicit kind: admitted supplied fact, selected immutable preparation/witness, output, ordered state scope, configuration/coverage gate, result join, resource admission or publication owner. Every edge names its reason and exact source contract. Keep lineage different from a runtime prerequisite. Immutable compatibility includes exact population/instrument, grid/window/anchor/seed, unit/adjustment basis, config/algorithm, C/K/E, input source/revision and ownership/lifetime. Public task identity and reuse identity remain their accepted canonical domains; the graph cannot substitute a shallow key.

An executable refinement is allowed only for qualified built-ins with proven ownership. Unknown/dynamic/aliased callback paths receive an explicit conservative disposition; they must not silently become supposedly pure parallel nodes. Detect cycles and unresolved aliases before execution. Preserve true cross-sectional joins, recurrence order and full task-result/publication identity. A common malformed-input rejection is distinct from missing-field readiness in a valid admitted input.

Expected independent examples must cover:

1. Selected close-only EMA/RSI valid with H/L absent; ATR consuming H/L unavailable without blocking those cells; single-anchor ATR observes one close and remains warm-up.
2. Bands consuming exactly last N scheduled slots; unrelated earlier missing close irrelevant, required missing slot remains missing; no compaction. Constant width0 with unavailable position; unclamped position outside[0,1].
3. Large-offset/unrounded moment/radius/centered-residual fixtures, seeds/anchors and hostile global Decimal context; whole-call overflow remains the existing contract.
4. Different interval/window/period/cutoff/source revision/population/initialization keys cannot alias. Equal labels cannot certify equal input bytes, and mutable nested caller data cannot acquire a longer trusted lifetime by a label.
5. Same-symbol independent qualified families versus ordered recurrences, unknown callbacks, transitive population intersections and real universe joins. Extra configured workers alone do not prove overlap.
6. Complete selected FeatureResult headers/identity and once-global sorted evidence cap across any prospective join. Result and publication joins remain real edges.
7. Cancellation, retry/lookup, stale/revised input, partial result/commit, budget pressure and transport rejection. No invented postcommit rollback or physical durability.

Use independently specified expected graph edges/readiness and original numerical fixtures; running the current scheduler twice is not a dependency oracle. Keep numerical correctness distinct from full direct/SDK parity.

## Cost protocol

At exact reviewed worker/core/I/O heads, qualify an execution inventory from callback admission through partitioning, hashing/encoding, preparation/calculation/result joining, transport, coordinator validation, sink publication and lookup/readback. Preserve complete task/header/byte identity in the trace and actual shard topology. Existing CALCULATION/SERIALIZATION spans are composite, not exclusive arithmetic/encoding. Define nested/parallel spans and counts without adding them into an invented makespan ledger. Qualify actual clocks, event ordering, source binding, collector completeness, failure retention and instrumentation A/A overhead first.

Run the frozen small/balanced/skewed admitted cases with all-eight and focused independent family/task compositions, supported sequential/thread/process degrees and cold/admitted-compute classes. Retain 2 warmups+7 samples, all A before any later optimization B, original full result/readback hashes, CPU, parent/child memory, byte/copy/IPC/queue/startup/publication observations and explicit unavailable counters. Existing R17 raw source/timings remain historical controls and are not relabeled as fresh measurements.

Before Ready, publish the final concrete node/trace schemas, fixtures, counts/overhead criteria, exact task matrix, admission evidence, executable benchmark/adoption rules, source pins/versions and review findings disposition. These remaining choices are planned EQ142 preparation; they are not silently settled by this governance packet. No timing starts until its actual committed harness/source/protocol are separately reviewed and local qualification work has finished.

## Accepted end state

Independent graph/counterexample tests, current behavior/core compatibility, opt-in trace closure and measured overhead, reproducible full current baselines and exact complete-result parity pass. Document actual costs and unobserved areas without assuming a repeated source path dominates time. Publish all nonwins/failures, resource limits, measured component topology and recommended next evidence; no runtime optimization adoption. Update linked API/design/example or explicit no-impact records, release evidence, lessons and handoff. Complete final exact-head review, current source-bound CI/both-platform artifacts, guarded publication, actual main/channel readback and separate release acceptance before Done. Only that accepted result can admit EQ143.
