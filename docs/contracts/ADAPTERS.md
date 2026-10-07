# Adapter contracts and synthetic development kit (EQ-016)

## R4.1 ownership clarification

Existing pure input protocol/SDK contracts remain compatible in `equity-feature-contracts`. New storage publication and explicit factory interfaces are planned in companion I/O packages; concrete adapters/sinks stay outside calculations. [Architecture](../IO_WORKER_ARCHITECTURE.md) specifies responsibilities and consumer extension paths. Do not interpret a historical absence-of-DuckDB statement below as current R4 delivery status. No contract/runtime change occurs in this planning story.


Experimental0.0.1a6 exports a dependency-light `equity_feature_contracts.adapters`
module. Protocols declare `HistoricalAdapter.capabilities/iter_batches` and optional
`LiveAdapter.capabilities/stream_batches` (async iterator). Declarations perform no
acquisition, job, clock, file, credential or network access. Numerical packages never
import concrete adapters. The synthetic implementation lives only in `examples`.

`AdapterCapabilities` explicitly declares canonical kinds/schema1, namespace, exact
UTCns-int64, scaled price units, adjustment bases, quote sampling, historical/live
modes and maximum chunk size. It is source-declared metadata, not evidence of
entitlements, provider coverage, financial truth or actual historical availability.
`AcquisitionRequest` supplies unique instrument/session IDs, source snapshot,
namespace, exact units/basis/sampling, C/K/E policy, start/end and positive int64
max_batch_rows/max_rows/max_batches. Requests contain no credentials.

Acquisition selection is explicit: trades/quotes use `[start,end)`; bars/daily must
be wholly inside the range with end<=end; references select effective-start in
`[start,end)`. These are acquisition boundaries, independent of market/knowledge
eligibility. Requests do not silently filter unknown or future known_at timestamps.
Closing-auction inclusive acquisition and pre-open quote seeds need a future
separately qualified adapter/request extension; no such support is claimed here.

`AdapterBatch` binds request ID, ordinal, final marker, canonical batch and source
snapshot/mapping/input identity. `source_coverage` matches original canonical
metadata; `delivery_coverage` describes only the delivered chunk. Coverage scope
never expands automatically. Observed-empty has a real zero-row canonical batch;
missing/unavailable have no batch, a reason, unknown/incomplete zero delivery count
and one terminal envelope. Authentication, entitlement, rate limit, transport,
schema, unavailable, cancellation, unsupported capability and resource limits have
separate stable `SourceErrorCode` values. Messages must exclude credentials.

`validate_delivery` accepts a concrete finite tuple/list, checks declared limits,
request/ordinal/final identity, schema/units/snapshot/entity/time/order, source/mapping
consistency and duplicates/order across chunks. It may concatenate up to max_rows
for semantic validation; it is a bounded conformance helper, not a streaming engine.
It never consumes lazy iterators. Consumers own bounded collection/cancellation and
retries. Passing conformance does not make declared source coverage true or establish
historical source admission. Source services require independent qualification.

Run `python examples/in_memory_adapter.py` after installing both distributions.
`InMemoryTradeAdapter` owns a frozen synthetic canonical fixture, explicitly certifies
only its finite range and supports ordinary raw trades/historical acquisition.
It filters requested IDs and half-open times, creates owned deterministic chunk IDs,
preserves original source coverage and every known_at/null, and reports selected
chunk coverage separately. Empty selected slices are observed-empty; absent fixture
is missing. It rejects live requests, auctions, unsupported units/basis/snapshot/
range and resource limits before yielding any misleading partial complete slice.
Cancellation is checked before and between chunks; already yielded chunks cannot
be retracted. Async live is a Protocol only. There is no DuckDB/provider/file adapter,
provider mapping discovery, calendar lookup, retry/cache/worker or calculator.

Mapping guidance: normalize source data explicitly before constructing canonical
columns; preserve source snapshot/mapping and stable input/row identities, UTCns,
quantization policy, masks, sample type, action basis, ordering and original known_at.
Use validation/normalization reports rather than silently sorting/repairing gaps.
Conformance fixtures are synthetic and require no credentials or paid data.


EQ043 adds the [public reusable development kit](ADAPTER_KIT.md), named supplied-delivery/error cases and a separately packaged synthetic BAR adapter/custom consumer. Existing protocol/schema1 meanings remain unchanged; pure helpers never acquire or iterate sources. Actual story review/artifact acceptance is tracked on issue49.
