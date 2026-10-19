# Flow Analyst: initial product decisions

Owner discussion, October 19, 2026. Planning under [EQ-207](https://github.com/atulsrivas1/equity-features/issues/556), [GOV-033](https://github.com/atulsrivas1/equity-features/issues/525) and the [R29 plan](R29_RELEASE_PLAN.md). This records product direction, not a delivered application, new source qualification or selected operating deployment. Live GitHub Project status remains authoritative.

## Product and initial markets

The consumer application is **Flow Analyst**. **Exposure Analyst** and **Volatility Analyst** name the other discussed applications; their product scope will be discussed separately. The underlying reusable libraries keep their technical names.

Flow Analyst initially targets trading activity in:

| Market | Product coverage direction | Admission boundary |
| --- | --- | --- |
| Stocks | Equity trading activity, volume/notional, large prints and selected activity comparisons | Only qualified instruments, dates, fact types, units and source coverage |
| Options | Contracts/premium, executions, clusters, strike/expiry concentration and explicitly labelled direction estimates | Contract definitions, multiplier, quote alignment, OI/model inputs and knowledge-time coverage admitted per selected output |
| ETFs | ETF share trading within equity data, and options on covered ETFs | ETF membership/classification and options coverage explicit; no blanket universe or historical coverage inferred |

This choice is informed by retained-data inventory evidence discussed with the owner. That evidence is historical and private; it is not a fresh audit of every source file, complete market coverage, live-feed availability, redistribution permission or production readiness. The public product plan does not publish a private corpus or its paths. Availability must be reported by instrument, date/session and data type, preserving missing, partial and unavailable states.

**ETF trading activity is not ETF fund flow.** Creation/redemption and subscription/withdrawal analysis are not part of the confirmed initial data claim. Holdings records alone do not establish those flows. Likewise traded volume, estimated trade direction and open-interest changes are separate observations; they do not establish investor intent, net capital entering a market or dealer positions.

Futures, FX, bonds, crypto and ETF creation/redemption datasets are possible later discussions, not selected first-release markets or acquisition work.

## Data generation and product use

1. I/O acquires/reads and normalizes selected facts and publishes selected results through declared source/sink contracts.
2. Feature libraries calculate from supplied facts/configuration/state; they do not fetch, schedule or publish.
3. Workers coordinate inputs, dependency readiness, calculations, bounded shared resources, recovery and verified publication to generate datasets.
4. The product backend/query layer consumes admitted generated datasets and exposes them to the UI with identity, freshness, availability, quality and evidence.
5. The UI provides views, filtering, exploration and user workflows. It does not duplicate feature mathematics. A product can request a worker job; multiple products may reuse the same compatible generated dataset.

These are responsibility boundaries, not a requirement to create separate processes/services or recompute data for each product. Ad hoc/research callers may still invoke the pure library API directly. Shared input/intermediate reuse, coordinated worker/backend CPU-memory-I/O budgets and the shortest correct processing time within configured resources remain architecture goals; no measured speed or live latency target is established by this discussion.

## Existing work to reuse

Reuse equity trade/quote/window and largest-print scope in EQ-158/159/162, admitted equity integration in EQ-180, option foundations in EQ-182–187 and option/shared microstructure in EQ-188–193. EQ-207 owns Flow Analyst product policy/composition; EQ-210/211 retain selected delivery/integration and release gates. This document adds no competing calculations, adapters or worker framework.

## Deferred product details

The owner subsequently clarified that this discussion is only defining high-level products. Intraday monitoring versus end-of-day research versus both remains unselected and is deferred; it is not a prerequisite question to force during this discussion. It would later guide screens, history, cadence and freshness, without itself authorizing acquisition or deployment.

Use the [high-level product map](PRODUCT_MAP.md) for product purposes and watchlist/strategy placement. Candidate activity/concentration/unusual-activity/price-versus-flow views and detailed datasets/feature IDs, filters and UI behavior remain proposals for later discussion. Any genuinely new implementation scope still needs linked stories before Ready.
