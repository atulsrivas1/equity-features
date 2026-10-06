"""Independent production breadth arithmetic, missingness and exact witness fixtures."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import unittest
from equity_feature_contracts import (
    BreadthCounts, BreadthFraction, BreadthSpec, CompletedClose, ContractError,
    Coverage, DeclaredUniverseSpec, EntityKey, ErrorCode, InputBinding, InputScope,
    MemberFeatures, Parameter, PriceUnit, Reason, SMAInput, SourceBinding, Status,
    WindowSpec, builtin_registry,
)
from equity_features.breadth import compute_above_sma_breadth, compute_direction_breadth
from equity_features.history import compute_sma_reference
from test_relative import reference


def direction_setup(closes=((100, 110), (100, 95), (100, 100)), ids=("a", "b", "c", "d")):
    refs = tuple(reference(i, prices)[0] for i, prices in zip(ids, closes))
    cfg = replace(refs[0].config, identity="breadth", parameters=(Parameter("period", 1), Parameter("evidence_limit", 20)))
    u = DeclaredUniverseSpec("synthetic", "S1", "U", "membership-r1", 11, ids)
    spec = BreadthSpec(EntityKey("U", "S1"))
    return tuple(MemberFeatures(r.context.entity, return_reference=r) for r in refs), cfg, u, spec


def sma_member(instrument="a", prices=(9, 11), close=11, *, known=20, close_source=None):
    r, batch = reference(instrument, prices)
    cfg = replace(r.config, identity="sma-"+instrument, parameters=(Parameter("period", 2), Parameter("evidence_limit", 20)), window=WindowSpec(2, "S1", ("S0", "S1"), "completed_eod"))
    sma = SMAInput(compute_sma_reference(batch, cfg, context=r.context), cfg, r.context)
    source = InputBinding("completed_close", batch.kind, replace(batch.metadata, source=SourceBinding("fixture", "r1", "v1", "close-"+instrument))) if close_source is None else close_source
    target = CompletedClose(r.context.entity, close, known, source, 1, InputScope(11, 20, "supplied"), Coverage(1, 1, True))
    return MemberFeatures(r.context.entity, sma=sma, close=target)


def above_setup():
    members = tuple(sma_member(i, close=c) for i, c in zip(("a", "b", "c"), (11, 9, 10)))
    cfg = replace(members[0].sma.config, identity="above")
    u = DeclaredUniverseSpec("synthetic", "S1", "U", "membership-r1", 11, ("a", "b", "c", "d"))
    return members, cfg, u, BreadthSpec(EntityKey("U", "S1"))


class Breadth(unittest.TestCase):
    def assertCode(self, code, call):
        with self.assertRaises(ContractError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)

    def direction(self, members, cfg, u, spec):
        return compute_direction_breadth(members, cfg, universe=u, spec=spec)

    def above(self, members, cfg, u, spec):
        return compute_above_sma_breadth(members, cfg, universe=u, spec=spec)

    def test_partial_and_complete_manual_direction_counts(self):
        m, c, u, s = direction_setup()
        r = self.direction(m, c, u, s)
        self.assertEqual(r.result.values[0].values[0], BreadthCounts(1, 1, 1, 4))
        self.assertEqual(r.result.values[0].values[0].coverage, Fraction(3, 4))
        self.assertEqual(r.result.quality[0].status, Status.INCOMPLETE_COVERAGE)
        self.assertEqual(r.exclusions[0].entity, EntityKey("d", "S1"))
        self.assertFalse(any(e.row_id == "d" for e in r.result.evidence))
        r = self.direction(m, c, replace(u, members=("a", "b", "c")), s)
        self.assertEqual(r.result.quality[0].status, Status.AVAILABLE)
        self.assertEqual(r.exclusions, ())

    def test_manual_above_sma_counts_and_eligible_denominator(self):
        m, c, u, s = above_setup()
        r = self.above(m, c, u, s)
        self.assertEqual(r.result.values[0].values[0], BreadthFraction(1, 3, 4))
        self.assertEqual(r.result.values[0].values[0].fraction, Fraction(1, 3))
        self.assertEqual(r.result.quality[0].observed, 3)
        self.assertEqual(r.result.quality[0].status, Status.INCOMPLETE_COVERAGE)

    def test_exact_int64_half_tick_above_despite_float_equality(self):
        high = 2**63-1
        member = sma_member(prices=(high-1, high), close=high)
        self.assertEqual(float(high), member.sma.reference.result.values[0].values[0])
        cfg = member.sma.config
        u = DeclaredUniverseSpec("synthetic", "S1", "U", "r1", 11, ("a",))
        r = self.above((member,), cfg, u, BreadthSpec(EntityKey("U", "S1")))
        self.assertEqual(r.result.values[0].values[0], BreadthFraction(1, 1, 1))

    def test_empty_absent_and_known_empty_dataset_remain_distinct(self):
        for setup, compute in ((direction_setup, self.direction), (above_setup, self.above)):
            m, c, u, s = setup()
            absent = compute(m, c, None, s)
            self.assertEqual(absent.result.quality[0].status, Status.MISSING_INPUT)
            self.assertIsNone(absent.result.quality[0].expected)
            missing = compute(None, c, u, s)
            self.assertEqual(missing.result.quality[0].status, Status.MISSING_INPUT)
            empty_data = compute((), c, u, s)
            self.assertEqual(empty_data.result.quality[0].status, Status.INCOMPLETE_COVERAGE)
            self.assertEqual(empty_data.result.quality[0].observed, 0)
            self.assertEqual(len(empty_data.exclusions), 4)
            self.assertIsNone(empty_data.result.values[0].values[0])
            empty_u = compute((), c, replace(u, members=()), s)
            self.assertEqual(empty_u.result.quality[0].status, Status.NOT_APPLICABLE)
            self.assertEqual(empty_u.result.quality[0].reasons, (Reason.EMPTY_UNIVERSE,))

    def test_all_unready_and_zero_are_not_interchangeable(self):
        m, c, u, s = direction_setup(closes=((100, None), (100, None), (100, None)))
        r = self.direction(m, c, u, s)
        self.assertIsNone(r.result.values[0].values[0])
        self.assertEqual(r.result.quality[0].observed, 0)
        m, c, u, s = direction_setup(closes=((100, 100), (100, 100), (100, 100)))
        self.assertEqual(self.direction(m, c, u, s).result.values[0].values[0], BreadthCounts(0, 0, 3, 4))

    def test_missing_close_and_sma_exclude_only_their_members(self):
        m, c, u, s = above_setup()
        data = (replace(m[0], close=None), replace(m[1], sma=None), m[2])
        r = self.above(data, c, u, s)
        self.assertEqual(r.result.values[0].values[0], BreadthFraction(0, 1, 4))
        self.assertEqual({e.entity.instrument_id for e in r.exclusions}, {"a", "b", "d"})
        r = self.above((replace(m[0], close=replace(m[0].close, coefficient=None)),), c, replace(u, members=("a",)), s)
        self.assertIn(Reason.NULL_FIELD, r.exclusions[0].reasons)

    def test_unknown_late_and_reconstructed_close_keep_original_evidence(self):
        m, c, u, s = above_setup()
        for known, reason in ((None, Reason.UNKNOWN_AVAILABILITY), (26, Reason.FUTURE_KNOWLEDGE)):
            data = (replace(m[0], close=replace(m[0].close, known_at_ns=known)),)
            r = self.above(data, c, replace(u, members=("a",)), s)
            self.assertEqual(r.exclusions[0].reasons, (reason,))
            self.assertTrue(any(e.known_at_ns == known and e.use == "excluded" for e in r.result.evidence))
        from equity_feature_contracts import AvailabilitySpec
        avail = AvailabilitySpec(20, 25, 25, "reconstruction", "synthetic audit")
        sm = m[0].sma
        from equity_features.history import compute_sma_reference
        _, b = reference("a", (9, 11))
        cfg = replace(sm.config, availability=avail)
        rebuilt = SMAInput(compute_sma_reference(b, cfg, context=sm.context), cfg, sm.context)
        data = (replace(m[0], sma=rebuilt, close=replace(m[0].close, known_at_ns=None)),)
        r = self.above(data, replace(c, availability=avail), replace(u, members=("a",)), s)
        self.assertEqual(r.result.quality[0].status, Status.AVAILABLE)
        self.assertTrue(any(e.known_at_ns is None for e in r.result.evidence))

    def test_partial_close_and_wrong_completed_interval(self):
        m, c, u, s = above_setup()
        r = self.above((replace(m[0], close=replace(m[0].close, coverage=Coverage(1, 1, False))),), c, replace(u, members=("a",)), s)
        self.assertEqual(r.exclusions[0].status, Status.INCOMPLETE_COVERAGE)
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.above((replace(m[0], close=replace(m[0].close, interval=InputScope(11, 19, "supplied"))),), c, u, s))

    def test_duplicate_extra_and_membership_point_guards(self):
        m, c, u, s = direction_setup()
        self.assertCode(ErrorCode.DUPLICATE, lambda: replace(u, members=("a", "a")))
        self.assertCode(ErrorCode.DUPLICATE, lambda: self.direction((m[0], m[0]), c, u, s))
        for bad in (replace(u, members=("d",)), replace(u, namespace="other"), replace(u, session_id="S0"), replace(u, effective_ns=20), replace(u, effective_ns=10)):
            self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.direction(m, c, bad, s))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(m[0], entity=EntityKey("other", "S1")))

    def test_horizon_currency_grid_backend_and_cutoff_alignment(self):
        m, c, u, s = direction_setup()
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: self.direction(m, replace(c, price_unit=PriceUnit(1, "USD")), u, s))
        r, _ = reference("a", (100, 105, 110), period=2, target=1)
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.direction((MemberFeatures(r.context.entity, r),), c, u, s))
        r = m[1].return_reference
        cfg = replace(r.config, availability=replace(r.config.availability, knowledge_cutoff_ns=24))
        rr = replace(r.result, metadata=replace(r.result.metadata, availability=cfg.availability, config_digest=cfg.digest))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.direction((replace(m[1], return_reference=replace(r, config=cfg, result=rr)),), c, u, s))
        rr = replace(r.result, metadata=replace(r.result.metadata, backend_version="old"))
        self.assertCode(ErrorCode.INCOMPATIBLE_VERSION, lambda: self.direction((replace(m[1], return_reference=replace(r, result=rr)),), c, u, s))
        ctx = replace(r.context, grid_version="v2")
        inp = tuple(replace(b, metadata=replace(b.metadata, source=replace(b.metadata.source, input_id=ctx.identity_digest))) if b.role == "history_context" else b for b in r.result.metadata.inputs)
        rr = replace(r.result, metadata=replace(r.result.metadata, inputs=inp))
        other = replace(m[1], return_reference=replace(r, context=ctx, result=rr))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.direction((m[0], other), c, u, s))

    def test_requested_family_ignores_unrequested_values(self):
        m, c, u, s = direction_setup()
        extra = sma_member("a", close=999)
        self.assertEqual(self.direction(m, c, u, s), self.direction((replace(m[0], sma=extra.sma, close=extra.close), *m[1:]), c, u, s))
        m, c, u, s = above_setup()
        ref, _ = reference("a", (100, None))
        self.assertEqual(self.above(m, c, u, s), self.above((replace(m[0], return_reference=ref), *m[1:]), c, u, s))

    def test_original_evidence_bounds_revision_and_membership_identity(self):
        m, c, u, s = above_setup()
        r = self.above(m, replace(c, parameters=(Parameter("period", 2), Parameter("evidence_limit", 1))), u, s)
        self.assertEqual(len(r.result.evidence), 1)
        self.assertEqual(r.result.evidence[0].entity, s.entity)
        self.assertEqual(r.result.evidence[0].row_id, "0")
        self.assertTrue(any(b.metadata.source.input_id == m[0].sma.identity_digest for b in r.result.metadata.inputs))
        revised = replace(m[0].close.source, metadata=replace(m[0].close.source.metadata, source=replace(m[0].close.source.metadata.source, snapshot_id="r2")))
        r1 = self.above(m, c, u, s)
        r2 = self.above((replace(m[0], close=replace(m[0].close, source=revised)), *m[1:]), c, u, s)
        self.assertEqual(r1.result.values, r2.result.values)
        self.assertNotEqual(r1.result.metadata.identity_digest, r2.result.metadata.identity_digest)
        r3 = self.above(m, c, replace(u, membership_identity="r2"), s)
        self.assertEqual(r1.result.values, r3.result.values)
        self.assertNotEqual(r1.result.metadata.identity_digest, r3.result.metadata.identity_digest)

    def test_supplied_conflicting_row_proof_rejected_with_output_limit_zero(self):
        m, c, u, s = above_setup()
        original = next(b for b in m[0].sma.reference.result.metadata.inputs if b.role == "daily_history")
        # Same original SMA row claims known20, contradictory target certificate known21.
        target = replace(m[0].close, source=original, known_at_ns=21)
        c = replace(c, parameters=(Parameter("period", 2), Parameter("evidence_limit", 0)))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.above((replace(m[0], close=target),), c, replace(u, members=("a",)), s))

    def test_same_original_sma_and_close_row_deduplicates_exactly(self):
        m, c, u, s = above_setup()
        source = next(b for b in m[0].sma.reference.result.metadata.inputs if b.role == "daily_history")
        target = replace(m[0].close, source=source)
        r = self.above((replace(m[0], close=target),), c, replace(u, members=("a",)), s)
        self.assertEqual(r.result.quality[0].status, Status.AVAILABLE)
        self.assertEqual(len(r.result.evidence), 2)
        self.assertEqual(len([b for b in r.result.metadata.inputs if b.metadata.source.input_id == source.metadata.source.input_id]), 1)

    def test_close_auction_inclusion_matches_actual_session(self):
        m, c, u, s = above_setup()
        for interval in (replace(m[0].close.interval, include_opening_auction=True), replace(m[0].close.interval, include_closing_auction=True)):
            self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.above((replace(m[0], close=replace(m[0].close, interval=interval)),), c, u, s))

    def test_future_completed_target_cannot_enter_eligible_population(self):
        m, c, u, s = above_setup()
        sm = m[0].sma
        cfg = replace(sm.config, availability=replace(sm.config.availability, market_cutoff_ns=18))
        _, b = reference("a", (9, 11))
        rebuilt = SMAInput(compute_sma_reference(b, cfg, context=sm.context), cfg, sm.context)
        r = self.above((replace(m[0], sma=rebuilt),), replace(c, availability=cfg.availability), replace(u, members=("a",)), s)
        self.assertEqual(r.result.quality[0].observed, 0)
        self.assertIsNone(r.result.values[0].values[0])
        self.assertIn(Reason.FUTURE_MARKET, r.exclusions[0].reasons)
        self.assertTrue(any(e.use == "excluded" and e.exclusion_reason == Reason.FUTURE_MARKET for e in r.result.evidence))

    def test_compatible_member_specific_action_revisions_and_policy_guard(self):
        from equity_feature_contracts import ActionPolicy, AdjustmentSpec, BatchMetadata, CanonicalBatch, Column, DataKind, ReturnReference
        from equity_features.history import compute_history
        from equity_features.policies import admit_action_policy
        members = []
        for name, prices in (("a", (100, 110)), ("b", (200, 190))):
            ref, batch = reference(name, prices)
            adjustment = AdjustmentSpec("split", "split-factors-v1", "actions-"+name, "S1")
            cfg = replace(ref.config, adjustment=adjustment)
            facts = CanonicalBatch(DataKind.REFERENCE, (Column("instrument_id", (name,)), Column("session_id", ("S1",)), Column("reference_id", ("split",)), Column("fact_kind", ("split_factor",)), Column("effective_start_ns", (11,)), Column("factor_num", (1,)), Column("factor_den", (2,)), Column("known_at_ns", (20,))), BatchMetadata("synthetic", SourceBinding("fixture", "actions-"+name, "v1", "actions-"+name), Coverage(1, 1, True), None))
            admission = admit_action_policy(facts, ActionPolicy(adjustment, 20, representation="caller_transformed"), cfg, entity=ref.context.entity)
            ctx = replace(ref.context, action_admission=admission)
            batch = replace(batch, metadata=replace(batch.metadata, adjustment=adjustment))
            r = ReturnReference(compute_history(batch, cfg, context=ctx, feature_ids=("history.return",)), cfg, ctx)
            members.append(MemberFeatures(ctx.entity, return_reference=r))
        cfg = replace(members[0].return_reference.config, identity="breadth")
        u = DeclaredUniverseSpec("synthetic", "S1", "U", "r1", 11, ("a", "b"))
        spec = BreadthSpec(EntityKey("U", "S1"))
        r = self.direction(tuple(members), cfg, u, spec)
        self.assertEqual(r.result.values[0].values[0], BreadthCounts(1, 1, 0, 2))
        self.assertEqual({b.metadata.source.snapshot_id for b in r.result.metadata.inputs if b.metadata.source.input_id in ("actions-a", "actions-b")}, {"actions-a", "actions-b"})
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.direction(tuple(members), replace(cfg, adjustment=AdjustmentSpec()), u, spec))

    def test_owned_schema_config_and_backend_modes(self):
        m, c, u, s = above_setup()
        with self.assertRaises(FrozenInstanceError):
            u.universe_id = "changed"
        for cfg in (replace(c, parameters=(Parameter("period", True),)), replace(c, window=replace(c.window, count=3))):
            self.assertCode(ErrorCode.INVALID_CONFIG, lambda: self.above(m, cfg, u, s))
        self.assertCode(ErrorCode.INVALID_SCHEMA, lambda: replace(m[0].close, row_index=2))
        self.assertCode(ErrorCode.BOUNDS, lambda: replace(m[0].close, coefficient=0))
        for fid in ("breadth.direction_counts", "breadth.above_sma_fraction"):
            self.assertTrue(builtin_registry().get(fid).capabilities.batch)
            for mode in ("update", "restore", "merge"):
                self.assertCode(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: builtin_registry().require_capability(fid, mode))

    def test_supplied_sma_proof_and_breadth_companion_guard(self):
        m, c, u, s = above_setup()
        sm = m[0].sma
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(sm, config=replace(sm.config, identity="wrong")))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(sm, context=replace(sm.context, grid_version="wrong")))
        self.assertCode(ErrorCode.INVALID_SCHEMA, lambda: replace(sm, reference=object()))
        r = self.above(m, c, u, s)
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: replace(r, exclusions=()))
        self.assertCode(ErrorCode.INCOMPATIBLE_VERSION, lambda: replace(r.exclusions[0], schema_version="2"))
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: self.above((replace(m[0], close=replace(m[0].close, source=replace(m[0].close.source, metadata=replace(m[0].close.source.metadata, price_unit=PriceUnit(1, "USD"))))),), c, u, s))

    def test_aggregate_spec_identity_is_bound_separately_from_universe(self):
        m, c, u, s = direction_setup()
        r = self.direction(m, c, u, s)
        other = self.direction(m, c, u, BreadthSpec(EntityKey("other-aggregate", "S1")))
        self.assertEqual(r.result.values[0].values, other.result.values[0].values)
        self.assertNotEqual(r.result.metadata.identity_digest, other.result.metadata.identity_digest)
        self.assertTrue(any(b.metadata.source.input_id == s.identity_digest for b in r.result.metadata.inputs))

    def test_future_history_rows_do_not_change_admitted_breadth(self):
        r1, _ = reference("a", (100, 110, 999), target=1)
        r2, _ = reference("a", (100, 110, 1), target=1)
        c = replace(r1.config, identity="breadth")
        u = DeclaredUniverseSpec("synthetic", "S1", "U", "r1", 11, ("a",))
        spec = BreadthSpec(EntityKey("U", "S1"))
        self.assertEqual(self.direction((MemberFeatures(r1.context.entity, r1),), c, u, spec), self.direction((MemberFeatures(r2.context.entity, r2),), c, u, spec))


if __name__ == "__main__":
    unittest.main()
