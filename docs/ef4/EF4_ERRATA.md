# EF4 errata for the PO rulings E1, E2 and E4 (2026-10-28)

Additive errata. The four frozen EF4 contracts, their `fixture_counts` and [EF4_SHARED_AMENDMENT.md](EF4_SHARED_AMENDMENT.md) are not edited. Regression recipes are in [EF4_ERRATA_RECIPES.json](EF4_ERRATA_RECIPES.json) (8 recipes, ER01 to ER08) and run by `tools/verify_ef4_errata.py`; `tools/verify_ef4_fixtures.py` pins that the frozen refusal censuses stay (tape 75, quote/VWAP 80, path efficiency 39, projections 114) and that the errata list is whole. Both are picked up by `tools/pre_merge_check.py`.

## E1. Rank-aware TopKTrades check (ER01 to ER04)

`TopKTrades(k, rows, ranking="size")`: `ranking` is a constructor-only argument (`InitVar`, not a stored field), `size` (default, key `(-size, event_ns, order_key, event_id)`) or `notional` (key `(-(price * size), event_ns, order_key, event_id)`, `TopKTradeRow.notional_rank_key`). The constructor checks the rows against the named ranking (INVALID_ORDER otherwise; INVALID_SCHEMA for an unknown ranking). `FeatureResult` additionally binds the ranking to the feature id: `NOTIONAL_RANKED_FEATURES = {"tape.top_k_notional"}` must be notional ranked, every other TopKTrades feature size ranked (INVALID_ORDER). Fields, wire form (io codec), Arrow struct, content digest and the size-ranked `session.trade.top_k` are unchanged. `notional_cell` uses the constructor; the `object.__new__` workaround is gone. I/O readers rebuild the cell with `ranking="notional"` for that feature only.

## E2. No fail-open on undeclared coverage (ER05 to ER07)

Library: `declared_coverage` (quote and VWAP trade source) refuses an undeclared batch that delivers rows (no interval entry, aggregate incomplete with unknown expected count) with `INVALID_SCHEMA` ("coverage not declared"), the code io #51 uses for the tape adapter. Zero rows with no declaration stays `undeclared`, which the producers read as `absent_input`. The tape library already reads an incomplete batch (complete false or expected different from the delivered count) as `governed_gap` (TAPE contract DP-T12), so it never reads undeclared as complete and is unchanged. Tape adapter (equity-feature-io): no default to complete, see the paired io PR. The fixture notation `quotes.coverage`/`trades.coverage` default `complete` applies to fixtures only; the quote/VWAP I/O mapper (`quote_vwap._event_coverage`) already refuses `absent` with rows. Contract lines affected: QUOTE_VWAP DP-Q3 and DP-Q11 (delivery completeness is the declared IntervalCoverage), TAPE DP-T12.

## E4. Explicit governed_history window check (ER08)

`build_path_efficiency_config` and the closed decoder refuse `epoch_profile = governed_history` with `window > 63` as `INVALID_CONFIG` (`PATH_GOVERNED_WINDOW_MAX = 63`), instead of an always-`insufficient_history` result at compute. `session_reset` keeps the range 2..4096. PATH_EFFICIENCY contract line 22 (window N 2..4096) is read together with this errata.
