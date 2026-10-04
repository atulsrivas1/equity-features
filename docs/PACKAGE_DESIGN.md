# Equity calculation packages — final design baseline

Date: 2026-10-04. Design only; implementation and publication not started.
Repository planned: `equity-features`.
This supersedes the Go-first library recommendation in earlier worker proposal.
Delivery order: calculation packages, then DuckDB adapter, then workers.

## 1. Architectural boundary

Calculation packages accept caller-supplied data and configuration and return typed results. They do not open files, query databases, fetch APIs, obtain credentials, consult the wall clock, create processes, manage jobs, or persist outputs. No DuckDB, Parquet reader, MCP or orchestration dependency in the calculation distribution. Package installation/build metadata and documentation are not calculation-time I/O.

Batch functions are deterministic for identical inputs/configuration/backend version. Incremental objects own explicit bounded calculation state and accept supplied events; they never pull events from a source. The caller owns input discovery, delivery, ordering, cancellation, partitioning, reference availability, source admission, output persistence and resource scheduling.

Initial public interface is Python. NumPy supplies typed numerical arrays; PyArrow supplies columnar batches and schemas. Polars is an optional acceleration extra only where justified by a benchmark and compatible semantics. Python coordinates native array kernels; no Python dictionary/object loop over billions of records. Custom stateful hot kernels may later use Rust behind the same API, justified by profiling. No Rust implementation or second independent formula engine required initially.

## 2. Publishable distributions

| Distribution | Import | Contents |
| --- | --- | --- |
| equity-feature-contracts | equity_feature_contracts | Public input/result schemas, specifications, status/error types, feature definitions and validation |
| equity-features | equity_features | Session, history, baseline, relative, breadth calculations and incremental APIs; depends on contracts |

Start with two distributions in one repository. Feature families are Python modules, not separate releases/services. Contracts can be used by future adapters without installing every computation backend. Both include type annotations and py.typed, standard wheel/sdist metadata, semantic versions and executable documentation. Declare supported Python/platform versions after verifying CI and dependency support; don't promise untested portability.

Future adapters depend inward on these contracts/APIs. Calculation packages never depend outward on adapters. A future native accelerator is an optional implementation detail or wheel extra, not a new public API. Repository is intended to be public under the human owner’s personal GitHub account; owner is atulsrivas1; license selection is pending. No package registry release is implied by this design.

## 3. Public modules

| Module | Responsibility |
| --- | --- |
| contracts | TradeBatch, QuoteBatch, BarBatch, DailyBatch, supplied reference frames, SessionSpec, WindowSpec, AdjustmentSpec, AvailabilitySpec |
| validation | Structural checks, declared order checks, timestamp bounds, price/size validity, identity and duplicate policy |
| registry | In-memory feature discovery, formulas, units, required columns, warm-up, timing eligibility and algorithm version |
| session.bars | OHLC, volume, dollar-volume where supported, ranges, returns, opening/closing intervals and bar-based structure |
| session.trades | Trade count/size statistics, trade VWAP, dollar volume, top-trade evidence, trade-based structure |
| session.quotes | Observed spread statistics and supported quote measures with explicit sampling semantics |
| history | SMA/EMA, returns, RSI, ATR, rolling highs/lows and volatility from supplied history |
| baselines | Prior-only daily and time-of-day reference volume, coverage and relative-volume calculation |
| relative | Symbol versus supplied benchmark returns, sector comparisons with supplied membership evidence |
| breadth | Aggregation over a caller-declared universe, including missing-member coverage |
| incremental | Streaming accumulators for supported calculations; snapshot and versioned in-memory state transfer |
| compose | Align compatible result families and preserve independent quality/availability; does not fetch dependencies |

Reference classification, corporate-action and fundamental ingestion are not feature-library jobs. Packages accept supplied facts with availability and validation state. Scanners/watchlist selection, strategy scores, order simulation and forward-outcome labels are separate future packages; they are not required for equity features.

## 4. Canonical input contract

Data is columnar: Arrow RecordBatch/Table for batch boundaries and NumPy arrays for numerical kernels. Python lists/dataframes may be converted explicitly by helper functions; conversion and copy costs are visible. Conversion helpers accept in-memory objects only. No generic dataframe protocol silently triggering lazy database execution.

