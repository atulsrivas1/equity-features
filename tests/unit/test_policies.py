"""Independent rational/cutoff fixtures for the public supplied policy APIs."""
from dataclasses import FrozenInstanceError, replace
from fractions import Fraction
import unittest

from equity_feature_contracts import (
    ActionPolicy, AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch,
    ClassificationAdmission, Column, ConfigSpec, ContractError, Coverage, DataKind,
    EntityKey, ErrorCode, PriceUnit, Reason, ReferenceFact, SessionSpec, SourceBinding,
    Status, WindowSpec,
)
from equity_features.policies import admit_action_policy, admit_classification, apply_action_policy

UNIT = PriceUnit(2, "USD")
ENTITY = EntityKey("A", "S2")


def policy(basis="split", **kwargs):
    versions = {"raw": "raw-v1", "split": "split-factors-v1", "total_return": "total-return-reinvest-v1"}
    adjustment = AdjustmentSpec() if basis == "raw" else AdjustmentSpec(basis, versions[basis], "actions-r1", "S2")
    values = dict(adjustment=adjustment, anchor_ns=200, quantity_basis="split_shares" if basis != "raw" else "raw_shares",
                  dividend_convention="supplied_reinvestment_factors" if basis == "total_return" else "none")
    values.update(kwargs)
    return ActionPolicy(**values)


def config(p, **kwargs):
    values = dict(identity="actions", algorithm_version="v1", parameters=(),
                  session=SessionSpec("synthetic", "S2", 100, 200, "supplied"),
                  window=WindowSpec(2, "S2", ("S0", "S1", "S2"), "completed_eod"),
                  availability=AvailabilitySpec(200, 210, 210), adjustment=p.adjustment, price_unit=UNIT)
    values.update(kwargs)
    return ConfigSpec(**values)


def reference(rows=None, **metadata):
    # Rows are manually supplied, not generated from production selection logic.
    if rows is None:
        rows = [dict(reference_id="split", fact_kind="split_factor", effective_start_ns=100,
                     factor_num=1, factor_den=2, known_at_ns=210)]
    names = ("instrument_id", "session_id", "reference_id", "fact_kind", "effective_start_ns",
             "effective_end_ns", "factor_num", "factor_den", "text", "known_at_ns")
    values = dict(namespace="synthetic", source=SourceBinding("fixture", "actions-r1", "v1", "actions"),
                  coverage=Coverage(len(rows), len(rows), True), price_unit=None)
    values.update(metadata)
    columns = tuple(Column(name, tuple(row.get(name, "A" if name == "instrument_id" else "S2" if name == "session_id" else None)
                                       for row in rows)) for name in names)
    return CanonicalBatch(DataKind.REFERENCE, columns, BatchMetadata(**values))


def market(kind=DataKind.DAILY, **fields):
    values = dict(instrument_id=("A", "A"), session_id=("S1", "S2"), known_at_ns=(210, 210))
    if kind in (DataKind.DAILY, DataKind.BAR):
        values.update(start_ns=(0, 100), end_ns=(100, 200), open=(10000, 5000), high=(10000, 5000),
                      low=(10000, 5000), close=(10000, 5000), volume=(10, 20), trade_count=(3, 4),
                      actual_notional=(100000, 100000))
    elif kind in (DataKind.TRADE, DataKind.QUOTE):
        values.update(event_ns=(99, 100), order_key=(0, 1), event_id=("a", "b"))
        if kind == DataKind.TRADE:
            values.update(eligible=(True, True), price=(10000, 5000), size=(10, 20))
        else:
            values.update(bid=(10000, 5000), ask=(10002, 5001), bid_size=(10, 20), ask_size=(12, 24))
    else:
        values.update(reference_id=("prior1", "prior2"), fact_kind=("prior_close", "prior_close"),
                      effective_start_ns=(99, 100), price=(10000, 5000))
    values.update(fields)
    count = len(values["instrument_id"])
    return CanonicalBatch(kind, tuple(Column(name, val) for name, val in values.items()),
                          BatchMetadata("synthetic", SourceBinding("fixture", "prices-r1", "v1", "prices"),
                                        Coverage(count, count, True), UNIT,
                                        sampling="trade_snapshot" if kind == DataKind.QUOTE else "none"))


def field(batch, name):
    return batch.column(name).values


