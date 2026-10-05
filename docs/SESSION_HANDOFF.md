# Development continuity

Updated2026-10-04. Public repository: atulsrivas1/equity-features; Apache-2.0. Read AGENTS.md and PUBLIC_DEVELOPMENT.md; GitHub Project is the actual status authority.

## Scope and completed work

Source-independent Python contracts/features first, then DuckDB adapter, workers, provider/file adapters and optional remote/MCP access. Calculation libraries do no source I/O. Other applications are separate products; their designs/integrations belong outside this repository. See decisions/product-boundaries.md. No production calculation package has been implemented or published.

EQ-001 feature scope Done in PR106 (39IDs); EQ-002 session/bar/trade mathematics Done in PR112 (20definitions,17reference cases); EQ-003 quote formulas Done in PR121 mergeaf0dbb8552a3667c242bd46756bf6cb2292d4a5d (3definitions,26reference cases). Final-head CI, publication comparison and post-publication tests were verified on their issues. EQ-004 historical formulas is Ready and needs a detailed plan next. R0 remains incomplete. EQ-093 custom extensions remains Backlog/R3, with no implementation or sandbox claim.

## Current scope correction

Owner withdrew external-product-specific integration scope. GOV-006 issue#122 removes the external-product document/references and existing story additions; EQ-094 is retired as not planned, removed from active Project/milestone/parent scope and must not be reused.93active EQ stories remain. Generic precision, availability, state and replay contracts are preserved. Previous proposal GOV-004/PR118 is historical and superseded, not current scope. History is retained; published historical diffs are not erased.

Resume: verify GOV-006 linked PR/final checks/publication and GitHub withdrawal metadata. Ensure deferred PR120 is synchronized so it cannot restore retired material. Then start EQ-004 planning; do not recreate removed product-specific scope.

## Review and validation

GOV-005 issue119/PR120 remains open and explicitly deferred by owner. No hosted integration or separate Codex review is claimed. Existing self-review, CI, acceptance/documentation and publication checks apply until owner resumes setup. Actual reviewers and limitations must be recorded; administrator merges do not imply human review.

Documentation CI checks93active EQ IDs,39builtin feature IDs and eight lifecycle states. Reference verifiers check17session and26quote cases; no backend/performance/provider qualification follows. Use explicit UTF-8. GOV-002 recorded a local encoding failure and a shell sequence that incorrectly continued to merge; corrected post-merge checks passed. All command sequences must stop on failed checks. Documentation releases are not parent milestone/package releases. Public fixtures stay synthetic or explicitly licensed; never publish private data/credentials.

Scope-cleanup validation note: a Project removal command used an unsupported CLI flag and stopped before commit/publication. Corrected to the documented project-number/owner syntax; verify Project removal in final acceptance. No failed command was treated as a successful whole sequence.
