# EF1 supplied opening and physical status history

The normative [observable freeze](../ef1/OBSERVABLE_SOURCE_AUTHORING_FREEZE.json)
binds the reviewed [contract](../ef1/OBSERVABLE_CONTRACT_PROPOSAL.md), read with
the metadata-only [publication amendment](../ef1/OBSERVABLE_PUBLICATION_AMENDMENT.md)
and its independent publication packets. This bounded EQ165 subset adds twelve headers across three
separately selected producers. Original consumer/source joins and the complete
EQ165/EQ164 obligations remain open.

For actual supplied regular bounds O,Z and requested market cutoff C, the selected
population is [O,min(C,Z)). Original knowledge must be nonnull and <=K in both
known_at and reconstruction modes. A complete prefix certificate, complete actual
delivery, source capability and causal calendar are required for factual values.
No later-known original record may disappear to make a later trade appear first.

`opening_trade` selects the earliest eligible original TRADE by (event_ns,
order_key). It publishes observed, first_trade_time_ns and checked delay_ns=T-O,
plus admission_state/admission_reason. Complete empty eligibility publishes false
observed and not-applicable null timing. At C<=O the calendar-only result has
not-applicable null observations and expected0/observed0; no zero-width scope is
constructed. `opening_trade_seconds` separately publishes floor(delay_ns/1e9),
with exactly the ns delay's dependency quality and evidence. It never renames ns.

`status_history` counts each qualified original physical event once, independently
of how many flags change. Distinct original identities with equal payload count
separately; duplicate identity or epoch order rejects. Halt and SSR-on are
existential historical facts, not current states. Resume is an explicit mapped
resume or a supplied interrupted-to-active relation. Initial activation is not
resume. Unknown action breaks the relation but cannot erase an already witnessed
positive. A seed is required only for an unresolved boundary relation; count,
halt and SSR remain independent. Original publisher/epoch identity and stable
order are required; row ordinals and payload hashes cannot supply them.

Unavailable/partial scalar values remain null. Positive causal witnesses may
survive in evidence, without asserting an exact partial bool/count. Per-output
quality reconciles calendar+capability+prefix+max(certified, delivered, declared)
record slots, with a seed slot only where needed. It never publishes that maximum
as event_count. Checked int64 arithmetic includes dependency-count addition.

Every original cell is validated before readiness/filtering. Proof hashes bind
actual source/revision/input, selection, calendar, interval and knowledge cutoff.
All supplied bindings remain, including empty/late/unused batches. Consumed
evidence always has original known_at<=K and witness time<=C. Evidence is bounded,
deduplicated and deterministically sorted; no hidden truncation is used.

The closed grammar/map2 preserves source raw fields but provides no source-truth
authentication. Retained historical inputs without original IDs/order remain
unavailable. No private provider thresholds, live acquisition, update/checkpoint,
legacy numerical parity or N-drive dataset acceptance is implied.
