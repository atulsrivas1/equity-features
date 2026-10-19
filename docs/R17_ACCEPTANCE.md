# R17 intraday foundation qualification

[EQ141](https://github.com/atulsrivas1/equity-features/issues/475) audits the five accepted predecessors and prepares final R17 delivery. This source is the reviewed-audit candidate; actual EQ141 final review/current CI/publication/main/channel/acceptance/Released/Done and E25/milestone closure remain mandatory. [Live Project](https://github.com/users/atulsrivas1/projects/2) owns execution status. [Machine-readable inputs](R17_ACCEPTANCE_INPUTS.json) records exact sources, package/archive hashes, installed method/skip ledgers and review identities.

## Accepted predecessor evidence

| Story | Actual accepted canonical main | Exact final acceptance receipt SHA256 |
| --- | --- | --- |
| [EQ-136](https://github.com/atulsrivas1/equity-features/issues/470) | `8044f2a0f59d29b85981aaa446777ac2f92fc29b` | `b9b0982552750b8c7430bc898a6ab0e7bc6b2e6106646db741d58fbb2a81a201` |
| [EQ-137](https://github.com/atulsrivas1/equity-features/issues/471) | `e790c30241c4420a08adbf2e92403a4cd9a74375` | `83b66b6d4632d3d2c2d4f374284258644f3e6c57cccc5f641f8087c9c4cfccc0` |
| [EQ-138](https://github.com/atulsrivas1/equity-features/issues/472) | `ee516615aec269e75f9f053ef14b39e440cae743` | `992a9bfcd1c6994d1c75812eefef811c3a65cbf16bd44b157c30b413f69e03c9` |
| [EQ-139](https://github.com/atulsrivas1/equity-features/issues/473) | `b1f5445eb9799b73753e413669b94166997fc468` | `7cbf5e65a9d0a14014b0a9607e43d924b3a4e1c573b247be315d35d812fcf62d` |
| [EQ-140](https://github.com/atulsrivas1/equity-features/issues/474) | `c7010a0a7b8ad290d1fe9f10bc1528ea09b3885b` | `bdbf76a1d99cd0f9c461a96d462c0460ef313cb69f72a1261b0367af653634b9` |

All five issues are CLOSED/ProjectDone. EQ136 is original mathematics/API/reference qualification, not a runtime package. EQ137 supplies compatible immutable preparation; EQ138/139 deliver eight own batch outputs; EQ140 delivers explicit supplied-worker bindings and original core dispatcher gaps. Independent source/numerical fixtures and full-result A/B parity remain separate evidence. [Ready-input review](stories/r17-delivery/EQ141_READY_INPUT_PUBLIC_REVIEW.md) verifies original receipts, actual fiveDone and six package versions in both actual main channels. Its source snapshot is not acceptance of this later audit head.

## Selected capability and dependency matrix

| Output | Direct mathematical operands | Ordered dependency | Readiness independence |
| --- | --- | --- | --- |
| intraday.ema | Eligible anchored closes, configured period/seed | Seed then chronological recurrence within the exact context/revision | High/low, ATR, RSI and bands are not prerequisites |
| intraday.rsi | Eligible anchored close changes, configured seed/period | Seed gains/losses then chronological smoothing | High/low and unrelated outputs are not prerequisites |
| intraday.atr | For target>anchor: predecessor closes anchor..target-1 and high/low only at governed successors anchor+1..target, true ranges, seed/period | Seed then chronological true-range smoothing | For target>anchor: anchor high/low and target close are not consumed; missing target close cannot globally block its valid true range. When anchor==target, observe the single anchor close only (expected N+1/observed1 if eligible), no H/L or TR, insufficient_history |
| intraday.band_middle | Last N scheduled epoch/grid slots, each required close eligible; never compact missing/null/gap slots | Rolling price mean | No EMA/RSI/ATR dependency; missing closes outside that window do not block it |
| intraday.band_upper/lower | Same close window, centered price variance and configured rational k | Compatible mean/variance shared once per selected closure | No unrelated feature or return-volatility prerequisite |
| intraday.band_width_ratio | Same scheduled close window/mean/variance/k; unrounded compatible mean/radius witness | Compatible selected preparation; never subtract rounded upper/lower outputs | Zero variance gives available width0 with positive admitted price mean |
| intraday.band_position | Same scheduled close window/target close/mean/variance/k; unrounded centered residual/radius witness | Compatible selected preparation; never divide differences of rounded published bounds | Constant-band undefined position does not invalidate other valid band outputs; unclamped position may lie outside [0,1] |

The precise authority is accepted math/API/configuration and conditional readiness fixtures; this table is explanatory. All eight IDs are experimental batch snapshots/full supplied-history replay, with update/restore/merge unsupported. Immutable preparation reuse requires exact input/context/configuration identity and lifetime. No external data acquisition, scheduling, credentials, publication or persistence occurs in numerical packages.

Workers also explicitly bind accepted core structure, top-K trades, continuous quotes with optional seed, and bars with optional prior close. Optional prior-close/seed dependencies apply to consuming outputs; existing default acquisition/dispatch and service/client/MCP boundaries remain documented separately. Raw absence, observed empty delivery/batch and unavailable feature value retain different meanings.


## Original correctness and timing contracts

[Mathematics](features/INTRADAY_FOUNDATIONS.md), [API/precision/readiness](api/INTRADAY.md), [original math/readiness fixtures](../tests/fixtures/intraday_math/README.md), [original band goldens](../tests/fixtures/intraday_bands/README.md) and [worker binding contract](stories/EQ-140_BINDING_CONTRACT.md) govern the implementation. EMA/RSI/ATR ordered recurrences and seeds, rational/Decimal contexts, population price variance, unrounded radius/centered residuals, int64 ns/scaled prices, causal C/K/E, revision/anchor/reset/carry/coverage and unavailable-quality identity remain unchanged. Missing required grid slots cannot be filled or compacted; unrelated missing inputs cannot create false readiness edges. Public state flags remain batch-only for intraday, with full supplied-history recalculation/replay rather than persistent update/restore/merge. Core39 compatibility is separate and unchanged.

Accepted producer tests use independent rational/Decimal expected mathematics, not the optimized implementation as its only oracle. EQ140 includes independent original scalar/SDK/committed-byte fixtures, all nonempty selected subsets and branch/temporal/unknown/future/revision cases. The final audit reuses those qualified bytes only with explicit source closure; it adds no numerical implementation or new numerical/performance result.

## Actual delivery channel and installed qualification

Worker main231349aaf2bf1b9ec21f45807382ca9c6522520c / [actual PUSH39301445653](https://github.com/atulsrivas1/equity-feature-workers/actions/runs/39301445653) supplies twelve archives per OS for six distributions: contracts/core0.0.4a4, intraday0.1.0a3, I/O contracts/SDK0.1.0a2, workers0.1.0a14. Core build pinb1f5445eb9799b73753e413669b94166997fc468 and I/O18d86761aa3eebb7414e51e8fa2aba089717b5eb are the actual component sources; canonical deliveryc701 changed documents only and its entire package tree equals acceptedb1f. This audit also changes documentation only. A new documentation commit is not a new package build or renamed measurement source.

| Producer / actual artifact | CPython | Expiry UTC | Fresh base wheel/SDist | Fresh combined wheel/SDist |
| --- | --- | --- | --- | --- |
| Linux /12212142183 | 3.12.15 | 2026-11-18 18:20:09 | each58 discovered,16 skipped,42 executed | each58 discovered,4 Windows-native skipped,54 executed |
| Windows /12211898603 | 3.12.10 | 2026-11-18 18:21:33 | each58 discovered,12 optional skipped,46 executed | each58 discovered,0 skipped,58 executed |

All forms report zero failures/errors. Optional absence and positive/negative public typing, core invariance, repeat archives, selected-source SDist rebuilding, closed source/archive/metadata/install namespaces and exact test skip identities are recorded. [Actual main artifact review](stories/r17-delivery/EQ140_MAIN_HOSTED_ARTIFACT_PUBLIC_REVIEW.md) and its JSON bind server ZIP hashes/run/source/access/expiry,24raw archives and1998whole+510selected Git inputs per OS. Installed RECORD/directURL/generated-launcher raw bytes were not retained: the executed source-bound collector and closed receipt joins qualify their origins, not independent redecoding of missing bytes or reconstruction of deleted hosted environments. Four Linux-native skips do not establish Windows Job parity or Linux performance.

[Main source readback](stories/r17-delivery/EQ140_MAIN_SOURCE_PUBLIC_READBACK.md) accepted147assertions, [main final acceptance](stories/r17-delivery/EQ140_MAIN_FINAL_ACCEPTANCE_PUBLIC_REVIEW.md) accepted42 with all35canonical+16worker main jobs SUCCESS, and [postrelease readback](stories/r17-delivery/EQ140_POSTRELEASE_PUBLIC_REVIEW.md) accepted25 before actual EQ140 CLOSED/Done. These are automated local reviews, not human review. Public derivatives reference original exact private receipt hashes and have distinct bytes; JSON hashes in the inventory are exact public derivative identities. Readable Markdown may have repository line-ending normalization.

## Performance results and fallback

[Preparation evidence](stories/EQ-137_BENCHMARK.md), [indicator evidence](stories/EQ-138_BENCHMARK.md) and [band evidence](stories/EQ-139_BENCHMARK.md) retain their separate original sources, workloads, complete winning/nonwinning cases and reviewed applicability. Do not add their percentage improvements or apply old whole-source timings to the final worker. Shared direct preparation improved qualified selected workloads; this is distinct from current whole-worker behavior.

[Full EQ140 table, raw archive and reviews](https://github.com/atulsrivas1/equity-feature-workers/blob/231349aaf2bf1b9ec21f45807382ca9c6522520c/docs/benchmarks/eq140/EQ140_RESULTS.md) preserve frozenbe4:6A+48B cohorts/486ownedJobs/108warmups/378retained. All48 alternatives fail frozen adoption, with sequential default/fallback unchanged. Balanced16x1024/all-eight medians12.292977s admitted compute and44.815368s cold E2E are synthetic observations, not a speed improvement. Worker workload sizes obey actual wire/resource bounds; original direct64x4096 preparation cases are not silently claimed as admitted worker cases. The original1536/2048/4096 committed-byte admission rejections remain evidence, not failed calculations or a universal bar limit.

Direct EQ138/139 harnesses use2warmups+7retained calls within each fresh child, with input reconstruction; they qualify warmed direct code/import paths, not persistent warm-worker pools. Older raw warmups/timestamps/full SDK bodies were not retained. EQ140 retains108actual warmup Jobs, admitted-compute and cold fresh-process/pool E2E classes. Compute after imports is not a persistent warm pool. No public update/restore/merge or unsupported warm-state class is invented.

Whole owned-Job CPU includes terminated descendants. Concurrent RSS probes are sampled, may miss transient peaks and are not physical memory enforcement. Queue/calculation/serialization/publication probes overlap or include nested admission, so their sums cannot be subtracted from wall time to identify an exclusive bottleneck. Retained SDK/result hashes do not equal absent raw SDK body redecoding. Controlled source/baseline checkpoints support chronology without an independently signed witness. No fastest/live/SLA/Linux-speed/physical-durability claim follows.

## Compatibility, migration and retained failures

Use the [six-package installation guide](INSTALLING.md) and [examples](EXAMPLES.md). Existing daily discovery/configuration/core39 and default worker dispatch remain unchanged; import the optional intraday/supplied-session callbacks explicitly. Receipt-wire admission is additive and does not imply rollback after sink commit or physical durability. Existing service/jobs0.1.0a23/frozen a13 builder remains a separately qualified integration boundary; no service/client/MCP a14 migration is claimed. [Compatibility](COMPATIBILITY.md) records package/state/source boundaries. No package version/schema/algorithm/runtime change is introduced by EQ141.

Preserve the original fixture helper/rounding corrections, first failed package closure, installed metadata-list failure, per-runner source-binding correction, transient canonicalHTTP502 attempt and actual same-source retry, and reviewer tool/regex false-positive corrections. Corrected qualified successors replace failed qualification without relabeling old failures or old green source. Original dirty and frozen137/138/139/be4 checkouts and measured environment remain preserved. The initial EQ141 Ready helper refused a preliminary receipt SHA before any mutation; the authoritative51-assertion public-input-bound receipt was used for actual Ready/start.

## EQ141 author checks of the documentation

The audit's [author validation](stories/EQ-141_AUTHOR_VALIDATION.json) records UTF8/JSON/local-link/privacy/inventory joins and unchanged runtime/source scope, plus39registry IDs/31table formulas,24original mathematical reference methods and pure import isolation. One additional fresh Windows CPython3.12.10 environment with pip25.0.1 installed the actual main Windows six matching wheels offline using the documented combined-extra command. Both unchanged direct/worker examples passed (selected11.0/11.0/0.5 and all-eight EMA14.75); the original seven-profile pure-API/SDK fixture passed83assertions/eightresults. This is author documentation/example verification, not separate review, a new Linux installed run, a replacement for the eight main qualification forms/pip25.1.1 process, or new timing/benchmark evidence.

## Final exit and next release

Require this actual final audit head's separate semantic/evidence/source review, findings disposition and applicable current CI; guarded reviewed-head publication; actual main tree/Atul/GitHub attribution/current checks and declared channel/artifact access/expiry readback; separate final acceptance; actual Released verification and Done. Only then verify all six children Done and complete E25/milestone21. The five predecessor acceptances alone are not R17 acceptance.

After verified R17, prepare existing R18 E26/EQ142–146 handoff: exact output DAG/cost baselines, demonstrated compatible reuse, independent ready branches, bounded resource profiles and measured delivery in dependency order. Existing R17 review grant is not R18 authorization. No new chat/automation, provider/live operating scope or universal concurrency increase is selected here.
