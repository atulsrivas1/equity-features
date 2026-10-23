# EQ164 wave 3, story W3-A: the 25 watchlist consumers

Findings only, dated 2026-10-22. Every statement is an adjudicated finding or a proposed resolution. Nothing here is accepted: no mathematics, API, source, rights, consumer-equivalence or Ready status, and no tracker issue was created or edited. Opaque ids and public issue numbers only. Records: [EQ164_WAVE3_WATCHLISTS.json](EQ164_WAVE3_WATCHLISTS.json). Builds on [wave 2 X4](EQ164_WAVE2_X4.md) and the [wave 1](EQ164_WAVE1_DECISIONS.md) and [wave 2](EQ164_WAVE2_DECISIONS.md) decisions.

## 1. Summary

| Item | Result |
| --- | --- |
| Watchlists | 25 (W0001-W0025) |
| Common operand set | 33 fields: 32 common-validation fields plus 1 membership-refusal field; the 2 eligibility-tag fields are already inside the 32 |
| Predicate operand sets | 3 to 19 fields per watchlist, 25 distinct fields in union, 17 distinct sets |
| Predicate operands outside the common 33 | 0 for every watchlist |
| Common fields read by no predicate | 8 (F0431, F0432, F0433, F0442, F0451, F0455, F0460, F0464) |
| Proposed resolution | 23 RESOLVED_COMMON_OPERANDS, 2 RESOLVED_WITH_OWN_OPERANDS (W0014, W0015), 0 STILL_AMBIGUOUS; confidence medium for all 25 |
| The six with extra direct joins | Not identifiable (section 4) |
| Operand gaps | 0 of 33 lack a planned owner; 3 non-field policy inputs shared by all 25 have no mapped owner |
| Delivered with a proven binding on main | 0 of 33 |

## 2. How the operands were resolved

