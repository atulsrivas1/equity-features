# Equity Feature Contracts

Experimental0.0.3a5, Apache-2.0, CPython3.12 x64 on qualified Windows/Linux.
R1 session calculations use caller-supplied immutable canonical inputs and explicit
config/entity/source/coverage/knowledge declarations. Core imports require no
optional backend or source acquisition. Contracts depend only on stdlib; features
depend inward on the exact contracts package version.

The39-ID catalog advertises31 implemented batch IDs,23 R1 update/restore IDs and22
conditional merge IDs. Bar/price, interval structure, trade aggregates/topK,
sampled quote summaries and continuous time-weighted spread are implemented.
Continuous integration merge is unsupported; all eight history IDs support batch; other R2/custom execution remains false.
Typed structured results, quality/provenance/evidence, exact checked units/counts,
UTCns, explicit copied Arrow/NumPy bridges and stable contract errors apply.

SessionAccumulator has bounded fixed summaries/windows/K rows/N observations,
explicit prefix certificates, forward watermarks, immutable exact in-memory state
and compatible owned restore. Merge requires adjacent disjoint caller-certified
ranges, source/config/count/order compatibility and no publication/finalization.
Digests are corruption checks, not authentication; global discarded identity and
source delivery trust remain caller-owned. No persistence or throughput promise.

See [session API](../../docs/api/INCREMENTAL.md),
[R1 acceptance](../../docs/R1_ACCEPTANCE.md), and repository examples.
Experimental main GitHub Actions wheels/sdists are the distribution channel;
actual source/hashes/expiry/install receipts are recorded per story. No public
registry publication, stable API, concrete provider or automatic thread ownership.

EQ033 adds [pure supplied action/classification policies](../../docs/api/ACTION_POLICIES.md)
and immutable policy/evidence contracts; history.return/prior_high/prior_low now have batch APIs.
See [qualification record](../../docs/stories/EQ-033_DELIVERY.md).

[Historical context/windows](../../docs/api/HISTORY.md) define exact supplied grids
and independent readiness; no history state mode is claimed.

EQ028 adds exact SMA/anchored EMA and an owned exact SMAReference dependency;
[API](../../docs/api/HISTORY.md), [qualification](../../docs/stories/EQ-028_DELIVERY.md).

EQ029 adds anchored Wilder RSI/ATR with explicit gaps/previous close;
[API](../../docs/api/HISTORY.md), [qualification](../../docs/stories/EQ-029_DELIVERY.md).

EQ030 adds centered sample return volatility with explicit scaling/default1;
[API](../../docs/api/HISTORY.md), [qualification](../../docs/stories/EQ-030_DELIVERY.md).

EQ031 adds owned volume dependencies and batch-only daily baseline/relative volume; [API](../../docs/api/DAILY_VOLUME.md). No history state modes or source acquisition.
