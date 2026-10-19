# EQ138 measured output comparison

Actual source `f1e35e151adb7a28273a7158a7cd7718deca474f`; separate automated local reviewer /root/r17_review accepted523 evidence assertions, receipt SHA256390460bc6cfcb12932c2a26aabce19aaee3d76cd485e5070c49cb982065744e4. This qualifies the exact measured component; final-head/current artifacts and delivery remain on EQ138.

| Case | Separate A s | Shared B s | Median reduction | Frozen margin | B peak MiB | Adopt |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| large/all | 28.714383 | 16.679354 | 41.91% | 10.97% | 219.61 | yes |
| large/atr | 11.943615 | 11.569569 | 3.13% | 5.85% | 219.21 | no: improvement |
| large/ema | 11.408052 | 11.789493 | -3.34% | 13.64% | 220.28 | no: improvement |
| large/rsi | 12.979637 | 13.467983 | -3.76% | 5.00% | 219.66 | no: improvement |
| long14/all | 0.363678 | 0.203469 | 44.05% | 16.64% | 74.34 | yes |
| long14/atr | 0.160751 | 0.156397 | 2.71% | 24.52% | 72.91 | no: improvement |
| long14/ema | 0.172214 | 0.150446 | 12.64% | 13.42% | 73.07 | no: improvement |
| long14/rsi | 0.191972 | 0.176160 | 8.24% | 14.20% | 73.02 | no: improvement |
| long20/all | 0.397369 | 0.206332 | 48.08% | 8.35% | 74.75 | yes |
| long20/atr | 0.162576 | 0.155375 | 4.43% | 20.06% | 74.79 | no: improvement |
| long20/ema | 0.171298 | 0.181888 | -6.18% | 9.74% | 74.25 | no: improvement |
| long20/rsi | 0.184592 | 0.205663 | -11.41% | 5.76% | 74.42 | no: improvement |
| long60/all | 0.357854 | 0.199036 | 44.38% | 12.37% | 75.48 | yes |
| long60/atr | 0.161350 | 0.179942 | -11.52% | 23.13% | 74.41 | no: improvement |
| long60/ema | 0.159692 | 0.152023 | 4.80% | 9.43% | 75.29 | no: improvement |
| long60/rsi | 0.176335 | 0.201832 | -14.46% | 18.41% | 74.63 | no: improvement |
| skewed/all | 2.292025 | 1.240733 | 45.87% | 39.30% | 84.29 | yes |
| skewed/atr | 0.952369 | 0.866512 | 9.02% | 19.23% | 84.36 | no: improvement |
| skewed/ema | 0.895706 | 0.843179 | 5.86% | 12.84% | 84.08 | no: improvement |
| skewed/rsi | 1.022626 | 0.992257 | 2.97% | 12.51% | 83.48 | no: improvement |
| small/all | 0.025665 | 0.013653 | 46.80% | 7.51% | 66.63 | yes |
| small/atr | 0.010861 | 0.011035 | -1.60% | 20.27% | 66.41 | no: improvement |
| small/ema | 0.011956 | 0.011360 | 4.99% | 14.71% | 65.74 | no: improvement |
| small/rsi | 0.012382 | 0.012243 | 1.13% | 12.43% | 66.42 | no: improvement |

All24cases preserve full unchanged FeatureResult projections. Nonwinning cases retain separate-call fallback.

One parent+measurement child, supplied synthetic snapshots. Conservative sum of peak working sets, not simultaneous or enforced. No actual worker/provider/sink latency or library ranking.

Report SHA256 `64ac8acbdaf8bd571a574704998f86303bb27f212071f5cb833436fd6e65e3a4`; frozen baseline `a05cd38c88b5cf389c6cbeada2ab97298ae6c7c563f523ed6fcc670606050c47`.

## Inputs, arithmetic and comparison

The original positive-scaled-integer-quadratic-v1 generator supplies real immutable canonical BAR inputs at scale4. Cases: small1x256,N20; large64x4096,N20; skewed63x256+1x4096,N20; long14/20/60 one4096-slot history. Each runs EMA,RSI,ATR separately and all three. A invokes ordinary selected direct calls and assembles the same complete FeatureResult with independently tested global evidence truncation. B prepares the union once and computes the selected result using actual original-object/context/config reuse checks. Construction, admission/config validation, preparation, ordered recurrences, result construction and complete deterministic dataclass/JSON serialization are inside sample elapsed/core time; construction is separately reported. Other stages are a declared combined calculation/serialization measurement, not an invented per-stage breakdown.

