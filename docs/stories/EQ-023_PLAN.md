# EQ-023 — bounded session accumulator lifecycle plan

Prepared before code, issue27/epic20/R1. Confirm13points (revise provisional8:
qualifying all23 IDs across six families, transactional updates and explicit prefix
certificates is more work; feature scope unchanged). Pull only after EQ022 Done.
Preserve EQ095/PR120; one active story; author self-review+CI.

## Public interface and supplied proof

`SessionAccumulator(family, config, *, entity, population: StreamPopulation,
prior_close: CanonicalBatch | None = None, seed: CanonicalBatch | None = None)`
with family bars/structure/trades/top_k/quotes/continuous. Constructor validates
family/config requirements and fixed canonical source schema/identity; prior is
only bars, seed only continuous. No calculator registration/composition/R2 API.
`update(batch: CanonicalBatch, *, start_ordinal: int) -> None` accepts supplied
owned chunks only. `snapshot(certificate: PrefixCoverage) -> FeatureResult` and
`finalize(certificate: PrefixCoverage) -> FeatureResult` publish explicit cutoffs;
finalize requires configured finalC and seals once (repeat finalize/update reject).

New owned immutable StreamPopulation(kind,fields,metadata,identity_policy) binds
constant source snapshot/mapping/input_id/schema/unit/basis/sampling/scope/policy.
fields are exact ordered column names and fixed across chunks; schema changes
require replay. identity_policy literal caller-certified-global-unique-v1 records
caller responsibility for global normalized event IDs. The calculator proves
ordinal contiguity/nonreuse and strict cross-chunk event or completed-bar order,
and detects chunk/known retained duplicates. It cannot prove nonretained opaque IDs
never repeat without unbounded history; no such proof is claimed. No unbounded
seen-ID set or growing per-chunk InputBindings. Population declaration is trusted
source governance, not cryptographic/source-truth proof. Chunk coverage must match
actual raw rows; do not infer prefix completeness from whole-target counts.

PrefixCoverage(cutoff_ns,coverage,interval_coverage=()) explicitly attests requested
prefix delivered/expected/complete counts. C must be within(open,configured finalC]
and coverage.observed must equal actual consumed count. Interval certificates bind
configured windows and actual selected counts, independently of denominator/source
coverage; future windows remain unready. Result config/availability/input scope and
coverage describe requested prefix, with stable one target binding plus optional
fixed prior/seed binding. Do not accumulate chunk provenance tokens.

## Bounded reductions and lifecycle

Extract/reuse pure admission/numerical/format helpers from accepted kernels, without
invented synthetic market rows or parallel untyped result APIs. Bar states retain
observed/positive counts, OHLC extrema/endpoints, exact volume/notional/proxy totals
and bounded field/knowledge readiness; structure retains one such state per fixed
configured window. Trade states retain eligible count/Q/A and payload readiness.
TopK retains at mostK rows. Sampled quotes retain exact counts/coefficient sum,
compensated bps pair and at most configured firstN observations. Continuous reuses
accepted six durations/numerator/compensated pair/cursor/current quote/original
expiry plus optional fixed seed. No raw-input history or unbounded Fraction sums.
Retained bytes depend on supplied ID/config sizes; row retention is bounded by
configuration, not an arbitrary constant-byte promise. Batch admission still
costs proportional to each supplied chunk.

Validate full chunk identity/schema/ordinal/order before bounded candidate-state
updates; commit state only after successful validation/reduction. Snapshot/finalize
also validate certificate and construct result before advancing/sealing, preserving
state on error. Positive numeric sums use checked bounded representations; an
overflow marker may preserve unavailable-prefix behavior, while any ready dependent
publication raises OVERFLOW before wrap. Raw observed-count overflow always rejects.

Snapshots cannot precede consumed market facts or prior integration watermark.
Ordinary trade/quote event must be<C; completed bars end<=C and configured closing
trade auction can equal finalC. After snapshot advancement, late events/closed bars
cannot alter that prefix; corrections require explicit replay/new accumulator.
Equal-time events across chunks require increasing order key. Seed ID remains one
fixed duplicate check; original seed expiry never restarts. Repeated unchanged
snapshot at legal C is deterministic; later update prevents earlier snapshots.
Inputs/returned results are owned immutable; no caller mutation of future results.

## Independent verification/delivery

Test every family full batch versus chunked outputs/quality/evidence at explicit
prefix and finalC, missing fields/empty/zero/incomplete/knowledge/interval coverage,
prior-close/seed, equal-time and auction boundaries. Wrong ordinal/source/schema/
config/entity, duplicate/order across boundaries, earlier snapshot/late correction,
future snapshot, certificate count mismatch, repeated finalize and post-final
update reject without partial state mutation. Golden count/Q/A, weighted quote
integral and topK fixtures remain independent, including numeric overflow behavior.
Increasing input/chunk counts show fixed counters and retained K/N/configured-window
state bounds; no throughput claim. Public export/restore/merge remain unsupported
until EQ024/025. Advertise update only for all qualified R1 IDs and existing batch
flags; custom/R2 remain false. Version0.0.2a6 both packages; ninth installed example,
API/contract/capability matrix/registry/release/continuity/EQ022 receipt. Full exact-
head/main/actual bundle/four fresh install gates before Done; then EQ024.

Before implementation: finalC certificate expected count must match any fixed expected cardinality declared by the population. Prefix expected counts remain explicit. A sealed accumulator permits only an identical final certificate for repeat snapshots; repeated finalize rejects.

Lifecycle detail before implementation: incomplete chunk delivery or a prefix certificate declaring expected>observed records a permanent known-gap flag; later complete prefix claims reject until explicit replay. Unproved expected=None prefixes can later be certified complete with unchanged facts. This prevents carrying over known missing past delivery.
