## EQ080 staged header callback contract — development candidate

Service header callback is trusted staging, not protected body visibility. Reentrant Service calls or previously prepared iterator emission inside it are explicitly rejected with fixed reentrant_header_callback before new protected work/audit mutation. Closing an abandoned prepared iterator is permitted. Renew current authority after callback and final diagnostic encoding before the one protected chunk. If authority/clock/accounting fails after headers were staged, body is aborted to empty; staged status/length may describe an incomplete response. A consumer must reject truncated/absent result data. No status replacement or durable/hosted guarantee. Pre-header credential retirement returns401 authentication. Current same-story review/WinLinux installed release qualification remains pending.

## EQ080 internal audit development checkpoint

Optional service.a3 can explicitly admit an owned synthetic finite audit store through Ledger(audit=...). It reserves HTTP/native diagnostic slots before protected work and records fixed redacted outcomes, with a separately provisioned exact-object reader. No remote audit operation or transport/calculation/worker/I/O change. This internal candidate remains In progress, not a qualified public deployment; mandatory guarded entry/cache/all32/current installed/release qualification remains pending.

## EQ080 bootstrap foundation candidate

Optional service0.1.0a3 defers native graph initialization until explicit public access, preserving existing exports. [Current implementation and remaining isolation gates](../R7_QUOTA_CACHE_AUDIT.md) records121 editable Windows tests/strict7, approved pre-code and actual start. Supervisor/cache/audit runtime and physical/installed/release qualification remain pending. Prior EQ079 is accepted6097119023; older pending captures below are history.

## R7 data-only transport design

[Remote transport](REMOTE_TRANSPORT.md) defines lossless versioned JSON envelopes outside calculations. [Access policy](REMOTE_ACCESS_POLICY.md) and downstream authentication/native-conversion/authorization qualification remain required. The schema/reference verifier is a design deliverable, not an installed remote service/client or permission to deserialize executable Python objects.

# Current experimental public API

EQ039 documents matching core pair0.0.4a4 and independently packaged consumer0.3.0. The delivered inventory is39 builtin batch IDs,23 session update/restore IDs and22 conditional merge IDs. All16 history/context/breadth R2 IDs remain batch-only; continuous quote merge is unsupported. Custom execution supports explicit canonical batch requests only. Read actual capabilities rather than inferring modes from a module name. This guide's consistency does not establish a stable API, broad platform promise or registry publication. [Compatibility](../COMPATIBILITY.md), [registry](../contracts/REGISTRY.md), [incremental matrix](INCREMENTAL.md).

## Imports and ownership

`equity_feature_contracts` exports owned input/spec/result/error/validation/discovery/context types through its `__all__`. `equity_features` root exposes versions only; calculators are explicit family-module imports. Public protocol/SDK/optional backend modules below are imported explicitly; internal names beginning with an underscore are implementation details. Examples, tools and tests are repository resources, not shipped core modules. Separate consumer imports come from its own installed distribution.

