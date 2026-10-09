## R6 scope closure selected by owner — October 8, 2026

Owner explicitly moves Databento/Massive to Backlog and requests R6 closure. [GOV019](https://github.com/atulsrivas1/equity-features/issues/354)/[decision](../decisions/R6_SCOPE_CLOSURE.md)/[revised acceptance](../R6_ACCEPTANCE.md) retain four accepted runtime stories and defer dependent composition/provider-aggregate qualification. All four deferred issues stay open without R6 milestone/future release assignment; original criteria/source/tests/draft PRs remain preserved. This supersedes the all-eight R6 mission, not its unmet provider criteria. Actual closure follows reviewed publication/readback; R7 provider dependencies and private rights/admission remain separate. No R7 implementation is started by this decision.

# Decision history

Engineering summaries of owner decisions and accepted records, prepared October 5, 2026. Canonical specifications control details. Preserve supersession rather than silently replacing history.

| Decision | Current consequence | Source / superseded direction |
| --- | --- | --- |
| Separate reusable open-source equity packages | Public original code, synthetic/licensed examples, Apache-2.0; private data/source reuse needs verified rights | [Release access](../decisions/release-access.md); supersedes a source-specific bundled worker project |
| Python-first public API with two distributions | Dependency-light contracts; calculations depend inward; optional/native acceleration only after justified measurement | [Package design](../PACKAGE_DESIGN.md), [layout](../PACKAGE_LAYOUT.md); supersedes Go-first and earlier provider-prefixed package names |
| Calculations never acquire inputs | No file/DB/network/credential/clock/scheduler access in calculation code; caller supplies data/configuration/availability | [AGENTS](../../AGENTS.md), [adapter contracts](../contracts/ADAPTERS.md) |
| Mathematics before implementation | Formula, units, initialization, timing, coverage and edge examples precede feature code | [Feature scope](../features/V1_SCOPE.md), linked formula stories |
| Exact identity and explicit missingness | Preserve UTC int64 nanoseconds, scaled integer values, source revisions and independent quality; missing is not zero | [Inputs](../contracts/INPUTS.md), [results](../contracts/RESULTS.md) |
| Causal and reconstructed history are distinct | Supplied market/reference/decision cutoffs and known-at evidence govern admission; generation time does not prove historical availability | [Timing policy](../features/TIMING_ADJUSTMENT_POLICY.md) |
| Release-based continuous pull | One active story initially; pull dependency-satisfied Ready work; dates are evidence-based forecasts, no mandatory sprint ceremony | [Delivery policy](../DELIVERY_POLICY.md); supersedes the initial sprint suggestion |
| Eight lifecycle stages and documentation with every story | Backlog → Ready → In progress → Code review → Test → Ready to release → Released → Done; merged code is not automatically delivered | [Public workflow](../PUBLIC_DEVELOPMENT.md) |
| Experimental artifacts are the current channel | Verify actual main bundles and fresh installations; no registry/stable/throughput claim from source merge alone | [Build delivery](../BUILD_DELIVERY.md), [release access](../decisions/release-access.md) |
| External products remain separate | No consumer-specific architecture/integration requirement; EQ-094 withdrawn and reserved | [Product boundaries](../decisions/product-boundaries.md), [PR123](https://github.com/atulsrivas1/equity-features/pull/123) supersedes the earlier integration proposal |
| Explicit consumer extension qualification | Distinct custom ID/version, no built-in replacement, declared timing/capabilities and public-API clean-install example; registration is planned until delivered | [EQ-093](https://github.com/atulsrivas1/equity-features/issues/113), [EQ-095](https://github.com/atulsrivas1/equity-features/issues/150) |
| Reviewer activation deferred | Retain author self-review/CI and honest identity; do not claim independent/automated review | [Workflow owner decision](../PUBLIC_DEVELOPMENT.md), [GOV-005](https://github.com/atulsrivas1/equity-features/issues/119) |
| R2 precedes R3 feature work | Finish two R1 repairs with their owner; R2 waits for verified delivery; R3 requires renewed scope at the appropriate boundary | [GOV-010](https://github.com/atulsrivas1/equity-features/issues/167), [PR168](https://github.com/atulsrivas1/equity-features/pull/168); supersedes the earlier R3 execution priority |

When a decision changes, add date, owner/source evidence, affected records and consequences. Earlier decisions remain historical and cannot authorize today's account, publication, source-access or live-process actions.

## October 5, 2026 — evidence roadmap planning

The owner requested epics/stories/releases for reproducible calculation evidence, point-in-time diagnostics and agent evidence. [GOV-012](https://github.com/atulsrivas1/equity-features/issues/192) adds E13–E15, EQ-096–110 and R9–R11. Reuse EQ-053 acquisition provenance, EQ-057/061 worker manifests and EQ-082 MCP; new work links evidence rather than duplicating those systems. Planning does not interrupt R2, resume paused R3, alter current equations or certify regulatory compliance. [Plans and limitations](../EVIDENCE_ROADMAP.md).

## Owner-authorized proposal refinements — October 5, 2026

Corrected ledger proposal maps into existing EQ-096/097/101/102/106/107; no ID reassignment. [Design](../AGENT_EVIDENCE_DESIGN.md) fixes unanchored truncation, metadata-only hashing, historical decision timing and quadratic append risks. Continuous-market proposals use separate E16/R12/EQ-111–115 and begin with capability-gap/formula decisions, not assumed new session types. [Design](../CONTINUOUS_MARKET_DESIGN.md). All implementation remains Backlog; R2 priority unchanged. Original private proposal files preserved locally; only revised source-independent design is published.

## Owner direction — low-priority evidence service validation

Plan our own evidence service as a focused synthetic consumer pilot, not a new blockchain. E17/R13/EQ-116–120 stay Backlog with priority:low; evaluate value against structured logs before conditional witness design/implementation. [Plans](../EVIDENCE_SERVICE_PILOT.md). No-go is legitimate evidence; deferred implementation cannot be relabeled Done.


## October 6: R4.1 before R5

Owner selects separate feature/I/O/worker repositories with explicit input adapter/output sink factories and third-party extension kits. [Decision](../decisions/IO_REPOSITORY_SEPARATION.md), [GOV-014 #275](https://github.com/atulsrivas1/equity-features/issues/275). This supersedes earlier planned co-location of adapter/worker implementations; it does not invalidate delivered R4 or change numerical/input contracts.

## R4.1 execution handoff and dedicated session

October 6 owner requests preparing and assigning bounded R4.1 to a new session. [GOV-015 #289](https://github.com/atulsrivas1/equity-features/issues/289), [handoff](../R4_1_AUTONOMOUS_HANDOFF.md). Canonical stories remain in the feature repository/Project across companion PRs; separate release session may bootstrap after verified handoff publication while the parent verifies assignment/closes GOV-015; it starts implementation only after live Done and stops before R5. Existing local reviewer authorization applies to this R4.1 preparation/delivery; no new hosted activation or later-release review waiver.
