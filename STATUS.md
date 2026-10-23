# Status (newest first)

## 2026-10-22 - EQ164 audit wave 2 done (exclusions and operand gaps)
- Merged findings PRs: X1 #654 (101 ingest/admin/validation commands: 80 confirm, 5 reject, 16 owner decisions), X2 #652 (101 other-domain plus 6 standalone: 87 confirm, 8 reject, 12 owner decisions), X3 #653 (24 priority rows: 208 operands; 92 delivered candidates, 32 planned, 29 proposed new story, 0 uncovered), X4 #651 (245 = consumers without a single explicit numerical owner, 220 scanners and 25 watchlists; reproduces from private material only; 226 rows classified outside the priority set, 132 ambiguous). Decisions are in docs/ef1/audit/EQ164_WAVE2_DECISIONS.md (pending owner review). Delivery ledger rows for EQ165 and EQ168 corrected.
- Not done: wave 3 (public plan flag corrections, 132 ambiguous consumers, contracts for 7 proposed stories, hygiene fixes, non-selected identities); no tracker issue created; full EQ164 stays open. Audit confidence is low to medium. The scratchpad was shared between agents, so one helper script may have been overwritten; each author re-verified its own output.

## 2026-10-22 - EQ164 audit wave 1 (selected rows) done
- Merged findings PRs core #647 (slice C, 36 EF8-only rows), #648 (slice A, 28 EF1/EF2/EF4 rows), #649 (slice B, 58 EF3 rows): 122 selected rows, opaque ids only. Totals: 3 partly delivered on main, 82 covered by a planned producer, 24 need operand producers, 13 ambiguous, 0 exclusions. All owner/release/I-O/worker issue numbers checked read-only against GitHub: no mismatches. Coordinator decisions on the 17 raised questions are in docs/ef1/audit/EQ164_WAVE1_DECISIONS.md (pending owner review). No tracker issue created or edited.
- Not done: wave 2 (208 command exclusions, row-level operand lists for consumer gaps, proposed stories, remaining identities), so full EQ164 stays open. Audit confidence is low to medium per row because opaque ids could not be tied to private inventories.

## 2026-10-22 - EF1 readable results view merged and demoed
- Merged workers #74 (e030433): tools/ef1_readable_view.py plus runner changes; each of the 62 cases now has view/<stem>.html with a features table (exact values, float repr + hex, decimal coefficient, unit, dtype, status, reasons, quality counts) and an evidence table; index links readable, raw JSON and DuckDB. Values are parsed from the canonical JSON embedded in each example page, never recomputed. Author compared every displayed value on all 62 pages with the typed DuckDB cells/evidence tables (360 cells, 109 evidence rows, 0 mismatches; one enum-display bug caught and fixed). No tests added (policy).
- Browser re-demo (coordinator): served the regenerated output locally, viewed the index (62 runs, 0 failed, Values column) and the close C02 page at 1200px and 400px in the browser pane; C02 values matched the contract (79.36507936507937 / 0x1.3d75d75d75d76p+6, supplied 1260, outside_tolerance, within_tolerance false). Server stopped afterwards.
- Known cosmetic limits: long feature ids and floats wrap mid-word in narrow columns; evidence row ids shown raw; index summary shows at most four features per case; only the index and one case page were opened in the browser.
- Still open for EF1: full EQ164 audit, installed Windows/Linux qualification, original-source parity and rights, real N: source demo, EQ169 acceptance.

## 2026-10-22 - EF1 amendment merged; browser demo of results page
- Merged core #644: sibling PRODUCER_SET_AMENDMENT (reference_close, multivenue_status; ledger 45 -> 56 headers vs frozen CONTRACT.json; merged code defines 66 -> 77). Independent reviewer approved; frozen CONTRACT.json untouched. Open findings recorded in it: units count/s/price/observations used in code but absent from the frozen unit set; frozen calendar lists omit several post-freeze producers.
- Browser demo: ran tools/ef1_results_demo.py (workers main 8c666fe) for 62 cases, 0 failed, served the folder on a local port and viewed index.html and the close C02 page in the browser pane (server stopped afterwards). Page text confirmed: synthetic labels, no-tests statement, per-case flags. Honest gaps: the per-case pages show the canonical result as raw JSON (not human-friendly); pane screenshot was narrow so layout was not judged beyond the header; only index and one case page were opened; no real N: source.
- Still open for EF1: full EQ164 audit, installed Windows/Linux qualification of the later slices, original-source parity and rights, EQ169 acceptance, human-readable results view.

