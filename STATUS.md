# Status (newest first)

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
