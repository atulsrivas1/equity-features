# Status (newest first)

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
