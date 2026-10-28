# EF5 freeze evidence (price structures and patterns contract)

Status: evidence record for `ef5-price-structures-1`. Docs only. Based on main after PR #735 merged (squash 24ace1e); docs/ef5 content checked at the #735 head 2d57e9e, identical to the 04b81ff read-through head.
Freeze verdict: NOT MARKED FROZEN. The tester recompute found 0 discrepancies, but the independent docs review found open defects (section 3). The contract stays "proposal" until D1 is fixed and the docs review is re-run.

## 1. Evidence summary

| Evidence | Result |
|---|---|
| Second-author recompute (reviewer, PR #735 head 50ae18c) | approved: 88 result fixtures, 280 values, 0 discrepancies; refusals single-fault; tamper test failed the expander as required |
| PO read-through at 04b81ff | READY TO FREEZE |
| Tester recompute (this record, section 2) | 12 of 88 result fixtures (141 outputs checked by hand against md formulas) and 6 of 51 refusals: 0 discrepancies |
| Independent docs review (section 3) | md/json parity clean; 1 stale-text defect (D1) and 4 doc-gap findings (D2-D5) |
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

Defects (verdict blocker):
- **D1 stale text (blocker)**: `docs/ef5/EF5_SHARED_AMENDMENT.json` line 3 status says "pending PO ruling PO-2"; the md (line 3) records PO-2 and PO-7 accepted 2026-10-28. md/json parity break; fix the JSON status.

Findings (non-blocking, fix or accept):
- **D2 reason order**: PRICE_STRUCTURES md line 108 lists a precedence but does not say retained reasons are listed in lexical order (EF4 md line 83 does). Fixtures KA09/KA18/KA27 list `future_knowledge` before `unknown_availability`, which reads as contradicting the line 108 order. Add the lexical-order sentence and the reason-to-status map (missing_input, incomplete_coverage, not_applicable), which only the JSON shows.
- **D3 undefined terms in refusals (lines 276-290 area, RF24-RF43)**: price scale bound (RF39: 19), currency spelling (RF40), the v1 adjustment vocabulary (RF41), unsupported update/restore (RF42, RF43) and epoch_profile `carry` (RF20) are not defined in the md; they rely on shared EF3/EF4 text. Add one sentence citing it.
- **D4 unexplained terms**: READY, R17, E1-E9, C8-C10, EQ numbers and "slot clock" are used without a glossary line (lines 7, 154, 160).
- **D5 EF4 unit cross-reference**: md line 25 and the amendment say underscore forms appear on no header; EF4_LEDGER_APPLICATION.md section 2 defers EF4's slash migration, so EF4 headers keep underscore spellings for now. State this asymmetry once.
- Expected freeze-time text (not defects): "not frozen" wording at md lines 3, 344, 352 and JSON `status`/`coordinator_freeze` must change only when freeze is declared.

## 4. Gate commands

Environment: the pinned venv `wt-ef4-venv` (mypy 1.15.0, duckdb 1.5.6, databento-dbn 0.70.0, numpy 2.2.6, pyarrow 20.0.0, jsonschema 4.26.0, non-editable installs), run from the core root at the #735 head 2d57e9e (content identical to merged 24ace1e):
- `python tools/verify_ef5_fixtures.py`: PASS (expander matched, counts pinned, known_at and fail-closed rules hold)
- `python tools/check_equity_delivery_replan.py`: PASS (35 stories, 47 planned outputs)
- `python tools/pre_merge_check.py`: 17 of 17 automated checks PASS; verify_public_typing, verify_remote_transport, verify_supplied_worker_examples SKIP (need `--installed`)

## 5. Next step

Fix D1 (and decide D2-D5), re-run the docs review on the new head, then add the freeze line. No freeze is declared by this record.
