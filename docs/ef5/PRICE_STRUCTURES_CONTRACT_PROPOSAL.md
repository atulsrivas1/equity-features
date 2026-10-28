# EF5 price structures and patterns - library contract proposal (candle, structure, technical)

Status: architect proposal for EQ-171 #512 (acceptance story EQ235 #623). Docs and fixtures only. No library, I/O or worker code. Not frozen: freeze needs the second-author recompute, the tester stratified recompute, an independent docs review (including md/json parity) and a reviewer verdict artifact; PO rulings PO-1 to PO-7 are accepted and applied. Scope of any acceptance: internal, synthetic data, not releasable. Machine-readable twin: [PRICE_STRUCTURES_CONTRACT_PROPOSAL.json](PRICE_STRUCTURES_CONTRACT_PROPOSAL.json).

## Authority and inspected sources

PO scope brief `work/po-acceptance-ef1-ef4-2026-10-28.md` section 4; `docs/EQUITY_DELIVERY_REPLAN.md` (EF5 section; supplemental output ownership); `docs/plans/equity-output-ownership.json` (EQ-171 planned outputs); the EF3/EF4 contract template (`docs/ef4/PATH_EFFICIENCY_CONTRACT_PROPOSAL.*`, `docs/ef4/EF4_SHARED_AMENDMENT.md` rulings E1-E9 as ratified by the PO on 2026-10-28) and `tools/contract_fixtures`. The quality vocabulary, knowledge semantics, wire expansion and refusal stages are reused from EF4 unchanged; this packet adds no shared-validator behaviour. Formulas are written from public definitions (candle geometry, k-bar swing neighbourhoods, close-to-close return); no proprietary pattern set or threshold is used.

## Unchanged boundary

Mathematical evidence is separate from consumer policy: a result is value + readiness + witnesses + reason, never a signal, ranking or recommendation. Out of scope: consumer policy, live data, option-native patterns, non-bar sources, named multi-bar formations, first-open/drive/readiness and generic EQ167 return/gap (EF1), pure close EQ166, supplied close EQ168, multi-venue EQ165, corporate-action detection. The signed completed-window trend count is assigned to EQ-171 only.

## Producers and config identity

| Producer | Config identity | Policy version | Parameters (all required, no defaults) | Outputs |
|---|---|---|---|---|
| candle | `ef5.candle` | `ef5-candle1` | policy_version; epoch_profile (session_reset\|governed_history); doji_body_max_fraction (text p/q, 1 <= p <= q, no default); evidence_limit (0..10000); adjustment label + adjustment_spec {policy_version, action_snapshot, anchor} (D6; see Inputs) | 7 |
| structure | `ef5.structure` | `ef5-structure1` | policy_version; epoch_profile; swing_strength k (1..64); lookback L (2k..4096); evidence_limit (0..10000); adjustment label + adjustment_spec {policy_version, action_snapshot, anchor} (D6; see Inputs) | 4 |
| technical | `ef5.technical` | `ef5-technical1` | policy_version; epoch_profile; trend_window N (1..1024); trend_count M (1..256); evidence_limit (0..10000); adjustment label + adjustment_spec {policy_version, action_snapshot, anchor} (D6; see Inputs) | 4 |

Algorithm versions `ef5-candle-v1`, `ef5-structure-v1`, `ef5-technical-v1`, schema version 1. Hosting proposal: packages/features EF5 module, namespace `ef5.*`, separate catalog; `describe_intraday()` and its digest unchanged; no package version bump here.

## Outputs and headers

Units use the E9 canonical slash spelling from day one; underscore forms are aliases recorded in the ownership manifest and the amendment, never on a header.

| Header id | dtype | Unit | Producer | Available when |
|---|---|---|---|---|
| `candle.body_fraction` | float64 | `fraction` | candle | bar t READY (OHLC) and range > 0 |
| `candle.doji` | bool | `boolean` | candle | bar t READY (OHLC) and range > 0 |
| `candle.engulfing_bearish` | bool | `boolean` | candle | bars t-1 and t READY (OHLC) |
| `candle.engulfing_bullish` | bool | `boolean` | candle | bars t-1 and t READY (OHLC) |
| `candle.inside_bar` | bool | `boolean` | candle | bars t-1 and t READY (OHLC) |
| `candle.lower_shadow_fraction` | float64 | `fraction` | candle | bar t READY (OHLC) and range > 0 |
| `candle.upper_shadow_fraction` | float64 | `fraction` | candle | bar t READY (OHLC) and range > 0 |
| `structure.last_swing_high_price` | float64 | `currency/share` | structure | slots t-L..t READY (OHLC) and at least one confirmed swing high among candidates t-L+k..t-k |
| `structure.last_swing_low_price` | float64 | `currency/share` | structure | slots t-L..t READY (OHLC) and at least one confirmed swing low among candidates t-L+k..t-k |
| `structure.swing_high_confirmed` | bool | `boolean` | structure | slots t-2k..t READY (OHLC) |
| `structure.swing_low_confirmed` | bool | `boolean` | structure | slots t-2k..t READY (OHLC) |
| `technical.momentum_acceleration_fraction_per_second_squared` | float64 | `fraction/s^2` | technical | closes t-2..t READY |
| `technical.price_velocity_fraction_per_second` | float64 | `fraction/s` | technical | closes t-1..t READY |
| `technical.session_return_fraction` | float64 | `fraction` | technical | open of slot 0 and close of slot t READY (session_reset only) |
| `technical.signed_trend_window_count` | int64 | `windows` | technical | closes t-M*N..t READY |

The four `technical.*` headers are the existing EQ-171 planned outputs in the ownership manifest; the 11 `candle.*` and `structure.*` headers are added to the manifest in `ef5_delivered_outputs` (proposed, not accepted, not implemented). `tools/check_equity_delivery_replan.py` enforces header/manifest parity and unit equality.

