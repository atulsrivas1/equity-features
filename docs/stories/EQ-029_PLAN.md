# EQ-029 RSI/ATR — pre-code draft

Issue #34; E05/R2;13 provisional points. Requires delivered EQ028 state/context
contract; no code or Ready claim while prerequisite gates remain pending.

RSI seed is firstN changes from explicit close anchor (N+1 closes); subsequent
gain/loss Wilder update ((N-1)*prior+current)/N. N>=2/default14. Flat initialized
seed=50, gain-only100,loss-only0; a nonneutral flat continuation preserves its
gain/loss ratio. ATR uses explicit TR anchor, previous close for every TR,
N TR mean seed then Wilder update; period>=1/default14. No first high-low fallback.
Latest close is only the following TR dependency; missing high/low blocks ATR
independently of RSI. Recursive gaps require new epoch or admissible replay.

Extend public compute_history/HistoryAccumulator/HistoryState for these two IDs
after concrete EQ028 contract qualification. No arbitrary recursive merge.
Avoid unbounded Fraction denominators. RSI state retains normalized binary64
gain/loss mantissas and a bounded signed exponent, plus last exact close, seed
count and identity. Rescale proportionally through flat updates so underflow of
absolute magnitudes cannot manufacture a neutral50. When a later nonzero change
arrives, align exponents before combining; discarded terms must be below declared
binary64/tolerance bound and independently tested. Exponent/count bounds reject
overflow explicitly. ATR/EMA retain qualified bounded Float64 recurrence. Exact
rational and high-precision Decimal oracles are test-only and independent.

Production API goldens: period3 RSI4700/57,ATR122/9; defaults14/period1 ATR;
gain/loss/entirely-flat seeds; 20000+flat updates after nonneutral seed, export/
restore during continuation and later fresh movement; independent high precision
ratio preservation and future response; missing previous close, zeroTR, anchor
changes/replay, maximum int64 prices/wide differences, knowledge/cutoff/gaps,
random synthetic batch/chunk/restored parity, bounded state and typed atomic
malformed/version/identity failures. Preserve repaired session and123references.

Document initialization/required membership, normalized RSI numerical policy and
limits, modes/state migration, example/changelog/version/continuity. Publish plan
before code, accurate author self-review, local/exact-head/main bothOS CI, repeated
archives/fresh installs and actual downloaded source-bound bundles/four installed
pairs precede receipt and all eight lifecycle stages through Done.
