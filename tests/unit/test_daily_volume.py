"""Independent prior-only volume and supplied-dependency acceptance fixtures."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import unittest
from equity_feature_contracts import (
    ActionPolicy, AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, ContractError,
    Coverage, DataKind, EntityKey, ErrorCode, HistoryContext, InputBinding, InputScope,
    Parameter, PriceUnit, Reason, SessionSpec, SourceBinding, Status, TargetVolume,
    VolumeBaseline, WindowSpec, builtin_registry,
)
from equity_features.volume import compute_daily_baseline, compute_relative_volume
from equity_features.policies import admit_action_policy


def fixture(volumes=(100, 200, 300, 500), *, target=None, missing=(), period=3, cutoff=None, evidence=20, parameters=None):
    n = len(volumes)
    target = n-1 if target is None else target
    sessions = tuple(SessionSpec("synthetic", f"S{i}", i*10+1, i*10+10, "supplied") for i in range(n))
    present = tuple(i for i in range(n) if i not in missing)
    columns = dict(instrument_id=("A",)*n, session_id=tuple(s.session_id for s in sessions),
                   start_ns=tuple(s.open_ns for s in sessions), end_ns=tuple(s.close_ns for s in sessions),
                   volume=volumes, known_at_ns=tuple(s.close_ns for s in sessions))
    batch = CanonicalBatch(DataKind.DAILY, tuple(Column(k, tuple(v[i] for i in present)) for k, v in columns.items()),
                           BatchMetadata("synthetic", SourceBinding("synthetic", "r1", "v1", "volumes"),
                                         Coverage(n, len(present), len(present) == n), PriceUnit(0, "USD")))
    context = HistoryContext(EntityKey("A", f"S{target}"), "grid-v1", sessions,
                             tuple(Coverage(1, int(i in present), i in present) for i in range(n)))
    session = sessions[target]
    config = ConfigSpec("volume", "v1", parameters if parameters is not None else
                        (Parameter("period", period), Parameter("evidence_limit", evidence)), session,
                        WindowSpec(period, session.session_id, tuple(s.session_id for s in sessions), "prior_only"),
                        AvailabilitySpec(session.close_ns if cutoff is None else cutoff, session.close_ns+5, session.close_ns+5), price_unit=PriceUnit(0, "USD"))
    return batch, config, context


def target_fact(batch, config, context, volume=500, *, prefix=False, complete=True, known=None):
    interval = InputScope(config.session.open_ns, config.availability.market_cutoff_ns if prefix else config.session.close_ns, "all")
    source = InputBinding("target_volume", DataKind.BAR if prefix else DataKind.DAILY,
                          BatchMetadata("synthetic", SourceBinding("synthetic", "r1", "v1", "target"), Coverage(1, 1, True), config.price_unit))
    return TargetVolume(context.entity, volume, interval.end_ns if known is None else known, source, 0, interval,
                        Coverage(1, 1, complete), "observed_prefix" if prefix else "completed_eod", "raw_shares")


class DailyVolume(unittest.TestCase):
    def assertCode(self, code, callback):
        with self.assertRaises(ContractError) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def calculate(self, b, cfg, ctx):
        return compute_daily_baseline(b, cfg, context=ctx)

    def test_exact_prior_mean_and_supplied_ratio(self):
        b, cfg, ctx = fixture()
        ref = self.calculate(b, cfg, ctx)
        self.assertEqual((ref.numerator, ref.denominator, ref.result.values[0].values), (600, 3, (200.0,)))
        result = compute_relative_volume(target_fact(b, cfg, ctx), ref, cfg, context=ctx)
        self.assertEqual(result.values[0].values, (float(Fraction(5, 2)),))
        self.assertEqual((result.quality[0].expected, result.quality[0].observed), (2, 2))
        self.assertEqual(len(result.evidence), 4)

    def test_target_and_future_values_never_enter_baseline(self):
        b, cfg, ctx = fixture((100, 200, 300, 9000, 999999), target=3)
        first = self.calculate(b, cfg, ctx)
        changed = replace(b, columns=tuple(Column(c.name, (100, 200, 300, 0, None)) if c.name == "volume" else c for c in b.columns))
        second = self.calculate(changed, cfg, ctx)
        self.assertEqual(first, second)
        self.assertTrue(all(e.row_id in ("0", "1", "2") for e in second.result.evidence))

    def test_default20_and_one_slot(self):
        b, cfg, ctx = fixture(tuple(range(21)), period=20, parameters=())
        self.assertEqual(self.calculate(b, cfg, ctx).result.values[0].values, (9.5,))
        b, cfg, ctx = fixture((123, 999), period=1)
        self.assertEqual(self.calculate(b, cfg, ctx).result.values[0].values, (123.0,))

    def test_exact_wide_sum_and_fractional_projection(self):
        m = 2**63-1
        b, cfg, ctx = fixture((m, m-1, m-2, 1))
        ref = self.calculate(b, cfg, ctx)
        self.assertEqual(ref.numerator, 3*m-3)
        self.assertEqual(ref.result.values[0].values, (float(Fraction(3*m-3, 3)),))

    def test_zero_baseline_is_available_ratio_is_undefined(self):
        b, cfg, ctx = fixture((0, 0, 0, 0))
        ref = self.calculate(b, cfg, ctx)
        self.assertEqual(ref.result.quality[0].status, Status.AVAILABLE)
        self.assertEqual(ref.result.values[0].values, (0.0,))
        result = compute_relative_volume(target_fact(b, cfg, ctx, 0), ref, cfg, context=ctx)
        self.assertEqual(result.quality[0].status, Status.NOT_APPLICABLE)
        self.assertEqual(result.quality[0].reasons, (Reason.ZERO_DENOMINATOR,))

    def test_zero_target_and_missing_target_have_distinct_readiness(self):
        b, cfg, ctx = fixture()
        ref = self.calculate(b, cfg, ctx)
        zero = compute_relative_volume(target_fact(b, cfg, ctx, 0), ref, cfg, context=ctx)
        missing = compute_relative_volume(None, ref, cfg, context=ctx)
        null = compute_relative_volume(target_fact(b, cfg, ctx, None), ref, cfg, context=ctx)
        self.assertEqual(zero.values[0].values, (0.0,))
        self.assertEqual(missing.quality[0].status, Status.MISSING_INPUT)
        self.assertIn(Reason.NULL_FIELD, null.quality[0].reasons)

    def test_insufficient_gap_null_absent_and_finite_recovery(self):
        b, cfg, ctx = fixture((10, 20), period=3)
        self.assertEqual(self.calculate(b, cfg, ctx).result.quality[0].status, Status.INSUFFICIENT_HISTORY)
        b, cfg, ctx = fixture(missing=(1,))
        q = self.calculate(b, cfg, ctx).result.quality[0]
        self.assertEqual((q.status, q.expected, q.observed), (Status.INCOMPLETE_COVERAGE, 3, 2))
        b, cfg, ctx = fixture((100, None, 300, 500))
        self.assertIn(Reason.NULL_FIELD, self.calculate(b, cfg, ctx).result.quality[0].reasons)
        b, cfg, ctx = fixture((100, 200, 300, 400, 500), missing=(0,))
        self.assertEqual(self.calculate(b, cfg, ctx).result.quality[0].status, Status.AVAILABLE)
        self.assertEqual(self.calculate(None, cfg, ctx).result.quality[0].status, Status.MISSING_INPUT)

    def test_observed_prefix_is_explicit_and_completed_target_not_ready(self):
        b, cfg, ctx = fixture(cutoff=35)
        ref = self.calculate(b, cfg, ctx)
        prefix = target_fact(b, cfg, ctx, 50, prefix=True)
        ready = compute_relative_volume(prefix, ref, cfg, context=ctx)
        self.assertEqual(ready.values[0].values, (0.25,))
        self.assertEqual(ready.evidence[-1].event_ns, 35)
        eod = compute_relative_volume(target_fact(b, cfg, ctx), ref, cfg, context=ctx)
        self.assertIn(Reason.FUTURE_MARKET, eod.quality[0].reasons)
        partial = compute_relative_volume(replace(prefix, coverage=Coverage(1, 1, False)), ref, cfg, context=ctx)
        self.assertEqual(partial.quality[0].status, Status.INCOMPLETE_COVERAGE)
        self.assertCode(ErrorCode.INVALID_SCHEMA, lambda: replace(prefix, source=replace(prefix.source, kind=DataKind.DAILY)))

    def test_target_scope_and_original_row_bounds(self):
        b, cfg, ctx = fixture()
        ref = self.calculate(b, cfg, ctx)
        fact = target_fact(b, cfg, ctx)
        self.assertCode(ErrorCode.BOUNDS, lambda: replace(fact, row_index=1))
        self.assertCode(ErrorCode.BOUNDS, lambda: compute_relative_volume(replace(fact, interval=InputScope(32, 40, "all")), ref, cfg, context=ctx))
        self.assertCode(ErrorCode.BOUNDS, lambda: compute_relative_volume(replace(fact, interval=InputScope(31, 39, "all")), ref, cfg, context=ctx))
        self.assertCode(ErrorCode.BOUNDS, lambda: replace(fact, source=replace(fact.source, metadata=replace(fact.source.metadata, scope=InputScope(32, 40, "all")))))

    def test_same_original_frame_is_retained_once(self):
        b, cfg, ctx = fixture()
        ref = self.calculate(b, cfg, ctx)
        fact = replace(target_fact(b, cfg, ctx), source=InputBinding("target_volume", DataKind.DAILY, b.metadata), row_index=3)
        result = compute_relative_volume(fact, ref, cfg, context=ctx)
        bindings = [x for x in result.metadata.inputs if x.metadata.source.input_id == "volumes"]
        self.assertEqual(len(bindings), 1)
        self.assertEqual(bindings[0].metadata.coverage.observed, 4)
        self.assertEqual(result.evidence[-1].row_id, "3")
        bad = replace(fact, source=replace(fact.source, metadata=replace(b.metadata, source=replace(b.metadata.source, snapshot_id="r2"))))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_relative_volume(bad, ref, cfg, context=ctx))

    def test_source_revision_and_dependency_identity(self):
        b, cfg, ctx = fixture()
        ref = self.calculate(b, cfg, ctx)
        revised = self.calculate(replace(b, metadata=replace(b.metadata, source=replace(b.metadata.source, snapshot_id="r2"))), cfg, ctx)
        self.assertEqual(ref.result.values, revised.result.values)
        self.assertNotEqual(ref.identity_digest, revised.identity_digest)
        changed = replace(cfg, identity="another")
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_relative_volume(target_fact(b, cfg, ctx), ref, changed, context=ctx))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_relative_volume(target_fact(b, cfg, ctx), ref, cfg, context=replace(ctx, grid_version="r2")))

    def test_knowledge_cutoff_unknown_and_reconstruction(self):
        b, cfg, ctx = fixture()
        ref = self.calculate(b, cfg, ctx)
        unknown = replace(target_fact(b, cfg, ctx), known_at_ns=None)
        self.assertIn(Reason.UNKNOWN_AVAILABILITY, compute_relative_volume(unknown, ref, cfg, context=ctx).quality[0].reasons)
        late = replace(unknown, known_at_ns=46)
        self.assertIn(Reason.FUTURE_KNOWLEDGE, compute_relative_volume(late, ref, cfg, context=ctx).quality[0].reasons)
        reconstructed = replace(cfg, availability=AvailabilitySpec(40, 45, 50, "reconstruction", "synthetic replay"))
        rec_ref = self.calculate(b, reconstructed, ctx)
        rec = compute_relative_volume(late, rec_ref, reconstructed, context=ctx)
        self.assertEqual(rec.quality[0].status, Status.AVAILABLE)
        self.assertEqual(rec.evidence[-1].known_at_ns, 46)

    def test_missing_dependency_precedes_zero_denominator(self):
        b, cfg, ctx = fixture((0, 0, 0, 0))
        ref = self.calculate(b, cfg, ctx)
        result = compute_relative_volume(None, ref, cfg, context=ctx)
        self.assertEqual(result.quality[0].status, Status.MISSING_INPUT)
        self.assertNotIn(Reason.ZERO_DENOMINATOR, result.quality[0].reasons)
        missing = compute_relative_volume(target_fact(b, cfg, ctx), None, cfg, context=ctx)
        self.assertEqual(missing.quality[0].observed, 1)

    def test_configuration_quantity_unit_and_identity_guards(self):
        b, cfg, ctx = fixture()
        for params in ((Parameter("period", True),), (Parameter("period", 0),), (Parameter("unused", 3),)):
            self.assertCode(ErrorCode.INVALID_CONFIG, lambda: self.calculate(b, replace(cfg, parameters=params), ctx))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.calculate(b, replace(cfg, parameters=(Parameter("period", 3), Parameter("quantity_basis", "split_shares"))), ctx))
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: self.calculate(replace(b, metadata=replace(b.metadata, price_unit=PriceUnit(1, "USD"))), cfg, ctx))
        fact = target_fact(b, cfg, ctx)
        ref = self.calculate(b, cfg, ctx)
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_relative_volume(replace(fact, entity=EntityKey("B", "S3")), ref, cfg, context=ctx))

    def test_owned_reference_malformed_operands_and_false_modes(self):
        b, cfg, ctx = fixture()
        ref = self.calculate(b, cfg, ctx)
        with self.assertRaises(FrozenInstanceError):
            ref.numerator = 0
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(ref, numerator=601))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(ref, denominator=2))
        self.assertCode(ErrorCode.OVERFLOW, lambda: replace(ref, numerator=-1))
        missing = self.calculate(None, cfg, ctx)
        self.assertCode(ErrorCode.INVALID_SCHEMA, lambda: replace(missing, numerator=0))
        for name in ("baseline.daily_volume", "baseline.relative_volume"):
            caps = builtin_registry().get(name).capabilities
            self.assertTrue(caps.batch)
            self.assertFalse(caps.update or caps.restore or caps.merge)

    def test_baseline_unknown_late_and_reconstructed_knowledge(self):
        b, cfg, ctx = fixture()
        altered = replace(b, columns=tuple(Column(c.name, (10, None, 46, 40)) if c.name == "known_at_ns" else c for c in b.columns))
        ref = self.calculate(altered, cfg, ctx)
        self.assertEqual(ref.result.quality[0].status, Status.MISSING_INPUT)
        self.assertIn(Reason.UNKNOWN_AVAILABILITY, ref.result.quality[0].reasons)
        self.assertIn(Reason.FUTURE_KNOWLEDGE, ref.result.quality[0].reasons)
        rec_cfg = replace(cfg, availability=AvailabilitySpec(40, 45, 50, "reconstruction", "synthetic replay"))
        replay = self.calculate(altered, rec_cfg, ctx)
        self.assertEqual(replay.result.values[0].values, (200.0,))
        self.assertIsNone(replay.result.evidence[1].known_at_ns)

    def test_missing_action_admission_and_quantity_basis_conflict(self):
        b, cfg, ctx = fixture()
        adjustment = AdjustmentSpec("split", "split-factors-v1", "actions", "S3")
        cfg = replace(cfg, adjustment=adjustment)
        b = replace(b, metadata=replace(b.metadata, adjustment=adjustment))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.calculate(b, cfg, ctx))
        admission = admit_action_policy(None, ActionPolicy(adjustment, 40), cfg, entity=ctx.entity)
        ctx = replace(ctx, action_admission=admission)
        ref = self.calculate(b, cfg, ctx)
        self.assertIn(Reason.MISSING_ACTION_EVIDENCE, ref.result.quality[0].reasons)
        self.assertIsNone(ref.numerator)
        wrong_basis = replace(cfg, parameters=cfg.parameters+(Parameter("quantity_basis", "split_shares"),))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.calculate(b, wrong_basis, ctx))

    def test_supplied_adjusted_shares_admission_without_hidden_scaling(self):
        b, cfg, ctx = fixture()
        adjustment = AdjustmentSpec("split", "split-factors-v1", "actions", "S3")
        cfg = replace(cfg, adjustment=adjustment, parameters=cfg.parameters+(Parameter("quantity_basis", "split_shares"),))
        refs = CanonicalBatch(DataKind.REFERENCE, (
            Column("instrument_id", ("A",)), Column("session_id", ("S3",)), Column("reference_id", ("split",)),
            Column("fact_kind", ("split_factor",)), Column("effective_start_ns", (31,)),
            Column("factor_num", (1,)), Column("factor_den", (2,)), Column("known_at_ns", (40,))),
            BatchMetadata("synthetic", SourceBinding("fixture", "actions", "v1", "action-facts"), Coverage(1, 1, True), None))
        policy = ActionPolicy(adjustment, 40, representation="caller_transformed", quantity_basis="split_shares")
        admission = admit_action_policy(refs, policy, cfg, entity=ctx.entity)
        self.assertEqual(admission.status, Status.AVAILABLE)
        ctx = replace(ctx, action_admission=admission)
        b = replace(b, metadata=replace(b.metadata, adjustment=adjustment))
        ref = self.calculate(b, cfg, ctx)
        self.assertEqual(ref.numerator, 600)  # Supplied transformed shares, no factor applied again.
        fact = target_fact(b, cfg, ctx)
        fact = replace(fact, quantity_basis="split_shares", source=replace(fact.source, metadata=replace(fact.source.metadata, adjustment=adjustment)))
        result = compute_relative_volume(fact, ref, cfg, context=ctx)
        self.assertEqual(result.values[0].values, (2.5,))
        self.assertTrue(any(x.metadata.source.input_id == "action-facts" for x in result.metadata.inputs))

    def test_bounded_evidence_and_unavailable_witness_proof(self):
        b, cfg, ctx = fixture(evidence=1)
        ref = self.calculate(b, cfg, ctx)
        result = compute_relative_volume(target_fact(b, cfg, ctx), ref, cfg, context=ctx)
        self.assertEqual(len(result.evidence), 1)
        self.assertTrue(any(x.role == "target_certificate" for x in result.metadata.inputs))
        forged_ctx = replace(ctx, slot_coverage=(Coverage(1, 1, False),)+ctx.slot_coverage[1:])
        binding = next(x for x in ref.result.metadata.inputs if x.role == "history_context")
        forged_binding = replace(binding, metadata=replace(binding.metadata, source=replace(binding.metadata.source, input_id=forged_ctx.identity_digest)))
        forged_result = replace(ref.result, metadata=replace(ref.result.metadata, inputs=tuple(forged_binding if x.role == "history_context" else x for x in ref.result.metadata.inputs)))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(ref, context=forged_ctx, result=forged_result))


if __name__ == "__main__":
    unittest.main()
