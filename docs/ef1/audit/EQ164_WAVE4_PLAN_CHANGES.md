# EQ164 wave 4, story W4-B: plan changes implied by wave 2 and 3 decisions

October 22, 2026. Plan hygiene only. Nothing here is acceptance: full EQ164 stays open, no mathematics, API, source, rights or consumer equivalence is accepted, no row is Ready, and no tracker issue was created or edited. Opaque ids only. Every addition is a coordinator working decision, pending owner review. Method as in [wave 3 hygiene](EQ164_WAVE3_HYGIENE.md): additive fields only, no existing field altered. Inputs: [wave 3 decisions](EQ164_WAVE3_DECISIONS.md), [wave 2 decisions](EQ164_WAVE2_DECISIONS.md), [watchlists](EQ164_WAVE3_WATCHLISTS.json), [scanners 1](EQ164_WAVE3_SCANNERS_1.json) and [scanners 2](EQ164_WAVE3_SCANNERS_2.json).

## What changed

1. `docs/plans/equity-audit-route-coverage.json`: new additive field `audit_wave3_adjudication` on 132 rows, each with the resolution class, source document and the status "coordinator-decided, pending owner review".
   - 25 watchlist rows: class from the watchlists report, `common_operand_set_id` `common33`, decision W3A-1. W0014 (7 members) and W0015 (6 members) also carry `watchlist_membership_dependencies` exactly as in the report, decision W3A-3.
   - 107 ambiguous scanner rows: class only (46 resolved with all operands covered, 55 resolved with gaps, 6 still ambiguous) from the scanners 1 and 2 reports. No operand lists are copied.
   - S0172 and S0189 additionally carry `dormant_declaration`: recorded as dormant declarations with no selected emitter, not consumers, decision D6, pending the owner's view on retiring them. Their existing `dormant_declaration_retained` flag is unchanged.
2. `docs/plans/equity-selected-dependencies.json`: two records appended, both `status` `proposed_not_applied`, existing records untouched.
   - W4B-PROPOSED-1 (W3A-5): #489 baseline as a required supplied validation input for the common validation of the 25 watchlists. The target is recorded as #518 (the watchlist policy owner in the route coverage), flagged for owner confirmation because the decision names no target story.
   - W4B-PROPOSED-2 (Q3): provisional dependency of S0338, S0339, S0353 and S0354 on EQ-239 (#664), unless the #489 cohort freeze is proved sufficient. `target_issue` is null because no target story is stated.

## Decisions not applied to plans, and why

- W3A-2 (retire the "six with extra joins" statement): that statement lives in the report, not in a plan file; nothing to edit additively.
- W3A-4 (proposed owner #518 with I/O #621 for three shared policy inputs): unconfirmed and no story is mapped; a contract must confirm.
- W3A-6 and the W-id mapping: an owner item.
- D1 to D5, D7 to D9H, Q1, Q2, Q4 to Q8: contract, proof or procedure decisions with no plan field to change. D7 (withdraw the #21 primitive proposal) would alter existing `prior_primitive_proposals_for_review` content, which this additive-only change does not do.
- Per-field delivery (Q4): a wave 4 audit task, not a plan edit.

## Proof

A scratch script loaded each file from `origin/main` and from the branch and asserted that removing exactly the additions (132 row fields; the two appended records) restores the original document. Line endings unchanged. `python -I tools/check_equity_delivery_replan.py` passes (47 planned outputs, 35 existing stories, 18 proposed tasks, 8 releases, 1 supplemental story).
