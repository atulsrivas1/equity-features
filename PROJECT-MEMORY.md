# Project memory (keep lean; update when scope, contracts or architecture change)

## Shape
- Three repos: equity-features (core), equity-feature-io, equity-feature-workers. Dependencies flow inward: I/O and workers use core; core uses neither.
- Contracts between layers are frozen per release; only the coordinator amends them.
- Dev adapter: DuckDB data on the owner's N: drive where possible, else clearly labelled mock data. Outputs go to a separate DuckDB database. Exact paths are set per release contract.
- Option Features is a separate project group, out of scope for now.

## Where things live
- Roadmap/stories: docs/BACKLOG.md, GitHub issues, Project (atulsrivas1/equity-features).
- Current work: STATUS.md. Decisions: DECISIONS.md. Older detail: docs/ (large, historical; read only what a task needs).

## Open at last check (2026-10-21)
- EF1 regular completed-bar prices merged in all three repos (core #607, io #27, workers #68).
- EF1 first-trade prices: core PR628, io PR28, workers PR69 unmerged on GitHub; installed qualification was running in an old workspace and is not inherited.