| Public entry point | Supplied facts and output | Contract and mathematics |
| --- | --- | --- |
| `equity_feature_contracts`: CanonicalBatch, Column, schema_for, BatchMetadata, SourceBinding, Coverage, PriceUnit, InputScope | Exact concrete canonical columns and source declarations | [Inputs](../contracts/INPUTS.md) |
| `equity_feature_contracts`: SessionSpec, IntervalSpec, WindowSpec, AvailabilitySpec, ConfigSpec, Parameter | Caller-owned calendars, C/K/E, parameter/config identity | [Specifications](../contracts/SPECS.md) |
| `equity_feature_contracts`: FeatureResult, FeatureColumn, EntityKey, QualityRow, Status, Reason, ResultMetadata, InputBinding, EvidenceRow and structured cells | Keyed values, per-feature readiness, bounded original evidence | [Results](../contracts/RESULTS.md) |
| `equity_feature_contracts`: validate_batch, require_compatible_inputs, checked_int64/decimal128/product/sum, normalize_batch, quantize_float_prices | Typed admission and explicit materializing normalization reports | [Validation](../contracts/VALIDATION.md) |
| `equity_feature_contracts`: builtin_registry, Registry, FeatureDefinition, InputRequirement, OutputField, Capabilities; `equity_features.registry` inward convenience | Immutable metadata discovery; no automatic execution | [Registry](../contracts/REGISTRY.md) |
| `equity_feature_contracts.columnar`: from_arrow/to_arrow, from_numpy/to_numpy, to_arrow_result | Optional explicit materializing backend bridges | [Inputs/copy semantics](../contracts/INPUTS.md), [results](../contracts/RESULTS.md) |
| `equity_feature_contracts.adapters`: AcquisitionRequest, AdapterCapabilities, AdapterBatch, Cancellation, HistoricalAdapter, LiveAdapter, require_adapter_capability, validate_delivery, SourceError/SourceErrorCode | External acquisition protocols and finite supplied-envelope validation | [Adapters](../contracts/ADAPTERS.md) |
| `equity_feature_contracts.adapter_kit`: ConformanceCase, ConformanceOutcome, ConformanceReport, run_conformance | Pure named finite delivery/error checks; does not invoke sources | [SDK](../contracts/ADAPTER_KIT.md) |
| `equity_features.session`: compute_bars, compute_structure | Canonical bars plus explicit config/entity/prior; FeatureResult | [Bars](SESSION_BARS.md), [structure](SESSION_STRUCTURE.md) |
| `equity_features.session`: compute_trades, compute_top_k | Canonical trades; exact aggregates or bounded original ranked rows | [Trades](SESSION_TRADES.md), [top K](SESSION_TOP_K.md) |
| `equity_features.session`: compute_quotes, compute_time_weighted | Explicit sampled/continuous quotes and optional seed | [Event summaries](SESSION_QUOTES.md), [continuous](CONTINUOUS_QUOTES.md) |
| `equity_features.incremental.SessionAccumulator`; `equity_features.merging.merge_partitions` | Explicit family/population/config, ordinal updates, prefix snapshot/finalize, owned export/restore; conditional partition certificates | [Incremental](INCREMENTAL.md) |
| `equity_features.policies`: admit_action_policy, apply_action_policy, admit_classification | Supplied reference facts/policy; explicit admissions/application | [Timing and adjustments](../features/TIMING_ADJUSTMENT_POLICY.md) |
| `equity_features.history`: compute_history, compute_sma_reference; contracts HistoryContext/SMAReference | Governed DAILY slots, explicit anchor and config; requested history results/exact companion | [History](HISTORY.md), [frozen formulas](../features/HISTORICAL_FORMULAS.md) |
| `equity_features.volume`: compute_daily_baseline, compute_relative_volume; contracts VolumeBaseline/TargetVolume | Prior-only exact baseline and separately supplied target | [Daily volume](DAILY_VOLUME.md) |
| `equity_features.buckets`: compute_interval_baseline, compute_interval_relative_volume; contracts VolumeBucket/BucketContext/IntervalBaseline/BucketVolume | Explicit historical bucket coverage and comparable target | [Interval volume](INTERVAL_VOLUME.md) |
| `equity_features.relative.compute_relative`; contracts ReturnReference/RelativeSpec/SectorBenchmark | Supplied symbol/benchmark results and explicit membership | [Relative returns](RELATIVE_RETURNS.md) |
| `equity_features.breadth`: compute_direction_breadth, compute_above_sma_breadth; contracts DeclaredUniverseSpec/CompletedClose/SMAInput/MemberFeatures/BreadthSpec/BreadthResult/MemberExclusion | Supplied universe/member facts; independent eligible/expected coverage | [Breadth](DECLARED_BREADTH.md) |
| `equity_features.composition.compose_features`; contracts CompositionSpec/FamilyResult/FeatureBundle | Ordered supplied result instances with config/context/companion; never executes dependencies | [Composition](FEATURE_COMPOSITION.md) |
| `equity_features.custom`: CustomDefinition, CustomInput, CustomRequest, BatchCalculator, CustomRegistration, CustomRegistry | Explicit immutable trusted local registration and one-column batch execution | [Custom API](CUSTOM_FEATURES.md), [extension guide](EXTENSIONS.md) |

