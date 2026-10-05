# Equity Features

Source-independent equity feature calculations for reproducible research, backtesting and LLM-driven analysis.

**Status: R1 experimental0.0.2a9 package qualification accepted.
All 23 session IDs support batch/update/restore;22 noncontinuous IDs support
conditional partition merge. [R1 acceptance and limits](docs/R1_ACCEPTANCE.md)
and [experimental CI distribution](docs/BUILD_DELIVERY.md) describe the actual
channel. R0 repaired acceptance remains historical. R1 follow-up repairs are verified at0.0.2a11. R2 supplied-policy utility implementation
is qualified at0.0.3a0; three history batch IDs are qualified at0.0.3a1;
no public registry release, stable API or throughput claim.**

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

- [Project knowledge and session startup](docs/PROJECT_KNOWLEDGE.md)
- [Dashboard](docs/DASHBOARD.md)
- [R1 execution handoff](docs/R1_AUTONOMOUS_HANDOFF.md)
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

## Experimental R1 calculations

EQ-017 adds twelve batch bar/price IDs with independent quality, exact real notional and separate close-weighted proxy. See [API/admission/precision](docs/api/SESSION_BARS.md) and [synthetic example](examples/session_bars.py). EQ017 is delivered; [receipt](docs/stories/EQ-017_DELIVERY.md). EQ018 adds [typed interval structures](docs/api/SESSION_STRUCTURE.md) at0.0.2a1, [delivered receipt](docs/stories/EQ-018_DELIVERY.md); prior R0 acceptance remains historical. [Trade aggregates](docs/api/SESSION_TRADES.md) are delivered at0.0.2a2; [receipt](docs/stories/EQ-019_DELIVERY.md). [Bounded topK](docs/api/SESSION_TOP_K.md) is delivered at0.0.2a3; [receipt](docs/stories/EQ-020_DELIVERY.md). [Sampled quotes](docs/api/SESSION_QUOTES.md) are delivered at0.0.2a4; [receipt](docs/stories/EQ-021_DELIVERY.md). [Continuous quotes](docs/api/CONTINUOUS_QUOTES.md) are delivered at0.0.2a5; [receipt](docs/stories/EQ-022_DELIVERY.md). [Bounded accumulators](docs/api/INCREMENTAL.md) are delivered at0.0.2a6; [receipt](docs/stories/EQ-023_DELIVERY.md). Exact in-memory restore is delivered at0.0.2a7; [receipt](docs/stories/EQ-024_DELIVERY.md). Conditional merge is delivered at0.0.2a8; [receipt](docs/stories/EQ-025_DELIVERY.md). Final R1 audit is qualified at0.0.2a9; [acceptance](docs/R1_ACCEPTANCE.md) and [receipt](docs/stories/EQ-026_DELIVERY.md). No throughput or provider-readiness claim.

## Supplied action and reference policies

EQ033 applies exact supplied factors and independently admits point-in-time sector/
universe membership. Read the [policy API](docs/api/ACTION_POLICIES.md), run the
[synthetic example](examples/action_policies.py), and consult the
[delivery record](docs/stories/EQ-033_DELIVERY.md) for actual gate evidence.

EQ027 adds [governed returns and prior extrema](docs/api/HISTORY.md),
[synthetic example](examples/history_windows.py) and [delivery record](docs/stories/EQ-027_DELIVERY.md).
Historical state modes remain unsupported.
