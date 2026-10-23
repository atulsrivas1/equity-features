# EQ164 wave 2: coordinator decisions

October 22, 2026. Decisions on the questions raised by the merged wave 2 reports: [X1](EQ164_WAVE2_X1.md) #654 (101 ingest/admin/validation exclusions), [X2](EQ164_WAVE2_X2.md) #652 (101 other-domain exclusions and 6 standalone rows), [X3](EQ164_WAVE2_X3.md) #653 (operand lists for the 24 priority rows) and [X4](EQ164_WAVE2_X4.md) #651 (definition of the 245 and consumer gaps). Status: every row below is a coordinator working decision under the working agreement, pending owner review; none is owner-approved, and rows marked provisional rest on proposals or unproven evidence. Findings and decisions are not acceptance; full EQ164 stays open; no tracker issue was created or edited; "proposed story" means a numbered story is needed and does not yet exist. Opaque ids only.

## Verdict totals
- X1: 80 confirm exclusion, 5 reject (C0034, C0099, C0257, C0187, C0029), 16 need owner decision.
- X2: 82 confirm, 8 reject (C0280, C0281, C0284, C0290, C0291 to #488; C0140, C0132, C0135 to #515), 11 need owner decision; standalone 5 confirm, 1 needs owner decision.
- Rejected exclusions are adopted as retained components with the named owner; the plan flag "no retained component" is corrected for those rows in wave 3.

## Decisions
| Id | Question | Decision |
| --- | --- | --- |
| X1-1 | Provider acquisition and normalization commands (10 rows, plus C0053 which also cites this question): retained source access or optional adapters? | Optional adapters. Only a neutral admission contract is retained, expressed as caller-supplied facts and defined by a later reviewed contract (no provider rule is adopted here), owned by I/O #570 and later EF I/O tasks. No provider-specific rule or threshold is adopted. |
| X1-2 | C0058 declared-universe membership rule | Retained as a supplied declared-universe fact; owners #598 and #508. The universe is caller supplied; no selection algorithm is adopted. |
| X1-3 | Can C0184 reference calculations serve as qualification evidence? | Provisional: not qualification evidence on its own. The adjudicator leaned toward allowing it after an independence review; the coordinator's choice is the stricter one because qualification fixtures must be authored independently. C0184 may serve as a cross-check witness. The owner may overturn this. |
| X1-4 | Notification envelope builders (C0031, C0062, C0064) | Consumer side only: excluded. External notifications stay outside scope. |
| X1-5 | C0204 equity candidate consumed by the option selection worker | Retained supplied-operand contract, defined when option releases consume equity output (EQ153 and EQ158 gates); not EF1 work. |
| X2-1 | Trade prints admitted into underlying-price observations (C0148, C0109, C0161 to C0163) | Retained as I/O mapping of supplied facts (#570 and later EF I/O tasks); no new mathematics; #506 only if price construction is involved. |
| X2-2 | Stock-universe selection (C0151, like C0215) | Retained as supplied declared-universe membership; owners #598 and #508; no selection algorithm. |
| X2-3 | Event-schedule validator and event-free test (C0118, C0279) | Retained as supplied-fact validation under #514, I/O #617. |
| X2-4 | Window return over product-carried prices (C0122, C0249) | Retained under #513 (return profiles over supplied prices). |
| X2-5 | Candidate artifact schema rewritten by C0209 | Representation obligation owned by #521, with #520 as consumer; contract to be defined in EF8. |
| X2-6 | Wire-schema consistency (C0139) | Consistency check owned by #522; the wire schema itself stays product-private. The C0153 child set and C0215 stay open items with the owners above. |
| X3-1 | Observed-population output list for #598 | Narrow companion story (proposed) listing the seven outputs, to keep #598 scope clean. |
| X3-2 | Reuse of closed story #102 for the ten rank rows | Not accepted until proved (consistent with the wave 1 decision C1). |
| X3-3 | Retracement rows and F0702 contract gaps | Contract authors define them: close variant and tie rule (EF2), window end and empty-window behavior (EF4, #513). |
| X3-4 | Proposed answers A4, B2, B5, B6 | Provisional working answers (each needs its contract and owner review): F0702 is a value copy of F0193 (#513); F0700 and F0701 are supplied identity and clock (#611); F0721 is computed by #626; seven observed-population outputs; S0336, S0337 and S0357 read F0721 and named F0690 to F0699 outputs. Each needs its contract before Ready. |
| X4-1 | Meaning of the 245 | Working definition from X4: consumers (220 scanners, 25 watchlists) without a single explicit numerical candidate owner. It reproduces from private material only. The 216 representation-slot figure did not reproduce from the public flags (X4 found 220); it is not used as a gate number until reproduced, and the owner decides whether to retire it. |

## Proposed stories (not created)
Sources: 1 X3 and wave 1 A1; 2 wave 1 C1 and X3; 3 wave 1 C2; 4 wave 1 B3 and X4 (13 missing-producer rows); 5 X3 (B5); 6 X1-1; 7 X2-5. Items 3, 6 and 7 are driven by wave 1 and X1/X2 findings, not by X3/X4.
1. Retracement-level producer (EF2).
2. Cohort-normalization producer (EF8).
3. Anchor discovery primitive (EF1/EF8 boundary).
4. Mean-companion story (EF3), serving 13 consumers.
5. Observed-population companion story (EF3, #598 companion).
6. Neutral provider-admission contract (I/O).
7. Candidate-artifact representation contract (EF8, #521).

Issue creation needs owner approval.

## Wave 3 (planned)
Correct the public plan flags for the rejected exclusions; resolve the 132 ambiguous consumers (the 25 watchlists first: common versus per-key operand choice); write contracts for the proposed stories; hygiene fixes in `equity-selected-dependencies.json` and `equity-output-ownership.json`; reconcile the remaining non-selected identities with duplicate and orphan accounting.
