Source: work/po-rulings-coverage-map-adoption-2026-10-30.md (Product Owner ruling record, 2026-10-30). Verbatim copy follows the blank line; internal, synthetic, pre-release.

# PO rulings: adoption of the 46 adopted_from_parity_check rows, W1-W3, provider names (2026-10-30)

Internal, synthetic, pre-release. Role: Product Owner, Equity Features. Resolves must-fix M4 and flag 2 of `review-core-763-2026-10-30.md` on core PR #763 (head 9900545, map `docs/plans/design-coverage-map.json`, design basis c439067). Inputs: `po-parity-reconciliation-2026-10-29.md`, `po-rulings-coverage-table-2026-10-30.md`, `PARITY_CHECK_EQUITY_2026-10-29.md`.

## 1. What I checked and what I did not

- I read the design line for each of the 46 rows (story rows by the corrected story heading and goal) and checked shipped ids and source on core `967d13d` for a sample.
- Checked by me (design text plus shipped ids or source): 23 of the 46 (marked yes), plus W3. Checks: id existence, field sets (robust.* accepts volume/open/high/low/close only), the status_history output list, period and extended producers, classification fact kinds, absence of z-score, all-time, leverage and dollar-volume outputs.
- NOT individually checked against code (marked no, 23 rows): P12, V5, V13, V14, V17, V18, V19, M16, M20, U4, U5, U7, U12, C10, S1, S2, S3, S6, S8, S9, S10, L3, T4. I adopt these on the parity check plus my reading of the design line. They keep `adopted_from_parity_check`; the first CV1 or Tester touch of any of them re-checks it.
- Not run: no gate, no fixture. Findings are from reading.

## 2. Rulings

1. **Adoption.** I adopt the classifications of the 46 rows as listed in the table, with three status changes (W1, W2, L2 to out_of_library_scope) and W3 changed from implemented to partial. The other 43 rows keep their status (42 partial, V5 out_of_library_scope).
2. **Basis labels.** After this record `asserted.by` is PO for all rows. Rows marked checked yes use `basis: po_ruling`; rows marked checked no keep `basis: adopted_from_parity_check`. Both cite this record in `asserted.record`, `record_ref: section 3 table`. The seed `record_ref` strings hold a double-encoded section sign; the Developer fixes the encoding when rewriting them.
3. **Corrections that do not change status** (Developer, same push as review M2): the rows marked note correction (P2, P30, P38, P39, V5b, S4, U11) get their notes and output lists fixed (calendar.period.*, session.extended.high/low, history.window_high/low, venue_status.aggregate_reason, reference.classification.value). The G6 gap code on P2 and S4 is re-reviewed together with the capability_gaps legend.
4. **Ref corrections** for the rows marked ref correction follow review M2 (its table gives the lines). Status does not depend on them.
5. **W1-W3.** The line 'watchlist matching (W1-W3)' in my reconciliation section 3 was too broad. Final: W1 and W2 out_of_library_scope (confluence engine and mirrored catalogue); W3 partial (VolScore arithmetic ships; retest tolerance and rule evaluation do not). The reconciliation record is not edited; this record supersedes that one line.
6. **Provider names in the verbatim record copy.** Keep verbatim. Reasons: D5 requires verbatim copies; the owner said providers are not our concern; redacting breaks the byte-compare with the source. The no-provider rule stays for the table, schema, tests and generated text only. Changes: (a) `DESIGN_COVERAGE_MAP.md` gets one line: 'Records under docs/plans/records are verbatim historical copies; provider names in them are not part of the table.' (b) The validator scans the map, the doc and generated text, never the records. (c) The BANNED regex stays as it is (internal, acceptable). Nothing else changes.
7. **Final counts** (166 rows): implemented 40 (confirmed 33, provisional 7; two numbers, never summed in one line), partial 44, missing 59, differs 6, out_of_library_scope 17. Extras 11 unchanged. Seed was 41/46/59/6/14: implemented -1 (W3), partial -2 (W3 in, W1, W2, L2 out), out_of_library_scope +3. The validator's expected counts and the pinned baseline (review M3.2) take these numbers.
8. **Not a release claim.** These are classifications of synthetic-data library calculations; no coverage or readiness claim is made.

## 3. Machine table

Columns: design_id | final_status | ruling | reason | checked_by_me (yes = design plus code read; no = design line and parity check only)

