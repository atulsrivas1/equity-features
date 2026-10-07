# R4.1 independent compatibility and publication test strategy

Prepared with [execution handoff](R4_1_AUTONOMOUS_HANDOFF.md),
[story plans](R4_1_DELIVERY_PLAN.md) and
[architecture](IO_WORKER_ARCHITECTURE.md). This is a required matrix, not executed
test evidence. Each implementation story freezes its concrete expected fixtures,
supported configurations and actual result counts before code.

| Gate / stories | Independent expected behavior | Acceptance evidence |
| --- | --- | --- |
| Repository/build boundary, EQ-121/129 | Core installs/calculates with I/O and worker packages absent/forbidden; only inward contract dependencies. Backend packages install independently; workers remains a skeleton. | Actual supported-platform wheel/sdist builds, dependency/import audit, clean installations and component-version matrix. |
| DuckDB extraction, EQ-122/129 | Accepted resolver/mapping/acquisition fixtures retain identities, units, UTCns, nulls, coverage, errors, sampling and source availability. Original input stores remain read-only. | Compare standalone installed implementation against frozen accepted R4 expected results and documented compatibility. Relevant private checks rerun when behavior changes; archive/source/runtime/golden bindings preserved. |
| Contract traces, EQ-123/125 | Missing, observed-empty and unavailable differ; every values/quality/evidence component is bound. Same-key same logical content returns original receipt; different content conflicts. Unsupported capability/version fails explicitly. | Hand-worked lifecycle/failure traces and golden serialization/digest cases independent of implementation; reviewer checks invariants before code. |
| Factory/configuration, EQ-124/128 | Direct instances and explicit registries compose identically. Duplicate/unknown IDs, bad config/capability/version fail before I/O; no import-time registration or credential disclosure. | Independently packaged custom factories/source/sink, installed typing, redacted errors, negative capabilities and side-effect probes. Local trusted code is not represented as a sandbox. |
| Sink content, EQ-125/126/127 | Independent source -> calculation expected result -> sink -> readback preserves exact integer/ns/scaled representation, float tolerances, null masks, statuses, units, algorithm/config/source/availability and all evidence. | Small synthetic goldens with independently expected values and readback checks; mutations to one field/table/hash/count/identity must be detected. No mirrored serializer-only assertions. |
| Parquet visibility, EQ-126 | Staged/partial output cannot be admitted as complete. Completion manifest binds all components; readers reject missing/corrupted receipts. Same content retry is idempotent; different content under same key conflicts. | Controlled process interruption before/after component writes and completion boundary; supported filesystem concurrent writer tests, cleanup ownership and bounded resource evidence. Do not assume directory rename is universally atomic. |
| DuckDB transaction/writers, EQ-127 | Rollback prevents incomplete committed generation; read visibility and completion receipt are consistent. Writer topology is declared/serialized; unsupported multi-process sharing is rejected. Input adapter cannot become an implicit source-store writer. | Transaction/crash/retry/commit-uncertainty/status lookup tests, contention, independent content readback and tested connection/process/OS matrix. No universal exactly-once claim. |
| Installed extension composition, EQ-128/129 | External packages use only public interfaces without modifying core/SDK/backends. Direct/factory paths retain result parity and truthful failures. | Fresh supported-platform installs, external imports/typing/conformance, explicit supported versions and absence of private/provider data. |
| Migration/release, EQ-122/129/130 | Old public import/distribution identities remain compatible within recorded policy; current implementation authority moves with explicit links. Historical R4 evidence is retained. | Migration guide, compatibility/deprecation decision, all contributing final-head reviews/CI, actual experimental artifact publication, hashes/install/readback and ten canonical Done records. |

## Fault and identity matrix

At minimum cover interrupted writes, crash before commit, crash after commit with
lost response, retry receipt lookup, same/different content duplicates, cancellation
before and after commitment, conflicting writers, wrong config/schema/algorithm,
missing evidence, altered counts/content, unavailable/null versus zero, empty
observed results, opaque source/known-at gaps and version incompatibility. Keep
task-claim and catalog behavior in R5; a sink test does not establish worker resume.
Storage backend guarantees are scoped to actual qualified deployment assumptions.

## Measurements and source limits

Measure relevant resource bounds with actual workload, rows/batch, copy/conversion,
thread and platform evidence when claiming bounded throughput/memory behavior.
No performance improvement is assumed from repository separation. Use synthetic
fixtures by default; provider truth, entitlements and historical causal completeness
require separate source evidence. Native public CI and private installed execution
retain their distinct platform provenance. Conformance/round trips are not private
full-corpus validation, regulatory certification or backend durability proof.

## Release evidence

For every contributing component, record reviewed head, actual published source,
CI run, build/archive identities, clean install method, expected fixture identity,
executed outcomes and limits. Verify after publication, reconcile canonical issue/
Project states and link evidence in R4.1 acceptance. Reuse unchanged evidence only
with actual relevant code/artifact/fixture equality; new installed packaging needs
its own provenance. Do not create repetitive tests solely to increase counts.
