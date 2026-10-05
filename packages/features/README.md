# Equity Features

Experimental0.0.2a6, Apache-2.0, depending inward on equity-feature-contracts.
Nineteen batch bar/price/structure/trade IDs are implemented through equity_features.session family calls.
Source-independent caller-supplied canonical inputs, config and entity are required;
see docs/api/SESSION_BARS.md and examples/session_bars.py in the repository.

Immutable39-ID discovery and caller-scoped metadata registration remain available.
Only the nineteen bar/price/structure/trade IDs advertise batch support; other families and every
update/restore/merge/custom execution mode remain unimplemented.

Delivery uses experimental main GitHub Actions artifacts, pending verified receipts
for this version. No public registry, stable API or throughput claim.

EQ020 adds typed bounded original topK trade rows and exact evidence, batch only. See docs/api/SESSION_TOP_K.md in the source repository. No merge/update/restore capability or throughput claim.

EQ021 adds compute_quotes for two event-weighted quote IDs with sampling identity and bounded observations. No duration coverage, quantile, streaming or throughput claim. See docs/api/SESSION_QUOTES.md.

EQ022 adds compute_time_weighted, continuous only, with explicit age/initialization/seed, original-anchor expiry and exact category conservation. Batch only; no source acquisition or performance claim.

EQ023 adds SessionAccumulator with supplied chunks, fixed source/schema, explicit prefix certificates, atomic update/snapshot/finalize and bounded family state. Pure single-caller lifecycle; no restore/merge, acquisition or throughput claim.

EQ024 adds immutable AccumulatorState and exact compatible in-memory restore for all23 R1 IDs; see [incremental API](../../docs/api/INCREMENTAL.md). Strict schema/version/source/config checks and bounded owned state apply; digest is not authentication. Merge remains false.

EQ025 qualifies conditional adjacent caller-certified partition merge for22 noncontinuous R1 IDs; current inventory23 batch/update/restore and22 merge. Continuous merge remains false. See the incremental API for proof, order, retention and replay limits.
