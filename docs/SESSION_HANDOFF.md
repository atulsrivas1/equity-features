# Development continuity

Updated: 2026-10-04. Repository: atulsrivas1/equity-features. License: Apache-2.0.

## Agreed direction

Read AGENTS.md for the human owner's work agreements. Deliver source-independent Python contracts/features first, then a DuckDB adapter, independent workers, provider/file adapters, and optional remote/MCP access. Public fixtures must be synthetic or explicitly licensed. No numerical package implementation exists yet.

## Completed baseline

- Public repository, Project, nine release milestones, 12 epics and 92 EQ story issues created.
- EQ-001 completed in PR106, merged2844256888b4f4547df2c9b57aa164a264175bc9:39 feature IDs with inputs, releases, formula-story mappings and capability/exclusion boundaries. Exact-head documentation CI passed. This is scope documentation, not implemented calculations or package release.
- EQ-002 is Ready: exact session/bar/trade formulas and independent worked examples.
- Work-agreement/lifecycle change is being delivered on codex/work-agreements. Verify its PR/checks/merge and live Project before treating it as delivered; this document does not assert that future merge succeeded.

## Current work and resume

Finalize the agreed eight-stage status workflow and documentation-with-every-story rule in AGENTS.md and PUBLIC_DEVELOPMENT.md. Verify Project options and preserve each item's actual state during migration. Validate documentation links and workflow consistency, publish linked PR, record evidence, and move its tracked work item through actual review/test/release gates. Then resume EQ-002 from docs/features/V1_SCOPE.md and the issue's acceptance criteria.

For documentation-only stories, publishing validated documentation on the default branch counts as that story's release; it does not release its parent milestone or a Python package. Implementation stories wait for their declared package/deployment release.

## Validation and limitations

The current check validates planning documents, all92EQ story IDs and39scope IDs/formula mappings. Tests, typing, wheel builds and benchmarks will be added as package implementation warrants them. No provider-source admission, realtime guarantee or performance acceptance follows from documentation checks. Consult live GitHub issue/PR/Project evidence for current delivery status; this handoff is a resume aid, not a duplicate status database.
