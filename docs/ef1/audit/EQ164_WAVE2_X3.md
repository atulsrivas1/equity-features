# EQ164 wave 2, story X3: row-level operand lists for the 24 NEEDS_OPERAND_PRODUCER rows

October 22, 2026. Audit findings only, on `origin/main` at `d04e820`. Every statement below is an adjudicated finding or a proposed answer, not a decision and not acceptance. Full EQ164 stays open, no row is Ready, and no tracker issue was created or edited. Operand identities come from read-only private operand and source material; only opaque ids (F####, S####) appear here, and no private names, formulas, thresholds or values are reproduced. The machine-readable record is [EQ164_WAVE2_X3.json](EQ164_WAVE2_X3.json).

Inputs: [A](EQ164_SELECTED_A.json), [B](EQ164_SELECTED_B.json), [C](EQ164_SELECTED_C.json), [wave 1 decisions](EQ164_WAVE1_DECISIONS.md), the [route coverage](../../plans/equity-audit-route-coverage.json) and [selected components](../../plans/equity-selected-scope-components.json) plans, [NUMBERED_LAYER_OWNERS](../NUMBERED_LAYER_OWNERS.md), [DELIVERY_LEDGER](../DELIVERY_LEDGER.md), [AUDIT_ROUTE_PUBLICATION](../AUDIT_ROUTE_PUBLICATION.md) and [OWNERSHIP_RECONCILIATION](../OWNERSHIP_RECONCILIATION.md). Public selected manifest SHA256 `b76c50912bd015dcd3a69fa3617fd3527899db20700bd6ca6fe6ae8f88cbbc17`.

## Method and vocabulary

Public lexical bridges are empty for all 24 rows, so the operand sets were derived from the private operand and source profiles and then expressed as opaque F#### fields plus a few derived operands and caller parameters. Each operand carries one status:

- `DELIVERED_ON_MAIN`: a producer or carrier exists on main at the base commit; compatibility with the original profile is not proved.
- `PLANNED_NUMBERED`: a numbered story owns it; not delivered or not yet mapped.
- `PROPOSED_NEW_STORY`: needs a story that wave 1 proposed and that does not exist.
- `UNCOVERED_GAP`: no producer found or proposed.
- `PARAMETER_ONLY`: caller parameter; not a producer gap; values withheld.

Confidence is per operand (high, medium, low-medium, low). Evidence classes: `private_source_static_read` (static read of private profiles and source, not run), `public_plan_and_issue_text`, `delivery_ledger_and_tree_at_base` (file and feature-id presence on main, nothing re-run). Nothing was executed or numerically compared.

## Summary

24 rows, 208 operand entries (153 producer-supplied, 55 parameter-only). Producer-supplied entries by status:

| Status | Entries | Distinct operands |
| --- | --- | --- |
| DELIVERED_ON_MAIN | 92 | 12 |
| PLANNED_NUMBERED | 32 | 8 |
| PROPOSED_NEW_STORY | 29 | 3 |
| UNCOVERED_GAP | 0 | 0 |
| PARAMETER_ONLY | 55 | 7 |

Wave 1 could not recover per-consumer operands. Now all 24 rows have an operand list and no operand is an `UNCOVERED_GAP`. What remains is smaller and specific. Delivered entries are candidates whose compatibility with the original profile is still unproved.

### Remaining operand gaps by missing producer kind

Gap = any entry that is not DELIVERED_ON_MAIN (61 entries).

| Missing producer kind | Entries | Distinct operands |
| --- | --- | --- |
| No story exists (proposed new story) | 29 | OP-COHORT-RANK, OP-ELIG-RANK, OP-LEVEL |
| Story exists, output not enumerated | 8 | OP-ELIG-BREADTH, OP-OBS-BREADTH |
| Numbered story, not delivered | 8 | F0193, F0251, OP-TRAILING-WINDOW |
| Representation mapping pending (layer story) | 16 | F0186, F0259, F0338 |

### Per release and story

| Release | Producer | Status | Entries |
| --- | --- | --- | --- |
| EF4 | #19 (route, closed); layer #613 | DELIVERED_ON_MAIN | 16 |
| EF4 | #492 | PLANNED_NUMBERED | 1 |
| EF1 | #506 (route); layer #570 | DELIVERED_ON_MAIN | 29 |
| EF1 | #507 (route); layer #570 | DELIVERED_ON_MAIN | 6 |
| EF4 | #513 (route) | PLANNED_NUMBERED | 6 |
| EF4 | #513 (route); upstream #492 | PLANNED_NUMBERED | 1 |
| EF1 | #570 (route) | DELIVERED_ON_MAIN | 14 |
| EF1 | #570 (route) | PLANNED_NUMBERED | 1 |
| EF1 | #570 (route); #508 | DELIVERED_ON_MAIN | 6 |
| EF4 | #570 (route); #513 | PLANNED_NUMBERED | 6 |
| EF1 | #570 (route, in progress) | PLANNED_NUMBERED | 9 |
| EF3 | #598 observed companion | PLANNED_NUMBERED | 4 |
| EF3 | #598 observed companion (per-member eligibility) | PLANNED_NUMBERED | 4 |
| EF2 | core history.atr; #472 interval-aware variant | DELIVERED_ON_MAIN | 3 |
| EF2 | core history.prior_high; #473/#483 numbered | DELIVERED_ON_MAIN | 9 |
| EF2 | core history.prior_low; #473/#483 numbered | DELIVERED_ON_MAIN | 9 |
| EF2 | proposed new EF2 retracement-level story | PROPOSED_NEW_STORY | 9 |
| EF8 | proposed new EF8 cohort-normalization story | PROPOSED_NEW_STORY | 10 |
| EF8 | proposed new EF8 cohort-normalization story (population admission step) | PROPOSED_NEW_STORY | 10 |

### Proposed new stories this implies

- **N1, Narrow caller-parameterized retracement-level producer (EF2)**: Pure arithmetic over a prior-window extrema pair and a caller ratio; extrema from delivered history.prior_high/prior_low or numbered #473/#483. Rows: S0276, S0277, S0278, S0279, S0280, S0281, S0282, S0283, S0284. Origin: wave 1 decision A1. Status: proposed, not created.
- **N2, Current-observed-cohort normalization and rank producer (whole cohort and supplied group, with admission step) (EF8)**: Includes the population admission step OP-ELIG-RANK; closed #102 reuse stays unproved; not #489 (prior-only history). Rows: S0090, S0091, S0092, S0093, S0094, S0095, S0096, S0097, S0098, S0099. Origin: wave 1 decision C1. Status: proposed, not created.
- **A-598, Amend #598 with an observed-population output profile (or number a narrow companion) (EF3)**: Output list in answer B5; an amendment of an existing numbered story, not a new numbered producer, unless the owner prefers a companion. Rows: S0003, S0004, S0005, S0006. Origin: wave 1 decision D-POP. Status: proposed amendment, owner decision.

No other new story is implied by these rows. Pure arithmetic of the policy rows (proximity, crossing, tail membership, regime cut-offs, scores) stays with #518 as policy; the operand producers above are the missing parts.

### Incidental findings

- Delivery of history.prior_high, history.prior_low and history.atr is established from the implemented-feature catalog and README at the base commit; wave 1 reported delivery of the extrema operand as not established.
- DELIVERY_LEDGER section 1 lists the supplied-close absolute BPS and tolerance comparison as not found; at the base commit the module and feature ids exist (#639). The ledger row is stale.
- Route owner and delivered module disagree for F0206: the route names #507, the delivered prior-close return is in the #506 period module (see attribution rule A5).
- A private source profile names #489 as candidate numerical owner of the cohort rank; #489 is prior-only history, so that candidate does not hold for a current-cohort rank.

## Proposed answers to the open wave 1 items

### A4

Question: Which #513 profile supplies F0702, and how do F0702 and the #492 profile link?

Proposed answer: F0702 has no independent producer. It is a value copy of F0193, which the route already assigns to the #513 trailing-window rate projection (share-rate variant of the raw rolling return/share-rate/rate-difference role). The #513 rate projection divides a window sum by the window length and consumes the #492 plain rolling trade-window volume profile (not the tick-signed profile); #513 already lists #492 as a prerequisite. Recommend recording F0702 as an alias of F0193 (duplicate profile, identical value) and naming it as the supplied raw rate operand of #626.

Evidence class: private_source_static_read + public_plan_and_issue_text. Confidence: medium-high. Residual: window-end convention and empty-window behavior are not frozen; EF4 producer versus EF3 consumer: per wave 1 B7 the value enters #626 as a supplied operand through I/O, so no EF4 production edge for EF3 acceptance. Status: proposed answer, not a decision.

### B2

Question: What do F0700, F0701 and F0721 carry and who produces them?

Proposed answer: F0700 is the entity identity echoed from the input observation. F0701 is the input observation event clock echoed from the input; it is also an ordering operand (an update applies only if its clock advances for the entity and session). F0721 is the nested session-summary aggregate holding the computed session-summary outputs F0690 to F0699. So F0700 and F0701 are supplied facts: #611 maps them, #626 must name them as input identity and ordering operands in its contract. F0721 is a computed #626 output group that #611 only envelopes. Proposed re-attribution of the primary owner: F0721 to #626; F0700 and F0701 to supplied-operand status with #611 as mapping and #626 as consumer. The serialized carrier F0179 stays with #570.

Evidence class: private_source_static_read + public_plan_and_issue_text. Confidence: medium-high for F0700 and F0701; medium for F0721. Residual: #626 contract has not stated whether the session-summary group is emitted per update or at session end; reset-on-new-session semantics belong to the #626 contract. Status: proposed answer, not a decision.

### B5

Question: Which observed-population companion outputs does #598 need, and who produces their operands?

Proposed answer: Seven draft outputs, kept under distinct observed-population names so denominators are never mixed with declared-universe outputs: (1) qualifying observed member count; (2) observed advancing member count (strictly positive change); (3) observed advance fraction = (2)/(1), which is not the advance/decline ratio because non-advancing members are not split; (4) to (6) the same three per supplied group label together with group size; (7) a per-cohort and per-group coverage record (observed members, no expected population). Regime classification, cut-offs, score scaling and projection of the cohort result onto each member stay in #518. Operand producers: per-member change F0206 (delivered candidates, #507 route), eligibility inputs F0150 and F0161 with caller floors (delivered candidates), group label F0255 (delivered #508 candidate), identity F0137 (delivered). The consumer counts duplicates of an identity while the rank consumers keep one value per identity, so duplicate-identity handling must be frozen once. Placement: either retitle and extend #598 with a separately versioned observed-population profile or number a narrow companion story; this is an owner decision.

Evidence class: private_source_static_read + public_plan_and_issue_text. Confidence: medium for the output list; low-medium for the placement. Residual: D-POP owner decision on placement; whether a declared-universe profile may later reuse the same arithmetic. Status: proposed answer, not a decision.

### B6

Question: Which adaptive outputs do S0336, S0337 and S0357 consume?

Proposed answer: All three read the session-summary group F0721 (carried by F0179) and the session change F0206 for direction, plus caller thresholds. S0336 consumes the acceleration-diagnostic episode count F0695 and peak score F0696. S0337 consumes the baseline-availability flag F0699, the trigger count F0694 and the composite peak score F0690. S0357 consumes F0699 and the peak short-window relative volume F0692. Transitive #626 inputs: the supplied raw rate F0702 (all three families through the minimum-rate gate and the acceleration diagnostic), the relative-volume window values and availability flags F0208 to F0211 (route #490, EF3), F0186 and F0700. Proposed output-level edges: #518 to #626 for exactly these six outputs plus the envelope; the #519 optional edge covers the same set only if #519 re-derives them, otherwise it is unnecessary for these three rows. The private source profile for these rows names #490 as numerical owner; it predates #626 and is superseded by decision D-FLIP.

| Row | Consumed adaptive outputs and carriers |
| --- | --- |
| S0336 | F0721, F0695, F0696, F0206, F0179 |
| S0337 | F0721, F0699, F0694, F0690, F0206, F0179 |
| S0357 | F0721, F0699, F0692, F0206, F0179 |

Transitive #626 inputs: F0702, F0208, F0209, F0210, F0211, F0186, F0700.

Evidence class: private_source_static_read + public_plan_and_issue_text. Confidence: medium-high for the consumed outputs; medium for the transitive list. Residual: thresholds are caller parameters and are not defaulted; #626 contract must state when the session summary is final. Status: proposed answer, not a decision.

## Rows still undecidable, and why

- S0276, S0277, S0278, S0279, S0280, S0281, S0282, S0283, S0284: Operands resolved. Still open: which close variant the consumers read (the source row has several), level-equality tie rule, and the parameter values, which must be supplied rather than defaulted.
- S0003, S0004, S0005, S0006: Operands resolved. Placement of the observed-population outputs (D-POP) and duplicate-identity treatment need an owner decision.
- S0090, S0091, S0092, S0093, S0094, S0095, S0096, S0097, S0098, S0099: Operands resolved. Rank convention, ties, non-finite handling and whether closed #102 can be reused are unproved; N2 is needed unless reuse is proved.
- F0702: Operand chain resolved. Window-end convention and empty-window behavior are not frozen by any contract.

No row is fully undecidable at the operand level; each has residual contract-level items that no static read can settle.

## Row-level operand lists

Each line: operand id, role, status, producer, confidence. Operand ids starting `OP-` are derived operands, `PARAM-` are caller parameters. Full detail is in the JSON.

### F0702 (supplied-rate copy, slice A)

Finding: Operand chain resolved: F0702 has no independent producer. It equals F0193, whose planned owner is the #513 trailing rate projection, which consumes the #492 rolling trade window profile (answer A4).

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0193 | value source: F0702 is a pass-through copy of this rate (same value at each source site read) | PLANNED_NUMBERED | #513 (route); upstream #492 (EF4) | medium |
| OP-TRAILING-WINDOW | upstream window sum feeding the rate | PLANNED_NUMBERED | #492 (EF4) | medium |
| F0186 | window-end clock of the rate | PLANNED_NUMBERED | #570 (route) (EF1) | medium-low |

Residual: trailing-window end convention and empty-window behavior are not frozen in any contract.

### S0276 (retracement proximity (neutral location), slice A)

Finding: The nine wave 1 rows are three operand families, not nine identical routes. Proximity rows need the range-average operand and the current high/low; they do not use the previous close as a crossing operand.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0150 | current close compared with the level | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0338 | supplied bar history (prior bars, previous close) | PLANNED_NUMBERED | #570 (route, in progress) (EF1) | medium-low |
| OP-PRIOR-HIGH | upper end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_high; #473/#483 numbered (EF2) | medium |
| OP-PRIOR-LOW | lower end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_low; #473/#483 numbered (EF2) | medium |
| OP-LEVEL | retracement level consumed by the predicate and score | PROPOSED_NEW_STORY | proposed new EF2 retracement-level story (EF2) | medium |
| PARAM-RATIO | ratio for this row only | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-HISTORY-GATE | history length gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| F0148 | current high in the range-average sequence | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0149 | current low in the range-average sequence | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| OP-RANGE-AVG | sets the proximity tolerance | DELIVERED_ON_MAIN | core history.atr; #472 interval-aware variant (EF2) | medium-low |
| PARAM-TOL | tolerance floor and multiple | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: which close variant of the F0150 family is read; ratio and tolerance values are parameters to be supplied, not defaulted.

### S0277 (retracement proximity (neutral location), slice A)

Finding: The nine wave 1 rows are three operand families, not nine identical routes. Proximity rows need the range-average operand and the current high/low; they do not use the previous close as a crossing operand.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0150 | current close compared with the level | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0338 | supplied bar history (prior bars, previous close) | PLANNED_NUMBERED | #570 (route, in progress) (EF1) | medium-low |
| OP-PRIOR-HIGH | upper end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_high; #473/#483 numbered (EF2) | medium |
| OP-PRIOR-LOW | lower end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_low; #473/#483 numbered (EF2) | medium |
| OP-LEVEL | retracement level consumed by the predicate and score | PROPOSED_NEW_STORY | proposed new EF2 retracement-level story (EF2) | medium |
| PARAM-RATIO | ratio for this row only | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-HISTORY-GATE | history length gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| F0148 | current high in the range-average sequence | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0149 | current low in the range-average sequence | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| OP-RANGE-AVG | sets the proximity tolerance | DELIVERED_ON_MAIN | core history.atr; #472 interval-aware variant (EF2) | medium-low |
| PARAM-TOL | tolerance floor and multiple | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: which close variant of the F0150 family is read; ratio and tolerance values are parameters to be supplied, not defaulted.

### S0278 (retracement proximity (neutral location), slice A)

Finding: The nine wave 1 rows are three operand families, not nine identical routes. Proximity rows need the range-average operand and the current high/low; they do not use the previous close as a crossing operand.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0150 | current close compared with the level | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0338 | supplied bar history (prior bars, previous close) | PLANNED_NUMBERED | #570 (route, in progress) (EF1) | medium-low |
| OP-PRIOR-HIGH | upper end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_high; #473/#483 numbered (EF2) | medium |
| OP-PRIOR-LOW | lower end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_low; #473/#483 numbered (EF2) | medium |
| OP-LEVEL | retracement level consumed by the predicate and score | PROPOSED_NEW_STORY | proposed new EF2 retracement-level story (EF2) | medium |
| PARAM-RATIO | ratio for this row only | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-HISTORY-GATE | history length gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| F0148 | current high in the range-average sequence | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0149 | current low in the range-average sequence | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| OP-RANGE-AVG | sets the proximity tolerance | DELIVERED_ON_MAIN | core history.atr; #472 interval-aware variant (EF2) | medium-low |
| PARAM-TOL | tolerance floor and multiple | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: which close variant of the F0150 family is read; ratio and tolerance values are parameters to be supplied, not defaulted.

### S0279 (retracement crossing up (reclaim), slice A)

Finding: Crossing rows need the previous-bar close (from F0338) and the current close against the level; no range-average operand.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0150 | current close compared with the level | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0338 | supplied bar history (prior bars, previous close) | PLANNED_NUMBERED | #570 (route, in progress) (EF1) | medium-low |
| OP-PRIOR-HIGH | upper end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_high; #473/#483 numbered (EF2) | medium |
| OP-PRIOR-LOW | lower end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_low; #473/#483 numbered (EF2) | medium |
| OP-LEVEL | retracement level consumed by the predicate and score | PROPOSED_NEW_STORY | proposed new EF2 retracement-level story (EF2) | medium |
| PARAM-RATIO | ratio for this row only | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-HISTORY-GATE | history length gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: close variant; level-equality tie rule belongs to the contract.

### S0280 (retracement crossing up (reclaim), slice A)

Finding: Crossing rows need the previous-bar close (from F0338) and the current close against the level; no range-average operand.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0150 | current close compared with the level | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0338 | supplied bar history (prior bars, previous close) | PLANNED_NUMBERED | #570 (route, in progress) (EF1) | medium-low |
| OP-PRIOR-HIGH | upper end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_high; #473/#483 numbered (EF2) | medium |
| OP-PRIOR-LOW | lower end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_low; #473/#483 numbered (EF2) | medium |
| OP-LEVEL | retracement level consumed by the predicate and score | PROPOSED_NEW_STORY | proposed new EF2 retracement-level story (EF2) | medium |
| PARAM-RATIO | ratio for this row only | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-HISTORY-GATE | history length gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: close variant; level-equality tie rule belongs to the contract.

### S0281 (retracement crossing up (reclaim), slice A)

Finding: Crossing rows need the previous-bar close (from F0338) and the current close against the level; no range-average operand.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0150 | current close compared with the level | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0338 | supplied bar history (prior bars, previous close) | PLANNED_NUMBERED | #570 (route, in progress) (EF1) | medium-low |
| OP-PRIOR-HIGH | upper end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_high; #473/#483 numbered (EF2) | medium |
| OP-PRIOR-LOW | lower end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_low; #473/#483 numbered (EF2) | medium |
| OP-LEVEL | retracement level consumed by the predicate and score | PROPOSED_NEW_STORY | proposed new EF2 retracement-level story (EF2) | medium |
| PARAM-RATIO | ratio for this row only | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-HISTORY-GATE | history length gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: close variant; level-equality tie rule belongs to the contract.

### S0282 (retracement crossing down (rejection), slice A)

Finding: Mirror of the crossing-up family with the opposite comparison direction; same operand set.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0150 | current close compared with the level | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0338 | supplied bar history (prior bars, previous close) | PLANNED_NUMBERED | #570 (route, in progress) (EF1) | medium-low |
| OP-PRIOR-HIGH | upper end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_high; #473/#483 numbered (EF2) | medium |
| OP-PRIOR-LOW | lower end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_low; #473/#483 numbered (EF2) | medium |
| OP-LEVEL | retracement level consumed by the predicate and score | PROPOSED_NEW_STORY | proposed new EF2 retracement-level story (EF2) | medium |
| PARAM-RATIO | ratio for this row only | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-HISTORY-GATE | history length gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: close variant; level-equality tie rule belongs to the contract.

### S0283 (retracement crossing down (rejection), slice A)

Finding: Mirror of the crossing-up family with the opposite comparison direction; same operand set.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0150 | current close compared with the level | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0338 | supplied bar history (prior bars, previous close) | PLANNED_NUMBERED | #570 (route, in progress) (EF1) | medium-low |
| OP-PRIOR-HIGH | upper end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_high; #473/#483 numbered (EF2) | medium |
| OP-PRIOR-LOW | lower end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_low; #473/#483 numbered (EF2) | medium |
| OP-LEVEL | retracement level consumed by the predicate and score | PROPOSED_NEW_STORY | proposed new EF2 retracement-level story (EF2) | medium |
| PARAM-RATIO | ratio for this row only | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-HISTORY-GATE | history length gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: close variant; level-equality tie rule belongs to the contract.

### S0284 (retracement crossing down (rejection), slice A)

Finding: Mirror of the crossing-up family with the opposite comparison direction; same operand set.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0150 | current close compared with the level | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0338 | supplied bar history (prior bars, previous close) | PLANNED_NUMBERED | #570 (route, in progress) (EF1) | medium-low |
| OP-PRIOR-HIGH | upper end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_high; #473/#483 numbered (EF2) | medium |
| OP-PRIOR-LOW | lower end of the range the level is built from | DELIVERED_ON_MAIN | core history.prior_low; #473/#483 numbered (EF2) | medium |
| OP-LEVEL | retracement level consumed by the predicate and score | PROPOSED_NEW_STORY | proposed new EF2 retracement-level story (EF2) | medium |
| PARAM-RATIO | ratio for this row only | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-HISTORY-GATE | history length gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: close variant; level-equality tie rule belongs to the contract.

### S0003 (observed-population breadth regime (whole cohort), slice B)

Finding: Public bridges were empty; the private profile gives the operand set. The consumer counts positive changes over all observed qualifying members, which is not the declared-universe advance/decline ratio.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0206 | per-member change whose sign is counted | DELIVERED_ON_MAIN | #507 (route); layer #570 (EF1) | low-medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-BREADTH | observed-cohort membership | PLANNED_NUMBERED | #598 observed companion (per-member eligibility) (EF3) | low |
| F0137 | member identity (duplicate handling) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| OP-OBS-BREADTH | counts and fraction over the observed cohort | PLANNED_NUMBERED | #598 observed companion (EF3) | low-medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-REGIME-CUTS | cut-offs applied to the fraction (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: observed-versus-declared population semantics need an owner decision (D-POP); duplicate-identity treatment must be frozen.

### S0004 (observed-population breadth regime (whole cohort), slice B)

Finding: Public bridges were empty; the private profile gives the operand set. The consumer counts positive changes over all observed qualifying members, which is not the declared-universe advance/decline ratio.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0206 | per-member change whose sign is counted | DELIVERED_ON_MAIN | #507 (route); layer #570 (EF1) | low-medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-BREADTH | observed-cohort membership | PLANNED_NUMBERED | #598 observed companion (per-member eligibility) (EF3) | low |
| F0137 | member identity (duplicate handling) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| OP-OBS-BREADTH | counts and fraction over the observed cohort | PLANNED_NUMBERED | #598 observed companion (EF3) | low-medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-REGIME-CUTS | cut-offs applied to the fraction (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: observed-versus-declared population semantics need an owner decision (D-POP); duplicate-identity treatment must be frozen.

### S0005 (observed-population breadth regime (sector-grouped), slice B)

Finding: Public bridges were empty; the private profile gives the operand set. The consumer counts positive changes over all observed qualifying members, which is not the declared-universe advance/decline ratio.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0206 | per-member change whose sign is counted | DELIVERED_ON_MAIN | #507 (route); layer #570 (EF1) | low-medium |
| F0255 | group label for the sector-grouped fraction | DELIVERED_ON_MAIN | #570 (route); #508 (EF1) | low-medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-BREADTH | observed-cohort membership | PLANNED_NUMBERED | #598 observed companion (per-member eligibility) (EF3) | low |
| F0137 | member identity (duplicate handling) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| OP-OBS-BREADTH | counts and fraction over the observed cohort per supplied group | PLANNED_NUMBERED | #598 observed companion (EF3) | low-medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-REGIME-CUTS | cut-offs applied to the fraction (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-GROUP-GATE | group-size gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: observed-versus-declared population semantics need an owner decision (D-POP); duplicate-identity treatment must be frozen.

### S0006 (observed-population breadth regime (sector-grouped), slice B)

Finding: Public bridges were empty; the private profile gives the operand set. The consumer counts positive changes over all observed qualifying members, which is not the declared-universe advance/decline ratio.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0206 | per-member change whose sign is counted | DELIVERED_ON_MAIN | #507 (route); layer #570 (EF1) | low-medium |
| F0255 | group label for the sector-grouped fraction | DELIVERED_ON_MAIN | #570 (route); #508 (EF1) | low-medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-BREADTH | observed-cohort membership | PLANNED_NUMBERED | #598 observed companion (per-member eligibility) (EF3) | low |
| F0137 | member identity (duplicate handling) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| OP-OBS-BREADTH | counts and fraction over the observed cohort per supplied group | PLANNED_NUMBERED | #598 observed companion (EF3) | low-medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-REGIME-CUTS | cut-offs applied to the fraction (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-GROUP-GATE | group-size gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: observed-versus-declared population semantics need an owner decision (D-POP); duplicate-identity treatment must be frozen.

### S0090 (cohort rank, dollar-volume cohort, bottom tail, slice C)

Finding: Cohort values come from three distinct producers depending on the family; the common step is a current-cohort rank with no numbered producer. A private candidate owner (#489) is prior-only history and is not a match.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0152 | cohort value being ranked | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| F0137 | member identity (tie order, one value per identity) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-RANK | observed-cohort membership | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (population admission step) (EF8) | low |
| OP-COHORT-RANK | rank position of each member within the cohort | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (EF8) | medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-TAIL-CUT | tail cut (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: exact reuse of closed #102 is unproved; rank convention, tie and non-finite handling are contract items.

### S0091 (cohort rank, dollar-volume cohort, top tail, slice C)

Finding: Cohort values come from three distinct producers depending on the family; the common step is a current-cohort rank with no numbered producer. A private candidate owner (#489) is prior-only history and is not a match.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0152 | cohort value being ranked | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| F0137 | member identity (tie order, one value per identity) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-RANK | observed-cohort membership | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (population admission step) (EF8) | low |
| OP-COHORT-RANK | rank position of each member within the cohort | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (EF8) | medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-TAIL-CUT | tail cut (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: exact reuse of closed #102 is unproved; rank convention, tie and non-finite handling are contract items.

### S0092 (cohort rank, industry-grouped excess-return cohort, bottom tail, slice C)

Finding: Cohort values come from three distinct producers depending on the family; the common step is a current-cohort rank with no numbered producer. A private candidate owner (#489) is prior-only history and is not a match.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0251 | cohort value being ranked | PLANNED_NUMBERED | #513 (route) (EF4) | medium |
| F0137 | member identity (tie order, one value per identity) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| F0259 | admission marker: member enters only when present | PLANNED_NUMBERED | #570 (route); #513 (EF4) | low |
| F0256 | group label partitioning the cohort | DELIVERED_ON_MAIN | #570 (route); #508 (EF1) | low-medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-RANK | observed-cohort membership | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (population admission step) (EF8) | low |
| OP-COHORT-RANK | rank position of each member within the cohort group | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (EF8) | medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-TAIL-CUT | tail cut (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-GROUP-GATE | group-size gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: exact reuse of closed #102 is unproved; rank convention, tie and non-finite handling are contract items.

### S0093 (cohort rank, industry-grouped excess-return cohort, top tail, slice C)

Finding: Cohort values come from three distinct producers depending on the family; the common step is a current-cohort rank with no numbered producer. A private candidate owner (#489) is prior-only history and is not a match.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0251 | cohort value being ranked | PLANNED_NUMBERED | #513 (route) (EF4) | medium |
| F0137 | member identity (tie order, one value per identity) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| F0259 | admission marker: member enters only when present | PLANNED_NUMBERED | #570 (route); #513 (EF4) | low |
| F0256 | group label partitioning the cohort | DELIVERED_ON_MAIN | #570 (route); #508 (EF1) | low-medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-RANK | observed-cohort membership | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (population admission step) (EF8) | low |
| OP-COHORT-RANK | rank position of each member within the cohort group | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (EF8) | medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-TAIL-CUT | tail cut (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-GROUP-GATE | group-size gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: exact reuse of closed #102 is unproved; rank convention, tie and non-finite handling are contract items.

### S0094 (cohort rank, sector-grouped excess-return cohort, bottom tail, slice C)

Finding: Cohort values come from three distinct producers depending on the family; the common step is a current-cohort rank with no numbered producer. A private candidate owner (#489) is prior-only history and is not a match.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0251 | cohort value being ranked | PLANNED_NUMBERED | #513 (route) (EF4) | medium |
| F0137 | member identity (tie order, one value per identity) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| F0259 | admission marker: member enters only when present | PLANNED_NUMBERED | #570 (route); #513 (EF4) | low |
| F0255 | group label partitioning the cohort | DELIVERED_ON_MAIN | #570 (route); #508 (EF1) | low-medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-RANK | observed-cohort membership | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (population admission step) (EF8) | low |
| OP-COHORT-RANK | rank position of each member within the cohort group | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (EF8) | medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-TAIL-CUT | tail cut (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-GROUP-GATE | group-size gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: exact reuse of closed #102 is unproved; rank convention, tie and non-finite handling are contract items.

### S0095 (cohort rank, sector-grouped excess-return cohort, top tail, slice C)

Finding: Cohort values come from three distinct producers depending on the family; the common step is a current-cohort rank with no numbered producer. A private candidate owner (#489) is prior-only history and is not a match.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0251 | cohort value being ranked | PLANNED_NUMBERED | #513 (route) (EF4) | medium |
| F0137 | member identity (tie order, one value per identity) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| F0259 | admission marker: member enters only when present | PLANNED_NUMBERED | #570 (route); #513 (EF4) | low |
| F0255 | group label partitioning the cohort | DELIVERED_ON_MAIN | #570 (route); #508 (EF1) | low-medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-RANK | observed-cohort membership | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (population admission step) (EF8) | low |
| OP-COHORT-RANK | rank position of each member within the cohort group | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (EF8) | medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-TAIL-CUT | tail cut (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-GROUP-GATE | group-size gate | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: exact reuse of closed #102 is unproved; rank convention, tie and non-finite handling are contract items.

### S0096 (cohort rank, session-change cohort, bottom tail, slice C)

Finding: Cohort values come from three distinct producers depending on the family; the common step is a current-cohort rank with no numbered producer. A private candidate owner (#489) is prior-only history and is not a match.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0206 | cohort value being ranked | DELIVERED_ON_MAIN | #507 (route); layer #570 (EF1) | low-medium |
| F0137 | member identity (tie order, one value per identity) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-RANK | observed-cohort membership | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (population admission step) (EF8) | low |
| OP-COHORT-RANK | rank position of each member within the cohort | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (EF8) | medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-TAIL-CUT | tail cut (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: exact reuse of closed #102 is unproved; rank convention, tie and non-finite handling are contract items.

### S0097 (cohort rank, session-change cohort, top tail, slice C)

Finding: Cohort values come from three distinct producers depending on the family; the common step is a current-cohort rank with no numbered producer. A private candidate owner (#489) is prior-only history and is not a match.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0206 | cohort value being ranked | DELIVERED_ON_MAIN | #507 (route); layer #570 (EF1) | low-medium |
| F0137 | member identity (tie order, one value per identity) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-RANK | observed-cohort membership | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (population admission step) (EF8) | low |
| OP-COHORT-RANK | rank position of each member within the cohort | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (EF8) | medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-TAIL-CUT | tail cut (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: exact reuse of closed #102 is unproved; rank convention, tie and non-finite handling are contract items.

### S0098 (cohort rank, market-wide excess-return cohort, bottom tail, slice C)

Finding: Cohort values come from three distinct producers depending on the family; the common step is a current-cohort rank with no numbered producer. A private candidate owner (#489) is prior-only history and is not a match.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0251 | cohort value being ranked | PLANNED_NUMBERED | #513 (route) (EF4) | medium |
| F0137 | member identity (tie order, one value per identity) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| F0259 | admission marker: member enters only when present | PLANNED_NUMBERED | #570 (route); #513 (EF4) | low |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-RANK | observed-cohort membership | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (population admission step) (EF8) | low |
| OP-COHORT-RANK | rank position of each member within the cohort | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (EF8) | medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-TAIL-CUT | tail cut (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: exact reuse of closed #102 is unproved; rank convention, tie and non-finite handling are contract items.

### S0099 (cohort rank, market-wide excess-return cohort, top tail, slice C)

Finding: Cohort values come from three distinct producers depending on the family; the common step is a current-cohort rank with no numbered producer. A private candidate owner (#489) is prior-only history and is not a match.

| Operand | Role | Status | Producer | Confidence |
| --- | --- | --- | --- | --- |
| F0251 | cohort value being ranked | PLANNED_NUMBERED | #513 (route) (EF4) | medium |
| F0137 | member identity (tie order, one value per identity) | DELIVERED_ON_MAIN | #570 (route) (EF1) | medium |
| F0259 | admission marker: member enters only when present | PLANNED_NUMBERED | #570 (route); #513 (EF4) | low |
| F0150 | eligibility input | DELIVERED_ON_MAIN | #506 (route); layer #570 (EF1) | medium-low |
| F0161 | eligibility input | DELIVERED_ON_MAIN | #19 (route, closed); layer #613 (EF4) | medium-low |
| OP-ELIG-RANK | observed-cohort membership | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (population admission step) (EF8) | low |
| OP-COHORT-RANK | rank position of each member within the cohort | PROPOSED_NEW_STORY | proposed new EF8 cohort-normalization story (EF8) | medium |
| PARAM-ELIG-FLOORS | floors | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |
| PARAM-TAIL-CUT | tail cut (policy #518) | PARAMETER_ONLY | caller parameter; policy #518 (EF8) | high |

Residual: exact reuse of closed #102 is unproved; rank convention, tie and non-finite handling are contract items.

## Operand catalog notes

- **F0150** (DELIVERED_ON_MAIN): current-session close of the observation row. Delivered or candidate id: session.close.calculated_price; core session.bar.close. The row carries separate intraday, end-of-day and difference variants of close; which variant the consumers read is not fixed by the route. Candidate only; compatibility unproved.
- **F0148** (DELIVERED_ON_MAIN): current-session high of the observation row. Delivered or candidate id: core session.bar.high. Used only as an input of the true-range sequence for the current bar.
- **F0149** (DELIVERED_ON_MAIN): current-session low of the observation row. Delivered or candidate id: core session.bar.low. As F0148.
- **F0338** (PLANNED_NUMBERED): supplied completed daily-bar history (carrier of prior bars). Delivered or candidate id: core HistoryContext DAILY batch carrier (history.* grids). Serves three roles at once: history for prior-window extrema, history for the range-average operand, and the previous-bar close. The carrier exists in core; the field-level mapping is owned by the in-progress layer story.
- **F0137** (DELIVERED_ON_MAIN): member/entity identity key. Delivered or candidate id: explicit EntityKey in compute_ef1 and core batch contracts. Duplicate-identity handling differs between the breadth and the rank consumers in the source; see summary.
- **F0161** (DELIVERED_ON_MAIN): session share volume of the observation row. Delivered or candidate id: core session.trade.volume. Used only in the eligibility predicate.
- **F0152** (DELIVERED_ON_MAIN): session dollar volume of the observation row. Delivered or candidate id: core session.trade.notional. Candidate; trade-notional versus bar-notional profile and precision unproved.
- **F0206** (DELIVERED_ON_MAIN): session change versus prior close for the observation. Delivered or candidate id: core session.price.close_close_return; EF1 calendar.period prior-close return (#506). Route names #507 but the delivered prior-close return sits in the #506 period module (attribution rule A5). Percent versus fraction scale and prior-close-absent behavior unproved.
- **F0255** (DELIVERED_ON_MAIN): supplied sector classification label. Delivered or candidate id: EF1 reference.classification.value (#508). Supplied-classification carrier exists; point-in-time membership and trimming of the label are not proved.
- **F0256** (DELIVERED_ON_MAIN): supplied industry classification label. Delivered or candidate id: EF1 reference.classification.value (#508). As F0255.
- **F0251** (PLANNED_NUMBERED): matched-window excess return versus primary-market benchmark. Delivered or candidate id: related candidate only: core relative.market_return (window equivalence unproved). Matches the #513 clarification (matched rolling interval, primary-market role). The single value is reused by the market-wide, sector-grouped and industry-grouped consumers; grouping does not change the excess return.
- **F0259** (PLANNED_NUMBERED): as-of identity of the relative value (availability marker). Delivered or candidate id: none. Consumers admit a member only when this marker is present; the producer must expose availability/known-at of the F0251 output in a form the cohort step can test.
- **F0193** (PLANNED_NUMBERED): trailing-window share-volume rate. Delivered or candidate id: none. The same value is copied into F0702 at every source site read.
- **F0186** (PLANNED_NUMBERED): observation event clock. Delivered or candidate id: none for the echo; EF1 clock module covers the session clock only. Defines the trailing-window end for F0193.
- **OP-TRAILING-WINDOW** (PLANNED_NUMBERED): supplied trade tape inside the trailing window (window sum precursor). Delivered or candidate id: none. Needs the plain window-volume sum profile (not the tick-signed profile); window-end convention and empty-window behavior must be frozen in the #492 contract.
- **OP-LEVEL** (PROPOSED_NEW_STORY): caller-parameterized retracement level from a prior-window range and a ratio. Delivered or candidate id: none. Wave 1 decision A1 already proposes the story; the nine rows are the consumers that make it necessary. Inside #511 only conditionally.
- **OP-PRIOR-HIGH** (DELIVERED_ON_MAIN): high extremum over the prior completed-bar window, target excluded. Delivered or candidate id: core history.prior_high. Delivery is now established from the implemented-feature catalog and README; wave 1 reported it as not established. Window length is a caller parameter; target exclusion matches in principle; exact equivalence unproved.
- **OP-PRIOR-LOW** (DELIVERED_ON_MAIN): low extremum over the prior completed-bar window, target excluded. Delivered or candidate id: core history.prior_low. As OP-PRIOR-HIGH.
- **OP-RANGE-AVG** (DELIVERED_ON_MAIN): average true range over completed bars including the current bar. Delivered or candidate id: core history.atr (anchored smoothed ATR per README). Smoothing method matches in kind; initialization, anchor and gap treatment equivalence unproved. Used only by the three proximity rows.
- **OP-OBS-BREADTH** (PLANNED_NUMBERED): observed-population advance count, qualifying-member count and advance fraction (whole cohort and per supplied group). Delivered or candidate id: none. Story exists but its output list is declared-universe only. Proposed output enumeration is in answer B5.
- **OP-ELIG-BREADTH** (PLANNED_NUMBERED): per-member eligibility flag from price and volume floors (observed breadth cohort). Delivered or candidate id: none. Floors are caller parameters; the predicate is trivial but needs an owner and unknown-input handling.
- **OP-ELIG-RANK** (PROPOSED_NEW_STORY): per-member eligibility flag from price and volume floors (observed rank cohort). Delivered or candidate id: none. Proposed to be folded into the cohort-normalization story so the population admission is not hidden in catalogue policy; alternative is #518 policy.
- **OP-COHORT-RANK** (PROPOSED_NEW_STORY): current-observed-cohort rank position of a member among finite values (whole cohort or supplied group), with group-size gate. Delivered or candidate id: none. Wave 1 decision C1. A private candidate owner (#489) is a prior-only history summary and does not cover a current-cohort rank; closed #102 reuse is unproved.

## What could not be verified

- No code was run and no numerical, unit or window equivalence was tested; every DELIVERED_ON_MAIN entry is a presence finding at the base commit plus a static match in kind.
- Private operand identities rest on a static read of source profiles; they are not accepted bindings, and accepted private mathematical, source and consumer bindings remain zero.
- Issue state was read read-only; the live Project remains the status authority.
- Parameter values (ratios, tolerance, floors, cut-offs, gates) are deliberately withheld and must be supplied by callers; none is a default.
