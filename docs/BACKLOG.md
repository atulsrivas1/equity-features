# Equity packages, adapters and workers — delivery backlog

Baseline: 2026-10-04. Status: planned, no implementation started.
Design authority: PACKAGE_DESIGN.md in this directory.
Planned repository: equity-features. Links and actual delivery status are maintained in DASHBOARD.md. No package registry release yet.

## Planning rules

Each numbered story below has exactly one release assignment and a concrete acceptance condition. All stories are planned and unassigned. Release labels are planning milestones, not promises of published version numbers or dates. Estimates follow formula/scope decisions and the first implementation benchmark. Later releases remain visible but cannot bypass earlier gates. Public package publication is separate from internal artifact delivery.

Story completion requires implementation or explicit decision evidence, required tests/documentation, a reviewed change, and a recorded artifact/commit. Test results must show what they establish; no source admission from file presence, no performance claim without measurements. A release requires every assigned story complete, dependencies satisfied and a recorded release acceptance checklist. Deferred scope must become a named later story rather than disappear. Conditional performance stories complete with a documented no-change decision when evidence does not justify acceleration.

## Release map

| Release | Outcome | Stories | Depends on |
| --- | --- | --- | --- |
| R0 Design and repository foundation | Freeze v1 scope/contracts/formulas and create package-only foundation | EQ-001–EQ-016 | None |
| R1 Core session packages | Verified bars/trades/quote calculations, first streaming API | EQ-017–EQ-026 | R0 |
| R2 Historical and contextual packages | History, baselines, relative/breadth, complete v1 composition | EQ-027–EQ-038 | R1 |
| R3 Package release readiness | Tested distributable packages, examples, benchmarks and adapter kit | EQ-039–EQ-048 | R2 |
| R4 DuckDB adapter | First real adapter using our optimized store | EQ-049–EQ-056 | R3 |
| R5 Independent workers | Bounded parallel feature generation and catalog publication | EQ-057–EQ-066 | R4 |
| R6 Provider and file adapters | Direct provider access and bring-your-own-file workflows | EQ-067–EQ-074 | R5 baseline; adapter work only needs R3 contracts |
| R7 Remote access and LLM tools | Hosted slices/jobs, client SDK and MCP | EQ-075–EQ-084 | R5; provider-backed endpoints also need relevant R6 adapter |
| R8 Advanced performance and research | Profile-driven acceleration and separate strategy/label packages | EQ-085–EQ-092 | R5 measurements; relevant earlier capabilities |

Default delivery is sequential. R6 adapter implementation may run independently of R5 after R3 if later authorized; it must not delay DuckDB as our first adapter. R7/R8 are future scope, not prerequisites for the package phase.

## Epic E01 — Scope and mathematical definitions

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-001 | R0 | Freeze v1 feature list and exclusions | Versioned list covers initial bar/trade/quote/history/baseline/relative/breadth features; strategies/labels remain separate; additions require scope change |
| EQ-002 | R0 | Specify session, bar and trade formulas | Exact equations, units, eligible inputs, VWAP/notional distinctions, auctions, ties and denominator rules have hand-calculated examples |
| EQ-003 | R0 | Specify quote formulas and sampling | Trade-associated versus continuous quotes, crossed/locked handling, midpoint basis, weighting and quote-validity limits are defined; unsupported measures rejected |
| EQ-004 | R0 | Specify historical formulas | Return windows, SMA/EMA initialization, RSI/ATR smoothing, rolling extrema, volatility conventions and gaps are defined with fixtures |
| EQ-005 | R0 | Specify baseline, relative and breadth formulas | Prior-only windows, time buckets, benchmark alignment, universe denominator and missing-member rules are explicit |
| EQ-006 | R0 | Freeze historical timing and adjustment policy | EOD/intraday cutoffs, eligibility, known-at versus reconstruction, split/dividend policies and input-gap handling documented and tested in design fixtures |