## Inputs and role

One role, `bars`: R17 chunked BAR delivery on the governed grid of the epoch, one instrument, positive-volume bars with positive coherent OHLC, zero-volume proven-empty bars with null OHLC, completed bars only (end at or before the market cutoff C). Every row carries its original `known_at`, an optional revision id and the adjustment basis. A `split_adjusted` series also requires the caller's `adjustment_spec` {action_snapshot, anchor, policy_version}, and every series declares `adjustment_spec.policy_version` (D6, PQ-2). `columns=close` is a legal close-only delivery that serves only the close-based technical outputs. The structural context is the R17 context: governed slot grid, declared coverage, session identity and adjustment basis, plus the config values below. Swing strength, lookback, doji fraction, trend window and count, evidence limit, adjustment basis, price unit, K and the coverage declaration are all required; none has a default.

## Exact mathematics

Notation: target slot t, epoch slots 0..t, bar i = (O, H, L, C, V) positive int64 coefficients at `price_unit.scale`; R = H-L, B = |C-O|, U = H-max(O,C), D = min(O,C)-L of the target bar. All arithmetic is exact rational; a float64 output is the exact value correctly rounded once.

- **body_fraction**: B / R in [0,1]; R = 0 is zero_denominator
- **upper_shadow_fraction**: U / R; lower_shadow_fraction = D / R; body + upper + lower = 1 exactly when R > 0
- **doji**: B * q <= p * R for doji_body_max_fraction p/q (integer test, inclusive); R = 0 is zero_denominator
- **inside_bar**: H_t < H_(t-1) and L_t > L_(t-1) (both strict)
- **engulfing_bullish**: C_(t-1) < O_(t-1) and C_t > O_t and O_t <= C_(t-1) and C_t >= O_(t-1) and (O_t < C_(t-1) or C_t > O_(t-1))
- **engulfing_bearish**: C_(t-1) > O_(t-1) and C_t < O_t and O_t >= C_(t-1) and C_t <= O_(t-1) and (O_t > C_(t-1) or C_t < O_(t-1))
- **swing_high_confirmed**: s = t-k; H_s > H_i for every i in s-k..s+k, i != s; needs slots t-2k..t
- **swing_low_confirmed**: s = t-k; L_s < L_i for every i in s-k..s+k, i != s
- **last_swing_price**: scan s = t-k down to t-L+k; the first swing gives H_s / 10^scale (or L_s); needs slots t-L..t; none found is no_eligible_observations
- **session_return_fraction**: (C_t - O_0) / O_0; when t = 0 the single bar gives (C_0 - O_0) / O_0
- **price_velocity**: v_t = ((C_t - C_(t-1)) / C_(t-1)) / dt_t with dt_t = (end_t - end_(t-1)) / 10^9 seconds, exact rational
- **momentum_acceleration**: a_t = (v_t - v_(t-1)) / dt_t, where v_t uses dt_t and v_(t-1) uses its own dt_(t-1); needs closes t-2..t
- **signed_trend_window_count**: NORMATIVE (PO-1): M adjacent non-overlapping N-bar windows (window stride = N) ending at the target; window direction = sign of the completed-window close change; a flat window counts 0; result in [-M, M]; M=1 is one window (TD19, TD20). Formula: sum over j = 0..M-1 of sign(C_(t-jN) - C_(t-(j+1)N)); an integer in [-M, M]; needs closes t-MN..t and every slot in between READY (adjacent windows, no bridging). Rejected alternatives: sliding (overlapping) windows and half-counting flat windows are consumer policy and are not part of this catalogue version
- **publication**: float64 outputs are the exact rational correctly rounded once (Python float(Fraction) equals IEEE round-to-nearest-even); bool and int64 outputs are exact; price outputs divide the integer coefficient by 10^scale

Tie and edge conventions (all pinned by fixtures): doji is inclusive at the threshold (CD02); inside bar is strict, an equal high is not inside (CD05); engulfing needs opposite colours, a covering body and at least one strictly beyond side (CD07, CD08, CD11); a zero-body bar has no colour (CD10); a zero-range bar gives zero_denominator on the fractions and doji and false on the boolean geometry (CD04); equal highs never form a swing (SD03); a flat trend window counts 0 (TD02).

## Epochs, windows and gaps

`session_reset`: the epoch is the target session (slot 0 is its first governed bar). `governed_history`: the epoch is the supplied governed daily grid. Windows are strict: no shrinking, no bridging of a hole, no min_history; fewer epoch slots than an output requires is `insufficient_history` (early close: SD05, TD06). Ruling E4 is applied from day one: under `governed_history` any selected output whose span exceeds 63 is INVALID_CONFIG at config, and `technical.session_return_fraction` is not defined for it. Spans: candle 0 or 1, swing confirmation 2k, last swing L, velocity 1, acceleration 2, trend M*N.

## Normative tie table, elapsed time and limits

| Tie | Rule | Boundary fixture |
|---|---|---|
| doji body/range equals the threshold | inclusive: doji true | CD02 |
| zero-range bar | fractions and doji zero_denominator; inside and engulfing false | CD04 |
| equal high against the prior bar | inside bar false (strict) | CD05 |
| equal low against the prior bar | inside bar false (strict) | CD24 |
| identical body extents, opposite colours | engulfing false (needs one strict side) | CD08 |
| one side equal, other strictly beyond | engulfing true | CD11 |
| prior body zero (no colour) | engulfing false | CD10 |
| equal highs around the candidate | no swing high (strict) | SD03 |
| equal lows around the candidate | no swing low (strict) | SD17 |
| flat trend window | counts 0 | TD02 |
| flat single window, M=1 | count 0 | TD19 |

