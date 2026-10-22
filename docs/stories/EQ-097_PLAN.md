# EQ097 — deterministic full typed content fingerprints

Pre-code packet, October15,2026; [story197](https://github.com/atulsrivas1/equity-features/issues/197), eight provisional complexity points, [R9 plan](../releases/R9/R9_RELEASE_PLAN.md). Dependency EQ096 is accepted Closed/Done at mainb307dde285b4541714dd69555f9976af878a05ca, [acceptance](https://github.com/atulsrivas1/equity-features/issues/196#issuecomment-6192835359). R9 owner execution/local-review grant continues. This is a design packet, not implementation, Ready or qualification evidence.

## Ownership, supported records and public behavior

Extend optional pure `equity-feature-evidence` to0.1.0a2, required contracts exactly0.0.4a4. Existing receipt schema1/receipt-json-v1 and supplied-reference API retain their meanings. No core/contracts/features/strategies/labels math/source/version changes. No PyArrow/native buffer hashing, source acquisition, clock, file/network/credential, provider, worker, publication, bundle/replay or explanation work inside the package. Choose logical typed encoding, independent of Arrow/chunk layout or host byte order.

Only exact CanonicalBatch, FeatureResult and ConfigSpec root types are supported. All five DataKind schemas and current FeatureResult ValueType alternatives are supported within the fixed bounds below. Other configuration classes/extensions/custom types/arrays/NumPy scalars/arbitrary mappings are rejected, not stringified. Nested records are only the exact closed types in the field table below. Pure helper reads accepted supplied facts; it does not certify structural facts as mathematically calculated or authentic.

Public additions:

- `canonical_content(value)->bytes` materializes the exact bounded content encoding.
- `content_chunks(value)->Iterator[bytes]` validates the entire fixed graph before first yield, then emits chunks of at most65536bytes. It retains the supplied immutable graph, not a full projected tree. Cancellation has no owned external resource. This is not atomic publication; an external sink must handle its own partial write/cleanup.
- `fingerprint_batch`, `fingerprint_result`, `fingerprint_config` compute ContentFingerprint from actual supplied typed content; SHA256 updates stream, without materializing the full encoded content. Generic root selection is based on exact supported type, never caller-selected hash/domain/encoder.
- `verify_content(reference,value)->bool` recomputes typed content and compares complete fingerprint domain/schema/canonicalization/algorithm/length/digest. Valid typed mismatch is false; unsupported/malformed/over-budget content raises fixed EvidenceError. This verifies supplied content consistency only.
- `make_content_receipt(result,configuration,inputs,environment,execution,evidence)` accepts actual FeatureResult, ConfigSpec and concrete <=64 role/CanonicalBatch pairs. Validate all roles/kinds/full input metadata against result.metadata, complete configuration.digest/availability/session/namespace bindings and actual result feature versions/evidence count; fingerprint the full configuration, all supplied batches and complete result; then call accepted make_receipt. No callback, calculation or registry execution is added. A missing-input result legitimately has zero input bindings.
- `verify_receipt_content(receipt,configuration,inputs,result)->bool` checks supplied content and those structural relationships against the receipt. Reuse receipt's environment/execution/disclosure declarations without asserting their truth. Valid content/binding mismatch returns false; malformed/unsupported/over-budget inputs remain explicit errors. No global safety score or source/mathematical/execution verification claim.

Computing correct hashes does not prove those inputs produced an output. The actual synthetic public example runs accepted compute_trades, then produces/verifies the receipt and preserves all five original outputs/quality/metadata. A same-metadata one-value change fails content verification. Actual replay remains EQ098's separately trusted registry composition.

## Exact typed-json-v1 encoding

The complete content is ASCII JSON with ensure_ascii=true, allow_nan=false, sort_keys=true and comma/colon separators without spaces/BOM/newline. Root keys are exactly `algorithm`, `canonicalization`, `contracts_version`, `domain`, `project`, `schema_version`, `value`. Constants are sha256, typed-json-v1,0.0.4a4, equity-features,1; domain is canonical_batch/feature_result/configuration selected from the root type. Runtime contracts version mismatch refuses unsupported_version. SHA256 hashes these complete bytes; ContentFingerprint.byte_length counts all of them. No digest is stored inside its own preimage.

Every record is exactly `{ "type": TYPE_ID, "fields": {all listed fields} }`, with canonical JSON key ordering. TYPE_ID is a closed data tag, never a module import or executable class path. Arrays retain order except CanonicalBatch.columns sorted by unique column name (presentation only). All row positions and tie keys, FeatureResult feature/entity/value/quality/evidence order, parameter/session/window order as retained by their accepted constructors, and retained diagnostic rows are preserved. No hidden sort/deduplication, missing-column filling or omitted-field normalization.

Primitive encoding: null→null; exact bool→true/false; exact int with absolute value<10^38→unquoted canonical decimal integer; exact finite float64→`{"float64": value.hex()}`; exact string→JSON string; known enums→their exact string value; concrete tuple→JSON array. No conversion through float for integers/UTCns/Decimal128 scaled integers. Field/type/schema tags bind scalar meanings; Decimal128 is the accepted scaled integer, not an arbitrary Python Decimal. Negative zero and positive zero float64 remain distinct via hex; subnormals retain exact bits; NaN/infinity are rejected. Fractions, float32, generic iterables and unknown objects are rejected. Null and missing columns remain distinct. Unicode code points are preserved without normalization; surrogate code points are rejected. Numeric or string values never select code, paths, URLs or providers.

The fixed accepted core validators define field widths/relationships: int64 UTC/order/count/unit fields, Decimal128 scaled values, finite float64 cells and explicit boolean fields. The encoder revalidates primitive admission and exact record/version types; it never expands accepted values beyond their existing contracts. ConfigSpec.Parameter integer values additionally require abs(value)<10^38 for this content version; larger otherwise-generic parameters are unsupported. Payload strings (Column.values, scalar FeatureColumn.values and Parameter.value) may be empty or contain escaped controls, <=4096codepoints/16384UTF8bytes. All identity/other labels obey EQ096's <=256codepoint/1024UTF8/control/surrogate rules. No payload value is echoed in errors.

### Closed TYPE_ID and field registry

All fields listed are mandatory, optional facts explicitly null; no derived property is added or stored field omitted. Nested metadata field sets are exactly [EQ096's wire table](EQ-096_PLAN.md#review-correction-exact-wire-and-pre-projection-bounds), now wrapped in the corresponding TYPE_ID/fields record. Fixed IDs/fields:

| TYPE_ID | All stored fields |
| --- | --- |
| inputs.CanonicalBatch | kind, columns, metadata |
| inputs.Column | name, values |
| inputs.BatchMetadata | namespace, source, coverage, price_unit, adjustment, sampling, quantity_unit, ordering, duplicate_policy, scope, interval_coverage |
| inputs.SourceBinding | source_id, snapshot_id, mapping_version, input_id |
| inputs.Coverage | expected, observed, complete |
| inputs.PriceUnit | scale, currency |
| inputs.AdjustmentSpec | basis, policy_version, action_snapshot, anchor |
| inputs.InputScope | start_ns, end_ns, eligibility_policy, include_opening_auction, include_closing_auction |
| inputs.IntervalCoverage | name, start_ns, end_ns, coverage |
| specs.ConfigSpec | identity, algorithm_version, parameters, session, window, availability, adjustment, price_unit, schema_version |
| specs.Parameter | name, value |
| specs.SessionSpec | namespace, session_id, open_ns, close_ns, timezone_label, intervals, scheduled_close_ns, early_close, include_opening_auction, include_closing_auction |
| specs.IntervalSpec | name, start_ns, end_ns |
| specs.WindowSpec | count, target_session_id, governed_sessions, anchor |
| specs.AvailabilitySpec | market_cutoff_ns, knowledge_cutoff_ns, evaluation_ns, mode, reconstruction_reason |
| results.FeatureResult | values, quality, metadata, evidence |
| results.FeatureColumn | feature_id, algorithm_version, dtype, unit, entities, values, schema_version |
| results.EntityKey | instrument_id, session_id |
| results.QualityRow | entity, feature_id, status, expected, observed, reasons |
| results.ResultMetadata | namespace, session_id, availability, config_digest, inputs, backend_id, backend_version, evidence_limit, schema_version, math_policy_version |
| results.InputBinding | role, kind, metadata, schema_version |
| results.EvidenceRow | entity, feature_id, input_id, row_id, event_ns, known_at_ns, effective_start_ns, effective_end_ns, use, exclusion_reason, boundary |
| results.BreadthCounts | advancing, declining, unchanged, expected |
| results.BreadthFraction | above, eligible, expected |
| results.TopKTrades | k, rows |
| results.TopKTradeRow | input_id, event_id, event_ns, order_key, known_at_ns, price, size |
| results.QuoteStateCounts | normal, locked, crossed, invalid |
| results.QuoteObservation | input_id, event_id, event_ns, order_key, known_at_ns, bid, ask, state, spread, bps |
| results.SampledSpread | sampling, total, valid, mean_spread, mean_bps, observation_limit, rows |
| results.QuoteDurations | normal, locked, crossed, invalid, expired, unknown |
| results.TimeWeightedSpread | durations, mean_spread, mean_bps, max_age_ns, initial_state |
| results.IntervalOHLCV | rows |
| results.IntervalOHLCVRow | interval, open_price, high_price, low_price, close_price, volume, quality |
| results.IntervalVolumeShares | rows |
| results.IntervalVolumeShareRow | interval, share, quality |

Known enum types are only inputs.DataKind/DType and results.Status/Reason/ValueType; no derived integer enums or generic StrEnum. The field registry is explicit static code, not dataclass reflection, getattr, object dictionaries, arbitrary adapters or artifact-driven type lookup. Content encoder/streamer never decodes or executes supplied wire records; data-only reconstruction is separate EQ098 work.

## Bounds and cost contract

Per content: <=32MiB exact encoded bytes; <=1,000,000JSON value/key nodes; <=24 simultaneous containers; <=100,000 elements per generic stored tuple. CanonicalBatch <=64columns/100,000rows; FeatureResult <=256feature columns, <=100,000quality/evidence/entity/value/diagnostic rows in each stored tuple. Metadata <=64input bindings and <=256interval_coverage per input, with EQ096 metadata-specific validation retained. Individual maxima do not imply their combination fits aggregate bytes/nodes. make_content_receipt additionally admits <=32MiB and1,000,000nodes across configuration+all inputs+output before generating any fingerprint/receipt.

Node/depth counting uses EQ096 lexical rules, INCLUDING every wrapper/type/fields/key token and the float64 wrapper. Validate the entire immutable fixed graph and exact size/node/depth/string/sequence budgets before first emitted chunk or full projection. No full projected record tree, lazy caller iterable or array copy is required for streamed hashing. Content materialization explicitly accumulates/copies the full bounded output; streaming retains the caller's original immutable input graph. A single encoded string token is bounded and emitted chunks never exceed65536bytes. Both paths must yield exactly the same bytes/hash/length.

Complexity is O(supplied content) per bounded traversal; prevalidation/streaming/materialization are separate passes/costs. Exclude already-owned input storage from incremental allocation claims and report it explicitly. These are application-level controls and measurements, not total process/native RSS quotas, physical I/O counts, hard kernel deadlines or universal cleanup guarantees. Errors do not grant replacement execution or certify missing evidence. No external resources are opened, closed or borrowed by the pure helpers.

## Independent fixtures, measurements and delivery

Before Ready, freeze independently authored complete typed wire oracles and literal SHA256/byte/node/depth expectations, including float64 negative zero, exact UTCns/int64 bounds and an integer above2^53. The expected wire is authored before the production projection exists, not generated by it. Additional tests cover all five batch kinds/all ValueType graphs, one-value/null/unit/row-order/metadata/quality/evidence/config/revision changes, missing versus all-null columns, column presentation permutation invariance, UTF8/control/surrogates, bool versus int, Decimal128 extremes, +/-zero/subnormals/nonfinite, immutable source/no callback and exact aggregate limits. Metadata-identical/value-different results must hash differently; old ResultMetadata.identity_digest remains unchanged.

Actual synthetic compute_trades example asserts all five values (3,10,1011,101.1,10/3) and complete original output/quality/metadata before/after content receipt generation/verification. Mutate actual batch/output under identical metadata and require false; malformed/version/limit cases remain errors. Unknown environment/time/source declarations remain unknown, not authenticated by a matching content hash.

Measured script outside pure package uses fixed synthetic1,000/10,000row populations, three raw samples per population/operation: canonical materialization, hash-only over already materialized bytes, streamed complete fingerprint and complete receipt generation using an already-produced result. Retain raw timings, encoded bytes/rows/environment and traced-Python incremental allocation peaks; separately report existing input storage excluded and allocator/native/RSS limitations. Verify parity before timing. No speedup/physical-budget claim or automatic backend change. Run in a fresh installed combined wheel consumer once perOS; sdist/other forms still execute fixtures/examples/typing. Source snapshot and exact benchmark inputs are pinned in the qualifier.

Extend existing evidence build/CI gate for0.1.0a2 with repeat archives, fresh Windows/Linux wheel/sdist isolated/actual-core combined consumers, strict public typing/import boundaries, complete source/RECORD/sdist/current serverZIP metadata/maps, unchanged original numerical packages and actual-main publication. Add content API/threat/version/format docs, independent oracle fixtures, synthetic example, raw measurement evidence, compatibility/changelog/lesson/handoff with this story. Preserve accepted EQ096/R8/R7 and original FAILED/REWORK; no unchanged status reruns or receipt-only publication loops.

Ready requires the frozen oracles, complete reviewed packet/decisions, accepted196 dependency and current issue/PR/review route. Then actual Ready→In progress; separate final source/docs/artifact/current-main acceptance before Released/Done. EQ098–100 stay Backlog; no stable registry, arbitrary replay, signing/ledgers, source truth, provider/private acquisition, public service/admin or R7 automation scope.

## Frozen independent wire oracles before production code

These are explicit hand-authored wire objects, not output from a dataclass/production projection. Configuration includes int64 UTC extrema, exact9007199254740993 above2^53 and float64 negative zero; result includes negative-zero content with complete value/quality/metadata/evidence graph. Detached synthetic declarations do not assert an actual execution. Files contain exact canonical ASCII bytes with no terminal newline. Standard-library JSON sorts the explicitly authored keys; independent hashlib computes the literal digests below. Tests must bind these files to these literal values, not recompute both expected and actual through the production encoder.

- `docs/stories/EQ-097_CONFIG_ORACLE.json`: 1341bytes; SHA256 `e1b12d267ef25cadd48549725e7ff1c8f1f4254bde30b910ee8fd27aaee5585d`; 129nodes; max container depth7.
- `docs/stories/EQ-097_RESULT_ORACLE.json`: 1219bytes; SHA256 `4f78413ee898ed72031423695a16bdb4d8a3d7f5b38b4f814bd709fbed8dc287`; 121nodes; max container depth9.

- `docs/stories/EQ-097_BATCH_ORACLE.json`: 1558bytes; SHA256 `fa7e282711dc54e88bf2ae51a247a4969ea416be74e1bfe3e4e633207998e1bf`; 183nodes; max container depth7. The explicit wire object is a structurally valid one-row TRADE batch with lexically sorted columns, null price/known-at, exact int64-min event time, order_key9007199254740993 and scale2/USD. It is a typed content fixture, not an asserted successful trade calculation. This third independent oracle closes known-byte coverage for all three root domains before production code.
