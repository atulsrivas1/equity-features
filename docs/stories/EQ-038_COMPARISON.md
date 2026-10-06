# EQ038 Go definition and migration comparison

This report compares the16 frozen R2 numerical IDs with owner-supplied Go
calculation/reference/context/baseline/breadth definitions inspected read-only.
Private source, checkout paths, module identifiers and provenance fingerprints
remain unpublished. Descriptions below are original mathematical summaries;
fixtures and outputs are synthetic. This is not whole-worker/provider acceptance.
[Pre-code plan](EQ-038_PLAN.md), [issue43](https://github.com/atulsrivas1/equity-features/issues/43).

## Actual execution and reproducibility

An original external, untracked harness invoked exported independent EMA and
WilderATR kernels without modifying supplied source or running a worker, scheduler,
provider or database. Actual runtime: Go1.26.7/windows/amd64, native Float64;
read-only module flags, automatic toolchain selection. Exact source/file fingerprints
were checked before and after; private receipt records command, exit0, vectors and
stdout. A separate reviewer can inspect this local evidence. Public CI cannot
rebuild the unpublished Go source: it replays [captured actual observations](../../tests/references/legacy_comparison.json)
and executes the public library against independent goldens via the
[22nd installed example](../../examples/legacy_comparison.py). That distinction is
part of the qualification, not a claim of public Go CI or unexecuted broad parity.

All5vectors were actually executed. Values are in USD/share at coefficient scale0.
Ordinary closes100,110,105,120,115,130; highs102,112,111,122,121,132;
lows98,99,103,104,113,114. EMA3 seed105, then225/2,455/4,975/8.
TRs13,8,18,8,18: ATR3 seed13, then34/3,122/9. Public actual APIs and Go
finite outputs match independent goldens at rtol/atol1e-12 on compatible inputs.

| Vector | Public EMA | Actual Go EMA | Public ATR | Actual Go ATR | Interpretation |
| --- | --- | --- | --- | --- | --- |
| Ordinary,period3 |975/8=121.875|121.875|122/9|13.555555555555557| Matching seed/recurrence on supplied complete vector |
| Two slots,period3 |null,insufficient_history|NaN| null,insufficient_history|NaN| Warm-up representation differs; captured JSON null also records nan classification |
| Six flat100slots,period3 |100|100|0|0| Available zero true range, no invented missing value |
| Ordinary,period1 |130|130|18|18| Latest close/latest true range |
| p=2^63-1,one-tick range,period1 |Float64(p)|Float64(p)|1|0| Native Float64 input conversion loses one-tick range |

The wide vector has closes[p-1,p], highs[p,p], lows[p-1,p-1]. Exact
max(H-L,abs(H-Cprev),abs(L-Cprev))=1. Native Float64 maps p and p-1 to the
same representable number. Go's measured0 differs from public exact-coefficient
arithmetic1. This is a representation capability difference, not a claim that
ordinary Wilder mathematics is defective. The final EMA price rounding alone
cannot prove integer precision; the ATR counterexample exposes it directly.

## Sixteen-ID migration inventory

Executed parity is limited to the independent EMA/ATR kernels above. All other
rows are source-reviewed definitions and independently reasoned migration
requirements; no measured execution is claimed for them. Absence means no
matching definition in the examined paths, not proof about every external system.

| R2 ID | Examined Go definition | Match/difference and required migration |
| --- | --- | --- |
| history.return | Multi-session endpoint and session-change percentages | Cend/Cstart-1 arithmetic agrees after percent-to-fraction conversion; windows/date selection/completion/admission must align; not executed |
| history.prior_high | Prior-day and fixed rolling high reference levels | Max arithmetic agrees for same prior rows; supplied ordered governed slots versus selected reference rows/calendar periods and rounded coefficients differ; not executed |
| history.prior_low | Prior-day and fixed rolling low reference levels | Min arithmetic agrees conditionally; same grid/target exclusion/precision qualifications as high; not executed |
| history.sma | Fixed20/50/100/200 daily close means rounded to reference coefficients | Mean matches conditionally; rounding, fixed windows and reference filtering differ from public exact witness/custom period; not executed |
| history.ema | Mean-seeded exported kernel plus intraday worker state | Independent kernel executed above; worker fixed9/21/50/gap/reset policies are distinct and unexecuted; public anchor/governed gaps must remain explicit |
| history.rsi | Worker14-change mean gain/loss seed, Wilder smoothing, neutral50 when both0 | Conventional recurrence agrees conditionally; worker interval/gap/state and native underflow behavior need qualification; no exported equivalent executed |
| history.atr | Exported Wilder kernel and daily reference; worker firstTR permits high-low without previous close | Exported kernel executed with mandatory previous close; worker seed/timing/reset differs and is unexecuted; do not transplant worker warm-up into public definition |
| history.volatility | Annualized population deviation of logarithmic returns | Different from public sample deviation of simple returns with explicit A(default1); count denominator/transform/annualization/roundoff must change; not executed |
| baseline.daily_volume | Robust daily expectation using median, early-close duration normalization | Different from public mean of exactN prior governed volumes with no implicit duration scaling; not executed |
| baseline.relative_volume | Live cumulative volume/reference expectation and related robust normalization | Ratio arithmetic conditional; numerator timing/completeness and median/scaled denominator differ; unavailable flags differ from typed result; not executed |
| baseline.interval_volume | Minute interval/cumulative baseline builds, sample statistics and compact serving medians | Build contains an arithmetic Expected statistic, but serving denominator uses median; densification/selection/sample count/Float32 compaction differ from exact declared-bucket prior mean; not executed |
| baseline.interval_relative_volume | Median normalization and rolling overlapped-minute prorated expectations | Different from fully elapsed caller-defined individual bucket V/B; rolling/cumulative/pro-rata serving semantics cannot be silently relabeled; not executed |
| relative.market_return | Symbol-minus-market percent change plus separate beta residual | Arithmetic spread agrees after unit conversion; beta residual is a different metric; freshness tolerance differs from exact public endpoint/C-K-E/config alignment; not executed |
| relative.sector_return | Sector percent-change spread with classification/reference state | Conditional spread arithmetic agrees; supplied effective membership and exact identities must replace implicit classification/freshness behavior; not executed |
| breadth.direction_counts | Threshold-qualified evolving/sticky session population; advancing/declining/unchanged counts with prior readiness | Counts conditionally agree on identical admitted members; threshold population differs from immutable declared U/expected count/exclusions; no missing-as-unchanged migration; not executed |
| breadth.above_sma_fraction | Examined breadth calculates aboveVWAP/other ratios; no matching close-vs-SMA fraction | AboveVWAP is not aboveSMA. Public requires exact supplied close/SMA witnesses and eligible denominator; absence limited to examined definitions; not executed |

Independent semantic counterexamples, not measured Go outputs: prior volumes
[100,100,1000] have public mean400 versus median100; target500 yields public5/4
versus median-based5. Missing one expected prior slot remains unavailable rather
than shrinkingN. Simple returns[1/10,-1/10] have sample variance1/50 before
explicit A scaling; log-return population/annualized variance is another definition.
An expected universe of4 with3eligible keeps expected4 and exclusions; a threshold
population of3 alone cannot establish that missing-member coverage. These explain
migration decisions without fabricating runtime comparisons.

## Decisions, documentation and acceptance limits

Keep frozen mathematics and package pair0.0.3a11; package source/dependencies,
input/result/state schemas and39batch/23session update-restore/22conditionalmerge
capabilities are unchanged. R2 historical/contextual/breadth state modes remain
unsupported. No private algorithm, datasets or identifiers were copied into public
packages. Public example/fixture only contain original synthetic data and observed
numbers. No provider correctness, source authenticity, cross-language worker/state
parity, performance, stable/tag/PyPI or new publication channel claim.

Independent local review, exact-head/source gates, repeated builds/fresh installed
22-example qualification, main bothOS actual archives and final receipt remain
required for EQ038Done. Existing accepted036 package execution is reusable only
where exact per-OS archive equality is proven; new example execution is separately
recorded. EQ037 will verify final R2 causality/capabilities and exit; R3paused.
