# EF4 errata (PO ruling E6, 2026-10-28)

The frozen EF4 contract files (`TAPE_`, `QUOTE_VWAP_`, `PATH_EFFICIENCY_`, `PATH_PROJECTIONS_CONTRACT_PROPOSAL.json`) are **not edited**. This table is the recorded truth where a recorded `raised_by` label or code differs from what the merged layers do. Details and per-layer counts: [EF4_SHARED_AMENDMENT.md](EF4_SHARED_AMENDMENT.md) E6.

## Code errata (library codes are the recorded truth)

| Recipe | Contract | Input | Contract code | Recorded truth (code, raiser) | Ruling |
| --- | --- | --- | --- | --- | --- |
| RF18 | TAPE | `batch_kind = quote` | `INVALID_SCHEMA` | `UNSUPPORTED_SAMPLING`, shared batch validator | ACCEPT library code; shared validator not altered |
| RF35 | TAPE | two identical seed facts | `INVALID_SCHEMA` | `DUPLICATE`, shared REFERENCE validator | ACCEPT library code; shared validator not altered |

Both inputs are still refused. Census figure: tape 73 of 75 recipes raise the contract code (RF18 and RF35 are the two ruled differences); across the four EF4 contracts 306 of 308 refusal recipes match the contract code (G 75, H 80, I1 39, I2 114 = 308). 306/308 is the ruled, documented number. A reader comparing a driver's output with the contract code must apply this table.

## raised_by label errata (refused input and code unchanged)

| Recipe | Contract `raised_by` | Actual raiser |
| --- | --- | --- |
| RQ09 (QUOTE_VWAP) | shared validator | library (`S.cutoff`; the batch validator does not see the market cutoff) |
| RQ12 (QUOTE_VWAP) | library | shared batch constructor (the column schema fixes the kind) |
| RV43 (QUOTE_VWAP) | shared validator | I/O boundary (`S.bar_notional_bounds`) |
| SPR10, SPR11, SPR18, BPR10, BPR20, RXR22, RXR26, RXR27, RXR28, RXR33, RPR27 (PATH_PROJECTIONS) | producer admission | shared canonical batch constructors at the I/O boundary (library when run library-only) |
| SPR12, SPR13 (PATH_PROJECTIONS) | shared validator | library checks on top of the BAR validator (not refused at I/O) |
| RF01, RF58 (TAPE; BOUNDS) | shared validator | refused at compute in the G worker |

Worker code mapping (EF3 ruling R9): worker codes collapse to `INVALID_COMMAND`, with `RESULT_IDENTITY_MISMATCH` for library `INCONSISTENT_IDENTITY` and `CALCULATION_FAILED` for `OVERFLOW`; the closed `contract_code` carries the library code.

## Accepted limit (E8, unchanged)

The nine tape merge recipes RF41, RF42, RF43, RF54, RF55, RF60, RF65, RF66 and RF69 are library-checked only, with no worker path.

---

## Errata for PO rulings E1, E2 and E4 (2026-10-28)

Additive errata. The four frozen EF4 contracts, their `fixture_counts` and [EF4_SHARED_AMENDMENT.md](EF4_SHARED_AMENDMENT.md) are not edited. Regression recipes are in [EF4_ERRATA_RECIPES.json](EF4_ERRATA_RECIPES.json) (11 recipes, ER01 to ER11) and run by `tools/verify_ef4_errata.py`; `tools/verify_ef4_fixtures.py` pins that the frozen refusal censuses stay (tape 75, quote/VWAP 80, path efficiency 39, projections 114) and that the errata list is whole. Both are picked up by `tools/pre_merge_check.py`.

### E1. Rank-aware TopKTrades check (ER01 to ER04)

