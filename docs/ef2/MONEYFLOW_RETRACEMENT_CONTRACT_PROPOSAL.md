# EF2 money-flow and retracement-level contract — proposal

Prepared for EQ-150 [#484](https://github.com/atulsrivas1/equity-features/issues/484) (OBV, accumulation/distribution, Chaikin money flow) and EQ-238 [#663](https://github.com/atulsrivas1/equity-features/issues/663) (caller-parameterized retracement-level producer, draft W3D-1), for consumption by EF2 I/O [#609](https://github.com/atulsrivas1/equity-features/issues/609), worker [#610](https://github.com/atulsrivas1/equity-features/issues/610) and release acceptance EQ-152 [#486](https://github.com/atulsrivas1/equity-features/issues/486). **This is a contract proposal, not accepted.** It is contract preparation only: no review, freeze, Ready state, implementation, numerical acceptance, release or performance claim is made. Every convention choice is marked DECISION-PROPOSED (with named alternatives) and every unresolved question OPEN for the coordinator.

Companion data: [MONEYFLOW_RETRACEMENT_CONTRACT_PROPOSAL.json](MONEYFLOW_RETRACEMENT_CONTRACT_PROPOSAL.json) holds the machine-readable headers, roles, extremum reference schema, mathematics, 35 money-flow result fixtures, 31 retracement result fixtures and 32 typed-refusal fixtures. Expected values were derived with plain `fractions.Fraction` arithmetic in a scratch script that imports nothing from the equity packages; float64 results carry `float.hex`. The library was not imported, run or tested. Fixtures use compact notation (not canonical wire) and still need expansion into canonical packets.

## Authority and inspected sources

Read-only inputs: the accepted R17 intraday foundations (`packages/intraday`: `_indicators.py`, `_bands.py`, `_prepare.py`, `_context.py`, `_registry.py`, `_admission.py`, `_dispatch.py`), `docs/features/INTRADAY_FOUNDATIONS.md`, `docs/releases/R17/*`, the frozen shared boundary `docs/ef1/CONTRACT.json` (headers, units, availability, quality, evidence), the merged EF1 contracts `CLOSE_RECONCILIATION_CONTRACT_PROPOSAL.md` and `MULTI_VENUE_STATUS_CONTRACT_PROPOSAL.md` (structure and quality bar), the audit drafts `PROPOSED_STORIES.md` (W3D-1), `EQ164_WAVE1_DECISIONS.md`, `EQ164_WAVE2_DECISIONS.md`, `EQ164_SELECTED_A.md` and `EQ164_WAVE4_FIELD_DELIVERY.md` (extrema carriers). The indicators are standard, publicly documented arithmetic specified here from first principles with explicit conventions; no private source, threshold or default is used or copied, and no default ratio or default period is adopted.

## Unchanged boundary

Existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult`, `Status`, `Reason`, `ErrorCode` and scalar `ValueType` values (`int64`, `float64`); the R17 grid, admission, anchor reset/carry epoch, exact-rational preparation and batch/full-replay modes; the frozen ef1-contract1 and every accepted core and R17 header. No new DataKind, DTO, result codec, scheduler or default, no closure, no weakening of context bounds. Update, restore and merge are unsupported (`UNSUPPORTED_CAPABILITY`). This packet is additive: the three money-flow ids are new optional-package catalog entries (the catalog digest changes; existing entries and digest inputs for them do not), and the retracement producer is a new homogeneous producer requiring an equivalent additive amendment, following the precedent of the EF1 producer-set amendments. No new unit string is introduced (`shares`, `fraction`, `currency/share` already exist).

## Producers and config identities

| Item | Money flow | Retracement level |
| --- | --- | --- |
| Identity | `ef2.money_flow` | `ef2.retracement_level` |
| Algorithm / schema | `ef2-money-flow-v1` / `1` | `ef2-retracement-level-v1` / `1` |
| Policy label | `policy_version` = `ef2-mf1` | `policy_version` = `ef2-retrace1` |
| Parameters | R17 context (reset/carry, anchor, target, grid) plus `policy_version`; `cmf_period` N only when `intraday.cmf` is selected | `policy_version`, `direction` (`from_high` or `from_low`), `ratio_num`, `ratio_den` |
| ConfigSpec | PriceUnit mandatory; adjustment declared once and shared by bars; BAR with volume | PriceUnit mandatory; adjustment basis equals both extremum rows |

A policy label names the whole convention set of its version (tie rule, seeds, zero-range and zero-volume handling, empty-slot treatment, window rule, rounding). An unsupported label is `INCOMPATIBLE_VERSION`; a future convention needs a new label, never a silent change. `ef2-mf1` freezes: OBV seed zero at the anchor, OBV tie adds 0, zero-range multiplier 0, proven-empty slots are zero-volume flow, CMF over the last N governed slots wholly inside the epoch, zero CMF volume is zero-denominator. `ef2-retrace1` freezes: ratio domain `0..1` inclusive, the two direction formulas, zero range zero-denominator, inverted range ineligible.

## Outputs and headers

| Feature id | dtype | unit | scale | min period | operand family |
| --- | --- | --- | --- | --- | --- |
| `intraday.ad_line` | float64 | shares | none | 1 | anchored money flow (H, L, C, V from anchor to target) |
| `intraday.cmf` | float64 | fraction | none | N (caller) | windowed money flow (H, L, C, V of the last N slots) |
| `intraday.obv` | int64 | shares | none | 1 | anchored signed volume (C, V from anchor to target) |
| `retracement.level` | float64 | currency/share | converted once from retained integer coefficients | not applicable | prior-extrema pair |

Order: lexicographic by feature id within a producer. Money-flow selections follow R17 per-feature selection: each output has its own required operands, expected/observed counts and independent readiness; an unrelated missing field or slot never blocks a ready output (fixtures M24 and M31 show CMF available while OBV and AD are not). The retracement producer returns its single header per config; a different ratio or direction is a different config and result. DECISION-PROPOSED DP-R1: one output with the direction in config; alternatives: two outputs (`..._from_high`, `..._from_low`) per ratio, or a direction column.

## Inputs and roles

Money flow: one nullable role `bars` (BAR, chunked on the R17 governed grid, unchanged admission, ordering, duplicate and cutoff rules). Required columns by output: `intraday.obv` needs close and volume; `intraday.ad_line` and `intraday.cmf` need high, low, close and volume. Volume is int64 shares at least 0. Prices are positive integer coefficients in one scale and one adjustment basis. No acquisition, clock or I/O. The R17 admission fact record gains a `volume` field and the proven-empty slot becomes an admitted zero-volume observation for this family (DP-M5); it is otherwise unchanged and R17 outputs keep their current empty-slot reasons.

Retracement: two nullable roles in order `prior_high`, `prior_low`, each a REFERENCE batch with exactly one extremum row (schema in the JSON `extremum_reference_schema`):

| Column | dtype | Rule |
| --- | --- | --- |
| `instrument_id`, `session_id` | string | equal the target entity |
| `reference_id` | string | `x1:B(window_set_id)`; identical on both roles |
| `fact_kind` | string | `ef2.extremum.high` or `ef2.extremum.low` per role |
| `effective_start_ns` / `effective_end_ns` | utc_ns | evidence only: boundary of the upstream window |
| `text` | string | equals the batch `source.snapshot_id` (revision binding) |
| `price` | int64, null | exact extremum coefficient at `ConfigSpec.price_unit.scale`; null when the extrema owner reported unavailable |
| `factor_num`, `factor_den` | int64, null | observed slots and required window length N of the upstream extremum; all-or-none |
| `known_at_ns` | utc_ns, null | original knowledge; causal in both availability modes |

Extrema are reused, never re-derived: the supplied values are the existing prior-window high/low (`history.prior_high`, `history.prior_low`, or `session.daily_observations.high/low` with `last_observations`, per the wave 4 delivery map). Because those outputs are rounded float64, the I/O layer must map the exact integer coefficients that the owner itself converts and must not parse a float64 (DP-R6). Whether the extrema come from the history family or the daily-observation family is recorded only in the window set id and snapshot; the level is identical for equal coefficients. The prior-window length belongs to the extrema owner; it travels as `factor_den` and the two roles must agree (DP-R7). Both rows must be instrument and session consistent, share unique actual `input_id`s, and use the unrounded exact coefficient.

## Exact mathematics — money flow

Notation: bars `i = a..t` of one epoch (`a` anchor, `t` target, reset or carry as R17), `C`, `H`, `L` positive integer coefficients, `V` int64 shares, N the CMF period. A slot is priced (row with V > 0 and complete OHLC), empty (proven zero volume: complete coverage expected 0, or a row with V = 0; it has no price) or unready (absent, gap, unknown, future).

1. **Money-flow multiplier.** `MFM_i = ((C_i - L_i) - (H_i - C_i)) / (H_i - L_i) = (2C_i - H_i - L_i)/(H_i - L_i)`, exact rational in `[-1, 1]`; `+1` at the high, `-1` at the low. **Zero range `H_i = L_i`: `MFM_i = 0`** (DP-M4; alternatives: unavailable/zero_denominator for the dependent outputs, carry the previous multiplier, sign of the close change). A zero-range bar is a legal priced bar and its volume still counts in CMF's denominator (M13, M14).
2. **Money-flow volume.** `MFV_i = MFM_i * V_i`; an empty slot has `MFV = 0` and `V = 0`.
3. **OBV.** `OBV[a] = 0` (DP-M1; alternatives: `V_a` assuming a direction, caller-supplied seed). The base close for bar `i` is the close of the latest priced bar before `i` in the epoch; `OBV[i] = OBV[i-1] + sign(C_i - base) * V_i`. If no base exists, the increment is 0 and the bar becomes the base (the first priced bar of the epoch contributes 0, including when the anchor itself is empty: M18). **Ties add 0** (DP-M2; alternatives: add `+V`, carry the previous direction). Empty slots add 0 and never become the base (DP-M3; alternative: the empty slot blocks the output as R17 does for EMA). In carry mode the anchor bar supplies the base close but its volume is not accumulated (M23). The published value is the exact integer, int64; only the published value is bounded: outside `[-2^63, 2^63-1]` is `OVERFLOW` (M34), exactly the bounds is available (M32, M33), and intermediate excursions that return in range are fine (M35).
4. **Accumulation/distribution line.** `AD[t] = sum_{i=a..t} MFV_i` accumulated from the anchor with `AD[a-1] = 0`, so the anchor bar's own flow is included (DP-M8: this deliberately differs from OBV, whose first bar has no price change). Exact rational; published as `float(Fraction)` once (round-half-even binary64), `+0.0` never `-0.0`. The line is origin-dependent: values from different anchors are not comparable. `|AD| <= sum V < 2^76`, so it cannot overflow float64.
5. **Chaikin money flow.** `CMF[t] = sum_{i=t-N+1..t} MFV_i / sum_{i=t-N+1..t} V_i`, the window being the last N governed slots counting empty slots. N is a caller integer in `1..4096` with no default (DP-M6). The window must lie wholly inside the epoch: `t-N+1 >= a`, else `insufficient_history` with observed = ready slots inside the epoch (M02, M03; available exactly at `t-a+1 = N`, M04). When the volume sum is 0 (every slot empty): null, `not_applicable/zero_denominator` (DP-M7; alternative: 0.0) (M19, M20). Exact rational, one rounding, result in `[-1, 1]`; +1.0 and -1.0 are reachable exactly (M11, M12).
6. **Readiness and dependencies.** OBV and AD require every slot `a..t` ready (priced or proven-empty), known (`known_at <= K`) and causal. CMF requires only its window. Expected = `t-a+1` for OBV and AD, N for CMF; observed counts ready slots. A future, unknown or absent slot outside an output's own dependency never affects it.

DECISION-PROPOSED DP-M5 (empty slots): a proven-empty slot is a known fact, volume 0, so its flow is exactly 0 independent of price; admitting it avoids a single illiquid minute disabling the whole epoch. R17 price outputs keep marking it `observed_empty/no_eligible_observations`; alternative: reuse R17 behaviour and let an empty slot make OBV/AD unavailable and CMF's zero-denominator unreachable.

## Exact mathematics — retracement level

Operands: `H` = prior-window high, `L` = prior-window low (positive integer coefficients, scale `s`), ratio `r = ratio_num/ratio_den` exact. `R = H - L`.

- `from_high` (retracing a decline from the high): `level = (H - r*R) / 10^s`.
- `from_low` (retracing a rise from the low): `level = (L + r*R) / 10^s`.

They satisfy `from_high(r) = from_low(1-r)` (T07 and T08 share one float64). Computed as an exact rational and published as `float(Fraction)` once. With `0 <= r <= 1` and `L > 0`, `L/10^s <= level <= H/10^s`, so no overflow or nonfinite value exists (T12 uses coefficients `2^63-1` and `1`). `r = 0` returns the anchor extremum exactly and `r = 1` the opposite one (T03 to T06).

DECISION-PROPOSED: DP-R2 formulas as above; DP-R3 the ratio is a free caller parameter encoded as a reduced exact rational pair (`0 <= num <= den`, `den` in `1..2^63-1`, zero only as 0/1, one only as 1/1), no default, no fixed set; floats, bools, decimal text and extension ratios above 1 are `INVALID_CONFIG` (alternative: a separate `ef2-retrace-ext1` label admitting a larger domain); DP-R8 the level uses no close price at all, so the "close variant" and the side comparison belong to the proximity/crossing consumer (#518), not here; the only side convention is the direction parameter.

Degenerate and invalid pairs (DP-R4, DP-R5): `H = L` gives null, `not_applicable/zero_denominator` (precedent: `session.price.close_location` is null for `H = L`; alternatives: available level = H, or a typed refusal); this applies even for `r = 0` (T15). `H < L` gives null, `missing_input/ineligible` (alternative: `BOUNDS` refusal). A non-positive coefficient makes that side ineligible and unobserved (T18, T19). A side whose row is future, unknown or not complete is never inspected and cannot influence the verdict (T27, T31).

## Availability, coverage, quality, evidence and refusals

Typed refusal precedes assessment, per existing precedents. Quality uses existing `Status`/`Reason` only. All applicable reasons are retained in lexical order; the reported status follows the first applicable reason in this fixed precedence: `absent_input`, `unknown_availability`, `future_knowledge`, `null_field`, `ineligible` (all `missing_input`), `governed_gap` (`incomplete_coverage`), `insufficient_history`, `no_eligible_observations`, `zero_denominator` (the last two `not_applicable`), else `available` (consistent with `CONTRACT.json` precedence). A value is null exactly when the status is not available.

| Condition | Money flow | Retracement |
| --- | --- | --- |
| slot or role missing, complete-empty batch | `absent_input` | `absent_input` |
| known_at null | `unknown_availability` | same |
| known_at > K | `future_knowledge` | same |
| declared incomplete coverage | `governed_gap` | same (row not admitted) |
| window beyond the anchor | `insufficient_history` | upstream shortfall: price null with `factor_num < factor_den` |
| null price with a full window | not reachable (malformed BAR is refused) | `null_field` |
| non-positive price, inverted pair | not reachable | `ineligible` |
| zero denominator | CMF all-empty window | `H = L` |

Counts: OBV/AD expected `t-a+1`, observed ready slots; CMF expected N, observed ready slots inside `max(a, t-N+1)..t`; retracement expected 2, observed the sides admitted causal with a non-null positive price. Knowledge is enforced identically in `known_at` and reconstruction modes with original `known_at`.

Evidence (available outputs only; unavailable outputs emit none): OBV and AD cite the anchor and target slots (limit 2), CMF the first and last window slot (limit 2), retracement the `prior_high` and `prior_low` rows (limit 2) with original `row_id` (`reference_id`), `event_ns`, known_at and boundary `ordinary`. Money-flow bar evidence uses boundary `completed_interval`.

Refusals (no `FeatureResult`): money flow MR01 to MR16 and retracement TR01 to TR16 in the JSON. Highlights: out-of-order slots `INVALID_ORDER`; duplicates `DUPLICATE`; positive-volume row with null OHLC `INVALID_SCHEMA`; contradictory OHLC or negative volume `BOUNDS`; wrong scale or currency `INVALID_UNIT`; wrong basis `UNSUPPORTED_ADJUSTMENT`; bad N, ratio, direction or missing ratio `INVALID_CONFIG`; unsupported policy `INCOMPATIBLE_VERSION`; published OBV beyond int64 `OVERFLOW`; mismatched window set or `factor_den` between roles `INCONSISTENT_IDENTITY`; a priced row presenting a partial window `INCONSISTENT_IDENTITY`; update/restore/merge `UNSUPPORTED_CAPABILITY`.

## Layer responsibilities

- **Library (#484, #663).** Admission of the supplied facts, the multiplier, OBV, AD, CMF and level mathematics, quality, evidence and every refusal above, pure and deterministic, with exact rational intermediates and one final rounding; shared per-bar preparation (admitted OHLCV, multiplier, signed step) reused by the three money-flow outputs without a second implementation and without coupling their readiness.
- **EF2 I/O #609.** Maps ordered OHLCV (including volume) and warm-up windows into BAR chunks exactly as supplied; maps the exact integer extrema coefficients (never a rounded float64), their window length, snapshot and knowledge into the two extremum REFERENCE roles; maps results (int64 OBV, float64 hex-exact values, status, reasons, counts, witnesses) to the existing sink conversion; never derives a multiplier, level or sign, never fills, infers or replaces a missing volume, extremum or ratio, never injects a default period or ratio, never normalizes scale or currency silently.
- **Worker #610.** Routes selected outputs with exact warm-up and operand closure, preserves independent readiness and shared-preparation compatibility within resource bounds, executes one config per complete result, binds all inputs and the config digest and persists the library result unchanged. Direct, worker and stored results must be identical, including refusal class.

## Fixtures

35 money-flow result fixtures (M01 to M35), 31 retracement result fixtures (T01 to T31) and 32 refusal fixtures. Each lists its inputs, literal expected values (`float.hex` for float64), status, reasons, expected/observed counts and witnesses. The JSON `coverage_map` indexes them: insufficient history (M02, M03, M30, T24); exact initial values (M01, M02, M18, M20); ties (M05, M06, M09); constant and monotone series (M06, M14; M07, M08); zero range (M13, M14, T14, T15); zero volume (M17 to M21); boundary equalities (M04, M10 to M12, M32, M33, T03 to T06, T13, T15, T17); degenerate and inverted retracement ranges (T14 to T19); missing history (M24, M25, M29, T20 to T24); unknown and future knowledge (M27, M28, M31, T26, T27, T31); precedence (M29, M30, T29 to T31); int64 and float64 limits (M16, M32 to M35, T12); rounding (M15, M16, T07 to T09, T12). The null/unavailable reasons reachable per output appear at least once: `absent_input`, `unknown_availability`, `future_knowledge`, `null_field` (T25), `ineligible` (T16 to T19), `governed_gap`, `insufficient_history`, `zero_denominator`; `no_eligible_observations` is deliberately unreachable here (empty slots are zero flow). Required readback: the stored OBV is an int64 never converted through float, and the stored retracement level equals `float64` of the exact coefficient rational, never of a float input.

## Explicit non-goals

No acquisition of bars, volumes or extrema; no re-derivation of prior-window extrema; no proximity tolerance, crossing or score (#518); no default ratio, default period, tolerance or threshold; no extension ratios; no smoothing, signal lines, oscillators or price-volume trend variants (Chaikin oscillator, EMA of AD); no volume or price adjustment or currency conversion; no cross-session carry beyond R17's declared carry epoch; no update, restore or merge capability; no new DataKind, DTO, codec, scheduler or default; no change to the frozen contract or R17 outputs; no performance, parity, release or publication claim; no private-source equivalence.

## Decisions proposed (DECISION-PROPOSED, for coordinator ruling)

| Id | Choice | Alternatives named |
| --- | --- | --- |
| DP-M1 | OBV seed 0 at the anchor | `V_a`; caller seed |
| DP-M2 | OBV tie adds 0 | add `V`; carry previous direction |
| DP-M3 | OBV base is the last priced close; empties never become the base | empty blocks the output (R17 style) |
| DP-M4 | zero-range multiplier 0 | null/zero_denominator; carry previous; close-direction sign |
| DP-M5 | proven-empty slot is zero-volume flow | R17 `observed_empty` blocking |
| DP-M6 | CMF is the plain ratio of window sums over N governed slots within the epoch, N caller-given | shorter initial window; calendar-time window |
| DP-M7 | CMF with zero window volume is null, `zero_denominator` | publish 0.0 |
| DP-M8 | AD includes the anchor bar flow, OBV excludes anchor volume | OBV includes anchor volume (needs DP-M1 alternative) |
| DP-M9 | exact rationals, one float64 rounding; OBV exact int64 with `OVERFLOW` | decimal128 for AD |
| DP-M10 | ids `intraday.obv`, `intraday.ad_line`, `intraday.cmf` in the optional package | an `ef2.` or `momentum.` namespace |
| DP-R1 | single output, direction in config | two outputs or a direction column |
| DP-R2 | `from_high = H - rR`, `from_low = L + rR` | other labelling of directions |
| DP-R3 | free reduced-rational ratio in `[0,1]`, no default | fixed ratio set; extension domain |
| DP-R4 | `H = L` is `zero_denominator` | available level = H; refusal |
| DP-R5 | `H < L` or non-positive coefficient is `ineligible` | `BOUNDS` refusal |
| DP-R6 | extrema supplied as exact integer coefficients; rounded float64 not accepted | exact binary rational of the float64 |
| DP-R7 | window length is the extrema owner's, carried as `factor_den`, must agree across roles | window length in this config |
| DP-R8 | the level uses no close; close variant and side comparison belong to #518 | a close operand here |
| DP-R9 | upstream insufficient history transported as null price with `factor_num < factor_den` | absent row (loses the reason) |

## Open questions for the coordinator (OPEN)

- OPEN-1: naming and package home of the three ids (`intraday.*` optional package versus an EF2 namespace) and the exact catalog-digest amendment.
- OPEN-2: how the existing BAR contract treats a zero-volume row with non-null OHLC (this proposal ignores its prices; confirm or refuse).
- OPEN-3: volume basis when prices are split-adjusted; this proposal accepts supplied shares as given and adjusts nothing.
- OPEN-4: whether OBV in carry mode should include a cross-session overnight change (currently yes, via the declared carry epoch) and the exact anchor-bar semantics for AD there.
- OPEN-5: the exact `ErrorCode` for contradictory supplied OHLC (`BOUNDS` proposed) and for a non-positive price on a BAR row.
- OPEN-6: whether the extrema owners (#473, #483 or history/daily carriers) can expose the exact integer coefficient and window shortfall; reuse of closed #32 remains unproved, and the extremum REFERENCE route versus a prepared-operand route is unratified.
- OPEN-7: add `retracement.level` as a proposal-only entry to the 47-output manifest (decision A2) before or after this contract is accepted.
- OPEN-8: evidence limits (2 per output proposed) and the CMF maximum N (4096 proposed from the grid bound).
- OPEN-9: whether `intraday.ad_line` should be float64 shares or a decimal128 type, and a named unit for an unnormalized origin-dependent cumulative value.
- OPEN-10: whether consumers need the extension domain above 1 later (new policy label) and whether the range itself should be emitted by this producer.
