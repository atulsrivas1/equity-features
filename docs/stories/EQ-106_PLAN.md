# EQ106 — agent event contracts and authority boundaries

Pre-code preparation, October15,2026. [Story206](https://github.com/atulsrivas1/equity-features/issues/206), [handoff](../R11_AUTONOMOUS_HANDOFF.md), [release plan](../R11_RELEASE_PLAN.md), [test strategy](../R11_TEST_STRATEGY.md). Five provisional complexity points. The owner selected R11; this design draft is not a Ready decision, implemented API or acceptance.

## First actions and allocation

Read accepted EQ096 receipt/content contracts, EQ101 diagnostic time/authority rules and the corrected AGENT_EVIDENCE_DESIGN. Verify actual196/201ClosedDone and governance packet publication, inspect relevant callers and prepare one small synthetic public consumer. Freeze exact package/dependency/domain/API/schema/limits, literal independent oracle and negative cases before runtime Ready. Existing `ResultMetadata`, feature/calculation versions, R9 content domains and R10 diagnostics are not redefined.

Proposed pure canonical package: `equity-feature-agent-evidence`, import `equity_feature_agent_evidence`, experimental0.1.0a1, Python3.12/Apache-2.0. Dependencies point inward to accepted pure evidence/contracts only; decide exact required imports and pins in the completed packet. Numerical kernels must not import agent evidence. External SQLite ledger belongs to EQ107, worker MCP extension to EQ108, synthetic orchestration/replay to EQ109. No filesystem, clock, environment, network, credential, model, database, scheduling or publication operation belongs in EQ106.

## Record and authority decisions

Specify immutable closed records with exact built-in scalar validation and copied concrete sequences. Separate a recording envelope (chain ID, schema/canonicalization, positive sequence, unique namespaced event ID, previous hash) from a kind-specific immutable event subject. Proposed supported kinds are request/trigger, model declaration, tool call/result, feature read, decision, human review, cancellation/error and correction. Freeze exact tags/required fields and reference relation types; do not accept an extensible metadata/payload mapping or arbitrary serialized model object.

Each subject records only declared public/synthetic bounded values or explicit content/receipt references and disclosure state. A caller-supplied actor/model identity is not authenticated. Missing identity remains unavailable. Human approval is an explicitly supplied record, never inferred from a model label or a successful tool result. Do not record hidden chain-of-thought. Fixed public error codes/messages must not echo payloads, secrets, file paths or original exception context.

Use separate supplied occurred/executed UTCns, recording sequence and optional simulated C/K/E. All integer domains must be exact, with bool rejected and signed int64 validation before arithmetic; define nonnegative count/sequence bounds separately. Occurrence time may decrease between recorded events; sequence orders recording only. Optional clock source/uncertainty remain declarations and require the associated supplied timestamp. No clock read or timestamp inference inside pure contracts.

Feature evidence binds an actual accepted receipt reference and full typed input/config/output content identities where retained. Metadata identity alone is insufficient. Explicit evidence states distinguish retained, unavailable, redacted, truncated and not supplied; freeze each state's exact count/reference constraints. A reference declaration is not content verification or proof of source consumption. Corrections append a new subject referencing an earlier retained record and preserve the original; do not silently mutate, remove or mark a chain cryptographically complete after forgetting data.

## Canonical mathematics and fixture gate

Proposed event digest is `SHA256(canonical_event_bytes)`. The canonical object includes a fixed event domain, schema/canonicalization identifier, chain/sequence/predecessor and every typed subject field; the event digest is excluded from its own preimage. The first record's predecessor uses one literal documented genesis value, not an absent wildcard. The chain ID and version must be bound on every event. Specify exact ASCII JSON token representation, Unicode preservation/control/surrogate rules, optional nulls, key ordering, array ordering and integer grammar before selecting final identifiers. Existing content fingerprint domains are not reused for new event subjects.

Freeze literal byte, string, subject collection, depth and node limits, lexical preflight before JSON allocation, aggregate construction/encoding budgets, error precedence and typed versus decoded parity. These are application limits, not physical memory/CPU quotas. No runtime constructor, parser or hashing helper may precede this settled schema/oracle and separate review.

Hand-author at least one minimal canonical event and a linked two-event continuation before production implementation; compute byte length/node count/SHA256 independently over literal fixture bytes. Include one-field mutation expectations for each identity/time/disclosure/reference dimension. Do not generate the expected golden through the implementation being tested. EQ106 may implement bounded in-memory event/link verification, but full persisted global uniqueness/recovery/indexing and checkpoint export remain EQ107.

Internal consistency verifies only the supplied records and context. A shortened valid prefix can remain internally consistent. Expected terminal head/count are explicit trusted external assertions; genesis or a self-declared head is not independent anchoring. Missing earlier reference context is not proof of a valid reference. As-of reconstruction requires an explicit supported prefix/context; arbitrary filtering breaks linkage.

## Decisions still required before Ready

1. Exact kind tags, subject keys/types, public functions, error codes, schema/canonicalization/domain identifiers and package dependency pins.
2. Literal scalar/collection/byte/depth/node limits, canonical bytes and independent fixture digests.
3. Required versus optional actor/model/time/reference/disclosure fields, cross-kind prior-reference rules and bounded continuation context.
4. Exact privacy/retention/redaction/migration policy and supported public example; no secret-detection or historical-authenticity guarantee.
5. Complete independent cases, pure import boundary, owned source/fresh installed wheel-sdist Windows/Linux qualification design and same-story documentation map.
6. Supported separate R11 review route and exact pre-code Ready approval. The previous R10 local-review grant does not establish this decision.

## Accepted end state

Qualified optional pure event contracts with literal canonical/hash fixtures, kind/reference/time/privacy validation, independently passing final source/tests, public typed examples/API/compatibility/security/rights documentation, current installed/source artifacts on both OS, guarded publication, independent actual-main readback and actual Released/Done acceptance. No ledger persistence, new MCP endpoint, model execution, authentication, source-truth or compliance certification is claimed by EQ106. Subsequent stories retain their own readiness gates.
