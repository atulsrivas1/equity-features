# R26 additive boundaries and qualification proposal

Status: GOV038 source-only proposal; not frozen, implemented or admitted. Read [preparation and pending owner choice](PREPARATION.md). Existing seven delivery stories and full EQ190/EQ193 scope remain; accepted equity producers are not manufactured by this design.

## Candidate packages and compatibility

Keep the three option repositories and existing four distributions. Propose a `0.2.0a1` qualification cohort, independently versioned with exact intra-cohort pins: option-feature-contracts, option-features, option-feature-io and option-feature-workers. Matching numbers identify this proposed cohort, not a requirement that all future libraries share versions. No version, wheel or new capability is published by planning.

Add explicit flow modules alongside R25 APIs. Existing R25 canonical record/wire/hash domains, saved result bytes and APIs remain unchanged and get regression checks. The old `0.1.0a1` installed verifier admits only its original cohort; do not loosen its version/inventory checks. A separate closed flow cohort/schema and build/qualification manifest is required. A new package version does not imply a new wire version or acceptance of mixed cohorts. Optional domain extraction can be decided later without creating a new repository.

## Boundary work to freeze under EQ188

- Immutable option execution events need exact price, contracts, multiplier/currency/action identity, event/known-at instants, source partition and unique order, revision/action and correction target, plus observed-side or quote-alignment evidence with a named inference method. R25 Trade has no price/correction/order contract and cannot represent this by relabelling quantity.
- Request identities bind declared window, knowledge cutoff, source/completeness population, group and baseline identities, selected outputs, formulas and inference policies. Causal quote admission requires both clocks, eligible unique ordering, quote validity and a declared maximum age. Unknown order/sign remains explicit; no lexical ID sort is market chronology.
- Exact premium accumulation uses a frozen decimal/scaled-integer policy with explicit quantity/price precision, bounded magnitude and overflow admission. Results retain exact value representation, units, numerator/denominator evidence, status/reason/coverage and contributing identities. Do not force exact premiums into R25's binary-float-only result type.
- Separate trade new/cancel/replace actions from execution cancellation. Revisions are immutable and as-of visible only when known. A correction can affect later signs/clusters, so subtraction of one aggregate is insufficient. Reject malformed target chains, conflicting duplicates and unsupported history horizons according to a reviewed policy.
- Batch, chronological replay and checkpoint restore require distinct actual contracts. Replaying independent R25 snapshots does not prove carried state. Freeze retained prefix/state/hash and correction-invalidation semantics before claiming restart support. Unsupported incremental/live modes fail admission explicitly and remain visible in release coverage; mode reduction is not silently accepted by this outline.

Final record fields, closed enums, wire/hash domains, causal ordering, numeric limits, DDL and literal independent conformance cases still need exact reviewed contracts before implementation. This outline is not that freeze.

## I/O and execution

Adapters perform source normalization and evidence acquisition; kernels remain free of file/database/network/clock access. Start with original synthetic canonical inputs unless source paths/schema/rights are independently admitted. Do not claim a supplied equity summary demonstrates EQ153/EQ158 producer integration.

Use a new separate flow-output DuckDB schema and sink. R25's strict database rejects extra tables and migrations; do not modify a released R25 database in place. Atomically commit complete generation/results/bindings and supported checkpoint state. Same run key with identical complete content is idempotent; changed content conflicts. Verify full typed canonical stored readback/count/order/digest, including recovery after commit-before-ack failure.

Begin with one bounded request owner, one worker/inflight/I/O slot and one native/DuckDB thread. Cache keys include revision/content, clocks, policy, units and population; no unbounded global cache or reuse from a future cutoff. Shared preparation is reused only for identical admitted facts. R25 measurements do not establish R26 resource capacity. Runtime qualification requires an actual nonconflicting grant; no full-machine benchmark is admitted by this plan.

## Evidence before release

Freeze exact supported Windows/Linux sources, original wheels/sdists, sdist rebuilds, native provenance/notices and external coordinator artifact trust. Execute clean installed original/rebuilt suites, dependency isolation and actual tamper rejection, R25 API/byte regression and independent R26 expected fixtures. Complete direct -> codec -> installed worker -> separate sink full result/evidence parity, corrections, causal ties, retries/conflicts, cancellation and supported replay/restore modes.

Define bounded representative synthetic balanced/skewed workloads and capture actual elapsed time, process memory, copies/I/O and result parity. Candidate scales are 1k/10k/100k events, subject to reviewed limits and actual resource admission; they are not executed measurements or performance promises. Inspect a browser demo rendering actual stored flow/activity/cluster outputs and qualified cross-asset results. EQ193 full acceptance retains real equity producer compatibility, numerical/resource/artifact gates and owner publication boundaries.

Local builds/tests and independent exact-head review govern merge. Hosted CI is optional under the existing owner policy. No new service, product UI, provider cost, private-data operation or publication is selected here.
