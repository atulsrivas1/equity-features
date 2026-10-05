# Session accumulators — experimental0.0.2a11

`equity_features.incremental.SessionAccumulator(family, config, *, entity,
population, prior_close=None, seed=None)` receives owned data/configuration only.
Family is bars, structure, trades, top_k, quotes or continuous. Config/admission
and results match the corresponding accepted batch API. Prior close is bars only;
seed is continuous only. No acquisition, output persistence or automatic threading.
Caller serializes access; the mutable accumulator has no concurrent-call guarantee.

| Family | R1 IDs | State | Update support |
| --- | --- | --- | --- |
| bars | 12 bar/price | counts/OHLC/checked totals/field readiness; fixed prior if supplied | yes |
| structure | 2 interval | one bar summary per configured window and target denominator | yes |
| trades | 5 aggregates | eligible/raw counts, exact Q/A, payload readiness | yes |
| top_k | largest trades | deterministic bounded K original rows | yes |
| quotes | 2 event summaries | counts/exact spread/compensated bps/first bounded N observations | yes |
| continuous | time-weighted spread | six durations/numerator/compensated pair/cursor/current quote/original expiry; optional seed | yes |

All23 R1 IDs advertise batch/update/restore. Twenty-two noncontinuous IDs advertise
conditional merge under the rules below; continuous merge remains false.
R2/custom execution remains unsupported.
No batch quantiles were added; bounded optional observations are supported in updates.

`StreamPopulation(kind, fields, metadata, identity_policy)` owns fixed ordered
canonical field names and source snapshot/mapping/input_id/schema/unit/basis/
sampling/scope/policy. `from_batch` checks a fully covered actual canonical population
and its semantic order/duplicates, then retains only its declaration. For a supplied
stream declaration, caller explicitly certifies global normalized identity with
`caller-certified-global-unique-v1`. This is caller governance, not cryptographic
or independent source-truth proof. Field/schema changes require replay. Original
full-target coverage cannot certify a smaller prefix. Known final expected count
is a fixed cardinality constraint; final certificate must match it.

`update(batch, *, start_ordinal)` requires the next contiguous ordinal (initial0)
and exact source/schema identity. Actual chunk observed coverage must equal its
row count. Chunk-local declared interval counts, if supplied, must match that
chunk; strip/re-certify full-population interval counts when splitting. Strict
cross-chunk event order and bar nonoverlap reject reused order/ranges. Known last,
retained and seed IDs reject duplicates. A bounded summary cannot prove all past
nonretained opaque IDs unique; caller certification remains necessary. No growing
seen-ID set or per-chunk InputBindings is retained.

`PrefixCoverage(cutoff_ns, coverage, interval_coverage=())` is an immutable explicit
requested-prefix certificate. `snapshot(certificate)` requires C in(open,finalC],
actual consumed observed count, compatible interval declarations/counts and no
consumed facts beyond C. Ordinary events must be<C; completed bars may end=C;
configured closing trade auction may equal finalC. Metadata/config digest describe
this exact prefix, with stable source plus optional fixed prior/seed binding.
Intervals need their own certificates; future windows remain unready. Counts do
not establish delivery truth or complete duration. Unproved coverage yields honest
unavailable output, never automatic completeness from full-target counts.

Snapshot cannot move backward after ingestion or cutoff advancement. Future updates
cannot alter returned immutable results. Late events/closed bars require explicit
replay/new accumulator. A forming bar ending after an earlier snapshot may later
be supplied when completed, provided its actual interval remains nonoverlapping.
Equal-time events across chunks require increasing order keys; earlier tied quote
states have zero duration. Continuous prefix snapshots preserve original expiry.

Incomplete chunk delivery or a certificate with expected>observed records known
missing past delivery. Later complete claims reject until replay. Unknown expected
counts without a known missing fact may later be certified with unchanged facts.
This prevents carrying over known outages. Independent interval certificates can
still establish a window while whole-target denominator coverage is unavailable.

`finalize(certificate)` requires configured finalC and seals once, even if output
is honestly unavailable. Repeated finalize and further update reject. Only an
identical sealed certificate may be used for repeated snapshot; corrections need
replay. Update/snapshot/finalize validate a bounded candidate and construct output
before committing state, so errors leave prior state intact.

Shared batch/update reducers preserve exact arithmetic and readiness. Positive sums
keep checked values or a bounded overflow marker. A ready dependent publication
raises OVERFLOW; unavailable prefixes can remain unavailable without wrapping or
storing growing wide totals. Raw count overflow always rejects. Float ratios and
compensated bps/time sums use rtol/atol1e-12; integers compare exactly. Splitting a
continuous interval at a snapshot can change floating addition order within those
limits. No unbounded Fraction denominator or averages-of-averages reduction.

Retained state scales with configured K/N/window count and supplied fixed ID/config
sizes, not ingested row/chunk history. Atomic copies temporarily hold two bounded
states; immutable results are caller-owned. Canonical chunk admission and optional
Arrow copies scale with supplied chunks. No measured throughput claim. The Source
boundary guard remains development policy, not a runtime sandbox. [Example](../../examples/session_incremental.py).

## EQ024 state export and restore

