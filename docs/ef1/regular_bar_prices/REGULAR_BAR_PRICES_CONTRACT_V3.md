# Regular completed-bar price contract

Version: V3 public preparation candidate. Numerical owner: EQ166 #506; representation: EQ212 #570; execution: EQ213 #571.

This document restates the independently reviewed V3 proposal as a complete shared-contract candidate. It is not frozen, implementation-authorized or released. Actual generic transport probes and a fresh independent publication review are still required. All examples and literal packets are synthetic. The existing producers, schemas and evidence remain unchanged.

## Producer and exact version identities

The proposed producer is `regular_bar_prices`, with config identity `ef1.regular_bar_prices`. It adds two prices for an explicitly supplied regular completed-BAR population:

| Lexical output order | Feature ID | Type | Literal unit |
| --- | --- | --- | --- |
| 1 | `session.close.calculated_price` | `FLOAT64` | `currency/share` |
| 2 | `session.regular.first_completed_bar_open` | `FLOAT64` | `currency/share` |

Both headers use algorithm version `v1` and schema version `1`. ConfigSpec has `algorithm_version="v1"` and `schema_version="1"`. ResultMetadata has `backend_id="python-exact"`, `backend_version="0.0.4a5"`, `schema_version="1"`, `math_policy_version="v1"` and `evidence_limit=2`. These are exact values, not compatible-version wildcards.

ConfigSpec has no package/build version field. Its actual fields are `identity`, `algorithm_version`, `parameters`, `session`, `window`, `availability`, `adjustment`, `price_unit` and `schema_version`. A package/backend version belongs in the existing result metadata and artifact identities; no new ConfigSpec constructor argument is introduced. Any future version change needs an explicit reviewed amendment consistent with the independent literals. A version string alone is not source or artifact qualification.

The existing `build_ef1_config`, `decode_ef1_context`, `ef1_definitions` and `compute_ef1` APIs are the proposed additive library entry points. This packet does not claim that the current decoder, dispatcher or worker supports this producer.

## Context and fixed input roles

The context has exactly four top-level keys: `version`, `producer`, `calendar`, `selection`. They identify version `ef1-context1`, this producer, the existing supplied calendar object, and exactly:

```json
{"phase_profile":"regular_no_auctions1","sampling":"completed_bar_close"}
```

The only parameter is `ef1_context_json`: sorted, compact, canonical ASCII JSON of at most 4,096 bytes. Existing context limits stay unchanged: depth 8, at most 64 elements in each collection, and labels of at most 128 code points / 512 UTF-8 bytes with no controls. This does not create a 64-BAR row limit.

Pure input is a concrete tuple or list of exactly three `CanonicalBatch | None` slots:

| Position | Role | Required kind when present |
| --- | --- | --- |
| 0 | `calendar_provenance` | `REFERENCE` |
| 1 | `bars` | `BAR` |
| 2 | `population_proof` | `REFERENCE` |

A present empty batch differs from absence. Reference roles are never guessed from DataKind. Validate their fact families before the legacy calendar text-label admission. All present original identities are retained, and duplicate input IDs refuse with `DUPLICATE`. The adapter exposes exactly these `.roles` and `.slots`; `.batches` contains only present slots in role order. The worker declares all three roles and reconstructs the three pure slots from those declarations and their original bindings. There is no prior-close, history, notional or supplied official-close role.

CanonicalBatch has exactly the constructor fields `kind`, `columns`, `metadata`. The literal transport's `schema_version` is checked separately; it is not a fourth constructor argument. `Column` has `name` and `values`. `IntervalCoverage.coverage`, when present, is a typed Coverage object, not a raw dictionary.

## Calendar, clocks and ordinary regular phase

Let A and Z be the supplied regular session open and end, C the market cutoff, and K the knowledge cutoff. All are signed-int64 UTC nanoseconds. Require A < C <= Z, including C = Z. WindowSpec is exactly `count=1`, the target session, `governed_sessions=(target,)`, and `anchor="completed_eod"`. The supplied calendar contains exactly that target session and agrees with its supplied civil date, timezone and A/Z. Existing regular-segment, actual/scheduled close, early-close and supplied pre/post-segment rules remain.

