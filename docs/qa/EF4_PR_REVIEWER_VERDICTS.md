# EF4 PR reviewer verdicts (core #729-#731, io #49-#51, workers #93-#94)

Record compiled 2026-10-28 from `gh pr view` (body, reviews, comments, commits) of each merged PR. Nothing here is invented: where GitHub holds no review or comment, the row says so. This is a record of what exists, not a new review and not owner acceptance. Source of the open item: `work/po-verdict-ef4-2026-10-28.md` (baseline gap 4, condition C5).

## Finding

Each PR was reviewed before merge by a fresh independent read-only reviewer agent. The outcomes were posted to the coordinator, not on GitHub: GitHub shows 0 reviews, 0 comments and 0 status checks on all eight PRs (no CI exists). The evidence for the reviewer outcomes is therefore agent transcripts plus coordinator notes, not GitHub review artifacts, and this record relays them (coordinator message, 2026-10-28); it did not re-observe them. Merges were done by the coordinator (account atulsrivas1) after approval. A durable reviewer artifact in the repo (`work/retro-review-*ef4*`) still does not exist.

## Core (atulsrivas1/equity-features)

| PR | Merge commit | Reviewer outcome (independent agent, reported to coordinator) | Checks stated in the PR body |
|---|---|---|---|
| #729 feat(ef4): verify gate, ownership headers, capability matrices, open owner items | c3e7257 | APPROVE. Reviewer ran the EF4 gate, boundary and replan checker; mutation tests (altered fixture count, removed manifest entry) each made the checks fail | "Verified in pinned venv: all verify_*, check_boundary, delivery-replan pass." Adds `tools/verify_ef4_fixtures.py`, 51 EF4 headers (59 = 8 planned + 51) with `check_ef4_header_parity`, capability matrices in the 4 contract docs, E1-E9 as open owner items. |
| #730 docs: decide tape coverage fails closed (pending owner review) | 2a7a0c2 | APPROVE | Body: "DECISIONS.md entry; no contradiction with E2 or the tape contract." No checks listed. 1 file, +1. |
| #731 docs: align EF4 tape coverage text with fail-closed ruling | 932b1ca | REQUEST CHANGES (md/json mirror divergence, quote escaping), then APPROVE at 93e3abc | "Checks pass: check_equity_delivery_replan, verify_ef4_fixtures, check_boundary." 2 commits, 4 doc files, +12/-12. |

## io (atulsrivas1/equity-feature-io)

| PR | Merge commit | Reviewer outcome (independent agent, reported to coordinator) | Checks stated in the PR body |
|---|---|---|---|
| #49 fix(io): clear remaining 13 mypy --strict errors | 4f5e9e1 | APPROVE. mypy duckdb src clean; 20 digests verified as blob hashes; tests per subdir; refusals 62/48/48. Noted: ef1 whole-dir discover crashed natively once, per-file passes | mypy --strict `packages/duckdb/src` clean (mypy 1.15.0); `tools/check_extraction.py` passes; io tests per subdir all OK (acquisition 32, bundles 29, duckdb-sink 27, duckdb 94, ef1 176, extensions 12, files 43, matrix 6, parquet 28); ef3 refusals 62/62, 48/48, 48/48. Out of scope: 2 pre-existing strict errors in `examples/`. |
| #50 fix(io): EF4 projections never default known_at (D1) | 9acb255 | APPROVE. All callers checked; default gone outside the fixture opt-in | check_extraction, mypy --strict (packages src), io tests per subdir pass. Not changed: tape coverage default (D2), left for a ruling. |
| #51 fix(io): tape coverage fails closed | 31590b1 | APPROVE. Probe: rows without coverage refuse INVALID_SCHEMA, zero rows stay empty/complete; other TradeSupply callers fixed | Tape refusals 73/75 (RF18, RF35 known); mypy strict, check_extraction, io tests pass. |

## workers (atulsrivas1/equity-feature-workers)

| PR | Merge commit | Reviewer outcome (independent agent, reported to coordinator) | Checks stated in the PR body |
|---|---|---|---|
| #93 fix(workers): EF4 drivers supply fixture ka explicitly, surface worker_contract_code | 860f2ea | APPROVE | Projections 114/114 refusals and 111/111 results; tape 73/75 (RF18, RF35 known); quote_vwap 80/80; path_efficiency 39/39. Requires io #50. |
| #94 fix(workers): tape drivers declare coverage explicitly | b15d708 | APPROVE. Note: reviewer saw 23 workers pytest failures in its own environment (missing anyio), not confirmed on base | Tape refusals 73/75 (RF18, RF35 known). Pairs with io #51. |

## Caveats

- Check results are the author's statements in the PR bodies; this record did not rerun them. The core gate (`tools/pre_merge_check.py`) was run on 2026-10-28 on origin/main plus this PR (see the PR body).
- `path_efficiency` driver still carries the K-50 token (PO verdict, same class as D1); not addressed by these PRs.
- Reviewer outcomes are not verifiable from GitHub; see Finding.
