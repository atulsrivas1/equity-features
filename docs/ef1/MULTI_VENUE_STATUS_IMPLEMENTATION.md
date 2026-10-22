# Multi-venue status implementation

[EQ165 #505](https://github.com/atulsrivas1/equity-features/issues/505) library layer: the opt-in `multivenue_status` producer through the existing EF1 builder, decoder, discovery and dispatcher. The frozen [multi-venue status contract](MULTI_VENUE_STATUS_CONTRACT_PROPOSAL.md) (`ef1-multivenue-status1`, decisions D01 to D16 and its coordinator freeze) governs; this slice implements it and redefines nothing. The I/O mapping (EQ212) and worker (EQ213) layers, full EQ164 and release gates remain separate.

The seven outputs, in lexical header order, are `session.venue_status.aggregate_reason` (STRING, `reason`), `aggregate_state` (STRING, `state`), `known_nontrading_count` and `known_trading_count` (INT64, `publishers`), `latest_event_ns` (INT64, `utc_ns`), `quoting_any` and `restriction_any` (BOOL, `boolean`). The single-publisher `status` producer is untouched.

## Behavior

Five nullable fixed slots (`venue_population`, `venue_seed`, `venue_states`, `venue_prefix`, `venue_validity`), all REFERENCE with mapping `ef1-venue-map1`. Every row of every present slot is validated before any semantics, with the typed refusals of the contract (duplicate, inconsistent identity, order, bounds, closed vocabulary, slot shape, config). The expected population is the applicable members in batch order and is never reduced by missing facts. Each (publisher, dimension) stream is evaluated as a known, stale (clock proved, state withheld) or unknown fact with the first finding of `absent_input`, `incomplete_status_prefix`, `unknown_availability`, `future_knowledge`, `outside_effective_interval`, `stale_state`; the seven outputs then follow the contract's null-unless-complete counts, single-witness OR flags, precedence dominance and C-1 latest-clock saturation. Evidence (limit 4) cites original states rows in the order aggregate_state, quoting_any, restriction_any, latest_event_ns.

The precedence policy is caller supplied (`venue_precedence_v1`, version `1`, a permutation of active/halted/closed); there is no default order. Calendar is null; price unit must be null; the window is target-only.

## Source validation

A standalone manual script (not committed, no test files added) built canonical packets from the contract JSON and compared every value, status, reason, expected/observed count and witness (publisher, dimension, order and original row fields) for the 42 result fixtures and the typed error code for the 13 refusals: all matched, no expected value altered. A before/after snapshot of 381 EQ166 and first-trade oracle outcomes was byte-identical. `tests/unit/test_purity_audit.py` was not edited; its module list may need `_venue_status` if the owner wants the new module audited. `CONTRACT.json` is not amended here; the additive header/unit amendment (D10) remains owed.

See the [API](../api/EF1_MULTI_VENUE_STATUS.md). No acquisition, installed, cross-layer, performance or release claim follows from this source result.
