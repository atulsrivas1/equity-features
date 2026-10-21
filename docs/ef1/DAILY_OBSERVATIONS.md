# Daily observations

The optional `ef1.daily_observations` producer uses algorithm
`daily-observations-v2`, context `ef1-daily-context2` in the single
`ef1_context` parameter, and mapping `ef1-daily-map2`. Existing EF1
producers and the default registry retain their contracts.

Supply six nullable REFERENCE batches in order: calendar_manifest,
calendar_slots, observation_coverage, raw_observations,
common_observations, basis_provenance. Missing batches and present empty
batches remain distinct. Calendar and source assertions are caller facts;
the library performs no acquisition, timezone inference or persistence.

The supported profile is `exact_integer_price_units_v1`: exact int64
OHLC coefficients with explicit scale and currency, nullable unknown
fields, and explicit nonfinite extraction markers. Admission requires
known positive coherent OHLC. Zero volume does not exclude coherent
prices. Optional reduced rational range limits are explicit caller policy.
Raw and common currencies must agree: scale and basis conversion never
authorize foreign exchange conversion.

Selectors are last N admitted observations (1 through 252), the current
civil week/month/year strictly before target, or the latest populated
prior civil week/month within the declared complete bounded history.
An optional raw lookback restricts the actual delivered population before
admission and selection. Minimum-history and latest-admitted gates apply
to that population. Missing membership never becomes an exclusion or a
replacement observation.

Selected common prices satisfy, separately for every supplied OHLC cell,
`common * 10**raw_scale * denominator = raw * 10**common_scale * numerator`.
Each complete product must have absolute value below `10**38`.
Open is the first selected common open; high and low are extrema, with
earliest date and record identity breaking ties. Conversion to float64
happens once at the output boundary. Selected observed count depends only
on raw admission, independently of common prices and factor knowledge.

Both availability modes enforce original known-at cutoffs. Exact decision
fences require calendar closure and causal membership/exclusion/absence
proof. Quality expected/observed counts describe proof slots, not selected
observation count. Unavailable outputs emit no evidence. Available outputs
carry bounded original witnesses, with at most 28 evidence rows in total.

Use `build_ef1_config`, `decode_ef1_context`, `ef1_definitions` and
`compute_ef1`; the latter accepts the six nullable roles and an explicit
EntityKey. Discovery returns high, low, open and selected_observed_count
in alphabetical order. Publication retains schema 1 and math policy v1.

The literal synthetic conformance pack in
`tests/fixtures/ef1_daily_observations.json` predates this implementation.
It covers actual large input populations as well as missingness,
causality, precision and stage-specific structural refusals. Original
binary64/inferred adjustment routes are unsupported and require separate
source qualification. This implementation alone establishes neither
source parity nor release acceptance.

The V3A1 quality clarification binds the complete historical fence when the
entire raw role is missing: coverage naming raw records does not establish
their admission. The `V318-raw_observations-none` example has three physically
observed proof slots and reports expected 3/observed 3, all four null values,
missing_input/absent_input and no evidence. Its inputs and numerical semantics
retain their original identity. This correction changes quality accounting;
it does not infer raw prices or selected members.

Pure and worker admission can refuse at different actual stages. For
`X212-duplicate-record`, the direct pure API returns duplicate. The same batch
declares observed two but physically contains three rows, so the existing
generic worker guard refuses earlier with RESULT_IDENTITY_MISMATCH. A worker
test must not claim the pure callback executed through that earlier refusal.

## Canonical inputs

Each batch has exactly instrument_id, session_id, reference_id, fact_kind,
effective_start_ns, effective_end_ns, text and known_at_ns columns. Optional
outer price/factor fields are absent. Text is canonical ASCII JSON with sorted
keys, compact separators and no newline. Duplicate keys, unknown fields,
floats/exponents, Boolean integers and nonfinite JSON are refused. All supplied
rows are checked structurally, including rows outside the eventual decision
fence. Source components and record identities are printable ASCII, at most
128 characters. Row identities come from supplied facts.

| Role | fact_kind suffix after `ef1.daily.` | Exact text keys |
| --- | --- | --- |
| calendar_manifest | calendar_manifest | version, calendar_id, revision, timezone, history_start_date, target_date, slot_count, slots_sha256, calendar_source |
| calendar_slots | calendar_slot | date |
| observation_coverage | observation_coverage | state, raw_reference_id, common_reference_id, basis_reference_id |
| raw_observations | raw_observation | date, open, high, low, close, volume, invalid_fields |
| common_observations | common_observation | date, raw_reference_id, open, high, low, close |
| basis_provenance | basis_provenance | raw_reference_id, common_reference_id, raw_source, common_source, raw_price_unit, common_price_unit, common_adjustment, factor_num, factor_den |

Manifest version is `ef1-daily-calendar-manifest1`. Its source identity and
reference ID are independently bound by configuration. The manifest text hash
is SHA256 of its canonical ASCII bytes. The slot hash uses this exact object:
version `ef1-daily-calendar-slots1`, namespace, instrument_id, calendar_id,
revision, timezone, history_start_date, target_date, calendar_source and slots.
Each ordered slots member has session_id, date, open_ns, close_ns and
known_at_ns. The complete manifest describes every governed open slot within
its inclusive civil fence. Hash consistency verifies supplied identity;
it does not establish external source truth.

