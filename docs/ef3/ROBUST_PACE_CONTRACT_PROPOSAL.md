# EF3 robust history, robust volume pace and mean-ratio companion contract - proposal

Prepared for EQ-155 [#489](https://github.com/atulsrivas1/equity-features/issues/489) (robust historical summaries and ranks), EQ-156 [#490](https://github.com/atulsrivas1/equity-features/issues/490) (robust volume pace and anomaly normalization) and EQ-241 [#666](https://github.com/atulsrivas1/equity-features/issues/666) (mean-ratio volume pace companion, draft W3D-4), for consumption by EF3 I/O [#611](https://github.com/atulsrivas1/equity-features/issues/611), worker [#612](https://github.com/atulsrivas1/equity-features/issues/612) and release acceptance EQ-157 [#491](https://github.com/atulsrivas1/equity-features/issues/491). **This is a contract proposal, not accepted by any review; all former DECISION-PROPOSED conventions and OPEN questions are now coordinator decisions (final sections), pending owner review, and the contract carries a coordinator freeze statement.** It is contract preparation only: it admits no Ready state, implementation, numerical acceptance, release or performance claim. The conventions (DP-*) were accepted as proposed and the former open questions (OQ-*) are ruled in the final sections.

Companion data: [ROBUST_PACE_CONTRACT_PROPOSAL.json](ROBUST_PACE_CONTRACT_PROPOSAL.json) holds the machine-readable producers, headers, roles, fact schemas, mathematics, quality table, 43 history, 23 cohort, 34 pace and 19 mean-ratio result fixtures and 45 typed-refusal fixtures. Expected values are hand-derived: each headline value is written by hand in the fixture definition and asserted equal to a plain `fractions.Fraction` reference computed by a scratch script that imports only the Python standard library and nothing from the equity packages. Float64 results carry the exact rational, `float.hex` and a per-output acceptance rule. The library was not imported, run or tested. Fixtures use compact notation (not canonical wire) and need expansion into canonical packets.

## Authority and inspected sources

Read-only inputs: the accepted foundations `docs/features/INTRADAY_FOUNDATIONS.md`, `HISTORICAL_FORMULAS.md` and `CONTEXT_FORMULAS.md`, `docs/api/DAILY_VOLUME.md`, `INTERVAL_VOLUME.md` and `HISTORY.md`, `docs/releases/R17/*`, the frozen shared boundary `docs/ef1/CONTRACT.json`, the three merged EF2 contracts under `docs/ef2/` (structure, fixture rigor, numeric policy, reason precedence, band-width percentile mid-rank precedent) and `docs/ef2/PRODUCER_SET_AMENDMENT.md`, the audit records `docs/ef1/audit/EQ164_SELECTED_B.md`, `EQ164_WAVE2_DECISIONS.md`, `EQ164_WAVE3_DECISIONS.md` and the draft `PROPOSED_STORIES.md` (W3D-4), the baseline dispositions `docs/plans/equity-baseline-reuse-source-dispositions.json` (no closed baseline reuse is accepted), and the shared validators and enums in `packages/contracts` (`validation.py`, `inputs.py`, `errors.py`, `results.py`), so that every fixture and refusal is constructible with existing codes. The statistics are standard, publicly documented definitions (median, median absolute deviation about the median, Hyndman-Fan type 7 quantile, mid-rank percentile) specified here from first principles with each varying convention chosen explicitly. No private source, threshold, window length or default is used or copied. The audit context for the three stories: decision D-MED (mean companion is its own numbered story, #490 stays median/MAD), wave 2 decision X4 (NS-MEAN-COMPANION), wave 3 decision Q3 and the #489 bridge for the watchlists (the #489 edge is required, W3A-5).

## Unchanged boundary

Existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult`, `Status`, `Reason`, `ErrorCode` and scalar `ValueType` values (`int64`, `float64`); the shared BAR, DAILY and REFERENCE validators; the frozen ef1-contract1 and every accepted core, R17, EF1 and EF2 header; the accepted `baseline.daily_volume`, `baseline.relative_volume`, `baseline.interval_volume` and `baseline.interval_relative_volume` (mean based, prior only, unchanged and not reused: see "Relation to the accepted baselines"). No new DataKind, DTO, result codec, scheduler or default, no new error code, no new validator, no change to a shared validator and no new unit string (`shares`, `fraction`, `currency/share` and `members` already exist). This packet is additive: three new producers and thirteen new headers, four new reference `fact_kind` values, new policy labels and a new catalog entry set whose digest is new (existing entries and digest inputs do not change). Update, restore and merge are unsupported (`UNSUPPORTED_CAPABILITY`); batch and full replay only. A sibling amendment document follows a freeze, as for EF2.

## Producers and config identities

| Item | Robust history (#489) | Robust volume pace (#490) | Mean-ratio companion (#666) |
| --- | --- | --- | --- |
| Identity | `ef3.robust_history` | `ef3.volume_pace_robust` | `ef3.volume_ratio_mean` |
| Algorithm / schema | `ef3-robust-history-v1` / `1` | `ef3-volume-pace-robust-v1` / `1` | `ef3-volume-ratio-mean-v1` / `1` |
| Policy label | `ef3-robust1` | `ef3-pace1` | `ef3-mean1` |
| Parameters (no defaults) | `policy_version`, `field` (`volume`, `open`, `high`, `low`, `close`), `window` N (1..4096), `min_history` m (1..N), `quantile_num`/`quantile_den` (exactly when `robust.quantile` is selected), `min_population` (1..65536, exactly when a cohort output is selected), `evidence_limit` (0..10000) | `policy_version`, `profile` (`cumulative`, `bucket`), `window` N, `min_history` m, `grid_version`, `scale_num`/`scale_den` (exactly when `pace.robust_z` is selected), `evidence_limit` | `policy_version`, `field` (`volume` only in v1), `numerator_window` S, `baseline_window` L (1..4096), `numerator_inclusion`, `baseline_inclusion` (`prior_only`, `current_inclusive`), `evidence_limit` |
| Roles in order | `series`, `sessions`, `population`, `cohort_values` | `grid`, `sessions`, `bars` | `series`, `sessions` |
| ConfigSpec | PriceUnit mandatory; adjustment declared once and shared by every role | same | same |

A policy label names the whole convention set of its version (median, MAD scale, quantile estimator, rank and tie rule, window rule, exclusion rule, missingness mapping, rounding). An unsupported label is `INCOMPATIBLE_VERSION`; a future convention needs a new label, never a silent change. The three producers have separate version and config identities so the median/MAD profiles and the mean companion are never conflated, per decision D-MED. Rational parameters (`quantile`, `scale`) are reduced int64 pairs; floats, bools and decimal text are `INVALID_CONFIG`. Window bounds reuse the R17 period bound of 4096; the grid is bounded to 4096 buckets.

## Outputs and headers

| Feature id | dtype | unit | Producer | Available when |
| --- | --- | --- | --- | --- |
| `robust.median` | float64 | shares or currency/share, by `field` | history | retained prior sample ready, n >= m |
| `robust.mad` | float64 | same | history | same closure |
| `robust.quantile` | float64 | same | history | same closure, quantile parameter present |
| `robust.percentile_rank` | float64 | fraction | history | sample closure plus the target observation |
| `cohort.percentile_rank` | float64 | fraction | history | every declared member eligible, declared >= min_population |
| `cohort.rank` | int64 | members | history | same closure |
| `pace.baseline_median` | float64 | shares | pace | evaluation bucket defined, retained prior sample ready, n >= m |
| `pace.baseline_mad` | float64 | shares | pace | same closure |
| `pace.ratio` | float64 | fraction | pace | baseline ready, current ready, median > 0 |
| `pace.robust_z` | float64 | fraction | pace | baseline ready, current ready, MAD > 0 |
| `mean.numerator` | float64 | shares | mean | S-session window complete and known |
| `mean.baseline` | float64 | shares | mean | L-session window complete and known |
| `mean.ratio` | float64 | fraction | mean | both windows ready, baseline > 0 |

Order: lexicographic by feature id within a producer. Each output has its own required operands, expected and observed counts and independent readiness; an unrelated missing operand never blocks a ready output (fixtures H26 to H28: summaries available while the rank is blocked by the target; P11, P12, P15b: baseline available while ratio and z are blocked by the current observation; R06, R07: numerator available while the baseline is blocked). A different config (window, quantile, scale, inclusion) is a different result.

## Inputs and roles

Value basis (DP-W4 below). Volume is int64 shares, `0 <= v <= 2^63-1`; a negative volume is `BOUNDS`. Price fields are positive int64 coefficients at `ConfigSpec.price_unit.scale` (0..18) in one currency and one adjustment basis. All comparisons, sorts, medians, deviations, ranks and sums run on exact integers or rationals; the price coefficient is divided by `10^scale` only when a value is published, so no float enters any comparison. Cumulative pace operands and window sums are exact wide integers (at most 4096 terms of at most 2^63-1, far below the decimal128 bound) and only published values are float64, so no `OVERFLOW` path exists for them (fixtures P24, R13 exceed int64 internally and stay exact). Every row declares the config adjustment basis (`UNSUPPORTED_ADJUSTMENT` otherwise). There is no acquisition, clock or I/O. The governed grid is the supplied `sessions` role; omitted expected sessions are never compressed away.

| Role | Kind | Content |
| --- | --- | --- |
| `series` | DAILY | one row per governed session of the window and the target; the operand column named by `field`; `start_ns`/`end_ns` equal the session bounds fact; completed sessions only (a forming daily row ends after the market cutoff and is `BOUNDS`) |
| `sessions` | REFERENCE | `ef3.session.bounds` per governed session (actual open and close = the governed grid) and optional `ef3.session.excluded` facts (reason label in `text`) |
| `population` | REFERENCE | `ef3.population.member` per declared member, session = target session |
| `cohort_values` | DAILY | one row per member for the target session; the target member's row is the target value |
| `grid` | REFERENCE | `ef3.bucket.edge` rows, `effective_start_ns` = offset from the actual open, first edge 0, strictly increasing, `text` = `grid_version` |
| `bars` | BAR | one row per session per grid bucket: prior sessions and the target session in one role; volume int64 shares; zero-volume rows have null OHLC (shared rule) |

Fact schemas are in the JSON `reference_fact_schemas`: `reference_id` is `x1:B(id)` as in EF2, `price`, `factor_num` and `factor_den` are null, rows within one (instrument, session) group are ordered by `(effective_start_ns, reference_id)` as the shared validator requires, and `known_at_ns` is the original knowledge, nullable. The shared validators already enforce BAR/DAILY duplicate, order, interval, positivity and zero-volume rules and the REFERENCE duplicate, order and bounds rules; the library adds only identity checks that use existing codes. Roles are fixed nullable slots per producer; `None` is an absent delivery. Roles not needed by the selected outputs are not required (cohort roles for a history-only selection; `grid` and `bars` for none of the history outputs).

## Exact mathematics

### Shared statistics (used by #489 and #490; admission shared with #666)

Sample X: multiset of n exact rationals, sorted x(1) <= ... <= x(n).

- **Median.** x((n+1)/2) for odd n; the mean of the two middle values for even n (DP-S2). Half-integers are exact.
- **MAD.** `MAD(X) = median(|x_i - median(X)|)`, raw, scale constant 1, exact (DP-S1). Zero is an available value (a majority of equal values, or n = 1). No header applies the normal-consistent constant; the z-like normalization takes a caller rational k.
- **Quantile.** Hyndman-Fan type 7 with exact rational p = `quantile_num/quantile_den` in [0, 1] (DP-S3): `h = (n-1)p` exactly, `j = floor(h)`, `g = h - j`, `Q = x(j+1) + g (x(j+2) - x(j+1))`; `p = 1` returns x(n); n = 1 returns x(1). Exact rational p matters: `p = 1/3` over n = 4 gives `h = 1` exactly (H24b) where a binary float 0.333.. would interpolate.
- **Percentile rank.** `PR = (L + E/2) / n` with `L = #{s < x}`, `E = #{s == x}`: ties count half (DP-S4, the convention of the accepted EF2 band-width percentile). A rank is a fraction in [0, 1].
- **Publication.** Exact rational, one correctly rounded (round-half-even) float64 at the end; `cohort.rank` is an exact int64 (DP-S6).

### #489 robust history

Window (DP-W1). For target session t and caller N, the window is the N governed sessions t-N .. t-1 on the `sessions` grid; the target never enters the sample (prior-only; H10a/H10b: changing the target from 5 to 1e9 leaves median and MAD at 4 and 2 and moves only the rank, and including the target would have moved the median to 9/2). Fewer than N governed sessions before the target is `insufficient_history` whatever m is (H09, H33). A session with a declared exclusion fact is removed from the sample and from the expected count (DP-W2): `expected = N - exclusions`, `observed` = ready retained sessions, available requires `observed == expected >= m`; `expected < m` is `insufficient_history` (H07 boundary available at n = m = 3, H08 insufficient at n = 2). Gap, absent, null, unknown and future slots inside the window are never tolerated; an unready slot older than the window does not matter (H17, finite recovery). An exclusion fact whose own knowledge is null or later than K makes membership unknowable and blocks (H30, H31); an exclusion fact on the target session is refused with `INCONSISTENT_IDENTITY` (RF45, OQ-13).

Outputs: `robust.median`, `robust.mad`, `robust.quantile` over the retained sample, converted to the operand unit at publication; `robust.percentile_rank` is the mid-rank of the target value against the prior sample, so 0 and 1 are reachable when the target is below or above every prior value (H06, H06b). A forming target is not admitted (use #490).

Cohort (DP-C1, DP-C2). The declared population P is the `population` role; the target instrument must be a declared member. Eligible members have a ready value for the target session. `cohort.percentile_rank = (L + E/2)/n` over all eligible members including the target (E >= 1, so 0 and 1 are unreachable; a single member gives 1/2, C04) and `cohort.rank = 1 + #{v > x}` (competition rank, 1 is the largest, ties share the best rank, DP-S5). A declared member that is absent, null, unknown, future or gapped makes the population partial: `incomplete_coverage`/`partial_universe` with null values and counts expected = declared, observed = eligible (C07 to C10b); the target member's own unreadiness reports its ordinary reason (C11, C12) and takes precedence (C13). Declared size below `min_population` is `insufficient_history` (C06a/C06b). `empty_universe` is deliberately unreachable (the target is always a declared member).

### #490 robust volume pace

Grid and evaluation bucket (DP-P2, DP-P6). Bucket c is `[open + g_c, open + g_{c+1})` on the actual session open, with edges `g_0 = 0 < g_1 < ... < g_B` from the `grid` role (unequal bucket widths are legal, P20). Let `e_s` = actual target close offset and `e_c` = market cutoff offset. The evaluation bucket is `b = max{c : g_{c+1} <= min(e_s, e_c)}`. If no bucket fits the actual target session the result is `missing_input`/`ineligible` (P25); if buckets fit the session but none has fully elapsed at the cutoff it is `incomplete_coverage`/`future_market` for every pace output (P10). A cutoff inside a bucket evaluates the previous bucket (P09 equals P01b), and a target session that closes early evaluates the last bucket inside the session (P08).

Operand (DP-P1, DP-P4). For session j: `y_j = V[j,b]` (profile `bucket`) or `y_j = sum_{c=0..b} V[j,c]` (profile `cumulative`: current observations combine across buckets 0..b; every one of them must be present, known and covered, P11 versus the bucket-profile P27). The target operand y is built the same way from the same role. Compatible means same instrument, session, exact grid bounds, unit and basis; a consolidated bucket volume is supplied, venue merging is not done here.

Baseline (DP-W1, DP-W2, DP-P3). The sample is the retained prior sessions of the N-session window: sessions with an exclusion fact are removed (P06) and sessions whose actual close precedes the end of bucket b are structurally ineligible and removed (never volume 0, never a gap; P07, P19 shows a close exactly at the bucket end is eligible, P20 shows an unequal grid); `expected = N - excluded - ineligible`, `n` = ready retained, `n >= m` required (P16a insufficient at n = 2 < 3, P16b available at n = m = 2). `M = median`, `D = MAD` of the retained `y_j` (raw). Target contamination is excluded by construction: the target row is never a baseline member (P17a/P17b: current 450 versus 90000 leaves M = 300 and D = 100) and rows after the target or beyond bucket b are never inspected (P18).

Arithmetic (DP-P5), plain relations with caller parameters and no policy: `pace.ratio = y / M`; `pace.robust_z = (y - M) / (k D)` with `k = scale_num/scale_den` (P01: 3/2 gives 1, P01b: 1 gives 3/2, P01c: 1/3 gives 9/2). `M = 0` makes the ratio `not_applicable`/`zero_denominator` even for `0/0` (P05, P05b); `D = 0` makes z `not_applicable`/`zero_denominator` even if `y = M` (P04, P23, P28). For nonnegative samples `M = 0` implies `D = 0`, so zero baseline disables both. z may be negative and is not clamped (P21); `y = M` gives exact +0.0 (P22). `pace.baseline_median` and `pace.baseline_mad` remain available when only the current observation is unready. Mean ratios do not replace these medians: P28 and H36 give median 10 and ratio 2 on the series that gives a mean baseline of 208 in R12.

### #666 mean-ratio companion

A separate producer (DP-M1) whose operand is the daily volume series. Windows (DP-M2): for caller S and L and an inclusion each, a window ends at t-1 (`prior_only`) or at t (`current_inclusive`), so `mean.numerator = sum over the S-window / S`, `mean.baseline = sum over the L-window / L`, `mean.ratio = (L * sumS) / (S * sumL)`, all exact. Overlap and any ordering of S and L are legal (R03 overlap on the target, R10 identical windows give exactly 1, R11 S > L). A prior-only window never consumes the target row, so it stays available without it (R08a); a current-inclusive window needs it (R08b, R09). Complete governed windows only (DP-M3): no exclusions, no shrunken denominator; fewer sessions than the window is `insufficient_history` (R06); a zero baseline is `not_applicable`/`zero_denominator` (R05) and no negative baseline exists. One common ratio operand serves all consumers; they differ by config, not by code (DP-M4). Its arithmetic with `S = 1` current-inclusive over an `L` prior-only baseline equals the accepted `baseline.relative_volume` formula (R02) but is a distinct versioned output (OQ-3).

### Relation to the accepted baselines

`baseline.daily_volume` and `baseline.interval_volume` (EQ031, EQ032) are prior-only arithmetic means over exactly N sessions that block on any missing slot and treat an early-close bucket as an incomplete (not removed) observation. `robust.*` and `pace.*` are median and MAD profiles: they differ by estimator, by the explicit minimum-history rule and by removing declared exclusions and structurally ineligible early-close sessions. The prior-only convention (target excluded, governed grid, no compression) is the same. `mean.baseline` with `prior_only` and `L = N` has the same arithmetic as `baseline.daily_volume`, but no closed baseline reuse is accepted (dispositions file) and #36 reuse is unproved, so it is a distinct variant (OQ-3). The existing prior-only extrema `history.prior_high/low` are unaffected.

## Availability, coverage, quality, evidence and refusals

Typed refusal precedes assessment. Quality uses existing `Status`/`Reason` only. All applicable reasons are retained in lexical order and the status follows the first applicable reason in the fixed precedence (DP-Q1): `absent_input`, `unknown_availability`, `future_knowledge`, `null_field`, `ineligible` (all `missing_input`), `governed_gap`, `future_market`, `partial_universe` (all `incomplete_coverage`), `insufficient_history`, `no_eligible_observations`, `empty_universe`, `zero_denominator` (the last three `not_applicable`), else `available`. This is the money-flow precedence extended by the two existing incomplete-coverage reasons `future_market` and `partial_universe`. A value is null exactly when the status is not available, and `available` implies `observed == expected`. `no_eligible_observations` and `empty_universe` are deliberately unreachable. The slot-reason mapping follows the merged EF2 contracts (DP-W3): no row and no coverage is `absent_input`, declared incomplete coverage is `governed_gap`, a null field is `null_field`, `known_at` null is `unknown_availability` and `known_at > K` is `future_knowledge` (`known_at == K` is available, H20a, C16a, R18). Knowledge is enforced identically in `known_at` and reconstruction modes with original `known_at`. Fixtures H18/H19 show multi-reason precedence.

Counts (also in the JSON): history expected `N - exclusions`, observed ready retained; rank expected + 1; cohort expected declared, observed eligible; pace baseline expected `N - excluded - ineligible` (observed 0 when no evaluation bucket); pace ratio and z expected 2 (baseline, current); mean numerator S, baseline L, ratio 2.

Evidence (available outputs only, unavailable outputs emit none): the limit is the existing `evidence_limit` 0..10000 and witnesses never exceed it (H29a, H29b, C19, P29, R17). Order: the target row first for outputs that consume it, then retained sample rows ascending by session, then excluded then ineligible session facts. Row ids are `session:<session_id>` (pace aggregates a session's bucket rows 0..b under one witness), `member:<instrument_id>`, `excluded:<session_id>`, `ineligible:<session_id>` and `target:<session_id>`, with boundary `completed_interval` and event time at the end of the evaluation bucket or the session.

Refusals (no `FeatureResult`) RF01 to RF45 in the JSON, each listing whether an existing shared validator or the library raises it: duplicates `DUPLICATE`; out-of-order daily rows or grid edges `INVALID_ORDER`; negative volume, forming rows and non-positive intervals `BOUNDS`; zero-volume rows with a price, positive-volume rows with a null price, float volumes and a foreign fact kind `INVALID_SCHEMA`; `int64` excess `OVERFLOW`; scale or currency differences `INVALID_UNIT`; basis differences `UNSUPPORTED_ADJUSTMENT`; bad window, minimum history, field, quantile, scale, profile, inclusion, missing or unknown parameter `INVALID_CONFIG`; unsupported label `INCOMPATIBLE_VERSION`; unknown feature `UNKNOWN_FEATURE`; update, restore, merge `UNSUPPORTED_CAPABILITY`; a target outside the population, a value row for an undeclared member, a bar matching no grid bucket (irregular), a bar beyond the actual close, a grid version mismatch or a series row without a bounds fact `INCONSISTENT_IDENTITY`. Every code was checked against `packages/contracts/.../errors.py` and the shared validators; no new code or validator change is needed.

## Numeric policy and acceptance

Exact integer/rational arithmetic throughout, one correctly rounded float64 per published value (DP-S6, compatible with the R17 Decimal120 policy and its error contract). Acceptance rule per fixture output (field `acceptance` in the JSON):

- `exact_float64`: the reference is a dyadic rational with numerator below 2^53, so any exact-rational or Decimal120 path produces it without rounding; the published float64 must equal the hex bit for bit (212 outputs).
- `exact_plus_zero`: the reference is exactly 0 from exact integer arithmetic (equal integers subtract to zero, counts of zero); bit-exact +0.0, never -0.0 (23 outputs).
- `tolerance`: `abs(y - r) <= max(8 ulp(r), 1e-12 |r|)` with r the fixture float64, the R17 numeric error contract (34 outputs, non-dyadic rationals such as 3/10, 12/5 or any value that exceeds 53 bits like 2^63-1).
- `exact_integer`: `cohort.rank` (13 outputs).

No documented exceptions. Measurement of cost is not part of this contract; the processing is O(n log n) per sample with bounded N and no whole-series barrier, and any speed claim belongs to the release baseline.

## Layer responsibilities

- **Library (#489, #490, #666).** Admission of the supplied facts, window, population and bucket selection, exclusion and ineligibility handling, the exact statistics, ratios and z, quality, evidence and every library refusal above; pure and deterministic with exact rational intermediates and one final rounding; one shared sample-summary kernel reused by the history and pace producers and one shared window admission reused by the mean companion, with no coupling of output readiness.
- **EF3 I/O #611.** Maps ordered daily and bucket rows, session bounds, exclusion facts, declared populations and grid edges exactly as supplied with their original `known_at`; maps results (int64 `cohort.rank`, hex-exact float64, status, reasons, counts, witnesses) to the existing sink conversion; never sorts, fills, imputes, drops, converts scale or currency, chooses a window, derives an evaluation bucket or computes any statistic.
- **Worker #612.** Routes selected outputs with exact window and population closure, shares bounded histories across outputs and keeps independent readiness, executes one config per complete result, binds inputs and the config digest and persists the library result unchanged. Direct, adapter, worker and stored results must be identical, including refusal class.

## Fixtures

43 history fixtures (H01 to H39, H32 removed by ruling OQ-13), 23 cohort fixtures (C01 to C19), 34 pace fixtures (P01 to P29) and 19 mean-ratio fixtures (R01 to R18), 119 result fixtures, plus 45 refusal fixtures. The JSON `coverage_map` indexes them by tag, `reasons_reached` by reason and `prefix_equivalences` lists identical-result pairs. Coverage: odd and even windows (H01, H02, H05, H37, P03); ties and rank ties (H03, H04, H35, H39, C02, C03, C14, C15); zero MAD (H03, H04, H23, H36, P04, P23, P28); minimum-history boundary (H07, H08, P16a, P16b, C06a, C06b); prior-only target exclusion and contamination counterexamples (H10a, H10b, P17a, P17b, R08a); excluded sessions (H07, H08, H11, H30, H31, P06, P16a, P16b); early-close and irregular buckets (P07, P08, P19, P20, P25); elapsed coverage (P08, P09, P10); zero baseline (P05, P05b, R05); cohort availability and cutoff availability (C07 to C13, C16a, C16b, H20a, H20b); rank and percentile ties and population edges (H06, H06b, C04, C05a, C05b, C15, C17); mean-ratio companion fixtures distinct from the median/MAD ones (R01 to R18; R12 versus H36 and P28); prefix property (H25, P09, P18, R16); price value basis and int64 limits (H21, H22, H22b, C18, P24, R13); quantile exactness (H24 to H24c); independent readiness (H26 to H28, P11, P12, P15b, P27, R06, R07, R08b). Every reason reachable appears at least once: `absent_input`, `unknown_availability`, `future_knowledge`, `null_field`, `ineligible` (P25), `governed_gap`, `future_market` (P10), `partial_universe`, `insufficient_history`, `zero_denominator`; `no_eligible_observations` and `empty_universe` are unreachable by design.

Fixture notation, including how a null, empty, gap, absent, future and unknown slot is constructed, is in the JSON `fixture_notation`. Construction rules recorded there: prices are positive; zero-volume rows carry null OHLC when a price column is delivered, and a positive-volume row with a null price is malformed, so `null_field` is reached through a null volume column or through the null column of a price-only series; there is no recursion, epoch or anchor in these producers (the pace profile resets at every session open and carry across sessions is not supported). Prefix property: every output at target t depends only on sessions before t (plus t itself for the rank, the current-inclusive mean windows and the pace current operand) and on buckets 0..b, so appended later sessions with later knowledge change nothing. Required readback: a stored `cohort.rank` is an int64 never converted through float, and every stored float64 equals the float64 of the exact rational.

## Explicit non-goals

No thresholds, scanners, alert or catalogue policy (#518); no default window, minimum history, quantile, scale, ratio or inclusion; no replacement of median/MAD by mean ratios and no mean inside the robust producers; no approximate algorithm (no streaming sketch, t-digest or sampled quantile, so no error contract is needed); no calendar lookup, session or exclusion discovery; no acquisition, price or volume adjustment, currency conversion, imputation or forward fill; no rank of a forming daily value; no cross-venue merging; no carry across sessions; no update, restore or merge; no cohort ranking of derived float values; no new DataKind, DTO, codec, scheduler, validator or error code; no performance, parity, release or publication claim; no private-source equivalence or source formula.

## Coordinator decisions: conventions (accepted as proposed, pending owner review)

| Id | Convention (alternatives in the JSON) |
| --- | --- |
| DP-S1 | MAD is raw (scale 1); no normal-consistent constant; z divides by caller `k`. |
| DP-S2 | Even-n median is the mean of the two middle values. |
| DP-S3 | Quantile is Hyndman-Fan type 7 with exact rational p. |
| DP-S4 | Percentile rank is mid-rank `(L + E/2)/n`; history rank excludes the target, cohort rank includes it. |
| DP-S5 | Cohort ordinal rank is competition, 1 is the largest. |
| DP-S6 | Exact rational arithmetic, one float64 rounding, per-fixture acceptance rule. |
| DP-W1 | Window is the N governed sessions immediately before the target; target never in the sample; N and m caller-set. |
| DP-W2 | Declared exclusions are removed from sample and expected; gaps never tolerated; m bounds the retained sample. |
| DP-W3 | Absent slot is `absent_input` (EF2 mapping), not EQ031's `incomplete_coverage`. |
| DP-W4 | Header units follow the operand field. |
| DP-C1 | Partial population withholds the cohort rank (`partial_universe`); `min_population` shortfall is `insufficient_history`. |
| DP-C2 | The target must be a declared member. |
| DP-P1 | Two profiles, `cumulative` and `bucket`. |
| DP-P2 | Evaluation bucket derived from the cutoff and the actual close. |
| DP-P3 | Early-close and structurally ineligible prior sessions are removed, not blocking (differs from EQ032). |
| DP-P4 | Current observation is the target's consolidated bucket rows 0..b. |
| DP-P5 | `ratio = y/M`, `z = (y-M)/(kD)`, zero M or D is `zero_denominator`. |
| DP-P6 | The bucket grid travels as a `grid` reference role. |
| DP-M1 | The mean companion is a separate producer and identity. |
| DP-M2 | Independent numerator and baseline inclusion parameters; overlap and any S, L order legal. |
| DP-M3 | Complete windows only, no exclusions in v1. |
| DP-M4 | One common ratio operand; consumers differ by config. |
| DP-Q1 | Reason precedence as above. |
| DP-E1 | Witness order and row ids as above. |
| DP-R1 | Rational parameters are reduced int64 pairs. |
| DP-X1 | Batch and full replay only. |

## Coordinator rulings on the former open questions (pending owner review)

| Id | Ruling |
| --- | --- |
| OQ-1 | Monetary volume proxy: v1 is shares only; the proxy is deferred to an amendment. |
| OQ-2 | #666 needs no numeric mean edge from #489: it computes its own mean from the same admitted sessions (shared admission only) and stays independent. |
| OQ-3 | `baseline.daily_volume` is not reused; `mean.baseline` is its own computation (reuse unproved). |
| OQ-4 | (coordinator-decided, conservative) exact integers only; no rational-valued cohort variant in v1. |
| OQ-5 | (conservative) no named normal-consistent profile; the caller `k` is the only scale. |
| OQ-6 | (conservative) exclusion reason is an opaque non-empty caller label; no vocabulary invented. |
| OQ-7 | `ef3.population.member` is the shared declared-population kind for EF3; contract F (breadth, branch ef3-contract-f) reuses it. The duplicate-identity rule is stated once here: a duplicate (instrument, session, reference_id) is rejected with `DUPLICATE` (RF12). The definition is self-contained: one row per declared member, `instrument_id` = member, `session_id` = target session, `reference_id` `x1:B(population_id)` identical across members, effective bounds = target session bounds, `text` = snapshot id, `price`/`factor_*` null, `known_at_ns` nullable; the target instrument must be a member. |
| OQ-8 | No pace header for the evaluation bucket; it is evidence only. |
| OQ-9 | (conservative) the mean companion is daily series only in v1. |
| OQ-10 | All three producers live in `packages/features` (EF3 module, config namespace `ef3.*`), separate catalog; `describe_intraday()` and its digest unchanged; no package version bump. |
| OQ-11 | The median fields of the F0707 to F0712 style are computed outputs of #490 from the #489 baseline producer; the #490 to #489 edge is added. |
| OQ-12 | #626 consumes none of these in v1; any later consumption by amendment. |
| OQ-13 | (conservative) an exclusion fact on the target session is refused (`INCONSISTENT_IDENTITY`, RF45); fixture H32 is removed. |
| OQ-14 | (conservative) `min_population` is bounded 1..65536. |

Coordinator-decided by conservative default (not named in the rulings): OQ-4, OQ-5, OQ-6, OQ-9, OQ-13, OQ-14.

## Header ledger and amendment (to be applied)

The 13 headers of this contract are to be applied by a sibling amendment document after the freeze. The unit `members` (`cohort.rank`) already exists in the declared-breadth catalog but is new to this ledger; `shares`, `fraction` and `currency/share` exist.

## Coordinator freeze

Frozen as `ef3-robust1`, `ef3-pace1` and `ef3-mean1` (v1) for implementation once this PR merges (coordinator statement; no review or acceptance claim by the author). Reset epoch mode only: the pace profile resets at every session open and carry is out of v1. There are no defaults for windows, `k`, `p` or `m`. Any change to a convention, label semantics, header, role or fixture after merge requires a new policy label and an amendment document.
