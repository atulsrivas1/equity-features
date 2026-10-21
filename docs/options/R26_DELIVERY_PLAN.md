# R26 — Option flow, activity and execution

[Replan](../OPTION_DELIVERY_REPLAN.md). Existing epic [E34](https://github.com/atulsrivas1/equity-features/issues/533); milestone [30](https://github.com/atulsrivas1/equity-features/milestone/30). Planning only; Project owns live status. Preserve equity/R18 ownership and option implementation gates.

## Parallel layer contracts

Contract owner: EQ-188. Published reviewed release contracts, independent conformance fixtures and accepted implementation prerequisites; integration follows actual producer readiness.

| Track | Stories | Deliverables |
| --- | --- | --- |
| libraries | EQ-188, EQ-189, EQ-190, EQ-215 | Compute option execution/cluster, directional-premium, concentration, activity baselines and admitted equity-option measures. |
| io | EQ-191 | Map ordered trades/quotes, quote-alignment witnesses, prior populations and compatible equity histories; persist flow/window outputs and eligibility evidence. |
| workers | EQ-192 | Preserve event order/sign carry and independent ready windows with bounded shared preparation and stored-result parity. |

## Integrated acceptance and demonstration

Release acceptance: EQ-193; integrated composition: EQ-193. No setup-only release; no API/product UI/public deployment gate.

Ordered synthetic prints/quotes with ties, baseline gaps, short-DTE/OTM shares and an independent equity-option alignment example.

Compare independently expected results with direct calls, installed workers and stored readback. Include available, unavailable and invalid cases, timing/identity/provenance, supported modes, retries and sink conflicts. Freeze actual compatible package artifacts, applicable Windows/Linux checks and resource workloads before implementation. Required fresh independent review and CI remain mandatory. Demonstration is performed at implementation acceptance, not claimed by this planning packet.

## Story contracts

### EQ-188: Specify option execution and shared tape semantics

[#534](https://github.com/atulsrivas1/equity-features/issues/534). Layer: contracts/design. Provisional complexity: 3 points; not an estimate of days.

Freeze supported execution/quote alignment, sign proxies/unknowns, event ordering/ties, cancellations/corrections, eligibility, windows and multiplier/price precision. Reuse equity tape/quote kernels only where mathematics and evidence match; retain explicit asset conventions and source-specific inference limits.

Dependencies: EQ-182, EQ-158, EQ-159. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent tiny tapes, causal quote alignment/sign carry, missing coverage and correction replay; observed trade direction is not customer intent or dealer positioning.

### EQ-189: Implement option flow rollups and concentration primitives

[#535](https://github.com/atulsrivas1/equity-features/issues/535). Layer: pure calculation. Provisional complexity: 5 points; not an estimate of days.

Implement selected eligible counts/contracts, premium/notional, signed/unknown summaries, declared group/window rollups and concentration over supplied populations. Separate reducer arithmetic from unusual-flow screens and trade-selection policy.

Dependencies: EQ-188, EQ-183. Delivery gates are separate from runtime operand dependencies.

Independent validation: Literal independently calculated tape/group results, exact scaled accumulation/overflow, ties, unknown/empty/partial populations and legal ordered merge/replay parity.

### EQ-190: Implement admitted equity-option participation and lead-lag measures

[#536](https://github.com/atulsrivas1/equity-features/issues/536). Layer: pure calculation. Provisional complexity: 5 points; not an estimate of days.

Define compatible equity/option signed buckets, shares/contracts/premium denominators and aligned descriptive lag/correlation measures. Preserve time direction, paired sample counts and zero-variance/denominator behavior; no future buckets as current prerequisites.

Dependencies: EQ-188, EQ-153, EQ-158. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent paired bucket vectors, sign/clock/unit/coverage mismatches, positive/negative lag and leakage counterexamples; reused equity arithmetic only under exact matching definitions.

### EQ-191: Qualify option flow input, replay and sink mappings

[#537](https://github.com/atulsrivas1/equity-features/issues/537). Layer: I/O. Provisional complexity: 5 points; not an estimate of days.

Map selected normalized execution/quote/spot/group facts and replay inputs to flow contracts and typed sinks. Share immutable admitted populations across products when identities/rights match; bound source reads and cached memory.

Dependencies: EQ-185, EQ-188, EQ-215. Delivery gates are separate from runtime operand dependencies.

Independent validation: Synthetic source-to-fact/readback and replay closure, revisions, partial windows, actual versus proxy direction/quote semantics and denied unsupported mappings.

### EQ-192: Implement bounded flow and microstructure workers

[#538](https://github.com/atulsrivas1/equity-features/issues/538). Layer: workers. Provisional complexity: 5 points; not an estimate of days.

Wire independent rollup/concentration/cross-market branches; preserve ordered per-contract/underlying signing state and only selected joins. Reuse buckets across outputs and products; coordinate native/worker parallelism, memory, I-O and publication.

Dependencies: EQ-189, EQ-190, EQ-191, EQ-144, EQ-145, EQ-215. Delivery gates are separate from runtime operand dependencies.

Independent validation: Direct/worker/evidence parity, causal state/replay, restart/fault/readback, skew/hot-entity and shared-input workload measurements without oversubscription.

### EQ-193: Qualify shared microstructure and option flow release

[#539](https://github.com/atulsrivas1/equity-features/issues/539). Layer: release acceptance. Provisional complexity: 5 points; not an estimate of days.

Prove selected option/equity reuse and separate asset-specific definitions, explicit capabilities, source-independent packages, adapter/worker combinations and synthetic examples. Product screens remain later policy scope.

Dependencies: EQ-187, EQ-192, EQ-215. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent tiny-tape and cross-asset fixtures, both-platform installed artifacts, resource/throughput/latency/copy evidence with parity, separate review and actual release/readback.

### EQ-215: Implement option activity baselines and execution-window measures

[#574](https://github.com/atulsrivas1/equity-features/issues/574). Layer: pure calculation. Provisional complexity: 5 points; not an estimate of days.

Specify prior-only relative volume/trade-count and median/MAD premium anomaly measures, quote-aligned execution clusters and short-DTE/OTM participation over declared populations. Reuse compatible equity/tape reducers without treating mean and median or event and known-at clocks as interchangeable.

Dependencies: EQ-188, EQ-189. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent sorted history and ordered event vectors, zero-MAD/empty/incomplete baseline, tick/quote ties and gaps, corrections, window boundaries, eligibility and unit-scaled premium cases.
