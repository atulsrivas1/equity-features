# Session mathematical semantics

Decision: EQ-002, definition version1. Original synthetic specifications under Apache-2.0.

Choose explicit supplied target/auction/eligibility policies, not hard-coded provider conditions. Ordinary event ranges are half-open; designated closing auction at exactly close is the only supported endpoint exception when explicitly included. Bars are indivisible completed intervals with compatible construction policy; subwindow straddling is unsupported. This keeps feed acquisition and historical normalization outside calculations.

Choose positive-size eligible trades and integer-share v1 quantity units. Observed empty bars carry zero volume/null OHLC; nonnull stale zero-volume bars require caller normalization. This prevents fabricated price observations. Canonical schemas and provider mappings must expose these assumptions instead of silently discarding data.

Choose fraction returns/ranges, actual trade VWAP/notional, and a distinctly named bar-close proxy. Do not infer actual notional from bar prices. Null is used for undefined ratios and prices, with independent count/volume zeros only for fully observed empty input. Missing coverage yields unavailable formal values; observed aggregates can be evidence. Partial cutoff results remain labeled as such.

Choose exact rational fixture arithmetic and checked production accumulation with documented float tolerances. Choose deterministic top-K by quantity, then supplied order, rather than notional ranking or incidental input order. No silent sort/dedup or historical price-basis adjustment. Compatibility of prior close is required; action/availability policy stays EQ-006.

Alternatives rejected: closing both endpoints for ordinary intervals (double counting); OHLC proration; replacing empty price with yesterday's close; labeling close-weighted bars as VWAP; average-of-batch-VWAP reduction; flat-range close-location0.5; fixing vendor-specific trade-condition tables in the numerical package. These change meaning or hide evidence and would need separately specified features/policies.

Impact: future contracts/adapters must supply identity, eligibility, boundaries, complete coverage and compatible units/basis. These decisions don't require source I/O in packages and don't qualify proprietary data. Extended hours, fractional quantities, provider recovery and ambiguous aggregated-trade inputs need later explicit contracts, not accidental acceptance.
