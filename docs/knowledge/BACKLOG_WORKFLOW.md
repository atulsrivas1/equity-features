# Backlog and learning workflow

Use [BACKLOG.md](../BACKLOG.md) as the versioned scope baseline and the live [Project](https://github.com/users/atulsrivas1/projects/2) as status authority. This process supplements [delivery policy](../DELIVERY_POLICY.md); it does not create a competing story list or change current execution ownership.

## Prepare the next work

1. Read the latest owner direction, handoff, selected release gates, current issue and dependencies. Check open PRs and active owners before choosing work.
2. Identify the decision that needs evidence: an unresolved contract, reproducible defect, inadequate coverage, unverified delivery, consumer usability or measured performance bottleneck. Consult [lessons](LESSONS.md) so previously rejected assumptions do not reappear under another name.
3. Extend an existing story when its acceptance already covers the need. Create a numbered issue only for distinct scope; preserve IDs, retired IDs and release assignments. Record affected epic/dependencies and explicit blocked reason.
4. Rank dependency and correctness work before added capabilities. Prefer the smallest comparison that resolves uncertainty. A later-release idea can remain valuable without becoming Ready or interrupting the current owner.
5. Before implementation, publish story points as provisional complexity, first actions, mathematical/design choices, open questions, independent tests, documentation, and the exact accepted end state. Points are not days or measured velocity.

Ready requires established scope, acceptance, inputs and prerequisites. Pull only the highest-priority dependency-satisfied Ready story in the authorized release. Routine work proceeds within existing authorization; ask only for consequential missing scope/access choices, public commitments or destructive actions under the work agreements. If blocked, continue independent preparation and state the exact dependency.

## Learn while delivering

Freeze source/protocol identities for meaningful checks. Use independent expected results, temporal/precision/admission cases and relevant mode parity. Record failed builds/reviews and corrected versions; never count a superseded green run as evidence for changed code without justification.

Update formulas/API/examples/decision records with the story, including explicit no-impact decisions. Link review concerns and actual reviewer identity. Follow each lifecycle stage using its evidence. For installable changes, verify the declared main artifacts and clean installation; docs-only delivery uses its applicable checks and published-source verification. Do not create unrelated benchmarks or tests for a small documentation edit.

After a result or correction:

- Update the scoped lesson and supporting/contradicting evidence.
- Reconcile affected issue acceptance/dependencies/status rather than creating duplicate trackers.
- Record any superseded assumption or scope change and its owner/source.
- Refresh the handoff with actual completed work, remaining gate, owner, version and exact next step.
- Explain the top three priorities and why they outrank alternatives, while retaining blocked/rejected ideas and revisit conditions.

If new literature is useful, read current primary documentation/papers for the concrete gap and record version, sections read, claim and local validation plan. Published claims do not become library semantics without a versioned decision and verification. Do not start a trading-research program inside the feature package project.

## Current priority decision to preserve

October 5 owner direction: finish BUG-003/BUG-004 deliveries with their repair owner, verify GOV-010 handoff publication, complete R2, then assess R3 readiness. EQ-095 remains later consumer qualification; automated reviewer activation remains deferred. Recheck live status before executing: this paragraph is a dated decision record, not a claim about today's completed gates.

Knowledge transfer and new-checkout preparation authorize no automatic worker, reminder or recurring schedule. Every future session should read current repository knowledge and update it after meaningful work.
