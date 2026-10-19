# R22 — Equity sessions, references and coverage closure

Owner-requested future planning. [Epic](https://github.com/atulsrivas1/equity-features/issues/503), [milestone](https://github.com/atulsrivas1/equity-features/milestone/26), [governance](https://github.com/atulsrivas1/equity-features/issues/502). Planned Backlog; live Project owns current status. No dates or runtime selection.

## EQ-164: Reconcile every equity family and worker to accepted or planned scope

[Issue](https://github.com/atulsrivas1/equity-features/issues/504). Dependencies: GOV032 planning publication.

Audit the complete frozen command register including shared/mixed candidates; retain explicit in-scope, out-of-scope, accepted-reuse and unresolved dispositions. Reconcile all 78 equity family groups, original core definitions and cross-layer gaps. Every in-scope output/worker must have a primary numbered implementation or accepted-reuse story and release, not only an umbrella audit. Newly discovered gaps require explicit follow-up stories before this story can be accepted.

Validation and acceptance: Independent inventory accounting, source-safe public manifest, no orphan/duplicate IDs, actual issue/milestone/Project/parent readback. Static reachability is not numerical completeness.

## EQ-165: Define and implement supplied session clock and trading-status semantics

[Issue](https://github.com/atulsrivas1/equity-features/issues/505). Dependencies: EQ-164.

Separate supplied trading/quoting/halt/resume/SSR events from inferred opening diagnostics. Specify session phase, early closes, elapsed/remaining session time, units, timezone/DST, unknown/stale state and ordered publisher/event transitions.

Validation and acceptance: Independent calendar/event fixtures, boundary equality, missing/contradictory status and reset/replay cases; qualified supported input bindings.

## EQ-166: Implement calendar-period levels and extended-session aggregates

[Issue](https://github.com/atulsrivas1/equity-features/issues/506). Dependencies: EQ-164.

Specify prior/current week/month/YTD boundaries, target inclusion and calendar extrema separately from fixed-count windows. Specify premarket/extended-hours extrema, volume, changes and regular open under supplied calendars/eligible facts.

Validation and acceptance: Independent holidays/week/month/year boundaries, early closes, DST, missing sessions, adjustments and phase eligibility; no fixed-day substitution.

## EQ-167: Implement explicit VWAP anchors and gap/opening-drive primitives

[Issue](https://github.com/atulsrivas1/equity-features/issues/507). Dependencies: EQ-164.

Specify caller-supplied causal anchor/reset identities and compatible VWAP reuse. Define scalar gap-fill/drive/crossing primitives separately from scanner/episode policies, with chronology, tie order and missing prior-reference behavior.

Validation and acceptance: Independent tiny trade/bar paths, anchor/denominator/reset/correction fixtures; no future-derived anchor at origin time; compare direct and supplied-series paths.

## EQ-168: Qualify supplied classifications and reference/action gates

[Issue](https://github.com/atulsrivas1/equity-features/issues/508). Dependencies: EQ-164.

Complete required supplied sector/industry/universe/action/reference checks under known-at, effective interval, revision and declared coverage. Reuse accepted contracts and existing R6 provider stories; do not fetch providers or infer missing history.

Validation and acceptance: Historical/current-only membership counterexamples, split/basis mismatches, missing/partial/observed-zero populations and cross-layer refusal parity.

## EQ-169: Qualify session and reference completion release

[Issue](https://github.com/atulsrivas1/equity-features/issues/509). Dependencies: EQ-165, EQ-166, EQ-167, EQ-168, EQ-163.

Audit exact selected R22 output/API/I-O/worker capability bindings, independent documentation and compatibility; preserve unresolved scope through new numbered stories rather than blanket completion.

Validation and acceptance: Both-platform installed artifacts, independent math/time/status fixtures, bounded end-to-end baselines, applicable reviews/CI/publication/readback; all selected children accepted.

## Cross-cutting release gates


Mandatory acceptance for this story:
- [ ] Freeze original formulas, units, timing, initialization, coverage, edge cases and supported capabilities before Ready; no private source formulas/thresholds copied without rights.
- [ ] Keep calculations pure; adapters own acquisition and workers own scheduling/persistence. Reuse existing qualified APIs; document no-change decisions.
- [ ] Independent synthetic/licensed expected fixtures and complete result/status/quality/evidence parity; explicit unsupported or missing inputs.
- [ ] Plan reuse of compatible inputs/intermediates, legal ordered state and bounded shared CPU/RAM/I-O/backend-thread budgets, configurable/full-machine policies. Measure defined workloads against credible baselines before speed claims; no invented SLA or fastest result.
- [ ] Update story/PR/formula/API/examples/decisions/release documents; complete required review, applicable tests/CI/installed artifacts, publication and actual readback before Done.

Future Backlog, unassigned, no due date. This planning does not start implementation, alter active R17/R18 sequencing, grant provider/private/live/hosting/admin/destructive/recurring operations or authorize future review. Existing deferred provider/LIVE/SEC stories remain authorities for their scopes.

All selected children must satisfy actual review/test/documentation/release acceptance. Complete no-orphan manifest with every in-scope family/worker tied to accepted scope or a separately numbered residual; unresolved scope cannot be hidden by closing the release.
