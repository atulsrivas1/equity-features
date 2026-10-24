# EF4 shared producer-set, ledger and ruling amendment

Proposed by the contract author for review and owner decision, based on main at c4e4c70. Docs only; nothing is accepted. This additive amendment preserves the frozen [CONTRACT.json](../ef1/CONTRACT.json) (ef1-contract1), the [EF1 amendment](../ef1/PRODUCER_SET_AMENDMENT.md), the [EF2 amendment](../ef2/PRODUCER_SET_AMENDMENT.md), the [EF3 amendment](../ef3/EF3_SHARED_AMENDMENT.md) and the four EF4 contracts byte for byte and is recorded as a sibling file, in the form of the EF3 amendment. The record in machine-readable form is [EF4_SHARED_AMENDMENT.json](EF4_SHARED_AMENDMENT.json). No validator, code, fixture or `CONTRACT.json` is edited.

It covers the nine producers of the four frozen EF4 contracts, whose library, I/O and worker layers are merged:

| Contract | Document | Core library | I/O adapter | Worker |
| --- | --- | --- | --- | --- |
| G tape window and notional top-K | [TAPE_CONTRACT_PROPOSAL.md](TAPE_CONTRACT_PROPOSAL.md) (core #704) | #706, #710 | io #41 | workers #86 |
| H quote dynamics and VWAP path | [QUOTE_VWAP_CONTRACT_PROPOSAL.md](QUOTE_VWAP_CONTRACT_PROPOSAL.md) (core #703) | #707 | io #39 | workers #84 |
| I1 path efficiency and choppiness | [PATH_EFFICIENCY_CONTRACT_PROPOSAL.md](PATH_EFFICIENCY_CONTRACT_PROPOSAL.md) (core #705) | #708 | io #40 | workers #83 |
| I2 equity statistical projections | [PATH_PROJECTIONS_CONTRACT_PROPOSAL.md](PATH_PROJECTIONS_CONTRACT_PROPOSAL.md) (core #705) | #709 | io #42 | workers #85 |

The vendored fixture expanders landed as core #711. Sources read: the four contract `.md`/`.json` files, [TAPE_IMPLEMENTATION.md](TAPE_IMPLEMENTATION.md), [QUOTE_VWAP_IMPLEMENTATION.md](QUOTE_VWAP_IMPLEMENTATION.md), [PATH_EFFICIENCY_IMPLEMENTATION.md](PATH_EFFICIENCY_IMPLEMENTATION.md) and [PATH_PROJECTIONS_IMPLEMENTATION.md](PATH_PROJECTIONS_IMPLEMENTATION.md); the merged core code (packages/features `equity_features.ef4`, packages/intraday `_path*`, packages/contracts `results.py`); equity-feature-io main 4ebfa30 (the four `EF4_*_IO.md` documents, the io-sdk `codec.py` and the bundles `_typed.py`); and equity-feature-workers main 51f5e7f (the four `EF4_*_WORKER.md` documents and the service `codec.py` import list). The only code executed was an import of the merged definitions to read dtypes and unit strings; no fixture or test was run.

## (a) Producer-set and header-ledger delta

| Producer | Config identity | Algorithm / schema | Policy label | Roles | Host | Headers |
| --- | --- | --- | --- | --- | --- | --- |
| `tape_window_sign` | `ef4.tape_window_sign` | `ef4-tape-window-v1` / 1 | ef4-tape1 | trades, seed | packages/features (equity_features.ef4), own catalog | 9 |
| `trade_top_k_notional` | `ef4.trade_top_k_notional` | `ef4-top-k-notional-v1` / 1 | ef4-notional1 | trades | packages/features (equity_features.ef4), own catalog | 1 |
| `quote_dynamics` | `ef4.quote_dynamics` | `ef4-quote-dynamics-v1` / 1 | ef4-quote1 | bounds, quotes | packages/features (equity_features.ef4), own catalog | 9 |
| `vwap_path` | `ef4.vwap_path` | `ef4-vwap-path-v1` / 1 | ef4-vwap1 | bounds, grid, trades, bars, proof | packages/features (equity_features.ef4), own catalog | 7 |
| `path_efficiency` | `ef4.path_efficiency` | `ef4-path-efficiency-v1` / 1 | ef4-path1 | bars | packages/intraday (equity_features_intraday), own catalog | 7 |
| `session_projection` | `ef4.session_projection` | `ef4-session-projection-v1` / 1 | ef4-proj1 | daily | packages/features (equity_features.ef4), own catalog | 7 |
| `bar_projection` | `ef4.bar_projection` | `ef4-bar-projection-v1` / 1 | ef4-proj1 | bars | packages/features (equity_features.ef4), own catalog | 6 |
| `relative_excess` | `ef4.relative_excess` | `ef4-relative-excess-v1` / 1 | ef4-rel1 | legs, membership | packages/features (equity_features.ef4), own catalog | 8 |
| `rate_projection` | `ef4.rate_projection` | `ef4-rate-projection-v1` / 1 | ef4-rate1 | tape, legs | packages/features (equity_features.ef4), own catalog | 5 |

Identities, versions and labels were read from the `producers` objects of the four contract JSON files. The two tape producers, the two quote/VWAP producers and the four projection producers sit in `packages/features` (`equity_features.ef4`, own discovery and capability check, nothing in the core registry); `path_efficiency` sits in `packages/intraday` (ruling E5). The contract role lists are the fixed nullable slots of the libraries; roles no selected output needs are not examined.

**Header ledger additions (59).** Verified by parsing the `headers` arrays: tape 10, quote/VWAP 16, path efficiency 7, projections 26, total 59 with 59 distinct feature ids, none present in the 45 headers of `docs/ef1/CONTRACT.json`, the 11 of the EF1 amendment, the 39 of the EF2 amendment or the 52 of the EF3 amendment (147 earlier ids compared). The dtype and unit of every one of the 59 headers equals the merged library definition (compared by import).

**Ledger totals.** 45 (frozen) + 11 (EF1 amendment) + 39 (EF2 amendment) + 52 (EF3 amendment) + 59 (this amendment) = 206. As with EF3, the EF4 headers sit in their own catalogs and no code enumerates the combined ledger; 206 is a documentation figure, not a code count.

**By dtype and unit.** bool boolean 1; decimal128 currency 2; decimal128 currency coefficient / 10^price_scale 2; float64 bps 4; float64 currency/share 11; float64 currency/share/second 2; float64 currency_per_second 1; float64 fraction 21; float64 fraction_per_second 1; float64 shares/s 1; float64 trades_per_second 1; int64 pairs 2; int64 points 1; int64 shares 7; int64 trades 1; top_k_trades bounded original trade-row evidence 1.

**Unit and dtype additions (to be applied, additive).** Unit strings of the 59 headers that are neither frozen nor already proposed by the EF1, EF2 or EF3 amendments:

- `trades` (int64): `tape.window.count`.
- `currency coefficient / 10^price_scale` (decimal128): `tape.window.notional`, `tape.tick.net_notional`.
- `bounded original trade-row evidence` (top_k_trades): `tape.top_k_notional`.
- `pairs` (int64): `quote.change.pair_count`, `quote.change.midpoint_change_count`.
- `points` (int64): `vwap.path.point_count`.
- `currency/share/second` (float64): `vwap.slope.endpoint`, `vwap.slope.ols`.
- `trades_per_second` (float64): `rate.window.trade_rate`.
- `currency_per_second` (float64): `rate.window.notional_rate`.
- `fraction_per_second` (float64): `rate.window.return_rate_difference`.

Already proposed earlier and reused: `bps` (float64; EF1 amendment) by `quote.sampled.maximum_midpoint_bps`, `quote.microprice.last_offset_bps`, `quote.change.midpoint_bps` and `vwap.path.change_bps`; `shares/s` (float64; EF3 amendment) by `rate.window.share_volume_rate`. Frozen and reused: `boolean`, `currency`, `currency/share`, `fraction`, `shares`. `decimal128` is a frozen dtype; `top_k_trades` (the registry value type of `tape.top_k_notional`) has no earlier ledger row. No scale is stated by the contracts for these headers beyond the contract text; EF2 finding F7 (scale wording) applies equally and is not resolved here. See ruling E9 on unit spelling.

### Ledger rows

| Feature id | dtype | unit | Producer |
| --- | --- | --- | --- |
| `core.benchmark_direction_agreement_fraction` | float64 | fraction | relative_excess |
| `core.benchmark_return_dispersion_fraction` | float64 | fraction | relative_excess |
| `path.choppiness_fraction` | float64 | fraction | path_efficiency |
| `path.efficiency_ratio` | float64 | fraction | path_efficiency |
| `path.log_efficiency_ratio` | float64 | fraction | path_efficiency |
| `path.net_displacement` | float64 | currency/share | path_efficiency |
| `path.path_length` | float64 | currency/share | path_efficiency |
| `path.true_range_sum` | float64 | currency/share | path_efficiency |
| `path.window_range` | float64 | currency/share | path_efficiency |
| `projection.close_above_sma` | bool | boolean | session_projection |
| `projection.close_vs_sma_fraction` | float64 | fraction | session_projection |
| `projection.distance_from_low_fraction` | float64 | fraction | session_projection |
| `projection.down_dollar_volume` | decimal128 | currency | bar_projection |
| `projection.down_session_fraction` | float64 | fraction | session_projection |
| `projection.down_volume` | int64 | shares | bar_projection |
| `projection.drawdown_fraction` | float64 | fraction | session_projection |
| `projection.max_drawdown_fraction` | float64 | fraction | session_projection |
| `projection.up_dollar_volume` | decimal128 | currency | bar_projection |
| `projection.up_dollar_volume_fraction` | float64 | fraction | bar_projection |
| `projection.up_session_fraction` | float64 | fraction | session_projection |
| `projection.up_volume` | int64 | shares | bar_projection |
| `projection.up_volume_fraction` | float64 | fraction | bar_projection |
| `quote.change.midpoint_bps` | float64 | bps | quote_dynamics |
| `quote.change.midpoint_change_count` | int64 | pairs | quote_dynamics |
| `quote.change.pair_count` | int64 | pairs | quote_dynamics |
| `quote.change.spread` | float64 | currency/share | quote_dynamics |
| `quote.microprice.last` | float64 | currency/share | quote_dynamics |
| `quote.microprice.last_offset_bps` | float64 | bps | quote_dynamics |
| `quote.microprice.mean` | float64 | currency/share | quote_dynamics |
| `quote.sampled.maximum_midpoint_bps` | float64 | bps | quote_dynamics |
| `quote.sampled.maximum_spread` | float64 | currency/share | quote_dynamics |
| `rate.window.notional_rate` | float64 | currency_per_second | rate_projection |
| `rate.window.raw_return_fraction` | float64 | fraction | rate_projection |
| `rate.window.return_rate_difference` | float64 | fraction_per_second | rate_projection |
| `rate.window.share_volume_rate` | float64 | shares/s | rate_projection |
| `rate.window.trade_rate` | float64 | trades_per_second | rate_projection |
| `relative.session.primary.prior_close_excess_fraction` | float64 | fraction | relative_excess |
| `relative.session.primary.window_excess_fraction` | float64 | fraction | relative_excess |
| `relative.session.secondary.prior_close_excess_fraction` | float64 | fraction | relative_excess |
| `relative.session.secondary.window_excess_fraction` | float64 | fraction | relative_excess |
| `relative.session.sector.prior_close_excess_fraction` | float64 | fraction | relative_excess |
| `relative.session.sector.window_excess_fraction` | float64 | fraction | relative_excess |
| `tape.tick.down_volume` | int64 | shares | tape_window_sign |
| `tape.tick.imbalance` | float64 | fraction | tape_window_sign |
| `tape.tick.net_notional` | decimal128 | currency coefficient / 10^price_scale | tape_window_sign |
| `tape.tick.net_volume` | int64 | shares | tape_window_sign |
| `tape.tick.neutral_volume` | int64 | shares | tape_window_sign |
| `tape.tick.up_volume` | int64 | shares | tape_window_sign |
| `tape.top_k_notional` | top_k_trades | bounded original trade-row evidence | trade_top_k_notional |
| `tape.window.count` | int64 | trades | tape_window_sign |
| `tape.window.notional` | decimal128 | currency coefficient / 10^price_scale | tape_window_sign |
| `tape.window.volume` | int64 | shares | tape_window_sign |
| `vwap.path.change_bps` | float64 | bps | vwap_path |
| `vwap.path.last` | float64 | currency/share | vwap_path |
| `vwap.path.maximum` | float64 | currency/share | vwap_path |
| `vwap.path.minimum` | float64 | currency/share | vwap_path |
| `vwap.path.point_count` | int64 | points | vwap_path |
| `vwap.slope.endpoint` | float64 | currency/share/second | vwap_path |
| `vwap.slope.ols` | float64 | currency/share/second | vwap_path |

Availability, null rules, operand families and minimum periods stay in the four contracts and are not restated.

## (b) Coordinator rulings (decided, pending owner review)

These are the coordinator's rulings. They are decided for the work in flight and are pending owner review; none is an acceptance. Each lists the contract lines it affects and what the merged library, I/O adapter and workers do, as read from the code and documents named above. Where the code differs from the ruling it is stated under the ruling and again in section (d).

### E1. Rank-aware TopKTrades order check; notional cell construction

**Ruling.** No other shared-validator change is made in EF4. The shared `TopKTrades` order check becomes rank-aware (a ranking-aware order check or a ranking field) in a later change before any layer relies on the notional cell through the public constructor. Until then the pinned workaround stands: `tape.top_k_notional` cells are assembled with `object.__new__(TopKTrades)` plus `object.__setattr__`; the io codec reads a stored cell feature-aware (only `tape.top_k_notional` is notional-ordered); the bundles decoder still refuses notional cells.

**Contract lines affected.**

- TAPE_CONTRACT_PROPOSAL.md DP-K4 (line 190) and OQ-6 (line 209): the cell, its Arrow struct and the registry type stay unchanged
- TAPE_CONTRACT_PROPOSAL.md line 78 and DP-K2 (line 188): rank key (-notional, event_ns, order_key, event_id)
- fixture TK01 (rank d, a, c against the size order e, b, d)

**What the merged layers do.**

- Library (core main c4e4c70): `notional_cell` (ef4/_tape_topk.py:62) first validates the rows with the shared constructor in the size order (types, bounds, duplicates, K), then builds the frozen cell in the notional order with `object.__new__` and `object.__setattr__`. It is used by `compute_trade_top_k_notional` and `merge_trade_top_k_notional`. The shared `TopKTrades.__post_init__` (packages/contracts results.py:211) is unchanged and still demands the size-ranked key, so `dataclasses.replace(cell)`, `TopKTrades(k, rows)` on notional-ordered rows or any restore that revalidates raises `INVALID_ORDER`. The rank-aware check itself is NOT implemented anywhere; it is the amendment item.
- I/O (equity-feature-io main 4ebfa30): equity-feature-io main 4ebfa30, io-sdk codec.py: `_decode` decodes the `feature_id` of a `FeatureColumn` first and passes `notional = (feature == 'tape.top_k_notional')` down; only then `_notional_cell` assembles the cell: k bound 1..10000, row types, duplicate (input_id, event_id) identity, AND the rows must follow the notional rank (-price*size, event_ns, order_key, event_id), else `SinkError INVALID_CONTENT`; then `object.__new__`. Every other feature keeps the shared constructor and its size order. Bundles (packages/bundles `_typed.py`) rebuild `r.TopKTrades(k=..., rows=...)` through the public constructor, so a notional cell is refused there.
- Workers (equity-feature-workers main 51f5e7f): EF4_TAPE_WORKER.md (workers main 51f5e7f): the worker never rebuilds a cell; it stores and reads through the io-sdk codec; TK01 and TK15 pass the store, read-back, replay and close/reopen path (author-reported, not re-run). The service package codec (`equity_feature_service/codec.py`) was not traced for this cell.

### E2. Coverage form and the fail-open of undeclared coverage

**Ruling.** The declaration is one `IntervalCoverage` entry exactly equal to [S, E) on the quote or trade batch, with the aggregate `Coverage` as fallback (complete; incomplete with a known `expected`; undeclared when `expected` is null). Bars use per-slot entries equal to a grid slot. An undeclared batch that delivers rows is read as complete: this fails open, so every I/O mapper must always declare coverage.

**Contract lines affected.**

- QUOTE_VWAP_CONTRACT_PROPOSAL.md line 85 (DP-Q3, DP-Q11): delivery completeness is the declared IntervalCoverage
- QUOTE_VWAP_CONTRACT_PROPOSAL.md line 60 (trades role: declared IntervalCoverage)
- PATH_EFFICIENCY_CONTRACT_PROPOSAL.md line 46 and PATH_PROJECTIONS (per-slot coverage names `bar:<i>`, `slot:<i>`)

**What the merged layers do.**

- Library (core main c4e4c70): `declared_coverage` (ef4/_common.py:200): any interval entry must be exactly one entry equal to [S, E) with observed equal to the delivered rows, else `INCONSISTENT_IDENTITY`; with no entry the aggregate is read: complete is complete, incomplete with `expected` not null is incomplete, incomplete with `expected` null is `undeclared`. Zero rows with `undeclared` (or an undelivered role) is `absent_input` (_quote.py:170, _vwap.py:149). `undeclared` with rows is not gated as incomplete, so it reads as complete. Bars (VWAP bar source): a per-slot entry must equal a grid slot; no row with an entry is `governed_gap`, no row without one is `absent_input`, a delivered row whose entry is incomplete is `governed_gap` (implementation document; no fixture). Path efficiency and the projections declare per slot and treat a slot without a coverage entry as absent.
- I/O (equity-feature-io main 4ebfa30): Not verified in the adapter source for this amendment (only the I/O documents were read). The H I/O record states the library behavior is what its fixture harness also does.
- Workers (equity-feature-workers main 51f5e7f): Not specific; the workers pass the adapter batches through.

### E3. REFERENCE evidence boundary is `ordinary`

**Ruling.** Evidence rows built from REFERENCE inputs use boundary `ordinary`; so do quote and trade witnesses. `completed_interval` is used only for BAR and DAILY slots and bars. Contract line 151 of the projections contract (boundary `completed_interval` for all witnesses) cannot be implemented for REFERENCE witnesses and is corrected to this.

**Contract lines affected.**

- PATH_PROJECTIONS_CONTRACT_PROPOSAL.md line 151: Evidence ... Boundary `completed_interval` (unimplementable for relative-excess leg/membership witnesses and rate-projection tape/leg witnesses)

**What the merged layers do.**

- Library (core main c4e4c70): The shared cutoff predicate (packages/contracts results.py:499-501) raises `BOUNDS` for `completed_interval` evidence on any kind except BAR and DAILY. I2 (PATH_PROJECTIONS_IMPLEMENTATION.md ruling 7 and ef4/_session_projection.py:174, _bar_projection.py:379): REFERENCE witnesses `ordinary`; session slots and bar witnesses `completed_interval`. H: quote and trade witnesses `ordinary`, bar witnesses `completed_interval`; the bounds, grid and proof facts are bound but give no witness. G: window and top-K witnesses are `ordinary`, except the top-K row of a print at the cutoff, which uses `closing_auction`. Same shape as EF3 ruling R3.
- I/O (equity-feature-io main 4ebfa30): No separate behavior; the adapters hand the batches to the library.
- Workers (equity-feature-workers main 51f5e7f): EF4_PROJECTIONS_WORKER.md (design item 6): REFERENCE evidence boundary `ordinary`, observed on the stored relative-excess and rate results.

### E4. governed_history is capped at N <= 63 and uses the R17 carry context

**Ruling.** `epoch_profile = governed_history` requires an R17 context in `carry` mode (anchor at the start of the supplied daily grid; no value crosses a session boundary); `session_reset` requires `reset`. The R17 context holds at most 64 sessions and `governed_history` has one governed slot per session, so N is capped at 63 daily returns per context. The cap is a coordinator decision; no code split is made.

**Contract lines affected.**

- PATH_EFFICIENCY_CONTRACT_PROPOSAL.md line 22: window N 2..4096, epoch_profile session_reset | governed_history
- PATH_EFFICIENCY_CONTRACT_PROPOSAL.md line 46 (bars role, R17 chunked delivery) and line 70 (epoch, DP-E3, line 123: no carry)

**What the merged layers do.**

- Library (core main c4e4c70): `_path_config.py`: `_MODE = {session_reset: reset, governed_history: carry}`; an `epoch_profile` that disagrees with the context mode, or the profile value `carry` itself, is `INVALID_CONFIG` (lines 38, 64); a `carry` context whose slot count differs from its session count is `INVALID_CONFIG` (line 65). `_context.py:80` bounds a context at 1..64 sessions, which gives N + 1 <= 64 slots, N <= 63. There is no explicit `window <= 63` check: `window` keeps the range 2..4096 and a window beyond the delivered slots gives `insufficient_history` at compute (window 4096 is a valid config whose result is always `insufficient_history`; 4095 is the largest session_reset window that can be available).
- I/O (equity-feature-io main 4ebfa30): Not specific to the cap (the I1 I/O record builds the context and config with the adapter and compares the envelope to `build_path_efficiency_config`).
- Workers (equity-feature-workers main 51f5e7f): Not specific.

### E5. I1 (path efficiency) is hosted in packages/intraday

**Ruling.** `ef4.path_efficiency` lives in `packages/intraday` (equity_features_intraday) next to `ef3.intraday_realized_variance`, because it consumes the R17 `IntradayContext` and BAR admission and `equity-features` does not depend on `equity-features-intraday`. The config namespace stays `ef4.path_efficiency`. Moving it is a mechanical follow-up if the owner prefers `packages/features`.

**Contract lines affected.**

- PATH_EFFICIENCY_CONTRACT_PROPOSAL.md OQ-E5 (line 147): hosted in `packages/features` (EF4 module, namespace `ef4.*`, separate catalog)

**What the merged layers do.**

- Library (core main c4e4c70): Modules `_path_config`, `_path_registry`, `_path` in packages/intraday; public names `compute_path_efficiency`, `describe_path_efficiency`, `require_path_efficiency_capability`; own catalog of 7 entries (describe_path_efficiency in _path_registry.py); `describe_intraday()` still lists the eight R17 ids and its digest is stated unchanged by the implementation document (cited, not re-run). `ef4/__init__.py` is untouched. `tools/check_intraday_boundary.py` lists the three modules (author-reported).
- I/O (equity-feature-io main 4ebfa30): I1 adapter: equity-feature-io EF4_PATH_EFFICIENCY_IO.md (io #40).
- Workers (equity-feature-workers main 51f5e7f): I1 worker: equity-feature-workers EF4_PATH_EFFICIENCY_WORKER.md (workers #83).

### E6. Refusal label errata (raised_by layer and two codes)

**Ruling.** The recorded `raised_by` of the refusal recipes named below is corrected to the layer that actually refuses, and the two G codes are recorded as the first shared validator's code. The refused inputs and the contract codes are unchanged except RF18 and RF35. The frozen contract files are not edited.

**Contract lines affected.**

- QUOTE_VWAP_CONTRACT_PROPOSAL.json refusal_fixtures RQ09 (raised_by shared validator), RQ12 (library), RV43 (shared validator)
- PATH_PROJECTIONS_CONTRACT_PROPOSAL.json refusal_fixtures SPR10, SPR11, SPR18, BPR10, BPR20, RXR22, RXR26, RXR27, RXR28, RXR33, RPR27 (producer admission), SPR12 and SPR13 (shared validator)
- TAPE_CONTRACT_PROPOSAL.json refusal_fixtures RF18 and RF35 (library; contract code INVALID_SCHEMA)

**What the merged layers do.**

- Library (core main c4e4c70): H: RQ09 (`S.cutoff`) is raised by the library, because the batch validator does not see the market cutoff; RQ12 is raised by the shared batch constructor, because the column schema fixes the kind; RV43 (`S.bar_notional_bounds`) is raised at the I/O boundary, the shared validator's position there. I2: SPR12 (DUPLICATE, two daily rows for one instrument and session) and SPR13 (INVALID_ORDER) are library checks on top of the BAR validator (PATH_PROJECTIONS_IMPLEMENTATION.md ruling 2). Library-only runs match every recorded code (G 75 of 75, H 80 of 80, I2 114 of 114, author-reported).
- I/O (equity-feature-io main 4ebfa30): H (io #39): 29 of 80 refused at the I/O boundary, 51 in the library, 80 of 80 codes match. I2 (io #42): the 11 `producer admission` recipes (SPR10, SPR11, SPR18, BPR10, BPR20, RXR22, RXR26, RXR27, RXR28, RXR33, RPR27) are refused at I/O by the shared canonical batch constructors (wire type and precision faults, unknown adjustment basis, REFERENCE identity duplicates); SPR12 and SPR13 are not refused at I/O; 26 of 114 refused at I/O, 88 by the library, 114 of 114 codes match. G (io #41): 16 of 75 refused by the I/O layer, 59 by the library; 73 of 75 recipes raise the contract code; RF18 (`batch_kind = quote`) raises `UNSUPPORTED_SAMPLING` from the shared batch validator (contract `INVALID_SCHEMA`) and RF35 (two identical seed facts) raises `DUPLICATE` from the shared REFERENCE validator (contract `INVALID_SCHEMA`); both inputs are still refused.
- Workers (equity-feature-workers main 51f5e7f): G worker: the same two code differences, refused at adapter build; RF01 and RF58 (BOUNDS) are refused at compute although the contract names the shared validator. H worker: RQ12 refused at adapter build, RQ09 at compute, RV43 at adapter build. Worker codes collapse to `INVALID_COMMAND` with `RESULT_IDENTITY_MISMATCH` for library `INCONSISTENT_IDENTITY` and `CALCULATION_FAILED` for `OVERFLOW`, as in EF3 ruling R9.

### E7. Tape (contract G) per-output evidence_limit

**Ruling.** DP-T15 bounds each available window output by `evidence_limit`, while the shared `FeatureResult` bounds the whole table by `ResultMetadata.evidence_limit`. The window result therefore publishes the fixed bound `evidence_limit * 9` (the number of window outputs, whatever the selection); the config parameter is unchanged. The seed witness counts toward the per-output limit. All other EF4 producers keep the result-wide bound of EF3 ruling R2.

**Contract lines affected.**

- TAPE_CONTRACT_PROPOSAL.md line 22 (evidence_limit 0..10000), line 94 (the seed witness counts toward evidence_limit), line 106 and DP-T15 (line 185): per-output evidence

**What the merged layers do.**

- Library (core main c4e4c70): `_tape_window.py:303` passes `limit * len(TAPE_FEATURES)` (9) as `ResultMetadata.evidence_limit`; a full selection reproduces every fixture witness list. The notional top-K lists the retained rows in rank order; `evidence_limit` is K..10000. H, I1 and I2 are result-wide (a single-output selection reproduces each fixture witness list; a joint selection truncates in lexical output order), as stated in their implementation documents.
- I/O (equity-feature-io main 4ebfa30): The adapter passes the config parameter unchanged (EF4_TAPE_IO.md deviation 8).
- Workers (equity-feature-workers main 51f5e7f): The example sizes the sink caps to the sink's own maxima (EF4_TAPE_WORKER.md design item 6).

### E8. Top-K merge worker uses one shared configuration

**Ruling.** A merge task has one reviewed configuration for all partitions. The worker computes one partial per leaf with the library top-K producer and merges along the role tree with `merge_trade_top_k_notional`. Nine refusal recipes therefore have no worker path and are checked at the library only: RF41, RF42, RF43, RF54, RF55, RF60, RF65, RF66 and RF69.

**Contract lines affected.**

- TAPE_CONTRACT_PROPOSAL.md DP-K6 (line 192) and lines 80-82: merge of partials built with the same policy_version, K, evidence_limit, price unit, adjustment, eligibility policy, entity, market cutoff and knowledge cutoff
- TAPE_CONTRACT_PROPOSAL.md DP-K7 (line 193): update and restore are UNSUPPORTED_CAPABILITY

**What the merged layers do.**

- Library (core main c4e4c70): `merge_trade_top_k_notional` takes `NotionalPartial(config, entity, result)` items so it can see differing configs; it refuses in the DP-K6 order (policy version, price unit, adjustment, eligibility policy, K and evidence limit, then entity, market cutoff and knowledge cutoff, then partial row order, then retained duplicates); a merged result can be a partial of a further merge; an empty list is `INVALID_CONFIG`. Update, restore and the window merge are `UNSUPPORTED_CAPABILITY`.
- I/O (equity-feature-io main 4ebfa30): RF69 (a supplied partial whose rows arrive in delivered order) is not an adapter input; the runner built it by reordering a computed partial's rows and the library merge refused with `INVALID_ORDER`.
- Workers (equity-feature-workers main 51f5e7f): EF4_TAPE_WORKER.md: no worker path for RF41, RF42, RF43, RF54, RF55 (capability calls the worker does not expose), RF69 (the worker computes its own partials) and RF60, RF65, RF66 (partials with another K, knowledge cutoff or policy version: one reviewed configuration per merge task). Merge manifest roles spell the tree (`p0.trades`, `p1.trades`, or `p0.p0.trades` ...).

### E9. New unit strings (read from the merged code and equal to the contract headers)

**Ruling.** Apply the unit strings in the `unit_additions` list additively to the shared ledger. The code unit of all 59 EF4 headers was compared with the contract header unit and dtype: no difference. `bps` is already proposed by the EF1 amendment and `shares/s` by the EF3 amendment. Spelling is not unified (`currency/share/second` against `currency_per_second`, `trades_per_second`, `fraction_per_second`, and `shares/s`): recorded as an owner decision, not changed here.

**Contract lines affected.**

- TAPE, QUOTE_VWAP, PATH_EFFICIENCY and PATH_PROJECTIONS contract JSON `headers` arrays (59 headers)

**What the merged layers do.**

- Library (core main c4e4c70): Read from FEATURE_META / SESSION_META / BAR_META / the relative-excess and rate-projection META tables in ef4 and from `describe_path_efficiency()` by running the import (no test executed). The value type `top_k_trades` is the registry type of `tape.top_k_notional`; the ledger has no earlier row of that dtype.
- I/O (equity-feature-io main 4ebfa30): Not applicable.
- Workers (equity-feature-workers main 51f5e7f): Headers come from the library's own definitions (EF4_TAPE_WORKER.md design item 3).

## (c) Known limits

- **L1** Refusal recipes of H and I2 (RQ, SP and sibling ids) are raised by different layers than the contract `raised_by` (E6); codes match, layers differ. The contract is not edited.
- **L2** The Parquet and bundles round trip was not run for notional cells. The DuckDB sink round trip was (227 of 227 G results, author-reported). The bundles decoder refuses notional cells (E1).
- **L3** mypy was not installed in the author environments; strict typing is not claimed for any EF4 layer.
- **L4** The io codec re-check of notional order on read (INVALID_CONTENT) was read in the source; the EF4_TAPE_IO.md risk text says the codec does not re-check the order, which is stale against io main 4ebfa30. A forged cell with a valid notional order and a valid encoding is still not refused.
- **L5** Undeclared coverage with delivered rows reads as complete (E2): fails open for any producer fed by a mapper that does not declare.
- **L6** `tools/check_boundary.py` fails on the base at ef1/_reference_close.py (`import base64`); the EF4 modules report no violation (author-reported).
- **L7** No performance, installed-artifact, cross-layer, source-rights or release acceptance is claimed; cost figures and all fixture pass counts are author-reported.

## (d) Places where the code differs from a ruling or from its documents

- E1: the rank-aware check is a ruling to implement; merged shared code is unchanged and still size-ranked. io main rechecks notional order on read while EF4_TAPE_IO.md says it does not (document stale).
- E4: the cap is implicit (one slot per session, at most 64 sessions) with no explicit N <= 63 check or code.
- E7: the window result publishes evidence_limit * 9 result-wide; per-output limiting is by the producer, not by the shared validator.
- E6: through the adapter 73 of 75 G recipes match the contract code (RF18, RF35 differ), against 75 of 75 in library-only runs.
- E2: the I/O adapters' coverage declaration was not read; only the library behavior is verified.

## (e) Open items not decided (flagged for the owner)

1. E1: the rank-aware `TopKTrades` check is still to be written (shared-validator change in packages/contracts) before any layer rebuilds the notional cell through the public constructor; bundles must then accept the cell.
2. E2: whether to make an undeclared batch a refusal instead of reading it as complete (contract amendment).
3. E4: whether to add an explicit window <= 63 check for governed_history instead of insufficient_history at compute.
4. E5: owner preference on moving the I1 producer to packages/features.
5. E6: whether to edit the four contract files' raised_by labels and the RF18/RF35 codes or keep them as errata only.
6. E9: unit spelling unification (`currency/share/second` and the underscore forms).
7. Output ownership manifest `docs/plans/equity-output-ownership.json` was not checked against the 59 EF4 headers.
8. Package version bump (owed at release), .gitattributes line-ending rule (owner decision), release acceptance (EQ-163), OQ-J3 (EQ-155 edge reserved/unused) and the D6 slot_reasons both-reasons nit (PATH_PROJECTIONS_IMPLEMENTATION.md) remain with the coordinator.

## Explicit statements

- Docs only: no code, validator, fixture or CONTRACT.json is edited, and no unit test was added.
- Pure additive; frozen EF1 contract, EF1, EF2 and EF3 amendments and the four EF4 contracts are byte for byte unchanged.
- Header ids, dtypes and units of the 59 EF4 headers were compared with the merged library definitions by importing them; no fixture was run.
- Nothing is accepted; no numerical, installed-artifact, cross-layer, source-rights, performance or release acceptance is claimed.

## What could not be verified

- Fixture pass counts (G 82 results and 75 refusals, H 69 and 80, I1 31 and 39, I2 111 and 114, and the io and worker run counts) are author-reported in the implementation, I/O and worker documents and were not re-run.
- The I/O adapters' source and the workers' source were not read beyond the io-sdk codec, the bundles typed decoder and the service codec import list; the sibling documents were read (io main 4ebfa30, workers main 51f5e7f).
- The combined ledger total 206 is a static count; no code enumerates it.
- Catalog digests of `describe_intraday()` and the other catalogs are cited from the implementation documents.
