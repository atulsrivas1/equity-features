# R4.1 delivery plan

[Milestone](https://github.com/atulsrivas1/equity-features/milestone/15): repository separation and extensible I/O. Planning: [GOV-014 #275](https://github.com/atulsrivas1/equity-features/issues/275). Two epics, ten implementation stories, 60 provisional complexity points; no dates or measured velocity. All new stories are Backlog pending published design and per-story readiness.

[Architecture](IO_WORKER_ARCHITECTURE.md) is the boundary decision. R4 is accepted and unchanged; R5 is blocked by verified EQ-130. Start EQ-121 after planning publication and repository access verification, then dependency-ready work with one active implementation story. Extraction EQ-122 and contract EQ-123 may be independently prepared; parallel execution needs a documented work-limit decision.

## Open decisions assigned to implementation

EQ-121 verifies repository/package name availability and CI/platform scope. EQ-122 freezes compatibility versions, migration/deprecation and exact artifact delivery. EQ-123 specifies envelope serialization, logical digest canonicalization, capability/error taxonomy and publication traces. EQ-126/127 qualify filesystem/transaction/process guarantees. EQ-129 records supported combinations; no silent version promise. PostgreSQL is an extension example, not an initial implementation commitment. Registry publishing, remote hosting, data redistribution and private generation remain separately gated.

## Release gate

All ten stories require public numbered execution links, separate final-head review, relevant tests, same-story docs and verified actual publication. R4 receipts/import identity/semantics remain preserved. Qualify pure core installations, extracted DuckDB adapter, both sinks and independently packaged custom examples from built artifacts on declared platforms. R5 receives an explicit acceptance handoff; no worker is complete solely because the skeleton builds.

## EQ-121

[Establish companion repository and package foundations](https://github.com/atulsrivas1/equity-features/issues/278) — 5 points; epic [E18](https://github.com/atulsrivas1/equity-features/issues/276); R4.1.

**Start:** Read the current issue/Project and linked source specifications; verify dependencies ([GOV-014](https://github.com/atulsrivas1/equity-features/issues/275) publication and verified repository access), then publish the concrete implementation plan and independent expected fixtures before coding.

**Design and scope:** Create equity-feature-io and equity-feature-workers with Apache-2.0, governance, typed builds and CI. I/O contains independently installable io-contracts, SDK and implementation packages; workers starts as a skeleton. Retain numbered planning links; do not duplicate issue authorities.

**Open questions:** Resolve the relevant assigned decisions above in this story before code; unsupported backend/platform guarantees are explicit. Existing mathematics and source-admission limits are unchanged.

**Tests:** Clean wheel/sdist installs; dependency graph/import checks; no I/O dependency enters core; no worker command implemented.

**Documentation with the story:** Repository map, contribution rules, compatibility ownership and links to canonical issues.

**Done state:** Scoped behavior implemented, separately final-head reviewed, tested from applicable installed artifacts, documented, actually released and read back. Update authoritative issue/Project and release evidence; do not count planning as implementation.


## EQ-122

[Extract the accepted DuckDB adapter without changing semantics](https://github.com/atulsrivas1/equity-features/issues/279) — 8 points; epic [E18](https://github.com/atulsrivas1/equity-features/issues/276); R4.1.

**Start:** Read the current issue/Project and linked source specifications; verify dependencies ([EQ-121](https://github.com/atulsrivas1/equity-features/issues/278)), then publish the concrete implementation plan and independent expected fixtures before coding.

**Design and scope:** Move the optional equity-feature-duckdb distribution, its tests and qualification harness to the I/O repository. Keep distribution/import identities, resolver/mapping/acquisition semantics and accepted R4 limitations. Publish tested migration/deprecation procedure; retain historical R4 receipts and Git history.

**Open questions:** Resolve the relevant assigned decisions above in this story before code; unsupported backend/platform guarantees are explicit. Existing mathematics and source-admission limits are unchanged.

**Tests:** Independent R4 fixtures and installed core/adapter combinations on supported CI platforms; compare current result/provenance/error behavior; private source qualification remains separately gated.

**Documentation with the story:** Extraction inventory, migration guide, preserved R4 acceptance links and actual artifact/version evidence.

**Done state:** Scoped behavior implemented, separately final-head reviewed, tested from applicable installed artifacts, documented, actually released and read back. Update authoritative issue/Project and release evidence; do not count planning as implementation.


## EQ-123

[Freeze input and output I/O contracts and dependency ownership](https://github.com/atulsrivas1/equity-features/issues/280) — 5 points; epic [E19](https://github.com/atulsrivas1/equity-features/issues/277); R4.1.

**Start:** Read the current issue/Project and linked source specifications; verify dependencies ([EQ-121](https://github.com/atulsrivas1/equity-features/issues/278)), then publish the concrete implementation plan and independent expected fixtures before coding.

**Design and scope:** Keep existing pure acquisition protocols in equity-feature-contracts as compatibility authority. Define separate source and sink APIs in companion I/O contracts, reusing canonical inputs/results without copying schemas. Specify versioned publication envelope, receipt, identity, duplicate/conflict, visibility, abort and failure semantics before implementation.

**Open questions:** Resolve the relevant assigned decisions above in this story before code; unsupported backend/platform guarantees are explicit. Existing mathematics and source-admission limits are unchanged.

**Tests:** Hand-worked protocol traces for same-key same/different content, missing/empty values, partial failure and incompatible versions; dependency graph and schema review.

**Documentation with the story:** Normative I/O specification, capability matrix, error taxonomy and no-impact mathematical decision.

**Done state:** Scoped behavior implemented, separately final-head reviewed, tested from applicable installed artifacts, documented, actually released and read back. Update authoritative issue/Project and release evidence; do not count planning as implementation.


## EQ-124

[Implement explicit adapter and sink registration and factories](https://github.com/atulsrivas1/equity-features/issues/281) — 5 points; epic [E19](https://github.com/atulsrivas1/equity-features/issues/277); R4.1.

**Start:** Read the current issue/Project and linked source specifications; verify dependencies ([EQ-123](https://github.com/atulsrivas1/equity-features/issues/280)), then publish the concrete implementation plan and independent expected fixtures before coding.

**Design and scope:** Accept directly supplied source/sink instances or explicit per-run factory registries. Separate namespaces/config validation; verify compatibility/capabilities before acquisition or writes. No automatic plugin import/registration, unrestricted module strings, credential logging or hidden global registry.

**Open questions:** Resolve the relevant assigned decisions above in this story before code; unsupported backend/platform guarantees are explicit. Existing mathematics and source-admission limits are unchanged.

**Tests:** Externally installed custom factories, duplicate/unknown IDs, incompatible capability/schema, redacted credentials and import-side-effect checks.

**Documentation with the story:** Factory API, configuration example, trusted-local-code and remote allowlist boundaries.

**Done state:** Scoped behavior implemented, separately final-head reviewed, tested from applicable installed artifacts, documented, actually released and read back. Update authoritative issue/Project and release evidence; do not count planning as implementation.


## EQ-125

[Implement sink contracts and reusable conformance SDK](https://github.com/atulsrivas1/equity-features/issues/282) — 8 points; epic [E19](https://github.com/atulsrivas1/equity-features/issues/277); R4.1.

**Start:** Read the current issue/Project and linked source specifications; verify dependencies ([EQ-123](https://github.com/atulsrivas1/equity-features/issues/280)), then publish the concrete implementation plan and independent expected fixtures before coding.

**Design and scope:** Implement typed publication envelope/receipts, begin-write-commit-abort lifecycle and sink capabilities. Preserve values, nulls, units, quality, evidence, source/algorithm/config identities and availability. Separate retryable failure, conflict, cancellation and unsupported atomicity; no universal exactly-once promise.

**Open questions:** Resolve the relevant assigned decisions above in this story before code; unsupported backend/platform guarantees are explicit. Existing mathematics and source-admission limits are unchanged.

**Tests:** Independent fake-sink crash/retry traces, same-key digest replay, different-content conflict, evidence tamper, commit receipt mismatch, partial write/cancel and version rejection.

**Documentation with the story:** Public sink API and extension kit with guarantees per capability; conformance is not durability certification.

**Done state:** Scoped behavior implemented, separately final-head reviewed, tested from applicable installed artifacts, documented, actually released and read back. Update authoritative issue/Project and release evidence; do not count planning as implementation.


## EQ-126

[Implement immutable Parquet generation sink](https://github.com/atulsrivas1/equity-features/issues/283) — 8 points; epic [E19](https://github.com/atulsrivas1/equity-features/issues/277); R4.1.

**Start:** Read the current issue/Project and linked source specifications; verify dependencies ([EQ-125](https://github.com/atulsrivas1/equity-features/issues/282)), then publish the concrete implementation plan and independent expected fixtures before coding.

**Design and scope:** Bounded staged columnar output with explicit destination and schema/version; completion manifest last. Readers admit only committed generations. Same-key same-content replay returns original receipt; different content conflicts. Define platform/filesystem limits and cleanup ownership without deleting source data.

**Open questions:** Resolve the relevant assigned decisions above in this story before code; unsupported backend/platform guarantees are explicit. Existing mathematics and source-admission limits are unchanged.

**Tests:** Synthetic round trips preserving null/UTCns/units/evidence; process interruption at write/manifest boundaries; hash/count corruption, retries and supported concurrent writer conflicts.

**Documentation with the story:** Storage layout, completion-reader contract, filesystem assumptions, error recovery and measured resource bounds.

**Done state:** Scoped behavior implemented, separately final-head reviewed, tested from applicable installed artifacts, documented, actually released and read back. Update authoritative issue/Project and release evidence; do not count planning as implementation.


## EQ-127

[Implement transactional DuckDB result sink](https://github.com/atulsrivas1/equity-features/issues/284) — 8 points; epic [E19](https://github.com/atulsrivas1/equity-features/issues/277); R4.1.

**Start:** Read the current issue/Project and linked source specifications; verify dependencies ([EQ-125](https://github.com/atulsrivas1/equity-features/issues/282)), then publish the concrete implementation plan and independent expected fixtures before coding.

**Design and scope:** Persist standardized results and provenance in a caller-selected output database. Declare serialized/single-writer ownership, transaction boundaries, generation identities and completion receipt. Input adapter remains read-only; prohibit unsupported shared multi-process writes and implicit mutation of source stores.

**Open questions:** Resolve the relevant assigned decisions above in this story before code; unsupported backend/platform guarantees are explicit. Existing mathematics and source-admission limits are unchanged.

**Tests:** Transactional rollback/crash, same/different content retries, round trips, writer contention and read visibility on tested supported platforms; compare to independent in-memory outputs.

**Documentation with the story:** Destination schema, supported process/connection matrix and transaction/idempotency limitations.

**Done state:** Scoped behavior implemented, separately final-head reviewed, tested from applicable installed artifacts, documented, actually released and read back. Update authoritative issue/Project and release evidence; do not count planning as implementation.


## EQ-128

[Qualify third-party adapter and sink extension examples](https://github.com/atulsrivas1/equity-features/issues/285) — 5 points; epic [E19](https://github.com/atulsrivas1/equity-features/issues/277); R4.1.

**Start:** Read the current issue/Project and linked source specifications; verify dependencies ([EQ-124](https://github.com/atulsrivas1/equity-features/issues/281), [EQ-125](https://github.com/atulsrivas1/equity-features/issues/282), [EQ-126](https://github.com/atulsrivas1/equity-features/issues/283)), then publish the concrete implementation plan and independent expected fixtures before coding.

**Design and scope:** Independently packaged synthetic source and sink run through public APIs without modifications to core, I/O implementations or workers. Provide runnable source-to-calculation-to-sink composition via direct injection and validated factories; user implementations retain their own qualification responsibility.

**Open questions:** Resolve the relevant assigned decisions above in this story before code; unsupported backend/platform guarantees are explicit. Existing mathematics and source-admission limits are unchanged.

**Tests:** Fresh installed packages, typing and public conformance; unrelated dependencies absent; wrong schemas/capabilities, secrets and failure propagation rejected; no private/provider data.

**Documentation with the story:** Custom adapter/sink tutorial, protocol stubs and test instructions; do not claim remote uploaded-code safety.

**Done state:** Scoped behavior implemented, separately final-head reviewed, tested from applicable installed artifacts, documented, actually released and read back. Update authoritative issue/Project and release evidence; do not count planning as implementation.


## EQ-129

[Verify repository independence and compatibility matrix](https://github.com/atulsrivas1/equity-features/issues/286) — 5 points; epic [E18](https://github.com/atulsrivas1/equity-features/issues/276); R4.1.

**Start:** Read the current issue/Project and linked source specifications; verify dependencies ([EQ-122](https://github.com/atulsrivas1/equity-features/issues/279), [EQ-124](https://github.com/atulsrivas1/equity-features/issues/281), [EQ-126](https://github.com/atulsrivas1/equity-features/issues/283), [EQ-127](https://github.com/atulsrivas1/equity-features/issues/284), [EQ-128](https://github.com/atulsrivas1/equity-features/issues/285)), then publish the concrete implementation plan and independent expected fixtures before coding.

**Design and scope:** Core installs and calculates without I/O or worker packages. Qualify declared core/contracts/I/O/adapter/sink combinations using built artifacts and independent synthetic expected results. Keep R4 real-source limitations; rerun private checks if extraction changes source behavior. Record exact supported versions.

**Open questions:** Resolve the relevant assigned decisions above in this story before code; unsupported backend/platform guarantees are explicit. Existing mathematics and source-admission limits are unchanged.

**Tests:** Wheel/sdist clean supported-platform installs, core boundary audit, source-result-sink parity, dependency conflict/rejected combinations and artifact reproducibility checks.

**Documentation with the story:** Compatibility matrix, provenance/build evidence, migration release notes and actual limits.

**Done state:** Scoped behavior implemented, separately final-head reviewed, tested from applicable installed artifacts, documented, actually released and read back. Update authoritative issue/Project and release evidence; do not count planning as implementation.


## EQ-130

[Accept R4.1 and unblock worker implementation](https://github.com/atulsrivas1/equity-features/issues/287) — 3 points; epic [E18](https://github.com/atulsrivas1/equity-features/issues/276); R4.1.

**Start:** Read the current issue/Project and linked source specifications; verify dependencies ([EQ-129](https://github.com/atulsrivas1/equity-features/issues/286)), then publish the concrete implementation plan and independent expected fixtures before coding.

**Design and scope:** Audit all ten story gates, final-head separate reviews, CI/install artifacts and migration docs. Verify released artifacts/publication, preserved R4 history and third-party examples. Reconcile R5 issues to use shared I/O contracts; explicitly select the highest dependency-satisfied Ready worker story after acceptance.

**Open questions:** Resolve the relevant assigned decisions above in this story before code; unsupported backend/platform guarantees are explicit. Existing mathematics and source-admission limits are unchanged.

**Tests:** Evidence-linked release checklist and actual publication readback; no workers or private historical generation declared complete.

**Documentation with the story:** R4.1 acceptance, exact resume handoff and reconciled GitHub lifecycle/dependencies.

**Done state:** Scoped behavior implemented, separately final-head reviewed, tested from applicable installed artifacts, documented, actually released and read back. Update authoritative issue/Project and release evidence; do not count planning as implementation.