- **elapsed time (PO-6)**: PO-6 normative: dt_k = (end_k - end_(k-1)) / 10^9 seconds from the supplied end instants (not nominal bar length); velocity divides by dt_t, acceleration is (v_t - v_(t-1)) / dt_t from the two successive velocities (each with its own dt); a missing end instant is INVALID_SCHEMA (wire, RF50) and a non-positive dt is refused by the shared validator (INVALID_ORDER RF51, BOUNDS); TD11 shows a 3-day weekend dt; under session_reset slot 0 is the first bar, has no velocity (a window reaching before it is insufficient_history) and no interval crosses the session boundary
- **'refused' for EF5 acceptance (PO-3)**: PO-3: for EF5 acceptance 'refused' means (a) a typed refusal, or (b) a result-level fail-closed outcome: a non-available status, value null, no witnesses and a reason code, never a substituted value or a silently dropped row. Missing or future known_at is (b) with the ESTABLISHED reason codes unknown_availability / future_knowledge under status missing_input (the PO ruling wrote 'missing_input', which is the status; EF3/EF4 and this contract keep the codes, so no code change is needed). A bar incomplete at the market cutoff is future_market, unavailable. KA-set and fail-closed drivers assert null value plus reason code; every output echoes the declared adjustment basis in the result field `basis` (PO-4; decision: a result field, not a witness, because witnesses are slot row ids; recorded in DECISIONS.md).
- **known limit**: TD10: the declared basis is trusted and no action facts are consumed; no split is detected (PO-4). EF6 may add action facts (a new optional REFERENCE role) that mark windows unavailable; non-breaking

## Knowledge, no lookahead and refusal precedence

- **K**: K is the knowledge cutoff, distinct from the market cutoff C (the end of the last delivered slot); a bar is KNOWN iff its original known_at_ns is non-null and <= K (== K is known)
- **revision**: a correction is delivered as the one current version of the bar (identity key excludes the revision id) with the known_at of the correction; a correction known after K is future_knowledge and the original version is NOT used; delivering both versions is DUPLICATE (RF refusal); the I/O layer selects the version known at K, the library never picks between versions
- **consumed_only**: only slots an output requires are assessed; a null or late known_at on a slot no selected output reads has no effect (KA future_outside_window and future_after_target)
- **partial_bar**: a bar that has not completed at the market cutoff is never delivered as a row (BOUNDS) and a forming target slot yields future_market, never a value
- **compact**: ka maps to known_at_ns = K_ns - (100 - ka) seconds with K_ns = C_ns + 100 s; ka 100 is exactly K, 150 is 50 s after it, 50 is 50 s before it
- **no lookahead**: swings are confirmed k bars late (newest s = t-k); slots after an explicit target are delivered in the prefix fixtures (CD18, SD06, TD17, KA future_after_target) and never matter.
- **stages**: wire, shared, config, version, identity; a refusal raises the code of the first stage with a fault and a row failing an earlier stage is not evaluated by a later one. Every refusal fixture is single-fault, audited by the independent expander.

## Availability, quality, evidence and refusals

Reason precedence: `absent_input`, `unknown_availability`, `future_knowledge`, `null_field`, `governed_gap`, `future_market`, `insufficient_history`, `no_eligible_observations`, `zero_denominator`. Status follows the first applicable reason; a value is null exactly when status is not available; available implies observed = expected. expected = number of slots the output requires (including slots before the epoch start); observed = READY required slots inside the epoch; insufficient_history is added when the first required slot precedes the epoch; there is no shrinking window and no bridging of a hole. All applicable reasons are retained in lexical order (alphabetical), not in precedence order; only the status follows precedence. That is why KA09, KA18 and KA27 list `future_knowledge` before `unknown_availability` while the status is `missing_input` either way (as in EF4). Status of each reason: `missing_input` for absent_input, unknown_availability, future_knowledge and null_field; `incomplete_coverage` for governed_gap and future_market; `insufficient_history` for insufficient_history; `not_applicable` for no_eligible_observations and zero_denominator.

Basis echo (PO-4): every output, available or not, carries the declared adjustment basis in the result field `basis` (not in the witnesses: witnesses are slot row ids). Decision recorded in DECISIONS.md; the JSON and the expander do exactly this.

Evidence: target slot first, then the remaining required slots ascending; the two last_swing_*_price outputs list the located swing slot first, then the target, then the rest ascending; unavailable outputs emit none. `evidence_limit` 0..10000 truncates (CD20, CD21, SD16, TD16).

## Numeric policy and acceptance

- `exact_float64`: the exact rational is dyadic with numerator below 2^53: the float must equal it
- `exact_plus_zero`: exact zero from exact arithmetic: the float must be +0.0
- `tolerance`: abs(y - r) <= max(8*ulp(r), 1e-12*abs(r)) with r the fixture float64 (R17 numeric policy)
- `exact_integer`: int64 outputs are exact
- `exact_bool`: bool outputs are exact
- `documented_exceptions`: none

R17/EF2 numeric policy applies: exact rationals in the contract, int64 coefficients, no epsilon in any zero or tie test (integer comparison).

## Data-capability matrix

Per the capability-matrix rule: data each output needs, whether the client or the server supplies/computes it, per source; a source that cannot supply an input yields the documented unavailable result, never a default.

