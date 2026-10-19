# R28 — Option exposure grids and numerical changes

Owner-requested future planning, October19,2026. [Epic](https://github.com/atulsrivas1/equity-features/issues/548), [milestone](https://github.com/atulsrivas1/equity-features/milestone/32), [governance](https://github.com/atulsrivas1/equity-features/issues/525). Planned Backlog/unassigned/no due date; live Project owns status.

## EQ-201: Specify exposure assumptions, population and model boundaries

[Issue](https://github.com/atulsrivas1/equity-features/issues/549); layer: contracts/design. Dependencies: EQ-182, EQ-183.

Define selected gamma/vanna or other admitted sensitivity exposures, dimensional scaling, OI/position/sign assumptions, standard/nonstandard multiplier policy, scope and causal spot/model reference alignment. OI is not observed dealer positioning. Freeze independent GEX/VEX operands and completeness before code.

Validation: Independent dimensional/small-contract reference vectors, unknown sign/OI/multiplier/spot inputs and distinct metric readiness; declared position scenarios and model conventions explicit.

## EQ-202: Implement exposure contributions and declared grids

[Issue](https://github.com/atulsrivas1/equity-features/issues/550); layer: pure calculation. Dependencies: EQ-201.

Compute selected supplied-Greek/position contributions and governed strike/expiry/entity reductions. Reuse leaf contributions; completeness/partial sums are explicit. A metric needing additional model inputs must not block a separately ready metric.

Validation: Independent exact/small decimal reductions, sign/unit/overflow/tie cases, partial/missing/complete populations and stable reduction/parity policy; no automatic dealer net-position claim.

## EQ-203: Implement exposure changes and explicit counterfactual arithmetic

[Issue](https://github.com/atulsrivas1/equity-features/issues/551); layer: pure calculation. Dependencies: EQ-201, EQ-202.

Compare compatible before/after grids and selected ordered repricing/OI counterfactuals under actual clocks/reference identities. Distinguish arithmetic attribution from causal explanation. Product node filters/alerts and level selection remain later policy.

Validation: Independent multi-step scenarios, order sensitivity, unequal frames, corrections/duplicate snapshots and unavailable intermediates; reuse grids without recomputing leaf exposures.

## EQ-204: Implement exposure reference and generation I-O

[Issue](https://github.com/atulsrivas1/equity-features/issues/552); layer: I/O. Dependencies: EQ-185, EQ-201.

Bind supplied Greek/model/OI/position/spot/definition facts and exact declared populations to typed exposure snapshots and generation sinks. Reuse original source/receipt evidence and bounded immutable input caches.

Validation: Synthetic reference/normalization/sink/readback conformance, missing/stale/foreign scope and OI revision cases; backend writer restrictions and rights limits retained.

## EQ-205: Implement bounded exposure and change workers

[Issue](https://github.com/atulsrivas1/equity-features/issues/553); layer: workers. Dependencies: EQ-202, EQ-203, EQ-204, EQ-144, EQ-145.

Wire per-metric/contract/cell readiness and compatible reductions, snapshot changes and verified publication. One coordinated resource owner accounts for grids, backend threads, queues and concurrent products; GEX does not await VEX-only operands.

Validation: Direct/worker/full receipt parity, partial-grid isolation, source correction/replay, faults/recovery and synthetic small/large/skewed grid resource/time measurements.

## EQ-206: Qualify exposure library and cross-layer release

[Issue](https://github.com/atulsrivas1/equity-features/issues/554); layer: release acceptance. Dependencies: EQ-187, EQ-205.

Qualify explicit assumption/model/population/output/API/I-O/worker combinations and preserve reusable option-contract facts. Publish original synthetic exposure examples and honest limits; do not equate arithmetic to investor intent.

Validation: Independent dimensional/numerical/timing fixtures, both-platform installed artifacts, measured current/alternative baselines and parity, separate final-head review and exact publication/readback.

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
