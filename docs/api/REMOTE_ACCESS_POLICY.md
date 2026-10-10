# R7 remote access and entitlement policy

Draft for [EQ075 #85](https://github.com/atulsrivas1/equity-features/issues/85), [PR356](https://github.com/atulsrivas1/equity-features/pull/356), October 9, 2026. This defines requirements before external exposure; no service, authentication implementation, hosted dataset or deployment is delivered by this document. Acceptance and enforcement evidence remain separate. See the [pre-code plan](../stories/EQ-075_PLAN.md), [architecture](../IO_WORKER_ARCHITECTURE.md) and [R6 scope decision](../decisions/R6_SCOPE_CLOSURE.md).

## Users and trust boundary

The initial qualification population consists of explicit test users and service identities operating owned synthetic fixtures. Two distinct principals are required for isolation tests. An operator must separately approve real identities, datasets and deployment before external access. No anonymous data access, self-issued grants or automatic public registration is admitted. Service identities have the same scoped rights and accounting obligations as human users.

Authentication establishes a server-verified opaque principal; it does not establish dataset rights. The server owns identity mapping, grants, dataset catalog, approved adapter/sink IDs and configurations. Client requests may select approved logical IDs and supported filters only. They cannot supply SQL, filesystem paths, arbitrary destinations, imports, executable callables or serialized Python objects. The calculation packages remain source-independent; authentication, fetching, scheduling and publication stay outside them.

Transport must protect authentication secrets and data. If bearer tokens are selected, possession confers their authority: protect storage and transport, use the authorization header, and never place tokens in URLs, logs or artifacts. TLS is required for external access. Authentication mechanism, issuer, token validation and wire errors are implementation decisions requiring their own tests in EQ076/077; this policy does not claim an OAuth deployment. [RFC6750](https://www.rfc-editor.org/rfc/rfc6750) supplies bearer-token semantics; implementation must use current security guidance rather than historical TLS examples.

## Dataset admission and rights

Every admitted dataset has a server-owned identifier, immutable revision/snapshot, normalization/mapping revision, source provenance, permitted instrument/session/time scope, and documented rights evidence with an owner and validity interval. Rights are separate for raw reads, calculation, derived-result reads, export/redistribution, and retained or cached copies. A grant cannot exceed these dataset rights. A code license, installed adapter, credential or local computation permission is insufficient evidence for hosted distribution.

| Candidate | Current remote admission decision | Evidence needed before changing the decision |
| --- | --- | --- |
| Owned synthetic fixtures | Eligible for bounded qualification after explicit catalog admission and test grants | Ownership/provenance, immutable fixture revision and exact permitted operations |
| Existing local files or databases | Not admitted by their local acceptance | Owner approval and applicable raw/derived/retention/export rights for the exact hosted use |
| Databento or Massive inputs | Not admitted | Relevant deferred provider acceptance plus explicit dataset rights, account entitlement and cost/download approval |
| Unknown source or revision | Deny | Complete source, revision, scope and rights evidence |

No provider or private-data exposure is authorized by starting R7. Deferred EQ069/070/072/074 remain Backlog with future release assignment pending. Numerical coverage, known-at and C/K/E facts must remain supplied facts. Permission cannot convert unknown coverage into completeness, future knowledge into causal availability, or incompatible units/populations/sessions into valid inputs.

## Operations and authorization

Logical operations are metadata discovery, raw slice, calculation submission, owned job status/cancellation, derived-result read and artifact export. Discover permission is required even for catalog metadata; job identifiers reveal nothing to a foreign principal. Status/cancellation use the original owner's still-active job-management grant. Raw and derived reads require their respective rights; export additionally requires redistribution rights. Cache/result persistence requires retention rights. Rights may be combined only when each independently covers the operation.

An authorization decision permits a request only when all of the following hold: authenticated principal; active server grant and current policy revision; admitted immutable dataset revision; request scope contained in both dataset rights and grant; all required action rights; valid numerical admission; and available principal/global budgets. Unknown or unavailable information denies. Validity uses a trusted server clock and half-open intervals `[valid_from, expires_at)`; equality at expiry denies. Revoked grants deny immediately at the next authorization boundary.

Pin principal, grant and policy revisions, dataset/snapshot/mapping, algorithm and feature versions, full calculation configuration, selected instruments/sessions/time windows, availability mode and approved source/sink into command identity. The server validates requests against current rights as well as their pinned reproducibility inputs. Identity hashes cannot replace rights checks.

Reauthorize at admission, start of execution, each input/output chunk boundary, result publication and every subsequent fetch. Revocation or expiry prevents further visible output and cache/result retrieval; partial unpublished output is not returned. Already committed worker receipts remain historical facts, and accepted writer/foreign-completion semantics remain intact. Implementations must make authorization and visibility/reservation updates atomic against concurrent revocation; cooperative chunk checks alone do not prove this property. Stop and cleanup behavior requires actual race/cancellation tests in EQ078–080.

Idempotency is scoped to principal plus a client key and exact command identity. Repeating an accepted identical command returns its original job identity without scheduling duplicate work. Reusing the key with changed scope/configuration fails. A foreign principal cannot discover or reuse that receipt. Every request attempt still consumes request-rate budget; actual execution and transferred bytes are accounted once per occurrence.

## Initial bounded qualification profile

These exact inclusive maxima constrain small synthetic qualification. They are policy choices, not measured throughput, memory isolation or a production SLO. Wider limits require a recorded policy revision and capacity/security qualification before admission; an operator may tighten limits. Failure to configure finite limits denies service startup.

| Dimension | Per principal | Whole service |
| --- | --- | --- |
| Request attempts in a fixed server interval `[t, t+60 seconds)` | 60 | 60 |
| Request body bytes | 16,384 per request | Same per-request cap |
| Total normalized input rows | 100 per job across all input roles | Same per-job cap |
| Instruments / sessions / features | 1 / 1 / 39 per job | Same per-job caps |
| Input bytes / produced result bytes | 1,048,576 / 1,048,576 per job | Same per-job caps |
| Running jobs / queued jobs | 1 / 1 | 1 / 2 |
| Result or slice response bytes | 262,144 per response/chunk | Same per-response cap |
| Retained result/cache bytes | 1,048,576 total | 2,097,152 total |
| Transferred response bytes in the same fixed 60-second interval | 1,048,576 total | 2,097,152 total |
| Wall time | 30 seconds per job | Same per-job deadline |
| Result/cache lifetime | At most 300 seconds and grant expiry, whichever is earlier | Same expiry rule |

The 39-feature cap admits only actually supported registered features and valid dependency inputs, never arbitrary functions. Separate process memory/CPU limits, isolation, queue fairness and hard deadline enforcement must be specified and verified before hosted qualification in EQ080/084. The logical byte/row caps do not establish RSS limits; small inputs do not prove bounded CPU. No claim of hard preemption follows from cooperative worker cancellation.

Shared accounting covers all controllers/instances, retries, failures, partial work, cache hits and downloads. Reserve scarce queue, retained/output and transfer capacity atomically before work or visibility; settle actual usage without freeing already consumed rate/transfer allowance. Requests whose required reservation exceeds a remaining budget deny before execution. Streaming stops before the next chunk would exceed the cap. A fresh controller cannot reset a principal's or global interval allowance. At the next interval, new transfer/request allowance may begin; existing queued/running jobs and retained storage remain accounted until their actual release. Wall-time intervals and policy expiry do not use client clocks.

## Cache, retention and audit

Partition cache/result visibility by principal, grant/rights revision, policy revision and full reproducibility identity. A cache hit still requires current authorization and transfer budget. Shared computational deduplication must not expose another principal's job, metadata or results; it is outside initial qualification unless separately proven safe. Grant revocation blocks fetch immediately; expiry denies even when physical cleanup has not run. Cached raw and derived material require their corresponding retention rights.

Results expire no later than the configured TTL or grant expiry. The operator must specify a finite cleanup schedule and retention for backing stores, audit records and backups before deployment, and prove cleanup/recovery behavior in EQ079/084. Logical expiry is not proof of physical deletion. Audit retention requires its own documented rights and operational approval; no indefinite storage is implied here.

Audit records contain only an opaque principal reference, request/command identifier, policy/grant revision, action, decision code and accounting totals needed to diagnose enforcement. No credentials, payload rows, raw private paths or arbitrary user strings. Audit/log consumers are separately authorized. Error/status responses preserve transport and mathematical error categories without revealing foreign dataset/job existence, internal paths or secrets; their exact schema is EQ076. Timing and resource side channels need explicit evaluation before external exposure.

## Independent decision vectors

These expected outcomes precede enforcement. They are requirements for later executed adversarial tests, not evidence of tested endpoints. Each allow case assumes all unmentioned predicates above pass.

| Case | Expected result |
| --- | --- |
| Explicit synthetic admission, active owner grant, supported bounded calculation | Allow |
| Anonymous identity or unverifiable identity/clock | Deny |
| Principal B queries principal A's job/result | Deny without revealing its existence |
| Missing dataset, immutable revision, feature or requested-scope permission | Deny |
| At grant expiry or after revocation | Deny, including cache/result fetch |
| Derived-read/export grant attempts raw slice/export | Deny raw access |
| Raw-read grant lacks required export or retention right | Deny that export/persistence |
| Working provider credentials but no hosted rights/admission | Deny |
| Count/byte reservation exactly at available inclusive maximum | Allow subject to every other limit |
| Reservation one unit above any cap or remaining allowance | Deny before work/visibility |
| Fresh controller, failed retry or cache hit attempts to reset cumulative allowance | Deny the excess |
| Identical owner idempotency key and exact command | Return original authorized identity; no duplicate execution |
| Same key with changed command or different principal | Conflict for owner change; no foreign receipt reuse |
| SQL, path, import or uploaded callable outside approved logical contract | Reject before component construction |
| Valid rights with unknown coverage or future known-at | Preserve numerical unknown/causal admission outcome; no fabricated value |
| Concurrent revocation during publication or fetch | No newly unauthorized visible output; receipt history retained |

## Delivery boundaries

EQ075 defines permissions, users, operations and limits. EQ076 defines lossless schemas/errors/versioning; EQ077 enforces authentication and bounded slices; EQ078 jobs; EQ079 scoped delivery/expiry; EQ080 quotas/cache/audit; EQ081 optional client; EQ082 MCP; EQ083 end-to-end reproducibility/resilience; EQ084 actual approved hosted operations, load/security/rollback/backup/recovery. All ten acceptance criteria remain in R7. Accepted local worker/file behavior is a prerequisite, not remote-service proof.

Before EQ075 Done, require separate final-head semantic review, documentation/planning checks, applicable CI and guarded publication/readback linked on the story. Before any actual external exposure, require real dataset/identity/operational admission and executed downstream acceptance. The author has not claimed any of those runtime or deployment gates passed in this draft.