Exact Fraction seeds and explicit local Decimal120 recurrences implement the original mathematics. Independent producer fixtures and reviewer impulse-response/interval-envelope oracles establish arithmetic separately from A/B parity. Complete result digests include unchanged values/nulls/quality/reasons/counts/evidence/availability/input/backend/config bindings; no evidence or identity projection is removed to obtain equality.28 source-bound parity profiles additionally cover complete, absentH/L, gaps, flat, corrected, None and observed-empty input variants.

Two warmups and seven recorded samples per case/mode; all24A samples/summaries and max(5%,3*IQR(A)/median(A)) margins freeze in the exclusive baseline sidecar before anyB. Adopt only when median reduction clears the exact case margin, fullP holds, conservative aggregate peaks fit min(1GiB,25%initialfree) and<=1.25A, child core-seconds<=1.25A, and each small-set p95<=1.10A. Baseline and final raw bytes are preserved exactly; the sidecar intentionally records the completed A phase with running status and empty candidates/decisions. The final report is completed. Table rounding does not change exact decisions.

## Capacity and limits

Actual OS `Windows-11-10.0.26300-SP0`, CPython3.12.10; 48 physical/96 logical CPUs, current Windows process-group affinity48. Initial free memory224525385728bytes, declared budget1073741824bytes. Affinity is permitted capacity, not CPU reservation or evidence of multi-group scaling.


One parent collector plus one measurement child, no concurrent author build/heavy test workload. Core time describes the measured child work; parent collector/startup/source-closure/subprocess elapsed is recorded separately, not advertised as worker latency. Aggregate memory is a conservative sum of parent and child peak working sets, not simultaneous sampling or physical enforcement. Input construction/serialization costs are included; no traced count of every interpreter allocation/copy byte is claimed. No provider, actual worker/IPC/queue/publication sink, persistent live path, production SLA or ranking against other libraries was measured. Actual worker and full release qualification remains EQ140/EQ141; R18 addresses selected-output scheduling/resource optimization after R17 acceptance.

Exactly six all-three profiles meet adoption, with41.91–48.08% lower medians. All18 single-feature profiles fail the frozen improvement margin, including some positive/noisy reductions; ordinary direct calls remain the supported fallback. All24 preserve fullP and the recorded memory/core/small-p95 conditions. Caller grouping is conditional on the measured workload; there is no automatic executor/default budget change.

## Source closure and reproduction

All336 retained samples across48 measurements bind exact imported origins/versions and source before/after children and parent closure. Raw warmup samples/timestamps/full result bodies are not retained; two warmups, A-before-B order and full serialization are qualified by exact bound code, exclusive sidecar and complete result digests, not an external event trace. The independent audit recalculated summaries, margins and every decision. [Measured-execution applicability](EQ-138_MEASUREMENT_APPLICABILITY.json) verifies all37 source entries remain byte-identical in the successor. This is historical exactf1 evidence applied to unchanged execution entries, not whole-head identity or a new-source timing rerun. The legacy preparation harness retention repair changes an excluded tool, while the standalone output producer/harness stays unchanged.

Use a fresh checkout of `f1e35e151adb7a28273a7158a7cd7718deca474f`, CPython3.12 and exact requirements-dev.txt. Install contracts and intraday in that source environment with no-deps/no-build-isolation, verify actual origins, then run `python -I -B tools/benchmark_intraday_indicators.py --output <new-external-path.json>`. Preserve its exclusive sidecar and all failures. Keep source/HEAD frozen and avoid concurrent heavy tests/builds. New measurements retain their actual source/capacity/values; they do not replace these raw bytes. Installed artifacts are separately qualified through tools/build_intraday.py on both supported OS.

[Raw completed report](EQ-138_INDICATOR_BENCHMARK.json), [frozen A sidecar](EQ-138_INDICATOR_BASELINE.json), [pre-code plan](EQ-138_PLAN.md) and [live acceptance](https://github.com/atulsrivas1/equity-features/issues/472).
