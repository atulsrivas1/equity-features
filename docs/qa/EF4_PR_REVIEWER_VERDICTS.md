# EF4 PR reviewer verdicts (core #729-#731, io #49-#51, workers #93-#94)

Record compiled 2026-10-28 from `gh pr view` (body, reviews, comments, commits) of each merged PR. Nothing here is invented: where GitHub holds no review or comment, the row says so. This is a record of what exists, not a new review and not owner acceptance. Source of the open item: `work/po-verdict-ef4-2026-10-28.md` (baseline gap 4, condition C5).

## Finding

All eight PRs were merged by `atulsrivas1` with zero GitHub reviews, zero PR comments and zero status checks (no CI exists; `check` was removed from branch protection, DECISIONS.md 2026-10-21). No independent reviewer verdict is recorded on GitHub for any of them. Under the standing merge policy (DECISIONS.md 2026-10-22) the coordinator reviewed each diff before merging, which is not an independent review and left no artifact. A reviewer outcome of "not recorded" below means exactly that. Independent read-only reviews for these PRs remain owed (PO condition C5) and must be added as separate records, stating which were done in-session.

## Core (atulsrivas1/equity-features)

| PR | Merge commit | Reviewer outcome (GitHub) | Checks stated in the PR body |
|---|---|---|---|
| #729 feat(ef4): verify gate, ownership headers, capability matrices, open owner items | c3e7257 | Not recorded (0 reviews, 0 comments) | "Verified in pinned venv: all verify_*, check_boundary, delivery-replan pass." Adds `tools/verify_ef4_fixtures.py`, 51 EF4 headers (59 = 8 planned + 51) with `check_ef4_header_parity`, capability matrices in the 4 contract docs, E1-E9 as open owner items. |
| #730 docs: decide tape coverage fails closed (pending owner review) | 2a7a0c2 | Not recorded | Body: "DECISIONS.md entry; no contradiction with E2 or the tape contract." No checks listed. 1 file, +1. |
| #731 docs: align EF4 tape coverage text with fail-closed ruling | 932b1ca | Not recorded | "Checks pass: check_equity_delivery_replan, verify_ef4_fixtures, check_boundary." 2 commits, 4 doc files, +12/-12. |

## io (atulsrivas1/equity-feature-io)

| PR | Merge commit | Reviewer outcome (GitHub) | Checks stated in the PR body |
|---|---|---|---|
| #49 fix(io): clear remaining 13 mypy --strict errors | 4f5e9e1 | Not recorded | mypy --strict `packages/duckdb/src` clean (mypy 1.15.0); `tools/check_extraction.py` passes; io tests per subdir all OK (acquisition 32, bundles 29, duckdb-sink 27, duckdb 94, ef1 176, extensions 12, files 43, matrix 6, parquet 28); ef3 refusals 62/62, 48/48, 48/48. Out of scope: 2 pre-existing strict errors in `examples/`. |
| #50 fix(io): EF4 projections never default known_at (D1) | 9acb255 | Not recorded | check_extraction, mypy --strict (packages src), io tests per subdir pass. Not changed: tape coverage default (D2), left for a ruling. |
| #51 fix(io): tape coverage fails closed | 31590b1 | Not recorded | Tape refusals 73/75 (RF18, RF35 known); mypy strict, check_extraction, io tests pass. |

## workers (atulsrivas1/equity-feature-workers)

| PR | Merge commit | Reviewer outcome (GitHub) | Checks stated in the PR body |
|---|---|---|---|
| #93 fix(workers): EF4 drivers supply fixture ka explicitly, surface worker_contract_code | 860f2ea | Not recorded | Projections 114/114 refusals and 111/111 results; tape 73/75 (RF18, RF35 known); quote_vwap 80/80; path_efficiency 39/39. Requires io #50. |
| #94 fix(workers): tape drivers declare coverage explicitly | b15d708 | Not recorded | Tape refusals 73/75 (RF18, RF35 known). Pairs with io #51. |

## Caveats

- Check results are the author's statements in the PR bodies; this record did not rerun them. The core gate (`tools/pre_merge_check.py`) was run on 2026-10-28 on origin/main plus this PR (see the PR body).
- `path_efficiency` driver still carries the K-50 token (PO verdict, same class as D1); not addressed by these PRs.
- No PR in this set has a linked independent reviewer artifact (`work/retro-review-*ef4*` does not exist).
