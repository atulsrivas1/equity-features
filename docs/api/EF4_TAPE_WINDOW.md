# EF4 tape window and tick-rule signed volume

Use `build_tape_window_config`, `decode_tape_window_config`, `compute_tape_window` (or the closed `compute_ef4_tape`), `ef4_tape_definitions` and `require_ef4_tape_capability` from `equity_features.ef4`. Config identity is `ef4.tape_window_sign`, algorithm `ef4-tape-window-v1`, schema `1`, policy `ef4-tape1`.

```python
from equity_features.ef4 import TAPE_FEATURES, TAPE_POLICY, build_tape_window_config, compute_tape_window

config = build_tape_window_config(policy_version=TAPE_POLICY, window_ns=60_000_000_000, seed_policy="supplied",
                                  evidence_limit=25, eligibility_policy=policy_label, session=target_session,
                                  availability=availability, adjustment=adjustment, price_unit=price_unit)
result = compute_tape_window((trades, seed), config, entity=entity,
                             features=("tape.window.count", "tape.tick.net_volume", "tape.tick.imbalance"))
```

Outputs (lexical): `tape.tick.down_volume`, `tape.tick.imbalance` (float64, fraction), `tape.tick.net_notional` (decimal128), `tape.tick.net_volume`, `tape.tick.neutral_volume`, `tape.tick.up_volume` (int64, shares), `tape.window.count` (int64, trades), `tape.window.notional` (decimal128, currency coefficient / 10^price_scale) and `tape.window.volume` (shares). The tick outputs are tick-rule proxies, never an observed aggressor or dealer position.

Parameters (no defaults): `policy_version`, `window_ns` W (1..2^63-1), `seed_policy` (`none` or `supplied`), `evidence_limit` (0..10000) and the `eligibility_policy` label; the session must not include opening or closing auctions. One window is one config and one result. The role slots are `trades` (a TRADE batch of the target entity and session in `[open, C)`; price, size and `known_at_ns` columns may be absent) and `seed` (one `ef4.tick.seed` REFERENCE fact, `reference_id` `x1:` plus the base64url of the caller's seed-set id, `effective_start_ns` strictly before the open, `effective_end_ns` the open, `text` `+`, `-` or `0`, `price` the print's coefficient; delivered exactly when the policy is `supplied`, a `None` slot is `absent_input` on the sign-based outputs).

The window is `[C - W, C)`; `C - W` before the open is `insufficient_history` for every output. The sign is `+1` on a price rise, `-1` on a fall and the previous sign on an unchanged price, from the seed (or `0` without one) over the whole epoch; expiry only removes prints from the totals, so the first in-window print inherits its sign from an expired one. Imbalance is `net_volume / window volume` with neutral volume in the denominator. Update, restore and merge are unsupported; a correction is a new tape revision recomputed from the seed. Evidence lists `seed:<reference_id>` first and then `trade:<event_id>`, cut to `evidence_limit` per output. See [implementation, deviations and validation](../ef4/TAPE_IMPLEMENTATION.md).
