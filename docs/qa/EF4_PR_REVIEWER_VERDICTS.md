# EF4 PR reviewer verdicts (core #729-#731, io #49-#51, workers #93-#94; later PRs in the last section)

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

## Later PRs (added 2026-10-28, after the PO re-check)

Compiled from `gh pr view` (body, reviews, comments, commits) of each merged PR on 2026-10-28. For every PR below GitHub holds 0 reviews and 0 status checks (no CI). The only comments are the three coordinator "Update per PO rulings" notes on the bump PRs. **No reviewer verdict text for any of these PRs exists in the repositories or on GitHub, and this record does not invent one.** The reviewer outcome column is therefore "not recorded here": whatever independent-agent verdicts were given went to the coordinator in session (coordinator notes only), and a record of them has to come from the coordinator (see Open item). The only reviewer-related evidence is that the nit PRs below describe themselves as fixing "review nits". Head sha is the PR head at merge (`headRefOid`); the checks column is the author's statement in the PR body, not rerun here.

| Repo | PR | Head sha | Merge commit | Reviewer outcome | Nits and outcome | Checks stated in the PR body |
|---|---|---|---|---|---|---|
| core | #734 E1/E2/E4 rank-aware TopKTrades, fail-closed coverage, window <= 63 | 9221371 | 85f9fe1 | not recorded here | none on GitHub | verify_ef4_errata (ER01-ER08), verify_ef4_fixtures pin; 3 commits, 12 files |
| core | #737 errata ER09-ER11, error-code split | a3736dd | abe6331 | not recorded here | none on GitHub | verify_ef4_errata, verify_ef4_fixtures, check_equity_delivery_replan pass; pre_merge_check failed only verify_compatibility (local numpy/pyarrow pin mismatch, environment) |
| core | #738 compatibility note, notional cells under same version | f0df5eb | 39bf727 | not recorded here | none on GitHub | docs only |
| core | #739 coordinated bump contracts a5 / features a6 | aed8a43 | 710fe05 | not recorded here | coordinator comment: revised per PO rulings (evidence a3 cascade) | pre_merge_check --installed 22/22, repeat-build 27/27, qualify smoke |
| core | #740 builder re-pin | 89dfe2c | 4462b25 | not recorded here | scope-entry nit PRs #741 and #744 follow it (inferred from their bodies, not from a reviewer record) | verify_versions, pre_merge_check --installed 22/22; builders listed in PRERELEASE_BUMP_A5_A6.md as not run |
| core | #741 drop nonexistent workflow scope entries | c08b292 | d977c60 | not recorded here (body: "Review nit") | the nit fix itself | py_compile only |
| core | #744 drop remaining nonexistent scope entries | eedf488 | 3af2d99 | not recorded here | closes the same nit class for six more builders | compile only |
| core | #742 EF5 library [1/2] | 2fab246 | 9a91572 | not recorded here | none on GitHub | check_intraday_boundary, mypy intraday at 13 baseline errors, tests/intraday 78 OK, tests/unit 1075 OK |
| core | #743 EF5 fixture gate [2/2] | 82a8c4a | 20a57ee | not recorded here | seven ambiguities listed in EF5_LIBRARY_IMPLEMENTATION.md (author-declared, not reviewer nits) | tools/verify_ef5_library.py 89 results (534 runs), 57 refusals, 12 codes; pre_merge_check 23/23 |
| io | #54 notional cells in bundles/codec, tape coverage never defaults | 97feb48 | cc8313f | not recorded here | none on GitHub | check_bundles 35 branches, check_extraction, verify_ef4_notional_cells |
| io | #55 compatibility note | c40087c | 0942351 | not recorded here | none on GitHub | docs only |
| io | #56 bump | 16742b2 | f889426 | not recorded here | coordinator comment: bundles admits evidence a3, oracle manifest regenerated | all io suites, ef1 per file, checks and mypy rerun green (comment) |
| io | #57 builder re-pin | 189bfcd | b2ed938 | not recorded here | none on GitHub | verify_versions; builders not run listed in PRERELEASE_BUMP_A5_A6.md |
| io | #58 EF5 supplied price-structure inputs | 6d5774f | 106897a | not recorded here | none on GitHub | verify_ef5_io 89 results (534 runs), 59 refusals/12 codes, check_extraction (EF1_SOURCE_EVOLUTION sha refreshed), mypy --strict duckdb src clean, tests/duckdb 94 OK |
| workers | #97 bump | dc4a2a3 | 2222d43 | not recorded here | coordinator comment: mcp 0.1.0a2 with evidence extra at a3 | full suite 484 OK, drivers and qualify smoke rerun green (comment) |
| workers | #98 builder re-pin | 428a63d | 7acd655 | not recorded here | nit PR #99 follows it (inferred from its body) | verify_versions; builders not run listed in PRERELEASE_BUMP_A5_A6.md |
| workers | #99 name same-as-main failing suites, drop nonexistent scope | 7e5f611 | c279001 | not recorded here (body: "Review nits") | the nit fix itself | docs and scope only |
| workers | #100 EF5 workers layer plan | 79ae4ea | efa0fbf | not recorded here | none on GitHub | plan only, no code |

### Open item

The independent-agent verdicts for the rows above, and for #729-#731, #49-#51 and #93-#94, exist only in coordinator session notes. PO ruling 7 for EF5 (reviewer verdicts are artifacts merged before the layer PR) means they should be written to `work/retro-review-*.md` or here by the coordinator or reviewer who gave them. The independent docs review of the EF4 documents is also not done.
