# EQ029 RSI/ATR pre-code plan

Issue34/E05#31/R2;13 provisional complexity points. EQ028 and prior dependencies
are verified Done. This frozen plan precedes source implementation.

RSI N>=2/default14 uses first Nchanges from explicit close anchor (N+1closes)
to seed average positive/negative deltas, then Wilder ((N-1)*prior+delta)/N.
RSI=100*G/(G+D), entirely flat seed50/gain-only100/loss-only0. Every close
anchor-through-target required. Flat continuation after a nonneutral state must
preserve that ratio even after absolute magnitudes would underflow binary64.

ATR N>=1/default14 uses explicit TRanchor, each TR=max(H-L,abs(H-prevC),
abs(L-prevC)); first NTRmean seed then Wilder recurrence. Previous close before
TRanchor is mandatory; no high-low fallback. Target current close is not a
current TR dependency; preceding closes and every TRhigh/low are required.
Period1 latestTR/coveredzeroTR valid0. Missing high/low blocks ATR independently
of close-derived RSI. No gap skip/reset; explicit new epoch or admissible replay.

Extend compute_history batch only. RSI completed_eod WindowSpec.count=N+1,
ATR completed_eod count=N; use separate configurations/calls because anchor and
membership differ. EMA/SMA existing calls remain. RSI dependencies/quality count
all anchor-to-target close rows; ATR count preceding anchor close plus all TRrows,
requiring at least N+1rows. At each ATRrow require high/low and prior-close context;
target's close is optional, earlier TRrow closes are needed for the next TR.
TRanchor at the first supplied grid row lacks a governed previous-close slot and
stays insufficient_history; an existing preceding slot with missing/null close
is incomplete_coverage. Never synthesize a predecessor ID or high-low seed.
Same context/source/grid/unit/basis/C/K/E/action/structural guards and original
bounded evidence. Missing/unknown warm-up/readiness remains explicit/null.

Representation: bounded binary64 RSI gain proportion r and normalized positive
total-magnitude mantissa with signed int64 base2exponent; zero total is explicit.
Exact seed sums/ratio then Float64. On delta0 decay magnitude but preserve r
unchanged. On nonzero delta align old decayed and new abs(delta)/N terms at the
larger exponent, combine weighted gain proportions, normalize magnitude. Terms
underflow only when below binary64/tolerance contribution to a dominant new term;
they never turn a still nonzero old-only state into neutral50. Guard exponent
bounds explicitly. No retained unbounded Fraction recursion or published state API.
ATR uses exact int64 differences/transient decimal128 seed and bounded Float64
recurrence in scaled units. Independent exact Fraction/80-digit Decimal oracles
qualify rtol/atol1e-12, not library/source copies or performance claims.

Tests: hand period3 RSI4700/57/ATR122/9, default14, ATR1 with previousclose gaps,
gain/loss/entirely-flat seeds,20000+flat nonneutral continuation and later movement,
missing seed/continuation and recovered new epoch, current ATRclose independence,
high/low/close guards, wide/scaled/small prices/long oscillations, future mutation,
knowledge/causal/reconstruction/action and revised context identities. Preserve
existing session/averages and123references; explicitly false history state modes.

Pair0.0.3a3 adds two batch flags (30total),39definition math unchanged; session23
update/restore22merge unchanged. Config/results/context schema1 and sessionstate2
unchanged but exact-version restore needs replay. This supersedes unqualified
private HistoryAccumulator/HistoryState proposals under handoff batch-first scope
and conditional supported-mode acceptance, no waiver or future state promise.

Public API/precision/anchor/mode/migration/examples/contracts/registry/changelog/
lesson/continuity with source. Pre-code plan commit before implementation. Author
self-review+CI labeled honestly. Local unit/reference/type/purity/import/license/
compatibility/docs gates, exact-head repeat4archives/freshwheel+sdist, SIX PRchecks,
guarded merge/tree/main docs/bothOS CI/actual bundles/fourfreshpair installed tests
and final receipt/main byte equality before eight-stage Released/Done. No provider/
source acquisition/private copying/throughput/stable/tag/PyPI; R3 stays paused.
