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

Next: EQ-002, session/bar/trade formulas with independently worked examples. Follow with formula stories EQ-003–006 according to their dependencies, then public contracts and package foundation. Do not require another architecture meeting to resolve decisions already assigned to stories.

| Decision still required | Owning story |
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