| data needed | used by | client side | server side | supplied bars (any source) | daily bars (governed_history) | DuckDB store (read-only) | if absent |
|---|---|---|---|---|---|---|---|
| completed OHLCV bars of the target session with original known_at | candle.*, structure.*, technical.session_return_fraction | chooses the instrument, session and target bar, supplies bars | admission, readiness, arithmetic | unverified | unverified | unverified | absent_input / unknown_availability |
| completed close series (close-only delivery) | technical velocity, acceleration, trend count | supplies closes | arithmetic | unverified | unverified | unverified | absent_input for OHLC-dependent outputs |
| first governed slot of the session (open of slot 0) | technical.session_return_fraction | must deliver slot 0 | admission | unverified | not applicable: INVALID_CONFIG under governed_history | unverified | absent_input / no_eligible_observations |
| structural context: governed slot grid, declared coverage, session identity | all | declares coverage and grid | membership and gap checks | unverified | unverified | unverified | refusal (INVALID_SCHEMA / INCONSISTENT_IDENTITY) |
| adjustment basis (one label for the whole series) and adjustment_spec {policy_version; action_snapshot and anchor for split_adjusted} | all price outputs | declares | compares to the batch basis | unverified | unverified | unverified | INVALID_CONFIG / INCONSISTENT_IDENTITY / UNSUPPORTED_ADJUSTMENT |
| knowledge cutoff K and original known_at per bar | all | supplies K and known_at | gates every consumed bar | unverified | unverified | unverified | unknown_availability / future_knowledge |
| market cutoff C (completion of the last bar) | all | supplies | forming bar is future_market | unverified | unverified | unverified | future_market |
| swing_strength, lookback, doji fraction, trend window and count, evidence limit | per producer | chooses (no default anywhere) | validates | unverified | unverified | unverified | INVALID_CONFIG |
| corporate-action facts | none in v1 | not consumed | not consumed; actions are not detected (PO-4) | not applicable | not applicable | not applicable | not applicable |
| volume | readiness only (zero volume proves an empty slot) | supplies | no arithmetic on volume | unverified | unverified | unverified | null_field |

Source cells are `unverified` until provider terms and field availability are checked; nothing here claims a provider supports a field. Every missing or late datum degrades to a quality outcome (absent_input, unknown_availability, future_knowledge, insufficient_history) or a typed refusal; the degradation text is in the last column. No provider is required and none is named by the contract.

## No defaults (defaults ledger)

the library contract has no default value anywhere: every parameter in `producers.*.parameters`, the adjustment basis, the price unit, K, the coverage declaration and the structural context must be supplied; a missing item is INVALID_CONFIG or a typed shared/identity refusal, a missing bar fact is absent_input, unknown_availability or insufficient_history. Fixture-only conventions: default known_at 50 and volume 5 in the compact fixture notation (expanded to explicit values in the canonical wire); slot clock 1.7e18 ns + i*60 s. Forbidden tokens: `K-50`, `KNOWN_DEFAULT`, `default-to-complete`. every EF5 adapter brief must list every default it applies and justify it; the reviewer checks the list against this ledger; the expected list is empty.

## Layer responsibilities

- **library**: admission of supplied bars and context, slot readiness, exact arithmetic, quality, evidence and every library refusal; pure and deterministic; one shared slot table reused by outputs without coupling their readiness
- **io**: maps ordered bars, the governed grid, coverage, adjustment basis, original known_at and revision identities exactly as supplied; selects the version known at K; never sorts, fills, imputes, drops, resamples, converts, chooses a window or computes a pattern; the brief lists every default (expected: none)
- **worker**: routes selected outputs with exact window closure, executes a bounded pattern window without future data, preserves correction and replay scope, persists the library result unchanged; direct, adapter, worker and stored results are identical including refusal class

I/O and worker layers do not start before PO conditions C8-C10 (E1 rank-aware check, E2 fail-closed coverage, E4 explicit check) are merged. No layer uses an EF5 header that is not in the ledger.

## Fixtures

Counts (pinned in `tools/verify_ef5_fixtures.py`): candle 24, structure 17, technical 21, known_at KA-set 27 = 89 result fixtures, and 57 refusal fixtures over 12 distinct error codes. `tools/contract_fixtures/ef5_fixture_expand.py` (stdlib) recomputes every output of every result fixture and applies every refusal mutation to an independent admission model.

Notation: compact, NOT canonical wire. K = 100, default known_at 50, volume 5. A fixture lists slots 0..n-1 in epoch order; the target is the last slot unless `target` names an earlier index (later slots are delivered but must not matter). A slot is [O,H,L,C,V] (columns=ohlcv), [C] (columns=close), or 'absent' (no row, no coverage), 'gap' (no row, declared incomplete coverage), 'forming' (bar not complete at the market cutoff), 'null' (row with null volume and OHLC), 'empty' (zero volume, null OHLC, coverage complete), or {row, ka, rev} (ka 100 == K known, 150 > K, null unknown). Structure fixtures list H and L in the description; each slot is [L,H,L,H,5] (open at the low, close at the high). Technical fixtures build slot i from the previous close (slot 0 from the stated open) with H/L the max/min of open and close. `grid: daily` selects governed_history daily slots, `ends_s` their end offsets in seconds. hand_check states the hand-derived headline values. Result fixtures: CD (candle), SD (structure), TD (technical), KA (known_at set); refusals RF.

### Candle fixtures (CD)

