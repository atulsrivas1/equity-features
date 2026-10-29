# EF5 freeze evidence (price structures and patterns contract)

Status: evidence record for `ef5-price-structures-1`. Docs only. Based on main after PR #735 merged (squash 24ace1e); docs/ef5 content checked at the #735 head 2d57e9e, identical to the 04b81ff read-through head.
Freeze verdict: **frozen pending merge** (of this PR). Tester recompute 0 discrepancies (88 sampled fixtures/refusals of the original set plus TD21 and RF52), D1-D5 fixed and re-reviewed, PQ-1 ruling applied with FX-1 (TD21) and FX-2 (RF52) added, docs review clean, gates pass.

Evidence list: second-author recompute at 50ae18c (88 fixtures, 280 values, 0 discrepancies); PO read-through READY TO FREEZE at 04b81ff; tester recompute seed 20261028, 0 discrepancies (section 2); tester recompute of TD21 and RF52 from the md only, 0 discrepancies (section 6); independent docs review clean; gates pass. **Outstanding: the second-author reviewer's recompute of TD21 and RF52 (coordinator will have the reviewer cover it).**

## 1. Evidence summary

| Evidence | Result |
|---|---|
| Second-author recompute (reviewer, PR #735 head 50ae18c) | approved: 88 result fixtures, 280 values, 0 discrepancies; refusals single-fault; tamper test failed the expander as required |
| PO read-through at 04b81ff | READY TO FREEZE |
| Tester recompute (this record, section 2) | 12 of 88 result fixtures (141 outputs checked by hand against md formulas) and 6 of 51 refusals: 0 discrepancies |
| Independent docs review (section 3) | first pass: 1 stale-text defect (D1) and 4 doc-gap findings (D2-D5), all fixed; re-run clean |
| Gates (section 4) | verify_ef5_fixtures PASS, check_equity_delivery_replan PASS, pre_merge_check 17 of 17 PASS (3 installed-only SKIP) |

## 2. Tester recompute

Method: seed 20261028 (`random.Random(20261028)`), stratified sample drawn in order: 3 of 24 candle, 2 of 17 structure, 3 of 20 technical, 4 of 27 known_at, 6 of 51 refusals. Inputs (slots, params, K, target) read from the JSON fixture; every expected value, status, reasons, expected/observed counts and witness list derived from the formulas and rules in PRICE_STRUCTURES_CONTRACT_PROPOSAL.md only. The expander and any other reviewer's recompute were not read. Float64 and hex of every sampled exact value were also checked as float(Fraction) (no mismatch across all 88 fixtures).

Sample: CD18, CD20, CD23, SD02, SD07, TD02, TD16, TD18, KA01, KA05, KA09, KA27; RF14, RF15, RF30, RF38, RF39, RF43.

| Fixture | Recomputed vs fixture |
|---|---|
| CD18 / CD20 (CD07 data) | body 8/10 = 4/5, upper 1/10, lower 1/10, doji false (80 <= 10 false), inside false, bullish true, bearish false; CD18 slot 2 ignored; CD20 witnesses cut to slot:1. Match |
| CD23 | R=16, B=5: body 5/16, upper 1/16, lower 10/16 = 5/8, doji false, inside false (equal high), both engulfing false. Match |
| SD02 | high s=1: 9>10 false; low 5<8,7 true; last high none (no_eligible_observations, 3/3); last low 5 at slot 1, witnesses 1,2,0. Match |
| SD07 | slot 0 gap: last swing outputs governed_gap, expected 5 observed 4; confirmations false/false available 3/3. Match |
| TD02 | count (12-12)=0 + (12-10)=+1 = 1; velocity 0; acceleration 0; session (12-10)/10 = 1/5; witnesses 4,0,1,2,3. Match |
| TD16 | v_t = 1/3030, v_(t-1) = -1/6120, a = 61/7417440, session 3/100, count +1; witnesses truncated to 2 (3,1 / 3,0). Match |
| TD18 | empty target: all four no_eligible_observations; observed 2/1/1/3 of 3/2/2/4. Match |
| KA01 | null target ka: unknown_availability, observed 0 (one-bar) and 1 (two-bar). Match |
| KA05 | ka 99 revision known, values equal CD07. Match |
| KA09 | one-bar outputs future_knowledge; two-bar outputs both reasons, observed 0. Match (see D2 on reason order) |
| KA27 | observed 1 / 0 / 0 of 3 / 2 / 2, both reasons. Match |
| RF14, RF15, RF30, RF38, RF39, RF43 | codes INVALID_SCHEMA, INVALID_SCHEMA, INVALID_CONFIG, UNKNOWN_FEATURE, INVALID_UNIT, UNSUPPORTED_CAPABILITY; stages and single faults match the md table. The md does not itself define the scale bound (RF39) or the restore capability (RF43): see D3. Match as to code and stage |

Discrepancies: 0.

## 3. Independent docs review (docs/ef5/*.md against JSON, EF3/EF4 conventions)

Parity checked programmatically: all 61 CD/SD/TD rows (description and hand_check), 51 RF rows (code, stage, base, fault), 15 headers (dtype, unit, producer, availability) in both md files, tie table, fail-closed driver lists, counts 24/17/20/27/51 and 12 distinct error codes: no difference. Conventions: known_at (== K known, null unknown_availability, later future_knowledge), slash units, capability matrix present with every source unverified, no defaults ledger: consistent with EF3/EF4.

First-pass defects, all FIXED in this PR (text only) and re-reviewed clean (md/json parity re-run: 0 differences over 61 result rows and 51 refusal rows; verify_ef5_fixtures unchanged):
- **D1 stale text (fixed: json status now records PO-2 and PO-7 accepted 2026-10-28)**: `docs/ef5/EF5_SHARED_AMENDMENT.json` line 3 status says "pending PO ruling PO-2"; the md (line 3) records PO-2 and PO-7 accepted 2026-10-28. md/json parity break; fix the JSON status.

Findings (non-blocking, fix or accept):
- **D2 (fixed: md line 108 now states lexical retained order, why KA09/KA18/KA27 are as pinned, and the reason-to-status map)** reason order: PRICE_STRUCTURES md line 108 lists a precedence but does not say retained reasons are listed in lexical order (EF4 md line 83 does). Fixtures KA09/KA18/KA27 list `future_knowledge` before `unknown_availability`, which reads as contradicting the line 108 order. Add the lexical-order sentence and the reason-to-status map (missing_input, incomplete_coverage, not_applicable), which only the JSON shows.
- **D3 (fixed, then PQ-1 ruled and applied: new md section 'Shared rules and terms'; scale 0..18 is the shared PriceUnit, currency letters, update/restore, epoch_profile and the v1 adjustment labels are stated; the label mismatch with the shared AdjustmentSpec is raised as PO question PQ-1, not decided)** undefined terms in refusals (lines 276-290 area, RF24-RF43)**: price scale bound (RF39: 19), currency spelling (RF40), the v1 adjustment vocabulary (RF41), unsupported update/restore (RF42, RF43) and epoch_profile `carry` (RF20) are not defined in the md; they rely on shared EF3/EF4 text. Add one sentence citing it.
- **D4 (fixed: glossary in the same section)** unexplained terms: READY, R17, E1-E9, C8-C10, EQ numbers and "slot clock" are used without a glossary line (lines 7, 154, 160).
- **D5 (fixed: stated in the md section and the amendment md/json)** EF4 unit cross-reference: md line 25 and the amendment say underscore forms appear on no header; EF4_LEDGER_APPLICATION.md section 2 defers EF4's slash migration, so EF4 headers keep underscore spellings for now. State this asymmetry once.
- Expected freeze-time text (not defects): "not frozen" wording at md lines 3, 344, 352 and JSON `status`/`coordinator_freeze` must change only when freeze is declared.

## 4. Gate commands

Environment: the pinned venv `wt-ef4-venv` (mypy 1.15.0, duckdb 1.5.6, databento-dbn 0.70.0, numpy 2.2.6, pyarrow 20.0.0, jsonschema 4.26.0, non-editable installs), run from the core root at the #735 head 2d57e9e (content identical to merged 24ace1e):
- `python tools/verify_ef5_fixtures.py`: PASS (expander matched, counts pinned, known_at and fail-closed rules hold)
- `python tools/check_equity_delivery_replan.py`: PASS (35 stories, 47 planned outputs)
- `python tools/pre_merge_check.py`: first run 17 of 17 PASS; re-run after the text fixes 16 of 16 PASS with verify_quickstart skipped (its scratch folder existed from the first run) and the 3 installed-only checks skipped (need `--installed`)

## 5. Next step

Reviewer recompute of TD21 and RF52, then merge this PR to record the freeze of `ef5-price-structures-1`.

## 6. FX-1 and FX-2 added (coordinator decision, PQ-1)

FX-1 is result fixture TD21 (accepted config `split_adjusted`, maps to shared `split`, basis echo `split_adjusted`, values equal to TD01) and FX-2 is refusal RF52 (`total_return`, UNSUPPORTED_ADJUSTMENT at config, single fault; RF41 `dividend_adjusted` unchanged). Counts are now technical 21 (89 result fixtures) and 52 refusals, pinned in `tools/verify_ef5_fixtures.py`. The expander needed no change (it is generic over the adjustment label) so its blob SHA in `tools/contract_fixtures/README.md` is unchanged.

Tester recompute of the new rows (md only; the expander was not read):
- TD21: closes 100,102,101,103, N=1 M=3, dt 60 s. v_t = (2/101)/60 = 1/3030; v_(t-1) = (-1/102)/60 = -1/6120; a = (1/3030 + 1/6120)/60 = 61/7417440; session (103-100)/100 = 3/100; count +1-1+1 = +1. Counts expected/observed 3/3, 2/2, 2/2, 4/4; witnesses (3,1,2), (3,2), (3,0), (3,0,1,2); `basis` echoes `split_adjusted` on all four outputs (`split_adjusted` is in the v1 vocabulary, maps to shared `split`). Fixture matches on every value, status, count, witness and basis.
- RF52: single fault `total_return` on CD07; not in the v1 vocabulary (`unadjusted`, `split_adjusted`), so UNSUPPORTED_ADJUSTMENT raised at config (stage config, after wire and shared stages pass). Matches.
- Parity: 62 result rows and 52 refusal rows (description, hand_check, code, stage, base, fault) identical between md and json; counts 24/17/21/27 = 89 and 52 over 12 codes agree in md line 158, json fixture_counts and the pinned verifier. Stale text: none (the PQ-1 coverage sentence already names TD21 and RF52).
- Gates: `verify_ef5_fixtures` PASS; `pre_merge_check` 17 of 17 PASS (3 installed-only skipped).

## 7. split_adjusted snapshot/anchor (second-author finding)

The shared `AdjustmentSpec(basis=split)` raises UNSUPPORTED_ADJUSTMENT unless `action_snapshot` and `anchor` are not `none`. The contract now states that `split_adjusted` needs a caller-declared `adjustment_spec` {action_snapshot, anchor} (no default, fail closed). TD21 carries explicit values; new single-fault refusals RF53 (no snapshot) and RF54 (anchor none) were added (refusals now 54); the expander has a new admission rule, so its blob SHA in the README changed. **TD21's config and RF53/RF54 are new and need reviewer/tester recompute.**

## 7. adjustment_spec for split_adjusted (head 0b1b76e): TD21 config, RF53, RF54

Tester recompute from the md only (the expander was not read):
- TD21 config: `split_adjusted` maps to shared `split`, which requires a non-empty, non-`none` action_snapshot and anchor; the fixture declares `actions-2026-10-28` and `anchor-2026-10-28`, so the config is accepted (md line 350 rule). Values unchanged from section 6 (a = 61/7417440, v = 1/3030, session 3/100, count +1; counts 3/3, 2/2, 2/2, 4/4; basis echo `split_adjusted`): match.
- RF53: TD21 with action_snapshot deleted, a single fault, no default: UNSUPPORTED_ADJUSTMENT at config. Match.
- RF54: TD21 with anchor `none`, a single fault: UNSUPPORTED_ADJUSTMENT at config. Match.
- Parity: 62 result rows and 54 refusal rows identical between md and json; counts 24/17/21/27 = 89 and 54 over 12 codes agree in md line 158, json fixture_counts and the pinned verifier; the adjustment_spec rule appears in md line 350 and the json config_rules.
- Docs review of the changed text, non-blocking findings (no fixture impact): D6 the md producers table (line 17), the inputs paragraph (line 49) and the capability-matrix adjustment row (line 135) do not list `adjustment_spec {action_snapshot, anchor}` as a required split_adjusted input; D7 the shared `AdjustmentSpec` also has a `policy_version` field that defaults to `raw-v1`: the md does not say whether EF5 requires it or ignores it (no-defaults rule), a question for the Architect or PO.
- Gates: `verify_ef5_fixtures` PASS; `pre_merge_check` 17 of 17 PASS (3 installed-only skipped).
- The second-author reviewer's recompute of TD21 (with its adjustment_spec), RF52, RF53 and RF54 is requested from the reviewer separately and is still outstanding.

## 8. PQ-2 policy_version and D6 (coordinator, PO ruling)

`adjustment_spec.policy_version` is declared explicitly (raw-v1 for unadjusted, split-factors-v1 for split_adjusted, the shared string); absent, unknown or mismatched is UNSUPPORTED_ADJUSTMENT at config. New single-fault recipes RF55 (missing), RF56 (unknown), RF57 (mismatched pair); refusals are now 57 (the PO figure 51 to 54 was stale). All 89 result fixtures now declare `adjustment_spec.policy_version`: this changes config text only, no expected value or status changed. D6 is applied (producers table, inputs paragraph, capability row). The expander changed (SHA in the README). **RF55-RF57 and the changed fixture config text need reviewer and tester recompute.**

## 8. PQ-2 explicit adjustment_spec.policy_version (head 15c7321): RF55-RF57, D6, D7

Tester check from the md (the expander was not read):
- RF55: CD07 with `adjustment_spec.policy_version` deleted: the policy must be declared (shared default raw-v1 never applied), so UNSUPPORTED_ADJUSTMENT at config. Match.
- RF56: CD07 with policy `raw-v2`: not a supported policy (v1: `raw-v1` for `unadjusted`, `split-factors-v1` for `split_adjusted`), UNSUPPORTED_ADJUSTMENT at config. Match.
- RF57: TD21 (`split_adjusted`, snapshot and anchor declared) with policy `raw-v1`: mismatched label/policy pair, UNSUPPORTED_ADJUSTMENT at config. Match. Each is a single fault; none collides with RF22 (the producer `policy_version`, INVALID_CONFIG) or RF44 (INCOMPATIBLE_VERSION, version stage).
- Pair strings confirmed against the shared code (`raw` -> `raw-v1`, `split` -> `split-factors-v1`: packages/contracts breadth.py, relative.py, policies.py).
- D6 confirmed fixed: the three producer rows (md lines 17-19), the inputs paragraph (line 49) and the capability-matrix adjustment row now list `adjustment_spec`. D7 confirmed fixed: PQ-2 text in the config rules states the policy is explicit, the shared default is never read, and the exact label/policy pairs.
- Result-set diff against 8669711: all 89 result fixtures declare `adjustment_spec.policy_version` (88 `raw-v1` with `unadjusted`, TD21 `split-factors-v1` with `split_adjusted`); the `expected` block of every fixture (status, reasons, counts, value, witnesses, basis) is byte-identical to 8669711 (0 changed), and slots, outputs, target, unit, K and columns are unchanged. Only the config declaration was added.
- Parity: 62 result rows and 57 refusal rows identical between md and json; counts 24/17/21/27 = 89 and 57 over 12 codes agree in md line 158, json fixture_counts and the pinned verifier. No stale text found in the changed lines.
- Gates: `verify_ef5_fixtures` PASS; `pre_merge_check` 17 of 17 PASS (3 installed-only skipped).

Verdict: no discrepancy and no open docs defect. **Frozen pending merge** (of this PR). Outstanding: the second-author reviewer's recompute of TD21 (spec and policy), RF52-RF57 is requested from the reviewer separately.

> Note: the refusal count 57 stated in this document was corrected to 59 (new refusals RF58 and RF59) by `EF5_LIBRARY_ERRATA.md`; this frozen text and JSON are unchanged.
