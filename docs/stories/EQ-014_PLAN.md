# EQ-014 execution plan

Story #17, E03/R0;8points confirmed on pull. Prerequisites: equations/timing and
actual EQ-011–013 alpha3 input/spec/result/error delivery. Inspect live Project/
issue and clean main. First action: map EQ-002/003/006 order, bar/trade validity,
quote classification, exact scale and admission rules to executable checks.

Implement pure semantic validation of caller batches: per-entity/session total
order, event/interval/references identity uniqueness and tie ambiguity, nonoverlap,
nonnegative quantities, eligible positive trades, positive-volume OHLC coherence,
zero-volume/null-OHLC and actual notional bounds, supplied session/auction bounds.
Crossed/locked/nonpositive/null quotes remain classified observations, never dropped.
Absent optional payload fields are reported for dependent readiness; present malformed
eligible values fail. Optional supplied C/K/E returns knowledge exclusions without
mutating/filtering input. Checked int64/decimal128 sum/product helpers use wide Python
arithmetic then enforce representation; no wrapping or feature calculator.

Normalization is opt-in: exact per-partition sort, only explicitly identical-row
deduplication (conflicting identities fail), same-currency price/notional rescale with
exact or declared half-even rounding. Always owned output; input identity/mapping
changes only when data/order/representation changes, with source snapshot preserved,
new content digest and original-row mapping. Never basis/FX/calendar conversion.
Explicit float conversion declares binary64-exact vs decimal-repr interpretation and
rounding, rejects nonfinite/out-of-range values and records quantization evidence.
No implicit cast, lazy iterable, source access or correction replay.

Tests: independent sorted/unsorted/tie/duplicate/overlap fixtures, empty/missing/null,
auction/early-close/known-at bounds, quote four-state preservation, zero-volume/OHLC/
notional violations, int64/wide products and sums, positive/negative half-even/exact
scales, float0.1 interpretation, mutation ownership, identity changes and idempotence,
conflicting dedup rejection and compatibility. Keep87units/123references, strict
mypy/boundary/core isolation, installed runnable example and repeat builds, exact
Linux/Windows head/main CI, published bytes and actual alpha0.0.1a4 artifacts before
Done. API/docs/plan/continuity included; author self-review only. Registry/protocols
EQ-015/016 next; no R1/R2 calculators or R3 callbacks. E03 remains open.

## Focused rework2026-10-05

EQ-015 schema mapping found nonpositive close-only daily input could bypass semantic
price checks when volume was absent. EQ-004 requires independent positive price
admission. Preserve registry draft, reopen EQ-014/In progress and EQ-015 Backlog.
Implement positive supplied OHLC/coherence independently of volume while preserving
legitimate zero-volume/null-OHLC and missing-field independence. Add negative close/
unknown-volume, inconsistent close/high/low and valid close-only fixtures. Deliver
new experimental0.0.1a4.post1 artifacts through all normal gates, then reaccept and
resume preserved EQ-015 alpha5 work. No formulas changed; author self-review only.
