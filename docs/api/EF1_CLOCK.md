# Supplied clock API — EQ165 clock slice

This source-authored candidate adds `clock` dispatch to the explicit `equity_features.ef1` API in development features0.0.4a5/contracts0.0.4a4. Checks have not been executed under the active study resource hold. Status/history diagnostics remain unimplemented; this slice does not complete EQ165. The [frozen contract](../ef1/CONTRACT.json) and [clock mathematics](../features/EF1_CLOCK.md) govern the slice.

Use the existing `build_ef1_config`, `decode_ef1_context`, `ef1_definitions` and `compute_ef1` signatures. Supply full context `{version:"ef1-context1", producer:"clock", calendar:calendar, selection:{}}`. Calendar has exactly calendar_id, revision, timezone, target_date, sessions, segments, scheduled_close_ns and early_close. Session rows are `[id, Gregorian_date, open_ns, close_ns]`; segments are ordered disjoint `[premarket|regular|postmarket,start_ns,end_ns]`. Regular is required and equals the target SessionSpec. All bounds are supplied UTC int64 nanoseconds. Dates/timezone are declarations; the library performs no clock or timezone lookup.

The explicit WindowSpec uses `completed_eod`, exact supplied session IDs/count and the target identity. Target date, bounds, timezone, scheduled close and early-close declaration must equal the actual SessionSpec. `price_unit=None` is permitted. The same canonical ASCII mathematical context limit of4096bytes, nested collection limits and immutable decoder apply. Calendar sessions are finite; no rolling history is silently truncated.

Pass `compute_ef1((proof,), config, entity=entity)` or `()` for absent proof. Only one actual REFERENCE role, `calendar_provenance`, is supported. Its sole row has `fact_kind=ef1.calendar.provenance`, `text=supplied_schedule`, and reference_id `c1:` plus lowercase SHA256 of compact, sorted-key, ensure_ascii JSON of the **entire exact calendar object**. Source snapshot equals calendar revision; mapping_version is `ef1-reference-map1`; namespace/instrument/session match. Original known-at is retained. No price/factor columns are admitted. The finite positive effective interval must encompass every supplied session and phase segment. This is scope evidence, so querying at its right endpoint can still report `closed` when the schedule is available.

Absent/empty, unknown/future-known or incomplete proof makes all five cells null with canonical readiness reasons. Original proof known-at must be nonnull and no later than the requested knowledge cutoff in every availability mode, including explicitly reasoned reconstruction. Omitted/null known-at yields `unknown_availability`; future known-at yields `future_knowledge`. The requested mode, reconstruction reason and C/K/E remain unchanged in result metadata. Malformed identity/hash/revision raises inconsistent_identity; deficient bounds raises bounds. No schedule implies no phase claim. Result source bindings, availability, config digest, backend/version and coverage are original canonical metadata. Output is always the full five-header producer, algorithmv1/schema1, empty bounded evidence:

| ID suffix (`session.clock.`) | dtype | unit |
| --- | --- | --- |
| early_close | bool | boolean |
| phase | string | state |
| regular_elapsed_ns | int64 | ns |
| regular_fraction | float64 | fraction |
| regular_remaining_ns | int64 | ns |

Anchor calls retain their original implementation, three outputs and actual-source semantics. Built-in39 discovery and transport contracts remain unchanged. See the [standalone synthetic example](../../examples/ef1_clock.py).
