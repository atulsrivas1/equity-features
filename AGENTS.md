# Work agreements

These are the human owner's agreed project rules. Read this file, docs/PUBLIC_DEVELOPMENT.md, docs/SESSION_HANDOFF.md and the current issue/Project status before starting work. Keep durable project memory in these tracked documents rather than assuming chat memory persists.

1. Work publicly through numbered GitHub stories, epic links, release milestones and linked pull requests. GitHub Project status is the current work-status authority; docs/BACKLOG.md records versioned scope and dependencies.
2. Follow the backlog. Satisfy acceptance criteria and release gates before declaring completion. Record changes in scope and consequential decisions explicitly.
3. Keep calculation packages source-independent. No fetching, database/file access, credentials, job scheduling or output publication inside calculations. Adapters and workers remain separate.
4. Define mathematics first: formulas, units, timing, initialization, coverage and edge cases before implementing a feature.
5. Verify correctness with independent fixtures and relevant tests. Support performance claims with measured benchmarks and result parity. Never invent review, validation or acceptance evidence.
6. Preserve privacy and rights. Public examples use synthetic or explicitly licensed data. Never publish credentials, private datasets or code without established permission.
7. Work autonomously within agreed scope. Make routine implementation choices; ask when changing scope, public commitments or performing destructive actions. Preserve unrelated work.
8. Update continuity after meaningful decisions, changes, failures and validation. Record current evidence, remaining work and exact resume steps in docs/SESSION_HANDOFF.md. Never claim unfinished work is completed.
9. Library design and implementation belong in the development conversation. GitHub profile/account administration belongs in the separate setup conversation. This development conversation manages the project's issues, dashboard and delivery workflow as authorized.
10. Report planned, implemented, reviewed, tested, released and completed work distinctly. Update GitHub status as actual work changes; do not leave an active story in Backlog or close a merely merged implementation awaiting release.
11. Use the exact lifecycle: Backlog -> Ready -> In progress -> Code review -> Test -> Ready to release -> Released -> Done. Apply entry/exit criteria in docs/PUBLIC_DEVELOPMENT.md. Rework returns to the correct earlier state; blocked reasons/dependencies are explicit. Do not fabricate transitions or skip required evidence.
12. Documentation is part of every story. Update relevant GitHub issue acceptance/evidence, public design/API/examples/decision/release documentation and linked PR alongside the change. Document no-impact decisions when appropriate. Documentation cannot be deferred to a later cleanup story to declare this story complete.

Use short-lived codex/ branches when this agent creates branches. A human approval is required only where the user or applicable review policy requires it; do not invent an approval requirement. Record actual reviewer identity and limitations. Numerical tests and release gates remain mandatory even when work is autonomous.

Delivery uses release-based planning and continuous pulling, not mandatory sprints. Read docs/DELIVERY_POLICY.md. Start the highest-priority dependency-satisfied Ready story, initially one active story at a time. Review progress weekly during active work; release dates are evidence-based forecasts, with no invented deadlines or automated reminders.
