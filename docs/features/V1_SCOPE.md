# V1 feature scope

Scope revision: 1. Story: [EQ-001](https://github.com/atulsrivas1/equity-features/issues/2).
Status: scope baseline; numerical formulas and implementation remain subsequent stories.

Session/bar/trade definitions and synthetic reference evidence are in [SESSION_FORMULAS.md](SESSION_FORMULAS.md). This defines the mathematics; production kernels remain later stories.

## Product boundary

V1 is a source-independent Python calculation API for equity session measurements and supplied historical context. It accepts in-memory typed data and returns typed features, quality and evidence. It does not acquire data, discover calendars, read credentials, create jobs, publish files or select strategies.

First qualification uses US equity regular sessions, with caller-supplied session boundaries, instrument identity and eligibility rules. Early closes are part of the session contract. Other markets may use the same supplied-boundary contracts, but are not qualified by v1 US fixtures. Extended-hours aggregation, venue-specific live corrections and complete exchange-feed reconstruction are out of scope. Regular-session auction eligibility is an explicit formula/configuration decision in EQ-002, not an assumed provider default.

The numbered releases R0–R3 deliver this package scope incrementally; R1 alone is not the complete v1 feature set. Adapters and workers begin afterward. A feature listed here is planned, not implemented or benchmarked.

## Input classes

| Key | Caller-supplied input |
| --- | --- |
| B | Completed interval OHLCV bars with session/time boundaries and declared coverage |
| T | Eligible trades with event time/order, price, size and eligibility provenance |
| Qs | Bid/ask observations with explicit sampling, available sizes and coverage |
| Qc | Continuous quote updates with order and validity/gap rules |
| D | Historical daily series, supplied governed session grid and adjustment basis |
| H | Historical intraday interval volume on a supplied bucket grid |
| P | Compatible prior closing price and previous-session identity |
| R | Benchmark series and optional point-in-time sector membership |
| U | Declared universe and compatible per-symbol feature results |
| A | Adjustment/reference evidence and availability policy when needed |

All calculations also require explicit instrument/session/cutoff/config contracts. Source selection, original/optimized hashes and source admission remain caller responsibilities; calculation results retain supplied bindings without certifying them.

## Feature catalog

Feature IDs identify definitions rather than data providers. Configurable windows are parameters, not new IDs. Units, precise equations, eligibility and edge cases are specified in the linked formula stories. Unknown/missing inputs do not become zeros.

| ID | Result | Inputs | Package release | Formula owner |
| --- | --- | --- | --- | --- |
| session.bar.open | First eligible interval open | B | R1 | EQ-002 |
| session.bar.high | Session high | B | R1 | EQ-002 |
| session.bar.low | Session low | B | R1 | EQ-002 |
| session.bar.close | Last eligible interval close | B | R1 | EQ-002 |
| session.bar.volume | Aggregated interval volume | B | R1 | EQ-002 |
| session.bar.notional | Aggregated actual notional, only when supplied | B with actual notional | R1 | EQ-002 |
| session.bar.close_weighted_price | Explicit bar-close volume-weighted proxy; not trade VWAP | B | R1 | EQ-002 |
| session.price.open_close_return | Return between session open and close | B | R1 | EQ-002 |
| session.price.range_fraction | Session high-low relative to close | B | R1 | EQ-002 |
| session.price.close_location | Close position in session range | B | R1 | EQ-002 |
| session.price.overnight_gap | Open versus compatible previous close | B, P, A where required | R1 | EQ-002, EQ-006 |
| session.price.close_close_return | Close versus compatible previous close | B, P, A where required | R1 | EQ-002, EQ-006 |
| session.structure.interval_ohlcv | OHLCV for configured opening/closing intervals | B, interval spec | R1 | EQ-002 |
| session.structure.interval_volume_share | Configured interval volume as share of observed session volume | B, interval spec | R1 | EQ-002 |
| session.trade.count | Count of eligible trades | T | R1 | EQ-002 |
| session.trade.volume | Eligible traded volume | T | R1 | EQ-002 |
| session.trade.notional | Sum of actual traded price times size | T | R1 | EQ-002 |
| session.trade.vwap | Actual trade volume-weighted price | T | R1 | EQ-002 |
| session.trade.mean_size | Mean eligible trade size | T | R1 | EQ-002 |
| session.trade.top_k | Bounded largest-trade evidence, ranked by size with stable ties | T, K | R1 | EQ-002 |
| session.quote.sampled_spread | Per-observation absolute and midpoint-bps spreads; declared sampled summaries | Qs or Qc | R1 | EQ-003 |
| session.quote.state_counts | Valid, locked, crossed and invalid observation counts | Qs or Qc | R1 | EQ-003 |
| session.quote.time_weighted_spread | Time-weighted spread over valid intervals with coverage duration | Qc only | R1 | EQ-003 |
| history.return | Close-to-close horizon return; defaults 1/5/20/60/252 sessions | D, A where required | R2 | EQ-004, EQ-006 |
| history.sma | Simple moving average; defaults 20/50/200 | D | R2 | EQ-004 |
| history.ema | Exponential moving average; default 20 | D | R2 | EQ-004 |
| history.rsi | Relative strength index; default 14 | D | R2 | EQ-004 |
| history.atr | Average true range; default 14 | D with OHLC and previous close | R2 | EQ-004 |
| history.prior_high | Prior-only rolling high; defaults 20/60/252 | D with highs | R2 | EQ-004 |
| history.prior_low | Prior-only rolling low; defaults 20/60/252 | D with lows | R2 | EQ-004 |
| history.return_volatility | Historical return volatility with explicit scaling/convention | D | R2 | EQ-004 |
| baseline.daily_volume | Prior-only average daily volume; default 20 | D with volume | R2 | EQ-005 |
| baseline.relative_volume | Supplied target volume relative to prior-only baseline | Target volume, baseline | R2 | EQ-005 |
| baseline.interval_volume | Prior-session volume baseline per caller-defined bucket | H | R2 | EQ-005 |
| baseline.interval_relative_volume | Target interval volume relative to compatible bucket baseline | Target buckets, baseline | R2 | EQ-005 |
| relative.market_return | Symbol return minus supplied market benchmark return | Compatible returns, R | R2 | EQ-005 |
| relative.sector_return | Symbol return minus supplied sector benchmark return | Compatible returns, R with membership | R2 | EQ-005, EQ-006 |
| breadth.direction_counts | Advancing, declining and unchanged member counts | U, compatible returns | R2 | EQ-005 |
| breadth.above_sma_fraction | Fraction above configured SMA, with eligible and expected-member coverage | U, closes and SMA | R2 | EQ-005 |

Structured features may have multiple typed fields. Per-observation quote evidence is optional returned evidence; its storage is not an accumulator's obligation. Top-K has bounded evidence and a fixed selection definition; a notional-ranked variant would be a separately specified feature.

Scalar comparisons derivable from already supplied features, such as close-minus-SMA, can be caller expressions. Additional named features require a scope amendment rather than an undocumented registry entry.

EQ-093 adds an optional custom-feature extension mechanism in R3. Consumer namespaced definitions do not expand or overwrite this39-ID built-in catalog; their correctness and capability tests remain consumer responsibilities.

## Batch, streaming and partition support

| Family | Batch | Incremental v1 obligation | Partition rule |
| --- | --- | --- | --- |
| Session bars/structure | Required | Bar accumulator over supplied ordered completed intervals | Only explicitly implemented identity/order-safe merges; interval boundary conservation required |
| Session trades/top-K | Required | Required, bounded state and versioned restore | Aggregates/top-K can merge only under documented compatibility, duplicate and order rules |
| Sampled quote summaries/counts | Required | Required summaries/counts; no unbounded retained observation list | Supported aggregate merge only; retained per-observation evidence is caller-managed |
| Continuous time-weighted quotes | Required for Qc | Required bounded carry state with gap/validity handling | Arbitrary chunks cannot merge without quote-boundary state; no general merge promise |
| History indicators/returns/extrema | Required | Supported SMA/EMA/RSI/ATR/rolling calculations explicitly registered; exact per-feature state tests required | Ordered session history; no arbitrary merge of EMA/RSI/ATR states |
| Baselines | Required | Daily/interval rolling state where explicitly registered | Prior-window and grid boundaries preserved; no unrestricted merge promise |
| Relative and breadth | Required | No event-stream accumulator promised; recompute from compatible supplied results | Universe completeness and input horizon compatibility checked |
| Composition | Required | No incremental join engine | Align complete supplied families; no dependency fetching |

Registry metadata must state actual implemented batch/update/restore/merge capabilities. A family description does not permit exposing an untested streaming feature. Accumulator snapshots cannot report an earlier cutoff after later events were consumed. Late corrections require explicit caller replay/rebuild behavior in v1.

## Shared quality and evidence requirements

All IDs report applicable readiness, actual/expected coverage, window observations, adjustment basis, cutoff and algorithm/configuration identity. Availability is separate from mathematical computability. Missing required references make affected fields unavailable while independent fields remain usable. An observed empty session differs from no session input.

Trade VWAP and a bar-close proxy remain distinct; TBBO-style samples cannot provide continuous time-weighted quote statistics. Volatility cannot assume a hidden annualization factor. Historical warm-up uses supplied governed sessions and explicitly handles gaps. Prices, quantities and notional use declared precision and overflow policies; epochs never pass through floating-point seconds.

## Exclusions and later scope

- Provider/file/database I/O, calendars fetched internally, credentials, caches, scheduling and output publication: later adapters/workers.
- Scanners, rankings, watchlist memberships, strategy scores, entries/exits, transaction-cost simulation and forward outcomes: separate strategy/label packages.
- Options, futures, order books, queue position, order-flow reconstruction, continuous spreads inferred from trade snapshots and security classification inferred from ticker text.
- Proprietary trained models, specialized anomaly/pattern scores and detailed technical/price-action features beyond the catalog above.
- Guaranteed live feed recovery, retrospective arbitrary snapshots, arbitrary mergeable indicator state and unrestricted exact streaming quantiles.
- Hosted data access and MCP inside calculations; native acceleration without profiling.

## Scope acceptance and subsequent stories

EQ-001 freezes the 39 planned feature IDs above, shared quality/evidence requirements, capability boundaries and exclusions. It does not approve precise formulas, claim calculations are implemented or assert any provider data is historically admissible.

Before implementing each family, EQ-002–006 must define exact mathematical/temporal semantics and independent expected examples. EQ-011–016 turn these into schemas/config/results/registry/protocols. Any new ID, changed feature meaning, expanded market scope or stronger stream/merge promise requires a reviewed scope revision and linked story.
