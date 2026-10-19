# Intraday foundations contract

EQ136 [#470](https://github.com/atulsrivas1/equity-features/issues/470), R17. Working original contract for separate review; not accepted mathematics or implemented API. The [initial proposal](../stories/EQ-136_PLAN.md) is preserved as history. This document refines direct dependencies and precision using explicit synthetic counterexamples. [Packaging choice](../decisions/R17_INTRADAY_PACKAGE.md).

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

These are eight own optional-package IDs, not additions to the current core 39-ID registry. The package's discovery/version contract remains to be frozen before dependent implementation Ready. A supplied compatible prepared moment/range object may satisfy a direct operand without computing another feature's output. A feature label alone is never a compatibility proof.

ATR does not read the target close in current arithmetic. Its predecessor close is mandatory; do not silently replace the first TR with H-L. It does not need H/L at the initial close anchor. RSI is 100 for gain-only, 0 for loss-only and 50 only when the initialized gain/loss sums are both mathematically zero. A flat continuation after movement preserves their ratio even when naive floating recurrence would underflow.

Band variance is population price variance, not return volatility or sample variance. Zero variance produces available equal middle/upper/lower and available width ratio 0; only position is not_applicable/zero_denominator. Band position can lie outside [0,1]; do not clamp. Prices are positive, so an admitted complete window has positive mean.

## Precision counterexample and qualification

For scale0 closes [2^60-1,2^60,2^60+1], N=3 and k=2: mean=2^60, V=2/3, radius=2*sqrt(2/3), width ratio=4*sqrt(2/3)/2^60 and position=1/2+1/(4*sqrt(2/3)). Float64 upper and lower can both round to 2^60. Their rounded difference is zero although mathematical width is positive. Therefore width and position consume the unrounded radius/centered residual witness, not rounded published bounds. This removes an unnecessary dependency barrier and preserves the intended mathematics.

An independent oracle must center in exact integer/rational arithmetic before square root or conversion; computing mean(x*x)-mean(x)^2 in Float64 is not a sufficient reference. Do not silently clamp material negative variance, overflow or nonfinite arithmetic. Exact guarded or stable bounded algorithms are implementation choices that must meet a frozen error contract and resource plan. The final per-output tolerance, supported numeric bounds and typed arithmetic-failure behavior are explicit remaining EQ136 decisions; the old draft's general tolerance proposal alone does not qualify this adversarial case.

## Admission and readiness boundaries

Validate supplied canonical structure and identities before cell readiness. Absent optional H/L columns cannot block EMA/RSI/bands. Malformed supplied H/L metadata or contradictory supplied OHLC are not ignored. In the existing BAR contract, positive-volume supplied-null OHLC is malformed even when absent OHLC columns are legal; a zero-volume row has null OHLC and cannot become an invented unchanged close. Use structural validation without default all-OHLCV field requirements, then determine required fields by the requested output's own closure.

Missing whole inputs, absent columns, null/empty slots, insufficient warm-up, governed gaps and knowledge exclusions retain distinct quality reasons. Expected/observed counts refer to the feature's governed dependency slots, never to all requested features as one global status. Final precedence and evidence serialization are still EQ136 API deliverables. A missing out-of-window close does not block a complete rolling band window; a required gap anywhere in an anchored EMA/RSI/ATR chain does block that recursive branch until explicit replay/reinitialization.

## State, performance and remaining specification work

R17 selects batch snapshots and explicit full-history replay; public update/restore/merge are unsupported for this first optional version. Internal reusable preparation must be immutable, bounded and bound to exact instrument/population/grid/scale/action/window/anchor/cutoff/configuration/source-revision identities. Recurrences within a symbol remain ordered. Shared admission/preparation and independent symbol/family work may run in existing supported worker modes; no new executor or unconditional concurrency increase is selected here.

Before EQ136 acceptance, freeze exact constructor/function signatures, closed context/config transport and limits, own discovery digest/version rules, per-cell status/reason/evidence precedence, numerical error bounds and independent temporal/missingness/precision goldens. Before any dependent kernel Ready, independently review and publish that complete specification. EQ136 itself claims no production implementation, installed package, benchmark or R17 acceptance.
