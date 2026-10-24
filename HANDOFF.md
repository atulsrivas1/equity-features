# Coordinator handoff (read first; keep under 60 lines; update after every merge)

Updated 2026-10-23. Owner: Atul Srivastava (atulsrivas1). Repos under C:\Atul\Claude: equity-features (core), equity-feature-io, equity-feature-workers. Rules: memory files + WatchYourList AGENTS.md with equity repos substituted. Owner wants autonomous decisions (log each in DECISIONS.md as "decided, pending owner review"), full working agreement (real diff reads, fresh independent reviewer per PR, authors merge own PR after approval, no worker reuse across releases, retro per release). Local build, no CI. Haiku/Sonnet by complexity; no Opus/Fable unless asked.

## Release plan EF1-EF8
- EF1 gaps, EF2 (retracement, momentum, channels: contracts + library + I/O + workers + qualification + demo): done and merged.
- EF3 contracts D (relative RV, docs/ef3/RELATIVE_RV_CONTRACT_PROPOSAL.*), E (robust pace), F (breadth adaptive): frozen.
- EF3 merged: libraries core #692 (D), #694 (E), #695 (F); I/O io #36, #37, #38; workers #80 (D), #81 (F); shared amendment core #696 (rulings R1-R9, pending owner review). Reconstruction-mode exception kept (no shared-validator change).
- EF3 delivered (not accepted): also workers #82 (f92fd6a), tools #699 (contract_pack, run_batch), qualification run #700, evidence #701, retrospective with EF3 close update. Browser walkthrough done; demo server (PID 46940, port 18000) to stop; leftover wt-* worktrees to clean.
- NEXT: start EF4 in a FRESH coordinator session (read this file, STATUS, DECISIONS, the skill, docs/knowledge/RETRO_EF2_EF3.md section 9). Owner items first: acceptance decisions, WSL venv, issues #663-#669, line-ending rule, review of R1-R9 and coordinator decisions. Apply the section 9 changes.

## Open items
- Contract follow-ups: evidence id `slot:<i>` for E/F; contract F nits (DB11 derived-output counting, RB28 factor_den); `retracement` consumer rows still name #511/#518 (link #663); apply new unit strings to frozen shared contract; EF2 release gates (version bump, exact-zero residual limits, squeeze flag flip, O(n) memory).
- Perf note: ef3.relative_stats slows with close magnitude (documented).
- EQ164 audit: through wave 4; further waves only if EQ169 acceptance needs them.
- Owner actions: install python3-venv/pip in WSL Ubuntu (Linux qualification); issues #663-#669 to Project Backlog (token lacks project scope); confirm W-id mapping; review coordinator decisions; dataset rights; release acceptance (EQ-152 #486, EQ-169, full EQ164, publication).

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

## EF4 build complete (2026-10-24); release close pending
- Contracts frozen: G tape core#704, H quote/VWAP #703, I1 path efficiency + I2 projections #705. Libraries: G #706 (+#710 bisect fix), H #707, I1 #708, I2 #709. I/O: H io#39, I1 io#40, G io#41, I2 io#42. Workers: I1 #83, H #84, I2 #85, G #86. Tools: fixture expanders vendored core#711 (tools/contract_fixtures/). Not accepted.
- NEXT (fresh coordinator, one session): (1) EF4 shared amendment PR: rank-aware TopKTrades check (notional cell built via object.__new__; io codec fallback is feature-aware for tape.top_k_notional; bundles decoder still refuses notional cells), coverage form (IntervalCoverage==[S,E), always declare; undeclared reads complete = fails open), REFERENCE evidence boundary 'ordinary' (contract line 151 unimplementable), N<=63 governed_history cap + carry mode, I1 hosted in packages/intraday, refusal label errata (H RQ09 library, RV43; I2 11 producer-admission recipes + SPR12/13; G RF18/RF35 codes), K per-output evidence_limit, merge worker one shared config (RF41-43, 54-55, 60, 65, 66, 69 no worker path), new unit strings. (2) DECISIONS.md entries (split G/H/I1/I2; OQ-J3 EQ-155 edge reserved/unused; D6 slot_reasons both reasons; codec fix; vendored expanders; coordinator merged some PRs after reviewer approval). (3) TOKEN_LEDGER rows (agent usage lines in this session's notes; build ~200-500k per unit, reviews 110-250k). (4) Evidence doc docs/ef4/EF4_DELIVERY_EVIDENCE.md; installed Windows qualification (full demos once; set EF4G_HARNESS/EF4H_HARNESS/EF4I_HARNESS to core tools/contract_fixtures; session/bar I2 routes need one process per case, not a pool); browser demo for owner; retrospective update (verdict per EF3 change; EF4 changes applied: pack, quiet batch, sample reviews, display check, profile first); version bump owed; line-ending rule (.gitattributes) owner decision; cleanup worktrees (wt-ef3*, wt-ef4*, .claude/worktrees/agent-*), reviewer scripts live in side-session-notes folder.
- Known limits: RQ/SP refusals with different raised_by layers; Parquet/bundles round trip not run for notional cells; mypy not installed; boundary check fails on base64 in ef1 (old) only.
- Process notes: agents decline merges relayed by SendMessage (coordinator merges with GH_TOKEN of atulsrivas1 after reading diff/reviewer verdict); coordinator chat was ~300k tokens at build end: rotate here.
