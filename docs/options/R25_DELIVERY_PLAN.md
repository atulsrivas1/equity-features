# R25 — Option reference, pricing, Greeks and implied volatility

[Replan](../OPTION_DELIVERY_REPLAN.md). Existing epic [E33](https://github.com/atulsrivas1/equity-features/issues/526); milestone [29](https://github.com/atulsrivas1/equity-features/milestone/29). Planning only; Project owns live status. Preserve equity/R18 ownership and option implementation gates.

## Parallel layer contracts

Contract owner: EQ-182. Published reviewed release contracts, independent conformance fixtures and accepted implementation prerequisites; integration follows actual producer readiness.

| Track | Stories | Deliverables |
| --- | --- | --- |
| libraries | EQ-182, EQ-183, EQ-184, EQ-214 | Compute supported reference/liquidity/chain, pricing, Greek and IV outputs from admitted supplied facts. |
| io | EQ-185 | Map option definitions/trades/quotes, underlying, clocks, multiplier, model/reference facts and result rows; qualify selected DuckDB tables or synthetic fixtures and configure the separate output sink. |
| workers | EQ-186 | Route selected contract metrics with independent readiness, bounded batches and retry/readback. |

## Integrated acceptance and demonstration

Release acceptance: EQ-187; integrated composition: EQ-187. No setup-only release; no API/product UI/public deployment gate.

A small chain with model price/IV round-trip, supplied Greek path, expired/unsupported and missing-reference cases; show stored values and provenance.

Compare independently expected results with direct calls, installed workers and stored readback. Include available, unavailable and invalid cases, timing/identity/provenance, supported modes, retries and sink conflicts. Freeze actual compatible package artifacts, applicable Windows/Linux checks and resource workloads before implementation. Required fresh independent review and CI remain mandatory. Demonstration is performed at implementation acceptance, not claimed by this planning packet.

## Story contracts

### EQ-182: Specify option facts, model boundaries and library ownership

[#527](https://github.com/atulsrivas1/equity-features/issues/527). Layer: contracts/design. Provisional complexity: 3 points; not an estimate of days.

Reconcile option and mixed source candidates/finite product definitions into source-safe output and dependency manifests. Define option identity, exercise/settlement, expiry/time conventions, price/size/currency/multiplier units, underlying alignment, rates/dividends, quote eligibility, revisions and known-at. Select the initial model/exercise scope explicitly before Ready. Keep supplied model facts separate from calculated outputs. Assign every admitted gap a concrete story; decide modules versus distributions from consumers, preserving existing APIs.

Dependencies: EQ-012, EQ-013, EQ-014, EQ-016. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent contract/timestamp/multiplier/exercise counterexamples, no orphan admitted definitions and compatibility review; unresolved conventions remain blocked, not defaults.

### EQ-183: Implement admitted contract pricing and Greek calculations

[#528](https://github.com/atulsrivas1/equity-features/issues/528). Layer: pure calculation. Provisional complexity: 5 points; not an estimate of days.

Specify and implement only the reviewed pricing/model/exercise profiles and selected Greeks. Define discount/carry/time bases, dimensions, scaling, limits, expiry/zero-volatility and unsupported-input behavior. Share compatible model intermediates; supplied Greek facts need not invoke the model.

Dependencies: EQ-182. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent analytic/high-precision or independently implemented fixtures and finite-difference crosschecks with declared error budgets, edge limits, input ownership and bounded batch memory.

### EQ-184: Implement bounded implied-volatility inversion

[#529](https://github.com/atulsrivas1/equity-features/issues/529). Layer: pure calculation. Provisional complexity: 5 points; not an estimate of days.

Define admissible quotes/price bounds, model-specific IV roots, bracketing, tolerances, convergence budgets, ambiguous/nonexistent roots, expiry and null/status. Reuse pricing operands without changing selected model semantics.

Dependencies: EQ-182, EQ-183. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent known-price/volatility pairs and invalid/near-boundary/poor-conditioning cases; residual and solver-budget evidence, exact statuses and measured baseline parity.

### EQ-185: Implement option and model-reference I-O contracts and conformance

[#530](https://github.com/atulsrivas1/equity-features/issues/530). Layer: I/O. Provisional complexity: 5 points; not an estimate of days.

Define explicitly supplied/file/synthetic option trade/quote/definition, rates/dividends/model/OI/position reference and output-sink contracts using existing SDK/receipt/version boundaries. Preserve source identity, clocks, action/multiplier and declared coverage. Provider entitlement and actual provider acquisition stay in separately selected adapter scope.

Dependencies: EQ-182, EQ-125. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent synthetic source/sink conformance, missing/stale/revised references, normalized-unit/precision/error fixtures, bounded reads and complete receipt/readback; no private/provider call required.

### EQ-186: Wire independent option compute worker branches

[#531](https://github.com/atulsrivas1/equity-features/issues/531). Layer: workers. Provisional complexity: 5 points; not an estimate of days.

Expose selected pricing/Greek/IV requests over admitted supplied facts and existing I/O. Schedule independently ready contract/metric branches under one resource owner; IV-only inputs cannot block a supplied-Greek or different ready output. Bound task/batch size, backend threads, copies, in-flight memory and sink ownership.

Dependencies: EQ-183, EQ-184, EQ-185, EQ-143, EQ-144, EQ-214. Delivery gates are separate from runtime operand dependencies.

Independent validation: Direct versus installed-worker full-result/quality/evidence parity, unrelated-missing-input isolation, retry/recovery/readback and repeated budget-constrained kernel/end-to-end workloads.

### EQ-187: Qualify option foundation library and cross-layer release

[#532](https://github.com/atulsrivas1/equity-features/issues/532). Layer: release acceptance. Provisional complexity: 5 points; not an estimate of days.

Qualify exact supported model/contract/API/I-O/worker combinations, package/module boundaries, independent consumer examples and immutable release evidence. Existing equity APIs and pure dependency boundaries remain intact.

Dependencies: EQ-183, EQ-184, EQ-185, EQ-186, EQ-214. Delivery gates are separate from runtime operand dependencies.

Independent validation: Both-platform clean wheel/sdist installs, independent numerical/causal/error fixtures, artifact/source closure, separate final-head review and actual publication/readback; finite supported model scope stated.

### EQ-214: Implement option reference, liquidity and chain evidence

[#573](https://github.com/atulsrivas1/equity-features/issues/573). Layer: pure calculation. Provisional complexity: 5 points; not an estimate of days.

Define and implement supplied-fact DTE, moneyness, multiplier, spread/quote-coverage and admitted chain/liquidity summaries. Separate raw measures from versioned eligibility/score policy; no inferred trade direction, observed liquidity or synthetic coverage.

Dependencies: EQ-182. Delivery gates are separate from runtime operand dependencies.

Independent validation: Independent expiry/calendar/settlement, strike/spot/zero denominator, multiplier/action, locked/crossed/stale quote, partial-chain and supplied-versus-calculated cases.
