# EF6 shared amendment (proposal): header ledger and unit additions

Status: draft proposal, additive, docs only; not frozen. Internal, synthetic, pre-release.

## Unit additions (E9 slash style)

| Unit | dtype | Used by |
|---|---|---|
| `sessions` | int64 | history.window_high_offset, history.window_low_offset |

Reused without change: `currency/share`, `fraction`.

## Header ledger additions

The 10 headers of [DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json](DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json) are to be added additively to the shared ledger:

| Id | dtype | Unit | Producer |
|---|---|---|---|
| `core.benchmark_return_range_fraction` | float64 | `fraction` | core_spread |
| `core.benchmark_return_stdev_fraction` | float64 | `fraction` | core_spread |
| `history.atr_simple_mean` | float64 | `currency/share` | atr_simple_mean |
| `history.window_high` | float64 | `currency/share` | window_extreme |
| `history.window_high_offset` | int64 | `sessions` | window_extreme |
| `history.window_low` | float64 | `currency/share` | window_extreme |
| `history.window_low_offset` | int64 | `sessions` | window_extreme |
| `relative.log_return_beta` | float64 | `fraction` | relative_log_stats |
| `relative.log_return_correlation` | float64 | `fraction` | relative_log_stats |
| `session.price.range_over_open` | float64 | `fraction` | session_range_over_open |

## Deprecated id (no ledger change)

`core.benchmark_return_dispersion_fraction` stays in the EF4 ledger unchanged. It publishes the range of core returns; the deprecation is a description-only change (EF6-3) recorded in [EF4_ERRATA.md](../ef4/EF4_ERRATA.md), with removal at the scheduled EF4 next-contract-version migration.

## Ownership manifest

`docs/plans/equity-output-ownership.json` gains `ef6_delivered_outputs` (10 proposed entries, not accepted, not implemented). `tools/check_equity_delivery_replan.py` enforces header/manifest parity and unit equality. The 47-output planned count is unchanged.

## Hash impact

No unit string or text of a frozen contract changes. The only edited EF4 file is the errata table, which no digest covers.
