# Option and product feature-library roadmap

Owner requested the next library planning set after the equity roadmap, October19,2026. [GOV033](https://github.com/atulsrivas1/equity-features/issues/525). This packet plans30stories/fivefuturemilestones; it does not start implementation or create new repositories/distributions.

| Release | Outcome | Epic | Stories |
| --- | --- | --- | --- |
| [R25](https://github.com/atulsrivas1/equity-features/milestone/29) | Option contracts, pricing and feature foundations | [E33](https://github.com/atulsrivas1/equity-features/issues/526) | [EQ-182](https://github.com/atulsrivas1/equity-features/issues/527), [EQ-183](https://github.com/atulsrivas1/equity-features/issues/528), [EQ-184](https://github.com/atulsrivas1/equity-features/issues/529), [EQ-185](https://github.com/atulsrivas1/equity-features/issues/530), [EQ-186](https://github.com/atulsrivas1/equity-features/issues/531), [EQ-187](https://github.com/atulsrivas1/equity-features/issues/532) |
| [R26](https://github.com/atulsrivas1/equity-features/milestone/30) | Option flow and shared microstructure extensions | [E34](https://github.com/atulsrivas1/equity-features/issues/533) | [EQ-188](https://github.com/atulsrivas1/equity-features/issues/534), [EQ-189](https://github.com/atulsrivas1/equity-features/issues/535), [EQ-190](https://github.com/atulsrivas1/equity-features/issues/536), [EQ-191](https://github.com/atulsrivas1/equity-features/issues/537), [EQ-192](https://github.com/atulsrivas1/equity-features/issues/538), [EQ-193](https://github.com/atulsrivas1/equity-features/issues/539) |
| [R27](https://github.com/atulsrivas1/equity-features/milestone/31) | Volatility surfaces, tenors and comparisons | [E35](https://github.com/atulsrivas1/equity-features/issues/540) | [EQ-194](https://github.com/atulsrivas1/equity-features/issues/541), [EQ-195](https://github.com/atulsrivas1/equity-features/issues/542), [EQ-196](https://github.com/atulsrivas1/equity-features/issues/543), [EQ-197](https://github.com/atulsrivas1/equity-features/issues/544), [EQ-198](https://github.com/atulsrivas1/equity-features/issues/545), [EQ-199](https://github.com/atulsrivas1/equity-features/issues/546), [EQ-200](https://github.com/atulsrivas1/equity-features/issues/547) |
| [R28](https://github.com/atulsrivas1/equity-features/milestone/32) | Option exposure grids and numerical changes | [E36](https://github.com/atulsrivas1/equity-features/issues/548) | [EQ-201](https://github.com/atulsrivas1/equity-features/issues/549), [EQ-202](https://github.com/atulsrivas1/equity-features/issues/550), [EQ-203](https://github.com/atulsrivas1/equity-features/issues/551), [EQ-204](https://github.com/atulsrivas1/equity-features/issues/552), [EQ-205](https://github.com/atulsrivas1/equity-features/issues/553), [EQ-206](https://github.com/atulsrivas1/equity-features/issues/554) |
| [R29](https://github.com/atulsrivas1/equity-features/milestone/33) | Option flow, exposure and volatility integration | [E37](https://github.com/atulsrivas1/equity-features/issues/555) | [EQ-207](https://github.com/atulsrivas1/equity-features/issues/556), [EQ-208](https://github.com/atulsrivas1/equity-features/issues/557), [EQ-209](https://github.com/atulsrivas1/equity-features/issues/558), [EQ-210](https://github.com/atulsrivas1/equity-features/issues/559), [EQ-211](https://github.com/atulsrivas1/equity-features/issues/560) |

## Boundaries and dependency branches

Option facts/model/solver foundations are shared. Volatility R27 and exposure R28 are independent branches of R25; no volatility-product completion is required to compute admitted exposure, and no exposure required for RV/IV. R26 shares only semantically compatible tape/quote primitives. R29 composes separately qualified branches; a selected product request depends only on its actual operands.

Existing EQ154/155/168/173/174/176-179 own equity RV/statistics/reference/event/label/generic-policy/lifecycle work. Reuse accepted equity contracts/evidence/I-O SDK/sinks/workers/service scope; do not duplicate them, move existing APIs silently or infer options support. Option-specific conventions, evidence and product thresholds need original reviewed specifications and independent fixtures before Ready. Only confirmed missing reusable ownership justifies new distributions.

Every release includes distinct contracts/calculation/I-O/worker/acceptance scopes; R29 separately owns product policies and delivery composition. Legacy source and finite catalogues are planning evidence, not numerical parity or proof of exhaustive mathematical completeness. Exact private paths/formulas/thresholds and raw source-derived manifests stay local. EQ182 and each product story must assign every admitted missing output a concrete existing/new story before acceptance; EQ211 audits complete selected traceability and retained exclusions.

Core objective: shortest correct processing time within available resource budget. Reuse immutable compatible facts/intermediates, minimize repeated reads/copies/calculations, coordinate worker/backend parallelism, preserve causal/state/population dependencies and support configurable/full-machine admission. Benchmark defined workload alternatives with complete result/availability parity, kernel versus end-to-end time, throughput, peak memory and live-update tails only where supported. No fastest claim or deadline.

Existing equity execution priority and draft R22-R24 remain unchanged. Provider/private/live/hosting/notifications/admin/registry/destructive/recurring operations and new review grants are not selected. Required separate review/current CI/publication/readback remain pending for this planning packet.


## Capability naming

Owner direction: use Option flow analysis, Option exposure analysis and Volatility analysis as descriptive capability groups. These are not selected product brands. Historical source identifiers remain only as provenance; current issue/release/matrix naming uses capabilities. Naming does not change story IDs, dependencies, scope or status.


## Product discussion: Flow Analyst

[Initial decisions](FLOW_ANALYST_PRODUCT.md) record Flow Analyst targeting stocks, options and ETF trading. ETF fund flows are separate and unverified. I/O and pure features support worker-generated datasets; products query/display them. Intraday versus end-of-day first-version focus is still open. The owner-discussed application names are Flow Analyst, Exposure Analyst and Volatility Analyst; earlier capability-only naming paragraphs are retained as history, superseded for application names.


## High-level product roles and cross-product capabilities

[Product map](PRODUCT_MAP.md) records the seven discussed product groups, watchlists within relevant analysts plus shared watchlists, and Research Analyst as the proposed strategy-definition/historical-evaluation home. Current matching candidates may appear in relevant products. Four additional product boundaries remain proposals; automated execution is separate. Owner scope is high-level discussion: no screens/workflow/cadence or new delivery commitments selected.


## Owner execution priority — October19,2026

Wait for verified R17 and R18 completion before starting option implementation. The intended next option foundation is R25/EQ182-187; this does not require every equity release R19-R24 to finish first. Keep the separate option releases/stories planned Backlog and preserve current equity ownership. R17/R18 release acceptance (EQ141/EQ146), option-plan review/publication and concrete story readiness remain actual gates; no automatic start or new review/operating authority is inferred. This decision creates no reminder, monitor or recurring work.
