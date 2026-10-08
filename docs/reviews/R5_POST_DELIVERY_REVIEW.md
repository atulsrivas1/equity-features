# R5 post-delivery review — October 8, 2026

Owner-requested review after [R5 aggregate acceptance](https://github.com/atulsrivas1/equity-features/issues/64#issuecomment-6055034939). Reviewed worker `0f41db20730bafa27d79d116f6432ff168959d08`, canonical `93545515f08a196b8701f9b40a21537a87c63b16`, I/O `4603c6e50331a5e8a82b13b62a0cdd5ffaa0e4bf`; workers0.1.0a11. This is separate local automated review, not human or hosted review. It preserves original acceptance and adds newly discovered postrelease evidence.

## Finding: P2 default supervisor consumes unrelated publisher completions

[BUG006 #337](https://github.com/atulsrivas1/equity-features/issues/337), affected [supervisor.py lines579–581](https://github.com/atulsrivas1/equity-feature-workers/blob/0f41db20730bafa27d79d116f6432ff168959d08/packages/workers/src/equity_feature_workers/supervisor.py#L579).

With no progress reporter, a foreign producer submits task B to the shared SerialPublisher during task A's successful calculation. Initial queue admission is valid. The supervisor submits A and performs an unscoped drain, then indexes B's returned identity in its own executions map. KeyError is caught as CALCULATION_FAILED. Both returned completion records have been consumed; A has no verified output and B is absent from pending/subsequent explicit drain although the sink committed it. Stored data is not deleted or corrupted; computation/publication accounting and diagnosis are wrong.

Separate `/root/r5_reliability_review` and root independently reproduced this with real Parquet and DuckDB; root additionally installed all nine actual released Windows wheels into an isolated target and reproduced both sinks there. Source and released supervisor SHA256 agree: `11978c62d3456c4532ecfb75e418185990597c89adf7d2b0b90e3e20f971a1ed`. The reporter-enabled path scopes draining and its existing regression passes. Optional observability must not change publication ownership correctness.

```json
{"producer_errors":[],"supervisor_reason":"CALCULATION_FAILED","supervisor_output":false,"pending":[],"foreign_storage_state":"COMMITTED","explicit_drain_count":0}
```

The [synthetic reproducer](r5_shared_publisher_repro.py) accepts `--worker-tests` pointing at the matching public worker test directory and `--sink parquet` or `--sink duckdb`. It ran on both real sinks and uses temporary synthetic outputs only.

Repair should drain only the supervisor's admitted identities and preserve other producers' work for their owner. Filtering after an unscoped drain cannot recover consumed completion records. BUG006 remains unimplemented/Backlog; corrective release assignment and implementation ownership are pending. It links accepted EQ062/EQ065/E08 without reopening or rewriting their original receipts. No repair or R6 implementation is performed by this review.

## Nonblocking contract clarification

[MANIFESTS.md line9](https://github.com/atulsrivas1/equity-feature-workers/blob/0f41db20730bafa27d79d116f6432ff168959d08/docs/MANIFESTS.md#L9) says history tasks require ordered_history=True. The generic TaskManifest validator admits a produced daily_baseline task changed to False with empty warm-up/no initialization digest; its codec round-trips. Built-in commands enforce True and canonical history mathematics still validate supplied facts, so no numerical/publication harm was demonstrated. Clarify generic versus built-in admission or explicitly enforce the intended contract in a separately selected change. This is not a second demonstrated runtime defect.

## Code and story coverage

| Story | Inspected behavior | Independent evidence |
| --- | --- | --- |
| EQ057 | Closed manifests, identity, input/result binding, codec/history declarations | 11 retained manifest methods; independent ordering declaration probe |
| EQ058 | Session bars/trades/quotes commands and physical sink admission/readback | 14 methods; empty prefix plus three trade chunks and exact literals |
| EQ059 | History/baseline/reference/relative dispatch, initialization and prior-only admission | 16 methods; independent raw history chunk baseline300/2=150 |
| EQ060 | Dependency/assembly/universe barriers and retained proof consumption | 20 methods; false global complete certificate rejected |
| EQ061 | Serialized publication, immutable generation and original full-result verification | 20 methods; publication/generation source inspected |
| EQ062 | Partition/reuse/budget/spill/default supervisor and producing-thread interaction | 35 methods; BUG006 independently uncovered beyond existing suite |
| EQ063 | Stable task claims, attempt/cancellation/receipt-first recovery | 24 methods; additional unknown-to-commit and postcommit-cancellation probes |
| EQ064 | Accepted-generation selection/history/reader visibility and CAS | 21 methods; both-sink old-snapshot original results with zero new begin |
| EQ065 | Redacted diagnostics, timing/resource observations, reentry/backpressure/fault ownership | 38 methods independently passed; owner-boundary source reviewed |
| EQ066 | Configured physical source-to-catalog pipeline, report/readiness and performance protocol | 8 pilot methods; two extra large/skew physical samples; independent raw measurement audit |

Root reran the full 208-method worker suite from nine installed source distributions: PASS in 339.367 seconds. Strict mypy passed 13 source files; pip check passed. These existing tests do not cover the confirmed default foreign-producer failure. Independently executed reference probes, focused tests and artifact-wheel reproductions are recorded separately in [review evidence](R5_POST_DELIVERY_EVIDENCE.json). Source/installed tests ran on Windows CPython3.12.10 with DuckDB1.5.6, PyArrow20.0.0 and NumPy2.2.6. No Linux runtime rerun is claimed.

## Release and artifact audit

All ten EQ057–066 issues are Closed/Project Done with acceptance checklists complete; E08 is Closed/Done and milestone6 closed with11 closed/zero open (ten stories plus BUG005). Final worker37742837400, canonical37742341444 and docs37742341425 runs all succeeded at the actual accepted heads. Whole published Git trees equal final separately reviewed worker415ddfe/canonicala33dc52 trees. Canonical packages tree equals the accepted core20c08c tree, so no core implementation change is inferred from R5 delivery.

Root downloaded the exact final native server ZIPs, verified both server digests, all20 archive hashes and each final manifest's own artifact/dependency mappings, both56-source maps, four recorded installed forms and finite retention:

- Windows artifact11534832234, server SHA256006d3c5fcfb31cf4992c19063603fd1cf0e8913d2597e52abeae6d92e9f7a6a0; expires2026-11-07T07:32:51Z.
- Linux artifact11534781250, server SHA2568ceb0c807bcef4998300575f2ceabc2380472610efc59db97858c909cf2d352e; expires2026-11-07T07:24:54Z.

Final evidence manifests identify the final commit/runtime and legitimately differ from original-runtime receipt manifests. Package archive parity and scoped source parity are exact; manifest equality across different run identities is not asserted. An initial audit-helper assertion incorrectly included original manifest parity, was corrected, and is not a release defect. Canonical Windows working Markdown/JSON can have CRLF: exact public receipt comparisons used committed LF bytes, not checkout bytes. Core/source receipts remain historical immutable evidence.

## Performance and production boundary

Separate `/root/r5_pilot_review` independently recomputed all162 measurements/54 groups and published rows, six excluded references, min/median/p95/throughput/ratios, recorded sequence, reporter reservations and sampled memory sums. Frozen56 source hashes, result/input identities and committed cross-repository receipts agree. All24 process medians exceed the corresponding sequential1 medians; each fixed thread count loses in at least one workload/sink pair. The bounded sequential1/backendthread1 starting recommendation is supported for these fixtures.

Two new installed synthetic samples passed independent trade goldens/full sink readback/input parity/generation/catalog: large4096-row Parquet/process4 and skew2528-row DuckDB/thread2. They corroborate those paths; they are not a replacement performance campaign or new comparative claim. Sampled RSS, overlapping stage timings, logical wire reservations and file-byte estimates retain documented limits. The original162-sample campaign was audited, not rerun.

Private pilot, corrected month and annual generation remain NOT_ADMITTED. Rights/privacy/source/PIT/known-at/adjustment/calendar/warm-up/math and worst-case capacity/correction/cancellation/restart gates were not qualified here. No private work, provider/service/scheduler/registry/stable tag or R6 work was started.

## Continuity and priorities

Preserve accepted R5 as its exact historical engineering receipt and link the newer BUG006 evidence. First select/qualify a bounded BUG006 repair before relying on shared-publisher default supervision; its tests must compare progress-enabled/disabled behavior and both real sinks. Next clarify the generic history declaration wording without inventing a numerical defect. Keep production gates and the stop-before-R6 instruction explicit; this review starts neither private generation nor a new release.

Earlier pending-publication paragraphs in reviewed audit/handoff documents are preclosure captures explicitly superseded by the final E08 acceptance, not missing current release gates. This new postrelease finding is different: successful prior review/CI/artifacts did not test the unobserved foreign-producer case. All review preparation import failures and helper-assumption errors were excluded from validation; no fabricated success or failed production gate is inferred.
