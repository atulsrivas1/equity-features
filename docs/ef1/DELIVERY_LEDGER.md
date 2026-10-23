# EF1 delivery ledger

Inventory as of 2026-10-22 for the [EQ164 #504](https://github.com/atulsrivas1/equity-features/issues/504) audit. This is an inventory, not acceptance: it does not claim anything is accepted, released, tested or complete. Whole EF1 stories remain In progress. Qualification evidence is only what the named docs record; nothing was re-run here.

Method: file existence was checked against `origin/main` of the three repos (core `a32d44e`, I/O `37f9b69`, workers `f5adde5`) using git; contents were not re-validated. "on main" means the file was found there. "not found" means the expected location and the module/feature names were searched and nothing turned up. "unverified" means the claim could not be confirmed from what was found. Owners follow [NUMBERED_LAYER_OWNERS](NUMBERED_LAYER_OWNERS.md): library EQ165 #505, EQ166 #506, EQ167 #507, EQ168 #508; I/O EQ212 #570; workers EQ213 #571; release acceptance EQ169 #509. Story-to-capability attribution comes from [OWNERSHIP_RECONCILIATION](OWNERSHIP_RECONCILIATION.md) and the cumulative qualification notes; where those do not name a story the cell says unverified.

Legend: Lib = `packages/features/src/equity_features/ef1/` in this repo. IO = `equity-feature-io`. Wk = `equity-feature-workers/packages/workers/src/equity_feature_workers/`. Ex = `equity-feature-workers/examples/`.

## 1. Library and worker coverage

| Capability | EQ story | Library feature ids (module in Lib) | Worker module (Wk) / example (Ex) |
| --- | --- | --- | --- |
| Session clock | unverified | `session.clock.{phase,early_close,regular_elapsed_ns,regular_remaining_ns,regular_fraction}` (`_clock.py`), on main | `equity_clock.py`, `ef1_clock.py`, on main |
| Status | unverified | `session.status.{admission_state,admission_reason,<dimension>_state,<dimension>_age_ns}` (`_status.py`), on main | `equity_status.py`, `ef1_status.py`, on main |
| Status history | unverified | `session.status_history.*` (`_observable.py`), on main | `equity_status_history.py`, `ef1_status_history.py`, `ef1_status_history_missing_capability.py`, on main |
| Extended sessions | unverified | `session.extended.*` incl. `session.extended.prior_close_return` (`_period.py`), on main | `equity_extended.py`, `ef1_extended.py`, on main |
| Calendar / period levels | EQ166 #506 (period evidence comment) | `calendar.period.*` incl. scheduled and completed sessions (`_period.py`), on main; the prior-close return is `session.extended.prior_close_return` (extended-sessions row), not a `calendar.period` header (corrected, per the wave 4 field audit) | `equity_period.py`, `ef1_period.py`, on main |
| Anchors, anchored VWAP | unverified | `session.anchor.{vwap,volume,notional}` (`_anchor.py`), on main | `equity_sessions.py`, `ef1_anchors.py`, on main |
| Gaps and gap endpoints | EQ167 #507 | `session.gap.{fill_fraction,filled,first_fill_ns,remaining_fraction}` (`_path.py`); `session.gap_endpoint.{current_fill_fraction,opening_gap_fraction}` (`_gap_endpoint.py`), on main | `equity_path_gap.py`, `equity_gap_endpoint.py`, `ef1_path_gap.py`, `ef1_gap_endpoint.py`, on main |
| Opening trade | unverified | `session.open_observation.*` (admission, delay_ns, first_trade_time_ns, observed) (`_observable.py`), on main | `equity_opening_trade.py`, `equity_opening_trade_seconds.py`, `ef1_opening_trade.py`, `ef1_opening_trade_seconds.py`, on main |
| Opening drive, path drive | EQ167 #507 | `session.opening_drive.{excursion_down,excursion_up,return}` (`_path.py`), on main | `equity_path_drive.py`, `ef1_path_drive.py`, on main |
| Reference action | EQ168 #508 | `reference.gate.{action_state,action_reason}` (`_reference.py`), on main | `equity_reference_action.py`, `ef1_reference_action.py`, on main |
| Reference classification | EQ168 #508 | `reference.classification.value`, `reference.gate.{classification_state,classification_reason}` (`_reference.py`), on main | `equity_reference_classification.py`, `ef1_reference_classification.py`, on main |
| Daily observations | EQ166 #506 (published daily source evidence comment) | `session.daily_observations.*` (`_daily.py`, `_daily_context.py`), on main; prior-only open, high, low and a selected count, no close; selector kinds last_observations (N of 1 to 252 observations), pre_target and latest_observed_prior | `equity_daily_observations.py`, `ef1_daily_observations.py`, on main |
| Regular bar prices | EQ166 #506 | `session.regular.first_completed_bar_open`, `session.close.calculated_price` (`_regular_bar_prices.py`), on main | `equity_regular_bar_prices.py`, `ef1_regular_bar_prices.py`, on main |
| Regular first-trade price | EQ166 #506 | `session.regular.first_trade_price` (`_regular_first_trade_price.py`), on main | `equity_regular_first_trade_price.py`, `ef1_regular_first_trade_price.py`, on main |
| Multi-venue counts, OR summaries, state, latest clock | EQ165 #505 | `session.venue_status.*` (`_venue_status.py`), on main since core #642; contract `MULTI_VENUE_STATUS_CONTRACT_PROPOSAL`; I/O #31 | `equity_venue_status.py`, `ef1_venue_status.py`, on main since workers #73 |
| Supplied-close absolute BPS and tolerance comparison | EQ168 #508 | `reference.close.*` (`_reference_close.py`), on main since core #639; contract `CLOSE_RECONCILIATION_CONTRACT_PROPOSAL` with Amendment 1; I/O #30 | `equity_reference_close.py`, `ef1_reference_close.py`, on main since workers #72 |

Every worker entry point above is also wired in `ef1_runner.py` (`run_ef1_*`), on main. The last two rows are planned outputs in the 47-output ownership manifest, where planned ownership is accepted but mathematical/API bindings are not; at the time this ledger was first written no producer was found for them; both have since been delivered (see the rows above and STATUS.md, 2026-10-22).

## 2. I/O mapping and evidence documents

| Capability | I/O mapping (IO) | Implementation / qualification doc |
| --- | --- | --- |
| Session clock | `packages/duckdb/.../ef1.py` (`ClockInputs`), `docs/api/EF1_CLOCK_INPUTS.md`, on main | core `docs/features/EF1_CLOCK.md`, `docs/api/EF1_CLOCK.md`; workers `docs/EF1_CLOCK_IMPLEMENTATION.md`; on main |
| Status | `ef1.py` (`StatusInputs`), `docs/api/EF1_STATUS_INPUTS.md`, on main | core `docs/features/EF1_STATUS.md`, `docs/ef1/STATUS_INPUT_SLOTS.md`; workers `docs/EF1_STATUS_IMPLEMENTATION.md`; on main |
| Status history, opening trade | `docs/api/EF1_OBSERVABLE_INPUTS.md`, `docs/EF1_OBSERVABLE_IO.md`, on main; separate adapter source file not located: unverified | core `docs/ef1/OBSERVABLE_IMPLEMENTATION.md`; workers `docs/EF1_OBSERVABLE_IMPLEMENTATION.md`; on main |
| Extended sessions, period levels | `docs/EF1_PERIOD_PHASE_IO.md`, on main; adapter source file unverified | core `docs/ef1/PERIOD_PHASE_IMPLEMENTATION.md`; workers `docs/EF1_PERIOD_PHASE_IMPLEMENTATION.md`; on main |
| Anchors, anchored VWAP | `ef1.py` (`AnchorInputs`), `docs/api/EF1_ANCHOR_INPUTS.md`, on main | core `docs/features/EF1_ANCHORS.md`, `docs/reviews/EF1_ANCHOR_SOURCE_REVIEW.md`; workers `docs/EF1_IMPLEMENTATION.md`; on main |
| Gaps, path, opening drive | `ef1.py` (`PathGapInputs`), `docs/api/EF1_PATH_INPUTS.md`, on main | core `docs/features/EF1_PATHS.md`, `docs/ef1/PATH_CONTRACT_PROPOSAL.md` (a proposal); workers `docs/EF1_PATH_IMPLEMENTATION.md`; on main |
| Gap endpoints | `duckdb/.../gap_endpoint.py`, `docs/EF1_GAP_ENDPOINT_IO.md`, on main | core `docs/ef1/GAP_ENDPOINT_QUALIFICATION.md`, `GAP_ENDPOINT_IMPLEMENTATION.md`; workers `docs/EF1_GAP_ENDPOINT_IMPLEMENTATION.md`; on main |
| Reference action, classification | `docs/EF1_REFERENCE_IO.md`, on main; adapter source file unverified | core `docs/ef1/REFERENCE_IMPLEMENTATION.md`; workers `docs/EF1_REFERENCE_IMPLEMENTATION.md`; on main |
| Daily observations | `docs/EF1_DAILY_OBSERVATIONS_IO.md`, `examples/ef1_daily_observations.py`, on main | core `docs/ef1/DAILY_OBSERVATIONS.md`, `DAILY_OBSERVATIONS_VALIDATION.md`; workers `docs/EF1_DAILY_OBSERVATIONS_IMPLEMENTATION.md`; on main |
| Regular bar prices | `duckdb/.../regular_bar_prices.py`, `docs/api/EF1_REGULAR_BAR_PRICES_INPUTS.md`, on main | core `docs/ef1/REGULAR_BAR_PRICES_LOCAL_QUALIFICATION.md`; workers `docs/EF1_REGULAR_BAR_PRICES_IMPLEMENTATION.md`; on main |
| Regular first-trade price | `duckdb/.../regular_first_trade_price.py`, `docs/api/EF1_REGULAR_FIRST_TRADE_PRICE_INPUTS.md`, on main | core `docs/ef1/REGULAR_FIRST_TRADE_PRICE_IMPLEMENTATION.md`; workers `docs/EF1_FIRST_TRADE_INSTALLED_QUALIFICATION.md`; on main |

Cumulative cross-repo evidence: `docs/EF1_CUMULATIVE_QUALIFICATION.md` exists in all three repos (on main). It describes a bounded synthetic installed-artifact cohort at earlier frozen source pins (library `ca6340c`, I/O `55161a5`, workers `1681270`) and states it is not whole EF1 acceptance. The later regular-bar and first-trade slices (core PRs #607, #628) post-date that cohort; their per-slice docs above are the only evidence located for them, and whether an installed-artifact run covers them is unverified. An existing doc is not evidence that its content was accepted; some (for example the path contract) are labelled proposals in their own text.

## 3. Unmerged remote branches `origin/codex/ef1-*`

Ahead = commits on the branch not on main; behind = commits on main not on the branch. Squash check: every file the branch changed since its merge-base under `packages/`, `tests/`, `docs/ef1`, `docs/api`, `docs/features` and `examples/` was compared by blob with main.

| Branch | Ahead / behind | Changed / identical on main / differing / absent from main | Reading |
| --- | --- | --- | --- |
| `ef1-audit-route-publication` | 5 / 8 | 2 / 2 / 0 / 0 | appears squashed into main (#630) |
| `ef1-first-trade-price` | 13 / 8 | 31 / 30 / 1 / 0 | appears squashed (#628); the differing file is `docs/api/PUBLIC_API.md` |
| `ef1-session-clock` | 13 / 31 | 34 / 27 / 7 / 0 | appears squashed (via #589); differing files are shared integration files |
| `ef1-supplied-status` | 18 / 31 | 43 / 36 / 7 / 0 | as above |
| `ef1-sampled-path` | 23 / 31 | 51 / 43 / 8 / 0 | as above |
| `ef1-reference` | 30 / 31 | 57 / 50 / 7 / 0 | as above |
| `ef1-period-phase` | 34 / 31 | 65 / 59 / 6 / 0 | as above |
| `ef1-contracts` | 9 / 31 | 28 / 21 / 7 / 0 | as above |

No file changed on any branch is absent from main. The differing files are mainly `ef1/__init__.py`, `_context.py`, `_definitions.py`, `_dispatch.py`, `packages/features/README.md` and `docs/ef1/COMPANION_QUALIFICATION.md`, which later slices on main also edit. That is consistent with later evolution but the differences were not diffed line by line, so the reading is "appears squashed, residual difference not individually confirmed". This ledger does not merge or delete any branch. `origin/status-ef1-demo-20261021` also exists and is outside the `codex/ef1-*` set.

## 4. Outstanding

- Full EQ164 #504: 296 command routes and the consumer operand gaps unresolved (the 245 counts consumers without a single explicit numerical owner; the 216 representation-slot figure did not reproduce, see docs/ef1/audit/EQ164_WAVE2_X4.md); zero accepted private mathematical/source/consumer bindings (per `NUMBERED_LAYER_OWNERS.md` and `IMPLEMENTATION_ADMISSION.md`).
- Producers not found: neither of the two once listed here remains missing (EQ165 multi-venue and EQ168 supplied-close comparison were delivered after this ledger was first written; see STATUS.md, 2026-10-22).
- Installed Windows/Linux qualification: the recorded cohort is bounded and synthetic and predates some slices (regular bar prices, first-trade price, gap endpoints, daily observations are unverified as covered).
- Real N: DuckDB source demo: not done; synthetic checks do not qualify suitable source data.
- Original-source numerical parity and rights, precision, clocks and benchmarks: not claimed anywhere; the original EQ142 study remains unaccepted.
- Daily-observations corpus demo and browser results demo: pending; generated HTML and verified storage readback do not satisfy the browser gate.
- EF1 release acceptance (EQ169 #509), fresh independent review and package publication: not done.
- Story attribution for clock, status, status history, extended sessions, anchors and opening trade is not stated in the ownership docs; the coordinator should assign it.

## 5. Per-field delivery and core carriers (wave 4 field audit)

Rows above are capability-level. The per-field audit [EQ164_WAVE4_FIELD_DELIVERY](audit/EQ164_WAVE4_FIELD_DELIVERY.md) (47 EF1 fields: 24 matched to merged headers, 11 partial, 12 not delivered) records which merged header carries which field; it is a finding, not parity or acceptance. Core carriers the capability rows omit: `session.bar.high`, `session.bar.low` and `session.bar.close`, `session.price.close_close_return` (regular-session family) and `history.prior_high` and `history.prior_low` (history family). Among the EF1 headers there is no trade-print last-price header and no history-carrier output header; the core history family documents its own `history.*` outputs. A header-level table (one row per header with producer module, unit and selector set) is still to be written.
