> Historical record of the original run (commit 9d51cbd, original machine). Adoption in this table is measured on that machine and is not contractual; parity is the contract. A later run (docs/stories/EQ-139_BAND_BENCHMARK_20261029.json, provenance in the .PROVENANCE.json beside it) adopts a different set. No release claim cites band adoption or speedup numbers before the controlled-machine Linux rerun (open owner/Linux item).

# EQ139 measured band comparison and frozen protocol

Compare six fixed synthetic workloads with six output selections (each of five bands and all five), for 36 profiles. A uses ordinary selected calls plus a real full-result join and one globally sorted evidence cap. B uses explicit supplied price-moment preparation followed by the public compute API, including reuse validation. Neither path fetches or publishes data. All construction, admission, preparation, moments/radius evaluation, identity and full result serialization costs stay inside each measured sample.

Freeze all 36 A baselines and their margins in an exclusive sidecar before any B sample. Each mode has two warmups and seven retained repetitions: 504 retained samples across 72 mode/profile measurements. Preserve failures, partial repetitions, unchanged original sidecar bytes, full source/import identities and nonwinning cases. A fresh source freeze is required before the actual run; these protocol guards are synthetic tests, not performance measurements.

Adoption for a profile requires complete projection parity, median improvement at least max(5%, three A IQR divided by A median), aggregate parent-plus-child peak bound within both 1 GiB/25% initially free memory and 1.25 A, median core seconds at most 1.25 A, and small-profile p95 at most 1.10 A. Keep direct calls supported regardless of the outcome. No tuning or dropping profiles after observing B.

The harness checks 72 complete-result projections across twelve independent readiness/input profiles and six selections, including missing, empty, gap, known-at, correction, warmup and zero-variance cases. Numerical correctness is qualified separately by original exact/independent decimal fixtures. Seven protocol guard methods verify evidence retention, source closure, baseline ordering and real join metadata/evidence behavior. An eighth guard now preserves actual raw proof/sidecar bytes, all36 profiles/504 samples and exact38-entry source applicability.

Actual a3 measurements below are bound to9d51cbd26ba0de390fedccdf870f2c157ad6f054. Historical a1/a2 results retain their original identities and are not relabeled a3 measurements. This direct synchronous synthetic comparison establishes no worker parallelism, live latency, physical containment, production SLA or fastest-library claim. EQ140 owns supplied worker integration and later releases own additional execution improvements.

## Actual observed results

Separate local automated reviewer `/root/r17_review` independently recomputed781 evidence assertions across all504 retained samples,72 mode/profile summaries and36 thresholds/decisions. Measurement receipt SHA256 `b8bbd6dae2dc4aeb5338b78eb9e70bf2aba5ae9004f751ec3ffbd7a58a9ad3f7` qualifies this exact measured component; eventual final-head review/installed artifacts/CI/main delivery remain separate.

