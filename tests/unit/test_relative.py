"""Independent supplied-return spread, identity and membership fixtures."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import unittest
from equity_feature_contracts import (
    ActionPolicy, AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column,
    ConfigSpec, ContractError, Coverage, DataKind, EntityKey, ErrorCode, HistoryContext,
    Parameter, PriceUnit, Reason, RelativeSpec, ReturnReference, SectorBenchmark, SessionSpec,
    SourceBinding, Status, WindowSpec, builtin_registry,
)
from equity_features.history import compute_history
from equity_features.policies import admit_action_policy, admit_classification
from equity_features.relative import compute_relative


def reference(instrument="A", closes=(100, 110), *, period=1, target=None, known=None, unit=None):
    n = len(closes)
    target = n-1 if target is None else target
    sessions = tuple(SessionSpec("synthetic", f"S{i}", 10*i+1, 10*i+10, "supplied") for i in range(n))
    ctx = HistoryContext(EntityKey(instrument, f"S{target}"), "grid-v1", sessions, (Coverage(1, 1, True),)*n)
    cfg = ConfigSpec("return-"+instrument, "v1", (Parameter("period", period), Parameter("evidence_limit", 10)),
                     sessions[target], WindowSpec(period+1, f"S{target}", tuple(s.session_id for s in sessions), "completed_eod"),
                     AvailabilitySpec(sessions[target].close_ns, sessions[target].close_ns+5, sessions[target].close_ns+5),
                     price_unit=PriceUnit(0, "USD") if unit is None else unit)
    b = CanonicalBatch(DataKind.DAILY, (
        Column("instrument_id", (instrument,)*n), Column("session_id", tuple(s.session_id for s in sessions)),
        Column("start_ns", tuple(s.open_ns for s in sessions)), Column("end_ns", tuple(s.close_ns for s in sessions)),
        Column("close", closes), Column("known_at_ns", tuple(s.close_ns for s in sessions) if known is None else known)),
        BatchMetadata("synthetic", SourceBinding("fixture", "r1", "v1", "prices-"+instrument), Coverage(n, n, True), cfg.price_unit))
    result = compute_history(b, cfg, context=ctx, feature_ids=("history.return",))
    return ReturnReference(result, cfg, ctx), b


def setup():
    symbol, _ = reference()
    market, _ = reference("M", (200, 210))
    sector, _ = reference("T", (300, 321))
    cfg = replace(symbol.config, identity="relative", parameters=(Parameter("period", 1), Parameter("evidence_limit", 20)))
    spec = RelativeSpec(symbol.context.entity, market.context.entity, SectorBenchmark("synthetic-sector", sector.context.entity), 11)
    return symbol, market, sector, cfg, spec


def membership(cfg, spec, *, text="synthetic-sector", start=11, end=None, known=25, snapshot="r1"):
    b = CanonicalBatch(DataKind.REFERENCE, (
        Column("instrument_id", ("A",)), Column("session_id", ("S1",)), Column("reference_id", ("membership",)),
        Column("fact_kind", ("sector_membership",)), Column("effective_start_ns", (start,)),
        Column("effective_end_ns", (end,)), Column("text", (text,)), Column("known_at_ns", (known,))),
        BatchMetadata("synthetic", SourceBinding("fixture", snapshot, "v1", "membership"), Coverage(1, 1, True), None))
    return admit_classification(b, cfg, entity=spec.entity, effective_ns=spec.membership_effective_ns, fact_kind="sector_membership")


class RelativeReturns(unittest.TestCase):
    def assertCode(self, code, callback):
        with self.assertRaises(ContractError) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def compute(self, symbol, market, sector, cfg, spec, member=None, ids=("relative.market_return", "relative.sector_return")):
        return compute_relative(symbol, market, sector, member, cfg, spec=spec, feature_ids=ids)

    def test_hand_arithmetic_difference_and_explicit_sector_benchmark_mapping(self):
        s, m, t, cfg, spec = setup()
        result = self.compute(s, m, t, cfg, spec, membership(cfg, spec))
        self.assertAlmostEqual(result.values[0].values[0], float(Fraction(1, 20)), places=15)
        self.assertAlmostEqual(result.values[1].values[0], float(Fraction(3, 100)), places=15)
        self.assertNotAlmostEqual(result.values[0].values[0], float(Fraction(22, 21)-1), places=12)
        self.assertEqual(tuple(q.observed for q in result.quality), (2, 3))
        self.assertEqual(spec.sector_benchmark.sector_id, "synthetic-sector")
        self.assertEqual(spec.sector_benchmark.entity.instrument_id, "T")

    def test_missing_membership_only_blocks_sector(self):
        s, m, t, cfg, spec = setup()
        result = self.compute(s, m, t, cfg, spec)
        self.assertEqual(tuple(q.status for q in result.quality), (Status.AVAILABLE, Status.MISSING_INPUT))
        self.assertIsNone(result.values[1].values[0])
        result = self.compute(s, None, t, cfg, spec, membership(cfg, spec))
        self.assertEqual(tuple(q.status for q in result.quality), (Status.MISSING_INPUT, Status.AVAILABLE))

    def test_missing_symbol_and_benchmarks_do_not_trigger_calculation(self):
        s, m, t, cfg, spec = setup()
        result = self.compute(None, m, t, cfg, spec, membership(cfg, spec))
        self.assertTrue(all(q.status == Status.MISSING_INPUT for q in result.quality))
        self.assertEqual(tuple(q.observed for q in result.quality), (1, 2))
        result = self.compute(s, None, None, cfg, spec)
        self.assertTrue(all(c.values == (None,) for c in result.values))

    def test_half_open_membership_expired_future_unknown_and_reconstruction(self):
        s, m, t, cfg, spec = setup()
        for member in (membership(cfg, spec, start=1, end=11), membership(cfg, spec, start=12), membership(cfg, spec, known=None), membership(cfg, spec, known=26)):
            result = self.compute(s, m, t, cfg, spec, member)
            self.assertEqual(result.quality[0].status, Status.AVAILABLE)
            self.assertEqual(result.quality[1].status, Status.MISSING_INPUT)
        rec = replace(cfg, availability=AvailabilitySpec(20, 25, 25, "reconstruction", "synthetic audit"))
        def replay(ref):
            child = replace(ref.config, availability=rec.availability)
            _, b = reference(ref.context.entity.instrument_id, (100, 110) if ref is s else (200, 210) if ref is m else (300, 321))
            return ReturnReference(compute_history(b, child, context=ref.context, feature_ids=("history.return",)), child, ref.context)
        result = self.compute(replay(s), replay(m), replay(t), rec, spec, membership(rec, spec, known=None))
        self.assertEqual(result.quality[1].status, Status.AVAILABLE)
        self.assertIsNone(next(e.known_at_ns for e in result.evidence if e.input_id == "membership"))

    def test_explicit_membership_point_and_identity_guards(self):
        s, m, t, cfg, spec = setup()
        for point in (11, 15, 19):
            selected = replace(spec, membership_effective_ns=point)
            result = self.compute(s, m, t, cfg, selected, membership(cfg, selected))
            self.assertEqual(result.quality[1].status, Status.AVAILABLE)
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: self.compute(s, m, t, cfg, replace(spec, membership_effective_ns=20)))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.compute(s, m, t, cfg, spec, membership(cfg, spec, text="wrong-sector")))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.compute(s, m, t, cfg, spec, replace(membership(cfg, spec), effective_ns=12)))

    def test_unrequested_membership_and_sector_cannot_change_market_readiness(self):
        s, m, t, cfg, spec = setup()
        ids = ("relative.market_return",)
        a = self.compute(s, m, None, cfg, spec, ids=ids)
        unrelated = replace(spec, sector_benchmark=None, membership_effective_ns=None)
        b = self.compute(s, m, t, cfg, unrelated, membership(cfg, spec, known=999), ids=ids)
        self.assertEqual(a.values, b.values)
        self.assertEqual(a.quality, b.quality)
        self.assertFalse(any(x.metadata.source.input_id == "membership" for x in b.metadata.inputs))

    def test_horizon_cutoff_grid_price_and_backend_guards(self):
        s, m, t, cfg, spec = setup()
        h2, _ = reference("M", period=2)
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.compute(s, h2, t, cfg, spec))
        scaled, _ = reference("M", (200, 210), unit=PriceUnit(1, "USD"))
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: self.compute(s, scaled, t, cfg, spec))
        eur, _ = reference("M", (200, 210), unit=PriceUnit(0, "EUR"))
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: self.compute(s, eur, t, cfg, spec))
        stale = replace(m, result=replace(m.result, metadata=replace(m.result.metadata, backend_version="old")))
        self.assertCode(ErrorCode.INCOMPATIBLE_VERSION, lambda: self.compute(s, stale, t, cfg, spec))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.compute(s, m, t, replace(cfg, availability=AvailabilitySpec(20, 24, 25)), spec))
        ctx = replace(m.context, grid_version="grid-v2")
        result = replace(m.result, metadata=replace(m.result.metadata, inputs=tuple(replace(b, metadata=replace(b.metadata, source=replace(b.metadata.source, input_id=ctx.identity_digest))) if b.role == "history_context" else b for b in m.result.metadata.inputs)))
        revised = replace(m, context=ctx, result=result)
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.compute(s, revised, t, cfg, spec))

    def test_unready_close_coverage_and_warmup_propagate(self):
        s, m, t, cfg, spec = setup()
        null, _ = reference("M", (200, None))
        result = self.compute(s, null, t, cfg, spec, membership(cfg, spec))
        self.assertEqual(result.quality[0].status, Status.INCOMPLETE_COVERAGE)
        self.assertEqual(result.quality[1].status, Status.AVAILABLE)
        unknown, _ = reference("M", (200, 210), known=(10, None))
        result = self.compute(s, unknown, t, cfg, spec)
        self.assertIn(Reason.UNKNOWN_AVAILABILITY, result.quality[0].reasons)

    def test_bounded_original_evidence_and_retained_component_configs(self):
        s, m, t, cfg, spec = setup()
        result = self.compute(s, m, t, cfg, spec, membership(cfg, spec))
        self.assertTrue(all(e.entity == spec.entity for e in result.evidence))
        self.assertEqual({e.input_id for e in result.evidence}, {"prices-A", "prices-M", "prices-T", "membership"})
        self.assertTrue(all(e.row_id in ("0", "1") for e in result.evidence))
        self.assertTrue(any(x.metadata.source.input_id == s.identity_digest for x in result.metadata.inputs))
        self.assertNotEqual(cfg.digest, s.config.digest)
        limited = replace(cfg, parameters=(Parameter("period", 1), Parameter("evidence_limit", 1)))
        bounded = self.compute(s, m, t, limited, spec, membership(limited, spec))
        self.assertEqual(len(bounded.evidence), 1)

    def test_source_and_membership_revision_bind_without_changing_values(self):
        s, m, t, cfg, spec = setup()
        a = self.compute(s, m, t, cfg, spec, membership(cfg, spec))
        b = self.compute(s, m, t, cfg, spec, membership(cfg, spec, snapshot="r2"))
        self.assertEqual(a.values, b.values)
        self.assertNotEqual(a.metadata.identity_digest, b.metadata.identity_digest)
        inputs = tuple(replace(x, metadata=replace(x.metadata, source=replace(x.metadata.source, snapshot_id="r2"))) if x.kind == DataKind.DAILY else x for x in m.result.metadata.inputs)
        revised = replace(m, result=replace(m.result, metadata=replace(m.result.metadata, inputs=inputs)))
        c = self.compute(s, revised, t, cfg, spec, membership(cfg, spec))
        self.assertEqual(a.values, c.values)
        self.assertNotEqual(a.metadata.identity_digest, c.metadata.identity_digest)

    def test_owned_references_malformed_proofs_and_explicit_benchmark_entity(self):
        s, m, t, cfg, spec = setup()
        with self.assertRaises(FrozenInstanceError):
            s.config = cfg
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(s, config=cfg))
        for value in (-2.0, 1e20):
            bad_result = replace(s.result, values=(replace(s.result.values[0], values=(value,)),))
            self.assertCode(ErrorCode.BOUNDS, lambda: replace(s, result=bad_result))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.compute(s, m, t, cfg, replace(spec, market_benchmark=EntityKey("wrong", "S1"))))
        bad_metadata = replace(s.result.metadata, inputs=tuple(replace(x, metadata=replace(x.metadata, coverage=Coverage(1, 1, True))) if x.kind == DataKind.DAILY else x for x in s.result.metadata.inputs))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(s, result=replace(s.result, metadata=bad_metadata, evidence=())))
        collision = replace(m.result.metadata, inputs=tuple(replace(x, metadata=replace(x.metadata, source=replace(x.metadata.source, input_id="prices-A"))) if x.kind == DataKind.DAILY else x for x in m.result.metadata.inputs))
        bad = replace(m, result=replace(m.result, metadata=collision, evidence=()))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.compute(s, bad, t, cfg, spec))

    def test_truthful_modes_and_invalid_requests(self):
        s, m, t, cfg, spec = setup()
        for name in ("relative.market_return", "relative.sector_return"):
            caps = builtin_registry().get(name).capabilities
            self.assertTrue(caps.batch)
            self.assertFalse(caps.update or caps.restore or caps.merge)
        self.assertCode(ErrorCode.DUPLICATE, lambda: self.compute(s, m, t, cfg, spec, ids=("relative.market_return",)*2))
        self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: self.compute(s, m, t, cfg, spec, ids=("history.return",)))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.compute(None, None, None, replace(cfg, adjustment=AdjustmentSpec("raw", "raw-v2")), spec))

    def test_all_frozen_horizons_and_compatible_distinct_child_config_identity(self):
        for horizon in (1, 5, 20, 60, 252):
            s, _ = reference("A", tuple(1000+i for i in range(horizon+1)), period=horizon)
            m, b = reference("M", tuple(2000+i for i in range(horizon+1)), period=horizon)
            parent = replace(s.config, identity="comparison", parameters=(Parameter("period", horizon),))
            spec = RelativeSpec(s.context.entity, m.context.entity)
            child = replace(m.config, identity="different-child", parameters=(Parameter("period", horizon),))
            m = ReturnReference(compute_history(b, child, context=m.context, feature_ids=("history.return",)), child, m.context)
            result = self.compute(s, m, None, parent, spec, ids=("relative.market_return",))
            self.assertAlmostEqual(result.values[0].values[0], float(Fraction(horizon, 2000)), places=15)

    def test_future_closes_do_not_change_selected_relative_return(self):
        s, _ = reference("A", (100, 110, 999, 9999), target=1)
        m, _ = reference("M", (200, 210, 1000, 9999), target=1)
        cfg = replace(s.config, identity="relative")
        spec = RelativeSpec(s.context.entity, m.context.entity)
        a = self.compute(s, m, None, cfg, spec, ids=("relative.market_return",))
        s2, _ = reference("A", (100, 110, None, 1), target=1)
        m2, _ = reference("M", (200, 210, 2, None), target=1)
        b = self.compute(s2, m2, None, cfg, spec, ids=("relative.market_return",))
        self.assertEqual(a, b)

    def test_valid_instrument_specific_action_snapshots_and_policy_mismatch(self):
        s, m, _, _, _ = setup()
        def adjusted(ref, closes):
            name = ref.context.entity.instrument_id
            adjustment = AdjustmentSpec("split", "split-factors-v1", "actions-"+name, "S1")
            cfg = replace(ref.config, adjustment=adjustment)
            refs = CanonicalBatch(DataKind.REFERENCE, (
                Column("instrument_id", (name,)), Column("session_id", ("S1",)), Column("reference_id", ("split",)),
                Column("fact_kind", ("split_factor",)), Column("effective_start_ns", (11,)),
                Column("factor_num", (1,)), Column("factor_den", (2,)), Column("known_at_ns", (20,))),
                BatchMetadata("synthetic", SourceBinding("fixture", "actions-"+name, "v1", "action-facts-"+name), Coverage(1, 1, True), None))
            policy = ActionPolicy(adjustment, 20, representation="caller_transformed")
            ctx = replace(ref.context, action_admission=admit_action_policy(refs, policy, cfg, entity=ref.context.entity))
            _, b = reference(name, closes)
            b = replace(b, metadata=replace(b.metadata, adjustment=adjustment))
            return ReturnReference(compute_history(b, cfg, context=ctx, feature_ids=("history.return",)), cfg, ctx)
        s, m = adjusted(s, (100, 110)), adjusted(m, (200, 210))
        cfg = replace(s.config, identity="relative")
        spec = RelativeSpec(s.context.entity, m.context.entity)
        result = self.compute(s, m, None, cfg, spec, ids=("relative.market_return",))
        self.assertAlmostEqual(result.values[0].values[0], .05, places=15)
        self.assertEqual({b.metadata.source.snapshot_id for b in result.metadata.inputs if b.metadata.source.input_id.startswith("action-facts")}, {"actions-A", "actions-M"})
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.compute(s, m, None, replace(cfg, adjustment=AdjustmentSpec()), spec, ids=("relative.market_return",)))

    def test_compatible_warmup_propagates_without_rebuilding_dependency(self):
        s, _ = reference("A", period=5)
        m, _ = reference("M", (200, 210), period=5)
        cfg = replace(s.config, identity="relative")
        spec = RelativeSpec(s.context.entity, m.context.entity)
        result = self.compute(s, m, None, cfg, spec, ids=("relative.market_return",))
        self.assertEqual(result.quality[0].status, Status.INSUFFICIENT_HISTORY)
        self.assertEqual(result.quality[0].observed, 0)
        self.assertIsNone(result.values[0].values[0])

    def test_conflicting_supplied_evidence_rejected_even_with_zero_output_limit(self):
        s, _, _, cfg, _ = setup()
        cfg = replace(cfg, parameters=(Parameter("period", 1), Parameter("evidence_limit", 0)))
        spec = RelativeSpec(s.context.entity, s.context.entity)
        good = self.compute(s, s, None, cfg, spec, ids=("relative.market_return",))
        self.assertEqual(good.values[0].values, (0.0,))
        self.assertEqual(good.evidence, ())
        changed = tuple(replace(e, known_at_ns=21) if e.row_id == "1" else e for e in s.result.evidence)
        contradictory = replace(s, result=replace(s.result, evidence=changed))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.compute(s, contradictory, None, cfg, spec, ids=("relative.market_return",)))


if __name__ == "__main__":
    unittest.main()
