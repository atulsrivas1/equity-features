"""Original A01–03/B01 arithmetic and boundary fixtures; no producer-generated oracle."""
from dataclasses import replace
import hashlib
import json
from types import MappingProxyType
import unittest

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column,
    ContractError, Coverage, DataKind, EntityKey, ErrorCode, InputScope, Parameter,
    PriceUnit, Reason, SessionSpec, SourceBinding, Status, ValueType, WindowSpec,
    builtin_registry,
)
from equity_features import __version__, contracts_version
from equity_features.ef1 import build_ef1_config, compute_ef1, decode_ef1_context, ef1_definitions

ENTITY = EntityKey("X", "S")
UNIT = PriceUnit(2, "USD")
DEFINITION = {"anchor_id": "A", "reset_id": "R", "start_ns": 10,
              "selection_policy_id": "supplied-v1", "revision": "R1"}


def context(mode="trades", **definition_changes):
    return {"version": "ef1-context1", "producer": "anchor", "calendar": None,
            "selection": {"mode": mode, "definition": {**DEFINITION, **definition_changes}}}


def config(mode="trades", *, cutoff=20, knowledge=20, selection=None, session=None):
    return build_ef1_config(context(mode) if selection is None else selection,
                            session=SessionSpec("SYN", "S", 10, 30, "UTC") if session is None else session,
                            window=WindowSpec(1, "S", ("S",), "completed_eod"),
                            availability=AvailabilitySpec(cutoff, knowledge, max(cutoff, knowledge)),
                            price_unit=UNIT, adjustment=AdjustmentSpec())


def market(kind=DataKind.TRADE, *, data=None, cutoff=20, complete=True):
    if data is None:
        data = ({"event_ns": (10, 15), "order_key": (0, 1), "event_id": ("a", "b"),
                 "eligible": (True, True), "price": (1000, 1300), "size": (2, 1),
                 "known_at_ns": (10, 15)} if kind == DataKind.TRADE else
                {"start_ns": (10,), "end_ns": (20,), "open": (1000,), "high": (1300,),
                 "low": (1000,), "close": (1300,), "volume": (3,),
                 "actual_notional": (3300,), "known_at_ns": (20,)})
    n = len(next(iter(data.values())))
    columns = {"instrument_id": ("X",) * n, "session_id": ("S",) * n, **data}
    metadata = BatchMetadata("SYN", SourceBinding("F", "R1", "market-v1", "mk"),
                             Coverage(n if complete else n + 1, n, complete), UNIT,
                             scope=InputScope(10, cutoff, "eligible-v1"))
    return CanonicalBatch(kind, tuple(Column(k, v) for k, v in columns.items()), metadata)


def proof(*, definition=None, known_at=10, end=None, input_id="ap", complete=True):
    definition = DEFINITION if definition is None else definition
    # Independent specification hash; no imports of the producer's hashing helper.
    text = json.dumps(definition, sort_keys=True, ensure_ascii=True, separators=(",", ":"), allow_nan=False)
    data = {"instrument_id": ("X",), "session_id": ("S",),
            "reference_id": ("a1:" + hashlib.sha256(text.encode("ascii")).hexdigest(),),
            "fact_kind": ("ef1.anchor.provenance",), "effective_start_ns": (definition["start_ns"],),
            "effective_end_ns": (end,), "text": ("supplied_anchor",), "known_at_ns": (known_at,)}
    meta = BatchMetadata("SYN", SourceBinding("F", definition["revision"], "ef1-reference-map1", input_id),
                         Coverage(1 if complete else 2, 1, complete), None)
    return CanonicalBatch(DataKind.REFERENCE, tuple(Column(k, v) for k, v in data.items()), meta)


def changed(batch, **columns):
    values = {c.name: c.values for c in batch.columns}
    for name, value in columns.items():
        if value is None:
            values.pop(name, None)
        else:
            values[name] = value
    return replace(batch, columns=tuple(Column(k, v) for k, v in values.items()))


def view(result):
    return {c.feature_id.rsplit(".", 1)[1]: c.values[0] for c in result.values}


def quality(result):
    return {q.feature_id.rsplit(".", 1)[1]: q for q in result.quality}


