# EF4 quote dynamics and VWAP path contract - proposal

Prepared for EQ-159 [#493](https://github.com/atulsrivas1/equity-features/issues/493) (microprice and selected quote dynamics) and EQ-160 [#494](https://github.com/atulsrivas1/equity-features/issues/494) (VWAP slopes and selected path statistics), for consumption by the EF4 I/O and worker tasks and release acceptance EQ-163. **This is a contract proposal, not accepted by any review; every convention (DP-*) and former open question (OQ-*) below is an author decision, pending coordinator and owner review, and the contract carries a proposed freeze statement.** It is contract preparation only: it admits no Ready state, implementation, numerical acceptance, release or performance claim. Trade windows and signing (EQ-158 #492), EQ-172 and the tape and path-efficiency contracts are by other authors and are neither specified nor consumed here.

Companion data: [QUOTE_VWAP_CONTRACT_PROPOSAL.json](QUOTE_VWAP_CONTRACT_PROPOSAL.json) holds the machine-readable producers, headers, roles, fact schemas, mathematics, quality table, 30 quote result fixtures, 39 VWAP result fixtures and 80 typed-refusal fixtures. Expected values are hand-derived: each headline value is written by hand in the fixture definition as an exact fraction. An independent recompute harness that imports only the Python standard library (and nothing from the equity packages) recomputes every fixture from its inputs with exact `fractions.Fraction` arithmetic and compares status, reasons, expected and observed counts, the exact value, the float64, `float.hex` and the witnesses; it covers all 69 result fixtures (507 selected outputs, 260 with a value). For the 80 refusal fixtures it applies each executable mutation recipe to its base fixture, evaluates the shared-validator rules (transcribed from `validation.py`) and the library rules, and requires that exactly the one stated rule fires with the stated error code and layer. It also checks identical-result pairs and the absence of hardcoded identities. A separate reviewer comparator, written from this document, was run as well. The harnesses are scratch tools kept outside the repository, like the EF3 scratch script. The library was not imported, run or tested. Fixtures use compact notation (not canonical wire) and need expansion into canonical packets.

## Authority and inspected sources

Read-only inputs: the issues EQ-159 (including the reviewed 21 October 2026 ownership clarification of `quote.sampled.maximum_spread` and `quote.sampled.maximum_midpoint_bps`) and EQ-160; `docs/EQUITY_DELIVERY_REPLAN.md` (EF4: ordered trade/quote/path kernels, trade/quote mapping and compatible supporting histories, persisted window and path results); the accepted foundations `docs/features/QUOTE_FORMULAS.md` (classification, sampling, continuous carry), `INTRADAY_FOUNDATIONS.md` (governed grid, exact arithmetic, availability and compatibility), `EF1_PATHS.md` (sampled paths, original known_at, completeness, evidence) and `EF1_ANCHORS.md` (actual notional, anchored totals); `docs/api/CONTINUOUS_QUOTES.md`; the merged EF3 contract `docs/ef3/ROBUST_PACE_CONTRACT_PROPOSAL.*` (structure, fixture rigor, numeric policy, reason precedence, slot-reason mapping); and the shared validators and enums in `packages/contracts` (`inputs.py`: `DataKind.QUOTE` rows are full bid/ask with sizes, sampling `trade_snapshot` or `continuous`; `DataKind.TRADE` and `BAR`; `results.py`, `errors.py`), so every fixture and refusal is constructible with existing codes. The statistics are standard publicly documented definitions (spread, midpoint, size-tilted microprice, cumulative volume-weighted average price, endpoint and ordinary least squares slope) specified from first principles with each varying convention chosen explicitly. No private source, threshold or default is used or copied.

## Unchanged boundary

Existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult`, `Status`, `Reason`, `ErrorCode` and scalar `ValueType` values (`int64`, `float64`); the shared QUOTE, TRADE, BAR and REFERENCE validators; the frozen ef1-contract1 and every accepted core, R17, EF1, EF2 and EF3 header; the accepted `session.quote.sampled_spread`, `session.quote.state_counts` and `session.quote.time_weighted_spread` (unchanged, not reused, no duration weighting here) and the accepted EF1 anchored totals. No new DataKind, DTO, result codec, scheduler or default, no new error code, no new validator, no change to a shared validator. This packet is additive: two new producers and sixteen new headers, three new reference `fact_kind` values, new policy labels and a new catalog entry set whose digest is new (existing entries and digest inputs do not change). Update, restore and merge are unsupported (`UNSUPPORTED_CAPABILITY`); batch and full replay only. A sibling amendment document follows a freeze, as for EF3.

## Producers and config identities

| Item | Quote dynamics (#493) | VWAP path (#494) |
| --- | --- | --- |
| Identity | `ef4.quote_dynamics` | `ef4.vwap_path` |
| Algorithm / schema | `ef4-quote-dynamics-v1` / `1` | `ef4-vwap-path-v1` / `1` |
| Policy label | `ef4-quote1` | `ef4-vwap1` |
| Parameters (no defaults) | `policy_version`, `sampling` (`trade_snapshot`, `continuous`; must equal the quotes batch sampling), `evidence_limit` (0..10000) | `policy_version`, `series_source` (`trade`, `bar`, `prepared_window`), `grid_version` (exactly when the source is `bar` or `prepared_window`), `series_policy_id` (exactly when the source is `prepared_window`), `evidence_limit` |
| Roles in order | `bounds`, `quotes` | `bounds`, `grid`, `trades`, `bars`, `proof` |
| ConfigSpec | PriceUnit mandatory; adjustment declared once and shared by every role | same |

A policy label names the whole convention set of its version (classification, size rule, microprice, change rule, tie rule, interval and cutoff rule, series source, anchor, time axis, estimator, missingness mapping, rounding). An unsupported label is `INCOMPATIBLE_VERSION`; a future convention needs a new label, never a silent change. Entity, instrument, session, role, snapshot, grid and series identifiers are call parameters and are never fixed by this contract (DP-R1). Evidence limits reuse the 0..10000 range of EF3.

## Outputs and headers

| Feature id | dtype | unit | Producer | Available when |
| --- | --- | --- | --- | --- |
| `quote.sampled.maximum_spread` | float64 | currency/share | quote | interval ready, at least one valid observation |
| `quote.sampled.maximum_midpoint_bps` | float64 | bps | quote | same closure |
| `quote.microprice.last` | float64 | currency/share | quote | final admitted observation valid with both sizes positive |
| `quote.microprice.last_offset_bps` | float64 | bps | quote | same closure |
| `quote.microprice.mean` | float64 | currency/share | quote | every valid observation has both sizes present, at least one with both positive |
| `quote.change.midpoint_bps` | float64 | bps | quote | continuous sampling, at least two valid observations |
| `quote.change.spread` | float64 | currency/share | quote | same closure |
| `quote.change.pair_count` | int64 | pairs | quote | continuous sampling, interval ready (0 is a value) |
| `quote.change.midpoint_change_count` | int64 | pairs | quote | same closure |
| `vwap.path.last` | float64 | currency/share | vwap | path ready, at least one point |
| `vwap.path.maximum` | float64 | currency/share | vwap | same closure |
| `vwap.path.minimum` | float64 | currency/share | vwap | same closure |
| `vwap.path.point_count` | int64 | points | vwap | anchor, proof and every slot's volume or size ready (0 is a value) |
| `vwap.path.change_bps` | float64 | bps | vwap | path ready, at least two points |
| `vwap.slope.endpoint` | float64 | currency/share/second | vwap | at least two points and a positive time span |
| `vwap.slope.ols` | float64 | currency/share/second | vwap | at least two points and a positive time variance |

Order: lexicographic by feature id within a producer. Each output has its own required operands, expected and observed counts and independent readiness; an unrelated missing operand never blocks a ready output (Q11 and Q12: maxima, change and counts stay available while the microprice mean or last is blocked by null sizes; V08: `vwap.path.point_count` stays available while every price-bearing output is blocked by a null notional). A different config (sampling mode, series source, grid) is a different result. New unit strings are `pairs` and `points`; `currency/share/second` is the existing price unit over time (OQ-6).

## Inputs and roles

Value basis. Quote and trade prices, and bar notionals, are positive int64 (notional: decimal128) coefficients at `ConfigSpec.price_unit.scale` (0..18) in one currency and one adjustment basis; a quote side that is null or not positive is an invalid market state and is counted, not refused; an eligible trade must have a non-null positive price and size (the shared validator raises `INVALID_SCHEMA` otherwise, so `null_field` is not reachable on the trade source). Sizes and volumes are int64 shares, `0 <= v <= 2^63-1`; a negative one is `BOUNDS`. All comparisons, sorts, midpoints, microprices, cumulative sums and regression sums run on exact integers or `Fraction`s; the coefficient is divided by `10^scale` only when a value is published, so no float enters a comparison and no `OVERFLOW` path exists inside the arithmetic (Q24, V23 exceed int64 internally and stay exact). Every row declares the config adjustment basis (`UNSUPPORTED_ADJUSTMENT` otherwise). There is no acquisition, clock or I/O. Time is exact UTC int64 nanoseconds.

| Role | Kind | Content |
| --- | --- | --- |
| `bounds` | REFERENCE | exactly one `ef4.interval.bounds` fact: the declared half-open interval [S, E); S is also the VWAP anchor |
| `quotes` | QUOTE | full normalized bid/ask state per admitted row; sizes optional; batch sampling `trade_snapshot` or `continuous` with a declared IntervalCoverage; `event_ns` in [S, E) and before the cutoff |
| `grid` | REFERENCE | `ef4.window.edge` facts (bar and prepared sources): absolute edges, first S, last E, `text` = `grid_version` |
| `trades` | TRADE | trade source only: eligible flag, price, size, event time and order; declared IntervalCoverage |
| `bars` | BAR | bar and prepared sources: one row per grid slot with volume and actual notional; a slot may instead be declared incomplete |
| `proof` | REFERENCE | prepared source only: one `ef4.series.proof` fact whose `text` equals `series_policy_id` |

Fact schemas are in the JSON `reference_fact_schemas`: `reference_id` is `x1:B(id)` as in EF3, `price`, `factor_num` and `factor_den` are null, rows within one (instrument, session) group are ordered by `(effective_start_ns, reference_id)`, and `known_at_ns` is the original knowledge, nullable. The shared validators already enforce QUOTE/TRADE/BAR duplicate, order, interval, positivity and zero-volume rules and the REFERENCE duplicate, order and bounds rules; the library adds only identity, bounds-against-interval and mismatch checks that use existing codes. The proof fact binds identity only: it does not carry series values. The exact split, read from `packages/contracts/.../validation.py`, is in the JSON `shared_validator_split`: the shared validator raises trade duplicates, order and cutoff, `INVALID_SCHEMA` for an eligible trade with a null or nonpositive price or size (RV10, RV11, RV42), bar interval, duplicate, overlap and cutoff rules, zero-volume bars with OHLC or a notional other than null or 0 (`INVALID_SCHEMA`, RV14), positive-volume bars with OHLC columns whose notional is outside [low x volume, high x volume] (`INVALID_SCHEMA`, RV43), negative quantities, and the REFERENCE duplicate, order and `start >= end` rules (RQ07, RV17). The library adds: interval membership of rows (before S, at or after E), `E > C` for bar sources, a positive notional on a positive-volume bar when no OHLC columns are delivered (`INVALID_SCHEMA`, RV13), and every identity, grid, proof, role, sampling, unit, basis and config check.

## Exact mathematics

### Quote observations (EQ-159)

For an admitted row with bid b and ask a (coefficients): invalid if either is null or not positive; otherwise d = a - b: normal d > 0, locked d = 0, crossed d < 0 (DP-Q4). Valid means normal or locked. For a valid observation the cash spread is s = a - b (published s/10^scale), the midpoint m = (a + b)/2 exactly (never rounded to a tick) and its own basis points z = 10000 s / m = 20000 (a - b)/(a + b) (locked gives 0). Sizes Qb, Qa are int64 shares; a valid observation is size-eligible when both are positive (DP-Q5) and then its microprice is

mp = (b Qa + a Qb) / (Qa + Qb), the midpoint tilted toward the side with the smaller displayed size,

published as mp/10^scale; a locked quote gives mp = b = a. The offset is 10000 (mp - m)/m in basis points (DP-Q6). Let V be the valid observations, Z the size-eligible ones, F and L the first and last element of V and fin the final admitted observation, all in the admitted total order (event_ns, order_key, event_id).

Outputs (published as one correctly rounded float64 or exact int64):

- `quote.sampled.maximum_spread` = max over V of s; `quote.sampled.maximum_midpoint_bps` = max over V of z, each quote's own midpoint, never the maximum spread over another midpoint and never a ratio of means (Q04). The maximum is taken over all admitted valid observations whatever the evidence limit; ties select the earliest observation by (event_ns, order_key, event_id); the limit changes neither the value, quality nor the primary witness (Q03, Q05, Q06) (DP-Q10).
- `quote.microprice.last` and `quote.microprice.last_offset_bps` use fin only. If fin is invalid, crossed or size-ineligible the output is `not_applicable`/`no_eligible_observations`; the previous valid quote is never carried through it (Q10, Q13) (DP-Q7).
- `quote.microprice.mean` = (sum of mp over Z)/|Z|, an equal-observation mean: update-weighted under continuous sampling and snapshot-weighted under trade_snapshot, not size-weighted across observations and not time-weighted (DP-Q8). A valid observation with a null size makes it `null_field` (Q11); a zero size merely removes the observation from Z (Q10).
- `quote.change.midpoint_bps` = 10000 (m_L - m_F)/m_F and `quote.change.spread` = s_L - s_F over the first and last valid observations, which must be two observations (one gives `insufficient_history`, expected 2, observed 1; none gives `no_eligible_observations`). `quote.change.pair_count` counts pairs of observations adjacent in the admitted total order that are both valid; `quote.change.midpoint_change_count` counts those whose midpoints differ. An invalid or crossed observation between two valid ones breaks adjacency; equal-time ordered updates are adjacent (Q25). These four outputs require continuous sampling (DP-Q9).

Sampling (DP-Q2). The config `sampling` must equal the quotes batch metadata. Trade-snapshot quotes never satisfy a continuous requirement and continuous quotes are never relabelled snapshot-weighted: a mismatch, and the selection of a change output on a snapshot batch, are `UNSUPPORTED_SAMPLING` refusals (RQ19 to RQ21), not missing inputs. Repeated identical prices at distinct admitted snapshots stay distinct observations (Q26). The two modes are never pooled and the mode, entity, source, order, scale and currency, basis, cutoff and original availability are part of the result identity; Q02 shows identical values under a different identity.

Interval, cutoff and coverage (DP-Q3, DP-Q11). The target is the declared interval [S, E) and the market cutoff C; E > C is `future_market` (Q22); a row outside [S, E) or at/after C is a `BOUNDS` refusal. There is no seed, pre-open state, expiry or staleness limit: the outputs are statistics of the sampled observations, and a long silence under complete coverage is neither an error nor filled (Q28). Delivery completeness is the declared IntervalCoverage: incomplete is `governed_gap` (Q17); zero rows with complete coverage is an observed empty interval (Q14); zero rows without coverage and an undelivered role are `absent_input` (Q15, Q16). A cutoff replay is the prefix property: the outputs at E depend only on the rows before E known by K (Q23).

### VWAP path (EQ-160)

Series source (DP-V1) is an explicit parameter. A point is (x, N, V): for the trade source each eligible trade is (event_ns, p q, q); for the bar and prepared_window sources each positive-volume window is (end_ns, actual_notional, volume), using the supplied actual notional and never close times volume (V02 carries a bar close that would give a different notional) (DP-V3). Ineligible trades are not operands: their price, size and knowledge are never read (V01, V19). A covered zero-volume window is a ready slot that contributes no point and no weight (V05, V34) (DP-V7).

The path is the anchored cumulative VWAP (DP-V2): W_k = (N_1 + ... + N_k)/(V_1 + ... + V_k) for k = 1..n, reset at the declared anchor S with nothing carried across intervals (DP-V5), published as W_k/10^scale. This is not an average of window VWAPs (V30).

Time axis (DP-V4). x is wall-clock UTC nanoseconds: the trade event time, or the completed window end for bar sources (the content of a window is known only at its end). It is not an index, a count or a volume axis; slopes are per second by the exact factor 10^9. Spacing is whatever was supplied (irregular grids, V01 and V02): no resampling and no fill (DP-V6).

Outputs: `vwap.path.last` = W_n, `vwap.path.maximum` = max W_k, `vwap.path.minimum` = min W_k (ties take the earliest point, DP-V13), `vwap.path.point_count` = n, `vwap.path.change_bps` = 10000 (W_n - W_1)/W_1, `vwap.slope.endpoint` = (W_n - W_1) 10^9/(x_n - x_1)/10^scale and `vwap.slope.ols` = 10^9 (n Sxw - Sx Sw)/(n Sxx - Sx^2)/10^scale over the n path points with equal weights (DP-V11). n = 0 gives `no_eligible_observations` (point_count 0 is a value); n = 1 gives `insufficient_history` (expected 2, observed 1) for change and both slopes (V20); a zero time span or zero time variance gives `not_applicable`/`zero_denominator` while level, change and count stay available (V21). Negative values are not clamped (V25) and a flat path gives exact +0.0 (V26).

Supplied compatible series (DP-V9). With `series_source` prepared_window the windows are accepted exactly as supplied, with no trade-window recomputation and trades never read, when: one `ef4.series.proof` fact has `text` equal to `series_policy_id`, the grid text equals `grid_version` with first edge S and last edge E, each bar equals a grid slot, and unit and basis are compatible. The proof is an identity binding by the preparer; the arithmetic is identical to the bar source (V02 equals V03), and one prepared series serves several outputs and configs without recomputation (V04 equals the subset of V03). Whether the preparer computed N and V correctly belongs to the preparer's own tests.

Missing intervals and corrections (DP-V8, DP-V10). The grid fixes expected slots. A slot with no row and a declared incomplete coverage is `governed_gap` (V06); a slot with neither is `absent_input` (V07); either blocks every output because the cumulative path depends on all earlier points. A correction is a new batch revision: one batch holds exactly one version of a row or slot, the library never chooses between versions, a corrected version known after K is `future_knowledge` (V14) and one known by K is used (V15), while the earlier result is unchanged (V13).

## Pinned edge cases

- **Crossed and locked:** locked contributes spread 0 and bps 0 (Q08); crossed is excluded from every value, counted as a ready observation and breaks adjacency (Q01, Q09, Q13).
- **Zero and null size:** zero size removes an observation from the microprice population only; null size on a consumed valid observation is `null_field`; sizes are never read by maxima, change or counts (Q10, Q11, Q12).
- **Invalid prices:** a null, zero or negative side is a counted invalid state, not a refusal (Q09, Q27).
- **Trade-snapshot versus continuous:** no relabelling, no pooling, change outputs continuous only (RQ19 to RQ21, Q02, Q26).
- **Zero-volume slots:** following EF1_PATHS, the `known_at` and notional of a slot whose volume is exactly 0 are not operands and are not read (V35); a null volume is different and its knowledge is read (V09). A notional of 0 on zero volume is allowed, as the shared validator allows null or 0 (V36); a nonzero one is `INVALID_SCHEMA` (RV14).
- **Grid edge knowledge:** each grid edge fact is read like the anchor; an edge with `known_at` null or after K blocks every output with observed 0 (V37, V38).
- **Bar sources and the cutoff:** a bar ending after the cutoff is already a shared `BOUNDS` refusal, so for bar and prepared sources `E > C` is the library `BOUNDS` refusal RV44 and `future_market` is reachable only for the quote and trade sources (Q22, V22).
- **Epoch scale and cancellation:** V39 shifts the V31 trades to an anchor of 1700000000 s (x about 1.7e18 ns) and must equal V31; V40 adds prices near 1e15 whose path differences are 1/2 and 1/4, so a float64 or late-centering OLS loses the result while the exact sums give 3/560 per second (R17 near-cancellation).
- **Unknown or future rows:** any delivered row with null or later-than-K knowledge blocks all outputs of its producer, even a crossed or ineligible-looking quote row (Q18 to Q21); an ineligible trade is the only row whose knowledge is never read (V28 versus V01).
- **Interval and anchor knowledge:** an unready bounds fact or proof fact gives observed 0 on every output (Q29, Q30, V10, V11, V32, V33).
- **Equal time:** equal-time quotes are ordered observations; equal-time trades are ordered points and give a zero time span (Q25, V21).
- **Partial availability:** `no_eligible_observations`, `insufficient_history` and `zero_denominator` are value-level reasons that apply only when the inputs are ready.

## Availability, coverage, quality, evidence and refusals

Typed refusal precedes assessment. Quality uses existing `Status`/`Reason` only. All applicable reasons are retained in lexical order and the status follows the first applicable reason in the EF3 precedence (DP-Q13): `absent_input`, `unknown_availability`, `future_knowledge`, `null_field`, `ineligible` (all `missing_input`), `governed_gap`, `future_market`, `partial_universe` (all `incomplete_coverage`), `insufficient_history`, `no_eligible_observations`, `empty_universe`, `zero_denominator`, else `available`. `ineligible`, `partial_universe` and `empty_universe` are deliberately unreachable. A value is null exactly when the status is not available, and `available` implies `observed == expected`. The slot-reason mapping follows EF3: no row and no coverage is `absent_input`, declared incomplete coverage is `governed_gap`, a null field is `null_field`, `known_at` null is `unknown_availability` and `known_at > K` is `future_knowledge` (`known_at == K` is available, Q20, V12). Knowledge is enforced identically in `known_at` and reconstruction modes with original `known_at`. Q21 shows a multi-reason precedence.

Counts (also in the JSON): quote expected = admitted rows, observed = rows ready for the output (an unready bounds fact gives 0; absent gives 0/0); trade expected = eligible trades; bar expected = grid slots; an unready anchor or proof gives observed 0; `insufficient_history` reports expected 2, observed = points; every other value-level reason keeps expected = observed.

Evidence (available outputs only, unavailable outputs emit none): the limit is `evidence_limit` 0..10000 and witnesses never exceed it. Order: quote maxima, `microprice.last` and its offset: the single selecting or final observation; quote change: the first then the last valid observation; microprice mean and `point_count`: all contributing rows in canonical order; pair counts: the rows of counted pairs, each once. A VWAP path output reads the cumulative sums of every earlier point, so one selecting point would not justify its value: `vwap.path.last`, `change_bps`, both slopes and `point_count` list every point in canonical order, and `vwap.path.maximum` and `minimum` list the points from the first through the earliest selecting point. The limit truncates the tail only and never changes the primary witness, value, status or count (Q05, Q06). Row ids are `quote:<event_id>`, `trade:<event_id>` and `bar:<start_ns>:<end_ns>`, boundary `completed_interval` for bars; the bounds, anchor and proof facts are bound to the result but consume no witness budget.

Refusals (no `FeatureResult`) RQ01 to RQ36 and RV01 to RV44 in the JSON, each with the layer that raises it, the single rule it fires, a base fixture, a concrete recipe and an executable mutation list.

Refusal precedence (JSON `refusal_precedence`). A call is refused by the first applicable tier: T1 config (`INCOMPATIBLE_VERSION`, `UNKNOWN_FEATURE`, `UNSUPPORTED_CAPABILITY`, `INVALID_CONFIG`); T2 shared batch construction (cell type, int64 overflow, missing price unit, sampling none); T3 the shared `validate_batch` per batch in role order (bounds, grid, proof, then quotes, trades, bars), where within a row duplicate identity or tie key precedes ordering, which precedes interval, cutoff and bounds, which precede schema rules, with negative quantity last; T4 the library checks (batch and fact kinds, unit scale, basis, sampling, identity, interval membership, grid, alignment, proof, notional). Three checks depend on others being sound so that one fault is reported once: the sampling-mismatch check needs a valid config sampling, the grid-text and proof-text checks need a valid config value, and bar-to-slot alignment needs a sound grid (so RV15, RV16 and RV18 report the grid fault, not also RV25). Each refusal fixture is a single-fault construction and the harness verifies that its recipe fires exactly that rule; for inputs with several faults the tier order decides.

By code: duplicates `DUPLICATE`; unordered rows or grid edges `INVALID_ORDER`; rows outside the interval or at the cutoff, negative sizes, bad grids, a bar source with `E > C` `BOUNDS`; float or bool values, foreign fact or batch kinds, eligible trades with a null or nonpositive price or size, zero-volume or out-of-bounds notionals `INVALID_SCHEMA`; int64 excess `OVERFLOW`; missing or differing price units `INVALID_UNIT`; basis differences `UNSUPPORTED_ADJUSTMENT`; sampling none, sampling mismatch, change outputs on snapshots `UNSUPPORTED_SAMPLING`; instrument, session, bounds, proof, grid and role mismatches `INCONSISTENT_IDENTITY`; bad or missing parameters `INVALID_CONFIG`; unsupported label `INCOMPATIBLE_VERSION`; unknown feature `UNKNOWN_FEATURE` (RQ35 uses `session.quote.sampled_spread`, an existing output of another producer, not of `ef4.quote_dynamics`); update, restore, merge `UNSUPPORTED_CAPABILITY`. Every code exists in `packages/contracts/.../errors.py`; no new code or validator change is needed.

## Numeric policy and acceptance

Exact integer/rational arithmetic throughout, one correctly rounded float64 per published value (DP-S1, compatible with the R17 Decimal120 policy and its error contract). Acceptance rule per fixture output (field `acceptance` in the JSON):

- `exact_float64`: the reference is a dyadic rational with numerator below 2^53, so any exact-rational or Decimal120 path produces it without rounding; the published float64 must equal the hex bit for bit (74 outputs).
- `exact_plus_zero`: the reference is exactly 0 from exact integer arithmetic; bit-exact +0.0, never -0.0 (18 outputs).
- `tolerance`: `abs(y - r) <= max(8 ulp(r), 1e-12 |r|)` with r the fixture float64, the R17 numeric error contract (`docs/api/INTRADAY.md`, "Numeric error contract and capabilities") (114 outputs, non-dyadic rationals such as 20000/101 or values that exceed 53 bits such as 2^62 + 1).
- `exact_integer`: `pair_count`, `midpoint_change_count`, `point_count` (54 outputs). Total 260 classified outputs.

No documented exceptions. Measurement of cost is not part of this contract; the processing is linear in the rows (the OLS sums are one pass) with no whole-series barrier, and any speed claim belongs to the release baseline.

## Layer responsibilities

- **Library (#493, #494).** Admission of the supplied facts, interval and anchor handling, observation classification, microprice, maxima, change and path arithmetic, extrema and slopes, quality, evidence and every library refusal; pure and deterministic with exact rational intermediates and one final rounding; one shared interval and knowledge admission for both producers with no coupling of output readiness.
- **EF4 I/O.** Maps ordered quote and trade rows, bar windows, grid edges, interval bounds and proof facts exactly as supplied with their original `known_at` and declared coverage; maps results (int64 counts, hex-exact float64, status, reasons, counts, witnesses) to the existing sink conversion; never sorts, fills, imputes, dedupes, converts scale or currency, selects a correction version, derives windows from trades or computes any statistic.
- **Worker.** Routes selected outputs, shares one admitted interval or prepared series across outputs and configs (series preparation reuse), keeps independent readiness, executes one config per complete result, binds inputs and the config digest and persists the library result unchanged. Direct, adapter, worker and stored results must be identical, including refusal class.

## Fixtures

30 quote result fixtures (Q01 to Q30), 39 VWAP result fixtures (V01 to V26 and V28 to V40; V27, an eligible trade with a null price, was withdrawn because the shared validator refuses it), 69 result fixtures in all, plus 80 typed-refusal fixtures (36 quote, 44 VWAP). The JSON `coverage_map` indexes them by tag, `reasons_reached` by reason and `prefix_equivalences` lists identical-result pairs. Coverage: crossed, locked, invalid, zero-size and null-size states (Q01, Q08 to Q13, Q27); maximum ties, unequal midpoints and truncation (Q03 to Q06); sampling identity and snapshot repeats (Q02, Q26); equal-time order and adjacency (Q25); scale and int64 limits (Q07, Q24, V23, V24); empty, absent, gap and silence (Q14 to Q17, Q28, V06, V07, V16 to V19); knowledge boundary and origin availability (Q18 to Q21, Q29, Q30, V10 to V12, V28, V29, V32, V33); cutoff replay and future market (Q22, Q23, V22, V31); series source, irregular spacing, actual notional and zero volume (V01, V02, V05, V30, V34); supplied compatible series and reuse (V03, V04, V32, V33); correction (V13 to V15); same-time and single-point degeneracies (V20, V21); negative and flat paths (V25, V26); independent readiness (Q11, Q12, V08); zero-volume knowledge and notional (V35, V36); grid edge knowledge (V37, V38); epoch scale and near cancellation (V39, V40).

Fixture notation, including how a null, empty, gap, absent, future and unknown slot is constructed, is in the JSON `fixture_notation`. Construction rules recorded there: times are exact integer nanoseconds (illustrative seconds times 10^9 for VWAP); a zero-volume bar carries null notional; a positive-volume bar with a null notional is `null_field`, never zero (`null_field` is reachable only for quote sizes and bar volume or notional); expected entries list exact fractions, float64, `float.hex`, the acceptance rule and witnesses; refusal fixtures name a base fixture, a concrete recipe and an executable mutation list over a placeholder model (instrument `I`, session `S0`, snapshot `snap`), because contract identifiers are never hardcoded. There is no recursion, epoch or anchor beyond the interval start: the path resets at the declared anchor and carry across intervals is not supported. Required readback: a stored count is an int64 never converted through float, and every stored float64 equals the float64 of the exact rational.

## Explicit non-goals

No thresholds, scanners, alert or signal policy; no default sampling, series source, grid or interval; no time-weighted or continuous-time quote statistic and no change to the existing `session.quote.*` outputs; no quote seed, expiry or staleness limit; no depth beyond top of book and no venue merging; no trade signing, tick rule or tape statistic (EQ-158, EQ-161 to EQ-163); no path efficiency, choppiness or notional top-K (other authors); no per-window or rolling VWAP slope, no volume-time axis, no weighted regression; no recomputation of a prepared series from trades and no audit of the preparer; no acquisition, calendar lookup, price adjustment, currency conversion, imputation or forward fill; no new DataKind, DTO, codec, scheduler, validator or error code; no update, restore or merge; no performance, parity, release or publication claim; no private-source equivalence or source formula.

## Author decisions: conventions (proposed, pending coordinator and owner review)

| Id | Convention (reasons and alternatives in the JSON) |
| --- | --- |
| DP-Q1 | Two new producers with separate identities; existing `session.quote.*` unchanged. |
| DP-Q2 | Sampling is an explicit config equal to the batch; trade-snapshot never satisfies a continuous requirement; no pooling; mismatch is `UNSUPPORTED_SAMPLING`. |
| DP-Q3 | Declared half-open interval [S, E) and cutoff C; E > C is `future_market`; no seed. |
| DP-Q4 | Classification as QUOTE_FORMULAS; nonpositive side is invalid; crossed excluded, never by absolute value; locked contributes 0. |
| DP-Q5 | Sizes read only by microprice; zero size is size-ineligible; null size on a consumed valid observation is `null_field`. |
| DP-Q6 | Microprice (b Qa + a Qb)/(Qa + Qb); sizes are shares as supplied; exact wide arithmetic. |
| DP-Q7 | `last` is the final admitted observation only, no carry-back. |
| DP-Q8 | Microprice mean is equal-observation (update- or snapshot-weighted), not size- or time-weighted. |
| DP-Q9 | Change outputs: first and last valid, adjacent valid pairs; continuous only; new unit `pairs`. |
| DP-Q10 | Maxima per the reviewed clarification: own-midpoint bps, all admitted valid observations, earliest tie, truncation-invariant. |
| DP-Q11 | Any unknown or future delivered row blocks all outputs; coverage and emptiness mapping; no staleness limit. |
| DP-Q12 | Total order (event_ns, order_key, event_id); equal-time rows are all observations. |
| DP-Q13 | Reason precedence as EF3; existing Status and Reason only. |
| DP-V1 | `series_source` explicit (`trade`, `bar`, `prepared_window`), never mixed. |
| DP-V2 | The path is anchored cumulative VWAP; per-window VWAP slope deferred. |
| DP-V3 | Operand: eligible price times size, or supplied actual notional; no close times volume. |
| DP-V4 | Time axis: UTC wall-clock ns, bar end, slopes per second. |
| DP-V5 | Anchor is the declared interval start, needs known_at; reset epoch only. |
| DP-V6 | Irregular spacing used as supplied; equal time legal; zero span is `zero_denominator`. |
| DP-V7 | Covered zero-volume window contributes no point; its knowledge and notional are not read; notional 0 or null allowed. |
| DP-V8 | Missing slot: `governed_gap` or `absent_input`, blocks all outputs; grid edge knowledge is read; bar sources require `E <= C`. |
| DP-V9 | Supplied compatible series accepted without recomputation under a proof fact. |
| DP-V10 | Corrections are new batch revisions; the library never selects a version. |
| DP-V11 | Endpoint and equal-weight OLS slopes; weighted estimators deferred. |
| DP-V12 | `point_count` is an output; no minimum-points parameter. |
| DP-V13 | Extrema ties take the earliest point. |
| DP-S1 | Exact rational arithmetic, one float64 rounding, per-fixture acceptance rule. |
| DP-E1 | Witness order and row ids; the limit truncates the tail only; VWAP path outputs list every contributing point (maximum and minimum the prefix to the selecting point). |
| DP-X1 | Batch and full replay only. |
| DP-R1 | No hardcoded entity, instrument, role or grid ids. |

## Author rulings on the former open questions (pending coordinator and owner review)

| Id | Ruling |
| --- | --- |
| OQ-1 | Only the size-tilted midpoint microprice in v1; imbalance and depth variants deferred. |
| OQ-2 | No continuous-time maximum, mean or change is inferred from sampled observations. |
| OQ-3 | EQ-158's window interface is not frozen: this contract needs only (volume, actual notional) windows on an explicit grid expressible as BAR rows and does not consume signing; if EQ-158 freezes a different shape the `prepared_window` role is amended, not the arithmetic. |
| OQ-4 | EQ-172, the tape and path-efficiency contracts are other authors' work: no operand edge in either direction in v1. |
| OQ-5 | Volume-time axis deferred. |
| OQ-6 | `pairs` and `points` are new unit strings recorded in the ledger; `currency/share/second` derives from existing units. |
| OQ-7 | Sizes are shares as supplied; no round-lot conversion; one size unit across both sides. |
| OQ-8 | Per-window VWAP slope deferred. |
| OQ-9 | No seed or pre-open quote. |
| OQ-10 | Both producers live in `packages/features` (EF4 module, namespace `ef4.*`, separate catalog); `describe_intraday()` and its digest unchanged; no package version bump. |
| OQ-11 | Trade-sign and tick-rule fields are not consumed. |
| OQ-12 | The trade eligibility flag and policy are caller-owned and supplied. |
| OQ-13 | A lenient variant ignoring unknown crossed or invalid rows is rejected (it changes adjacency and the final observation). |

## Header ledger and amendment (to be applied)

The 16 headers of this contract are to be applied by a sibling amendment document after the freeze. The unit strings `pairs` and `points` are new to the ledger; `bps`, `currency/share` and `shares` exist and `currency/share/second` is derived. Three new reference fact kinds are recorded: `ef4.interval.bounds`, `ef4.window.edge` and `ef4.series.proof`.

## Proposed coordinator freeze

Proposed freeze as `ef4-quote1` and `ef4-vwap1` (v1) for implementation once this PR merges and the coordinator accepts it (author statement; no review or acceptance claim). Reset epoch mode only: the VWAP path resets at the declared anchor and carry is out of v1. There are no defaults for sampling, series source, grid or interval. Any change to a convention, label semantics, header, role or fixture after merge requires a new policy label and an amendment document.
