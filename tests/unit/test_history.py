"""Independent governed-slot, exact arithmetic and causality fixtures."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import unittest

from equity_feature_contracts import (
    ActionPolicy, AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch,
    Column, ConfigSpec, ContractError, Coverage, DataKind, EntityKey, ErrorCode,
    HistoryContext, InputScope, Parameter, PriceUnit, Reason, SessionSpec, SourceBinding, Status,
    WindowSpec, builtin_registry,
)
from equity_features.history import compute_history
from equity_features.policies import admit_action_policy


def fixture(closes=(100, 110, 105, 120, 115, 130), target=None, missing=(), **fields):
    n = len(closes)
    target = n-1 if target is None else target
    sessions = tuple(SessionSpec("synthetic", f"S{i}", i*10+1, i*10+10, "supplied") for i in range(n))
    values = dict(instrument_id=("A",)*n, session_id=tuple(s.session_id for s in sessions),
                  start_ns=tuple(s.open_ns for s in sessions), end_ns=tuple(s.close_ns for s in sessions),
                  close=closes, known_at_ns=tuple(s.close_ns for s in sessions))
    values.update(fields)
    present = tuple(i for i in range(n) if i not in missing)
    batch = CanonicalBatch(DataKind.DAILY, tuple(Column(name, tuple(val[i] for i in present)) for name, val in values.items()),
                           BatchMetadata("synthetic", SourceBinding("fixture", "r1", "v1", "prices"),
                                         Coverage(n, len(present), len(present) == n), PriceUnit(0, "USD")))
    context = HistoryContext(EntityKey("A", f"S{target}"), "grid-v1", sessions,
                             tuple(Coverage(1, int(i in present), i in present) for i in range(n)))
    return batch, context


def config(ctx, period=3, *, prior=False, cutoff=None, evidence=0, **kwargs):
    session = next(s for s in ctx.sessions if s.session_id == ctx.entity.session_id)
    cutoff = session.close_ns if cutoff is None else cutoff
    values = dict(identity="history", algorithm_version="v1",
                  parameters=(Parameter("period", period), Parameter("evidence_limit", evidence)),
                  session=session, window=WindowSpec(period if prior else period+1, session.session_id,
                                                    tuple(s.session_id for s in ctx.sessions), "prior_only" if prior else "completed_eod"),
                  availability=AvailabilitySpec(cutoff, session.close_ns+5, session.close_ns+5),
                  price_unit=PriceUnit(0, "USD"))
    values.update(kwargs)
    return ConfigSpec(**values)


def result_value(result, feature="history.return"):
    return next(c.values[0] for c in result.values if c.feature_id == feature)


class GovernedHistory(unittest.TestCase):
    def assertCode(self, code, call):
        with self.assertRaises(ContractError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)

    def compute(self, batch, ctx, period=3, *, prior=False, **kwargs):
        ids = ("history.prior_high", "history.prior_low") if prior else ("history.return",)
        return compute_history(batch, config(ctx, period, prior=prior, **kwargs), context=ctx, feature_ids=ids)

    def test_hand_computed_return_and_prior_extrema(self):
        b, ctx = fixture(high=(102, 112, 111, 122, 121, 132), low=(98, 99, 103, 104, 113, 114))
        self.assertEqual(result_value(self.compute(b, ctx)), float(Fraction(5, 21)))
        extrema = self.compute(b, ctx, prior=True)
        self.assertEqual(result_value(extrema, "history.prior_high"), 122.0)
        self.assertEqual(result_value(extrema, "history.prior_low"), 103.0)
        self.assertTrue(all(q.status == Status.AVAILABLE and q.expected == q.observed == 3 for q in extrema.quality))

    def test_all_frozen_default_horizons_and_prior_windows(self):
        closes = tuple(1000+i for i in range(253))
        b, ctx = fixture(closes, high=tuple(x+5 for x in closes), low=tuple(x-5 for x in closes))
        for horizon in (1, 5, 20, 60, 252):
            result = self.compute(b, ctx, horizon)
            self.assertEqual(result_value(result), float(Fraction(1252, 1252-horizon)-1))
            self.assertEqual(result.quality[0].observed, horizon+1)
        for period in (20, 60, 252):
            result = self.compute(b, ctx, period, prior=True)
            self.assertEqual(result_value(result, "history.prior_high"), 1256.0)
            self.assertEqual(result_value(result, "history.prior_low"), float(1252-period-5))

    def test_missing_middle_close_not_hidden_by_valid_endpoints(self):
        b, ctx = fixture(missing=(3,))
        result = self.compute(b, ctx)
        self.assertIsNone(result_value(result))
        self.assertEqual(result.quality[0].status, Status.INCOMPLETE_COVERAGE)
        self.assertEqual((result.quality[0].expected, result.quality[0].observed), (4, 3))
        self.assertIn(Reason.GOVERNED_GAP, result.quality[0].reasons)
        # A later exact finite window recovers without compressing the earlier gap.
        self.assertEqual(result_value(self.compute(b, ctx, 1)), float(Fraction(3, 23)))

    def test_null_middle_close_and_field_independence(self):
        b, ctx = fixture(closes=(100, 110, 105, None, 115, 130),
                         high=(102, 112, 111, 122, 121, 132), low=(98, 99, 103, 104, 113, 114))
        result = self.compute(b, ctx)
        self.assertIsNone(result_value(result))
        self.assertIn(Reason.NULL_FIELD, result.quality[0].reasons)
        extrema = self.compute(b, ctx, prior=True)
        self.assertEqual(result_value(extrema, "history.prior_high"), 122.0)
        b = replace(b, columns=tuple(c for c in b.columns if c.name != "high"))
        extrema = self.compute(b, ctx, prior=True)
        self.assertIsNone(result_value(extrema, "history.prior_high"))
        self.assertEqual(result_value(extrema, "history.prior_low"), 103.0)

    def test_prior_extrema_available_before_target_close_and_ignore_target(self):
        b, ctx = fixture(high=(102, 112, 111, 122, 121, 999), low=(98, 99, 103, 104, 113, 1))
        result = self.compute(b, ctx, prior=True, cutoff=ctx.sessions[-1].open_ns)
        self.assertEqual(result_value(result, "history.prior_high"), 122.0)
        self.assertEqual(result_value(result, "history.prior_low"), 103.0)
        forming = self.compute(b, ctx, cutoff=ctx.sessions[-1].open_ns, evidence=10)
        self.assertEqual(forming.quality[0].status, Status.INCOMPLETE_COVERAGE)
        self.assertIn(Reason.FUTURE_MARKET, forming.quality[0].reasons)
        self.assertEqual(forming.evidence[-1].use, "excluded")

    def test_future_rows_and_future_knowledge_do_not_change_selected_return(self):
        b, ctx = fixture((100, 110, 105, 120, 115, 130, 999), target=5,
                         known_at_ns=(10, 20, 30, 40, 50, 60, None))
        result = self.compute(b, ctx)
        self.assertEqual(result_value(result), float(Fraction(5, 21)))
        changed = replace(b, columns=tuple(Column(c.name, c.values[:-1]+(12345,)) if c.name == "close" else c for c in b.columns))
        self.assertEqual(result_value(self.compute(changed, ctx)), result_value(result))
        self.assertEqual(self.compute(changed, ctx).quality, result.quality)

    def test_minimum_period_one_and_missing_history(self):
        b, ctx = fixture((100, 110))
        self.assertEqual(result_value(self.compute(b, ctx, 1)), 0.1)
        result = self.compute(b, ctx, 5)
        self.assertEqual(result.quality[0].status, Status.INSUFFICIENT_HISTORY)
        self.assertIsNone(result_value(result))
        absent = self.compute(None, ctx, 1)
        self.assertEqual(absent.quality[0].status, Status.MISSING_INPUT)
        b, ctx = fixture((100, 110), missing=(0, 1))
        self.assertEqual(self.compute(b, ctx, 1).quality[0].status, Status.INCOMPLETE_COVERAGE)

    def test_known_at_equality_unknown_future_and_reconstruction(self):
        for knowledge, reason in ((None, Reason.UNKNOWN_AVAILABILITY), (66, Reason.FUTURE_KNOWLEDGE)):
            b, ctx = fixture(known_at_ns=(10, 20, 30, knowledge, 50, 65))
            result = self.compute(b, ctx, evidence=10)
            self.assertEqual(result.quality[0].status, Status.MISSING_INPUT)
            self.assertIn(reason, result.quality[0].reasons)
            self.assertEqual(result.evidence[1].exclusion_reason, reason)
            recon = self.compute(b, ctx, availability=AvailabilitySpec(60, 100, 60, "reconstruction", "audit"), evidence=10)
            self.assertEqual(result_value(recon), float(Fraction(5, 21)))
            self.assertEqual(recon.evidence[1].known_at_ns, knowledge)
        b, ctx = fixture(known_at_ns=(10, 20, 30, 65, 50, 65))
        self.assertEqual(self.compute(b, ctx).quality[0].status, Status.AVAILABLE)

    def test_bounded_original_row_evidence_and_context_identity(self):
        b, ctx = fixture()
        result = self.compute(b, ctx, evidence=2)
        self.assertEqual(len(result.evidence), 2)
        self.assertEqual([(e.row_id, e.event_ns, e.known_at_ns) for e in result.evidence], [("2", 30, 30), ("3", 40, 40)])
        self.assertTrue(all(e.boundary == "completed_interval" for e in result.evidence))
        changed = self.compute(b, replace(ctx, grid_version="grid-v2"))
        self.assertEqual(result_value(changed), result_value(result))
        self.assertNotEqual(result.metadata.identity_digest, changed.metadata.identity_digest)
        b2 = replace(b, metadata=replace(b.metadata, source=replace(b.metadata.source, snapshot_id="r2")))
        self.assertNotEqual(self.compute(b2, ctx).metadata.identity_digest, self.compute(b, ctx).metadata.identity_digest)

    def test_wide_endpoint_precision_and_scaled_prices(self):
        maximum = 2**63-1
        b, ctx = fixture((maximum-1, maximum))
        self.assertEqual(result_value(self.compute(b, ctx, 1)), float(Fraction(1, maximum-1)))
        self.assertGreater(result_value(self.compute(b, ctx, 1)), 0)
        b, ctx = fixture((10000, 11000), high=(10002, 11002), low=(9998, 10998))
        b = replace(b, metadata=replace(b.metadata, price_unit=PriceUnit(2, "USD")))
        result = self.compute(b, ctx, 1, prior=True, price_unit=PriceUnit(2, "USD"))
        self.assertEqual(result_value(result, "history.prior_high"), 100.02)

    def test_duplicate_grid_row_bounds_order_and_certificates(self):
        b, ctx = fixture()
        self.assertCode(ErrorCode.DUPLICATE, lambda: replace(ctx, sessions=ctx.sessions+(ctx.sessions[-1],),
                                                           slot_coverage=ctx.slot_coverage+(Coverage(1, 1, True),)))
        self.assertCode(ErrorCode.INVALID_ORDER, lambda: replace(ctx, sessions=tuple(reversed(ctx.sessions))))
        wrong = replace(b, columns=tuple(Column(c.name, (0,)+c.values[1:]) if c.name == "start_ns" else c for c in b.columns))
        self.assertCode(ErrorCode.BOUNDS, lambda: self.compute(wrong, ctx))
        wrong = replace(b, metadata=replace(b.metadata, coverage=Coverage(1, 1, True)))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.compute(wrong, ctx))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.compute(b, replace(ctx, slot_coverage=(Coverage(1, 0, False),)+ctx.slot_coverage[1:])))
        wrong = replace(b, columns=tuple(Column(c.name, c.values+(c.values[-1],)) for c in b.columns),
                        metadata=replace(b.metadata, coverage=Coverage(7, 7, True)))
        self.assertCode(ErrorCode.DUPLICATE, lambda: self.compute(wrong, ctx))

    def test_invalid_unit_basis_period_window_and_requested_modes(self):
        b, ctx = fixture()
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: self.compute(b, ctx, price_unit=PriceUnit(1, "USD")))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.compute(b, ctx, adjustment=AdjustmentSpec("raw", "unknown")))
        for period in (True, 0, 1.5):
            self.assertCode(ErrorCode.INVALID_CONFIG, lambda: self.compute(b, ctx, period))
        cfg = config(ctx)
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: compute_history(b, replace(cfg, window=replace(cfg.window, count=3)),
                                                                         context=ctx, feature_ids=("history.return",)))
        self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: compute_history(b, cfg, context=ctx, feature_ids=("history.sma",)))
        for name in ("history.return", "history.prior_high", "history.prior_low"):
            self.assertTrue(builtin_registry().get(name).capabilities.batch)
            for mode in ("update", "restore", "merge"):
                self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: builtin_registry().require_capability(name, mode))

    def test_adjusted_policy_missing_ready_and_stale_identity(self):
        b, ctx = fixture()
        adjustment = AdjustmentSpec("split", "split-factors-v1", "actions", "S5")
        cfg = config(ctx, adjustment=adjustment)
        b = replace(b, metadata=replace(b.metadata, adjustment=adjustment))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: compute_history(b, cfg, context=ctx, feature_ids=("history.return",)))
        p = ActionPolicy(adjustment, 60)
        admission = admit_action_policy(None, p, cfg, entity=ctx.entity)
        ctx_missing = replace(ctx, action_admission=admission)
        result = compute_history(b, cfg, context=ctx_missing, feature_ids=("history.return",))
        self.assertEqual(result.quality[0].status, Status.MISSING_INPUT)
        self.assertIn(Reason.MISSING_ACTION_EVIDENCE, result.quality[0].reasons)
        ref = CanonicalBatch(DataKind.REFERENCE, tuple(Column(name, ()) for name in
                            ("instrument_id", "session_id", "reference_id", "fact_kind", "effective_start_ns")),
                            BatchMetadata("synthetic", SourceBinding("fixture", "actions", "v1", "refs"), Coverage(0, 0, True), None))
        ready = replace(ctx, action_admission=admit_action_policy(ref, p, cfg, entity=ctx.entity))
        self.assertEqual(result_value(compute_history(b, cfg, context=ready, feature_ids=("history.return",))), float(Fraction(5, 21)))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_history(b, replace(cfg, identity="changed"), context=ready, feature_ids=("history.return",)))

    def test_context_ownership_and_invalid_certificates(self):
        _, ctx = fixture()
        source = list(ctx.sessions)
        owned = replace(ctx, sessions=source)
        source.clear()
        self.assertEqual(len(owned.sessions), 6)
        with self.assertRaises(FrozenInstanceError):
            owned.grid_version = "changed"
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: replace(ctx, slot_coverage=(Coverage(0, 0, True),)*6))
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: replace(ctx, initialization_anchor="not-in-grid"))

    def test_actual_api_rejects_malformed_identity_scope_order_and_price(self):
        b, ctx = fixture()
        bad = replace(b, metadata=replace(b.metadata, namespace="different"))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.compute(bad, ctx))
        bad = replace(b, metadata=replace(b.metadata, scope=InputScope(11, 60, "supplied")))
        self.assertCode(ErrorCode.BOUNDS, lambda: self.compute(bad, ctx))
        bad = replace(b, columns=tuple(Column(c.name, tuple(reversed(c.values))) for c in b.columns))
        self.assertCode(ErrorCode.INVALID_ORDER, lambda: self.compute(bad, ctx))
        bad = replace(b, columns=tuple(Column(c.name, c.values[:-1]+(0,)) if c.name == "close" else c for c in b.columns))
        self.assertCode(ErrorCode.INVALID_SCHEMA, lambda: self.compute(bad, ctx))

    def test_incomplete_slot_proof_blocks_only_its_selected_window(self):
        b, ctx = fixture()
        certificates = list(ctx.slot_coverage)
        certificates[3] = Coverage(1, 1, False)
        ctx = replace(ctx, slot_coverage=certificates)
        result = self.compute(b, ctx)
        self.assertEqual(result.quality[0].status, Status.INCOMPLETE_COVERAGE)
        self.assertEqual(result.quality[0].observed, 3)
        self.assertEqual(self.compute(b, ctx, 1).quality[0].status, Status.AVAILABLE)


if __name__ == "__main__":
    unittest.main()
