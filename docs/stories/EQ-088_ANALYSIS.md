# EQ088 measured scheduling, spill and output result

The complete revision 4 experiment supports retaining sequential1 and the current production output layout. All 72 measured pipeline samples, eight references, six sort diagnostics and 18 layout queries completed without a recorded failure. This is a bounded synthetic Windows observation, not a universal speed, production-capacity or hard memory guarantee. Final release status is owned by [story99](https://github.com/atulsrivas1/equity-features/issues/99).

## Evidence and method

[Verbatim measurements](EQ-088_MEASURED.json), SHA256 cd77e789f255874f903032e7c5555baa728f725ad89287deb888a8d3ed144294 (1528616 bytes), bind worker source 4023b86d28e5f63ae652a0255e133db8463902b5 and [protocol revision4](EQ-088_PROTOCOL.md), frozen at canonical 6fc6dc66a45b3d5915996abf3d92d3a0f3d4cc04. [Post-run closure](EQ-088_POST_CLOSURE.json), SHA256 602c46e2333a2c8e1a75993d485d81a1de27e1bc09baeab060fac7c55a9d3675, verified 158 actual Git/worktree source files, eight installed accepted-archive RECORD/payload maps unchanged since reviewed preflights, all four immutable input populations, all 80 pipeline cases and all 87 returned result-file file hashes. The collector reads metadata/files and launches read-only Git subprocesses; it does not import products or execute native-engine workloads. Actual child harness assertions enforce installed runtime origins. Separate local automated Codex reviewer `/root/r8_preparation_review` verified the original substantive criteria with no findings, report SHA256 a6269f7fa976aeeaae43561e01b58fd4ba6feef51017f76e5fd22f339346dca3. Final documentation/current-candidate checks-artifacts and actual-main release gates remain distinct; see the [execution ledger](EQ-088_EXECUTION.json).

The real pipeline is DuckDB acquisition, five pure trade calculations, physical Parquet or DuckDB sink, canonical receipt readback, generation publication, accepted catalog selection/verification and close. All configurations agree on complete canonical result/quality/evidence/input content; independent count, volume, notional, VWAP and mean-size goldens pass. Capacity is 64 instruments × 256 rows, with per-instrument count 256, volume 640, notional 64768, VWAP 506/5 and mean size 5/2. All 72 samples plus eight references are fresh at one frozen source/input cohort; neither failed 54-sample population nor preflight timings are pooled.

Three repetitions rotate sequential1/thread2/thread4 order. Table timing is whole pipeline `pipeline_elapsed_ns`, including acquisition/publication/readback/close; fixture creation and measurement report assembly are outside it. Raw `isolated_process_wall_ns` also includes interpreter/import/observer/owned-process overhead. References warm inputs; OS cache, thermal state and ordinary background work are uncontrolled. GC defaults and native thread requests stay fixed. Windows 11/AMD64, CPython 3.12.10, DuckDB 1.5.6, NumPy 2.2.6 and PyArrow 20.0.0 were observed. The host reported 96 logical CPUs but 48 affinity/admitted slots, 273400750080 physical bytes and 174395461632 available bytes at initial admission. No exclusive host claim or Linux full-timing claim follows from the separate both OS small installation checks.

Every capacity mode/sink/repeat uses 360 seconds and nominal 25 ms memory sampling; other pipeline populations use 180 seconds/10 ms; native diagnostics 120 seconds. This prospectively reviewed new admission is not a pass under the old 180-second limit. Sampling can miss peaks/short children and ancestry, scan windows are sequential, shared pages can be double counted and observer RSS is excluded. The measured pipeline sampled aggregate RSS maximum was 170414080 bytes. Logical 128 MiB worker reservation and native configured limits are not process-RSS guarantees. Final observed owned-root bytes 426950557 were below the 1 GiB between-case admission ceiling; this is observation, not a filesystem quota. Production package code, dependency pins, equations, recorder defaults and all native/logical/disk budgets remain unchanged. Qualification caller reporting alone admits 256 tasks/12800 spans within the same 4 MiB allowance.

## Whole-pipeline elapsed seconds

Each entry is median [minimum, maximum], exactly three samples. Raw nanoseconds, per-task latency/throughput, memory observations and all source identities are retained above.

| Population | Sink | Sequential (1) | Threads (2) | Threads (4) |
| --- | --- | --- | --- | --- |
| small (4 tasks/16 rows) | parquet | 4.467 [4.422, 4.689] | 4.323 [4.260, 4.426] | 4.457 [4.361, 5.017] |
| small (4 tasks/16 rows) | duckdb | 12.741 [12.377, 12.856] | 12.510 [12.407, 12.833] | 12.844 [12.732, 13.049] |
| large (16 tasks/4096 rows) | parquet | 19.377 [18.043, 24.035] | 18.728 [16.765, 21.144] | 17.775 [17.478, 20.081] |
| large (16 tasks/4096 rows) | duckdb | 54.456 [51.486, 55.295] | 51.465 [49.581, 53.861] | 52.482 [50.499, 56.801] |
| skew (16 tasks/2528 rows) | parquet | 17.352 [16.645, 17.454] | 18.286 [18.047, 18.482] | 19.609 [17.523, 20.435] |
| skew (16 tasks/2528 rows) | duckdb | 52.473 [51.351, 53.550] | 55.575 [54.509, 57.231] | 53.271 [50.904, 54.236] |
| capacity (64 tasks/16384 rows) | parquet | 69.333 [67.987, 79.428] | 72.574 [68.060, 78.467] | 77.237 [73.377, 80.469] |
| capacity (64 tasks/16384 rows) | duckdb | 205.460 [205.082, 213.244] | 217.156 [216.850, 228.131] | 214.957 [214.438, 215.507] |

Neither wider mode meets the frozen rule: every large/skew/capacity sink must have median at least 10% below sequential with candidate maximum below baseline minimum, while every small sink median may regress at most 10%. Large-case ranges overlap and the largest population is slower with both wider modes; skew also supplies negative observations. The full computed decision is `adopt_workers=null`, retain sequential1. These three shared-host samples are descriptive, not a statistical speed guarantee. The harness changes no production default; no new kernel, codec shortcut or accelerator package is justified by this result.

## Spill-policy observations

Every successful sort verifies the complete unique ID population, exact independent Python-MD5 payloads and global(payload,ID) order. No OOM was required or observed in this fixed six-case experiment. Elapsed here is instrumented sort diagnostic time, not pipeline timing.

| IDs | Policy / configured memory | Result | Seconds | Native peak temp bytes |
| --- | --- | --- | --- | --- |
| 500000 | sink-zero-spill / 128 MiB | completed | 2.367 | unsupported |
| 500000 | source-spill-control / 32 MB | completed | 2.460 | 43843584 |
| 500000 | source-spill-control / 256 MB | completed | 2.190 | 0 |
| 2000000 | sink-zero-spill / 128 MiB | completed | 11.913 | unsupported |
| 2000000 | source-spill-control / 32 MB | completed | 10.390 | 196837376 |
| 2000000 | source-spill-control / 256 MB | completed | 9.989 | 148406272 |

The500,000-ID source pair supplies the required actual positive-spill observation at32 MB (43843584 native peak temp bytes) and matching completed 256 MB control with zero reported peak temp, both with full correctness. At 2,000,000 IDs, both32 MB and256 MB spill (196837376 and148406272bytes). Therefore 256 MB is not generally a nonspill setting and no contrary interpretation is made. All remaining temp files had disappeared after close; absence alone would not prove nonspill. Native configured limits/profile peaks are not a proof of all-allocation or process-RSS enforcement.

The accepted sink remains 128 MiB, threads 1, temp 0B, external access/extension auto-loading/install disabled. Its two unprofiled sorts completed exact correctness, but native profiling is unsupported under this unchanged policy after the preserved capability controls. No measured zero-temp counter or hard enforcement claim is invented for that sink. Separate source-style diagnostics establish positive spill/control; they do not relax the sink policy or alter production settings.

## Output-layout and query observations

All three new diagnostic files preserve every field/type/metadata and all 65,536 logical cells under the actual 22-field accepted projection schema. A is interleaved/no statistics; B is instrument/result-ordinal sorted/no statistics; C uses the same sorted rows with statistics. NONE compression, no dictionary, row groups 4096, write batches 1024, page size 65536 and store_schema=True are fixed. A/B each 9678313 bytes; C 9694569 bytes. These are synthetic scratch projections, not modified authoritative receipts.

Full queries independently return(65536,16777216); selective B0017 queries return(1024,262144). Eighteen queries use three rotating repetitions of each layout/query pair on source-style threads 1/memory 128 MB/temp 512 MiB. Time is instrumented query milliseconds, and bytes are engine profile counters.

| Layout | Query | Median ms [min, max] | Native cumulative rows scanned | Native total bytes read |
| --- | --- | --- | --- | --- |
| A | full | 8.0427 [7.8345, 10.8211] | 65536 | 29317 |
| A | B0017 selective | 11.0273 [10.8726, 11.5304] | 65536 | 33413 |
| B | full | 8.3651 [8.3618, 8.6487] | 65536 | 29317 |
| B | B0017 selective | 10.6505 [10.2546, 10.6607] | 65536 | 29573 |
| C | full | 8.3270 [8.2604, 8.3363] | 65536 | 37445 |
| C | B0017 selective | 7.8084 [7.6341, 8.2901] | 65536 | 33861 |

Only C has row-group instrument min/max statistics: 15 of 16 ranges exclude B0017, leaving one candidate group. That is metadata inference. The actual cumulative rows-scanned counter stays 65,536 for all queries; native byte counters do not directly establish physical disk reads. The lower observed selective C median alone does not qualify a production layout/receipt/validator change. Retain the current no-statistics writer and exact receipt validation.

## Preserved failures and delivery limits

The first full attempt failed after 54 samples/six references when the caller's default 64-task recorder could not retain the four 64-task phases. Corrected qualification-only 256-task/12800-span reporting admits 3801600 reserved bytes within the same 4 MiB; production defaults stay unchanged. The second full attempt failed after 54 samples/seven references at the DuckDB capacity 180-second deadline. Its original independent cleanup outcome remains unestablished; it is not retroactively marked verified.

A separately instrumented stack diagnostic exited natively 0xC0000005 with a truncated stack and no established cause. A selected-line tracing diagnostic timed out at 180 seconds after reaching generation entry, but its overhead prevents original-phase or baseline timing inference. Original durable generation/catalog files show reached write points, not completed verification/close. All raw failure identities, review findings/corrections, separate two-sink preflights and new-admission justification remain in the execution ledger. The completed full03 report is the sole full timing cohort.

Both OS current worker archive/small-smoke qualification and independent source/artifact review are recorded separately. Documentation-only final heads must preserve the 158 frozen executable inputs, renew relevant current-head checks/artifact review and verify actual main before release. Source/CI artifacts are the declared experimental channel; no stable registry, private/provider dataset, R7 replay, wider default or unsupported physical-resource guarantee is supplied by this benchmark.
