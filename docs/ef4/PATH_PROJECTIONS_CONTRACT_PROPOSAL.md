# EF4 remaining equity statistical projections contract - proposal (contract I2)

Prepared for EQ-172 [#513](https://github.com/atulsrivas1/equity-features/issues/513) (complete remaining equity statistical projections), including the October 21 reviewed relative-excess ownership clarification and the proposed raw-return, share-volume-rate and rate-difference profiles recorded on that issue, for consumption by EF4 I/O [#613](https://github.com/atulsrivas1/equity-features/issues/613), worker [#614](https://github.com/atulsrivas1/equity-features/issues/614) and release acceptance EQ-163 [#497](https://github.com/atulsrivas1/equity-features/issues/497). It is the second half of contract I; EQ-161 [#495](https://github.com/atulsrivas1/equity-features/issues/495) (path efficiency and choppiness) is the sibling [PATH_EFFICIENCY_CONTRACT_PROPOSAL.md](PATH_EFFICIENCY_CONTRACT_PROPOSAL.md). **This is a contract proposal, not accepted by any review; every convention below is a coordinator decision (final sections), pending owner review, and the contract carries a coordinator freeze statement.** It is contract preparation only: it admits no Ready state, implementation, numerical acceptance, release or performance claim.

Companion data: [PATH_PROJECTIONS_CONTRACT_PROPOSAL.json](PATH_PROJECTIONS_CONTRACT_PROPOSAL.json) holds the machine-readable producers, headers, roles, reference fact schemas, mathematics, quality table, 21 session-projection, 19 bar-projection, 27 relative-excess, 10 core-benchmark and 30 rate-projection result fixtures (107 fixtures, 332 expected outputs) and 114 typed-refusal fixtures. Expected values are hand-derived: each headline value is written by hand in the fixture definition and asserted equal to a plain `fractions.Fraction` reference computed by a scratch script that imports only the Python standard library and nothing from the equity packages. A second, independent standard-library harness recomputes every fixture output (status, reasons, counts, value, float64, `float.hex`, acceptance, witnesses) and every refusal (the recorded mutation of its base fixture, through an independent admission model) from the JSON inputs alone; all fixtures and refusals match. No logarithm or square root occurs in this contract, so no decimal reference is needed. The library was not imported, run or tested. Fixtures use compact notation (not canonical wire) and need expansion into canonical packets.

## Why two files and why four producers

EQ-172 is a bundle: the issue lists up-session fractions, core-benchmark agreement/dispersion, scalar SMA/relative momentum comparisons, dollar-volume/up-volume projections, drawdown/distance and trailing trade/notional rate projections, and its clarifications add six relative excess outputs and a raw-return, share-volume-rate and rate-difference group. Together with EQ-161 that is too large for one clean contract, so contract I is split into I1 (path efficiency) and I2 (this file). Inside I2 the work falls into four producers with different operands, populations and failure modes (daily closes; epoch bars; paired price witnesses; window aggregates and witnesses). They have separate identities, parameters, roles and independent readiness and share only conventions (quality, units, numeric policy, the reference fact grammar).

| Issue item | Where it lands (decision DP-J1) |
| --- | --- |
| up-session fractions | `session_projection`: `projection.up_session_fraction`, `projection.down_session_fraction` |
| drawdown/distance | `session_projection`: drawdown, max drawdown, distance from low |
| scalar SMA comparison | `session_projection`: `projection.close_vs_sma_fraction`, `projection.close_above_sma` |
| relative momentum comparison | no new output: completed-history spreads are the accepted `relative.market_return`/`relative.sector_return` (DP-J5); current-endpoint and rolling spreads are the six excess outputs |
| dollar-volume/up-volume projections | `bar_projection`: up/down volume and dollar volume and fractions; the total is the accepted `session.bar.notional` |
| core-benchmark agreement/dispersion | `relative_excess`: `core.benchmark_direction_agreement_fraction`, `core.benchmark_return_dispersion_fraction` |
| six excess outputs (Oct 21 clarification) | `relative_excess`: primary/secondary/sector x prior-close/rolling-window |
| trailing trade/notional rates, share-volume rate, raw return, rate difference | `rate_projection` |

## Authority and inspected sources

Read-only inputs: the issues EQ-172 and EQ-161 as published (including both ownership clarifications); `docs/features/EF1_ANCHORS.md` and `EF1_PERIOD_PHASE.md` and `SESSION_FORMULAS.md` (actual traded notional, never close*volume; checked int64 volume; decimal128 notional coefficient; readiness per field), `HISTORICAL_FORMULAS.md` and `CONTEXT_FORMULAS.md` (positive scaled closes, SMA, equality is not above, `relative.market_return` arithmetic spread, the 100->110 and 200->210 worked example), `INTRADAY_FOUNDATIONS.md`, `docs/EQUITY_DELIVERY_REPLAN.md` (EF4: retain the whole EQ172 projection scope and its actual EQ155/EQ158 operands), `docs/plans/equity-output-ownership.json` (the six excess outputs, the preserved EQ-153 beta/residual owner, EQ-171 technical velocity/acceleration units), `docs/ef1/audit/` records on #513, the merged EF2 and EF3 contracts (structure, fixture rigor, reason precedence, partial-population rule, reference fact grammar `x1:B(id)`), and the shared validators and enums in `packages/contracts` (`validation.py`, `errors.py`). Contracts G (tape: EQ-158 trade windows, EQ-162 notional top-K) and H (quote/VWAP) belong to other authors; this contract depends on G only by documented operand names (tape count, volume and notional of an exact window) and on H not at all.

## Unchanged boundary

Existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult`, `Status`, `Reason`, `ErrorCode` and scalar `ValueType` values (`int64`, `float64`, `bool`, `decimal128` as already used by the accepted EF1 notional outputs); the shared BAR, DAILY and REFERENCE validators; the R17 grid, admission, reset epoch and modes; the frozen ef1-contract1 and every accepted core, R17, EF1, EF2 and EF3 header. `relative.market_return`, `relative.sector_return`, `relative.beta`, `relative.residual_return`, `history.sma`, `session.bar.notional`, `breadth.session.*` (EQ-220), `technical.*` (EQ-171) keep their definitions and ids (explicit no-change reuse decisions DP-J4, DP-J5, DP-J7). No new DataKind, DTO, result codec, scheduler or default, no new error code, no new validator and no change to a shared validator. This packet is additive: four producers, 26 new headers, six new reference fact kinds and three new unit strings. Update, restore and merge are unsupported (`UNSUPPORTED_CAPABILITY`); batch and full replay only.

## Producers and config identities

| Item | Session projection | Bar projection | Relative excess | Rate projection |
| --- | --- | --- | --- | --- |
| Identity | `ef4.session_projection` | `ef4.bar_projection` | `ef4.relative_excess` | `ef4.rate_projection` |
| Algorithm / schema | `ef4-session-projection-v1` / `1` | `ef4-bar-projection-v1` / `1` | `ef4-relative-excess-v1` / `1` | `ef4-rate-projection-v1` / `1` |
| Policy label | `ef4-proj1` | `ef4-proj1` | `ef4-rel1` | `ef4-rate1` |
| Parameters (no defaults) | `policy_version`, `window` N (1..4096), `evidence_limit` | `policy_version`, `evidence_limit` | `policy_version`, `primary_/secondary_/sector_benchmark_id` (exactly when that role is selected), `alignment_tolerance_ns`, `max_endpoint_age_ns`, `window_ns` (exactly when a window profile is used), `core_benchmark_ids` (2..16) and `core_profile` (exactly when a core output is selected), `evidence_limit` | `policy_version`, `window_ns`, `max_endpoint_age_ns`, `alignment_tolerance_ns` (exactly when raw return or rate difference is selected), `adjacency` (`adjacent`, `disjoint`; exactly when rate difference is selected), `evidence_limit` |
| Roles | `daily` | `bars` | `legs`, `membership` | `tape`, `legs` |
| ConfigSpec | PriceUnit mandatory; adjustment declared once and shared by every role | same | same | same |

A policy label names the whole convention set of its version. An unsupported label is `INCOMPATIBLE_VERSION`; a future convention needs a new label, never a silent change. Parameters that apply to only some outputs are present exactly when those outputs are selected: a missing or extra parameter is `INVALID_CONFIG` (no fabricated default for any tolerance, age, window, adjacency or benchmark id).

## Outputs and headers

| Feature id | dtype | unit | Producer | Available when |
| --- | --- | --- | --- | --- |
| `projection.up_session_fraction` | float64 | fraction | session | closes t-N..t READY |
| `projection.down_session_fraction` | float64 | fraction | session | closes t-N..t READY |
| `projection.drawdown_fraction` | float64 | fraction | session | closes t-N+1..t READY |
| `projection.max_drawdown_fraction` | float64 | fraction | session | closes t-N+1..t READY |
| `projection.distance_from_low_fraction` | float64 | fraction | session | closes t-N+1..t READY |
| `projection.close_vs_sma_fraction` | float64 | fraction | session | closes t-N+1..t READY |
| `projection.close_above_sma` | bool | boolean | session | closes t-N+1..t READY |
| `projection.up_volume` | int64 | shares | bar | every epoch bar READY with volume |
| `projection.down_volume` | int64 | shares | bar | same |
| `projection.up_volume_fraction` | float64 | fraction | bar | same, total volume > 0 |
| `projection.up_dollar_volume` | decimal128 | currency | bar | every bar READY and actual notional on every positive-volume bar |
| `projection.down_dollar_volume` | decimal128 | currency | bar | same |
| `projection.up_dollar_volume_fraction` | float64 | fraction | bar | same, total notional > 0 |
| `relative.session.primary.prior_close_excess_fraction` | float64 | fraction | relative | instrument and primary prior_close legs READY and compatible |
| `relative.session.primary.window_excess_fraction` | float64 | fraction | relative | instrument and primary window_start legs READY, matched window |
| `relative.session.secondary.prior_close_excess_fraction` | float64 | fraction | relative | as primary, secondary benchmark |
| `relative.session.secondary.window_excess_fraction` | float64 | fraction | relative | as primary window, secondary benchmark |
| `relative.session.sector.prior_close_excess_fraction` | float64 | fraction | relative | as primary, sector benchmark and causal membership |
| `relative.session.sector.window_excess_fraction` | float64 | fraction | relative | as primary window, sector benchmark and causal membership |
| `core.benchmark_direction_agreement_fraction` | float64 | fraction | relative | every declared core benchmark leg READY and compatible |
| `core.benchmark_return_dispersion_fraction` | float64 | fraction | relative | same |
| `rate.window.trade_rate` | float64 | trades_per_second | rate | count operand READY on an exact declared window |
| `rate.window.notional_rate` | float64 | currency_per_second | rate | notional operand READY on an exact declared window |
| `rate.window.share_volume_rate` | float64 | shares/s | rate | volume operand READY on an exact declared window |
| `rate.window.raw_return_fraction` | float64 | fraction | rate | window_start and end witnesses READY, matched window |
| `rate.window.return_rate_difference` | float64 | fraction_per_second | rate | window A and window B witnesses READY, matched, ordered |

Order: lexicographic by feature id within a producer. The six excess ids are the draft names of the EQ-172 clarification (`relative.session.<benchmark_role>.prior_close_excess_fraction` and `.window_excess_fraction`); the other ids are proposed and unaccepted until the owner review. The `decimal128` currency outputs publish the exact integer coefficient at the PriceUnit scale (as the accepted `session.bar.notional`). Each output has its own required operands, expected and observed counts and independent readiness: a sector gap never blocks a market comparison (RX07), a missing actual notional never blocks the volume outputs (BP06, BP07), a missing count never blocks the notional or volume rate (RP07), missing window-B facts never block the raw return (they only block the rate difference).

## Inputs and roles

| Role | Kind | Content |
| --- | --- | --- |
| `daily` | BAR | close-only BAR on the daily governed grid in the R17 context (one slot per governed session, coverage per slot, target slot, cutoff, K); one instrument; positive scaled closes |
| `bars` | BAR | R17 chunked BAR delivery for the reset epoch of the target session: OHLC, volume and optionally `actual_notional`; positive-volume bars carry positive coherent OHLC with `low*volume <= actual_notional <= high*volume`; zero-volume proven-empty bars carry null OHLC and zero or absent notional |
| `legs` | REFERENCE | `ef4.leg.start` and `ef4.leg.end` facts: exact price witnesses with time, session, profile, revision and action snapshot |
| `membership` | REFERENCE | one `ef4.sector.membership` fact for the target instrument (sector outputs only) |
| `tape` | REFERENCE | `ef4.tape.count`, `ef4.tape.volume`, `ef4.tape.notional` facts: independently ready window aggregates of contract G |

Fact schemas are in the JSON `reference_fact_schemas`. Summary: `ef4.leg.start`/`ef4.leg.end` carry the leg owner as `instrument_id`, the witness session as `session_id`, `reference_id` `x1:B(...)`, the actual witness time in `effective_start_ns`, a positive int64 coefficient in `price`, and a `text` grammar `profile=<prior_close|window_start|regular_open>;slot=<A|B>;rev=<id>;act=<id>` (start) or `slot=...;rev=...;act=...` (end), where `rev` is the original record revision (evidence only) and `act` is the instrument's independently retained corporate-action snapshot id. `ef4.sector.membership` binds the target instrument to the sector benchmark instrument id in `text` (never derived from a sector name) with `effective_start_ns` the effective-from time. The tape facts carry the window bounds in `effective_start_ns`/`effective_end_ns` and the value as a canonical non-negative decimal integer in `text` (the shared validator rejects `factor_num <= 0`, so a zero count cannot ride there; counts and volume <= 2^63-1, notional < 10^38). The tape carrier is provisional because contract G has not merged (OQ-J2): a different carrier changes the I/O mapping, not the mathematics. Rows inside one (instrument, session) group must be ordered by `(effective_start_ns, reference_id)` as the shared validator requires; `require_compatible_inputs` applies only among the market roles (`daily`, `bars`).

Value basis: closes, opens, highs, lows and leg prices are positive int64 coefficients at the PriceUnit scale; volumes and counts are int64; notional is a decimal128 coefficient. All arithmetic is exact; share-volume sums that are published as int64 are checked (`OVERFLOW`), denominators use wide exact integers; division by `10^scale` or by seconds happens only at publication.

## Exact mathematics

### Session projection (ef4-proj1)

Closes C_i on the daily governed grid, target t, window N. Up fraction `= #{i in t-N+1..t : C_i > C_(i-1)} / N` and down fraction likewise with `<`: strict, a tie is in neither (SP01: up 1/2, down 1/4, one tie; SP04 all zero). Both need the N+1 closes t-N..t. Over the N closes `w = C_(t-N+1)..C_t` with maximum M, minimum m and sum S:

- `drawdown_fraction = (M - C_t) / M`; `max_drawdown_fraction` = the largest `(R_i - C_i)/R_i` with R_i the running maximum of w (the peak-to-trough decline inside the window; SP05: 1/2 against a current drawdown of 1/4); `distance_from_low_fraction = (C_t - m) / m` (DP-J3). The peak and trough are the window's own: there is no all-time or anchored peak, so a deep drop older than the window is irrelevant (SP20).
- `close_vs_sma_fraction = C_t / (S/N) - 1 = N*C_t/S - 1` and `close_above_sma = (N*C_t > S)`, strict; equality is not above (SP04, SP05, SP15). The SMA is computed here with exactly the arithmetic of the accepted `history.sma` but as this producer's own computation, without a result edge (DP-J4, the EF3 mean-companion precedent).

Prices are positive so every denominator is positive: `zero_denominator` is unreachable for this producer.

### Bar projection (ef4-proj1)

Bars i = 0..t of the reset epoch, volume V_i, actual notional A_i (0 for a proven-empty bar). A positive-volume bar is **up** if close > open, **down** if close < open, flat otherwise (DP-J6): the rule needs no predecessor, includes the first bar, and is not OBV. `up_volume = sum V_i over up bars` (int64 shares), `down_volume` likewise; `up_volume_fraction = up_volume / sum of all V_i`; `up_dollar_volume = sum A_i over up bars`, `down_dollar_volume` likewise (decimal128 coefficient; currency = coefficient/10^scale); `up_dollar_volume_fraction = up_dollar_volume / sum of all A_i`. A flat bar contributes to the totals only (BP01). Zero total volume or notional makes only the fraction `not_applicable`/`zero_denominator`; the sums are available zeros (BP05). Dollar volume is **actual notional only**, never `close*volume` (EF1 rule, DP-J7); the epoch total is `session.bar.notional` and is not duplicated. The population is every epoch bar through the target, all READY (strict; a one-bar epoch is valid, BP14).

### Relative excess (ef4-rel1)

A leg has a start price S and an end price E, so `r = E/S - 1` exactly (the library derives it; a pre-rounded float return is never accepted, DP-J9). `excess(role, profile) = r_instrument - r_benchmark`, an arithmetic spread published as a fraction (RX01: 1/10 - 1/20 = 1/20; the existing relative spread is `r_symbol - r_market`, not `(1+r)/(1+b) - 1`). A prior-close return and a rolling-window return are different profiles with different start facts and one shared end fact per instrument (DP-J10). All of these must hold, otherwise the output is unavailable with the stated reason (DP-J11):

1. Both legs' start and end facts and, for sector, the membership fact are present (`absent_input`), `known_at` non-null (`unknown_availability`) and `<= K` (`future_knowledge`).
2. End times `<= C`; an endpoint after the cutoff is `future_market` and is never replaced by an earlier known row (RX12, RX13).
3. `|end_instrument - end_benchmark| <= alignment_tolerance_ns` and `C - end <= max_endpoint_age_ns` for each end (RX11, RX20).
4. Per leg `act` of the start equals `act` of the end (RX16).
5. Profile `prior_close`: the start fact's session differs from the end fact's session and is the same session for instrument and benchmark (RX14). Profile `window_start`: start and end share one session for both legs; `|(end - start) - window_ns| <= alignment_tolerance_ns` for each leg; `|start_instrument - start_benchmark| <= alignment_tolerance_ns` (RX09, RX10). A leg that only has a `regular_open` start has no `prior_close` fact: `absent_input` (RX15).
6. Sector: the membership fact binds the instrument to the configured `sector_benchmark_id` (never inferred from a sector string, RX24) and is effective at or before the instrument end (RX23); missing sector membership blocks only sector outputs (RX07).

Failures of 3 to 6 are `ineligible` (`missing_input`): present but incompatible witnesses are never relabelled. Self-benchmark (a benchmark id equal to the instrument) and two roles bound to one instrument are refused (`INCONSISTENT_IDENTITY`). Beta, correlation and residual stay with EQ-153; nothing here consumes them. The record revision is retained as evidence and not compared (DP-J13).

**Core benchmark agreement and dispersion (DP-J14).** For K = 2..16 declared core benchmarks with the same profile and the same per-leg eligibility, returns r_k: `direction_agreement = max(#{r>0}, #{r<0}, #{r=0}) / K` (zero is its own class; CB03: 2 up and 2 down give 1/2; CB04: two zeros give 2/3) and `return_dispersion = max r_k - min r_k` (an exact range; no square root, and a standard deviation over a handful of benchmarks would be unstable and inexact). A benchmark leg that is not eligible for any reason makes the population partial: `incomplete_coverage`/`partial_universe`, observed < expected, both values withheld (CB05, CB08, CB09, CB10); among eligible members the end times (and, for `window_start`, the start times) must agree within the tolerance and share sessions, else `ineligible` (CB06).

### Rate projection (ef4-rate1)

Tape outputs consume an exact window `[s, e)` with `e - s = window_ns`, `e <= C` and `C - e <= max_endpoint_age_ns` (otherwise `ineligible`, `future_market` for `e > C`): `trade_rate = count / (window_ns/1e9)`, `share_volume_rate = volume / (window_ns/1e9)`, `notional_rate = (notional/10^scale) / (window_ns/1e9)` (RP01 to RP06). The denominator is the declared window duration, never the span of observed events (DP-J15). An observed zero is an available `+0.0` (RP02); an absent operand is `absent_input`, never zero (RP07). The operands are consumed by documented name only; this contract does not define trade windows, eligibility, signs, ties or notional ranking (contract G).

`raw_return_fraction` is `E/S - 1` from the slot A `window_start` and end witnesses of the declared window (same session, same `act`, `|(end - start) - window_ns| <= alignment_tolerance_ns`, `end <= C`, `C - end <= max_endpoint_age_ns`). It is the raw sampled endpoint return, distinct from the EF5 `technical.session_return_fraction` (session open to endpoint) and the EF1 `session.open_to_endpoint_return_fraction` (DP-J16). A start in the prior session fails the reset rule (RP17).

`return_rate_difference = (r_A - r_B) / (window_ns/1e9)`, i.e. `rate_A - rate_B` with `rate_X = r_X / (window_ns/1e9)`, for two windows of the same declared duration: A is the later window; the age bound applies to A only; `adjacency = adjacent` requires `|start_A - end_B| <= alignment_tolerance_ns`, `disjoint` requires `end_B - start_A <= alignment_tolerance_ns` (B entirely before A, any gap) (RP20 to RP24). The value has the dimension of a rate (`fraction_per_second`); it is not divided by the time between windows. It is a difference of rates, not a second time derivative, and EQ-171 #512 keeps the technical acceleration dimensions unchanged.

## Pinned edge cases

- **Short closure:** up/down need N+1 closes and the other session projections N, so with exactly N closes only the latter are available while up/down are `insufficient_history` (SP07: expected 4, observed 3).
- **Gap at the base slot only:** up/down `governed_gap`, the rest available (SP08).
- **Empty bar:** in the bar projection a proven-empty bar is a READY observation contributing 0 (BP04), unlike the path contract where a price is required.
- **Missing notional:** one positive-volume bar without `actual_notional` blocks the dollar outputs only (BP06); an absent column does the same with `absent_input` (BP07).
- **Wide values:** 2^63+5 actual notional (decimal128, BP18), closes 2^62+-1 whose window sum exceeds int64 (SP16), prices 2^62 and 2^61 (RX25), volume 2^62 over 60 s (RP12).
- **Age on window B:** the max-age bound is checked on the later window only (RP20 would otherwise fail).
- **Future and unknown:** a known_at of 150 against K = 100 is `future_knowledge` (SP11, BP11, RX17, RP11, RP28); `known_at == K` is known (SP12, BP12, RX18); null is `unknown_availability` (SP13, BP13, RX19, RX26).

## Availability, coverage, quality, evidence and refusals

Typed refusal precedes assessment. Quality uses existing `Status`/`Reason` only, with the merged robust-pace precedence (DP-J18): `absent_input`, `unknown_availability`, `future_knowledge`, `null_field`, `ineligible` (all `missing_input`), `governed_gap`, `future_market`, `partial_universe` (all `incomplete_coverage`), `insufficient_history`, `no_eligible_observations`, `empty_universe`, `zero_denominator` (the last three `not_applicable`), else `available`. All applicable reasons are retained in lexical order; the status follows the first applicable reason; a value is null exactly when the status is not available; `available` implies `observed == expected`. `no_eligible_observations` and `empty_universe` are unreachable here by design. Knowledge is enforced identically in `known_at` and reconstruction modes with original `known_at`.

Counts: session projection expected = closure size (N+1 or N), observed READY slots among the existing closure slots; bar projection expected `t+1`, observed READY bars for the output's fields; relative excess expected 4 facts (5 with membership), observed present and known facts (compatibility failures leave observed unchanged); core expected K, observed eligible benchmarks; tape rate expected 1, raw return 2, rate difference 4.

Evidence (available outputs only): the limit is the existing `evidence_limit` 0..10000, result-wide as `FeatureResult` bounds it; fixtures list per-output witnesses when selected alone. Order: session and bar projections target first then the other rows ascending (`slot:<i>`, `bar:<i>`); relative excess instrument start, instrument end, benchmark start, benchmark end, then `membership:<instrument>` (core: per benchmark in declaration order, start then end); rate projection `tape:<kind>` or `leg:<instrument>:start|end:<slot>`. Boundary `completed_interval`.

Refusals (no `FeatureResult`) SPR01 to SPR22, BPR01 to BPR24, RXR01 to RXR37 and RPR01 to RPR31 in the JSON (114), each with its base fixture and the exact mutation (the construction recipe) and whether a shared validator or the library raises it: duplicate and overlapping rows `DUPLICATE`/`INVALID_ORDER`; bar beyond the cutoff, negative volume, start >= end, tape window with start >= end `BOUNDS`; incoherent OHLC, notional outside `[low*volume, high*volume]`, zero-volume bar with prices or notional, zero or float prices, empty ids, unknown profile/slot/kind labels, non-canonical tape text `INVALID_SCHEMA`; int64 or decimal128 excess and published volume sums above int64 `OVERFLOW`; target outside the roles, self-benchmark, two roles on one instrument, undeclared instrument, a second instrument `INCONSISTENT_IDENTITY`; duplicate legs, memberships or tape kinds `DUPLICATE`; missing, extra or out-of-range parameters, core id list size, adjacency vocabulary `INVALID_CONFIG`; unsupported label `INCOMPATIBLE_VERSION`; unit, currency `INVALID_UNIT`; adjustment `UNSUPPORTED_ADJUSTMENT`; unknown feature `UNKNOWN_FEATURE`; update, restore, merge `UNSUPPORTED_CAPABILITY`. Every code was checked against `errors.py` and `validation.py`; no new code or validator change is needed.

## Numeric policy and acceptance

Exact integer/rational arithmetic throughout, one correctly rounded float64 per published value, compatible with the R17 Decimal120 policy and its error contract (DP-J20). Acceptance rule per fixture output (field `acceptance` in the JSON):

- `exact_float64`: dyadic rational, numerator below 2^53; bit for bit (35 outputs).
- `exact_plus_zero`: exactly 0 from exact arithmetic; bit-exact `+0.0`, never `-0.0` (47 outputs).
- `tolerance`: `abs(y - r) <= max(8 ulp(r), 1e-12 |r|)` with r the fixture float64, the R17 numeric error contract (`docs/api/INTRADAY.md`) (72 outputs, non-dyadic rationals such as 1/20, 7/22, 365/5304).
- `exact_integer`: `int64` and `decimal128` outputs, the latter as the coefficient at the PriceUnit scale (44 outputs).
- `exact_bool`: `projection.close_above_sma` (14 outputs).

Total 212 classified outputs among the available ones; no documented exceptions. Measurement of cost is not part of this contract.

## Layer responsibilities

- **Library (#513).** Admission of the supplied rows, facts and context, closure and eligibility per output, exact sums, returns, ratios and rates, quality, evidence and every library refusal; pure and deterministic with exact rational intermediates and one final rounding; one shared closure preparation per producer reused across its outputs without coupling their readiness.
- **EF4 I/O #613.** Maps ordered closes and bars, leg witnesses with original `known_at`, revision and action snapshot, memberships and tape-window operands exactly as supplied, including the explicit start/reference identity, endpoint identity and time, requested interval and phase and cutoff; maps results (int64, decimal128, bool, hex-exact float64, status, reasons, counts, witnesses) to the sink conversion; never derives a return, chooses a benchmark or window, infers a benchmark from a sector string, fills, bridges or replaces an unknown endpoint with an earlier known row, converts scale or currency, or computes a rate.
- **Worker #614.** Routes each selected output to its own operands only, shares bounded closures and facts, keeps independent readiness, executes one config per complete result, binds inputs and the config digest and persists the library result unchanged. Direct, adapter, worker and stored results must be identical, including refusal class.

## Fixtures

107 result fixtures and 114 refusal fixtures: session projection SP01 to SP21, bar projection BP01 to BP19, relative excess RX01 to RX27, core benchmarks CB01 to CB10, rate projection RP01 to RP30. The JSON `coverage_map` indexes them by tag, `reasons_reached` by reason and `prefix_equivalences` lists identical-result pairs. Coverage: monotone, flat, tie, equality and negative cases (SP02 to SP05, SP15); max versus current drawdown and window scope (SP05, SP20); boundary and independent closures (SP07, SP08); up/down/flat volume, empty bars, all-empty and single-bar epochs (BP01, BP04, BP05, BP14, BP15); missing notional and absent column (BP06, BP07); all six excess outputs from one fact set (RX06) and each profile (RX01 to RX05); mismatched window, misaligned start or end, future endpoint, phase, action snapshot, stale endpoint, sector-only gap, membership, self-benchmark (RX07 to RX24, RXR15); agreement ties and zero class, partial population (CB01 to CB10); tape rates with observed zero, duration and age mismatch, independent operands (RP01 to RP12); raw return and reset (RP13 to RP19); rate difference adjacency, overlap, gap, negative, equal (RP20 to RP28); every reason reachable here appears at least once (`absent_input`, `unknown_availability`, `future_knowledge`, `null_field`, `ineligible`, `governed_gap`, `future_market`, `partial_universe`, `insufficient_history`, `zero_denominator`).

Fixture notation, including how a null, empty, gap, absent, future and unknown slot is constructed and how refusal mutations are written, is in the JSON `fixture_notation`. Prefix property: every output at target t depends only on rows and facts at or before t (and the cutoff), so appended later rows or facts change nothing (SP17, BP16). Required readback: a stored `int64`/`decimal128` is never converted through float, and every stored float64 equals the float64 of the exact rational.

## Explicit non-goals

No acquisition of prices, trades, memberships, benchmarks or calendars; no default window, tolerance, age, adjacency or benchmark; no relative momentum output (completed-history spreads stay `relative.market_return`/`relative.sector_return`), no beta/correlation/residual; no breadth or cohort construction (`ef3.session_breadth` keeps `breadth.session.up_volume` etc.; the up volume here is a single-instrument epoch projection); no quote, spread or VWAP operand and no redefinition of trade windows, signs or notional top-K (contracts G and H); no technical return/velocity/acceleration (EQ-171 #512); no percentile or rank of a projection over history or cohort and no EQ-155 result consumed in v1 (OQ-J3); no scanners, thresholds or catalogue policy (EF8); no update, restore or merge; no new DataKind, DTO, codec, scheduler, validator or error code; no performance, parity, release or publication claim; no private-source equivalence or source formula.

## Coordinator decisions: conventions (accepted as proposed, pending owner review)

| Id | Convention (alternatives in the JSON) |
| --- | --- |
| DP-J1 | Scope map: four producers, one story; sibling file for EQ-161. |
| DP-J2 | Up/down session fractions: strict, ties in neither, denominator N. |
| DP-J3 | Drawdown, max drawdown and distance from low on the N-close window, closes only. |
| DP-J4 | Scalar SMA comparison computed here (history.sma arithmetic), strict above, no result edge. |
| DP-J5 | No relative-momentum output; reuse `relative.market_return`/`relative.sector_return` for completed-history spreads. |
| DP-J6 | Bar direction by close versus open; flat in denominators only; empty bars contribute 0. |
| DP-J7 | Dollar volume is actual notional only; total is `session.bar.notional`. |
| DP-J8 | Bar projection is epoch-to-date, strict, no window. |
| DP-J9 | Excess = arithmetic spread of exact simple returns, a fraction. |
| DP-J10 | Profile-labelled start facts, one shared end fact; regular_open accepted but unconsumed. |
| DP-J11 | Explicit alignment and age parameters; `ineligible`, `future_market`; no earlier-row substitution. |
| DP-J12 | Sector benchmark bound by config id and causal membership; sector gap isolated; roles distinct. |
| DP-J13 | Per-instrument action snapshot must match across a leg; revision retained as evidence. |
| DP-J14 | Core agreement = largest direction class / K; dispersion = range; partial population withheld. |
| DP-J15 | Rates divide by the declared window; tape operands by documented name only. |
| DP-J16 | Raw return and rate difference definitions; adjacency parameter; not an acceleration. |
| DP-J17 | Reset: a window never spans sessions; no carry. |
| DP-J18 | Reason precedence of the merged EF3 robust-pace contract. |
| DP-J19 | Units; three new strings. |
| DP-J20 | Exact arithmetic, one rounding, no logarithm or root. |
| DP-J21 | Dependencies: G by operand names, H none, EQ-166/167/168/153 as mapped facts, EQ-155 retained edge without a consumed result. |
| DP-J22 | Batch and full replay only. |

## Coordinator rulings on the open questions (pending owner review)

| Id | Ruling |
| --- | --- |
| OQ-J1 | `fraction_per_second` uses the spelling already planned by EQ-171; whichever amendment merges first registers it. |
| OQ-J2 | The three `ef4.tape.*` fact kinds are a provisional carrier for contract G operands; a different G carrier changes only the I/O mapping. |
| OQ-J3 | (conservative) no I2 output consumes a robust-history (EQ-155) result in v1; the dependency stays as allocated and a rank or median of a projection over history is composed through `ef3.robust_history` with a supplied series. The owner may drop or re-route the edge. |
| OQ-J4 | Beta-residual and relative-momentum owners unchanged; no new momentum-gap output. |
| OQ-J5 | All comparison outputs are fractions; percent display is a consumer or sink presentation. |
| OQ-J6 | Hosted in `packages/features` (EF4 module, config namespace `ef4.*`, separate catalog); no package version bump. |
| OQ-J7 | (conservative) drawdown on closes only in v1; a high/low drawdown needs a new policy label. |

## Header ledger and amendment (to be applied)

The 26 headers of this contract are to be applied by a sibling amendment document after the freeze. Units `fraction`, `shares`, `shares/s`, `currency` and `boolean` exist; `trades_per_second`, `currency_per_second` and `fraction_per_second` are new to the ledger. Six reference fact kinds (`ef4.leg.start`, `ef4.leg.end`, `ef4.sector.membership`, `ef4.tape.count`, `ef4.tape.volume`, `ef4.tape.notional`) and their role schemas are recorded in the JSON. No change to shared validators is required or proposed.

## Coordinator freeze

Frozen as `ef4-proj1`, `ef4-rel1` and `ef4-rate1` (v1) for implementation once this PR merges (coordinator statement; no review or acceptance claim by the author). There are no defaults for windows, tolerances, ages, adjacency or benchmark ids. Any change to a convention, label semantics, header, role, fact schema or fixture after merge requires a new policy label and an amendment document.
