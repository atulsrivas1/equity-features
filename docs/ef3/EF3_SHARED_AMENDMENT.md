# EF3 shared producer-set, ledger and ruling amendment

Proposed by the contract author for review and owner decision, based on main at ee92759. Docs only; nothing is accepted. This additive amendment preserves the frozen [CONTRACT.json](../ef1/CONTRACT.json) (ef1-contract1), the [EF1 amendment](../ef1/PRODUCER_SET_AMENDMENT.md), the [EF2 amendment](../ef2/PRODUCER_SET_AMENDMENT.md) and the three EF3 contracts byte for byte and is recorded as a sibling file, in the form of the EF2 amendment (core PR #685). The record in machine-readable form is [EF3_SHARED_AMENDMENT.json](EF3_SHARED_AMENDMENT.json). No validator, code, fixture or `CONTRACT.json` is edited.

It covers the nine producers of the three frozen EF3 contracts, whose library, I/O and worker layers are merged:

| Contract | Document | Core library | I/O adapter | Worker |
| --- | --- | --- | --- | --- |
| D relative statistics, daily log volatility, realized variance | [RELATIVE_RV_CONTRACT_PROPOSAL.md](RELATIVE_RV_CONTRACT_PROPOSAL.md) (incl. Amendment 1, core #693) | #692 | io #36 | workers #80 |
| E robust history, volume pace, mean ratio | [ROBUST_PACE_CONTRACT_PROPOSAL.md](ROBUST_PACE_CONTRACT_PROPOSAL.md) | #694 | io #37 | not among the PRs cited here |
| F session breadth, observed breadth, adaptive volume | [BREADTH_ADAPTIVE_CONTRACT_PROPOSAL.md](BREADTH_ADAPTIVE_CONTRACT_PROPOSAL.md) | #695 | io #38 | workers #81 |

The contract proposals themselves landed as core #689, #690 and #691. Sources read: the three contract `.md`/`.json` files, [RELATIVE_RV_IMPLEMENTATION.md](RELATIVE_RV_IMPLEMENTATION.md), [ROBUST_PACE_IMPLEMENTATION.md](ROBUST_PACE_IMPLEMENTATION.md) and [BREADTH_ADAPTIVE_IMPLEMENTATION.md](BREADTH_ADAPTIVE_IMPLEMENTATION.md) (including their review notes), the I/O documents `EF3_RELATIVE_RV_IO.md`, `EF3_ROBUST_PACE_IO.md` and `EF3_BREADTH_ADAPTIVE_IO.md` (equity-feature-io origin/main 86cbff2) and the worker documents `EF3_RELATIVE_RV_WORKER.md` and `EF3_BREADTH_ADAPTIVE_WORKER.md` (equity-feature-workers origin/main 1317428). No library code was run and no test was executed.

## (a) Producer-set and header-ledger delta

| Producer | Config identity | Algorithm / schema | Policy label | Roles in slot order | Headers |
| --- | --- | --- | --- | --- | --- |
| `relative_stats` | `ef3.relative_stats` | `ef3-relative-stats-v1` / 1 | ef3-rel1 | two fixed role slots (contract D) | 3 |
| `daily_log_volatility` | `ef3.daily_log_volatility` | `ef3-daily-log-vol-v1` / 1 | ef3-dlv1 | one fixed role slot | 1 |
| `intraday_realized_variance` | `ef3.intraday_realized_variance` | `ef3-realized-variance-v1` / 1 | ef3-rv1 | `bars` (R17 context, packages/intraday) | 2 |
| `robust_history` | `ef3.robust_history` | `ef3-robust-history-v1` / 1 | ef3-robust1 | series, sessions, population, cohort_values | 6 |
| `volume_pace_robust` | `ef3.volume_pace_robust` | `ef3-volume-pace-robust-v1` / 1 | ef3-pace1 | grid, sessions, bars | 4 |
| `volume_ratio_mean` | `ef3.volume_ratio_mean` | `ef3-volume-ratio-mean-v1` / 1 | ef3-mean1 | series, sessions | 3 |
| `session_breadth` | `ef3.session_breadth` | `ef3-session-breadth-v1` / 1 | ef3-breadth1 | population, prior_reference_availability, current_return, cumulative_volume, endpoint_price, vwap, momentum, selected_high, selected_low | 16 |
| `observed_breadth` | `ef3.observed_breadth` | `ef3-observed-breadth-v1` / 1 | ef3-obsbreadth1 | members, change, qualifier_price, qualifier_volume | 7 |
| `adaptive_volume` | `ef3.adaptive_volume` | `ef3-adaptive-volume-v1` / 1 | ef3-adaptive1 | observations | 10 |

Identities, versions and labels were read from the `producers` objects of the three contract JSON files. The two daily producers carry a local `DailyGrid` bound by SHA-256 (RELATIVE_RV_IMPLEMENTATION.md, Daily grid context); the robust, pace, mean and breadth producers take the governed grid from reference roles. The library places the daily and reference-role producers in `packages/features` (`equity_features.ef3`) and the realized-variance producer in `packages/intraday` with its own catalog; `describe_intraday()` and its digest are stated unchanged by the implementation documents (cited, not re-run).

**Header ledger additions (52).** Verified by parsing the `headers` array of each contract JSON: relative_rv 6, robust_pace 13, breadth_adaptive 33, total 52 with 52 distinct feature ids, none present in the 45 headers of `docs/ef1/CONTRACT.json` or the 39 headers of `docs/ef2/PRODUCER_SET_AMENDMENT.json`, and none named in the EF1 amendment text. By producer: relative_stats 3, daily_log_volatility 1, intraday_realized_variance 2, robust_history 6, volume_pace_robust 4, volume_ratio_mean 3, session_breadth 16, observed_breadth 7, adaptive_volume 10. By dtype and unit: float64 fraction 18, int64 members 12, float64 shares 4, int64 utc_ns 4, float64 ratio 3, float64 operand-defined 3, int64 observations 3, int64 shares 2, bool boolean 1, float64 shares/s 1, float64 1/s 1.

**Ledger totals.** `CONTRACT.json` parses to 45 headers. Regenerated frozen-file ledger if only this amendment were applied: 97 (45 + 52). With the EF1 amendment (11): 108. With the EF1 amendment and the EF2 amendment (39) as well: 147 (45 + 11 + 39 + 52). The EF1 figures 11, 66 and 77 and the EF2 figure 39 are cited from the earlier amendments (the EF2 39 was also re-counted from its JSON). As with EF2, the EF3 headers sit in their own registries and the code does not enumerate the combined ledger in one place; the 147 is a documentation figure, not a code count.

**Unit and dtype additions (to be applied, additive).** Frozen units: `boolean`, `classification`, `currency`, `currency/share`, `fraction`, `ns`, `reason`, `sessions`, `shares`, `state`. Unit strings of the 52 EF3 headers that are not in the frozen set:

- `members` (int64; 12 headers: 6 `breadth.session.*` counts, 5 `breadth.observed.*` counts and `cohort.rank`).
- `observations` (int64; `adaptive.volume.observation_count`, `scored_count`, `acceleration_scored_count`).
- `ratio` (float64; `breadth.session.advance_decline_ratio`, `up_down_volume_ratio`, `adaptive.volume.peak_relative_rate`).
- `shares/s` (float64; `adaptive.volume.baseline_rate`) and `1/s` (float64; `adaptive.volume.peak_relative_acceleration`).
- `operand-defined` (float64; `robust.median`, `robust.mad`, `robust.quantile`): a ledger string only. The implementation emits the resolved operand unit (`shares` or `currency/share`) in the `FeatureColumn.unit` (ROBUST_PACE_IMPLEMENTATION.md note 8).
- `utc_ns` (int64; four headers: `adaptive.volume.latest_event_ns`, `peak_relative_acceleration_event_ns`, `peak_relative_rate_event_ns`, `breadth.session.latest_observed_member_event_ns`). Not in the frozen set, but already proposed by the EF1 amendment.
- New dtype and unit pairing only: `shares` with float64 (`mean.baseline`, `mean.numerator`, `pace.baseline_mad`, `pace.baseline_median`); `shares` is frozen with int64 only (EF2 already proposed the same pairing for `intraday.ad_line`).
- Reused and already frozen: `fraction` float64 (18), `boolean` bool (1), `shares` int64 (2: `breadth.session.up_volume`, `down_volume`).

No new dtype beyond `int64`, `float64` and `bool`. Scale: where a contract header states none, the ledger records it as not stated; EF2 finding F7 (scale wording) applies equally and is not resolved here.

### Ledger rows

| Feature id | dtype | unit | Producer |
| --- | --- | --- | --- |
| `adaptive.volume.acceleration_scored_count` | int64 | observations | adaptive_volume |
| `adaptive.volume.baseline_available` | bool | boolean | adaptive_volume |
| `adaptive.volume.baseline_rate` | float64 | shares/s | adaptive_volume |
| `adaptive.volume.latest_event_ns` | int64 | utc_ns | adaptive_volume |
| `adaptive.volume.observation_count` | int64 | observations | adaptive_volume |
| `adaptive.volume.peak_relative_acceleration` | float64 | 1/s | adaptive_volume |
| `adaptive.volume.peak_relative_acceleration_event_ns` | int64 | utc_ns | adaptive_volume |
| `adaptive.volume.peak_relative_rate` | float64 | ratio | adaptive_volume |
| `adaptive.volume.peak_relative_rate_event_ns` | int64 | utc_ns | adaptive_volume |
| `adaptive.volume.scored_count` | int64 | observations | adaptive_volume |
| `breadth.observed.advance_fraction` | float64 | fraction | observed_breadth |
| `breadth.observed.advancing_member_count` | int64 | members | observed_breadth |
| `breadth.observed.nonadvancing_member_count` | int64 | members | observed_breadth |
| `breadth.observed.observed_member_count` | int64 | members | observed_breadth |
| `breadth.observed.qualifying_fraction` | float64 | fraction | observed_breadth |
| `breadth.observed.qualifying_member_count` | int64 | members | observed_breadth |
| `breadth.observed.unknown_member_count` | int64 | members | observed_breadth |
| `breadth.session.above_vwap_fraction` | float64 | fraction | session_breadth |
| `breadth.session.advance_decline_ratio` | float64 | ratio | session_breadth |
| `breadth.session.advancing_count` | int64 | members | session_breadth |
| `breadth.session.declining_count` | int64 | members | session_breadth |
| `breadth.session.direction_net_count` | int64 | members | session_breadth |
| `breadth.session.down_volume` | int64 | shares | session_breadth |
| `breadth.session.latest_observed_member_event_ns` | int64 | utc_ns | session_breadth |
| `breadth.session.near_high_fraction` | float64 | fraction | session_breadth |
| `breadth.session.near_low_fraction` | float64 | fraction | session_breadth |
| `breadth.session.positive_momentum_fraction` | float64 | fraction | session_breadth |
| `breadth.session.prior_reference_coverage_fraction` | float64 | fraction | session_breadth |
| `breadth.session.prior_reference_eligible_count` | int64 | members | session_breadth |
| `breadth.session.selected_member_count` | int64 | members | session_breadth |
| `breadth.session.unchanged_count` | int64 | members | session_breadth |
| `breadth.session.up_down_volume_ratio` | float64 | ratio | session_breadth |
| `breadth.session.up_volume` | int64 | shares | session_breadth |
| `cohort.percentile_rank` | float64 | fraction | robust_history |
| `cohort.rank` | int64 | members | robust_history |
| `history.log_return_volatility` | float64 | fraction | daily_log_volatility |
| `intraday.realized_variance` | float64 | fraction | intraday_realized_variance |
| `intraday.realized_volatility` | float64 | fraction | intraday_realized_variance |
| `mean.baseline` | float64 | shares | volume_ratio_mean |
| `mean.numerator` | float64 | shares | volume_ratio_mean |
| `mean.ratio` | float64 | fraction | volume_ratio_mean |
| `pace.baseline_mad` | float64 | shares | volume_pace_robust |
| `pace.baseline_median` | float64 | shares | volume_pace_robust |
| `pace.ratio` | float64 | fraction | volume_pace_robust |
| `pace.robust_z` | float64 | fraction | volume_pace_robust |
| `relative.beta` | float64 | fraction | relative_stats |
| `relative.correlation` | float64 | fraction | relative_stats |
| `relative.residual_return` | float64 | fraction | relative_stats |
| `robust.mad` | float64 | operand-defined | robust_history |
| `robust.median` | float64 | operand-defined | robust_history |
| `robust.percentile_rank` | float64 | fraction | robust_history |
| `robust.quantile` | float64 | operand-defined | robust_history |

Availability, null rules, operand families and minimum periods stay in the three contracts and are not restated.

## (b) Coordinator rulings (decided, pending owner review)

These are the coordinator's rulings. They are decided for the work in flight and are pending owner review; none is an acceptance.

- **R1 Reconstruction mode.** The documented exception stays: for `ef3.relative_stats`, excluded `unknown_availability` and `future_knowledge` evidence rows are omitted in reconstruction mode (the shared `FeatureResult` validator rejects them there because `knowledge_reason` is `None`; RELATIVE_RV_IMPLEMENTATION.md, Author source validation). The shared validator is not amended now, as EF2 made no change to shared validators. Revisit only if the owner asks.
- **R2 Evidence limit.** `evidence_limit` is result-wide, not per output. Fixtures list per-output witnesses, so single-output runs reproduce them and a joint selection truncates in lexical output order (stated in all three implementation documents).
- **R3 Excluded and ineligible witnesses.** They use boundary `ordinary` where the shared validator forbids `completed_interval` (REFERENCE inputs); the `INELIGIBLE` reason is reused for declared exclusions.
- **R4 Observed breadth roster (proposed ruling for a future contract amendment; known divergence).** Proposed: a roster row of another group never blocks a group-scoped result (rows are considered only for the scoped group); unselected roles are not validated; the declared snapshot-id check excludes the population batch. What merged code does, per BREADTH_ADAPTIVE_IMPLEMENTATION.md: note 5 and review note 5 record that roster-level `unknown_availability`/`future_knowledge` is assessed for every record with an event time before the cutoff, before the group filter, so a roster row of another group before the cutoff with null or future `known_at` does block a group-scoped result (about line 175 of `_observed.py`); roles no selected output needs are never validated (so the unselected-roles part already matches); and the declared snapshot check includes the population batch (note 6, `source_id` not compared), which differs from the proposal. The I/O adapter passes such roster rows through unchanged and makes no ruling. This is a divergence to resolve in the release gates, by amending either the contract or the code.
- **R5 Knowledge of bounds, population and edge facts.** The `known_at` of `ef3.session.bounds`, `ef3.population.member` and `ef3.bucket.edge` facts is carried into evidence, not gated (ROBUST_PACE_IMPLEMENTATION.md note 6). Proposed for a future amendment: gate on the knowledge cutoff.
- **R6 Absent roles and builder default.** Absent-role behavior (an absent `sessions` or `grid` slot gives `absent_input` with observed 0; an absent `population` gives cohort `absent_input` with `expected` `None`) and the builders' `evidence_limit=0` default (the contracts say no defaults) are implementation choices, adopted.
- **R7 RB28.** The non-positive `factor_den` clause is unreachable behind RB10 (the shared validator refuses first with `UNSUPPORTED_ADJUSTMENT`): a contract nit; the merged behavior is adopted.
- **R8 P18.** Not buildable literally (cutoff rule RF06 versus the derived evaluation bucket); the alternate construction (target closing at offset 200, cutoff behind the appended session) is accepted as the verification.
- **R9 Refusal codes at the worker layer.** Refusal codes collapse to `INVALID_COMMAND`, as in EF2, and this is accepted. The breadth/adaptive worker additionally maps `INCONSISTENT_IDENTITY` to `RESULT_IDENTITY_MISMATCH` and `OVERFLOW` to `CALCULATION_FAILED` (EF3_BREADTH_ADAPTIVE_WORKER.md); the relative worker document records all codes collapsing to `INVALID_COMMAND`.

## (c) Implementation-chosen identifiers and conventions to pin

None of these is fixed by a frozen contract text unless stated; each should be pinned by the owner, in this amendment or in the I/O layer.

| Item | Chosen value | Where chosen |
| --- | --- | --- |
| Evidence row id, daily and intraday relative/RV | `slot:<index>`, boundary `completed_interval`; compact `instrument:slot:i` is notation | core #692 (Amendment 1 item 3) |
| Evidence ids, robust/pace/mean | `session:<id>`, `target:<id>` (pace), `member:<id>`, `excluded:<id>`, `ineligible:<id>` | core #694; the contract fixtures use them |
| Evidence ids, breadth/adaptive | `member:<instrument_id>`; adaptive witness `seq:<sequence>` | core #695 |
| Coverage entry names, robust/pace | `session:<session_id>` (series), `member:<instrument_id>` (cohort values), `bucket:<session_id>:<index>` (bars) | core #694 note 4; the contract fixes none |
| Coverage, breadth/adaptive | batch-level declaration only, no per-interval names | contract F; io #38 |
| Reference id grammar | `x1:` plus unpadded base64url of the id text (`x1:B(id)` is notation; the literal string is refused) | io #37; library |
| Breadth fact grammars | `bh1:` (six digit zero padded stint, `stint6`), `bf1:` (declared fact roles), `ob1:` (observed fact roles and roster; the contract fixes only the roster), `ao1:` (19 digit zero padded sequence, `seq19`), declared static population `x1:` | core #695 note 3; io #38 |
| Grid version label (volume pace) | `ef3-grid1`; the contract fixtures state none | io #37 |
| Placeholder close for an `unknown` slot (relative/RV) | close 1; the compact notation omits it; the slot is never ready and no output uses it | io #36 |
| Placeholder window and min_history for cohort-only fixtures | 1 and 1; cohort outputs do not read them | io #37 |
| Placeholder row value for exclusion-only slots | value 1, ignored because the session is excluded | io #37 |
| Session ids in I/O fixtures | bare governed index (`"0"`, `"5"`) so witnesses read `session:5`; breadth uses session `0` over `[0, 10^12)` ns | io #37, #38 |
| Breadth I/O constants | population id `SYN-POP`, revision `rev-1`, roster record set `SYN-ROSTER`, epoch `e1`, adaptive event ids `ev<sequence>` | io #38 |
| Entity labels in harnesses | `Q9` (robust/pace, adaptive), `SYN-BREADTH`, `SYN-ROSTER-AGG` | io #37, #38 (harness choices, not contract values) |
| Price rows in robust/pace I/O | volume 100 with open = high = low = close; a null price row has null OHLC and volume 0 | io #37 |
| Units in breadth I/O | scale 2 for declared and observed roles, scale 0 for the adaptive stream | io #38 |
| Mapping versions | not named by the contracts; the EF3 I/O modules carry their own (not read for this document) | io #36 to #38 |
| `DailyGrid` | local immutable grid bound by SHA-256 (`grid_schema`, `grid_sha256`) | core #692 |
| Builders | `evidence_limit` defaults to 0; result `entity` is caller supplied | core #692, #694, #695 |

## (d) Open items not decided (flagged for the owner)

1. **R4 divergence** between the proposed roster/snapshot ruling and merged behavior; which side changes is undecided.
2. **R5** gating of fact `known_at` is undecided beyond the proposal; this needs a future contract amendment.
3. **R1** exception stays unless the owner asks to amend the shared validator.
4. Extra refusals added by the implementation and not in the contract text: fact `session_id` not the target session, adaptive instrument not equal to the result entity, population `text` not equal to the batch snapshot, rational factors on kinds that carry none, price or factors on state, roster or population kinds (BREADTH_ADAPTIVE_IMPLEMENTATION.md note 6, review note 4).
5. Edge `reference_id` uniqueness per edge is not enforced beyond the `x1:` grammar and the shared duplicate check (ROBUST_PACE review note 5).
6. Pace precedence: when no grid bucket fits the actual target session, `ineligible` outranks `future_market` (note 7); the contract pins P10 and P25 only.
7. Coverage cases not fixed by a fixture: incomplete coverage with a missing row (`absent_input` and `governed_gap`), a null rate with warm-up (`null_field`), and the union of unresolved inputs for an unknown direction class.
8. The adapters sort reference facts silently (breadth) or partly (robust/pace), so `INVALID_ORDER` (RB08, RA14) cannot be triggered through the breadth adapter (io #38 document).
9. The exact-zero limits recorded for EF3-D (+0.0 only where the mechanism is exact) and the correlation of exactly plus or minus one (bit-exact only through the perfect-square path) are release-gate limits, as the EF2 equivalents were.
10. The output ownership manifest `docs/plans/equity-output-ownership.json` already contains lines matching EF3 output names (16 lines matched a grep of five sample id prefixes); its EF3 entries were not compared with the 52 headers here and the manifest is not edited.
11. Package version bump (owed at release), whether the purity audit covers the EF3 modules, `tools/check_boundary.py` failing on the base at `ef1/_reference_close.py`, mypy strict (author-reported only), and the E worker are not decided or verified here.
12. Header ledger scale wording (EF2 F7) and the `operand-defined` ledger string versus resolved column units.

## Explicit statements

- Pure additive; no frozen byte changes; no code, validator, fixture or `CONTRACT.json` edit.
- Published results of existing producers are stated unchanged by the three implementation documents through before/after snapshots (R17, EF2 producers, `describe_intraday()` and digest, and earlier EF3 slices); they are cited, not re-run.
- Reset epoch mode only for the adaptive producer; batch API only, no incremental state.
- No numerical, installed-artifact, cross-layer, source-rights, performance or release acceptance is claimed; nothing is accepted.

## What could not be verified

- No library code, tests, mypy or fixtures were run; fixture pass counts (62, 44/24/37/19, 49/20/30 and the refusal sets) are author-reported in the implementation documents and not independently confirmed here.
- The 52, 97, 108 and 147 figures are static counts from the contract JSON; the combined ledger is not enumerated by any code.
- The EF1 counts 11, 66 and 77 are cited from the EF1 amendment.
- I/O and worker documents were read, not executed; the E (robust, pace, mean) worker layer was not read.
- Mapping versions of the EF3 I/O modules were not read.
- Whether the output manifest agrees with the 52 headers was not checked.
