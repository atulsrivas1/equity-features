# EF4 path efficiency and choppiness contract - proposal (contract I1)

Prepared for EQ-161 [#495](https://github.com/atulsrivas1/equity-features/issues/495) (path efficiency and choppiness measures), for consumption by EF4 I/O [#613](https://github.com/atulsrivas1/equity-features/issues/613), worker [#614](https://github.com/atulsrivas1/equity-features/issues/614) and release acceptance EQ-163 [#497](https://github.com/atulsrivas1/equity-features/issues/497). It is the first half of contract I: EQ-172 [#513](https://github.com/atulsrivas1/equity-features/issues/513) (remaining equity statistical projections) is too large to share one clean contract with it and is the sibling [PATH_PROJECTIONS_CONTRACT_PROPOSAL.md](PATH_PROJECTIONS_CONTRACT_PROPOSAL.md). **This is a contract proposal, not accepted by any review; every convention below is a coordinator decision (final sections), pending owner review, and the contract carries a coordinator freeze statement.** It is contract preparation only: it admits no Ready state, implementation, numerical acceptance, release or performance claim.

Companion data: [PATH_EFFICIENCY_CONTRACT_PROPOSAL.json](PATH_EFFICIENCY_CONTRACT_PROPOSAL.json) holds the machine-readable producer, headers, role, mathematics, quality table, 31 result fixtures (203 expected outputs) and 39 typed-refusal fixtures. Expected values are hand-derived: each headline value is written by hand in the fixture definition and asserted equal to a plain `fractions.Fraction` reference (and, only where a logarithm is irrational, a 90-digit stdlib `decimal` value) computed by a scratch script that imports only the Python standard library and nothing from the equity packages. A second, independent standard-library harness then recomputes every fixture output (status, reasons, counts, value, float64, `float.hex`, acceptance rule, witnesses) and every refusal (the recorded mutation of its base fixture, through an independent admission model) from the JSON inputs alone, and all 31 result fixtures and 39 refusals match; two further independent reviewer scripts also match (except where they still encode the pre-fix PE20 observed count and the PR17 label that this revision deliberately changed). Float64 results carry the exact rational (or closed form plus decimal), `float.hex` and a per-output acceptance rule. The library was not imported, run or tested. Fixtures use compact notation (not canonical wire) and need expansion into canonical packets.

## Authority and inspected sources

Read-only inputs: the issues EQ-161 and EQ-172 as published; `docs/features/INTRADAY_FOUNDATIONS.md` (R17 governed grid, reset epoch, exact preparation, evidence bound), `HISTORICAL_FORMULAS.md` (positive scaled-integer closes, strict windows, ATR true range with a mandatory predecessor close, prior extrema), `CONTEXT_FORMULAS.md`, `EF1_PATHS.md` and `EF1_OBSERVABLES.md` (sampled extrema, hit semantics and the exact-arithmetic/single-conversion convention), `docs/EQUITY_DELIVERY_REPLAN.md` (EF4 tracks), `docs/plans/equity-output-ownership.json`, the frozen shared boundary `docs/ef1/CONTRACT.json`, the merged EF2 contracts and the merged EF3 contracts (structure, fixture rigor, numeric policy, reason precedence, the realized-variance treatment of log returns and reset epochs) and the shared validators and enums in `packages/contracts` (`validation.py`, `errors.py`), so that every fixture and refusal is constructible with existing codes. The mathematics is standard public technical analysis (Kaufman efficiency ratio, the Dreiss choppiness index, Wilder true range) restated from first principles with each varying convention chosen explicitly. No private source, threshold, window length or default is used or copied.

## Unchanged boundary

Existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult`, `Status`, `Reason`, `ErrorCode` and scalar `ValueType` values (`float64` is the only dtype used); the shared BAR validators; the R17 grid, admission, reset epoch, exact preparation and batch/full-replay modes; the frozen ef1-contract1 and every accepted core, R17, EF1, EF2 and EF3 header. `history.return`, `history.atr`, `intraday.atr`, `history.prior_high`, `history.prior_low`, `history.log_return_volatility`, `intraday.realized_variance` and the EF2 stochastic and Donchian outputs keep their definitions and ids and are not reused as operands (decision DP-E16). No new DataKind, DTO, result codec, scheduler or default, no new error code, no new validator, no change to a shared validator, no new reference fact kind and no new unit string (`fraction` and `currency/share` exist). This packet is additive: one new producer and seven new headers with a new catalog entry set whose digest is new (existing entries and digest inputs do not change). Update, restore and merge are unsupported (`UNSUPPORTED_CAPABILITY`); batch and full replay only. A sibling amendment document follows a freeze, as for EF2 and EF3.

## Producer and config identity

| Item | Path efficiency (#495) |
| --- | --- |
| Identity | `ef4.path_efficiency` |
| Algorithm / schema | `ef4-path-efficiency-v1` / `1` |
| Policy label | `ef4-path1` |
| Parameters (no defaults) | `policy_version`, `window` N (2..4096), `epoch_profile` (`session_reset`, `governed_history`), `evidence_limit` (0..10000) |
| Role | `bars` |
| ConfigSpec | PriceUnit mandatory; adjustment declared once |

A policy label names the whole convention set of its version (window rule, return basis, range basis, true-range basis, choppiness form, missingness mapping, rounding). An unsupported label is `INCOMPATIBLE_VERSION`; a future convention needs a new label, never a silent change. The window bound reuses the R17 period bound of 4096. Kaufman's 10 and Dreiss's 14 are literature examples, never defaults.

## Outputs and headers

| Feature id | dtype | unit | Available when |
| --- | --- | --- | --- |
| `path.choppiness_fraction` | float64 | fraction | closes t-N..t and high/low t-N+1..t READY, window range > 0 |
| `path.efficiency_ratio` | float64 | fraction | closes t-N..t READY, path length > 0 |
| `path.log_efficiency_ratio` | float64 | fraction | closes t-N..t READY, path length > 0 |
| `path.net_displacement` | float64 | currency/share | closes t-N..t READY |
| `path.path_length` | float64 | currency/share | closes t-N..t READY |
| `path.true_range_sum` | float64 | currency/share | closes t-N..t and high/low t-N+1..t READY |
| `path.window_range` | float64 | currency/share | closes t-N..t and high/low t-N+1..t READY |

Order: lexicographic by feature id. The price quantities carry the operand price unit and are divided by `10^scale` at publication. Each output has its own required operands, expected and observed counts and independent readiness: a close-only BAR delivery keeps the four close outputs available while the three range outputs are `missing_input`/`absent_input` (fixture PE20). A different config (window, epoch profile) is a different result.

## Inputs and role

| Role | Kind | Content |
| --- | --- | --- |
| `bars` | BAR | R17 chunked delivery on the governed grid of the epoch: intraday bars of the target session for `session_reset`, daily bars for `governed_history`; one instrument; positive-volume bars carry positive coherent OHLC, proven-empty zero-volume bars carry null OHLC; completed bars only (end <= market cutoff); close-only delivery is legal |

Value basis: prices are positive int64 coefficients at `ConfigSpec.price_unit.scale` (0..18) in one currency and one adjustment basis. All sums, differences, maxima and ratios are exact integers or rationals; coefficients are divided by `10^scale` once at publication. Sums of up to 4096 coefficients below 2^63 are exact wide integers, so no `OVERFLOW` path exists for a sum (PE24 reaches 3(2^62-1) internally); a single coefficient above int64 is refused. Every row declares the config adjustment basis (`UNSUPPORTED_ADJUSTMENT` otherwise). There is no acquisition, clock or I/O; the governed grid is the R17 context and omitted expected slots are never compressed away.

## Exact mathematics

Notation: target slot t, window N, base slot b = t - N, closes C_i, highs H_i, lows L_i for i = b..t. The window is the N+1 governed slots b..t (N returns), ending at the target bar inclusive (DP-E2).

- **Net displacement.** `ND = C_t - C_b`, signed, currency/share (DP-E5).
- **Path length.** `PL = sum_{i=b+1..t} |C_i - C_(i-1)|`, currency/share, `PL >= |ND|`.
- **Efficiency ratio (price domain).** `ER = |ND| / PL` in [0,1]. `PL = 0` is `not_applicable`/`zero_denominator` (then `ND = 0` too). Kaufman's ratio (DP-E4).
- **Log efficiency ratio.** `LER = |ln(C_t/C_b)| / sum_{i=b+1..t} |ln(C_i/C_(i-1))|` in [0,1]. Every ratio is formed from the exact coefficient ratio, so the price scale cancels. Equal closes `C_t = C_b` give exactly `+0.0`; all steps in one direction give exactly 1 mathematically; `PL = 0` is `zero_denominator`. The two efficiency ratios differ whenever step sizes differ in relative terms: PE04 gives ER = 1/2 and LER = ln 3 / (2 ln 2 + ln 3) ~ 0.4421, PE08 gives 1/3 for both only because every step is a doubling.
- **True range sum.** `TRS = sum_{i=b+1..t} max(H_i - L_i, |H_i - C_(i-1)|, |L_i - C_(i-1)|)` (DP-E7): the predecessor close is mandatory for every one of the N bars, so a gap beyond the bar counts (PE05: TR = 12 where H-L = 4). A plain sum over a finite window: not a Wilder recurrence, not anchored.
- **Window range.** `WR = max(max_{i=b+1..t} H_i, C_b) - min(min_{i=b+1..t} L_i, C_b)` (DP-E6). The base close extends the range; the base bar contributes only its close (PE06: base close 100 above every window high gives 12, not 8).
- **Choppiness fraction.** `CF = ln(TRS / WR) / ln(N)` (DP-E8). `WR = 0` is `zero_denominator`.
- **Bounds.** Each true range lies inside the interval `[min(L_i, C_(i-1)), max(H_i, C_(i-1))]`; consecutive intervals share the point `C_i`, so their union is the window range interval and `WR <= TRS`; each `TR_i <= WR` because both its endpoints lie in the extended range. Hence `1 <= TRS/WR <= N` and `0 <= CF <= 1` for every valid input. No clamp is applied or needed; an out-of-range value would be a defect.
- **Log-domain validity (DP-E9).** All prices are positive (the shared BAR validator, `INVALID_SCHEMA` otherwise), so every close ratio is a positive rational; `TRS/WR >= 1` by the bound, so `ln(TRS/WR) >= 0`; `N >= 2`, so `ln N > 0`. There is no invalid-log status: an invalid-log input is a refused input (zero, negative, non-integer or incoherent price: PR07 to PR15), never a null with a reason.
- **Publication.** Price outputs and ER: exact rational, one correctly rounded float64. LER and CF: natural logarithms to at least 120 digits from the exact integer ratios (log1p-grade near 1: PE27 steps of one tick on a 1e14 coefficient make log ratios 2e-14 from 1), one float64 rounding, tolerance acceptance; exact zeros are `+0.0`.

Worked values: PE01 closes 10, 20, 40, 80 (N=3): ND = PL = 70, ER = LER = 1, TRS = WR = 70, CF = 0 (a gapless trend has q = 1). PE03 closes 10, 20, 10, 20, 10 (N=4): ND = 0, PL = 40, WR = 10, TRS = 40, q = 4 = N and CF = 1 (maximal chop), ER = 0. PE04 closes 10, 20, 10, 20, 30: ER = 1/2, q = 2, CF = ln 2 / ln 4 = 1/2. PE09 (N=8, a pyramid 10..50..10): q = 2, CF = ln 2 / ln 8 = 1/3.

## Epochs, windows and gaps

- **Window (DP-E2).** Strict: exactly N+1 READY slots, no shrinking, no bridging of a hole, no `min_history`. Fewer than N+1 slots in the epoch (`t - N < a`) is `insufficient_history` when the slots present have no hole (PE11; a hole adds its own reason and leads the status, PE30); a window exactly full is available (PE06, `t = N`).
- **Epoch (DP-E3).** `session_reset`: the epoch is the target session; the first governed bar supplies only a base close; no return or true range crosses the session boundary (overnight changes never enter); a bar of another session inside the epoch is `INCONSISTENT_IDENTITY` (PR16). `governed_history`: the epoch is the supplied governed daily grid (PE28). Carry across sessions is not supported (`INVALID_CONFIG`, PR24).
- **Slot readiness (DP-E11).** A slot is READY iff its row exists, its required fields are non-null, its coverage is complete and `known_at <= K` (`known_at == K` is known, PE17). Causes: no row and no coverage `absent_input` (PE13), `known_at` null `unknown_availability` (PE18), `known_at > K` `future_knowledge` (PE16), null volume or null close `null_field` (PE14), declared incomplete coverage `governed_gap` (PE12), a coverage-proven empty slot (zero volume, null OHLC) `no_eligible_observations` (PE15): a return needs a price, so an empty slot is not a zero move. A slot older than the window never matters (PE10, PE29: finite recovery).
- **Zero denominators (DP-E10).** Exact integer tests, no epsilon. A flat window inside a moving history is flat (PE26). The operands stay available with value `+0.0` (PE02): zero is a value, not a missing observation.
- **Independent closures (DP-E12).** Close group: closes t-N..t. Range group: closes t-N..t plus high and low of t-N+1..t.

## Knowledge, canonical expansion and refusal precedence

- **Knowledge readiness.** K is the knowledge cutoff, distinct from the market cutoff C (K may be later than C). A bar is KNOWN iff its original `known_at_ns` is non-null and <= K (== K is known). The shared `AvailabilitySpec.knowledge_reason` returns None in reconstruction mode, so a shared validator never excludes a late row there; the producer therefore enforces knowledge itself from the original `known_at_ns`, identically in `known_at` and reconstruction modes. Compact token `ka` maps to `known_at_ns = K_ns - (100 - ka)` s with `K_ns = C_ns + 100` s.
- **Canonical expansion.** Slot i of a fixture is placed at `start_ns = 1.7e18 + i*60e9` (epoch scale, beyond 2^53), session S1, instrument X (daily slots: 86400e9 spacing, session D<i>); C is the end of the last delivered slot and the target slot is explicit, so slots after the target are completed bars before C (prefix fixture PE25) and a bar ending after C is `BOUNDS`. `{wire: {inst, ss, start, end, row}}` replaces a compact slot by an explicit row; refusals PR01 to PR05, PR16 and PR17 use it, so duplicate, order, bound, cutoff and identity defects are real values that the independent harness feeds to its emulation of `validate_batch` and of the producer identity checks. PR03 is a distinct grid mismatch (a bar starting one second late, overlapping nothing); PR17 (second instrument) is raised by producer admission, because `validate_batch` does not raise on it.
- **Refusal precedence (one order).** wire (cell types, ranges, row width, grammar: `INVALID_SCHEMA`, `OVERFLOW`), then shared validator (`DUPLICATE`, `INVALID_ORDER`, `BOUNDS`, OHLC `INVALID_SCHEMA`), then config (`INVALID_CONFIG`, `UNSUPPORTED_CAPABILITY`, `UNKNOWN_FEATURE`, `INVALID_UNIT`, `UNSUPPORTED_ADJUSTMENT`), then version (`INCOMPATIBLE_VERSION`), then identity (`INCONSISTENT_IDENTITY`), then data (producer rules over valid data). The first stage with a fault raises, and a row rejected earlier is not also reported by a later stage. Every recipe is a first-stage single fault: one defect in the stage recorded in the refusal's `stage` field, and exactly one error code fires; later-stage checks are not evaluated for a row rejected earlier (PR04 and PR05 are also off-grid, but the shared validator rejects them first).

## Availability, coverage, quality, evidence and refusals

Typed refusal precedes assessment. Quality uses existing `Status`/`Reason` only, with the merged robust-pace precedence: `absent_input`, `unknown_availability`, `future_knowledge`, `null_field`, `ineligible` (all `missing_input`), `governed_gap`, `future_market`, `partial_universe` (all `incomplete_coverage`), `insufficient_history`, `no_eligible_observations`, `empty_universe`, `zero_denominator` (the last three `not_applicable`), else `available`. All applicable reasons are retained in lexical order; the status follows the first applicable reason; a value is null exactly when the status is not available; `available` implies `observed == expected`. `ineligible`, `future_market`, `partial_universe` and `empty_universe` are unreachable in this producer. Knowledge is enforced identically in `known_at` and reconstruction modes with original `known_at`. PE19 and PE30 show multi-reason precedence.

Counts: expected `N + 1` slots; observed READY slots among `max(a, t-N)..t` for the output's own fields; the reasons are the causes of the lost slots only, plus `insufficient_history` only when `t - N < a`. For the range outputs of a close-only delivery the high and low of slots t-N+1..t are not delivered (`absent_input`) while the base slot needs only its close, so observed is 1 when the base close is READY (PE20).

Evidence (available outputs only): the limit is the existing `evidence_limit` 0..10000, result-wide as `FeatureResult` bounds it; fixtures list the per-output witnesses when selected alone. Order: target slot first, then the base slot, then slots t-N+1..t-1 ascending; row ids `slot:<i>`, boundary `completed_interval`. PE22 (ND selected alone, limit 2: `slot:3`, `slot:0`) and PE23 (limit 0) cover truncation; a joint selection shares the limit result-wide and lists outputs in lexical feature-id order.

Refusals (no `FeatureResult`) PR01 to PR39 in the JSON, each recording its base fixture and the exact mutation (the construction recipe) and whether a shared validator or the library raises it: duplicate bar `DUPLICATE`; overlapping or out-of-grid-order bars `INVALID_ORDER`; start >= end, a bar beyond the cutoff or negative volume `BOUNDS`; high below low, close outside high/low, zero price, zero-volume bar with prices, positive-volume null price, float price or volume, wrong row width `INVALID_SCHEMA`; a coefficient above int64 `OVERFLOW`; a bar of another session or a second instrument `INCONSISTENT_IDENTITY`; bad, missing or unknown window, epoch profile, evidence limit or parameter `INVALID_CONFIG`; unsupported label `INCOMPATIBLE_VERSION`; scale, currency or missing price unit `INVALID_UNIT`; adjustment `UNSUPPORTED_ADJUSTMENT`; unknown feature `UNKNOWN_FEATURE`; update, restore, merge `UNSUPPORTED_CAPABILITY`. Every code was checked against `errors.py` and `validation.py`; no new code or validator change is needed.

## Numeric policy and acceptance

Exact integer/rational arithmetic throughout, one correctly rounded float64 per published value, compatible with the R17 Decimal120 policy and its error contract. Acceptance rule per fixture output (field `acceptance` in the JSON):

- `exact_float64`: the reference is a dyadic rational with numerator below 2^53, so any exact-rational or Decimal120 path produces it without rounding; the published float64 must equal the hex bit for bit (71 outputs).
- `exact_plus_zero`: the reference is exactly 0 from exact arithmetic (equal integers, equal closes, `TRS/WR = 1`): bit-exact `+0.0`, never `-0.0` (23 outputs).
- `tolerance`: `abs(y - r) <= max(8 ulp(r), 1e-12 |r|)` with r the fixture float64, the R17 numeric error contract (`docs/api/INTRADAY.md`, "Numeric error contract and capabilities"); used for non-dyadic rationals and for every value that passes through a logarithm even when its reference is dyadic (37 outputs, e.g. CF = 1/2 in PE04), so implementations need not special-case it.

Total 131 classified outputs; no documented exceptions. Reconciliation with the single-rounding publication rule: the published value is the exact rational (or 120-digit logarithm value) rounded once, so an exact implementation returns the correctly rounded float64 (within 0.5 ulp) and the fixture float64 is that value; the envelope is the R17 pass/fail rule inherited for Decimal120 and other conforming backends, not a licence for a looser exact path. Measurement of cost is not part of this contract; the processing is O(N) per window with bounded N, and any speed claim belongs to the release baseline.

## Layer responsibilities

- **Library (#495).** Admission of the supplied bars and context, window and slot readiness, exact sums and ratios, logarithms with the stated accuracy, quality, evidence and every library refusal above; pure and deterministic; one shared window preparation (closes, true ranges, extended range) reused by the seven outputs without coupling their readiness.
- **EF4 I/O #613.** Maps ordered bars, the governed grid and coverage into the BAR role and the R17 context exactly as supplied with original `known_at`; maps results to the existing sink conversion; never sorts, fills, imputes, drops, resamples, converts scale or currency, chooses a window or epoch, or computes a return, range or logarithm.
- **Worker #614.** Routes selected outputs with exact window closure, shares one bounded window per symbol and epoch across outputs, keeps independent readiness, executes one config per complete result, binds inputs and the config digest and persists the library result unchanged. Direct, adapter, worker and stored results must be identical, including refusal class.

## Fixtures

31 result fixtures (PE01 to PE31, 203 expected outputs) and 39 refusal fixtures (PR01 to PR39). The JSON `coverage_map` indexes them by tag, `reasons_reached` by reason and `prefix_equivalences` lists identical-result pairs (PE04/PE25, PE01/PE17). Coverage: monotone, flat, oscillating and mixed OHLC paths (PE01 to PE09); gap and zero-range (PE02, PE05, PE26); extended range and true range (PE05, PE06); short history and the boundary (PE06, PE11, PE30); window scope and finite recovery (PE10, PE29); every reason reachable here (`absent_input` PE13, `unknown_availability` PE18, `future_knowledge` PE16, `null_field` PE14, `governed_gap` PE12, `insufficient_history` PE11, `no_eligible_observations` PE15, `zero_denominator` PE02); knowledge boundary (PE17); precedence (PE19, PE30); independent readiness (PE20); price scale (PE21); evidence truncation (PE22, PE23); int64 limits (PE24); prefix property (PE25); near-flat log accuracy and near-cancellation (PE27; PE31: closes 1e14, three 1000-tick steps and a 1-tick pullback, N=4, choppiness ln(3001/3000)/ln 4 ~ 2.4e-4, which an ln of a rounded float ratio would lose); governed daily grid (PE28); choppiness exact rationals 0, 1/3, 1/2, 1 (PE01, PE09, PE04, PE03). Refusals include the invalid-log inputs (zero, negative, non-integer, incoherent price).

Fixture notation is in the JSON `fixture_notation`. Prefix property: every output at target t depends only on slots t-N..t, so appended later slots with later knowledge change nothing (PE25). Required readback: every stored float64 equals the float64 of the exact rational (or of the 120-digit logarithm value).

## Explicit non-goals

No thresholds, trend/range classification, scanners, alerts or catalogue policy (EF8 #518-#520); no default window, minimum history or tolerance; no ADX, Kaufman adaptive moving average, smoothed efficiency ratio or Ulcer index; no carry epoch, overnight return or cross-session window; no resampling or volume/time re-bucketing; no change to `history.atr`, `intraday.atr`, `history.prior_high`, `history.prior_low`, `history.return`, `history.log_return_volatility` or `intraday.realized_variance`; no acquisition, adjustment, currency conversion, imputation or forward fill; no update, restore or merge; no new DataKind, DTO, codec, scheduler, validator or error code; no performance, parity, release or publication claim; no private-source equivalence or source formula.

## Coordinator decisions: conventions (accepted as proposed, pending owner review)

| Id | Convention (alternatives in the JSON) |
| --- | --- |
| DP-E1 | One producer, seven outputs including the operands net, path, TRS and range, each with its own closure. |
| DP-E2 | N returns from N+1 governed slots ending at the target inclusive; N caller-set 2..4096; strict, no min_history. |
| DP-E3 | `session_reset` and `governed_history` epochs; no carry. |
| DP-E4 | Two efficiency outputs: price-domain (Kaufman) and log-domain. |
| DP-E5 | Net displacement is signed; ratios use its absolute value. |
| DP-E6 | Window range includes the base close. |
| DP-E7 | True range with the predecessor close, plain sum over N bars; not Wilder, not history.atr. |
| DP-E8 | Choppiness published as the fraction `ln(q)/ln(N)` in [0,1]; the 100x Dreiss index is presentation. |
| DP-E9 | Logs only of exact positive rationals; invalid-log inputs are refused, never nulled; no clamp. |
| DP-E10 | Exact zero tests; zero path or range is `zero_denominator`; operands stay available. |
| DP-E11 | Slot causes mapped to the merged EF3 reasons; an empty slot is `no_eligible_observations`; holes never tolerated. |
| DP-E12 | Close group and range group closures; close-only delivery serves the close group. |
| DP-E13 | Exact arithmetic, one rounding, logs >= 120 digits, log1p-grade; tolerance acceptance for log-derived values. |
| DP-E14 | Units `currency/share` and `fraction`; no new unit string. |
| DP-E15 | Evidence: target, base, interior ascending. |
| DP-E16 | No change to, and no operand from, the accepted return/ATR/extrema/volatility outputs. |
| DP-E17 | Batch and full replay only. |

## Coordinator rulings on the open questions (pending owner review)

| Id | Ruling |
| --- | --- |
| OQ-E1 | Publish the choppiness fraction; the 100x index is a consumer presentation; a points unit is deferred to an amendment. |
| OQ-E2 | One producer for daily and intraday via `epoch_profile`; the arithmetic is identical. |
| OQ-E3 | (conservative) no minimum history; a later `min_history` needs a new policy label. |
| OQ-E4 | Efficiency on midpoints or typical price is deferred; closes only in v1. |
| OQ-E5 | Hosted in `packages/features` (EF4 module, config namespace `ef4.*`, separate catalog); `describe_intraday()` and its digest unchanged; no package version bump. |

## Header ledger and amendment (to be applied)

The 7 headers of this contract are to be applied by a sibling amendment document after the freeze; the units `currency/share` and `fraction` already exist and no new unit string is needed.

## Coordinator freeze

Frozen as `ef4-path1` (v1) for implementation once this PR merges (coordinator statement; no review or acceptance claim by the author). There are no defaults for window or any threshold. Any change to a convention, label semantics, header, role or fixture after merge requires a new policy label and an amendment document.
