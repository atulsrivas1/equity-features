# EQ164 audit findings: selected slice C (EF8-only rows)

Findings only. Nothing here is acceptance, Ready, or a contract change. Records are in [EQ164_SELECTED_C.json](EQ164_SELECTED_C.json). Opaque ids only.

## Scope

Rows of the selected-scope components manifest whose proposed owners all have planned release EF8: 36 rows, 26 fields and 10 consumers. Rows containing EF1, EF2, EF3 or EF4 are covered by other slices.

Row ids taken:
- Fields (26): F0715-F0720, F0287, F0288, F0291, F0292, F0293, F0296, F0297, F0303, F0289, F0290, F0294, F0295, F0298, F0299, F0300, F0301, F0343-F0346.
- Consumers (10): S0090-S0099.

## Counts by classification

| Classification | Rows |
| --- | --- |
| DELIVERED_ON_MAIN | 0 |
| COVERED_BY_PLANNED_PRODUCER | 21 |
| NEEDS_OPERAND_PRODUCER | 10 |
| AMBIGUOUS_OR_CONFLICTING | 5 |
| CANDIDATE_EXCLUSION | 0 |

- COVERED (21): F0715-F0719 (#519), eight stateless predicates (#518), eight latched transitions (#520).
- NEEDS_OPERAND_PRODUCER (10): S0090-S0099.
- AMBIGUOUS (5): F0720, F0343-F0346.

## Issue checks (read-only)

All numbers exist, are open and match the numbered-owner map: #518, #519, #520, #521 (milestone 28), I/O #621 and worker #622 (milestone 28), and #626 (EF3 library, milestone 24). No mismatches. #521 owns no row in this slice. Closed #102 appears only as a conditional reuse. The route coverage index agrees with the components manifest for all 36 rows, and no id is duplicated.

The 47-output ownership manifest has no EF8 owner and carries no opaque ids, so none of these rows can be cross-checked there. This is expected, not a contradiction. The selected-dependencies manifest carries edges for #518 (conditional #102), #519 (optional #626) and #520 (#505-#507, preserving #518 and #519). It has no per-row entries and none for #521.

## Key findings

1. **Cohort normalization (S0090-S0099) has no named operand producer.** Each row's prior primitive proposal is the policy owner #518 itself. The cohort normalization step sits in a catalogue story. #518's own text says a separately reusable scalar needs a narrowly numbered producer, and none exists. The #102 reuse is conditional and unproved, and #102 is closed. Confidence: low-medium, because the operand definitions are private and were not copied.
2. **Anchor discovery (F0343-F0346) may be a hidden numerical producer.** The role reads "discovery or state projection" and is not decided per row. #520 is a lifecycle story, and #507 only consumes a supplied anchor. EF1 anchor arithmetic is on main.
3. **F0720 has two primary owners (#519 and #520).** The seam is not specified. The plan correctly requires both, and no reverse EF8 gate is added.
4. **F0715-F0719 optionally depend on #626.** The manifests do not say which of the five rows consume it. No blanket #626 or #490 gate follows.
5. **No early primitive is wrongly gated by EF8.** All edges run EF1/EF3 to EF8. The one risk is finding 2: if anchor discovery is needed by an earlier primitive, an EF8 owner would gate it.
6. **Row-level operands are unnamed for all 36 rows.** Stateless predicate and latched-transition rows (16) are covered at story level only. Their operands are plausibly EF1 #505-#507, but this is unconfirmed. This is part of the 245 consumer operand gaps and is not reduced by this audit.
7. **Nothing in this slice is delivered.** No EF8 module exists on main. The generic policies module is not shown to be compatible.

## Coordinator decisions needed

1. For S0090-S0099: is current-cohort normalization a separately numbered producer, or is exact #102 reuse proved? Either way, which story owns it?
2. For F0343-F0346: is first-crossing anchor discovery a pure primitive that needs its own numbered producer, or lifecycle state owned by #520?
3. For F0720: which of #519 or #520 is the single publishing owner, with the other named as an operand producer?
4. For F0715-F0719: which rows actually consume #626, so the optional edge becomes explicit per output?

## Recommended next stories

- A narrowly numbered current-cohort normalization producer, if decision 1 says so, with its population, ties, scaling and denominator contract and independent fixtures.
- A row-level operand mapping for the 16 predicate and transition rows, naming exact EF1 producers.
- A per-output seam note for F0720.
- Independent full-result fixtures for each row's owning story before Ready.

## Not verified

- Private operand and formula definitions: ids are opaque and were not copied.
- Issue bodies beyond #518, #519 and #520, and project status.
- Any numerical semantics, rights or fixtures.
