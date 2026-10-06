# Equity Features

Source-independent equity feature calculations for reproducible research, backtesting and LLM-driven analysis.

**Status: experimental pair 0.0.4a3 has qualified scoped trusted custom batch extensions.
R2 remains accepted under its original0.0.3a13 receipt.
All 39 IDs support batch; the 23 session IDs support update/restore and 22 support
conditional merge. The 16 R2 history/context/breadth IDs remain batch-only.
All twelve R2 stories are closed/Project Done; the R2 milestone and E05 are closed. R3 has resumed; EQ093 final receipt publication is completing.
[Custom API](docs/api/CUSTOM_FEATURES.md) and [delivery evidence](docs/stories/EQ-093_DELIVERY.md)
record supported modes and review/installation limits.
[R2 acceptance evidence](docs/R2_ACCEPTANCE.md), [R1 acceptance and limits](docs/R1_ACCEPTANCE.md),
and [experimental CI distribution](docs/BUILD_DELIVERY.md) describe the declared
channel. No stable API, public registry publication or throughput claim.**

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

EQ028 SMA/EMA implementation delivery is qualified at0.0.3a2;
[API](docs/api/HISTORY.md), [installed example](examples/history_averages.py),
[verified source/artifacts/install receipt](docs/stories/EQ-028_DELIVERY.md).


EQ029 anchored RSI/ATR implementation delivery is qualified at0.0.3a3;
[API](docs/api/HISTORY.md), [installed example](examples/history_recursive.py),
[verified source/artifacts/install receipt](docs/stories/EQ-029_DELIVERY.md).


EQ030 sample volatility implementation is qualified at0.0.3a4; [API](docs/api/HISTORY.md), [installed example](examples/history_volatility.py), [delivery gates](docs/stories/EQ-030_DELIVERY.md).

EQ031 daily volume implementation is qualified at0.0.3a5; [API](docs/api/DAILY_VOLUME.md), [installed example](examples/daily_volume.py), [delivery gates](docs/stories/EQ-031_DELIVERY.md).

EQ032 interval-volume implementation is qualified at0.0.3a6; [API](docs/api/INTERVAL_VOLUME.md), [installed example](examples/interval_volume.py), [delivery gates](docs/stories/EQ-032_DELIVERY.md).

EQ034 relative-return implementation is qualified at0.0.3a7; [API](docs/api/RELATIVE_RETURNS.md), [installed example](examples/relative_returns.py), [delivery gates](docs/stories/EQ-034_DELIVERY.md).


EQ035 declared-universe breadth is accepted at0.0.3a9; [API](docs/api/DECLARED_BREADTH.md), [example](examples/declared_breadth.py), [delivery gates](docs/stories/EQ-035_DELIVERY.md). Partial expected universes and exact close-versus-SMA comparisons are preserved.

## Planned research evidence extensions

[Evidence roadmap](docs/EVIDENCE_ROADMAP.md): execution receipts and reproduction bundles (R9), explicit point-in-time diagnostics (R10), and agent decision evidence with optional ledger/MCP integration (R11). These are Backlog capabilities, not current product guarantees. Existing calculation/adapter/worker boundaries remain intact.

EQ036 supplied feature composition corrected implementation delivery is qualified at0.0.3a11; [API](docs/api/FEATURE_COMPOSITION.md), [synthetic example](examples/feature_composition.py). Whole instance identities and explicit missing families are preserved without hidden dependency execution.

EQ038 [Go comparison](docs/stories/EQ-038_COMPARISON.md) records five actual synthetic EMA/ATR vectors and a16-ID source/migration inventory. [Example](examples/legacy_comparison.py) replays captured observations and verifies public APIs; unpublished Go source is not rerun by public CI. Qualification/acceptance gates remain; R3paused.