The calendar object uses exactly `calendar_id`, `target_date`, `timezone`, `revision`, `sessions`, `segments`, `scheduled_close_ns`, `early_close`. Session entries retain `[session_id, civil_date, open_ns, close_ns]`; segment entries retain `[name, start_ns, end_ns]`, including the regular segment. Existing calendar/config consistency and canonical type/order/coverage rules apply; the complete synthetic requests instantiate those actual fields.

Calendar provenance is one original causal REFERENCE fact of kind `ef1.calendar.provenance`. Its reference ID is `c1:` plus SHA256 of the canonical calendar; source snapshot identifies the actual calendar revision; mapping version is `ef1-reference-map1`; text is `supplied_schedule`. Its effective interval covers every supplied segment/session. Original known-at is nonnull and <= K in both availability modes. Reconstructed mode does not waive this requirement. A present malformed calendar refuses even when another role is absent.

Both SessionSpec auction flags are false. This profile means caller-supplied ordinary regular BARs with no auction ticks. The library cannot inspect a BAR's constituent ticks: truthful phase/auction provenance is an adapter/source-admission premise bound by the profile, metadata and proof. Relabelling an auction-inclusive source cannot satisfy that premise. Other phase variants require separately reviewed contracts.

BAR metadata scope is exactly [A,C), with eligibility policy `supplied_path` and both auction flags false. Sampling is `none`, quantity unit `shares`, ordering `declared`, duplicate policy `reject`, and interval coverage empty. Every row satisfies A <= start < end <= C. Equality at A or C is admitted. Straddling, future and out-of-phase rows refuse with `BOUNDS`; never clip, filter, drop or reorder them. Canonical duplicate intervals refuse with `DUPLICATE`; overlapping or backward intervals refuse with `INVALID_ORDER`. Namespace, instrument/session, unit and basis must agree with the config, and observed coverage equals actual delivered rows.

Gaps between supplied bars do not imply fabricated missing rows. Completeness means complete under the declared source profile, not continuous trading at every instant. The calculated close is the last positive-volume completed regular BAR close available in this population at C. It is a provisional prefix endpoint when C < Z. Even C = Z does not prove an authoritative exchange close, auction settlement or official price, nor require a BAR ending exactly at Z. No third finality field is added; the session/cutoff/profile provenance supplies the distinction. EQ168 supplied authoritative close remains separate.

## Independent membership proof

Use the new fact family `ef1.regular_bar.population.v1`, semantic version `ef1-regular-bar-population1`, and profile ID `regular-bar-membership-asof1`. Reference ID is `rbp1:` plus lowercase SHA256 of the exact canonical ASCII payload text.

SourceBinding has only `source_id`, `snapshot_id`, `mapping_version`, `input_id`. There is no revision property or synthetic/provider/mapping-version whitelist. Every actual binding field must agree with the payload. A matching alternate opaque source identity is valid internally; names and digests do not authenticate source truth, historical existence, rights or availability.

The proof is exactly one canonical REFERENCE row for the requested instrument/session, with these columns in this order:

`instrument_id`, `session_id`, `reference_id`, `fact_kind`, `effective_start_ns`, `effective_end_ns`, `text`, `known_at_ns`.

Effective bounds equal [A,C). Proof metadata has price_unit None, the config adjustment, no scope or interval coverage, sampling `none`, quantity `shares`, ordering `declared`, duplicate policy `reject`, and observed coverage equal to actual count. A valid empty proof is missing_input/absent_input. More than one distinct row is INVALID_SCHEMA after canonical validation; duplicate reference IDs refuse first with DUPLICATE. An invalid PriceUnit may refuse at construction; an otherwise valid nonnull proof price unit is INVALID_UNIT. Basis mismatch is UNSUPPORTED_ADJUSTMENT.

Payload keys are closed and exact:

`version`, `profile_id`, `producer`, `phase_profile`, `namespace`, `instrument_id`, `session_id`, `start_ns`, `end_ns`, `market_cutoff_ns`, `knowledge_cutoff_ns`, `sampling`, `eligibility_policy`, `include_opening_auction`, `include_closing_auction`, `path_source`, `proof_source`, `row_count`, `complete`, `price_unit`, `adjustment`, `population_sha256`.

Producer/phase bind `regular_bar_prices` / `regular_no_auctions1`. Sampling is `completed_bar_close`. Identity, clocks, scope, auction flags, units and adjustment equal the request and actual BAR metadata. `path_source` identifies the bars binding; `proof_source` identifies the proof's own binding. Even with absent bars, validate all supplied self/config/closed payload facts; do not invent an actual bars binding or digest comparison. Payload row count/completeness must agree with actual bars when present. Consistent incomplete population is unavailable/governed_gap; disagreement is INCONSISTENT_IDENTITY.

