# Coordinator handoff (read first; keep about 30 lines; update after every merge)

Updated 2026-10-31. Owner: Atul Srivastava (atulsrivas1), facilitator only. Repos under C:\Atul\Claude: equity-features (core), equity-feature-io, equity-feature-workers. Wording: "internal, synthetic, pre-release". Local build, no CI, no new unit tests.

## How we work
- Playbook: docs/playbook/ (ADOPTION.md first) and docs/COORDINATOR_WORKING_AGREEMENT.md. Team: 3 Developers + 1 Tester; PO and Architect one release ahead.
- Every PR: three independent reviews, verdict artifact in docs/qa/, PO accept, squash-merge by the coordinator only. One worktree per agent, outside the repo.
- Run `gh auth switch -u atulsrivas1` before every push or merge. On this machine `verify_compatibility` fails (known).

## Done (RL-01, per docs/planning/RELEASE-MAP.md)
- Release 0 docs: #764-#769.
- io: #68 (-07), #69 (io-contracts 0.1.0a6), #70 (-08), #71 (-09, partial EF1), #72 (-10 io), #73 (-11), #74 (-21, cc2cf31), #75 (-22, 39a5f97; 34 pairs in tools/header_crosscheck_accepted.json).
- core: #773 (-14 core), #774 (-13), #776 (-12 core hook, 203445a), #777 (workers pin 474f79d, provenance a4 to a5 row), #778 (-03, 3ea6efc).
- workers: #111 (-12), #112 (474f79d re-pin), #113 (-14 workers, e9e5f5b), #114 (-10 workers lane, 570d14c).
- RL-01-03, -07..-14, -21, -22 are done.

## Remains
- RL-01-01 and -02 wait on core #761; then -05 (PO) and -06 (C4 PR).
- RL-01-15 is Ready (io, L split). RL-01-16 Blocked on -15; RL-01-17 on -06 and -16; RL-01-19 on the Architect's notional-cell decode confirmation.
- RL-01-18 (E9 migration) and RL-01-20 (EF1 catalogue pages) blocked.
- DV1 closeout, coverage CV1-CV6 and backlog still stand.

## Owner-only
Ratify E1-E9 and PO-1..PO-7; EF5 "stop at primitives" reversal; 252-vs-253; Linux machine/qualification; owner demo; publish/tag/sign-off. Providers/cost/rights are not ours.

## Rules learned
Check downstream pins on any version change; re-pin after squash; run every builder whose pin moves; verdict artifacts in docs/qa/ (work/ is git-ignored); merge main into a PR branch when DECISIONS.md rows conflict.

Work records: C:\Atul\Claude\equity-features\work\ (git-ignored).