Common identity fields: instrument_id (opaque caller/provider namespace), session_id, event_ns UTC int64 where applicable; symbol is optional display/mapping information. Require identity namespace and mapping version rather than assume a ticker is permanent. Session grouping uses supplied SessionSpec: session identifier, open/close, timezone label, scheduled intervals/early close and cutoff. Library does not discover exchange calendars. Boundary inclusion rules are specified per interval, including opening/closing auction policies.

Trade fields: event_ns, ordering/tie key, price, size, optional condition/eligibility fields. Caller supplies normalized admissible event policy; packages validate required eligibility fields rather than silently treating every print as eligible. Quote fields: event_ns, bid/ask prices and available sizes, sampling kind (trade-associated snapshot versus continuous quote), optional sequence. Bar fields: start/end bounds, open/high/low/close, volume, optional trade count and actual notional. Do not derive exact traded dollar volume or trade VWAP from bar close*volume and label it exact; approximate measures have distinct feature IDs.

Price representation: scaled int64 plus explicit scale/currency at the contract boundary where the source supports exact values. Conversion from floating sources requires caller-specified quantization policy and validation. Volumes/counts are nonnegative integer columns with overflow checks; rates/indicators use float64 with documented tolerances. Native kernels must guard product/accumulation overflow or use safe wider accumulation; no implicit overflowing int64 price*volume. Missing input is represented by null/validity, never an invented zero. All timestamps retain nanoseconds; no float epoch conversion.

Inputs declare sortedness, duplicate/tie rules, units, adjustment basis and coverage. Time-sensitive algorithms require monotonic event order; a checked fast path is separate from explicit normalize/sort helpers. No silent full-data sort or dedup. Equal timestamps resolve using supplied stable order; open/close/top-trade selection remains deterministic. Invalid schema/order is an error; unavailable enrichment is a result status. Empty observed session is distinguishable from absent input.

## 5. Result contract and timing

FeatureResult contains a typed columnar values table, a quality/status table keyed by entity+feature, metadata and optional evidence tables. Common identity: instrument/session/cutoff, feature schema version, algorithm version, input identity bindings and config digest. Registry exposes required inputs, history windows, formula, units and approximation basis.

Status vocabulary: available, insufficient_history, missing_input, incomplete_coverage, not_applicable. Invalid schema, overflow, inconsistent identity, unsupported sampling/adjustment and illegal order raise typed errors. Values for unavailable features are null. Coverage includes actual vs expected samples/sessions and warm-up state; input gaps cannot masquerade as low market activity.

Distinguish feature market cutoff, reference cutoff, actual source known-at, and caller-selected simulation eligibility policy. Generation time is outside the pure library and attached by a worker later. Unknown availability is preserved. Observation time after a backfill is not silently converted into historical causal evidence. Session-close is a calculation bound, not a promise that every EOD feature was available instantly.

Windows count supplied governed trading sessions rather than calendar days or rows with data. Baselines exclude target session; completed EOD indicators may include it if documented. Adjustment policy and corporate-action availability are explicit, immutable inputs. No current membership or revised fundamental fact substituted into earlier history. EMA/RSI/ATR initialization and missing-session treatment are mathematical contracts, not backend defaults.

## 6. Initial feature specification

Implement a modest, well-defined first release rather than all advanced feature ideas.

| Family | Initial features |
| --- | --- |
| Bars | OHLC, volume, open-to-close return, range/close, close-location value, overnight gap and close-to-close return when prior close supplied |
| Trades | Count, volume, notional, VWAP, mean size, configurable deterministic top-K trades |
| Quotes | Per-observation absolute/bps spread, valid/crossed/locked counts, declared sampled aggregation; time-weighting only for continuous quote input with bounded validity |
| History | Returns 1/5/20/60/252 sessions; SMA20/50/200; EMA20; RSI14; ATR14; prior rolling highs/lows20/60/252 |
| Baselines | Prior20-session average volume and relative volume; optional supplied time-bucket grid for intraday baseline |
| Relative | Return minus benchmark return for matching horizon; sector comparison only with matching supplied membership/benchmark |
| Breadth | Advancing/declining/unchanged counts and above-SMA fractions against a declared universe |

For implementation each feature gets an exact equation and edge-case example. Decisions include simple versus Wilder initialization, denominator-zero semantics, minimum observations, auctions/conditions and standard deviation convention. Feature IDs include materially different definitions; changing a formula increments algorithm version. Proposed windows are configuration defaults, not hard-coded dependencies.

