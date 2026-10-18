# Reserved future release: live intraday feature delivery

Owner-reserved on October 18, 2026; deferred, not scheduled or selected for immediate execution. Goal: fresh, correct calculated data delivered quickly to traders during the trading day. End-of-day work may tolerate delay.

- [Future milestone 20](https://github.com/atulsrivas1/equity-features/milestone/20), open with no due date.
- [E24#456](https://github.com/atulsrivas1/equity-features/issues/456), proposed epic in Backlog and unassigned.
- [LIVE001#457](https://github.com/atulsrivas1/equity-features/issues/457): admitted live input, rights, initialization, sequence/gap/correction and replay semantics.
- [LIVE002#458](https://github.com/atulsrivas1/equity-features/issues/458): bounded persistent incremental orchestration, capability matrix and dependency-correct state ownership.
- [LIVE003#459](https://github.com/atulsrivas1/equity-features/issues/459): trader delivery, freshness, quality and revision semantics.
- [LIVE004#460](https://github.com/atulsrivas1/equity-features/issues/460): end-to-end latency, parity, recovery, overload and contention qualification.

All five future items are Open/Backlog/unassigned at reservation; GitHub Project owns subsequent live status. They have no runtime points or approved execution date. No R17 designation is inferred. Input precedes dependent orchestration/delivery/qualification; exact dependency edges and acceptance details require a concrete future Ready packet. Existing provider prerequisites are reused only if selected; neither Databento nor Massive is selected here.

[Architecture direction](decisions/LIVE_INTRADAY_ARCHITECTURE_DIRECTION.md) guides present/future design without starting these stories. [GOV029#455](https://github.com/atulsrivas1/equity-features/issues/455) owns publication of that direction outside this future milestone, so completing governance cannot imply runtime release progress. [Reservation inputs](FUTURE_LIVE_INTRADAY_INPUTS.json) preserve deliberately unset choices.

## Selection gate

Before implementation Ready: select the actual feed/entitlements and feature slice; freeze data/temporal/recovery/initialization contracts, universe and rates/bursts, supported operating target, transport/consumer, numeric latency/freshness/error/queue/state budgets, tests and relevant independent review. Obtain genuine target/access/spending/private-data permissions only where required by that concrete design. The owner need not supply these facts merely to reserve the release.

One-second publication is not an accepted SLA or cadence. No network/provider/private acquisition, SDK install, scheduler/process/deployment operation, benchmark or live pipeline is executed by this packet. Existing batch/EOD APIs stay supported; existing batch-only features need honest capability labels, not an immediate rewrite. Unrelated accepted releases and deferred research/C1/witness/security scope remain unchanged.

## Release acceptance

Qualify selected input/replay and dependency-correct incremental orchestration; expose honest trader freshness/cutoff/quality/revision behavior; measure representative end-to-end p95/p99 latency and correctness/recovery under bursts, gaps, overload and EOD contention. Retain numerical/status/quality/evidence parity, source rights and normal both-platform/installed/artifact/review/publication/operational gates. Synthetic replay or source-only evidence cannot establish actual live-feed or production readiness.