## Epic E02 — Repository and publishable package foundation

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-007 | R0 | Create repository and package boundaries | Repository has contracts/features distributions, contribution/continuity docs and no adapter/worker imports in calculation code |
| EQ-008 | R0 | Set supported runtime and dependency policy | Tested Python/platform baseline, NumPy/PyArrow ranges, optional backend policy and development lock/environment instructions recorded |
| EQ-009 | R0 | Establish builds, CI and dependency-boundary checks | Both wheels/sdists build; type/unit checks run; checks prevent calculation I/O/provider dependencies; no secrets in fixtures |
| EQ-010 | R0 | Decide release access and licensing path | Record personal public-repository owner and selected open-source license; package naming availability checked before registry release |

## Epic E03 — Public contracts and discovery

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-011 | R0 | Define canonical market/reference inputs | Trades/quotes/bars/daily/reference schemas preserve identity namespace, UTCns, units, scales, sampling, eligibility, coverage and adjustment basis |
| EQ-012 | R0 | Define supplied session/window/config specifications | Callers provide calendar boundaries/early closes/cutoffs/window policy; stable serialization and config digest; no wall-clock/calendar lookup |
| EQ-013 | R0 | Define result, quality, evidence and error contracts | Typed values/status/evidence and stable errors distinguish missing/empty/zero/invalid; algorithm/input identities and availability retained |
| EQ-014 | R0 | Implement validation and explicit normalization helpers | Bad order/duplicates/units/overflow/bounds fail clearly; sorting/conversion/dedup are explicit; copying behavior documented |
| EQ-015 | R0 | Implement in-memory feature registry | Every v1 ID exposes schema, requirements, formulas, units, warm-up, timing and version; registry works without source/credentials |
| EQ-016 | R0 | Define adapter capability/request/batch protocols | Historical and optional live interfaces, bounded batches and source metadata defined; in-memory example proves no calculation dependency on adapters |

## Epic E04 — Core session calculation packages

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-017 | R1 | Implement bar session metrics | OHLC/volume/range/close location/returns and supplied-prior-close gap match EQ-002 fixtures; true vs approximate notional explicit |
| EQ-018 | R1 | Implement opening/closing bar structure | Caller-defined intervals, early close, coverage and auction rules produce expected boundary values; no interval leakage |
| EQ-019 | R1 | Implement trade aggregates | Count/volume/notional/VWAP/mean size match fixtures, guard overflow and distinguish no eligible trades from missing source |
| EQ-020 | R1 | Implement bounded top-K trade evidence | Stable tie order, configurable K, row identity and bounded state verified; partition merge conserves evidence |
| EQ-021 | R1 | Implement sampled quote metrics | Spread distributions/aggregation and valid/locked/crossed counts follow EQ-003, declare sampling, never imply continuous coverage |
| EQ-022 | R1 | Implement supported continuous-quote measures | Time-weighting respects validity gaps/session ends and requires continuous input; unavailable source produces explicit status |
| EQ-023 | R1 | Introduce streaming update/snapshot lifecycle | Supported session accumulators ingest supplied batches only; order/session/cutoff/finalization/late-correction rules tested |
| EQ-024 | R1 | Implement bounded state export/restore | In-memory state preserves numerical/order/evidence identity; incompatible versions/config/inputs rejected; no file access |
| EQ-025 | R1 | Verify batch/stream/merge equivalence | Multiple batch sizes and legal partition merges agree within defined tolerances; ordered nonmergeable state is rejected |
| EQ-026 | R1 | Verify core edge cases and independent math | Ties, nulls, zero denominators, invalid prints/quotes, early closes, integer limits and missing/empty distinctions covered |