The payload uses compact sorted-key canonical ASCII JSON, at most 4,096 bytes, depth <= 8 and each collection <= 64. No floats, duplicate or unknown keys, NaN or loose bool/int coercion. Clocks/counts are signed-int64; counts are nonnegative. Binding objects have exactly their four string fields; price unit has exactly scale/currency; adjustment exactly basis/policy_version/action_snapshot/anchor. Labels retain existing bounds; the population digest is lowercase 64-hex. Proof text and context each have independent 4,096-byte budgets.

Malformed/noncanonical values or wrong types are INVALID_SCHEMA; duplicate JSON keys DUPLICATE; oversized text BOUNDS; unsupported semantic version/profile INCOMPATIBLE_VERSION. Contradictory producer/phase/clock/identity/policy/actual binding/count/completeness/hash/reference ID is INCONSISTENT_IDENTITY. Unit mismatch is INVALID_UNIT; adjustment mismatch UNSUPPORTED_ADJUSTMENT. A consistent older proof with original known-at <= K remains eligible; no new TTL is inferred.

## Historical projection name and compatibility

Reuse the exact reviewed BAR membership projection document, including its historical version string `ef1-gap-membership-projection1`, kind `bar`, and membership_columns:

`instrument_id`, `session_id`, `start_ns`, `end_ns`, `volume_present`, `volume_class`.

Rows preserve original order, identities and bounds, whole-column volume presence, and the class `positive`, `zero` or `unknown`. Positive means supplied volume > 0; zero means 0; unknown means absent/null. Canonical sorted compact ASCII JSON is SHA256-hashed. Negative volume remains a structural error, never a projection class.

The historical word `gap` is a projection-schema identity only. It does not adopt gap mathematics or permit an `ef1.gap.population.v1` fact here. This producer's distinct proof family/version, producer and phase bindings prevent that substitution. Both families use positive-volume membership independently of OHLC/numeric availability, so this exact membership document can be shared without claiming their numerical outputs are aliases.

Exclude all OHLC prices, numeric-row known-at, positive volume magnitude, actual_notional and optional numeric-column presence from the membership projection; supplied cells still receive structural validation. Volume 1 -> 2 keeps the digest, while positive -> zero/unknown or identity/order changes do not. Hash the population directly, without embedding its row array inside bounded context/proof JSON; there is no added 64-row restriction.

Membership known by K is a factual capability distinct from price publication. The BAR row's original known_at controls its supplied numerical prices. An independently causal proof may establish membership/class by K while a selected or interior price is unknown/future only when the source truly knew those membership and bound snapshot facts then. If that source identity/class exists only after the delayed price, the adapter must report unavailable or explicit synthetic fallback, never backdate a newly computed checksum. Unknown volume remains unknown. A single row known-at cannot represent separate open/close publication clocks: both selected prices on that same row share it. Finer clocks need a new reviewed DTO/profile.

## Structural admission and readiness order

