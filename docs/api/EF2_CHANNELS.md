# EF2 Ichimoku and price channels

Use `build_channels_config`, `decode_channels_config`, `compute_channels`, `describe_channels`, `channels_catalog_digest` and `require_channels_capability` from `equity_features_intraday`. The context is the unchanged R17 `IntradayContext` and must be `reset` mode (carry is out of v1). Algorithm `ef2-channels-v1`, schema `1`, contract version `ef2-v1`; config identity `ef2.<producer>`.

```python
from equity_features_intraday import build_channels_config, compute_channels, describe_channels

config = build_channels_config(context, producer="ichimoku", conversion_period=9, base_period=26,
                               leading_b_period=52, displacement=26,
                               availability=availability, adjustment=adjustment,
                               price_unit=price_unit, evidence_limit=8)
result = compute_channels(batches, context, config)  # complete sorted header set; features=(...) selects a subset
```

One config computes one homogeneous producer and returns its complete sorted header set (an optional `features` tuple selects a subset of that producer's IDs). Parameters are exactly that producer's operation parameters, `convention_version` (the producer's single label), `evidence_limit` (0..10000) and the R17 context transport (`context_schema`, `context_sha256`, `context_chunks`, `context_000`...). No parameter has a default. The builder takes only the producer's keywords (a missing or surplus one is `INVALID_CONFIG`; `convention_version` defaults to the label and any other value is `INCOMPATIBLE_VERSION`). `decode_channels_config(context, config)` validates the closed envelope and returns `ChannelsSettings(producer, values, evidence_limit)`.

| Producer (identity, label) | Operation parameters and bounds | Headers (id prefix; unit) |
| --- | --- | --- |
| `ichimoku` (`ef2.ichimoku`, `ef2-ichimoku-conv1`) | `conversion_period`, `base_period`, `leading_b_period`, `displacement` in 1..4096 | `trend.ichimoku.` `base_line`, `conversion_line`, `lagging_line_observed`, `lagging_line_reference_close`, `leading_span_a_displayed`, `leading_span_a_observed`, `leading_span_b_displayed`, `leading_span_b_observed` (`currency/share`) |
| `keltner` (`ef2.keltner`, `ef2-keltner-conv1`) | `ema_period` 1..4096, `atr_period` 1..4095, `atr_multiplier_num/den` reduced, 1..1000000 | `channel.keltner.` `lower`, `middle`, `upper` (`currency/share`), `width_ratio` (`fraction`) |
| `donchian` (`ef2.donchian`, `ef2-donchian-conv1`) | `period` 1..4096 | `channel.donchian.` `lower`, `middle`, `upper` (`currency/share`), `width_ratio` (`fraction`) |
| `pivot_levels` (`ef2.pivot_levels`, `ef2-pivot-conv1`) | none | `channel.pivot.` `point`, `resistance_1`, `resistance_2`, `support_1`, `support_2` (`currency/share`) |
| `band_width_percentile` (`ef2.band_width_percentile`, `ef2-bandpct-conv1`) | `band_period` 2..4096, `band_k_num/den` reduced, `population_size` 1..4096, `min_population` 1..`population_size` | `channel.band_width.percentile` (`fraction`) |
| `bollinger_keltner_squeeze` (`ef2.bollinger_keltner_squeeze`, `ef2-squeeze-conv1`) | `band_period`, `band_k_num/den`, `ema_period`, `atr_period`, `atr_multiplier_num/den` as above | `channel.squeeze.` `bollinger_inside_keltner` (bool, `boolean`), `lower_gap`, `upper_gap` (`currency/share`) |

`batches` is `None` (absent delivery) or a tuple of R17 BAR chunks on the governed grid with the R17 per-slot coverage, ordering, duplicate and cutoff rules (one chunk per governed session; the pivots read the whole immediately preceding session, so its bars must be supplied). Required columns: Ichimoku `high` and `low` (and `close` for the lagging pair), Keltner and the squeeze `close`, `high` and `low`, Donchian `high` and `low`, pivots `high`, `low` and the last prior-session `close`, the percentile `close` only. The result has one scalar per header in lexical order, each with its own quality row, column algorithm `ef2-channels-v1`, backend `intraday.python` and the R17 input bindings `bars:000`.... Discovery (`describe_channels`) lists the 25 IDs with batch capability only; `require_channels_capability` refuses update, restore and merge with `UNSUPPORTED_CAPABILITY`. The R17 `describe_intraday`, `compute_intraday` and the R17 catalog digest are unchanged. Numeric policy is the R17 Decimal120 recurrence policy with the R17 tolerance; exact zeros publish `+0.0`; the percentile and the squeeze boolean are decided on exact integers and Decimal120 algebra.

Observation versus display: the `_observed` spans are origin-time values (to be drawn `displacement` bars later; no timestamp is produced), the `_displayed` spans are computed at `t - displacement` and read no later bar, `lagging_line_observed` is the close at `t` and `lagging_line_reference_close` the close at `t - displacement`; any shifted value outside the anchored grid is `insufficient_history`.

Typed refusals (no `FeatureResult`): `INVALID_CONFIG` (parameter shape, bounds, reduced multipliers, `band_period` 1, `min_population`, missing or surplus parameter, evidence limit, carry mode), `INCOMPATIBLE_VERSION` (unsupported convention label, algorithm or context codec), `UNKNOWN_FEATURE` (an ID outside the producer), `UNSUPPORTED_CAPABILITY`, `INCONSISTENT_IDENTITY`, `INVALID_UNIT`, `UNSUPPORTED_ADJUSTMENT`, `DUPLICATE`, `INVALID_ORDER`, `BOUNDS`, `INVALID_SCHEMA` (from shared BAR validation) and `OVERFLOW`. See [mathematics, readiness and open points](../ef2/ICHIMOKU_CHANNELS_IMPLEMENTATION.md) and the [frozen contract](../ef2/ICHIMOKU_CHANNELS_CONTRACT_PROPOSAL.md).