## Epic E05 — History, enrichment and composition

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-027 | R2 | Implement horizon returns and rolling extrema | 1/5/20/60/252-session returns and prior20/60/252 highs/lows use supplied session grid and explicit target inclusion |
| EQ-028 | R2 | Implement SMA and EMA | SMA20/50/200 and EMA20 match EQ-004 initialization/gap fixtures; bounded incremental variants where supported |
| EQ-029 | R2 | Implement RSI and ATR | RSI14/ATR14 match exact smoothing/seed definitions, action policy and missing-session readiness |
| EQ-030 | R2 | Implement historical volatility | Definition, scaling/session basis and minimum observations match approved EQ-004 spec; no invented annualization defaults |
| EQ-031 | R2 | Implement daily volume baselines | Prior20 reference and relative volume exclude target from baseline; insufficient history and zero baseline explicit |
| EQ-032 | R2 | Implement time-of-day baselines | Supplied interval grids/early close and observed-day denominators preserved; gaps not converted into zero volume |
| EQ-033 | R2 | Apply supplied action/reference policies | Split/dividend adjustments and classification/reference availability enforced; unsupported/unknown policy fails explicitly |
| EQ-034 | R2 | Implement benchmark and sector comparisons | Instrument/session/horizon/adjustment compatibility checked; missing sector membership affects sector results only |
| EQ-035 | R2 | Implement declared-universe breadth | Advance/decline/unchanged/above-SMA totals and coverage match complete/partial universe fixtures |
| EQ-036 | R2 | Compose feature families without hidden dependencies | Join identities/versions/config/cutoffs checked; unavailable optional families preserved; no reads/calculation of missing dependencies |
| EQ-037 | R2 | Verify historical causality and stream parity | Target/prior window boundary tests, future-input mutations and supported state-replay comparisons prove defined no-lookahead behavior |
| EQ-038 | R2 | Compare existing Go definitions and migration semantics | Inventory matched/different legacy definitions; parity where valid and independent math for defects; no wholesale legacy acceptance |

## Epic E06 — Package usability, performance and release assurance

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-039 | R3 | Complete API typing and stable documentation | Public APIs/errors/registry documented, py.typed included and caller examples type-check |
| EQ-040 | R3 | Publish runnable in-memory examples | Local-source-free batch/stream/history/composition examples run from installed wheels; show unavailable-input handling |
| EQ-041 | R3 | Establish representative benchmark suite | Seeded small/large/skewed data, rows/sec, peak process memory, copies and batch-size measurements record hardware/backend/thread settings |
| EQ-042 | R3 | Verify bounded computation and resource behavior | State grows only as documented; no hidden process pools; legal cancellation/batch limits and supported thread controls demonstrated |
| EQ-043 | R3 | Deliver adapter development kit and conformance suite | Protocol docs, mapping guidance, in-memory adapter, fixtures and conformance tests cover order/precision/availability/errors/batch boundaries |
| EQ-044 | R3 | Verify versioning and backward compatibility | Contract/schema/math/state version policy and incompatible-state tests; reference changelog and migration procedure |
| EQ-045 | R3 | Test clean installation and distribution contents | Wheels/sdists install in supported clean environments; examples/tests pass; no private paths, datasets or credentials included |
| EQ-046 | R3 | Audit pure calculation boundary | Public computation runs without database/network/file reads or clock dependency; hidden backend execution and mutable globals checked |
| EQ-047 | R3 | Review dependency/release integrity | Dependency licenses, pinned build provenance, artifact checksums and required release credentials handled outside code; public release gated on EQ-010 |
| EQ-048 | R3 | Record package release acceptance | All R0–R3 stories evidenced, numerical suite passes, benchmark baseline stored and internal installable artifacts produced; no provider/data readiness claim |

## Epic E07 — First adapter: our DuckDB store

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-049 | R4 | Implement catalog/source resolution | Select one pinned curated/prepared generation; preserve original/optimized hashes, substitutions and admission state; no overlap double-counting |
| EQ-050 | R4 | Map Databento equity schemas into contracts | Trades/TBBO/minute/daily mappings preserve scale/time/eligibility/sampling and identity; unavailable columns don't get guessed |
| EQ-051 | R4 | Implement bounded filtered reads | Instrument/session predicates, batch delivery, configured private connections and cancellation; query/copy/memory behavior measured |
| EQ-052 | R4 | Supply calendar, warm-up and reference requests | Governed sessions and target-required history resolved explicitly; reference/PIT gaps remain visible and are not inferred from file dates |
| EQ-053 | R4 | Bind acquisition provenance and source validation | Receipt/hash/schema/stability scope recorded; legacy source admission remains separate from physical rewrite verification |
| EQ-054 | R4 | Pass adapter conformance and integration fixtures | EQ-043 suite plus synthetic DuckDB/Parquet fixtures; curated/prepared overlaps and missing partitions tested |
| EQ-055 | R4 | Validate representative actual data slices | Frozen target/symbol scope; input counts/identity/precision and computed values checked; no full-corpus proof inferred |
| EQ-056 | R4 | Record DuckDB adapter acceptance | Installable optional adapter, docs/examples, measured reads and EQ-049–055 evidence; no worker launch required |

