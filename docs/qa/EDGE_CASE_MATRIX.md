# Edge-case matrix, EF1 to EF4

Tester deliverable, 2026-10-27, docs only. Expected behaviour is taken from the frozen contracts (`docs/ef1..ef4/*_CONTRACT_PROPOSAL.md`), the shared validator tests and the delivery evidence. Nothing was re-run for this document (the baseline figures quoted in the checklist come from the Developer's run in `work/baseline-2026-10-27.md`, not from this document); the status column was decided by listing and searching `tests/`, `tools/` and the sibling repos' `tests/`.

## Status key

- **T** verified-by-existing-test: a named unit test in `tests/unit/` (or a sibling-repo test/oracle) exercises it.
- **D** verified-by-demo: only a frozen-contract fixture driven by the author manual run or the installed qualification demos (`docs/ef1/qualification/`, `docs/ef2/qualification/`, `docs/ef3/EF3_INSTALLED_QUALIFICATION.md`, `docs/ef4/EF4_INSTALLED_QUALIFICATION.md`). Pass counts are author-reported and were not re-run here. D is not regression-protected.
- **U** unverified: stated or implied by a contract, but no test, fixture or demo targeting it was found, or the contract is silent.

Key fact: EF2, EF3 and EF4 have **no unit tests** (`tests/unit/` has `test_ef1_*` only; no `test_ef2*`, `test_ef3*`, `test_ef4*`; the only EF2-4 files under `tests/` and `tools/` are registry/trades/incremental generic tests and `tools/contract_fixtures/ef4{g,h,i}_fixture_expand.py`). That is policy ("no unit tests by policy" in the delivery evidence), so every EF2-4 row is at best D.

Refusal vocabulary: shared-validator codes `INVALID_SCHEMA`, `DUPLICATE`, `INVALID_ORDER`, `UNSUPPORTED_SAMPLING`, `INVALID_CONFIG`, `INCOMPATIBLE_VERSION`, `BOUNDS`, `INCONSISTENT_IDENTITY`. At the workers layer all collapse to `INVALID_COMMAND` (EF3 ruling R9, EF4 amendment). "Value" means a typed result with status/reason (for example `insufficient_history`, `not_applicable/zero_denominator`), not an exception.

## Cross-cutting rows (shared validator, all families)

| # | Case | Expected (source) | Status | Evidence |
|---|---|---|---|---|
| X1 | NaN / inf in a float field or context JSON | Refuse; context JSON canonical with `allow_nan=false`; `normalization.py` L116 requires finite float | T | `tests/unit/test_validation.py::test_float_nonfinite_and_overflow`, `test_state_float_overflow.py` |
| X2 | Duplicate event id / equal key | `DUPLICATE` | T | `test_validation.py::test_duplicate_event_id`; `test_trades.py::test_equal_time_total_order_and_duplicate_errors`; `test_quotes.py::test_order_duplicate_and_cutoff_errors` |
| X3 | Decreasing timestamp | `INVALID_ORDER`; equal time keeps supplied order, never sorted | T | `test_validation.py::test_equal_time_supplied_order`; same trades/quotes tests |
| X4 | Empty vs absent vs incomplete coverage | Present-empty with complete coverage is a value; `None` is absent; incomplete coverage is `governed_gap` | T | `test_trades.py::test_empty_observed_and_missing_differ`; `test_quotes.py::test_empty_covered_vs_missing_and_absent_sides`; `test_validation.py::test_empty_and_no_lazy_helpers` |
| X5 | int64 overflow (counts, volume, rescale) | Typed failure, no wrap | T | `test_trades.py::test_volume_overflow_is_typed_failure`; `test_validation.py::test_coverage_count_overflow`, `test_rescale_overflow_and_currency` |
| X6 | Overlapping / forming bars, daily order by time not label | Refuse | T | `test_validation.py::test_overlap_duplicate_and_forming_bars`, `test_daily_order_uses_time_not_session_label` |
| X7 | Corporate-action policy mismatch (raw / split / total_return) | raw needs raw_shares; split policy needs split factors; total_return needs reinvestment factors; mismatch refuses | T | `tests/unit/test_policies.py`, `test_ef1_reference.py` |
| X8 | Undeclared coverage fails open (tape adapter defaults to complete) | Known defect E2/L5; not a refusal | U | `docs/ef4/EF4_DELIVERY_EVIDENCE.md` limits; no negative test |
| X9 | RF18/RF35 adapter deviation (`UNSUPPORTED_SAMPLING`/`DUPLICATE` instead of `INVALID_SCHEMA`) | Accepted deviation E6; input still refused | D | EF4 evidence (306 of 308 refusals matched) |

## EF1

| # | Case | Expected (source) | Status | Evidence |
|---|---|---|---|---|
| E1-1 | Splits / corporate actions | Gate computes admission only; multiplies supplied factors with `t < a <= anchor`; factors positive exact num/den; never mutates a batch (`REFERENCE_CONTRACT_PROPOSAL.md` L27-41) | T | `test_ef1_reference.py`, `test_policies.py`; worker `ef1_reference_oracle.json` |
| E1-2 | Close reconciliation boundary and 128-bit exactness | Inclusive `<=`; zero tolerance means exact equality (N06 within, N07 outside); `10000*D` exceeds 64 bits (`CLOSE_RECONCILIATION_CONTRACT_PROPOSAL.md` L92-93) | D | contract fixtures N01-N08; no `test_ef1_close*` exists |
| E1-3 | Halt / resume | `halt_observed`, `resume_observed` event-driven; initial state is not a resume (H02), explicit resume without seed (H03) | T | `test_ef1_observable.py` (H02/H03), `test_ef1_status.py` |
| E1-4 | Multi-venue partial population, stale age | Dominance: aggregate is best only if rank 0, else null; age == max_age not stale, > stale; events at C excluded (`MULTI_VENUE_STATUS...` L65-83) | T / D | `test_ef1_status.py`; MV04, MV05 by demo |
| E1-5 | DST day | Supplied UTC opens, no timezone lookup; two opens one hour apart give identical regular fraction | T | `test_ef1_clock.py::test_supplied_dst_utc_offsets_need_no_timezone_lookup` |
| E1-6 | Early close | `scheduled_close_ns`, `early_close` flag; inconsistent flag gives `INCONSISTENT_IDENTITY` | T | `test_ef1_clock.py` L19-72, L170-175 |
| E1-7 | Calendar null / bad date | `INVALID_CONFIG` / `BOUNDS` ("2026-02-30") | T | `test_ef1_clock.py::test_malformed_schedule_and_concrete_role_limits`; `PERIOD_PHASE...` L21 |
| E1-8 | Gap endpoint / drive when A<C<=Z violated; straddling rows | `BOUNDS`, never filtered silently (`PATH_CONTRACT_PROPOSAL.md` L15-17) | T (partial) | `test_ef1_path.py`; `test_ef1_gap_endpoint.py` has no NaN/dup/order/empty assertions |
| E1-9 | Zero volume / no qualifying first trade | Typed unavailable | T | `test_ef1_first_trade_price.py`; `test_ef1_regular_bar_prices.py` (thin: no NaN/dup/empty) |
| E1-10 | Single bar / empty input | `insufficient_history` or unavailable | T | `test_ef1_path.py`, `test_ef1_anchor.py` |
| E1-11 | Duplicate / out-of-order | `DUPLICATE` / `INVALID_ORDER` | T | `test_ef1_anchor.py`, `test_ef1_path.py`, `test_ef1_reference.py` |
| E1-12 | Context JSON: bool-as-int, duplicate keys, non-canonical ints | Refuse | T | `test_ef1_*` context tests |
| E1-13 | Float parity | Mostly exact; literal goldens | T | worker `ef1_*_oracle.json` |
| E1-14 | Linux vs Windows identical output | Not run | U | Linux qualification outstanding |

## EF2

| # | Case | Expected (source) | Status | Evidence |
|---|---|---|---|---|
| E2-1 | Splits | One action basis per batch; mixed basis `INVALID_SCHEMA`; no in-feature adjustment | D | contract refusal fixtures |
| E2-2 | Halts | No halt concept; halted slot is a proven-empty slot when covered, `governed_gap` when coverage incomplete (`MONEYFLOW...` L85-92) | D | contract fixtures |
| E2-3 | Early close | Early session has fewer slots; periods count governed bars (`MOMENTUM_TREND...` L58) | U | no early-close fixture located by name |
| E2-4 | DST | Grid supplied, no wall-clock arithmetic | U | none |
| E2-5 | Zero-volume bar | Observed-empty slot, null OHLC; MFV=0; OBV[a]=0; empty never becomes OBV base | D | `MONEYFLOW...` L40-66; ICH-04/05 |
| E2-6 | Zero range (HH=LL) / zero DI sum | `undefined_not_applicable` / `not_applicable_zero_denominator` | D | `MOMENTUM_TREND...` L44-50 |
| E2-7 | NaN / inf | Cannot reach kernels (positive int64 coefficients); shared validator refuses floats | T (shared) | X1 |
| E2-8 | Empty / single bar / warm-up | Per-output `insufficient_history` (line available while signal warms) | D | `MOMENTUM_TREND...` L105 |
| E2-9 | Gap in epoch | OBV/AD need every slot a..t ready; CMF only its window; displayed Ichimoku reads nothing after t-d | D | ICH-04, ICH-05 |
| E2-10 | Duplicate / out-of-order | `DUPLICATE` / `INVALID_ORDER` (R17 admission unchanged) | T (code) / D | X2, X3 |
| E2-11 | Squeeze flag flip on exact ties with non-terminating EMA | Known defect, release gate | U | STATUS 2026-10-23 |
| E2-12 | Exact-zero residual outside marked fixtures | Known release gate | U | STATUS 2026-10-23 |
| E2-13 | Overnight carry epoch | Not supported in v1 (reset only) | D | `MOMENTUM_TREND...` L58 |

## EF3

| # | Case | Expected (source) | Status | Evidence |
|---|---|---|---|---|
| E3-1 | Splits | Closes on one adjustment basis; `ln(C_i/C_{i-1})` from exact ratio (log1p-grade near 1) | D | `RELATIVE_RV...` L91; DV14, RV16 |
| E3-2 | Halts / membership (breadth) | `static_snapshot` all members; `ordered_history` stint half-open start<=C<end; known-unavailable not an error | D | `BREADTH_ADAPTIVE...` L97-102 |
| E3-3 | Early close | Fewer declared slots, complete at last slot (RV07), nothing rescaled | D | `RELATIVE_RV...` L77 |
| E3-4 | DST | Grid supplied | U | none |
| E3-5 | Zero volume | Zero-volume rows have null OHLC (shared rule) | D | `ROBUST_PACE...` L59 |
| E3-6 | Zero variance / equal values | MAD 0 is available (majority equal or n=1); correlation `+0.0`, never `-0.0` | D | RS05; `ROBUST_PACE...` L70 |
| E3-7 | NaN / inf | Cannot arise from integer inputs; A is a caller integer | T (shared) | X1 |
| E3-8 | Empty / single / short history | `insufficient_history` (RS01, DV01, RV01) | D | `RELATIVE_RV...` L113 |
| E3-9 | Duplicate (instrument, session, reference_id) | `DUPLICATE` (RF12, OQ-7) | D | `BREADTH_ADAPTIVE...` L93 |
| E3-10 | Target leakage into baseline | Prior-only window; changing target leaves median/MAD (H10a/H10b) | D | `ROBUST_PACE...` L77 |
| E3-11 | Missing slot in reset epoch | RV needs all slots a..t READY | D | `RELATIVE_RV...` L73 |
| E3-12 | Reconstruction-mode exception | Documented; shared validator unchanged | D | `EF3_SHARED_AMENDMENT.md` |
| E3-13 | Worker refusal code collapse | `INVALID_COMMAND` | D | ruling R9; worker refusal coverage partial |
| E3-14 | Performance with large close magnitude | `ef3.relative_stats` slows; documented | U | HANDOFF |

## EF4

| # | Case | Expected (source) | Status | Evidence |
|---|---|---|---|---|
| E4-1 | Splits | Same adjustment basis; raw_shares or split_shares as declared | D | `TAPE...` refusal fixtures |
| E4-2 | Window before session open | `[C-W, C)`; if `C-W < O` all outputs `insufficient_history`, never clipped (W05d) | D | `TAPE...` L62 |
| E4-3 | Early close / DST | Contract silent on DST | U | none |
| E4-4 | Empty tape window | Totals/splits 0; imbalance `not_applicable/zero_denominator` (W11a-d) | D | `TAPE...` L90 |
| E4-5 | Same-nanosecond prints | Sequential by `order_key`, not netted; equal key `DUPLICATE`, decreasing `INVALID_ORDER` (RF03, RF04) | D (code: T) | `TAPE...` L88 |
| E4-6 | Epoch-scale ns > 2^53, 1-hour window | Exact integers; imbalance one correctly rounded float64 (W18, W20) | D | `TAPE...` L96 |
| E4-7 | Crossed / locked / null quote | Null or non-positive invalid; locked valid (mp=b=a); crossed excluded; invalid final observation gives `not_applicable/no_eligible_observations`, no carry (Q10, Q13) | D | `QUOTE_VWAP...` L53-79 |
| E4-8 | Single valid quote | `quote.change.*` needs two: one gives `insufficient_history` (expected 2, observed 1) | D | `QUOTE_VWAP...` L81 |
| E4-9 | Zero path length / flat / equal closes | `PL=0` and `WR=0` give `zero_denominator`; LER equal closes exactly `+0.0` | D | `PATH_EFFICIENCY...` L56-60 |
| E4-10 | Gap beyond bar | True range uses predecessor close for all N bars (PE05: TR=12, H-L=4) | D | `PATH_EFFICIENCY...` L58 |
| E4-11 | Up/down ties | Strict; tie in neither (SP01, SP04) | D | `PATH_PROJECTIONS...` L94 |
| E4-12 | Bar notional coherence | `low*volume <= actual_notional <= high*volume` else refuse | D | `PATH_PROJECTIONS...` L81 |
| E4-13 | Benchmark count K outside 2..16; zero return class | K bound refused; zero is its own class | D | `PATH_PROJECTIONS...` L118 |
| E4-14 | NaN / inf | Only imbalance is float; inputs integer | T (shared) | X1 |
| E4-15 | Tape coverage undeclared | Adapter defaults complete (fail-open) | U | X8 |
| E4-16 | Notional top-K rank order and Parquet/bundles round trip | Rank-aware check not built (E1); bundles decoder refuses notional cells; round trip not run (L2) | U | EF4 evidence |
| E4-17 | Tape merge refusals RF41,42,43,54,55,60,65,66,69 | Checked at library only, no worker path (E8) | D (library only) | EF4 evidence |
| E4-18 | Tape generator fixtures G01-G03 | Not in qualification | U | EF4 evidence |
| E4-19 | `evidence_limit` = 9x config; governed_history N<=63 implicit | No explicit check (E7, E4) | U | EF4 evidence |
| E4-20 | Output ownership manifest vs 59 EF4 headers | Not checked | U | EF4 evidence |
| E4-21 | 1000 seeded random fixtures per I1/I2 | Author claim | D (author-reported) | `PATH_*_IMPLEMENTATION.md` |

## Float parity tolerance policy

1. No floats where avoidable: prices, volumes and notionals are int64/decimal128 coefficients; statistics are exact rationals rounded once.
2. Published float64 is one correctly rounded value of an exact rational (for example tape `imbalance`, DP-T14).
3. Comparison classes (EF3 contract L88-91, adopted here as the working policy): `bits` for exact rationals and exact zero (`+0.0`, never `-0.0`); otherwise `r17_tol`: `abs(x-ref) <= max(8 ulp(ref), 1e-12*abs(ref))`, no absolute floor. `ln` and `sqrt` are judged against Decimal120 correctly rounded references.
4. Cross-form check on one platform is identical canonical `content_sha256` (EF3 346/346 and EF4 297/297 demos across four install forms on Windows).
5. Cross-platform (Windows vs Linux, CPython build, libm) equality is **not established** and no single document states whether tolerance or bit equality governs there. This matrix proposes: bit equality on the canonical hash is the acceptance criterion; any fall back to `r17_tol` needs an owner ruling. Marked U until Linux qualification runs.
