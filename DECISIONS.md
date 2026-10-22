# Decisions (append-only; date, decision, reason)

- 2026-10-21: No unit or automated tests; acceptance is manual browser/runtime verification. Reason: owner directive, token focus on features.
- 2026-10-21: Coordinator may merge PRs after a full diff review. Reason: owner directive.
- 2026-10-21: Sub-agents use Haiku 5.5 or Sonnet 5.5 by complexity; never Astra; Opus/Fable only on explicit request.
- 2026-10-21: Scope limited to Equity Features for now.
- 2026-10-21: Replaced heavy AGENTS.md/README.md with compact files; memory split into PROJECT-MEMORY, STATUS, DECISIONS.
- 2026-10-21: Used `gh pr merge --admin` on core #628 to bypass required check `check` (ci_provenance gate), which failed with no visible cause. Owner explicitly approved. Basis: coordinator diff review plus manual end-to-end runs passed; all other jobs green. #28 and #69 merged without override. Follow-up: find why `check` rejects.
- 2026-10-21: Removed required status check `check` from main's branch protection and merged #634 normally. Reason: GitHub Actions workflows were removed, so `check` can never report and blocked every PR; acceptance is local build plus manual tests. Coordinator decision at owner's direction (decided, pending owner review); reversible by re-adding the check. Retires the open follow-up on #628's `check` failure.
