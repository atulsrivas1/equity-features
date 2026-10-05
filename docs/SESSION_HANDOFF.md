# Development continuity

Updated: 2026-10-04. Repository: atulsrivas1/equity-features. License: Apache-2.0.

## Agreed direction

Read AGENTS.md for the human owner's work agreements. Deliver source-independent Python contracts/features first, then a DuckDB adapter, independent workers, provider/file adapters, and optional remote/MCP access. Public fixtures must be synthetic or explicitly licensed. No numerical package implementation exists yet.

## Completed baseline

- Public repository, Project, nine release milestones, 12 epics and initially 92 EQ story issues created.
- EQ-001 completed in PR106, merged2844256888b4f4547df2c9b57aa164a264175bc9:39 feature IDs with inputs, releases, formula-story mappings and capability/exclusion boundaries. Exact-head documentation CI passed. This is scope documentation, not implemented calculations or package release.
- EQ-002 Done: PR112 mergeddf08aa13e25e15d824a6e4aac94cd099b1bb26c6; final-head CI,17reference tests/20definition coverage and published spec/fixtures verification passed. EQ-003 quote formulas is Ready.
- Work-agreement/lifecycle change GOV-001 issue107 completed in PR108, merged14af590aa17a5674abd4ba46d7e713064a9ba5b3. Exact-head documentation CI and published content verification passed; eight-state Project migration verified. AGENTS.md and PUBLIC_DEVELOPMENT.md contain the agreed rules.

## Current work and resume

Delivery policy GOV-002 issue109 completed in PR110 mergedf3dd9e08d2b0328dee5785adeea4343c79e6a883; exact-head CI and remote publication verified. Local Windows encoding checks failed and the shell mistakenly continued to merge before their correction; explicit UTF-8 checks then passed and the gate-order exception is recorded in issue109. Stop command sequences on failed validation. Use explicit UTF-8 for document reads and writes.

Project owns current status. Custom extension roadmap change GOV-003 completed in PR115, merge0592c9b3202069bd08db93cfd6c9b7f99805f81e; EQ-093 remains Backlog/R3, with no implementation or sandbox guarantee.

User authorized the chart consumer integration contract. GOV-004 issue#117 publishes the proposed boundary and EQ-094 issue#116 (E03/R3, Backlog). Contract: initial Python analysis host/explicit batch boundary; immutable data revision binding, exact int64/scaled prices, full-resolution calculations, provisional previews separate from committed state and correction/backfill replay. No production chart adapter, native kernel or new market coverage is implemented. Final schema/transport and capability details are open until EQ-094 planning. Rust is a suitable chart-engine choice; shared calculation kernels remain evidence-gated EQ-085–087.

GOV-004 publication PR: #118. Self-review corrected a table separator and removed a circular EQ-044 dependency: EQ-094 needs contract/typing/incremental foundations; EQ-044 jointly qualifies its compatibility. Planning checks and17reference cases pass; consult PR for final-head CI and publication evidence.

Resume: verify GOV-004 linked PR/checks/publication and live Project status; finish its documentation release if necessary. Then resume EQ-003 quote formulas with a story plan. R0 remains incomplete; production kernels/API are not implemented. Do not start EQ-094 ahead of its prerequisites.

For documentation-only stories, publishing validated documentation on the default branch counts as that story's release; it does not release its parent milestone or a Python package. Implementation stories wait for their declared package/deployment release.

## Validation and limitations

The current check validates planning documents, all94EQ story IDs and39built-in scope IDs/formula mappings, plus17session reference cases. Tests, typing, wheel builds and benchmarks will be added as package implementation warrants them. No provider-source admission, realtime guarantee or performance acceptance follows from documentation checks. Consult live GitHub issue/PR/Project evidence for current delivery status; this handoff is a resume aid, not a duplicate status database.

## Current active story: EQ-003

User deferred Codex review setup; GOV-005 issue119 and draftPR120 stay open/deferred. Their proposed separate-review gate is postponed by the owner. Continue existing self-review, CI, documentation and publication gates; never claim bot review. Pending reviewer branch records this deferral too.

EQ-003 issue4 is In progress, estimated5provisional points. codex/eq-003-quote-formulas delivers3quote definitions, sampling/state/time-weighting decisions and synthetic exact references. Resume its linked PR/review/tests before release; no numerical package implementation or provider trust is claimed. GOV-004 PR118 already merged5583ec35730472c023b2f1c0b1a1a3b0ea75edc9 and published contents were verified.

EQ-003 artifacts now include execution plan,3quote definitions, quote-semantics decisions, synthetic exact golden fixtures and quote reference verifier. Qs/Qc separated; locked0valid, crossed excluded from means, midpoint-bps per observation, explicit age and original seed age, invalid reset, unknown boundary and delivery completeness specified. Verify final-head reference/CI checks and publication before Done; next EQ-004 needs a plan.

EQ-003 local acceptance evidence:26quote reference cases plus17existing session cases pass, all3quote IDs mapped,94story/39feature/eight-state planning checks pass. Self-review added delivery-gap/no-valid-time/int64 boundary cases and guarded duration representation. Final-head CI and remote publication still required. After documentation delivery, verify issue/Project Done and set EQ-004 Ready; GOV-005 remains deferred.