| design_id | final_status | ruling | reason | checked_by_me |
|---|---|---|---|---|
| P1 | partial | adopt | Rolling 10s-60m return output absent (true gap); ATR-normalised part is arithmetic on history.return and history.atr but the item mixes both | yes |
| P2 | partial | adopt; note correction | Break/fail/reclaim events are consumer rules (EF9). Note is stale: calendar.period.high/low (iso_week, month, civil_ytd), session.extended.high/low (premarket) and history.window_high/low ship; remove 'no premarket, no YTD' and list these ids | yes |
| P4 | partial | adopt | Daily grid has only history.rsi, history.atr, ema, sma; no daily MACD/ADX/Bollinger/Donchian (EF7) | yes |
| P7 | partial | adopt | Gap size and fill ship; held/reversal outputs absent; premarket mover return ships as session.extended.prior_close_return | yes |
| P11 | partial | adopt | ATR distance is arithmetic but no price z-score or price stdev output exists; z-score half is a real gap | yes |
| P12 | partial | adopt | Intraday-grid only per parity check; design line read, code not checked | no |
| P30 | partial | adopt; note correction | Halt state over supplied events ships. session.venue_status.aggregate_reason exists but is a precedence code, not an exchange reason text; say so in the note | yes |
| P31 | partial | adopt | status_history gives halt_observed boolean and event_count only; no moment output | yes |
| P32 | partial | adopt | resume_observed boolean only; no moment output | yes |
| P33 | partial | adopt | event_count and halt_observed ship; no reasons list | yes |
| P34 | partial | adopt | ssr_on_observed over supplied events; no 10%-from-prior-close computation | yes |
| P35 | partial | adopt | ssr_on_observed boolean only; no moment output | yes |
| P38 | partial | adopt; note correction | history.window_high takes an explicit period; no all-time or since-first-date form; add window_high as an output | yes |
| P39 | partial | adopt; note correction | As P38; the event is a consumer comparison against prior high | yes |
| V5 | out_of_library_scope | adopt | Stateful rising-edge episode counter; my reconciliation section 3 (scanner engine). Design line read only | no |
| V5b | partial | adopt; note correction | adaptive.volume.peak_relative_rate is a time-weighted running baseline, not a session maximum of a median-based multiple. Note wording 'EWMA' should read 'time-weighted' | yes |
| V9 | partial | adopt | cohort.rank and robust.* accept fields volume/open/high/low/close only; no dollar-volume field (G3 correct) | yes |
| V13 | partial | adopt | Retest and dollar-volume baseline missing per parity check; not code-checked | no |
| V14 | partial | adopt | Not code-checked | no |
| V17 | partial | adopt | Top-K by notional vs threshold count; not code-checked | no |
| V18 | partial | adopt | All-print tick proxies exist (tape.tick.*); not code-checked beyond id existence | no |
| V19 | partial | adopt | Trailing windows only per parity check; not code-checked | no |
| M16 | partial | adopt | session.clock.early_close ships; adjacency absent (EF11) | no |
| M20 | partial | adopt | robust.percentile_rank works on supplied index bars; no source (EF13 adapter). Not code-checked | no |
| U4 | partial | adopt | Generic classification string gate; label-set test is consumer; no source adapter. Not code-checked | no |
| U5 | partial | adopt | As U4 | no |
| U6 | partial | adopt | No leverage or inverse concept anywhere in the feature code (grep empty) | yes |
| U7 | partial | adopt | As U4 | no |
| U8 | partial | adopt | robust.median field set excludes dollar volume (verified in source); EF8 | yes |
| U11 | partial | adopt; note correction | universe_membership is an accepted fact kind of the classification producer, so reference.classification.value is a usable output; list it (outputs currently empty) | yes |
| U12 | partial | adopt | Composite of U1 (out of scope), U8 and an ETP flag; pieces partial. Not code-checked | no |
| C10 | partial | adopt | reference.gate.action_state is admission over declarations; no five-state vocabulary. Not code-checked | no |
| S1 | partial | adopt | Seven geometry outputs only; named formations deferred to EF14 owner decision. Not code-checked | no |
| S2 | partial | adopt; ref correction | Swing primitives only; chart-structure presets EF14. Ref belongs to EQ-03 :87 (story title read) | no |
| S3 | partial | adopt; ref correction | Daily-grid indicators absent (EF7). Ref belongs to EQ-04 :109 (story title read) | no |
| S4 | partial | adopt; note correction | Event rules are consumer. Note 'no 3w/6w/YTD/premarket ids' is stale: window_high/low, calendar.period.*, session.extended.high/low ship; list them | yes |
| S6 | partial | adopt; ref correction | See P11. Ref EQ-06 :150 | no |
| S8 | partial | adopt; ref correction | Primitives only; ranking banned client-side. Ref EQ-01 :28 | no |
| S9 | partial | adopt; ref correction | See V6-V14. Ref EQ-07 :171 | no |
| S10 | partial | adopt; ref correction | Ratios ship, thrust predicates consumer. Ref EQ-08 :192 | no |
| W1 | out_of_library_scope | changed from partial | Design WL-01 is the confluence engine (group assignment, scoring, 2-group minimum). My reconciliation section 3 puts watchlist matching out of library scope; shipped inputs do not make the item partial. Inputs stay as evidence | yes |
| W2 | out_of_library_scope | changed from partial | Design WL-02 is the mirrored bearish catalogue and monitor: rule engine, same reasoning as W1 | yes |
| W3 | partial | changed from implemented | Design WL-03: VolScore is arithmetic on shipped outputs, but the item also carries the retest tolerance and relative_strength/weakness rule evaluation. Retest is missing (V13) and thresholds are rule engine. Section 3 'W1-W3' was too broad for the VolScore part, so not out of scope either | yes |
| L2 | out_of_library_scope | changed from partial | Design SC-05 MFE/MAE and benchmark alpha engine; my section 3 lists MFE/MAE per-candidate outcomes as out of scope and the design bans them (WL125). Elapsed-horizon labels remain a separate primitive | yes |
| L3 | partial | adopt; ref correction | Library keeps unavailable states and evidence rows; inspector UI is consumer. Ref SC-06 :192 | no |
| T4 | partial | adopt | Registries give id, unit, version, minimum period, digest, refusals; no S/E/M/V/A flags. Not code-checked | no |
| T5 | partial | adopt | Incremental accumulators exist for session bars/trades only, no indicator series publisher; design says a worker publishes the series | yes |
