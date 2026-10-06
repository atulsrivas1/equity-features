"""Independent exact bucket math, coverage and supplied dependency fixtures."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import unittest
from equity_feature_contracts import (
    ActionPolicy, AdjustmentSpec, AvailabilitySpec, BatchMetadata, BucketContext, BucketVolume,
    CanonicalBatch, Column, ConfigSpec, ContractError, Coverage, DataKind, EntityKey,
    ErrorCode, InputBinding, InputScope, Parameter, PriceUnit, Reason, SessionSpec,
    SourceBinding, Status, VolumeBucket, WindowSpec, builtin_registry,
)
from equity_features.buckets import compute_interval_baseline, compute_interval_relative_volume
from equity_features.policies import admit_action_policy


def fixture(volumes=(10, 20, 30, 50), *, period=3, bucket=None, early=(), missing=(), target=None, cutoff=None, evidence=20):
    bucket = VolumeBucket("morning", 0, 10, "grid-v1") if bucket is None else bucket
    n = len(volumes)
    target = n-1 if target is None else target
    sessions = tuple(SessionSpec("synthetic", f"S{i}", 100*i+1, 100*i+(21 if i in early else 61), "supplied",
                                 scheduled_close_ns=100*i+61, early_close=i in early) for i in range(n))
    present = tuple(i for i in range(n) if i not in missing and bucket.bounds(sessions[i])[1] <= sessions[i].close_ns)
    values = dict(instrument_id=("A",)*n, session_id=tuple(s.session_id for s in sessions),
                  start_ns=tuple(bucket.bounds(s)[0] for s in sessions), end_ns=tuple(bucket.bounds(s)[1] for s in sessions),
                  volume=volumes, known_at_ns=tuple(bucket.bounds(s)[1] for s in sessions))
    unit = PriceUnit(0, "USD")
    batch = CanonicalBatch(DataKind.BAR, tuple(Column(k, tuple(v[i] for i in present)) for k, v in values.items()),
                           BatchMetadata("synthetic", SourceBinding("fixture", "r1", "v1", "bucket-volumes"), Coverage(n, len(present), len(present) == n), unit))
    context = BucketContext(EntityKey("A", f"S{target}"), bucket.grid_version, sessions, bucket,
                            tuple(Coverage(1, int(i in present), i in present) for i in range(n)))
    session = sessions[target]
    cfg = ConfigSpec("bucket", "v1", (Parameter("period", period), Parameter("evidence_limit", evidence)), session,
                     WindowSpec(period, session.session_id, tuple(s.session_id for s in sessions), "prior_only"),
                     AvailabilitySpec(min(bucket.bounds(session)[1], session.close_ns) if cutoff is None else cutoff,
                                      session.close_ns+5, session.close_ns+5), price_unit=unit)
    return batch, cfg, context


def fact(cfg, ctx, volume=50, *, end=None, complete=True):
    start, full_end = ctx.bucket.bounds(cfg.session)
    interval = InputScope(start, full_end if end is None else end, "all")
    binding = InputBinding("bucket_target", DataKind.BAR, BatchMetadata("synthetic",
                           SourceBinding("fixture", "r1", "v1", "target-bucket"), Coverage(1, 1, True), cfg.price_unit, cfg.adjustment))
    return BucketVolume(ctx.entity, volume, interval.end_ns, binding, 0, interval, Coverage(1, 1, complete), ctx.bucket, "raw_shares")


class BucketVolumeTests(unittest.TestCase):
    def assertCode(self, code, callback):
        with self.assertRaises(ContractError) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def calculate(self, b, cfg, ctx):
        return compute_interval_baseline(b, cfg, context=ctx)

    def test_exact_individual_bucket_mean_and_supplied_ratio(self):
        b, cfg, ctx = fixture()
        ref = self.calculate(b, cfg, ctx)
        self.assertEqual((ref.numerator, ref.denominator, ref.result.values[0].values), (60, 3, (20.0,)))
        result = compute_interval_relative_volume(fact(cfg, ctx), ref, cfg, context=ctx)
        self.assertEqual(result.values[0].values, (2.5,))
        self.assertEqual(result.quality[0].observed, 2)
        self.assertEqual(result.evidence[-1].event_ns, 311)

    def test_early_close_does_not_shrink_denominator_other_bucket_ready(self):
        late = VolumeBucket("late", 20, 40, "grid-v1")
        b, cfg, ctx = fixture(bucket=late, early=(1,))
        ref = self.calculate(b, cfg, ctx)
        q = ref.result.quality[0]
        self.assertEqual((q.status, q.expected, q.observed), (Status.INCOMPLETE_COVERAGE, 3, 2))
        self.assertIn(Reason.INELIGIBLE, q.reasons)
        self.assertIsNone(ref.numerator)
        self.assertEqual(len(ref.result.evidence), 2)  # No fabricated source row for absent bucket.
        b, cfg, ctx = fixture(early=(1,))
        self.assertEqual(self.calculate(b, cfg, ctx).result.values[0].values, (20.0,))

    def test_half_open_offset_alignment_and_variable_actual_opens(self):
        bucket = VolumeBucket("offset", 7, 17, "grid-v1")
        b, cfg, ctx = fixture(bucket=bucket)
        self.assertEqual(self.calculate(b, cfg, ctx).result.evidence[0].effective_start_ns, 8)
        self.assertEqual(self.calculate(b, cfg, ctx).result.evidence[0].effective_end_ns, 18)
        shifted = replace(b, columns=tuple(Column(c.name, tuple(x+1 for x in c.values)) if c.name == "start_ns" else c for c in b.columns))
        self.assertCode(ErrorCode.BOUNDS, lambda: self.calculate(shifted, cfg, ctx))
        widened = replace(b, columns=tuple(Column(c.name, tuple(x+1 for x in c.values)) if c.name == "end_ns" else c for c in b.columns))
        self.assertCode(ErrorCode.BOUNDS, lambda: self.calculate(widened, cfg, ctx))

    def test_target_future_mutation_and_independent_finite_recovery(self):
        b, cfg, ctx = fixture((10, 20, 30, 9999, 8888), target=3)
        changed = replace(b, columns=tuple(Column(c.name, (10, 20, 30, None, 0)) if c.name == "volume" else c for c in b.columns))
        self.assertEqual(self.calculate(b, cfg, ctx), self.calculate(changed, cfg, ctx))
        b, cfg, ctx = fixture((10, 20, 30, 40, 50), missing=(0,))
        self.assertEqual(self.calculate(b, cfg, ctx).result.values[0].values, (30.0,))

    def test_missing_null_absent_and_insufficient(self):
        b, cfg, ctx = fixture(missing=(1,))
        self.assertEqual(self.calculate(b, cfg, ctx).result.quality[0].observed, 2)
        b, cfg, ctx = fixture((10, None, 30, 50))
        self.assertIn(Reason.NULL_FIELD, self.calculate(b, cfg, ctx).result.quality[0].reasons)
        self.assertEqual(self.calculate(None, cfg, ctx).result.quality[0].status, Status.MISSING_INPUT)
        absent = replace(b, columns=tuple(c for c in b.columns if c.name != "volume"))
        self.assertEqual(self.calculate(absent, cfg, ctx).result.quality[0].status, Status.MISSING_INPUT)
        b, cfg, ctx = fixture((10, 20), period=3)
        self.assertEqual(self.calculate(b, cfg, ctx).result.quality[0].status, Status.INSUFFICIENT_HISTORY)

    def test_zero_mean_undefined_ratio_and_missing_precedence(self):
        b, cfg, ctx = fixture((0, 0, 0, 0))
        ref = self.calculate(b, cfg, ctx)
        self.assertEqual(ref.result.values[0].values, (0.0,))
        zero = compute_interval_relative_volume(fact(cfg, ctx, 0), ref, cfg, context=ctx)
        self.assertEqual(zero.quality[0].status, Status.NOT_APPLICABLE)
        self.assertIn(Reason.ZERO_DENOMINATOR, zero.quality[0].reasons)
        missing = compute_interval_relative_volume(None, ref, cfg, context=ctx)
        self.assertEqual(missing.quality[0].status, Status.MISSING_INPUT)
        self.assertNotIn(Reason.ZERO_DENOMINATOR, missing.quality[0].reasons)

    def test_elapsed_equals_cutoff_partial_and_future_target(self):
        b, cfg, ctx = fixture(cutoff=306)
        ref = self.calculate(b, cfg, ctx)
        future = compute_interval_relative_volume(fact(cfg, ctx), ref, cfg, context=ctx)
        self.assertIn(Reason.FUTURE_MARKET, future.quality[0].reasons)
        partial = compute_interval_relative_volume(fact(cfg, ctx, 25, end=306), ref, cfg, context=ctx)
        self.assertEqual(partial.quality[0].status, Status.INCOMPLETE_COVERAGE)
        self.assertIn(Reason.GOVERNED_GAP, partial.quality[0].reasons)
        b, cfg, ctx = fixture()
        ref = self.calculate(b, cfg, ctx)
        ready = compute_interval_relative_volume(fact(cfg, ctx), ref, cfg, context=ctx)
        self.assertEqual(ready.quality[0].status, Status.AVAILABLE)
        uncertified = compute_interval_relative_volume(fact(cfg, ctx, complete=False), ref, cfg, context=ctx)
        self.assertEqual(uncertified.quality[0].status, Status.INCOMPLETE_COVERAGE)

    def test_ineligible_target_without_phantom_row(self):
        b, cfg, ctx = fixture(bucket=VolumeBucket("late", 20, 40, "grid-v1"), early=(3,))
        ref = self.calculate(b, cfg, ctx)
        self.assertEqual(ref.result.quality[0].status, Status.AVAILABLE)
        result = compute_interval_relative_volume(None, ref, cfg, context=ctx)
        self.assertEqual(result.quality[0].status, Status.INCOMPLETE_COVERAGE)
        self.assertIn(Reason.INELIGIBLE, result.quality[0].reasons)
        self.assertEqual(len(result.evidence), 3)

    def test_default20_period1_and_wide_exact_sum(self):
        b, cfg, ctx = fixture(tuple(range(21)), period=20)
        cfg = replace(cfg, parameters=())
        self.assertEqual(self.calculate(b, cfg, ctx).result.values[0].values, (9.5,))
        m = 2**63-1
        b, cfg, ctx = fixture((m, m-1, m-2, 1))
        self.assertEqual(self.calculate(b, cfg, ctx).numerator, 3*m-3)
        b, cfg, ctx = fixture((7, 99), period=1)
        self.assertEqual(self.calculate(b, cfg, ctx).result.values[0].values, (7.0,))

    def test_configuration_grid_unit_and_quantity_guards(self):
        b, cfg, ctx = fixture()
        for parameters in ((Parameter("period", True),), (Parameter("period", 0),), (Parameter("unused", 1),)):
            self.assertCode(ErrorCode.INVALID_CONFIG, lambda: self.calculate(b, replace(cfg, parameters=parameters), ctx))
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: replace(ctx, grid_version="another"))
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: self.calculate(replace(b, metadata=replace(b.metadata, price_unit=PriceUnit(1, "USD"))), cfg, ctx))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.calculate(b, replace(cfg, parameters=cfg.parameters+(Parameter("quantity_basis", "split_shares"),)), ctx))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_interval_relative_volume(replace(fact(cfg, ctx), bucket=replace(ctx.bucket, name="another")), self.calculate(b, cfg, ctx), cfg, context=ctx))

    def test_source_revision_same_frame_and_original_evidence(self):
        b, cfg, ctx = fixture()
        ref = self.calculate(b, cfg, ctx)
        target = replace(fact(cfg, ctx), source=InputBinding("target", DataKind.BAR, b.metadata), row_index=3)
        result = compute_interval_relative_volume(target, ref, cfg, context=ctx)
        self.assertEqual(sum(x.metadata.source.input_id == "bucket-volumes" for x in result.metadata.inputs), 1)
        self.assertEqual(result.evidence[-1].row_id, "3")
        revised = replace(b, metadata=replace(b.metadata, source=replace(b.metadata.source, snapshot_id="r2")))
        self.assertNotEqual(self.calculate(revised, cfg, ctx).identity_digest, ref.identity_digest)
        bad = replace(target, source=replace(target.source, metadata=revised.metadata))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_interval_relative_volume(bad, ref, cfg, context=ctx))

    def test_original_row_scope_and_shifted_target_bounds(self):
        b, cfg, ctx = fixture()
        target = fact(cfg, ctx)
        ref = self.calculate(b, cfg, ctx)
        self.assertCode(ErrorCode.BOUNDS, lambda: replace(target, row_index=1))
        self.assertCode(ErrorCode.BOUNDS, lambda: compute_interval_relative_volume(replace(target, interval=InputScope(302, 311, "all")), ref, cfg, context=ctx))
        self.assertCode(ErrorCode.BOUNDS, lambda: compute_interval_relative_volume(replace(target, interval=InputScope(301, 312, "all")), ref, cfg, context=ctx))
        self.assertCode(ErrorCode.BOUNDS, lambda: replace(target, source=replace(target.source, metadata=replace(target.source.metadata, scope=InputScope(302, 311, "all")))))

    def test_knowledge_unknown_late_and_reconstruction_preserved(self):
        b, cfg, ctx = fixture()
        altered = replace(b, columns=tuple(Column(c.name, (11, None, 999, 311)) if c.name == "known_at_ns" else c for c in b.columns))
        ref = self.calculate(altered, cfg, ctx)
        self.assertEqual(ref.result.quality[0].status, Status.MISSING_INPUT)
        self.assertIn(Reason.FUTURE_KNOWLEDGE, ref.result.quality[0].reasons)
        rec_cfg = replace(cfg, availability=AvailabilitySpec(311, 366, 366, "reconstruction", "synthetic audit"))
        replay = self.calculate(altered, rec_cfg, ctx)
        self.assertEqual(replay.result.values[0].values, (20.0,))
        self.assertIsNone(replay.result.evidence[1].known_at_ns)
        target = replace(fact(cfg, ctx), known_at_ns=None)
        result = compute_interval_relative_volume(target, self.calculate(b, cfg, ctx), cfg, context=ctx)
        self.assertIn(Reason.UNKNOWN_AVAILABILITY, result.quality[0].reasons)

    def test_action_dependency_and_identity_guards(self):
        b, cfg, ctx = fixture()
        adjustment = AdjustmentSpec("split", "split-factors-v1", "actions", "S3")
        cfg = replace(cfg, adjustment=adjustment)
        b = replace(b, metadata=replace(b.metadata, adjustment=adjustment))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.calculate(b, cfg, ctx))
        admission = admit_action_policy(None, ActionPolicy(adjustment, 311), cfg, entity=ctx.entity)
        ctx = replace(ctx, action_admission=admission)
        self.assertIn(Reason.MISSING_ACTION_EVIDENCE, self.calculate(b, cfg, ctx).result.quality[0].reasons)

    def test_owned_witness_bounded_evidence_and_false_modes(self):
        b, cfg, ctx = fixture(evidence=1)
        ref = self.calculate(b, cfg, ctx)
        with self.assertRaises(FrozenInstanceError):
            ref.numerator = 0
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(ref, numerator=61))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(ref, denominator=2))
        result = compute_interval_relative_volume(fact(cfg, ctx), ref, cfg, context=ctx)
        self.assertEqual(len(result.evidence), 1)
        for name in ("baseline.interval_volume", "baseline.interval_relative_volume"):
            caps = builtin_registry().get(name).capabilities
            self.assertTrue(caps.batch)
            self.assertFalse(caps.update or caps.restore or caps.merge)

    def test_available_supplied_split_shares_are_not_adjusted_twice(self):
        b, cfg, ctx = fixture()
        adjustment = AdjustmentSpec("split", "split-factors-v1", "actions", "S3")
        cfg = replace(cfg, adjustment=adjustment, parameters=cfg.parameters+(Parameter("quantity_basis", "split_shares"),))
        refs = CanonicalBatch(DataKind.REFERENCE, (
            Column("instrument_id", ("A",)), Column("session_id", ("S3",)), Column("reference_id", ("split",)),
            Column("fact_kind", ("split_factor",)), Column("effective_start_ns", (301,)),
            Column("factor_num", (1,)), Column("factor_den", (2,)), Column("known_at_ns", (311,))),
            BatchMetadata("synthetic", SourceBinding("fixture", "actions", "v1", "action-facts"), Coverage(1, 1, True), None))
        policy = ActionPolicy(adjustment, 311, representation="caller_transformed", quantity_basis="split_shares")
        ctx = replace(ctx, action_admission=admit_action_policy(refs, policy, cfg, entity=ctx.entity))
        b = replace(b, metadata=replace(b.metadata, adjustment=adjustment))
        ref = self.calculate(b, cfg, ctx)
        self.assertEqual(ref.numerator, 60)
        result = compute_interval_relative_volume(replace(fact(cfg, ctx), quantity_basis="split_shares"), ref, cfg, context=ctx)
        self.assertEqual(result.values[0].values, (2.5,))
        self.assertTrue(any(x.metadata.source.input_id == "action-facts" for x in result.metadata.inputs))

    def test_owned_grid_invalid_offsets_duplicate_order_and_overflow(self):
        b, cfg, ctx = fixture()
        sessions, certificates = list(ctx.sessions), list(ctx.slot_coverage)
        owned = replace(ctx, sessions=sessions, slot_coverage=certificates)
        sessions.clear()
        certificates.clear()
        self.assertEqual(len(owned.sessions), 4)
        for start, end in ((True, 10), (-1, 10), (10, 10), (20, 10)):
            self.assertCode(ErrorCode.BOUNDS, lambda: VolumeBucket("bad", start, end, "v1"))
        huge = VolumeBucket("huge", 0, 2**63-1, "grid-v1")
        self.assertCode(ErrorCode.OVERFLOW, lambda: replace(ctx, bucket=huge))
        self.assertCode(ErrorCode.DUPLICATE, lambda: replace(ctx, sessions=ctx.sessions[:3]+(ctx.sessions[0],)))
        reverse = replace(b, columns=tuple(Column(c.name, tuple(reversed(c.values))) for c in b.columns))
        self.assertCode(ErrorCode.INVALID_ORDER, lambda: self.calculate(reverse, cfg, ctx))
        self.assertCode(ErrorCode.INVALID_SCHEMA, lambda: replace(fact(cfg, ctx), source=replace(fact(cfg, ctx).source, kind=DataKind.DAILY)))

    def test_early_close_certificates_and_original_scope_cannot_contradict_bounds(self):
        late = VolumeBucket("late", 20, 40, "grid-v1")
        b, cfg, ctx = fixture(bucket=late, early=(1,))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(ctx, slot_coverage=(ctx.slot_coverage[0], Coverage(1, 1, True))+ctx.slot_coverage[2:]))
        b, cfg, ctx = fixture()
        narrowed = replace(b, metadata=replace(b.metadata, scope=InputScope(2, 311, "all")))
        self.assertCode(ErrorCode.BOUNDS, lambda: self.calculate(narrowed, cfg, ctx))
        sessions = tuple(replace(s, open_ns=s.open_ns+3, close_ns=s.close_ns+3, scheduled_close_ns=s.scheduled_close_ns+3) for s in ctx.sessions)
        ctx2 = replace(ctx, sessions=sessions)
        cfg2 = replace(cfg, session=sessions[-1], availability=replace(cfg.availability, market_cutoff_ns=314))
        b2 = replace(b, columns=tuple(Column(c.name, tuple(v+3 for v in c.values)) if c.name in ("start_ns", "end_ns", "known_at_ns") else c for c in b.columns))
        self.assertEqual(self.calculate(b2, cfg2, ctx2).result.values[0].values, (20.0,))


    def test_original_row_proof_admission_independent_of_retention(self):
        for limit in (1, 20):
            with self.subTest(evidence_limit=limit):
                b, cfg, ctx = fixture(evidence=limit)
                ref = compute_interval_baseline(b, cfg, context=ctx)
                target = replace(fact(cfg, ctx), source=InputBinding("bucket_target", DataKind.BAR, b.metadata), row_index=0)
                self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,
                                lambda: compute_interval_relative_volume(target, ref, cfg, context=ctx))
                coherent = replace(target, row_index=3)
                result = compute_interval_relative_volume(coherent, ref, cfg, context=ctx)
                self.assertEqual(result.values[0].values, (2.5,))
                self.assertLessEqual(len(result.evidence), limit)


if __name__ == "__main__":
    unittest.main()
