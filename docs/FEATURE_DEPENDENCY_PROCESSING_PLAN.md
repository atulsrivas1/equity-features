# Feature dependencies and measured parallel processing

Owner-requested planning, October 18, 2026. [GOV-030 #462](https://github.com/atulsrivas1/equity-features/issues/462) owns this packet. This is a draft proposal; separate final-head review, applicable CI, default-branch publication and readback remain delivery gates. It selects no runtime release, feature expansion, executor/default change, benchmark outcome or performance SLA.

The goal is the shortest correct processing time within the configured available CPU, memory and I/O budget. Independent work should proceed as soon as its actual inputs are available. A feature's position in a list or family does not create a mathematical prerequisite. Claims of fastest processing require defined workloads, credible comparisons, repeated measurements and full result parity.

## Evidence and source boundaries

The owner requested inspection of a local comparison implementation and the three public repositories. A detailed source-derived field/catalog/dependency crosswalk and a resource/measurement proposal were prepared locally. Source access for inspection does not establish redistribution rights. That inventory, its extraction code, source-specific rules and host inventory are excluded from this public change. No private code, dataset or raw chat is published here. Public guidance below is original planning supported by the public sources listed here.

| Repository | Inspected public baseline |
| --- | --- |
| equity-features | `76f650058cf10825706385272c940a161a8f5c4e` |
| equity-feature-io | `18d86761aa3eebb7414e51e8fa2aba089717b5eb` |
| equity-feature-workers | `a69ae9cfeb62730fc78705b4752b94c6f9438275` |

See the [accepted overall architecture audit](reviews/OVERALL_ARCHITECTURE_REVIEW_2026-10-18.md), [existing parallel execution plan](R5_PARALLEL_EXECUTION_PLAN.md), [feature scope](features/V1_SCOPE.md), [live architecture direction](decisions/LIVE_INTRADAY_ARCHITECTURE_DIRECTION.md) and [deferred live release](FUTURE_LIVE_INTRADAY_RELEASE.md). Static source inspection is not a new numerical/parity/installed/operational acceptance run. Historical measurements remain historical.

## Current feature/input/capability matrix

This matrix groups the 39 built-in IDs by actual public input/API and capability. Parameter variants are not extra IDs. Every calculation also needs compatible identity, units, timing, coverage and configuration admission. Compatible facts can be reused only within those exact identities.

| Family / IDs | Actual prerequisites | Batch / update / restore / merge | Parallel boundary |
| --- | --- | --- | --- |
| Session bar/price: 12 | Supplied completed bars; prior-close reference only for gap/close-close return | yes / yes / yes / qualified | Independent admitted instrument/session instances; legal bar partition merge only |
| Session interval structure: 2 | Completed aligned bars, supplied named intervals; whole session volume for interval share | yes / yes / yes / qualified | Independent instruments; share needs compatible whole-session denominator |
| Trade aggregates: 5 | Supplied eligible ordered trades; actual notional/volume/count sufficient statistics | yes / yes / yes / qualified | Share compatible scan/reducer; independent populations may overlap |
| Trade top-K: 1 | Supplied trades, K, stable size-ranked selection/ties | yes / yes / yes / qualified | Independent populations; no substitution for notional-ranked selection |
| Sampled quote summaries/counts: 2 | Supplied quotes, declared sampling, validity and coverage | yes / yes / yes / qualified | Independent from trade/history math when its own inputs are admitted |
| Continuous quote spread: 1 | Continuous updates, seed/inactive/unknown initialization, expiry and gap policy | yes / yes / yes / no arbitrary merge | Ordered carry chain per identity; unrelated chains proceed |
| History returns/extrema/SMA/EMA/RSI/ATR/volatility: 8 | Supplied daily history, governed grid, target inclusion and action policy; recurrence anchor as required | yes / no / no / no | Independent symbol/cutoff/window calls; recurrence order inside a call |
| Daily/interval baselines and target ratios: 4 | Prior daily/bucket history and explicit grid; ratio consumes compatible target and baseline witness | yes / no / no / no | Baseline and target preparation independent; ratio joins only those facts |
| Market/sector relative return: 2 | Compatible instrument and benchmark return witnesses; sector membership when required | yes / no / no / no | Pairwise join; no whole-universe dependency |
| Breadth direction / above-SMA: 2 | Declared universe and compatible member inputs; exact SMA witnesses for above-SMA | yes / no / no / no | Parallel member preparation; reduce only at declared population/cutoff coverage |

Source: [implementation inventory](https://github.com/atulsrivas1/equity-features/blob/76f650058cf10825706385272c940a161a8f5c4e/packages/contracts/src/equity_feature_contracts/_implemented.py), [literal definitions](https://github.com/atulsrivas1/equity-features/blob/76f650058cf10825706385272c940a161a8f5c4e/packages/contracts/src/equity_feature_contracts/_catalog.py), [required-input commands](https://github.com/atulsrivas1/equity-feature-workers/blob/a69ae9cfeb62730fc78705b4752b94c6f9438275/packages/workers/src/equity_feature_workers/required_inputs.py) and [barriers](https://github.com/atulsrivas1/equity-feature-workers/blob/a69ae9cfeb62730fc78705b4752b94c6f9438275/packages/workers/src/equity_feature_workers/barriers.py).

The optional continuous-market package has six separate batch definitions; it does not expand the 39-ID equity registry or make history incremental. Generic strategy scanning/ranking and future labels are optional consumers. An extension mechanism is not implementation of every externally named feature. Daily APIs do not imply arbitrary intraday-bar support. Exact notional, close-weighted proxies, sampling, window anchors and formula versions remain distinct.

## Dependency records before scheduling

For each selected output, record:

| Required field | Purpose |
| --- | --- |
| Feature/algorithm/version/parameters and output units | Distinguish definition and parameter compatibility |
| Raw schemas/fields, source revision and input admission | Identify facts that can be shared safely |
| Exact derived prerequisites, optional inputs and absence policy | Block only actual prerequisites |
| Session/interval/cutoff/action/knowledge basis | Preserve causality and availability |
| Initialization/warm-up/state key/order/replay rules | Define independent mutable chains |
| Batch/update/restore/merge capabilities and limitations | Avoid unsupported partition/state assumptions |
| Expected universe/shards and reduction identity | Scope cross-sectional barriers |
| Publication ownership and completion visibility | Respect sink/receipt/catalog boundaries |
| Measured cost/bytes and resource reservations | Choose useful granularity and admission |
| Evidence precision: code-declared, inspected or proposed | Prevent a planning association becoming an execution guarantee |

Keep raw-input, mathematical, ordered-state, current component-admission, universe, publication and release dependencies separate. A grouped inventory may conservatively union prerequisites across multiple suboutputs; expand it to the selected output/parameter graph before executing it. Do not schedule such union rows as if every displayed parent were mathematically necessary.

EMA, RSI and ATR need their admitted history and initialization; they do not require each other's completed result. Independent periods may run concurrently or share a compatible input pass. A recursive time chain remains ordered within its own state identity. Pairwise comparisons join only their two witnesses. Breadth/ranking waits for its declared member population, while unrelated ready tasks continue. Future outcomes never feed origin-time signals.

Prefer selected-output closure and compatible fusion over a process per scalar. Share validated immutable inputs and sufficient statistics under exact identity; keep optional consumers outside the direct calculation path. Independent invocation does not establish thread safety for arbitrary caller callbacks or shared mutable accumulators.

## Actual orchestration/resource constraints

The public [supervisor](https://github.com/atulsrivas1/equity-feature-workers/blob/a69ae9cfeb62730fc78705b4752b94c6f9438275/packages/workers/src/equity_feature_workers/supervisor.py) supports sequential, thread and spawn-process modes. It groups intersecting instrument populations into coarse shards and executes items within each shard sequentially. This protects chronology but may be broader than some independent feature/state dependencies. Refinement needs per-state ownership and immutable-input/result proof; deleting the protection alone is insufficient.

Current admission caps workers at 32 and tasks at 4096; `io_slots` is restricted to 1. CPU admission uses `workers * compute_threads + backend_threads <= max_cpu_slots`. Those declarations are neither hard physical CPU/RSS enforcement nor automatic configuration of arbitrary backend thread pools. Whole-shard process transport, prepared inputs before dispatch and parent-side publication also matter. The existing bounded input cache and result/spill limits must retain source/cutoff/config isolation.

The [Parquet sink](https://github.com/atulsrivas1/equity-feature-io/blob/18d86761aa3eebb7414e51e8fa2aba089717b5eb/packages/parquet/src/equity_feature_parquet/sink.py) locks an output root across a write attempt. The [DuckDB sink contract](https://github.com/atulsrivas1/equity-feature-io/blob/18d86761aa3eebb7414e51e8fa2aba089717b5eb/docs/api/DUCKDB_SINK.md) preserves serialized database ownership. More compute workers cannot change those publication guarantees. Separate destinations need qualified assembly/readback/catalog rules; a bounded publisher can overlap independent computation only within existing ownership rules.

Use one combined resource owner for compute, adapters, backend threads, IPC copies, queues, state, results, writer and spill. A configurable full-machine profile should use available resources within explicit reserves and observed capacity. More workers, native-thread reservations or memory allocation are not objectives by themselves. Record what is logically reserved, genuinely enforced and measured. Budget nested pools together and apply bounded backpressure.

The existing audit found wider modes slower on retained workloads. This supports measurement and conservative defaults, not a claim that future representative compute-heavy work cannot benefit. No new timing, hardware benchmark, speedup or fastest-library ranking is established by this documentation.

## Proposed sequence and validation gates

These work packages guide later selection; they are not newly Ready runtime stories or an invented release/date. Keep one selected implementation story at a time.

| Order | Work | Required evidence before adoption |
| --- | --- | --- |
| 1 | Select representative workload/features; freeze per-output dependency and semantic crosswalk | Exact raw/derived/state/universe edges, formulas/units/seed/timing/gaps and independent fixtures; distinguish missing APIs from parameters/consumer policies |
| 2 | Measure current direct and worker paths without changing math/defaults | Repeated compute-only and complete-pipeline reference, source/hardware/runtime/config identity, full logical-result parity and attributed stage/queue/lock/memory costs |
| 3 | Optimize one dominant measured cost | A/B benefit with numerical/status/quality/evidence/identity parity; ownership, bounded memory, retry/cancel/uncertain-commit and readback correctness |
| 4 | Refine coarse state/feature scheduling only where independence is proved | Trace actual overlap for independent same-instrument branches, preserve ordered recurrence and avoid mutable aliasing; waiting dependencies do not idle unrelated work |
| 5 | Select and add missing reusable kernels in small specified batches | Original math specifications, input/timeframe/state contracts, independent synthetic fixtures and installed/platform/release evidence; no wholesale source-specific port |
| 6 | Qualify resource profiles and any wider interface limits | Supported worker/native-thread/task-granularity matrix, repeated elapsed-time/resource distributions, actual parent/child memory and I/O, skew/saturation/overload and fallback when wider loses |

Freeze an adoption rule with the selected workload before optimizing. Include startup, decode/conversion, validation, calculation, encoding/hash/IPC, queues/locks, publication, verification and catalog in end-to-end claims. Report elapsed makespan and critical path; overlapping stage durations cannot be summed as elapsed wall time. Distinguish throughput from p95/p99 trader freshness and test their contention if a live path is later selected.

Independent math oracles and exact integer/notional/ns preservation remain mandatory. Test missing versus empty inputs, zero denominators, warm-up/gaps, prior-only and cutoff boundaries, early close/actions, state restore/legal merge/replay, skew, blocked dependencies, declared-universe coverage, retries/cancellation and publication contention. A shared optimized kernel agreeing with itself is insufficient. Source/config/result identities and evidence/quality parity are part of correctness.

## Delivery and continuity

Author checks for this draft: the existing documentation planning/UTF-8/lifecycle gate passed (134 active story IDs, 39 feature IDs and eight lifecycle stages), as did the existing session/quote/history/context/timing reference checks (123 methods total), new relative-link checks and `git diff --check`. The prior contents of all three continuity documents were preserved as byte-identical suffixes in this checkout. These are author/static/documentation checks; they are not independent review, new legacy numerical parity, benchmark results or runtime release evidence. Current candidate CI and separate review remain additional gates.

GOV-030 is planning outside the deferred runtime milestone. Existing accepted R5/R8 delivery evidence is preserved; recommendations do not reopen accepted stories as defects. Related future [LIVE002 #458](https://github.com/atulsrivas1/equity-features/issues/458) and [LIVE004 #460](https://github.com/atulsrivas1/equity-features/issues/460) remain Backlog; reuse their scope when selected rather than create duplicate runtime trackers. No R17, feed, cadence/SLA, provider/private-data work, deployment, trading, automation or new package release is authorized by this packet.

The detailed comparison remains local. Publication of that material needs established redistribution rights. This public packet still requires supported separate final-head review under [CODE_REVIEW.md](CODE_REVIEW.md); earlier bounded local-review grants are not extended by inference. Author self-checks and CI do not satisfy that gate. Keep the draft reviewable and record actual reviewer identity/checks/limitations before normal Test/publication/Done transitions.
