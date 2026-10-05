"""Explicit implementation inventory; dependency-light discovery never imports kernels."""
BAR_IDS = (
    "session.bar.open", "session.bar.high", "session.bar.low", "session.bar.close",
    "session.bar.volume", "session.bar.notional", "session.bar.close_weighted_price",
    "session.price.open_close_return", "session.price.range_fraction",
    "session.price.close_location", "session.price.overnight_gap",
    "session.price.close_close_return",
)
BATCH_IDS = frozenset(BAR_IDS)