Target slot bounds equal SessionSpec. Historical observations finish by both
target open and market cutoff. Historical row intervals equal their supplied
slot intervals. The manifest spans first supplied slot open through target
close. Each batch scope spans that same interval with policy
`ef1_daily_observations_v2`, both auctions false and no interval_coverage.
Calendar roles require complete physical populations. Coverage expected is
the historical slot count, while observed is actual assertions. Numeric
completeness metadata never replaces per-slot membership proof.

V3A2 separates civil syntax from actual represented instants. Date labels
must be canonical valid Gregorian ISO dates, ordered within the declared
calendar fence. Decoder acceptance establishes neither authentic calendar
membership nor representability of an actual source interval. The source
adapter supplies the factual timezone/date-to-interval mapping and original
provenance. Actual UTC instants remain signed int64, with positive, completed
and causal interval checks. The pure library infers neither UTC midnight nor
IANA timezone mappings from a label, and makes no blanket year-range source
representability claim. A decoder control for `1677-09-20` tests syntax only;
it does not qualify actual endpoint execution or source calendar truth.

Coverage states are `present`, `absent_in_snapshot` and `unknown`; the latter
two require null record references. Present raw joins are exact and one-to-one.
Missing named common/basis facts are price capability gaps. Existing extra,
contradictory or incorrectly joined rows refuse `inconsistent_identity`.
Absent snapshot proof describes that snapshot, not exchange-wide absence.

Raw invalid_fields is a sorted unique subset of close/high/low/open; marked
fields must be null. Ordinary null means unknown membership. Known invalid
geometry, nonpositive OHLC or explicit nonfinite markers establish exclusion.
Lower and upper ratios compare low to min(open,close) and high to
max(open,close), respectively; equality admits. Ratio and factor components
are positive reduced integers through 1,000,000. Volume is nullable
nonnegative int64. Basis provenance preserves complete source/unit/adjustment
objects for both sides. Raw identity requires factor 1/1 and raw basis;
split basis requires an explicit action snapshot and anchor. Total return is
unsupported.

## Decision and output rules

Standalone last N scans backward until N structurally decidable admitted rows
establish a complete suffix, or uses the whole declared bounded fence if fewer
are proved. Every intervening absence, exclusion and membership assertion is
required. Unknown and future facts never trigger exclusion or refill.
Pre-target needs civil closure from Monday/month day 1/January 1 to target.
Latest-prior needs the chosen period in full and all intervening prior-period
absence/exclusion proofs, stopping before the current period. A partial period
cannot establish complete extrema or a no-prior assertion. Earlier unknown
facts outside a complete suffix and common facts on excluded/unselected rows
remain irrelevant to numerical readiness.

For raw cap L, restrict to the latest min(L, delivered raw count) records
before admission. A full cap requires membership closure from its oldest row
through target; a short cap requires the full bounded history. Minimum/latest
gates without cap also require the full history. Proof quality uses the union
of gate and selector slots; unioning proof never adds numerical rows. Once
membership is known, no admitted population suppresses all outputs as
not_applicable/no_eligible_observations; latest excluded suppresses all as
not_applicable/ineligible; then minimum failure gives insufficient_history.

Required dependency reasons are ordered absent_input, null_field,
unknown_availability, future_knowledge, governed_gap. Any of the first four
means missing_input, otherwise governed_gap means incomplete_coverage.
Incomplete civil closure uses expected null and actual observed assertions
in the delivered decision interval. Missing actual calendar/manifest uses
expected null and observed zero. Known-at failures preserve physically
observed assertion counts. Fewer than N complete bounded observations gives
available count and insufficient_history prices. A proved empty civil
selector gives count zero and not_applicable/no_eligible_observations prices.
Unavailable outputs have null values and no evidence.

Every output has a QualityRow. InputBindings preserve all present batches,
including empty ones, sorted by role. Available price witnesses include the
manifest, decision coverage boundaries and selected raw/common/basis witness.
Available count uses manifest, coverage boundaries and first/last selected raw
rows, plus applicable cap/latest witnesses. Original row identity, effective
bounds and known-at are retained. Evidence sorts by feature_id/input_id/row_id
and deduplicates that key. These bounded witnesses are audit pointers,
not an enumeration of every selected member.

## Bounds and example

Context is at most 4096 ASCII bytes, nesting 8 and collections 64. Calendar
contains at most 1024 slots including target; each other multirow role at most
1023, manifest at most one. Text byte limits are manifest 2048, calendar slot
512, coverage 512, raw/common 768 and basis 1536. The configured selector's N
is bounded by 252 independently of delivered history. Integer-ratio products
under int64 and the ratio component limits cannot reach decimal128 overflow;
the scale/factor equality products still require explicit decimal128 checks.

The synthetic example with target October 8, coverage on October 5 through 7,
one absent slot and admitted raw/common observations October 6 and 7 produces
open 10, high 15, low 9 and count 2 for current-week pre-target. Every quality
row reports expected 3 and observed 3. The literal full packet
`V201-observed-not-scheduled` supplies all original sources, bounds and facts;
its expected outputs are independent of the implementation.

Workers pass only present actual batches into generic input-byte admission,
preserving the six nullable role declarations separately. Input payload is
bounded by 1 MiB of actual protocol-5 present-batch tuple serialization;
TaskManifest JSON has its own unchanged bound. Sink requirements are existing
protocol 1/efio-json1/efio-key1/efio-content1, canonical 0.0.4a4/schema 1/math v1,
one result, four scalar cells, 28 evidence rows and 1 MiB chunk/total bytes.
The calculation module itself performs no serialization-based resource I/O.
