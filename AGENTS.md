# Agent rules (read every session; keep under 40 lines)

Session start: read this file, then PROJECT-MEMORY.md, then the top of STATUS.md. Open DECISIONS.md and docs/ only when a task needs them.

## Roles
- Main session = coordinator: scope, frozen contracts, integration, full code review before any merge.
- Workers = bounded layer tasks (app / API / adapter). Give them only their layer context plus the frozen contract. Never pass full history. Ask for code changes plus a brief status.
- Models: Haiku 5.5 for routine boilerplate/CRUD/schema wiring; Sonnet 5.5 for contracts, integration, subtle work. Never Astra. Never Opus or Fable unless the owner asks.

## Delivery
- Plan releases: goals, frozen layer contracts, stories, then parallel workers.
- Contract defect -> workers report to coordinator; coordinator versions and reissues the contract.
- Routine ambiguity: take the industry default, log it in DECISIONS.md, continue.
- Self-correct up to 5 attempts per issue, then escalate.
- Calculation packages stay pure: no fetching, files/DB, credentials, scheduling or publication. Those belong to I/O and workers.

## Verification (manual only)
- No unit tests or automated test suites: do not write, run or maintain them.
- Before a release or feature is done: run the real app/API, drive a browser, check network calls (app -> API -> adapter), UI interactions, state after refresh, responsive sizes.
- Record routes checked, payloads, mock-data labels and known gaps in STATUS.md or the PR.

## Merging
- Coordinator may merge any PR after a thorough review of the full diff and passed manual verification.

## Needs owner approval
Public deployment, production writes/credentials/migrations, live orders, external notifications, destructive shared-history operations, reference-only repos, spend over the per-task threshold, scope changes.
Local containers, mock stores and local web servers are pre-authorized.

## Hygiene
- Keep this file and README.md compact. Put detail in PROJECT-MEMORY.md / docs, history in STATUS.md / DECISIONS.md.
- Never invent evidence. Say what was and was not run.
