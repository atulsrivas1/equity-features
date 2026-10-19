# Equity Features Intraday

Experimental pure supplied-data intraday preparation, distribution
`equity-features-intraday`0.1.0a1, Python3.12, Apache-2.0.
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

Own discovery describes eight planned EMA/RSI/ATR and band outputs, but all
output capabilities are false in this preparation-only version; invoking an
output raises UNSUPPORTED_CAPABILITY. Output kernels belong to EQ138/EQ139.
Existing core39 discovery and daily calculations remain unchanged. Public
incremental update, checkpoint restore and arbitrary merge are unsupported.

The channel is qualifying GitHub Actions main artifacts/source with finite
retention, described in the repository build/delivery guide; registry/stable
publication is not selected. [EQ137 acceptance](https://github.com/atulsrivas1/equity-features/issues/471)
records actual current review, installed-platform and delivery status.