| Id | Case | Hand-derived headline |
|---|---|---|
| CD01 | bullish-colour doji: body 1 of range 20 | body 1/20, upper 9/20, lower 10/20, doji true (1/20 <= 1/10), inside/engulfing false |
| CD02 | body/range exactly 1/10 equals the threshold: inclusive, doji true | 2/20 = 1/10 <= 1/10 |
| CD03 | body 11 of range 100 above 1/10: doji false | 11/100 > 1/10 |
| CD04 | zero-range bars at 50: fractions and doji zero_denominator, inside false, no colour | range 0 -> zero_denominator; H_t < H_p is false; neither colour |
| CD05 | equal high with higher low: strict inside bar is false | 20 < 20 false; body 1/14, upper 4/7, lower 5/14, doji true |
| CD06 | high 18 < 20 and low 7 > 5: inside bar true | inside true; doji 1/11 <= 1/10 |
| CD07 | bearish bar then a bullish bar whose body covers it with a strict side | O_t 14 <= C_p 15, C_t 22 >= O_p 20, strict: bullish true, bearish false |
| CD08 | identical body extents in opposite colour: no strict side, bullish false | O_t = C_p and C_t = O_p: not strict -> false |
| CD09 | bullish bar then a bearish bar whose body covers it | bearish true, bullish false |
| CD10 | prior body zero: neither colour, no engulfing | prior not bearish/bullish |
| CD11 | O_t equals C_p but C_t strictly beyond O_p: still true | 20>=20 and 13<15 strict |
| CD12 | single completed bar: one-bar outputs available, two-bar outputs insufficient_history | expected 2 observed 1 for two-bar |
| CD13 | zero-volume proven-empty target bar |  |
| CD14 | target row present with null volume and null OHLC |  |
| CD15 | target bar absent, no coverage |  |
| CD16 | prior bar in declared incomplete coverage: one-bar outputs unaffected |  |
| CD17 | target bar still forming at the market cutoff: never computed on a partial bar |  |
| CD18 | bar 2 delivered after target 1 must not matter | equal to CD07 |
| CD19 | close-only delivery cannot serve any candle output |  |
| CD20 | evidence_limit 1 keeps only the target witness |  |
| CD21 | evidence_limit 0 emits no witnesses |  |
| CD22 | governed_history: daily bars, same arithmetic as CD07 |  |
| CD23 | coefficients at the int64 limit: exact rational, no overflow |  |
| CD24 | equal low with lower high: strict inside bar is false | 5 > 5 false |

### Structure fixtures (SD)

| Id | Case | Hand-derived headline |
|---|---|---|
| SD01 | k=1 L=2: bar 1 is a swing high (12 > 10, 11) but not a swing low | confirmed high true; low false (9 < 8 fails); last high 12 at slot 1; no swing low |
| SD02 | bar 1 low 5 below 8 and 7: swing low | low true price 5; high false |
| SD03 | equal highs 12,12: strict comparison, no swing high | 12 > 12 false |
| SD04 | k=2 L=6: last swing high 9 at slot 2, last swing low 1 at slot 4 (confirmed at target) | high confirmed false (6 < 9); low confirmed true (1); last high 9; last low 1 |
| SD05 | session of 3 bars with k=2 L=4: insufficient_history | expected 5 observed 3 |
| SD06 | bar 3 (H 99) delivered after target 2 must not matter | equal to SD01 |
| SD07 | gap at slot 0 blocks the lookback outputs; the confirmation outputs only need slots 2..4 | confirmed false/false available; last_swing governed_gap |
| SD08 | k=1 L=3: the swing at the oldest candidate slot t-L+k is found | last high 9 at slot 1; lows rise: none |
| SD09 | k=1 L=6: several swings; the most recent is chosen | last high 8 at slot 5; last low 3 at slot 5; both confirmed true |
| SD10 | zero-volume slot inside the lookback | confirmed outputs use slots 2..4 only |
| SD11 | target row null |  |
| SD12 | target still forming |  |
| SD13 | scale 2 daily grid: swing high price 12.50 = 1250/100 exact |  |
| SD14 | close-only delivery cannot serve structure |  |
| SD15 | k=2 L=4: the single candidate s=2 is a swing high | high 5, confirmed true |
| SD16 | limit 1 keeps only the first witness (the located swing for price outputs) |  |
| SD17 | equal lows 5,5: strict comparison, no swing low | 5 < 5 false |

### Technical fixtures (TD)

| Id | Case | Hand-derived headline |
|---|---|---|
| TD01 | closes 100,102,101,103 N=1 M=3: +1 -1 +1 = +1; session return 3/100; velocity 1/3030 | v_t = (103-101)/101/60 = 1/3030; v_(t-1) = -1/6120; session 3/100; count +1 |
| TD02 | N=2 M=2: newest window flat contributes 0; count +1 | windows (12->12)=0, (10->12)=+1; velocity 0; session 1/5 |
| TD03 | all three windows down: -3 | count -3; session -3/5 |
| TD04 | up then down: count exact 0; session return exact 0 | v = -1/360; v_p = 1/300; a = -11/108000; count 0 |
| TD05 | one bar: session return (C-O)/O only | session 1/25; others insufficient |
| TD06 | session of 3 bars with N=2 M=2: trend insufficient, rest available |  |
| TD07 | slot 1 in declared incomplete coverage: only the trend count is blocked |  |
| TD08 | zero-volume first retained bar: no session open |  |
| TD09 | close-only delivery: velocity, acceleration, trend available; session return needs the open |  |
| TD10 | 100 -> 50 on an unadjusted basis: the library does not detect actions; arithmetic stands | v = -1/120; session -1/2; count -1 |
| TD11 | daily grid with a 3-day gap before the last bar: elapsed from the bar end times | v_t = (11/121)/259200; v_p = (11/110)/86400 |
| TD12 | scale 2: ratios are scale-invariant | equal to TD01 |
| TD13 | adjacent closes at the int64 limit: velocity 1/(9223372036854775806*60) |  |
| TD14 | target bar forming |  |
| TD15 | slot t-1 absent: velocity and acceleration absent_input, session return unaffected |  |
| TD16 | limit 2 truncates the trend witnesses |  |
| TD17 | bar 4 delivered after target 3 must not matter | equal to TD01 |
| TD18 | zero-volume target bar |  |
| TD19 | M=1 N=2: the single window is flat, count 0 (flat counts 0) | close 10 -> 10: count 0 |
| TD20 | M=1 N=1: one window up, count +1 | count +1 |
| TD21 | accepted config with adjustment split_adjusted (shared basis split): arithmetic equal to TD01; every output echoes basis split_adjusted (PQ-1 FX-1); adjustment_spec declares action_snapshot actions-2026-10-28 and anchor anchor-2026-10-28 (required for split_adjusted, shared AdjustmentSpec) | same closes as TD01: v = 1/3030, session 3/100, count +1, a = 61/7417440; basis echo split_adjusted |

