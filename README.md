# Equity Features

Source-independent equity feature calculations for reproducible research, backtesting and LLM-driven analysis.

**Status: design and planning. No installable implementation yet.**

## Planned architecture

- Typed Python contracts for caller-supplied bars, trades, quotes and history.
- Calculation packages with no file, database, network or credential access.
- Batch and supported incremental APIs with explicit quality and timing.
- Independent adapters, starting with DuckDB, then provider APIs and local files.
- Bounded parallel workers; optional remote access and MCP later.

## Follow the work

- [Dashboard](docs/DASHBOARD.md)
- [Package design](docs/PACKAGE_DESIGN.md)
- [Backlog](docs/BACKLOG.md)
- [Development workflow](docs/PUBLIC_DEVELOPMENT.md)
- [Issues](https://github.com/atulsrivas1/equity-features/issues)
- [Milestones](https://github.com/atulsrivas1/equity-features/milestones)

Tests and examples will use synthetic data and require no paid credentials.

## License

License selection is pending. Public visibility does not grant an open-source license; an explicit license is needed before the first package release.