1. Validate config, exact slots/kinds, reference families/entity and every supplied DTO, canonical row and metadata contradiction before readiness. Include source, scope, unit, basis, ordering, quantity and OHLC. Use canonical optional-column behavior (`required_fields=()`). Negative volume is BOUNDS. Supplied NULL/nonpositive OHLC on positive-volume rows is INVALID_SCHEMA, including an unused interior row or a missing peer role. Zero-volume rows must not carry nonnull OHLC. Supplied prices on unknown-volume rows remain positive/coherent. Validate optional actual_notional/trade_count if present; neither is required. Retain actual constructor/int overflow behavior.
2. Validate every present proof's closed structure, identity, semantics and closure before absence or knowledge gating. Canonical duplicate checks precede exact one-row shape. Wrong proof fact family is INVALID_SCHEMA before a legacy text-label error. Proof/request C or K disagreement is an error, not a stale flag.
3. Establish common population readiness: causal complete calendar, present complete bars, and present complete independently causal proof with original known-at <= K in both modes. Accumulate lexical unique reasons for absence, unknown/future original availability and governed gaps. Any missing reason other than governed_gap gives missing_input; governed_gap alone gives incomplete_coverage. Population-unready fields have no numerical evidence.
4. If ready population is empty or definitely all zero volume, both outputs are null/not_applicable/no_eligible_observations. Irrelevant absent numeric columns do not change this. All supplied contradictions have already refused. Unknown volume is not empty: without any definite positive row both fields are unavailable, using null_field for present-null volume or absent_input for a missing volume column.
5. Select the first and last structurally positive-volume rows, never first/last known-price rows. Unknown volume before the first blocks only first-open; after the last blocks only calculated-close; strictly between fixed endpoints blocks neither. Unknown rows on both sides of a sole positive row block the two fields independently.
6. For each field, membership uncertainty short-circuits irrelevant numerical readiness for that field. Otherwise the selected open/close column must exist, with original selected-row known-at nonnull and <= K. Missing column gives absent_input; unknown clock unknown_availability; clock > K future_knowledge; equality at K is admitted. A present NULL price on positive volume was already rejected, not converted into normal unavailability. Do not rescue missing first/last prices with another row. One endpoint's readiness does not gate the other; unused interior prices need no additional availability check after independent membership admission.
7. For an available selected price coefficient p and PriceUnit scale s, output exactly `float(Fraction(p, 10**s))`: checked integer coefficients and power/division followed by one float conversion. No subtraction, repeated float rounding, FX, adjustment-factor application or quantization. One positive BAR can supply both fields; no ratio denominator or minimum history is added. Canonical DTO bounds retain positive signed-int64 coefficients and scale 0..18. No original Go/binary64 compatibility is claimed.

## Full results, counts and evidence

Both QualityRows use delivered BAR population counts: actual bars.coverage.expected (None if bars absent), observed actual BAR rows (0 if absent). Calendar/proof rows are excluded; there is no prior-close +1. Unknown expected is legal only for incomplete canonical coverage, so an available result cannot have expected None. Complete empty expected/observed 0 is valid not-applicable.

Bind complete metadata for every present actual input, lexically ordered as bars, calendar_provenance, population_proof; never fabricate an absent input binding. Preserve namespace/session, availability C/K/mode, basis, original identities and the canonical ConfigSpec digest. Values and quality are in the two-header lexical order. Result versions/backend/evidence declaration are exactly those above.

Each available field has one EvidenceRow for its selected BAR only: row_id `bar:<start>:<end>`, event_ns=end, original known_at, exact effective bounds, use `consumed`, exclusion_reason None, boundary `completed_interval`. An end equal to C is valid completed-interval evidence. No calendar/proof/interior/extrema evidence is fabricated. The same BAR supplying both fields creates two per-feature witnesses; deduplication is within a field, never across headers. Unavailable fields have no numerical evidence. Declared evidence_limit is exactly 2 and actual evidence <= 2; result has exactly two scalar cells.

The worker must reject wrong backend/version/config/header/entity/math policy/evidence declaration (including 1 or 3), source binding/roles or excess actual evidence with RESULT before any sink begin/write/commit/read. Existing generic result comparison is not proof that these new producer-specific guards exist. Structurally admissible missing columns and unknown/future numerical clocks normally return the exact unavailable result; supplied invalid/null OHLC does not take that path.

Keep protocol-5 input pickle <= 1 MiB, context/proof budgets 4,096 bytes each, and TaskJSON/output-codec budgets separate. Measure actual encoded sizes through the pending generic probes before shared freeze. Do not enlarge the generic 64-session guard, text-label bounds, JSON limits or add a DTO/codec/sink schema. Integration later uses synthetic inputs and a new separate output DuckDB.

## Literal oracle and unfinished gates

The unchanged oracle contains 100 complete synthetic requests: 46 full expected FeatureResults and 54 refusal targets. Those targets declare proposed earliest stages: 3 CanonicalBatch constructors, 1 Coverage constructor, 10 canonical batch validation, 3 new endpoint config decode and 37 new endpoint semantic/geometry cases. These are stage expectations, not observed runtime passes. Do not credit a constructor failure as pure callback execution or unsupported dispatch as implemented semantics.

Independent review reconstructed all 46 complete expected results before implementation and checked V3's version/null clarifications. This public preparation has executed no project imports, DTO constructors, transport probes or producer calculation. Pending actual generic probes, coordinator disposition and fresh distinct public-packet review must precede a shared freeze and any source-authoring grant. All source rights/capability, original parity, full EQ164, remaining outputs, installed integration/platform/browser and release/publication gates remain.
