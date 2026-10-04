# Chart consumer integration contract

Status: proposed design, 2026-10-04. Qualification story: [EQ-094](https://github.com/atulsrivas1/equity-features/issues/116). No production API, wire schema, chart adapter or package has been implemented. The parallel charting platform is a reference consumer, not a dependency or part of this repository's release.

## Ownership and integration path

Calculation packages own formula semantics, typed inputs/results, explicit quality and supported incremental state. The consumer owns data acquisition, immutable input revisions, update scheduling, charts/drawings, GPU rendering, subscriptions, command/undo state, transport and its agent/MCP interface. Calculations do not perform I/O.

Initially a Python analysis host supplies normalized columnar input to the packages and sends bounded result batches to the Rust consumer through a separate integration adapter. Historical overlays and headless backtesting are the first use cases. Choose the transport during EQ-094 planning; in-memory Arrow objects are not automatically a wire format. Do not place per-frame RPC or per-row language-boundary calls in the rendering path. Local live operation requires an explicitly measured host/adapter and supported incremental calculations; it is not established by this proposal.

Rust/WASM shared mathematical kernels may be considered under EQ-085–087 after profiling, platform/build qualification and cross-backend parity. Python-first packages remain the current baseline. Browser-local/offline Python execution is not assumed. The chart can implement its own native indicators using shared specifications/fixtures, but must identify its implementation and establish parity rather than claim it uses this package.

## Proposed request and response envelope

These are logical fields, not final APIs or mandatory choices of JSON/Arrow/IPC:

| Field group | Required meaning |
| --- | --- |
| Envelope | Schema version and caller-supplied request identity; retries/idempotency owned by adapter/consumer |
| Data binding | Consumer dataset identity, immutable data revision, instrument namespace/mapping and session identity; every referenced input snapshot independently bound |
| Calculation | Feature ID, algorithm/backend version, parameter/config digest, input schema, units, price scale/currency and adjustment basis |
| Timing | Requested market cutoff, applicable reference cutoff, source known-at and declared simulation eligibility; unknown availability remains unknown |
| Result | Typed scalar or aligned series, explicit timestamp/bar bounds, validity/quality, coverage, warm-up, approximation basis and optional evidence |
| Confirmation | Per-result provisional/confirmed state and basis; provisional current-bar values remain distinct from completed-bar results |

The adapter attaches request/data-revision identifiers; the library remains independent of chart state. Event timestamps align observations, but do not establish when a value became available. The consumer may only apply a response to a view whose requested input bindings match. A late response from an older revision is rejected or explicitly displayed as an older snapshot, never relabeled current. Multi-input results bind all dependencies. Chart state revision and market data revision are distinct; panning alone does not change numerical inputs.

The selected transport must retain signed int64 UTC nanoseconds, integer volumes/counts, scaled-price integers and null validity exactly. Plain JavaScript Number is not a lossless general representation of int64; use a tested exact representation at that boundary. Floating indicator outputs have declared tolerances. Rendering may derive floating coordinates from canonical values without replacing numerical truth. Serialization cannot include Python callables/pickled state.

## Update and correction semantics

| Consumer change | Required handling |
| --- | --- |
| Append a completed bar/event | Apply once in admitted order using supported incremental capabilities; adapter owns retry/duplicate delivery handling |
| Replace the unfinished bar | Recalculate a provisional preview from the last committed state with the replacement input; do not accumulate each revision as a new bar |
| Confirm a bar | Commit the admitted final input once, publish confirmed results bound to the resulting revision |
| Correct historical data | Invalidate affected results and replay from a valid earlier checkpoint, or rebuild from full canonical input |
| Backfill earlier history | Reassess warm-up/initialization and history-dependent outputs; a changed EMA seed can affect all subsequent results |
| Change parameters/basis | Use a new config/input binding and rebuild as required; do not reuse incompatible state |

Provisional preview uses a separate state or replay; cloning/restore availability cannot be presumed for every feature. Confirmed means finalized under the caller's admission policy, not immune to later corrections. The earliest changed input does not alone prove a universal finite recalculation window: recursive indicators can invalidate an entire later suffix. Checkpoints require compatible algorithm/config/input prefix. If mutation/restore is unsupported, explicit batch replay is the baseline. Do not retroactively query earlier cutoffs from state that already consumed later data.

## Agent and chart interpretation

Expose feature descriptions, units, required inputs, warm-up, quality and algorithm/config identities to the chart's discovery layer. Its typed commands, queries, event subscriptions, MCP tools and image/description consistency remain consumer responsibilities. Query and rendered views must bind to the same accepted snapshot where the chart claims agreement.

Calculate from full-resolution canonical data, not visual level-of-detail aggregates. Bar proxies cannot be labeled exact trade VWAP/notional. Sampled bid/ask cannot stand in for continuous quotes or a reconstructed order book. Initial equity scope does not establish crypto/futures session semantics, footprint classification or depth heatmaps.

Local custom Python calculators are trusted caller code under EQ-093; they provide no sandbox. A chart-owned expression interpreter or future execution sandbox has separate validation and resource limits. Remote services expose only approved implementations. No unrestricted code upload follows from this contract.

## Qualification, open decisions and delivery

EQ-094 delivers the finalized portable contract, synthetic consumer harness, examples and compatibility evidence. It does not deliver a production Rust application/adapter. Estimate and a detailed execution plan are set when prerequisites are ready.

Required cases: exact int64/scaled-price/null round trips; stale multi-input revision rejection; unfinished-bar replacements without double counting or committed-state mutation; final confirmation; late correction and older-history backfill replay versus independent batch expectations; gaps/warm-up/availability; metadata and config mismatch; unsupported feature/update errors. Conversion/copy and batch-delivery benchmarks record hardware, workload, versions and precision parity, without a promised frame rate or zero-copy claim.

Open decisions: concrete transport/schema encoding; caller revision token mapping; preview/checkpoint capabilities per feature; batch sizing/backpressure; local host lifetime and cancellation; which chart-side deployment modes require native computation. Resolve during planning with the chart consumer. Foundation work EQ-012/024 records compatible semantics; EQ-044/048 includes the final qualification. Existing equations are unchanged.
