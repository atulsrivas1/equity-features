# EF2 trend, momentum and channel oscillators contract: proposal (coordinator rulings applied)

Prepared for EQ-147 [#481](https://github.com/atulsrivas1/equity-features/issues/481) (MACD line, signal, histogram), EQ-148 [#482](https://github.com/atulsrivas1/equity-features/issues/482) (directional movement, DMI, ADX) and EQ-149 [#483](https://github.com/atulsrivas1/equity-features/issues/483) (stochastic oscillators, Williams percent R). EF2 I/O [#609](https://github.com/atulsrivas1/equity-features/issues/609) and the worker [#610](https://github.com/atulsrivas1/equity-features/issues/610) consume it; release acceptance is EQ-152 [#486](https://github.com/atulsrivas1/equity-features/issues/486).

This is contract preparation only. The coordinator has ruled on every convention (DP1 to DP19 accepted) and every former open question (Q1 to Q13, rulings below), pending owner review; the contract carries a coordinator freeze statement. It is documentation and hand-derived reference values only and admits no Ready state, implementation, numerical acceptance, release or performance claim. All three indicator families are standard, publicly documented technical-analysis definitions, specified here from those public definitions with explicit conventions.

Companion data: [MOMENTUM_TREND_CONTRACT_PROPOSAL.json](MOMENTUM_TREND_CONTRACT_PROPOSAL.json) holds the machine-readable headers, roles, config, conventions, mathematics, quality rules, 97 result fixtures (94 single-target plus 3 prefix-property) and 24 typed-refusal fixtures. Expected values were derived with plain `fractions` arithmetic in a scratch script that imports nothing from the equity packages; the library was not imported, run or tested.

## Authority and unchanged boundary

Inspected (read, not run): `INTRADAY_FOUNDATIONS.md`, `docs/api/INTRADAY.md`, `docs/releases/R17/*`, `R17_ACCEPTANCE.md`, the `equity_features_intraday` modules `_indicators`, `_bands`, `_prepare`, `_context`, `_registry`, `_admission`, `_dispatch`, and the merged EF1 proposals `CLOSE_RECONCILIATION_CONTRACT_PROPOSAL` and `MULTI_VENUE_STATUS_CONTRACT_PROPOSAL` with `docs/ef1/CONTRACT.json` (quality bar and shared conventions only).

Unchanged by this proposal:

- The accepted R17 mathematics, outputs, catalog, quality table, numeric contract and package. Nothing here edits an R17 document or ID.
- The frozen `docs/ef1/CONTRACT.json`. EF2 does not amend it. The R17-style envelope below (not the EF1 `ef1_context_json` envelope) is used because EF2 needs the R17 governed intraday grid with anchor, target and reset or carry epoch.
- Existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult`, `ValueType`, `QualityRow`, `EvidenceRow`, `ErrorCode`, `Reason` and `Status`. No new DataKind, DTO, codec, scheduler or default.

## Producers and config identities

Three homogeneous producers inside the optional intraday component: `macd` (EQ-147), `dmi` (EQ-148), `stochastic` (EQ-149). One config computes one family; the caller selects any subset of that family's output IDs (R17 selection style; each selected output has its own readiness; accepted DP16). Compute is batch snapshot plus caller-supplied full-history replay. Update, restore, merge and carry epochs are out of scope in v1 (DP19, ruling Q7): update, restore and merge fail with UNSUPPORTED_CAPABILITY, and a context whose mode is not `reset` is INVALID_CONFIG. Anchored batch (reset epoch) only.

Envelope (accepted, ruling Q10): `ConfigSpec` identity `intraday.momentum.v1`, algorithm `intraday-momentum-v1`, schema 1. It reuses the R17 context unchanged (`IntradayContext`, the chunked `context_*` parameters, `context_sha256`, `evidence_limit`, the reduced canonical final-envelope check). It drops the R17 `period`, `k_num`, `k_den` and adds a closed, per-family parameter set. No parameter has a default.

| Family | Closed parameters | Bounds |
| --- | --- | --- |
| macd | `fast_period`, `slow_period`, `signal_period` | integers, 1 <= fast < slow; slow + signal - 1 <= 4096 |
| dmi | `di_period`, `adx_period` | integers >= 1; di + adx <= 4096 |
| stochastic | `k_period`, `k_slowing`, `d_period` | integers >= 1; k + slowing + d - 2 <= 4096 |

All envelopes also carry `momentum_family`, `evidence_limit` (0..10000), the context parameters and the convention parameters below. Booleans are not integers. Parameters are validated before any data: INVALID_CONFIG for shape and bounds, INCOMPATIBLE_VERSION for an unsupported convention value or version label.

### Versioned conventions (all choices live in config)

Each convention is a closed parameter accepting exactly one value in v1; the group is labeled `ef2-conv1`. A different choice needs a new value and a new label, never a silent change. Alternatives are named in the decision register.

| Parameter | v1 value | Meaning |
| --- | --- | --- |
| `ema_seed` | `sma_first_n` | EMA seeded by the simple mean of the first p epoch closes (DP1) |
| `ema_alpha` | `two_over_n_plus_one` | alpha = 2/(p+1) (DP4) |
| `signal_seed` | `sma_first_n_macd` | signal seeded by the mean of the first g MACD values (DP2) |
| `macd_start` | `slow_seed_bar` | MACD defined once the slow chain is seeded (DP3) |
| `smoothing` | `wilder_average_seeded_by_mean` | Wilder average form for TR, +DM, -DM (DP5) |
| `dm_rule` | `strict_greater_zero_on_tie` | directional movement rule (DP6) |
| `di_scale` | `points_0_100` | DI, DX, ADX scale (DP7) |
| `undefined_di_dx` | `not_applicable_zero_denominator` | zero smoothed TR or zero DI sum (DP8) |
| `adx_chain_start` | `first_defined_dx` | ADX seeding position (DP9) |
| `raw_k` | `close_location_in_window_including_current` | raw %K (DP11) |
| `stoch_smoothing` | `sma` | slowing and %D smoothing (DP11) |
| `zero_range` | `undefined_not_applicable` | HH = LL handling (DP13) |
| `oscillator_scale` | `points_0_100_williams_minus100_0` | (DP12) |
| `numeric_policy` | `r17_decimal120_v1` | R17 Decimal120 recurrences and tolerance (ruling Q2) |

## Inputs and roles

One role `bars` of kind BAR: the unchanged R17 supplied chunks (`None` means absent delivery; an empty tuple means an observed-empty delivery). Same admission as R17: positive scaled int64 prices in one currency, scale and action basis, exact UTC half-open slots, real session identities, explicit calendar/grid/source/revision identities, no sorting, duplicate resolution, resampling, adjustment or forward fill. An observation counts only when slot coverage, field presence and knowledge (end <= C, known by K in the declared availability mode) qualify.

Epoch (inherited from R17, DP17, reset only per ruling Q7): the epoch starts at the first governed bar of the target session and drops overnight changes. The R17 carry epoch is not supported in v1. Periods count governed bars, not minutes. Every chain and window below lies inside `[anchor, target]`; a rolling window never reaches before the anchor, and older bars and old gaps never count.

### Which R17 outputs and operands are inputs

| R17 item | Used by | How |
| --- | --- | --- |
| `anchored_closes` operand (exact closes anchor..target, from EQ137/EQ138 preparation) | MACD fast chain and slow chain | Reused unchanged. Fast and slow chains are independent of each other (neither reads the other's state or seed). |
| MACD observations M[k] | `macd_signal`, `macd_histogram` | Derived inside the EF2 kernel from the two chains; the signal depends on the ordered MACD observations M[slow-1..t], not on any whole-indicator output. |
| `true_ranges` operand (TR anchor+1..target) | DMI | Reused unchanged. Smoothed TR is exactly the value behind R17 `intraday.atr` for the same period. |
| `high_extrema`, `low_extrema` operands (one window ending at the target) | stochastic, Williams | The window rule is reused unchanged. Smoothing needs the same window at earlier targets, so EF2 adds the internal family `rolling_extrema_runs`; its last element equals the R17 operand for the same n. |
| published Float64 `intraday.ema`, `intraday.atr` | none | Not consumed: they are rounded witnesses. Only their exact mathematics is shared (a cross-check, below). |

Additive internal preparation families (same immutable, bounded, source-bound rules as R17 preparation; accepted rulings Q1, Q11, implemented inside `packages/intraday`): `directional_moves` (+DM, -DM for k = 1..T-1; needs high and low on slots anchor..target) and `rolling_extrema_runs` (HH, LL and C for a run of consecutive window ends of one length). No whole-indicator barrier exists: an output waits only for the exact slots in its dependency table.

Cross-check requirement for the implementing story: for the same context, anchor, mode and closes, the exact fast and slow chain values at the target equal the unrounded values of R17 `intraday.ema` with periods fast and slow, and the exact smoothed TR equals the unrounded R17 `intraday.atr`; and Williams %R equals raw %K minus 100.

## Headers

Float64, one scalar per selected ID for `EntityKey(instrument_id, target session)`, column `algorithm_version` `intraday-momentum-v1`, schema 1, sorted by ID. Units are new strings except currency/share; they are accepted as additive units (ruling Q5) and will be listed in the later shared-contract header ledger and unit amendment, a sibling document after freeze.

| ID | Unit | Minimum epoch slots |
| --- | --- | --- |
| `intraday.macd_histogram` | currency/share | slow + signal - 1 |
| `intraday.macd_line` | currency/share | slow |
| `intraday.macd_signal` | currency/share | slow + signal - 1 |
| `intraday.adx` | DMI points | di + adx (more if DX starts late, DP9) |
| `intraday.dx` | DMI points | di + 1 |
| `intraday.minus_di` | DMI points | di + 1 |
| `intraday.plus_di` | DMI points | di + 1 |
| `intraday.stoch_d` | stochastic points | k + slowing + d - 2 |
| `intraday.stoch_k` | stochastic points | k + slowing - 1 |
| `intraday.williams_r` | Williams %R points | k |

`intraday.stoch_k` is the slowed %K (slowing 1 gives fast %K). `ResultMetadata` follows R17: namespace, session, availability, config digest, actual input bindings, backend `intraday.python`, the delivered package version (a new `equity_features_intraday` prerelease and catalog digest, ruling Q1).

## Exact mathematics

Notation: epoch slots k = 0..T-1, k = 0 the anchor, k = T-1 the target. C, H, L are exact rationals (coefficient / 10^scale). All values below are exact rationals; nothing is rounded until publication.

### MACD (EQ-147)

- EMA of period p: E_p[p-1] = mean(C[0..p-1]); E_p[k] = (2 C[k] + (p-1) E_p[k-1]) / (p+1) for k >= p. Defined for k >= p-1. p = 1 gives E_1 = C.
- Line: M[k] = E_fast[k] - E_slow[k] for k >= slow-1.
- Signal (g = signal_period): G[slow+g-2] = mean(M[slow-1 .. slow+g-2]); G[k] = (2 M[k] + (g-1) G[k-1]) / (g+1) for k >= slow+g-1.
- Histogram: M[k] - G[k].
- Units: published = exact result / 10^scale.

Warm-up and readiness: line needs slow epoch slots; signal and histogram need slow + g - 1. Fewer governed epoch slots is `insufficient_history` for that output only (the line can be available while the signal is warming). Every output is always numerically defined once ready (no divisor): there is no `not_applicable`. Constant closes give exactly +0.0 for all three. g = 1 gives signal = line and histogram exactly +0.0. Every output reads closes on all epoch slots (the recursion is anchored), so a gap or null close anywhere in anchor..target blocks all MACD outputs until explicit replay with a new epoch, exactly like R17 EMA. Highs and lows are never required (fixture M18).

Worked check (fixtures M02, M03, closes 10, 12, 14, 15, periods 2, 3, 2): E_2: seed (10+12)/2 = 11, then k=2: (28+11)/3 = 13, k=3: (30+13)/3 = 43/3. E_3: seed 12 at k=2, k=3: (30+24)/4 = 27/2. M[2] = 13 - 12 = 1; M[3] = 43/3 - 27/2 = 5/6. Signal seed = (1 + 5/6)/2 = 11/12. Histogram = 5/6 - 11/12 = -1/12.

### DMI and ADX (EQ-148)

- TR[k] = max(H-L, |H - C[k-1]|, |L - C[k-1]|), k >= 1 (the R17 `true_ranges` operand; the target's close is not needed, the anchor's high and low are).
- up[k] = H[k] - H[k-1]; dn[k] = L[k-1] - L[k]. +DM = up if up > dn and up > 0 else 0. -DM = dn if dn > up and dn > 0 else 0. Inside bar: both moves <= 0, both DM 0. Outside bar: the larger move wins. Tie (up = dn) and zero moves give 0 for both (DP6).
- Smoothing (n = di_period) for x in {TR, +DM, -DM}: S[n] = mean(x[1..n]); S[k] = ((n-1) S[k-1] + x[k]) / n, defined for k >= n. This is the R17 ATR recurrence; the sum form (S = n times the average) gives identical DI and DX.
- +DI = 100 S_+DM / S_TR; -DI = 100 S_-DM / S_TR.
- DX = 100 |+DI - -DI| / (+DI + -DI) = 100 |S_+DM - S_-DM| / (S_+DM + S_-DM).
- ADX (m = adx_period): f = first k >= n with DX defined. ADX[f+m-1] = mean(DX[f..f+m-1]); ADX[k] = ((m-1) ADX[k-1] + DX[k]) / m.

Undefined states (DP8): DI undefined iff S_TR = 0 (every TR so far is 0). DX undefined iff DI undefined or S_+DM + S_-DM = 0. Weights are exactly positive, so once S_TR > 0 or the DM sum > 0 it stays so; undefined states are a prefix of the epoch only. Undefined outputs publish `not_applicable` / `zero_denominator` with value null and full expected and observed counts (R17 band-position precedent). ADX is `not_applicable` while DX is undefined at the target, `insufficient_history` while fewer than m DX values exist from f (expected = f + m slots, observed = ready epoch slots), and available afterwards (fixtures D06_*). Alternatives for the ADX start are in DP9 / ruling Q3.

Warm-up: plus_di, minus_di, dx need di + 1 slots; adx needs di + adx slots at minimum. N = 1 is allowed (DI is the raw DM / TR; adx_period 1 gives ADX = DX; fixture D09).

Dependency: close, high, low on epoch slots anchor..target-1; high and low on the target (target > anchor). When target = anchor only the anchor (close, high, low) is tracked and the outputs are `insufficient_history`. Unlike R17 ATR, DMI needs the anchor's high and low (fixture D11); a null target close does not block (fixture D12); a null close on the previous bar does (D13).

Worked check (D03_3/D03_4, bars (20,16,18), (22,17,21), (21,16,17), (24,18,23), periods 2, 2): TR = 5, 5, 7; +DM = 2, 0, 3; -DM = 0, 1, 0. At k = 2: S_TR = 5, S_+DM = 1, S_-DM = 1/2 so +DI = 20, -DI = 10, DX = 100/3. At k = 3: S_TR = 6, S_+DM = 2, S_-DM = 1/4 so +DI = 100/3, -DI = 25/6, DX = 700/9; ADX = mean(100/3, 700/9) = 500/9.

### Stochastic oscillators and Williams %R (EQ-149)

- Window (n = k_period): HH[j] = max(H[j-n+1..j]), LL[j] = min(L[j-n+1..j]), j >= n-1, always inside the epoch. Ties among equal highs or lows do not change the extremum.
- Raw: R[j] = 100 (C[j] - LL[j]) / (HH[j] - LL[j]); undefined iff HH[j] = LL[j] (zero range).
- %K (s = k_slowing): K[j] = mean(R[j-s+1..j]), j >= n+s-2.
- %D (d = d_period): D[j] = mean(K[j-d+1..j]), j >= n+s+d-3.
- Williams %R: W[j] = -100 (HH[j] - C[j]) / (HH[j] - LL[j]) = R[j] - 100.

Zero range (DP13): R and W are undefined where the window range is zero. A smoothed value that consumes any undefined contributor is itself undefined (`not_applicable` / `zero_denominator`, full counts). The undefined condition therefore persists through a K window (s raw values) and a D window (s + d - 1 raw values) (fixtures T09 to T11). Exact zeros publish +0.0 (Williams %R with close at the high is -0 in raw arithmetic; the published value is +0.0, fixtures T04, T06). Close at the low gives raw 0 and Williams -100 (T07).

Dependency (rolling, per-output windows): williams_r reads high and low on the last n epoch slots and the close on the last slot only; stoch_k reads high and low on the last n + s - 1 slots and the close on the last s; stoch_d reads high and low on the last n + s + d - 2 slots and the close on the last s + d - 1. A gap or null before an output's own window does not block it (fixtures T16, T18, T19: a gap or null close that lies only in D's window leaves K and Williams available).

Worked check (T03/T04, bars (10,8,9), (12,9,11), (13,10,12), (14,11,11), (14,12,14), periods 3, 2, 2): R[2] = 100 (12-8)/(13-8) = 80; R[3] = 100 (11-9)/(14-9) = 40; R[4] = 100 (14-10)/(14-10) = 100. K[3] = 60, K[4] = 70, D[4] = 65; W[4] = 0.

## Publication and numeric policy (ruling Q2)

The implementation follows the established R17 numeric policy: exact `Fraction` seeds, ordered recurrences in a fresh local Decimal context (precision 120, ROUND_HALF_EVEN, Emin -999999, Emax 999999, the R17 traps; kernel `packages/intraday/src/equity_features_intraday/_indicators.py`), one guarded final Float64 conversion, normalized exact zero, whole-call OVERFLOW on arithmetic failure. Exact-rational recurrences are not implementable on long series (an EMA chain's denominators grow without bound), so they are not the implementation policy.

The exact fractions and `float.hex` values in the fixtures are the REFERENCE values, derived independently. Acceptance rule per fixture output (field `acceptance` in the JSON):

- `tolerance` (reference nonzero): `abs(y - r) <= max(8 * ulp(r), 1e-12 * abs(r))` with r the fixture float64. This is the R17 numeric error contract in `docs/api/INTRADAY.md` ("Numeric error contract and capabilities").
- `exact_plus_zero` (reference exactly 0, guaranteeable): the published value must be bit-exact +0.0. Guarantees: MACD with identical epoch closes uses identical-input detection (every EMA equals that close exactly, so all three outputs are set to +0.0); MACD histogram with `signal_period` 1 defines signal = line (alpha 1, exact), so line - line = +0.0; DMI and stochastic zeros arise from an exactly zero integer or decimal numerator or sum before any division rounding, and a zero is published as +0.0 (never -0.0, including Williams %R with the close at the high).
- `zero_bound` (reference exactly 0, not guaranteeable): a mathematically zero MACD line or histogram on non-identical input (fixtures M05, M06, M25 histogram and M26 line) cannot be guaranteed bit-exact with Decimal120 recurrences, and no detection rule is defined for it. These four fixture outputs are relaxed to `abs(y) <= 1e-12 * max epoch close price` in currency/share.

State and cost: O(1) recurrence state per bar and no whole-series barrier; measurement belongs to the release baseline (ruling Q13).

## Availability, quality, evidence and refusals

Quality is the accepted R17 table, unchanged (status precedence `missing_input`, `insufficient_history`, `incomplete_coverage`, `not_applicable`, `available`; all applicable reasons in enum order; an entirely absent delivery gives only `absent_input` with observed 0). The only addition is `not_applicable` / `zero_denominator` for a complete operand with a mathematically zero divisor (DI, DX, ADX, Williams, %K, %D). Reasons in use: `absent_input`, `future_knowledge`, `governed_gap`, `insufficient_history`, `no_eligible_observations`, `null_field`, `observed_empty`, `unknown_availability`, `zero_denominator`.

Counts: for anchored outputs (MACD, DMI) expected = max(seed, epoch slots); for rolling outputs expected = the window span (seed). Observed = dependency slots whose required fields, coverage and knowledge qualify. Counts never depend on which other outputs were requested, and never on evidence truncation.

Independence: each selected output waits only for its own fields and slots. Examples fixtured: MACD without high/low columns (M18); line available while signal warms (M02, M23); Williams available while D is blocked by a gap or null (T16, T19); K available when only D's wider span is defective (T16, T18).

Evidence follows R17: actually supplied consumed or knowledge-excluded dependency rows only, `row_id` `slot:<global index>`, event time the slot end, effective bounds the slot, boundary `completed_interval`, sorted by feature id then slot, truncated to the result-wide `evidence_limit` (0 returns none; fixtures M22, D19, T29).

Typed refusals (no result), checked before cell readiness, in R17 order: configuration shape and versions, limits/unit/identity, batch structure, cross-chunk grid, then cells. Refusal fixtures E01 to E24: INVALID_CONFIG (fast >= slow, nonpositive or boolean periods, window over 4096, missing or extra parameters, feature not owned by the family, evidence limit), INCOMPATIBLE_VERSION (unsupported convention value), UNKNOWN_FEATURE, UNSUPPORTED_CAPABILITY, INVALID_SCHEMA (contradictory OHLC, enforced by shared validation, see ruling Q6), a non-`reset` context mode as INVALID_CONFIG, INVALID_UNIT, UNSUPPORTED_ADJUSTMENT, INCONSISTENT_IDENTITY, DUPLICATE and OVERFLOW.

## Layer responsibilities

- Library (EQ-147/148/149, core): pure functions over supplied facts. Admission via the R17 path, the three producers, the additive preparation families, exact mathematics, quality, evidence, refusals, catalog entries with all state flags false. No acquisition, credentials, clock, file or database access, scheduling or publication.
- EF2 I/O (#609): maps actually supplied BAR facts and their provenance into the unchanged `bars` batches exactly as given; maps Float64 results with their units (including the three new unit strings), status, reasons, counts and evidence to storage; never derives, fills, smooths or repairs a value; never invents a missing high, low or close; preserves exact bits (`float.hex`).
- Worker (#610): executes one homogeneous family config per task, binds all actual inputs and the config digest, runs the library operation and persists the result unchanged; no hidden aggregation, no cross-family barrier, no default periods. Direct, worker and stored results must be identical, including refusal class.
- Acceptance (EQ-152): reruns these fixtures independently, adds the freeze of performance workloads and the adoption rule before any timing, and compares direct, fused and worker paths for full-result parity. This contract gives no timing.

## Fixtures

97 result fixtures (32 MACD, 35 DMI, 30 stochastic, including the 3 prefix-property fixtures P01 to P03) and 24 refusal fixtures in the JSON. Output statuses covered in the 94 single-target fixtures: available 192, insufficient_history 25, incomplete_coverage 48, missing_input 20, not_applicable 27. Coverage map groups: short history, exact seeds, boundary equalities (epoch slots equal to each output's minimum), constant, monotone, crossings (histogram sign change fixtures M07_5 to M07_10, exact zero M08, M25, M26), gaps and missing bars, null fields, future and unknown knowledge, observed-empty slots, absent column, absent delivery, zero range and flat series (D02_flat2, D05, D06_*, T08 to T11, T14), DM classification (inside, outside up and down, ties, zero move, gap, shift: D02_*), eviction and extremes (T05 to T07, T15), independence (M18, M23, T16, T18, T19, T30), reset epoch with ignored prior-session bars (M20, D18, T25), scale (M09, T28), 2^60 precision (M10), degenerate parameters (M08, D09, T12 to T14), evidence truncation (M22, D19, T29) and selected-subset requests.

Each fixture lists compact inputs (not canonical wire), the exact expected value, its `float64` and `float.hex`, status, reasons, expected and observed counts and the evidence rows. Intermediate exact chains (EMAs, TR, DM, smoothed TR, raw %K) are included for hand checking. The prefix property is REQUIRED (ruling Q12): the output at bar n must not depend on later bars. Fixtures P01 (MACD), P02 (DMI) and P03 (stochastic) give two series sharing a prefix but differing afterwards, with the expected outputs at each listed prefix length; a snapshot at target n must equal the full-history replay value at n. Each result output also carries its acceptance rule (see the numeric policy).

## Decision register (all ACCEPTED by the coordinator)

| ID | Choice (alternatives named) |
| --- | --- |
| DP1 | EMA seed: SMA of first p closes (R17). Alt: first close as seed; longer-history seeding. |
| DP2 | Signal seed: SMA of first g MACD values. Alt: first MACD value; signal from the fast seed bar. |
| DP3 | MACD defined from the slow seed bar only. |
| DP4 | EMA alpha = 2/(p+1), not Wilder 1/p. |
| DP5 | DMI smoothing: Wilder average form seeded by the mean (= R17 ATR). Alt: EMA alpha; SMA windows. Sum form equals this for DI and DX. |
| DP6 | DM: strict greater and positive; ties and zero moves give 0. |
| DP7 | DI, DX, ADX in points 0..100. Alt: fractions. |
| DP8 | Undefined DI (S_TR = 0) and DX (DM sum 0): not_applicable / zero_denominator. Alt: 0; carry-forward. |
| DP9 | ADX seeds at the first defined DX (data-dependent warm-up). Alt: fixed index a + di + adx - 1 with poisoning; undefined DX as 0. |
| DP10 | Separate di_period and adx_period. |
| DP11 | Stochastic: raw %K in the n-window including the current bar; %K = SMA over slowing; %D = SMA over d. Alt: EMA or Wilder smoothing; %D on raw. |
| DP12 | Stochastic 0..100; Williams -100..0. Alt: fractions. |
| DP13 | Zero range undefined and propagating through smoothing. Alt: neutral 50 (RSI precedent); 0; carry. |
| DP14 | Williams %R uses k_period. |
| DP15 | Superseded by ruling Q2: R17 Decimal120 recurrences with the R17 tolerance; exact rationals are fixture reference values only. |
| DP16 | One homogeneous config per family with selectable subset. |
| DP17 | Everything inside the epoch; no look-before-anchor. |
| DP18 | Output IDs and units as in the header table. |
| DP19 | Anchored batch only (reset epoch); update, restore, merge and carry out of scope (ruling Q7). |

## Explicit non-goals

No code, tests, CI, benchmark or performance claim; no change to R17 or the frozen EF1 contract; no acquisition, calendar inference, resampling, price adjustment or forward fill; no default periods; no update, restore, merge or carry epoch; no raw or fast %K, +DM/-DM, TR, ADXR, percentage MACD or crossover flags; no source, rights or provider claim; no persistent live behavior.

## Coordinator rulings (decided, pending owner review)

All DP1 to DP19 are accepted as written, except DP15 and DP19 as restated above.

- **Q1 packaging**: extend `packages/intraday` (`equity_features_intraday`) with additive modules, a new prerelease and catalog digest. The money-flow contract B uses the same package.
- **Q2 numeric policy**: R17 Decimal120 policy and tolerance; fixture exact values are reference values; per-fixture acceptance rules as in the numeric policy section, including the relaxed `zero_bound` cases.
- **Q3 ADX start**: first defined DX, data-dependent warm-up (DP9).
- **Q4 zero range**: undefined and propagating (DP13).
- **Q5 units**: `DMI points`, `stochastic points`, `Williams %R points` accepted as additive units, to be listed in the later amendment document.
- **Q6 OHLC validity (verified)**: `validate_batch` in `packages/contracts/src/equity_feature_contracts/validation.py` already refuses `low > high` and any of open, high, low, close outside `[low, high]` with INVALID_SCHEMA (positive-volume rows; zero-volume rows must have null OHLC). The EF2 producers add no check, no new error code and no change to the shared validators.
- **Q7 state**: update, restore, merge and carry are not in v1; anchored batch, reset epoch only.
- **Q8 extra outputs**: none beyond the 10.
- **Q9 defaults**: none. All periods are caller parameters; standard values (12/26/9, 14, 14/3/3) appear only inside fixtures.
- **Q10 identity**: `intraday.momentum.v1` accepted.
- **Q11 operand families**: `directional_moves` and `rolling_extrema_runs` accepted as additive internal families.
- **Q12 prefix property**: required, fixtures P01 to P03.
- **Q13 performance**: not a contract item in v1 beyond O(1) state per bar and no whole-series barrier; measurement belongs to the release baseline.

The shared-contract header ledger and unit amendment will be a sibling document after freeze.

## Coordinator freeze

Per the coordinator, this contract is frozen as `ef2-conv1` (config identity `intraday.momentum.v1`) for implementation once this PR merges. This statement is the coordinator's; the author makes no acceptance claim, and numerical, artifact and release gates remain.

## What was not verified

Nothing was executed against the library, installed artifacts, workers, databases or CI. The fixtures' compact notation was not expanded into canonical `CanonicalBatch` and `ConfigSpec` packets and config digests were not computed. The Q6 check was a source read of `validate_batch`; it was not run. The behavior of the R17 preparation internals was read from source, not run. Ownership, tracker and Project state were not rechecked beyond the issue bodies. Nothing here is accepted or Ready; the freeze is the coordinator's statement above.
