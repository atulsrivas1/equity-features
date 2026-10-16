# R12 release plan — continuous-market research extensions

Selected by the owner October16,2026 after R11 delivery. [E16#212](https://github.com/atulsrivas1/equity-features/issues/212), [milestone13](https://github.com/atulsrivas1/equity-features/milestone/13), [GOV024#414](https://github.com/atulsrivas1/equity-features/issues/414). This packet prepares original scope, not a runtime acceptance. GitHub Project is current authority.

## Starting evidence and scope

R11 is accepted: [whole-release receipt](https://github.com/atulsrivas1/equity-features/issues/195#issuecomment-6214256540), [release limits](R11_ACCEPTANCE.md). Canonical main3a3c24bf3220aad088665eedc5757daa1b36c537 and worker maina69ae9cfeb62730fc78705b4752b94c6f9438275 are the delivered baselines. The [fresh independent post-delivery review](reviews/R11_POST_DELIVERY_REVIEW.md) found no new actionable findings. It verified current closure/39main checks and passed118 exact-source pure methods including5new independent controls. Initial reviewer-harness3errors are preserved; no SQLite operation/native/build/install/qualification rerun or new physical guarantee. [Exact report and limits](reviews/R11_POST_DELIVERY_REVIEW.json) retain their own source identities. Accepted I/O pin18d86761aa3eebb7414e51e8fa2aba089717b5eb retains its original scope. Verify current default refs/owners before each mutation.

Preserve [continuous-market design](CONTINUOUS_MARKET_DESIGN.md), original five IDs and31 provisional complexity points. Five runtime stories plus GOV024 (3points) and epic make seven milestone members212–217/414. Points are complexity, not days. No delivery date is promised. R13+ and deferred provider/security work remain separate.

| Order | Story | Points | Readiness / accepted end state |
| --- | --- | --- | --- |
| 1 | [EQ111#213](https://github.com/atulsrivas1/equity-features/issues/213) | 5 | Accepted012/013/014/033/039/044/048 plus completed governance/review route; demonstrate finite24/7 day/week partitions and ConfigSpec identity; capability table separates reuse from real duration/feed/cross-venue gaps. No new type without evidence. |
| 2 | [EQ112#214](https://github.com/atulsrivas1/equity-features/issues/214) | 5 | Accepted111,006,033; freeze basis/premium, freeze deviation and reopen-gap equations, units, conversion/adjustment/cutoff/availability/precision/overflow rules with independent hand-derived fixtures before kernels. |
| 3 | [EQ113#215](https://github.com/atulsrivas1/equity-features/issues/215) | 8 | Accepted111/112/048; implement only demonstrated missing finite duration/feed-state contracts, or justified no-change for unnecessary session types; preserve old digests and explicit migration/admission. |
| 4 | [EQ114#216](https://github.com/atulsrivas1/equity-features/issues/216) | 8 | Accepted112/113/017/020/036; pure supplied-input batch kernels with per-leg readiness/quality and exact or declared-tolerance witnesses/top-K evidence. New namespaced IDs only after reviewed registry/package decision. |
| 5 | [EQ115#217](https://github.com/atulsrivas1/equity-features/issues/217) | 5 | Accepted111–114/045/048; fresh Windows/Linux wheel/SDist installed synthetic end-to-end examples, old-feature/compatibility/evidence parity, actual artifacts/publication and final release acceptance. |

All listed pre-R12 dependencies were freshly read Closed/Done during preparation. This is not readiness for the five new stories: the preceding R12 dependency, concrete reviewed pre-code packet and actual review route must also be satisfied.

## Architecture decisions owned by the stories

SessionSpec already admits caller-supplied finite int64 UTC bounds and disabled auctions. WindowSpec governs session-count slots; ConfigSpec schema1 requires exact existing component types. These source facts motivate EQ111 probes, not a claim that all duration/feed/cross-venue needs are already implemented. Reuse finite SessionSpec and independent supplied partitions where sufficient. Missing governed slots stay missing rather than compressed. Distinguish UTC duration from civil-day/DST partitions whose boundaries/calendars/holidays are supplied externally.

EQ112 owns reference mid/last/official-close choice, normalization/conversion evidence, per-leg age, backward alignment/ties and mismatch tolerances; weighting/coverage/denominators; freeze boundaries; first-known reopen and result availability. No future-nearest selection, interpolation, FX lookup or inferred economic/token equivalence. Freeze fractional mean/rational or explicitly rounded output semantics and overflow before code. An output about reopening is not available before both selected legs and their knowledge are admitted.

EQ113/114 must choose additive companion contracts versus explicit versioned evolution and the smallest distribution/registry placement after the gap and mathematics decisions. Do not insert a new subtype into ConfigSpec schema1, override the39accepted builtins or silently change old JSON/digests/equations. Keep calculations free of clocks, calendars, file/database/network I/O, scheduling and publication. Feed facts are supplied declarations, not authenticated availability or liquidity proof.

## Delivery gates

One runtime story active:111→112→113→114→115. Before each Ready, freeze literal inputs/oracles, source/API/version choices, open-decision resolution, provisional points, tests/docs and accepted end state. Apply every lifecycle stage and record actual review identities and limits. Relevant subsequent changes renew review and tests. A no-change result must prove which original criterion it satisfies; it cannot erase required feed-state or kernel work without an explicit scope decision.

Design/docs work receives scoped source/link/contract checks and current required CI/publication readback. Installable changes require source-bound reviewed builders and actual new Windows/Linux clean wheel/SDist cohorts, full source/metadata/license/dependency/RECORD/installed-origin maps, old-feature parity and current unexpired provider ZIP identities/digests/every-entry audit. Retained accepted evidence is reusable only through complete explicit input/archive equality in its own scope. Never replace a failed current gate with an older pass or rerun a failed unchanged source as a substitute for diagnosis.

Final release: all five original stories and GOV024 Done with linked acceptance; complete original criteria reconciliation and exact public-main source/artifacts/attribution review; finish epic lifecycle/close212, then verify exact seven Closed/Done/zero-open before closing milestone13. Merge alone is not acceptance. [Test strategy](R12_TEST_STRATEGY.md); [handoff](R12_AUTONOMOUS_HANDOFF.md).

## Boundaries

Synthetic supplied facts only. Provider/private datasets, paid APIs/models, trading/settlement/bridging, market-launch/liquidity/price-discovery claims, public hosting, registry-stable publication, account administration, destructive/recurring work and R7automation changes are not part of this release. No regulatory/security certification or physical whole-resource/hard-cleanup promise. Preserve all earlier accepted receipts, failed evidence and unrelated primary work.
