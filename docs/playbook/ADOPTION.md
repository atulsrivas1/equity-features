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

## Applicability in this project (overrides every mention elsewhere in the playbook)

- **Legal:** there is no legal gate, counsel role or legal-pending wording here. "Legal" in owner-level lists means only that the owner decides any legal position; providers, cost and data rights belong to the data-generating process, not to us. Ignore "legal" closer codes and gates in templates.
- **Design repo, boards, strings file, feature switches:** not used. Definition of Done items 4 to 6 and 8 and the Designer's board work do not apply. "Contract" means the frozen library/I-O/worker contracts under `docs/`; the Architect owns them.
- **Tester:** verifies by running installed artifacts and synthetic demos (CLI, API, worker runs, browser demo harness where one exists). The browser/keyboard/contrast pass applies only to PRs that touch a browser demo or page.
- **Source attribution:** the playbook text still names WatchYourList where it credits its origin; that is deliberate history.

## Architecture and cross-repo rules (added after architecture review)

- **Verdict artifact is a merge precondition, in addition to the PR Review table.** For any PR that changes contract or library code, and any layer PR in a release, the independent reviewer's verdict is saved as an artifact (`work/review-<repo>-<pr>.md` or `docs/qa/`) and referenced in the PR before the coordinator merges (`docs/COORDINATOR_WORKING_AGREEMENT.md`, "Merge preconditions"). Both are required.
- **Architecture review checks this project's boundary:** layering core <- io <- workers (ADR-1), no storage or vendor access in libraries, source adapters and sinks as the only conversion points, entry-point registration with allow-list (ADR-4), capability matrix (ADR-3). Ignore "client or server", "switches" and "data placement" items in the templates.
- **Cross-repo stories:** merge upstream first (core, then io, then workers), then a re-pin PR per downstream repo (versions, commit pins; run every builder whose pin moves), with its own three reviews. Check downstream pins on any version change; re-pin after a squash merge.
- **Merging:** squash-merge only, by the coordinator, in all three repos, after three reviews and PO acceptance. The playbook's "developers merge their own PR" option does not apply.
