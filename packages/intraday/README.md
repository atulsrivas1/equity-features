# Equity Features Intraday

Experimental pure supplied-data intraday preparation and snapshot EMA/RSI/ATR and rolling price bands,
distribution `equity-features-intraday`0.1.0a4, Python3.12, Apache-2.0.
Callers supply canonical BAR facts, actual exchange sessions and an explicit
bounded intraday grid. Context/configuration, coverage, action/unit/source
identity and known-at eligibility are validated without acquisition or I/O.

`prepare_intraday` builds selected immutable operands: anchored closes, true
ranges, rolling price moments, high/low extrema and latest simple return.
Each family retains its own required fields, status, counts, reasons and
bounded evidence. Missing H/L does not block close-only calculations. Reuse
requires the same original immutable batches plus exact context/configuration;
there is no global cache or public serialization/restore/merge.

See the [supplied synthetic example](https://github.com/atulsrivas1/equity-features/blob/main/examples/intraday_preparation.py),
[API](https://github.com/atulsrivas1/equity-features/blob/main/docs/api/INTRADAY.md)
and [measurement evidence](https://github.com/atulsrivas1/equity-features/blob/main/docs/stories/EQ-137_BENCHMARK.md).
The recorded one-process preparation benchmark at sourcec7a46d6 reduced median
elapsed time59.55–64.76% across six synthetic workloads with full projection
parity and declared resource gates; this is no library ranking or worker SLA.

`compute_intraday` calculates selected EMA/RSI/ATR cells, using exact rational
seeds and ordered Decimal120 recurrences in an explicit local context. Each
output has its own N/N+1 warm-up, required fields, quality and evidence. RSI
preserves the initialized gain/loss ratio through a long flat tail. Shared
preparation and direct calls produce the same complete selected result.
Rolling middle/upper/lower/width/position consume exact population moments
and an unrounded radius witness. Cancellation-safe expressions preserve exact
zeros, tiny/nonpositive lower values and positions outside[0,1]. Zero variance
leaves price bands and width available; only position is not applicable.
Own discovery has eight executable batch IDs, with all state flags false.
This a3 source is under EQ139 qualification; source tests do not establish
installed delivery or new measured performance.
Existing core39 discovery and daily calculations remain unchanged. Public
incremental update, checkpoint restore and arbitrary merge are unsupported.

The channel is qualifying GitHub Actions main artifacts/source with finite
retention, described in the repository build/delivery guide; registry/stable
publication is not selected. [EQ137 acceptance](https://github.com/atulsrivas1/equity-features/issues/471)
records accepted preparation0.1.0a1 delivery. [EQ138](https://github.com/atulsrivas1/equity-features/issues/472)
records accepted0.1.0a2 delivery. [EQ139](https://github.com/atulsrivas1/equity-features/issues/473)
records current0.1.0a3 review, qualification and delivery status. Historical
preparation timings do not establish output performance for this version.
