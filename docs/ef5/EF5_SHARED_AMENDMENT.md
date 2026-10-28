# EF5 shared amendment (proposal): header ledger and unit additions

Status: proposal, additive, PO-2 and PO-7 accepted 2026-10-28. Docs only.

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

## E9 erratum (squared form)

Additive erratum to E9, not a frozen-file edit: the squared form of the slash style is `fraction/s^2`. The underscore spellings `fraction_per_second` and `fraction_per_second_squared` are aliases only, recorded in the ownership manifest (`unit_aliases`), and appear in no header. EF4 headers keep their underscore spellings until the scheduled next-contract-version migration (core `DECISIONS.md` E9, `docs/ef4/EF4_LEDGER_APPLICATION.md`); this erratum concerns EF5 headers only.


## Cross-reference: undeclared coverage (PO-7)

EF5 refuses rows delivered with undeclared coverage as INVALID_SCHEMA, matching the merged tape adapter; the EF4 library uses the code ruled in E2. The divergence is documented, not accidental. Zero rows with undeclared coverage stays absent_input.


## Ownership manifest

`docs/plans/equity-output-ownership.json`: the two EQ-171 planned outputs `technical.price_velocity_fraction_per_second` and `technical.momentum_acceleration_fraction_per_second_squared` change unit to `fraction/s` and `fraction/s^2` (canonical names unchanged, old spellings in `unit_aliases`); 11 candle and structure headers are listed in `ef5_delivered_outputs` (proposed, not accepted, not implemented). The 47-output planned count is unchanged.

## Hash impact

No unit string of a frozen contract changes. The two manifest unit strings are documentation read in this PR only; the only reader is `tools/check_equity_delivery_replan.py`, which compares units between EF5 headers and manifest rows, and no content hash covers them.

## Divergences from the shared validators (PO ruling PQ-1)

- Currency: EF5 admission enforces exactly three upper-case letters (RF40, INVALID_UNIT at config). The shared `PriceUnit` is unchanged and accepts any non-empty string.
- Adjustment labels: EF5 `unadjusted` maps to shared `raw` and `split_adjusted` to shared `split`, for comparison only; the `basis` field echoes the EF5 label. `total_return` and every other label are UNSUPPORTED_ADJUSTMENT at config (RF41). The shared `AdjustmentSpec` is unchanged.
