# Development continuity

Updated: 2026-10-04. Repository: atulsrivas1/equity-features. License: Apache-2.0.

## Agreed direction

Read AGENTS.md for the human owner's work agreements. Deliver source-independent Python contracts/features first, then a DuckDB adapter, independent workers, provider/file adapters, and optional remote/MCP access. Public fixtures must be synthetic or explicitly licensed. No numerical package implementation exists yet.

## Completed baseline

- Public repository, Project, nine release milestones, 12 epics and 92 EQ story issues created.
- EQ-001 completed in PR106, merged2844256888b4f4547df2c9b57aa164a264175bc9:39 feature IDs with inputs, releases, formula-story mappings and capability/exclusion boundaries. Exact-head documentation CI passed. This is scope documentation, not implemented calculations or package release.
- EQ-002 is In progress, five provisional points. Plan PR111 merged4020457606392b394e5a776a4bc024bf336f530c. The formula/fixture work is on codex/eq-002-session-formulas; verify linked final-head CI and publication before accepting it.
- Work-agreement/lifecycle change GOV-001 issue107 completed in PR108, merged14af590aa17a5674abd4ba46d7e713064a9ba5b3. Exact-head documentation CI and published content verification passed; eight-state Project migration verified. AGENTS.md and PUBLIC_DEVELOPMENT.md contain the agreed rules.

## Current work and resume

Delivery policy GOV-002 issue109 completed in PR110 mergedf3dd9e08d2b0328dee5785adeea4343c79e6a883; exact-head CI and remote publication verified. Local Windows encoding checks failed and the shell mistakenly continued to merge before their correction; explicit UTF-8 checks then passed and the gate-order exception is recorded in issue109. Stop command sequences on failed validation. Use explicit UTF-8 for document reads and writes.

Project owns current status; redundant status labels were removed. EQ-002 now has SESSION_FORMULAS.md defining all20IDs, session-semantics decision note, exact golden fixtures and a stdlib verifier with17cases. Local checks pass; final-head CI/publication remain to be confirmed on the formula PR. Verify remote published spec/fixtures and record issue acceptance after merge; then advance to EQ-003 quote formulas. R0 remains incomplete and production kernels/API are not implemented.

For documentation-only stories, publishing validated documentation on the default branch counts as that story's release; it does not release its parent milestone or a Python package. Implementation stories wait for their declared package/deployment release.

## Validation and limitations

The current check validates planning documents, all92EQ story IDs and39scope IDs/formula mappings. Tests, typing, wheel builds and benchmarks will be added as package implementation warrants them. No provider-source admission, realtime guarantee or performance acceptance follows from documentation checks. Consult live GitHub issue/PR/Project evidence for current delivery status; this handoff is a resume aid, not a duplicate status database.
