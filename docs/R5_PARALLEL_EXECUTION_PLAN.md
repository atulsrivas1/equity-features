## Current R5 review and measured evidence — October 8, 2026

Current canonical AGENTS.md authorizes separate local automated Codex reviewers for PR303 and all bounded R5 final heads. This supersedes the historical unresolved-authorization preparation text below; no hosted activation or human review is claimed. EQ066 now records [complete physical measurements](stories/EQ-066_BENCHMARK.json), [bounded measured defaults and private admission matrix](api/WORKER_PILOT_READINESS.md) and [actual source/native/repeat receipt](stories/EQ-066_SOURCE_RECEIPT.json). Publication/actual-main/readback/final acceptance remain separate gates. Earlier pre-code design/scope/failed review and native evidence remain preserved; stop before R6 after bounded R5 closure.

## Current R5 review authorization — October 7, 2026

The owner authorized separate local Codex reviewers for PR303 and all R5 stories. See [review policy](CODE_REVIEW.md). This supersedes earlier pending-authorization statements below without waiving completed final-head review or other acceptance gates. PR303 planning remains under qualification; no R5 worker implementation starts here.

# R5 bounded parallel execution plan

Owner-authorized planning clarification, October 7, 2026. This refines existing E08/R5 stories; it starts no worker implementation, adds no release/date commitment and changes no calculation or sink contract. The live Project remains status authority. Advanced native acceleration and broad tuning remain R8.

## Accepted component baseline and limits

