# EF4 delivery evidence (EF4 package)

October 24, 2026. Evidence summary for the EF4 release (tape windows and notional top-K, quote dynamics and VWAP path, path efficiency and choppiness, equity statistical projections). This is delivery evidence, not acceptance: **EF4 is delivered, not accepted.** EQ-158, EQ-159, EQ-160, EQ-161, EQ-162 and EQ-172 acceptance is not done, and every decision recorded here is a coordinator decision, pending owner review. Merge facts below were read from GitHub and git on this date. Verdicts, fixture counts and timings are taken from the documents named in each section and were not re-run for this package.

## Scope delivered

| Contract | Stories | Producers | Headers | Frozen contract |
| --- | --- | --- | --- | --- |
| G: tape window and notional top-K | EQ-158, EQ-162 | `ef4.tape_window_sign`, `ef4.trade_top_k_notional` | 10 | `docs/ef4/TAPE_CONTRACT_PROPOSAL.*` (#704) |
| H: quote dynamics and VWAP path | EQ-159, EQ-160 | `ef4.quote_dynamics`, `ef4.vwap_path` | 16 | `docs/ef4/QUOTE_VWAP_CONTRACT_PROPOSAL.*` (#703) |
| I1: path efficiency and choppiness | EQ-161 | `ef4.path_efficiency` (hosted in packages/intraday, ruling E5) | 7 | `docs/ef4/PATH_EFFICIENCY_CONTRACT_PROPOSAL.*` (#705) |
| I2: equity statistical projections | EQ-172 | `ef4.session_projection`, `ef4.bar_projection`, `ef4.relative_excess`, `ef4.rate_projection` | 26 | `docs/ef4/PATH_PROJECTIONS_CONTRACT_PROPOSAL.*` (#705) |

59 new headers and 9 producers in total (source: `docs/ef4/EF4_SHARED_AMENDMENT.md`, section a). The frozen `docs/ef1/CONTRACT.json` is unchanged. The shared amendment is `docs/ef4/EF4_SHARED_AMENDMENT.*` (#713); nothing in it is accepted. The four contracts are not accepted either.

## PRs merged (merge commits read from GitHub)

Core repository (equity-features). Times are UTC.

| PR | Layer | Merge commit | Merged |
| --- | --- | --- | --- |
| #703 | Contract H | `46d38e2` | Oct 23 21:20 |
| #704 | Contract G | `e25b44d` | Oct 23 21:23 |
| #705 | Contract I1 and I2 | `609d16e` | Oct 23 21:32 |
| #706 | Library G | `c0afee0` | Oct 23 21:47 |
| #707 | Library H | `55455fe` | Oct 23 21:49 |
| #710 | Library G fix (drop bisect import) | `c4042b8` | Oct 23 21:50 |
| #708 | Library I1 | `bbb39cd` | Oct 23 21:52 |
| #709 | Library I2 | `2517ce5` | Oct 23 22:04 |
| #711 | Tools: vendored fixture expanders | `b6c5063` | Oct 24 01:04 |
| #712 | Handoff for release close | `c4e4c70` | Oct 24 01:40 |
| #713 | Shared amendment (producer set, ledger, rulings E1 to E9) | `a18f6fd` | Oct 24 02:11 |

Sibling repositories (equity-feature-io, equity-feature-workers).

| Contract | I/O PR | Merge commit | Workers PR | Merge commit |
| --- | --- | --- | --- | --- |
| G | io #41 | `77fde51` | workers #86 | `51f5e7f` |
| H | io #39 | `2f9c14c` | workers #84 | `c506d94` |
| I1 | io #40 | `19a5dde` | workers #83 | `be86298` |
| I2 | io #42 | `4ebfa30` | workers #85 | `8109c52` |

io main at the end of the build is `4ebfa30`; workers main is `51f5e7f`. Installed Windows qualification is core PR #714, **merged** (squash, merge commit `ab80b98`, October 24 03:19 UTC).

## How each part was verified

- Review (not auditable from GitHub): reviews were done by subagents and reported to the coordinator in session; no verdict artifact exists, so independence and outcome cannot be verified from the repository; merges were made with the owner's account, so no GitHub approval could exist. The handoff records that an independent reviewer recomputed each unit and that the coordinator merged some PRs after reading the diff and the reviewer verdict. The PRs on GitHub carry no review objects or comments (0 on core #703 to #713, io #39 to #42 and workers #83 to #86), and no per-PR verdict text was found in the repository docs. Per-PR reviewer verdicts are therefore not recorded in any source read here and are not restated.
- Author manual runs (implementation docs `docs/ef4/*_IMPLEMENTATION.md`, author-reported, no unit tests by policy): G 82 of 82 result fixtures and 75 of 75 refusals under two identity bindings, with a deliberately broken tick carry and a size-ranked insertion failing the script (negative control); H 69 of 69 results and 80 of 80 refusals under three id sets, plus 1000 seeded random fixtures per id set against an independent stdlib recompute harness (no mismatch); I1 31 of 31 results and 39 of 39 refusals under two bindings, plus 400 random cases; I2 111 of 111 results (340 outputs, 1360 cells) and 114 of 114 refusals under two bindings and both availability modes, with a negative control.
- Shared amendment #713: the dtype and unit of all 59 headers were compared with the merged library definitions by importing them, and the 59 ids were checked as distinct against 147 earlier ids. No fixture or test was run for it, and it lists what it could not verify.
- Installed qualification (core #714, merged `ab80b98`): 297 of 297 demos in each of 4 install forms (all wheels, all sdists, and the two mixed forms), 1188 of 1188 demo processes passed on the first attempt, pip check clean in each form, and identical canonical `content_sha256` across the four forms for all 293 result cases. These are the PR's own claims; the figures were not re-run for this package.

## What was matched, at which layer

| Contract | Result fixtures | Refusal recipes | Library (author) | I/O and worker (qualification demo, #714) |
| --- | --- | --- | --- | --- |
| G | 82 | 75 | 82 of 82, 75 of 75 | 82 result demos and a 75-refusal run passed in all 4 forms; RF18 and RF35 counted as expected adapter deviations |
| H | 69 | 80 | 69 of 69, 80 of 80 | 69 and 80 passed in all 4 forms |
| I1 | 31 | 39 | 31 of 31, 39 of 39 | 31 and 39 passed in all 4 forms |
| I2 | 111 | 114 | 111 of 111, 114 of 114 | 111 and 114 passed in all 4 forms |
| Total | 293 | 308 | | 297 demos per form (293 results plus 4 refusal runs) |

Each result demo ran adapter, worker, library, a separate DuckDB sink, SDK readback, replay and close/reopen, and passed when readback, reopen and literal match were true. Layer-level refusal behavior (from the amendment): H io #39 refused 29 of 80 at the I/O boundary and 51 in the library with 80 of 80 codes matching; I2 io #42 refused 26 of 114 at I/O and 88 in the library, 114 of 114 codes matching; G io #41 refused 16 of 75 at I/O and 59 in the library, with 73 of 75 recipes raising the contract code. Fixture counts are author-reported and were not independently re-run for this package.

### What was NOT driven

- Nine tape merge refusal recipes have no worker path and are checked at the library only: RF41, RF42, RF43, RF54, RF55, RF60, RF65, RF66 and RF69 (ruling E8). Status: accepted limit (decided, pending owner review, DECISIONS.md 2026-10-28). They are library-only by design under ruling E8: the top-K merge worker uses one shared configuration. They stay covered by the library fixtures and `tools/verify_ef4_fixtures.py` counts; the owner may choose a worker path under E8.
- Tape generator fixtures G01 to G03 were not run in the qualification.
- Unit test suites (none by policy), real or observed data, browser inspection of generated HTML. (The Parquet and bundles notional round trip is now recorded, see L2 below.)

## Installed qualification (Windows)

Core PR #714 (`docs/ef4/EF4_INSTALLED_QUALIFICATION.md`) is **merged** (`ab80b98`). It records core `c4e4c70`, io `4ebfa30`, workers `51f5e7f` (the later core `a18f6fd` differs only by the amendment docs), 8 packages as wheel and sdist, Windows 11, CPython 3.12.10, the results above, and a batch time of about 3556 s with the four forms running concurrently. It is not fully standalone: example scripts, contract JSON and fixture expanders were read from source trees, and the default contract lookup from an installed copy was not exercised. Linux was not run.

## Known limits and release-gate items

- E1 (rank-aware check): CLOSED. Core #734 built the rank-aware `TopKTrades(k, rows, ranking=)` check and removed the `object.__new__` workaround; io #54 makes the bundles typed decoder and the io-sdk codec accept `tape.top_k_notional` cells (merged 2026-10-28; `EF4_TAPE_IO.md` was refreshed in io #52 and #54). Historic text (pre-#734: the shared validator demanded the size-ranked key and the bundles decoder refused notional cells) no longer applies.
- E2 (coverage fails open): CLOSED. Tape adapter: rows without declared coverage are refused INVALID_SCHEMA (io #51), no rows without coverage INVALID_CONFIG (io #54); core #734 makes `declared_coverage` for quote and VWAP trade sources refuse an undeclared batch that delivers rows; incomplete coverage reads as `governed_gap` (DP-T12, recipes ER09 to ER11, #737).
- RF18 and RF35 adapter deviation (E6): through the adapter the shared validator refuses first with `UNSUPPORTED_SAMPLING` and `DUPLICATE` instead of the contract `INVALID_SCHEMA`; both inputs are still refused.
- Refusals are raised by different layers than the contract `raised_by` for H (RQ09, RQ12, RV43) and I2 (11 producer-admission recipes, SPR12, SPR13); codes match, layers differ, contract files not edited (L1). Worker codes collapse to `INVALID_COMMAND` as in EF3 ruling R9.
- L2 (Parquet and bundles round trip for notional cells): RUN and recorded. `tools/verify_ef4_notional_cells.py` in equity-feature-io (extended by io #59) round trips a `tape.top_k_notional` result (prints a(1x10), b(2x3), c(1x1): size order b,a,c; notional order a,b,c) through the bundles typed decoder, the io-sdk codec, the core Arrow conversion and a `ParquetSink` publish and read-back, and inspects the stored `cells.parquet` cell wire and `evidence.parquet` rows (notional order a,b,c). Result on 2026-10-28: OK, with io main `106897a`, core main `3af2d99`, CPython 3.12.10, pyarrow 20.0.0, Windows (the first three round trips were recorded by io #54 for `97feb48`). Not covered: the workers remote client cannot decode notional cells (documented limit; PO verdict C3), and a full reproduction bundle for `tape.top_k_notional` does not exist because the bundle format is `session.compute_trades.v1` only (bundle `result.json` goes through the typed decoder checked above).
- L3 (mypy): CLOSED for the io examples (io #52) and the workers EF4 modules (workers #95); `mypy --strict packages/duckdb/src` is clean in io. Not claimed for core: `mypy` on `packages/intraday` still reports the 13 baseline errors (core #742 body), unchanged by EF4/EF5.
- Package versions (as built in #714: workers `0.1.0a15`, features `0.0.4a5`, intraday `0.1.0a3`) are STALE. As of the A5/A6 bump (later superseded by the EF5 bump: intraday a5, duckdb a11, workers a17, client a1, provenance a4; see core `docs/PRERELEASE_BUMP_EF5.md`), after the coordinated pre-release bump (core #739 `710fe05`, io #56 `f889426`, workers #97 `2222d43`; record `docs/PRERELEASE_BUMP_A5_A6.md`): contracts `0.0.4a5`, features `0.0.4a6`, intraday `0.1.0a4`, explanations `0.1.0a3`, evidence `0.1.0a3`, diagnostics/conformance/agent-evidence/agent-ledger `0.1.0a2`, io-contracts and io-sdk `0.1.0a3`, bundles `0.1.0a2`, duckdb `0.1.0a10`, duckdb-sink `0.1.0a1`, parquet `0.1.0a2`, workers `0.1.0a16`, provenance `0.1.0a3`, mcp `0.1.0a2`. Pre-release label move only: no tag, no publish, no release claim; publication still needs the owner. Wording stays "internal, synthetic, pre-release a5/a6".
- Batch API holds data in memory (O(n)); no incremental state.
- `tools/check_boundary.py` (L6): historic text said it failed on the base at `ef1/_reference_close.py`; on origin/main `3af2d99` it exits 0 (run 2026-10-28).
- Tape window `evidence_limit` is published as 9 times the config value (E7); the `governed_history` window N <= 63 is now an explicit INVALID_CONFIG check (E4, core #734); I1 is hosted in packages/intraday (E5); unit spelling is not unified (E9: ledger applied in `EF4_LEDGER_APPLICATION`, unit-spelling unification deferred to the next contract-version migration because of hash impact).
- The output ownership manifest `docs/plans/equity-output-ownership.json` was not checked against the 59 EF4 headers.
- Shared amendment rulings E1 to E9 are pending owner awareness (PO ratified them 2026-10-28, PO ruling (recorded in DECISIONS.md)). Cost figures and fixture pass counts are author-reported (L7).

## Later changes and open items (added 2026-10-28)

Merged after this package was written: E1/E2/E4 core #734 with io #54 and #51, errata #737, compatibility notes #738/#55, bump #739/#56/#97, builder re-pin #740/#57/#98, nits #741/#99/#744, EF5 library #742/#743, EF5 io #58, EF5 workers plan #100. Reviewer verdict records: `docs/qa/EF4_PR_REVIEWER_VERDICTS.md` (GitHub holds no reviews). Builders not run to completion are listed in each repo's `docs/PRERELEASE_BUMP_A5_A6.md`; the later state is in core `docs/PRERELEASE_BUMP_EF5.md` (builder re-pin, partly closed) and the latest `DECISIONS.md` entry. Independent EF4 docs review is not done.

## Not done (not claimed)

- Acceptance of EQ-158, EQ-159, EQ-160, EQ-161, EQ-162 and EQ-172, and of the release acceptance story EQ-163. EF4 is not accepted.
- Linux installed qualification (owner action).
- A real-source demo, source-rights and parity, benchmarks, an owner demo (browser) of the EF4 results, the owner's review of all coordinator decisions, DECISIONS.md and token ledger entries for EF4, and the retrospective update.
- Worktree cleanup.

## Owner items

Review rulings E1 to E9; decide the open items in the amendment section (e); approve the version bump and release publication; line-ending rule (`.gitattributes`); Linux qualification; owner demo; decide acceptance.
