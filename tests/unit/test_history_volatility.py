"""Independent hand variance/Decimal centered-reference production API cases."""
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction
import math
import unittest
from equity_feature_contracts import (
    ActionPolicy, AdjustmentSpec, AvailabilitySpec, Column, ContractError, ErrorCode,
    Parameter, PriceUnit, Reason, Status, builtin_registry,
)
from equity_features.history import compute_history
from equity_features.policies import admit_action_policy
from test_history import fixture, config, result_value


def decimal_volatility(closes, factor=1):
    with localcontext() as ctx:
        ctx.prec = 110
        changes = [Decimal(b-a)/Decimal(a) for a, b in zip(closes, closes[1:])]
        center = sum(changes)/len(changes)
        return float((factor*sum((r-center)**2 for r in changes)/(len(changes)-1)).sqrt())


class HistoryVolatility(unittest.TestCase):
    def compute(self, batch, ctx, n=3, factor=None, **kwargs):
        cfg = config(ctx, n, **kwargs)
        if factor is not None:
            cfg = replace(cfg, parameters=cfg.parameters+(Parameter("annualization_factor", factor),))
        return compute_history(batch, cfg, context=ctx, feature_ids=("history.return_volatility",))

    def value(self, result):
        return result_value(result, "history.return_volatility")

    def assertCode(self, code, callback):
        with self.assertRaises(ContractError) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def test_hand_exact_sample_variance_and_explicit_scaling(self):
        b, ctx = fixture()
        result = self.compute(b, ctx)
        with localcontext() as decimal_ctx:
            decimal_ctx.prec = 80
            expected = float((Decimal(476449)/Decimal(44791488)).sqrt())
        self.assertEqual(self.value(result), expected)
        self.assertEqual((result.quality[0].expected, result.quality[0].observed), (4, 4))
        self.assertEqual(result.values[0].unit, "fraction")
        scaled = self.compute(b, ctx, factor=4)
        self.assertEqual(self.value(scaled), 2*expected)
        self.assertNotEqual(scaled.metadata.config_digest, result.metadata.config_digest)

    def test_centered_sample_not_rms_or_population(self):
        b, ctx = fixture((100, 110, 99))
        self.assertTrue(math.isclose(self.value(self.compute(b, ctx, 2)), math.sqrt(2)/10, rel_tol=1e-12, abs_tol=1e-12))
        self.assertNotEqual(self.value(self.compute(b, ctx, 2)), 0.1)
        b, ctx = fixture((1000, 1100, 1210, 1331))
        self.assertEqual(self.value(self.compute(b, ctx)), 0.0)
        self.assertEqual(self.compute(b, ctx).quality[0].status, Status.AVAILABLE)

    def test_default20_has_no_inferred_annualization(self):
        closes = tuple(1000+(i*37)%271 for i in range(40))
        b, ctx = fixture(closes)
        result = self.compute(b, ctx, 20)
        expected = decimal_volatility(closes[-21:])
        self.assertTrue(math.isclose(self.value(result), expected, rel_tol=1e-12, abs_tol=1e-12))
        explicit = self.compute(b, ctx, 20, factor=1)
        self.assertEqual(explicit.values, result.values)
        self.assertNotEqual(explicit.metadata.config_digest, result.metadata.config_digest)
        self.assertTrue(math.isclose(self.value(self.compute(b, ctx, 20, factor=252)), expected*math.sqrt(252), rel_tol=1e-12, abs_tol=1e-12))

    def test_flat_zero_and_missing_never_zero(self):
        b, ctx = fixture((100,)*5)
        self.assertEqual(self.value(self.compute(b, ctx)), 0.0)
        b, ctx = fixture((100, None, 100, 100))
        self.assertIsNone(self.value(self.compute(b, ctx)))
        self.assertEqual(self.compute(b, ctx).quality[0].status, Status.INCOMPLETE_COVERAGE)
        self.assertIn(Reason.NULL_FIELD, self.compute(b, ctx).quality[0].reasons)
        self.assertIsNone(self.value(self.compute(None, ctx)))

    def test_int64_near_equal_tiny_variance_remains_strictly_positive(self):
        limit = 2**63-1
        closes = (limit-2, limit-1, limit)
        b, ctx = fixture(closes)
        result = self.compute(b, ctx, 2)
        value = self.value(result)
        self.assertGreater(value, 0.0)
        self.assertLess(value, 1e-37)
        self.assertTrue(math.isclose(value, decimal_volatility(closes), rel_tol=1e-12, abs_tol=0.0))
        self.assertEqual(tuple(float(p) for p in closes), (float(limit),)*3)

    def test_units_scale_cancels_only_when_declared_compatible(self):
        b, ctx = fixture()
        before = self.compute(b, ctx)
        unit = PriceUnit(18, "USD")
        scaled = replace(b, metadata=replace(b.metadata, price_unit=unit))
        after = self.compute(scaled, ctx, price_unit=unit)
        self.assertEqual(after.values, before.values)
        self.assertNotEqual(after.metadata.identity_digest, before.metadata.identity_digest)
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: self.compute(scaled, ctx))

    def test_large_ratios_and_largest_declared_factor_remain_finite(self):
        closes = (1, 2**63-1, 1)
        b, ctx = fixture(closes)
        result = self.compute(b, ctx, 2, factor=2**63-1)
        self.assertTrue(math.isfinite(self.value(result)))
        self.assertTrue(math.isclose(self.value(result), decimal_volatility(closes, 2**63-1), rel_tol=1e-12, abs_tol=1e-12))

    def test_missing_middle_close_and_finite_recovery(self):
        b, ctx = fixture((100, 110, 105, 120, 115, 130, 140), missing=(3,))
        result = self.compute(b, ctx)
        self.assertIsNone(self.value(result))
        self.assertEqual((result.quality[0].expected, result.quality[0].observed), (4, 3))
        self.assertIn(Reason.GOVERNED_GAP, result.quality[0].reasons)
        recovery = self.compute(b, ctx, 2)
        self.assertTrue(math.isclose(self.value(recovery), decimal_volatility((115, 130, 140)), rel_tol=1e-12, abs_tol=1e-12))

    def test_future_mutation_and_bounded_original_evidence(self):
        b, ctx = fixture((100, 110, 105, 120, 115, 130, 999), target=5)
        before = self.compute(b, ctx, evidence=2)
        changed = replace(b, columns=tuple(Column(c.name, c.values[:-1]+(1,)) if c.name == "close" else c for c in b.columns))
        after = self.compute(changed, ctx, evidence=2)
        self.assertEqual(after.values, before.values)
        self.assertEqual(after.quality, before.quality)
        self.assertEqual(after.evidence, before.evidence)
        self.assertEqual([(e.row_id, e.event_ns) for e in before.evidence], [("2", 30), ("3", 40)])

    def test_completion_knowledge_and_explicit_reconstruction(self):
        b, ctx = fixture(known_at_ns=(10, 20, 30, None, 50, 65))
        causal = self.compute(b, ctx)
        self.assertEqual(causal.quality[0].status, Status.MISSING_INPUT)
        replay = self.compute(b, ctx, availability=AvailabilitySpec(60, 100, 60, "reconstruction", "audit"), evidence=10)
        self.assertTrue(math.isclose(self.value(replay), decimal_volatility((105, 120, 115, 130)), rel_tol=1e-12, abs_tol=1e-12))
        self.assertIsNone(replay.evidence[1].known_at_ns)
        forming = self.compute(b, ctx, cutoff=51, availability=AvailabilitySpec(51, 100, 60, "reconstruction", "audit"))
        self.assertIsNone(self.value(forming))
        self.assertIn(Reason.FUTURE_MARKET, forming.quality[0].reasons)

    def test_minimum_history_absent_fields_and_invalid_conventions(self):
        b, ctx = fixture((100, 110))
        self.assertEqual(self.compute(b, ctx, 2).quality[0].status, Status.INSUFFICIENT_HISTORY)
        absent = replace(b, columns=tuple(c for c in b.columns if c.name != "close"))
        self.assertEqual(self.compute(absent, ctx, 2).quality[0].status, Status.MISSING_INPUT)
        for period in (0, 1, True, 1.5):
            self.assertCode(ErrorCode.INVALID_CONFIG, lambda: self.compute(b, ctx, period))
        for factor in (0, -1, True, 1.5, 2**63):
            self.assertCode(ErrorCode.INVALID_CONFIG, lambda: self.compute(b, ctx, 2, factor=factor))
        cfg = config(ctx, 2)
        wrong = replace(cfg, window=replace(cfg.window, count=2))
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: compute_history(b, wrong, context=ctx, feature_ids=("history.return_volatility",)))
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: compute_history(b, cfg, context=ctx, feature_ids=("history.return_volatility", "history.return")))
        extra = replace(cfg, parameters=cfg.parameters+(Parameter("annualization_factor", 1),))
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: compute_history(b, extra, context=ctx, feature_ids=("history.return",)))

    def test_missing_adjustment_and_source_revision_identity(self):
        b, ctx = fixture()
        adjusted = AdjustmentSpec("split", "split-factors-v1", "actions", "S5")
        cfg = config(ctx, adjustment=adjusted)
        transformed = replace(b, metadata=replace(b.metadata, adjustment=adjusted))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: compute_history(transformed, cfg, context=ctx, feature_ids=("history.return_volatility",)))
        admission = admit_action_policy(None, ActionPolicy(adjusted, 60), cfg, entity=ctx.entity)
        result = compute_history(transformed, cfg, context=replace(ctx, action_admission=admission), feature_ids=("history.return_volatility",))
        self.assertIsNone(self.value(result))
        self.assertIn(Reason.MISSING_ACTION_EVIDENCE, result.quality[0].reasons)
        original = self.compute(b, ctx)
        revised = replace(b, metadata=replace(b.metadata, source=replace(b.metadata.source, snapshot_id="r2")))
        self.assertEqual(self.compute(revised, ctx).values, original.values)
        self.assertNotEqual(self.compute(revised, ctx).metadata.identity_digest, original.metadata.identity_digest)

    def test_only_batch_mode_is_qualified(self):
        registry = builtin_registry()
        self.assertTrue(registry.get("history.return_volatility").capabilities.batch)
        for mode in ("update", "restore", "merge"):
            self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: registry.require_capability("history.return_volatility", mode))


if __name__ == "__main__":
    unittest.main()