## Epic E08 — Independent parallel workers

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-057 | R5 | Implement task/input/output manifest contracts | Tasks bind family/session/shard/input/config/math identity; outputs schema/count/hash/quality/availability/provenance |
| EQ-058 | R5 | Implement session bars/trades/quotes commands | Thin commands invoke adapters+public packages, independently executable with bounded inputs; no duplicated formulas |
| EQ-059 | R5 | Implement history/baseline/reference/relative commands | Independent required-input tasks with explicit missing states; historical inputs don't require previous derived jobs unnecessarily |
| EQ-060 | R5 | Implement assembly and universe breadth barriers | Only declared dependencies block; universe/shard completeness checked; optional-family policy explicit |
| EQ-061 | R5 | Publish immutable typed output generations | Private staging and completion manifest last; crash/retry cannot expose partial output; original sources preserved |
| EQ-062 | R5 | Implement bounded supervisor and partitioning | CPU/memory/thread/I/O budgets, isolated spill, deterministic partitions and row conservation; no redundant unrestricted whole-file scans |
| EQ-063 | R5 | Implement claims, retries, resume and cancellation | Duplicate tasks/failed shards/restarts handled with recorded identity; storage-platform claim semantics validated |
| EQ-064 | R5 | Implement serialized catalog publication | Accepted generation selection, history and read-only access tested; no multiworker shared database writes; live readers handled explicitly |
| EQ-065 | R5 | Add progress, diagnostics and end-to-end fault tests | Structured task/family statuses and failure reasons; invalid input/interruption/corruption/retry proofs recorded |
| EQ-066 | R5 | Qualify pilot and historical generation readiness | Representative end-to-end parity/performance; separate source/PIT/warm-up/math gates before corrected month; annual only after month and capacity acceptance |

## Epic E09 — Provider and local-file adapters

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-067 | R6 | Verify provider capabilities and contracts | Databento/Massive endpoints/SDKs/entitlements/history/live sampling and terms checked against actual implementation needs |
| EQ-068 | R6 | Implement shared acquisition behavior | Safe credential injection, redacted errors, bounded retry/rate-limit/cancellation semantics, explicit cache policy; no secrets in results |
| EQ-069 | R6 | Implement Databento adapter | Supported historical/direct-download/live modes mapped explicitly; conformance and recorded bounded integration proof |
| EQ-070 | R6 | Implement Massive adapter | Supported data/reference endpoints normalized with honest capability/availability metadata; conformance and bounded integration proof |
| EQ-071 | R6 | Implement local CSV/Parquet/DBN adapters | Declared mapping/config, units/identity/order, bounded reads and unsupported schema errors; user fixture examples |
| EQ-072 | R6 | Validate cross-provider composition | Explicit identity/session/unit/adjustment mapping and lineage; incompatible sources rejected rather than ticker-only joins |
| EQ-073 | R6 | Add user-facing runner acquisition planning | Feature requirements select installed capabilities; one-command/library flow works; unsupported/unauthorized inputs clearly reported |
| EQ-074 | R6 | Qualify adapter releases and custom-adapter guide | Independent install/build/examples, provider matrix, cache/error tests and third-party fixture adapter passes development kit |

## Epic E10 — Remote service, client and LLM access

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-075 | R7 | Freeze hosted access/entitlement policy | Dataset permissions and redistribution decision documented before external exposure; users/services/quotas defined |
| EQ-076 | R7 | Define transport schemas and version policy | Requests/responses preserve int64/ns, config/dataset/math identity, errors/statuses; no untrusted Python deserialization |
| EQ-077 | R7 | Implement authenticated bounded slice endpoints | Instrument/session/feature filters validated, authorization server-side and parameterized queries; no unrestricted SQL endpoint |
| EQ-078 | R7 | Implement asynchronous calculation jobs | Job IDs, retries/idempotency, progress/cancel and bounded scheduling; remote invokes same packages through workers |
| EQ-079 | R7 | Implement scoped result delivery and expiry | Authorized artifacts/downloads, retention policy and precision/schema verification; datasets/filesystem paths not directly exposed |
| EQ-080 | R7 | Implement quota/cache/audit isolation | CPU/memory/concurrency/results bounded; caches include entitlement scope; cross-user negative tests and redacted audits |
| EQ-081 | R7 | Publish optional Python remote client | Authentication/retries/batch conversion outside features; local library works without client; version compatibility tests |
| EQ-082 | R7 | Add MCP discovery/query/job tools | Structured schemas, bounded summaries/artifact references; MCP separate from calculation packages; actual tool integration proof |
| EQ-083 | R7 | Verify reproducibility, errors and service resilience | Pinned snapshots/versions, unavailable data, expired result, cancellation and authorization failures tested end-to-end |
| EQ-084 | R7 | Qualify hosted release and operations | Deploy/rollback/load/security/backup/recovery/runbook evidence; access permitted only for approved datasets |

