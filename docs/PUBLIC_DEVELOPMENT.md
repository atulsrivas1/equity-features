# Public development workflow

Status: proposed workflow, 2026-10-04. Repository: atulsrivas1/equity-features. Issues, milestones and the public Project are linked in DASHBOARD.md. Implementation has not started.

## Planning and progress

Keep docs/BACKLOG.md as the versioned scope/dependency baseline. Create one GitHub Issue per story, retaining EQ-001 through EQ-092. Epic tracking issues link their child stories. Use GitHub milestones for R0 through R8; milestones represent readiness outcomes rather than promised dates. A Project board tracks Backlog, Ready, In progress, In review and Done. Represent blocked work with an explicit linked dependency/reason, not an unsupported percentage-complete claim.

Issue title: [EQ-001] Freeze v1 feature scope. Issue body: problem/user value, included/excluded scope, acceptance checklist, prerequisites, release, validation and related design links. Labels identify epic and work type (design, feature, test, docs, performance); Project fields track status and release. Avoid maintaining different status lists in markdown and GitHub. GitHub is the work-status authority once set up; backlog markdown remains scope/version history and records deliberate scope changes.

Only move a story to Ready when its required decisions and inputs are available. Limit active implementation work initially to one story or a small explicitly dependent group. Assign authors when work starts rather than inventing ownership. Later-release issues remain backlog. Milestone completion requires its documented acceptance gate; a package can be complete without any proprietary dataset being admitted for production.

## Change delivery

Work on short-lived branches, preferably codex/eq-001-feature-scope when this agent creates a branch. Open a draft PR early for a reviewable design or implementation, include the story ID, and link dependencies. Each PR describes behavior, evidence and limitations. Close a story through a merged change that satisfies its acceptance criteria; a draft PR or code written locally is not completion.

Use the default branch as the coherent reviewed state. Require relevant CI when implemented: tests, typing, package builds and examples. Numerical changes need mathematical fixtures and documented algorithm-version impact. Performance changes need measured comparisons and result parity. Avoid mirroring implementation in tests; verify meaningful independent expected outcomes. Design/docs changes require applicable link/scope checks, not irrelevant computation benchmarks.

Keep consequential architecture/formula decisions in docs/decisions/ with context, choice and consequences; decisions should link affected issues. PR review can be performed with tooling, but don't imply an independent human reviewed work when no human did. Record actual reviewers and validation. Secrets, paid provider data, private code and internal deployment paths are excluded from public fixtures/docs; use synthetic data or explicitly licensed examples.

## Portfolio presentation

README explains the concrete problem, source-independent API, current capabilities, runnable example, installation and honest development status. Include architecture and roadmap links, test/CI badges once real workflows exist, feature definitions and reproducible benchmark methodology. Tag releases only after acceptance; distinguish experimental APIs from stable ones. Show clear engineering choices and results rather than inflated performance claims or fabricated activity.

Use release notes for delivered behavior, compatibility changes and known limitations. Project updates describe meaningful milestones; no obligation to manufacture daily commits. Contribution guide, license, security reporting guidance and issue/PR templates are foundation tasks. Public announcements and profile edits remain user-directed setup work.

## First work item: EQ-001

Start with the feature scope, not code generation. Deliver docs/features/V1_SCOPE.md as a reviewable proposal that maps feature IDs to families, initial windows, input kinds, batch/incremental support, exact versus approximate measures and excluded strategies/labels. Scope completion requires explicit formula-story links and no undocumented promised feature. EQ-002 through EQ-006 settle formulas/timing; contracts and implementation follow those decisions.

Until GitHub setup finishes, store reviewable drafts here and clearly report local-only status. After the repository is available, migrate the documents without overwriting setup work, create/link the first issue and PR, and preserve the numbered backlog. Repository/profile administration stays in the setup conversation; design and implementation stay in this conversation.
