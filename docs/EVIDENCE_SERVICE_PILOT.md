# Evidence service pilot — low-priority future planning

Epic [E17](https://github.com/atulsrivas1/equity-features/issues/221); [R13](https://github.com/atulsrivas1/equity-features/milestone/14). EQ-116–120, all Backlog with priority:low. Planning authorized by owner; implementation, outreach, repository creation and deployment are not. No due dates or production commitment.

## Purpose and sequencing

Demonstrate whether financial calculation evidence helps developers detect research mistakes and reproduce results compared with ordinary structured logs. Reuse R9 execution receipts/replay, R10 diagnostics and R11 events/ledger/examples. This is a consumer composition/validation effort, not a second ledger or blockchain. Core releases and existing owners keep priority. R13 is future optional scope; later execution requires dependency-ready status and explicit owner prioritization.

First a minimal synthetic workflow, then controlled usefulness evaluation. Freeze expected results, baseline and success/overhead thresholds before collecting evidence. Report uncertainty and contrary outcomes. Independent witness design/implementation follows demonstrated cross-party trust need and owner go decision, not the existence of a hash chain. No private data or unapproved participant outreach.

## Story plans

### [EQ-116](https://github.com/atulsrivas1/equity-features/issues/222) — Build a focused agent evidence pilot using existing packages

5 provisional points. Dependencies: EQ-098, EQ-105, EQ-106, EQ-107, EQ-109; relevant prior release acceptance.

First actions/design: First define paired scenarios and baseline logs, freeze independently expected findings and task measurements, then implement a minimal local orchestration example.

Acceptance/end state: Compose existing APIs into one synthetic research workflow: record request/tool/result/decision, expose deliberate future-data contamination and narrative/result mismatch, export and replay in a fresh environment. Compare with the same workflow using ordinary structured logs. No competing ledger, acquisition framework or hosted production service.

Tests: Fresh-install replay, clean/contaminated controls, agent claims versus actual execution, missing artifacts and bounded traces; pin identical data/calculations for both comparison arms.

Open questions: Which developer tasks and minimum pilot scope? Freeze evaluation criteria before measuring.

Documentation: protocol/API and synthetic examples where changed, evaluation/limits, delivery evidence and session continuity accompany the story.

### [EQ-117](https://github.com/atulsrivas1/equity-features/issues/223) — Evaluate developer usefulness and record a go/no-go decision

3 provisional points. Dependencies: EQ-116.

First actions/design: Prepare task instructions/metrics, run controlled internal assessment, gather consented external feedback if separately authorized, report supporting and contrary evidence.

Acceptance/end state: Publish reproducible comparison of debugging steps/time, reproducibility success, evidence gaps and overhead; state sample size/limitations. External developer feedback only from explicitly authorized willing participants; absent feedback is unknown, not success. Owner accepts thresholds before evaluation. A documented defer/no-go is valid completion; no fabricated commercial demand.

Tests: Verify task results, baseline comparability, repeatability and overhead measurement; separate automated checks from human usability claims.

Open questions: What benefit/overhead thresholds justify further work, and is an independent witness actually needed?

Documentation: protocol/API and synthetic examples where changed, evaluation/limits, delivery evidence and session continuity accompany the story.

### [EQ-118](https://github.com/atulsrivas1/equity-features/issues/224) — Design optional signed checkpoint and witness contracts

5 provisional points. Dependencies: EQ-107, EQ-117 positive trust-need decision; accepted content fingerprint contracts.

First actions/design: Define threat model and minimal protocol, reuse existing canonical hashes, review checkpoint retention and tenant isolation before selecting transport.

Acceptance/end state: Specify pluggable checkpoint publication/verification and witness receipts with chain/version/head/count, independent identity/key trust, freshness, replay/equivocation policy and key rotation/revocation. Separate signatures from truthful logging or completeness. No blockchain dependency. If need is unproven, retain a documented deferred design decision without implementation.

Tests: Independent signature/test-vector and altered/old/wrong-chain/unknown-key/revoked-key fixtures; honest prefix versus trusted-head suffix loss, conflicting checkpoints and unavailable witnesses.

Open questions: Who independently holds checkpoints, trust bootstrap and rotation rules, privacy commitments and needed retention?

Documentation: protocol/API and synthetic examples where changed, evaluation/limits, delivery evidence and session continuity accompany the story.

### [EQ-119](https://github.com/atulsrivas1/equity-features/issues/225) — Implement a minimal optional independent witness adapter

8 provisional points. Dependencies: EQ-118; EQ-117 owner-authorized positive decision; R7 security gates if remote hosted scope.

First actions/design: Implement the smallest justified storage/transport behind the approved protocol, use synthetic keys/data, then exercise independent retention and adversarial recovery.

Acceptance/end state: External optional adapter signs/publishes/verifies checkpoints against an independently retained witness receipt. Reuse EQ-107 ledger; no calculation I/O, consensus, token or public-chain requirement. Provide separate-party synthetic deployment/demo, queued retries/idempotency and explicit unavailable/unwitnessed status. A self-controlled demo does not establish real independent operation.

Tests: Tamper/suffix removal against retained head, substitution/equivocation, key rotation, crash/retry, tenant isolation and lost-witness behavior; remote scope adds auth/cancellation/resource tests.

Open questions: Local witness process versus hosted endpoint, operational owner, deployment approval, secrets lifecycle and cost ceiling.

Documentation: protocol/API and synthetic examples where changed, evaluation/limits, delivery evidence and session continuity accompany the story.

### [EQ-120](https://github.com/atulsrivas1/equity-features/issues/226) — Record evidence pilot acceptance and future product decision

3 provisional points. Dependencies: EQ-116/117; EQ-118/119 only if explicitly selected and justified.

First actions/design: Review collected evidence against frozen criteria, verify fresh artifacts/examples and document precisely which conditional scope was delivered.

Acceptance/end state: Publish pilot findings, supported verification guarantees, limitations, installation examples, measured overhead and owner go/defer/no-go decision. Distinguish a qualified local pilot from production readiness or regulatory compliance. Explicitly deferred witness child stories remain open Backlog or owner-cancelled; never fabricate implementation or epic completion.

Tests: Fresh installation/replay and published-source checks; witness cases only when delivered, no missing test treated as pass.

Open questions: Is there enough demonstrated value for a standalone service or repository? No automatic repository creation/deployment.

Documentation: protocol/API and synthetic examples where changed, evaluation/limits, delivery evidence and session continuity accompany the story.

## Trust and product boundaries

Our service can record and verify committed evidence, but cannot prove omitted events were captured, source data was truthful or model declarations were authentic. Signed checkpoints authenticate possession of a key under a trust policy; independently retained expected heads detect some rewrite/truncation attacks. Witness availability, freshness and conflicting checkpoints remain explicit. Public hashes may leak predictable sensitive content, so privacy commitments are designed before remote publication. No automatic regulatory/commercial/market-exclusivity claim.

A negative pilot result is useful evidence. Keep conditional witness work deferred and record an explicit scope decision; closing the pilot acceptance story alone does not close the epic or claim an implemented witness service.
