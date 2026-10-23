# EQ164 wave 1: coordinator decisions

October 22, 2026. Coordinator decisions on the questions raised by the three merged slice reports ([A](EQ164_SELECTED_A.md) #648, [B](EQ164_SELECTED_B.md) #649, [C](EQ164_SELECTED_C.md) #647), covering the 122 selected rows. Status of every decision: decided, pending owner review. Rows A3, A4, A5, B3 and B7 are provisional working rules: the slice reports left the underlying question open or unproven, so they are recorded as the coordinator's current routing choice and may be overturned by the owner or by contract evidence. Findings and decisions are not acceptance: full EQ164 stays open, no row is Ready, and no tracker issue was created or edited. "Proposed story" means a numbered story is needed and has not been created.

## Slice C (EF8-only rows)

| Id | Question | Decision |
| --- | --- | --- |
| C1 | S0090-S0099 cohort normalization: own producer or closed-story #102 reuse? | Needs its own numbered pure producer (proposed story, EF8). #102 reuse is not accepted until proved; the policy owner #518 must not hide the arithmetic. |
| C2 | F0343-F0346 anchor discovery: numbered primitive or #520 lifecycle state? | Separate numbered pure primitive (proposed story, extends the EF1 anchor family). #520 consumes it; it must not gate earlier primitives. |
| C3 | F0720 owner seam between #519 and #520 | #520 publishes F0720 (ordered episode) and consumes #519's current-policy component; #519 owns the component only. |
| C4 | Which of F0715-F0719 consume #626 | None assumed. The optional #626 edge stays unproven until a row-level operand list names the consuming rows. |

## Slice A (EF1, EF2, EF4 rows)

| Id | Question | Decision |
| --- | --- | --- |
| A1 | Retracement level: inside #511 or a gap story? | Narrow numbered gap story (proposed story, EF2); do not stretch #511's channel/squeeze scope. |
| A2 | Add the three proposal-only outcomes to the 47-output manifest? | Yes, as proposed and unaccepted entries through a reviewed docs change: rejected-path diagnostic (#506), retracement level, raw return/rate/rate-difference profiles (#513). |
| A3 | Is the #506 rejected-path section the conditional diagnostic follow-up? | No. The conditional follow-up stays uncreated and cannot count as an owner; #506 owns its own section only. |
| A4 | #513 field profiles and F0702 profile source | Deferred to wave 2 as a row-level operand task (owner: EF4 contract author). |
| A5 | Which delivered modules belong to which story | Attribution rule: clock, status, status history, opening-trade observables to #505; extended sessions, period levels, regular prices, daily observations to #506; anchors, gaps, opening drive to #507. Applied to the delivery ledger in wave 2. |
| A6 | Identical-route pairs F0271/F0284 and F0341/F0342 | Treated as distinct profiles until proved duplicates; profile definitions required. |

## Slice B (EF3 rows)

| Id | Question | Decision |
| --- | --- | --- |
| B1 (D-FLIP) | F0691, F0697, F0698 computed #626 outputs or supplied operands? | Computed by the #626 adaptive producer unless a contract shows a supplied operand. Confirm in the #626 contract. |
| B2 (D-ENV) | F0700, F0701, F0721 contents and producer | Undecided; the #626 contract author defines them (wave 2). |
| B3 (D-MED) | Mean companion story; F0707-F0712 supplied or computed | Mean companion (F0452) gets its own numbered story (proposed). F0707-F0712 are computed from the #489 baseline producer: add the #489 edge. |
| B4 (D-WL) | #489 bridge and the six watchlists with extra joins | Record the #489 bridge as a selected override; publishing the six watchlists with direct joins is a wave 2 item. |
| B5 (D-POP) | Observed-population companion outputs (#598) | Enumerate outputs and operand producers in wave 2. |
| B6 (D-EDGE) | Adaptive outputs consumed by S0336, S0337, S0357 | Row-level operand list in wave 2. |
| B7 (D-FWD) | #626 raw inputs from EF4 #492, a later release | #626 takes supplied inputs through I/O in EF3 and does not depend on EF4 production. If an output truly needs #492 output, that edge applies to that output only and EF3 acceptance waits on it. |

## Hygiene findings to fix (docs)
- `equity-selected-dependencies.json` still marks four edges "draft, not applied" although the issue bodies are published.
- The 47-output manifest lacks #626, #490 companion and #598 entries.
- About 95 EF3 route entries sit outside the 122-row packet and are not yet de-duplicated.

## Wave 2 (planned, not started)
1. Adjudicate the 208 proposed command exclusions (101 ingest/admin/validation, 101 other-domain, 6 reviewed standalone) by category; source-safe, opaque ids.
2. Row-level operand lists for consumer rows (the 245 consumer operand gaps), starting with the ten rows that need operand producers in slices A and C and four in B.
3. Draft the proposed stories (cohort normalization, anchor discovery, retracement gap, mean companion) as a docs PR; issue creation needs owner OK.
4. Reconcile the remaining identities outside the 122 selected rows (fields 721, scanners 357, watchlists 25, commands 296) with duplicate/orphan accounting.
5. Fix the hygiene findings above.
