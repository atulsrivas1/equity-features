# EQ164 wave 3, story W3-B2: second half of the ambiguous scanner consumers

Findings only, dated 2026-10-22. Every statement is an adjudicated finding or a proposed resolution. Nothing here is accepted: no mathematics, API, source, rights, consumer-equivalence or Ready status, and no tracker issue was created or edited. Opaque ids and public issue numbers only. Records: [EQ164_WAVE3_SCANNERS_2.json](EQ164_WAVE3_SCANNERS_2.json).

## 1. Scope

From [EQ164_WAVE2_X4.json](EQ164_WAVE2_X4.json) the scanner consumers (S####) whose primary gap class is AMBIGUOUS number 107 (the other 25 AMBIGUOUS rows are watchlists). Sorted by id, the first ceil(107/2) = 53 (S0106 to S0196) belong to the sibling story; this story takes the last floor(107/2) = **54: S0197 to S0357** (non-contiguous inside that range: S0197-S0201, S0205-S0218, S0256-S0257, S0259-S0260, S0262-S0263, S0268-S0275, S0311-S0318, S0329-S0332, S0334-S0339, S0353-S0354, S0357).

## 2. Result

| Resolution class | Consumers |
| --- | --- |
| RESOLVED_ALL_OPERANDS_COVERED | 7 |
| RESOLVED_WITH_GAPS | 43 |
| STILL_AMBIGUOUS | 4 |
| Total | 54 |

Confidence: medium 19, low 35. Operand items named: 260 (242 planned numbered, 10 delivered on main, 8 uncovered, 0 proposed new story). The 54 consumers all route policy to **#518** (I/O #621, worker #622, release EF8); the three adaptive rules also touch **#519** (EF8). #518 owns predicates and projection and absorbs no numerical operand.

What changed relative to X4: the "cannot be named" part of the ambiguity is resolved for 50 of 54 (22 as series and indicator-family operands that need no F id, 28 as lists of F ids). The "producer or profile unresolved" part is resolved to a producer story for all 54 but remains a recorded gap for 47 of them.

## 3. Per-story demand

Distinct consumers, operand items routed to the story, and operand gap items the story must absorb or answer (one consumer can touch several stories). Gap items count operands, not decisions.

| Story | State | Consumers | Operands routed | Gap items | Gap codes |
| --- | --- | --- | --- | --- | --- |
| #23 | CLOSED | 6 | 6 | 8 | GAP-BASELINE-REUSE-UNPROVED 6; GAP-AGGREGATE-PROFILE-SELECTION 2 |
| #33 | CLOSED | 11 | 17 | 25 | GAP-BASELINE-REUSE-UNPROVED 17; GAP-PERIOD-INIT-SELECTION 8 |
| #34 | CLOSED | 14 | 22 | 34 | GAP-BASELINE-REUSE-UNPROVED 18; GAP-EXACT-PROFILE-SELECTION 4; GAP-OPERAND-NOT-IN-FIELD-CATALOGUE 12 |
| #472 | CLOSED | 18 | 36 | 36 | GAP-BASELINE-REUSE-UNPROVED 18; GAP-EXACT-PROFILE-SELECTION 18 |
| #473 | CLOSED | 4 | 8 | 8 | GAP-BASELINE-REUSE-UNPROVED 4; GAP-EXACT-PROFILE-SELECTION 4 |
| #489 | OPEN | 4 | 4 | 4 | GAP-COHORT-FREEZE 4 |
| #490 | OPEN | 7 | 44 | 0 | - |
| #492 | OPEN | 3 | 0 | 3 | GAP-UPSTREAM-PROFILE-UNSELECTED 3 |
| #505 | OPEN | 6 | 10 | 0 | - |
| #506 | OPEN | 19 | 50 | 0 | - |
| #507 | OPEN | 22 | 26 | 0 | - |
| #508 | OPEN | 14 | 14 | 0 | - |
| #513 | OPEN | 6 | 6 | 0 | - |
| #570 | OPEN | 3 | 6 | 0 | - |
| #611 | OPEN | 3 | 3 | 3 | GAP-ENVELOPE-PROVISIONAL 3 |
| #626 | OPEN | 3 | 10 | 10 | GAP-ADAPTIVE-CONTRACT-ABSENT 10 |

Highest absorption: #472 (36 gap items, 18 consumers), #34 (34 including 12 catalogue gaps), #33 (25), #626 (10), #23 (8), #473 (8). Open EF1 owners #506/#507/#508 carry operands but no gap items, only contract-time selection. No proposed story is created or demanded by this half; Q1 and Q3 may add conditional ones.

## 4. Patterns

- P1. 22 rules read only an ordered daily bar series through one indicator family each; three families under closed baseline #472 (18 rules) and one under #473 (4 rules). All carry the same two gaps: reuse proof and exact profile. The public baseline dispositions record zero accepted canonical reuses.
- P2. 12 rules compare a price against level or range operands: 8 with per-period initialization under closed #33 plus #508/#506 fields, and 4 (S0198, S0208, S0209, S0218) with direct level and range operands under #33/#34. The level fields F0347-F0350 and F0351 route to closed baselines (reuse unproved).
- P3. 7 rules (S0197, S0199, S0200, S0201, S0205, S0206, S0207) have every named field operand routed to open EF1 owners #506/#507/#508 or delivered (F0271, F0284); only contract-time profile selection and per-field delivery mapping remain.
- P4. 4 category rules (S0329-S0332) use two context scalars that have no F id in the field catalogue plus a third whose supplied-versus-computed origin is unresolved: STILL_AMBIGUOUS.
- P5. 3 adaptive rules (S0336, S0337, S0357) are named at output level only through the provisional public answer X3-4; all depend on one supplied rate operand F0702 whose upstream ordered profile under #492 is unselected and on a #626 contract that does not exist.
- P6. 4 rules (S0338, S0339, S0353, S0354) share an identical 9-field operand set owned by #490 plus #489 cohort freeze and a closed #23 baseline; they are one gap for producer-demand purposes, not four.
- P7. 2 rules (S0334, S0335) read one per-symbol aggregate volume row value (inferred F0098 or F0097, #23 closed) and a direction field F0206 (#507); the aggregate profile choice is unselected.
- P8. No rule needed a PROPOSED_NEW_STORY from the wave 2 decisions; the only possible new stories are conditional (a narrow variant story if baseline reuse proof fails; a cohort-normalization producer if decision Q3 is yes).

## 5. Per-consumer table (clusters)

The per-consumer operand lists (F ids, family labels, per-operand status, gaps) are in the JSON. Consumers with the same class, profile class, touched stories and gap codes are grouped.

| Resolution | Profile class | Consumers | n | Stories touched | Gap codes |
| --- | --- | --- | --- | --- | --- |
| RESOLVED_ALL_OPERANDS_COVERED | PC07 | S0197, S0199-S0200 | 3 | #505, #506, #507, #508 | - |
| RESOLVED_WITH_GAPS | PC07 | S0198 | 1 | #34, #505, #506, #507, #508 | GAP-BASELINE-REUSE-UNPROVED |
| RESOLVED_ALL_OPERANDS_COVERED | PC07 | S0201 | 1 | #506 | - |
| RESOLVED_ALL_OPERANDS_COVERED | PC07 | S0205-S0206 | 2 | #505, #506, #508 | - |
| RESOLVED_ALL_OPERANDS_COVERED | PC07 | S0207 | 1 | #506, #507 | - |
| RESOLVED_WITH_GAPS | PC07 | S0208-S0209 | 2 | #33, #506, #513 | GAP-BASELINE-REUSE-UNPROVED |
| RESOLVED_WITH_GAPS | PC08 | S0210-S0217 | 8 | #33, #34, #506, #507, #508 | GAP-BASELINE-REUSE-UNPROVED, GAP-PERIOD-INIT-SELECTION |
| RESOLVED_WITH_GAPS | PC07 | S0218 | 1 | #33, #34, #506, #513 | GAP-BASELINE-REUSE-UNPROVED |
| RESOLVED_WITH_GAPS | PC10 | S0256-S0257, S0268-S0275, S0311-S0318 | 18 | #472 | GAP-BASELINE-REUSE-UNPROVED, GAP-EXACT-PROFILE-SELECTION |
| RESOLVED_WITH_GAPS | PC10 | S0259-S0260, S0262-S0263 | 4 | #473 | GAP-BASELINE-REUSE-UNPROVED, GAP-EXACT-PROFILE-SELECTION |
| STILL_AMBIGUOUS | PC01 | S0329-S0332 | 4 | #34 | GAP-BASELINE-REUSE-UNPROVED, GAP-EXACT-PROFILE-SELECTION, GAP-OPERAND-NOT-IN-FIELD-CATALOGUE |
| RESOLVED_WITH_GAPS | PC11 | S0334-S0335 | 2 | #23, #507 | GAP-AGGREGATE-PROFILE-SELECTION, GAP-BASELINE-REUSE-UNPROVED |
| RESOLVED_WITH_GAPS | PC11 | S0336-S0337, S0357 | 3 | #490, #507, #513, #570, #611, #626 | GAP-ADAPTIVE-CONTRACT-ABSENT, GAP-ENVELOPE-PROVISIONAL, GAP-UPSTREAM-PROFILE-UNSELECTED |
| RESOLVED_WITH_GAPS | PC11 | S0338-S0339, S0353-S0354 | 4 | #23, #489, #490, #507 | GAP-BASELINE-REUSE-UNPROVED, GAP-COHORT-FREEZE |

Field operand sets of note: S0338, S0339, S0353, S0354 share F0206, F0207, F0219, F0225-F0229, F0233 (all #490 except F0206 under #507). S0208 and S0209 share F0188, F0347-F0350. S0210-S0217 read F0188, F0190, F0191, F0206, F0351 plus one of F0347-F0350. S0336, S0337, S0357 use the public X3 lists (F0721, F0179, F0206 and per-row outputs; transitive F0702, F0208-F0211, F0186, F0700).

## 6. Decisions needed

- Q1 (#472, #473, #34, #33, #23). For the 26+ rules whose series operand routes to a closed baseline story (22 under #472/#473, 4 under #34, plus level fields under #33/#34 and aggregate fields under #23): what proof standard and which author accepts reuse of the closed baseline for a given source profile, and if the proof fails, may one narrow variant story per indicator family (FAM-A to FAM-F) be proposed?
- Q2 (#34, #609). For S0329-S0332: are the three context scalars that have no F id added to the field catalogue as supplied facts under the EF2 I/O layer (#609), or are they computed from the bar series inside #34? Which catalogue ids, if any, do they correspond to (candidates F0096, F0151, F0189, F0671 and F0087, F0141 exist only in other contexts)?
- Q3 (#489, proposed cohort-normalization). For S0338, S0339, S0353, S0354: are the cross-sectional rank operands produced by the #489 cohort freeze alone, or do they require the proposed EF8 cohort-normalization producer (wave 1 C1), which today is demanded only by the ten current-cohort rank rows?
- Q4 (#505, #506, #507, #508). Which EF1 modules on main produce F0188, F0190, F0191, F0206, F0218, F0272, F0273, F0275, F0276 (delivery ledger section 1 lists capabilities, not field mappings)? This decides whether S0197, S0199, S0200, S0201, S0205-S0207 move from planned to delivered operands.
- Q5 (#626, #611, #513, #492). Confirm or overturn X3-4: F0721 computed by #626, F0700 supplied identity under #611, F0702 a value copy of F0193 under #513. Which story names the raw operand producers of #626, and which source profile under #492 feeds F0702?
- Q6 (#23). For S0334, S0335: is the per-symbol aggregate volume value a supplied I/O fact or computed from bars under #23, and which exact source profile and eligibility apply?
- Q7 (#33). For S0210-S0217: which level periods and initialization rules are admitted by #33, and may an unsupported period be refused rather than given a variant story?
- Q8 (#506, #507, #508). For rules whose derived values name two or three EF1 owners (S0197, S0198, S0205, S0206): is the owner of each derived value fixed per output (one owner each) or chosen per rule at contract time?

## 7. What could not be verified

- The F-id lists for price and volume rules come from a lexical trace of private requirement records plus the private exact bridges; they are a proposal. Where a local value is defined from fields, the expansion is included, so a few fields may be in the list that the rule reaches only through a helper.
- Per-field delivery of fields owned by #505-#508 is undetermined (the ledger names capabilities, not fields); only F0271 and F0284 are classified delivered.
- For S0334 and S0335 the per-symbol row type is inferred; F0097/F0098 are inferred, not confirmed.
- For indicator-series rules there are no F ids at all; the family labels FAM-A to FAM-F are local to this report and are not catalogue ids. Which closed baseline matches which family (exact window, seed, precision) cannot be shown from opaque ids.
- The three adaptive rules rest on the provisional X3-4 answer; the private route record for them still names #490 and predates #626.
- Nothing was compared to a released contract; no fixtures exist for any of these rules.

## 8. Method

Operand names come from three sources: the X4 record, the private exact field bridges (opaque ids only) and a lexical trace of the private source requirement records mapped to field catalogue ids; indicator families are labelled FAM-A to FAM-F by order of first appearance. Producer status uses the public route coverage index, the selected packets A, B, C and the delivery ledger. The three adaptive rules use the public X3 answer. Read-only inputs: the public plan files, `NUMBERED_LAYER_OWNERS.md`, `DELIVERY_LEDGER.md`, the wave 1 and wave 2 audit records, and the owner's private closure material (consumer route proposals, field route proposals, source requirement records). Nothing from private material is reproduced beyond opaque ids and public numbers.