Public result fields remain typed unions: inspect dtype/status and handle null before scalar arithmetic. Optional backend objects are intentionally `Any` at their bridge and are runtime-admitted; static typing alone cannot prove exact cell precision, enum value/semantic validity, OHLC consistency, C/K/E or source truth. Signed int64 UTCns and integer scaled-price coefficients must never pass through float timestamps. Canonical schema1, algorithm/config/result/state versions are distinct identities; exact experimental restore requirements remain in [incremental](INCREMENTAL.md), with the actual [version and replay policy](../VERSIONING.md).

## Invalid calls versus unavailable calculations

`ContractError(ValueError)` has an `ErrorCode` member in `.code`; use the code, not exception text, for behavior. Programmer/schema/identity errors raise; valid absent/incomplete/insufficient data normally returns explicit null and quality. Never replace unavailable null with zero or suppress failure as an available calculation.

| ErrorCode | Invalid condition |
| --- | --- |
| INVALID_SCHEMA | Malformed typed/serialized representation, cell/schema or structured result |
| UNKNOWN_FEATURE | Missing discovery or execution ID |
| UNSUPPORTED_CAPABILITY | Requested execution mode is not implemented |
| INVALID_ORDER, DUPLICATE | Noncanonical ordering, repeated keys/IDs |
| INVALID_UNIT | Incompatible exact price/unit declarations |
| BOUNDS, OVERFLOW | Invalid configured bounds or checked integer accumulation |
| INCONSISTENT_IDENTITY | Contradictory namespace/config/source/provenance/companion binding |
| INVALID_CONFIG | Invalid parameter/configuration/admission policy |
| INCOMPATIBLE_VERSION | Unsupported contract/math/state/algorithm identity |
| UNSUPPORTED_SAMPLING, UNSUPPORTED_ADJUSTMENT | Unqualified sampling or adjustment semantics |

External acquisition uses `SourceError(ValueError)`/SourceErrorCode: UNSUPPORTED, AUTHENTICATION, ENTITLEMENT, RATE_LIMIT, TRANSPORT, SCHEMA, UNAVAILABLE, CANCELLED and LIMIT. The synthetic adapter translates its owned contract failures to safe SCHEMA and preserves the cause. Captured error codes in the pure SDK classify supplied facts, not prove provider events. Trusted custom callback exceptions propagate unchanged. Callers decide retry/logging outside core and keep credentials out of public messages.

Status.AVAILABLE requires the admitted nonnull value and appropriate complete coverage. INSUFFICIENT_HISTORY, MISSING_INPUT, INCOMPLETE_COVERAGE and NOT_APPLICABLE retain typed reasons; structured breadth/quote/table exceptions preserve explicit diagnostic cells as documented in results. Quality is independent for each feature/entity; one missing quote does not erase a ready trade count. ResultMetadata binds config digest, C/K/E, source/snapshot/mapping/input identities and actual implementation. Digests identify declarations, not authenticate source truth or certify mathematical correctness.

## Installed typing qualification

Both core distributions and the external consumer contain py.typed. [Typed caller](../../examples/typed_caller.py) spans public batch/history/composition/custom/SDK/discovery/results/errors. [Installed verifier](../../tools/verify_public_typing.py) rejects editable/source imports, checks installed markers/exports, type-checks caller and actual installed consumer with pinnedmypy, and independently requires wrong ConfigSpec/PriceUnit/ConformanceCase calls to produce three argument-type diagnostics. Static checks do not replace the619unit tests or independent mathematical fixtures.

Each fresh wheel/sdist pair in [build delivery](../BUILD_DELIVERY.md) runs these checks after installing the separately built consumer. Development mypy may also check the source, but only actual clean installation qualifies a delivered artifact. Reproduction and command topology are in [extensions](EXTENSIONS.md); EQ040/EQ095 retain their broader example/consumer gates.