| Profile | Separate A seconds | Shared B seconds | Median reduction | Frozen margin | B aggregate peak MiB | Adopt |
| --- | ---: | ---: | ---: | ---: | ---: | --- |
| large/all | 34.293208300 | 9.555170100 | 72.14% | 5.00% | 221.55 | yes |
| large/lower | 10.304999700 | 9.620539300 | 6.64% | 5.82% | 222.27 | yes |
| large/middle | 10.235410400 | 9.689706000 | 5.33% | 5.00% | 222.54 | yes |
| large/position | 10.037771400 | 10.145952600 | -1.08% | 5.45% | 221.06 | direct fallback |
| large/upper | 10.806383600 | 10.157836700 | 6.00% | 6.05% | 221.02 | direct fallback |
| large/width_ratio | 10.474434000 | 10.331721100 | 1.36% | 5.00% | 221.60 | direct fallback |
| long14/all | 0.459395600 | 0.138626500 | 69.82% | 8.65% | 76.41 | yes |
| long14/lower | 0.143008800 | 0.136239200 | 4.73% | 24.68% | 75.82 | direct fallback |
| long14/middle | 0.143101300 | 0.151508600 | -5.88% | 5.00% | 75.87 | direct fallback |
| long14/position | 0.147908000 | 0.135369900 | 8.48% | 13.98% | 75.88 | direct fallback |
| long14/upper | 0.142112400 | 0.139878500 | 1.57% | 19.93% | 75.91 | direct fallback |
| long14/width_ratio | 0.143501400 | 0.127752500 | 10.97% | 11.15% | 75.65 | direct fallback |
| long20/all | 0.475737500 | 0.139546400 | 70.67% | 20.92% | 77.68 | yes |
| long20/lower | 0.137698000 | 0.140545800 | -2.07% | 5.92% | 77.68 | direct fallback |
| long20/middle | 0.135620200 | 0.138327000 | -2.00% | 10.69% | 76.19 | direct fallback |
| long20/position | 0.139572100 | 0.150949400 | -8.15% | 21.20% | 77.68 | direct fallback |
| long20/upper | 0.152752900 | 0.132288600 | 13.40% | 31.13% | 76.14 | direct fallback |
| long20/width_ratio | 0.135463100 | 0.143013800 | -5.57% | 9.54% | 77.57 | direct fallback |
| long60/all | 0.441769700 | 0.145796300 | 67.00% | 12.33% | 78.34 | yes |
| long60/lower | 0.135626900 | 0.139588800 | -2.92% | 15.92% | 77.64 | direct fallback |
| long60/middle | 0.143388600 | 0.139786400 | 2.51% | 9.66% | 77.29 | direct fallback |
| long60/position | 0.138995700 | 0.133202800 | 4.17% | 14.32% | 78.02 | direct fallback |
| long60/upper | 0.137755300 | 0.139720900 | -1.43% | 8.35% | 77.89 | direct fallback |
| long60/width_ratio | 0.131008000 | 0.138696600 | -5.87% | 25.87% | 77.91 | direct fallback |
| skewed/all | 2.424298200 | 0.756231600 | 68.81% | 5.00% | 86.04 | yes |
| skewed/lower | 0.765561900 | 0.796895200 | -4.09% | 11.22% | 85.84 | direct fallback |
| skewed/middle | 0.751207700 | 0.755005800 | -0.51% | 12.48% | 85.68 | direct fallback |
| skewed/position | 0.777311600 | 0.772425100 | 0.63% | 14.19% | 85.47 | direct fallback |
| skewed/upper | 0.796308700 | 0.752433400 | 5.51% | 10.50% | 85.61 | direct fallback |
| skewed/width_ratio | 0.741061500 | 0.757427900 | -2.21% | 12.33% | 85.69 | direct fallback |
| small/all | 0.034321000 | 0.009617000 | 71.98% | 23.49% | 69.48 | yes |
| small/lower | 0.009593300 | 0.009840200 | -2.57% | 12.59% | 69.04 | direct fallback |
| small/middle | 0.010431500 | 0.009503500 | 8.90% | 35.53% | 68.40 | direct fallback |
| small/position | 0.010848000 | 0.009480600 | 12.61% | 16.65% | 69.27 | direct fallback |
| small/upper | 0.009360600 | 0.010152100 | -8.46% | 16.35% | 68.54 | direct fallback |
| small/width_ratio | 0.010044200 | 0.010325100 | -2.80% | 24.99% | 69.13 | direct fallback |

All six combined-band profiles meet every frozen parity/wall/memory/core/small-latency gate, with66.997–72.137% lower medians. The large64-symbol ×4096-slot,N20 combined profile measured34.293208300s A versus9.555170100s B, with conservative B aggregate peak232316928bytes. The two observed single-band passes are narrower: large/middle5.33% against5.00% margin and large/lower6.64% against5.82% margin. Retain both observations without generalizing them into single-output defaults; the other28 profiles retain direct fallback. No automatic profile heuristic or worker executor was introduced.

Original raw SHA256 `7faea4e4a1178c4989c59b2fca92d333ada98b1efe6253c589cf5224efb128c8`; original frozen baseline SHA256 `50f84119b0a17980ac11d3737b8f2b3920c522db28c36aadac702236cc23fdab`. See [unaltered measurement](EQ-139_BAND_BENCHMARK.json), [unaltered A sidecar](EQ-139_BAND_BASELINE.json) and [38-entry applicability map](EQ-139_MEASUREMENT_APPLICABILITY.json). Both raw files preserve their original bytes through explicit Git attributes. The [public checkpoint](https://github.com/atulsrivas1/equity-features/issues/473#issuecomment-6268234811) records the frozen-sidecar hash during B, not a fabricated pre-B public timestamp.

Actual environment: Windows11/CPython3.12.10, two Xeon Platinum8160 CPUs,48 physical/96 nominal logical CPUs, current-group affinity48, one measurement worker/native thread. Initial available memory224046624768bytes is an observation, not a reservation; the frozen effective memory budget is1GiB. Parent+child peak sums are conservative separate observed maxima, not simultaneous or physically enforced memory. Actual capacity values are retained in raw evidence.

Retained records include every measured wall/core/memory sample and complete deterministic result projection digest. Warmup timing samples, an independent external chronological trace and per-sample serialized result bodies were not retained. Source/child/parent closure, sidecar, full-result digest joins and independent numerical fixtures provide their stated evidence; do not claim the missing trace/bodies exist. In-process input generation and full result serialization are measured; actual provider/source acquisition, worker transport/queue, sink/readback and persistent live operation are not this experiment. Final all-eight/worker qualification remains EQ140/EQ141.