### Known_at KA-set (KA01-KA27)

KA01-KA27: for each producer a base fixture and nine known_at variants (null, future, equal to K, one before K, revised and known, revised and late, future outside the window, future after the target, mixed null and future); built with the contract, not retrofitted. Ids by producer: candle KA01-KA09, structure KA10-KA18, technical KA19-KA27, in the order null_target, future_target, equal_cutoff, one_before, revised_known, revised_late, future_outside_window, future_after_target, mixed_null_future. Every null or later-than-K row asserts status missing_input, value null, no witnesses and the reason unknown_availability or future_knowledge (that outcome is 'refused' for EF5, PO-3). Equal to K and one second before K are available; null and later than K lose the target; a late revision is not replaced by the original; a leading slot no output reads and a slot after the target have no effect; null and future on different slots keep both reasons.

### Refusal fixtures (RF)

| Id | Code | Stage | Base | Single fault |
|---|---|---|---|---|
| RF01 | INVALID_SCHEMA | wire | CD07 | a non-integer OHLC cell (10.5) |
| RF02 | INVALID_SCHEMA | wire | CD07 | a bool cell where an integer is required |
| RF03 | INVALID_SCHEMA | wire | CD07 | a text cell |
| RF04 | INVALID_SCHEMA | wire | CD07 | row width 4 for an OHLCV delivery |
| RF05 | OVERFLOW | wire | CD07 | a coefficient above int64 |
| RF06 | INVALID_SCHEMA | wire | TD01 | known_at given as a float |
| RF07 | DUPLICATE | shared | CD07 | bar 1 delivered with the identity of bar 0 |
| RF08 | INVALID_ORDER | shared | SD04 | bars 2 and 3 delivered swapped |
| RF09 | BOUNDS | shared | CD07 | bar ends after the market cutoff (a forming bar delivered as a row) |
| RF10 | BOUNDS | shared | CD07 | bar with start equal to end |
| RF11 | INVALID_SCHEMA | shared | CD07 | high below low |
| RF12 | INVALID_SCHEMA | shared | CD07 | close above high |
| RF13 | INVALID_SCHEMA | shared | CD07 | a zero price |
| RF14 | INVALID_SCHEMA | shared | CD07 | negative volume |
| RF15 | INVALID_SCHEMA | shared | CD07 | rows delivered with coverage not declared (E2: no default-to-complete) |
| RF16 | INVALID_SCHEMA | shared | SD04 | structural context (governed grid) not delivered |
| RF17 | DUPLICATE | shared | CD07 | original and revision of bar 1 both delivered |
| RF18 | INVALID_CONFIG | config | CD07 | evidence_limit missing: no default |
| RF19 | INVALID_CONFIG | config | CD07 | epoch_profile missing |
| RF20 | INVALID_CONFIG | config | CD07 | epoch_profile carry (not supported) |
| RF21 | INVALID_CONFIG | config | CD07 | adjustment not declared |
| RF22 | INVALID_CONFIG | config | CD07 | policy_version missing |
| RF23 | INVALID_CONFIG | config | CD07 | doji_body_max_fraction missing: no default threshold |
| RF24 | INVALID_CONFIG | config | CD07 | doji threshold 0/1 (must be above zero) |
| RF25 | INVALID_CONFIG | config | CD07 | doji threshold 11/10 (above one) |
| RF26 | INVALID_CONFIG | config | CD07 | doji threshold as decimal text 0.1 |
| RF27 | INVALID_CONFIG | config | CD07 | unknown parameter min_history |
| RF28 | INVALID_CONFIG | config | CD07 | evidence_limit 10001 |
| RF29 | INVALID_CONFIG | config | SD04 | swing_strength missing |
| RF30 | INVALID_CONFIG | config | SD04 | lookback missing |
| RF31 | INVALID_CONFIG | config | SD04 | swing_strength 0 |
| RF32 | INVALID_CONFIG | config | SD04 | lookback 3 below 2*swing_strength |
| RF33 | INVALID_CONFIG | config | SD04 | governed_history with lookback 64 (E4: span above 63 refused at config) |
| RF34 | INVALID_CONFIG | config | TD01 | trend_window missing |
| RF35 | INVALID_CONFIG | config | TD01 | trend_count missing |
| RF36 | INVALID_CONFIG | config | TD01 | trend_window 0 |
| RF37 | INVALID_CONFIG | config | TD01 | session_return selected with governed_history |
| RF38 | UNKNOWN_FEATURE | config | CD07 | unknown feature id |
| RF39 | INVALID_UNIT | config | CD07 | price scale 19 |
| RF40 | INVALID_UNIT | config | CD07 | currency in lower case |
| RF41 | UNSUPPORTED_ADJUSTMENT | config | CD07 | adjustment dividend_adjusted not in the v1 vocabulary |
| RF42 | UNSUPPORTED_CAPABILITY | config | CD07 | incremental update call |
| RF43 | UNSUPPORTED_CAPABILITY | config | CD07 | restore call |
| RF44 | INCOMPATIBLE_VERSION | version | CD07 | policy_version ef5-candle0 |
| RF45 | INCONSISTENT_IDENTITY | identity | CD07 | bar 1 starts one second late: off the governed grid |
| RF46 | INCONSISTENT_IDENTITY | identity | CD07 | bar 1 for another instrument |
| RF47 | INCONSISTENT_IDENTITY | identity | CD07 | bar 1 in another session under session_reset |
| RF48 | INCONSISTENT_IDENTITY | identity | TD01 | bar 2 on another adjustment basis than the config |
| RF49 | INCONSISTENT_IDENTITY | identity | SD04 | last bar ends 30 s after its start: not a governed slot |
| RF50 | INVALID_SCHEMA | wire | TD01 | bar 2 delivered without an end instant (missing interval) |
| RF51 | INVALID_ORDER | shared | TD01 | bars 2 and 3 delivered with decreasing end instants (non-positive elapsed time) |
| RF52 | UNSUPPORTED_ADJUSTMENT | config | CD07 | adjustment total_return not in the v1 vocabulary (shared label, not an EF5 label; PQ-1 FX-2) |
| RF53 | UNSUPPORTED_ADJUSTMENT | config | TD21 | split_adjusted without a declared action_snapshot (shared AdjustmentSpec requires it; no default) |
| RF54 | UNSUPPORTED_ADJUSTMENT | config | TD21 | split_adjusted with anchor none (shared AdjustmentSpec rejects none) |
| RF55 | UNSUPPORTED_ADJUSTMENT | config | CD07 | adjustment_spec.policy_version not declared (the shared default raw-v1 is never applied; PQ-2) |
| RF56 | UNSUPPORTED_ADJUSTMENT | config | CD07 | adjustment_spec.policy_version unknown value raw-v2 (PQ-2) |
| RF57 | UNSUPPORTED_ADJUSTMENT | config | TD21 | label split_adjusted paired with policy raw-v1 (mismatched pair; snapshot and anchor declared; PQ-2) |

