# DV1 definition variants - library contract proposal `dv1-definition-variants-1`

Status: **draft, not frozen.** Contract and fixtures only (DV1-0). No library, I/O or worker code. Internal, synthetic, pre-release; nothing here claims real-data readiness, product availability or a performance property, and no conflict is called fixed or covered until its wrong-convention fixtures pass in the library story. Additive: no frozen EF1-EF5 file is edited; the only edit outside `docs/dv1` text is an errata entry in [EF4_ERRATA.md](../ef4/EF4_ERRATA.md) (PO ruling 4). "DV1" here is the definition-variants program of the 2026-10-29 PO rulings, not the EF6 release (EQ-173) of [EQUITY_DELIVERY_REPLAN.md](../EQUITY_DELIVERY_REPLAN.md).

## Authority and inputs

PO rulings (Q1 to Q5, contract name, story split, acceptance, wording), the Architect design, the parity check and the PO reconciliation of 2026-10-29; the frozen EF3 `ef3-rel1` contract (simple-return statistics), EF4 I2 (core outputs, leg eligibility) and EF5 (compact notation, quality vocabulary, knowledge semantics, refusal stages, basis echo, adjustment_spec rules). The rulings and design notes live in the git-ignored `work/` folder; the decisions are recorded in `DECISIONS.md`.

## Why this contract exists

The WatchYourList design states definitions that differ from shipped ids. Library rule: another convention is another label. Each variant below is a NEW id carrying its convention in its name; no shipped id changes meaning.

| Design item | Shipped id | Difference | New id |
|---|---|---|---|
| P40-P42 beta, correlation | `relative.beta`, `relative.correlation` | simple vs log returns | `relative.log_return_beta`, `relative.log_return_correlation` |
| V12a ATR | `history.atr` | Wilder vs simple mean of true range | `history.atr_simple_mean` |
| P15 range | `session.price.range_fraction` | (H-L)/close vs (H-L)/open | `session.price.range_over_open` |
| M11 spread | `core.benchmark_return_dispersion_fraction` | publishes the range; stdev wanted; open-to-close basis | `core.benchmark_return_range_fraction`, `core.benchmark_return_stdev_fraction` |
| P36-P39, S4 window extremes | `history.prior_high/low` | target excluded, high/low field only, no date | `history.window_high`, `history.window_low`, `history.window_high_offset`, `history.window_low_offset` |

## Conventions fixed by the rulings

| # | Ruling | Convention | Fixtures |
|---|---|---|---|
| C1 | Q1 | ATR window is target-inclusive: the N most recent completed sessions ending at the target (N true ranges, N+1 closes). history.atr (Wilder) is untouched. | AT01, AT03, AT05, AT18 |
| C2 | Q1 | The 20-day average of V12a is the close SMA over 20 sessions including the target (history.sma 20); consumer arithmetic on stored ids. | AT05 |
| C3 | Q1 | Missing-data rule strict: no skipping, no zero fill; unavailable with the reason; no inclusion parameter. | AT08, AT09, AT10, AT11, AT12, AT13, AT14 |
| C4 | Q2 | regular_open operand is the open of the regular-session daily bar of the exact session; end leg the same-session close; sources lacking an exact-session daily open make the leg unavailable. | CS02, CS08, CS09, CS10, CS13 |
| C5 | Q3 | Window extremes: period includes the current session, extreme_basis (intraday|close) explicit, no default, offset 0 = target, the latest session wins ties; 253 vs 252 is the design owner's single number, carried by the closeout binding table; the contract holds no second default. | WX01, WX06, WX07, WX09, WX10, WX11, WX12 |
| C6 | Q3 | P25 and V12b stay on history.prior_high/low (prior-only, target excluded); equivalence max(prior, current) on the intraday basis is pinned by cross-check fixtures. | WX01, WX03, WX09, WX10, WX13, WX14 |
| C7 | Q4 | core.benchmark_return_dispersion_fraction is DEPRECATED by description only (it publishes the range of core returns); two new ids; removal at the scheduled EF4 next-contract-version migration; EF4 errata entry. | CS01, CS06, CS07 |
| C8 | Q5 | session.price.range_over_open is a built-in R1 catalog entry (algorithm v1), (H-L)/O in all modes; range_fraction unchanged; non-positive open rejected at admission. | RO01, RO06 |
| C9 | DV1-1 | Log beta/correlation: Decimal120 logarithm of the exact ratio, one float64, hex pinned bit for bit; zero variance by exact ratio equality; n pairs in QualityRow. | RL01, RL05, RL06, RL19 |
| C10 | DV1-3 | Population standard deviation (divisor K) over the declared funds; withheld if any fund is missing. | CS02, CS03, CS08 |
| C12 | PO Q-1 | Two operands, never swapped: session.price.range_over_open (P15, intraday-capable) divides by session.bar.open = operand label first_eligible_regular_trade (first eligible regular-session trade price); core regular_open (M10/M11, end of day) uses operand label daily_bar_open (official daily-bar open of the exact session). They can differ (first trade 100.00, official open 100.20); P15 and M11 figures are never compared or substituted. | RO11, CS21, CS02 |
| C13 | PO Q-3 | Unit `sessions` (int64): a non-negative integer count of sessions before the target (0 = the target); not scaled, never a float, never negative; an offset output is unavailable whenever its extreme value is; INVALID_UNIT covers `sessions` offered where a price unit is required and a price unit offered where `sessions` is required. Additive vocabulary in the DV1 contract only; the E9 slash-style units and the EF5 contract are not edited. | WX01, WX15 |
| C11 | acceptance | Numeric near-tie rule and 'value within 1e-100 of zero published as computed' written in numeric_policy. | RL03, RL19 |

## Producers and config identity

