# EQ-016 execution plan

Story #19 E03/R0; confirm8points at pull after EQ-015 actual artifact acceptance.
Define dependency-light typed capability/request/batch/error and historical/optional
async-live Protocols. Acquisition bounds are distinct from calculation C/K/E:
return raw known_at, including unknown/future, without silently causal filtering.
Canonical kinds/schema1/namespace/scaled price/adjustment/sampling/UTCns precision,
source snapshot/mapping/input identities, explicit bounded row/batch limits and
missing/unavailable/observed-empty dispositions are required. No calendar lookup.

Requests use event half-open, completed-interval or effective-start half-open
selection explicitly. The synthetic example supports only ordinary trade event
half-open historical slices and rejects auctions/other/live capability. All fixture
source coverage and its finite certified range are explicit, not provider truth.
Protocol methods do not access sources; example implementation stays in examples,
outside both distributions. Cancellation is cooperative at batch boundaries.
Typed source errors distinguish unsupported/authentication/entitlement/rate/transport/
schema/unavailable/cancelled/resource-limit failure; no credential handling added.

Pure helpers validate delivered canonical schema/units/identities/request bounds,
source coverage versus chunk coverage, bounded finite envelopes/ordinals/final marker,
and cross-batch order/duplicates. A concrete bounded sequence helper may concatenate
up to max_rows for conformance, never consumes arbitrary/lazy iterables or performs I/O.
It does not certify provider coverage, entitlement or actual historical knowledge.

Tests independently assert ns precision and half-open edges, units/sampling/basis,
request identity/snapshot/kind/namespace, malformed finite limits/envelopes,
missing/unavailable/observed-empty, original source coverage and known-at retention,
chunk order/duplicates/final markers, cancellation and resource errors, ownership,
repeat determinism and Protocol static conformance. Keep145unit/123math cases,
registry parity/strict typing/import/boundary and actual clean-installed example.
Version both experimental distributions alpha6. Review draft, all six exact-head
checks, repeat builds and main checks/publication bytes; download/hash/inspect both
actual main artifacts and four installs before Released/Done. E03 stays open for
EQ-093/R3. Final R0 acceptance follows, with no EQ-017 implementation.
