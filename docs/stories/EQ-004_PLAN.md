# EQ-004 — historical formula execution plan

Story [EQ-004](https://github.com/atulsrivas1/equity-features/issues/5); E01/R0; **8points, provisional relative complexity**, not hours or forecast date. Mathematical specification only; no production API/kernels.

## Start and scope

Confirm EQ-001 eight-ID history scope and accepted session/quote contracts, then specify supplied governed grid, cutoff/availability and compatible adjustment input requirements. Define window membership and recursive initialization before individual equations. Derive synthetic expected results independently and add warm-up/gap/causality tests. Review the complete documentation through a linked PR; final-head CI, publication verification and issue evidence precede Done.

## Design and artifacts

HISTORICAL_FORMULAS.md covers return, SMA, EMA, RSI, ATR, prior_high, prior_low and return_volatility. history-semantics.md records initialization, strict recursive gaps and volatility/denominator choices. Synthetic history_math fixtures/README and a standard-library exact verifier check expected arithmetic. CI, scope/dashboard navigation, GitHub acceptance and SESSION_HANDOFF update alongside the story.

## Decisions and bounded dependencies

| Question | Decision / owner |
| --- | --- |
| Which sessions count? | Supplied governed trading-session slots; no compressing missing observations or replacing sessions with calendar days |
| Is target included? | Completed target included for return/SMA/EMA/RSI/ATR/volatility; prior extrema exclude target |
| EMA initialization? | FirstNeligible closes from explicit anchor seed by SMA; alpha2/(N+1); anchor/version part of identity |
| RSI/ATR? | Wilder1/Nsmoothing after firstNchanges/TRs; RSI needsN+1closes, ATR needs previous close for every TR; flatRSI50 explicitly declared |
| Gaps? | Finite windows recover when all needed slots are complete; recursive history remains unavailable after gaps until explicit new epoch/anchor or verified replay |
| Volatility? | Nsimple session returns, centered sample variance ddof1, optional explicit positive integer sessions-per-year factor; default factor1 means unannualized |
| Reference availability/adjustments? | EQ-006 supplies compatible admitted point-in-time price basis; no adjustment engine/source trust is implemented here |
| Remaining encoding/state decisions? | EQ-011–016 schemas/config/errors and EQ-027–038 implementation/state/parity; no unresolved mathematical default is delegated to a backend |

## Tests and documentation

Independently derived period3fixture covers8IDs. Cases cover exact seed boundaries, period1where supported, missing/empty input, field-specific missingness, governed gaps, explicit anchor changes, target exclusion, unfinished target cutoff, unknown/unavailable reference admission, valid0ATR, gap-sensitive TR, flat/rising/falling RSI and long-flat ratio preservation, volatility centering/ddof/annualization, invalid representation/order and wide sums, scale parity and recursive partition carry.

Source references establish conventional smoothing definitions; fixtures do not assert numerical parity with a third-party library's defaults, flat-history handling or initialization modes. No speed benchmark/package build is needed for a specification. Owner-deferred automated reviewer setup remains deferred; self-review is labeled accurately.

## End state

Eight IDs have equations, units, initialization/window/warm-up/gap/denominator/availability rules and checked examples. All questions are resolved or bounded to explicit supplied references. Documentation and relevant checks pass on final head, public contents are verified, issue/Project/epic updated, and next EQ-005 becomes Ready for planning. R0 and production packages remain incomplete.
