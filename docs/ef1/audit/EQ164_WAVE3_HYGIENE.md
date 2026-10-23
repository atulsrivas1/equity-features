# EQ164 wave 3, story W3-C: plan hygiene corrections

October 22, 2026. Docs and plan hygiene only. Nothing here is acceptance: full EQ164 stays open, no mathematics, API, source, rights or consumer equivalence is accepted, no row is Ready, and no tracker issue was created or edited. Opaque ids only. All additions are coordinator working decisions, pending owner review.

Inputs: [X4 section 7](EQ164_WAVE2_X4.md), [selected slice B](EQ164_SELECTED_B.md), [wave 1 decisions](EQ164_WAVE1_DECISIONS.md), [wave 2 decisions](EQ164_WAVE2_DECISIONS.md), [X1](EQ164_WAVE2_X1.json), [X2](EQ164_WAVE2_X2.json) and [the publication record](../AUDIT_ROUTE_PUBLICATION.md).

## What changed

1. `docs/plans/equity-selected-dependencies.json`: the four edges (#491, #611, #612, #519) had `publication_status` `draft_dependency_append_not_applied`. The value is now `published_and_read_back`, with an added `publication_source` field citing the "Actual selected dependency publication readback" section of `docs/ef1/AUDIT_ROUTE_PUBLICATION.md`. No other record or field changed. The other seven records still have no status field (X4 finding, not fixed here).
2. `docs/plans/equity-output-ownership.json`: one new top-level key `proposed_unaccepted_outputs` with three entries, each marked `PROPOSED_UNACCEPTED`, `accepted: false`, `planned_ownership_accepted: false`: the #626 adaptive outputs, the #490 mean companion, and the #598 observed-population companion. They are deliberately outside the `outputs` array so the accepted 47-output count and per-owner counts stay intact. Only stated facts are recorded (owner, release, role, opaque ids, the seven-output count for #598). Canonical names, units, operands, and the #626 output count are not stated in the audit docs, so they are null, with a note per entry. The mean companion has no numbered story yet. The wave 1 A2 entries (#506 diagnostic, retracement level, #513 raw profiles) are not added here because this task scoped three groups; they remain open.
3. `docs/plans/equity-audit-route-coverage.json`: for the 13 rows whose exclusion was rejected (C0034, C0099, C0257, C0187, C0029, C0280, C0281, C0284, C0290, C0291, C0140, C0132, C0135) a new additive field `audit_wave2_adjudication` holds the verdict `REJECT_EXCLUSION`, the retained component kinds with owner stories as stated in X1/X2, the source document, and the status "coordinator-decided, pending owner review". Existing fields, including `no_retained_component_requires_individual_exclusion_review`, the empty retained-component list and the evidence hashes, are unchanged, so the historical proposal stays visible beside the adjudication. The old flag is therefore contradicted by the new field, not rewritten.

`equity-delivery-replan.json` is unchanged; `tools/check_equity_delivery_replan.py` passes before and after.

## Not done

Other X4 section 7 items (record schema consistency, hidden #489 edge records, group label tidy-up, source head snapshot note, the "accepted" flag renaming, encoding damage in a milestone title) and the 16 plus 11 plus 1 owner-decision rows are out of scope.

## Proof

A scratch comparison loaded each file from `origin/main` and from the branch and asserted that removing exactly the additions (the two status fields on four records, the one new key, the 13 new row fields) restores the original document. Line endings (CRLF) are preserved; the diff is additive (358 insertions, 17 deletions, the deletions being status lines and trailing-comma changes).
