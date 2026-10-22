# EF1 close-reconciliation contract — proposal

Prepared for EQ168 [#508](https://github.com/atulsrivas1/equity-features/issues/508), supporting EQ212 [#570](https://github.com/atulsrivas1/equity-features/issues/570) and EQ213 [#571](https://github.com/atulsrivas1/equity-features/issues/571). This is contract preparation only. It is a proposal: not reviewed, not frozen, not accepted. It admits no Ready state, implementation, numerical acceptance, source rights, official price or release claim. Independent review and coordinator freeze remain required. Every unresolved choice is marked **OPEN** for the coordinator and collected in the final section; nothing was guessed silently.

Companion data: [CLOSE_RECONCILIATION_CONTRACT_PROPOSAL.json](CLOSE_RECONCILIATION_CONTRACT_PROPOSAL.json) holds the machine-readable headers, roles, authoritative-close schema, mathematics, 44 result fixtures and 28 typed-refusal fixtures. Expected values were derived with plain `fractions` arithmetic in a scratch script that imports nothing from the equity packages; the library was not imported, run or tested. Fixtures use compact notation (not canonical wire) and still need expansion into canonical packets.

## Authority and inspected sources

The issue body section "Reviewed output ownership clarification" (October 21, 2026), [OWNERSHIP_RECONCILIATION.md](OWNERSHIP_RECONCILIATION.md), [equity-output-ownership.json](../plans/equity-output-ownership.json) (group SR04: four outputs, planned ownership accepted, mathematics/API `accepted: false`), the frozen [CONTRACT.json](CONTRACT.json) ef1-contract1 (unchanged; this packet is additive), [REFERENCE_CONTRACT_PROPOSAL.md](REFERENCE_CONTRACT_PROPOSAL.md) and [REFERENCE_IMPLEMENTATION.md](REFERENCE_IMPLEMENTATION.md) (structure and quality template), [REGULAR_BAR_PRICES_IMPLEMENTATION.md](REGULAR_BAR_PRICES_IMPLEMENTATION.md) with [REGULAR_BAR_PRICES_LOCAL_QUALIFICATION.md](REGULAR_BAR_PRICES_LOCAL_QUALIFICATION.md), and [IMPLEMENTATION_ADMISSION.md](IMPLEMENTATION_ADMISSION.md). Source modules `_reference.py`, `_regular_bar_prices.py`, `_path.py` and `_anchor.py` were read (not run) to align error codes and precedents. The existing reference gates (`reference_action`, `reference_classification`) are not changed and do not deliver this arithmetic; the manifest records that an explicit EQ168 comparison/projection amendment is required.

## Scope rules carried from the issue

- `reference.close.supplied_price` projects an actually admitted supplied fact. It does not calculate or authenticate the close.
- Two distinct operands: the independently calculated regular close (EQ166 owns construction) and a distinct supplied same-session authoritative close with actual identity, source, effective interval, known-at, revision, basis and coverage.
- The supplied close is the positive denominator. Tolerance and a versioned comparison policy are explicit caller inputs. No default, no private or symbol-specific threshold.
- The two close values stay separate in results and storage. A successful comparison authenticates neither source rights nor an unsupplied official price.
- EQ212 maps facts and results only. It never derives BPS and never replaces the calculated close.

## Unchanged boundary

Existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult`, scalar `ValueType` values, `compute_ef1(batches, config, *, entity)`, `ef1_definitions(config)`, the EF1 config builder and decoder. One homogeneous producer and config returns its complete sorted header set. Algorithm v1, schema 1. No new DataKind, DTO, result codec, scheduler or default, no closure, no combined result with EQ166, no weakening of the context (<=4096 codepoints and UTF8 bytes, depth <=8), no change to manifest limits. Modes: batch and full supplied replay; update, restore and merge unsupported.

The new producer is a tenth homogeneous EF1 producer. The frozen file says exact nine-producer boundaries; the regular BAR and first-trade producers already extended that set by reviewed additive contracts, so this proposal follows the same route and requires an equivalent additive amendment. **OPEN O5.**

## Config identity

| Item | Value |
| --- | --- |
| Identity | `ef1.reference_close` (**OPEN O5**: name `reference_close`; alternative is extending a reference gate, not recommended because the gates carry no calendar and no numeric payload) |
| Algorithm / schema | `v1` / `1`; scale `none` for state/bool/BPS, coefficient scale for price |
| Parameter | exactly `ef1_context_json`, canonical ASCII JSON, exact re-encoding, duplicates and unknown keys rejected, bool-as-int rejected |
| Top-level keys | `version` (`ef1-context1`), `producer` (`reference_close`), `calendar`, `selection` |
| Calendar | required, target-only (one session), identical schema and `c1:` proof as `regular_bar_prices` |
| Selection (exact keys) | `phase_profile` = `regular_no_auctions1`, `sampling` = `completed_bar_close`, `policy_version` = `ef1-close-compare1`, `scope_id`, `tolerance_bps_num`, `tolerance_bps_den` |
| ConfigSpec | PriceUnit mandatory; session ordinary regular without auctions; `open_ns < market_cutoff_ns <= close_ns`; adjustment is the declared basis for both operands |

`policy_version` names the whole comparison convention in this document (formula, operand order, rounding, inclusive boundary, state vocabulary). An unsupported label is refused with INCOMPATIBLE_VERSION. A future convention needs a new label, never a silent change.

Tolerance encoding (**OPEN O9**): an exact reduced non-negative rational in BPS as two JSON integers. `tolerance_bps_num` in `0..2^63-1`, `tolerance_bps_den` in `1..2^63-1`, `gcd = 1`, and numerator 0 requires denominator 1. Floats, bools, decimal text, omitted keys and non-reduced forms are INVALID_CONFIG. This keeps the context free of floating point and makes the boundary test exact. `scope_id` is a nonblank label (<=128 codepoints) that must equal the scope decoded from the authoritative-close `reference_id`.

## Inputs and roles

Fixed nullable slots in this order; the actual tuple follows the existing nonmissing-role order, exact manifest/batch bijection, unique actual `input_id`s, original complete metadata of every supplied batch in the result inputs.

| Role | Kind | Contract |
| --- | --- | --- |
| `calendar_provenance` | REFERENCE | unchanged from EQ166 |
| `bars` | BAR | unchanged from EQ166 (exact regular completed prefix, scope, unit, adjustment) |
| `population_proof` | REFERENCE | unchanged from EQ166 (`ef1.regular_bar.population.v1`) |
| `authoritative_close` | REFERENCE | new, below |

The first three roles are identical to EQ166, so the same physical batches can feed both producers. The calculated close is not an input fact: it is selected from `bars` under the EQ166 rules.

### Calculated-close operand (OPEN O1)

The comparison needs the calculated close, and EQ166 publishes it only as a lossy `float64` (`float(Fraction(p, 10**scale))`). Comparing floats would make boundary equality depend on binary representation (for example 100.10 as a double is below 100.10). Options:

- **A (recommended).** The new producer reuses the EQ166 selection and readiness logic (shared internal helper, no second implementation of "last structurally positive-volume completed BAR close, with its interior/trailing unknown-volume and causality rules") and takes the exact integer coefficient `p_c` that EQ166 itself would convert. EQ166's published `session.close.calculated_price` equals `float(Fraction(p_c, 10**scale))` and remains the only place the calculated close is emitted. This needs a no-behavior-change refactor of the EQ166 module to expose the selected coefficient; that is a source change outside this docs-only task and needs coordinator approval and review.
- **B.** Consume the published float64 as the exact binary rational `Fraction(float)`. No EQ166 change, but the boundary cannot be exact in decimal terms (fixture N09 illustrates the representational gap), and the tolerance boundary then means "of the double", not of the supplied decimal.
- **C.** A caller-supplied REFERENCE row carrying the calculated coefficient. Rejected here: it lets an adapter replace the calculated close, which the issue forbids.

The mathematics below assume A. Under B, replace `p_c` by `Fraction(c)` and every identity remains exact rational arithmetic, but fixtures N02, N05, N08 and N09 would need re-derivation.

### Authoritative-close role

A supplied fact, not a calculation. Canonical REFERENCE columns (`price` is the existing nullable int64 column):

| Column | dtype | Rule |
| --- | --- | --- |
| `instrument_id`, `session_id` | string | equal the target entity |
| `reference_id` | string | `k1:B(scope_id):B(source_close_id)`; B = reversible unpadded base64url of UTF8; total <=128 codepoints and <=512 UTF8 bytes; decoded scope equals `selection.scope_id`; `source_close_id` is the opaque provider/source identity of the close print |
| `fact_kind` | string | exactly `ef1.close.authoritative` |
| `effective_start_ns` | utc_ns | exactly `ConfigSpec.session.close_ns` (actual close; early close handled by the actual session) |
| `effective_end_ns` | utc_ns, null | null or strictly greater than start |
| `text` | string | exactly the batch `source.snapshot_id` (row-level revision binding) |
| `price` | int64, null | close coefficient at `ConfigSpec.price_unit.scale` |
| `factor_num`, `factor_den` | int64 | absent or all null |
| `known_at_ns` | utc_ns, null | original knowledge; causal in both availability modes |

Batch metadata: `price_unit` equals `ConfigSpec.price_unit` (no rescale, no currency conversion); `adjustment` equals `ConfigSpec.adjustment`, which the bars also equal, so both operands share one basis; `source.mapping_version` = `ef1-reference-map1`; ordering `declared`, duplicate policy `reject`; revision is `source.snapshot_id`; coverage is the actual `Coverage`. Admission requires `complete` with `expected = observed = row_count`.

OPEN items here: **O6** (no separate certificate proof role is added; completeness rests on the batch `Coverage` assertion plus the single-row cardinality rule, whereas the reference gates use `r1:` proofs; adding one would be a fifth role), **O10** (revision carried as `text == snapshot_id`, effective instant fixed to the actual close, basis by metadata equality), **O11** (scale and currency must equal the config; no rescale).

## Precise mathematics

Notation: `s` = PriceUnit scale, `p_c` = calculated close coefficient (positive, int64), `p_s` = supplied authoritative close coefficient (int64), `D = |p_c - p_s|`, `num/den` = tolerance.

1. **Operands share a scale.** Both are integers at `s` in one currency and basis; `s` cancels, so BPS is scale-free (fixtures N12, N13).
2. **Absolute relative difference.** Exact rational `B = 10000 * D / p_s` for `p_s > 0`. The supplied close is the only denominator. Operand order matters for the denominator, not the numerator: swapping operands changes the result (N10: 100.0, N11: 99.00990099009901).
3. **Published BPS.** `float(Fraction(10000*D, p_s))`: one correctly rounded IEEE binary64 conversion, round-half-even, from the exact rational. No intermediate float, no repeated rounding. `D = 0` publishes `+0.0` (never `-0.0`). Fixture N16 is an exact midpoint between adjacent doubles (`0x1.00000000001b9p+17` and `0x1.00000000001bap+17` are each 1/2^36 away) and publishes the even one, `0x1.00000000001bap+17`.
4. **Tolerance test.** Exact integer comparison `10000 * D * den <= num * p_s`. It is never evaluated on the rounded float, so the float field can equal the tolerance as a double while the exact verdict is "outside" (N09: float64 of 10000/3 equals float64 of 3333.3333333333333, exact BPS is larger, result outside).
5. **Boundary semantics (OPEN O3, recommended).** Inclusive: exactly equal is within (`<=`). Zero tolerance means exact equality (N06 within, N07 outside). Equal (N02, N05, N08), just above (N03, 10.01 BPS) and just below (N04, 9.99 BPS) are all fixtured.
6. **Overflow and precision.** `10000*D` is at most `10000*(2^63-1)`, about 9.2e22, so the exact numerator needs more than 64 bits (arbitrary precision or at least 128-bit integers); no int64 or float64 overflow can occur, and the maximum published value is `9.223372036854776e22` (N14, exact `92233720368547758060000`). The minimum nonzero value is about 1.08e-15 and is a normal double (N15, `0x1.3880000000000p-50`). Relative rounding error is at most 2^-53. No tolerance range beyond int64 is accepted.
7. **Denominator validity.** `p_s > 0` is the admission condition for the denominator. `p_s = 0` and `p_s < 0` are never divided by; see below. A price on a row that is not causal (known_at null or after K) is not inspected and cannot influence any output (R08, R11, R12).

## Availability, coverage, quality and error semantics

Typed refusal precedes assessment, following the existing reference and path precedents (INVALID_UNIT, UNSUPPORTED_ADJUSTMENT, INCONSISTENT_IDENTITY, DUPLICATE are `ContractError`, never a state). Refusals (no `FeatureResult`), 28 fixtures E01 to E28:

- DUPLICATE: more than one authoritative-close row (counted before knowledge arbitration, even when one row is late or unknown, even when prices agree), duplicate `reference_id`, shared actual `input_id`.
- INCONSISTENT_IDENTITY: row session or instrument differs from the target; `effective_start_ns` differs from the actual `close_ns`; `text` differs from `snapshot_id` (or null); `reference_id` scope differs from `scope_id`.
- INVALID_UNIT: scale or currency differs from the config. UNSUPPORTED_ADJUSTMENT: basis differs.
- INVALID_SCHEMA: wrong fact kind, populated factor columns, wrong slot kind, malformed or oversize `reference_id`. INCOMPATIBLE_VERSION: wrong mapping or policy label. BOUNDS: bad effective interval or cutoff. INVALID_CONFIG: invalid, missing or float tolerance.

Whether duplicate and inconsistent facts should be typed refusals (precedent, recommended) or `comparison_state` values is **OPEN O7**; the state vocabulary below deliberately avoids a fifth header (the ownership manifest fixes four) and avoids new Reason enum members.

Assessment after admission. Reference side (independent of the calculated close):

| Condition | Reason | Note |
| --- | --- | --- |
| slot missing, or row count 0 | `absent_input` | missing and complete-empty differ only in Coverage counts |
| batch Coverage incomplete (including unknown expected) | `governed_gap` | a present row is then not admitted: hidden duplicates cannot be excluded |
| `known_at` null | `unknown_availability` | |
| `known_at > K` | `future_knowledge` | |
| causal row with null price | `null_field` | |
| causal row with `p_s < 0` | `ineligible` | |
| causal row with `p_s = 0` | `ineligible` for `supplied_price`; `zero_denominator` for BPS and tolerance | |

Calculated side: exactly the EQ166 readiness for `session.close.calculated_price` (missing bars `absent_input`, incomplete coverage or `C < close_ns` provisional prefix `governed_gap`, unknown trailing volume `null_field`, missing proof `absent_input`, selected bar future or unknown knowledge). Provisional comparison before the regular close is not allowed in this proposal: **OPEN O4** (recommended: not comparable, because EQ166 states the prefix close is provisional and never an official close; the alternative allows comparison of a provisional prefix with a later-known official close).

Status for each numerical output from the union of its applicable reasons, all retained in lexical order: `missing_input` if any of `absent_input`, `null_field`, `unknown_availability`, `future_knowledge`, `ineligible`; else `incomplete_coverage` if `governed_gap`; else `not_applicable` if `zero_denominator`; else `available`. Knowledge applies identically in `known_at` and `reconstruction` modes.

### Outputs

| Output | dtype / unit | Value | Readiness |
| --- | --- | --- | --- |
| `reference.close.absolute_difference_bps` | float64 / bps | published BPS | both operands ready and `p_s > 0` |
| `reference.close.comparison_state` | string / state | vocabulary below | always available (assessment) |
| `reference.close.supplied_price` | decimal128 / currency/share | `p_s` as the integer coefficient at PriceUnit.scale | reference side only; independent of the calculated close (C01 to C06 keep it available) |
| `reference.close.within_tolerance` | bool / boolean | exact `<=` verdict | same as BPS |

`supplied_price` is decimal128 so the supplied fact is projected exactly with no float conversion and cannot be confused with EQ166's float64 `session.close.calculated_price` (**OPEN O2**: float64 `currency/share` would mirror EQ166 but loses digits above 2^53). The calculated close is not emitted by this producer, so there is no duplicate feature id and no overwrite: the two values are stored under different feature ids by two homogeneous results and joined by config/entity (**OPEN** sub-point of O1: no echo of the calculated close here).

`comparison_state` vocabulary (closed, exact strings): `within_tolerance`, `outside_tolerance`, `reference_unavailable`, `reference_future`, `reference_invalid`, `calculated_unavailable`. Precedence: `reference_future` > `reference_invalid` (`p_s <= 0`) > `reference_unavailable` > `calculated_unavailable` > `within_tolerance`/`outside_tolerance`. A visible reference failure wins over an unknown calculated operand; combined cases are fixtured (X01 to X03). The state never claims authenticity: `within_tolerance` means arithmetic agreement of two supplied/calculated numbers under the caller's tolerance.

Coverage counts (**OPEN O8**): `supplied_price` expected = authoritative batch `Coverage.expected` (null when slot missing or unknown), observed = row count. BPS and tolerance: expected 2, observed = number of independently ready operands (calculated close ready, supplied close admitted). State: 1/1. Evidence: bounded selected witnesses, limit 7. `bars` witness = the EQ166 selected last positive-volume completed BAR (boundary `completed_interval`); `authoritative_close` witness = original row (`row_id` = `reference_id`, `event_ns` = original `effective_start_ns`, original known_at, original bounds, consumed). Numerical outputs cite witnesses only when available; `comparison_state` cites each causal applicable witness. Order: feature id, then slot order (`bars`, `authoritative_close`), then original row order. Result metadata inputs are lexicographic by role as the canonical contract requires. This is bounded evidence, not an audit.

## Layer responsibilities

- **Library (EQ168).** Admission of the supplied close, the BPS convention, tolerance verdict, state and quality, witnesses; reuse of the EQ166 selection without a second implementation. Pure: no acquisition, no clock, no I/O, no mutation, no apply-action. All refusals above.
- **EQ212 I/O mapping.** Maps an actually supplied close and its provenance (source, snapshot/revision, mapping version, effective and known-at, coverage) into the `authoritative_close` batch exactly as given; maps results (including decimal128 coefficients, float64 hex-exact BPS, bool, state, quality, evidence) to storage; preserves the two close values under separate feature ids; never derives BPS, never fills, infers or replaces the calculated close, never substitutes a caller-computed value for a missing supplied close, never normalizes scale or currency silently.
- **EQ213 worker.** Executes one homogeneous `ef1.reference_close` config per complete result, binds all actual inputs and the config digest, and persists the library result unchanged; no hidden aggregation, close construction or comparison. Direct, worker and stored results must be identical, including refusal class.

## Fixtures

44 result fixtures and 28 refusal fixtures in the JSON (counts: boundary 8, precision 6, overflow 2, rounding 1, denominator 4, reference 12, calculated 6, combined 3, distinct 2). Each result fixture lists operands, tolerance, C/K/E, and literal expected state, four outputs with value (with `float.hex` for float64), status, reasons, expected/observed counts and witness ids. Required coverage is mapped in `coverage_map`: missing, invalid and duplicate close; inconsistent session, unit, basis and revision; unknown and future knowledge; tolerance equal, just above, just below; zero and negative denominator; distinct-value and readback; precision, overflow and rounding; independent operand readiness. Highlights: N02 (10.0, within), N03 (10.01, outside), N04 (9.99, within), N09 (float equality but exact outside), N10/N11 (operand order), N14/N15 (extremes), N16 (half-even tie), Z01/Z02 (invalid denominator), C01 (supplied price survives a missing calculated close), D01/D02 (separate values).

Readback requirement: for D01 the stored supplied coefficient is 10000 and the independently stored EQ166 value is `float.hex(101.0)`; the comparator result must never contain 10100, and EQ166 must never contain 10000. Cross-layer fixtures must preserve every field through adapter, library, worker and serialized sink. No database execution was performed or authorized here.

## Explicit non-goals

No acquisition, fetching or inference of an official close; no authentication of source rights or price; no calculation or replacement of the calculated close; no hidden threshold, symbol-specific policy or default tolerance; no cross-basis, currency or scale conversion; no closing-auction print construction; no new DataKind, DTO, codec, scheduler or default; no combined result with EQ166; no change to the frozen contract or either sibling repository; no performance, parity, release or publication claim; no full EQ164 acceptance.

## OPEN questions for the coordinator

- **O1** Calculated-close operand: exact coefficient via shared EQ166 helper (A, recommended), published float64 (B), or caller-supplied (C, rejected). A needs an EQ166 no-behavior-change refactor. Also whether to echo the calculated close in this result (recommended no).
- **O2** `supplied_price` dtype: decimal128 coefficient (recommended) or float64.
- **O3** Confirm inclusive `<=` boundary (recommended) rather than strict `<`.
- **O4** Provisional comparison before regular close: not comparable (recommended) or allowed.
- **O5** Producer name `reference_close` and the additive amendment to the ef1-contract1 producer set, discovery, dispatch and version.
- **O6** Whether the authoritative close needs a certificate/proof role like `r1:`; currently Coverage plus single-row cardinality.
- **O7** Typed refusal versus state for duplicate and inconsistent facts; the six-value `comparison_state` vocabulary with no reason header.
- **O8** Quality coverage counts and the witness set and limit (7).
- **O9** Tolerance encoding as a reduced integer pair, bounds, and the `ef1-close-compare1` policy label.
- **O10** Revision binding (`text == snapshot_id`), effective instant equal to actual close, basis by metadata equality including action snapshot/anchor.
- **O11** Same scale and currency required for both operands; no rescale.

## What was not verified

Nothing was executed against the library, installed artifacts, workers, databases or CI. The fixtures' compact notation was not expanded into canonical `CanonicalBatch`/`ConfigSpec` packets, config digests were not computed, and the EQ166 calculated-close operand values stand for an independent EQ166 oracle result on valid calendar/bars/population packets that still must be authored. Behavior of EQ166 internals (selection helper reuse) was read from source but not run. Ownership planned status, tracker state and Project readback were not rechecked beyond the issue text. Nothing here is frozen, accepted or Ready.
