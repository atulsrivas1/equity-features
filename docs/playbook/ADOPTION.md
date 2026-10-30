# Adoption: Equity Features (2026-10-30)

Adapted from the WatchYourList playbook. Read-only source: `watchyourlist-design/playbook/`. Where this file and the rest of the playbook differ, this file wins. The older `docs/COORDINATOR_WORKING_AGREEMENT.md` stays in force for data, adapter, worker, release-hygiene and review rules; this playbook adds the team model and story loop.

## Project choices (owner answers 2026-10-30; logged in DECISIONS.md)

| Choice | Value |
|---|---|
| Team | 3 Developers (one per repo: core, io, workers) + 1 Tester, with PO, Architect, coordinator always on. Fourth Developer only if 20+ Ready stories share no files |
| Tests / CI | None, as decided 2026-10-21. Merge gate: `python tools/pre_merge_check.py`, manual runtime verification, a regression fixture or refusal recipe per defect class |
| Test environment | Local only. No hosted staging, no Linux gate unless the owner adds one |
| Release gates | Owner publish gate only: PO accepts a release after three reviews and Tester pass per story and a demo; publish, tag and sign-off stay owner-only |
| Licence | Apache-2.0 (existing `LICENSE`) |
| Repos | `equity-features` (core), `equity-feature-io`, `equity-feature-workers`; one writable worktree per agent, outside the repo |

## Three reviews per PR

UI design, architecture, code: each by a fresh agent that is not the author. The Review table is in every PR. This project has no product UI, so UI design is `N/A: no UI file touched` unless the PR changes a browser demo harness or page; then a fresh reviewer checks it. Never skip the row.

## Not adopted from WatchYourList

- Legal/counsel gates, counsel-prep role, legal-pending string keys.
- Stored-data-only rule and "nothing computed to fill a gap" (this project computes in libraries).
- List-first, boards, strings file and feature-switch Definition-of-Done items (4 to 6, 8).
- Proprietary licence; WL decision ids.

## Local rules that still apply

`gh auth switch -u atulsrivas1` before every push or merge; squash-merge only; wording "internal, synthetic, pre-release"; no new unit tests; Haiku or Sonnet for sub-agents unless the owner asks otherwise; never Astra; owner-only items per HANDOFF (E1-E9, PO-1..PO-7 ratification, Linux machine, demo, publish).
