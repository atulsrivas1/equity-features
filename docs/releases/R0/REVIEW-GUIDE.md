# Release 0 owner review guide

> Working document, not a decision. PO, 2026-10-30. Internal, synthetic, pre-release. After this review the owner is the facilitator only. **"Approve" is a complete answer.**

## Read, in this order (about 45 minutes)
1. [`RELEASE-0.md`](RELEASE-0.md) exit table (10 min): what Release 0 had to produce and where each item stands.
2. [`docs/planning/RELEASE-MAP.md`](../../planning/RELEASE-MAP.md) and [`RL-01/SCOPE.md`](../RL-01/SCOPE.md) (10 min): what exists, what is next, Ready and Blocked.
3. [`docs/playbook/ADOPTION.md`](../../playbook/ADOPTION.md) and [`docs/planning/REQUIREMENTS-DIGEST.md`](../../planning/REQUIREMENTS-DIGEST.md) (15 min): the team model and your rules in your words.
4. [`docs/architecture/SYSTEM-DESIGN.md`](../../architecture/SYSTEM-DESIGN.md), [`EXISTING-SYSTEM-AUDIT.md`](../../architecture/EXISTING-SYSTEM-AUDIT.md), [`RELEASE-0-RULINGS.md`](../../architecture/RELEASE-0-RULINGS.md) (10 min).

## Decide (each has a recommendation)
| # | Decision | Recommendation | If you say nothing |
|---|---|---|---|
| 1 | Approve Release 0: working model, three-review rule, RL-01 plan | Approve | Team starts RL-01 as written, after the team meeting |
| 2 | Ratify E1-E9 (EF4 rulings, [`EF4_SHARED_AMENDMENT.md`](../../ef4/EF4_SHARED_AMENDMENT.md)) | Ratify; E9 unit spelling last | Coordinator rulings stay in force; E9 migration stays unstarted |
| 3 | Ratify PO-1..PO-7 (EF5 contract rulings) | Ratify | Applied as accepted; EF5 stays internally frozen |
| 4 | Reverse EF5 "stop at primitives" (named patterns) | Do not reverse now | Stop at primitives |
| 5 | Design owner's period number, 252 vs 253 | Supply one number | Contract leaves it to the consumer; no default added |
| 6 | Provide a Linux machine for qualification (incl. EQ-139 rerun) | Provide when convenient | Windows-only evidence; no Linux claim |
| 7 | Hold an owner demo | After RL-01 closeout | No demo; browser-demo evidence only |
| 8 | Publish, tag, sign-off | Not yet | Nothing is published or tagged |
| 9 | Line-ending rule (.gitattributes); package version bump at release | Decide at the first release candidate | Existing behaviour |

Providers, cost and data rights are not ours and are not on this list. Unanswered items keep their provisional readings, listed in the RELEASE-MAP owner table.

## Risks (in order)
1. Unratified E1-E9 and PO-1..PO-7: later work rests on provisional readings; reversal after the E9 migration would be costly, so E9 is ordered last.
2. Nothing verified on Linux; real-source and parity evidence minimal.
3. Throughput: reviews and one Tester set the pace; the io catalogue chain is serial on one writer. The Ready buffer is 9 until core #761 merges.
4. Cross-repo pins and bumps: a missed re-pin or builder run breaks a downstream repo.
5. Autonomy drift: the stop condition and decision log are the control; any row can be reversed by amending it.

## After this review
Rows marked "decided, pending owner review" in [`DECISIONS.md`](../../../DECISIONS.md) are listed to you at each next-release planning; work does not wait; you can ask for a change at any time.