## 7. API shape (illustrative)

    from equity_features import session, history, baselines, registry
    from equity_feature_contracts import SessionSpec, WindowSpec

    result = session.trades.compute(trade_batch, session=spec, config=trade_config)
    indicators = history.compute(daily_batch, target=target, windows=window_spec)
    baseline = baselines.daily(history_batch, target=target, window=20)
    definitions = registry.list_features(family="history")

    accumulator = session.trades.accumulator(session=spec, config=trade_config)
    accumulator.update(batch_a)
    accumulator.update(batch_b)
    snapshot = accumulator.snapshot(cutoff_ns=cutoff)
    state = accumulator.export_state()  # in-memory object/bytes, never a file

Public functions use explicit keyword configuration, no mutable global settings or environment-dependent defaults. Incremental update validates session/order/cutoff; snapshot cannot claim a retrospective earlier cutoff after ingesting later events. Supports declared state/schema/math versions and refuses incompatible restore. Export captures sums/compensation, order bounds, warm-up and bounded evidence, not only final feature values. Finalization behavior is explicit; late corrections require a caller-selected replay/rebuild policy, not silent mutation.

## 8. Performance and correctness

Batch size is independent of mathematical results within specified float tolerances. No required whole-history load for streaming-compatible features. Rolling buffers scale with configured warm-up; top-K state is bounded. Exact quantiles are not an unbounded streaming promise; approximate future quantiles need distinct algorithms/error contracts.

Library has no automatic multiprocessing or unlimited threads. Caller controls backend threading; calculations expose cancellation at batch boundaries where relevant. Adapters/workers later manage shards/CPU/memory. Partition reductions require explicitly supported merge operations: counts/notional and top-K can merge with defined identity/order semantics; EMA/RSI and other ordered state cannot merge arbitrary independent partitions. Batch/stream parity and supported merge parity are mandatory checks.

Benchmark suite measures rows/sec, peak process memory, allocation/copy overhead and multiple batch sizes with seeded representative small/large/skewed inputs; run native-process measurements, not Python allocation tracking alone. Results record CPU, backend versions, thread budget and numerical tolerances. Establish baselines before performance gates; do not invent throughput targets. Optimization requires correctness equivalence plus measured benefit. Source I/O performance belongs to future adapters.

Tests cover hand-calculated fixtures, batch/incremental parity, missing/empty distinction, warm-up and lookahead boundaries, split-adjustment policy, duplicate/tie order, early close, integer overflow, nulls, zero denominators, shard conservation and versioned state round trips. Compare existing Go results where definitions agree; known defects are checked against independent mathematics rather than copied.

## 9. LLM-facing usability

Feature registry is callable in memory and exposes machine-readable schemas, concise definitions, readiness, units and input requirements. Include small complete examples, clear typed errors and typed result descriptions. APIs remain composable rather than accepting a vague natural-language request. No LLM dependency, model call or MCP server inside packages. Future MCP tools wrap these same APIs/worker jobs and return summaries/artifact references.

## 10. Implementation layout and completion gates

    packages/contracts/src/equity_feature_contracts/
    packages/features/src/equity_features/
    tests/fixtures/
    benchmarks/
    docs/features/
    docs/contracts/
    examples/

Each distribution has its own pyproject.toml and release metadata; dependency ranges are explicit and release-compatible. Build/install wheels into clean environments and execute documented examples before release. CI checks types, tests, package builds and dependency boundaries; native wheels later need separately tested platform release coverage. License/public registry decision remains outside implementation.

Package phase is complete when schemas/formulas are specified, initial functions work, batch/stream semantics are verified for supported families, examples install from built artifacts, and benchmark baselines are recorded. Only then build the DuckDB adapter, which maps pinned prepared data into these contracts and preserves original/optimized source identity and causal evidence. Workers follow after adapter validation. No historical build is launched merely because packages exist; existing data admission/month gates remain.

## 11. Future remote data access

The architecture supports both bring-your-own-data calculations and authenticated access to hosted project datasets. Remote access is a later delivery phase after packages, DuckDB adapter and workers; it does not add network access or hosting dependencies to the calculation packages.

Remote execution path: client SDK or MCP tools -> authenticated service -> server-side adapters/workers -> hosted data store. DuckDB database files and N: paths stay server-side. The service owns authorization, dataset entitlements, request validation, resource limits, job scheduling and result retention. Start with scoped data/feature endpoints rather than unrestricted caller-supplied SQL; parameterized server queries and bounded result sizes are service responsibilities.

