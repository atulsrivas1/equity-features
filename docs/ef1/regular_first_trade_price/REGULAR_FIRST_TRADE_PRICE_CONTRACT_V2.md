# Regular first eligible trade price: proposed contract V2

Status: PROPOSED, UNFROZEN, NOT IMPLEMENTED. This synthetic public-candidate
contract expresses the independently reviewed mathematics and full literals.
Actual generic prerequisite probes, observed-stage review, public packet review
and a separate coordinator freeze/source-authoring decision remain pending.
See [status precedence](STATUS_AND_EVIDENCE_PRECEDENCE.md). This text grants no
execution, publication, source-data admission or release acceptance.

## Identity and exact roles

Producer `regular_first_trade_price`; ConfigSpec identity
`ef1.regular_first_trade_price`; algorithm `v1`, schema `1`. The scalar header is
`session.regular.first_trade_price`, algorithm `v1`, dtype `float64`, unit
`currency/share`, schema `1`. ResultMetadata backend is `python-exact`, backend
version `0.0.4a5`, schema `1`, math policy `v1`, exact evidence_limit `1`.
The existing canonical package identity is `0.0.4a4`; it is distinct from the
backend identity. Retaining these versions does not qualify new artifacts.

The proposed additive API uses the existing build_ef1_config,
decode_ef1_context, ef1_definitions and compute_ef1 shape. The current frozen API
does not implement this producer. No new DTO field or build-version property is
introduced. See [API boundary](API_BOUNDARY.json) and
[existing DTO fields](EXISTING_DTO_FIELDS.json).

There are exactly three concrete nullable positional slots:
calendar_provenance REFERENCE, trades TRADE, population_proof REFERENCE. Present
empty and absent are distinct. The adapter exposes these roles/slots and their
present-only batches in role order. Metadata bindings retain all actual present
inputs, lexically calendar_provenance, population_proof, trades. No absent
binding is fabricated. The worker declares all three roles and reconstructs
nullable slots by role and binding, never by DataKind.

Context keys are exactly version, producer, calendar, selection; version is
ef1-context1, and selection is exactly phase_profile=regular_no_auctions1 and
sampling=eligible_trade. No prior-close, BAR, history, official-close or fourth
capability role supplies this result.

## Timing and selected operand

Let A/Z be the supplied actual regular open/end, C the market cutoff and K the
knowledge cutoff, all exact signed-int64 UTCns. Require A<C<=Z. C=A and C>Z are
BOUNDS, not clipped requests. WindowSpec is count1, target session only,
governed_sessions=(target,), anchor completed_eod. The single target calendar
agrees with actual/scheduled close, civil date, timezone, early-close declaration
and regular segment. Valid premarket/postmarket calendar segments may exist;
no corresponding market rows enter this producer. Both session auction flags
are false.

Trade scope is exactly [A,C), eligibility_policy supplied_path, both auction
flags false, sampling none, quantity shares, ordering declared, duplicate reject,
and empty interval_coverage. Every delivered row satisfies A<=event_ns<C.
Event A is admitted; event C is excluded, including event Z when C=Z. Out-of-scope
or auction rows refuse rather than being silently filtered, even eligible=false.
Condition may be a whole absent column, supplied null, or literal regular.
Opening/closing_auction refuses BOUNDS; another supplied string INVALID_SCHEMA.
Absent/null condition does not establish phase: the truthful source profile,
scope and causal membership proof must establish regular non-auction membership.

Preserve original instrument/session, event_ns, order_key and event_id. Strict
canonical (event_ns,order_key) order admits same timestamps with increasing keys.
Never sort or derive ordering from event_id. A repeated original event_id is
DUPLICATE before backward-key comparison; adjacent equal pairs with distinct
IDs are DUPLICATE; backward order, including a nonadjacent repeated pair with
distinct IDs, is INVALID_ORDER. Do not change shared canonical validation.
Observed data cannot invent missing original IDs/order from row numbers.

After structural validation and population readiness, select the first row j
whose required exact nonnull eligible bool is True. Its original identity/order
selects the operand before numerical availability. The result is exactly
float(Fraction(price_j, 10**PriceUnit.scale)), checked signed-int64 coefficient,
scale0..18, with one final binary64 conversion. No FX, factor application,
quantization, intermediate rounding, history, warmup, minimum size, delay or
first-delivered/first-known fallback is introduced. BAR open, vendor session
open and official auction price are different operands and cannot substitute it.

