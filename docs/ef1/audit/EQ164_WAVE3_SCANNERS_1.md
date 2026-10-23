# EQ164 wave 3, story W3-B1: ambiguous scanner consumers, first half

Findings only, dated 2026-10-22. Every statement is an adjudicated finding or a proposed resolution. Nothing here is accepted: no mathematics, API, source, rights, consumer-equivalence or Ready status, and no tracker issue was created or edited. Opaque ids (C####, F####, S####, W##) and public issue numbers only. Records: [EQ164_WAVE3_SCANNERS_1.json](EQ164_WAVE3_SCANNERS_1.json). Inputs: [EQ164_WAVE2_X4](EQ164_WAVE2_X4.md), [EQ164_WAVE2_DECISIONS](EQ164_WAVE2_DECISIONS.md), the public plans, `NUMBERED_LAYER_OWNERS.md`, `DELIVERY_LEDGER.md`, the module definitions on main, and the owner's private read-only closure material (not reproduced).

## 1. Scope

X4 lists 107 scanners whose primary gap class is ambiguous. Sorted by opaque id ascending, the first ceil(107/2) = 54 are this story.

- **Id range: S0106 to S0197, 54 ids** (non-contiguous: only ids that are ambiguous scanners are included). The other agent takes the remaining 53 ids that sort after S0197.
- Policy owner of every row: #518 (EF8 policy), with I/O #621 and worker #622.
- Structure of the 54: 18 rows from one shared category evaluator (S0106, S0109-S0111, S0115-S0124, S0138-S0141); 32 rows from one shared level evaluator (S0158-S0161, S0164-S0177, S0180-S0193); 2 close-location rows (S0194, S0195); 2 gap-classification rows (S0196, S0197).

## 2. Method and the main change from X4

X4 could not name operands for 200 of 245 consumers because the public bridges are lexical. Here the operand lists were obtained by reading each consumer's call chain in the private closure material (what the evaluator is handed, which context and row fields feed it, which gates it applies) and mapping each handed input to the opaque field inventory by structure and group, then reading the public route of that field for its owner. Result: all 52 non-dormant rows now have a named F#### operand list (62 distinct fields, 315 operand instances). Operand identity is therefore source-read, but no binding is accepted and no field-to-semantics mapping is verified by an independent reviewer.

Producer statuses used: DELIVERED_ON_MAIN (a capability on main plausibly produces the operand; exact binding, profile and units unaccepted, always qualified in the JSON), PLANNED_NUMBERED (a numbered story owns it in the public routes; includes closed baseline stories whose reuse is unproved), PROPOSED_NEW_STORY (none needed here), UNCOVERED_GAP.

## 3. Counts

| Resolution class | Scanners | Ids |
| --- | --- | --- |
| RESOLVED_ALL_OPERANDS_COVERED | 40 | S0106, S0109-S0111, S0122-S0123, S0158-S0161, S0164-S0171, S0173-S0177, S0180-S0188, S0190-S0197 |
| RESOLVED_WITH_GAPS | 12 | S0115-S0121, S0124, S0138-S0141 |
| STILL_AMBIGUOUS | 2 | S0172, S0189 |
| Total | 54 | |

Confidence: 52 medium, 2 low (the two dormant rows). No row is high: operand identity is source-read but unreviewed, and the producer mapping rests on proposed routes.

Operand instances by producer status: 48 DELIVERED_ON_MAIN (qualified), 267 PLANNED_NUMBERED, 0 PROPOSED_NEW_STORY, plus 16 gap instances (UNCOVERED_GAP) on 12 scanners.

Operand gaps (all on RESOLVED_WITH_GAPS rows):

| Gap code | Meaning | Scanners | Candidate absorbing story |
| --- | --- | --- | --- |
| G-RANGE-FALLBACK | a range-based volatility fallback applies when the baseline volatility operand is absent; no owner | 12 (S0115-S0121, S0124, S0138-S0141) | variant under #34, or a new story |
| G-RECURSIVE-AVERAGE | a recursive trend average over supplied daily closes; no daily-series owner (only an intraday family has recursive averages) | 2 (S0117, S0120) | #472 if series-agnostic, else new story |
| G-DISPERSION-OPERAND | dispersion of the trailing close window is not an exposed output of the band family | 2 (S0121, S0124) | #473 (expose it, or prove a fixed band multiple) |

STILL_AMBIGUOUS evidence missing (S0172, S0189): the selected end-of-day source never emits these two declarations, so no operand set exists; what is missing is an owner decision whether a declaration with no selected emitter is a consumer at all (X4 raised the same question).

## 4. Per-story demand

Distinct scanners (of 54) whose named operands route to the story, operand instances, and how many of those instances are planned versus delivered-capability. Gap column: scanners with an UNCOVERED_GAP that the story would have to absorb.

| Story | State | Scanners | Instances | Distinct fields | Planned | Delivered (qualified) | Gap scanners to absorb |
| --- | --- | --- | --- | --- | --- | --- | --- |
| #506 | open, EF1 | 51 | 145 | 30 | 117 | 28 | 0 |
| #34 | closed baseline | 45 | 45 | 1 | 45 | 0 | 12 (G-RANGE-FALLBACK) |
| #507 | open, EF1 | 32 | 32 | 2 | 30 | 2 | 0 |
| #508 | open, EF1 | 28 | 28 | 1 | 28 | 0 | 0 |
| #570 (I/O) | open, EF1 | 22 | 22 | 2 | 4 | 18 | 0 |
| #505 | open, EF1 | 8 | 10 | 3 | 6 | 4 | 0 |
| #23 | closed baseline | 7 | 8 | 4 | 8 | 0 | 0 |
| #33 | closed baseline | 6 | 6 | 1 | 6 | 0 | 0 |
| #513 | open, EF4 | 6 | 6 | 6 | 6 | 0 | 0 |
| #493 | open, EF4 | 3 | 6 | 4 | 6 | 0 | 0 |
| #473 | closed baseline | 2 | 6 | 3 | 6 | 0 | 2 (G-DISPERSION-OPERAND) |
| #518 (policy) | open, EF8 | 3 | 3 | 3 | 3 | 0 | 0 |
| #490 | open, EF3 | 1 | 2 | 2 | 2 | 0 | 0 |
| #520 | open, EF8 | 2 | 2 | 2 | 2 | 0 | 0 |
| #472 | closed baseline | 0 | 0 | 0 | 0 | 0 | 2 (G-RECURSIVE-AVERAGE) |

Reading: EF1 stories #506, #507, #508 and #570 carry almost all of the demand (the level family is EF1 work: 30 of the 62 fields are #506). The one cross-cutting dependency is the daily volatility baseline F0351 under closed #34, needed by 45 of 54 rows (12 required plus fallback gap, the rest optional). Its public reuse disposition is "distinct versioned profile if original semantics retained" and reuse is not accepted. No row needs any of the seven stories proposed in the wave 2 decisions.

Where the X4 primitive proposals are not backed by operand evidence (instances): #513 on 8 rows (S0115, S0116, S0118, S0119, S0138-S0141; a derived displacement over supplied closes may still belong there but no operand field points to it), #25 on 3 (S0106, S0110, S0111; the operand fields route to #493), #508 on 4 (S0158-S0161), #21 on 2 (S0194, S0195; the operands are session extrema and the volatility baseline, not a bar count). Treat these proposals as unsupported until an owner confirms.

## 5. Patterns

1. **One evaluator, one context mapping (18 rows).** The category rows all receive the same inputs: a daily bar series (F0338 history plus current row F0147-F0150, F0161), the volatility baseline F0351, session VWAP F0189 and row aggregates for quotes F0153/F0145, book F0155/F0171 and trades F0141. Differences are only which of them a rule reads. A single typed input contract for that evaluator resolves the 18 together.
2. **One level evaluator (32 rows plus 2 close-location).** Every rule takes the same price and session extrema (F0188, F0190, F0191), optional volatility baseline F0351 and prior-close inputs (F0206, F0218), and differs only in the reference-level pair: F0309-F0320 (rolling windows and year-to-date), F0321-F0324 (prior week and month), F0275/F0276 (prior session), F0267/F0268 (extended-hours extremes) or derived-from-distance levels F0212-F0217 (3, 6 and 52 week). The 32 therefore reduce to 13 level-pair choices times two directions.
3. **Delivered capability exists for the level operands** (period and daily-observation high/low, extended-phase extremes, regular-open and gap-endpoint capabilities on main), but the window and profile selection that binds them to each rule is unproved. This is what is left of the "profile choice unresolved" ambiguity for the level rows.
4. **Baseline reuse is the real ambiguity of the category rows.** 52 of 54 rows carry a baseline-reuse pending marker in X4; the operand evidence shows that for the quote, book and trade-size rows the field owner (#493, #23) differs from the proposed primitive owner (#25), and that the volatility, trend-average and band operands depend on closed baselines whose exact profile is unproved.
5. **Two dormant declarations** (S0172, S0189) are in a family where the other half of each pair is emitted; only the one direction per extreme exists in the selected source.
6. **Predicate flags are policy-owned inputs.** Five rows (S0158-S0161, S0196) take predicate flags (F0287-F0291) whose public owners are #518/#520, the same layer as the consumer. Whether these are recomputed by policy from the numeric levels or retained as supplied flags is open (D5).

## 6. Decisions needed

| Id | Rows | Exact question |
| --- | --- | --- |
| D1 | 12 | Is the range-based volatility fallback (used when the daily volatility baseline F0351 is absent) retained as source behavior? If yes, is it a versioned variant under #34 or a new story; if no, is each rule explicitly unavailable when F0351 is absent? |
| D2 | 2 (S0117, S0120) | Which story owns a seeded recursive trend average over daily closes with a minimum-observations readiness: is closed #472 (intraday family) series-agnostic and reusable, or is a new daily-series story needed? |
| D3 | 2 (S0121, S0124) | Does #473 expose the trailing-window dispersion (or the standardized distance) as an output, or is a fixed band multiple proved so that it can be derived from F0417/F0418? |
| D4 | 3 (S0106, S0110, S0111) | Which owner is authoritative for the session-aggregate quote and book operands (F0153, F0155): #493 as the field routes say, or closed #25 as the primitive proposal says? Is the session-average profile inside #25's baseline? |
| D5 | 5 (S0158-S0161, S0196) | Are the predicate flags F0287-F0291 recomputed by policy (#518/#520) from the numeric levels and price, or retained as supplied flags? Which side owns touch, close-beyond and strictness semantics? |
| D6 | 2 (S0172, S0189) | Are declarations with no selected emitter retained as consumers (and with which operands) or retired from the consumer inventory? |
| D7 | 2 (S0194, S0195) | Is the #21 primitive proposal withdrawn in favor of #506 session extrema plus the #34 baseline? |
| D8 | 2 (S0196, S0197) | The planned gap measure F0272 is a percent-style field while the delivered gap capability is a fraction: which unit is the contract, and is the regular-open owner #506 or #505 (F0271 has both routes)? |
| D9 | 30 | Level windows: are the N-session and calendar-period reference levels (F0275/F0276, F0309-F0324) bound to the delivered period/daily-observation outputs with a fixed inclusion rule for the current session, and are F0212-F0217 kept as distance fields with the reference derived, or replaced by direct levels? |
| D9H | 18 | What daily-history profile (length, adjustment, completed-only or current-inclusive) does the supplied slot F0338 under #570 guarantee for the category evaluator? |

## 7. What could not be verified

- Independent review: all operand lists come from one reader of the private call chain; no second review, no fixture, no execution.
- Whether each planned field's own semantics equal what the rule consumes (for example the snapshot price versus a close, or the aggregate window of the quote and book fields); only role and owner were checked.
- Delivered status is capability-level: the mapping from F#### to a delivered feature id was made from names and ledger entries and is marked qualified; none is a verified join.
- Closed baseline stories (#21, #23, #25, #33, #34, #472, #473): whether their accepted outputs equal the profiles needed here (windows, seeds, inclusion of the current observation) is unproved, as in X4.
- Eligibility, minimum price/volume and status gates attach to the same rows as row-level policy inputs; they were noted but not made operand gaps.
- The mean companion, cohort-normalization, retracement-level and other proposed stories are not needed by this half; the other half may differ.