### Fail-closed drivers (PO acceptance: zero fail-open)

- undeclared coverage: RF15
- missing known at: KA01, KA10, KA19, KA09, KA18, KA27
- future known at: KA02, KA11, KA20, KA06, KA15, KA24, KA09, KA18, KA27
- missing context: RF16
- missing adjustment: RF21
- missing parameters: RF18, RF19, RF22, RF23, RF29, RF30, RF34, RF35, RF50
- note: missing and future known_at are result-level fail-closed (status missing_input, value null) as in EF3/EF4; see PO-3

## Explicit non-goals

- no named three-bar (or other multi-bar) patterns in this catalogue version; additions go through a new catalogue version
- consumer policy, signals, ranking thresholds or recommendations
- live data or partial-bar evaluation
- option-native patterns
- any non-bar source
- named multi-bar candle formations and chart patterns
- first-open, opening drive and readiness (EF1) and generic EQ167 return/gap
- pure close EQ166, supplied close EQ168, multi-venue EQ165
- corporate-action detection
- interpretation of any pattern as advice

## Architect decisions proposed

- **DP-F1 Scope**: three producers in one contract: ef5.candle (7 outputs), ef5.structure (4), ef5.technical (4, including the signed completed-window trend count assigned to EQ-171 only); evidence only, no signal (architect proposal)
- **DP-F2 Catalogue**: minimum catalogue from public definitions: geometry fractions, doji, inside bar, two engulfing forms, swing high/low with strict k-bar neighbourhoods. No named three-bar patterns and no proprietary thresholds; the only threshold is the caller doji fraction (architect proposal, PO-5)
- **DP-F3 No lookahead**: swings are confirmed k bars late (newest s = t-k); a forming target yields future_market; bars after the explicit target never matter (architect proposal)
- **DP-F4 Windows**: strict windows: no shrinking, no bridging, no min_history; fewer epoch slots is insufficient_history (early close covered by SD05, TD06) (architect proposal)
- **DP-F5 Epoch**: session_reset and governed_history as in EF4; E4 applied from day one (required span above 63 under governed_history is INVALID_CONFIG at config); session_return is session_reset only (architect proposal following PO ruling E4)
- **DP-F6 Units**: E9 slash spelling from day one: fraction/s, fraction/s^2, fraction, boolean, currency/share, windows; underscore forms are aliases and appear in no header (architect proposal, PO-2)
- **DP-F7 Fail-closed**: no default for any parameter, K, basis, unit or coverage; undeclared coverage with rows and missing structural context are refused; null/future known_at is missing_input with a null value (architect proposal following PO rule 2, PO-3 and PO-7)
- **DP-F8 Hosting**: packages/features EF5 module, config namespace ef5.*, separate catalog; describe_intraday() and its digest unchanged (architect proposal; not an implementation)

## PO rulings (accepted 2026-10-28)

- **PO-1 Trend count semantics**: confirm the signed completed-window trend count is M adjacent non-overlapping N-bar windows, direction = sign of the close change, flat window = 0, result in [-M, M]. Alternatives: sliding windows (overlapping), or flat counted as a half or excluded. The manifest operands (ordered_completed_close_windows, adjacency, session_reset) do not decide it.
- **PO-2 Unit spellings**: E9 gives no squared form. Proposed fraction/s^2 for acceleration and `windows` for the trend count; the manifest units fraction_per_second and fraction_per_second_squared are recorded as aliases and replaced with fraction/s and fraction/s^2 in this PR.
- **PO-3 Missing or future known_at**: the acceptance criterion says these are 'refused'. The EF3/EF4 contracts treat them as result-level fail-closed (missing_input, null value, reason unknown_availability or future_knowledge). Confirm that is 'refused' for EF5, or require a typed refusal (which would change a shared EF3/EF4 semantic).
- **PO-4 Corporate actions**: v1 consumes one caller-declared adjustment basis and does not detect splits (TD10 computes -1/120 across a 2:1 drop on an unadjusted basis). Alternative: require supplied action facts (a REFERENCE role) and mark windows crossing an action unavailable. Which for v1?
- **PO-5 Catalogue and tie conventions**: accept the minimum catalogue (7 candle, 4 structure outputs) and the tie conventions (doji inclusive, inside bar strict, engulfing needs one strict side, swings strict). Is any named multi-bar pattern required for EF5 acceptance?
- **PO-6 Elapsed time base**: velocity and acceleration divide by the exact difference of bar end instants (a daily bar after a weekend uses 3 days: TD11). Alternative: nominal bar length. Proposed: actual end-instant difference.
- **PO-7 Code for undeclared coverage**: EF5 uses INVALID_SCHEMA (matches the merged tape adapter); the EF4 library code for the same case is the one ruled in E2 and may differ (cross-reference in EF5_SHARED_AMENDMENT). INVALID_SCHEMA is used for rows without declared coverage, matching the merged tape adapter; E2 allowed any existing fitting code (INCONSISTENT_IDENTITY is the alternative).