`TopKTrades(k, rows, ranking="size")`: `ranking` is a constructor-only argument (`InitVar`, not a stored field), `size` (default, key `(-size, event_ns, order_key, event_id)`) or `notional` (key `(-(price * size), event_ns, order_key, event_id)`, `TopKTradeRow.notional_rank_key`). The constructor checks the rows against the named ranking (INVALID_ORDER otherwise; INVALID_SCHEMA for an unknown ranking). `FeatureResult` additionally binds the ranking to the feature id: `NOTIONAL_RANKED_FEATURES = {"tape.top_k_notional"}` must be notional ranked, every other TopKTrades feature size ranked (INVALID_ORDER). Fields, wire form (io codec), Arrow struct, content digest and the size-ranked `session.trade.top_k` are unchanged. `notional_cell` uses the constructor; the `object.__new__` workaround is gone. I/O readers rebuild the cell with `ranking="notional"` for that feature only.

### E2. No fail-open on undeclared coverage (ER05 to ER07)

Library: `declared_coverage` (quote and VWAP trade source) refuses an undeclared batch that delivers rows (no interval entry, aggregate incomplete with unknown expected count) with `INVALID_SCHEMA` ("coverage not declared"), the code io #51 uses for the tape adapter. Zero rows with no declaration stays `undeclared`, which the producers read as `absent_input`. The tape library already reads an incomplete batch (complete false or expected different from the delivered count) as `governed_gap` (TAPE contract DP-T12), so it never reads undeclared as complete and is unchanged. Tape adapter (equity-feature-io): no default to complete, see the paired io PR. The fixture notation `quotes.coverage`/`trades.coverage` default `complete` applies to fixtures only; the quote/VWAP I/O mapper (`quote_vwap._event_coverage`) already refuses `absent` with rows. Contract lines affected: QUOTE_VWAP DP-Q3 and DP-Q11 (delivery completeness is the declared IntervalCoverage), TAPE DP-T12.

**Normative error-code split (PO follow-up 2026-10-28, definitive; supersedes the INVALID_CONFIG wording in the earlier E2 ruling).** Rows delivered without declared coverage are refused `INVALID_SCHEMA` because the data violates the schema contract; no rows and no declaration is `INVALID_CONFIG` in the I/O adapter (caller misconfigured it) and `absent_input` in the library. Where each applies: the quote/VWAP library (`declared_coverage`) and the io tape adapter (`tape.py`, io #51) raise `INVALID_SCHEMA` for rows without a declaration, and the io tape adapter raises `INVALID_CONFIG` for no rows and no declaration. The tape library is different and unchanged: it never refuses on coverage, it reads undeclared coverage (for example `Coverage(None, 3, False)`) as status `incomplete_coverage` with reason `governed_gap` (`_tape_topk.py`, DP-T12), so it is never read as complete. The tape fail-closed refusal therefore lives in the adapter.

**Tape governed_gap refusal recipe (ER09 to ER11, DP-T12).** The tape library never reads undeclared coverage as complete: coverage declared incomplete (`complete` false), or whose expected count differs from the delivered count, gives status `incomplete_coverage` with reason `governed_gap` for every output (ER09 and ER10; ER10 cannot isolate a count mismatch from ER09, because `Coverage(5, 3, True)` is refused at construction, so both carry `complete` false), and a complete declaration with the delivered count stays `available` (ER11, control). Rows delivered with incomplete or undeclared coverage are therefore covered as follows: undeclared with rows is ER05 and ER06 (quote/VWAP library only, `INVALID_SCHEMA`; the tape adapter refusal is in equity-feature-io); declared incomplete is ER09 and ER10 (`governed_gap`). Census: frozen contract refusal recipes stay 75, 80, 39 and 114 (308); errata recipes are ER01 to ER11 (11), run by `tools/verify_ef4_errata.py` and counted by `tools/verify_ef4_fixtures.py`.

### E4. Explicit governed_history window check (ER08)

`build_path_efficiency_config` and the closed decoder refuse `epoch_profile = governed_history` with `window > 63` as `INVALID_CONFIG` (`PATH_GOVERNED_WINDOW_MAX = 63`), instead of an always-`insufficient_history` result at compute. `session_reset` keeps the range 2..4096. PATH_EFFICIENCY contract line 22 (window N 2..4096) is read together with this errata.
