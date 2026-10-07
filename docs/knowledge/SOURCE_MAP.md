# Sources and review coverage

GOV-011 knowledge import, October 5, 2026. Repository baseline inspected: `b9bc2934ef389b775f97d8d18f8b2ef70d6bd884`. Documents may evolve; resolve current authority before execution. See [repository fingerprints](repository-sources.json) for the inspected versioned source records.

## Authoritative entry points

| Question | Read |
| --- | --- |
| Purpose, boundaries, two-package ownership and planned companion I/O/workers | [Design](../PACKAGE_DESIGN.md), [layout](../PACKAGE_LAYOUT.md), [current I/O architecture](../IO_WORKER_ARCHITECTURE.md), [product boundaries](../decisions/product-boundaries.md) |
| Which features and release dependencies? | [V1 scope](../features/V1_SCOPE.md), [backlog](../BACKLOG.md), live [Project](https://github.com/users/atulsrivas1/projects/2) |
| Exact mathematics | [Session](../features/SESSION_FORMULAS.md), [quotes](../features/QUOTE_FORMULAS.md), [history](../features/HISTORICAL_FORMULAS.md), [context](../features/CONTEXT_FORMULAS.md) |
| Temporal admission and corporate actions | [Timing policy](../features/TIMING_ADJUSTMENT_POLICY.md), [timing decision](../decisions/timing-adjustment.md) |
| Public data, quality and adapter contracts | [Inputs](../contracts/INPUTS.md), [specifications](../contracts/SPECS.md), [results](../contracts/RESULTS.md), [validation](../contracts/VALIDATION.md), [registry](../contracts/REGISTRY.md), [adapters](../contracts/ADAPTERS.md) |
| Runtime, state and merge capabilities | [Incremental API](../api/INCREMENTAL.md), [continuous quotes](../api/CONTINUOUS_QUOTES.md), actual source registry and version |
| Accepted foundation/session artifacts | [R0 acceptance](../R0_ACCEPTANCE.md), [R1 acceptance](../R1_ACCEPTANCE.md), their story receipts, [build delivery](../BUILD_DELIVERY.md) |
| Later defects and repair qualification | [R1 review](../reviews/R1_REVIEW.md), BUG-001–004 issue/PR records, live status |
| Release work and authority | [Handoff](../SESSION_HANDOFF.md), release-specific execution packages, [GOV-010](https://github.com/atulsrivas1/equity-features/issues/167) and linked publication evidence |
| Rights/publication | [Release access](../decisions/release-access.md), [workflow](../PUBLIC_DEVELOPMENT.md) |

## Chat review scope

The available active cross-app list was screened along with the archived Codex listing. Relevant known execution chat IDs were also queried directly because the list is capped and omitted some active release sessions. Six relevant chats were inspected:

- **Compare database speed and storage**: eight newest pages, 80 turn records, covering the standalone-project decision, Python-first architecture, release workflow, scope corrections, reviews and R2 priority. Earlier database/import history remains outside this targeted import.
- **Complete equity-features R0 autonomously**: all three returned turn records, including follow-up review repairs.
- **Complete equity-features R1 autonomously**: its returned execution turn and final acceptance statements.
- **Complete equity-features R3 and R1 review…**: returned active execution turn; repair/receipt progress is a dated snapshot.
- **Complete equity-features R2 autonomously**: returned active execution turn; preparation is distinct from implementation.
- **Open-source equity library and GitHub…**: ten newest turn records screened for setup boundaries. Personal profile/account administration was excluded from the engineering knowledge pack.

Chat tools return summaries/message text and may truncate individual content. Tool payloads, private attachments and older unlisted account chats were not exhaustively audited. Relevant public repository documents were read in targeted sections and cross-checked against issue/PR metadata. This is not a full independent implementation review or reproduction of historical acceptance gates.

Public records contain engineering paraphrases and links to existing public evidence, not raw transcripts, private source, deployment locations or account details. Repository fingerprints identify versions; they do not imply every line of every document was inspected. Refresh active status and provider capabilities before making new decisions.

## Consumer/data boundaries

Do not create a second dataset or import corpus simply because this is a separate checkout. Pure packages are usable without production data. Future adapters must qualify schema, identity mapping, units, clocks, coverage, licensing and declared source capabilities. A previous data-import completion statement is not source admission, and code-license rights do not cover provider redistribution.

Legacy comparison needs separately verified source access and rights; public examples remain synthetic or licensed. File existence is not formula parity. Missing legacy evidence should be recorded as a concrete dependency rather than fabricated or silently waived. Keep application-specific architecture in its own project.
