"""Independent exact/Decimal expectations for moving averages and dependencies."""
from dataclasses import FrozenInstanceError, replace
from decimal import Decimal, localcontext
from fractions import Fraction
import math
import unittest

from equity_feature_contracts import (
    AvailabilitySpec, Column, ContractError, ErrorCode, Parameter, PriceUnit,
    Reason, SMAReference, Status, WindowSpec, builtin_registry,
)
from equity_features.history import compute_history, compute_sma_reference
from test_history import fixture, config, result_value


def average_config(ctx, n=3, **kwargs):
    cfg = config(ctx, n, **kwargs)
    return replace(cfg, window=WindowSpec(n, ctx.entity.session_id,
                                        tuple(s.session_id for s in ctx.sessions), "completed_eod"))


def decimal_ema(closes, period, scale=0):
    with localcontext() as ctx:
        ctx.prec = 80
        prices = [Decimal(p)/(Decimal(10)**scale) for p in closes]
        mean = sum(prices[:period])/period
        alpha = Decimal(2)/(period+1)
        for price in prices[period:]:
            mean = alpha*price+(1-alpha)*mean
        return float(mean)


class HistoricalAverages(unittest.TestCase):
    def compute(self, batch, ctx, n=3, **kwargs):
        return compute_history(batch, average_config(ctx, n, **kwargs), context=ctx,
                               feature_ids=("history.sma", "history.ema"))

    def assertCode(self, code, callback):
        with self.assertRaises(ContractError) as caught:
            callback()
        self.assertEqual(caught.exception.code, code)

    def test_hand_goldens_and_independent_dependency_counts(self):
        b, ctx = fixture()
        ctx = replace(ctx, initialization_anchor="S0")
        result = self.compute(b, ctx, evidence=20)
        self.assertEqual(result_value(result, "history.sma"), float(Fraction(365, 3)))
        self.assertEqual(result_value(result, "history.ema"), float(Fraction(975, 8)))
        self.assertEqual([(q.expected, q.observed) for q in result.quality], [(3, 3), (6, 6)])
        self.assertEqual([e.row_id for e in result.evidence if e.feature_id == "history.ema"], list(map(str, range(6))))

    def test_defaults_against_high_precision_reference(self):
        closes = tuple(10000+(i*37)%271 for i in range(260))
        b, ctx = fixture(closes)
        ctx = replace(ctx, initialization_anchor="S0")
        for n in (20, 50, 200):
            result = self.compute(b, ctx, n)
            self.assertEqual(result_value(result, "history.sma"), float(Fraction(sum(closes[-n:]), n)))
            self.assertTrue(math.isclose(result_value(result, "history.ema"), decimal_ema(closes, n), rel_tol=1e-12, abs_tol=1e-12))

    def test_period_one_and_seed_warmup(self):
        b, ctx = fixture((100, 110))
        ctx = replace(ctx, initialization_anchor="S0")
        result = self.compute(b, ctx, 1)
        self.assertEqual([c.values[0] for c in result.values], [110.0, 110.0])
        warm = self.compute(b, ctx, 3)
        self.assertTrue(all(q.status == Status.INSUFFICIENT_HISTORY for q in warm.quality))
        self.assertEqual(warm.quality[1].expected, 2)
        self.assertTrue(all(c.values[0] is None for c in warm.values))

    def test_gap_blocks_epoch_but_finite_sma_recovers(self):
        for missing in ((1,), (3,)):
            b, ctx = fixture(missing=missing)
            ctx = replace(ctx, initialization_anchor="S0")
            result = self.compute(b, ctx)
            self.assertIsNone(result_value(result, "history.ema"))
            self.assertEqual(result.quality[1].status, Status.INCOMPLETE_COVERAGE)
            self.assertIn(Reason.GOVERNED_GAP, result.quality[1].reasons)
            if missing == (1,):
                self.assertEqual(result_value(result, "history.sma"), float(Fraction(365, 3)))
                epoch = replace(ctx, initialization_anchor="S3")
                replay = self.compute(b, epoch)
                self.assertEqual(result_value(replay, "history.ema"), float(Fraction(365, 3)))
                self.assertNotEqual(replay.metadata.identity_digest, result.metadata.identity_digest)

    def test_nulls_and_absent_close_never_seed_zero(self):
        b, ctx = fixture((100, None, 105, 120, 115, 130))
        ctx = replace(ctx, initialization_anchor="S0")
        result = self.compute(b, ctx)
        self.assertEqual(result.quality[0].status, Status.AVAILABLE)
        self.assertIsNone(result_value(result, "history.ema"))
        self.assertIn(Reason.NULL_FIELD, result.quality[1].reasons)
        b = replace(b, columns=tuple(c for c in b.columns if c.name != "close"))
        self.assertTrue(all(q.status == Status.MISSING_INPUT for q in self.compute(b, ctx).quality))
        self.assertTrue(all(q.status == Status.MISSING_INPUT for q in self.compute(None, ctx).quality))

    def test_anchor_is_required_and_changes_legitimate_result(self):
        b, ctx = fixture()
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: self.compute(b, ctx))
        first = self.compute(b, replace(ctx, initialization_anchor="S0"))
        later = self.compute(b, replace(ctx, initialization_anchor="S2"))
        self.assertNotEqual(result_value(first, "history.ema"), result_value(later, "history.ema"))
        self.assertEqual(result_value(first, "history.sma"), result_value(later, "history.sma"))
        b, ctx = fixture(target=3)
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: self.compute(b, replace(ctx, initialization_anchor="S4")))

    def test_future_rows_and_known_at_causality(self):
        b, ctx = fixture((100, 110, 105, 120, 115, 130, 999), target=5,
                         known_at_ns=(10, 20, 30, 40, 50, 60, None))
        ctx = replace(ctx, initialization_anchor="S0")
        before = self.compute(b, ctx)
        changed = replace(b, columns=tuple(Column(c.name, c.values[:-1]+(987654,)) if c.name == "close" else c for c in b.columns))
        after = self.compute(changed, ctx)
        self.assertEqual(after.values, before.values)
        self.assertEqual(after.quality, before.quality)
        self.assertEqual(after.metadata.identity_digest, before.metadata.identity_digest)

    def test_prefix_knowledge_and_reconstruction_remain_independent(self):
        for known, reason in ((None, Reason.UNKNOWN_AVAILABILITY), (66, Reason.FUTURE_KNOWLEDGE)):
            b, ctx = fixture(known_at_ns=(10, known, 30, 40, 50, 65))
            ctx = replace(ctx, initialization_anchor="S0")
            causal = self.compute(b, ctx, evidence=20)
            self.assertEqual(causal.quality[0].status, Status.AVAILABLE)
            self.assertEqual(causal.quality[1].status, Status.MISSING_INPUT)
            self.assertIn(reason, causal.quality[1].reasons)
            reconstructed = self.compute(b, ctx, availability=AvailabilitySpec(60, 100, 60, "reconstruction", "audit"), evidence=20)
            self.assertEqual(result_value(reconstructed, "history.ema"), float(Fraction(975, 8)))
            self.assertEqual(next(e.known_at_ns for e in reconstructed.evidence if e.feature_id == "history.ema" and e.row_id == "1"), known)

    def test_target_not_completed_and_bounded_evidence(self):
        b, ctx = fixture()
        ctx = replace(ctx, initialization_anchor="S0")
        result = self.compute(b, ctx, cutoff=51, evidence=2)
        self.assertTrue(all(q.status == Status.INCOMPLETE_COVERAGE for q in result.quality))
        self.assertTrue(all(c.values[0] is None for c in result.values))
        self.assertEqual(len(result.evidence), 2)

    def test_wide_scaled_sums_and_long_ema_precision(self):
        limit = 2**63-1
        closes = tuple(limit-((i*73)%5000) for i in range(5000))
        b, ctx = fixture(closes)
        ctx = replace(ctx, initialization_anchor="S0")
        unit = PriceUnit(8, "USD")
        b = replace(b, metadata=replace(b.metadata, price_unit=unit))
        result = self.compute(b, ctx, 20, price_unit=unit)
        self.assertEqual(result_value(result, "history.sma"), float(Fraction(sum(closes[-20:]), 20*10**8)))
        self.assertTrue(math.isclose(result_value(result, "history.ema"), decimal_ema(closes, 20, 8), rel_tol=1e-12, abs_tol=1e-12))

    def test_exact_reference_preserves_one_tick_hidden_by_float(self):
        limit = 2**63-1
        b, ctx = fixture((limit-1, limit))
        reference = compute_sma_reference(b, average_config(ctx, 2), context=ctx)
        self.assertEqual(reference.numerator, 2*limit-1)
        self.assertEqual(reference.denominator, 2)
        self.assertEqual(reference.result.values[0].values[0], float(limit))
        self.assertEqual(reference.compare_price(limit, PriceUnit(0, "USD")), 1)
        self.assertEqual(reference.compare_price(limit-1, PriceUnit(0, "USD")), -1)
        with self.assertRaises(FrozenInstanceError):
            reference.numerator = 1

    def test_long_oscillating_small_prices_against_decimal(self):
        closes = tuple(1+(i*7919)%100003 if i % 7 else 10**12 for i in range(6000))
        b, ctx = fixture(closes)
        ctx = replace(ctx, initialization_anchor="S0")
        unit = PriceUnit(12, "USD")
        b = replace(b, metadata=replace(b.metadata, price_unit=unit))
        result = self.compute(b, ctx, 50, price_unit=unit)
        self.assertTrue(math.isclose(result_value(result, "history.ema"), decimal_ema(closes, 50, 12), rel_tol=1e-12, abs_tol=1e-12))
        self.assertEqual(result_value(result, "history.sma"), float(Fraction(sum(closes[-50:]), 50*10**12)))

    def test_source_revision_and_unit_guards_bind_averages(self):
        b, ctx = fixture()
        ctx = replace(ctx, initialization_anchor="S0")
        before = self.compute(b, ctx)
        revised = replace(b, metadata=replace(b.metadata, source=replace(b.metadata.source, snapshot_id="r2")))
        after = self.compute(revised, ctx)
        self.assertEqual(after.values, before.values)
        self.assertNotEqual(after.metadata.identity_digest, before.metadata.identity_digest)
        wrong = replace(b, metadata=replace(b.metadata, price_unit=PriceUnit(1, "USD")))
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: self.compute(wrong, ctx))

    def test_exact_reference_ties_and_unavailable_operands(self):
        b, ctx = fixture((100, 110))
        reference = compute_sma_reference(b, average_config(ctx, 2), context=ctx)
        self.assertEqual(reference.compare_price(105, PriceUnit(0, "USD")), 0)
        b, ctx = fixture((100, None))
        absent = compute_sma_reference(b, average_config(ctx, 2), context=ctx)
        self.assertEqual((absent.numerator, absent.denominator), (None, None))
        self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: absent.compare_price(100, PriceUnit(0, "USD")))
        self.assertCode(ErrorCode.INVALID_SCHEMA, lambda: replace(absent, numerator=100, denominator=1))

    def test_reference_rejects_malformed_projection_count_units_and_price(self):
        b, ctx = fixture((100, 110))
        ref = compute_sma_reference(b, average_config(ctx, 2), context=ctx)
        for operands in ((True, 2), (10**38, 2), (210, 0), (1, 2), (210, 3), (211, 2)):
            with self.assertRaises(ContractError):
                replace(ref, numerator=operands[0], denominator=operands[1])
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: replace(ref, price_unit=PriceUnit(1, "USD")))
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: ref.compare_price(100, PriceUnit(0, "EUR")))
        for price in (0, True, 2**63, 1.0):
            self.assertCode(ErrorCode.BOUNDS, lambda: ref.compare_price(price, PriceUnit(0, "USD")))
        self.assertCode(ErrorCode.INCOMPATIBLE_VERSION, lambda: replace(ref, schema_version="2"))
        result = self.compute(b, replace(ctx, initialization_anchor="S0"), 2)
        self.assertCode(ErrorCode.INVALID_SCHEMA, lambda: SMAReference(result, 210, 2, PriceUnit(0, "USD")))

    def test_config_membership_and_modes_are_truthful(self):
        b, ctx = fixture()
        ctx = replace(ctx, initialization_anchor="S0")
        cfg = average_config(ctx)
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: compute_history(b, cfg, context=ctx, feature_ids=("history.sma", "history.return")))
        bad = replace(cfg, parameters=(Parameter("period", True),))
        self.assertCode(ErrorCode.INVALID_CONFIG, lambda: compute_history(b, bad, context=ctx, feature_ids=("history.sma",)))
        for feature in ("history.sma", "history.ema"):
            self.assertTrue(builtin_registry().get(feature).capabilities.batch)
            for mode in ("update", "restore", "merge"):
                self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: builtin_registry().require_capability(feature, mode))


if __name__ == "__main__":
    unittest.main()
