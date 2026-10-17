# EQ117 controlled evidence evaluation — diagnostic results

**Workflow FAILED; diagnostic evidence only. This run is not admissible as a fully qualified study.** Both jobs reached all160 rows and returned0 from all33 recorded subprocess commands, including the driver and installed-map comparison. The final harness audit then attempted to read generated `__pycache__` as a file (Linux IsADirectoryError; Windows PermissionError). Final Git/IO closure was not reached. Original raw artifacts, failure log and the positive collector refusal are preserved. No replacement study was run.

Owner product decision: **DEFER**, explicitly accepted October17,2026. [Decision and scope](EQ117_PRODUCT_DECISION.json) select completion of EQ117/EQ120 with the negative findings and supported local-pilot documentation; unselected EQ118/EQ119 remain unimplemented future Backlog. No witness, future release, party or operations are selected. Automated observations do not establish human usefulness, demand or an independent trust need.

One fixed study: [39054264038](https://github.com/atulsrivas1/equity-features/actions/runs/39054264038), `eq117-fixed-v1-b1e9a11bdcf2`, source `b1e9a11bdcf2cb3196197a45d4d9aeaaca3cb45f`. The owner accepted proposal SHA256 `7405067b0360126a462bb7a66b5a89416cf93399843b0933b358760804e45073` before measurement. No replacement study was run.

| Observation | Actual |
| --- | --- |
| Planned | 320 |
| Attempted | 320 |
| Structurally valid | 320 |
| Failed | 0 |
| Not run | 0 |
| Exact full diagnoses | 320 |
| Eligible replay matches (required 240) | 240 |
| Missing/corrupt zero-call observations (required 80) | 80 |
| Clean false positives | 0 |
| Captured trial calculator entries | 240 |
| Unavailable calculator coverage observations | 0 |

| Accepted technical criterion | Actual outcome |
| --- | --- |
| Exact diagnoses, replay and refusal | MET IN DIAGNOSTIC DATA |
| Each stage median ≤2× baseline +5 ms | NOT MET IN DIAGNOSTIC DATA |
| Every pair’s closed-file bytes ≤2× baseline +32 KiB | MET IN DIAGNOSTIC DATA |
| Optional ≥20% fewer selected operations in ≥6/8 cases per OS/state | NOT MET IN DIAGNOSTIC DATA |

| OS | Process state | Optional improved cases /8 | Passing stage medians /24 | Passing storage pairs /40 |
| --- | --- | --- | --- | --- |
| Windows | PROCESS_COLD | 0/8 | 16/24 | 40/40 |
| Windows | PROCESS_WARM | 0/8 | 16/24 | 40/40 |
| Linux | PROCESS_COLD | 0/8 | 16/24 | 40/40 |
| Linux | PROCESS_WARM | 0/8 | 16/24 | 40/40 |

## Timing criteria not met in retained diagnostic data

| OS | State | Case | Stage | Baseline median ms | Evidence median ms | Accepted maximum ms |
| --- | --- | --- | --- | --- | --- | --- |
| Windows | PROCESS_COLD | P01 | export | 1.130 | 369.543 | 7.259 |
| Windows | PROCESS_COLD | P02 | export | 1.116 | 367.305 | 7.232 |
| Windows | PROCESS_COLD | P03 | export | 1.126 | 374.434 | 7.253 |
| Windows | PROCESS_COLD | P04 | export | 1.115 | 372.869 | 7.230 |
| Windows | PROCESS_COLD | P05 | export | 1.120 | 365.025 | 7.241 |
| Windows | PROCESS_COLD | P06 | export | 1.129 | 340.404 | 7.258 |
| Windows | PROCESS_COLD | P07 | export | 1.126 | 366.448 | 7.251 |
| Windows | PROCESS_COLD | P08 | export | 1.089 | 383.088 | 7.179 |
| Windows | PROCESS_WARM | P01 | export | 1.171 | 367.307 | 7.341 |
| Windows | PROCESS_WARM | P02 | export | 1.082 | 363.245 | 7.164 |
| Windows | PROCESS_WARM | P03 | export | 1.109 | 360.596 | 7.218 |
| Windows | PROCESS_WARM | P04 | export | 1.097 | 364.695 | 7.193 |
| Windows | PROCESS_WARM | P05 | export | 1.139 | 368.179 | 7.279 |
| Windows | PROCESS_WARM | P06 | export | 1.103 | 335.466 | 7.206 |
| Windows | PROCESS_WARM | P07 | export | 1.102 | 378.165 | 7.204 |
| Windows | PROCESS_WARM | P08 | export | 1.117 | 365.582 | 7.234 |
| Linux | PROCESS_COLD | P01 | export | 0.862 | 373.537 | 6.724 |
| Linux | PROCESS_COLD | P02 | export | 0.862 | 372.021 | 6.723 |
| Linux | PROCESS_COLD | P03 | export | 0.860 | 370.029 | 6.720 |
| Linux | PROCESS_COLD | P04 | export | 0.857 | 371.891 | 6.714 |
| Linux | PROCESS_COLD | P05 | export | 0.849 | 372.125 | 6.698 |
| Linux | PROCESS_COLD | P06 | export | 0.835 | 344.289 | 6.670 |
| Linux | PROCESS_COLD | P07 | export | 0.851 | 372.434 | 6.701 |
| Linux | PROCESS_COLD | P08 | export | 0.863 | 369.242 | 6.725 |
| Linux | PROCESS_WARM | P01 | export | 0.823 | 375.930 | 6.646 |
| Linux | PROCESS_WARM | P02 | export | 0.823 | 376.145 | 6.645 |
| Linux | PROCESS_WARM | P03 | export | 0.825 | 374.358 | 6.649 |
| Linux | PROCESS_WARM | P04 | export | 0.822 | 377.177 | 6.645 |
| Linux | PROCESS_WARM | P05 | export | 0.827 | 376.985 | 6.653 |
| Linux | PROCESS_WARM | P06 | export | 0.819 | 346.527 | 6.638 |
| Linux | PROCESS_WARM | P07 | export | 0.829 | 376.782 | 6.657 |
| Linux | PROCESS_WARM | P08 | export | 0.829 | 373.934 | 6.659 |

## Method and scope

Eight deliberately constructed synthetic cases; two arms; ten paired repetitions per case on each OS. Five repetitions use a new process per arm and five use one retained process per arm. These are 320 automated observations of eight cases, with zero human participants. They are not 320 independent users or randomly sampled real incidents. Each case/arm/OS/state has five observations. The fixed order and all planned slots are retained. No OS pooling, outlier removal or adaptive repeats were used.

Both arms received equal input facts, configuration, results, retained artifacts and terminal information. Generic observers derived findings from retained evidence; only the controlled producer and post-trial scorer used fixture expectations. Selected nested API/semantic operations and instrumented elapsed stage times are automated proxies, not human debugging steps or time. Instrumentation overhead is included. A new process does not imply cold OS caches; provider host co-load was uncontrolled.

Common fixture computation ran once per pair outside both arm timers and is reported separately, including combined stage-plus-common cost. Launch/import is separate. Warm rows reference one actual launch rather than counting another launch per request. Per-OS raw worker records and actual exits substantiate 82 study actors each. Qualification executions are disclosed separately and are not scheduled study observations. Closed-file bytes describe logical file lengths, not physical disk allocation.

Full typed native content, strict diagnostics, declarations versus recomputation, missing/corrupt evidence and replay counts remain in the raw records. Same-owner terminals and a matching replay do not establish independent trust, source authenticity, execution verification or truth of unsupported prose. Human usefulness, commercial demand and independent trust need remain UNKNOWN.

The diagnostic machine summary retains all 32 OS/state/case comparisons, five paired differences per comparison, per-stage distributions, separate launch/common costs, exact storage comparisons and optional ratio-of-medians gates. Zero denominators remain undefined. Source/qualification failures before this fixed study are separate history; none are relabeled as study successes.

## Retained execution evidence

Analysis DATA SHA256 `9e8486c62352b63cdfd4a0a240951f3c9e743e4107d2e13f7c73c9cdc2e2dc1f`. Independent diagnostic DATA reviews are recorded in [the machine-readable report](EQ117_DIAGNOSTIC_RESULTS.json); final source correction, qualification, public delivery remain pending.

- Windows, Python 3.12.10: artifact `12109272935`, SHA256 `2f410236ecd08cb4a218417f53ef3ffdd2e73c170b01ff6cae01efcfa1c25fec`, expires `2026-11-16T17:48:16Z`. Raw context, all rows, worker logs, operation sequences, closed-file/seed maps and qualification records are retained in the GitHub artifact.
- Linux, Python 3.12.15: artifact `12108957183`, SHA256 `fa82f2a9eee510c196e8da1423273d973995d8b4059a7955a8759f283341b578`, expires `2026-11-16T17:47:02Z`. Raw context, all rows, worker logs, operation sequences, closed-file/seed maps and qualification records are retained in the GitHub artifact.

The owner accepted DEFER and explicitly revised R13 to EQ116/EQ117/EQ120. EQ118/EQ119 remain open and unimplemented in future Backlog; their milestone/dependency records must reflect that decision. Delivery gates still apply before selected stories and R13 can be declared complete.

## Reproduce the diagnostic score

[All320 original diagnostic rows](EQ117_DIAGNOSTIC_ROWS.jsonl.gz) are retained as static gzip-compressed JSONL, with original row bytes and both raw/compressed hashes in the machine report. Read with the standard-library `gzip`/`json` modules and score using `examples/evidence_evaluation_scoring.py` and `docs/stories/EQ116_ORACLES.json` from the original study source commit above. Invoke `score(rows, load_oracle(oracle_bytes), ('Windows', 'Linux'))`; this is DATA-only rescoring and launches no calculator or study. Keep the separate failed-workflow/nonadoptable classification: metric predicates cannot establish missing final execution closure. Full worker traces/packets/source/archive and exit evidence remain in the original artifacts with their disclosed expiry.
