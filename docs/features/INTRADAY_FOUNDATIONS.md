## EQ139 cancellation-safe source evaluation

[EQ139 accepted plan](../stories/EQ-139_PLAN.md) retains the equations/units/schema/math policy below. The a3 implementation forms exact squared radius and exact lower/negative-position numerators before Decimal120 division, preserving exact zero/sign near cancellation. Independent centered/pairwise Fraction and direct high-precision oracles plus [original fixtures](../../tests/fixtures/intraday_bands/README.md) verify source behavior; production moments and shared-call parity are not the sole numerical reference. Rolling window readiness remains independent of old anchored gaps and unrelated H/L. Final installed/performance/release acceptance remains EQ139.

## EQ138 independent output and measured-sharing evidence

Independent exact impulse-response/interval-envelope cases validate102 scenarios/186 available scalar values/78warm-up checks, distinct from A/B parity. [Measured sourcef1](../stories/EQ-138_BENCHMARK.md) qualifies shared requests for all3indicators in six frozen cases; individual cases keep direct fallback. Actual math/units/warm-up/coverage/Float64 tolerance do not change. Current final source/installed/main acceptance remains the implementation issue's gate.

## EMA/RSI/ATR implementation checkpoint

[EQ138 plan](../stories/EQ-138_PLAN.md) implements the three accepted batch recurrences using exact rational seeds, explicitly local Decimal120 arithmetic and one guarded final Float64 conversion. Independent original expanded geometric weights verify seeds/tails/scale/wide offsets, with long-flat RSI and hostile global-context cases. Each output uses its own required operands and N/N+1 warm-up; no bands/output dependencies or public recurrence state are introduced. Actual qualification and release evidence remains on EQ138.

# Intraday foundations contract

