# EQ164 audit findings: selected-scope slice A

Findings only. Nothing here is accepted, and no tracker, contract or code change is made or implied. Opaque ids only. Per-row records are in [EQ164_SELECTED_A.json](EQ164_SELECTED_A.json).

Slice: rows of the selected-scope component packet whose planned releases include EF1, EF2 or EF4 and not EF3 (28 rows). EF3 rows and EF8-only rows are covered elsewhere.

Rows taken:
- Fields (19): F0088 F0089 F0142 F0143 (EF1 rejected-path), F0271 F0284 F0307 F0341 F0342 (EF1, with EF1 or EF8 companion), F0193 F0593 F0594 F0595 F0596 F0597 F0598 F0599 F0620 F0702 (EF4).
- Consumers (9): S0276 to S0284 (EF2 with EF8 policy).

## Method and evidence

Read: the selected-scope packet, route coverage index, selected dependencies, 47-output ownership manifest, numbered owner map, delivery ledger, publication plan and ownership reconciliation. Public issue titles and state were read for every owner, I/O and worker number, plus the bodies of #506, #511 and #513 and targeted body excerpts of #505, #518 and #520 (#507 title only). Private local inventories were not usable: the opaque ids do not appear in them, so no row could be tied to underlying source semantics. Row meaning rests on the role strings in the packet only.

## Numbering check

All owner, I/O and worker issues used by the slice (#505 #506 #507 #511 #513 #518 #520, #570/#571, #609/#610, #613/#614, #621/#622) exist, are open, and match the release map. No missing or mismatched number. Conditional or preserved prerequisites #32 and #473 are closed; #483 and #492 are open.

## Counts by classification

| Classification | Rows | Ids |
| --- | --- | --- |
| DELIVERED_ON_MAIN (partly) | 3 | F0271 F0284 F0307 |
| COVERED_BY_PLANNED_PRODUCER | 13 | F0088 F0089 F0142 F0143 F0193 F0593-F0599 F0620 |
| NEEDS_OPERAND_PRODUCER | 10 | F0702 S0276-S0284 |
| AMBIGUOUS_OR_CONFLICTING | 2 | F0341 F0342 |
| CANDIDATE_EXCLUSION | 0 | none |

Confidence is low to medium throughout; the best is medium for F0271/F0284 and F0702.

## Key findings

1. Three selected outcomes exist only as issue-body proposals and are absent from the 47-output manifest: the rejected-path diagnostic (#506, F0088/F0089 and their supplied copies F0142/F0143), the retracement level (#511, S0276-S0284), and the raw rolling return / share-volume rate / rate-difference profiles (#513, nine fields). The manifest therefore cannot yet be used as the output-level completeness check for these rows.
2. Delivered EF1 coverage is real but partial. The first-trade price producer, I/O mapping and worker entry are on main (F0271/F0284). Opening-observable features are on main (F0307) but the ledger marks their story attribution unverified. The multi-venue aggregation and supplied-close comparison producers are not on main.
3. The nine consumers S0276-S0284 have identical routes. Their level operand rests on a #511 companion whose own text says to number a narrow gap if it is outside #511 scope; #511's title is channels and squeeze. Extrema operand reuse of closed #32 is unproved, and proximity/crossing/score policy (#518) is planned only. These are consumer operand gaps; per-consumer operand lists are not recoverable from opaque ids.
4. The #513 role string is a union of three sub-profiles for all nine rate fields, so which row is a return, a rate or a rate difference is not recorded. F0702 depends on an unselected #492 ordered-window profile.
5. NUMBERED_LAYER_OWNERS says a conditional diagnostic follow-up was not created and cannot count as an owner. #506 now carries a rejected-path companion section. It is unclear whether these are the same item; until resolved, F0088/F0089 ownership is not firm.
6. F0142/F0143 name an I/O layer issue (#570) as primary owner, unlike library-story owners in other rows.
7. No hidden reverse edge from EF1/EF2/EF4 to EF8 was found. EF8 policy rows (#518/#520) depend on earlier operands only, consistent with the no-blanket-gate statement. Possible wrong edge to confirm: #513 lists #505/#506/#507 only as conditional operands, while its body names no frozen output-level binding.

## Coordinator decisions needed

- Q1 (S0276-S0284): Is the retracement-level arithmetic inside #511's scope, or should a narrowly numbered gap story be created?
- Q2 (F0088 F0089 F0142 F0143, S0276-S0284, F0193 F0593-F0599 F0620): Should the three proposal-only outcomes be added as entries to the output-ownership manifest, or stay body-only?
- Q3 (F0088/F0089): Is the #506 rejected-path section the same item as the "conditional diagnostic follow-up not created", and may #506 be counted as owner?
- Q4 (F0193 F0593-F0599 F0620 F0702): Which of these is a raw return, a rate, or a rate difference, and which #492 ordered-window profile supplies the rate operand?
- Q5 (F0341 F0342 F0307 F0271 F0284): Which delivered features correspond to the supplied-anchor arithmetic and the observation clock, and which story (#505, #506, #507) owns each delivered module?
- Q6 (F0271 vs F0284, F0341 vs F0342): Are the identical-route pairs duplicates or distinct profiles?

## Recommended next stories

1. Source-safe contract proposal and fixture list for the rejected-path diagnostic under #506, then mapping under #570/#571 for the supplied copies.
2. Scope decision on retracement level (#511 versus a narrow numbered gap), followed by an operand-level join list for S0276-S0284.
3. Output-manifest amendment covering the three proposal-only outcomes, and a per-row return/rate/difference split plus #492 profile selection for the #513 fields.
4. Ledger attribution of delivered opening-observation and anchor features to stories, and a check of whether the open-to-endpoint return output in the manifest has a delivered counterpart.

## Not verified

Source semantics behind any opaque id; numerical equivalence; rights; whether delivered modules were re-run; whether installed artifacts cover later slices; issue bodies of #483, #492 and #507 beyond titles; the full delivery replan. Delivery on main is not acceptance.
