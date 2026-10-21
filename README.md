# Equity Features

Experimental Python library of equity feature calculations over supplied data. Calculations are pure: no fetching, storage, credentials or scheduling.

Layers (separate repos):
- `equity-features` (this repo): pure calculation packages in `packages/` (features, contracts, intraday, evidence, labels, strategies, and others).
- `equity-feature-io`: source adapters and output sinks (DuckDB, Parquet).
- `equity-feature-workers`: task planning, execution and publication coordination.

Platform: CPython 3.12 on Windows and Linux. Experimental; no stable registry release.

Docs: [docs/START_HERE.md](docs/START_HERE.md), [docs/BACKLOG.md](docs/BACKLOG.md). Agent rules: [AGENTS.md](AGENTS.md). Memory: [PROJECT-MEMORY.md](PROJECT-MEMORY.md).