Two service operations: retrieve an authorized data/feature slice, or submit a bounded calculation job using a published feature definition and configuration. Large jobs return a job ID and later a scoped result artifact; compact results return typed summaries. Caller-provided job identifiers support retry handling. Cancellation, concurrency quotas, expiry and audit records belong to service/worker infrastructure, not numerical functions.

A future client distribution (for example equity-feature-client) handles HTTP authentication, retries and result delivery. It can translate returned Arrow batches into the existing package input contracts without changing the feature API. It is optional: local users can install contracts/features without the client. MCP is another service interface, not a dependency of either package.

Contract requirements established now: stable feature IDs and versioned schemas; serializable configuration and typed error/status codes; explicit requested instruments/session/cutoff; returned dataset snapshot and input identities; algorithm/config versions; quality and availability metadata. These are useful for local reproducibility as well as remote execution. Local Arrow/in-memory state objects are not automatically a wire protocol: define versioned transport envelopes later, preserve nanosecond/int64 precision, and never deserialize untrusted Python objects or checkpoints. The service validates requests and references approved datasets; clients cannot assert server authorization or source admission through supplied metadata.

Response metadata separates calculation results from service/job metadata. Reproducible requests pin dataset snapshots and algorithm versions where supported; cache identities include these plus configuration and authorization scope so cached results cannot cross user entitlements. Data rights and distribution permissions must be settled before offering hosted datasets externally; the package design itself grants no access to proprietary data.

No remote server, SDK, MCP endpoint, authentication system or data redistribution is part of the current package implementation. Remote support is an architectural extension with these compatibility requirements, not an additional package-phase completion gate.

## 12. Provider and user-built adapters

Support two acquisition modes: adapters fetch/stream supported data directly from a provider using the user's credentials, or read existing local/downloaded data. Both deliver the same validated calculation input contracts. Direct access removes manual download steps; data still transfers from the provider, and an adapter may cache or stage files under explicit caller configuration. Providers may expose historical download jobs instead of an immediate stream; the adapter handles those workflows where supported. Actual provider endpoints, dataset coverage, entitlements and SDK compatibility must be verified during implementation, not assumed by this design.

DuckDB remains the first implemented adapter. Subsequent candidates include Databento, Massive and local CSV/Parquet/DBN sources. Adapter packages are independently installable with their own optional provider dependencies. Users install only the adapters they need. Provider keys/configuration belong to adapters or caller credential stores, never calculation inputs/results or provenance logs. Credentials alone do not establish subscription access, historical coverage or permitted usage.

The contracts package will define a small, dependency-light adapter protocol alongside canonical schemas. Protocol definitions do not perform I/O. Methods describe supported capabilities, explicit acquisition requests and bounded batches; capability declarations include available data kinds, historical/live modes, instrument namespaces, timestamp/price precision, sampling, coverage and adjustment basis. A historical request binds instruments, session/time bounds, requested data kind and cutoff policy; batch delivery carries source identity, mapping, ordering, availability and coverage evidence. Metadata-only capability discovery must not require calculating features. Synchronous iteration and optional asynchronous streaming are distinct interfaces; a file adapter need not implement live streaming.

Deliver an adapter development kit with protocol documentation, schema/version compatibility rules, in-memory example adapter, mapping guidance, validator helpers, synthetic fixtures and conformance tests. Conformance checks cover units/timestamps, duplicate/order declarations, batch boundaries, instrument mapping, missing versus empty, source availability, cancellation/error semantics and bounded delivery. They establish contract compatibility, not provider truth, financial accuracy or legal entitlements. No network credentials are required for the reference fixtures or package-phase tests.

Adapters own source normalization and acquisition; calculation packages own formulas. Explicit errors distinguish unsupported capability, authentication/entitlement, rate limit, transport failure, schema mismatch and unavailable data. Providers' semantics remain visible: sampled quotes cannot masquerade as continuous quotes, bars cannot recreate trade evidence, and rounded/adjusted values must declare their basis. Cross-provider composition requires explicit instrument/session/unit/adjustment compatibility and provenance, not a ticker-only join.

A later runner can inspect feature input requirements, plan acquisition and invoke installed adapters/calculations. Scheduling, retries, caching, checkpoints and a single-command user experience belong to that runner/adapter layer. The package-phase deliverable includes protocol types and in-memory conformance fixtures only. Production DuckDB/provider/file adapters and the runner remain later phases; the pure numerical API stays unchanged.
