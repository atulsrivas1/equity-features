# EF5 shared amendment (proposal): header ledger and unit additions

Status: proposal, additive, pending PO ruling PO-2. Docs only.

## Unit additions (E9 slash style)

| Unit | dtype | Used by | Alias recorded |
|---|---|---|---|
| `fraction/s` | float64 | technical.price_velocity_fraction_per_second | fraction_per_second |
| `fraction/s^2` | float64 | technical.momentum_acceleration_fraction_per_second_squared | fraction_per_second_squared |
| `windows` | int64 | technical.signed_trend_window_count | - |

Reused without change: `boolean`, `currency/share`, `fraction`.

## Header ledger additions

The 15 headers of [PRICE_STRUCTURES_CONTRACT_PROPOSAL.json](PRICE_STRUCTURES_CONTRACT_PROPOSAL.json) are to be added additively to the shared ledger:

| Id | dtype | Unit | Producer |
|---|---|---|---|
| `candle.body_fraction` | float64 | `fraction` | candle |
| `candle.doji` | bool | `boolean` | candle |
| `candle.engulfing_bearish` | bool | `boolean` | candle |
| `candle.engulfing_bullish` | bool | `boolean` | candle |
| `candle.inside_bar` | bool | `boolean` | candle |
| `candle.lower_shadow_fraction` | float64 | `fraction` | candle |
| `candle.upper_shadow_fraction` | float64 | `fraction` | candle |
| `structure.last_swing_high_price` | float64 | `currency/share` | structure |
| `structure.last_swing_low_price` | float64 | `currency/share` | structure |
| `structure.swing_high_confirmed` | bool | `boolean` | structure |
| `structure.swing_low_confirmed` | bool | `boolean` | structure |
| `technical.momentum_acceleration_fraction_per_second_squared` | float64 | `fraction/s^2` | technical |
| `technical.price_velocity_fraction_per_second` | float64 | `fraction/s` | technical |
| `technical.session_return_fraction` | float64 | `fraction` | technical |
| `technical.signed_trend_window_count` | int64 | `windows` | technical |

## Ownership manifest

`docs/plans/equity-output-ownership.json`: the two EQ-171 planned outputs `technical.price_velocity_fraction_per_second` and `technical.momentum_acceleration_fraction_per_second_squared` change unit to `fraction/s` and `fraction/s^2` (canonical names unchanged, old spellings in `unit_aliases`); 11 candle and structure headers are listed in `ef5_delivered_outputs` (proposed, not accepted, not implemented). The 47-output planned count is unchanged.

## Hash impact

No unit string of a frozen contract changes. The two manifest unit strings are documentation read in this PR only; the only reader is `tools/check_equity_delivery_replan.py`, which compares units between EF5 headers and manifest rows, and no content hash covers them.
