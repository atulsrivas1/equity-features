# Historical equity mathematical contract

Definition version1; owner EQ-004, with EQ-006 joint return/reference admission policy. Covers8history IDs in V1_SCOPE.md. This document and synthetic references specify mathematics. Current source/qualification is linked in the [history API](../api/HISTORY.md) and receipts; no trusted provider history is certified.

## Supplied grid, completion and price basis

Caller supplies instrument/namespace, immutable input identity, currency/price scale, compatible adjustment/reference policy and availability evidence, ordered governed session IDs with completed session bounds, target session/cutoff and explicit initialization anchor for recursive features. Counts use governed trading sessions, not calendar days or rows that happen to contain data. Omitted expected sessions remain null/missing slots; no forward fill, skip or compressed rolling window. Holidays/nontrading dates are absent from the supplied session grid by calendar policy, not guessed from missing prices.

Prices are positive exact scaled int64 coefficients, p=coefficient/10^scale. Nonfinite/noninteger/nonpositive price-bearing values are invalid; missing prices use null. Missing input is distinct from observed empty/no-price sessions. High/low must be coherent, and supplied close lies within supplied high/low where all are present. Complete close-only inputs support close features independently of absent high/low columns. All needed sessions must be completed at cutoff (end<=cutoff) and available under the declared knowledge/simulation policy. Completed target indicators cannot use a forming target close. Prior-only extrema may be eligible earlier because they do not consume target prices. Generation time never establishes causal availability.

Exactly one normalized row/slot per instrument/session; duplicates, wrong identity/grid order and malformed timestamps are validation errors, not silently sorted/deduplicated. All input columns must have compatible scales/currency/basis or explicit caller normalization. Raw/adjusted data, split factors and current revised references cannot be mixed implicitly. EQ-006 owns corporate-action and point-in-time admission; unknown reference eligibility remains unknown/unavailable. This contract assumes compatible admitted inputs conditionally and does not certify them.

## Notation and defaults

Target session index t; close C_i, high H_i, low L_i; integer period N or return horizon h. Simple session return r_i=C_i/C_(i-1)-1. Price outputs are currency/share. Return/volatility are dimensionless fractions; RSI is on0–100scale. Default return horizons1/5/20/60/252; SMA20/50/200; EMA20; RSI14; ATR14; prior extrema20/60/252. Default volatility window20returns, sample denominator N-1 and factor A=1 (unannualized). Configuration/version identity carries actual periods, anchors, initialization, volatility return basis and A. Periods>=1 except RSI/volatility>=2; no boolean/fractional periods. No implicit252annualization.

## Exact definitions

| Feature ID | Equation and required membership | Units | Period3worked expectation at t5 |
| --- | --- | --- | --- |
| history.return | C_t/C_(t-h)-1; h+1complete consecutive governed price slots required, target included | fraction | h3:5/21 |
| history.sma | sum(C_i,i=t-N+1..t)/N; Ncomplete closes | currency/share | 365/3 |
| history.ema | At anchor a: seed E_(a+N-1)=sum(C_a..C_(a+N-1))/N; later E_i=alpha*C_i+(1-alpha)*E_(i-1), alpha2/(N+1) | currency/share | anchor0:975/8 |
| history.rsi | Delta_i=C_i-C_(i-1); G_i=max(Delta_i,0),D_i=max(-Delta_i,0). Seed Gbar/Dbar by firstNchanges from close anchor; update Xbar_i=((N-1)*Xbar_(i-1)+X_i)/N; RSI=100*Gbar/(Gbar+Dbar), with both0=>50 | RSI points0–100 | anchor0:4700/57 |
| history.atr | TR_i=max(H_i-L_i,abs(H_i-C_(i-1)),abs(L_i-C_(i-1))); seed average firstNTRs from TRanchor, then ATR_i=((N-1)*ATR_(i-1)+TR_i)/N | currency/share | TRanchor1:122/9 |
| history.prior_high | max(H_i,i=t-N..t-1), excluding target | currency/share | 122 |
| history.prior_low | min(L_i,i=t-N..t-1), excluding target | currency/share | 103 |
| history.return_volatility | r_i over i=t-N+1..t; mean=sum(r_i)/N; variance=sum((r_i-mean)^2)/(N-1); sigma=sqrt(A*variance), with Aexplicit positive integer and default1 | fraction; scaled units declared | variance476449/44791488; sigma≈0.10314 atA1 |

Return uses h+1complete slots even though only endpoints enter its arithmetic: missing governed price coverage is not quietly accepted. Prior extrema need Nprior observations, not N-1plus target. Volatility consumes Nreturns from N+1closes; it is centered sample standard deviation, not RMS, population variance or standard deviation of prices. This built-in version uses simple returns only; log-return or alternative denominator conventions require a separately approved mathematical variant/version, never silent backend defaults. A is sessions per year for square-root-time scaling; supplying it is a convention, not a claim that an annual risk model is empirically valid. A=1means per-session unannualized output. No return or volatility floor at0beyond the nonnegative variance definition.