| Producer | Config identity | Policy label | Parameters (all required, no defaults) | Outputs |
|---|---|---|---|---|
| relative_log_stats | `dv1.relative_log_stats` | `dv1-rlog1` | policy_version; benchmark_id; window W (2..4096); min_pairs (2..W); evidence_limit (0..10000); adjustment label + adjustment_spec | `relative.log_return_beta`, `relative.log_return_correlation` |
| atr_simple_mean | `dv1.atr_simple_mean` | `dv1-atrs1` | policy_version; period N (1..4096); evidence_limit; adjustment label + adjustment_spec | `history.atr_simple_mean` |
| core_spread | `dv1.core_spread` | `dv1-core1` | policy_version; core_benchmark_ids (2..16 distinct); core_profile (prior_close|window_start|regular_open); alignment_tolerance_ns; max_endpoint_age_ns; window_ns (exactly when window_start); evidence_limit | `core.benchmark_return_range_fraction`, `core.benchmark_return_stdev_fraction` |
| session_range_over_open | `built-in R1 catalog entry (no DV1 producer)` | `none (built-in algorithm v1)` | evidence_limit | `session.price.range_over_open` |
| window_extreme | `dv1.window_extreme` | `dv1-wext1` | policy_version; period P (1..4096, sessions INCLUDING the current one); extreme_basis (intraday|close, no default); offset_unit (build argument, exactly sessions, else INVALID_UNIT; no default); evidence_limit; adjustment label + adjustment_spec | `history.window_high`, `history.window_low`, `history.window_high_offset`, `history.window_low_offset` |

Algorithm versions `dv1-relative-log-stats-v1`, `dv1-atr-simple-mean-v1`, `dv1-core-spread-v1`, `dv1-window-extreme-v1`; built-in `session.price.range_over_open` algorithm `v1`. Hosting proposal: `equity_features.dv1`, namespace `dv1.*`; default registry, EF3/EF4 contracts and EF5 stay byte-identical; the built-in is the one R1 catalog change (DV1-4, coordinated bump). No package version bump by this PR.

## Input contract and output contract of every output id

Owner rule: each output states what an adapter must read from its source, convert and pass to the library (INPUT: fields, grain, adjustment, session, history depth, minimum samples; no provider, tier or cost named) and what a consumer may rely on (OUTPUT: value type, unit, basis echo, unavailable and refusal rules). The same text is in `headers[*].input_contract` and `headers[*].output_contract` of the JSON; each fixture carries an `inputs` block with its own grain, history depth and minimum samples.

Adapter boundary: an adapter reads, converts to the canonical integer coefficients at the declared price unit scale, labels the basis and the session, attaches original known_at and declared coverage, and passes the data on. It never fills, aligns, drops, resamples, adjusts, chooses a window, a basis or a period, and applies no default (the defaults ledger is empty).

### `core.benchmark_return_range_fraction`

float64, unit `fraction`, producer `core_spread`, available when: all K declared core funds eligible under the profile. Ownership: DV1-3 (range of core returns; replaces the misleading deprecated name).

| INPUT contract (adapter side) | |
|---|---|
| fields | start and end price witnesses per fund (leg facts) |
| grain | one witness pair per fund; K = 2..16 funds declared in the config |
| adjustment | action snapshot equal on both legs of a fund |
| session | regular_open: both legs in the exact regular session; prior_close: start in the prior session; window_start: both in one session |
| history depth | 1 session (regular_open), 2 (prior_close) |
| min samples | K eligible funds, no partial population |
| adapter must | supply the daily-bar open of the exact session as the regular_open start leg (operand daily_bar_open) and the same-session close as the end leg; never a first trade or first intraday bar open; omit the leg when the source has no exact-session daily open |

| OUTPUT contract (consumer side) | |
|---|---|
| value type | float64 |
| unit | fraction |
| basis echo | none (legs carry an action snapshot) |
| unavailable rules | partial population (partial_universe), misaligned or mixed-session population (ineligible), no facts (absent_input); values withheld, never 0 |
| refusals | INVALID_CONFIG / UNSUPPORTED_ADJUSTMENT / INVALID_UNIT / UNKNOWN_FEATURE / UNSUPPORTED_CAPABILITY at config, INCOMPATIBLE_VERSION on a wrong policy label, INVALID_SCHEMA / OVERFLOW / DUPLICATE / INVALID_ORDER / BOUNDS on malformed delivery, INCONSISTENT_IDENTITY on instrument or grid mismatch |
| note | max r - min r; the value the deprecated range id publishes (description-only deprecation) |

### `core.benchmark_return_stdev_fraction`

float64, unit `fraction`, producer `core_spread`, available when: all K declared core funds eligible under the profile. Ownership: DV1-3 (M11 binding).

| INPUT contract (adapter side) | |
|---|---|
| fields | start and end price witnesses per fund (leg facts) |
| grain | one witness pair per fund; K = 2..16 |
| adjustment | action snapshot equal on both legs of a fund |
| session | as core.benchmark_return_range_fraction |
| history depth | 1 session (regular_open) |
| min samples | K eligible funds |
| adapter must | as core.benchmark_return_range_fraction |

| OUTPUT contract (consumer side) | |
|---|---|
| value type | float64 |
| unit | fraction |
| basis echo | none |
| unavailable rules | as the range output; never 0 when unavailable (a computed 0 is a real 0 only when all returns are equal) |
| refusals | INVALID_CONFIG / UNSUPPORTED_ADJUSTMENT / INVALID_UNIT / UNKNOWN_FEATURE / UNSUPPORTED_CAPABILITY at config, INCOMPATIBLE_VERSION on a wrong policy label, INVALID_SCHEMA / OVERFLOW / DUPLICATE / INVALID_ORDER / BOUNDS on malformed delivery, INCONSISTENT_IDENTITY on instrument or grid mismatch |
| note | population standard deviation, divisor K |

### `history.atr_simple_mean`

float64, unit `currency/share`, producer `atr_simple_mean`, available when: closure of N+1 sessions READY (oldest: close; middle: high, low, close; target: high, low). Ownership: DV1-2 (V12a binding).

| INPUT contract (adapter side) | |
|---|---|
| fields | high, low, close |
| grain | daily session bar, regular session |
| adjustment | one declared basis for the whole series, unadjusted or split_adjusted, with adjustment_spec {policy_version} (and action_snapshot plus anchor for split_adjusted); the adapter converts nothing and mixes no bases |
| session | regular session OHLC of each governed daily session |
| history depth | N + 1 consecutive governed sessions ending at the target (N 1..4096) |
| min samples | all N + 1 (strict: no skipping, no zero fill, no shrinking) |
| adapter must | supply the ordered governed daily grid with declared coverage and original known_at, positive integer coefficients at the price unit scale |

