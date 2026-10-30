# Coordinator handoff (read first; keep under 60 lines; update after every merge)

Updated 2026-10-30 (RL-01 status). Owner: Atul Srivastava (atulsrivas1), facilitator only. Repos under C:\Atul\Claude: equity-features (core), equity-feature-io, equity-feature-workers. Wording: "internal, synthetic, pre-release". Local build, no CI, no new unit tests. Haiku/Sonnet sub-agents, never Astra.

## How we work
- Playbook: docs/playbook/ (ADOPTION.md first), plus docs/COORDINATOR_WORKING_AGREEMENT.md. Team: 3 Developers (core, io, workers) + 1 Tester; PO and Architect always on, one release ahead.
- Every PR: three independent reviews (UI design N/A with reason, architecture, code/docs), verdict artifact in docs/qa/ before merge, PO accept, squash-merge by the coordinator only. One worktree per agent, outside the repo.
- Run `gh auth switch -u atulsrivas1` before every push or merge (login flips to monikasrivas1).
- Owner answers 2026-10-30 (DECISIONS.md): team 3+1, no tests/CI, local-only test env, owner publish gate only, Apache-2.0 (confirmed by owner).

## Done this session (Release 0 so far)
- Merged: #764 playbook adopted, #765 system design + audit, #766 PO planning set, #767 Architect rulings, #768 RL-01 map after rulings, #769 templates adapted.
- Docs: docs/planning/{REQUIREMENTS-DIGEST,DEFINITIONS,RELEASE-MAP}.md, docs/releases/R0/RELEASE-0.md, docs/architecture/{SYSTEM-DESIGN,EXISTING-SYSTEM-AUDIT,RELEASE-0-RULINGS}.md.
- Rulings: core_spread option A (docs only); 39 cap stays 39; naming RL-nn, PX-09..14, EF6=DV1 label retired.

## Open now
- Merged in RL-01: io #68 (3410402, RL-01-07), #69 (927372a, io-contracts 0.1.0a6), #70 (3409c7a, -08), #71 (e47b0c5, -09, partial EF1), #72 (0dbe5f5, -10 io half), #73 (f1251ce, -11); core #773 (e646fe7, -14 core part), #774 (f43434b, -13); workers #111 (1df482e, -12 workers part).
- Open: workers re-pin PR (in progress); RL-01-12 core hook; RL-01-14 workers part; RL-01-10 workers lane; RL-01-03; RL-01-15..19. New backlog: RL-01-20 (Blocked on core freeze), -21, -22.
- Handoff steps 3-6 still stand: DV1-5 closeout (RL-01-01..06), coverage CV1-CV6, backlog.

## Owner-only
Ratify E1-E9 and PO-1..PO-7; EF5 "stop at primitives" reversal; 252-vs-253; Linux machine/qualification; owner demo; publish/tag/sign-off. Providers/cost/rights are not ours.

## Rules learned
Check downstream pins on any version change; re-pin after squash; run every builder whose pin moves; verdict artifacts in docs/qa/ (work/ is git-ignored); reviewers re-checked by the same reviewer id (look up the id before messaging); merge main into a PR branch when DECISIONS.md rows conflict (keep contiguous).

Work records: C:\Atul\Claude\equity-features\work\ (git-ignored), incl. work/HANDOFF-2026-10-30.md and review-equity-features-76x.md verdicts.
