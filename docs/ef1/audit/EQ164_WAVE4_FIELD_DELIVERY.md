# EQ164 wave 4 (W4-A): per-field delivery of the EF1 fields

October 22, 2026. Base commit `597e0c3`. Findings only: no code, contract or tracker change. This answers decision Q4 of [EQ164_WAVE3_DECISIONS.md](EQ164_WAVE3_DECISIONS.md). A MATCHED verdict is a finding that a merged public header carries the same class of meaning; it is not numerical, source-parity, rights or consumer acceptance, and no row becomes Ready. Opaque ids only; meanings are stated at class level.

## Scope and method

Set: every opaque field id that appears as an operand in [X3](EQ164_WAVE2_X3.json), [scanners 1](EQ164_WAVE3_SCANNERS_1.json), [scanners 2](EQ164_WAVE3_SCANNERS_2.json) or [watchlists](EQ164_WAVE3_WATCHLISTS.json) (133 distinct ids) and whose proposed owner in [the route coverage](../../plans/equity-audit-route-coverage.json) is an EF1 story (#505, #506, #507, #508, #570, #571). That gives **47 fields**. The second criterion (the note "capability present on main; per-field binding unproven") selects 36 ids, all already inside the owner-based set.

Method: each field was reduced to a class-level meaning (unit, window, inclusion rule, session scope, basis), then compared with the headers defined in `packages/features/src/equity_features/ef1/_definitions.py`, the producer modules and `docs/api`, `docs/features`, `docs/ef1`. Verdicts: MATCHED_BY_MERGED_HEADER (same class of meaning is carried by a merged header, possibly under a caller-chosen selector or with a pure unit scaling), PARTIAL_MATCH (a header covers part of the meaning; the difference is named), NOT_DELIVERED (no merged header carries it), UNDETERMINED (evidence missing; none needed here).

## Counts

| Verdict | Fields |
| --- | --- |
| MATCHED_BY_MERGED_HEADER | 24 |
| PARTIAL_MATCH | 6 |
| NOT_DELIVERED | 17 |
| UNDETERMINED | 0 |
| Total | 47 |

## Per owner story (primary owner in the route coverage)

| Primary owner | Matched | Partial | Not delivered | Undetermined | Total |
| --- | --- | --- | --- | --- | --- |
| #505 | 0 | 1 | 0 | 0 | 1 |
| #506 | 21 | 3 | 8 | 0 | 32 |
| #507 | 1 | 2 | 0 | 0 | 3 |
| #508 | 0 | 0 | 4 | 0 | 4 |
| #570 | 2 | 0 | 5 | 0 | 7 |

Reading: #506 holds most fields and most matches because the daily-observation, regular-bar, first-trade, period and extended producers sit under it. All five #508-owned fields are NOT_DELIVERED. The two #570-owned matches are the sector and industry labels, whose merged producer is the #508 classification subset (route and producer owner differ).

## Matched fields

| Field | Merged header | Producer module | Class-level note | Confidence |
| --- | --- | --- | --- | --- |
| F0255 | `reference.classification.value` | `_reference.py` | The header returns the causal active membership text for the selected membership kind (sector, industry or universe), one producer configuration per kind. The gate state and reason headers carry availability. | medium |
| F0256 | `reference.classification.value` | `_reference.py` | The header returns the causal active membership text for the selected membership kind (sector, industry or universe), one producer configuration per kind. The gate state and reason headers carry availability. | medium |
| F0271 | `session.regular.first_trade_price` | `_regular_first_trade_price.py` | Same meaning: first eligible regular-session trade price, currency per share. The delivery ledger attributes this producer to #506, which bears on the D8 owner question. | medium-high |
| F0272 | `session.gap_endpoint.opening_gap_fraction` | `_gap_endpoint.py` | The header is the fraction (O-P)/P with O the first selected regular sample (trade sampling) and P the supplied prior close. The private measure is the same ratio scaled by 100 (percent) and uses zero when the prior close is absent; the header unit is a fraction and absence is a null with reasons. The factor 100 and zero-versus-null are conversion items, not a semantic gap. | medium-high |
| F0275 | `session.daily_observations.high` | `_daily.py` | Selector last_observations with N=1 over admitted completed daily observations strictly before the target (prior-only window). Admission, quality limits and basis conversion are caller policy in the daily context. | medium |
| F0276 | `session.daily_observations.low` | `_daily.py` | Selector last_observations with N=1 over admitted completed daily observations strictly before the target (prior-only window). Admission, quality limits and basis conversion are caller policy in the daily context. | medium |
| F0309 | `session.daily_observations.high` | `_daily.py` | Selector last_observations with N=5 (allowed range 1 to 252), prior-only, earliest tie. The private window is a fixed session count, so a civil-month window (calendar.period rolling_months) would be a different rule; minimum history is daily-context policy. | medium |
| F0310 | `session.daily_observations.low` | `_daily.py` | Selector last_observations with N=5 (allowed range 1 to 252), prior-only, earliest tie. The private window is a fixed session count, so a civil-month window (calendar.period rolling_months) would be a different rule; minimum history is daily-context policy. | medium |
| F0311 | `session.daily_observations.high` | `_daily.py` | Selector last_observations with N=10 (allowed range 1 to 252), prior-only, earliest tie. The private window is a fixed session count, so a civil-month window (calendar.period rolling_months) would be a different rule; minimum history is daily-context policy. | medium |
| F0312 | `session.daily_observations.low` | `_daily.py` | Selector last_observations with N=10 (allowed range 1 to 252), prior-only, earliest tie. The private window is a fixed session count, so a civil-month window (calendar.period rolling_months) would be a different rule; minimum history is daily-context policy. | medium |
| F0313 | `session.daily_observations.high` | `_daily.py` | Selector last_observations with N=20 (allowed range 1 to 252), prior-only, earliest tie. The private window is a fixed session count, so a civil-month window (calendar.period rolling_months) would be a different rule; minimum history is daily-context policy. | medium |
| F0314 | `session.daily_observations.low` | `_daily.py` | Selector last_observations with N=20 (allowed range 1 to 252), prior-only, earliest tie. The private window is a fixed session count, so a civil-month window (calendar.period rolling_months) would be a different rule; minimum history is daily-context policy. | medium |
| F0315 | `session.daily_observations.high` | `_daily.py` | Selector last_observations with N=63 (allowed range 1 to 252), prior-only, earliest tie. The private window is a fixed session count, so a civil-month window (calendar.period rolling_months) would be a different rule; minimum history is daily-context policy. | medium-low |
| F0316 | `session.daily_observations.low` | `_daily.py` | Selector last_observations with N=63 (allowed range 1 to 252), prior-only, earliest tie. The private window is a fixed session count, so a civil-month window (calendar.period rolling_months) would be a different rule; minimum history is daily-context policy. | medium-low |
| F0317 | `session.daily_observations.high` | `_daily.py` | Selector last_observations with N=126 (allowed range 1 to 252), prior-only, earliest tie. The private window is a fixed session count, so a civil-month window (calendar.period rolling_months) would be a different rule; minimum history is daily-context policy. | medium-low |
| F0318 | `session.daily_observations.low` | `_daily.py` | Selector last_observations with N=126 (allowed range 1 to 252), prior-only, earliest tie. The private window is a fixed session count, so a civil-month window (calendar.period rolling_months) would be a different rule; minimum history is daily-context policy. | medium-low |
| F0319 | `session.daily_observations.high` | `_daily.py` | Selector pre_target with period civil_ytd: completed observations of the target civil year strictly before the target session. calendar.period year with current_to_cutoff would also include the target bar prefix, so it is not the matching header. | medium |
| F0320 | `session.daily_observations.low` | `_daily.py` | Selector pre_target with period civil_ytd: completed observations of the target civil year strictly before the target session. calendar.period year with current_to_cutoff would also include the target bar prefix, so it is not the matching header. | medium |
| F0321 | `session.daily_observations.high` | `_daily.py` | Selector latest_observed_prior with period iso_week: the most recent populated prior period. calendar.period with prior_complete would instead select the immediately preceding civil period even if empty, so it is not the matching header. | medium |
| F0322 | `session.daily_observations.low` | `_daily.py` | Selector latest_observed_prior with period iso_week: the most recent populated prior period. calendar.period with prior_complete would instead select the immediately preceding civil period even if empty, so it is not the matching header. | medium |
| F0323 | `session.daily_observations.high` | `_daily.py` | Selector latest_observed_prior with period civil_month: the most recent populated prior period. calendar.period with prior_complete would instead select the immediately preceding civil period even if empty, so it is not the matching header. | medium |
| F0324 | `session.daily_observations.low` | `_daily.py` | Selector latest_observed_prior with period civil_month: the most recent populated prior period. calendar.period with prior_complete would instead select the immediately preceding civil period even if empty, so it is not the matching header. | medium |
| F0463 | `session.daily_observations.high` | `_daily.py` | Selector last_observations with N=1 over admitted completed daily observations strictly before the target (prior-only window). Admission, quality limits and basis conversion are caller policy in the daily context. | medium |
| F0464 | `session.daily_observations.low` | `_daily.py` | Selector last_observations with N=1 over admitted completed daily observations strictly before the target (prior-only window). Admission, quality limits and basis conversion are caller policy in the daily context. | medium |

## Partial matches

| Field | Nearest merged header | Producer module | Difference | Confidence |
| --- | --- | --- | --- | --- |
| F0150 | `session.close.calculated_price` | `_regular_bar_prices.py` | Same unit (currency per share) and same session. The header is the last positive-volume close of causally admitted completed regular bars (provisional prefix); the private meaning is the last trade price of the session. Basis differs at class level: completed-bar close versus trade-print close, and closing-auction print handling is not shown to coincide. | medium |
| F0162 | `session.status.trading_state` | `_status.py` | The header is a closed-vocabulary state (active, halted, closed) of the last supplied transition strictly before the cutoff, inside a proved prefix and validity interval. The private meaning is the last status code seen in the input, with no cutoff, prefix proof or vocabulary mapping. Value domain and causal selection differ. | medium |
| F0206 | `session.extended.prior_close_return` | `_period.py` | The header exists only for premarket and postmarket phases (phase close versus predecessor regular close, as a fraction). The private meaning applies to the latest price in any phase and is scaled as percent; no header covers the regular session. The delivery ledger and the wave 2 note place a prior-close return under calendar.period, but main defines it only under session.extended. | medium |
| F0267 | `session.extended.high` | `_period.py` | The header is the extremum of supplied completed interval highs inside the supplied premarket phase prefix. The private meaning is the extremum over individual trade prints in the premarket phase. Sampling basis (interval bars versus trade prints) differs; phase bounds are supplied calendar segments in the header. | medium |
| F0268 | `session.extended.low` | `_period.py` | The header is the extremum of supplied completed interval lows inside the supplied premarket phase prefix. The private meaning is the extremum over individual trade prints in the premarket phase. Sampling basis (interval bars versus trade prints) differs; phase bounds are supplied calendar segments in the header. | medium |
| F0273 | `session.gap_endpoint.current_fill_fraction` | `_gap_endpoint.py` | Same clamped fill ratio on the final selected observation, but as a fraction rather than a 0 to 100 scale. Inclusion differs: the header uses the final selected observation inside the regular path scope, while the private latest price also reflects extended-hours prints. Zero-gap and absent-input handling (zero versus null) also differ. | medium |

## Not delivered

| Field | Class-level meaning | Why no merged header carries it | Confidence |
| --- | --- | --- | --- |
| F0137 | instrument identity key of the row | No feature header carries identity; the entity is the explicit EntityKey argument of the compute call and result metadata. | high |
| F0148 | regular-session high of the observation row | No header gives a regular-session extremum for the target session. session.extended.* covers only premarket and postmarket phases; calendar.period.* has week, month, year and rolling kinds with no single-session kind; session.daily_observations.* excludes the target session by construction. | medium-high |
| F0149 | regular-session low of the observation row | No header gives a regular-session extremum for the target session. session.extended.* covers only premarket and postmarket phases; calendar.period.* has week, month, year and rolling kinds with no single-session kind; session.daily_observations.* excludes the target session by construction. | medium-high |
| F0173 | path-feature completeness flag of the row | Availability flags are not feature headers. Readiness of the paired numeric header is reported as per-output status and quality in the result, not as a value; whether such a flag is derived from that readiness or supplied is a contract item. | medium |
| F0179 | serialized volume-anomaly summary blob | No header exists; a structured blob is not a scalar feature value. | high |
| F0186 | event time of the latest applied observation | No header echoes an event time. session.clock.* are functions of the supplied evaluation cutoff and calendar, not of the latest observation. | high |
| F0188 | latest trade price at the evaluation time, any phase | No last-price header. session.close.calculated_price is a completed-bar close of regular bars, not a latest print that includes extended hours. | medium-high |
| F0190 | running regular-session high at the evaluation cutoff | Same gap as the row-level extremum: no running regular-session extremum header exists on main, so the session extremum that D7 assigns to #506 is not delivered. | medium-high |
| F0191 | running regular-session low at the evaluation cutoff | Same gap as the row-level extremum: no running regular-session extremum header exists on main, so the session extremum that D7 assigns to #506 is not delivered. | medium-high |
| F0218 | prior-close availability flag | Availability flags are not feature headers. Readiness of the paired numeric header is reported as per-output status and quality in the result, not as a value; whether such a flag is derived from that readiness or supplied is a contract item. | medium |
| F0259 | as-of date identity of the relative value | No header or metadata echo of a relative-value as-of date exists; the concept belongs to relative-value producers, which are not EF1 headers on main. | medium |
| F0283 | prior-day level availability flag | Availability flags are not feature headers. Readiness of the paired numeric header is reported as per-output status and quality in the result, not as a value; whether such a flag is derived from that readiness or supplied is a contract item. | medium |
| F0284 | regular-open availability flag | Availability flags are not feature headers. Readiness of the paired numeric header is reported as per-output status and quality in the result, not as a value; whether such a flag is derived from that readiness or supplied is a contract item. | medium |
| F0338 | supplied recent completed daily-bar history carrier | Daily history is an input role of the period and daily-observation producers; no header outputs history. Length, adjustment and completed-only versus current-inclusive profile are not fixed by any merged header. | high |
| F0432 | count of history bars excluded by quality screening | session.daily_observations.selected_observed_count counts raw-admitted selected observations, not excluded ones, and no other EF1 header carries an exclusion count. | medium |
| F0434 | close of the last completed session of the reference history | Daily observations expose open, high, low and a count but no close. session.close.calculated_price is the close of the target session, a different time position. | medium |
| F0460 | corporate-action suspicion flag from the reference history | reference.gate.action_state is declaration and history admission only and never infers a suspicion from prices; no header carries an inferred-split flag. | medium |

Evidence per field (public file names only) is in the JSON companion `EQ164_WAVE4_FIELD_DELIVERY.json`, one record per field.

## Mismatches with the wave 3 decisions and the delivery ledger

1. **Ledger, calendar and period row.** The ledger lists a prior-close return under `calendar.period.*`. `_definitions.py` defines `prior_close_return` only for the extended producer (`session.extended.prior_close_return`); `calendar.period.*` has nine headers and no prior-close return. The wave 2 X3 note for the change-versus-prior-close field (F0206) repeats the same attribution. Effect: F0206 is only a PARTIAL_MATCH (extended phases only).
2. **Wave 2 X3 class DELIVERED_ON_MAIN for F0150.** Wave 3 correctly stopped treating this as delivered. The finding here is PARTIAL_MATCH: the header is a completed-bar close, the field is a trade-print close of the session.
3. **Route owner versus producer owner.** F0255 and F0256 are routed to #570/#571 but the merged producer is the #508 classification subset. F0271 carries both #505 and #506 routes; the ledger attributes the first-trade-price producer to #506.
4. **Wave 3 D9 wording.** D9 binds level windows to "the delivered period and daily-observation outputs". On main only the daily-observation outputs match the 18 level fields (F0275, F0276, F0309 to F0324) and also F0463, F0464: they are prior-only, whereas `calendar.period.*` with `current_to_cutoff` includes the target bar prefix and with `prior_complete` selects the immediately preceding civil period even when empty. So the period producer should not be named as the carrier of these fields.
5. **Wave 3 D7.** The withdrawal of the #21 proposal relies on a #506 session extremum. No merged header carries a regular-session high or low (F0148, F0149, F0190, F0191); session.extended.* is premarket and postmarket only. D7 therefore depends on an undelivered #506 output.

## Rows where D8, D9 and D9H contract items are implicated

| Item | Fields | Finding |
| --- | --- | --- |
| D8 unit | F0272, F0273 | Merged headers are fractions (`session.gap_endpoint.opening_gap_fraction`, `current_fill_fraction`). F0272 is a MATCH after a pure factor-100 scaling; F0273 is PARTIAL because the latest price also reflects extended-hours prints and zero/null handling differs. Supports the D8 choice of fraction with percent as presentation. |
| D8 owner | F0271 | `session.regular.first_trade_price` is merged under the #506 attribution in the ledger; consistent with D8 proposing #506. |
| D9 windows | F0275, F0276, F0309 to F0324 | All matched by `session.daily_observations.high` and `.low` through selectors: last_observations (N=1, 5, 10, 20, 63, 126), pre_target civil_ytd, latest_observed_prior (iso_week, civil_month). Current-session inclusion is settled for these headers: the target is excluded. The 3-month and 6-month fields match only if the contract treats them as 63 and 126 sessions (lower confidence); as civil months they would be a different rule. |
| D9 distance versus level | F0212 to F0217 | Not in this audit set (not EF1-owned in the route coverage). |
| D9H | F0338 | NOT_DELIVERED: the history is an input role, not a header. Length, adjustment and completed-only versus current-inclusive remain contract items. The daily producer is itself prior-only and requires a declared admission profile, which supports but does not settle the completed-only working assumption. |
| Availability gates | F0173, F0218, F0283, F0284 | Flags are not headers; per-output status and quality carry readiness. Whether to derive or supply them is a contract item. |

## Recommended ledger corrections (proposals only, no edit made)

1. Move the prior-close return from the calendar and period row to the extended-sessions row, as `session.extended.prior_close_return`.
2. Add a header-level table (one row per merged header with producer module, unit and selector set) so per-field bindings can be checked; the present rows are capability-level.
3. In the daily-observations row, list the selector kinds (last_observations N=1 to 252, pre_target, latest_observed_prior) and note that the producer is prior-only and exposes open, high, low and a selected count, with no close.
4. Record that no regular-session high or low header, no last-price header and no history-carrier header exists on main.
5. Record the owner attribution gaps still open in the ledger (clock, status, status history, extended sessions, anchors, opening trade story attribution); the status header is the nearest carrier of F0162 and has no named owner.

## Limits

- Findings come from reading the merged definitions, producer modules and public docs; nothing was executed, so no numerical equivalence is claimed.
- Class-level meanings were derived from the owner's read-only private material; none of its content is reproduced here. The 3-month and 6-month window rule (sessions versus civil months) is the main residual uncertainty.
- Three-repo I/O and worker bindings were not audited; only the core headers were.
- No UNDETERMINED verdicts were needed; confidence labels carry the residual doubt.
