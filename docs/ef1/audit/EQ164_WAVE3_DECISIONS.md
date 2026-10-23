# EQ164 wave 3: coordinator decisions

October 22, 2026. Working decisions on the questions raised by the merged wave 3 reports: [watchlists](EQ164_WAVE3_WATCHLISTS.md) #661, [scanners part 1](EQ164_WAVE3_SCANNERS_1.md) #670 and [scanners part 2](EQ164_WAVE3_SCANNERS_2.md) #662; the story drafts were filed as EQ-238 to EQ-244 (issues #663 to #669) and the plan hygiene edits merged as #659. Status of every row: coordinator working decision, pending owner review; none is owner-approved. Where a row only routes a question to a contract author it says so. No source behaviour is adopted by any decision here; findings and decisions are not acceptance; full EQ164 stays open. Opaque ids only.

## Results of the three reports
- Watchlists: 23 resolved on the common 33-field operand set, 2 composites (W0014, W0015) with their own member edges, 0 ambiguous.
- Scanners (107 ambiguous): 46 resolved with all operands covered, 55 resolved with gaps, 6 still ambiguous (S0172, S0189 in part 1; S0329 to S0332 in part 2). Part 1 covers S0106 to S0197 (54), part 2 covers S0198 to S0357 (53); no overlap, union 107.
- No operand is classed delivered: per-field delivery is unproven because the delivery ledger is capability-level.

## Watchlists
| Id | Decision |
| --- | --- |
| W3A-1 | Yes: the common 33-field set is the authoritative admission profile for all 25; per-watchlist predicate subsets are informational. |
| W3A-2 | Retire the "six with extra joins" statement in favour of the finding that no watchlist reads outside the common 33, unless the owner supplies the six. |
| W3A-3 | Yes: record W0014 (7 members) and W0015 (6 members) as consumer-to-consumer edges in a later plan hygiene change. |
| W3A-4 | Proposed owner, unconfirmed: #518 (catalogue and policy owner in the route coverage) with I/O #621 for the three shared policy inputs (eligibility configuration, classification, pinned override revision). The report assumed no owner; no story is mapped to them yet and a contract must confirm. |
| W3A-5 | Conservative: F0455 (#489 baseline) is treated as a required supplied validation input, so the #489 edge blocks all 25, until a contract shows it may be optional. |
| W3A-6 | Owner item: the opaque W-id to watchlist mapping cannot be checked publicly; the owner confirms it. |

## Scanners, part 1
| Id | Decision |
| --- | --- |
| D1 | The fallback behaviour for an absent baseline is not adopted: each affected rule is explicitly unavailable when F0351 is absent; a versioned variant under #34 may be proposed by the owner. |
| D2 | Contract author decides whether closed #472 is series-agnostic; if reuse is not proved, a narrow daily-series story is proposed (not created). |
| D3 | Contract author decides whether #473 exposes the trailing-window dispersion or a fixed band multiple; open contract item. |
| D4 | #493 is authoritative for F0153 and F0155 as the field routes say; reuse of closed #25 is unproved. |
| D5 | The predicate flags F0287 to F0291 are recomputed by policy (#518, #520) from numeric levels and price; supplied flags are not authority. Touch, close-beyond and strictness semantics are policy contract items. |
| D6 | Declarations with no selected emitter (S0172, S0189) stay recorded as dormant declarations (no selected emitter), not consumers, pending the owner's view on retiring them. |
| D7 | The #21 primitive proposal is withdrawn in favour of #506 session extrema plus the #34 baseline. |
| D8 | Working choice: the gap measure contract is a fraction (matching the delivered capability) with a percent-style field as a presentation conversion; #506 is proposed as the owner of the regular-open price (F0271), though the field has both an #505 and an #506 route and the contract author confirms. |
| D9 | Level windows bind to the delivered period and daily-observation outputs under #506; the current-session inclusion rule and the distance-versus-level choice for F0212 to F0217 are contract items for the EF1 contract author. |
| D9H | The daily-history profile guaranteed by the supplied slot F0338 under #570 is a contract item (length, adjustment, completed-only or current-inclusive); completed-only is the coordinator's working assumption, not a finding, until a contract says otherwise. |

## Scanners, part 2
| Id | Decision |
| --- | --- |
| Q1 | Proof standard for reusing a closed baseline: independent fixtures covering window, seed, precision and current-observation inclusion for the needed profile, reviewed by a fresh independent reviewer; if the proof fails, one narrow variant story per indicator family may be proposed. |
| Q2 | S0329 to S0332: the three context scalars are supplied facts under the EF2 I/O layer (#609) with catalogue ids added by contract; they are not computed inside #34. |
| Q3 | S0338, S0339, S0353, S0354: add a provisional dependency on the cohort-normalization producer (EQ-239, #664) unless the #489 cohort freeze is proved sufficient. |
| Q4 | Per-field delivery is a wave 4 task: audit EF1 field ids against the merged modules on main. Until proved, nothing counts as delivered. |
| Q5 | Confirm X3-4 provisionally: F0721 computed by #626, F0700 supplied identity (#611), F0702 a value copy of F0193 (#513); raw operand producers for #626 and the #492 source profile for F0702 are contract items. |
| Q6 | S0334, S0335: the per-symbol aggregate volume is a supplied I/O fact until #23 reuse is proved. |
| Q7 | S0210 to S0217: an unsupported level period is refused, not given a variant story. |
| Q8 | One owner per derived output, fixed at contract time and recorded in the contract. |

## Next (wave 4, planned, not started)
1. Field-level delivery audit: EF1 field ids against the merged producers on main (Q4).
2. Apply the plan changes these decisions imply: W0014/W0015 member edges, the #489 override, dormant declarations, withdrawn #21 proposal.
3. Contract authoring for the seven new stories (#663 to #669), starting with the shared duplicate-identity decision.
4. Owner items: confirm the W-id mapping (W3A-6); review all coordinator decisions; add the new issues to the Project Backlog.
