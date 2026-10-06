"""Production composition preserves independent supplied math and rejects false joins."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import unittest
from equity_feature_contracts import ContractError, ErrorCode, Parameter, SourceBinding, VolumeBucket, WindowSpec
from equity_feature_contracts.composition import CompositionSpec, FamilyResult, FeatureBundle
from equity_features.composition import compose_features
from equity_features.history import compute_history, compute_sma_reference
from equity_features.buckets import compute_interval_baseline
from equity_features.breadth import compute_direction_breadth
from test_relative import reference
from test_breadth import direction_setup
from test_bucket_volume import fixture
from test_quotes import cfg as quote_config, quotes, calc as quoted
from test_continuous import cfg as time_config, updates, calc as timed


def component(instance="return", **kwargs):
    ref, batch = reference(**kwargs)
    return FamilyResult(instance, ref.result, ref.config, companion=ref), batch


def spec(c, ids=None):
    return CompositionSpec(c.config.session.namespace, c.config.session, c.config.availability,
                           (c.instance_id,) if ids is None else ids)


class Composition(unittest.TestCase):
    def error(self, code, fn):
        with self.assertRaises(ContractError) as caught:
            fn()
        self.assertEqual(caught.exception.code, code)

    def test_distinct_horizons_order_and_explicit_missing(self):
        short, _ = component("short", closes=(100, 110, 121))
        long, _ = component("long", closes=(100, 110, 121), period=2)
        result = compose_features((short, long), spec=spec(short, ("long", "optional", "short")))
        self.assertEqual(result.components, (long, short))
        self.assertEqual(result.missing_instances, ("optional",))
        self.assertEqual(long.result.values[0].values[0], float(Fraction(21, 100)))
        self.assertEqual(short.result.values[0].values[0], float(Fraction(1, 10)))
        self.assertIs(result.components[0].result, long.result)

    def test_all_missing_and_owned_immutable_input(self):
        c, _ = component()
        declared = ["a", "b"]
        s = CompositionSpec(c.config.session.namespace, c.config.session, c.config.availability, declared)
        declared.append("other")
        result = compose_features([], spec=s)
        self.assertEqual(result.missing_instances, ("a", "b"))
        with self.assertRaises(FrozenInstanceError):
            result.components = ()
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compose_features(iter((c,)), spec=spec(c)))

    def test_unavailable_supplied_family_is_preserved(self):
        c, _ = component(closes=(100, None))
        r = compose_features((c,), spec=spec(c))
        self.assertEqual(r.components[0].result, c.result)
        self.assertIsNone(r.components[0].result.values[0].values[0])
        self.assertEqual(r.missing_instances, ())

    def test_exact_sma_and_breadth_companions_survive(self):
        c, batch = component()
        cfg = replace(c.config, parameters=(Parameter("period", 2), Parameter("evidence_limit", 10)),
                      window=WindowSpec(2, "S1", ("S0", "S1"), "completed_eod"))
        sma = compute_sma_reference(batch, cfg, context=c.companion.context)
        smac = FamilyResult("sma", sma.result, cfg, c.companion.context, sma)
        bundle = compose_features((smac,), spec=spec(smac))
        self.assertIs(bundle.components[0].companion, sma)
        self.assertEqual((sma.numerator, sma.denominator), (210, 2))
        members, bcfg, universe, bs = direction_setup()
        breadth = compute_direction_breadth(members, bcfg, universe=universe, spec=bs)
        bc = FamilyResult("breadth", breadth.result, bcfg, companion=breadth)
        self.assertIs(compose_features((bc,), spec=spec(bc)).components[0].companion, breadth)
        self.assertEqual(len(breadth.exclusions), 1)

    def test_duplicate_extra_missing_and_order_rejected(self):
        c, _ = component()
        self.error(ErrorCode.DUPLICATE, lambda: compose_features((c, c), spec=spec(c)))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compose_features((c,), spec=spec(c, ("other",))))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: FeatureBundle(spec(c), (c,), ("return",)))
        self.error(ErrorCode.DUPLICATE, lambda: replace(spec(c), instance_ids=("a", "a")))

    def test_config_context_and_companion_mismatch(self):
        c, _ = component()
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(c, config=replace(c.config, identity="other")))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(c, context=replace(c.companion.context, grid_version="other")))
        other, _ = component("other", closes=(100, 120))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(c, companion=other.companion))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: FamilyResult("plain", c.result, c.config))

    def test_full_session_timing_namespace_and_modes(self):
        c, _ = component()
        for s in (replace(spec(c), session=replace(c.config.session, timezone_label="different-declaration")),
                  replace(spec(c), availability=replace(c.config.availability, knowledge_cutoff_ns=26, evaluation_ns=26))):
            self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compose_features((c,), spec=s))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(spec(c), namespace="other"))
        for mode in ("update", "merge", "restore"):
            self.error(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: replace(spec(c), mode=mode))
        self.error(ErrorCode.INCOMPATIBLE_VERSION, lambda: replace(c, schema_version="2"))

    def test_actual_backend_version_algorithm_and_evidence_bounds(self):
        c, _ = component()
        stale = replace(c.result, metadata=replace(c.result.metadata, backend_version="old"))
        d = FamilyResult("stale", stale, c.config, c.companion.context)
        self.error(ErrorCode.INCOMPATIBLE_VERSION, lambda: compose_features((d,), spec=spec(d)))
        wrong = replace(c.result, metadata=replace(c.result.metadata, backend_id="python-exact-compensated"))
        self.error(ErrorCode.INCOMPATIBLE_VERSION, lambda: FamilyResult("wrong", wrong, c.config, c.companion.context))
        wrong = replace(c.result, metadata=replace(c.result.metadata, evidence_limit=11))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: FamilyResult("wrong", wrong, c.config, c.companion.context))

    def test_shared_source_revision_and_original_proof_conflicts(self):
        c, _ = component()
        r = c.result
        bindings = tuple(replace(b, metadata=replace(b.metadata, source=replace(b.metadata.source, snapshot_id="r2"))) if b.role == "daily_history" else b for b in r.metadata.inputs)
        d = FamilyResult("revision", replace(r, metadata=replace(r.metadata, inputs=bindings)), c.config, c.companion.context)
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compose_features((c, d), spec=spec(c, ("return", "revision"))))
        changed = tuple(replace(e, known_at_ns=e.known_at_ns+1) for e in r.evidence)
        d = FamilyResult("proof", replace(r, evidence=changed), c.config, c.companion.context)
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compose_features((c, d), spec=spec(c, ("return", "proof"))))

    def test_derived_proof_differences_preserve_components(self):
        c, _ = component()
        changed = tuple(replace(e, effective_start_ns=e.event_ns-1, effective_end_ns=e.event_ns+1) for e in c.result.evidence)
        d = FamilyResult("derived", replace(c.result, evidence=changed), c.config, c.companion.context)
        bundle = compose_features((c, d), spec=spec(c, ("return", "derived")))
        self.assertEqual(bundle.components[1].result.evidence, changed)

    def test_direct_daily_frame_ownership_checked_even_with_zero_evidence(self):
        a, batch = component()
        b, other = component("other", instrument="B")
        cfg = replace(a.config, parameters=(Parameter("period", 1), Parameter("evidence_limit", 0)))
        bcfg = replace(b.config, parameters=cfg.parameters)
        other = replace(other, metadata=replace(other.metadata, source=batch.metadata.source))
        x = FamilyResult("a", compute_history(batch, cfg, context=a.companion.context, feature_ids=("history.return",)), cfg, a.companion.context)
        y = FamilyResult("b", compute_history(other, bcfg, context=b.companion.context, feature_ids=("history.return",)), bcfg, b.companion.context)
        self.assertFalse(x.result.evidence or y.result.evidence)
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compose_features((x, y), spec=spec(x, ("a", "b"))))

    def test_bucket_instances_and_zero_evidence_normalized_scope(self):
        items = []
        for name, start, input_id in (("morning", 0, "morning"), ("late", 20, "late")):
            batch, cfg, ctx = fixture(bucket=VolumeBucket(name, start, start+10, "grid-v1"), evidence=0)
            cfg = replace(cfg, availability=replace(cfg.availability, market_cutoff_ns=cfg.session.close_ns))
            batch = replace(batch, metadata=replace(batch.metadata, source=SourceBinding("fixture", "r1", "v1", input_id)))
            baseline = compute_interval_baseline(batch, cfg, context=ctx)
            items.append(FamilyResult(name, baseline.result, cfg, companion=baseline))
        s = spec(items[0], ("morning", "late"))
        self.assertEqual(len(compose_features(items, spec=s).components), 2)
        late = items[1]
        bindings = tuple(replace(b, metadata=replace(b.metadata, source=SourceBinding("fixture", "r1", "v1", "morning"))) if b.role == "bucket_history" else b for b in late.result.metadata.inputs)
        d = FamilyResult("late", replace(late.result, metadata=replace(late.result.metadata, inputs=bindings)), late.config, late.companion.context)
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compose_features((items[0], d), spec=s))

    def test_actual_sampled_and_continuous_quote_conventions(self):
        sampled = FamilyResult("quotes", quoted(quotes()), quote_config())
        self.assertEqual(compose_features((sampled,), spec=spec(sampled)).components, (sampled,))
        continuous = FamilyResult("time", timed(updates()), time_config())
        self.assertEqual(compose_features((continuous,), spec=spec(continuous)).components, (continuous,))

    def test_digest_binds_missing_spec_original_values_and_companions(self):
        c, _ = component()
        b = compose_features((c,), spec=spec(c))
        missing = compose_features((c,), spec=spec(c, ("return", "optional")))
        plain = replace(c, companion=None, context=c.companion.context)
        self.assertNotEqual(b.identity_digest, missing.identity_digest)
        self.assertNotEqual(b.identity_digest, compose_features((plain,), spec=spec(plain)).identity_digest)

    def test_independent_units_preserved_and_source_unit_conflict_rejected(self):
        from equity_feature_contracts import PriceUnit, ReturnReference
        usd, _ = component()
        eur, batch = component("eur", unit=PriceUnit(0, "EUR"))
        batch = replace(batch, metadata=replace(batch.metadata, source=replace(batch.metadata.source, input_id="prices-EUR")))
        ctx = eur.companion.context
        result = compute_history(batch, eur.config, context=ctx, feature_ids=("history.return",))
        eur = FamilyResult("eur", result, eur.config, companion=ReturnReference(result, eur.config, ctx))
        bundle = compose_features((usd, eur), spec=spec(usd, ("return", "eur")))
        self.assertEqual(tuple(c.config.price_unit.currency for c in bundle.components), ("USD", "EUR"))
        self.assertEqual(usd.result.values, eur.result.values)
        badcfg = replace(usd.config, price_unit=PriceUnit(0, "EUR"))
        badresult = replace(usd.result, metadata=replace(usd.result.metadata, config_digest=badcfg.digest))
        self.error(ErrorCode.INVALID_UNIT, lambda: FamilyResult("bad", badresult, badcfg, usd.companion.context))

    def test_supplied_algorithm_version_is_checked(self):
        c, _ = component()
        changed = tuple(replace(col, algorithm_version="v2") for col in c.result.values)
        self.error(ErrorCode.INCOMPATIBLE_VERSION,
                   lambda: FamilyResult("v2", replace(c.result, values=changed), c.config, c.companion.context))

    def test_mandatory_producer_context_cannot_be_removed_for_missing_source(self):
        c, _ = component()
        ctx = c.companion.context
        missing = compute_history(None, c.config, context=ctx, feature_ids=("history.return",))
        changed = replace(missing, metadata=replace(missing.metadata, inputs=()))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: FamilyResult("history", changed, c.config))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: FamilyResult("history", changed, c.config, ctx))
        batch, cfg, bctx = fixture()
        baseline = compute_interval_baseline(None, cfg, context=bctx)
        changed = replace(baseline.result, metadata=replace(baseline.result.metadata, inputs=()))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: FamilyResult("bucket", changed, cfg))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: FamilyResult("bucket", changed, cfg, bctx))

    def test_delivered_builtin_output_schema_and_sma_config_guard(self):
        from equity_feature_contracts import ValueType
        c, batch = component()
        col = replace(c.result.values[0], dtype=ValueType.INT64, unit="shares", values=(1,))
        self.error(ErrorCode.INVALID_SCHEMA, lambda: FamilyResult("forged", replace(c.result, values=(col,)), c.config, c.companion.context))
        cfg = replace(c.config, parameters=(Parameter("period", 2), Parameter("evidence_limit", 10)),
                      window=WindowSpec(2, "S1", ("S0", "S1"), "completed_eod"))
        sma = compute_sma_reference(batch, cfg, context=c.companion.context)
        badcfg = replace(cfg, parameters=(Parameter("period", 1), Parameter("evidence_limit", 10)),
                         window=WindowSpec(1, "S1", ("S0", "S1"), "completed_eod"))
        changed = replace(sma.result, metadata=replace(sma.result.metadata, config_digest=badcfg.digest))
        witness = replace(sma, result=changed)
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: FamilyResult("sma", changed, badcfg, c.companion.context, witness))

    def test_actual_history_price_output_currency_and_extrema_dtype(self):
        from equity_feature_contracts import Column, PriceUnit, ValueType
        c, batch = component(unit=PriceUnit(0, "EUR"))
        cfg = replace(c.config, window=WindowSpec(1, "S1", ("S0", "S1"), "prior_only"))
        batch = replace(batch, columns=batch.columns+(Column("high", (102, 112)), Column("low", (98, 108))))
        result = compute_history(batch, cfg, context=c.companion.context,
                                 feature_ids=("history.prior_high", "history.prior_low"))
        item = FamilyResult("extrema", result, cfg, c.companion.context)
        bundle = compose_features((item,), spec=spec(item))
        self.assertEqual(tuple(col.dtype for col in result.values), (ValueType.FLOAT64, ValueType.FLOAT64))
        self.assertEqual(tuple(col.unit for col in result.values), ("EUR/share", "EUR/share"))
        self.assertEqual(tuple(col.values[0] for col in bundle.components[0].result.values), (102.0, 98.0))

    def test_direct_session_frame_owner_conflicts_without_retained_evidence(self):
        from equity_feature_contracts import EntityKey
        from equity_features.session import compute_bars, compute_trades, compute_quotes
        from test_bars import config, batch as bars
        from test_trades import trades
        for producer, factory, cfg in ((compute_trades, trades, config()),
                                       (compute_bars, bars, config()),
                                       (compute_quotes, quotes, quote_config(0))):
            with self.subTest(producer=producer.__name__):
                first = factory()
                second = factory(instrument_id=("B",)*first.row_count)
                a = FamilyResult("a", producer(first, cfg, entity=EntityKey("A", "S")), cfg)
                b = FamilyResult("b", producer(second, cfg, entity=EntityKey("B", "S")), cfg)
                self.assertFalse(a.result.evidence or b.result.evidence)
                self.error(ErrorCode.INCONSISTENT_IDENTITY,
                           lambda: compose_features((a, b), spec=spec(a, ("a", "b"))))

    def test_same_instrument_original_quote_frame_can_supply_distinct_features(self):
        from equity_feature_contracts import EntityKey
        from equity_features.session import compute_quotes, compute_time_weighted
        cfg = time_config()
        sampled_cfg = replace(cfg, parameters=(Parameter("eligibility_policy", "synthetic-v1"), Parameter("observation_limit", 0)))
        batch = updates()
        a = FamilyResult("sampled", compute_quotes(batch, sampled_cfg, entity=EntityKey("A", "S")), sampled_cfg)
        b = FamilyResult("time", compute_time_weighted(batch, cfg, entity=EntityKey("A", "S")), cfg)
        bundle = compose_features((a, b), spec=spec(a, ("sampled", "time")))
        self.assertEqual(bundle.components, (a, b))

    def test_session_and_bucket_share_original_frame_without_false_scope_conflict(self):
        from test_bars import config, batch, ENTITY
        from equity_features.session.bars import compute_bars
        from equity_feature_contracts import BucketContext, SessionSpec, Coverage
        b = batch(instrument_id=("A",), session_id=("S",), start_ns=(100,), end_ns=(200,),
                  open=(100,), high=(103,), low=(99,), close=(102,), volume=(200,),
                  actual_notional=(20300,), known_at_ns=(200,))
        cfg = config()
        ctx = BucketContext(ENTITY, "grid-v1", (SessionSpec("demo", "P", 0, 100, "supplied"), cfg.session),
                            VolumeBucket("full", 0, 100, "grid-v1"), (Coverage(1, 0, False), Coverage(1, 1, True)))
        bcfg = replace(cfg, identity="bucket", parameters=(Parameter("period", 1), Parameter("evidence_limit", 0)),
                       window=WindowSpec(1, "S", ("P", "S"), "prior_only"))
        baseline = compute_interval_baseline(b, bcfg, context=ctx)
        bars = FamilyResult("bars", compute_bars(b, cfg, entity=ENTITY), cfg)
        prior = FamilyResult("baseline", baseline.result, bcfg, companion=baseline)
        self.assertEqual(prior.result.evidence, ())
        self.assertEqual(prior.result.values[0].values, (None,))
        for components in ((bars, prior), (prior, bars)):
            with self.subTest(order=tuple(c.instance_id for c in components)):
                bundle = compose_features(components, spec=spec(bars, tuple(c.instance_id for c in components)))
                self.assertEqual(bundle.components, components)
                self.assertIs(bundle.components[components.index(prior)].result, baseline.result)


if __name__ == "__main__":
    unittest.main()
