"""Synthetic independent bucket readiness with an actual early close."""
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, BucketContext, BucketVolume, CanonicalBatch, Cell,
    Column, ConfigSpec, Coverage, DataKind, EntityKey, InputBinding, InputScope, Parameter,
    PriceUnit, SessionSpec, SourceBinding, Status, VolumeBucket, WindowSpec,
)
from equity_features.buckets import compute_interval_baseline, compute_interval_relative_volume

sessions = tuple(SessionSpec("synthetic", f"S{i}", 100*i+1, 100*i+(21 if i == 1 else 61),
                            "supplied", scheduled_close_ns=100*i+61, early_close=i == 1) for i in range(4))
ids = tuple(s.session_id for s in sessions)
unit = PriceUnit(0, "USD")
config = ConfigSpec("bucket-volume3", "v1", (Parameter("period", 3), Parameter("evidence_limit", 4)),
                    sessions[-1], WindowSpec(3, "S3", ids, "prior_only"), AvailabilitySpec(341, 366, 366), price_unit=unit)


def supplied(bucket: VolumeBucket) -> tuple[CanonicalBatch, BucketContext]:
    present = tuple(i for i, s in enumerate(sessions) if bucket.bounds(s)[1] <= s.close_ns)
    fields: dict[str, tuple[Cell, ...]] = {
        "instrument_id": ("A",)*4, "session_id": ids,
        "start_ns": tuple(bucket.bounds(s)[0] for s in sessions),
        "end_ns": tuple(bucket.bounds(s)[1] for s in sessions),
        "volume": (10, 20, 30, 50), "known_at_ns": tuple(bucket.bounds(s)[1] for s in sessions),
    }
    batch = CanonicalBatch(DataKind.BAR, tuple(Column(k, tuple(v[i] for i in present)) for k, v in fields.items()),
                           BatchMetadata("synthetic", SourceBinding("fixture", "r1", "v1", "buckets-"+bucket.name),
                                         Coverage(4, len(present), len(present) == 4), unit))
    context = BucketContext(EntityKey("A", "S3"), "grid-v1", sessions, bucket,
                            tuple(Coverage(1, int(i in present), i in present) for i in range(4)))
    return batch, context


late, late_context = supplied(VolumeBucket("late", 20, 40, "grid-v1"))
late_baseline = compute_interval_baseline(late, config, context=late_context)
assert late_baseline.result.quality[0].status == Status.INCOMPLETE_COVERAGE
assert (late_baseline.result.quality[0].expected, late_baseline.result.quality[0].observed) == (3, 2)
assert late_baseline.result.values[0].values == (None,)
morning, context = supplied(VolumeBucket("morning", 0, 10, "grid-v1"))
baseline = compute_interval_baseline(morning, config, context=context)
assert baseline.result.values[0].values == (20.0,)
target = BucketVolume(context.entity, 50, 311, InputBinding("target", DataKind.BAR, morning.metadata),
                      3, InputScope(301, 311, "all"), Coverage(1, 1, True), context.bucket, "raw_shares")
ratio = compute_interval_relative_volume(target, baseline, config, context=context)
assert ratio.values[0].values == (2.5,)
assert ratio.quality[0].status == Status.AVAILABLE
print("Independent morning mean20/ratio5/2 and early-close late bucket2/3 unavailable verified.")
