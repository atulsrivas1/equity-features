# Equity Features Intraday

Experimental pure supplied-data intraday preparation, under EQ137 development.
The original R17 specification and exact pre-code plan live in the canonical
repository's `docs/api/INTRADAY.md` and `docs/stories/EQ-137_PLAN.md`.

This package does not fetch, read databases/files, consult clocks, schedule or
publish. Callers supply canonical BAR facts and an explicit bounded intraday grid.
Preparation preserves independent field readiness and exact source/configuration
identity. Existing core discovery and daily calculations remain separate.

The selected EMA/RSI/ATR and band output kernels belong to EQ138/EQ139. This
development version makes no installed-artifact, performance or release claim.
Public incremental update, checkpoint restore and arbitrary merge are unsupported.
