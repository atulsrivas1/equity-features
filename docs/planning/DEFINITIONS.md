# Definitions: Ready, Done and epics

> Working document, not a decision. Written by the PO, 2026-10-30. Internal, synthetic, pre-release. Adapted from `docs/playbook/LIFECYCLE.md` sections 4-5 under `docs/playbook/ADOPTION.md` (ADOPTION wins). The pull order is the hand-kept table in `RELEASE-MAP.md` until a generator exists (about 20 stories).

## Definition of Ready (a story may be pulled)

| # | Item | In this project |
|---|---|---|
| 1 | Screen source | Not used. A story with no screen names its check: the CLI/worker/API run or contract read that proves it. |
| 2 | Contract | The frozen contract/library/I-O/worker file under `docs/` exists, or the Contract line names the Architect's stub. A stub whose "open" list names a shape the story needs does not count: the story says `Missing:` and the work package. A story on a draft contract is "Ready (stub)": buildable, rework expected, reported apart. |
| 3 | Data line | States what the story reads and where it comes from, using the capability matrix (ADR-3): data needed, source adapter, sink, synthetic vs stored. |
| 4 | Gate | Names its release; the gate decides switch-on/publication, not whether it may be built. |
| 5 | No open build blocker | No open ruling, owner item or engineering item in its blockers; every story it needs is Ready or Done. Owner items block publication, not the build, unless the story says so. |
| 6 | Testable acceptance | Each criterion is checkable by running the installed artifact, a synthetic demo, a fixture/refusal recipe, or reading the contract. |
| 7 | Boundary | Names the repo (core, io, workers), the files it may write, and that no file is shared with another Ready story assigned in parallel. |
| 8 | Size | S, M or L; an L is split before it is pulled. |

Dropped (ADOPTION): legal-pending wording as keys, board/brief sources.

## Definition of Done (a story may be accepted)

| # | Item |
|---|---|
| 0 | Three independent reviews recorded in the PR Review table, none by the author (UI design N/A with reason). Verdict artifact rule: see `docs/playbook/ADOPTION.md` ("Architecture and cross-repo rules"). Squash-merge only, by the coordinator, after PO acceptance. |
| 1 | Acceptance criteria pass a manual run on the installed artifact or synthetic demo; Tester results table in the PR. |
| 2 | `python tools/pre_merge_check.py` passes; every other check the repo's AGENTS.md lists passes; commands, commit and environment recorded. |
| 3 | A defect-class fix adds a regression fixture or refusal recipe that fails on the old behaviour; the census is updated in the same PR. No new unit tests. |
| 4 | Cross-repo story: upstream merged first (core, io, workers), re-pin PR per downstream repo with its own three reviews; every builder whose pin moves is run. |
| 5 | Changelog entry with Verified and Not verified; wording "internal, synthetic, pre-release"; no performance or "covered/production" claims without measurement. |
| 6 | Decisions it makes are logged in DECISIONS.md (append only, "decided, pending owner review"). |
| 7 | Covered by the release demo script on synthetic or explicitly licensed data (browser demo harness where one exists). |

Dropped (ADOPTION): playbook items 4 to 6 and 8 (strings file, blocked vocabulary, board mapping, switches).

## How Testers verify

Run installed artifacts and synthetic demos: CLI, API, worker runs, the fixture/refusal drivers, and the browser demo harness where a PR touches it. Record each criterion as pass / fail / not shown with evidence (command, commit, output). Blocking: a criterion fails, data is shown dishonestly, a safety rule breaks. A blocking defect stops the story; PO does not accept meanwhile. Browser/keyboard/contrast pass only for PRs that touch a demo page.

Existing related documents (not duplicated): release acceptance `docs/qa/RELEASE_ACCEPTANCE_CHECKLIST.md`, edge cases `docs/qa/EDGE_CASE_MATRIX.md`, verdicts `docs/qa/EF4_PR_REVIEWER_VERDICTS.md`, roadmap `docs/EQUITY_DELIVERY_REPLAN.md`, `docs/EQUITY_EXPANSION_ROADMAP.md`, history `docs/BACKLOG.md`, `STATUS.md`, `DECISIONS.md`.

## Epics

| Epic | Name | One line |
|---|---|---|
| EP-EF | Equity delivery EF1-EF8 | Feature releases from the replan (`docs/EQUITY_DELIVERY_REPLAN.md`); delivered, not accepted. |
| EP-DV | DV1 definition variants | Definition-conflict fixes per the PO parity reconciliation; closeout C4 pending. |
| EP-CAT | Contract catalogue | io-owned drift-gated catalogue (S1-S8, CAT-DV1). |
| EP-CV | Coverage table | 166-item design coverage map and its generator/gate (CV0-CV6). |
| EP-PLAT | Platform | Re-pins, bumps, builders, benchmarks, E9 migration. |
| EP-EXP | Exposure | Service/MCP exposure of ef2-ef5 families. |