## Epic E11 — Profile-driven acceleration

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-085 | R8 | Identify actual compute and copy bottlenecks | Representative package/adapter/worker profile separates compute/I/O; proposed optimization has measured target |
| EQ-086 | R8 | Add native hot kernels only where justified | Rust or validated native implementation behind stable API; parity, state/version and measured memory/throughput improvement, or documented no-change decision |
| EQ-087 | R8 | Qualify optional accelerator packaging | Supported platform wheels/fallback/thread policy tested; optional install doesn't change definitions; no-change if EQ-086 not justified |
| EQ-088 | R8 | Tune large-run scheduling and output layout | End-to-end throughput/capacity/spill/query pruning benchmarks and correctness; more workers accepted only with measured benefit |

## Epic E12 — Separate strategy and label packages

| ID | Release | Story | Acceptance condition |
| --- | --- | --- | --- |
| EQ-089 | R8 | Define strategy/label scope and contracts | Separate inputs/config/outputs/readiness; strategy-required features and future-label isolation explicit |
| EQ-090 | R8 | Implement configurable scanners/rankings/watchlists | Consume accepted features without recomputation; deterministic selection, rules/version parity and missing-feature policy |
| EQ-091 | R8 | Implement forward labels and maturity | Price path/horizon/corporate-action basis, pending/mature states; no labels in signal inputs; independent fixtures |
| EQ-092 | R8 | Qualify strategy and label distributions | Installable optional packages, documentation/backtest examples, causality tests and version compatibility; core packages remain independent |

## Dependency details and readiness constraints

EQ-011–016 follow mathematical decisions relevant to each schema. EQ-017–022 follow EQ-002/003 and contracts; EQ-023–025 follow implemented supported batch families. EQ-027–035 follow exact EQ-004–006 definitions. EQ-036 depends on result contracts and completed selected families. EQ-043 builds on EQ-016; EQ-048 needs every earlier package story. EQ-049–056 require package release acceptance. EQ-057–066 require DuckDB adapter acceptance; actual source qualification is independent and may keep builds blocked while package/adapter code is complete. EQ-067–074 require capability-specific decisions and tested package contracts. Remote exposure requires EQ-075 first. EQ-086/087 depend on EQ-085 evidence, not enthusiasm for another language.

Real-data deployments have separate provider rights, provenance, calendar, historical-availability, coverage, mathematical-validation and capacity gates. Package tests and successful file publication do not establish data readiness.

## Coverage matrix

| Design concern | Stories |
| --- | --- |
| Source-independent libraries and reusable public API | EQ-007,011–016,039–046 |
| Exact feature definitions and data semantics | EQ-001–006,017–038 |
| Historical/realtime-safe shared calculation state | EQ-006,012,023–025,037 |
| Packaging, versions, public/private distribution | EQ-008–010,039,044–048 |
| Performance and bounded resource use | EQ-020,025,041–042,051,062,085–088 |
| Adapter development kit and user-provided data | EQ-016,043,067–074 |
| DuckDB prepared-data compatibility/provenance | EQ-049–056 |
| Independent parallel processing and publication | EQ-057–066 |
| Hosted data, client API and LLM/MCP usability | EQ-015,039–040,075–084 |
| Future strategy and label isolation | EQ-089–092 |

## Immediate next action

Start R0 with EQ-001–006 and confirm personal owner/license/project name. Maintain this backlog in the standalone repository. GitHub issues and release tags are later implementation actions.