Eligible bool alone declares source-admitted membership. The whole optional
size column may be absent without changing membership or gating this price.
If supplied on any eligible row, size and price must be nonnull and positive,
including unused later rows and when peer proofs are absent. Supplied eligible
null/zero/negative cells refuse INVALID_SCHEMA. Ineligible negative size refuses
BOUNDS; zero/null size is allowed. Ineligible prices retain canonical rules and
are not selected numerical operands. Absent columns are not supplied invalid
cells. Do not silently rewrite eligibility from size.

## Independent causal population proof

The new closed family is ef1.regular_trade.population.v1, semantic version
ef1-regular-trade-population1, profile regular-trade-membership-asof1, reference
ID rtp1:+lowercase SHA256 of compact sorted canonical ASCII payload JSON.
Gap/BAR population, observable market-prefix and source-capability facts are
not aliases. Exact canonical proof payload keys are in
[the API boundary](API_BOUNDARY.json); full bytes occur in
[the synthetic sample request](examples/SAMPLE_REQUEST.json).

One canonical REFERENCE row has exactly instrument_id/session_id/reference_id/
fact_kind/effective_start_ns/effective_end_ns/text/known_at_ns in that order.
Effective bounds equal [A,C). Metadata has price_unit None, matching adjustment,
scope None, empty interval coverage, sampling none, quantity shares, declared
order/reject duplicates, observed equal actual row count. Empty proof yields
absent_input. More than one distinct row is INVALID_SCHEMA after canonical
duplicate-reference checks. Nonnull proof unit is INVALID_UNIT; adjustment
mismatch UNSUPPORTED_ADJUSTMENT. Family checks precede legacy text-label checks;
proof text has its own4096-byte budget.

Payload binds exact producer, phase, request clocks, namespace/entity, units,
adjustment, actual trade and proof source bindings, count, completeness and
membership hash. Each binding has exactly source_id/snapshot_id/mapping_version/
input_id, four nonempty bounded opaque strings; no revision property or source
whitelist. When trades are absent, validate the proof's self/config/closed shape
but do not invent actual trade binding/count/hash comparisons. Consistent
incomplete coverage is governed_gap; contradictions are INCONSISTENT_IDENTITY.

Reuse only the ef1-gap-membership-projection1 TRADE document representation:
kind trade, membership_columns instrument_id/session_id/event_ns/order_key/
event_id/eligible/condition_present/condition. Include every original row/order
and whole-column condition-presence distinction. Hash that compact sorted ASCII
document directly. Price, size, numerical known_at and their optional-column
presence are excluded; positive numerical changes do not change membership.
Do not place the row array in bounded proof/context. Projection reuse does not
adopt gap mathematics or old-proof acceptance.

Payload JSON disallows floats/nonfinite values, duplicate/unknown keys and loose
bool/int coercion. Counts/clocks are exact signed-int64, count nonnegative;
price_unit is exact integer scale/string currency, adjustment has exactly
basis/policy_version/action_snapshot/anchor, digest lowercase64hex. Shape errors
are INVALID_SCHEMA, overflow OVERFLOW, duplicate JSON keys DUPLICATE, bounds
BOUNDS. Unsupported semantic version/profile is INCOMPATIBLE_VERSION;
contradictory producer/phase/clocks/bindings/count/completeness/hash/reference ID
is INCONSISTENT_IDENTITY. Unit/basis mismatches retain their specific codes.

The source must factually know original identity/order/eligibility/condition
membership and the bound snapshot by K, independently of numerical publication
where that separation is claimed. Hashing later cannot manufacture historical
proof existence, completeness, rights or original known-at. Consistency hashes
and opaque bindings are not authentication. A single trade known_at represents
that row's numerical fields; no price-specific clock is invented. Original
calendar and proof clocks must be nonnull and <=K in both availability modes.
An old causal proof with exact request C/K is admitted without an invented TTL.

## Structural admission before causal readiness

1. Validate config, slot count/kinds, requested identities and distinct input
   IDs. Validate every present DTO/canonical row and metadata contradiction,
   including unused rows, supplied price/size, phase, counts, units and original
   ordering, before any absence/readiness result. Validate with required_fields=()
   and do not use its all-row numerical-knowledge report as the reducer gate.
2. Validate present calendar and proof closed shape and self/request identities.
   Calendar is causal supplied_schedule ef1.calendar.provenance, c1:hash of the
   actual calendar, actual revision, ef1-reference-map1 and finite coverage of
   every supplied session/segment. Duplicate checks precede one-row shape.
