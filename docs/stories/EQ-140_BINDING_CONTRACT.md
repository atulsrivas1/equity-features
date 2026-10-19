# EQ140 concrete binding and qualification proposal

Supplement to [the planning packet](EQ-140_PLAN.md), prospective choices for separate pre-code review. No worker implementation or Ready acceptance is claimed. Mathematics and pure APIs remain unchanged. EQ138/EQ139 delivery prerequisites are accepted.

## API and selection

Explicit optional module `equity_feature_workers.intraday` exports:

- `compute_intraday_inputs(task, batches)`: existing top-level Calculation callback, returns exactly `(result,)`.
- `intraday_headers(features)`: nonempty concrete unique selected ID tuple, validated against the public own catalog, returning sorted Float64/schema1 FeatureHeaders with actual units/algorithm.
- `required_intraday_inputs(config, features)`: existing InputRequirement records with exact independent selected-field/lookback rules.
- `intraday_history(config, features)`: returns `(ordered_history, warmup_sessions, initialization_sha256)` for existing TaskManifest construction.

Core-only module `equity_feature_workers.supplied_session` exports analogous `compute_supplied_session_inputs`, `supplied_headers(family)`, `required_supplied_inputs(config, family)`, and `supplied_history(config, family, inputs, governed_sessions)`. Families are exactly `structure`, `top_k`, `continuous_quotes`, `bars_prior_close`. Each returns the complete fixed accepted producer selection. No callback factory, new registry, serialized task schema, root export or default acquisition command is added. Existing WorkItem and TaskManifest remain the execution boundary. Each callback validates directly; bypassing a discovery/history helper cannot bypass admission.

Intraday config decoding uses only accepted public context deserialization/config construction. Validate exact closed parameter names, contiguous bounded chunks, schema/hash, reduced band fraction, period/evidence bounds, and equality with public build_intraday_config reconstructed from the decoded context. No imports from private producer modules. Call prepare_intraday once for the selected operand-family union and compute_intraday with that exact compatible preparation inside the worker. Return the original complete result unchanged.

## Exact supplied inputs

All operations require one instrument matching every admitted row and target entity; validate full source metadata, namespace, kind, coverage/row count, original batch order and exact nonmissing binding bijection. Unique source IDs are mandatory. Manifest metadata is never substituted for actual batch metadata.

Intraday has exactly three forms:

1. Actual chunks: task.inputs consists only of nonmissing compact roles bars:000 through bars:NNN in actual supplied tuple order; no gaps, duplicates, extra missing markers or mixed roles. Match every actual batch exactly once. Actual empty batches retain their bindings.
2. Absent delivery: no batches and exactly one state-missing InputManifest with role bars, no binding/known-at. Pass None to the pure API.
3. Observed empty delivery: no batches and no manifests. Pass the actual empty tuple. This remains distinct from an actual empty canonical chunk.

Core supplied operations require primary roles bars/trades/quotes respectively. The task declares that slot exactly once, either a real binding or an explicit missing marker. Primary actual rows are always the first actual batch. Structure/top-K permit no auxiliary slot. Bars/prior-close always declares a prior_close slot, actual or missing. Continuous seed mode always declares quote_seed, actual or missing; inactive/unknown modes forbid the seed slot. Actual batches follow the declared primary-then-auxiliary order with missing slots filtered out. Task input declarations use that same fixed order. Missing primary with a real admitted auxiliary is valid and preserves the original pure result/metadata; it does not fabricate primary availability. An empty observed source requires a real empty canonical batch.

Quote seed must be exactly one real target-session preopen continuous update; preserve actual source/event/known-at/max-age and original causal expiry. Prior close must be one real DAILY row of the immediately preceding config.window governed session; its actual scope/row interval must agree with that actual governed IntervalSpec and end by target open. Accepted pure unit/action/availability and identity validation remains authoritative. Future or unknown auxiliary knowledge is normal quality exclusion when the pure API says so; structurally wrong source/kind/session/scope rejects.

## History and initialization

Intraday sets ordered_history=True and initialization_sha256=context.digest. Its selected dependency closure starts at anchor_index if any EMA/RSI/ATR is selected; band-only selection starts at max(anchor_index,target_index-period+1). Include unique actual prior-session IDs touched by those slots through target, in governed order, excluding the target session. Keep every actual governed session and exact bounds in TaskManifest; warmup does not relabel/remove supplied history.

Structure/top-K set ordered_history=False, warmup=(), initialization=None. Continuous sets ordered_history=True and warmup=(): its seed belongs to the target session. Bars/prior-close sets ordered_history=True and warmup=(actual predecessor ID,) only when that actual nonmissing reference binding is supplied; an absent reference gives (). This is causal auxiliary ownership, not incremental/checkpoint support.