The private exact field bridge keeps, per watchlist, five lists of lexical field accesses (the retained functions' accesses, with helpers and fixed group sets expanded, no predicate evaluated): predicate reads, common validation, membership refusal, eligibility tag, and group-confluence members. Field keys were mapped to F#### by position in the private 721-field inventory (position plus one). Check: the resulting 33 equals the 33-field set in the public wave 2 records exactly (33 of 33; F0461 is absent from both).

Adjudicated findings:

1. **The common set is identical for all 25.** The validation list (32 fields), refusal list (1 field) and tag list (2 fields) are the same for every watchlist. The tag fields (F0434, F0455) are also in the validation list, so the union is 32 + 1 = 33.
2. **Predicate operands are always a subset of the common 33.** Per-watchlist predicate sets range from 3 to 19 fields; none reaches outside the common set. So "common versus per-key" does not change the field operand set: the total field dependency of every watchlist is the same 33 fields. Per-key sets only record which of the 33 a predicate reads directly, which matters for a minimal-prerequisite view (the public text already says the 33 are affected admission scope, not 25 proven minimal predicate prerequisites).
3. **Eight common fields are validation or gating only** (read by no predicate): F0431, F0432, F0433, F0442, F0451, F0455, F0460, F0464. The other 25 are read by at least one predicate.
4. **Watchlist-to-watchlist edges.** Two watchlists are composites over other watchlists: W0014 over 7 (W0001, W0004, W0007, W0012, W0018, W0022, W0024) and W0015 over 6 (W0008, W0009, W0013, W0017, W0023, W0025). These are consumer-to-consumer dependencies, not fields, and are absent from the public records. Their predicate field sets (19 and 18) contain every member's predicate fields. This is why they are classed RESOLVED_WITH_OWN_OPERANDS.
5. **Three shared non-field policy inputs.** All 25 also consume three non-field policy inputs (an eligibility configuration, a product classification, and a pinned override revision or explicit unknown). They have no F#### id and are not in the public operand lists; no producer for them is identified in the public plans (decision W3A-4).
6. **Identical predicate sets.** Eight pairs have identical predicate field sets: W0001/W0008, W0003/W0016, W0005/W0006, W0012/W0013, W0017/W0018, W0020/W0021, W0022/W0023, W0024/W0025. This is consistent with paired.

Confidence is medium, not high, for three reasons: the bridge is lexical (field accesses, not proven numerical need; F0455 is validation-only per the lexical bridge); the W#### to private key mapping is by sorted-key position and cannot be confirmed from public data (supporting sign: the paired sets and the composite membership lists are consistent under it); and nothing is numerically accepted.

## 3. Producer status of the 33 common operands

Status vocabulary: delivered on main (DELIVERY_LEDGER), planned numbered story (NUMBERED_LAYER_OWNERS), proposed story (wave 2 decisions), uncovered gap.

| Fields | Count | Owner | Status |
| --- | --- | --- | --- |
| F0435-F0446, F0449, F0450 | 14 | closed #32 / #33 | Closed baseline stories; reuse conditional and unproved (baseline dispositions); planned EF4 |
| F0458, F0459 | 2 | closed #39 | Closed story; operand route unresolved |
| F0431, F0447, F0448, F0451, F0453, F0454, F0462 | 7 | #513 (EF4) | Planned numbered story, open, not delivered |
| F0432, F0434, F0460 | 3 | #508 (EF1) | Planned numbered story; #508 has delivered reference slices on main but no field-level binding is proven |
| F0463, F0464 | 2 | #506 (EF1) | Planned; public class is EF1 delivery undetermined (period slices exist on main, binding unproven) |
| F0455 | 1 | #489 (EF3) | Planned numbered story, open |
| F0456, F0457 | 2 | #512 (EF5) | Planned numbered story, open |
| F0452 | 1 | #490 (EF3) | Planned in #490; wave 1 B3 and wave 2 proposed story 4 give it a separate mean-companion story (proposed, not created) |
| F0433 | 1 | #621 (EF8) | Planned I/O representation slot |

Totals: 0 delivered with a proven binding, 33 planned or proposed, 0 without an owner. The ledger has no field-level entry for any of the 33, so "delivered" cannot be asserted even for the five fields whose owners (#506, #508) have shipped slices. Because the set is common, every watchlist is blocked by the same ten owners (#32, #33, #39, #489, #490, #506, #508, #512, #513, #621); the per-watchlist predicate view (in the JSON) is smaller.

## 4. The six watchlists with extra direct predicate joins

**The private material cannot identify them.** No watchlist has a predicate field join outside the common 33, so the bridge does not single out six as "additional". Several six-member sets exist, so any choice is a guess:

- Set A: W0001, W0008, W0014, W0015, W0020, W0021 are exactly the readers of F0452 and F0453 (the mean-companion row and a companion operand). They form three pairs. Confidence that A is the published six: low.
- Set B: W0002, W0014, W0015, W0017, W0018, W0019 are exactly the readers of F0435 and F0441. Not a set of pairs.

What the evidence does support: whichever six is meant, their extra joins fall inside the common 33 and do not change any operand set. They matter only for minimal-prerequisite scoping.

## 5. Is the #489 baseline edge genuinely required?

The only #489 field in the set is F0455. Findings: (a) it is validation-only per the lexical bridge; (b) it is one of the two eligibility-tag fields; (c) it is read by no predicate in any of the 25. So the edge is genuinely required by the common validation (a watchlist result is withheld when validation fails) and is not required by any predicate. It is not merely lexical, but it is a validation-only dependency: a producer, or a supplied quality-flagged value, is needed with no numerical use in membership. Confidence: medium (lexical bridge only; no semantic acceptance). Wave 1 decision B4 / D-WL (record the #489 bridge as a selected override) is recorded as a decision in [EQ164_WAVE1_DECISIONS.md](EQ164_WAVE1_DECISIONS.md) but is NOT yet applied in the public plans: no watchlist's selected_scope_component_overrides contains #489, and F0455's route shows selected_scope_override_applied false. Whether F0455 blocks all 25 stays open (W3A-5). The same holds for the other seven validation-or-gating-only fields.

## 6. Decisions needed (exact questions)

- **W3A-1.** Operand model: record every watchlist with the common 33-field set as a shared profile, plus an optional per-watchlist predicate subset for minimal-prerequisite scoping? Proposed: yes; the common set is authoritative for admission and per-key subsets are informational.
- **W3A-2.** Is the published "six with additional direct joins" Set A, Set B or another set? If the owner cannot say, should the statement be retired in favor of the finding that no watchlist reads outside the common 33?
- **W3A-3.** Should W0014 and W0015 record explicit watchlist-membership dependencies (7 and 6 members) as consumer-to-consumer edges in the public plans?
- **W3A-4.** Which stories own the three shared non-field policy inputs (eligibility configuration, classification, pinned override revision)? #518 is the catalogue and policy owner in the route coverage, but no story is mapped to these three shared policy inputs, so none is assumed here.
- **W3A-5.** Is F0455 (#489) a required supplied or computed validation input, or may validation treat it as a quality-flagged optional input? This decides whether the #489 edge blocks all 25.
- **W3A-6.** Confirm the opaque W-id to watchlist mapping (sorted-key position) with the owner, since it cannot be checked from public data.

## 7. Limits

Lexical field accesses only; no predicate was evaluated and no numerical, source or rights claim is made. The W-id mapping and the identity of the six are not publicly verifiable. The 3 non-field policy inputs could not be mapped to F#### or C####. Delivered status was taken from the ledger only; no code on main was inspected for field-level bindings. The extra asynchronous route outside the 25 is not part of this audit.
