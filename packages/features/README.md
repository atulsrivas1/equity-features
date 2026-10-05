# Equity Features

Experimental0.0.2a1, Apache-2.0, depending inward on equity-feature-contracts.
Fourteen batch bar/price/structure IDs are implemented through equity_features.session.compute_bars.
Source-independent caller-supplied canonical inputs, config and entity are required;
see docs/api/SESSION_BARS.md and examples/session_bars.py in the repository.

Immutable39-ID discovery and caller-scoped metadata registration remain available.
Only the fourteen bar/price/structure IDs advertise batch support; other families and every
update/restore/merge/custom execution mode remain unimplemented.

Delivery uses experimental main GitHub Actions artifacts, pending verified receipts
for this version. No public registry, stable API or throughput claim.
