# R24 — Equity policies, lifecycle and complete worker integration

Owner-requested future planning. [Epic](https://github.com/atulsrivas1/equity-features/issues/517), [milestone](https://github.com/atulsrivas1/equity-features/milestone/28), [governance](https://github.com/atulsrivas1/equity-features/issues/502). Planned Backlog; live Project owns current status. No dates or runtime selection.

## EQ-176: Implement explicit equity scanner and watchlist catalogues

[Issue](https://github.com/atulsrivas1/equity-features/issues/518). Dependencies: EQ-164, EQ-163, EQ-169, EQ-175, EQ-102.

Inventory every selected equity scanner/watchlist identity; map to original public specifications and exact supplied feature/coverage dependencies. Reuse generic scan/rank APIs where valid; preserve matched/not-matched/unavailable and rule/version identity.

Validation and acceptance: One source-safe catalogue ledger per selected identity with independent positive/negative/unavailable/tie cases; missing formula/rights stays blocked, not silently dropped.

## EQ-177: Implement selected strategy context, tape summaries and score profiles

[Issue](https://github.com/atulsrivas1/equity-features/issues/519). Dependencies: EQ-164, EQ-175.

Define original versioned component normalization, weights, tape summaries, profile joins and level selection with per-output readiness. Keep generic math separate from product/source policy and distinguish evidence from narrative.

Validation and acceptance: Independent component/score examples, missing components, conflicting clocks/bases and unrelated-branch isolation; no future outcome input or performance claim from scores.

## EQ-178: Implement deterministic confirmation and candidate lifecycle

[Issue](https://github.com/atulsrivas1/equity-features/issues/520). Dependencies: EQ-164, EQ-176, EQ-177.

Freeze confirmation/persistence/reclaim/failure/episode transitions over supplied chronological evidence. Separate pure transition state from worker claims/retry/checkpoint persistence; specify identity, revision/reset, correction/replay and duplicate handling.

Validation and acceptance: Independent transition tables and adversarial histories, replay/correction idempotence, no duplicate alerts, serialized identity chain with independent-identity parity.

## EQ-179: Implement same-identity score and membership history

[Issue](https://github.com/atulsrivas1/equity-features/issues/521). Dependencies: EQ-164, EQ-177, EQ-178.

Define score trends and membership tenure/persistence over causal same-formula/config/scope histories; do not substitute raw price history or revised future knowledge for historical score facts.

Validation and acceptance: Independent prior-only trends/tenure examples, identity/config changes, missing sessions, late corrections and membership lifecycle boundaries.

## EQ-180: Qualify every admitted equity worker and I-O binding

[Issue](https://github.com/atulsrivas1/equity-features/issues/522). Dependencies: EQ-164, EQ-146, EQ-163, EQ-169, EQ-175, EQ-176, EQ-177, EQ-178, EQ-179.

For every equity and confirmed mixed/shared worker, link each output to accepted/new pure API, admitted source and sink, lifecycle/resource owner, installed worker route and exact dependencies. Reuse or consolidate commands without one-process-per-feature requirement. Audit acquisition, status, reference, history, publication, replay, maintenance and product-adapter roles. Out-of-scope options/product-only commands receive explicit exclusion or separate planning record. No private code/data migration without rights.

Validation and acceptance: Complete worker/role/output traceability with no unplanned in-scope records; synthetic end-to-end full-result/status/quality/evidence and refusal parity, fault/recovery/readback, bounded CPU/RAM/I-O and direct/current alternatives. Provider/live/product operation gates remain separate.

## EQ-181: Accept complete planned equity family and worker coverage

[Issue](https://github.com/atulsrivas1/equity-features/issues/523). Dependencies: EQ-180.

Independently reconcile the full selected family/worker ledger to Done accepted scopes and separately tracked residuals. Every selected implementation, adapter, worker, policy, compatibility/documentation and release gate must be evidenced; no acceptance from syntax census alone.

Validation and acceptance: Final no-orphan traceability; separate exact-head review/CI/both-platform installed artifacts and source/readback. Measure total time, throughput, memory and live latency only for declared supported workloads with result parity; retain all exclusions and failures.

## Cross-cutting release gates


Mandatory acceptance for this story:
- [ ] Freeze original formulas, units, timing, initialization, coverage, edge cases and supported capabilities before Ready; no private source formulas/thresholds copied without rights.
- [ ] Keep calculations pure; adapters own acquisition and workers own scheduling/persistence. Reuse existing qualified APIs; document no-change decisions.
- [ ] Independent synthetic/licensed expected fixtures and complete result/status/quality/evidence parity; explicit unsupported or missing inputs.
- [ ] Plan reuse of compatible inputs/intermediates, legal ordered state and bounded shared CPU/RAM/I-O/backend-thread budgets, configurable/full-machine policies. Measure defined workloads against credible baselines before speed claims; no invented SLA or fastest result.
- [ ] Update story/PR/formula/API/examples/decisions/release documents; complete required review, applicable tests/CI/installed artifacts, publication and actual readback before Done.

Future Backlog, unassigned, no due date. This planning does not start implementation, alter active R17/R18 sequencing, grant provider/private/live/hosting/admin/destructive/recurring operations or authorize future review. Existing deferred provider/LIVE/SEC stories remain authorities for their scopes.

All selected children must satisfy actual review/test/documentation/release acceptance. Complete no-orphan manifest with every in-scope family/worker tied to accepted scope or a separately numbered residual; unresolved scope cannot be hidden by closing the release.
