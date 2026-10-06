"""Final R2 actual-API causality/discovery audit with independent exact goldens."""
from dataclasses import replace
from fractions import Fraction
import math
import unittest
from equity_feature_contracts import Column, ContractError, ErrorCode, Status, ValueType, WindowSpec, builtin_registry
from equity_features.history import compute_history
from equity_features.breadth import compute_direction_breadth, compute_above_sma_breadth
from test_history import fixture, config
from test_breadth import direction_setup, above_setup

GOLDENS = {
    "history.return": Fraction(5, 21), "history.prior_high": Fraction(122), "history.prior_low": Fraction(103),
    "history.sma": Fraction(365, 3), "history.ema": Fraction(975, 8), "history.rsi": Fraction(4700, 57),
    "history.atr": Fraction(122, 9), "history.return_volatility": math.sqrt(float(Fraction(476449, 44791488))),
}


def frame(*, missing=()):
    return fixture((100, 110, 105, 120, 115, 130, 132), target=5, missing=missing,
                   high=(102, 112, 111, 122, 121, 132, 134), low=(98, 99, 103, 104, 113, 114, 129))


def calculate(batch, ctx, feature):
    prior = feature in ("history.prior_high", "history.prior_low")
    if feature in ("history.ema", "history.rsi", "history.atr"):
        ctx = replace(ctx, initialization_anchor="S1" if feature == "history.atr" else "S0")
    cfg = config(ctx, 3, prior=prior, cutoff=51 if prior else 60)
    if feature in ("history.sma", "history.ema", "history.atr"):
        cfg = replace(cfg, window=WindowSpec(3, "S5", tuple(s.session_id for s in ctx.sessions), "completed_eod"))
    return compute_history(batch, cfg, context=ctx, feature_ids=(feature,))


def mutate(batch, indices):
    return replace(batch, columns=tuple(Column(c.name, tuple(5000 if i in indices else v for i, v in enumerate(c.values)))
                   if c.name in ("high", "low", "close") else c for c in batch.columns))


class R2Integration(unittest.TestCase):
    def test_eight_history_goldens_discovery_and_unused_future_invariance(self):
        b, ctx = frame()
        for feature, expected in GOLDENS.items():
            with self.subTest(feature=feature):
                r = calculate(b, ctx, feature)
                col = r.values[0]
                self.assertEqual(r.quality[0].status, Status.AVAILABLE)
                self.assertTrue(math.isclose(col.values[0], float(expected), rel_tol=1e-12, abs_tol=1e-12))
                self.assertEqual(col.dtype, ValueType(builtin_registry().get(feature).outputs[0].dtype))
                self.assertEqual(r, calculate(mutate(b, (6,)), ctx, feature))
                if feature in ("history.prior_high", "history.prior_low"):
                    self.assertEqual(r, calculate(mutate(b, (5, 6)), ctx, feature))

    def test_missing_old_prefix_breaks_recursive_but_finite_windows_recover(self):
        b, ctx = frame(missing=(1,))
        for feature, expected in GOLDENS.items():
            with self.subTest(feature=feature):
                r = calculate(b, ctx, feature)
                if feature in ("history.ema", "history.rsi", "history.atr"):
                    self.assertEqual(r.quality[0].status, Status.INCOMPLETE_COVERAGE)
                    self.assertIsNone(r.values[0].values[0])
                else:
                    self.assertEqual(r.quality[0].status, Status.AVAILABLE)
                    self.assertTrue(math.isclose(r.values[0].values[0], float(expected), rel_tol=1e-12, abs_tol=1e-12))

    def test_actual_breadth_wire_units_and_truthful_mode_inventory(self):
        registry = builtin_registry()
        for setup, compute in ((direction_setup, compute_direction_breadth), (above_setup, compute_above_sma_breadth)):
            members, cfg, universe, spec = setup()
            col = compute(members, cfg, universe=universe, spec=spec).result.values[0]
            with self.subTest(feature=col.feature_id):
                output = registry.get(col.feature_id).outputs[0]
                self.assertEqual(col.dtype, ValueType(output.dtype))
                self.assertEqual(col.unit, output.unit)
        r2 = tuple(d for d in registry.list_features() if d.planned_release == "R2")
        self.assertEqual(len(r2), 16)
        self.assertEqual(tuple(len(registry.list_features(capability=m)) for m in ("batch", "update", "restore", "merge")), (39, 23, 23, 22))
        for definition in r2:
            registry.require_capability(definition.feature_id, "batch")
            for mode in ("update", "restore", "merge"):
                with self.subTest(feature=definition.feature_id, mode=mode):
                    self.assertFalse(getattr(definition.capabilities, mode))
                    with self.assertRaises(ContractError) as caught:
                        registry.require_capability(definition.feature_id, mode)
                    self.assertEqual(caught.exception.code, ErrorCode.UNSUPPORTED_CAPABILITY)


if __name__ == "__main__":
    unittest.main()
