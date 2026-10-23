# EF2 producer-set and header-ledger amendment

Proposed by the contract author for review and owner decision, based on main at a53f440. This additive amendment preserves the frozen [CONTRACT.json](../ef1/CONTRACT.json) (ef1-contract1; SHA256 `02940da0c4663bbced050ac551e7fbafe2a1da1534e4c6fa5c87eaf90d420076` is the hash of the CRLF working-copy form only, while the LF blob on origin/main hashes to `ff576caace8e89491a634e913e946ac4b0f8cf656faf40745d24da7684c6fe14`; both were recomputed here) and the [EF1 amendment](../ef1/PRODUCER_SET_AMENDMENT.md) byte for byte and is recorded as a sibling file. It registers the nine producers of the three frozen EF2 contracts that are already merged in the library: `intraday.momentum.v1` (core PR #682), `ef2.money_flow` and `ef2.retracement_level` (core PR #680) and the six `ef2.<producer>` channel producers (core PR #684). Mathematics, fixtures and decisions stay in [MOMENTUM_TREND_CONTRACT_PROPOSAL.md](MOMENTUM_TREND_CONTRACT_PROPOSAL.md) (including Amendment 1), [MONEYFLOW_RETRACEMENT_CONTRACT_PROPOSAL.md](MONEYFLOW_RETRACEMENT_CONTRACT_PROPOSAL.md) and [ICHIMOKU_CHANNELS_CONTRACT_PROPOSAL.md](ICHIMOKU_CHANNELS_CONTRACT_PROPOSAL.md); the record of this amendment is [PRODUCER_SET_AMENDMENT.json](PRODUCER_SET_AMENDMENT.json). It closes the owed items named in the three `*_IMPLEMENTATION.md` documents and in the contracts' shared-ledger notes. The code facts below were read from `_flow*.py`, `_momentum*.py`, `_channels*.py`, `_registry.py` and `_admission.py` in `packages/intraday`, and `ef2/_retracement.py`, `_definitions.py` and `_dispatch.py` in `packages/features`; the I/O modules were read-only. The three intraday catalogs were imported read-only to enumerate their entries; no tests were run.

## Additive producer-set entries

The eight intraday-hosted producers share one input shape: a single fixed nullable role `bars` (kind bar; the ordered BAR chunks of the governed grid, one per session; `None` is an absent delivery), the R17 context in 4096-codepoint chunks (`context_schema` = `equity-features.intraday-context.v1`, `context_sha256`, `context_chunks` 1 to 16), `completed_eod` window over the context sessions, reset epoch mode only, no calendar role and no ef1-context1 envelope. Result backend `intraday.python`, package `0.1.0a3`. `retracement_level` is hosted in `packages/features` with two fixed nullable reference roles.

| Producer | Config identity | Algorithm / schema | Label | Roles in slot order | Operation parameters (closed, no defaults) | Headers |
| --- | --- | --- | --- | --- | --- | --- |
| `money_flow` | `ef2.money_flow` | `ef2-money-flow-v1` / `1` | ef2-mf1 | `bars` (bar) | policy_version; cmf_period (present exactly when intraday.cmf is selected, 1..4096) | 3 |
| `retracement_level` | `ef2.retracement_level` | `ef2-retracement-level-v1` / `1` | ef2-retrace1 | `prior_high` (reference), `prior_low` (reference) | policy_version; direction (from_high\|from_low); ratio_num; ratio_den (reduced pair, 0 <= r <= 1, den 1..2^63-1, no default) | 1 |
| `momentum` | `intraday.momentum.v1` | `intraday-momentum-v1` / `1` | ef2-conv1 (convention group; the algorithm version is the label checked for INCOMPATIBLE_VERSION, Amendment 1) | `bars` (bar) | momentum_family (macd\|dmi\|stochastic); family periods: macd fast_period, slow_period, signal_period; dmi di_period, adx_period; stochastic k_period, k_slowing, d_period (each 1..4096); closed convention parameters with one legal value each (macd 5, dmi 6, stochastic 5) | 10 |
| `ichimoku` | `ef2.ichimoku` | `ef2-channels-v1` / `1` | ef2-ichimoku-conv1 (convention_version parameter; contract version ef2-v1) | `bars` (bar) | conversion_period; base_period; leading_b_period; displacement; convention_version | 8 |
| `keltner` | `ef2.keltner` | `ef2-channels-v1` / `1` | ef2-keltner-conv1 (convention_version parameter; contract version ef2-v1) | `bars` (bar) | ema_period; atr_period; atr_multiplier_num; atr_multiplier_den; convention_version | 4 |
| `donchian` | `ef2.donchian` | `ef2-channels-v1` / `1` | ef2-donchian-conv1 (convention_version parameter; contract version ef2-v1) | `bars` (bar) | period; convention_version | 4 |
| `pivot_levels` | `ef2.pivot_levels` | `ef2-channels-v1` / `1` | ef2-pivot-conv1 (convention_version parameter; contract version ef2-v1) | `bars` (bar) | convention_version | 5 |
| `band_width_percentile` | `ef2.band_width_percentile` | `ef2-channels-v1` / `1` | ef2-bandpct-conv1 (convention_version parameter; contract version ef2-v1) | `bars` (bar) | band_period; band_k_num; band_k_den; population_size; min_population; convention_version | 1 |
| `bollinger_keltner_squeeze` | `ef2.bollinger_keltner_squeeze` | `ef2-channels-v1` / `1` | ef2-squeeze-conv1 (convention_version parameter; contract version ef2-v1) | `bars` (bar) | band_period; band_k_num; band_k_den; ema_period; atr_period; atr_multiplier_num; atr_multiplier_den; convention_version | 3 |

Bounds read from the config builders: money flow `cmf_period` 1 to 4096 and bound exactly when `intraday.cmf` is selected; momentum periods 1 to 4096 with macd `fast_period < slow_period`, `slow_period + signal_period - 1 <= 4096`, dmi `di_period + adx_period <= 4096`, stochastic `k_period + k_slowing + d_period - 2 <= 4096`; each momentum convention parameter and each channels `convention_version` accepts one value (any other is `INCOMPATIBLE_VERSION`, a missing or extra parameter `INVALID_CONFIG`); channels periods 1 to 4096 (`band_period` 2 to 4096, `atr_period` 1 to 4095), multiplier and band-k fractions are reduced pairs 1 to 1,000,000, `min_population <= population_size`; retracement `ratio_num/ratio_den` is a reduced exact pair in 0 to 1 (extension ratios out of v1) and `direction` is `from_high` or `from_low`. `evidence_limit` is an integer 0 to 10000 in every producer (builder default 0); retracement can emit at most two evidence rows.

Roles: money flow, momentum and the six channel producers each have exactly the one role `bars`; `pivot_levels` reads the whole immediately preceding governed session from the same role (a context without one is `missing_input`/`absent_input`). `retracement_level` has `prior_high` (fact_kind `ef2.extremum.high`) then `prior_low` (`ef2.extremum.low`), each a single exact integer-coefficient reference row with columns reference_id (`x1:B(window_set_id)`), fact_kind, effective_start_ns, effective_end_ns, text (equal to the snapshot id), price, factor_num, factor_den, known_at_ns; float64 upstream outputs are not accepted.

Quality: momentum precedence `missing_input`, `insufficient_history`, `incomplete_coverage`, `not_applicable`, `available`; channels the same without `not_applicable`; money flow and retracement use the reason precedence `absent_input`, `unknown_availability`, `future_knowledge`, `null_field`, `ineligible`, `governed_gap`, `insufficient_history`, `no_eligible_observations`, `zero_denominator`. Evidence rows are `slot:<index>` with boundary `completed_interval` for the intraday producers, and a `missing_input` header has none.

Unchanged: existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult` and scalar `ValueType` set (`int64`, `float64` and `bool` are used); shared validators in `packages/contracts`; the R17 context codec and its bounds (4096 slots, 64 sessions); no new DataKind, DTO, result codec, scheduler or default; the default registry. Each producer returns its complete sorted header set from one homogeneous config, except that a call may select a subset (FINDING F6).

## Catalog relation to the shared ledger

| Registry | Entries | Relation |
| --- | --- | --- |
| `describe_intraday()` | 8 (`intraday.atr`, `band_lower`, `band_middle`, `band_position`, `band_upper`, `band_width_ratio`, `ema`, `rsi`) | R17 only; unchanged; digest `e7dcd5fbaf28a3a74f4b26a6e638b2c3cc5d6271fab744297ab16595bab02d86` unchanged; none of the 39 EF2 headers enter it |
| `describe_money_flow()` | 3 | own catalog, `money_flow_catalog_digest()` `4442cea3cf904e995494a7dce59bb35205fb8905b771ff82a282596c059c6844` (computed here) |
| `describe_momentum()` | 10 | own catalog, `momentum_catalog_digest()` `0e6c46370b380cf037ca7ca9ec3a61daa03b1c3d7c80f5d35eace7217da349fb` (computed here) |
| `describe_channels()` | 25 | own catalog, `channels_catalog_digest()` `616cd83001d74c78a28a2d3b6a5848c765f588d63a00626c0c4a2735154363e2` (computed here) |
| `ef2_definitions(config)` | 1 (`retracement.level`) | per-config discovery in `equity_features.ef2`; distinct from `ef1_definitions` |

Each catalog digest includes `PACKAGE_VERSION` 0.1.0a3. None of the four EF2 registries is part of `ef1_definitions` or of the `describe_intraday()` digest; the shared header ledger of this amendment is therefore a documentation ledger that the code does not yet enumerate in one place.

## Header ledger additions

Thirty-nine headers, lexical by feature id across the combined set. Values are typed full-range; null means the output is unavailable with the quality status and reason of the producer contract. Scale is the EF2 contract literal (FINDING F7).

| Feature id | dtype | unit | scale | Producer | Null / availability rule |
| --- | --- | --- | --- | --- | --- |
| `channel.band_width.percentile` | float64 | fraction | none | band_width_percentile | null unless the closes of c + N bars are ready and the population c >= min_population; below min_population is insufficient_history; target excluded, ties count half |
| `channel.donchian.lower` | float64 | currency/share | none | donchian | null unless the period window of lows ending t is ready (reads lows only); independent of highs |
| `channel.donchian.middle` | float64 | currency/share | none | donchian | null unless the period window of highs and lows ending t is ready |
| `channel.donchian.upper` | float64 | currency/share | none | donchian | null unless the period window of highs ending t is ready (reads highs only); independent of lows |
| `channel.donchian.width_ratio` | float64 | fraction | none | donchian | null unless the period window of highs and lows is ready |
| `channel.keltner.lower` | float64 | currency/share | none | keltner | null unless close is ready on every epoch slot and high/low from the second; epoch shorter than the EMA/ATR seeds is insufficient_history |
| `channel.keltner.middle` | float64 | currency/share | none | keltner | same closure as lower; equals R17 intraday.ema bit for bit |
| `channel.keltner.upper` | float64 | currency/share | none | keltner | same closure as lower |
| `channel.keltner.width_ratio` | float64 | fraction | none | keltner | same closure as lower |
| `channel.pivot.point` | float64 | currency/share | none | pivot_levels | null unless every slot of the immediately preceding governed session is ready (high, low; close on its last slot); a context without a preceding session is missing_input/absent_input, expected 1, observed 0 |
| `channel.pivot.resistance_1` | float64 | currency/share | none | pivot_levels | null unless every slot of the immediately preceding governed session is ready (high, low; close on its last slot); a context without a preceding session is missing_input/absent_input, expected 1, observed 0 |
| `channel.pivot.resistance_2` | float64 | currency/share | none | pivot_levels | null unless every slot of the immediately preceding governed session is ready (high, low; close on its last slot); a context without a preceding session is missing_input/absent_input, expected 1, observed 0 |
| `channel.pivot.support_1` | float64 | currency/share | none | pivot_levels | null unless every slot of the immediately preceding governed session is ready (high, low; close on its last slot); a context without a preceding session is missing_input/absent_input, expected 1, observed 0 |
| `channel.pivot.support_2` | float64 | currency/share | none | pivot_levels | null unless every slot of the immediately preceding governed session is ready (high, low; close on its last slot); a context without a preceding session is missing_input/absent_input, expected 1, observed 0 |
| `channel.squeeze.bollinger_inside_keltner` | bool | boolean | none | bollinger_keltner_squeeze | null unless close is ready on every epoch slot and high/low from the second; inclusive relation decided by exact algebra on Decimal120 operands (see FINDING F4) |
| `channel.squeeze.lower_gap` | float64 | currency/share | none | bollinger_keltner_squeeze | same closure as the flag; signed gap Bollinger lower minus Keltner lower (exact zero may carry a Decimal120 residual, see FINDING F4) |
| `channel.squeeze.upper_gap` | float64 | currency/share | none | bollinger_keltner_squeeze | same closure as the flag; signed gap Keltner upper minus Bollinger upper (same residual caveat) |
| `intraday.ad_line` | float64 | shares | none | money_flow | null unless every epoch slot a..t is ready (priced or coverage-proven empty; needs high, low, close, volume); a zero-range bar contributes multiplier 0 and stays defined; exact zero published as +0.0 |
| `intraday.adx` | float64 | DMI points | none | momentum | null until the data-dependent f + adx_period rule is met on ready dependency slots; an ADX chain that consumes an undefined DX is not_applicable/zero_denominator and is not re-seeded (Amendment 1) |
| `intraday.cmf` | float64 | fraction | none | money_flow | null unless all N window slots wholly inside the epoch are ready; a window reaching before the anchor is insufficient_history; a zero volume sum is not_applicable/zero_denominator |
| `intraday.dx` | float64 | DMI points | none | momentum | null unless di_period + 1 slots are ready; S+ + S- = 0 is not_applicable/zero_denominator |
| `intraday.macd_histogram` | float64 | currency/share | none | momentum | null unless close is ready on every epoch slot and the epoch has at least slow_period + signal_period - 1 slots; signal_period 1 gives +0.0 |
| `intraday.macd_line` | float64 | currency/share | none | momentum | null unless close is ready on every epoch slot and the epoch has at least slow_period slots |
| `intraday.macd_signal` | float64 | currency/share | none | momentum | null unless close is ready on every epoch slot and the epoch has at least slow_period + signal_period - 1 slots |
| `intraday.minus_di` | float64 | DMI points | none | momentum | null unless di_period + 1 slots are ready; a zero smoothed true range is not_applicable/zero_denominator |
| `intraday.obv` | int64 | shares | none | money_flow | null unless every epoch slot is ready (close, volume); starts at 0, anchor volume not accumulated; a value outside int64 is an OVERFLOW refusal of the whole request, never a null |
| `intraday.plus_di` | float64 | DMI points | none | momentum | null unless di_period + 1 slots are ready; a zero smoothed true range is not_applicable/zero_denominator |
| `intraday.stoch_d` | float64 | stochastic points | none | momentum | null unless high/low are ready on the last k_period + k_slowing + d_period - 2 slots and close on the last k_slowing + d_period - 1; a zero-range window is not_applicable/zero_denominator |
| `intraday.stoch_k` | float64 | stochastic points | none | momentum | null unless high/low are ready on the last k_period + k_slowing - 1 slots and close on the last k_slowing; a zero-range window is not_applicable/zero_denominator |
| `intraday.williams_r` | float64 | Williams %R points | none | momentum | null unless high/low are ready on the last k_period slots and close on the last one; HH = LL is not_applicable/zero_denominator; range -100..0 |
| `retracement.level` | float64 | currency/share | none (single rounding from the exact rational of the retained integer coefficients) | retracement_level | null unless both prior_high and prior_low are causal, completely covered, non-null and positive with H > L; H = L is not_applicable/zero_denominator; H < L or a non-positive coefficient is missing_input/ineligible; a short upstream window is insufficient_history |
| `trend.ichimoku.base_line` | float64 | currency/share | none | ichimoku | null unless every slot of its own closure (base_period window ending t) is ready; a window reaching before the anchor is insufficient_history, never shortened |
| `trend.ichimoku.conversion_line` | float64 | currency/share | none | ichimoku | null unless every slot of its own closure (conversion_period window ending t) is ready; a window reaching before the anchor is insufficient_history, never shortened |
| `trend.ichimoku.lagging_line_observed` | float64 | currency/share | none | ichimoku | null unless every slot of its own closure (close at t) is ready; a window reaching before the anchor is insufficient_history, never shortened |
| `trend.ichimoku.lagging_line_reference_close` | float64 | currency/share | none | ichimoku | null unless every slot of its own closure (close at t-d) is ready; a window reaching before the anchor is insufficient_history, never shortened |
| `trend.ichimoku.leading_span_a_displayed` | float64 | currency/share | none | ichimoku | null unless every slot of its own closure (max(conversion, base) window ending t-d) is ready; a window reaching before the anchor is insufficient_history, never shortened |
| `trend.ichimoku.leading_span_a_observed` | float64 | currency/share | none | ichimoku | null unless every slot of its own closure (max(conversion, base) window ending t) is ready; a window reaching before the anchor is insufficient_history, never shortened |
| `trend.ichimoku.leading_span_b_displayed` | float64 | currency/share | none | ichimoku | null unless every slot of its own closure (leading_b_period window ending t-d) is ready; a window reaching before the anchor is insufficient_history, never shortened |
| `trend.ichimoku.leading_span_b_observed` | float64 | currency/share | none | ichimoku | null unless every slot of its own closure (leading_b_period window ending t) is ready; a window reaching before the anchor is insufficient_history, never shortened |

**Header counts.** Momentum 10, money flow 3, retracement 1 and channels 25 make 39 additions (by dtype and unit: bool boolean: 1, float64 DMI points: 4, float64 Williams %R points: 1, float64 currency/share: 25, float64 fraction: 4, float64 shares: 1, float64 stochastic points: 2, int64 shares: 1). `CONTRACT.json` parses to 45 headers; this amendment alone would make a regenerated frozen-file ledger 84, and 95 together with the 11 headers of the EF1 amendment (56 + 39). The merged `ef1_definitions` are 77 after the EF1 amendment (66 before; cited from that amendment, not recounted, and `packages/features/src/equity_features/ef1` has no commit after 0fa8141). `describe_intraday()` is 8 before and 8 after. The 39 enumerate as 38 entries imported from the three intraday registries plus the one `retracement.level` cell (see FINDING F2).

## Unit and dtype additions

Frozen units: `boolean`, `classification`, `currency`, `currency/share`, `fraction`, `ns`, `reason`, `sessions`, `shares`, `state`. Enumerated from the unit strings the merged code emits (the registries, `_retracement.py`/`_definitions.py` and `FEATURE_UNITS` in the I/O modules `momentum` and `channels`, which agree with the library); each is **to be applied, additive**:

- `DMI points` (`intraday.adx`, `dx`, `minus_di`, `plus_di`; float64; 0 to 100 scale).
- `stochastic points` (`intraday.stoch_d`, `stoch_k`; float64; 0 to 100).
- `Williams %R points` (`intraday.williams_r`; float64; -100 to 0).
- New dtype/unit pairing only: `shares` with float64 (`intraday.ad_line`); `shares` is frozen with int64 and `intraday.obv` is int64 shares, already a frozen pairing.
- Reused and already frozen: `currency/share` float64 (25 headers), `fraction` float64 (4), `boolean` bool (1, `channel.squeeze.bollinger_inside_keltner`). No new dtype beyond the frozen `int64`, `float64`, `bool`.

## Explicit statements

- Pure additive; no frozen byte changes; docs/ef1/CONTRACT.json, docs/ef1/PRODUCER_SET_AMENDMENT.* and the three EF2 contracts are not edited.
- Published results of existing producers are unchanged: the implementation records state before/after snapshots of 2,520 (PR 680), 4,320 (PR 682) and 2,657 (PR 684) R17 requests (EMA, RSI, ATR, bands, preparation views, refusals, describe_intraday() and its digest) that were byte-identical; this amendment cites those records and did not re-run them.
- Describe_intraday() and its digest are unchanged; the EF2 catalogs are separate registries.
- Package versions are not bumped (equity-features 0.0.4a5, intraday 0.1.0a3); a bump would change the R17 catalog digest; the bump is owed at release.
- No change to shared validators; the zero-volume rule is the existing BAR validator rule (contract ruling O2): a zero-volume row with non-null OHLC is INVALID_SCHEMA.
- Reset epoch mode only; carry is out of v1; no update, restore or merge.
- Tests/unit/test_purity_audit.py is NOT updated by this PR; whether the EF2 modules are audited is an owner decision, pending.
- No numerical, installed-artifact, cross-layer, source-rights or release acceptance is claimed; nothing is accepted.

Cited snapshots: core PR #680 (2,520 R17 requests), PR #682 (4,320) and PR #684 (2,657) each report a before/after comparison against `origin/main` as byte-identical, including `describe_intraday()`, its digest and the package version. This amendment cites them and did not re-run them.

## FINDINGS

- **F1 catalog placement.** The money-flow contract (money_flow_producer.package, amendment_note) and the momentum contract Q1 speak of additive entries in the intraday catalog with a changed catalog digest. The merged code keeps three own catalogs (describe_money_flow, describe_momentum, describe_channels) and leaves describe_intraday() at exactly eight IDs with an unchanged digest, because the accepted R17 tests assert eight entries (money-flow implementation, point 1). This amendment follows the code; merging the entries is a one-line change the owner may still choose, but it would change the R17 digest.
- **F2 header count.** The three contracts do not state a shared-ledger total. The frozen CONTRACT.json has 45 headers; with the EF1 amendment (not itself a frozen byte change) it would regenerate to 56, and with these 39 to 95 (84 if the EF1 amendment is not applied). The merged ef1_definitions are 77 after the EF1 amendment (cited, not recounted). The 39 EF2 headers are in separate registries and are in neither ef1_definitions nor describe_intraday(). No EF2 header joins a registry that the shared digest covers.
- **F3 units and dtype pairs.** Three unit strings are new relative to the frozen unit set: DMI points, stochastic points, Williams %R points (momentum contract shared_contract_followup). The channels contract says no new unit, which is true of its 25 headers. The money-flow contract (O9) keeps unit shares for float64 intraday.ad_line, a dtype/unit pairing absent from the frozen set (shares is frozen only for int64). The merged R17 catalog also emits RSI points for intraday.rsi, absent from the frozen set and from the EF1 amendment; it is outside these contracts and not covered here.
- **F4 exact-zero language versus code.** The channels contract numeric_policy states that no documented deviation exists for the exact-zero rule and that the squeeze boolean tie is stable only for exactly representable operands. The implementation document records residual gaps and a boolean flip for non-terminating EMA/ATR ties, found by independent review. The momentum contract lists its exact-zero guarantees narrowly and the implementation records residuals outside them. The ledger rules above carry the caveat; release acceptance must account for it. Not resolved here.
- **F5 momentum catalog labels.** The momentum contract header table gives minimum_slots as formulas (for example di_period+adx_period) and lists true_ranges plus directional_moves as the operand of intraday.dx, plus_di and minus_di. The merged catalog stores a numeric minimum_period floor over all legal parameters (macd 2, dmi 2, stochastic 1) and operand_family directional_moves only, dx_observations for adx, macd_observations for the MACD signal and histogram (the implementation notes that these label derived series). Values and readiness are unaffected; the catalog digest includes the labels.
- **F6 channels header selection.** The channels contract returns the complete fixed header set of a producer; compute_channels takes an optional features tuple defaulting to the complete set (implementation point 1). Momentum and money flow likewise select a subset of their family. The producer set is unchanged; the optional selection is a code point the owner may want recorded in discovery.
- **F7 scale wording.** The EF2 contracts give scale none for every header including int64 intraday.obv. The frozen ledger uses scale 0 for int64 counts and the wording PriceUnit.scale input; output full currency/share for price floats. The ledger above records the EF2 contract literal. Owner to confirm whether the shared ledger should restate OBV as scale 0 and price outputs in the frozen wording.
- **F8 result metadata labels.** Intraday EF2 results carry backend intraday.python and package version 0.1.0a3 (the R17 label); retracement.level carries backend python-exact and equity-features 0.0.4a5. Both are the unchanged shared package versions.
- **F9 shared admission touched.** The EF2 contracts say the R17 admission is reused unchanged. The merged money-flow slice added an internal volume field to SlotFacts and one extra value in the admit() constructor in _admission.py, and extended the INTERNAL module set of tools/check_intraday_boundary.py for the new modules. No R17 output reads the field; byte identity is cited from the snapshots above, not re-run here.
- **F10 mapping versions.** The EF2 contracts do not name I/O mapping versions. The read-only I/O repository at c15f540 names ef2-momentum-map1, ef2-channels-map1, ef2-money-flow-map1 and ef2-retracement-map1; they are recorded for information and are I/O-owned, not contract values here. FEATURE_UNITS exists in the momentum and channels I/O modules only; the money-flow and retracement units come from the library catalog and definition.
- **F11 calendar lists.** None of the nine EF2 producers uses a calendar_provenance role or the ef1-context1 envelope (intraday producers carry sessions in the R17 context; retracement carries one SessionSpec), so the frozen calendar_required_for and calendar_null_for lists need no EF2 entries.
- **F12 manifest entry.** Money-flow ruling O7 says retracement.level is to be added to a 47-output manifest as a proposed unaccepted entry through a later hygiene PR. That manifest was not located or read here and is not touched.

## Known release-gate limits (documented in the implementation documents)

- Momentum exact-zero: +0.0 is guaranteed only for the exact_plus_zero fixture mechanisms; elsewhere an exact-zero reference can appear as a Decimal120 residual (about 1.1e-119 for the MACD histogram and 1.7e-118 for DMI dx in the documented cases); values are deliberately not snapped.
- Channels exact-zero: with non-terminating EMA/ATR (for example 110/9, 37/3, ema_period 2 to 7, tied bars) an exact-zero squeeze gap can be a residual of about 1e-119 or -1e-118 and channel.squeeze.bollinger_inside_keltner can flip to false on an exact boundary tie; an independent review found about 2% of 1,187 exact-zero gaps in a 400,000-configuration random search deviating.
- Batch API materializes the chain lists, O(n) memory per request; the contract per-bar O(1) state applies to a future incremental API (momentum implementation note).
- Package version bump owed at release.
- Strict typing (mypy) was not run in the implementation PRs.
- EF2 I/O mapping (#609), worker (#610) and release acceptance (#486) remain separate layers.

## What could not be verified

Nothing in the library was run apart from importing the three intraday registries read-only to list their entries and digests; no tests were run and no fixture was executed. Specifically unverified:

- Nothing in the library was run except importing the three intraday registries read-only to enumerate their 38 entries and digests; no tests were run and no fixture was executed.
- The byte-identity snapshots (2,520, 4,320, 2,657 requests) are cited from the implementation documents and the snapshot scripts were not available.
- The EF1 header counts 66 and 77 are cited from the EF1 amendment and were not recounted.
- The per-header availability rules were read from the contracts and the merged code, not exercised.
- Retracement.level discovery (ef2_definitions) needs a ConfigSpec and was read, not executed.
- The I/O repository was read only for units, identities and mapping labels; worker admission and sink behavior of the EF2 producers are unverified.
- The 47-output manifest named in money-flow ruling O7 was not located.
- Installed artifacts, CI results, strict typing, performance and source rights were not available.
