# EF4 notional-ranked largest prints

Use `build_notional_top_k_config`, `decode_notional_top_k_config`, `compute_trade_top_k_notional` (or the closed `compute_ef4_tape`), `merge_trade_top_k_notional`, `ef4_tape_definitions` and `require_ef4_tape_capability` from `equity_features.ef4`. Config identity is `ef4.trade_top_k_notional`, algorithm `ef4-top-k-notional-v1`, schema `1`, policy `ef4-notional1`. The output is `tape.top_k_notional` (the existing `top_k_trades` cell, unit bounded original trade-row evidence). The size-ranked `session.trade.top_k` is a different ranking and is unchanged.

```python
from equity_features.ef4 import (NotionalPartial, TOP_K_POLICY, build_notional_top_k_config,
                                 compute_trade_top_k_notional, merge_trade_top_k_notional)

config = build_notional_top_k_config(policy_version=TOP_K_POLICY, top_k=10, evidence_limit=10,
                                     eligibility_policy=policy_label, session=target_session,
                                     availability=availability, adjustment=adjustment, price_unit=price_unit)
result = compute_trade_top_k_notional((trades,), config, entity=entity, features=("tape.top_k_notional",))
merged = merge_trade_top_k_notional([NotionalPartial(config, entity, result_1), NotionalPartial(config, entity, result_2)])
```

Parameters (no defaults): `policy_version`, `top_k` K (1..10000), `evidence_limit` (K..10000) and the `eligibility_policy` label; auction choices follow the session config as for `session.trade.top_k`. The single role slot `trades` is admitted exactly as for `session.trade.*`. The rank key is `(-price * size, event_ns, order_key, event_id)` with the exact integer notional (always below 10^38) and the event identity compared by Unicode code point; the result holds `min(K, n)` rows and a fully covered empty or all-ineligible population is an available empty table. Evidence lists the retained rows in rank order by plain `event_id`, with boundary `closing_auction` for a print at the cutoff.

Merge: compatible available partials (same policy version, K, evidence limit, price unit, adjustment, eligibility policy, entity, market cutoff and knowledge cutoff) are concatenated, sorted by the rank key and cut to K; counts are summed, an unavailable partial makes the merged result unavailable with the union of reasons, the same retained `event_id` in two partials is `DUPLICATE` and disjointness of unretained rows is certified by the caller. Update and restore are unsupported. The cell rows are in notional order, which the shared `TopKTrades` constructor does not check; see the note in [the implementation document](../ef4/TAPE_IMPLEMENTATION.md).
