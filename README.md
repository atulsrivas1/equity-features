# Equity Features

Source-independent equity feature calculations for reproducible research, backtesting and LLM-driven analysis.

**Status: R0 foundation in development. Mathematical specifications are complete;
package layout is importable from source. Numerical kernels and artifact delivery
remain gated. No public registry release.**

[Development installation and package ownership](docs/PACKAGE_LAYOUT.md).

## Planned architecture

- Typed Python contracts for caller-supplied bars, trades, quotes and history.
- Calculation packages with no file, database, network or credential access.
- Batch and supported incremental APIs with explicit quality and timing.
- Independent adapters, starting with DuckDB, then provider APIs and local files.
- Bounded parallel workers; optional remote access and MCP later.

## Follow the work

- [Dashboard](docs/DASHBOARD.md)
- [Package design](docs/PACKAGE_DESIGN.md)
- [V1 feature scope](docs/features/V1_SCOPE.md)
- [Session formula specification](docs/features/SESSION_FORMULAS.md)
- [Backlog](docs/BACKLOG.md)
- [Development workflow](docs/PUBLIC_DEVELOPMENT.md)
- [Delivery policy](docs/DELIVERY_POLICY.md)
- [Work agreements](AGENTS.md)
- [Issues](https://github.com/atulsrivas1/equity-features/issues)
- [Milestones](https://github.com/atulsrivas1/equity-features/milestones)

Tests and examples will use synthetic data and require no paid credentials.

The first mathematical reference fixtures are available now: run `python tools/verify_session_examples.py` to check the session specification using exact arithmetic. This verifier is not the production package API.

## License

Licensed under [Apache License 2.0](LICENSE).
