"""Independent Wilder/Decimal oracles, epoch and actual API admission fixtures."""
from dataclasses import replace
from decimal import Decimal, localcontext
from fractions import Fraction
import math
import unittest
from equity_feature_contracts import (
    ActionPolicy, AdjustmentSpec, AvailabilitySpec, Column, ContractError, ErrorCode,
    Parameter, PriceUnit, Reason, Status, WindowSpec, builtin_registry,
)
from equity_features.history import compute_history
from equity_features.policies import admit_action_policy
from test_history import fixture, config, result_value


def recursive_config(ctx, period=3, *, atr=False, **kwargs):
    cfg = config(ctx, period, **kwargs)
    return replace(cfg, window=WindowSpec(period if atr else period+1, ctx.entity.session_id,
                                        tuple(s.session_id for s in ctx.sessions), "completed_eod"))


def decimal_rsi(closes, period):
    with localcontext() as context:
        context.prec = 80
        differences = [Decimal(b)-Decimal(a) for a, b in zip(closes, closes[1:])]
        gain = sum(max(x, Decimal(0)) for x in differences[:period])/period
        loss = sum(max(-x, Decimal(0)) for x in differences[:period])/period
        for x in differences[period:]:
            gain = ((period-1)*gain+max(x, Decimal(0)))/period
            loss = ((period-1)*loss+max(-x, Decimal(0)))/period
        return float(100*gain/(gain+loss)) if gain+loss else 50.0


def decimal_atr(closes, highs, lows, period, scale=0):
    with localcontext() as context:
        context.prec = 80
        tr = [Decimal(max(h-l, abs(h-c), abs(l-c))) for c, h, l in zip(closes, highs[1:], lows[1:])]
        average = sum(tr[:period])/period
        for x in tr[period:]:
            average = ((period-1)*average+x)/period
        return float(average/(Decimal(10)**scale))