For the two ordered core modes, initialization is SHA256 of `b"efworker-supplied-init1\0" + canonical_json(payload)`. Payload has exactly family, config_digest, governed_sessions and inputs. governed_sessions is the actual ordered list of [name,start_ns,end_ns]. inputs is the declared ordered list of complete dataclasses.asdict(InputManifest) records, including acquisition/revision/state/known-at and full actual binding metadata. JSON uses ASCII, sorted keys, separators(',',':'), allow_nan=False, with existing string-enum values. Hash no job/partition clock and no executable object; no new protocol is serialized. Recompute and compare inside the callback; do not insert controls into strict core math parameters. Task reuse still binds its existing complete config/input/history identity.

## Closed diagnostics

Canonical ContractError member mapping is exhaustive: INCONSISTENT_IDENTITY→CommandError.RESULT; OVERFLOW→CommandError.CALCULATION; INVALID_SCHEMA, UNKNOWN_FEATURE, UNSUPPORTED_CAPABILITY, INVALID_ORDER, DUPLICATE, INVALID_UNIT, BOUNDS, INVALID_CONFIG, INCOMPATIBLE_VERSION, UNSUPPORTED_SAMPLING, UNSUPPORTED_ADJUSTMENT→CommandError.CONFIG. Use actual enum members, not their symbolic spellings as wire values. Result/header/backend/history mismatch is RESULT; actual resource admission is LIMIT; unexpected faults are CALCULATION. Raise the exact existing recognized CommandError, suppressing private exception payloads.

For directly handled ManifestError: LIMIT→CommandError.LIMIT, BINDING→RESULT, INVALID/VERSION/UNSUPPORTED→CONFIG. Normal missing/partial/unknown/future quality stays a result rather than an exception. No new error enum or global fallback relaxation is selected.

## Receipt-aware publication bound

Necessary additive worker companion change: extend existing PublicationLimits with optional `max_receipt_wire_bytes: int | None = None`, validated1..1048576 when supplied. Default None preserves legacy behavior. This is the byte length of the entire escaped ASCII JSON string representing encode_receipt(receipt), including surrounding quotes, as embedded by encode_output; it is not raw receipt bytes or a bar count.

When supplied, SerialPublisher._submit computes the exact existing receipt-free OutputManifest bytes and requires `len(encoded_output_without_receipt)-4+max_receipt_wire_bytes <= 1048576` before queue mutation or sink I/O.4 is the replaced JSON null. This permits conservative receipt headroom without a fabricated receipt or producer rerun. Existing byte/resident/queue limits still apply independently. Qualified new-operation examples use an explicit bound400000 bytes and the admitted fixture/sink shape; document its trusted caller/sink obligation rather than claiming an arbitrary sink is bounded by its current generic capabilities.

After actual commit, check the actual escaped receipt contribution against that bound and retain exact output validation. A sink violating its declared bound produces RESOURCE_LIMIT and retains the pending task for explicit actual lookup/readback/reconciliation; never claim rollback or absent commit. Existing publisher/barrier waiting semantics already distinguish unverified publication from confirmed absence. Document this limitation and test the actual commit/lookup state. No general receipt schema migration, codec widening, discarded identity or new scheduler is selected. Whether the returned committed declaration should be retained in an additional recovery object is a separate design choice only if tests show existing pending/lookup semantics insufficient; do not introduce it silently.

## Independent expected boundary matrix

The original seven profiles have now passed83 installed pure-API/SDK assertions and separate reproduction plus39 additional metadata/quality/evidence checks. Initial helper-only backend field/expected-name mistakes were corrected against the actual public ResultMetadata/API; no formula, fixture value or tolerance changed. This is pre-code fixture evidence, not worker execution. Preserve original fixture specification and exact input/result/metadata identities.

Additional original expected cases to construct during qualification:

| Trigger | Independent expected result/admission |
| --- | --- |
| Intraday close-only history, N closes, all groups selected | Ready EMA/bands remain available; H/L-dependent ATR alone is missing/unready |
| Missing target close with admitted prior closes/current H/L | ATR may remain available; current-close outputs alone fail readiness |
| Old gap outside last-N window, inside recurrence epoch | Bands ready; affected EMA/RSI/ATR quality follows its actual closure |
| Required last-N gap / future / unknown close | Only consuming outputs carry exact accepted gap/knowledge reason; metadata/evidence unchanged |
| None / empty tuple / real complete0/0 chunk | Three distinct pure API admission/quality/input-binding outcomes, matched without rewriting |
| Bad digest/chunk/selection/header/aux kind/session/unit/action/scope | Exact closed CONFIG or RESULT class according to validation stage; no publication |
| Missing prior close | Ten bar outputs unchanged; overnight/close-close missing_input/absent_input; no fabricated binding |
| Prior close with future/unknown known-at | Prior-dependent outputs retain accepted exclusion reason; independent ten unchanged |
| Seed absent in seed mode, first update after open | Initial unknown duration, typed table retained, means null/incomplete; no fabricated seed |
| Seed future/unknown, first update at open | Excluded seed evidence retained; no positive unknown duration, ready accepted quote output |
| All locked valid quotes / no valid positive duration | Available zero spread / not_applicable zero-denominator respectively; preserve structured durations |
| Duplicate/unmatched/shifted batches or missing-marker mixtures | RESULT for actual identity disagreement; CONFIG for malformed role/declaration shape |
| Receipt-free fit but conservative final bound exceeds cap | RESOURCE_LIMIT before sink I/O; no partial commit |
| Actual sink receipt exceeds declared bound after commit | RESOURCE_LIMIT/waiting with pending task; actual sink lookup remains committed, no rollback claim |
| Sequence/thread/process on identical task set | Exact SDK full-result digest, values/nulls/status/quality/evidence/identity and publication readback parity |

