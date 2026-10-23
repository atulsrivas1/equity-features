# EF2 Ichimoku and price-channel contract - proposal

Prepared for EQ-151 [#485](https://github.com/atulsrivas1/equity-features/issues/485) (aligned Ichimoku) and EQ-170 [#511](https://github.com/atulsrivas1/equity-features/issues/511) (Keltner and Donchian channels, selected pivot levels, price-band width percentile, Bollinger/Keltner squeeze primitives), consumed by EF2 I/O [#609](https://github.com/atulsrivas1/equity-features/issues/609), worker [#610](https://github.com/atulsrivas1/equity-features/issues/610) and acceptance EQ-152 [#486](https://github.com/atulsrivas1/equity-features/issues/486). This is a contract proposal, not accepted. It admits no Ready state, implementation, numerical acceptance or release claim, and every convention below marked DECISION-PROPOSED awaits a coordinator ruling.

Companion data: [ICHIMOKU_CHANNELS_CONTRACT_PROPOSAL.json](ICHIMOKU_CHANNELS_CONTRACT_PROPOSAL.json) holds machine-readable producers, headers, roles, parameters, 59 result fixtures, 20 typed-refusal fixtures and 7 cross-fixture invariants. Expected values were derived with plain `fractions` and `decimal` arithmetic in a scratch script that imports nothing from the equity packages; the library was not imported, run or tested. Fixtures use compact notation (not canonical wire) and still need expansion into canonical packets.

All indicators here are standard, publicly documented constructions. They are specified from their public definitions with explicit conventions, with no private source, threshold, ratio or default.

## Authority and unchanged boundary

Read, not changed: the accepted R17 intraday package (`_context.py`, `_admission.py`, `_prepare.py`, `_indicators.py`, `_bands.py`, `_dispatch.py`, `_registry.py`), [INTRADAY_FOUNDATIONS.md](../features/INTRADAY_FOUNDATIONS.md), [INTRADAY API](../api/INTRADAY.md), the frozen [EF1 CONTRACT.json](../ef1/CONTRACT.json) conventions, and the structure of the merged EF1 [close-reconciliation](../ef1/CLOSE_RECONCILIATION_CONTRACT_PROPOSAL.md) and [multi-venue status](../ef1/MULTI_VENUE_STATUS_CONTRACT_PROPOSAL.md) proposals. [EQUITY_DELIVERY_REPLAN.md](../EQUITY_DELIVERY_REPLAN.md) requires the EQ-170 percentile population and rank convention to be reviewed before affected Ready; section "Percentile" proposes it for that review.

Unchanged: `CanonicalBatch`, `ConfigSpec`, `Parameter`, `FeatureResult`, scalar `ValueType` (float64 and bool are used), `Status`/`Reason`, the R17 `IntradayContext` codec and limits (at most 4096 governed slots, 64 sessions), R17 BAR admission, R17 status precedence, evidence boundary `completed_interval`. No new DataKind, DTO, codec, scheduler, default, clamp or closure. Capabilities: batch and full supplied replay only; update, restore and merge unsupported (as R17).

EQ-149 [#483](https://github.com/atulsrivas1/equity-features/issues/483) (stochastic) is a listed prerequisite of EQ-170 but no stochastic output is consumed here; see O1. No unused operand becomes a runtime barrier.

## Producers and config identities

Six homogeneous producers, each with its own closed parameter set, so a caller selecting one family never supplies another family's parameters. Each returns its complete sorted header set. All use algorithm `ef2-v1`, schema `1`, ConfigSpec identity `ef2.<producer>` (packaging route open: O11).

| Producer | Operation parameters (all required, no defaults) | Convention label |
| --- | --- | --- |
| `ichimoku` | `conversion_period`, `base_period`, `leading_b_period`, `displacement` | `ef2-ichimoku-conv1` |
| `keltner` | `ema_period`, `atr_period`, `atr_multiplier_num`, `atr_multiplier_den` | `ef2-keltner-conv1` |
| `donchian` | `period` | `ef2-donchian-conv1` |
| `pivot_levels` | none | `ef2-pivot-conv1` |
| `band_width_percentile` | `band_period`, `band_k_num`, `band_k_den`, `population_size` | `ef2-bandpct-conv1` |
| `bollinger_keltner_squeeze` | `band_period`, `band_k_num`, `band_k_den`, `ema_period`, `atr_period`, `atr_multiplier_num`, `atr_multiplier_den` | `ef2-squeeze-conv1` |

Every config also carries `convention_version` (exact label above), `evidence_limit` (0..10000) and the R17 context envelope (`context_schema`, `context_sha256`, `context_chunks`, `context_000..`). `convention_version` names the whole set of choices in this document for that producer (extrema basis, window inclusion, tie rule, boundary inclusivity, formulas). An unsupported label is `INCOMPATIBLE_VERSION`; a different convention needs a new label, never a silent change. Integers: periods 1..4096 (`band_period` 2..4096, `displacement` 1..4096, `population_size` 1..4096); multipliers `*_num/*_den` in reduced form, each 1..1000000 (the R17 band rule). Booleans are not integers. The Ichimoku set 9/26/52/26 is named in fixture ICH-14 only; it is never a default.

## Inputs and roles

One role, `bars` (BAR kind), exactly the R17 admission: actual BAR chunks on the governed context grid, exact positive int coefficients at one `PriceUnit` and adjustment, half-open `[start, end)` slots, `end <= market cutoff C`, knowledge judged at K. Required columns by producer:

| Producer | Columns read |
| --- | --- |
| `ichimoku` | `high`, `low` (lines and spans); `close` (lagging pair) |
| `keltner`, `bollinger_keltner_squeeze` | `close`, and `high`/`low` for true range |
| `donchian`, `pivot_levels` | `high`, `low`; pivots also `close` of the last prior-session slot |
| `band_width_percentile` | `close` only |

A column absent from a supplied chunk holding required slots is `missing_input/absent_input` for outputs that read it only (fixture ICH-07, PCT-10). A zero-volume admitted row is an observed-empty slot (R17).

## Notation

`t` target slot (final governed slot), `a` anchor slot (R17 reset: first target-session slot; carry: supplied earlier anchor), `n = t - a + 1`. `H[i]`, `L[i]`, `C[i]` integer coefficients, `D = 10^scale`. `HH(P, e) = max H[e-P+1..e]`, `LL(P, e) = min L[e-P+1..e]`, `mid(P, e) = (HH(P, e) + LL(P, e)) / 2`. Every window lies inside `[a, t]` (no shortening, no reaching before the anchor). All arithmetic is exact rational (or the single guarded Decimal120 step noted) in coefficient units; output = value / D.

## Mathematics

### Ichimoku (`ichimoku`), standard definitions

Let `Pt = conversion_period`, `Pk = base_period`, `Pb = leading_b_period`, `d = displacement`, `o = t - d`.

| Header (prefix `trend.ichimoku.`) | Value | Origin slot | Display slot |
| --- | --- | --- | --- |
| `conversion_line` | `mid(Pt, t)` | `t` | `t` |
| `base_line` | `mid(Pk, t)` | `t` | `t` |
| `leading_span_a_observed` | `(mid(Pt, t) + mid(Pk, t)) / 2` | `t` | `t + d` (beyond the governed grid) |
| `leading_span_b_observed` | `mid(Pb, t)` | `t` | `t + d` |
| `leading_span_a_displayed` | `(mid(Pt, o) + mid(Pk, o)) / 2` | `t - d` | `t` |
| `leading_span_b_displayed` | `mid(Pb, o)` | `t - d` | `t` |
| `lagging_line_observed` | `C[t]` | `t` | `t - d` |
| `lagging_line_reference_close` | `C[t - d]` | `t - d` | `t - d` |

DECISION-PROPOSED D1 (extrema basis): high/low extrema, midpoint of extrema `(HH + LL)/2`, window of `P` governed bars that includes the current bar. Alternatives named: close-based extrema; window excluding the current bar.

DECISION-PROPOSED D2 (periods and displacement): explicit required config, no default. Alternatives: a built-in 9/26/52/26 default; market-specific sets (for example 7/22/44). The 9/26/52/26 set appears only as a named fixture.

DECISION-PROPOSED D3 (observation versus display): a displayed shifted value is never published as if known earlier. Each leading span has two headers: `_observed` (computed at origin `t`, to be drawn `d` bars later; its display position is future and no timestamp for it is produced) and `_displayed` (the value drawn at `t`, computed at origin `t - d`, so it reads only bars `<= t - d`). The lagging line is published only as `lagging_line_observed = C[t]` (drawn at `t - d`); no output at `t` holds `C[t + d]`, which cannot exist at `t`. `lagging_line_reference_close = C[t - d]` is the price the shifted line is compared against at its display position and is available at `t`. Alternatives: one "displayed at t" header per span without the observed pair (rejected: hides the origin), emitting future display timestamps (O5).

D5: `leading_span_a_*` use exact extrema midpoints, never the rounded published lines.

Dependency exclusion: displayed outputs read no slot after `t - d`; a gap, empty, null or later-known value at slots `t-d+1..t` cannot affect them (ICH-04, ICH-05). Lines and observed spans need their own windows only.

### Keltner channel (`keltner`)

Centre `E = EMA(close, ema_period)` using the R17 `intraday.ema` recurrence and seed (SMA of the first `ema_period` closes from `a`, then `E[i] = (2 C[i] + (N-1) E[i-1])/(N+1)`), width unit `ATR = Wilder ATR(atr_period)` using the R17 `intraday.atr` recurrence (true range from `a+1`; seed mean of the first `atr_period` true ranges; `ATR[i] = ((N-1) ATR[i-1] + TR[i])/N`). `m = atr_multiplier_num/atr_multiplier_den`.

| Header (prefix `channel.keltner.`) | Value |
| --- | --- |
| `middle` | `E` |
| `upper` | `E + m ATR` |
| `lower` | `E - m ATR` (no positive clamp) |
| `width_ratio` | `2 m ATR / E` (fraction; `E > 0` always) |

DECISION-PROPOSED D6: EMA of close centre, Wilder ATR, rational caller multiplier. Alternatives: SMA or typical-price centre, SMA-of-true-range width, ATR multiple relative to price. D7: Keltner consumes the unrounded internal EMA/ATR recurrence values (Decimal120, exactly as R17 forms them), not the published float64 `intraday.ema`/`intraday.atr`; the only conversion is the final one. `channel.keltner.middle` equals R17 `intraday.ema` for the same period, anchor and inputs (no second EMA implementation; the header exists because it belongs to a different config; O9). Closure: all closes `a..t`, and high/low at `a+1..t`; a gap anywhere in the anchored chain blocks every header (KEL-03), as for R17 EMA/ATR.

### Donchian channel (`donchian`)

| Header (prefix `channel.donchian.`) | Value | Columns |
| --- | --- | --- |
| `upper` | `HH(N, t)` | high |
| `lower` | `LL(N, t)` | low |
| `middle` | `(HH + LL)/2` | high, low |
| `width_ratio` | `(HH - LL) / ((HH + LL)/2)` | high, low |

DECISION-PROPOSED D8: window of `N` bars including the current bar. Alternative: the previous `N` bars excluding the current bar (breakout-style). The middle equals the Ichimoku `mid` for the same period; both use one shared rolling-extrema operand. Upper and lower have independent readiness (DON-03).

### Selected pivot levels (`pivot_levels`)

Let `S` be the governed session immediately preceding the target session in the context's session list (not a calendar inference), with all its governed slots; `H = max H[S]`, `L = min L[S]`, `C = C[last slot of S]`.

`P = (H + L + C)/3`; `R1 = 2P - L`; `S1 = 2P - H`; `R2 = P + (H - L)`; `S2 = P - (H - L)`.

Headers (prefix `channel.pivot.`): `point`, `resistance_1`, `support_1`, `resistance_2`, `support_2`. Levels are published unclamped; supports may be negative (PIV-05).

DECISION-PROPOSED D9: classic floor-trader pivots from the immediately preceding governed session's exact bar high/low/close. Alternatives: Woodie, Camarilla, Fibonacci or DeMark variants; R3/S3 (non-goal); sourcing from EF1 `calendar.period.*` (float64, lossy) or a #506 calendar period (O4). Target exclusion: no target-session bar contributes (PIV-02); anchor and mode are irrelevant (PIV-07); only the immediately preceding session counts (PIV-06).

### Price-band width percentile (`band_width_percentile`)

Band width is the R17 Bollinger-style width ratio: for the window of `N = band_period` closes ending `j`, `mu_j` mean, `V_j` population variance, `k = band_k_num/band_k_den`, `w_j = 2 k sqrt(V_j) / mu_j`. Ranking uses the exact square `w2_j = 4 k^2 V_j / mu_j^2` (monotone for `w_j >= 0`, exact rational), never the published float64 width.

Population: the `M = population_size` widths at slots `t-M..t-1` (the target's own width is excluded). With `Lt = #{w2_j < w2_t}` and `Et = #{w2_j = w2_t}` over the population:

`percentile = (2 Lt + Et) / (2 M)` (fraction in [0, 1]; mid-rank, ties count half).

DECISION-PROPOSED D10 (population and rank, for the required review). Alternatives, all computed for PCT-01 under `alternatives_not_chosen`: strict `Lt/M`; weak `(Lt+Et)/M`; population including the target (`M+1` values); interpolated/nearest-rank percentile of the value distribution. Rank on exact witnesses is required because published widths can tie while exact widths differ (PCT-10, near 2^60). Closure: closes at `t-M-N+1..t` (`M+N` bars); any gap, null or later-known value in that span makes the output unavailable; a partial population is never ranked.

### Squeeze primitives (`bollinger_keltner_squeeze`)

Bollinger-style band: `mu`, `V` over the last `band_period` closes, `r = k sqrt(V)`, upper `mu + r`, lower `mu - r` (R17). Keltner as above. Signed gaps in currency/share:

`upper_gap = (E + m ATR) - (mu + r)`, `lower_gap = (mu - r) - (E - m ATR)`.

`bollinger_inside_keltner = (upper_gap >= 0) and (lower_gap >= 0)`, decided by exact algebra, never by the published floats: with `x = E + m ATR - mu`, `y = mu - E + m ATR`, `upper_gap >= 0` iff `x >= 0 and x^2 >= k^2 V`; likewise for `y`. Equal is inside (inclusive). Gap floats are one conversion of the exact value (the sqrt term evaluated once in Decimal120 when irrational).

This is arithmetic only. There is no threshold, no persistence count, no "squeeze on/off" semantics and no policy value; consumers and catalogue predicates (#518) build any signal. DECISION-PROPOSED D12: signed gaps plus an inclusive relation. Alternatives: strict relation; a ratio form (`keltner_width/bollinger_width`); a bool only without gaps (rejected: loses margin).

## Headers, dtypes and units

25 headers; full list with dtype/unit/offsets in the JSON. Float64 headers use one correctly rounded conversion (round-half-even) from the exact value, `+0.0` for exact zero, never computed from other rounded outputs. Non-finite output cannot occur (see overflow).

| Producer | Headers (id prefix) | dtype / unit |
| --- | --- | --- |
| `ichimoku` (8) | `trend.ichimoku.` `base_line`, `conversion_line`, `lagging_line_observed`, `lagging_line_reference_close`, `leading_span_a_displayed`, `leading_span_a_observed`, `leading_span_b_displayed`, `leading_span_b_observed` | float64 / currency/share |
| `keltner` (4) | `channel.keltner.` `lower`, `middle`, `upper`, `width_ratio` | float64 / currency/share; `width_ratio` fraction |
| `donchian` (4) | `channel.donchian.` `lower`, `middle`, `upper`, `width_ratio` | same |
| `pivot_levels` (5) | `channel.pivot.` `point`, `resistance_1`, `resistance_2`, `support_1`, `support_2` | float64 / currency/share |
| `band_width_percentile` (1) | `channel.band_width.percentile` | float64 / fraction |
| `bollinger_keltner_squeeze` (3) | `channel.squeeze.` `bollinger_inside_keltner`, `lower_gap`, `upper_gap` | bool / boolean; float64 / currency/share |

DECISION-PROPOSED D13: float64 outputs (R17 convention for computed values) rather than decimal128 (EF1 uses decimal128 only for projected supplied facts).

Ordering: lexicographic by `feature_id` within the producer; one scalar `EntityKey(instrument_id, target session)` per header; column `algorithm_version` `ef2-v1`.

## Warm-up, readiness and gaps

Each header is decided separately from its own closure; expected = closure size `R` (or the formula), observed = unique closure slots whose fields, coverage and knowledge qualify.

| Header | Closure (fields) | Insufficient history when | expected |
| --- | --- | --- | --- |
| conversion, base | `e-P+1..t` (H, L) | `n < P` | `P` |
| leading A observed | `t-max(Pt,Pk)+1..t` (H, L) | `n < max(Pt,Pk)` | `max(Pt,Pk)` |
| leading B observed | `t-Pb+1..t` (H, L) | `n < Pb` | `Pb` |
| leading A displayed | `o-max(Pt,Pk)+1..o` (H, L) | `n < max(Pt,Pk)+d` | `max(Pt,Pk)` |
| leading B displayed | `o-Pb+1..o` (H, L) | `n < Pb+d` | `Pb` |
| lagging observed | `t` (C) | never (n>=1) | 1 |
| lagging reference close | `o` (C) | `n < d+1` | 1 |
| Keltner (all four) | `C a..t`, `H/L a+1..t` | `n < max(ema_period, atr_period+1)` | `max(ema_period, atr_period+1, n)` |
| Donchian | `t-N+1..t` | `n < N` | `N` |
| Pivots | all slots of preceding session; `C` only of its last slot | no preceding session in the context | slot count of that session (1 when absent) |
| Percentile | `t-M-N+1..t` (C) | `n < M+N` | `M+N` |
| Squeeze (all three) | Keltner closure | `n < max(ema_period, atr_period+1, band_period)` | `max(ema_period, atr_period+1, band_period, n)` |

Status precedence is the R17 one: no delivery or absent operand column -> `missing_input/absent_input`; else short closure -> `insufficient_history/insufficient_history`; else `incomplete_coverage` with every applicable reason (`governed_gap`, `observed_empty` plus `no_eligible_observations`, `null_field`, `unknown_availability`, `future_knowledge`) in enum order; else `available`. When a short closure also has slot failures the reasons coexist under the first status. No delivery: `absent_input` only, observed 0, expected `R`, consequent reasons suppressed (ICH-13, DON-07). A pivot context without a preceding session is `missing_input/absent_input`, expected 1, observed 0 (D14, O8). A gap or later-known slot outside a header's closure never blocks it (DON-04, PCT-09, ICH-05).

## Availability, quality, evidence and refusals

Knowledge uses the R17 availability modes: `end <= C`, known_at `<= K`; unknown known_at -> `unknown_availability`; later -> `future_knowledge`; reconstruction mode keeps its declared reason. A forming or future supplied bar (`end > C`) is a typed refusal (RF01), not a state.

Zero-denominator is unreachable: every denominator is positive by construction (`E`, `mu` are means of positive prices; `HH+LL > 0`; `M >= 1`). Zero ranges are available values (flat data: width 0, band radius 0, gaps 0; fixtures ICH-09, KEL-04, DON-05, PIV-09, PCT-03, SQ-05). `not_applicable` is not emitted by this contract.

Overflow: inputs are positive int64 coefficients; sums of at most four such values and ratios bounded by multipliers `<= 10^6` stay far below float64 range, so float64 output is always finite. Internal exact arithmetic beyond the inherited Decimal120/bounded-integer policy is the R17 typed `OVERFLOW` guard (RF20); results are never clamped, rounded early or replaced by non-finite values.

Evidence: bounded `EvidenceRow`s, boundary `completed_interval`, `row_id` `slot:<global_index>`, sorted by feature id then slot, truncated at `evidence_limit` with counts always summarizing the full closure (as R17). Consumed and knowledge-excluded supplied rows only; never invented. Which slot supplied an extremum is not published (O7).

Typed refusals (20, RF01 to RF20 in the JSON): bar end beyond C (`BOUNDS`), duplicate slot (`DUPLICATE`), off-grid row or context/config mismatch (`INCONSISTENT_IDENTITY`), unknown convention (`INCOMPATIBLE_VERSION`), open/missing/out-of-range parameters (`INVALID_CONFIG`), unit/basis mismatch (`INVALID_UNIT`, `UNSUPPORTED_ADJUSTMENT`), wrong input kind or contradictory OHLC (`INVALID_SCHEMA`), unsupported state operations (`UNSUPPORTED_CAPABILITY`), unknown feature id (`UNKNOWN_FEATURE`), inherited `OVERFLOW`.

## Layer responsibilities

| Layer | Owns | Does not |
| --- | --- | --- |
| Library (EF2 core, #485/#511) | Pure calculation of the 25 headers over supplied BAR facts; config builder/decoder with closed parameters and convention labels; per-header readiness, quality and evidence; shared rolling-extrema, EMA/ATR and moment operands (generalized to a window end offset, O3); independent fixtures | Acquire data, resolve calendars, produce future timestamps, apply thresholds, schedule, persist |
| EF2 I/O #609 | Map admitted bars (and the preceding session's bars for pivots) to canonical BAR batches and R17 context; map results to rows unchanged; supply the displayed-position timestamp mapping if wanted (O5); never derive or replace values | Compute channels, reorder, fill gaps, relabel observed as displayed |
| Worker #610 | Scheduling, sharing preparation across the six producers, persistence; homogeneous WorkItems per producer | Change mathematics, defaults or status semantics |
| Acceptance EQ-152 #486 | Replays these fixtures through actual layers and checks full value/hex/quality/evidence parity and lookahead counterexamples | Accept formulas not frozen here |

## Fixtures

59 result fixtures: ICH-01..14, KEL-01..08, DON-01..08, PIV-01..09, PCT-01..11, SQ-01..09. Coverage map in the JSON: short history; displaced arrays and observation versus display (ICH-01 to 05, 14); lookahead counterexample pair (ICH-04: bars after `t-d` changed, displayed outputs equal ICH-01; ICH-05: later-known tail); gaps in and out of closures; cutoff/availability (future, unknown, empty, no delivery, absent column); zero range; target exclusion (pivots, percentile population); percentile ties, population edges and exact-versus-published rank (PCT-02 to 06, 10); squeeze boundary equalities (SQ-02 upper exactly 0, SQ-03 lower exactly 0, SQ-04 upper gap exactly -29/2592 so outside, SQ-05 both 0); separate readiness; carry versus reset. Every fixture lists inputs, per-header value, `float.hex`, exact rational, status, reasons, expected, observed and `max_input_slot` (always `<= t`).

Literal examples (scale 2; ICH-01 bars in the JSON, periods 3/5/8, displacement 4, target slot 11): `leading_span_a_observed` = 411/40 = 10.275 (`0x1.48ccccccccccdp+3`, drawn at slot 15, beyond the grid); `leading_span_a_displayed` = 161/16 = 10.0625 (`0x1.4200000000000p+3`, origin slot 7, uses slots 3..7 only); `lagging_line_observed` = 53/5 (`0x1.5333333333333p+3`); `lagging_line_reference_close` = 197/20 (`0x1.3b33333333333p+3`). PIV-01: point 611/60 (`0x1.45ddddddddddep+3`), support_2 115/12. PCT-01: 1/4. SQ-04 `upper_gap` = -29/2592 (`-0x1.6e9e06522c3f3p-7`), `lower_gap` = 16067/2592, inside = false.

## Explicit non-goals

Thresholds, scores, crossings, cloud colour, breakout and squeeze persistence or any signal policy (catalogue #518); future wall-clock timestamps for displaced positions; retracement levels (separate EF2 contract by another author, whose extrema operand and the #511 caller-parameterized ratios are not defined here); pivot families other than classic and R3/S3; Keltner or Donchian width percentiles; stochastic, DMI, MACD or money-flow operands; update/restore/merge/streaming state; data acquisition, calendars, scheduling, persistence, provider or private data; performance claims (the story's extrema-reuse and output-size measurement is an implementation-time workload, 25 scalar headers per target here).

## DECISION-PROPOSED summary

D1 high/low extrema midpoint, window includes current bar. D2 explicit periods/displacement, no defaults. D3 observed/displayed header pairs, lagging only as observed value plus reference close. D4 windows inside `[a, t]`, never shortened. D5 span A from exact midpoints. D6 EMA centre, Wilder ATR, rational multiplier. D7 Keltner and squeeze consume unrounded R17 recurrence values. D8 Donchian window includes current bar. D9 classic pivots (P, R1, S1, R2, S2) from the immediately preceding governed session's exact bars. D10 percentile: exact squared-width rank, target excluded, mid-rank ties, fraction. D11 width is the R17 Bollinger-style population-variance width. D12 squeeze as signed gaps plus inclusive relation, no thresholds. D13 float64 outputs. D14 six producers; pivots without a preceding session are `missing_input/absent_input`. D15 R17 status/reason precedence inherited unchanged.

## Open questions

- O1 (#483 EQ-149 stochastic): declared prerequisite, no operand consumed. If stochastic freezes extrema headers `<EQ-149 high/low extrema header OPEN>`, confirm the same inclusive-window convention and shared kernel; no redefinition here.
- O2 (#489 EQ-155 ranks): if the robust-rank kernel is later consumed, its tie/population convention must match D10 or a ruling replaces D10; sequencing after EF3 then applies.
- O3: R17 `high_extrema`/`low_extrema`/`price_moments` operands end at the target; Ichimoku displayed spans and the percentile need windows ending at earlier slots. Needs a no-behavior-change generalization (window end offset) of the preparation, outside this docs-only task.
- O4: pivots from bars (D9) versus selected #506 calendar-period operands; and whether EF2 also needs a daily-grid context (one slot per session) for conventional daily Ichimoku/pivots. The mathematics is slot-count based and unchanged.
- O5: who supplies timestamps for displayed positions beyond the grid (a caller calendar), if any.
- O6: relation to the retracement companion (#511 addendum) and its extrema window; not defined here.
- O7: evidence witness policy (extremum slot identity, truncation order) beyond R17's slot-ordered truncation.
- O8: classification of a missing preceding session (`absent_input` proposed) versus a warm-up classification.
- O9: whether `channel.keltner.middle` duplicating `intraday.ema` is wanted as a header.
- O10: whether the bool `bollinger_inside_keltner` counts as policy (this document says no: pure inclusive arithmetic) or should be left to #518.
- O11: ConfigSpec identity and packaging route for `ef2.*` producers (EF1 required an additive producer-set amendment).
- O12: minimum population policy (full population required here) and whether an optional smaller minimum is ever admitted.

## What was not verified

Nothing was run against the library or any installed package; R17 behavior is taken from reading source and documentation (including the assumption that a later-known row yields only its knowledge reason, and that contradictory OHLC is refused with a BAR validation code). Fixtures were not expanded into canonical packets. The Decimal120 recurrences of R17 versus the exact-rational oracle differ below float64 resolution; no fixture sits within that margin of a rounding midpoint, but this was not machine-checked. No independent review of this proposal has occurred.
