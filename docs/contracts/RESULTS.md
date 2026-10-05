# Typed results, quality, evidence and failures

EQ-013, experimental0.0.1a3. These contracts admit caller-supplied result data;
no numerical calculator exists yet. Construction proves structural compatibility,
not mathematical accuracy, provider truth or actual calculation capability.

## Values and independent readiness

`FeatureResult(values,quality,metadata,evidence=())` owns concrete tuple tables.
Each `FeatureColumn(feature_id,algorithm_version,dtype,unit,entities,values)` has
an exact declared `ValueType` and keyed `EntityKey(instrument_id,session_id)` rows.
Schema1 values support int64, exact decimal128 scale0 coefficient, finite float64,
Boolean/string and explicit structured breadth. Lists detach; lazy iterables fail.
`QualityRow(entity,feature_id,status,expected,observed,reasons)` must align exactly
with the value keys, with no duplicate entity/feature keys. Each feature's quality
is independent; a missing quote measure cannot erase an available trade count.

Stable `Status`: available, insufficient_history, missing_input,
incomplete_coverage, not_applicable. Available needs a nonnull typed value and
complete declared expected/observed coverage. Zero from an observed empty input
can be available where the formula defines it; unavailable scalars are always null.
Expected counts may be unknown for unavailable inputs. Every unavailable/partial
status needs a typed `Reason`; absent_input, null_field, observed_empty,
insufficient_history, governed_gap, unknown_availability, future_knowledge,
partial_universe, zero_denominator, empty_universe, ineligible and future_market
preserve the cause. EQ-014 also supplies no_eligible_observations and
missing_action_evidence for the accepted formula policies. Reasons do not replace formula-specific admission checks.

`BreadthCounts(advancing,declining,unchanged,expected)` and
`BreadthFraction(above,eligible,expected)` are the EQ-005 structured exception.
Positive E<=M is mandatory; fraction uses K/E, coverage E/M, represented by exact
Fraction properties. Partial universe retains structured values with
incomplete_coverage and exact quality E/M. Full universe uses available. E=0
uses a null structured value, not manufactured zero directions/fraction; empty
universe is not_applicable and absent universe missing_input. Missing members
never become unchanged. These constructors admit supplied counts, not compute them.

## Identity and evidence

`ResultMetadata` binds namespace/session, AvailabilitySpec C/K/E/mode/reason,
canonical config digest, role-keyed `InputBinding(kind,BatchMetadata,schema1)`,
backend ID/version, result schema/math-policy version and explicit evidence limit.
Input bindings retain source/snapshot/mapping/input identity, price unit, adjustment,
sampling and coverage. Duplicate role/input identities and namespace mismatch fail.
Algorithms and units are in each value column. `metadata_json()` serializes only
these identities; `identity_digest` hashes canonical metadata, not result values.
`require_same_identity(other)` requires exact metadata and feature definitions.
It is a conservative equality check, not the future general composition API.
No metadata field certifies source access or readiness of an unimplemented backend.

`EvidenceRow` binds entity/feature/input/original row IDs, exact event/known-at/effective
UTCns, `use` consumed/excluded, exclusion reason and boundary marker. Consumed
causal rows need known_at<=K; unknown/later knowledge fails. Excluded diagnostic
rows retain original null/future knowledge with an explicit reason. Reconstruction
can consume unknown/later knowledge but retains its distinct mode/reason identity.
Ordinary trade/quote evidence needs event<C; explicit trade closing_auction can be
at C, while quotes have no exception. Completed_interval is only for bars/daily
with end<=C. Reference effective evidence remains bounded. The caller must bind
and honor the actual session/auction configuration whose digest is recorded;
construction cannot recover that configuration from its hash or prove source row
contents.

The alpha6.post1 review repair shares a single input-kind/boundary cutoff predicate
for consumption and FUTURE_MARKET exclusion reasons. Ordinary trades/quotes at C
are excluded and may retain that reason, including original unknown/future knowledge.
Before C the reason contradicts the bound. Completed bar/daily/reference endpoints
and explicit closing-auction trade at C are admissible and cannot claim FUTURE_MARKET.
After C, market exclusion is consistent. Incompatible boundary/kind markers fail for
both consumed and excluded diagnostics; a consumed closing auction must be exactly C.
Six independent regressions cover this matrix and exact Arrow diagnostic retention.
Schema/math policy remain1/v1; this corrects admission without a formula change.
 Evidence is bounded by a caller-declared global row limit, keyed without
duplicates, and cannot reference missing result/input keys. No unbounded top-K
state or evidence discovery is introduced.

## Typed failures and optional Arrow output

`ContractError(ValueError)` exposes stable `ErrorCode`: invalid_schema,
invalid_order, duplicate, invalid_unit, bounds, overflow, inconsistent_identity,
invalid_config, incompatible_version, unsupported_sampling, unsupported_adjustment.
Schema/type/precision/config/bridge admission now uses this vocabulary. Invalid
input raises; absent/unready enrichment uses result status. ValueError handlers
remain compatible. Semantic order/duplicate/normalization enforcement is EQ-014;
there is no silent error-to-zero conversion. Backend resource exhaustion is not
misrepresented as malformed schema.

`equity_feature_contracts.columnar.to_arrow_result(result)` explicitly materializes
an owned dictionary of values tables keyed by feature, a quality table and an
evidence table. Each Arrow schema carries canonical `equity.result` metadata.
Wide values use decimal128(38,0), evidence time ns/UTC, quality keeps nullable
expected counts and reason lists, partial breadth keeps integer structs with E/M
and K/E operands. No float epoch/coefficient conversion, lazy source protocol or
zero-copy/performance claim. Metadata serialization does not serialize code; no
remote transport or executable result loading is established.

32new/87total synthetic unit cases cover all statuses, null/zero/empty distinctions,
independent quality, scalar bounds/types, explicit partial breadth, identity/version
compatibility, evidence bounds/causal exclusions/auction exceptions, copied Arrow
output and typed malformed JSON/NumPy/Arrow errors. Existing123mathematical
references remain separate equation evidence. Repeat build/install/example,
exact-head/main CI and actual artifact verification gate delivery.

## EQ018 structured migration —0.0.2a1

IntervalOHLCV/IntervalVolumeShares typed table cells extend ValueType. Nested IntervalSpec/QualityRow and nullable numerical fields preserve independent per-window readiness. FeatureResult permits explicit typed partial tables only with consistent aggregate expected/ready counts and keyed row quality. Missing sources remain null. Arrow materializes list-of-struct data with UTCns and nested quality; [interval API](../api/SESSION_STRUCTURE.md) describes schema, arithmetic and copy costs.