Freeze all exact enum/reason/header/evidence expectations from accepted original math/specification before changing an implementation to satisfy a failing check. Do not make the optimized callback its own only oracle.

## Frozen comparison protocol proposal

Original synthetic all-eight N20/evidence0 workloads: small1×256 slots, balanced16×1024, skewed15×256 plus1×1024. Use identical symbol IDs/config/full source metadata and actual contexts in all modes. Validate actual bytes with the explicit400000 receipt contribution bound and all independent defaults before timing; a preflight failure returns the packet to review rather than silently resizing after observing alternatives. Qualification budgets: max_tasks16, input16MiB, resident1GiB subject to min(1GiB,25%initialfree), per-task result262144, task transport1048576, total result16MiB; publisher pending16 tasks/8MiB; I/O1, native/backend1, compute_threads1. Record actual logical reservations, they are not physical enforcement.

Degree set is1,2,4,8, clipped before measurement to actual allowed CPU/affinity minus the one backend slot and supported worker<=32/in-flight<=workers. Record omitted degrees/reasons; do not allocate all nominal cores blindly. No synthetic per-feature task splitting. Compare sequential A to thread/process B at each admitted degree and workload. Retain direct whole-result reference separately; comparing direct and worker costs is descriptive, not a fabricated scheduler speedup.

For each mode/profile:2 warmups,7 retained samples, no concurrent heavy build/review/timing. Finish all A samples and freeze their SHA256/noise/resource table before any B timing. Adoption requires full result/diagnostic/commit/readback parity, median wall improvement strictly above max(5%,3*inclusive-IQR(A)/median(A)), aggregate core-seconds<=1.25A, peak aggregate sampled RSS<=min(1GiB,25%initialfree) and<=1.25A. Small-case p95 must be<=1.10A; use the same nearest-rank convention explicitly in the harness. No default mode/autoselector change follows automatically; retain every loser/failure and sequential fallback.

Measure compute-only and synthetic supplied-source-to-publication/readback separately. Full E2E includes source decode/construction, task admission/preparation/copies/IPC/queues, all result serialization/validation and actual fixture sink commit/readback. The fixture sink is in-memory; no physical durability/provider/live claim. A separate physical supplied-source/sink smoke may reuse accepted I/O adapters when its actual package/version/scope is recorded; it is not silently part of an in-memory benchmark. Record cold process/import/startup cost separately from repeated fresh-pool calls; there is no persistent/warm worker pool.

For Windows complete process-tree CPU, select an owned Job Object with the benchmark runner created suspended, assigned before resume, automatic child membership/no breakaway, retained native handles and final basic accounting after all owned descendants exit. Use total user+kernel100ns counters; actual membership/count/exit validation and error controls are mandatory before timing. [Microsoft accounting definition](https://learn.microsoft.com/en-us/windows/win32/api/winnt/ns-winnt-jobobject_basic_accounting_information) includes terminated member CPU; [assignment rules](https://learn.microsoft.com/en-us/windows/win32/api/jobapi2/nf-jobapi2-assignprocesstojobobject) define child membership. This selects a benchmark accounting method, not production scheduling/limits. Fail the measurement if complete accounting cannot be established. Linux correctness/installed acceptance remains mandatory; no Linux speed claim is selected by a Windows measurement.

Retain sampled parent+child RSS/probe errors/interval/missed-short-process limits independently from job CPU; do not confuse peak private commit or sum of per-process lifetime maxima with simultaneous peak RSS. Record encoded/pickled byte counts, observed queue/calculation/serialization/publication probes and end-to-end wall; do not subtract probe durations to manufacture exclusive stages. Primary documentation informs the method, it is not evidence that the future harness has executed correctly.

## Documentation and acceptance

Worker own API/discovery/examples, extra/install/optional-absence matrix, typed diagnostics, history/receipt/resource decision and changelog/test/build/continuity accompany the necessary companion. Preserve default dispatcher/root/source independence/core39. I/O contracts/SDK remain pinned absent an actual demonstrated incompatibility; actual installed codec/publication tests justify that no-impact decision, not this proposal alone. Qualify new modules and additive PublicationLimits on both operating systems with independent legacy/absence/strict/source/archive/artifact controls and actual final heads.

Publish/read back reviewed companion and canonical documentation, then complete actual main checks/artifacts/separate final acceptance and the exact lifecycle. Current draft requires a complete separate review of these prospective choices, current source pins and original boundary expectations before Ready. Permission is not completed review; this proposal does not advance Project status.