| OUTPUT contract (consumer side) | |
|---|---|
| value type | float64 |
| unit | currency/share (coefficient / 10^scale) |
| basis echo | every output, available or not, carries the declared adjustment basis in the result field basis |
| unavailable rules | any closure slot not READY or before the first session (insufficient_history); never 0 unless every TR is 0 |
| refusals | INVALID_CONFIG / UNSUPPORTED_ADJUSTMENT / INVALID_UNIT / UNKNOWN_FEATURE / UNSUPPORTED_CAPABILITY at config, INCOMPATIBLE_VERSION on a wrong policy label, INVALID_SCHEMA / OVERFLOW / DUPLICATE / INVALID_ORDER / BOUNDS on malformed delivery, INCONSISTENT_IDENTITY on instrument or grid mismatch |
| note | target-inclusive simple mean of N true ranges; not Wilder |

### `history.window_high`

float64, unit `currency/share`, producer `window_extreme`, available when: period P sessions READY for the basis field. Ownership: DV1-6 (P36/P37 window high).

| INPUT contract (adapter side) | |
|---|---|
| fields | high (intraday basis) or close (close basis) |
| grain | daily session bar |
| adjustment | one declared basis for the whole series, unadjusted or split_adjusted, with adjustment_spec {policy_version} (and action_snapshot plus anchor for split_adjusted); the adapter converts nothing and mixes no bases |
| session | regular session |
| history depth | P sessions including the target (P 1..4096, explicit; 252 or 253 is the consumer's choice) |
| min samples | all P |
| adapter must | supply the governed daily grid; the basis is chosen by the consumer, not the adapter |

| OUTPUT contract (consumer side) | |
|---|---|
| value type | float64 |
| unit | currency/share |
| basis echo | every output, available or not, carries the declared adjustment basis in the result field basis |
| unavailable rules | any window slot not READY for the field, or window beyond the first session (insufficient_history) |
| refusals | INVALID_CONFIG / UNSUPPORTED_ADJUSTMENT / INVALID_UNIT / UNKNOWN_FEATURE / UNSUPPORTED_CAPABILITY at config, INCOMPATIBLE_VERSION on a wrong policy label, INVALID_SCHEMA / OVERFLOW / DUPLICATE / INVALID_ORDER / BOUNDS on malformed delivery, INCONSISTENT_IDENTITY on instrument or grid mismatch |
| note | maximum over the window including the target |

### `history.window_high_offset`

int64, unit `sessions`, producer `window_extreme`, available when: as history.window_high. Ownership: DV1-6 (extreme date).

| INPUT contract (adapter side) | |
|---|---|
| fields | as history.window_high |
| grain | daily |
| adjustment | one declared basis for the whole series, unadjusted or split_adjusted, with adjustment_spec {policy_version} (and action_snapshot plus anchor for split_adjusted); the adapter converts nothing and mixes no bases |
| session | regular session |
| history depth | P sessions including the target |
| min samples | all P |
| adapter must | as history.window_high; the consumer maps the offset to a date through its grid |

| OUTPUT contract (consumer side) | |
|---|---|
| value type | int64 |
| unit | sessions before the target (0 = the target) |
| basis echo | every output, available or not, carries the declared adjustment basis in the result field basis |
| unavailable rules | as history.window_high |
| refusals | INVALID_CONFIG / UNSUPPORTED_ADJUSTMENT / INVALID_UNIT / UNKNOWN_FEATURE / UNSUPPORTED_CAPABILITY at config, INCOMPATIBLE_VERSION on a wrong policy label, INVALID_SCHEMA / OVERFLOW / DUPLICATE / INVALID_ORDER / BOUNDS on malformed delivery, INCONSISTENT_IDENTITY on instrument or grid mismatch |
| note | the latest session wins a tie |

### `history.window_low`

float64, unit `currency/share`, producer `window_extreme`, available when: period P sessions READY for the basis field. Ownership: DV1-6 (P37 window low).

| INPUT contract (adapter side) | |
|---|---|
| fields | low (intraday basis) or close (close basis) |
| grain | daily session bar |
| adjustment | one declared basis for the whole series, unadjusted or split_adjusted, with adjustment_spec {policy_version} (and action_snapshot plus anchor for split_adjusted); the adapter converts nothing and mixes no bases |
| session | regular session |
| history depth | P sessions including the target |
| min samples | all P |
| adapter must | as history.window_high |

| OUTPUT contract (consumer side) | |
|---|---|
| value type | float64 |
| unit | currency/share |
| basis echo | every output, available or not, carries the declared adjustment basis in the result field basis |
| unavailable rules | as history.window_high |
| refusals | INVALID_CONFIG / UNSUPPORTED_ADJUSTMENT / INVALID_UNIT / UNKNOWN_FEATURE / UNSUPPORTED_CAPABILITY at config, INCOMPATIBLE_VERSION on a wrong policy label, INVALID_SCHEMA / OVERFLOW / DUPLICATE / INVALID_ORDER / BOUNDS on malformed delivery, INCONSISTENT_IDENTITY on instrument or grid mismatch |
| note | minimum over the window including the target |

### `history.window_low_offset`

int64, unit `sessions`, producer `window_extreme`, available when: as history.window_low. Ownership: DV1-6 (extreme date).

| INPUT contract (adapter side) | |
|---|---|
| fields | as history.window_low |
| grain | daily |
| adjustment | one declared basis for the whole series, unadjusted or split_adjusted, with adjustment_spec {policy_version} (and action_snapshot plus anchor for split_adjusted); the adapter converts nothing and mixes no bases |
| session | regular session |
| history depth | P sessions including the target |
| min samples | all P |
| adapter must | as history.window_high |

| OUTPUT contract (consumer side) | |
|---|---|
| value type | int64 |
| unit | sessions before the target (0 = the target) |
| basis echo | every output, available or not, carries the declared adjustment basis in the result field basis |
| unavailable rules | as history.window_high |
| refusals | INVALID_CONFIG / UNSUPPORTED_ADJUSTMENT / INVALID_UNIT / UNKNOWN_FEATURE / UNSUPPORTED_CAPABILITY at config, INCOMPATIBLE_VERSION on a wrong policy label, INVALID_SCHEMA / OVERFLOW / DUPLICATE / INVALID_ORDER / BOUNDS on malformed delivery, INCONSISTENT_IDENTITY on instrument or grid mismatch |
| note | the latest session wins a tie |

### `relative.log_return_beta`

float64, unit `fraction`, producer `relative_log_stats`, available when: n >= min_pairs valid pairs and benchmark log-return variance > 0 (exact ratio test). Ownership: DV1-1 (P40-P42 binding).

| INPUT contract (adapter side) | |
|---|---|
| fields | close of the instrument and of the benchmark (two close-only BAR roles) |
| grain | daily, one value per governed regular session, the same governed grid and sessions for both series |
| adjustment | one declared basis for the whole series, unadjusted or split_adjusted, with adjustment_spec {policy_version} (and action_snapshot plus anchor for split_adjusted); the adapter converts nothing and mixes no bases |
| session | regular session close of each governed daily session; the benchmark id differs from the instrument id |
| history depth | window + 1 consecutive governed sessions ending at the target (window 2..4096) |
| min samples | min_pairs joint valid pairs (2..window); a pair needs both closes of both sessions |
| adapter must | supply both series on one grid with original known_at, declared coverage, positive integer closes at the price unit scale, and never fill, align or drop a session |

| OUTPUT contract (consumer side) | |
|---|---|
| value type | float64 |
| unit | fraction (dimensionless coefficient) |
| basis echo | every output, available or not, carries the declared adjustment basis in the result field basis |
| unavailable rules | fewer than min_pairs valid pairs, window not wholly inside the grid (insufficient_history), a lost close (absent_input / unknown_availability / future_knowledge / null_field / governed_gap / future_market), zero benchmark variance by exact ratio equality (zero_denominator); never published as 0 |
| refusals | INVALID_CONFIG / UNSUPPORTED_ADJUSTMENT / INVALID_UNIT / UNKNOWN_FEATURE / UNSUPPORTED_CAPABILITY at config, INCOMPATIBLE_VERSION on a wrong policy label, INVALID_SCHEMA / OVERFLOW / DUPLICATE / INVALID_ORDER / BOUNDS on malformed delivery, INCONSISTENT_IDENTITY on instrument or grid mismatch |
| note | published expected = observed = n valid pairs when available; log returns, not simple returns |

### `relative.log_return_correlation`

float64, unit `fraction`, producer `relative_log_stats`, available when: n >= min_pairs valid pairs and both log-return variances > 0 (exact ratio tests). Ownership: DV1-1 (P40-P42 binding).

| INPUT contract (adapter side) | |
|---|---|
| fields | close of the instrument and of the benchmark (two close-only BAR roles) |
| grain | daily, one value per governed regular session, the same governed grid and sessions for both series |
| adjustment | one declared basis for the whole series, unadjusted or split_adjusted, with adjustment_spec {policy_version} (and action_snapshot plus anchor for split_adjusted); the adapter converts nothing and mixes no bases |
| session | regular session close of each governed daily session; the benchmark id differs from the instrument id |
| history depth | window + 1 consecutive governed sessions ending at the target (window 2..4096) |
| min samples | min_pairs joint valid pairs (2..window); a pair needs both closes of both sessions |
| adapter must | supply both series on one grid with original known_at, declared coverage, positive integer closes at the price unit scale, and never fill, align or drop a session |

| OUTPUT contract (consumer side) | |
|---|---|
| value type | float64 |
| unit | fraction (dimensionless coefficient) |
| basis echo | every output, available or not, carries the declared adjustment basis in the result field basis |
| unavailable rules | fewer than min_pairs valid pairs, window not wholly inside the grid (insufficient_history), a lost close (absent_input / unknown_availability / future_knowledge / null_field / governed_gap / future_market), zero benchmark variance by exact ratio equality (zero_denominator); never published as 0 |
| refusals | INVALID_CONFIG / UNSUPPORTED_ADJUSTMENT / INVALID_UNIT / UNKNOWN_FEATURE / UNSUPPORTED_CAPABILITY at config, INCOMPATIBLE_VERSION on a wrong policy label, INVALID_SCHEMA / OVERFLOW / DUPLICATE / INVALID_ORDER / BOUNDS on malformed delivery, INCONSISTENT_IDENTITY on instrument or grid mismatch |
| note | published expected = observed = n valid pairs when available; log returns, not simple returns |

### `session.price.range_over_open`

float64, unit `fraction`, producer `session_range_over_open`, available when: the session has an eligible first trade (open), high and low. Ownership: DV1-4 (P15 binding; built-in R1 catalog entry).

| INPUT contract (adapter side) | |
|---|---|
| fields | eligible regular-session trade price and size in event order; the open is session.bar.open, operand label first_eligible_regular_trade (the first eligible regular-session trade price), which can differ from the official daily-bar open (operand label daily_bar_open, used only by core regular_open) and is never replaced by it |
| grain | trade events of one regular session |
| adjustment | none: a ratio of prices of one session |
| session | one regular session |
| history depth | none |
| min samples | 1 eligible trade |
| adapter must | supply regular-session trades with positive integer prices and positive-size eligible trades; never a pre-aggregated open |

| OUTPUT contract (consumer side) | |
|---|---|
| value type | float64 |
| unit | fraction (a fraction, not a percent) |
| basis echo | none |
| unavailable rules | no eligible trade (no_eligible_observations), no rows (absent_input); a non-positive open is refused at admission, never published |
| refusals | INVALID_SCHEMA / OVERFLOW / INVALID_UNIT / INCOMPATIBLE_VERSION / UNKNOWN_FEATURE as listed |
| note | (H - L) / O in batch, update, restore and merge; session.price.range_fraction (H - L) / C is unchanged |

## Exact mathematics

**relative_log_stats**

- **returns**: x_j = ln(Ci_j / Ci_(j-1)) and y_j likewise for the benchmark, natural logarithm of the EXACT rational close ratio; pairs j = t-W+1..t, complete-case joint pairs, means over the same n pairs
- **formulas**: beta = Sxy / Syy_b and rho = Sxy / sqrt(Sxx Syy) with centred sums; the n versus n-1 divisor cancels; same shape as ef3-rel1, different return type
- **numeric**: each logarithm is a Decimal120 evaluation of the exact ratio, sums two-pass in Decimal120, one correctly rounded float64 per published value; cannot be exact rational
- **zero tests**: exact Fraction comparison of the close ratios, never a Decimal variance: Var(y) = 0 iff every benchmark ratio in the n pairs is equal; likewise Var(x). Var(y) = 0 gives zero_denominator for both; Var(x) = 0 with Var(y) > 0 gives beta exactly +0.0 and correlation zero_denominator
- **near zero**: a covariance that is exactly zero in rational terms but not detectable from ratios is published as computed: a Decimal120 value within 1e-100 of zero is published as computed, not forced to 0.0; no fixture depends on it
- **no residual**: no log residual_return is added
- **simple variant**: relative.beta and relative.correlation stay the documented simple-return variants (ef3-rel1, frozen)

**atr_simple_mean**

- **true range**: TR_i = max(H_i - L_i, |H_i - C_(i-1)|, |L_i - C_(i-1)|)
- **window**: TARGET-INCLUSIVE: the N most recent completed sessions ending at the target session (N true ranges, N + 1 closes needed); value = (sum of TR over those N) / N, exact rational, one float64
- **average 20**: the '20-day average' in the V12a condition is the close SMA over 20 sessions INCLUDING the target (history.sma period 20); consumer arithmetic, not an DV1 output
- **missing**: strict: any closure slot not READY gives unavailable with its reason; no skipping, no zero fill; the 12 percent fallback is a consumer rule on status != available
- **no parameter**: no inclusion parameter and no initialization_anchor; history.atr (Wilder) is untouched

**core_spread**

- **eligibility**: unchanged from EF4 I2 (docs/ef4/PATH_PROJECTIONS_CONTRACT_PROPOSAL.md, relative_excess mathematics): per fund start and end facts present and known, end <= cutoff, endpoint age bound, equal action snapshot; a fund that fails is not eligible and the population is partial_universe with values withheld; funds that are individually eligible but misaligned or on different sessions are ineligible for the whole population
- **regular open**: start leg = the open field of the regular-session DAILY BAR of the exact session (official daily-bar open, operand label daily_bar_open), the same operand as M10; end leg = the close of the same session; both legs on one session; window_ns absent. Not the first regular trade, not the first completed intraday bar open. A source with no exact-session daily open gives no start fact: that fund's leg is unavailable (partial_universe). Leg text: the DV1 leg text is profile, slot, op, rev, act in that order (the EF4 grammar is untouched); the optional op token is the operand label; a regular_open start leg is eligible only with op=daily_bar_open, an absent or any other label is not eligible, and op is ignored for prior_close and window_start. The io adapter emits op=daily_bar_open only when the source has the official exact-session daily-bar open, otherwise it omits the leg. Start times of regular_open legs are not compared (both legs are of the exact session, which the session check pins; start alignment applies to window_start only). For core_spread the cutoff may lie after the session close (end-of-day)
- **return**: r_k = end / start - 1, simple, exact
- **range**: max r - min r (the value the deprecated EF4 id publishes)
- **stdev**: population standard deviation, divisor K: sqrt((K sum r^2 - (sum r)^2) / K^2) with K the number of declared funds (design K = 3); exact rational variance; the root is exact when numerator and denominator are perfect squares, else Decimal120 then one float64
- **withheld**: no output when any declared fund is missing: unavailable, never 0

**session_range_over_open**

- **formula**: (H - L) / O over the regular session, exact Fraction, one float64; O is session.bar.open (the first eligible regular-session trade price, as the shipped R1 reduction defines it)
- **modes**: batch, update, restore and merge give the same result
- **admission**: a non-positive open is rejected at canonical admission; a defensive zero denominator would be not_applicable
- **unchanged**: session.price.range_fraction (H - L)/C is unchanged and documented as over close

**window_extreme**

- **window**: the P most recent completed sessions ending at and including the target session
- **extreme basis**: intraday: window_high uses daily highs and window_low uses daily lows; close: both use daily closes; the parameter is not called basis because the result field basis echoes the adjustment basis on every output
- **offset**: sessions before the target, 0 = the target
- **ties**: the latest session wins
- **numeric period**: 253 (design wording 252 prior plus current) or 252 (252 including current) is the design owner's call; the library supports either, both are explicit and no default exists
- **p25 v12b**: history.prior_high / history.prior_low keep serving P25 and V12b with the stated inclusion: N PRIOR completed sessions, high or low field only, target EXCLUDED; no new id. On the intraday basis max(history.prior_high(P-1), current high) equals history.window_high(P) (cross-check fixtures)

## Numeric policy and acceptance

- **publication**: every float64 output is the exact value correctly rounded to nearest-even once; int64 exact; there is no tolerance band in DV1: the library must equal the pinned hex bit for bit
- `exact_plus_zero`: exact 0: bit-exact +0.0, never -0.0
- `exact_float64`: exact rational that is dyadic with numerator below 2^53
- `correctly_rounded`: exact rational (or an exact mathematical identity such as beta = 2) correctly rounded once; library path Fraction or Decimal120
- `decimal_correctly_rounded`: irrational value (log statistics, square roots): Decimal120 evaluation rounded once to float64
- `exact_integer`: int64 offsets
- `exact_bool`: none in DV1
- **logarithm**: ln of the EXACT rational close ratio (not a difference of logarithms of the closes) at 120 significant digits; the expander recomputes at 250 digits with an own series
- **near tie rule**: if a Decimal120 value lies within 1e-100 relative of the midpoint of two adjacent float64 values the two implementations may disagree; the contract excludes this by construction: the expander requires every pinned irrational value to be at least 1e-60 relative away from every float64 midpoint; on such an input outside the fixtures an implementation rounds the Decimal120 value half to even
- **tiny values**: a computed value within 1e-100 of zero is published as computed (not forced to 0.0) except where exactness is decided by ratios (Var(x)=0 gives beta exactly +0.0)
- **zero decisions**: all zero and tie decisions use exact integer or Fraction comparison; no epsilon anywhere

## Normative tie table

| Tie | Rule | Fixture |
|---|---|---|
| equal extreme values inside the window | the latest session wins (smallest offset) | WX01 |
| equal closes on close basis | the latest session wins | WX07 |
| all highs equal | offset 0 | WX08 |
| zero range in range_over_open | exactly +0.0 (available) | RO02 |
| all benchmark ratios equal | zero_denominator by exact ratio equality | RL05 |
| all instrument ratios equal | beta exactly +0.0, correlation zero_denominator | RL06 |
| equal returns across funds | range and stdev exactly +0.0 | CS05 |
| known_at equals K | known | AT15 |
| min_pairs equals n | available | RL07 |

## Deprecation of `core.benchmark_return_dispersion_fraction`

Wording: "RANGE of core returns (deprecated name), not dispersion; use core.benchmark_return_range_fraction (same value) or core.benchmark_return_stdev_fraction". description-only change in discovery text (DV1-3), recorded as an errata entry in docs/ef4/EF4_ERRATA.md now; the id keeps publishing the range unchanged; removal at the already scheduled EF4 next-contract-version migration (ef4-rel1 becomes ef4-rel2); no frozen EF4 file is edited. Equal-value fixtures against the frozen EF4 fixtures (read only): CS01, CS06, CS07.

## Availability, quality, evidence, knowledge and refusals

Reason precedence: `absent_input`, `unknown_availability`, `future_knowledge`, `null_field`, `ineligible`, `governed_gap`, `future_market`, `partial_universe`, `insufficient_history`, `no_eligible_observations`, `zero_denominator`.

- all applicable reasons retained in lexical order; status follows the first applicable reason in precedence; a value is null exactly when the status is not available; unavailable is never zero. Available implies observed == expected, except relative.* where an available row publishes expected = observed = n valid pairs and carries lost-pair causes as reasons
- count atr: expected N+1, observed READY closure slots
- count window: expected P, observed READY slots for the output's field
- short history: slots that exist inside the grid are checked as middle slots (ATR: high, low and close; window: the output's field) and counted in observed; observed is the number of READY slots inside the grid, so a closure or window that starts before the first session reports observed below expected (AT14 and WX15 pin the all-ready case)
- count relative: unavailable rows expected W observed n; available rows n and n
- count core: expected K, observed eligible funds
- count range_over_open: expected 1, observed 1 or 0
- evidence: target slot first, then the remaining required slots ascending (core: legs in declared order start then end; relative: instrument then benchmark per slot; core: slot = 2k for the start leg and 2k+1 for the end leg of declared fund k, the fixture witnesses are still written leg:<fund>:<kind> until the closeout renames them); a row id is slot:<index> bound to the role input id (fixture witnesses are written <role>/slot:<index>); unavailable outputs emit none; evidence_limit 0..10000 truncates the list, never the value, and bounds the combined evidence list across the selected outputs of one call (outputs in lexical order, so a joint call cuts mid-list; RL20 pins it)
- market cutoff: DV1 may place the market cutoff inside the target session (from its open to the last grid session close); a slot that ends after the cutoff is future_market (the row is not delivered); a delivered row past the cutoff is refused as BOUNDS. This is DV1 only; the stricter EF3 envelope is unchanged.
- knowledge: as EF5: a bar or fact is KNOWN iff original known_at is non-null and <= K; null is unknown_availability, later than K is future_knowledge; the producer enforces it identically in known_at and reconstruction modes
- refusal stages wire > shared > config > version > identity > data: a refusal raises the code of the first stage with a fault; every refusal fixture is single-fault and audited by the independent expander, which collects every trigger
- coverage admission (shared, every producer): rows delivered with no per-slot coverage entry on any row are INVALID_SCHEMA (RF11); coverage declared for only some of the delivered slots is INCONSISTENT_IDENTITY (RF73)
- config checks (every producer with an adjustment basis; core_spread has none), in the stage order unit and adjustment checks, cutoff, then the policy label, then identity: the declared adjustment must be the pair unadjusted with raw-v1 or split_adjusted with split-factors-v1, else UNSUPPORTED_ADJUSTMENT (RF21); the price currency must be three uppercase letters, else INVALID_UNIT (RF22)

## Data-capability matrix

data each output needs, client or server, per source; a source that cannot supply an input yields the documented unavailable result, never a default.

| data needed | used by | client side | server side | supplied data (any source) | if absent |
|---|---|---|---|---|---|
| daily high, low, close with original known_at and declared coverage | history.atr_simple_mean, history.window_* | chooses instrument, target, N or P, basis | admission, readiness, arithmetic | unverified | absent_input / unknown_availability / insufficient_history |
| daily closes of instrument and benchmark on one grid | relative.log_return_* | chooses benchmark, window, min_pairs | admission, pairing, logarithms, statistics | unverified | absent_input / insufficient_history |
| daily-bar open of the exact regular session and same-session close per core fund | core.benchmark_return_* | declares funds and profile | eligibility, returns, spread | unverified (a source without an exact-session daily open yields no start leg) | partial_universe |
| regular-session eligible trades | session.price.range_over_open | chooses the session | reduction | unverified | no_eligible_observations / absent_input |
| corporate-action facts | none in v1 | not consumed | not consumed | not applicable | not applicable |

source cells stay unverified until provider terms and field availability are checked; nothing here claims a provider supports a field.

## No defaults (defaults ledger)

no default anywhere: period, basis, window, min_pairs, benchmark id, core profile and funds, tolerances, evidence_limit, the adjustment basis and adjustment_spec.policy_version, the price unit and K must be supplied; a missing item is INVALID_CONFIG or a typed shared/identity refusal.

## Fixtures

compact, NOT canonical wire. K = 100, default known_at 50. Slots 0..n-1 in grid order, the target is the last unless `target` names an earlier index (later slots are delivered and must not matter). ATR/window: slots [H,L,C] (a null cell is a null field), `slots_fill` {n, base, set} expands a long series. Relative: `inst` and `bench` are lists of closes (an integer, null, 'absent', 'gap', 'forming' or {row, ka}) or the string 'absent'. `forming` means the slot is still forming at the market cutoff: the row is not delivered (in either series) and the library reads it as future_market; a fixture that delivers a forming slot is invalid. Core: facts {inst, kind start|end, t, p, ss, pf, act, rev, ka, op} with the cutoff C and `decoys` (first_trade_price, first_bar_open, prior_close per fund) for wrong-operand values. Range over open: `trades` [price, size] in event order, `chunks` index ranges for the update/restore/merge modes. `delivery` (slot order delivered), `coverage`, `capability`, `delivered_after_cutoff`, `batch_instrument` are refusal-only keys. Float results carry the exact rational (or a 50-digit decimal for irrational values), the float64 and its hex. Refusal fixtures are mutations (set/delete on fixture.*) of a named result fixture. A compact row of the wrong width is a fixture-load error of the gate decoder (RF03 records the wire-stage case), not a library refusal; the library takes typed rows.

20 ATR (AT01 to AT20), 25 window extreme (WX01 to WX25), 23 log relative statistics (RL01 to RL23), 21 core spread (CS01 to CS20), 11 range over open (RO01 to RO10) result fixtures and 73 refusal fixtures (RF01 to RF73, 12 distinct codes). Every expected value carries a hand-derived `hand_check` line; the independent expander `tools/contract_fixtures/dv1_fixture_expand.py` recomputes every value (logarithms with its own 270-digit series), every rival value, the prior-high cross-check, the V12a binding, the EF4 equality and the single-fault audit of every refusal. Gate: `python tools/verify_dv1_fixtures.py`.

Wrong-convention fixtures: every output id has at least one fixture whose `wrong_convention` list names a rival convention and its computed value; the value of the id must differ from every listed rival (except the two records marked equal, which document where conventions coincide: AT02, AT04)

| Fixture | Group | Description |
|---|---|---|
| AT01 | target_inclusive_mean | N=3 on eight sessions with a gap (session 6 opens above the prior close 17): the mean of the TRs of sessions 5, 6, 7 |
| AT02 | period_one | N=1: the single TR of the target session |
| AT03 | wilder_differs | N=5 on the eight sessions: simple mean of TR3..TR7 |
| AT04 | wilder_anchor_trick | N=5 with exactly N true ranges (six sessions): the Wilder seed IS the simple mean |
| AT05 | v12a_binding | N=20 over 22 sessions: ATR and the 20-session close SMA both include the target (V12a binding) |
| AT06 | oldest_slot_close_only | N=7: the oldest session only needs its close; high and low null there |
| AT07 | target_close_not_read | N=3: the target's close is null but TR needs only its high and low |
| AT08 | null_field | N=3: session 6 high is null: no skipping, no zero fill |
| AT09 | absent_input | N=3: session 5 not delivered |
| AT10 | governed_gap | N=3: session 6 inside a declared coverage gap |
| AT11 | unknown_availability | N=3: session 6 known_at null |
| AT12 | future_knowledge | N=3: session 6 known_at after K |
| AT13 | future_market | N=3: the target session is still forming at the market cutoff |
| AT14 | insufficient_history | N=8 with eight sessions: nine closure slots needed |
| AT15 | known_at_boundary | N=3: session 6 known_at equals K exactly |
| AT16 | evidence_limit | N=3 with evidence_limit 2: the witness list is truncated, the value is not |
| AT17 | split_adjusted_basis | N=3 with adjustment split_adjusted: arithmetic equal to AT01, basis echoed |
| AT18 | prefix_target | N=3 with an explicit target (slot 5): later sessions are delivered and must not matter |
| AT19 | flat_zero | N=2 on flat sessions: ATR exactly +0.0 (available, never unavailable) |
| AT20 | price_scale | N=3 at price scale 2 (coefficients are hundredths): value is the mean divided by 100 |
| WX01 | intraday_basis_tie | P=10 on the intraday basis: the maximum high 60 occurs on sessions 2 and 4, the latest wins |
| WX02 | close_basis | P=10 on the close basis: the extremes are of the closes, not of the highs and lows |
| WX03 | short_period | P=5 (sessions 5..9) on the intraday basis |
| WX04 | period_one | P=1: the window is the target session alone |
| WX05 | target_extreme_prefix | P=3 with an explicit target (session 8): the target is the maximum (offset 0); session 9 is delivered and ignored |
| WX06 | tie_midwindow | P=4 at target 5: highs 60,58,60,57: the later 60 wins |
| WX07 | close_tie | close basis with equal closes 10 on sessions 1 and 3: the later wins |
| WX08 | all_equal_highs | intraday basis, every high 10: the offset is 0 (the target wins every tie) |
| WX09 | period_253 | P=253 (252 prior sessions plus the target, the design wording): the extreme sits on session 0, 252 sessions back |
| WX10 | period_252 | P=252 on the same sessions (the width of 252 sessions including the target): session 0 is out of the window |
| WX11 | period_253_close | P=253 on the close basis |
| WX12 | period_252_close | P=252 on the close basis |
| WX13 | p25_prior_equivalence | P=127 intraday basis, target high below the old extreme: equals max(history.prior_high(126), H_t) |
| WX14 | p25_target_new_high | P=127 intraday basis, the target makes a new high: offset 0 while history.prior_high(126) excludes it |
| WX15 | insufficient_history | P=11 on ten sessions |
| WX16 | absent_input | P=5: session 6 not delivered |
| WX17 | governed_gap | P=5: session 7 in a declared coverage gap |
| WX18 | unknown_availability | P=5: session 8 known_at null |
| WX19 | future_knowledge | P=5: session 8 known_at after K |
| WX20 | independent_readiness | P=5 intraday basis: session 7 high is null: the high outputs are null_field, the low outputs stay available |
| WX21 | close_basis_ignores_hl | P=5 close basis: session 7 high and low are null but only closes are read |
| WX22 | future_market | P=5: the target session is still forming |
| WX23 | price_scale | P=5 at price scale 2: prices are coefficient / 100 |
| WX24 | evidence_limit | P=5 with evidence_limit 3: witnesses truncated |
| WX25 | split_adjusted_basis | P=5 with adjustment split_adjusted: values equal WX03, basis echoed |
| RL01 | exact_identity_beta2 | instrument close ratios are the squares of the benchmark ratios: log returns satisfy x = 2y exactly |
| RL02 | exact_identity_negative | instrument ratios are the reciprocals of the benchmark ratios: x = -y exactly |
| RL03 | generic_positive | four log returns on small moves, positive relation |
| RL04 | large_move_pair | a 20 percent instrument move paired with a 1 percent benchmark move |
| RL05 | zero_benchmark_variance | benchmark ratios all equal 11/10 at different magnitudes: zero variance decided by exact ratio equality |
| RL06 | zero_instrument_variance | instrument ratios all equal, benchmark varies: beta is exactly +0.0, correlation unavailable |
| RL07 | lost_pairs_available | one benchmark close absent loses two pairs; three pairs remain and min_pairs is 3 |
| RL08 | lost_pairs_unavailable | the same data with min_pairs 4: three pairs are fewer than four |
| RL09 | insufficient_history | window 5 but only four closes: the window is not wholly inside the grid |
| RL10 | unknown_availability | window 4: benchmark close of slot 3 known_at null |
| RL11 | future_knowledge | window 4: benchmark close of slot 3 known_at after K |
| RL12 | governed_gap | window 4: instrument slot 2 inside a declared gap |
| RL13 | null_field | window 4: instrument close of slot 2 null |
| RL14 | future_market | window 4: the target benchmark close is still forming |
| RL15 | known_at_boundary | window 4: benchmark close of slot 3 known_at equals K |
| RL16 | absent_role | the benchmark role is not delivered |
| RL17 | two_point | window 2, two pairs: correlation is exactly +1 in mathematics, beta the log-return slope |
| RL18 | negative_generic | generic negative relation |
| RL19 | near_constant_benchmark | benchmark ratios differ by about 1e-12: variance about 1e-24 is NOT zero |
| RL20 | evidence_limit | RL03 data with evidence_limit 3 |
| RL21 | split_adjusted_basis | RL03 data with adjustment split_adjusted: values equal RL03, basis echoed |
| RL22 | prefix_target | RL03 data with an explicit target (slot 3) and window 3; slot 4 delivered and ignored |
| RL23 | window_slice | window 3 on five closes: the oldest slot is outside the window |
| CS01 | prior_close_ef4_equal | prior_close profile, three core funds +1/10, +1/20, -1/100: the range output equals what the deprecated id publishes (EF4 CB01) |
| CS02 | regular_open_design_binding | regular_open profile (M11 binding): daily-bar opens 100, closes 100, 101, 105: returns 0.00, 0.01, 0.05 |
| CS03 | perfect_square | K=4 regular_open returns 0, 0, 1/5, 1/5: the population variance is the perfect square 1/100 |
| CS04 | two_funds | K=2 regular_open returns 0 and 1/10 |
| CS05 | equal_returns | K=2 equal returns 1/20: range and sd exactly +0.0 |
| CS06 | window_start_ef4_equal | window_start profile (EF4 CB07 inputs): range equals the deprecated id's EF4 value |
| CS07 | prior_close_four_funds | prior_close profile (EF4 CB03 inputs): two up two down by 1/10 |
| CS08 | start_absent | B2 daily-bar open not available: the leg is unavailable, the population is partial |
| CS09 | wrong_operand | B2 start fact carries the first regular trade price, not the daily-bar open |
| CS10 | other_session_open | B2 start fact is the daily open of the previous session |
| CS11 | end_after_cutoff | B2 end witness after the market cutoff |
| CS12 | end_future_knowledge | B2 end fact known_at after K |
| CS13 | profile_mismatch | B2 start fact is a prior_close fact under the regular_open profile |
| CS14 | misaligned_ends | member end witnesses 990 and 999 differ by 9 > tolerance 5 |
| CS15 | no_facts | no leg facts delivered |
| CS16 | end_unknown_availability | B2 end fact known_at null |
| CS17 | action_snapshot_mismatch | B2 start and end facts carry different action snapshots |
| CS18 | evidence_limit | CS02 data with evidence_limit 3 |
| CS19 | stale_endpoint | B2 end witness older than max_endpoint_age_ns (920, age 80 > 50) |
| CS20 | different_sessions | B2 start and end are both on session S2 while the others are on S1 |
| CS21 | operand_official_open_vs_first_trade | regular_open K=2: official daily-bar opens 10020 and 20000; the first regular trades were 10000 and 19990 |
| RO01 | open_vs_close | O100 H105 L100 C103: (H-L)/O differs from the shipped (H-L)/C |
| RO02 | zero_range | all trades at one price: range 0 |
| RO03 | close_below_open | O200 H220 L180 C190 |
| RO04 | low_after_open | O50 H52 L48 C49 |
| RO05 | price_scale | prices at scale 2: the ratio is scale free |
| RO06 | modes_update_merge | R1 split in two chunks: update, restore and merge give the batch result |
| RO07 | non_dyadic | O7 H9 L4 C6 |
| RO08 | zero_size_first_trade | a zero-size first trade is not eligible: the open is the first eligible trade |
| RO09 | no_eligible_trades | only zero-size trades: no open exists |
| RO10 | absent_session | no trade rows delivered |
| RO11 | operand_first_trade_vs_official_open | first eligible trade 100.00 but the official daily-bar open is 100.20: P15 uses the first trade |

## Decisions, open questions, non-goals

- **DP-V1** (Naming): ids carry the convention in the name (relative.log_return_beta, history.atr_simple_mean, core.benchmark_return_range_fraction / _stdev_fraction, session.price.range_over_open, history.window_*); relative.beta_log rejected [PO ruling 2026-10-29]
- **DP-V2** (Hosting): new package equity_features.dv1; default registry, EF3/EF4 frozen contracts and EF5 byte-identical; built-in range_over_open is the one R1 catalog change (DV1-4, coordinated bump) [Architect design, PO approved]
- **DP-V3** (Units): E9 slash style; one additive unit `sessions` (int64) for the window offsets, in the DV1 contract only; reused: currency/share, fraction [proposal]

Open questions for the PO:


Non-goals: no library, io or worker code in DV1-0; no change to any shipped id meaning; no log residual_return; no thresholds, crossings or consumer policy; no timing or efficiency claim of any kind; no claim of real-data readiness or product availability: every statement is about a library calculation on synthetic data.

## Layer responsibilities

- **library**: admission, readiness, exact arithmetic, logarithms and roots at the stated precision, quality, evidence and every refusal; pure and deterministic
- **io**: maps the supplied series to the INPUT contract of each header exactly as supplied (fields, grain, basis, session, history depth); selects the version known at K; never sorts, fills, aligns, drops or chooses a window, basis or period
- **worker**: routes selected outputs, persists the library result unchanged; direct, adapter, worker and stored results are identical including refusal class

Pre-merge command: python tools/verify_dv1_fixtures.py (runs tools/contract_fixtures/dv1_fixture_expand.py, pins the counts); then tools/check_equity_delivery_replan.py for header and manifest parity.
