# Session accumulators — experimental0.0.2a6

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

All23 R1 IDs advertise batch/update. Restore/export and merge remain unsupported
until their separate stories qualify them. R2/custom execution remains unsupported.
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
units/adjustments/sampling, enrichments and math/backend identity. Schema1 requires
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
All23 R1 IDs qualify restore. Merge remains unsupported. No file, pickle, executable
reconstruction, implicit registry state or asynchronous thread ownership is added.
See [synthetic restore example](../../examples/session_state.py).
