# EQ096 — receipt contracts and evidence boundaries

Pre-code packet, October15,2026. [Story196](https://github.com/atulsrivas1/equity-features/issues/196), [R9 plan](../releases/R9/R9_RELEASE_PLAN.md), [verification strategy](../releases/R9/R9_TEST_STRATEGY.md). Five provisional complexity points. The owner requested R9 execution and explicitly authorized local review throughout EQ096–100, including final delivery. This packet is a design proposal, not implemented API or acceptance.

## Scope and ownership

Introduce optional pure distribution `equity-feature-evidence`, import `equity_feature_evidence`, initial experimental version0.1.0a1 in canonical `packages/evidence`. Python3.12, Apache-2.0, sole required dependency `equity-feature-contracts==0.0.4a4`; no dependency from core/contracts onto evidence. Existing contracts/features/strategies/labels and numerical versions remain unchanged. No filesystem, clock, network, credentials, provider, scheduling, publication or replay inside this package.

EQ096 owns closed immutable receipt records and their in-memory envelope codec/structural validation. EQ097 owns actual full typed input/config/result content encoding and fingerprint computation/verification. EQ098 owns separate optional bundle I/O and trusted replay composition. EQ099 owns bounded explanations. Do not implement their runtime capabilities in this story or claim supplied fingerprint assertions were content-verified by EQ096.

First supported content domains, fixed by this packet for EQ097: `canonical_batch`, `feature_result`, `configuration`; schema `1`, canonicalization `typed-json-v1`, digest algorithm `sha256`. All three identifiers are independently bound by each fingerprint; an existing metadata/config identity digest is never silently reinterpreted as this content digest. Initial typed support is exact CanonicalBatch schema1 (all five DataKind values), exact FeatureResult schema1 (all current ValueType alternatives and their complete typed nested values/quality/metadata/retained evidence), and exact ConfigSpec schema1. Other configuration record classes/custom types/extensions are unsupported in initial R9; supporting a reference does not admit its external content. EQ097 freezes their explicit typed field encodings before its Ready transition; no generic/reflection encoder. Initial replay support in EQ098 is the existing public `compute_trades` with exact ConfigSpec and CanonicalBatch TRADE or the explicit accepted missing-input null case, returning the complete accepted trade result. Other core/R8 calculators remain usable independently but are not silently admitted to replay. This is a fixed initial capability boundary, not a promise of universal replay.

## Public records and invariants

All records are frozen; concrete tuple/list inputs are copied to tuples. Exact built-in scalar and exact contract record types are required; bool is never an integer. Reject unknown fields/types/versions/enum values and duplicate identities. No extensible metadata bag, dynamic class path or reflection encoder.

| Record | Bound facts and validation |
| --- | --- |
| `ContentFingerprint` | domain from the three above; schema/canonicalization/algorithm fixed above; lowercase64hex digest; nonnegative exact int64 byte length of canonical content. No path/URL/resolver/access token. Length is a claimed length until EQ097 recomputes it. |
| `InputFingerprint` | nonempty role and input_id plus canonical_batch fingerprint. Roles/input_ids unique and match every ResultMetadata input binding exactly; no omitted/additional input. |
| `FormulaBinding` | feature_id and formula_version declarations, unique feature IDs. Constructor does not authenticate a registry assertion. `make_receipt` requires exactly the feature IDs present in the supplied result. |
| `EnvironmentDeclaration` | supplied Python implementation/version, platform label and nonempty package name/version pairs. Package names unique, sorted lexically; at most64. These are caller declarations, never runtime introspection, installation or compatibility proof. |
| `ExecutionClaim` | optional exact signed int64 executed_at_ns, optional clock-source label, optional nonnegative int64 uncertainty_ns. Clock source/uncertainty require a supplied execution time; unknown stays null. Execution time need not equal or exceed simulated C/K/E. No wall-clock read or false ordering inference. |
| `EvidenceDisclosure` | state `retained_complete`, `truncated`, `not_supplied`, `unknown`; retained_count and optional total_count are exact nonnegative int64. Complete requires total=retained; truncated requires known total>retained; not_supplied requires retained0/total null; unknown has total null. No global consumption completeness is implied by retained_complete. |
| `ExecutionReceipt` | receipt schema `1`, canonicalization `receipt-json-v1`; full typed ResultMetadata; configuration fingerprint; ordered input references; output fingerprint; formula bindings; environment/execution/disclosure. Binds namespace/session/C/K/E/reconstruction/config identity/backend/version/math policy/input metadata/evidence limit through full metadata. Input roles and formula IDs are sorted for presentation; semantic order within content is not normalized by the receipt. |

`make_receipt(result, ...)` admits an exact FeatureResult, copies its metadata, checks every formula feature_id/formula_version against all actual feature columns' feature_id/algorithm_version pairs and disclosure retained_count against actual evidence length, then constructs the receipt. It binds supplied content fingerprints without asserting their correctness. Direct construction is allowed for detached receipt validation and remains entirely declarative. `receipt_digest` hashes the domain-separated canonical receipt bytes, including every declaration; it does not hash unprovided inputs or output values.

Closed `EvidenceError` codes: `invalid_schema`, `unsupported_version`, `inconsistent_binding`, `duplicate`, `limit_exceeded`. Messages contain fixed context only, not echoed payloads/paths/secrets. Existing ContractError semantics are not changed.

## Canonical receipt envelope and bounds

Public `encode_receipt(receipt)->bytes` and `decode_receipt(bytes)->ExecutionReceipt` accept only in-memory objects. Bytes are ASCII JSON with ensure_ascii=true, sort_keys=true, separators comma/colon without whitespace, allow_nan=false; no BOM/trailing bytes/newline. Envelope root includes `domain: equity-feature.execution-receipt`, receipt schema/canonicalization and all fields. Digest is SHA256 of these exact bytes. No digest field inside its own preimage. JSON integer grammar is used only for bounded exact int64 fields, not floats; no generic numeric payload is in the receipt envelope. Strings preserve Unicode code points exactly (no NFC/case folding), reject surrogate code points; identity text must be nonempty/non-whitespace and contain no control characters. Each identity string <=256 Unicode code points and <=1024 UTF-8 bytes. A string label is not a URL/path fetch instruction.

Maximum encoded envelope1MiB; maximum64 input references,256 feature bindings,64 environment package bindings. Decoder checks byte length before JSON parse; rejects duplicate keys, unknown fields, floats/nonfinite constants, oversized integer tokens, excessive depth (>16) and nodes (>32768). Parsing may allocate within the admitted envelope; these are application bounds, not physical memory quotas or universal parser/OS time guarantees. Structural preflight precedes JSON construction. Fixed typed decoding revalidates all fields and reconstructs existing contract metadata explicitly. Reject noncanonical input by re-encoding and requiring byte equality: alternate whitespace/key order/escapes/numeric spelling is not silently admitted under receipt-json-v1. Recursive generic serializers, object hooks, dataclass reflection and executable deserialization are excluded.

No fields are silently defaulted on decode; omitted fields and extra fields fail. Optional facts use explicit null. Known receipt schema1/canonicalization mismatch fails unsupported_version, with no best-effort reinterpretation. Evolution requires a distinct version and migration decision; accepted old bytes remain immutable.

## Independent validation before acceptance

1. Hand-authored minimal complete receipt wire bytes and independently computed SHA256; encode/decode byte equality and digest equality. Independent oracle builds the documented object explicitly, never calls production projection helpers. Separate literals for null execution, Unicode escaping and exact int64 extrema/above2^53.
2. Each one-field declaration mutation changes receipt bytes/digest, including C/K/E, backend, metadata identity, configuration/input/output digest, formula/environment/execution/disclosure. Metadata-identical/value-different content references remain distinct. Changing an external value without recomputing its reference is not detectable in EQ096 and is documented as such.
3. Duplicate roles/input IDs/features/packages, missing/extra result binding, wrong domain, malformed digest/length, bool-as-int, unknown versions/fields and unsupported receipt input fail deterministically. Mutation of caller lists cannot change a constructed receipt.
4. Reject duplicate JSON keys, trailing content, alternate noncanonical spelling, deep/wide/oversized envelopes, invalid UTF-8/surrogates, numeric floats/nonfinite constants and huge integer tokens before unsafe materialization. Boundary cases hit exact limits and one above.
5. Synthetic public core producer example calls actual accepted calculator, creates a structurally bound receipt with clearly labeled supplied fingerprints, round trips it, and preserves full original result. No claim of a completed EQ097 verifier or replay is made. Tests independently inspect binding/retained evidence rather than merely count methods.
6. Source boundary/strict typing/public imports/license/docs checks, independent optional import with features/I/O/worker packages absent, repeat wheel/sdist source maps and clean Windows/Linux installed consumers. Freeze exact generated archive/source/RECORD maps; final current-main delivery gates before Released/Done. Add a scoped evidence workflow/build gate rather than modifying numerical algorithms or weakening existing gates.

## Documentation and delivery

Public evidence API/schema/threat/rights guide, package README/license, synthetic example, independent fixtures/tests, compatibility/version entry, changelog/knowledge lesson and handoff accompany implementation. Existing accepted source/artifact/FAILED/REWORK history is preserved. New tests/build/workflow source are part of the final reviewable story PR; do not call source-only approval execution evidence. No stable registry publication or date promise.

Ready requires this complete packet, accepted dependency states (EQ013/039/044/048), the explicit local-review grant recorded in CODE_REVIEW, independent design review/findings disposition and exact issue/PR linkage. Then Ready→In progress for implementation; Code review→Test→Ready to release→Released→Done each needs actual evidence. R9 epic becomes In progress when its first child is actually pulled; remaining children stay Backlog. No R10/R11, signing/anchors/ledgers/PIT claims, provider/private acquisition or R7 automation work.

## Review correction: exact wire and pre-projection bounds

The original pre-code review requested an exact wire fixture and constructor bounds for nested metadata. These corrections are normative; no runtime had been written at review time. Original review/failure evidence remains retained. Initial docs-check invocation used the older primary working directory and failed its story count; the corrected isolated-clone invocation passed without a product change.

Every object below is closed: exactly the listed keys, including explicit null optional values, with no defaults on decode. Array order is preserved except the explicit receipt-level role/feature/package sorting. JSON keys are sorted by the encoder. All keys and values form the digest preimage.

| Object | Exact required keys / representation |
| --- | --- |
| root | canonicalization, configuration, domain, environment, evidence, execution, formulas, inputs, metadata, output, schema_version |
| root.configuration / root.output / inputs[].content | algorithm, byte_length, canonicalization, digest, domain, schema_version |
| root.inputs[] | content, input_id, role |
| root.formulas[] | feature_id, formula_version |
| root.environment | packages, platform, python_implementation, python_version |
| environment.packages[] | name, version |
| root.execution | clock_source, executed_at_ns, uncertainty_ns |
| root.evidence | retained_count, state, total_count |
| root.metadata | availability, backend_id, backend_version, config_digest, evidence_limit, inputs, math_policy_version, namespace, schema_version, session_id |
| metadata.availability | evaluation_ns, knowledge_cutoff_ns, market_cutoff_ns, mode, reconstruction_reason |
| metadata.inputs[] | kind, metadata, role, schema_version; kind is the exact DataKind string |
| metadata.inputs[].metadata (BatchMetadata) | adjustment, coverage, duplicate_policy, interval_coverage, namespace, ordering, price_unit, quantity_unit, sampling, scope, source |
| BatchMetadata.adjustment | action_snapshot, anchor, basis, policy_version |
| BatchMetadata.coverage / interval_coverage[].coverage | complete, expected, observed |
| BatchMetadata.source | input_id, mapping_version, snapshot_id, source_id |
| BatchMetadata.price_unit | null or object currency, scale |
| BatchMetadata.scope | null or object eligibility_policy, end_ns, include_closing_auction, include_opening_auction, start_ns |
| BatchMetadata.interval_coverage[] | coverage, end_ns, name, start_ns |

Nested objects reconstruct the exact existing AvailabilitySpec/InputBinding/BatchMetadata/AdjustmentSpec/Coverage/SourceBinding/PriceUnit/InputScope/IntervalCoverage classes. Existing contract validators remain applicable; EvidenceError normalizes invalid nested contracts into closed receipt errors without echoing data. Every supplied string at every nesting level obeys the same label code-point/UTF8/control/surrogate rules, including namespace, source/snapshot IDs, mode, reconstruction_reason, adjustment text, scope labels and interval names. Control means U+0000–001F or U+007F–009F; other Unicode code points are preserved. All integer values obey exact int64 constraints (nonnegative for counts/lengths/scale); booleans occur only in the documented typed bool fields.

Before copying receipt sequences or projecting any metadata, validate concrete list/tuple type, check length first, then exact member types. In addition to64 metadata inputs, limit every BatchMetadata.interval_coverage to256 entries. Traverse the exact fixed nested metadata shape with a running value/key-node counter before allocating the wire projection; stop at32768 nodes. Thus the combination of individually permitted counts may still fail the aggregate bound. Complete typed metadata is borrowed only as immutable contract records with tuple children; no input list or mapping is retained. Out-of-bound lists are rejected before tuple conversion. Construction and encode both enforce the same metadata/string/count/node budgets; direct construction cannot bypass the decoder's limits.

Node counting is lexical and exact: count one node for each object/array opening delimiter, each string token INCLUDING object keys, each integer token, and each true/false/null token. Closing delimiters/commas/colons/whitespace are not nodes. A container's depth is the number of currently open containers, including itself (root object depth1); max16 open containers, not16 primitive recursion levels. Decoder first checks bytes length, then an iterative lexical scan counts nodes/depth and bounds integer tokens to20 characters (optional leading minus plus at most19 digits), before json parsing. Strings are scanned with JSON quote/backslash escape state so delimiters within strings are inert. Syntax/escape/value validity is still validated by JSON parser and strict typed decoder. No object construction occurs before lexical budgets pass. Constructor/encoder node counts use the same object/key/value rules, with bounded traversal before building projection; final encoded bytes must also fit1MiB.

The detached oracle in [EQ-096_RECEIPT_ORACLE.json](EQ-096_RECEIPT_ORACLE.json) is hand-authored ASCII bytes, no terminal newline, before any production helper exists. It deliberately supplies zero/one placeholder content hashes; this tests receipt-envelope identity, not verified content or a successful execution. A detached receipt can have no inputs, and formula declarations can be empty only for an empty actual result when make_receipt is used. The existing contract permits an empty ResultMetadata.inputs tuple. The actual calculator example is a separate positive producer fixture.

Frozen oracle: 1313 bytes, SHA256 `a59809b288709a51abe17bd2fde1109d0c041cef61a352ebd5e8b68946ea2a86`, 107 nodes, maximum container depth4. SHA256 computed by independent standard-library hashlib over the literal file, not by a production receipt helper. Tests must compare actual bytes to this file and the literal digest; mutating the file and recomputing its expected hash together is not acceptance.
