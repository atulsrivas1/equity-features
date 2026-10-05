"""Explicit implementation inventory; dependency-light discovery never imports kernels."""
BAR_IDS = (
    "session.bar.open", "session.bar.high", "session.bar.low", "session.bar.close",
    "session.bar.volume", "session.bar.notional", "session.bar.close_weighted_price",
    "session.price.open_close_return", "session.price.range_fraction",
    "session.price.close_location", "session.price.overnight_gap",
    "session.price.close_close_return",
)
STRUCTURE_IDS = ("session.structure.interval_ohlcv", "session.structure.interval_volume_share")
TRADE_IDS = ("session.trade.count", "session.trade.volume", "session.trade.notional", "session.trade.vwap", "session.trade.mean_size")
TOP_K_IDS = ("session.trade.top_k",)
QUOTE_IDS = ("session.quote.sampled_spread", "session.quote.state_counts")
CONTINUOUS_IDS = ("session.quote.time_weighted_spread",)
SESSION_BATCH_IDS = frozenset(BAR_IDS+STRUCTURE_IDS+TRADE_IDS+TOP_K_IDS+QUOTE_IDS+CONTINUOUS_IDS)

HISTORY_IDS = ("history.return", "history.prior_high", "history.prior_low", "history.sma", "history.ema")
BATCH_IDS = SESSION_BATCH_IDS | frozenset(HISTORY_IDS)

UPDATE_IDS = SESSION_BATCH_IDS
RESTORE_IDS = SESSION_BATCH_IDS
MERGE_IDS = SESSION_BATCH_IDS - frozenset(CONTINUOUS_IDS)
