# R28 — Option exposure contributions, grids and changes

[Replan](../OPTION_DELIVERY_REPLAN.md). Existing epic [E36](https://github.com/atulsrivas1/equity-features/issues/548); milestone [32](https://github.com/atulsrivas1/equity-features/milestone/32). Planning only; Project owns live status. Preserve equity/R18 ownership and option implementation gates.

## Parallel layer contracts

Contract owner: EQ-201. Published reviewed release contracts, independent conformance fixtures and accepted implementation prerequisites; integration follows actual producer readiness.

| Track | Stories | Deliverables |
| --- | --- | --- |
| libraries | EQ-201, EQ-202, EQ-203 | Compute declared sensitivity contributions, per-metric grids and ordered before/after or explicit counterfactual changes. |
| io | EQ-204 | Map supplied/calculated Greeks, causal OI/position assumptions, spot, standard multiplier and population/frame versions; persist completeness per metric/cell. |
| workers | EQ-205 | Execute independent GEX/VEX-ready branches and bounded grid reductions without waiting for unrelated volatility products; serialize change/history publication. |

## Integrated acceptance and demonstration

Release acceptance: EQ-206; integrated composition: EQ-206. No setup-only release; no API/product UI/public deployment gate.

A small declared chain showing GEX ready while VEX is unavailable, incomplete cells and ordered repricing/OI comparison with stored evidence.

Compare independently expected results with direct calls, installed workers and stored readback. Include available, unavailable and invalid cases, timing/identity/provenance, supported modes, retries and sink conflicts. Freeze actual compatible package artifacts, applicable Windows/Linux checks and resource workloads before implementation. Required fresh independent review and CI remain mandatory. Demonstration is performed at implementation acceptance, not claimed by this planning packet.

## Story contracts

### EQ-201: Specify exposure assumptions, population and model boundaries

[#549](https://github.com/atulsrivas1/equity-features/issues/549). Layer: contracts/design. Provisional complexity: 3 points; not an estimate of days.

Define selected gamma/vanna or other admitted sensitivity exposures, dimensional scaling, OI/position/sign assumptions, standard/nonstandard multiplier policy, scope and causal spot/model reference alignment. OI is not observed dealer positioning. Freeze independent GEX/VEX operands and completeness before code.

Dependencies: EQ-182, EQ-183. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent dimensional/small-contract reference vectors, unknown sign/OI/multiplier/spot inputs and distinct metric readiness; declared position scenarios and model conventions explicit.

### EQ-202: Implement exposure contributions and declared grids

[#550](https://github.com/atulsrivas1/equity-features/issues/550). Layer: pure calculation. Provisional complexity: 5 points; not an estimate of days.

Compute selected supplied-Greek/position contributions and governed strike/expiry/entity reductions. Reuse leaf contributions; completeness/partial sums are explicit. A metric needing additional model inputs must not block a separately ready metric.

Dependencies: EQ-201. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent exact/small decimal reductions, sign/unit/overflow/tie cases, partial/missing/complete populations and stable reduction/parity policy; no automatic dealer net-position claim.

### EQ-203: Implement exposure changes and explicit counterfactual arithmetic

[#551](https://github.com/atulsrivas1/equity-features/issues/551). Layer: pure calculation. Provisional complexity: 5 points; not an estimate of days.

Compare compatible before/after grids and selected ordered repricing/OI counterfactuals under actual clocks/reference identities. Distinguish arithmetic attribution from causal explanation. Product node filters/alerts and level selection remain later policy.

Dependencies: EQ-201, EQ-202. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent multi-step scenarios, order sensitivity, unequal frames, corrections/duplicate snapshots and unavailable intermediates; reuse grids without recomputing leaf exposures.

### EQ-204: Implement exposure reference and generation I-O

[#552](https://github.com/atulsrivas1/equity-features/issues/552). Layer: I/O. Provisional complexity: 5 points; not an estimate of days.

Bind supplied Greek/model/OI/position/spot/definition facts and exact declared populations to typed exposure snapshots and generation sinks. Reuse original source/receipt evidence and bounded immutable input caches.

Dependencies: EQ-185, EQ-201. Delivery gates are separate from runtime operand dependencies.

Independent validation: Synthetic reference/normalization/sink/readback conformance, missing/stale/foreign scope and OI revision cases; backend writer restrictions and rights limits retained.

### EQ-205: Implement bounded exposure and change workers

[#553](https://github.com/atulsrivas1/equity-features/issues/553). Layer: workers. Provisional complexity: 5 points; not an estimate of days.

Wire per-metric/contract/cell readiness and compatible reductions, snapshot changes and verified publication. One coordinated resource owner accounts for grids, backend threads, queues and concurrent products; GEX does not await VEX-only operands.

Dependencies: EQ-202, EQ-203, EQ-204, EQ-144, EQ-145. Delivery gates are separate from runtime operand dependencies.

Independent validation: Direct/worker/full receipt parity, partial-grid isolation, source correction/replay, faults/recovery and synthetic small/large/skewed grid resource/time measurements.

### EQ-206: Qualify exposure library and cross-layer release

[#554](https://github.com/atulsrivas1/equity-features/issues/554). Layer: release acceptance. Provisional complexity: 5 points; not an estimate of days.

Qualify explicit assumption/model/population/output/API/I-O/worker combinations and preserve reusable option-contract facts. Publish original synthetic exposure examples and honest limits; do not equate arithmetic to investor intent.

Dependencies: EQ-187, EQ-205. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent dimensional/numerical/timing fixtures, both-platform installed artifacts, measured current/alternative baselines and parity, separate final-head review and exact publication/readback.