class SuppliedPolicy(unittest.TestCase):
    def assertCode(self, code, call):
        with self.assertRaises(ContractError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)

    def apply(self, batch=None, refs=None, p=None, cfg=None):
        p = p or policy()
        return apply_action_policy(batch or market(), reference() if refs is None else refs,
                                   p, cfg or config(p), entity=ENTITY)

    def test_split_price_share_reciprocity_and_immutable_notional(self):
        b = market(); before = b
        result = self.apply(b)
        self.assertEqual(result.status, Status.AVAILABLE)
        self.assertEqual(field(result.batch, "close"), (5000, 5000))
        self.assertEqual(field(result.batch, "volume"), (20, 20))
        self.assertEqual(field(result.batch, "actual_notional"), (100000, 100000))
        self.assertEqual(field(result.batch, "trade_count"), (3, 4))
        self.assertEqual(result.original_input.metadata, before.metadata)
        self.assertEqual(field(b, "close"), (10000, 5000))
        self.assertEqual(result.batch.metadata.adjustment, policy().adjustment)
        self.assertNotEqual(result.batch.metadata.source.input_id, b.metadata.source.input_id)
        self.assertEqual(result.admission.facts[0].row_index, 0)
        self.assertEqual(result.admission.facts[0].known_at_ns, 210)

    def test_raw_shares_and_exact_adjusted_notional(self):
        p = policy(quantity_basis="raw_shares")
        result = self.apply(p=p)
        self.assertEqual(field(result.batch, "close"), (5000, 5000))
        self.assertEqual(field(result.batch, "volume"), (10, 20))
        self.assertEqual(field(result.batch, "actual_notional"), (50000, 100000))
        self.assertEqual(result.admission.policy.quantity_basis, "raw_shares")

    def test_multiple_factors_compound_exactly(self):
        rows = [dict(reference_id="a", fact_kind="split_factor", effective_start_ns=100, factor_num=1, factor_den=2, known_at_ns=210),
                dict(reference_id="b", fact_kind="split_factor", effective_start_ns=200, factor_num=1, factor_den=5, known_at_ns=210)]
        result = self.apply(refs=reference(rows))
        self.assertEqual(field(result.batch, "close"), (1000, 1000))
        self.assertEqual(field(result.batch, "volume"), (100, 100))
        self.assertEqual(field(result.batch, "actual_notional"), (100000, 100000))

    def test_total_return_dividend_factor_without_quantity_or_duplicate_cash(self):
        p = policy("total_return", quantity_basis="raw_shares")
        rows = [dict(reference_id="div", fact_kind="dividend_factor", effective_start_ns=100, factor_num=99, factor_den=100, known_at_ns=210)]
        b = market(open=(10000, 9900), high=(10000, 9900), low=(10000, 9900), close=(10000, 9900),
                   actual_notional=(100000, 198000))
        result = self.apply(b, reference(rows), p)
        self.assertEqual(field(result.batch, "close"), (9900, 9900))
        self.assertEqual(field(result.batch, "volume"), (10, 20))
        self.assertEqual(field(result.batch, "actual_notional"), (99000, 198000))
        self.assertEqual(Fraction(9900, 9900) - 1, 0)
        self.assertEqual(Fraction(9900, 10000) - 1, Fraction(-1, 100))
        # Split basis deliberately excludes dividend knowledge and arithmetic.
        result_split = self.apply(b, reference(rows))
        self.assertEqual(field(result_split.batch, "close"), (10000, 9900))

    def test_combined_split_and_dividend_does_not_adjust_shares_by_dividend(self):
        rows = [dict(reference_id="div", fact_kind="dividend_factor", effective_start_ns=100, factor_num=99, factor_den=100, known_at_ns=210),
                dict(reference_id="split", fact_kind="split_factor", effective_start_ns=100, factor_num=1, factor_den=2, known_at_ns=210)]
        result = self.apply(refs=reference(rows), p=policy("total_return"))
        self.assertEqual(field(result.batch, "close"), (4950, 5000))
        self.assertEqual(field(result.batch, "volume"), (20, 20))
        self.assertEqual(field(result.batch, "actual_notional"), (99000, 100000))

    def test_caller_transformed_never_applies_again(self):
        initial = self.apply()
        p = policy(representation="caller_transformed")
        result = self.apply(initial.batch, p=p)
        self.assertIs(result.batch, initial.batch)
        self.assertEqual(field(result.batch, "close"), (5000, 5000))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.apply(initial.batch))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.apply(p=p))

    def test_raw_policy_requires_no_action_evidence(self):
        p = policy("raw"); b = market()
        result = apply_action_policy(b, None, p, config(p), entity=ENTITY)
        self.assertIs(result.batch, b)
        self.assertEqual(result.admission.facts, ())
        self.assertEqual(result.status, Status.AVAILABLE)

    def test_empty_complete_adjusted_snapshot_is_available(self):
        result = self.apply(refs=reference([]))
        self.assertEqual(result.status, Status.AVAILABLE)
        self.assertEqual(field(result.batch, "close"), (10000, 5000))

    def test_missing_and_incomplete_action_evidence(self):
        p = policy()
        result = admit_action_policy(None, p, config(p), entity=ENTITY)
        self.assertEqual(result.status, Status.MISSING_INPUT)
        self.assertIn(Reason.MISSING_ACTION_EVIDENCE, result.reasons)
        result = self.apply(refs=reference(coverage=Coverage(2, 1, False)))
        self.assertEqual(result.status, Status.INCOMPLETE_COVERAGE)
        self.assertIsNone(result.batch)

    def test_null_factor_operands_are_unavailable(self):
        for operand in ("factor_num", "factor_den"):
            row = dict(reference_id="split", fact_kind="split_factor", effective_start_ns=100, factor_num=1, factor_den=2, known_at_ns=210)
            row[operand] = None
            result = self.apply(refs=reference([row]))
            self.assertEqual(result.status, Status.MISSING_INPUT)
            self.assertIn(Reason.NULL_FIELD, result.reasons)
            self.assertIsNone(result.batch)

    def test_action_unknown_later_and_equal_knowledge(self):
        for known, status, reason in ((None, Status.MISSING_INPUT, Reason.UNKNOWN_AVAILABILITY),
                                      (211, Status.MISSING_INPUT, Reason.FUTURE_KNOWLEDGE),
                                      (210, Status.AVAILABLE, None)):
            ref = reference([dict(reference_id="split", fact_kind="split_factor", effective_start_ns=100,
                                  factor_num=1, factor_den=2, known_at_ns=known)])
            result = self.apply(refs=ref)
            self.assertEqual(result.status, status)
            if reason:
                self.assertIn(reason, result.reasons)
            self.assertEqual(result.admission.facts[0].known_at_ns, known)

    def test_reconstruction_retains_original_knowledge_and_identity(self):
        p = policy()
        ref = reference([dict(reference_id="split", fact_kind="split_factor", effective_start_ns=100,
                              factor_num=1, factor_den=2, known_at_ns=None)])
        causal = self.apply(refs=ref)
        recon_config = config(p, availability=AvailabilitySpec(200, 300, 200, "reconstruction", "later revision"))
        result = self.apply(refs=ref, cfg=recon_config)
        self.assertEqual(result.status, Status.AVAILABLE)
        self.assertIsNone(result.admission.facts[0].known_at_ns)
        self.assertEqual(result.admission.availability.mode, "reconstruction")
        self.assertNotEqual(result.admission.identity_digest, causal.admission.identity_digest)

    def test_future_actions_do_not_affect_readiness_or_values(self):
        base = self.apply()
        for kind, known, num in (("split_factor", None, 1), ("unknown_factor", 999, 3)):
            row = dict(reference_id="future", fact_kind=kind, effective_start_ns=201, factor_num=num, factor_den=7, known_at_ns=known)
            rows = [dict(reference_id="split", fact_kind="split_factor", effective_start_ns=100, factor_num=1, factor_den=2, known_at_ns=210), row]
            result = self.apply(refs=reference(rows))
            self.assertEqual(field(result.batch, "close"), field(base.batch, "close"))
            self.assertEqual(result.admission.facts, base.admission.facts)
            self.assertEqual(result.status, Status.AVAILABLE)

    def test_anchor_equality_and_event_effective_boundary(self):
        result = self.apply(market(DataKind.TRADE))
        self.assertEqual(field(result.batch, "price"), (5000, 5000))
        self.assertEqual(field(result.batch, "size"), (20, 20))
        p = policy(anchor_ns=99)
        result = self.apply(p=p)
        self.assertEqual(field(result.batch, "close"), (10000, 5000))
        self.assertCode(ErrorCode.BOUNDS, lambda: self.apply(p=policy(anchor_ns=201)))

    def test_crossing_action_interval_rejected(self):
        b = market(start_ns=(0, 100), end_ns=(101, 200))
        # Use a BAR to avoid overlap; one spanning interval is already sufficient.
        b = replace(b, kind=DataKind.BAR, columns=tuple(Column(c.name, c.values[:1]) for c in b.columns),
                    metadata=replace(b.metadata, coverage=Coverage(1, 1, True)))
        self.assertCode(ErrorCode.BOUNDS, lambda: self.apply(b))

    def test_quote_and_reference_price_fields(self):
        result = self.apply(market(DataKind.QUOTE))
        self.assertEqual(field(result.batch, "bid"), (5000, 5000))
        self.assertEqual(field(result.batch, "ask"), (5001, 5001))
        self.assertEqual(field(result.batch, "bid_size"), (20, 20))
        self.assertEqual(field(result.batch, "ask_size"), (24, 24))
        result = self.apply(market(DataKind.REFERENCE))
        self.assertEqual(field(result.batch, "price"), (5000, 5000))

    def test_all_ohlc_fields_same_factor(self):
        b = market(open=(10000, 5000), high=(12000, 6000), low=(8000, 4000), close=(11000, 5500))
        result = self.apply(b)
        for name, expected in (("open", (5000, 5000)), ("high", (6000, 6000)),
                               ("low", (4000, 4000)), ("close", (5500, 5500))):
            self.assertEqual(field(result.batch, name), expected)

    def test_absent_and_null_fields_preserved(self):
        b = market(close=(None, 5000), volume=(None, 20), actual_notional=(None, 100000))
        b = replace(b, columns=tuple(c for c in b.columns if c.name not in ("open", "high", "low")))
        result = self.apply(b)
        self.assertEqual(field(result.batch, "close"), (None, 5000))
        self.assertIsNone(result.batch.column("open"))
        self.assertEqual(field(result.batch, "volume"), (None, 20))

    def test_nonintegral_price_share_or_notional_rejected_without_mutation(self):
        for b in (market(close=(10001, 5000)),):
            # Keep independent OHLC coherent for this deliberately odd coefficient.
            b = replace(b, columns=tuple(c for c in b.columns if c.name not in ("open", "high", "low", "actual_notional")))
            before = b
            self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.apply(b))
            self.assertEqual(b, before)
        ref = reference([dict(reference_id="reverse", fact_kind="split_factor", effective_start_ns=100,
                              factor_num=2, factor_den=1, known_at_ns=210)])
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.apply(market(volume=(11, 20), actual_notional=(110000, 100000)), ref))
        # p'=p/2 is integral, but supplied actual_notional/2 is not for raw shares.
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.apply(market(high=(10002, 5000), actual_notional=(100001, 100000)),
                                                                          p=policy(quantity_basis="raw_shares")))

    def test_price_quantity_and_decimal_overflow_rejected(self):
        maximum = 2**63 - 1
        b = market(volume=(maximum, 20), actual_notional=(None, 100000))
        self.assertCode(ErrorCode.OVERFLOW, lambda: self.apply(b))
        ref = reference([dict(reference_id="reverse", fact_kind="split_factor", effective_start_ns=100,
                              factor_num=2, factor_den=1, known_at_ns=210)])
        b = market(close=(maximum, 5000), volume=(None, 20), actual_notional=(None, 100000))
        b = replace(b, columns=tuple(c for c in b.columns if c.name not in ("open", "high", "low")))
        self.assertCode(ErrorCode.OVERFLOW, lambda: self.apply(b, ref))
        b = market(actual_notional=(10**38-1, 100000), volume=(None, 20))
        self.assertCode(ErrorCode.OVERFLOW, lambda: self.apply(b, ref, p=policy(quantity_basis="raw_shares")))

    def test_wide_transient_products_do_not_overflow_before_reduction(self):
        maximum = 2**63 - 1
        ref = reference([dict(reference_id="wide", fact_kind="split_factor", effective_start_ns=100,
                              factor_num=maximum, factor_den=maximum, known_at_ns=210)])
        result = self.apply(refs=ref)
        self.assertEqual(field(result.batch, "close"), (10000, 5000))

    def test_market_readiness_does_not_change_action_readiness(self):
        for known, reason in ((None, Reason.UNKNOWN_AVAILABILITY), (211, Reason.FUTURE_KNOWLEDGE)):
            result = self.apply(market(known_at_ns=(known, 210)))
            self.assertEqual(result.admission.status, Status.AVAILABLE)
            self.assertEqual(result.status, Status.MISSING_INPUT)
            self.assertIn(reason, result.reasons)
            self.assertIsNone(result.batch)
        b = market(); b = replace(b, metadata=replace(b.metadata, coverage=Coverage(3, 2, False)))
        self.assertEqual(self.apply(b).status, Status.INCOMPLETE_COVERAGE)

    def test_future_market_rows_not_consumed(self):
        self.assertCode(ErrorCode.BOUNDS, lambda: self.apply(market(end_ns=(100, 201))))
        self.assertCode(ErrorCode.BOUNDS, lambda: self.apply(market(DataKind.TRADE, event_ns=(99, 200))))
        self.assertCode(ErrorCode.BOUNDS, lambda: self.apply(market(DataKind.REFERENCE, effective_start_ns=(99, 201))))

    def test_source_policy_and_config_revisions_change_identity(self):
        initial = self.apply()
        b = market(); b = replace(b, metadata=replace(b.metadata, source=replace(b.metadata.source, snapshot_id="prices-r2")))
        changed_price = self.apply(b)
        self.assertNotEqual(changed_price.batch.metadata.source.input_id, initial.batch.metadata.source.input_id)
        ref = reference(source=SourceBinding("fixture", "actions-r2", "v1", "actions"))
        p = policy(adjustment=replace(policy().adjustment, action_snapshot="actions-r2"))
        changed_ref = self.apply(refs=ref, p=p)
        self.assertNotEqual(changed_ref.admission.identity_digest, initial.admission.identity_digest)
        self.assertNotEqual(changed_ref.batch.metadata.source.input_id, initial.batch.metadata.source.input_id)
        changed_cfg = self.apply(cfg=replace(config(policy()), identity="other"))
        self.assertNotEqual(changed_cfg.batch.metadata.source.input_id, initial.batch.metadata.source.input_id)

    def test_unknown_policy_or_conventions_fail_explicitly(self):
        for kwargs in (dict(adjustment=replace(policy().adjustment, policy_version="unknown")),
                       dict(representation="guess"), dict(quantity_basis="contracts"),
                       dict(dividend_convention="cash-added")):
            self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: policy(**kwargs))
        self.assertCode(ErrorCode.INCOMPATIBLE_VERSION, lambda: policy(schema_version="2"))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: policy("total_return", dividend_convention="none"))
        self.assertCode(ErrorCode.BOUNDS, lambda: policy(anchor_ns=True))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: policy("raw", quantity_basis="split_shares"))

    def test_incompatible_namespace_unit_snapshot_basis_and_entity(self):
        b = market()
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.apply(replace(b, metadata=replace(b.metadata, namespace="other"))))
        self.assertCode(ErrorCode.INVALID_UNIT, lambda: self.apply(replace(b, metadata=replace(b.metadata, price_unit=PriceUnit(3, "USD")))))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.apply(refs=reference(source=SourceBinding("fixture", "wrong", "v1", "actions"))))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.apply(cfg=replace(config(policy()), adjustment=AdjustmentSpec())))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.apply(market(instrument_id=("B", "A"))))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.apply(market(session_id=("unknown", "S2"))))

    def test_malformed_reference_unknown_kind_duplicates_and_order(self):
        row = dict(reference_id="split", fact_kind="split_factor", effective_start_ns=100,
                   factor_num=1, factor_den=2, known_at_ns=210)
        self.assertCode(ErrorCode.DUPLICATE, lambda: self.apply(refs=reference([row, dict(row)])))
        self.assertCode(ErrorCode.DUPLICATE, lambda: self.apply(refs=reference([row, dict(row, session_id="different")])) )
        self.assertCode(ErrorCode.INVALID_ORDER, lambda: self.apply(refs=reference([dict(row, reference_id="a", effective_start_ns=101),
                                                                                 dict(row, reference_id="b", effective_start_ns=100)])))
        for name in ("stock_split", "unknown_factor"):
            self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.apply(refs=reference([dict(row, fact_kind=name)])))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.apply(refs=reference([dict(row, factor_num=0)])))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: self.apply(refs=reference([dict(row, effective_end_ns=150)])))

    def test_other_instruments_are_independent(self):
        row = dict(instrument_id="B", reference_id="split", fact_kind="split_factor", effective_start_ns=100,
                   factor_num=1, factor_den=2, known_at_ns=None)
        result = self.apply(refs=reference([row]))
        self.assertEqual(result.status, Status.AVAILABLE)
        self.assertEqual(result.admission.facts, ())

    def test_bar_and_zero_observation_fields_preserved(self):
        result = self.apply(market(DataKind.BAR))
        self.assertEqual(field(result.batch, "close"), (5000, 5000))
        b = market(open=(None, 5000), high=(None, 5000), low=(None, 5000), close=(None, 5000),
                   volume=(0, 20), trade_count=(0, 4), actual_notional=(0, 100000))
        result = self.apply(b)
        self.assertEqual(field(result.batch, "volume"), (0, 20))
        self.assertEqual(field(result.batch, "actual_notional"), (0, 100000))
        self.assertEqual(field(result.batch, "close"), (None, 5000))

    def test_supplied_target_session_and_algorithm_are_enforced(self):
        p = policy()
        self.assertCode(ErrorCode.BOUNDS, lambda: self.apply(cfg=config(p, availability=AvailabilitySpec(201, 210, 210))))
        self.assertCode(ErrorCode.BOUNDS, lambda: self.apply(market(start_ns=(0, 99), end_ns=(99, 200))))
        self.assertCode(ErrorCode.BOUNDS, lambda: self.apply(market(DataKind.TRADE, event_ns=(98, 99))))
        self.assertCode(ErrorCode.INCOMPATIBLE_VERSION, lambda: self.apply(cfg=config(p, algorithm_version="unknown")))

    def test_policy_admission_and_application_cannot_forge_basis_or_readiness(self):
        result = self.apply()
        self.assertCode(ErrorCode.INVALID_SCHEMA, lambda: replace(result.admission, reference=None, facts=()))
        self.assertCode(ErrorCode.UNSUPPORTED_ADJUSTMENT,
                        lambda: replace(result.admission, facts=(replace(result.admission.facts[0], fact_kind="dividend_factor"),)))
        self.assertCode(ErrorCode.INVALID_SCHEMA, lambda: replace(result, batch=None))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY,
                        lambda: replace(result, batch=replace(result.batch, metadata=replace(result.batch.metadata, price_unit=PriceUnit(3, "USD")))))

    def test_raw_context_and_reconstruction_market_knowledge_are_preserved(self):
        raw = AdjustmentSpec("raw", "raw-v1", "supplied-context", "S2")
        p = policy("raw", adjustment=raw)
        b = market(); b = replace(b, metadata=replace(b.metadata, adjustment=raw))
        self.assertIs(self.apply(b, p=p).batch, b)
        p = policy(); b = market(known_at_ns=(None, 211))
        cfg = config(p, availability=AvailabilitySpec(200, 300, 200, "reconstruction", "audit"))
        result = self.apply(b, cfg=cfg)
        self.assertEqual(result.status, Status.AVAILABLE)
        self.assertEqual(field(result.batch, "known_at_ns"), (None, 211))

    def test_contradictory_market_or_reference_observed_counts_rejected(self):
        b = market(); b = replace(b, metadata=replace(b.metadata, coverage=Coverage(1, 1, True)))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.apply(b))
        ref = reference(coverage=Coverage(0, 0, True))
        self.assertCode(ErrorCode.INCONSISTENT_IDENTITY, lambda: self.apply(refs=ref))

    def test_reference_evidence_indices_cannot_exceed_bound_population(self):
        result = self.apply()
        self.assertCode(ErrorCode.BOUNDS,
                        lambda: replace(result.admission, facts=(replace(result.admission.facts[0], row_index=1),)))


