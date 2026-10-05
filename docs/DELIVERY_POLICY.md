# Release-based planning and continuous pull

Agreed: 2026-10-04. Mandatory sprints are not used.

## Planning and selection

Releases R0–R8 retain their documented goals, story scope, dependencies and acceptance gates. GitHub milestones represent releases and the Project represents actual story status. Do not create a sprint backlog or require sprint approval before pulling work.

Select the highest-priority Ready story in the earliest uncompleted release whose dependencies are satisfied. Prefer dependency-unblocking work and finish active work before starting more. Maintain one In progress story initially; expand work in progress only with a recorded reason and capacity evidence. Code review/Test remain real gates, not shortcuts around the work limit.

Prioritize explicitly when multiple stories are Ready. The human owner sets product priority and scope; the implementation agent makes routine technical decisions within scope and records significant tradeoffs. New scope gets a numbered issue, epic/release assignment and acceptance criteria. Optional accelerators stay conditional on measurements. Urgent defects may interrupt planned work with the reason and displaced story recorded.

## Forecasting and review

Target release dates are forecasts, not commitments and not substitutes for readiness. No target dates or effort estimates are set yet: gather story completion, review/testing and dependency evidence first. Never shorten numerical correctness, documentation, causal checks or release gates to meet a date. Record date/scope forecast changes and their reasons in the milestone or release decision note.

Review weekly during active development: delivered stories, active/blocked work, readiness, scope/dependency changes and forecast confidence. This is a lightweight review cadence, not an automated reminder or scheduled task. If a review does not occur, do not fabricate it. No sprint approval is needed to continue already authorized Ready work.

## Completion

Follow Backlog -> Ready -> In progress -> Code review -> Test -> Ready to release -> Released -> Done and the entry/exit rules in PUBLIC_DEVELOPMENT.md. Release readiness requires its assigned stories, dependencies, acceptance checklist and validation evidence. Documentation accompanies each story. Do not close an implementation story solely because its PR merged before its actual release.

## Immediate work and remaining decisions

R0 foundation is delivered; [acceptance](R0_ACCEPTANCE.md) retains its evidence.
The next bounded execution package is [R1_AUTONOMOUS_HANDOFF.md](R1_AUTONOMOUS_HANDOFF.md):
first BUG-001 #144 and BUG-002 #145, then EQ-017–026 according to dependencies.
Consult live Project/issue evidence for current status. The earlier
[R0 handoff](R0_AUTONOMOUS_HANDOFF.md) remains historical. Do not require another
architecture meeting to resolve decisions already assigned to stories.

| R0 decision ownership (resolved; consult accepted documentation) | Owning story |
| --- | --- |
| Trade eligibility, auctions, bar aggregation, exact/proxy measures, ties and zero denominators | EQ-002 |
| Quote sampling, locked/crossed handling and bounded time weighting | EQ-003 |
| Indicator initialization, smoothing, windows and missing-session behavior | EQ-004 |
| Baseline exclusions, benchmark alignment and universe coverage | EQ-005 |
| Cutoffs, source availability and split/dividend adjustment policy | EQ-006 |
| Python/platform support and dependency compatibility | EQ-008 |
| Build, CI, typing and boundary enforcement | EQ-009 |
| Published distribution names and registry availability; Apache-2.0 already selected | EQ-010 |
| Exact schemas, precision, API/result/error and adapter protocol definitions | EQ-011–016 |

Provider access, remote hosting and workers remain later releases. No separate up-front decision is needed on deployment scale or native acceleration before the calculation packages exist and are measured.

## Owner-directed R3 priority — 2026-10-05

The owner requested the [R3 execution package](R3_AUTONOMOUS_HANDOFF.md) and a new chat after R1 review. Prioritize its two R1 defect repairs and dependency-ready R3 stories as an explicit exception to earliest-release pulling. R2 remains separately scoped and unstarted; this decision does not authorize R2 implementation or waive its prerequisite/acceptance gates. Full R3 closure must wait for verified R2.

## Owner restores release order —2026-10-05

The owner superseded the earlier R3 feature-priority exception: existing R3 session finishes only BUG003#162/BUG004#163, then stops; the [R2 session](R2_AUTONOMOUS_HANDOFF.md) verifies their Done delivery and completes R2 before R3 resumes. All numerical/documentation/publication gates remain required. No automatic R3 restart.
