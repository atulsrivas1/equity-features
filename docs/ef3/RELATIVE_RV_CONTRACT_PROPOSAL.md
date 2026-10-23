# EF3 relative statistics and realized-variance contract — proposal

Prepared for EQ-153 [#487](https://github.com/atulsrivas1/equity-features/issues/487) (correlation, beta and residual returns) and EQ-154 [#488](https://github.com/atulsrivas1/equity-features/issues/488) (daily centered log-return volatility and intraday regular-session realized variance), for consumption by EF3 I/O [#611](https://github.com/atulsrivas1/equity-features/issues/611) (EQ-223), worker [#612](https://github.com/atulsrivas1/equity-features/issues/612) (EQ-224) and release acceptance EQ-157 [#491](https://github.com/atulsrivas1/equity-features/issues/491). **This is a contract proposal, not accepted by any review.** It is contract preparation only: it admits no Ready state, implementation, numerical acceptance, release or performance claim. All former DECISION-PROPOSED conventions and OPEN questions are now coordinator decisions (final sections), decided and pending owner review, and the contract carries a coordinator freeze statement.

Companion data: [RELATIVE_RV_CONTRACT_PROPOSAL.json](RELATIVE_RV_CONTRACT_PROPOSAL.json) holds the machine-readable producers, headers, roles, mathematics, numeric policy, 24 relative-statistics fixtures, 17 daily log-volatility fixtures, 21 intraday realized-variance fixtures, 3 prefix-property fixtures and 48 typed-refusal fixtures. Expected values were derived with plain `fractions.Fraction` arithmetic and, only where `ln` or `sqrt` is irrational, the standard-library `decimal` module at 120 digits, in a scratch script that imports nothing from the equity packages. float64 results carry `float.hex` and a per-fixture acceptance rule. The library was not imported, run or tested. Fixtures use compact notation (not canonical wire) and still need expansion into canonical packets.

## Authority and inspected sources

Read-only inputs: `docs/features/INTRADAY_FOUNDATIONS.md` (R17 governed grid, reset epoch, exact preparation, evidence bound), `docs/features/HISTORICAL_FORMULAS.md` and `docs/api/HISTORY.md` (governed daily grid, strict windows, simple-return volatility), `docs/features/CONTEXT_FORMULAS.md` and `docs/api/RELATIVE_RETURNS.md` (supplied simple-return spreads, one benchmark, no hidden benchmark), `docs/releases/R17/*`, the shared validators and error codes in `packages/contracts` (`validation.py`, `errors.py`, `inputs.py`), the three merged EF2 contracts and `docs/ef2/PRODUCER_SET_AMENDMENT.md` (structure, quality bar, header registration), and the EQ-164 wave 4 audit notes (history carriers). The mathematics is standard public statistics: Pearson correlation, ordinary-least-squares beta with an explicit denominator convention, natural-log returns, realized variance as a sum of squared log returns, and an annualization factor that is a caller parameter. No private source, threshold, default window or default annualization constant is used or copied.

## Unchanged boundary

Existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult`, `Status`, `Reason`, `ErrorCode` and scalar `ValueType` values (`float64` is the only dtype used); the R17 grid, admission, reset epoch, exact preparation and batch/full-replay modes; the history context; the frozen ef1-contract1 and every accepted EF1, EF2, core and R17 header. The existing `history.return_volatility` (simple returns, centered, N-1) and `relative.market_return` / `relative.sector_return` keep their definitions and ids; the new log volatility is a distinct feature id and producer. No new DataKind, DTO, codec, scheduler, default, error code, unit string or shared-validator change. Update, restore and merge are unsupported (`UNSUPPORTED_CAPABILITY`). The packet is additive: three new producers and six new headers (producer-set and header-ledger entries to be recorded in a sibling amendment after a ruling, OQ1).

## Producers and config identities

| Item | Relative statistics | Daily log volatility | Intraday realized variance |
| --- | --- | --- | --- |
| Identity | `ef3.relative_stats` | `ef3.daily_log_volatility` | `ef3.intraday_realized_variance` |
| Algorithm / schema | `ef3-relative-stats-v1` / `1` | `ef3-daily-log-vol-v1` / `1` | `ef3-realized-variance-v1` / `1` |
| Policy label | `ef3-rel1` | `ef3-dlv1` | `ef3-rv1` |
| Parameters (closed, no defaults) | `benchmark_id`; `window` W (2..4096); `min_pairs` (2..W); `evidence_limit` (0..10000) | `period` N (2..4096); `annualization_factor` A (1..2^63-1); `evidence_limit` | `sampling` (single legal value `every_governed_slot`); `annualization_factor` A (present exactly when `intraday.realized_volatility` is selected); `evidence_limit`; R17 context (reset epoch only) |
| ConfigSpec | PriceUnit mandatory; both roles declare the same unit and adjustment | PriceUnit mandatory; adjustment declared once | PriceUnit mandatory; adjustment declared once |

A policy label names the whole convention set of its version. An unsupported label is `INCOMPATIBLE_VERSION`; a future convention needs a new label, never a silent change. Every parameter is explicit with no default: a missing or extra parameter is `INVALID_CONFIG`, and the convention and its version are part of the config identity and digest.

## Outputs and headers

| Feature id | dtype | unit | scale | min period | operand family |
| --- | --- | --- | --- | --- | --- |
| `history.log_return_volatility` | float64 | fraction | none | period + 1 closes | windowed log returns |
| `intraday.realized_variance` | float64 | fraction | none (dimensionless squared log return) | 2 bars | anchored log returns |
| `intraday.realized_volatility` | float64 | fraction | none | 2 bars | anchored log returns |
| `relative.beta` | float64 | fraction | none (dimensionless coefficient) | W + 1 closes per series | paired simple returns |
| `relative.correlation` | float64 | fraction | none, range -1..1 | W + 1 closes per series | paired simple returns |
| `relative.residual_return` | float64 | fraction | none | W + 1 closes per series | paired simple returns |

Order: lexicographic by feature id within a producer. Selection is per feature with independent readiness (fixture RS11: correlation and beta available while the residual is not). All six headers use unit `fraction` (dimensionless; beta and variance included): no new unit string is introduced (ruling O2).

## Inputs and roles

All inputs are exact positive scaled-integer closes; no acquisition, clock, calendar lookup, sorting, duplicate resolution, forward fill or I/O. Slot `i` is the `i`-th governed slot of the supplied grid; the target is slot `t`; `K` is the cutoff. A slot is READY iff its row exists, its close is non-null and positive, its coverage is complete and `known_at <= K`.

| Producer | Role | Kind | Contract |
| --- | --- | --- | --- |
| relative statistics | `instrument` | BAR on the daily governed grid, close only | one instrument id, one bar per governed session, grid order |
| relative statistics | `benchmark` | BAR on the daily governed grid, close only | instrument id equals config `benchmark_id`; same namespace, grid, price unit and adjustment declaration as `instrument` |
| daily log volatility | `daily` | BAR on the daily governed grid, close only | one instrument id, grid order |
| realized variance | `bars` | BAR (close and volume) | R17 chunked delivery; reset epoch of the target session |

The two relative roles are the only join: exactly the requested pair, no universe, sector or market construction, no third instrument (a typed refusal). Alignment is by identical governed session id and never by nearest time, interpolation or forward fill. Decided DP-S1: the library derives returns from the exact closes (the "return witness" is the pair of adjacent closes with their row ids as evidence). Rejected alternatives: float64 return series (already rounded), REFERENCE return rows, the existing `ReturnReference` scalar (one horizon, cannot form a series).

**Encoding of the daily grid (ruling O3).** Daily closes are BAR rows on a daily governed grid, following the R17 grid and slot-coverage conventions used by the EF2 contracts: the R17 context supplies the governed sessions as slots (one slot per governed trading session, `[start_ns, end_ns)` the session bounds, `session_id` the session identity), the grid and calendar identities, the target slot and the per-slot coverage (complete with expected 1, declared incomplete, or absent). Each role delivers one bar per governed session; a session without a row is an absent slot. There is no DAILY-kind input and no separate history context in these producers. For `relative_stats` both roles share the same context, so alignment by identical session id is by construction. Only `close` (and `known_at_ns`) is required; the BAR validator rules below apply unchanged.

Fixture construction rules, read from `validation.py` (shared validators unchanged and not executed): a close-only BAR batch (`required_fields=("close",)`) has no volume column, so a null-close slot is a row with `close` null and a zero or negative close is `INVALID_SCHEMA`; identity (instrument, session, start, end) is unique (`DUPLICATE`) and a bar overlapping the previous bar of the same (instrument, session) is `INVALID_ORDER`; note the shared BAR `order_group` is (instrument, session), so rows of different sessions delivered out of grid order are NOT caught by `validate_batch`. That check belongs to the producer admission (grid order against the context), which raises `INVALID_ORDER`. When a volume column is present, a BAR row with volume above 0 needs positive coherent OHLC; a null-price slot is volume null with OHLC null; a proven-empty slot is volume 0 with OHLC null on a slot whose coverage is complete with expected 0; volume 0 with a non-null price is `INVALID_SCHEMA`; negative volume is `BOUNDS`. Absent = no row and no coverage; gap = declared incomplete coverage. Positive prices only, reset epoch mode only.

## Exact mathematics — relative statistics (ef3-rel1)

1. **Return (DP-S2, DP-S3).** `r_j = C_j / C_{j-1} - 1`, an exact rational, defined iff slots `j-1` and `j` are both READY in that series. A return spanning a missing close is never formed. Rejected: log returns (would be policy `ef3-rel2`), spanning or forward-filled returns.
2. **Window and pairs (DP-S4, DP-S5).** Return slots `j = t-W+1..t`; the window must lie wholly inside the grid (`t - W >= 0`), else `insufficient_history` whatever `min_pairs` is (RS01). A pair `j` is valid iff both series have a defined `r_j`. `n` is the number of valid pairs; the outputs `correlation` and `beta` are available iff `n >= min_pairs` (`min_pairs = W` is strict mode; RS09 is the boundary `n = min_pairs`, RS10 the boundary minus one). Means are taken over the same `n` valid pairs for both series (joint, complete-case; RS11 shows an own-series mean would differ).
3. **Sums (DP-S6).** `x` instrument returns, `y` benchmark returns over the valid pairs: `Sxx = sum (y - ybar)^2` (benchmark), `Syy = sum (x - xbar)^2` (instrument), `Sxy = sum (x - xbar)(y - ybar)`, all exact rationals. This is centered (OLS with intercept). The covariance denominator is declared sample, `n-1`; because `beta = cov/var` and `rho = cov/sqrt(var var)` are ratios the denominator cancels exactly, so no published output depends on `n-1` versus `n` (RS02 lists both). The uncentered regression through the origin is a rejected alternative that gives a different beta (RS02: -10884930/6420689 versus the centered -5101530/2120591; RS18: 79/105 versus 11/14).
4. **Beta.** `beta = Sxy / Sxx`. **Correlation.** `rho = sign(Sxy) * sqrt(Sxy^2 / (Sxx * Syy))`, exactly in `[-1, 1]` (no clamp is needed or allowed to hide a defect), `+1` and `-1` reachable exactly (RS03, RS04, RS23), zero exactly `+0.0` (RS05). Reference-implementation statement: correlation of exactly plus or minus 1 is bit-required only through the exact-rational perfect-square path (`Sxy^2` and `Sxx*Syy` perfect squares, no irrational sqrt involved); every other correlation is irrational and uses the R17 tolerance.
5. **Zero variance (DP-S7).** Zero is an exact rational test with no epsilon: constant series have `Sxx` or `Syy` exactly 0, while a near-constant benchmark with variance about 1e-30 is available (RS17). Zero benchmark variance (`Sxx = 0`): correlation, beta and residual are `not_applicable/zero_denominator` (RS06, RS08). Zero instrument variance only (`Syy = 0`, `Sxx > 0`): correlation `zero_denominator`; beta is exactly 0 and the residual equals the instrument target return, here 0 (RS07).
6. **Residual (DP-S8).** `e_t = r_i,t - beta * r_b,t` with `beta` from the same window including the target, no intercept; it needs the target pair valid and `Sxx > 0`. Rejected: prior-only beta (window ending `t-1`), and the intercept-adjusted `r - alpha - beta r_b` (RS02 and RS18 list alpha and that value).
7. **Publication (DP-S10).** Exact rationals, one float64 rounding. Correlation is the correctly rounded value of the exact real `sign * sqrt(rational)`; it is an exact rational only when numerator and denominator are perfect squares (RS03, RS04, RS23).

## Exact mathematics — daily log volatility (ef3-dlv1)

For the target `t` and `N` log returns from `N+1` READY consecutive closes `t-N..t`: `l_i = ln(C_i / C_{i-1})`, `lbar = (1/N) sum l_i`, `s2 = sum (l_i - lbar)^2 / (N-1)`, `vol = sqrt(A * s2)` with `A` the caller integer annualization factor (DP-V1, DP-V2). `A = 1` is explicit and unannualized; the contract does not claim `A` is sessions per year. The window is strict: any non-READY slot among the `N+1` closes makes the value unavailable (no shrinking, no gap bridging; DP-V3), and fewer governed slots than `N+1` up to the target is `insufficient_history` (DV01). This is a new feature id; the existing `history.return_volatility` uses simple returns and stays untouched. DV15 uses the closes of the HISTORICAL_FORMULAS worked example (105, 120, 115, 130, N=3): the existing simple-return volatility is about 0.103136 (variance 476449/44791488, reproduced by the scratch script as a check) while the log volatility is 0.0986626851; population-denominator and uncentered-RMS values are listed as non-published alternatives. Constant price gives exactly `+0.0` (DV06); constant growth (DV07) is also exactly `+0.0`: three equal close ratios (11/10, decided by integer cross-multiplication) give three identical log values, and Decimal120 `ln` of identical inputs is identical, so the centered sum of squares is exactly 0. An implementation must therefore return `+0.0` whenever all N log returns are identical (equal exact ratios), not a rounding residue; there is no absolute floor anywhere in this contract. `A = 4` is exactly twice `A = 1` in float64 (DV02, DV03).

## Exact mathematics — intraday realized variance (ef3-rv1)

Over the reset epoch of the target session, bars `a..t` (`a` the first governed bar, `t` the target), all READY: `RV(t) = sum_{i=a+1..t} (ln(C_i / C_{i-1}))^2`; `realized_volatility = sqrt(A * RV)`; `realized_variance` is unannualized and takes no `A` (DP-R1, DP-R7).

- **Sampling (DP-R2).** Every governed slot of the supplied grid; the grid version is the sampling frequency. The single-valued `sampling` parameter makes any coarser step `UNSUPPORTED_SAMPLING`; no resampling in the library.
- **Overnight exclusion (DP-R3).** The epoch is the target session; no return crosses a session boundary and the first bar contributes only its close as the base (no open-to-close and no prior-close return). RV06 puts a 42.9% overnight jump before the first bar and the result equals RV03; the value if that return were included is listed as a non-published alternative.
- **Session calendars and early closes (DP-R4).** The governed grid defines the expected slots of each session. An early-close session simply has fewer slots and is complete at its last slot (RV07: 4 declared slots, expected 4). Nothing is rescaled to a full-day slot count; comparing sessions of different length is the consumer's responsibility. RV08 is not an early close: the grid declares 6 slots and two bars are absent.
- **Completeness (DP-R5).** Strict from anchor to target: no bridging return across a hole (RV09), no forward fill, no expected/observed scaling. A coverage-proven empty slot has no close and is `not_applicable/no_eligible_observations` (RV12), not zero flow (this differs from the EF2 money-flow rule because a return needs a price).
- **Minimum (DP-R6).** One return: `t = a` is `insufficient_history`, observed 1, expected 2 (RV01); `t = a+1` is available (RV02). RV-to-date at any later target is allowed (RV21).
- **Distinct from the daily family.** The daily family is centered, sample-denominator, over `N` returns of daily closes; RV is an uncentered sum over intraday returns. They are separate ids and producers.

## Precision and numeric policy

Windowed sums only; no recurrence exists in these families, so no Decimal120 recurrence fixture is required. Reference values: exact `Fraction` where the value is rational, `Decimal` (120 digits) for `ln` and `sqrt`. Each float64 expectation carries `float.hex` and exactly one acceptance rule:

| Rule | Meaning | Where |
| --- | --- | --- |
| `bits` | bit-identical; `+0.0` REQUIRED for zero, never `-0.0` | only where exactness is argued: representable exact rational or exact zero (RS03 correlation and beta, RS04, RS05 correlation and beta, RS07, RS23 correlation, DV06, DV07, RV04) |
| `r17_tol` | `abs(x - ref) <= max(8 ulp(ref), 1e-12 * abs(ref))`; the tolerance is listed per fixture | every other value |

Accuracy requirement on implementations (ruling O11): each `ln(C_i/C_{i-1})` is evaluated from the exact ratio with accuracy far below the tolerance even when the ratio is within 1e-15 of 1 (log1p-grade; DV14, RV16, with 1e15-scale coefficients that differ by one tick); variance is centered in a two-pass or exact manner, never `E[x^2] - E[x]^2` in float (RS17 and DV14 would fail it); zero tests are exact.

## Availability, coverage, quality, evidence and refusals

Typed refusal precedes assessment. Quality uses existing `Status`/`Reason` only, with the EF2 precedence (consistent with `CONTRACT.json`): `absent_input`, `unknown_availability`, `future_knowledge`, `null_field`, `ineligible` (missing_input), `governed_gap` (incomplete_coverage), `insufficient_history`, `no_eligible_observations` and `zero_denominator` (not_applicable). All applicable reasons are retained in lexical order; the status follows the first applicable reason; a value is null exactly when the status is not available. Slot causes: no row and no coverage `absent_input`; `known_at` null `unknown_availability`; `known_at > K` `future_knowledge` (`known_at = K` is known, RS22, DV17, RV18); null close `null_field`; declared incomplete coverage `governed_gap`; coverage-proven empty slot `no_eligible_observations` (intraday only). Knowledge is enforced identically in `known_at` and reconstruction modes. A benchmark known later than the instrument (cutoff misalignment) makes the pair `future_knowledge` (RS15).

Counts: relative statistics expected `W`, observed `n` valid pairs (identical for the three outputs); when `n >= min_pairs`, lost pairs leave no reason and the result is available with `observed < expected`; when `n < min_pairs` (or the window is not wholly in the grid) the reasons are the causes of the lost pairs only. `insufficient_history` is added only when the window is not wholly inside the grid (RS01: n = 2 valid pairs but W + 1 closes are not available); a window inside the grid with holes never carries it. Daily expected `N + 1`, observed READY closes in the window; with holes the reasons are the causes of the lost slots only, and `insufficient_history` appears only when `t - N < 0` (DV01). Intraday follows the same rule (insufficient only when `t = a`, RV01). Intraday expected `max(2, t - a + 1)`, observed READY bars among `a..t`. The residual additionally depends on the target pair: a lost target pair gives the residual the target slot's causes while correlation and beta stay available (RS11).

Prefix property: the output at target `t` is independent of every slot after `t` (later closes, absent, gap or future-known rows). PX01 to PX03 evaluate variants that differ only after the target and require the result of RS02, DV02 and RV21 respectively; window membership is covered by RS19 and DV16 (slots before the window cannot matter).

Evidence (available outputs only): the limit is the existing `evidence_limit` 0..10000; witnesses never exceed it; no new limit is invented. Relative statistics: the first and last used close of the instrument then of the benchmark (compact `instrument:slot:i`, `benchmark:slot:i`; ruling O8: the canonical evidence row id follows the EF2 convention `bar:<start_ns>:<end_ns>` of that slot's bar, with the role carried by the evidence role); daily: the bar of slot `t-N` then of `t`; intraday: anchor then target bar (all ids `bar:<start_ns>:<end_ns>`); boundary `completed_interval`; original `row_id`, `event_ns`, `known_at` kept. RS20, RS21 and RV19 cover truncation to 2, 0 and 1.

Refusals (no `FeatureResult`), RF01 to RF48 in the JSON, all from existing `ErrorCode` values (read from `errors.py`, `validation.py` and the R17 admission; nothing executed). Mechanisms: RF15/RF16 (instrument versus benchmark unit and adjustment) are batch-versus-batch checks by `require_compatible_inputs` (`INVALID_UNIT`, `UNSUPPORTED_ADJUSTMENT`, namespace `INCONSISTENT_IDENTITY`); RF29/RF30 and RF46/RF47 (config versus batch) are producer admission comparing the config price unit and adjustment with the batch metadata, exactly as R17 `packages/intraday/src/equity_features_intraday/_admission.py` does (`meta.price_unit != config.price_unit` raises `INVALID_UNIT`; `meta.adjustment != config.adjustment` raises `UNSUPPORTED_ADJUSTMENT`), with `_context.py` requiring an explicit price unit (`INVALID_UNIT`); RF17/RF27/RF44 grid-order checks are producer admission, not `validate_batch`; `DUPLICATE` is the same (instrument, session, start, end) interval. `INVALID_CONFIG` (bad or missing window, min_pairs, period, annualization, benchmark_id, evidence_limit, carry mode, annualization present without volatility selected, a second benchmark), `INCOMPATIBLE_VERSION` (unsupported label), `UNSUPPORTED_SAMPLING` (coarser sampling), `INCONSISTENT_IDENTITY` (benchmark id mismatch, self-pair, two instruments in a role, namespace mismatch), `INVALID_UNIT`, `UNSUPPORTED_ADJUSTMENT` (the roles must agree: no FX, no rescaling), `INVALID_ORDER`, `DUPLICATE`, `INVALID_SCHEMA` (zero or negative close; zero-volume bar with a price), `BOUNDS` (negative volume; bar beyond the cutoff), `UNKNOWN_FEATURE`, `UNSUPPORTED_CAPABILITY` (update, restore, merge). No `OVERFLOW` path exists: `A <= 2^63-1` and bounded log returns keep every result finite.

## Layer responsibilities

- **Library (#487, #488).** Admission, alignment, pair validity, returns, sums, beta, correlation, residual, log volatility and realized variance with the stated exactness and accuracy, quality, evidence and every refusal; pure and deterministic; per-pair preparation shared by the three relative outputs without coupling their readiness.
- **EF3 I/O #611.** Maps ordered closes with `known_at` into the BAR roles exactly as supplied, the daily governed grid and coverage into the R17 context, and the one benchmark identity into config; maps results (hex-exact float64, status, reasons, counts, witnesses) to the sink conversion; never derives a return, fills or interpolates a missing close, picks a benchmark, normalizes scale, currency or adjustment, or injects a default window, minimum, annualization or threshold.
- **Worker #612.** Routes selected outputs with exact warm-up closure, shares preparation within resource bounds, executes one config per complete result, binds inputs and the config digest and persists the library result unchanged. Direct, worker and stored results must be identical, including refusal class.

## Fixtures

24 relative-statistics (RS01 to RS24), 17 daily log-volatility (DV01 to DV17), 21 intraday realized-variance (RV01 to RV21), 3 prefix-property (PX01 to PX03) and 48 refusal fixtures (RF01 to RF48). The JSON `coverage_map` indexes them by tag. Coverage: insufficient history (RS01, DV01, RV01); exact small samples (RS02, RS03, RV02, RV03); perfect and zero correlation (RS03, RS04, RS05, RS23); zero benchmark variance and constant series (RS06 to RS08, DV06, DV07, RV04); missing, misaligned and cutoff-misaligned pairs (RS09 to RS11, RS15, RS16); minimum coverage boundaries (RS09, RS10, RS12); centered versus uncentered and sample versus population (RS02, RS18); daily versus intraday distinct and simple versus log (DV15, RV03, RV17); overnight exclusion (RV06); early close (RV07, RV08); annualization (DV02 to DV04, RV03, RV05); boundary equalities (RS02, RS09, RS22, RV02, RV18, DV17); null/unavailable reasons (`absent_input` RS10, `unknown_availability` RS14, `future_knowledge` RS15, `null_field` RS13 and RS11, `governed_gap` RS12, `insufficient_history` RS01, `no_eligible_observations` RV12, `zero_denominator` RS06; `ineligible` is deliberately unreachable here, nonpositive closes are refused); near-constant large coefficients (RS17, DV14, RV16); evidence (RS20, RS21, RV19); prefix property (PX01 to PX03, RS19, DV16, RV21); variance-only selection without annualization (RV20).

## Explicit non-goals

No acquisition of prices, benchmarks, calendars or schedules; no benchmark selection and no join beyond the one requested pair; no sector or market construction, multi-factor regression, rolling state, update, restore or merge; no carry epoch, overnight or open-to-close return features; no jump-robust, bipower, two-scale or subsampled realized measures; no default window, minimum coverage, annualization or threshold and no annual-risk claim for any annualization factor; no change to and no interplay with `history.return_volatility`, `relative.market_return`, `relative.sector_return` or `ReturnReference` (distinct producers; O12), nor any accepted R17, EF1 or EF2 output; no new DataKind, DTO, codec, scheduler, error code, unit string or shared-validator change; no performance, parity, release or publication claim; no private-source equivalence.

## Coordinator decisions (decided, pending owner review)

All former DECISION-PROPOSED conventions are accepted as proposed:

| Id | Decision | Alternatives rejected |
| --- | --- | --- |
| DP-S1 | two daily-grid BAR close roles; library derives returns | float64 returns, REFERENCE rows, `ReturnReference` |
| DP-S2 | simple session returns for EQ-153 | log (`ef3-rel2`), excess over risk-free |
| DP-S3 | return only from adjacent governed closes | spanning or forward-filled returns |
| DP-S4 | last W return slots ending at target inclusive, complete-case joint pairs | strict only, own-series means, prior-only |
| DP-S5 | caller `min_pairs` 2..W, window wholly inside grid | policy-fixed minimum, fraction threshold |
| DP-S6 | centered, sample `n-1` declared, cancels in all outputs | population `n`, uncentered through origin |
| DP-S7 | exact zero test; benchmark zero variance zero_denominator for all three; instrument zero variance gives beta 0 | epsilon, beta 0 or rho 0 conventions, nonfinite |
| DP-S8 | residual `r_i,t - beta r_b,t`, same-window beta, no intercept | prior-only beta, intercept-adjusted |
| DP-S9 | exactly one benchmark, same unit and adjustment, no FX; a differing price unit, currency or scale is refused `INVALID_UNIT` (ruling O4) | scale-free units |
| DP-S10 | exact rationals, one rounding, correlation within R17 tolerance | float accumulation |
| DP-V1 | new id `history.log_return_volatility`, ln returns, centered, N-1 | population, uncentered RMS, flag on existing id |
| DP-V2 | caller integer A, `sqrt(A s2)`, no default | variance annualization, calendar-derived A |
| DP-V3 | strict `N+1` closes | min coverage, bridging |
| DP-R1 | uncentered sum of squared log returns | centered, bipower, two-scale |
| DP-R2 | every governed slot; single-valued `sampling` | step k, library resampling |
| DP-R3 | reset epoch, first bar only base close | open-to-close, carry, separate overnight feature |
| DP-R4 | grid defines slots, no rescaling for early closes | scale by slot ratio, flag |
| DP-R5 | strict completeness; empty slot is no_eligible_observations | bridging, forward fill, scaling, tolerated missing fraction |
| DP-R6 | minimum one return | `min_returns` parameter |
| DP-R7 | variance unannualized, volatility `sqrt(A RV)` | annualize variance |
| DP-R8 | positive prices only; unit `fraction`, no new unit string (O2) | new units |

Rulings on the former open questions:

- **O1** `relative.*` and `history.log_return_volatility` live in `packages/features` as an EF3 module (config namespace `ef3.*`); `intraday.realized_variance` and `intraday.realized_volatility` live in `packages/intraday`. Separate catalogs; `describe_intraday()` and its digest are unchanged; no package version bump.
- **O2** Unit `fraction` for all six headers (dimensionless); no new unit string.
- **O3** Daily closes are BAR rows on a daily governed grid with R17 grid and slot-coverage conventions (encoding stated under Inputs and roles).
- **O4** A benchmark with a different price unit, currency or scale than the instrument is refused `INVALID_UNIT` (the code `require_compatible_inputs` raises for a unit mismatch); a namespace mismatch stays `INCONSISTENT_IDENTITY`. No conversion.
- **O5** Residual variants (prior-only beta, intercept-adjusted) are out of v1.
- **O6** No log-basis `ef3-rel2` label in v1.
- **O7** No session-complete flag; the strict completeness rule is internal.
- **O8** Evidence row ids follow the EF2 convention `bar:<start_ns>:<end_ns>`.
- **O9** The window and period bound is the R17 period bound 4096 for all producers (`packages/intraday/src/equity_features_intraday/_context.py`, `integer(..., 1, 4096)`).
- **O10** The lower bound of `min_pairs` is 2 (RS23 shows the two-point case).
- **O11** `ln` and `sqrt` are Decimal120 correctly rounded references; acceptance is the R17 tolerance `max(8 ulp, 1e-12 * |ref|)`. The earlier allowance of an absolute 1e-12 floor is withdrawn (R17 `docs/api/INTRADAY.md`: no universal absolute floor; exact mathematical zeros return normalized `+0.0`); DV07 is a `bits` fixture.
- **O12** No interplay with `ReturnReference` or the existing relative returns: distinct producers (non-goal).

## Amendment note

Producer-set and header-ledger entries (three producers; the six headers `history.log_return_volatility`, `intraday.realized_variance`, `intraday.realized_volatility`, `relative.beta`, `relative.correlation`, `relative.residual_return`; no new unit) are recorded as to-be-applied; the shared header/unit amendment will be a sibling document after the freeze. No change to shared validators is proposed.

## Coordinator freeze

Frozen as `ef3-rel1`, `ef3-dlv1` and `ef3-rv1` (v1) for implementation once this PR merges (coordinator statement; no review or acceptance claim by the author). Reset epoch mode only; no defaults for windows, `A` or `min_pairs`. Any change to a convention, label semantics, header, role or fixture after merge requires a new policy label and an amendment document. Numerical, artifact and release gates remain.
