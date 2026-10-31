# DV1 PR reviewer verdicts (core #753, #755-#760, #762; io #67; workers #110, #112)

Record compiled 2026-10-31 for RL-01-03 from `gh pr view` (body, reviews, comments, commits) of each merged PR, from DECISIONS.md, and from the recorded reviewer verdict files in the coordinator `work/` folder (git-ignored, so not part of this repository; named per row). Nothing here is invented: where no verdict text exists the cell says "not recorded". This is a record of what exists, not a new review and not owner acceptance. Internal, synthetic, pre-release. Layout follows `docs/qa/EF4_PR_REVIEWER_VERDICTS.md`.

## Finding

The PRs are the merged DV1 PRs named in or implied by the DECISIONS.md rows dated 2026-10-29 to 2026-10-30. Those rows name few PR numbers, so the set was completed from the "DV1-..." PR titles and from #110 and #112 named in the 2026-10-30 rows. GitHub shows 0 reviews, 0 comments and 0 status checks on every PR below (no CI exists). Each PR was reviewed by a fresh independent read-only agent whose verdict was saved as a file in `work/` and reported to the coordinator; the verdicts below relay those files and were not re-observed here. The reviewed head is stated per row; where it differs from the merged head, the later commits have no recorded review ("not recorded"). Merges were done by the coordinator (account atulsrivas1).

Excluded: core #761 (DV1-5a) is OPEN, not merged (a review file exists, `work/review-core-761-2026-10-29.md`). Workers #109 (io-contracts pin fix, merged 2026-10-30) is not named in DECISIONS.md and is not listed.

## Core (atulsrivas1/equity-features)

| PR | Merge commit | Merged head | Reviewed head and file | Reviewer verdict (independent agent, saved file) | Findings and outcome | Checks stated in the PR body |
|---|---|---|---|---|---|---|
| #753 DV1-0 draft contract, fixtures, gate | c0ffede | aeec747 | eae10e6, `work/review-core-753-2026-10-29.md`; delta eae10e6 to aeec747, `work/review-core-753-delta-2026-10-29.md` | APPROVE (two non-blocking notes); delta APPROVE (one cosmetic note) | Q-1 operand note (settled by PO rulings Q-1..Q-4, checked in the delta); grammar nit "an DV1 output" recorded, fix not recorded | Docs, fixtures, gate `verify_dv1_fixtures`; 100 result fixtures, 72 refusals. Body: earlier head approved, delta pending at that time |
| #755 DV1-1 relative.log_return_beta and correlation | b049b6c | 25bd550 | 7c96c61, `work/review-core-755-2026-10-29.md` | APPROVE WITH CHANGES (no blocker; two follow-ups, three notes) | `evidence_limit` builder default versus the "no default" contract; config check order. A second commit "PO rulings on DV1-1" followed; re-review not recorded | `pre_merge_check --installed` all pass except 3 environment-only failures; verify_ef5_library 89/534/59/12; mypy --strict clean |
| #756 DV1-6 window extremes | 9d457db | 365642a | 336c244, `work/review-core-756-2026-10-29.md`; delta 336c244 to 365642a, `work/review-core-756-delta-2026-10-29.md` | APPROVE (three non-blocking suggestions); delta APPROVE (two non-blocking notes) | Suggestions on the `offset_unit` build argument and stage order; the contract erratum was reviewed in the delta | Gate `verify_dv1_window_library` 25 fixtures (125 runs), 10 refusals; `pre_merge_check --installed` 26/26; mypy --strict clean |
| #757 DV1-2 history.atr_simple_mean | 49903df | 988a623 | 988a623, `work/review-core-757-2026-10-29.md` | APPROVE (no blocking findings; three non-blocking notes) | Notes only | `verify_dv1_atr_library` 20 results, 27 refusals; `pre_merge_check --installed` 27/27; mypy --strict clean |
| #758 DV1-3 core spread range and population stdev | 07f5736 | 3f06234 | ad8d726, `work/review-core-758-2026-10-29.md` | APPROVE WITH CHANGES (no blocking finding; two small non-blocking changes; four decisions accepted) | One change concerns a legs batch declaring a different adjustment. Commits "PO rulings on DV1-3" and "reviewer follow-ups on #758" followed; re-review not recorded | `verify_dv1_core_spread_library` 21 results, 16 refusals plus RF22; `pre_merge_check --installed` 29/29 |
| #759 DV1-5b core-spread witnesses to slot ordinals | 9888351 | 294a172 | 294a172, `work/review-core-759-2026-10-29.md` | APPROVE (two cosmetic nits, no change required) | Nits only | `pre_merge_check --installed` 29/29; counts unchanged; negative check on an injected `leg:` literal |
| #760 DV1-4a session.price.range_over_open | 9d12412 | 4694462 | a5b9b7d, `work/review-core-760-2026-10-29.md` | APPROVE WITH CHANGES (one mechanical change: rebase onto #759) | DECISIONS.md tail conflict; nits on strict mypy in the gate file and golden indentation. Merged head differs from reviewed head; re-review not recorded | Gate `verify_dv1_range_over_open_library`; mutation check fails 41 of 132; versions deliberately not moved (C2 follows) |
| #762 DV1-4 coordinated bump, C2 and C3 | 967d13d | ba5d3f8 | 7b53e5e, `work/review-core-762-2026-10-30.md` | APPROVE WITH CHANGES (small, none blocks the merge) | F1 wording change on the bundles dependency in `docs/PRERELEASE_BUMP_DV1.md`; F2 to F5 notes (gate narrowness, stale `SIBLINGS`, cosmetic, cascade reminder). A third commit "tighten the bump label relaxation" followed; re-review not recorded | Details in `docs/PRERELEASE_BUMP_DV1.md`; four sibling-dependent builders left open (body) |

