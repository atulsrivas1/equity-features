# EF1 producer-set and header-ledger amendment

Proposed by the contract author for review and owner decision, based on main at 0fa8141. This additive amendment preserves the frozen [CONTRACT.json](CONTRACT.json) (ef1-contract1; SHA256 `02940da0c4663bbced050ac551e7fbafe2a1da1534e4c6fa5c87eaf90d420076` is the hash of the CRLF working-copy form only, while the LF blob committed on origin/main hashes to `ff576caace8e89491a634e913e946ac4b0f8cf656faf40745d24da7684c6fe14`; both were recomputed here and are the same text) byte for byte and is recorded as a sibling file, as the observable publication and packaging amendments were. It adds two producers that are already merged in the library: `reference_close` (EQ168 #508; core PR #639, I/O PR #30, workers PR #72) and `multivenue_status` (EQ165 #505; core PR #642, I/O PR #31, workers PR #73). Mathematics, fixtures and decisions stay in [CLOSE_RECONCILIATION_CONTRACT_PROPOSAL.md](CLOSE_RECONCILIATION_CONTRACT_PROPOSAL.md) (including Amendment 1) and [MULTI_VENUE_STATUS_CONTRACT_PROPOSAL.md](MULTI_VENUE_STATUS_CONTRACT_PROPOSAL.md); the record of this amendment is [PRODUCER_SET_AMENDMENT.json](PRODUCER_SET_AMENDMENT.json). It closes the owed items named in `CLOSE_RECONCILIATION_IMPLEMENTATION.md` (O5) and `MULTI_VENUE_STATUS_IMPLEMENTATION.md` (D10). The code facts below were read from `_reference_close.py`, `_venue_status.py`, `_definitions.py`, `_context.py` and `_dispatch.py`; nothing was executed.

## Additive producer-set entries

| Item | `reference_close` | `multivenue_status` |
| --- | --- | --- |
| Config identity | `ef1.reference_close` | `ef1.multivenue_status` |
| Algorithm / schema | `v1` / `1` | `v1` / `1` |
| Parameter | exactly `ef1_context_json` (`ef1-context1`) | same |
| Roles in slot order (all fixed, nullable) | `calendar_provenance` (reference), `bars` (bar), `population_proof` (reference), `authoritative_close` (reference) | `venue_population`, `venue_seed`, `venue_states`, `venue_prefix`, `venue_validity` (all reference) |
| Calendar | required, target-only single session, as `regular_bar_prices`; `reference_close` joins the frozen `calendar_required_for` list | null; `multivenue_status` joins the frozen `calendar_null_for` list |
| Selection exact keys | `phase_profile`, `policy_version`, `sampling`, `scope_id`, `tolerance_bps_den`, `tolerance_bps_num` | `clock_dimensions`, `epoch`, `max_age_ns`, `population_id`, `population_revision`, `state_policy` (`policy_id`, `policy_version`, `precedence`) |
| Fixed values | `regular_no_auctions1`, `completed_bar_close`, policy label `ef1-close-compare1` | `venue_precedence_v1`, version `1` |
| Mapping version | `ef1-reference-map1` for the `authoritative_close` role; calendar and population roles unchanged from EQ166 | `ef1-venue-map1` (new) |
| Price unit | mandatory; ordinary regular session, `open_ns < market_cutoff_ns <= close_ns` | must be null; window target-only, count 1, `completed_eod` |
| Result evidence limit | 7 | 4 |

Unchanged: existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult` and scalar `ValueType` set; `compute_ef1` and `ef1_definitions` signatures; the ef1-context1 envelope (4096 codepoints and UTF8 bytes, depth 8); the 4096 aggregate reference-row bound; the 128 result evidence limit (both producers stay below it); the 1 MiB task bound; no new DataKind, DTO, result codec, scheduler or default; the default registry. Each producer returns its complete sorted header set from one homogeneous config.

## Header ledger additions

Eleven headers, lexical by feature id. Counts, bools and the state strings are full-range typed values; null means the output is unavailable with the quality status and reason of the producer contract.

| Feature id | dtype | unit | scale | Null / availability rule |
| --- | --- | --- | --- | --- |
| `reference.close.absolute_difference_bps` | float64 | bps | none | null unless the calculated close is ready and the supplied close is admitted with a positive denominator |
| `reference.close.comparison_state` | string | state | none | always available, 1/1, no reasons; six-value closed vocabulary |
| `reference.close.supplied_price` | decimal128 | currency/share | integer coefficient at `PriceUnit.scale` | null unless one causal complete-coverage positive row and cutoff equals the actual close; provisional cutoff gives `incomplete_coverage`/`governed_gap`, no witness |
| `reference.close.within_tolerance` | bool | boolean | none | same availability as BPS; exact inclusive integer verdict |
| `session.venue_status.aggregate_reason` | string | reason | none | always available, 1/1 |
| `session.venue_status.aggregate_state` | string | state | none | null unless every expected trading fact is known or the top-ranked state dominates |
| `session.venue_status.known_nontrading_count` | int64 | publishers | 0 | null unless every expected publisher trading fact is known |
| `session.venue_status.known_trading_count` | int64 | publishers | 0 | null unless every expected publisher trading fact is known |
| `session.venue_status.latest_event_ns` | int64 | utc_ns | 0 | null unless all declared clock facts are eligible or the maximum equals C-1 |
| `session.venue_status.quoting_any` | bool | boolean | none | true on one known positive; false only if all quoting facts are known disabled; else null |
| `session.venue_status.restriction_any` | bool | boolean | none | true on one known positive; false only if all ssr facts are known off; else null |

**Header counts.** `CONTRACT.json` parses to 45 headers; this amendment makes the frozen-file ledger 56 if it is ever regenerated. The merged `_definitions.py` already defines more than the frozen file: the nine frozen producers give 45, and later reviewed producers add `path_gap_endpoint` 2, `regular_bar_prices` 2, `regular_first_trade_price` 1, `daily_observations` 4, `status_history` 6, `opening_trade` 5 and `opening_trade_seconds` 1, which is 21, so 66 before and 77 after this amendment. These are static readings of the source, not an executed enumeration, and assume one header set per producer, not one per status dimension (the single-publisher `status` producer's dimension-specific ids are counted once, as in the frozen file) (see FINDING F1).

## Unit additions

Frozen units: `boolean`, `classification`, `currency`, `currency/share`, `fraction`, `ns`, `reason`, `sessions`, `shares`, `state`. New relative to the frozen `CONTRACT.json` unit set:

- `bps` (reference.close.absolute_difference_bps, float64).
- `publishers` (the two venue counts, int64).
- `utc_ns` (venue latest_event_ns, int64). The merged `VENUE_FIELDS` emits exactly `utc_ns` for this header, matching the multi-venue contract, so the amendment follows the code. The frozen ledger used `ns` for ages and clock deltas; absolute clocks use `utc_ns`, as the merged `opening_trade` header `first_trade_time_ns` already does.

## Explicit statements

- Pure additive; no frozen byte changes, no edit to `CONTRACT.json`.
- Existing producers' published results are unchanged. The merged implementation records state that the shared selection helper added to the EQ166 module (`_select_regular_bars`, with the unchanged final `float(Fraction(p, 10**scale))` conversion) was checked by a before/after snapshot of 381 EQ166 and first-trade oracle outcomes (results and refusals) that was byte-identical. This amendment cites that record; it did not re-run it.
- No change to the ef1-contract1 label, `equity-features` 0.0.4a5 or `contracts` 0.0.4a4.
- `tests/unit/test_purity_audit.py` and its module list are **not** updated by this PR; whether `_reference_close` and `_venue_status` are audited is an owner decision, pending.
- No numerical, installed-artifact, cross-layer, source-rights or release acceptance follows.

## FINDINGS

- **F1 header count.** The multi-venue contract and `IMPLEMENTATION_ADMISSION.md` speak of 45 frozen headers. That is true of `CONTRACT.json`, but the merged code-wide ledger was already 66 before these producers (77 after). Both numbers are given above; no count was guessed, but the 66 is a static reading.
- **F2 units.** The multi-venue contract (D10) calls `utc_ns` new. That holds relative to `CONTRACT.json` only. The merged code also emits `count`, `s`, `price` and `observations` (observable and daily producers), likewise absent from the frozen set and not covered here; a separate unit reconciliation is owed.
- **F3 mapping versions.** `ef1-close-compare1` is the comparison policy label carried in `selection.policy_version`, not a mapping version. The close role mapping version is `ef1-reference-map1`; only `ef1-venue-map1` is a new mapping version.
- **F4 calendar lists.** The frozen `calendar_required_for` and `calendar_null_for` lists must gain `reference_close` and `multivenue_status` respectively; they are recorded here, not edited in the frozen file. Those frozen lists also omit other post-freeze producers; verified from `_context.py` (each calls the calendar check): `regular_bar_prices`, `regular_first_trade_price` and `path_gap_endpoint` require a calendar. The observable and `daily_observations` producers have their own calendar handling that was not fully read, so they are not classified here.

## What could not be verified

Nothing was executed and no tests were run. The I/O and worker repositories (PRs #30, #31, #72, #73) were not read, so worker admission and sink behavior of the two producers are unverified. Header counts are static. The byte-identity claim is cited from merged documentation. Installed artifacts, CI results and the snapshot script were not available. Full EQ164 audit, consumer joins, browser verification and release gates remain open.