3. Establish complete causal calendar, trades and independent population proof.
   Accumulate unique lexical absent_input, unknown_availability, future_knowledge
   and governed_gap. Any non-gap reason yields missing_input; gap alone yields
   incomplete_coverage. Emit no evidence while population is unready.
4. Ready complete empty/all-false membership yields null/not_applicable with
   no_eligible_observations, regardless of absent irrelevant numerical columns
   or clocks. Delivered expected/observed counts remain unchanged.
5. Otherwise select first eligible original row before availability. Whole price
   absent gives only null/missing_input/absent_input, without irrelevant clock
   reasons. Supplied invalid eligible prices already refused structurally. A
   present selected price needs original known_at<=K in both known_at and
   reconstruction modes; absent/null clock gives unknown_availability, later
   clock future_knowledge, equality K passes. Later/ineligible numerical clocks
   do not gate this independently established firstness. Never fall forward.
6. Available means one scalar and one selected original trade witness; missing,
   incomplete and not-applicable results have no evidence and no false zero.

The oracle's constructor/canonical stages retain their recorded source-inspected
provisional status until independently accepted actual evidence, except N154
whose actual failed-run BatchMetadata BOUNDS constructor observation is recorded
in oracle V3. That constructor-invalid case cannot establish a later pure
semantic guard; the empty proof interval/scope profile remains mandatory. Exact validate_batch(batch, required_fields=())
without session/availability differs from the contextual optional-argument
variant. The latter can reject geometry earlier; never credit its response to
the first call. Unsupported current decoder/dispatcher responses do not count
as future producer-specific semantic conformance.

## Complete result and worker boundary

Quality expected is trades.coverage.expected, None when trades absent; observed
is actual delivered trade rows, zero when absent. These are not eligible/proof
counts. Preserve namespace/entity/session, availability C/K/mode/evaluation,
adjustment, actual complete source bindings and canonical ConfigSpec.digest.
One header, one entity, one quality row; declared evidence_limit exactly1,
actual0or1. Available evidence uses actual trade input_id, original event_id,
event_ns and selected original known_at; effective bounds None, use consumed,
exclusion_reason None, boundary ordinary. No calendar/proof/later witness.

Worker task family is regular_first_trade_price, one instrument, target-only
governed interval A/Z, ordered_history False, warmup empty, initialization None,
merge_policy none, serialized_destination, max_input_batches3 and actual
protocol5 present-input pickle<=1MiB. Existing efworker-task1/canonical0.0.4a4/
schema1/mathv1 identities remain distinct from result backend identity.
Close exact family/config/roles/bindings/scope and final header/backend/schema/
math/evidence1/entity/cell counts before sink begin/write/commit/read. Generic
DTO/comparator admission alone is not this producer-specific worker guard.
Whole-result independent fixture parity validates arithmetic; the worker must
not duplicate producer mathematics to intercept an arbitrary numerical tamper.

Adapters convert supplied rectangular facts without filtering, repairing,
deriving firstness/price or inventing proof/availability. Workers orchestrate;
calculations have no fetching, file/DB access, credentials or publication.
Initial integration uses explicitly synthetic inputs and a new separate output
DuckDB through the existing sink. Direct/worker/SDK/stored/reopened whole-result
parity, identical retry and true before-any-sink refusal evidence remain future
requirements. HTML generation is distinct from actual browser inspection.

## Bounds and unfinished acceptance

Context/proof text independently<=4096 canonical ASCII bytes; depth<=8, each
collection<=64; labels<=128 codepoints/512 UTF8 bytes, no controls. These do not
cap trade table rows: the independent65-trade case is required. Protocol5 input
pickle, TaskJSON and SDK/sink budgets are distinct and must be measured; no guard
is widened. Target probe transport limits are separately1,048,576 bytes. Actual
compatible build/install/platform evidence remains required before merge/release.

The [full oracle](REGULAR_FIRST_TRADE_PRICE_ORACLE.json) contains122 complete
results,159 isolated input refusals and17 separate DTO/worker/integration
controls, all synthetic and preexecution. Literal/reconstruction review is not
actual source admission or implementation. Original-source rights, causal
capability, factual known-at, exact original numerical/consumer parity, full
EQ164, remaining EF1 outputs, integration/browser/release/publication gates stay
open. This slice grants no package/tag publication or work in another release.