class ClassificationPolicy(unittest.TestCase):
    def admit(self, ref=None, effective=100, kind="sector_membership", cfg=None):
        return admit_classification(ref, cfg or config(policy()), entity=ENTITY, effective_ns=effective, fact_kind=kind)

    def row(self, **kwargs):
        row = dict(reference_id="sector", fact_kind="sector_membership", effective_start_ns=100,
                   effective_end_ns=200, known_at_ns=210, text="sector-a")
        row.update(kwargs)
        return row

    def test_membership_half_open_equality(self):
        ref = reference([self.row()])
        self.assertEqual(self.admit(ref, 99).status, Status.MISSING_INPUT)
        result = self.admit(ref, 100)
        self.assertEqual(result.status, Status.AVAILABLE)
        self.assertEqual(result.text, "sector-a")
        self.assertEqual(result.facts[0].effective_end_ns, 200)
        self.assertEqual(self.admit(ref, 199).text, "sector-a")
        self.assertEqual(self.admit(ref, 200).status, Status.MISSING_INPUT)

    def test_adjacent_membership_changes_without_overlap(self):
        rows = [self.row(reference_id="a", effective_start_ns=0, effective_end_ns=100, text="old"),
                self.row(reference_id="b", text="new")]
        self.assertEqual(self.admit(reference(rows), 99).text, "old")
        self.assertEqual(self.admit(reference(rows), 100).text, "new")

    def test_sector_and_universe_are_independent_of_action_fields(self):
        rows = [self.row(), self.row(reference_id="split", fact_kind="split_factor", effective_end_ns=None,
                                   known_at_ns=None, text=None),
                self.row(reference_id="universe", fact_kind="universe_membership", text="universe-a")]
        ref = reference(rows)
        self.assertEqual(self.admit(ref).text, "sector-a")
        self.assertEqual(self.admit(ref, kind="universe_membership").text, "universe-a")
        self.assertEqual(admit_action_policy(ref, policy(), config(policy()), entity=ENTITY).status, Status.MISSING_INPUT)

    def test_missing_null_unknown_and_future_reference(self):
        self.assertEqual(self.admit().status, Status.MISSING_INPUT)
        for row, reason in ((self.row(text=None), Reason.NULL_FIELD),
                            (self.row(known_at_ns=None), Reason.UNKNOWN_AVAILABILITY),
                            (self.row(known_at_ns=211), Reason.FUTURE_KNOWLEDGE)):
            result = self.admit(reference([row]))
            self.assertEqual(result.status, Status.MISSING_INPUT)
            self.assertIn(reason, result.reasons)
            self.assertIsNone(result.text)

    def test_reconstruction_and_future_mutation(self):
        ref = reference([self.row(known_at_ns=None)])
        cfg = config(policy(), availability=AvailabilitySpec(200, 300, 200, "reconstruction", "audit"))
        result = self.admit(ref, cfg=cfg)
        self.assertEqual(result.text, "sector-a")
        self.assertIsNone(result.facts[0].known_at_ns)
        ref = reference([self.row(), self.row(reference_id="future", effective_start_ns=200,
                                             effective_end_ns=300, known_at_ns=None, text="future")])
        self.assertEqual(self.admit(ref).text, "sector-a")

    def test_overlapping_even_equal_memberships_error(self):
        rows = [self.row(reference_id="a"), self.row(reference_id="b", known_at_ns=999)]
        with self.assertRaises(ContractError) as caught:
            self.admit(reference(rows))
        self.assertEqual(caught.exception.code, ErrorCode.DUPLICATE)

    def test_incomplete_classification_coverage(self):
        result = self.admit(reference([self.row()], coverage=Coverage(2, 1, False)))
        self.assertEqual(result.status, Status.INCOMPLETE_COVERAGE)
        self.assertIsNone(result.text)

    def test_typed_contracts_detach_and_reject_forged_readiness(self):
        admission = self.admit(reference([self.row()]))
        facts = list(admission.facts)
        detached = replace(admission, facts=facts)
        facts.clear()
        self.assertEqual(len(detached.facts), 1)
        with self.assertRaises(FrozenInstanceError):
            detached.effective_ns = 0
        for kwargs in (dict(status=Status.AVAILABLE, facts=()), dict(reasons=(Reason.ABSENT_INPUT,)),
                       dict(facts=(replace(admission.facts[0], known_at_ns=211),))):
            with self.assertRaises(ContractError):
                replace(admission, **kwargs)
        with self.assertRaises(ContractError):
            self.admit(reference([self.row()]), effective=201)
        with self.assertRaises(ContractError):
            self.admit(reference([self.row()]), kind="guessed")


if __name__ == "__main__":
    unittest.main()
