# EQ140 supplied-input worker qualification

Planning draft for [EQ140 #474](https://github.com/atulsrivas1/equity-features/issues/474), [E25](https://github.com/atulsrivas1/equity-features/issues/465), R17. This packet is incomplete preparation, not Ready or implemented behavior. Live Project remains status authority. EQ138 is accepted; EQ139 is published on main but still awaits its final main-channel acceptance. Finish that dependency and the unresolved gates below before pulling this story.

## Scope and pinned contracts

Qualify all eight batch intraday outputs and the four original supplied-input dispatcher gaps: structure, top-K trades, continuous quotes with optional seed, and bars with optional prior close. Call their accepted pure APIs without new mathematics, acquisition or metadata rewriting. Intraday update/restore/merge remain unsupported. Original core39 and contracts/core0.0.4a4 remain unchanged.

Inspection sources: canonical b1f5445eb9799b73753e413669b94166997fc468 (intraday0.1.0a3), workers a69ae9cfeb62730fc78705b4752b94c6f9438275 (0.1.0a13), I/O18d86761aa3eebb7414e51e8fa2aba089717b5eb (contracts/SDK0.1.0a2). Recheck public heads and relevant deltas before implementation. Earlier direct measurement remains bound to its original source and does not prove worker performance.

Proposed worker delivery is0.1.0a14 with an exact optional intraday0.1.0a3 extra. Keep root imports lightweight, default acquisition/command dispatch unchanged and optional dependencies absent in the base environment. Existing service/client/MCP require an explicit tested no-impact decision; their pins are not changed merely because a worker extra exists. Necessary companion PRs link this canonical story. Preserve unrelated workerPR42 and I/O PR15/16 ownership.

## Proposed public operations

Use two explicitly imported top-level callbacks matching existing `Calculation(task, batches) -> tuple[FeatureResult, ...]`: an optional intraday operation and a supplied-core session operation. Names and module locations must be frozen after affected-caller review. Each call returns exactly one complete combined FeatureResult in the existing outer tuple. Its complete header tuple must equal task.features; never split or filter a fixed producer result after calculation.

Existing WorkItem rejects closures and callable instances. Any convenience factory must return an actual TaskManifest/WorkItem and reference a top-level callback; it must not return a closure or introduce a serialized schema. Prepare intraday inputs once inside the computing process; prepared objects and callbacks are not uploaded or sent as an unbound context side channel. Use existing bounded supervisor/publication contracts rather than a new scheduler.

Intraday config is decoded from its accepted closed context chunks and checked against its digest. Build sorted Float64 headers from the public intraday catalog; do not force intraday IDs through the closed core registry. Existing core operations return their exact accepted headers:

| Operation | Actual supplied inputs | Independent readiness |
| --- | --- | --- |
| Intraday | Ordered BAR chunks or declared absence | EMA/RSI consume their actual seed and recurrence; ATR consumes H/L plus prior close; each band consumes only its selected last-N closes |
| Structure | BAR bars | Interval-local OHLCV and whole-session volume-share denominators stay distinct |
| Top-K | TRADE trades | Eligibility and exact stable size/event/order ties; accepted K/evidence bounds |
| Continuous quotes | Continuous QUOTE quotes and optional quote_seed | Accepted max-age, normal/locked/crossed/inactive/unknown duration rules; sampled inputs are unsupported |
| Bars/prior close | BAR bars and optional DAILY prior_close | Missing reference affects only overnight/close-close outputs; independent bar outputs remain available |

Use existing InputRequirement fields role/schema_id/fields/kind/sampling/rule for discovery. Describe actual parameter-bound lookback, causal availability and absence semantics per selected output. Required fields are availability requirements, not a ban on normal missing/null/empty deliveries. Do not make H/L a global close-only prerequisite or add artificial feature-to-feature edges.

## Input and history identity

Operation admission must enforce exact actual-batch/nonmissing-manifest bijection; supervisor subset checking alone is insufficient. Validate original order, actual kind/source/full metadata and compact intraday bars:000 roles over supplied chunks. Explicit missing declarations do not shift actual role numbering. No chunks with a missing declaration means absent input; no manifests means observed empty delivery; an actual empty canonical batch retains its binding. Complete0/0 alone supports state empty; partial zero rows remains partial.

Freeze missing-marker role, multiplicity and mixed actual/missing rejection rules before Ready. Never repair input/result roles or truncate metadata to satisfy output admission. Canonical ResultMetadata already sorts unique bindings by role; this is not a defect and does not define chunk execution order.

Intraday initialization uses the actual decoded context digest, exact sessions/grid/target/anchor/config and selected prerequisite closure. Warmup IDs must be actual prior unique governed sessions consumed by that closure. Reset/unused old intervals must not manufacture warmup. A band-only closure can consume fewer sessions than a recursive group; no one-session-per-bar placeholder is allowed.

A quote seed is a real preopen update labelled with the target session, not an invented prior-session warmup. Prior close is one real DAILY row from the immediately preceding governed session; its actual interval ends by target open and matches the accepted source/unit/action/availability contract. Freeze recomputable initialization digests, ordered_history choices and exact auxiliary scope checks before Ready. Core configs reject extra parameters: transport/initialization controls must not be inserted into their math parameters.

## Errors and unsupported requirements

Freeze exhaustive mappings against actual exception classes. Proposed canonical ContractError mapping: INCONSISTENT_IDENTITY to RESULT_IDENTITY_MISMATCH; OVERFLOW to CALCULATION_FAILED; remaining eleven closed errors to INVALID_COMMAND. Actual worker/codec byte and reservation admission produces RESOURCE_LIMIT; unexpected faults produce CALCULATION_FAILED. Use recognized exact CommandError classes rather than assuming arbitrary exception codes survive supervisor translation. Missing data normally yields the accepted quality result rather than an exception. No private exception text in diagnostics.

ManifestError requires its own explicit mapping and negative tests. Unsupported supplied shapes must be described honestly; they must not hide an admitted existing pure capability allocated by this story.

## Actual installed byte preflight

Original synthetic all-eight inputs used actual qualified canonical wheels and installed pinned workers/SDK. Direct result SDK roundtrip and task/output identity passed at all five sizes. A second preflight used the existing synthetic MemorySink fixture: SDK publish, real fixture commit, lookup, readback and idempotent replay passed. It then encoded the actual receipt-bearing OutputManifest. This is in-memory fixture publication, not durable physical storage, worker execution, a benchmark or release acceptance.

| Slots in this fixture | SDK result bytes | Task bytes | Output without receipt | Output with committed receipt | Committed output encoder |
| --- | ---: | ---: | ---: | ---: | --- |
|256|71383|60133|146416|220309|passed|
|1024|247340|225337|555156|838794|passed|
|1536|366124|336953|830612|1255562|RESOURCE_LIMIT|
|2048|484908|448569|1106068|1672330|RESOURCE_LIMIT|
|4096|960044|895033|2207892|3339402|RESOURCE_LIMIT|

The fixed manifest cap is1,048,576 bytes. Oversized lengths are independently constructed exact closed-wire sizing only; the actual encoder rejected them. For passing cases these lengths equal the real encoded bytes. The earlier receipt-free1536 pass does not establish final publication admissibility. No universal slot maximum follows: identity lengths, chunks, context, evidence and sink artifact references change actual bytes. Keep original preflight and the superseding committed result distinct.

Do not widen defaults, remove actual history/bindings or silently create another codec. Admission must account for receipt-bearing wire limits and bounded sink receipt requirements before claiming completion. Freeze how the supported sink's receipt size is bounded and how oversized final output is reported without falsely reporting rollback of an already committed sink. Direct4096 support remains a separate pure-library capability. Test result-cap, task-cap, transport/resident and fixed-codec rejection independently.

## Original fixtures and validation

[Original hand-derived fixture specification](EQ-140_ORIGINAL_FIXTURES.json) retains seven profiles. It is an unexecuted mathematical specification, not worker evidence: distinct actual notional versus close-weighted proxy; supplied/absent prior close; interval-local OHLCV with incomplete global share denominator; Top-K eligible size/tie ordering; causal quote expiry; unknown initial duration with retained typed table/null averages; and inactive initialization. Complete actual canonical construction, expected quality/evidence/metadata and independent assertions before implementation acceptance.

Also qualify each intraday selection and representative all-eight result for full OHLC, close-only, missing target close with ready ATR, old gap outside a band window with unready recursive output, required gaps, unknown/future known-at, None/empty deliveries, multiple chunks, reset/carry sessions and corrected replay. Direct full-result equality is necessary but not the sole numerical oracle. Compare sequential/thread/process and SDK publication/readback without rewriting backend/version or metadata.

Negative cases cover exact header/backend/source identity, duplicate/unmatched/misordered/shifted bindings, malformed context chunks and digest, auxiliary kind/session/scope/unit/action/cutoff, codecs/resource boundaries, pool/sink/cancellation and partial-commit diagnostic truth. Preserve legacy/default dispatcher and optional-absence controls.

## Resource and performance protocol to freeze

Use actual encoded sizes to select supported small, balanced many-symbol and skewed workloads.256 and1024-slot fixture results are feasibility examples, not yet frozen performance workloads or a general supported limit. Group compatible outputs per symbol and preserve ordered recurrence; avoid one task per scalar. The existing scheduler serializes intersecting instruments and publishes only after the pool completes. No same-symbol parallelism, early-symbol publication, persistent pool or live-latency claim follows.

Qualification must count actual source, task construction/admission, preparation, copies/serialization/IPC, queue, result admission and sink commit/readback. Separate cold-start and repeated fresh-pool measurements; do not label a new pool persistent/warm. Bound worker degree by actual permitted CPU/affinity, workers<=32, in-flight<=workers, compute/native/I/O thread budget and measured aggregate memory. Initial memory ceiling is min(1GiB,25%initial free), with explicit logical reservations distinguished from observations and physical enforcement.

Before observing alternatives, freeze workloads, warmups/repeats, sequential baselines, IQR-based noise margins, low-latency/resource/adoption bounds, complete parent/child CPU accounting and sampled aggregate-memory limitations. Retain nonwins/failures and the supported sequential/direct fallback. Existing RSS/pickle-only benchmark tools do not prove complete core-seconds or this new E2E workload. No performance result or selected faster default is claimed by this draft.

## Remaining Ready and delivery gates

1. Accepted EQ139 main-channel delivery, fresh repository/caller pins and complete separate review of this packet.
2. Exact public names/factories, missing-marker rules, selected closure/warmup/init digests, exhaustive errors and receipt-bound admission decisions.
3. Runnable original fixture construction with independent quality/evidence/identity expectations; frozen resource/performance protocol and complete CPU accounting method.
4. Linked worker draft plan/branch and canonical documentation, without taking unrelated PR ownership. Only then Ready and actual assigned In progress.

Same-story API/discovery/examples, optional install/dependency matrix, decision/errors/limits/changelog/test/release documentation and no-impact decisions accompany code. Separate final-head review, current candidate and actual main CI, fresh Windows/Linux installed forms/artifacts/optional absence, exact source/archive identity, real channel publication/readback and final acceptance precede Released/Done. EQ141 audits the complete R17 set. R18 handoff/execution follows verified R17; no R18 implementation is started here.