## 2026-10-22 - EF1 missing producers delivered (EQ168 close reconciliation, EQ165 multi-venue status)
- Merged: contracts core #637/#640 (close, ef1-close-compare1 + Amendment 1), #638/#641 (multi-venue, ef1-multivenue-status1); close producer core #639, io #30, workers #72; multi-venue producer core #642, io #31, workers #73. Each contract had a fresh independent reviewer who recomputed fixtures with an independent stdlib harness; each library PR had a second independent code review that rebuilt inputs and compared all fixtures (close 53 result + 28 refusal; multi-venue 42 result + 13 refusal), no mismatches.
- Manual runs: worker examples for close (C01-C03) and multi-venue (all 42 MV cases) passed with contract-literal match, SDK readback, replay and close/reopen; results demo ran 62 cases without failure. I/O sink round-trips new units (bps, publishers, boolean). Coordinator spot-ran C01-C03 and MV05/MV24/MV43.
- Not done: additive CONTRACT.json producer-set/unit amendment (O5, D10); installed-wheel qualification; mypy; browser demo of the new pages; real N: source; original-source parity and rights; full EQ164 gate; EQ169 acceptance.
- Known: tests/unit/test_purity_audit.py already failed on main (61 modules vs 60 expected) and now lists two more modules; left as is under the no-unit-tests policy (owner to decide). Library refactor nits (340-line function, noqa lambdas) and a doc note on RF11 (5 slot dicts, slot_count 4) are on the cleanup list.
- Process lessons: (1) a worktree agent inherits the session's current repo, so confirm the working directory first; (2) hand-authored fixtures can contradict their own contract text (policy id FP vs venue_precedence_v1, C02 cutoff before close), so run an independent harness before freeze; (3) expose synthetic I/O fixtures under the contract's own ids.

## 2026-10-21 - EF1 manual demo run (coordinator)
- Ran the workers repo synthetic examples by hand on main (core ad3c77b; io 37f9b69; workers f5adde5), Windows CPython 3.12.10, outputs in a scratch folder (not committed). Passed: regular first-trade price R001 and R019, regular bar prices, gap endpoint (independent literal match, SDK readback, close/reopen all true); clock, anchors and status ran and wrote DuckDB plus HTML (exit 0, no literal-match line printed).
- Not run: daily observations (needs --corpus input), the `_ef1_*` helpers (modules, not CLIs). No unit tests run (policy).
- Not shown: real DuckDB source on N:, installed-wheel qualification, original-source parity, rights, full EQ164 gate, rendered browser view (pane cannot screenshot local files; page text checked only).
- Unblocked: required status `check` removed from core main protection; #634 merged. Remote codex/ef1-* branches are unmerged by ancestry (squash merges), so their status needs a per-branch check before reuse.
- Next: triage EQ165-168 against main, then plan the EF1 results demo and the remaining EQ164 audit.

## 2026-10-21 - EF1 first-trade price merged
- Merged (squash): core #628 -> 61c004e (ADMIN OVERRIDE), I/O #28 -> d8c9119, workers #69 -> 24cde0c (both merged normally).
- Verification: full diffs reviewed by coordinator; manual end-to-end run of cases R001 and R019 (library -> I/O adapter -> worker -> new DuckDB -> HTML) matched the independent literal, with readback and reopen verified. Browser pane could not render the local HTML file, so the HTML was not viewed visually. No tests were run.
- Known gap: required CI job `check` (tools/ci_provenance.py) failed on #628 with no visible reason; cause not found. Windows hash failure was fixed by 4f16605 (.gitattributes -text on the oracle). Workers CI failures were from workflows pinned to older core commits; not re-verified after merge.
- Still open: full EQ164, installed qualification, source rights/original parity, release/publication, other open drafts (#630, #631, ...).

## 2026-10-21 - EF1 state (from GitHub, checked today)
- Merged on main: EF1 regular completed-bar prices (core #607 747bae0, io #27 ae8bb17, workers #68 8d00d33).
- First-trade prices, all open drafts, not merged: core #628 (BLOCKED), io #28 (CLEAN), workers #69 (UNSTABLE). Heads are the "bridge" commits ede86152, 5145157f, 1ff1f2b7. Per the old handoff they passed independent source review; installed Windows/Linux qualification was never completed or reaped, so no installed result is claimed.
- Other open drafts: #630 (route docs), #631 (R26 quote boundaries), #566, #524 and older planning PRs.
- Not accepted: full EQ164 gate, browser demo, source rights/original parity, release/publication.
- Next: owner picks the first story. Under the new agreement, finish #628/#28/#69 by review plus manual run, not tests.

## 2026-10-21
- Fresh workspace created: claude-workspace/ with clean clones of the three repos at main.
- Old AGENTS.md and README.md removed; replaced with compact versions. Not yet committed.
- Next: owner picks the first story or release.
