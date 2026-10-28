# EF4 ledger application and unit spelling (PO ruling E9, 2026-10-28)

Scope: documentation only. No library code, bundle, adapter, frozen contract file or fixture is edited. The machine-readable form is [EF4_LEDGER_APPLICATION.json](EF4_LEDGER_APPLICATION.json) (59 header rows, generated from the `headers` arrays of the four EF4 contract JSON files; ids, dtypes and units equal the merged library definitions as recorded in [EF4_SHARED_AMENDMENT.md](EF4_SHARED_AMENDMENT.md) E9).

## 1. Ledger application (additive)

The 59 EF4 header additions are applied to the ledger as recorded in the JSON file: tape 10, quote/VWAP 16, path efficiency 7, projections 26, 59 distinct ids, none in the earlier ledgers. Cumulative documentation figure: 45 + 11 + 39 + 52 + 59 = 206 (a static count; no code enumerates the combined ledger). The output ownership manifest `docs/plans/equity-output-ownership.json` already carries all 59 (51 in `ef4_delivered_outputs`, 8 in the planned `outputs`) and is enforced by `tools/check_equity_delivery_replan.py`. Unit strings added by EF4 (dtype, ids):

| Unit | dtype | Headers |
| --- | --- | --- |
| `trades` | int64 | `tape.window.count` |
| `currency coefficient / 10^price_scale` | decimal128 | `tape.window.notional`, `tape.tick.net_notional` |
| `bounded original trade-row evidence` | top_k_trades | `tape.top_k_notional` |
| `pairs` | int64 | `quote.change.pair_count`, `quote.change.midpoint_change_count` |
| `points` | int64 | `vwap.path.point_count` |
| `currency/share/second` | float64 | `vwap.slope.endpoint`, `vwap.slope.ols` |
| `trades_per_second` | float64 | `rate.window.trade_rate` |
| `currency_per_second` | float64 | `rate.window.notional_rate` |
| `fraction_per_second` | float64 | `rate.window.return_rate_difference` |

Reused: `bps`, `shares/s`, `boolean`, `currency`, `currency/share`, `fraction`, `shares`. Note: the output ownership manifest lists `quote.sampled.maximum_spread` with the planning unit `price` while the contract header and library say `currency/share`; the manifest string is a planning name (not hashed) and is left as is.

## 2. Canonical spelling and aliases

Canonical form (lowercase, slash style): `trades/s`, `currency/s`, `fraction/s`, `shares/s`, `currency/share/s`, `bps`.

| Alias (as implemented) | Canonical | Headers |
| --- | --- | --- |
| `trades_per_second` | `trades/s` | `rate.window.trade_rate` |
| `currency_per_second` | `currency/s` | `rate.window.notional_rate` |
| `fraction_per_second` | `fraction/s` | `rate.window.return_rate_difference` |
| `currency/share/second` | `currency/share/s` | `vwap.slope.endpoint`, `vwap.slope.ols` |

The four alias strings are recorded here as aliases and are **rejected on new headers** (EF5 onward use the canonical form from day one). `shares/s` and `bps` already conform.

## 3. Hash impact (read from code) and decision

The unit string is part of content hashes, so **the rename is NOT made now**. Evidence, by code path (all in core main d564a98):

- `FeatureColumn.unit` is serialised by `FeatureResult.metadata_json()` (`packages/contracts/src/equity_feature_contracts/results.py`, the `"unit"` key). That string is (a) compared by `require_same_identity` (partials and merges of the same feature must carry the identical string), and (b) written as the Parquet schema metadata `equity.result` by `columnar.py` line 118, so every Parquet/bundle/DuckDB artifact whose bytes or digest cover that metadata changes.
- `packages/evidence/src/equity_feature_evidence/_content.py` includes `('unit', value.unit)` in the canonical content of every `results.FeatureColumn`, so the evidence content hash of any result holding the five affected headers changes.
- `OutputField(..., unit)` in the EF4 definitions (`_vwap.py`, `_rate_projection.py` META tables feed `FeatureColumn` and the definition outputs) means the registry/definition descriptors of the five headers change.
- The expected-result fixtures and oracle digests of the cases that publish the five headers (EF4 quote/VWAP slope cases, projection rate cases) would be regenerated, and the same-identity check would refuse mixing pre- and post-rename partials.

Affected content hashes if renamed (all to be re-baselined together at the contract-version boundary): result metadata JSON and Parquet `equity.result` metadata for the five headers; evidence content hashes of those columns; definition/registry descriptors for `rate.window.trade_rate`, `rate.window.notional_rate`, `rate.window.return_rate_difference`, `vwap.slope.endpoint`, `vwap.slope.ols`; the result fixtures/digests of the cases that emit them in the core, io and workers EF4 drivers; any stored output (DuckDB/Parquet) of those headers.

Decision: **deferred**, logged as a scheduled migration: apply the canonical spellings at the a5-to-next-contract-version boundary together with the fixture re-baseline; until then the library META strings and the contract JSON files keep the alias spellings, and the aliases above are the mapping. No hash, fixture or code changed by this document.
