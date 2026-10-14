# EQ086 native-kernel decision packet

Prepared October 14, 2026. Local, unreviewed proposal for [EQ086 #97](https://github.com/atulsrivas1/equity-features/issues/97), E11 #95, R8 milestone9. Provisional five complexity points; no duration forecast. No Ready transition, implementation, independent review or acceptance is claimed.

## Proposed outcome and evidence

Select the issue's explicit documented no-change outcome. Accepted [EQ085 analysis](EQ-085_ANALYSIS.md) and [acceptance](https://github.com/atulsrivas1/equity-features/issues/96#issuecomment-6138514554) do not justify selecting a new calculator kernel for native implementation. This is a bounded decision about the admitted synthetic workloads, not a claim that native acceleration can never help.

EQ085 retained eighteen unprofiled samples for six sequential pipelines and separate diagnostics. Whole-pipeline medians range from 4,844.471 to 57,763.440 ms. Independent checked aggregate medians for 16,384 trades are 140.545 and 147.696 ms; checked inward Arrow conversion medians are 166.793 and 186.496 ms. Those separate calls do not share pipeline timing boundaries and cannot be divided into pipeline elapsed to infer an exclusive compute fraction or speedup ceiling.

The concrete repeated-surrogate-validation target is in the companion I/O codec, outside the calculator. The separate materialization target includes validation and ownership guarantees. Opaque native calls and orchestration/publication costs remain incompletely attributed. Profiler cumulative children are nonadditive; diagnostic overhead and uncontrolled shared-host/cache effects prevent treating self seconds as predicted savings. Accepted bothOS installations establish compatibility, not cross-platform performance.

Preserve [raw measurements](EQ-085_MEASURED.json), [summary](EQ-085_SUMMARY.json), [source qualification](EQ-085_SOURCE_QUALIFICATION.json), [readiness review](EQ-085_READINESS_REVIEW.json) and [frozen release receipt](EQ-085_RELEASE_RECEIPT.json). Do not regenerate them or relabel their reviewer as the EQ086 reviewer. Dated R7 parking statements in those records are historical; [R7 final acceptance](https://github.com/atulsrivas1/equity-features/issues/94#issuecomment-6160903589) supersedes current-status interpretation only.

## Contract and scope

No numerical algorithm, equation, unit, initialization, timing, availability, coverage, edge-case or state/schema/version change. The existing Python API, validation and ownership semantics remain the selected interface. No new Rust backend, ABI, native dependency, distribution, fallback selector or thread default is proposed. A docs decision cannot establish measured memory/throughput improvement; none is claimed.

EQ087 follows this proposed no-new-accelerator outcome only after EQ086 acceptance. EQ088 owns its separately reviewed whole-pipeline tuning protocol and any explicit scope reconciliation for codec work. Neither story is complete by this decision. Core calculations continue to receive supplied inputs, with acquisition, files/databases, credentials, scheduling and publication outside them.

Revisit native selection only with a named calculator kernel, independently justified attribution on an admitted workload, mathematical/state/version/thread/ABI contract, independent parity fixtures and a frozen bounded candidate-versus-baseline protocol. Preserve a negative or inconclusive comparison rather than requiring a native success.

## First actions and readiness gates

1. Verify restored Atul identity and Project access; refresh actual issue/Project ownership, dependencies and canonical/component defaults. No lifecycle state is inferred from this local packet.
2. Publish the reviewed R8 governance handoff through a real numbered story. GOV020 is only a candidate identifier until uniqueness is checked at creation.
3. Publish this concrete packet and provisional points to #97 with a linked draft change. Record the actual authorized review route; the owner has extended local review to the handoff, remaining R8 stories and final delivery; see AGENTS.md and CODE_REVIEW.md.
4. Have the separate reviewer assess the exact packet, admitted source evidence, no-change rationale and applicability of release checks. Record identity, exact head, executed checks, findings/disposition and limitations.
5. Once inputs and decisions are established, record Ready, then pull assigned In progress before delivering the documentation decision. Maintain one active implementation.

## Validation and accepted end state

Local preparation checks: public Markdown UTF8, relative links in new documents, unchanged versioned story coverage/lifecycle, evidence existence and exact admitted Git source identities. They are author checks, not independent review or hosted CI.

For formal acceptance, prove the final diff changes documentation only and leaves calculation/package/build/workflow inputs untouched; verify the relevant documentation CI and public default-branch UTF8/source/Atul attribution. New numerical fixtures, benchmarks and native wheel builds are inapplicable to this no-executable-change outcome. Existing accepted receipts remain scoped historical evidence, not fresh qualification.

Same-story publication includes the decision, issue/PR criteria and evidence, changelog, linked scoped lesson and SESSION_HANDOFF. Review findings must be resolved before Test; successful applicable checks and complete docs permit Ready to release. Validated documentation publication on main is the declared delivery channel. Independent final-main readback permits Released, then recorded acceptance and actual Project Done/issue closure. Do not close merely on merge or this proposal.

## Current preparation identities and limitations

Read-only October14 checks returned canonical main da74650e03d67acc5de6f8881065518f68b1f24f and worker main 95aa9ad25e3b095a7ea523140ce0f98fcad4d531. #96 is Closed; #97–99/#101–104 are Open, milestone9 Open with seven open/one closed. Project status could not be refreshed because CLI identity was monikasrivas1 and read:project was absent. The owner has authorized the R8 local-review route; actual review and access restoration remain pending. No account administration, GitHub mutation, implementation, benchmark or separate review was performed during this preparation.