## Initialization, warm-up and edge values

SMA/EMA first available after Ncomplete closes. EMAperiod1is the supplied close. RSI first available after Nchanges, requiring N+1closes from declared close anchor; gain-only yields100, loss-only0 and initialized entirely flat history50. Neutral50is an explicit convention for the0/0case, not a computed ratio or missing-data fill. After nonzero movement, a flat continuation decays both averages proportionally and preserves their ratio in exact arithmetic; implementations must handle numerical underflow stably rather than silently turn a previously nonneutral RSI into50. Tolerance/backend changes require numerical qualification.

ATR requires compatible previous close for each TR. If TRanchor is a, require C_(a-1) plus Ncomplete high/low states from a through a+N-1 and subsequent necessary closes/TRs. Never replace the first missing previous close with high-low and silently change the seed. ATRperiod1equals latestTR, not merely latesthigh-low. A flat session and unchanged previous close give true range0and validATR0. Current close is not in currentTRarithmetic, but is required for the following session'sTR.

All recursive results depend on initialization anchor and every required observation since it. Histories with different anchors can legitimately yield different results and cannot be labeled identical calculations. Cold-start EMA is mathematically seeded but not proven insensitive to a longer history. State metadata binds anchor/config/algorithm/input prefix; restored state must match those identities. A supplied previous-close context does not count as an extraTR/sample.

## Missingness, gaps and availability

Absent whole input or required field/reference columns are missing_input. Too few governed slots since required window/anchor is insufficient_history. A present expected slot with absent/null prices, incomplete coverage or uncompleted required session produces incomplete_coverage; its arithmetic is not published as a complete feature. Ineligible/unavailable reference inputs produce null with explicit reason and appropriate missing-input/readiness state; schema/order/basis inconsistency is a typed validation error. Every unavailable value stays null, never0,50or a previous value. Field readiness is independent: absent high may blockATR/prior_high while close-derivedSMA remains usable.

Finite windows recover once every slot in their exact required window is complete. Recursive EMA/RSI/ATR do not skip gaps or restart automatically; their anchor-to-target dependency remains broken. Caller may deliberately start a new initialization epoch with a new declared anchor/config/state identity and fresh warm-up, or supply corrected admissible history and replay. Such results are not continuity with the previous state. Omitted holidays do not break a valid supplied grid; an omitted expected trading session does. Whole-observed empty history has insufficient history, not price0.

Compatible corporate-action adjustments can be required across an entire recursive prefix, not only the lastNrows. Revised earlier history invalidates dependent state/results. In a backtest, current adjusted data cannot be silently substituted for facts available at the historical cutoff; EQ-006 establishes that admission. This document neither fetches calendars/actions nor executes adjustment policies.

## Precision, state and partition semantics

Sums/products/differences and variance intermediates use sufficiently wide checked representations or guarded numerical algorithms; int64 sums of valid prices may exceed int64 even when the mean fits. Reference fractions are exact, volatility square roots use high-precision decimal, and final float64 acceptance uses rtol1e-12/atol1e-12 in stated units against qualified references. Stable centered variance is required; materially negative variance from numerical failure is an error, not abs(variance). Any bounded roundoff clamp needs explicit tested tolerance during backend implementation.

SMA/extrema/return/volatility need their stated rolling window/context and governed coverage. EMAstores initialized E; RSIstores gain/loss averages plus last close; ATRstores its average and previous close. All carry bounds, initialization, readiness and compatibility identities. Sequential batches with compatible carry must equal batch evaluation from the same anchor. No arbitrary merge of EMA/RSI/ATRstates or averaging partition indicator values. Snapshot cannot request an earlier cutoff after later data was consumed. Corrections require ordered replay from compatible prior state or rebuild; EQ-037/state stories qualify actual supported update/restore APIs later.

## Worked example and references

Closes100,110,105,120,115,130; highs102,112,111,122,121,132; lows98,99,103,104,113,114. Period3at target5; close anchor0,TRanchor1. Fixture README independently derives every table expectation and seed/update. Run `python tools/verify_history_examples.py`; preserve session/quote reference checks too. These references do not implement production kernels or certify performance/provider data.

Conventional recurrence references: [TA-Lib EMA](https://ta-lib.org/functions/ema.html), [RSI](https://ta-lib.org/functions/rsi.html), [ATR](https://ta-lib.org/functions/atr.html). They document standard smoothing/seed definitions; this repository separately fixes grid, cutoff, gap and flat-history conventions and does not claim full third-party implementation/default parity.
