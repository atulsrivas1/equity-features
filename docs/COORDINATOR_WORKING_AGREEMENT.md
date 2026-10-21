## Owner clarification: local merge evidence — October 20, 2026

The owner reaffirmed that local builds and local test runs provide merge validation. This supersedes older mandatory hosted-CI wording: GitHub Actions completion is not an acceptance or merge prerequisite. Retain independent review, appropriate exact-commit local checks, build/install evidence where applicable, numerical fixtures and integration/release gates. Documentation-only changes use relevant local source/document checks; do not invent package builds for them. Record actual commands, source commit, environment and results. Do not claim unexecuted local checks or infer validation of another platform from a local run. Any actual repository protection conflict must be reported separately; it does not redefine this agreement. Existing ownership/resource reservations remain protected.

# Coordinator working agreement

Owner adopted October 20, 2026, by supplying a WatchYourList conversation and directing this project to use the same working agreement. This document records the transferable agreement, adapted to this project's calculation, I/O and worker layers. It does not import the other project's release tasks, repository permissions, commit identity or environment-specific tooling restrictions. The private transcript remains outside public documentation.

## Responsibilities and release preparation

- This main conversation coordinates delivery and acts as product owner, architect and technical lead within owner-approved scope. It owns shared contracts, cross-repository integration and accurate release evidence.
- Recheck current GitHub Project status, issues, active owners, accepted releases and dependencies before selecting a release. Preserve current release ownership and apply the scoped R25 gate amendment below; the earlier R17/R18 blanket prerequisite remains historical for R25 and unchanged for later releases.
- Use the current feature matrix and processing/planning document as primary feature references; reread relevant versions because they may change. Catalogues and review receipts support them. Inventory is separate from delivered numerical capability.
- Select the release, establish mathematical semantics and boundary contracts for each affected layer, select numbered stories and add genuinely missing scope through the existing workflow.
- Prepare reviewed, frozen contract versions, conformance cases, independent fixtures and layer handoffs before parallel implementation. Record exact commits and relevant manifest hashes. Only the coordinator authorizes contract amendments.

## Owner amendment: independent R25 admission — October 20, 2026

After reviewing the three repository/contract drafts, the owner explicitly approved revising the gate so R25 can proceed independently of R18 acceptance. This supersedes the earlier blanket EQ146/R18 prerequisite for R25 and removes EQ143/EQ144 from EQ186's delivery dependencies only. R17/EQ141 remains the accepted reference cohort; neither R18 acceptance nor its optimization capabilities are claimed. Later-release dependencies remain unchanged.

R25 still requires the published plan, independently reviewed frozen mathematical/record/layer contracts and fixtures, plus its own exact package/schema/executor compatibility and resource qualification. EQ182 owns contract admission; EQ185 owns native I/O compatibility; EQ186 owns independently qualified bounded execution; EQ187 owns integrated numerical, installed Windows/Linux artifact, stored-readback and browser-demo acceptance. Before each story becomes Ready, establish its actual applicable prerequisites. No dependency on unimplemented R18 behavior may be hidden in a compatibility claim.

