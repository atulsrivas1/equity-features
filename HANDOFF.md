# Coordinator handoff (read first; keep under 60 lines; update after every merge)

Updated 2026-10-24. Owner: Atul Srivastava (atulsrivas1). Repos under C:\Atul\Claude: equity-features (core), equity-feature-io, equity-feature-workers. Rules: memory files + WatchYourList AGENTS.md with equity repos substituted. Owner wants autonomous decisions (log each in DECISIONS.md as "decided, pending owner review"), full working agreement (real diff reads, fresh independent reviewer per PR, authors merge own PR after approval, no worker reuse across releases, retro per release). Local build, no CI. Haiku/Sonnet by complexity; no Opus/Fable unless asked.

## Release plan EF1-EF8
- EF1 gaps, EF2 (retracement, momentum, channels: contracts + library + I/O + workers + qualification + demo): done and merged.
- EF3 contracts D (relative RV, docs/ef3/RELATIVE_RV_CONTRACT_PROPOSAL.*), E (robust pace), F (breadth adaptive): frozen.
- EF3 merged: libraries core #692 (D), #694 (E), #695 (F); I/O io #36, #37, #38; workers #80 (D), #81 (F); shared amendment core #696 (rulings R1-R9, pending owner review). Reconstruction-mode exception kept (no shared-validator change).
- EF3 delivered (not accepted); retrospective with EF3 close update merged.
- EF4 (G tape, H quote/VWAP, I1 path efficiency, I2 projections) delivered, NOT accepted: contracts core #703-#705; libraries #706-#710; io #39-#42; workers #83-#86; vendored expanders #711; shared amendment #713 (rulings E1-E9, pending owner review); installed Windows qualification #714 (297 of 297 demos x 4 forms); evidence docs/ef4/EF4_DELIVERY_EVIDENCE.md #715; retrospective section 10 + skill EF5 changes + token ledger #716.
- Demo: EF4 browser demo shown (29 runs, 0 failed, 306 of 308 refusals matched; RF18/RF35 known adapter deviations). Server on 127.0.0.1:18400 (PID 64348) may still run: stop it.
- NEXT: owner items first, then EF5 in a FRESH coordinator session (read this file, STATUS, DECISIONS, the skill incl. EF5 changes, retro section 10).

## Open items
- Contract follow-ups: evidence id `slot:<i>` for E/F; contract F nits (DB11 derived-output counting, RB28 factor_den); `retracement` consumer rows still name #511/#518 (link #663); apply new unit strings to frozen shared contract; EF2 release gates (version bump, exact-zero residual limits, squeeze flag flip, O(n) memory).
- Perf note: ef3.relative_stats slows with close magnitude (documented).
- EQ164 audit: through wave 4; further waves only if EQ169 acceptance needs them.
- EF4 follow-ups: rank-aware TopKTrades check not built (E1); tape adapter defaults coverage to complete (fail-open, E2/L5); stale lines 17 and 41 in EF4_TAPE_IO.md; Parquet/bundles notional round trip not run; tape generator fixtures G01-G03 not in qualification; version bump owed.
- Owner actions: review E1-E9 and EF4 decisions; line-ending rule (.gitattributes); install python3-venv/pip in WSL Ubuntu (Linux qualification); issues #663-#669 to Project Backlog (token lacks project scope); confirm W-id mapping; review coordinator decisions; dataset rights; release acceptance (EQ-152 #486, EQ-169, full EQ164, publication).

## Method and gotchas
- Contract-first: frozen md+json contract with hand-derived fixtures; independent reviewer recomputes; one agent per layer; manual runs, no unit tests.
- One git worktree and one unique scratch subfolder per agent; verify agent cwd is the right repo (isolated agents inherit cwd).
- Demo: tools/ef1_results_demo.py with default sibling paths (never pass unquoted backslash paths); census: tools/check_extraction.py --core-root C:\Atul\Claude\equity-features.
- Private audit closure material is read-only and never copied; use opaque ids only.
- Token saving: lean agent reports, batch tool calls, no big pastes, try Haiku on template-driven I/O and workers layers with coordinator spot-runs; limit re-review rounds to changed fixtures; batch status/decision PRs per release.

## Learnings from the first coordinator session (token and process)
- ~117M effective tokens: 23% main-chat re-reads, 70% in 82 helper agents; ~99% on Sonnet. Contract authors 17%, reviewers 13%, audit 13%, library 13%, workers/I/O layers 11%.
- Independent recompute caught real defects (unbuildable fixtures, wrong evidence ids, false exact-zero claims): keep Sonnet there. Cut rework loops, re-review only changed fixtures, skip extra EQ164 audit waves.
- Reconstruction-mode evidence exception in EF3-D (shared validator) is documented; fold the decision into the EF3 shared amendment.
- Skill: `.claude/skills/equity-features-release-coordinator/SKILL.md` (commit if not yet).