class EF1Anchors(unittest.TestCase):
    def error(self, expected, call):
        with self.assertRaises(ContractError) as caught:
            call()
        self.assertEqual(caught.exception.code, expected)

    def test_a01_independent_trade_arithmetic_and_full_identity(self):
        c, m, p = config(), market(), proof()
        result = compute_ef1((m, p), c, entity=ENTITY)
        # (1000*2+1300*1)/100 = USD33, shares3 => USD11/share.
        self.assertEqual(view(result), {"notional": 3300, "volume": 3, "vwap": 11.0})
        self.assertTrue(all(q.status == Status.AVAILABLE and not q.reasons for q in result.quality))
        self.assertTrue(all((q.expected, q.observed) == (2, 2) for q in result.quality))
        self.assertEqual(result.metadata.config_digest, c.digest)
        self.assertEqual(result.metadata.availability, c.availability)
        self.assertEqual({b.role: b.metadata for b in result.metadata.inputs},
                         {"trades": m.metadata, "anchor_provenance": p.metadata})
        self.assertEqual((result.metadata.backend_id, result.metadata.backend_version),
                         ("python-exact", "0.0.4a5"))
        self.assertEqual(result.evidence, ())

    def test_a01_actual_notional_bars_and_proxy_counterexample(self):
        result = compute_ef1((market(DataKind.BAR), proof()), config("bars_actual_notional"), entity=ENTITY)
        self.assertEqual(view(result), {"notional": 3300, "volume": 3, "vwap": 11.0})
        self.assertNotEqual(view(result)["notional"], 1300 * 3)
        self.assertEqual({c.feature_id: (c.dtype, c.unit) for c in result.values}, {
            "session.anchor.notional": (ValueType.DECIMAL128, "currency"),
            "session.anchor.volume": (ValueType.INT64, "shares"),
            "session.anchor.vwap": (ValueType.FLOAT64, "currency/share")})

    def test_missing_actual_notional_preserves_volume(self):
        for value, reason in ((None, Reason.ABSENT_INPUT), ((None,), Reason.NULL_FIELD)):
            m = changed(market(DataKind.BAR), actual_notional=value)
            result = compute_ef1((m, proof()), config("bars_actual_notional"), entity=ENTITY)
            self.assertEqual(view(result), {"notional": None, "volume": 3, "vwap": None})
            self.assertEqual(quality(result)["volume"].status, Status.AVAILABLE)
            self.assertEqual(quality(result)["notional"].reasons, (reason,))

    def test_lib01_actual_notional_admission_is_independent_of_optional_ohlc(self):
        without_ohlc = changed(market(DataKind.BAR), open=None, high=None, low=None, close=None)
        for invalid in (-1, 0):
            self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(
                (changed(without_ohlc, actual_notional=(invalid,)), proof()),
                config("bars_actual_notional"), entity=ENTITY))
        result = compute_ef1((without_ohlc, proof()), config("bars_actual_notional"), entity=ENTITY)
        self.assertEqual(view(result), {"notional": 3300, "volume": 3, "vwap": 11.0})
        missing = compute_ef1((changed(without_ohlc, actual_notional=(None,)), proof()),
                              config("bars_actual_notional"), entity=ENTITY)
        self.assertEqual(view(missing), {"notional": None, "volume": 3, "vwap": None})
        self.assertEqual(quality(missing)["volume"].status, Status.AVAILABLE)
        self.assertEqual(quality(missing)["notional"].reasons, (Reason.NULL_FIELD,))

    def test_missing_trade_price_preserves_volume(self):
        m = changed(market(), price=None)
        result = compute_ef1((m, proof()), config(), entity=ENTITY)
        self.assertEqual(view(result), {"notional": None, "volume": 3, "vwap": None})

    def test_a02_positive_duration_covered_empty(self):
        for kind, mode in ((DataKind.TRADE, "trades"), (DataKind.BAR, "bars_actual_notional")):
            m = market(kind)
            m = replace(m, columns=tuple(Column(c.name, ()) for c in m.columns),
                        metadata=replace(m.metadata, coverage=Coverage(0, 0, True)))
            result = compute_ef1((m, proof()), config(mode), entity=ENTITY)
            self.assertEqual(view(result), {"notional": 0, "volume": 0, "vwap": None})
            self.assertEqual(quality(result)["vwap"].status, Status.NOT_APPLICABLE)
            self.assertEqual(quality(result)["vwap"].reasons, (Reason.ZERO_DENOMINATOR,))

    def test_ineligible_trades_and_observed_zero_volume_bar_are_not_missing(self):
        trades = changed(market(), eligible=(False, False), price=None, size=None)
        bars = changed(market(DataKind.BAR), open=(None,), high=(None,), low=(None,),
                       close=(None,), volume=(0,), actual_notional=None)
        for m, mode in ((trades, "trades"), (bars, "bars_actual_notional")):
            result = compute_ef1((m, proof()), config(mode), entity=ENTITY)
            self.assertEqual(view(result), {"notional": 0, "volume": 0, "vwap": None})
            self.assertEqual(quality(result)["volume"].status, Status.AVAILABLE)

    def test_absent_market_and_absent_proof_remain_distinct_bindings(self):
        for inputs, roles in (((proof(),), {"anchor_provenance"}),
                              ((market(),), {"trades"}), ((), set())):
            result = compute_ef1(inputs, config(), entity=ENTITY)
            self.assertTrue(all(v is None for v in view(result).values()))
            self.assertTrue(all(q.status == Status.MISSING_INPUT and Reason.ABSENT_INPUT in q.reasons
                                for q in result.quality))
            self.assertEqual({b.role for b in result.metadata.inputs}, roles)

    def test_unknown_future_or_expired_proof_never_becomes_ready(self):
        for p, reason in ((proof(known_at=None), Reason.UNKNOWN_AVAILABILITY),
                          (proof(known_at=21), Reason.FUTURE_KNOWLEDGE),
                          (proof(end=20), Reason.INELIGIBLE)):
            result = compute_ef1((market(), p), config(), entity=ENTITY)
            self.assertTrue(all(v is None for v in view(result).values()))
            self.assertTrue(all(reason in q.reasons for q in result.quality))
            self.assertEqual(result.metadata.inputs[0].metadata, p.metadata)

    def test_proof_knowledge_equality_and_finite_end_neighbor(self):
        result = compute_ef1((market(), proof(known_at=20, end=21)), config(), entity=ENTITY)
        self.assertEqual(view(result)["vwap"], 11.0)

    def test_incomplete_market_or_proof_preserves_missing_coverage(self):
        for m, p in ((market(complete=False), proof()), (market(), proof(complete=False))):
            result = compute_ef1((m, p), config(), entity=ENTITY)
            self.assertTrue(all(q.status == Status.INCOMPLETE_COVERAGE for q in result.quality))
            self.assertTrue(all(q.reasons == (Reason.GOVERNED_GAP,) for q in result.quality))

    def test_late_market_input_blocks_totals_without_rewriting_bindings(self):
        m = changed(market(), known_at_ns=(10, 21))
        result = compute_ef1((m, proof()), config(), entity=ENTITY)
        self.assertTrue(all(q.reasons == (Reason.FUTURE_KNOWLEDGE,) for q in result.quality))
        self.assertEqual(result.metadata.inputs[1].metadata, m.metadata)

    def test_a03_anchor_at_cutoff_is_bounds_before_fake_scope(self):
        self.error(ErrorCode.BOUNDS, lambda: config(selection=context(start_ns=20)))
        self.error(ErrorCode.BOUNDS, lambda: config(selection=context(start_ns=21)))

    def test_exact_scope_bar_straddle_and_future_trade_refuse(self):
        m = market()
        self.error(ErrorCode.INCONSISTENT_IDENTITY,
                   lambda: compute_ef1((replace(m, metadata=replace(m.metadata,
                        scope=InputScope(9, 20, "eligible-v1"))), proof()), config(), entity=ENTITY))
        self.error(ErrorCode.BOUNDS, lambda: compute_ef1(
            (changed(market(), event_ns=(10, 20)), proof()), config(), entity=ENTITY))
        self.error(ErrorCode.BOUNDS, lambda: compute_ef1(
            (changed(market(DataKind.BAR), start_ns=(9,)), proof()),
            config("bars_actual_notional"), entity=ENTITY))

    def test_closing_auction_boundary_requires_explicit_matching_construction(self):
        session = SessionSpec("SYN", "S", 10, 30, "UTC", include_closing_auction=True)
        c = config(cutoff=30, knowledge=30, session=session)
        m = changed(market(cutoff=30), event_ns=(10, 30), known_at_ns=(10, 30),
                    condition=("none", "closing_auction"))
        m = replace(m, metadata=replace(m.metadata,
                    scope=InputScope(10, 30, "eligible-v1", include_closing_auction=True)))
        self.assertEqual(view(compute_ef1((m, proof()), c, entity=ENTITY))["vwap"], 11.0)
        wrong = replace(m, metadata=replace(m.metadata, scope=InputScope(10, 30, "eligible-v1")))
        self.error(ErrorCode.BOUNDS, lambda: compute_ef1(
            (wrong, proof()), config(cutoff=30, knowledge=30), entity=ENTITY))

    def test_reconstruction_retains_original_unknown_knowledge_and_distinct_mode(self):
        c = config()
        c = replace(c, availability=AvailabilitySpec(20, 20, 20, "reconstruction", "original fixture"))
        p = proof(known_at=None)
        result = compute_ef1((market(), p), c, entity=ENTITY)
        self.assertEqual(view(result)["vwap"], 11.0)
        self.assertEqual(result.metadata.availability.mode, "reconstruction")
        self.assertEqual(result.metadata.inputs[0].metadata, p.metadata)

    def test_wrong_proof_hash_revision_vocabulary_and_duplicate_input(self):
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(
            (market(), changed(proof(), reference_id=("a1:" + "0" * 64,))), config(), entity=ENTITY))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(
            (market(), proof(definition={**DEFINITION, "revision": "R2"})), config(), entity=ENTITY))
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(
            (market(), changed(proof(), fact_kind=("unrecognized",))), config(), entity=ENTITY))
        self.error(ErrorCode.DUPLICATE, lambda: compute_ef1(
            (market(), proof(input_id="mk")), config(), entity=ENTITY))
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1((proof(), market()), config(), entity=ENTITY))

    def test_order_and_overflow_are_typed(self):
        self.error(ErrorCode.INVALID_ORDER, lambda: compute_ef1(
            (changed(market(), event_ns=(15, 10)), proof()), config(), entity=ENTITY))
        self.error(ErrorCode.OVERFLOW, lambda: compute_ef1(
            (changed(market(), size=(2**63 - 1, 1)), proof()), config(), entity=ENTITY))
        self.error(ErrorCode.OVERFLOW, lambda: compute_ef1(
            (changed(market(), price=(2**63 - 1, 2**63 - 1), size=(2**63 - 1, 2**63 - 1)), proof()),
            config(), entity=ENTITY))

    def test_checked_wide_product_and_fractional_price_once(self):
        m = changed(market(), price=(2**62, 2**62), size=(2, 2))
        result = compute_ef1((m, proof()), config(), entity=ENTITY)
        self.assertEqual(view(result)["notional"], 2**64)
        self.assertEqual(view(result)["volume"], 4)
        self.assertEqual(view(result)["vwap"], float(2**62 / 100))

    def test_decoder_is_canonical_bounded_immutable_and_detached(self):
        raw = context()
        c = config(selection=raw)
        raw["selection"]["definition"]["start_ns"] = 99
        decoded = decode_ef1_context(c)
        self.assertIsInstance(decoded, MappingProxyType)
        self.assertEqual(decoded["selection"]["definition"]["start_ns"], 10)
        with self.assertRaises(TypeError):
            decoded["selection"]["definition"]["start_ns"] = 11
        noncanonical = c.parameters[0].value.replace(":", ": ", 1)
        self.error(ErrorCode.INVALID_CONFIG, lambda: decode_ef1_context(
            replace(c, parameters=(Parameter("ef1_context_json", noncanonical),))))
        duplicate = c.parameters[0].value.replace('{', '{"version":"ef1-context1",', 1)
        self.error(ErrorCode.DUPLICATE, lambda: decode_ef1_context(
            replace(c, parameters=(Parameter("ef1_context_json", duplicate),))))
        self.error(ErrorCode.BOUNDS, lambda: decode_ef1_context(
            replace(c, parameters=(Parameter("ef1_context_json", " " * 4097),))))
        self.error(ErrorCode.BOUNDS, lambda: config(selection=context(start_ns=True)))

    def test_discovery_additive_catalogue_and_package_boundary(self):
        definitions = ef1_definitions(config())
        self.assertEqual([d.feature_id for d in definitions],
                         ["session.anchor.notional", "session.anchor.volume", "session.anchor.vwap"])
        self.assertTrue(all(d.capabilities.batch and not d.capabilities.update
                            and not d.capabilities.restore and not d.capabilities.merge for d in definitions))
        self.assertEqual(len(builtin_registry().list_features()), 39)
        self.assertEqual((__version__, contracts_version), ("0.0.4a5", "0.0.4a4"))
        other = context()
        other["producer"] = "period"
        self.error(ErrorCode.UNSUPPORTED_CAPABILITY, lambda: config(selection=other))
