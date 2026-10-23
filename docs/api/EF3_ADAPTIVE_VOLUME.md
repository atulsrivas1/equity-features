# EF3 adaptive volume diagnostics

Use `build_adaptive_volume_config`, `decode_adaptive_volume_config`, `compute_adaptive_volume` (or the closed `compute_ef3_breadth`), `ef3_breadth_definitions` and `require_ef3_breadth_capability` from `equity_features.ef3`. Config identity is `ef3.adaptive_volume`, algorithm `ef3-adaptive-volume-v1`, schema `1`, policy `ef3-adaptive1`. The family is defined generically by the contract and claims no equivalence with the audit opaque rows.

```python
from equity_features.ef3 import ADAPTIVE_POLICY, build_adaptive_volume_config, compute_adaptive_volume

config = build_adaptive_volume_config(policy_version=ADAPTIVE_POLICY, epoch="2026-10-23", tau_ns=60_000_000_000,
                                      warmup_count=5, session=target_session, availability=availability,
                                      adjustment=adjustment, price_unit=price_unit, evidence_limit=25)
result = compute_adaptive_volume((observations,), config, entity=entity,
                                 features=("adaptive.volume.baseline_rate", "adaptive.volume.peak_relative_rate"))
```

Outputs (lexical): `acceleration_scored_count`, `baseline_available` (bool), `baseline_rate` (`shares/s`), `latest_event_ns`, `observation_count`, `peak_relative_acceleration` (`1/s`), `peak_relative_acceleration_event_ns`, `peak_relative_rate` (`ratio`), `peak_relative_rate_event_ns`, `scored_count` (all `adaptive.volume.*`).

Parameters (no defaults): `policy_version`, `epoch`, `tau_ns` (1..2^62), `warmup_count` W (1..4096) and `evidence_limit`. The one nullable REFERENCE role `observations` carries `ef3.adaptive.rate` facts (`reference_id` `ao1:B(epoch):<19 digit sequence>:B(event_id)`, event time `effective_start_ns`, raw rate in shares per second `price * factor_num / factor_den`, both factors null or both positive, `text` the snapshot id); sequence strictly increases within the epoch and time is non-decreasing.

Observations with an event time before the market cutoff C are in scope, and every one must be known. The baseline is `B_1 = r_1`, `B_k = (tau B_(k-1) + d_k r_k) / (tau + d_k)` (an exact rational weight; an elapsed time of 0 leaves it unchanged). Observation `k >= W + 1` is scorable; its relative rate is `r_k / B_(k-1)` and its relative acceleration `(r_k - r_(k-1)) 10^9 / (d_k B_(k-1))` per second, each defined for a positive baseline (and a positive elapsed time; a zero baseline is counted, never an error). A peak is the exact maximum and its witness the event time of the earliest observation attaining it. A null rate in scope is `null_field` for every rate-dependent output; `observation_count` and `latest_event_ns` stay available. The result is a pure function of the in-scope prefix, a new epoch is a fresh stream, and update, restore and merge are unsupported. Evidence cites the witness observation (`seq:<n>`). See [implementation, gaps and contract nits](../ef3/BREADTH_ADAPTIVE_IMPLEMENTATION.md).