## io (atulsrivas1/equity-feature-io)

| PR | Merge commit | Merged head | Reviewed head and file | Reviewer verdict (independent agent, saved file) | Findings and outcome | Checks stated in the PR body |
|---|---|---|---|---|---|---|
| #67 DV1-4 bump, io side (I3) | 3c94be6 | 725d849 | ca7a43c, `work/review-io-67-2026-10-30.md` | APPROVE WITH CHANGES (one change: bump bundles 0.1.0a2 to 0.1.0a3, or an explicit PO re-ruling of D4 for bundles) | Finding 1 bundles pin-only; Finding 2 minor doc accuracy. How Finding 1 was settled is not recorded in the PR; merged head differs from reviewed head | Body lists versions moved and points to `docs/PRERELEASE_BUMP_DV1.md`; no check list in the body |

## workers (atulsrivas1/equity-feature-workers)

| PR | Merge commit | Merged head | Reviewed head and file | Reviewer verdict (independent agent, saved file) | Findings and outcome | Checks stated in the PR body |
|---|---|---|---|---|---|---|
| #110 DV1-4 bump, workers side (K3) | 6c3123c | f629f7e | f629f7e, `work/review-workers-110.md` | APPROVED (no blocking findings; three non-blocking notes) | Notes: unmoved `IO_COMMIT` and qualify pins to be stated in the record; CHANGELOG wording "numeric results unchanged" should say bars gain a 13th column. DECISIONS 2026-10-30 rules provenance a5 acceptable | verify_versions, verify_ef5_worker 89/534/59, mypy --strict, unit suites; eight builders exit 0 with repeat equality |
| #112 re-pin to core f43434b and io e47b0c5 (named in the DECISIONS 2026-10-30 row; merged 2026-10-31) | 474f79d | 9fcb818 | 9fcb818, `work/review-workers-112.md` | APPROVE / PASS (reviewer and tester, independent) | Observations only: workers pin 6c3123c is not the current workers main; the core-side `SIBLING_COMMITS` re-pin follows | Pins consistent; build_foundation and build_mcp_evidence exit 0; build_provenance exit 0 from a short path |

## Caveats

- Check results are the authors' statements in the PR bodies and reviewer files; this record did not rerun them.
- The verdict files live in the git-ignored coordinator `work/` folder; they are not reproduced here and are not verifiable from GitHub.
- Where a PR merged at a head later than the reviewed head, the commits after the reviewed head have no recorded review.
- The one open DV1 PR, core #761, is out of scope until merged.
