# R26 — Option flow and shared microstructure extensions

Owner-requested future planning, October19,2026. [Epic](https://github.com/atulsrivas1/equity-features/issues/533), [milestone](https://github.com/atulsrivas1/equity-features/milestone/30), [governance](https://github.com/atulsrivas1/equity-features/issues/525). Planned Backlog/unassigned/no due date; live Project owns status.

## EQ-188: Specify option execution and shared tape semantics

[Issue](https://github.com/atulsrivas1/equity-features/issues/534); layer: contracts/design. Dependencies: EQ-182, EQ-158, EQ-159.

Freeze supported execution/quote alignment, sign proxies/unknowns, event ordering/ties, cancellations/corrections, eligibility, windows and multiplier/price precision. Reuse equity tape/quote kernels only where mathematics and evidence match; retain explicit asset conventions and source-specific inference limits.

Validation: Independent tiny tapes, causal quote alignment/sign carry, missing coverage and correction replay; observed trade direction is not customer intent or dealer positioning.

## EQ-189: Implement option flow rollups and concentration primitives

[Issue](https://github.com/atulsrivas1/equity-features/issues/535); layer: pure calculation. Dependencies: EQ-188, EQ-183.

Implement selected eligible counts/contracts, premium/notional, signed/unknown summaries, declared group/window rollups and concentration over supplied populations. Separate reducer arithmetic from unusual-flow screens and trade-selection policy.

Validation: Literal independently calculated tape/group results, exact scaled accumulation/overflow, ties, unknown/empty/partial populations and legal ordered merge/replay parity.

## EQ-190: Implement admitted equity-option participation and lead-lag measures

[Issue](https://github.com/atulsrivas1/equity-features/issues/536); layer: pure calculation. Dependencies: EQ-188, EQ-153, EQ-158.

Define compatible equity/option signed buckets, shares/contracts/premium denominators and aligned descriptive lag/correlation measures. Preserve time direction, paired sample counts and zero-variance/denominator behavior; no future buckets as current prerequisites.

Validation: Independent paired bucket vectors, sign/clock/unit/coverage mismatches, positive/negative lag and leakage counterexamples; reused equity arithmetic only under exact matching definitions.

## EQ-191: Qualify option flow input, replay and sink mappings

[Issue](https://github.com/atulsrivas1/equity-features/issues/537); layer: I/O. Dependencies: EQ-185, EQ-188.

Map selected normalized execution/quote/spot/group facts and replay inputs to flow contracts and typed sinks. Share immutable admitted populations across products when identities/rights match; bound source reads and cached memory.

Validation: Synthetic source-to-fact/readback and replay closure, revisions, partial windows, actual versus proxy direction/quote semantics and denied unsupported mappings.

## EQ-192: Implement bounded flow and microstructure workers

[Issue](https://github.com/atulsrivas1/equity-features/issues/538); layer: workers. Dependencies: EQ-189, EQ-190, EQ-191, EQ-144, EQ-145.

Wire independent rollup/concentration/cross-market branches; preserve ordered per-contract/underlying signing state and only selected joins. Reuse buckets across outputs and products; coordinate native/worker parallelism, memory, I-O and publication.

Validation: Direct/worker/evidence parity, causal state/replay, restart/fault/readback, skew/hot-entity and shared-input workload measurements without oversubscription.

## EQ-193: Qualify shared microstructure and option flow release

[Issue](https://github.com/atulsrivas1/equity-features/issues/539); layer: release acceptance. Dependencies: EQ-187, EQ-192.

Prove selected option/equity reuse and separate asset-specific definitions, explicit capabilities, source-independent packages, adapter/worker combinations and synthetic examples. Product screens remain later policy scope.

Validation: Independent tiny-tape and cross-asset fixtures, both-platform installed artifacts, resource/throughput/latency/copy evidence with parity, separate review and actual release/readback.

## Release gates


## Mandatory acceptance and boundaries

- [ ] Original mathematics, dimensions/units, timing/knowledge, initialization, model/eligibility/coverage and edge cases frozen with independent expected fixtures before Ready. Detailed private code/formulas/thresholds require established rights; raw source-derived ledgers stay local.
- [ ] Source-independent supplied-fact kernels; acquisition/credentials/storage in I/O, dependency scheduling/resource/persistence in workers, policy in consumers. Existing equity calculations/events/labels/scanners reused where semantically compatible.
- [ ] Supported batch/update/restore/merge/replay capabilities explicit; result/null/status/quality/evidence/identity parity and independent positive/negative/adversarial fixtures. No invented support from a registry declaration.
- [ ] Minimize repeated reads/copies/calculations; share compatible immutable inputs/intermediates with exact identity and bounded lifetime. Preserve actual per-output dependencies and ordered state. One coordinated CPU/RAM/I/O/backend-thread budget across products; configurable limits and an explicit full-machine option within real constraints. No mandatory process/service per library.
- [ ] Measure defined cold/warm/small/large/skewed workloads against credible current/serial/alternative baselines with parity; report kernel versus total time, throughput, memory/copies/I-O and live p50/p95/p99/freshness where supported. No universal fastest or invented SLA.
- [ ] Documentation, mathematical/API/discovery/examples/decisions/compatibility, required separate final-head review, applicable CI/installed both-platform artifacts and actual publication/readback accompany the story. Only actual accepted release scope becomes Done.

Future Backlog, unassigned, no due date or runtime selection. Current equity R17/R18 sequence and R22-R24 draft plan are preserved. Dependency lists are admission gates, not global runtime barriers. Release numbers are planning order, not a fabricated mathematical dependence between volatility/exposure branches. No provider spending/private data operation, live-feed/SLA, hosted deployment, notification sending, registry/admin/destructive/recurring scope or future review authorization is granted by this plan. Existing deferred provider/LIVE/SEC stories remain authoritative.

All selected children accepted; every admitted output/worker/product definition tied to accepted scope or separately numbered residual before final coverage acceptance.
