# EQ164 wave 2, story X4: the 245 consumer operand gaps

Findings only, dated 2026-10-22. Every statement is an adjudicated finding or a proposal. Nothing here is accepted: no mathematics, API, source, rights, consumer-equivalence or Ready status, and no tracker issue was created or edited. Opaque ids and public issue numbers only. Records: [EQ164_WAVE2_X4.json](EQ164_WAVE2_X4.json).

## 1. What the number 245 is

**Definition (adjudicated finding).** 245 is a count of **consumers**, not of operands, fields or joins. It is the number of the 382 consumer identities (357 scanners S#### plus 25 watchlists W##) for which the earlier private ownership crosswalk records **no single explicit numerical candidate owner**. It splits into 220 scanners and 25 watchlists. The published phrase "consumer operand gaps" is therefore a misnomer in unit terms: one gap is one consumer row, and a row can hide anywhere from 1 to 33 operand items.

**Where it comes from.** It is carried unchanged through the private reconciliation manifests (versions 1 to 3), the private source-backed consumer route preparation (versions 1 to 3, where it is the number of consumer rows flagged as lacking a single original operand candidate) and the preparation checks. The public docs (`NUMBERED_LAYER_OWNERS.md`, `OWNERSHIP_RECONCILIATION.md`, `AUDIT_ROUTE_PUBLICATION.md`, `DELIVERY_LEDGER.md`, `BACKLOG.md`) repeat only the bare number. The mirror figure on the field side is 249 of 721 fields without a single numerical candidate; the 216 representation slots are a separate subset of the field inventory.

**Reproducibility.**

| Quantity | Value | Reproducible from |
| --- | --- | --- |
| Consumers (scanners + watchlists) | 382 (357 + 25) | public route coverage index |
| Consumers flagged as 245 | 245 (220 scanners, 25 watchlists) | private material only; the public index has no per-consumer flag |
| Consumers outside the 245 | 137 | derived (382 - 245) |
| Policy owner of all 382 consumers | #518 (I/O #621, worker #622, EF8) | public index |
| Lexical field bridge instances inside the 245 | 876 (64 unique fields; 25 watchlists share one identical 33-field set, 51 further bridges on 20 scanners) | public index |
| Non-field primitive proposals inside the 245 | 329 (209 consumers carry at least one) | public index (`prior_primitive_proposals_for_review`) |
| 245 consumers with no lexical field bridge | 200 | public index |
| Consumers outside the 245 with no lexical bridge / with a primitive proposal | 115 / 115 | public index |
| Fields flagged representation-or-supplied in the public index | 220 (not 216) | public index |

**Verdict.** 245 reproduces exactly as a consumer-row count from private material, and its composition (220 + 25) is stable across all private versions. It does **not** reproduce from public files alone: the public index cannot separate the 245 from the other 137 consumers, and no public file defines the unit. The closest public counts are the bridge and primitive counts above (876 field bridge instances and 329 primitive proposals, 1205 operand items in total, only 64 distinct fields). The 216 representation slots also do not reproduce from the public flag (220 flagged fields), so that figure and the 33 variants were not reconciled here.

**Consequence for the gap wording.** None of the 245 has a row-level operand contract. The public lexical bridges are explicitly not canonical joins and not a minimal runtime DAG. For 200 of the 245 (all scanners) there is no field-level bridge at all, so their operands cannot be named as F#### ids; they exist only as non-field primitive proposals with a numbered owner.

## 2. Scope of this table

The 24 priority rows covered elsewhere are F0702, S0003-S0006, S0090-S0099 and S0276-S0284. Only 19 of them lie inside the 245 (S0090-S0099, S0276-S0284). F0702 is a field and S0003-S0006 route to the observed-population companion without being part of the 245. Excluding the 19 leaves **226 consumer rows (201 scanners, 25 watchlists)** in this table. They carry 876 field-bridge items (64 unique fields) and 310 primitive items.

## 3. Gap classes

Per operand item and per consumer. A consumer's **primary** class is the first present class in this precedence: missing producer story, ambiguous, representation slot, supplied fact (I/O mapping only), covered. Class assignment is mechanical from public routes, pending-selection markers and the wave 1 decisions; it is a proposal, not a semantic review.

| Class | Meaning | Consumers (primary) | Consumers (present at all) |
| --- | --- | --- | --- |
| MISSING_PRODUCER_STORY | at least one operand needs a numbered story that does not exist yet (proposed: cohort normalization, retracement level, mean companion, per wave 1 decisions C1/A1/B3) | 13 | 13 |
| AMBIGUOUS | a numbered owner exists but an exact-profile selection, baseline-reuse proof, variant decision or root choice is pending, or the consumer is declared without a selected emitter | 132 | 132 |
| REPRESENTATION_SLOT | operand is a field flagged representation-or-supplied in the public coverage index and routed to an I/O layer | 0 | 25 |
| SUPPLIED_FACT_IO_MAPPING | operand is a supplied fact or flag (heuristic role class) needing adapter mapping only | 10 | 40 |
| COVERED | every operand has a proposed numbered owner and no pending selection; no row-level operand contract exists, so it is still a gap | 71 | 178 |
| Total | | 226 | |

Operand-item view (226 rows): COVERED_CLOSED_BASELINE_REUSE_UNPROVED 369; COVERED_NUMBERED_PLANNED_NOT_DELIVERED 336; SUPPLIED_FACT_IO_MAPPING 174; COVERED_NUMBERED_EF1_DELIVERY_UNDETERMINED 147; AMBIGUOUS 122; REPRESENTATION_SLOT 25; MISSING_PRODUCER_STORY 13.

Notes on the classes.

- MISSING_PRODUCER_STORY (13 scanners): all 13 need the mean-ratio companion that wave 1 decision B3 proposes as its own numbered story (proposed, not created). The cohort-normalization (C1) and retracement-level (A1) proposed stories are demanded only by priority rows (S0090-S0099, S0276-S0284), which this table excludes.
- AMBIGUOUS (132): 25 watchlists (common versus per-key validation operands unresolved), 3 adaptive-diagnostic consumers (numbered owner now exists as #626, but which outputs they consume is unrecorded, wave 1 B6), 2 scanners declared without a selected end-of-day emitter, and the remaining scanners (about 100) whose numbered owner is a closed baseline story or an open story but whose exact profile, window, seed, population or variant selection is pending. A closed baseline story is not an accepted reuse: exact-profile proof is outstanding.
- REPRESENTATION_SLOT (25, never primary): one field, routed to the EF8 I/O layer #621, shared by the 25 watchlists.
- SUPPLIED_FACT_IO_MAPPING (10 primary, 40 present): scanners whose remaining operands are supplied facts or flags. The supplied-versus-computed split is a heuristic over private role labels (only the class is published) and is low confidence.
- COVERED (71): every operand has a proposed numbered owner and no pending selection. They remain gaps because no operand contract, unit or fixture exists.

Gap classes by consumer kind: scanners SUPPLIED_FACT_IO_MAPPING 10, AMBIGUOUS 107, COVERED 71, MISSING_PRODUCER_STORY 13; watchlists all 25 AMBIGUOUS.

## 4. Per-story demand

Distinct consumers and operand items each numbered story must absorb or answer (226 rows; one consumer can touch several stories). "Pending" counts primitive items whose exact profile or variant selection is still open. Closed stories are accepted baselines; reuse for a source profile stays unproved. Proposed stories are not created.

| Story | State | Consumers | Field items | Primitive items | Pending selection |
| --- | --- | --- | --- | --- | --- |
| #21 | CLOSED | 2 | 0 | 2 | 2 |
| #23 | CLOSED | 24 | 0 | 24 | 5 |
| #25 | CLOSED | 3 | 0 | 3 | 3 |
| #32 | CLOSED | 25 | 200 | 0 | 0 |
| #33 | CLOSED | 42 | 159 | 17 | 17 |
| #34 | CLOSED | 47 | 1 | 47 | 47 |
| #39 | CLOSED | 25 | 50 | 0 | 0 |
| #472 | CLOSED | 18 | 0 | 18 | 18 |
| #473 | CLOSED | 6 | 0 | 6 | 6 |
| #481 | OPEN | 6 | 0 | 6 | 0 |
| #482 | OPEN | 3 | 0 | 3 | 0 |
| #483 | OPEN | 4 | 0 | 4 | 0 |
| #484 | OPEN | 8 | 0 | 8 | 0 |
| #485 | OPEN | 2 | 0 | 2 | 0 |
| #487 | OPEN | 2 | 2 | 0 | 0 |
| #489 | OPEN | 31 | 25 | 6 | 4 |
| #490 | OPEN | 42 | 29 | 15 | 13 |
| #505 | OPEN | 3 | 3 | 0 | 0 |
| #506 | OPEN | 73 | 67 | 43 | 7 |
| #507 | OPEN | 11 | 5 | 9 | 5 |
| #508 | OPEN | 69 | 77 | 42 | 2 |
| #511 | OPEN | 11 | 0 | 11 | 0 |
| #512 | OPEN | 25 | 50 | 0 | 0 |
| #513 | OPEN | 70 | 185 | 37 | 3 |
| #518 | OPEN | 1 | 1 | 0 | 0 |
| #519 | OPEN | 3 | 0 | 3 | 3 |
| #520 | OPEN | 4 | 0 | 4 | 0 |
| #621 | OPEN | 25 | 25 | 0 | 0 |
| NS-MEAN-COMPANION (proposed, wave 1 B3) | not created | 13 | 0 | 13 | 13 |

Highest demand: #506 (73 consumers), #513 (70), #508 (69), #34 (47, all pending), #33 (42), #490 (42). The EF8 policy #518 is the policy owner of every consumer and is not counted above as an operand producer. Largest pending blocks: baseline ATR-style profile reuse under #34/#33/#23/#25/#472/#473 (86 primitive items), and the mean-ratio variant (13).

Delivered versus planned. Of the owners above, only #505-#508 have any merged EF1 module (`DELIVERY_LEDGER.md`). Which operand item corresponds to which merged module cannot be decided from opaque ids, so 147 items routed to EF1 owners are labelled delivery-undetermined, 336 to open later-release owners as planned and not delivered, and 369 to closed baseline stories as reuse unproved. No item is classed DELIVERED_ON_MAIN.

Suggested owner: only the mean companion needs a new story (13 consumers). Everything else maps to an existing numbered owner, with the selection or variant decision pending (a variant story may follow if exact-profile proof fails; not predicted here).

## 5. Per-consumer table (clusters)

The complete per-consumer rows, with per-operand classes, are in the JSON. Consumers that share the same primary class, touched owners, pending-selection kinds and flags are grouped here (43 clusters over 226 rows). "Fields" is the number of field-bridge operands per consumer; 0 means operands are non-field primitives only and cannot be named as F####. Pending kinds: BASELINE-REUSE (exact profile must match a closed baseline or a variant is needed), PROFILE-SELECT (history, reference, phase and population profile), PERIOD-INIT (period and initialization selection), COHORT-FREEZE (observed cohort and ties), MEAN (mean-ratio variant), ADAPTIVE (adaptive diagnostic output selection).

| Primary class | Consumers | n | Fields | Numbered owners touched | Pending kinds | Flags |
| --- | --- | --- | --- | --- | --- | --- |
| MISSING_PRODUCER_STORY | S0341-S0352, S0356 | 13 | 0 | #23, #490 | MEAN | ROOT-CHOICE-MEAN-RATIO |
| AMBIGUOUS | S0158-S0161, S0164-S0171, S0173-S0177, S0180-S0188, S0190-S0193 | 30 | 0 | #34, #506, #508 | BASELINE-REUSE | - |
| AMBIGUOUS | W0001-W0025 | 25 | 33 | #32, #33, #39, #489, #490, #506, #508, #512, #513, #621 | - | ROOT-CHOICE-WATCHLIST-COMMON-VS-PER-KEY |
| AMBIGUOUS | S0256-S0257, S0268-S0275, S0311-S0318 | 18 | 0 | #472 | BASELINE-REUSE | - |
| AMBIGUOUS | S0210-S0217 | 8 | 0 | #33, #508 | PERIOD-INIT | - |
| AMBIGUOUS | S0121, S0124, S0259-S0260, S0262-S0263 | 6 | 0 | #473 | BASELINE-REUSE | - |
| AMBIGUOUS | S0138-S0141 | 4 | 0 | #34, #513 | BASELINE-REUSE | - |
| AMBIGUOUS | S0329-S0332 | 4 | 0 | #34 | BASELINE-REUSE | - |
| AMBIGUOUS | S0338-S0339, S0353-S0354 | 4 | 0 | #23, #489 | COHORT-FREEZE | - |
| AMBIGUOUS | S0106, S0110-S0111 | 3 | 0 | #25 | BASELINE-REUSE | - |
| AMBIGUOUS | S0109, S0334-S0335 | 3 | 0 | #23 | BASELINE-REUSE | - |
| AMBIGUOUS | S0336-S0337, S0357 | 3 | 0 | #519 | ADAPTIVE | ROOT-CHOICE-ADAPTIVE |
| AMBIGUOUS | S0115, S0118 | 2 | 0 | #33, #34, #513 | BASELINE-REUSE | - |
| AMBIGUOUS | S0116, S0119 | 2 | 0 | #23, #34, #513 | BASELINE-REUSE | - |
| AMBIGUOUS | S0117, S0120 | 2 | 0 | #33, #34 | BASELINE-REUSE | - |
| AMBIGUOUS | S0122-S0123 | 2 | 0 | #33 | BASELINE-REUSE | - |
| AMBIGUOUS | S0172, S0189 | 2 | 0 | #34, #506, #508 | BASELINE-REUSE | DORMANT-NO-SELECTED-EMITTER |
| AMBIGUOUS | S0194-S0195 | 2 | 0 | #21 | BASELINE-REUSE | - |
| AMBIGUOUS | S0199-S0200 | 2 | 0 | #507 | PROFILE-SELECT | - |
| AMBIGUOUS | S0205-S0206 | 2 | 3 | #505, #506, #508 | PROFILE-SELECT | - |
| AMBIGUOUS | S0208-S0209 | 2 | 5 | #33, #506, #513 | PROFILE-SELECT | - |
| AMBIGUOUS | S0196 | 1 | 4 | #490, #506, #507, #518 | PROFILE-SELECT | - |
| AMBIGUOUS | S0197 | 1 | 2 | #505, #506, #507 | PROFILE-SELECT | - |
| AMBIGUOUS | S0198 | 1 | 2 | #506, #507 | PROFILE-SELECT | - |
| AMBIGUOUS | S0201 | 1 | 4 | #506 | PROFILE-SELECT | - |
| AMBIGUOUS | S0207 | 1 | 0 | #506 | PROFILE-SELECT | - |
| AMBIGUOUS | S0218 | 1 | 2 | #33, #34, #513 | PROFILE-SELECT | - |
| SUPPLIED_FACT_IO_MAPPING | S0007-S0009 | 3 | 2 | #506, #513 | - | - |
| SUPPLIED_FACT_IO_MAPPING | S0100, S0112 | 2 | 2 | #507, #508 | - | - |
| SUPPLIED_FACT_IO_MAPPING | S0114, S0221 | 2 | 2 | #487, #513 | - | - |
| SUPPLIED_FACT_IO_MAPPING | S0125, S0235 | 2 | 2 | #513 | - | - |
| SUPPLIED_FACT_IO_MAPPING | S0234 | 1 | 2 | #490 | - | - |
| COVERED | S0107-S0108, S0126-S0137, S0142-S0145, S0295-S0296, S0305-S0310 | 26 | 0 | #513 | - | - |
| COVERED | S0258, S0261, S0266-S0267, S0287-S0288, S0301-S0304, S0321 | 11 | 0 | #511 | - | - |
| COVERED | S0251-S0252, S0264-S0265, S0297-S0300 | 8 | 0 | #484 | - | - |
| COVERED | S0289-S0294 | 6 | 0 | #481 | - | - |
| COVERED | S0162-S0163, S0178-S0179 | 4 | 0 | #507, #520 | - | - |
| COVERED | S0202-S0204, S0219 | 4 | 0 | #506 | - | - |
| COVERED | S0319-S0320, S0322-S0323 | 4 | 0 | #483 | - | - |
| COVERED | S0253-S0255 | 3 | 0 | #482 | - | - |
| COVERED | S0285-S0286 | 2 | 0 | #485 | - | - |
| COVERED | S0340, S0355 | 2 | 0 | #23, #489, #490 | - | - |
| COVERED | S0324 | 1 | 1 | #513 | - | - |

## 6. De-duplication of the EF3 route entries outside the 122-row packet

Wave 1 slice B reported about 95 EF3 route entries outside the 122-row packet. **Reproduced exactly: 95 field rows** (not in packet slices A, B or C) whose current proposed routes include a planned-EF3 owner: #490 (24), #611 (22), #598 (16), #489 (13), #487 (12), #488 (8). In addition, 19 scanners carry an EF3 primitive proposal, 4 an EF3 field bridge, and 20 commands mention EF3 outside the packet; those are consumer or command rows and are not part of the 95.

Duplicate test (structural only; semantics were not inspected): same field name, role, raw-input set, dependency set, ordering and type. Results:

| Result | Entries |
| --- | --- |
| Distinct (no structural twin in the 95, no same-name row in the packet) | 71 |
| Duplicate candidates: 8 groups of two structurally identical entries (representative + redundant copy) | 16 (8 redundant) |
| Same field name as a row inside the 122-row packet, structure not proved identical (needs review) | 8 |
| Total | 95 |

De-duplicated count: **87 distinct entries** (95 less 8 redundant copies); 79 after also treating the 8 packet-name matches as possible duplicates. Duplicate candidates are not proved duplicates: identical structure can still be two source records that need separate profiles (as with the A6 pairs in wave 1). Role mix of the 95: 69 measurement or nested outputs, 14 quality or count fields, 12 identity or provenance fields. The 22 entries owned by the I/O layer #611 are layer-as-owner entries (representation only, no numerical producer), and the 12 identity or provenance fields are probably envelope metadata rather than producer rows. Only 5 of the 95 are referenced by any consumer bridge (29 consumers, 31 bridge instances), so most are unreachable from the consumer gaps.

Per-entry classification is in the JSON (`ef3_outside_packet_fields`).

## 7. Hygiene corrections needed (findings; no file edited)

`docs/plans/equity-selected-dependencies.json`
1. Four records (#491, #611, #612, #519) still carry `draft_dependency_append_not_applied`, while `AUDIT_ROUTE_PUBLICATION.md` records those four bodies as published and read back. The other seven records have no `publication_status` field at all; the schema is inconsistent.
2. No record for the proposed mean companion edge on #490 other than the conditional closed-story reuse; the hidden #489 edge (wave 1 B3) and the #489 bridge shared by all 25 watchlists (B4) are absent.
3. The #598 observed-population record has no `actual_numbered_dependency`, and the optional #626 raw-operand source from EF4 #492 (B7) is recorded nowhere.
4. No records exist for the four proposed stories (cohort normalization, anchor discovery, retracement level, mean companion), the A2 proposal-only outputs, or consumer-level edges for the 3 adaptive consumers (B6).
5. The #518 conditional reuse edge names closed #102 without a statement of what proof closes it; the 10 pending current-cohort rank items (S0090-S0099) depend on that proof.

`docs/plans/equity-output-ownership.json`
1. The 47-output list has no entries for #626 adaptive outputs, the #490 median or mean companion outputs, the #598 observed-population companion, the #506 rejected-path diagnostic, retracement level or the #513 raw profiles (wave 1 A2, B-slice finding 2). Its 16 #598 entries are declared-universe slots.
2. `proposed_context_and_transport_roles` still says the release adapter task is "unnumbered until allocated" and that EQ212 applies only to EF1, although I/O and worker tasks #609-#622 now exist.
3. Group labels are inconsistent (`B11`, `B12`, `B11/SR04`, `SR03 preserved owner` beside `SR01`-`SR04`).
4. `current_source_heads` differ from the heads recorded in `DELIVERY_LEDGER.md`; the file does not say whether they are a dated snapshot.
5. `supplemental_owner_readback` is a single dated readback for #598; none exists for #626. The milestone title in that readback contains corrupted dash characters (encoding damage).
6. The top-level `ownership_plan_accepted: true` and per-row `planned_ownership_accepted: true` coexist with unaccepted bindings; consider renaming to avoid being read as acceptance. Unit-bearing outputs still say mathematics and API are unfrozen, which is correct and should stay.

## 8. Rows undecidable and why

- All 200 consumers with no field bridge (181 in this table): operand identity is not available publicly; classes rest on primitive proposals only.
- Delivered versus planned for every item routed to #505-#508: field-to-module mapping needs semantics that opaque ids hide.
- Supplied-versus-computed for field items: heuristic from private role labels; the public index offers only the representation-or-supplied flag (one field in this scope).
- The 25 watchlists carry one identical 33-field bridge set; the six watchlists said to have extra direct joins cannot be told apart (wave 1 D-WL). Identical sets also mean the 25 are not 25 independent gaps for producer-demand purposes.
- S0172 and S0189 are declared without a selected end-of-day emitter: whether they belong in the gap count at all is undecided.
- The 3 adaptive consumers: owner #626 exists, but the consumed outputs are unrecorded.
- The 216 representation slots and 33 variants figures, and the 249 field-side figure, were not reconciled with public flags (220 flagged).
- Consumer-to-consumer overlap and shared operand items were not de-duplicated beyond what the cluster table shows.

## 9. Method and limits

Read-only inputs: the public route coverage index, the three wave 1 slice records, `NUMBERED_LAYER_OWNERS.md`, `DELIVERY_LEDGER.md`, the two plan files above, read-only issue state for the numbered owners (closed: #21, #23, #25, #32, #33, #34, #39, #102, #472, #473; all others open), and the owner's private closure material for consumer membership, pending markers and structural field signatures. Only counts, opaque ids, issue numbers and generic class codes are reproduced; profile class codes PC01-PC11 in the JSON are opaque. A scratch script did the counting and is not committed. Opaque-id-to-field-ordinal mapping was checked against all 936 private exact bridges (936 of 936 agree). Confidence is medium for rows with field bridges and low otherwise.

