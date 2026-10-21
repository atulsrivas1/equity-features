# EF1 observable-v2 Python API

Use the existing `equity_features.ef1` entry points:
`build_ef1_config`, `decode_ef1_context`, `ef1_definitions`, `compute_ef1`.
The [frozen observable contract](../ef1/OBSERVABLE_CONTRACT_PROPOSAL.md) specifies
the exact closed `ef1-observable-context2` context and `ef1-observable-map2`
mapping. Config and feature algorithm_version remain `observable-v2`; global result
math_policy_version is `v1` under the reviewed
[publication amendment](../ef1/OBSERVABLE_PUBLICATION_AMENDMENT.md).
The existing canonical exact-integer/nullable/evidence rules need no new global
precision policy. Backend_id is `ef1`, backend_version is the actual distribution
version (currently0.0.4a5), and canonical schema remains1.

The pure call retains exact nullable positional roles:

| Producer | Input tuple |
| --- | --- |
| opening_trade / opening_trade_seconds | calendar_provenance, market_prefix, source_capability, trades |
| status_history | calendar_provenance, history_events, history_prefix, history_seed, source_capability |

Each element is an actual CanonicalBatch or None. A delivered zero-row batch stays
present at its declared index. Never compress the tuple, infer an empty role from
its input_id, or manufacture an empty batch for absence. All-None gives truthful
absent-calendar quality with no fabricated input bindings. Wrong container,
length or per-slot kind is invalid_schema.

```python
from equity_features.ef1 import build_ef1_config, compute_ef1, ef1_definitions

# caller_context contains the explicitly supplied calendar/selection/version;
# all other values below are caller-owned canonical contract objects.
config = build_ef1_config(caller_context, session=session, window=window,
    availability=availability, price_unit=price_unit, adjustment=adjustment)
headers = ef1_definitions(config)
result = compute_ef1((calendar_provenance, market_prefix,
    source_capability, trades), config, entity=entity)
```

Adapters own representation conversion and workers own orchestration/sink
publication. `.slots` on an adapter input object is the pure argument; a
present-only `.batches` view is insufficient. Calculations perform no database,
file, network, scheduling or wall-clock operation. Full replay is a new identical
pure call and returns identical values/quality/metadata/evidence. No mutable
restore/update protocol or public HTTP service is added.

Bounds include4096 aggregate REFERENCE rows,4096 TRADE rows,4096 context bytes,
closed256-byte ASCII proof IDs/payload,64 mapping rows, and32 evidence rows.
Workers additionally enforce the existing1MiB encoded task bound. A candidate
result with33 evidence rows is rejected by the canonical result boundary; a
candidate result is never a pure compute input. Existing producers, defaults,
codecs, versions and39 core feature IDs remain unchanged.