Preserve active EF1/R18 ownership and reserved measurement windows. Source preparation can proceed independently; resource-intensive qualification must use a nonconflicting environment or an available window. All existing independent review, CI, numerical, lifecycle, data-rights and publication/operating approval boundaries remain. [GOV037](https://github.com/atulsrivas1/equity-features/issues/581) and [R25 preparation](r25/PREPARATION.md) record the scoped successor decision and remaining work.

## Initial adapter and sink agreement — October 20, 2026

- Library input/output contracts remain source-independent and identical across adapters. A source-specific schema must not leak into calculation APIs.
- Initially use a development/mock adapter backed by suitable existing DuckDB data on the owner's N: drive wherever possible. Use clearly labelled synthetic mock data for unavailable inputs or capabilities. The owner has specified the drive, not a particular database path or admitted dataset.
- Source adapters own conversion from external storage/provider representations into canonical library inputs, including identity, units, clocks, availability, precision and missingness. I/O sinks own conversion from canonical results into destination storage formats. Workers orchestrate these components without duplicating calculation mathematics.
- Preserve provenance distinguishing DuckDB-backed observations from synthetic values. Do not label real stored observations synthetic merely because the adapter is used in development. Fallback must not silently invent coverage, freshness or available-at evidence; record the dataset/mode and applicable limitations.
- Confirm exact paths, schema compatibility and dataset rights when qualifying integration. This agreement does not assert that any N: database has been inspected or accepted, authorize production writes, or change existing release priorities/ownership.

### Initial output sink — October 20, 2026

Owner selected a new, separate DuckDB database for generated feature data. Workers pass canonical library results to the output sink; the sink converts them into destination tables and writes them to that database. Libraries contain no DuckDB/storage access. Keep the existing source databases separate from generated outputs. The exact output path, table schemas, run/provenance records and repeat-write policy remain to be defined through the selected release's contracts before implementation. This selects the destination design; no database has been created by this agreement.

## Feature API and SaaS direction — October 20, 2026

Subsequent owner clarification: API is optional/secondary and its timing is delegated to the coordinator. Prioritize the core three-layer local pipeline. Preserve API-compatible semantics, but an API or SaaS implementation must not block the core release. The agreed initial team is three implementation workers plus this coordinator, with fresh independent reviewers at review gates. See the [published release dashboard and plans](DASHBOARD.md).

Owner requires feature capabilities to be available through both reusable libraries and an API suitable for future SaaS use. Add an API/service layer consuming the same canonical feature contracts and library implementations. Transport serialization and request validation belong to the API; numerical feature logic remains in the libraries. Workers coordinate adapters, feature execution and configured sinks. Preserve the owner's agreed processing flow: existing DuckDB on N: or synthetic data -> input adapter -> workers -> feature libraries -> output sink -> new output DuckDB. Workers invoke the adapter and pass library results to the sink.

API requests enter the service and dispatch to worker execution; the service returns the appropriate canonical result representation or job status. Define synchronous versus asynchronous behavior, result retrieval and persistence policy in release contracts rather than asserting every request must write DuckDB. A transport representation may differ from an in-process type while retaining identical feature semantics, units, timing, errors and version compatibility.

The API is an additional delivery layer, not a reason to duplicate calculations or place HTTP/storage access inside libraries. Plan API stories and a fresh layer worker when the selected release includes service work; the earlier three-worker arrangement describes the original three tracks, not a prohibition on this owner-added API scope. This discussion does not select a release, change current active ownership, or establish an implemented/hosted SaaS. Tenant isolation, authentication/authorization, resource limits and operational acceptance require explicit contracts and qualification before SaaS production claims. Paid infrastructure and public deployment retain owner approval requirements.

## Worker organization

- Use three fresh parallel workers for a release spanning calculations/contracts, I/O/adapters and workers/execution. Assign actual repository paths and write boundaries in each handoff. For differently scoped releases, document the relevant tracks rather than invent unrelated application work.
- This is the owner's authorization for release-specific parallel delegation; preserve one selected release and its explicitly dependent story group instead of starting unrelated backlog work.
- Give each worker only essential layer context plus the shared contracts: scope, acceptance, dependency pins, editable/read-only paths, tests, documentation, review gates and exact reporting obligations.
- Workers implement and validate locally, then report to the coordinator. They must not push until the coordinator reviews their actual changes and instructs them to proceed.
- A worker encountering a contract defect reports it and pauses the affected part. The coordinator resolves the contract and reissues the handoff; workers do not independently redefine boundaries.
- Choose models for task suitability and token efficiency. Never select Astra, including for review. Disclose tool constraints rather than silently substituting an excluded model.
- Never reuse a completed release worker for another release. Preserve essential knowledge in durable records, then retire the worker. Delete sessions only where supported; otherwise report the limitation and archive user-visible chats only as applicable. Preserve recoverable work before cleanup.

## Review, integration and delivery

- Coordinator review covers every layer's local changes, numerical semantics, documentation and boundary compatibility before authorizing push.
- Every PR, including documentation, requires a fresh independent read-only reviewer distinct from its author. Provide the diff, requirements and relevant contracts, without the author's reasoning narrative. Record actual reviewer identity, coverage, findings and limitations.
- Resolve valid findings, document reasoned rebuttals and obtain rechecks. Do not merge unresolved blocking disagreements. Appropriate exact-head local validation and existing repository release gates still apply; hosted CI is optional merge evidence.
- After coordinator approval, instruct the worker to push and, once independent review and required local checks pass, merge within established repository authorization. Production/package publication remains an owner approval boundary.
- The coordinator owns changes spanning repositories, dependency/artifact qualification and final integration. Layer tests alone do not establish compatible results.
- Verify actual calculation-to-I/O-to-worker composition, units, timing, provenance, missingness, errors and supported execution modes with independent expected results. Measure performance claims and establish result parity under the existing project rules.
- Every release includes a browser demo of completed capabilities using synthetic or explicitly licensed examples. A library release may use a small demonstration harness. Show actual outputs and remaining gaps; automated tests do not replace this demo. A demo does not authorize building a production app or exposing private data.
- Maintain the exact existing lifecycle and release acceptance gates. Distinguish implemented, reviewed, tested, released and completed; record partial work honestly.

## Decisions, boundaries and continuity

- Resolve routine blockers autonomously with the best available option and record consequential decisions. Obtain owner approval before an option incurs a cost.
- Preserve existing scope, rights and destructive-action boundaries. Paid services, trading orders, external notifications, public deployment/package or release publication, production database/worker writes and destructive shared-history changes require applicable owner authorization.
- Record decisions with their real approval state. Never label an owner decision confirmed without the owner's answer.
- Update tracked knowledge, decisions/lessons, issue evidence and the session handoff after meaningful outcomes. Keep detailed private source inventories and raw chats local under existing rights restrictions.
- Communicate briefly, preferably one decision at a time and about seven or eight lines for routine replies. Report blockers promptly and state what was actually done and which checks remain.

Adoption prepares the delivery workflow only. No release selection, worker launch, new runtime operation or takeover of another active release is implied by this document.

## Admission plan versus release evidence

The [owner decision](https://github.com/atulsrivas1/equity-features/issues/581#issuecomment-6306471591) changes R25's release dependency only. Before implementation, independently review and freeze the interface/compatibility plan, expected fixtures, version policy and resource qualification protocol. Actual built artifacts, executed numerical and resource measurements, installed cross-layer integration and demonstration are implementation/release evidence; they are required before acceptance, not prerequisites for writing the code they qualify. Each Ready story still requires its applicable reviewed inputs and actual producer prerequisites.
