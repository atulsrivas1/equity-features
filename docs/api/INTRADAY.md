# Intraday snapshot API and transport contract

EQ136 [#470](https://github.com/atulsrivas1/equity-features/issues/470). Concrete specification for separate review, not an importable API or accepted implementation. [Mathematics](../features/INTRADAY_FOUNDATIONS.md), [package choice](../decisions/R17_INTRADAY_PACKAGE.md). All names below describe the selected first optional version; dependent implementation must match the accepted revision.

## Owned context and public operations

The following signatures use existing `CanonicalBatch`, `ConfigSpec`, `FeatureResult`, `SessionSpec`, `AvailabilitySpec`, `AdjustmentSpec`, `PriceUnit` and standard-library `Fraction`. All own records are frozen concrete dataclasses; sequences become owned tuples. No generators, callbacks, user-defined subclasses or mutable aliased buffers cross this boundary.

```python
IntradayRun(session_id: str, start_ns: int, step_ns: int, count: int)
IntradayContext(
    instrument_id: str, calendar_id: str, grid_id: str, revision: str,
    sessions: tuple[SessionSpec, ...], runs: tuple[IntradayRun, ...],
    anchor_index: int, target_index: int, mode: str,
)
build_intraday_config(
    context: IntradayContext, *, period: int, band_k: Fraction,
    availability: AvailabilitySpec, adjustment: AdjustmentSpec,
    price_unit: PriceUnit, evidence_limit: int = 0,
) -> ConfigSpec
compute_intraday(
    batches: tuple[CanonicalBatch, ...] | None,
    context: IntradayContext, config: ConfigSpec, *,
    features: tuple[str, ...],
) -> FeatureResult
describe_intraday() -> tuple[IntradayFeature, ...]
intraday_catalog_digest() -> str
require_intraday_capability(feature_id: str, capability: str) -> None
```

`None` is an absent delivery; an empty tuple is an observed delivery with no batches. Each supplied batch has BAR kind, one context instrument, one real context session and matching namespace/unit/action/scope. Multiple nonoverlapping chunks are allowed; duplicate slot rows across chunks are rejected. `features` is nonempty, unique, selected from this own catalog and normalized into lexicographic order. The function returns only selected cells. Period is required even for an output sharing another period's preparation. `band_k` is required, canonical positive Fraction with numerator and denominator each <=1,000,000; equality uses the reduced rational, not a float spelling. EMA/bands N<=4,096; RSI/ATR N<=4,095 because their warm-up requires N+1 slots within the4,096-slot context bound. The mathematical minimum N is checked for each selected output. A configuration may serve several selected outputs with the same period/k; different periods use separate configurations/results. Unused k is still bound, not silently dropped from identity.

Context is an explicit finite governed grid, not a calendar inference engine. Each run expands to count adjacent slots `[start+j*step,start+(j+1)*step)`. All exact UTC ns arithmetic is checked before expansion against signed int64. Run count and step are positive integers, not booleans. Sessions are chronological, unique actual SessionSpec values with one common namespace, no overlap, and empty `intervals` (this API owns bar intervals through runs). Runs reference those actual sessions, are chronological/nonoverlapping and remain inside them. A session break requires separate runs; a short final bar requires a separate run. Caller asserts that the resulting grid is the complete expected trading grid, including its calendar/auction policy. Omitting a real expected bar is invalid caller evidence, not something a price-only library can detect independently.

Global slot indices follow expanded run order. There are 1..4,096 slots, 1..64 sessions and 1..256 runs. Target is the final slot; no governed future suffix is encoded. Anchor is an explicit index 0..target. Only anchor..target is eligible for this epoch's features, including finite band windows. Earlier grid slots may be supplied for identity or another calculation but cannot silently extend a reset epoch. `mode` is exactly `reset` or `carry`. Reset requires anchor at the first governed slot of the target's actual session and target in that session; carry may cross supplied sessions from its explicit anchor. Sessions without grid slots are rejected. These bounds and semantics apply equally to direct and worker calls.

Identity labels are nonblank printable ASCII strings (codepoints32..126), <=128 characters, including instrument/calendar/grid/revision/session/namespace; timezone labels <=64. The same own printable/length restriction applies to supplied source/snapshot/mapping/input identifiers, action policy/snapshot/anchor labels and scope eligibility policy. Reject control characters/DEL before either direct or worker execution rather than admit a direct-only label that the existing worker codec rejects. Session names remain real opaque identifiers, not formatted timestamps substituted for bars. Unknown mode, zero/negative count, invalid index, missing session or mismatched context/config is a typed ContractError, not a null numerical result.

## Closed context codec and configuration identity

Context wire schema is `equity-features.intraday-context.v1`. Canonical JSON contains exactly `schema`, `instrument_id`, `calendar_id`, `grid_id`, `revision`, `sessions`, `runs`, `anchor_index`, `target_index`, `mode`. Sessions contain all SessionSpec dataclass fields; `intervals` is an empty array. Runs contain exactly `session_id`, `start_ns`, `step_ns`, `count`. Encode UTF-8 with sorted object keys, compact separators, ensure_ascii=True, no nonfinite numbers, and no floats anywhere in this context. Decoder rejects unknown/missing/duplicate keys, booleans in integer fields, excess limits, invalid UTF-8 and noncanonical bytes; no pickle, runtime imports or executable objects. Maximum canonical context size is 65,536 bytes. Digest is SHA256 of those exact bytes; it binds supplied identity and grid, not authenticity of external facts.

The config builder returns the final genuine ConfigSpec before calculation or task construction:

- identity `intraday.snapshot.v1`, algorithm_version `intraday-v1`, schema_version `1`;
- target actual SessionSpec; WindowSpec contains all actual context session IDs in order, count equals that session count, anchor `completed_eod` to include the target; count is not N and inclusion does not certify completion;
- supplied AvailabilitySpec, AdjustmentSpec and PriceUnit unchanged;
- parameters exactly `period`, `k_num`, `k_den`, `evidence_limit`, `context_schema`, `context_sha256`, `context_chunks`, and `context_000` through the final consecutive chunk name. No other operation parameters are accepted.

`context_schema` is the wire schema string. Split canonical ASCII context text into consecutive chunks of at most4,096 characters (all except last exactly4,096), at most16 chunks; `context_chunks` is the exact positive count. Each chunk is a scalar Parameter string, compatible with existing manifest scalar limits. Concatenation must decode canonically to the exact context supplied directly, and its digest must equal `context_sha256`. This is actual context transport, not a digest lookup into a global cache. Rebuilding the configuration must reproduce exactly config.digest. Scope/auction flags, actual session bounds and C/K/E must agree; no metadata rewrite or alternative config digest is permitted after direct calculation.

Worker transport also obeys the existing complete manifest preflight and MAX_MANIFEST_BYTES=1,048,576. Passing the context-size limit does not waive a smaller remaining manifest budget; a task exceeding that total is rejected before dispatch. Canonical source metadata can itself exhaust that budget. Reject oversize transport explicitly; do not silently truncate, split one snapshot into unbound pieces or broaden limits. EQ140 must prove the complete installed top-level trusted adapter reconstructs identical context and returns exact direct result identities under sequential/thread/process modes. Existing CustomRegistry/RequiredCommandSpec/acquisition APIs are not declared intraday-aware.

## Row admission, per-slot coverage and source independence

Perform existing canonical structural/semantic validation with `required_fields=()` before feature-specific field readiness. Check all supplied rows against actual context slot/session/instrument/scope and compatible source bindings. A row not on the declared grid, duplicate/overlap, malformed supplied OHLC, incompatible units/action basis or a supplied row with end>C raises the existing appropriate typed ContractError for the call. Do not invoke daily HistoryContext or require target session close<=C. Target slot end must be<=C; equality is valid. Known-at eligibility is evaluated only for the actual operand slots of each selected feature, not as a global feature barrier.

Each batch has an actual InputScope covering its represented interval, with the same eligibility policy and auction flags as other chunks for this operation. Its metadata.interval_coverage declares per-slot entries named `slot:<global_index>` with the exact slot bounds. A coverage entry is unique across chunks; each row has one matching entry. Coverage expected/observed is at most1. Expected1/observed1/completeTrue certifies one finalized governed observation. Expected1/observed0/completeFalse is a missing observation; expected0/observed0/completeTrue is an explicitly observed empty slot, distinct from an omitted entry. Null required price on an otherwise admitted row remains unready; no close or previous-close fabrication is allowed. Contradictions between entries, actual row counts, batch aggregate coverage and scope are admission errors. Aggregate batch completeness alone never substitutes for per-slot coverage or blocks a disjoint fully covered selected window.

The same role is not reused across chunks. Result input roles are `bars:000` etc. in supplied tuple order, each retaining its exact original BatchMetadata. Input IDs must be unique; source/snapshot/mapping identities must agree across chunks of the same operation. Context revision is the caller's grid revision and is independently bound in config; it does not replace those source bindings. Swapping chunk order changes binding identity even if arithmetic is equal. Missing entire deliveries have no invented input binding. No file/database/network acquisition, clocks, credentials, scheduling or output publication occurs inside this API.

## Quality, precedence and bounded evidence

After global admission, decide each selected output separately, in this precedence order. Collect all applicable reasons in their enum string order, without duplicates; the first applicable status wins.

| Condition | Status and reasons |
| --- | --- |
| Entire delivery None, or an operand column absent from any supplied chunk containing required slots | missing_input / absent_input |
| Fewer governed epoch slots than N (EMA/bands) or N+1 (RSI/ATR) | insufficient_history / insufficient_history |
| Empty delivery or required slot with no row/coverage entry | incomplete_coverage / governed_gap; empty delivery also observed_empty |
| Slot explicitly observed empty | incomplete_coverage / observed_empty, no_eligible_observations |
| Required null field or incomplete/unknown per-slot coverage | incomplete_coverage / null_field or governed_gap respectively |
| Required row unknown/later known at K | incomplete_coverage / unknown_availability or future_knowledge |
| Complete band position with mathematical variance zero | not_applicable / zero_denominator |
| All actual operands admitted and ready | available; no reasons |

No numeric data is returned for an unavailable cell. Observed counts use unique dependency slots whose required fields, coverage and known-at eligibility all qualify. Expected is N or N+1 during insufficient warm-up; otherwise it is the unique count of required epoch/window slots. ATR's dependency slot union is anchor..target: anchor requires close only, target H/L only, intervening slots close/H/L. For band windows, count only the last N slots from the current epoch; an older out-of-window gap or later-known value does not block them. A missing column in an unrelated old chunk is not an absent operand. Zero-width position retains full observed/expected counts. Warm-up is not a missing-price fill.

This API bounds evidence_limit to integer0..10,000 (a narrower own bound than the generic core count). It is normalized and bound in ConfigSpec by the builder, so the worker can recover it from task.config without out-of-band state. Selected feature IDs come from task.features headers and must match the direct request. There is one scalar EntityKey(context.instrument_id,target actual session) per selected feature, Float64 dtype and schema1; units `currency/share`, `RSI points` or `fraction` as appropriate. Column algorithm_version is `intraday-v1`. ResultMetadata retains exact namespace/session/availability/config digest and actual input bindings, backend_id `intraday.python`, delivered package backend_version, schema1/math_policy_version `v1` for companion compatibility; the explicit column/config version distinguishes the intraday mathematics. No claim is made that core registry verification accepts these own IDs.

Bounded EvidenceRows list actually supplied consumed or knowledge-excluded operand rows, never invented absent rows. row_id is `slot:<global_index>`, event_ns is slot end, effective_start/end are slot bounds and boundary is `completed_interval`, including end=C; known_at_ns is the row's supplied value. Input ID is the actual source input_id. Evidence is sorted by feature ID then slot index, truncated to the declared result-wide limit; limit0 returns none. Reasons/counts always summarize full selected dependencies independently of truncation. Preserve exact identities in direct/worker parity; the adapter must not rewrite backend or input metadata to manufacture equality.

## Numeric error contract and capabilities

Admitted prices are existing positive signed-int64 coefficients, scale0..18. The per-feature N bounds and rational k bound above keep mathematical outputs finite in Float64, but intermediate sums/squares may exceed int64/decimal128. Use sufficiently wide exact or guarded stable representations; no wraparound. Material negative variance, failed finite conversion or violated arithmetic invariant raises OVERFLOW, never a plausible zero or an unavailable-data status. This is a whole-call arithmetic failure; implementations may not claim per-cell numerical fault isolation in this version.

For each finite oracle result x, compare the returned Float64 y with correctly rounded reference r=float(x): `abs(y-r) <= max(8*ulp(r), 1e-12*abs(r))`. This applies to each output in its stated units, including tiny dimensionless width/position values, with no universal absolute1e-12 floor. Exact mathematical zeros must return normalized +0.0; initialized-flat RSI is exactly50. RSI remains in[0,100]. Do not clamp band lower or position. Reference variance is centered exact Fraction; square roots and irrational formulas use at least120 significant Decimal digits before final float conversion. Independent fixtures must include near-cancellation and large offsets; matching rounded price bounds is not proof of correct ratios. Record any future tolerance/version change explicitly.

Public capabilities for this version: batch snapshot and caller-supplied full-history replay; no update, checkpoint restore or arbitrary merge. `require_intraday_capability` rejects unsupported names/capabilities with UNKNOWN_FEATURE or UNSUPPORTED_CAPABILITY. No persistent/live service or full-series API is implied. Internal preparation may reuse compatible immutable operands, retaining full config/context/source/selected-window/anchor identity; benchmark its copying/allocation cost. EQ137 freezes the concrete preparation API before its implementation, and cannot expose public recurrence state by implication.

## Own discovery

Frozen `IntradayFeature` fields: feature_id, algorithm_version, unit, minimum_period, operand_family, supports_batch, supports_update, supports_restore, supports_merge. Operand families are `anchored_closes`, `anchored_true_ranges` or `rolling_price_moments` with the exact mathematical closure in the linked contract; RSI/EMA are separate recurrences despite sharing a family. Entries are lexicographically sorted and unique. Catalog digest is SHA256 of canonical ASCII compact sorted-key JSON with schema `equity-features.intraday-catalog.v1`, package_version and these complete entries. Reject unknown/different catalog versions/digests on imported prepared metadata. Declaration of a planned ID does not imply executable capability: before its kernel ships supports_batch isFalse and invoking it is UNSUPPORTED_CAPABILITY; after qualification it becomesTrue with a changed delivered package/catalog identity. All public state flags remainFalse in R17. EQ141's delivered discovery must show all eight actually supported batch outputs.

EQ136 delivers reviewed documents and independent fixtures only. No production export, worker binding, implemented discovery, runtime measurement or installed-artifact claim is made by this specification. EQ137–141 must qualify actual implementations and their own current evidence.

## Typed rejection and preparatory operands

Use existing ContractError codes: INVALID_SCHEMA for nonconcrete/wrong-shaped records and malformed supplied BAR payload; INVALID_CONFIG for unknown context keys, noncanonical encoding, invalid mode/index/period/k/evidence settings; BOUNDS for timestamp/range/size limits; INCONSISTENT_IDENTITY for context/config/source/coverage contradictions; INVALID_UNIT or UNSUPPORTED_ADJUSTMENT for incompatible unit/action declarations; DUPLICATE and INVALID_ORDER for those actual row/grid defects; INCOMPATIBLE_VERSION for codec/catalog/algorithm version mismatch; UNKNOWN_FEATURE and UNSUPPORTED_CAPABILITY for own dispatch. OVERFLOW denotes mathematical arithmetic failure as above. No silent fallback changes requested mathematics. When several admission errors exist, report the first detected in the fixed order: configuration/context shape and versions; limits/unit/identity; supplied batch structural semantics in input order; cross-chunk grid/coverage/order; then per-cell readiness. Tests must not rely on incidental dictionary iteration for precedence.

EQ137's internal preparation includes exact rolling price count/sum/mean/population variance, target-including max(high)/min(low) over N slots, one-slot simple return C[i]/C[i-1]-1, and TR as defined in mathematics. Extrema require only their respective H or L; returns require both adjacent closes, not H/L; TR requires H/L and prior close. Their readiness/units are inherited from those exact operand slots, with positive-price denominators. These are compatible reusable operands, not extra public feature IDs or substituted return-volatility bands. The concrete immutable preparation record/signatures and its own pre-code review belong to EQ137; reuse may not hide acquisition or add cross-feature barriers. New mutable/state capabilities would require a new explicit decision and qualification, not inference from the word rolling.
