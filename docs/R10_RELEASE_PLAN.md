# R10 release plan — point-in-time diagnostics

Owner-selected October15,2026; [GOV022 #398](https://github.com/atulsrivas1/equity-features/issues/398), [epic194](https://github.com/atulsrivas1/equity-features/issues/194), [milestone11](https://github.com/atulsrivas1/equity-features/milestone/11). Runtime EQ101–105 remain Backlog at preparation. This packet authorizes no claim of implemented diagnostics. The owner's request covers bounded R10 work in this chat; the owner also explicitly authorized separate local review for PR399/the handoff, all five stories and final delivery under CODE_REVIEW.md. Permission does not establish completed review.

[Handoff](R10_AUTONOMOUS_HANDOFF.md) supplies current pins, prerequisites, story sequence, ownership and exact release gates. [Test strategy](R10_TEST_STRATEGY.md) supplies coverage. [EQ101 preparation](stories/EQ-101_PLAN.md) identifies the first decisions. Existing BACKLOG/EVIDENCE_ROADMAP story scope and31 provisional complexity points are retained. GOV022 is additional documentation governance, not an additional runtime feature; milestone membership after its creation is seven including epic and governance.

## Outcome

A consumer can inspect declared point-in-time checks on supplied facts, distinguish observed failure from missing evidence, link accepted acquisition/task/generation provenance to content receipts, and exercise a synthetic adversarial conformance suite. Diagnostics do not discover historical facts, authenticate timestamps, calculate a universal safety score or certify profitability/compliance.

R9 full-content and receipt identities are reusable; metadata-only equality is insufficient. Accepted calculations and their C/K/E semantics remain unchanged. R10 neither broadens R9's fixed replay registry nor adds agent events/ledger/MCP services; those owners remain separate. Public fixtures are synthetic, with no provider/private acquisition.

## Scope allocation and decisions

EQ101 specifies the records, schema/version/check domain, temporal truth table and admission policy. EQ102 implements optional pure membership/revision/availability checks. EQ103 bridges already accepted I/O and worker evidence externally; it must retain exact provenance identity and completeness, without acquiring facts inside pure code. EQ104 qualifies declared attacks with independent controls. EQ105 qualifies the real installed composition and delivery. See the ordered handoff table for dependencies, points and concrete acceptance.

Proposed separate canonical diagnostics distribution is inward-only on accepted contracts/evidence. Settle names, exact dependencies, source ownership, supported typed fact domains and literal limits in EQ101 before runtime Ready. No baseline package version or schema change is implied by this handoff. New wire identities require explicit schema/domain/canonicalization, byte limits and independent pre-code fixtures; never repurpose existing digests.

Resolve severity and advisory-versus-admission explicitly. Recommended default is advisory immutable findings; a caller may select a separate strict policy for named checks. Unknown evidence remains unknown in the finding even if a strict policy declines admission. Invalid structured data remains an error. Require requested check identities and explicit coverage; absence of a requested check is not success. No opaque aggregate score.

## First release boundaries

Use supplied finite populations and exact UTCns/int64 identities. Reuse known-at/effective/market boundaries and closing-auction exceptions; no inferred calendars or retrospective timestamps. Support only named declared checks and fact schemas. R10 may detect inconsistency with declared historical rules while still being unable to prove historical acquisition truth or unreported contamination. Missing provenance cannot be repaired by matching hashes, a current-only universe or file presence.

The supported initial provenance path is synthetic accepted DuckDB acquisition plus accepted worker task/output generation and a R9 receipt. EQ103 must freeze concrete supported public object/version mappings before implementation; raw unknown provider metadata is not silently admitted. Full source/caller identity and unchanged-calculation tests precede any optimization or larger integration.

## Release gate and next action

Each story follows the actual eight-stage lifecycle and its own complete reviewed readiness packet. No commitment to delivery dates or speedups. Current bothOS/source/installed/review/main/artifact evidence is mandatory for changed installable code; documented no-impact design changes use their applicable checks. Complete all five runtime stories plus GOV022; then verify exact epic/milestone membership, acceptances, actual aggregate lifecycle and zero-open closure.

Next: publish/review GOV022 and settle the R10 review route, then finish EQ101's independent fixture table and schema/admission contract. R9 remains accepted; no past artifact/benchmark/operational rerun is needed merely to repeat its status.
