# Development continuity

Updated: 2026-10-04. Repository: atulsrivas1/equity-features. License: Apache-2.0.

## Agreed direction

Read AGENTS.md for the human owner's work agreements. Deliver source-independent Python contracts/features first, then a DuckDB adapter, independent workers, provider/file adapters, and optional remote/MCP access. Public fixtures must be synthetic or explicitly licensed. No numerical package implementation exists yet.

## Completed baseline

- Public repository, Project, nine release milestones, 12 epics and 92 EQ story issues created.
- EQ-001 completed in PR106, merged2844256888b4f4547df2c9b57aa164a264175bc9:39 feature IDs with inputs, releases, formula-story mappings and capability/exclusion boundaries. Exact-head documentation CI passed. This is scope documentation, not implemented calculations or package release.
- EQ-002 is Ready: exact session/bar/trade formulas and independent worked examples.
- Work-agreement/lifecycle change GOV-001 issue107 completed in PR108, merged14af590aa17a5674abd4ba46d7e713064a9ba5b3. Exact-head documentation CI and published content verification passed; eight-state Project migration verified. AGENTS.md and PUBLIC_DEVELOPMENT.md contain the agreed rules.

## Current work and resume

PR108 merged14af590aa17a5674abd4ba46d7e713064a9ba5b3; exact-head CI and remote published agreements/workflow/handoff verification passed; GOV-001 issue107 Done. New agreed delivery policy uses release milestones and continuous story pulling without mandatory sprints. codex/release-pull-policy is documenting this with one active story, weekly review and forecast dates only when evidence supports them. Verify its linked governance issue/PR before assuming this change published. Once delivered, start EQ-002; remaining mathematical/runtime/API decisions already have owning stories in DELIVERY_POLICY.md.

Project owns current status; redundant status labels were removed. Resume EQ-002 after delivery-policy publication: read docs/features/V1_SCOPE.md and the issue's acceptance criteria, then define exact session/bar/trade formulas and independent worked examples before numerical code.

For documentation-only stories, publishing validated documentation on the default branch counts as that story's release; it does not release its parent milestone or a Python package. Implementation stories wait for their declared package/deployment release.

## Validation and limitations

The current check validates planning documents, all92EQ story IDs and39scope IDs/formula mappings. Tests, typing, wheel builds and benchmarks will be added as package implementation warrants them. No provider-source admission, realtime guarantee or performance acceptance follows from documentation checks. Consult live GitHub issue/PR/Project evidence for current delivery status; this handoff is a resume aid, not a duplicate status database.
