# EQ164 audit, selected slice B (EF3 rows)

Findings only, dated 2026-10-22. Nothing here is accepted: no mathematics, API, source, rights, consumer-equivalence or Ready status, and no tracker was edited. Records are in [EQ164_SELECTED_B.json](EQ164_SELECTED_B.json). Opaque ids only.

## Slice

The 58 rows of the [selected component packet](../../plans/equity-selected-scope-components.json) whose proposed owners include planned release EF3: 26 fields and 32 consumers.

- Fields (26): F0690-F0701, F0703-F0714, F0721, F0452.
- Scanners (7): S0003-S0006, S0336, S0337, S0357.
- Watchlists (25): W0001-W0025.

Other EF1/EF2/EF4 and EF8-only rows (including F0720, whose #519 current-policy and #520 ordered components are both recorded in the packet) belong to the other slices.

## Counts by classification

| Classification | Rows |
| --- | --- |
| DELIVERED_ON_MAIN | 0 |
| COVERED_BY_PLANNED_PRODUCER | 48 (13 adaptive fields, 6 median fields, F0452, 25 watchlists, 3 adaptive scanners) |
| NEEDS_OPERAND_PRODUCER | 4 (S0003-S0006) |
| AMBIGUOUS_OR_CONFLICTING | 6 (F0691, F0697, F0698, F0700, F0701, F0721) |
| CANDIDATE_EXCLUSION | 0 |

Nothing is delivered: no EF3 capability appears in the delivery ledger, no EF3 module, contract or fixture set exists in the repo, and every EF3 owner issue is OPEN/Backlog. "Covered" means a numbered planned owner exists, not that a contract or fixtures do.

## Issue and release checks (read-only readback)

Owner, I/O and worker numbers all exist, are OPEN and agree with [NUMBERED_LAYER_OWNERS](../NUMBERED_LAYER_OWNERS.md): #626 (adaptive), #490, #489, #487, #488, #598, #491 (acceptance), I/O #611, worker #612, all milestone 24; EF8 owners #518/#519/#520, I/O #621, worker #622, milestone 28. #36 is CLOSED (accepted baseline). No missing or mismatched number was found.

## Key findings

1. Stale dependency status. The [selected dependencies file](../../plans/equity-selected-dependencies.json) still marks the #491/#611/#612/#519 edges "draft, not applied", while [AUDIT_ROUTE_PUBLICATION](../AUDIT_ROUTE_PUBLICATION.md) records them as published and read back, and the issue bodies contain them. Documentation drift, not an owner error.
2. Missing manifest entries. The 47-output ownership manifest has no entries for #626 adaptive outputs, the #490 median or mean companion outputs, or the #598 observed-population companion. Its 16 #598 entries are the declared-universe slots only.
3. Role flips and layer-as-owner. F0691, F0697 and F0698 were representation or supplied facts and are now routed to producer #626, whose body keeps supplied raw velocity or historical ratios as independently owned operands. F0700, F0701 and F0721 have the I/O layer #611 as primary owner (representation only) with no named producer of the enveloped value.
4. Median/MAD versus mean (#490). The issue outcome is median/MAD normalization and says not to replace it with mean ratios, yet the same issue houses the separately named mean companion (F0452 only). Its prerequisites (#489, #470) are median oriented, so the companion either inherits a hidden #489 edge or needs its own list. The six median fields (F0707-F0712) cite #490 alone although the baseline producer is #489; their role text is "operand or flag", so supplied versus computed is undecided. #36 reuse remains unproved.
5. #489 bridge. All 25 watchlists bridge one field to #489, but their selected overrides list only #518 and #490. All 25 carry an identical bridge set, so the six watchlists said to have extra direct joins cannot be told apart in the published file.
6. Adaptive edges. #626 has no dependency on all of #490 or EF8, consistent with its body. #519 carries the optional operand edge; #520 reaches it only transitively. For F0720 (other slice) both #519 and #520 are recorded in the packet and the dependencies file with no new story edge. S0336, S0337, S0357 list #626 as operand but record no field bridges, so output-level edges are unbound.
7. Possible forward edge. #626 says it may take raw operands from EF4 #492 (a later release than EF3 acceptance #491). Unresolved.
8. Observed population. S0003-S0006 route to #598 as an observed-population companion plus EF8 policy #518, with no bridges, no enumerated companion outputs and unnamed per-output member producers. The issue title still says declared-universe.
9. Adjacent, outside this slice: the route coverage file has about 95 further EF3 route entries (not de-duplicated) on rows outside the 122-row packet, mainly #487-#490, #598 and #611; those need the usual per-row review.

## Decisions needed from the coordinator

- D-FLIP: Are F0691, F0697, F0698 computed #626 diagnostics or supplied operands? If supplied, which story supplies them?
- D-ENV: What value does each of F0700, F0701, F0721 carry, and which numbered story produces it (or may the I/O layer be primary owner)?
- D-MED: Does the mean companion get its own numbered story or variant, or stay in #490? Are F0707-F0712 supplied flags or computed median/MAD outputs, and is #489 an explicit operand edge?
- D-WL: Record the #489 bridge as a selected override, and publish which six watchlists carry extra joins.
- D-POP: Enumerate the observed-population companion outputs and per-output operand producers, or number the missing producer.
- D-EDGE: Record which adaptive outputs S0336, S0337, S0357 consume.
- D-FWD: Accept earlier controls for #626 operands, or re-home the adaptive acceptance, given the possible #492 edge.

## Recommended next stories (not created)

1. Docs fix: reconcile the dependencies file status and add the 3 companion profiles to the output-ownership manifest.
2. Contract and fixture story for #626 outputs (formulas, units, warm-up, literal complete results), once D-FLIP and D-FWD are settled.
3. Prerequisite split for the #490 mean companion (or its own story) after D-MED.
4. Observed-population output enumeration for #598 after D-POP.

## Not verified

Semantics of each opaque id were not inspected; classifications rest on the packet, coverage file, plan documents and issue bodies. Whether #626 outputs overlap other rows was not checked. Confidence is per row in the JSON (low or medium; none high). The six watchlists with extra joins, minimal predicate prerequisites and non-EF3 bridges were not assessed.
