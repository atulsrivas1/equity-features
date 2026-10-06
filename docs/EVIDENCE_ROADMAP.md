# Evidence and agent research roadmap

Planning authority: [GOV-012](https://github.com/atulsrivas1/equity-features/issues/192). Owner-requested additional scope, October 5, 2026. Implementation stories are Backlog; live Project owns status. Points are provisional complexity, not elapsed time. No due dates or package versions are promised.

## Boundaries and delivery order

Existing typed quality/evidence, input identities, exact representations where specified and supplied point-in-time membership admission are foundations, not complete research audit trails. Calculations retain no file/network/database/credential access. Evidence persistence/replay and agent recording are separate optional packages; MCP stays in the existing service layer. Retained evidence is bounded, with explicit references and truncation indicators.

R0–R8 assignments remain intact. R9 needs R3, but does not require R8 acceleration; real-source examples additionally need admitted R4/R6 adapters. R10 follows R9. R11 follows R9/R10 and existing R7 for MCP/hosted integration. Default release order remains unchanged; dependency-ready independent work requires later owner authorization. This planning does not take ownership from R2 or resume paused R3.

## Releases

| Release | Epic | Stories | Points |
| --- | --- | --- | --- |
| [R9](https://github.com/atulsrivas1/equity-features/milestone/10) — Reproducible calculation evidence | [E13](https://github.com/atulsrivas1/equity-features/issues/193) | EQ-096–EQ-100 | 31 |
| [R10](https://github.com/atulsrivas1/equity-features/milestone/11) — Point-in-time diagnostics | [E14](https://github.com/atulsrivas1/equity-features/issues/194) | EQ-101–EQ-105 | 31 |
| [R11](https://github.com/atulsrivas1/equity-features/milestone/12) — Agent research evidence | [E15](https://github.com/atulsrivas1/equity-features/issues/195) | EQ-106–EQ-110 | 31 |

## Story plans

| Story | Points | Dependencies | Accepted capability |
| --- | --- | --- | --- |
| [EQ-096](https://github.com/atulsrivas1/equity-features/issues/196) — Specify execution receipts and evidence boundaries | 5 | EQ-013, EQ-039, EQ-044, EQ-048 | Versioned receipt binds formula/config, input content identity, availability, backend/environment and output identity; distinguish metadata digest from content hash and calculation evidence from agent evidence. |
| [EQ-097](https://github.com/atulsrivas1/equity-features/issues/197) — Implement deterministic input and output content fingerprints | 8 | EQ-096 | Hash supported typed content including units, nulls, ordering and UTC nanoseconds; reject unsupported values; document floating representation and copy/stream costs; never claim source truth. |
| [EQ-098](https://github.com/atulsrivas1/equity-features/issues/198) — Build portable reproduction bundles and replay verification | 8 | EQ-096, EQ-097, EQ-045 | Separate I/O package exports manifest, supplied input artifacts or immutable references, configs, package versions and results; replay verifies identity then parity with declared tolerance; no executable-object deserialization. |
| [EQ-099](https://github.com/atulsrivas1/equity-features/issues/199) — Expose bounded calculation explanations and evidence references | 5 | EQ-096, EQ-013, EQ-036 | Explain formula/version, admitted inputs, cutoffs, coverage and exclusions with typed findings and bounded summaries; distinguish omitted retained evidence from missing proof; complete evidence lives outside kernels. |
| [EQ-100](https://github.com/atulsrivas1/equity-features/issues/200) — Qualify reproducible evidence release and public examples | 5 | EQ-096–EQ-099, EQ-048 | Installed public APIs reproduce synthetic calculations and reject tampered bundles; record measured overhead, compatibility, threat model and release acceptance without provider certification. |
| [EQ-101](https://github.com/atulsrivas1/equity-features/issues/201) — Specify leakage findings and admissibility policy | 5 | EQ-096, EQ-033, EQ-037 | Define separate future market data, late/unknown knowledge, reconstruction, stale membership, revised data and incompatible adjustment findings; report pass/fail/unknown only for declared checks, no universal safety score. |
| [EQ-102](https://github.com/atulsrivas1/equity-features/issues/202) — Implement membership and revision leakage diagnostics | 8 | EQ-101, EQ-033, EQ-036 | Validate supplied effective/known-at membership and revision/action snapshots; reject current-only membership offered as historical proof; unknown evidence remains explicit; adapters acquire facts. |
| [EQ-103](https://github.com/atulsrivas1/equity-features/issues/203) — Bind adapter and worker provenance to evidence receipts | 5 | EQ-097, EQ-101, EQ-053, EQ-057, EQ-061 | Reuse existing acquisition/task/output manifests, link immutable content identities and availability claims to receipts, retain gaps and revisions; no duplicate catalog or source admission by file presence. |
| [EQ-104](https://github.com/atulsrivas1/equity-features/issues/204) — Create adversarial point-in-time conformance suite | 8 | EQ-101–EQ-103, EQ-037, EQ-043 | Reusable external suite detects declared leaks and preserves unknowns using synthetic contaminated/clean pairs; future-data invariance and current-versus-historical universe scenarios; no universal detector claim. |
| [EQ-105](https://github.com/atulsrivas1/equity-features/issues/205) — Qualify point-in-time diagnostics and consumer guidance | 5 | EQ-101–EQ-104, EQ-100 | Publish installed examples, coverage matrix, evidence prerequisites, false-positive/unknown limits and acceptance receipt; qualify bounded runtime with result parity. |
| [EQ-106](https://github.com/atulsrivas1/equity-features/issues/206) — Define agent decision events and authority boundaries | 5 | EQ-096, EQ-101 | Separate orchestration schema records trigger/request, supplied model identity, tool arguments/results, receipt refs, timestamps, actor, approval and outcome; no hidden chain-of-thought requirement; exclude secrets and private data by default. |
| [EQ-107](https://github.com/atulsrivas1/equity-features/issues/207) — Implement optional tamper-evident event ledger | 8 | EQ-106, EQ-097 | External persistence package uses canonical event hashes, sequence and prior hash; supports verification, crash recovery and exported anchors; distinguish alteration detection from authenticity, correctness and unanchored truncation. |
| [EQ-108](https://github.com/atulsrivas1/equity-features/issues/208) — Extend existing MCP tools with evidence and diagnostics | 8 | EQ-082, EQ-099, EQ-105, EQ-106; hosted deployments also EQ-075–EQ-080 | Extend one existing MCP server with receipt/explanation/diagnostic tools, bounded artifacts, explicit quality and supported capabilities; authorization and cancellation; no uploaded executable feature code. |
| [EQ-109](https://github.com/atulsrivas1/equity-features/issues/209) — Publish agent research integration and replay examples | 5 | EQ-098, EQ-107, EQ-108 | Synthetic external consumer records a research request, calculated evidence, diagnostics and agent action references, then independently replays calculation and checks ledger; no profitability claims or provider secrets. |
| [EQ-110](https://github.com/atulsrivas1/equity-features/issues/210) — Qualify agent evidence release and positioning limits | 5 | EQ-106–EQ-109, EQ-100, EQ-105, EQ-084 for hosted scope | Release receipt covers service threat model, access isolation, replay, ledger limits, compatibility and examples; messaging states reproducible evidence and declared checks, not compliance certification or unique-market claims. |

### EQ-096 — Specify execution receipts and evidence boundaries

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Versioned receipt binds formula/config, input content identity, availability, backend/environment and output identity; distinguish metadata digest from content hash and calculation evidence from agent evidence.

Open questions: Canonical representations, privacy-safe references and optional field rules.

Tests: Independent canonicalization/hash fixtures, schema evolution and malformed receipt cases.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-097 — Implement deterministic input and output content fingerprints

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Hash supported typed content including units, nulls, ordering and UTC nanoseconds; reject unsupported values; document floating representation and copy/stream costs; never claim source truth.

Open questions: Canonical Arrow representation versus logical encoding and supported extensions.

Tests: Independent known hashes, one-value/null/unit/order mutation, exact timestamps, bounded-memory measurements.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-098 — Build portable reproduction bundles and replay verification

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Separate I/O package exports manifest, supplied input artifacts or immutable references, configs, package versions and results; replay verifies identity then parity with declared tolerance; no executable-object deserialization.

Open questions: Embedded versus referenced data, licensing, retention and cross-platform tolerance.

Tests: Fresh-install synthetic round trip, changed/unavailable input, incompatible version, malformed archive and resource bounds.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-099 — Expose bounded calculation explanations and evidence references

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Explain formula/version, admitted inputs, cutoffs, coverage and exclusions with typed findings and bounded summaries; distinguish omitted retained evidence from missing proof; complete evidence lives outside kernels.

Open questions: Explanation schema and evidence reference lifetime.

Tests: Truncation, zero evidence limit, missing/empty/partial input, consistent values/metadata and exclusion boundaries.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-100 — Qualify reproducible evidence release and public examples

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Installed public APIs reproduce synthetic calculations and reject tampered bundles; record measured overhead, compatibility, threat model and release acceptance without provider certification.

Open questions: Retention defaults and unsupported reconstruction guarantees.

Tests: Independent end-to-end replay, clean wheel/sdist installations and supported-platform gates.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-101 — Specify leakage findings and admissibility policy

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Define separate future market data, late/unknown knowledge, reconstruction, stale membership, revised data and incompatible adjustment findings; report pass/fail/unknown only for declared checks, no universal safety score.

Open questions: Severity, strict admission versus advisory diagnostics and trusted timestamp assumptions.

Tests: Hand-derived time-boundary and known-at fixtures with expected findings.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-102 — Implement membership and revision leakage diagnostics

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Validate supplied effective/known-at membership and revision/action snapshots; reject current-only membership offered as historical proof; unknown evidence remains explicit; adapters acquire facts.

Open questions: Provider evidence completeness and correction identity.

Tests: Delisted constituents, index additions, late revisions, missing known-at and half-open boundary fixtures.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-103 — Bind adapter and worker provenance to evidence receipts

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Reuse existing acquisition/task/output manifests, link immutable content identities and availability claims to receipts, retain gaps and revisions; no duplicate catalog or source admission by file presence.

Open questions: Cross-provider identity, retained provider evidence and manifest compatibility.

Tests: Synthetic DuckDB acquisition-to-receipt chain, changed partition, resumed generation and missing provenance rejection.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-104 — Create adversarial point-in-time conformance suite

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Reusable external suite detects declared leaks and preserves unknowns using synthetic contaminated/clean pairs; future-data invariance and current-versus-historical universe scenarios; no universal detector claim.

Open questions: Supported attack classes and residual unobservable contamination.

Tests: Independent expected results, negative controls, unknown cases and public adapter integration.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-105 — Qualify point-in-time diagnostics and consumer guidance

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Publish installed examples, coverage matrix, evidence prerequisites, false-positive/unknown limits and acceptance receipt; qualify bounded runtime with result parity.

Open questions: Minimum evidence for each advertised check.

Tests: Clean installs, documented examples, migration and end-to-end adversarial checks.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-106 — Define agent decision events and authority boundaries

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Separate orchestration schema records trigger/request, supplied model identity, tool arguments/results, receipt refs, timestamps, actor, approval and outcome; no hidden chain-of-thought requirement; exclude secrets and private data by default.

Open questions: Retention, redaction versus replay, actor authentication and event-clock trust.

Tests: Schema/reference validation, redaction, missing supplied identity and cancellation/error events.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-107 — Implement optional tamper-evident event ledger

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. External persistence package uses canonical event hashes, sequence and prior hash; supports verification, crash recovery and exported anchors; distinguish alteration detection from authenticity, correctness and unanchored truncation.

Open questions: Storage backend, anchor ownership, signing/key management and deletion policy.

Tests: Alter/reorder/remove event, anchored truncation, concurrent writer, crash recovery and redaction policy tests.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-108 — Extend existing MCP tools with evidence and diagnostics

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Extend one existing MCP server with receipt/explanation/diagnostic tools, bounded artifacts, explicit quality and supported capabilities; authorization and cancellation; no uploaded executable feature code.

Open questions: Local versus hosted support, artifact expiry and protocol version at implementation.

Tests: Real MCP client integration, schema discovery, incomplete/unknown outputs, unauthorized access, oversized request and cancellation.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-109 — Publish agent research integration and replay examples

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Synthetic external consumer records a research request, calculated evidence, diagnostics and agent action references, then independently replays calculation and checks ledger; no profitability claims or provider secrets.

Open questions: Supported agent framework selection and stable optional dependencies.

Tests: Fresh consumer install, wrong narrative versus actual result, fallback behavior and missing evidence scenarios.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

### EQ-110 — Qualify agent evidence release and positioning limits

First actions/design: read dependency contracts and delivery receipts, publish the pre-code plan, resolve the questions below, freeze schema and independent expected cases, then implement a minimal public API example. Release receipt covers service threat model, access isolation, replay, ledger limits, compatibility and examples; messaging states reproducible evidence and declared checks, not compliance certification or unique-market claims.

Open questions: Local/hosted release scope and future independent security assessment.

Tests: Installed artifacts, MCP end-to-end, tamper/replay/isolation failure tests and supported-platform checks.

Documentation: update relevant public API/schema, synthetic installed examples, compatibility/rights/security limits, story acceptance and delivery evidence, and session continuity alongside implementation.

End state: the named capability is qualified through the agreed lifecycle and published-source/artifact verification. Planning and source merge alone do not establish Done.

## Existing stories reused

EQ-053 owns adapter acquisition provenance; EQ-057/061 own worker manifests/output generations; EQ-082 owns base MCP discovery/query/jobs. EQ-103/108 add evidence linkage and evidence-aware tools, without duplicating those owners. EQ-033 supplies membership/action admission; diagnostics do not discover historical facts. R3 EQ-093/095 remain the custom-feature/consumer extension work.

## Claims and security limits

Content hashes identify supplied bytes/values, not data truth. Replay needs retained or resolvable licensed inputs. Ledger chains detect alterations relative to trustworthy retained anchors; they do not establish authenticity or prevent unanchored truncation. Point-in-time checks cover declared evidence and preserve unknowns, not all leakage or model-training contamination. Missing proof is never relabeled passed. No hidden chain-of-thought capture, executable uploads, source/data rights assumption, profitability promise, regulatory certification or market-exclusivity claim. Public examples remain synthetic/licensed. A compliance product would require separately scoped legal, retention and operational assessment.

## Corrected agent ledger detail

[Agent evidence design](AGENT_EVIDENCE_DESIGN.md) refines EQ-096/097/101/102/106/107 with content hashes, simulated cutoffs, matching membership, explicit freshness and anchored truncation checks. R11 remains the ledger/service release. Continuous-market work is separate [E16/R12 scope](CONTINUOUS_MARKET_DESIGN.md), using new IDs EQ-111–115.
