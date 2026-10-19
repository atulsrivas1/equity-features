# R23 — Remaining equity calculations, events and observed outcomes

Owner-requested future planning. [Epic](https://github.com/atulsrivas1/equity-features/issues/510), [milestone](https://github.com/atulsrivas1/equity-features/milestone/27), [governance](https://github.com/atulsrivas1/equity-features/issues/502). Planned Backlog; live Project owns current status. No dates or runtime selection.

## EQ-170: Implement remaining price channels and squeeze primitives

[Issue](https://github.com/atulsrivas1/equity-features/issues/511). Dependencies: EQ-164, EQ-139, EQ-149.

Specify Keltner and Donchian channels, selected pivot levels, price-band width percentile and Bollinger/Keltner squeeze primitives. Distinguish primitive arithmetic from source-specific thresholds/policies and freeze exact input/seed/alignment dependencies.

Validation and acceptance: Independent extrema/ATR/price-moment examples, zero ranges, short histories, target exclusion and separate readiness; no duplicate existing band/kernel implementation.

## EQ-171: Specify and implement admitted candle and structural-pattern evidence

[Issue](https://github.com/atulsrivas1/equity-features/issues/512). Dependencies: EQ-164.

Freeze a bounded explicit catalogue of candle/NR4/NR7 and selected geometric structures with original specifications, tolerances, deterministic ties, confirmation times and causal availability. No vague promise of all named chart patterns; omitted variants remain separately numbered.

Validation and acceptance: Independent positive/negative/boundary fixtures including repaint/lookahead counterexamples and correction replay; scope decision before Ready.

## EQ-172: Complete remaining equity statistical projections

[Issue](https://github.com/atulsrivas1/equity-features/issues/513). Dependencies: EQ-164, EQ-155, EQ-158.

Resolve uncovered up-session fractions, core-benchmark agreement/dispersion, scalar SMA/relative momentum comparisons, dollar-volume/up-volume projections, drawdown/distance and trailing trade/notional rate projections. Reuse accepted primitives; freeze per-output units, population, zero/tie and window rules.

Validation and acceptance: Literal small-array/tape expectations, missing anchors, nonmatching windows, observed zeros and target inclusion; explicit no-change reuse decisions and source-safe output manifest.

## EQ-173: Implement supplied point-in-time event and fundamental features

[Issue](https://github.com/atulsrivas1/equity-features/issues/514). Dependencies: EQ-164, EQ-168.

Define arithmetic over supplied earnings/analyst/insider/float/short-interest and scheduled corporate-event records, including counts and trading-session distance. Freeze required fields/units and coverage. Provider acquisition, text-model inference and rights remain separate existing/deferred scope.

Validation and acceptance: Independent synthetic records, revisions/known-at, missing collections versus zero, dilution/units and event-calendar boundary cases; no provider operation required.

## EQ-174: Extend observed-path outcomes without signal leakage

[Issue](https://github.com/atulsrivas1/equity-features/issues/515). Dependencies: EQ-164, EQ-103.

Extend existing endpoint labels only where missing: sampled-path MFE/MAE, declared barriers, time-to-target and selected candidate/large-print outcome binding. Define maturity, observation resolution, origin identity, full path coverage and embargo; no tick-extreme or profitability inference.

Validation and acceptance: Independent mature/immature paths and barriers, gaps, sampling/threshold ties, late corrections and unchanged origin signal bytes; labels never become current-feature prerequisites.

## EQ-175: Qualify remaining equity calculation release

[Issue](https://github.com/atulsrivas1/equity-features/issues/516). Dependencies: EQ-170, EQ-171, EQ-172, EQ-173, EQ-174, EQ-169.

Close selected new pure calculation/label scope with discoverable output manifest, correct source-independent packaging and qualified selected consumer bindings. Broader unselected patterns remain visible.

Validation and acceptance: Independent numerical/temporal fixtures, clean both-platform artifacts, direct/worker parity where declared, measured resource-bounded workloads and actual acceptance/readback.

## Cross-cutting release gates


Mandatory acceptance for this story:
- [ ] Freeze original formulas, units, timing, initialization, coverage, edge cases and supported capabilities before Ready; no private source formulas/thresholds copied without rights.
- [ ] Keep calculations pure; adapters own acquisition and workers own scheduling/persistence. Reuse existing qualified APIs; document no-change decisions.
- [ ] Independent synthetic/licensed expected fixtures and complete result/status/quality/evidence parity; explicit unsupported or missing inputs.
- [ ] Plan reuse of compatible inputs/intermediates, legal ordered state and bounded shared CPU/RAM/I-O/backend-thread budgets, configurable/full-machine policies. Measure defined workloads against credible baselines before speed claims; no invented SLA or fastest result.
- [ ] Update story/PR/formula/API/examples/decisions/release documents; complete required review, applicable tests/CI/installed artifacts, publication and actual readback before Done.

Future Backlog, unassigned, no due date. This planning does not start implementation, alter active R17/R18 sequencing, grant provider/private/live/hosting/admin/destructive/recurring operations or authorize future review. Existing deferred provider/LIVE/SEC stories remain authorities for their scopes.

All selected children must satisfy actual review/test/documentation/release acceptance. Complete no-orphan manifest with every in-scope family/worker tied to accepted scope or a separately numbered residual; unresolved scope cannot be hidden by closing the release.