`state = accumulator.export_state()` returns immutable `AccumulatorState` text.
`SessionAccumulator.restore_state(state, family, config, *, entity, population,
prior_close=None, seed=None)` returns a fresh independent calculator. Supply the
same original declarations and one-row enrichments; no source rows are fetched.
The fingerprint covers config/algorithm/schema, entity, complete source/population,
units/adjustments/sampling, enrichments and math/backend identity. Schema2 requires
an exact implementation version; no migration between experimental versions.

Canonical JSON stores arbitrary-width exact integers within their checked field
bounds and hex strings for every finite binary64 sum/compensation/observation.
State contains sufficient statistics and overflow/readiness flags, fixed windows,
first/last order and bar boundaries, ordinal/watermark/gap/seal, K/N retained rows,
and temporal durations/cursor/original anchor/current quote. It contains no raw
history or growing ID set. A16MiB UTF8 envelope cap bounds parsing; export can reject
oversized retained identity text. Duplicate keys, unknown fields, truncated JSON,
noncanonical text, nonfinite floats, incorrect types/counts/rank/source identities,
inconsistent durations/cursors, incompatible declarations and version changes
reject before returning a calculator. Digests catch accidental corruption; they
are not signatures and cannot authenticate rehashed fabricated historical totals.
Caller-owned trusted state remains necessary. Checked structural relations do not
reconstruct discarded source facts.

Empty, partial, missing/noncausal, overflow-unready, prefix-published and finalized
states roundtrip. Restored instances own separate mutable private reducers; exported
text stays unchanged. Watermarks, permanent gaps and single finalization survive.
All23 R1 IDs qualify restore. Conditional merge is described below. No file, pickle, executable
reconstruction, implicit registry state or asynchronous thread ownership is added.
See [synthetic restore example](../../examples/session_state.py).

## EQ025 legal partition merge

`a.merge_partitions(b, *, left: PartitionSpan, right: PartitionSpan)` returns a
fresh independent accumulator. Caller supplies nonempty global ordinal ranges
[start,end); each length must equal that accumulator's actual consumed count.
Ranges must be adjacent/disjoint and lie inside known final expected population.
Arguments may arrive in either order; ranges determine global chronological order.
Both accumulators must have identical original family/config/entity/population,
source/schema/unit/basis/math/backend/enrichment bindings. They must be unsealed
and unpublished (watermarks at open). Bar partitions must not overlap; event
first/last keys must be strictly ordered across the boundary. Known retained/last
IDs cannot overlap. Missing chunk delivery propagates permanently.

Ranges and global nonretained opaque-ID uniqueness are caller-certified. Bounded
reducers cannot authenticate discarded history or a forged span. Order/count/
retained checks give concrete rejection of known contradictions, not an independent
source-truth proof. Empty partitions, nonadjacent ranges, overlaps, corrections,
post-snapshot/finalized inputs and continuous carry integration require replay.

Bar/window totals and trade totals combine checked integer sufficient statistics;
OHLC preserves first/last positive-volume endpoints and global extrema. TopK
merges ranked union retaining K; quote observations retain firstN in global order.
Temporary unions use at most2K/2N rows; final retention remains K/N. Quote bps
combines compensated sums and residuals; exact integer/count/quality/evidence
semantics match batch. Finite Float64 parity uses rel/abs1e-12 for differing
reduction groupings, supported by1,000-row skewed/equal-time uneven partitions;
no throughput guarantee or broad randomized qualification is implied. Return
state can update the remaining contiguous prefix or export/restore. Originals
remain unchanged on success or rejection. All22 noncontinuous R1 IDs qualify;
continuous batch/update/restored replay qualifies, arbitrary merge does not.
See [synthetic merge example](../../examples/session_merge.py).

## BUG003 closed-window omission governance (0.0.2a10)

A structure accumulator retains one Boolean omission flag per configured window.
A closed interval certificate with expected>observed, or an incomplete chunk-local
interval declaration, permanently records missing delivery for that window and
the whole target. Later complete affected-window or whole-target claims raise
INCONSISTENT_IDENTITY before changing state; lowering or omitting an incomplete
certificate cannot clear the flag. An unchanged fixed population interval expected
count is also required when one was originally supplied. Unknown expected without
a concrete known omission may later be certified complete. Source assertions remain
caller-owned; no discarded source history is authenticated.

Unaffected independently covered interval OHLCV remains available under incomplete
whole coverage. Shares need a complete whole denominator and stay unavailable.
Corrections require a new accumulator and replay of complete supplied facts.
Unpublished legal partition merge ORs each flag; restore preserves flags. Candidate
validation makes contradictory snapshot/finalize rejection atomic. Additional state
is O(configured windows), independent of row/chunk history.

State schema2 adds window_gaps and rejects schema1; exact implementation version
is still mandatory. No implicit migration can invent historical omitted-window
facts. Replay old experimental states with their original supplied input instead.
Formula IDs and equations stay unchanged; both distribution versions are0.0.2a10.

## BUG004 typed saved-state float rejection (0.0.2a11)

A rehashed state containing an out-of-range binary64 hexadecimal exponent rejects
with ContractError(INVALID_SCHEMA), retaining OverflowError as the cause. Nonfinite
and malformed hex also reject through the typed schema contract. No calculator is
returned and existing caller state stays unchanged. Finite canonical hex roundtrips
and corruption/config/source/version admission remain governed as above. State
schema2/equations are unchanged; exact implementation version remains mandatory,
so0.0.2a10 states require replay rather than an implicit migration to0.0.2a11.