R4.1 is accepted and [BUG-005 #301](https://github.com/atulsrivas1/equity-features/issues/301#issuecomment-6041276187) is Closed/Project Done. The corrected experimental Parquet version is 0.1.0a1 on I/O main `4603c6e50331a5e8a82b13b62a0cdd5ffaa0e4bf`; worker skeleton main is `3423c64d637885698f4ba471b2f4c969cd8b318d`. Core main before this planning change is `e149926e70a187117df911298d36a518c7ea6eb1`. Other declared versions are unchanged. Artifact retention is finite; recheck availability and identities before reuse. These receipts establish their stated qualification, not multi-worker throughput.

Calculations stay pure. Workers alone own scheduling, partitioning, dependency barriers, resource budgets, task claims and accepted-generation selection. Adapters own acquisition/normalization; sinks own backend conversion and publication. Source-independent calculations permit independent invocations, not arbitrary splitting of mathematical dependencies or an unconditional thread-safety guarantee for consumer extensions.

## Task and dependency model

Prefer an instrument or instrument shard, governed session/session range and compatible feature group as the task unit. Freeze exact task/input/config identities in EQ-057 before implementation. Acquire bounded canonical batches once for compatible calculations within a task; never reuse across incompatible revision, cutoff, availability or configuration scopes. Acquisition reuse cannot require an unbounded cache or full-corpus materialization.

Parallelize independent instruments and session-local tasks when all required inputs and initialization are supplied. History-dependent calculations preserve per-instrument order, explicit warm-up and qualified checkpoint/state transfer. Batch-only features can parallelize across independent instruments; splitting one calculation needs its declared capabilities. Continuous-quote partition merge remains unsupported. Cross-sectional assembly waits for declared universe coverage and committed receipts while unrelated ready tasks continue.

## Publication ownership

Current [Parquet implementation](https://github.com/atulsrivas1/equity-feature-io/blob/4603c6e50331a5e8a82b13b62a0cdd5ffaa0e4bf/packages/parquet/src/equity_feature_parquet/sink.py) acquires one `writer.lock` per output root namespace and retains it throughout the write attempt. Different keys/partitions under the same root serialize. Independent roots provide separate lock scopes, but require explicit destination ownership, receipt-based assembly and qualified query/catalog discovery; merely adding partitions does not establish parallel publication.

The [DuckDB sink](https://github.com/atulsrivas1/equity-feature-io/blob/4603c6e50331a5e8a82b13b62a0cdd5ffaa0e4bf/docs/api/DUCKDB_SINK.md) serializes output ownership per database; foreign live writers can make readers BUSY. A shared output database uses a bounded publication queue and serialized publisher. Separate output databases are another candidate only with explicit shard/catalog/reader qualification. Do not silently enable multiple worker-process writers to one database or mutate the read-only input store.

Select supported ownership during EQ-061 planning and honor capability admission. Do not change sink locking or storage layout in worker code. Task completion, committed sink receipts and serialized accepted-generation catalog selection remain distinct. Exactly-once execution, network-filesystem durability and power-loss safety are not implied.

## Resource and execution policy

EQ-062 defines one combined budget for worker execution, backend threads, resident input/result batches, queue capacity and I/O. Use bounded queues with backpressure and explicit cancellation/cleanup; report enforced versus measured/estimated limits. Each adapter/sink instance has explicit ownership; do not assume connection or custom callback sharing is safe. Coarse tasks amortize process startup and serialization while preserving deterministic row conservation. Compare process, thread and sequential strategies where relevant to the actual workload; choose defaults from measurements. Maximum configured worker count is not a performance target.

## Story ownership and acceptance

### [EQ-057 #65](https://github.com/atulsrivas1/equity-features/issues/65)

- Define deterministic task boundaries using instrument/shard, governed session range and compatible feature group, with input revision/configuration identities and explicit output ownership.
- Declare ordered-history, warm-up/state-transfer requirements and only qualified merge capabilities; batch-only calculations may still run independently across instruments.
- Specify bounded input reuse within a task without weakening source revision, cutoff, availability or configuration isolation.

### [EQ-060 #68](https://github.com/atulsrivas1/equity-features/issues/68)

- Block only declared dependencies; demonstrate unrelated ready tasks continue while a history/reference/universe dependency waits.
- Require expected universe/shard coverage and valid committed completion receipts before cross-sectional assembly; staged files do not satisfy barriers.

### [EQ-061 #69](https://github.com/atulsrivas1/equity-features/issues/69)

- Honor current lock scopes: Parquet serializes whole write attempts per output root; distinct partition IDs in one root do not permit concurrent writers. DuckDB output uses serialized writer ownership per database.
- Specify and qualify explicit publication ownership: independent Parquet roots with receipt-based assembly, or a bounded single publisher for a shared destination. Backend layout/conversion stays in the sink.
- Test contention, cancellation, retry and uncertain commit without dropped results or premature catalog visibility; do not change sink concurrency guarantees implicitly.

### [EQ-062 #70](https://github.com/atulsrivas1/equity-features/issues/70)

- Define coarse deterministic partitions, row conservation, input reuse and bounded queues/backpressure; avoid unrestricted repeated whole-file scans and per-row process tasks.
- Budget worker CPU, backend threads, memory, in-flight inputs/results and I/O together; state which limits are enforced and which are observed estimates.
- Compare process/thread/sequential execution where relevant before choosing defaults; record startup, copying/serialization and engine-thread costs. No assumed universal thread safety or linear speedup.
- Independently test resource admission, queue saturation, cancellation, ordering/warm-up and supported versus unsupported partition merges.

### [EQ-065 #73](https://github.com/atulsrivas1/equity-features/issues/73)

- Record acquisition, calculation, serialization/publication, queue wait and lock contention with units and measurement boundaries; distinguish overlapping stage work from elapsed wall time.
- Exercise dependency isolation, bounded backpressure and publisher faults with structured task/partition identities and unchanged result/evidence bindings.

### [EQ-066 #74](https://github.com/atulsrivas1/equity-features/issues/74)

- Benchmark the same frozen representative small/large/skewed workload with 1, 2, 4 and 8 workers where capacity permits; explicitly record skipped configurations and resource reasons.
- Record repeated-run end-to-end throughput, task latency distribution, peak process/job memory with sampling limits, input/output bytes, stage costs, queue waits and contention; bind hardware, runtime, versions, source revision, batch size, worker count and backend threads.
- Verify numerical/status/quality/evidence/input-identity parity against a single-worker reference and independent fixtures; compare logical content rather than incidental file bytes or operational timestamps.
- Select bounded defaults from measured benefit and correctness; document saturation or no improvement without an invented speedup threshold. Real-data pilot retains separate source/PIT/warm-up/privacy and month/annual capacity gates.

## Validation, documentation and accepted end state

Use independently expected synthetic fixtures for numerical/temporal boundaries plus single-worker versus multi-worker logical parity. Include empty/missing/partial inputs, ordered history, unsupported merge, blocked dependencies, duplicate task retry, queue saturation, publisher failure, uncertain commit recovery and no premature catalog visibility. Public workloads must be synthetic or explicitly licensed. No private pilot is admitted solely by passing synthetic tests.

Measure 1/2/4/8-worker runs where hardware permits, repeating comparable frozen workloads and recording sample counts, variability and cache state. Report end-to-end elapsed time separately from overlapping stage timings; report memory observation method and limits rather than asserting hard RSS guarantees. Baselines and caps must be explicit before the pilot. A recorded no-improvement outcome is valid; no numerical speedup or deadline is promised.

Documentation accompanies each implementation story: manifests/API and examples for EQ-057, dependency/barrier policy for EQ-060, supported destination ownership and receipt handling for EQ-061, resource/default configuration for EQ-062, measurement/error semantics for EQ-065 and reproducible benchmark/pilot acceptance for EQ-066. Update issues, backlog and handoff with actual evidence.

The R5 accepted end state is dependency-aware bounded execution, qualified sink-aware publication and reproducible scaling evidence with unchanged mathematical/availability guarantees. Existing lifecycle, separate final-head review, relevant installed/native checks and actual release/readback gates remain mandatory. General R5 local-review authorization remains unresolved; the bounded BUG-005 authorization does not extend by inference. This planning PR also needs an applicable separate review before merge.
