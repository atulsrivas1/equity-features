# Supplied current-status API — EQ165 subset

This additive source candidate extends the existing equity_features.ef1 build_ef1_config, decode_ef1_context, ef1_definitions and compute_ef1 API for features0.0.4a5/contracts0.0.4a4. It preserves existing anchor/clock dispatch and built-in39 discovery. No local runtime qualification has run during EQ142's resource reservation. Current-state support does not complete original observable history/open diagnostics or EQ165.

Context is {version:"ef1-context1",producer:"status",calendar:calendar,selection:{dimension,epoch,seed_reference_id,max_age_ns}}. Dimension is exactly trading/quoting/ssr. Epoch is a bounded supplied identity; seed_reference_id is null or an exact original s1 row identity. Maximum age is null or nonnegative int64, with null meaning no event-age expiry. Config identity is ef1.status. Calendar, exact WindowSpec/session binding, calendar hash proof, recursive immutability and canonical ASCII4096byte context bound follow the [supplied clock API](EF1_CLOCK.md). Source facts never belong in context.

The reviewed [slot/proof amendment](../ef1/STATUS_INPUT_SLOTS.md) and [freeze receipt](../ef1/STATUS_INPUT_SLOTS_FREEZE.json) define exactly four ordered in-process status slots: calendar_provenance, status_states, status_prefix, status_validity. Each is an actual CanonicalBatch REFERENCE or explicit None for missing. Empty actual batches retain their slots. This does not change WorkItem/wire serialization or the existing anchor/clock present-only calls. Workers remain responsible for passing declared missing roles explicitly at the pure call boundary.

Closed status fact kinds are ef1.status.trading, ef1.status.quoting, ef1.status.ssr. Texts are active/halted/closed, enabled/disabled and on/off respectively. Identity is s1:D:B(epoch):seq19:B(event_id), where D=t/q/s and seq19 is exactly19 decimal digits of nonnegative int64 semantic sequence. B is reversible canonical unpadded UTF8 base64url; invalid encoding, noncanonical pad bits, controls, surrogates and overflow reject. Prefix/validity IDs are p1:D:B(epoch):B(actual_status_input_id):B(certificate_id), kinds ef1.status.prefix_complete/ef1.status.validity, text D. Actual input IDs are distinct. Mapping version is ef1-reference-map1. No price or factor columns are admitted. With absent status states, present proofs must still agree on decoded target and source/revision without fabricating an absent input identity. Certificate candidates are counted by scope before knowledge admission; multiple applicable candidates reject even if one is late. Inputs are already canonically ordered by effective_start_ns/reference_id and additionally respect semantic sequence. Never sort or create completeness from gaps/counts.

Always returns exactly four canonical scalar headers, algorithmv1/schema1:

| ID suffix (session.status.) | dtype | unit |
| --- | --- | --- |
| admission_reason | string | reason |
| admission_state | string | state |
| selected_dimension_age_ns | int64 | ns |
| selected_dimension_state | string | state |

Each config selects only one dimension, with its own digest/job/generation. Result metadata retains every actual input binding, original availability and exact config digest. State/age require original causal calendar, seed, stream and proof evidence in all modes; diagnostic quality1/1 reports evaluation readiness. See [mathematics and literal S01–S03](../features/EF1_STATUS.md). When current identity is proved, state and age each carry one original canonical EvidenceRow: actual status input_id/reference_id, original effective time, known-at and effective bounds. Normal witnesses are consumed; explicit max-age rejection marks only the state witness excluded/ineligible. Unproved current identity emits no current witness. Evidence is bounded at two rows; no alternate DTO, result codec or evidence shape is introduced.

Malformed grammar/sequence/vocabulary, wrong actual source/revision/target/epoch, duplicate identities, invalid canonical order or overflow raises typed ContractError. Empty/missing/incomplete, unknown/future knowledge and finite expiry stay separate from structural rejection. Context and aggregate <=4096reference-row admission across all present slots, including calendar, remain bounded; actual worker1MiB task admission remains independently mandatory. No provider, storage, scheduling or wall-clock code enters calculations.

See the [synthetic standalone example](../../examples/ef1_status.py) and [independent literal goldens](../ef1/STATUS_LITERAL_GOLDENS.json). This documentation records source preparation; independent source review, remote CI, numerical, installed, integration, browser and release acceptance remain pending.


Validity's original known-at is checked for a uniquely scope-applicable required certificate even when a required transition is unknown/late. Prefix/transition prerequisites gate semantic expiry/max-age only. Combined failures retain all independently applicable factual reasons; unavailable current identity emits no witness.
