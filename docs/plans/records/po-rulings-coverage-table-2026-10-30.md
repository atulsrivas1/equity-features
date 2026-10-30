Source: work/po-rulings-coverage-table-2026-10-30.md (Product Owner ruling record, 2026-10-30). Verbatim copy follows the blank line; internal, synthetic, pre-release.

# PO rulings: feature coverage table (2026-10-30)

Internal, synthetic, pre-release. Basis: Architect design `architect-coverage-table-2026-10-30.md`, parity check, my reconciliation, DV1 rulings. Design APPROVED with the modifications below.

## 1. Decisions D1-D5

| # | Ruling |
|---|---|
| D1 | **Accepted: map in core** (`docs/plans/design-coverage-map.json`); generator, gate, generated table and packaged copy in io. Reason: the map cites output ids and I accept mapping changes where I accept ownership. |
| D2 | **Accepted: time-boxed `pending_catalogue: DV1` marker.** Modifications: (a) the marker carries `expires_at: CAT-DV1` and the gate FAILS if the marker is present and the catalogue already has the DV1 family (marker must be removed in CAT-DV1's PR); (b) while present, COVERAGE.md prints a visible banner "DV1 outputs: manifest says delivered, catalogue pages pending" and the 10 DV1 rows show `contract_status: planned`; (c) the marker is the only R6 warning exemption, no others. CAT-DV1 stays after C4 (consistent with DV1 rulings). |
| D3 | **Modified: CV2 carries its own io-contracts bump**, not folded into S6. The ordering puts S6 and S8 before CV1/CV2, so folding is not possible, and packaged data bytes change (same reasoning as DV1 D5: version string must not be weaker than the digest). CV2 bump must be sequenced before CAT-DV1's a5 to a6 bump; coordinator assigns the version strings. |
| D4 | **Accepted: provisional rows are counted separately.** Headline shows `implemented (confirmed)` and `implemented (provisional)` as two numbers, never summed in one line. Today: 41 MATCH is an upper bound; provisional = P6/P14/P17 (look-ahead unverified) and P25/P36/P37/V12b (window inclusion, consumer rule: max(prior_high, current high)). Each provisional row names the gate or Tester check that clears it. |
| D5 | **Accepted: copy the PO ruling subset to `docs/plans/records/`** (stable, commit-pinned) so R5 resolves inside releasable trees. Copies are verbatim, with a one-line header giving the source path and date. `work/` stays unreleased. |

## 2. Design: approved, with modifications

- **Where it lives:** as D1. One more rule: COVERAGE.md header states "derived from core commit X; judgements asserted by PO with records; internal, synthetic, pre-release; not a release claim".
- **PO-asserted vs derived:** approved as designed. Derived: missing, extra, implemented (with automatic downgrade to partial when a cited output is undelivered). Asserted with my record: partial, differs, out_of_library_scope. No hand-written `implemented`. Addition: the asserted-status set in the seed is exactly my 2026-10-29 reconciliation rulings; nothing is asserted by anyone else without a new PO record.
- **R8 stale-sha rule:** approved; re-confirmation is a PO action (a short ruling line), not a rubber stamp. If a re-confirmation is requested more than once per release for the same item, the Architect raises it as a design smell.
- **differs to implemented:** only via R7 wrong-convention fixture evidence plus a PO ruling record (as the Architect says). The six confirmed DIFFERS (P15, P40-P42, V12a, M11) stay `differs` until DV1 Wave 3/4 evidence exists. Window-inclusion items are not DIFFERS today; they are provisional implemented.
- **`extra` rows:** shown neutrally; I decide per id whether to map them. Not an error.
- **Wording:** internal, synthetic, pre-release; no provider names anywhere in table, schema, tests or generated text; no speedup or performance claims; no "covered" or "fixed" wording except computed `release_ready_items: n/166`, which appears only in closeout records; no "production" or "releasable". Naming hazard: M11 title must read "range", not "dispersion", in the table note.

## 3. Story order

| Story | Ruling |
|---|---|
| CV0 | **Start now**, core only, in parallel with DV1 Waves 1-2 (files disjoint; DV1 core PRs touch the ownership manifest and `check_equity_delivery_replan.py`, not `docs/plans/design-coverage-map.json`). Scope: 166 rows seeded from parity check plus reconciliation, `DESIGN_COVERAGE_MAP.md`, `tools/check_design_coverage_map.py` (schema-only), `docs/plans/records/`. Rule: if any DV1 PR is found touching those files, CV0 rebases, DV1 does not wait. |
| CV1 | After catalogue S3, S6, S8 on the io writer lane; before S2. Needs CV0 merged. CV6 folds in (cold-read and INDEX pointer). |
| CV2 | After CV1, serial with S6/S8 (same module). Own bump (D3). |
| CV3 | After CV1; core and workers parts parallel once the script merges. Failing-gate demonstration PR in each repo, recorded. |
| CV4 | After S2. |
| CV5 | After C4; adds the marker and flips DV1-targeted items only with R7 evidence and my record; the marker is removed by CAT-DV1. Items go `differs` to `implemented` only after the Wave 3/4 evidence, never in C4. |
| Lane | S1 (done), S3, S6, S8, CV1, CV2, S2, CV4, S4, S5, S7, CAT-DV1 (after C4), CV5 flip. CV does not delay any DV1 wave. |

Coordinator assigns EQ numbers. Universal gates as the Architect lists (clean-venv pre_merge, real reviewer, independent docs review, DECISIONS/CHANGELOG line).

## 4. Acceptance criteria (product level)

1. **Completeness:** exactly 166 rows, each with design_id, family, kind, status, status basis (derived or asserted with record), producer, input contract link, output contract link, delivery and accepted flags, note. CV0 may carry blank link fields (links arrive in CV1); the CV1 gate refuses blanks for any non-missing, non-out-of-scope row.
2. **Honest counts:** counts per status and per family, provisional separate (D4). Today's expectation to be reproduced: 41 MATCH as an upper bound, 6 differs, no promotion.
3. **Client ease (measured, R10):** a fresh reviewer who has not seen the repo, given only `INDEX.md`, finds for three named design features (one implemented, one differs, one missing or out of scope) the **status, producer, input contract and output contract in under 5 minutes each**, from the installed package alone (`catalogue.coverage_for_feature_id`, `design_items_for_producer`) and from the docs copy. Time recorded in the PR. Failure = the PR does not merge; fix the layout, not the test.
4. **Reverse view:** every producer output page lists the design items it serves with their status.
5. **Drift:** R1-R9 green, each rule with a failing negative fixture; byte-equal docs, packaged and regenerated copies; zero golden or hash churn.
6. **Consistency with manifest:** a test asserts coverage counts agree with `check_equity_delivery_replan.py`; that checker stays the manifest authority.
7. **Honesty:** the header and wording rules in section 2 present in generated output; a test scans for provider names and banned wording.

## 5. Acceptance and ownership process

I own asserted statuses. Map change flow: PR with evidence ref, real review, independent docs review, my ruling record cited by `asserted.record`. At each release closeout I sign the coverage counts (counts plus sha256 of `coverage.json`) in the closeout record. Tester check of P25/P36/P37/V12b design wording and the look-ahead gate for P6/P14/P17 are separate tasks that clear provisional rows; I will rule on each result.

## 6. Open items

None blocking. CV0 may start immediately. Coordinator: proceed, no need to return unless a DV1 file conflict appears or the 5-minute criterion fails.