class RecursiveHistory(unittest.TestCase):
    def assertCode(self, code, callback):
        with self.assertRaises(ContractError) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def compute(self, batch, ctx, period=3, *, atr=False, **kwargs):
        feature = "history.atr" if atr else "history.rsi"
        return compute_history(batch, recursive_config(ctx, period, atr=atr, **kwargs),
                               context=ctx, feature_ids=(feature,))

    def test_hand_goldens_exact_seed_and_quality_membership(self):
        b, ctx = fixture(high=(102, 112, 111, 122, 121, 132), low=(98, 99, 103, 104, 113, 114))
        rsi = self.compute(b, replace(ctx, initialization_anchor="S0"), evidence=20)
        atr = self.compute(b, replace(ctx, initialization_anchor="S1"), atr=True, evidence=20)
        self.assertTrue(math.isclose(result_value(rsi, "history.rsi"), float(Fraction(4700, 57)), rel_tol=1e-12, abs_tol=1e-12))
        self.assertTrue(math.isclose(result_value(atr, "history.atr"), float(Fraction(122, 9)), rel_tol=1e-12, abs_tol=1e-12))
        self.assertEqual((rsi.quality[0].expected, rsi.quality[0].observed), (6, 6))
        self.assertEqual((atr.quality[0].expected, atr.quality[0].observed), (6, 6))
        self.assertEqual([e.row_id for e in atr.evidence], list(map(str, range(6))))
        self.assertEqual(rsi.values[0].unit, builtin_registry().get("history.rsi").outputs[0].unit)

    def test_defaults_against_independent_high_precision(self):
        closes = tuple(10000+(i*37)%271 for i in range(250))
        highs, lows = tuple(x+17 for x in closes), tuple(x-23 for x in closes)
        b, ctx = fixture(closes, high=highs, low=lows)
        rsi = self.compute(b, replace(ctx, initialization_anchor="S0"), 14)
        atr = self.compute(b, replace(ctx, initialization_anchor="S1"), 14, atr=True)
        self.assertTrue(math.isclose(result_value(rsi, "history.rsi"), decimal_rsi(closes, 14), rel_tol=1e-12, abs_tol=1e-12))
        self.assertTrue(math.isclose(result_value(atr, "history.atr"), decimal_atr(closes, highs, lows, 14), rel_tol=1e-12, abs_tol=1e-12))

    def test_gain_loss_and_entirely_flat_seeds(self):
        for closes, expected in (((100, 110, 120, 130), 100.0), ((130, 120, 110, 100), 0.0), ((100,)*4, 50.0)):
            b, ctx = fixture(closes)
            self.assertEqual(result_value(self.compute(b, replace(ctx, initialization_anchor="S0")), "history.rsi"), expected)

    def test_long_non_neutral_flat_continuation_and_new_movement(self):
        closes = (100, 110, 105, 120, 115, 130)+(130,)*20001
        b, ctx = fixture(closes)
        ctx = replace(ctx, initialization_anchor="S0")
        result = self.compute(b, ctx)
        self.assertTrue(math.isclose(result_value(result, "history.rsi"), float(Fraction(4700, 57)), rel_tol=1e-12, abs_tol=1e-12))
        self.assertTrue(math.isclose(result_value(result, "history.rsi"), decimal_rsi(closes, 3), rel_tol=1e-12, abs_tol=1e-12))
        for last, expected in ((131, 100.0), (129, 0.0)):
            changed = replace(b, columns=tuple(Column(c.name, c.values[:-1]+(last,)) if c.name == "close" else c for c in b.columns))
            response = result_value(self.compute(changed, ctx), "history.rsi")
            self.assertTrue(math.isclose(response, expected, rel_tol=1e-12, abs_tol=1e-12))
            self.assertTrue(math.isclose(response, decimal_rsi(closes[:-1]+(last,), 3), rel_tol=1e-12, abs_tol=1e-12))

    def test_flat_seed_can_receive_first_gain_or_loss(self):
        for closes, expected in (((100,)*6+(101,), 100.0), ((100,)*6+(99,), 0.0)):
            b, ctx = fixture(closes)
            self.assertEqual(result_value(self.compute(b, replace(ctx, initialization_anchor="S0")), "history.rsi"), expected)

    def test_previous_close_never_high_low_fallback_and_atr_one(self):
        b, ctx = fixture((100, 110, 105), high=(102, 112, 111), low=(98, 99, 103))
        ctx = replace(ctx, initialization_anchor="S1")
        self.assertEqual(result_value(self.compute(b, ctx, 1, atr=True), "history.atr"), 8.0)
        absent = replace(b, columns=tuple(Column(c.name, (None,)+c.values[1:]) if c.name == "close" else c for c in b.columns))
        result = self.compute(absent, ctx, 1, atr=True)
        self.assertIsNone(result_value(result, "history.atr"))
        self.assertIn(Reason.NULL_FIELD, result.quality[0].reasons)
        first_anchor = replace(ctx, initialization_anchor="S0")
        self.assertEqual(self.compute(b, first_anchor, 1, atr=True).quality[0].status, Status.INSUFFICIENT_HISTORY)

    def test_zero_true_range_is_available(self):
        b, ctx = fixture((100,)*7, high=(100,)*7, low=(100,)*7)
        result = self.compute(b, replace(ctx, initialization_anchor="S1"), 3, atr=True)
        self.assertEqual(result_value(result, "history.atr"), 0.0)
        self.assertEqual(result.quality[0].status, Status.AVAILABLE)

    def test_atr_target_close_is_not_current_dependency(self):
        b, ctx = fixture((100, 110, 105, 120, 115, None), high=(102, 112, 111, 122, 121, 132), low=(98, 99, 103, 104, 113, 114))
        atr = self.compute(b, replace(ctx, initialization_anchor="S1"), atr=True)
        self.assertTrue(math.isclose(result_value(atr, "history.atr"), float(Fraction(122, 9)), rel_tol=1e-12, abs_tol=1e-12))
        rsi = self.compute(b, replace(ctx, initialization_anchor="S0"))
        self.assertEqual(rsi.quality[0].status, Status.INCOMPLETE_COVERAGE)
        self.assertIsNone(result_value(rsi, "history.rsi"))

    def test_field_independence_and_required_prefix_closes(self):
        b, ctx = fixture(high=(102, 112, None, 122, 121, 132), low=(98, 99, 103, 104, 113, 114))
        self.assertEqual(self.compute(b, replace(ctx, initialization_anchor="S0")).quality[0].status, Status.AVAILABLE)
        self.assertEqual(self.compute(b, replace(ctx, initialization_anchor="S1"), atr=True).quality[0].status, Status.INCOMPLETE_COVERAGE)
        b = replace(b, columns=tuple(c for c in b.columns if c.name != "low"))
        self.assertEqual(self.compute(b, replace(ctx, initialization_anchor="S1"), atr=True).quality[0].status, Status.MISSING_INPUT)

    def test_gap_never_restarts_and_new_epoch_rewarms(self):
        closes = (100, 110, 105, 120, 115, 130, 120, 140)
        b, ctx = fixture(closes, missing=(1,), high=tuple(x+2 for x in closes), low=tuple(x-2 for x in closes))
        old = self.compute(b, replace(ctx, initialization_anchor="S0"))
        self.assertEqual(old.quality[0].status, Status.INCOMPLETE_COVERAGE)
        replay = self.compute(b, replace(ctx, initialization_anchor="S4"))
        self.assertTrue(math.isclose(result_value(replay, "history.rsi"), decimal_rsi(closes[4:], 3), rel_tol=1e-12, abs_tol=1e-12))
        self.assertNotEqual(old.metadata.identity_digest, replay.metadata.identity_digest)
        atr = self.compute(b, replace(ctx, initialization_anchor="S5"), atr=True)
        self.assertTrue(math.isclose(result_value(atr, "history.atr"), decimal_atr(closes[4:], tuple(x+2 for x in closes[4:]), tuple(x-2 for x in closes[4:]), 3), rel_tol=1e-12, abs_tol=1e-12))

    def test_warmup_missing_input_and_period_guards(self):
        b, ctx = fixture((100, 110, 105), high=(102, 112, 111), low=(98, 99, 103))
        ctx = replace(ctx, initialization_anchor="S0")
        self.assertEqual(self.compute(b, ctx).quality[0].status, Status.INSUFFICIENT_HISTORY)
        self.assertEqual(self.compute(None, ctx).quality[0].status, Status.MISSING_INPUT)
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: self.compute(b, ctx, 1))
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: self.compute(b, replace(ctx, initialization_anchor=None)))
        bad = replace(recursive_config(ctx), parameters=(Parameter("period", True),))
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: compute_history(b, bad, context=ctx, feature_ids=("history.rsi",)))

    def test_future_mutation_cutoff_and_original_evidence(self):
        closes = (100, 110, 105, 120, 115, 130, 999)
        b, ctx = fixture(closes, target=5, high=tuple(x+2 for x in closes), low=tuple(x-2 for x in closes))
        ctx = replace(ctx, initialization_anchor="S0")
        before = self.compute(b, ctx, evidence=2)
        changed = replace(b, columns=tuple(Column(c.name, c.values[:-1]+(1000,)) if c.name == "close" else c for c in b.columns))
        after = self.compute(changed, ctx, evidence=2)
        self.assertEqual(after.values, before.values)
        self.assertEqual(after.quality, before.quality)
        self.assertEqual(after.evidence, before.evidence)
        self.assertEqual([(e.row_id, e.event_ns) for e in before.evidence], [("0", 10), ("1", 20)])
        forming = self.compute(b, ctx, cutoff=51)
        self.assertIsNone(result_value(forming, "history.rsi"))
        self.assertIn(Reason.FUTURE_MARKET, forming.quality[0].reasons)

    def test_unknown_prefix_knowledge_and_explicit_reconstruction(self):
        b, ctx = fixture(known_at_ns=(10, None, 30, 40, 50, 65))
        ctx = replace(ctx, initialization_anchor="S0")
        causal = self.compute(b, ctx)
        self.assertEqual(causal.quality[0].status, Status.MISSING_INPUT)
        self.assertIn(Reason.UNKNOWN_AVAILABILITY, causal.quality[0].reasons)
        replay = self.compute(b, ctx, availability=AvailabilitySpec(60, 100, 60, "reconstruction", "audit"), evidence=10)
        self.assertTrue(math.isclose(result_value(replay, "history.rsi"), float(Fraction(4700, 57)), rel_tol=1e-12, abs_tol=1e-12))
        self.assertIsNone(replay.evidence[1].known_at_ns)

    def test_scaled_wide_and_long_oscillating_precision(self):
        limit = 2**63-1
        closes = tuple(limit-1 if i % 3 else 100 for i in range(1200))
        highs, lows = (limit,)*len(closes), (1,)*len(closes)
        b, ctx = fixture(closes, high=highs, low=lows)
        unit = PriceUnit(18, "USD")
        b = replace(b, metadata=replace(b.metadata, price_unit=unit))
        rsi = self.compute(b, replace(ctx, initialization_anchor="S0"), 14, price_unit=unit)
        atr = self.compute(b, replace(ctx, initialization_anchor="S1"), 14, atr=True, price_unit=unit)
        self.assertTrue(math.isclose(result_value(rsi, "history.rsi"), decimal_rsi(closes, 14), rel_tol=1e-12, abs_tol=1e-12))
        self.assertTrue(math.isclose(result_value(atr, "history.atr"), decimal_atr(closes, highs, lows, 14, 18), rel_tol=1e-12, abs_tol=1e-12))

    def test_action_admission_is_required_and_missing_remains_null(self):
        b, ctx = fixture()
        ctx = replace(ctx, initialization_anchor="S0")
        adjustment = AdjustmentSpec("split", "split-factors-v1", "actions-r1", "S5")
        cfg = recursive_config(ctx, adjustment=adjustment)
        b = replace(b, metadata=replace(b.metadata, adjustment=adjustment))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: compute_history(b, cfg, context=ctx, feature_ids=("history.rsi",)))
        policy = ActionPolicy(adjustment, 60)
        admitted = admit_action_policy(None, policy, cfg, entity=ctx.entity)
        result = compute_history(b, cfg, context=replace(ctx, action_admission=admitted), feature_ids=("history.rsi",))
        self.assertIsNone(result_value(result, "history.rsi"))
        self.assertIn(Reason.MISSING_ACTION_EVIDENCE, result.quality[0].reasons)

    def test_atr_previous_row_high_low_are_not_dependencies(self):
        b, ctx = fixture(high=(None, 112, 111, 122, 121, 132), low=(None, 99, 103, 104, 113, 114))
        result = self.compute(b, replace(ctx, initialization_anchor="S1"), atr=True)
        self.assertTrue(math.isclose(result_value(result, "history.atr"), float(Fraction(122, 9)), rel_tol=1e-12, abs_tol=1e-12))

    def test_atr_unknown_previous_close_knowledge_and_target_completion(self):
        b, ctx = fixture(high=(102, 112, 111, 122, 121, 132), low=(98, 99, 103, 104, 113, 114),
                         known_at_ns=(None, 20, 30, 40, 50, 60))
        ctx = replace(ctx, initialization_anchor="S1")
        causal = self.compute(b, ctx, atr=True)
        self.assertEqual(causal.quality[0].status, Status.MISSING_INPUT)
        self.assertIn(Reason.UNKNOWN_AVAILABILITY, causal.quality[0].reasons)
        replay = self.compute(b, ctx, atr=True, availability=AvailabilitySpec(60, 100, 60, "reconstruction", "audit"))
        self.assertTrue(math.isclose(result_value(replay, "history.atr"), float(Fraction(122, 9)), rel_tol=1e-12, abs_tol=1e-12))
        forming = self.compute(b, ctx, atr=True, cutoff=51, availability=AvailabilitySpec(51, 100, 60, "reconstruction", "audit"))
        self.assertIsNone(result_value(forming, "history.atr"))
        self.assertIn(Reason.FUTURE_MARKET, forming.quality[0].reasons)

    def test_registry_modes_and_separate_anchor_configs(self):
        b, ctx = fixture()
        ctx = replace(ctx, initialization_anchor="S0")
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: compute_history(b, recursive_config(ctx), context=ctx, feature_ids=("history.rsi", "history.atr")))
        for feature in ("history.rsi", "history.atr"):
            self.assertTrue(builtin_registry().get(feature).capabilities.batch)
            for mode in ("update", "restore", "merge"):
                self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: builtin_registry().require_capability(feature, mode))


if __name__ == "__main__":
    unittest.main()