EQ136 [#470](https://github.com/atulsrivas1/equity-features/issues/470), R17. Accepted original mathematical contract; actual implementation/release acceptance belongs to the linked implementation stories. The [initial proposal](../stories/EQ-136_PLAN.md) is preserved as history. This document refines direct dependencies and precision using explicit synthetic counterexamples. [Packaging choice](../decisions/R17_INTRADAY_PACKAGE.md).

## Governed observations

Caller-supplied positive scaled integer prices have one compatible currency/scale/action basis. Actual BAR slots use exact UTC int64 nanoseconds, half-open [start,end) bounds, real exchange session identities, explicit calendar/grid/source/revision identities and an explicit target slot. Slots are positive, ordered and nonoverlapping within their actual sessions. Holidays and session breaks are caller-governed calendar facts; an absent expected slot cannot be compressed away. No sorting, duplicate resolution, resampling, price adjustment or forward fill occurs in calculations.

An observation is complete only when its supplied slot coverage qualifies, end <= C and its knowledge evidence qualifies at K under the explicit availability mode. Unknown or later-known observations remain unavailable in a known-at evaluation. Reconstruction mode must retain its declared reason; it is not relabeled causal. Late corrections require a new supplied revision/configuration and recalculation; earlier results remain immutable.

An explicit reset epoch starts at the first governed bar of the target session and excludes overnight changes. An explicit carry epoch starts at a supplied earlier close anchor and includes each governed successor through the target, including overnight close changes/TRs across supplied sessions. No automatic gap restart or mode switch is permitted. Periods count governed bar observations, not elapsed minutes, observed nonnull rows or WindowSpec session membership.

## Equations and direct operands

Let a be the declared close anchor, t the target and N the integer period. EMA/ATR require N>=1, RSI/bands N>=2; booleans are not periods. Prices in the formulas are exact coefficients in one scale, converted to currency/share for price outputs. A band multiplier k is an explicit finite positive value. There are no implicit period, annualization or multiplier defaults.

| Own feature ID | Mathematical value | Required observations / direct operands |
| --- | --- | --- |
| intraday.ema | Seed E[a+N-1]=sum(C[a:a+N])/N; E[i]=2*C[i]/(N+1)+(N-1)*E[i-1]/(N+1) | All closes a..t; first t=a+N-1 |
| intraday.rsi | Delta[i]=C[i]-C[i-1]; G=max(Delta,0), D=max(-Delta,0); seed means over first N changes, then Wilder X[i]=((N-1)*X[i-1]+current)/N; 100*Gbar/(Gbar+Dbar), both zero =>50 | All closes a..t; first t=a+N; units RSI points |
| intraday.atr | TR[i]=max(H[i]-L[i],abs(H[i]-C[i-1]),abs(L[i]-C[i-1])); mean first N TRs starting a+1, then Wilder recurrence | H/L a+1..t and predecessor closes a..t-1; first t=a+N |
| intraday.band_middle | mu=sum(C[i],i=t-N+1..t)/N | Last N complete closes only |
| intraday.band_upper | mu + k*sqrt(V), V=sum((C[i]-mu)^2)/N | Compatible exact/stable mean and population price variance |
| intraday.band_lower | mu - k*sqrt(V) | Same moments; no positive lower-bound clamp |
| intraday.band_width_ratio | 2*k*sqrt(V)/mu | Compatible mean and radius witness before output rounding |
| intraday.band_position | 1/2+(C[t]-mu)/(2*k*sqrt(V)) | Compatible centered target-close and radius witness before output rounding |

These are eight own optional-package IDs, not additions to the current core 39-ID registry. The [complete API proposal](../api/INTRADAY.md) freezes discovery/version, numeric and transport choices for review before dependent implementation Ready. A supplied compatible prepared moment/range object may satisfy a direct operand without computing another feature's output. A feature label alone is never a compatibility proof.

ATR does not read the target close in current arithmetic. Its predecessor close is mandatory; do not silently replace the first TR with H-L. It does not need H/L at the initial close anchor. RSI is 100 for gain-only, 0 for loss-only and 50 only when the initialized gain/loss sums are both mathematically zero. A flat continuation after movement preserves their ratio even when naive floating recurrence would underflow.

Band variance is population price variance, not return volatility or sample variance. Zero variance produces available equal middle/upper/lower and available width ratio 0; only position is not_applicable/zero_denominator. Band position can lie outside [0,1]; do not clamp. Prices are positive, so an admitted complete window has positive mean.

## Precision counterexample and qualification

For scale0 closes [2^60-1,2^60,2^60+1], N=3 and k=2: mean=2^60, V=2/3, radius=2*sqrt(2/3), width ratio=4*sqrt(2/3)/2^60 and position=1/2+1/(4*sqrt(2/3)). Float64 upper and lower can both round to 2^60. Their rounded difference is zero although mathematical width is positive. Therefore width and position consume the unrounded radius/centered residual witness, not rounded published bounds. This removes an unnecessary dependency barrier and preserves the intended mathematics.

An independent oracle must center in exact integer/rational arithmetic before square root or conversion; computing mean(x*x)-mean(x)^2 in Float64 is not a sufficient reference. Do not silently clamp material negative variance, overflow or nonfinite arithmetic. Exact guarded or stable bounded algorithms are implementation choices that must meet the API's frozen relative/ULP error contract and resource plan. The linked API proposal defines exact supported bounds, OVERFLOW behavior and the zero-value rule; the old draft's general tolerance proposal is superseded. `tools/verify_intraday_examples.py` uses expanded rational weights and Decimal120, independently of production code.

## Admission and readiness boundaries

Validate supplied canonical structure and identities before cell readiness. Absent optional H/L columns cannot block EMA/RSI/bands. Malformed supplied H/L metadata or contradictory supplied OHLC are not ignored. In the existing BAR contract, positive-volume supplied-null OHLC is malformed even when absent OHLC columns are legal; a zero-volume row has null OHLC and cannot become an invented unchanged close. Use structural validation without default all-OHLCV field requirements, then determine required fields by the requested output's own closure.

Missing whole inputs, absent columns, null/empty slots, insufficient warm-up, governed gaps and knowledge exclusions retain distinct quality reasons. Expected/observed counts refer to the feature's governed dependency slots, never to all requested features as one global status. The linked API defines status precedence and bounded evidence serialization. A missing out-of-window close does not block a complete rolling band window; a required gap anywhere in an anchored EMA/RSI/ATR chain does block that recursive branch until explicit replay/reinitialization.

## State, performance and remaining specification work

R17 selects batch snapshots and explicit full-history replay; public update/restore/merge are unsupported for this first optional version. Internal reusable preparation must be immutable, bounded and bound to exact instrument/population/grid/scale/action/window/anchor/cutoff/configuration/source-revision identities. Recurrences within a symbol remain ordered. Shared admission/preparation and independent symbol/family work may run in existing supported worker modes; no new executor or unconditional concurrency increase is selected here.

The linked API, [synthetic goldens](../../tests/fixtures/intraday_math/README.md), [test strategy](../R17_TEST_STRATEGY.md) and package decision form the accepted specification. Each dependent implementation still requires its own actual Ready inputs, separate final-head review, applicable validation and publication/readback. EQ136 itself claims no production implementation, installed package, benchmark or R17 acceptance.
