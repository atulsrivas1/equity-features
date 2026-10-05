# Equity Features

Source-independent equity feature calculations for reproducible research, backtesting and LLM-driven analysis.

**Status: R0 review repairs in verification (0.0.1a6.post1). Mathematical specifications are complete;
both experimental foundation distributions are delivered through verified
[internal CI artifacts](docs/BUILD_DELIVERY.md). Typed inputs/specifications/results/validation/discovery and adapter protocols
are implemented. [Acceptance evidence and artifacts](docs/R0_ACCEPTANCE.md).
Numerical kernels remain R1/R2.
No public registry release.**

[Development installation and package ownership](docs/PACKAGE_LAYOUT.md).

[Release access and licensing](docs/decisions/release-access.md) separates retained
foundation artifacts from any future owner-authorized registry publication.

[Canonical input API, precision and copy semantics](docs/contracts/INPUTS.md),
[supplied session/window/configuration APIs](docs/contracts/SPECS.md),
[typed result/quality/evidence APIs](docs/contracts/RESULTS.md),
[checked validation and explicit normalization](docs/contracts/VALIDATION.md),
[immutable definition discovery](docs/contracts/REGISTRY.md),
[adapter contracts and synthetic development kit](docs/contracts/ADAPTERS.md).
After installing both experimental distributions plus the contracts `columnar`
extra, run `python examples/canonical_inputs.py` for the synthetic exact-nanosecond
round trip. Final-head/main artifacts are verified before each story is Done.

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
