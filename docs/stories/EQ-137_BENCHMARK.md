# EQ137 preparation benchmark — measured candidate component

Measured source: `c7a46d6489ad9fde4c0bbfc401e9ccafaa6ad2b3`. This is six-family preparation with actual supplied BAR admission, immutable construction, compatible reuse checks and full projection inspection. It measures one process; output kernels, workers, queues and external source/sink latency remain later stories. No speed ranking against other libraries follows.

| Case | Separate median, s | Shared median, s | Reduction | Aggregate peak bound, MiB | Frozen rule |
| --- | ---: | ---: | ---: | ---: | --- |
| small | 0.037086 | 0.013071 | 64.76% | 63.24 | Pass |
| large | 37.845019 | 13.486320 | 64.36% | 219.18 | Pass |
| skewed | 2.773009 | 1.004948 | 63.76% | 82.49 | Pass |
| long14 | 0.545430 | 0.206271 | 62.18% | 72.45 | Pass |
| long20 | 0.531015 | 0.214813 | 59.55% | 71.52 | Pass |
| long60 | 0.583592 | 0.218369 | 62.58% | 72.16 | Pass |

Two warm-ups and seven retained observations per case/mode. All six A baselines and noise-based thresholds were frozen before any B timing. All full-projection digests match; all measured memory/core-second conditions and the small-case p95 condition pass. The memory budget was1GiB; reported memory is a conservative sum of parent and isolated measurement-child high-water working sets, not measured simultaneous residency or physical enforcement. Child core-seconds and total subprocess time are retained separately. Native compute threads, worker children, queues and IPC bytes are zero here; object construction/ownership/copy and inspection time are included, without claiming a count of every interpreter allocation/copy byte.

Hardware: two Xeon Platinum8160 processors,48physical/96logical CPUs; Windows process-group affinity permits48logical CPUs. CPython3.12.10, contracts0.0.4a4 and intraday0.1.0a1 source imports are explicitly verified. Full source hashes, generator, raw samples, capacity and decisions are in the raw report. Seven samples provide a coarse tail summary, not a statistical SLA.

Independent local automated reviewer `/root/r17_review` recomputed128 evidence assertions and accepted this exact measurement component; receipt SHA256 `94f30e513a0d090b5e59febc47b93fa3d47c83172ccbc562ea8878b08f8741c0`. The original raw report and frozen A sidecar retain exact bytes/hashes. Documentation successors may cite this historical measurement only with reviewed unchanged executed code/config/version/generator/projection/rule identities; they are not fresh measurements.

Current package source has no automatic cross-symbol executor. Shared preparation is explicit and separate calls remain supported. R18 owns wider selected-output scheduling/resource optimization; R17 output/worker baselines remain EQ138–141.

Raw report SHA256: `78f33000ae88ff0ad1612fb86813d2b8081de92567108eaacd6c4c710aa55996`.

Frozen baseline SHA256: `66b76dba6582cedab49c6a37dc9e174085b76e74e90b733cba72a72510be6c38`.

[Raw measurements](EQ-137_PREPARATION_BENCHMARK.json) and [frozen baseline](EQ-137_PREPARATION_BASELINE.json) retain their original source identity and bytes. Run the source-pinned tool with a new output path in an existing directory: `python -I -B tools/benchmark_intraday_preparation.py --output work/intraday-new.json`. Install pinned development requirements and editable contracts/intraday first; actual artifact installs are qualified separately.