## Shared rules and terms this contract relies on

Terms: **READY** is a slot with a complete, known, coherent bar for the fields the output reads (the quality table above lists the causes of a slot that is not). **R17** is the governed intraday grid, admission, reset epoch and exact-preparation foundation (`docs/features/INTRADAY_FOUNDATIONS.md`). **E1-E9** are the EF4 shared-amendment rulings (`docs/ef4/EF4_SHARED_AMENDMENT.md`; E2 coverage declaration, E4 governed_history span cap 63, E9 unit spelling). **C8-C10** are the PO merge conditions on E1, E2 and E4 that gate the I/O and worker layers (`DECISIONS.md`, entries of 2026-10-27 and 2026-10-28). **PO-1..PO-7** are the rulings in the section above (`DECISIONS.md`, 2026-10-28).

Config and unit rules used by the refusals: the price unit needs an integer `scale` in 0..18 and a currency (shared `PriceUnit`, `packages/contracts/.../inputs.py`; RF39 scale 19). EF5 admission additionally enforces the currency as exactly three upper-case letters (PO ruling PQ-1 (c2)), so RF40 stays an INVALID_UNIT refusal at config; the shared `PriceUnit` is unchanged (it only requires a non-empty string) and this divergence is stated in EF5_SHARED_AMENDMENT.md. The only EF5 config verb is batch compute: `update` (RF42) and `restore` (RF43) are UNSUPPORTED_CAPABILITY, as in EF4. `epoch_profile` accepts only `session_reset` and `governed_history` (RF19, RF20). The v1 adjustment vocabulary is exactly `unadjusted` and `split_adjusted`, mapped totally to the shared `AdjustmentSpec` bases for comparison only: `unadjusted` -> `raw`, `split_adjusted` -> `split`. split_adjusted maps to the shared AdjustmentSpec(basis=split), which requires a non-none action_snapshot and anchor: the EF5 config for split_adjusted must carry caller-declared adjustment_spec {action_snapshot, anchor} (non-empty, not none; no default); absent or none fails closed with UNSUPPORTED_ADJUSTMENT at config (RF53, RF54); unadjusted needs no spec. TD21 carries explicit values. PQ-2: adjustment_spec.policy_version is declared explicitly by the caller and the shared dataclass default is never read; v1 supports exactly raw-v1 for unadjusted (shared raw) and split-factors-v1 for split_adjusted (the shared AdjustmentSpec policy string, packages/contracts breadth.py, relative.py, policies.py); absent, empty, unknown or a mismatched label/policy pair is UNSUPPORTED_ADJUSTMENT at config (RF55 missing, RF56 unknown, RF57 mismatch); total_return stays unsupported. All existing result fixtures now declare policy_version explicitly (config text only; no expected value changes). The `basis` result field echoes the EF5 label, never the shared one. `total_return` and every other label (shared or not, RF41 `dividend_adjusted`) is UNSUPPORTED_ADJUSTMENT at config; a missing or undeclared basis stays refused (RF21).

PQ-1 resolved (PO ruling, work/po-ef5-contract-readthrough-2026-10-28.md): (b) the label mapping above is normative; (c2) the three-letter upper-case currency rule is an EF5 admission rule. Fixture coverage of the mapping: `unadjusted` is exercised by the result fixtures; `split_adjusted` by the accepted-config result fixture TD21 (FX-1, basis echo `split_adjusted`, maps to shared `split`) and RF48 (mismatching bar basis); `total_return` is refused by RF52 (FX-2, single fault, UNSUPPORTED_ADJUSTMENT at config) beside RF41 (`dividend_adjusted`). TD21 and RF52 were added with the independent expander and the verify_ef5_fixtures pins; they need recompute (EF5_FREEZE_EVIDENCE.md).

Unit spellings: the EF5 headers use the E9 slash spellings from day one. The EF4 headers keep their underscore spellings (for example `fraction_per_second`) in the library META and contract JSON until the scheduled migration at the next contract-version boundary (core `DECISIONS.md` E9, `docs/ef4/EF4_LEDGER_APPLICATION.md`); the underscore forms are recorded aliases only.

## Verification

Pre-merge command: `python tools/verify_ef5_fixtures.py (runs tools/contract_fixtures/ef5_fixture_expand.py, pins the counts, known_at probes and positive/negative/unavailable coverage); then tools/check_equity_delivery_replan.py for header and manifest parity`. The expander is a fixture-expansion helper, not a unit test. A negative control (a tampered expected value and a tampered refusal code) was run and made the expander fail. In-session authorship: the second-author recompute, the 10 percent stratified tester recompute and an independent docs review are conditions before freeze.

## Header ledger and amendment

Units and aliases for the sibling shared-ledger amendment are in [EF5_SHARED_AMENDMENT.md](EF5_SHARED_AMENDMENT.md). The ownership manifest entries and the parity check are part of this PR.

## Freeze

not frozen: freeze as ef5-price-structures-1 only after the second-author recompute, the tester stratified recompute, a reviewer verdict artifact and an independent docs review are merged (PO rulings PO-1..PO-7 are applied)
