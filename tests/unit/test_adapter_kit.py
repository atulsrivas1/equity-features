"""Independent public SDK and installed synthetic adapter cases."""
from dataclasses import replace
import unittest
from equity_feature_contracts import AvailabilitySpec, Column, ContractError, Coverage, PriceUnit, Status
from equity_feature_contracts.adapter_kit import ConformanceCase, ConformanceOutcome, ConformanceReport, run_conformance
from equity_feature_contracts.adapters import SourceError, SourceErrorCode
from equity_feature_demo import FEATURE_ID, calculate, definition, fixture
from equity_feature_demo.adapter import InMemoryBarAdapter, NeverCancelled, adapter_fixture
from equity_features.custom import CustomInput, CustomRegistry, CustomRequest


class AdapterKitTests(unittest.TestCase):
    def setUp(self):
        self.adapter, self.request = adapter_fixture()
        self.batches = tuple(self.adapter.iter_batches(self.request, NeverCancelled()))

    def source_error(self, code, action):
        with self.assertRaises(SourceError) as caught:
            action()
        self.assertEqual(caught.exception.code, code)

    def case(self, name, *, batches=None, request=None, expected=None, captured=None, live=False):
        return ConformanceCase(name, request or self.request, self.adapter.capabilities(),
            self.batches if batches is None else batches, expected, captured, live)

    def test_independent_full_and_chunk_coverage(self):
        request = replace(self.request, max_batch_rows=1)
        chunks = tuple(self.adapter.iter_batches(request, NeverCancelled()))
        report = run_conformance((self.case("whole"), self.case("chunks", batches=chunks, request=request)))
        self.assertTrue(report.passed)
        self.assertEqual([x.delivery_coverage for x in chunks], [Coverage(1, 1, True)]*2)
        self.assertEqual([x.source_coverage for x in chunks], [Coverage(2, 2, True)]*2)
        self.assertEqual([x.batch.columns[2].values for x in chunks], [(100,), (150,)])
        self.assertNotEqual(chunks[0].source.input_id, chunks[1].source.input_id)

    def test_preserve_unknown_and_future_knowledge(self):
        batch = self.adapter.data
        cols = tuple(replace(c, values=(None, 211)) if c.name == "known_at_ns" else c for c in batch.columns)
        adapter = replace(self.adapter, data=replace(batch, columns=cols))
        request = replace(self.request, availability=AvailabilitySpec(200, 150, 210))
        delivered = tuple(adapter.iter_batches(request, NeverCancelled()))
        self.assertEqual(next(c for c in delivered[0].batch.columns if c.name == "known_at_ns").values, (None, 211))
        self.assertTrue(run_conformance((self.case("knowledge-preserved", batches=delivered, request=request),)).passed)
        original = fixture()
        config = replace(original.config, availability=request.availability)
        custom = CustomRequest((CustomInput("bars", delivered[0].batch),), config, original.entity)
        result = CustomRegistry("demo").register(definition(), calculate).compute(FEATURE_ID, custom)
        self.assertIsNone(result.values[0].values[0])
        self.assertEqual(result.quality[0].status, Status.MISSING_INPUT)

    def test_empty_missing_unavailable_are_distinct(self):
        empty_request = replace(self.request, instruments=("absent",))
        empty = tuple(self.adapter.iter_batches(empty_request, NeverCancelled()))
        missing = tuple(replace(self.adapter, data=None).iter_batches(self.request, NeverCancelled()))
        unavailable = (replace(missing[0], disposition="unavailable", reason="synthetic outage"),)
        self.assertTrue(run_conformance((self.case("empty", batches=empty, request=empty_request),
            self.case("missing", batches=missing), self.case("unavailable", batches=unavailable))).passed)
        self.assertEqual(empty[0].batch.row_count, 0)
        self.assertEqual(empty[0].delivery_coverage, Coverage(0, 0, True))
        self.assertIsNone(missing[0].batch)
        self.assertEqual(missing[0].delivery_coverage, Coverage(None, 0, False))

    def test_wholly_contained_bar_boundaries(self):
        request = replace(self.request, start_ns=125, end_ns=200)
        batches = tuple(self.adapter.iter_batches(request, NeverCancelled()))
        self.assertEqual(next(c for c in batches[0].batch.columns if c.name == "start_ns").values, (150,))
        self.assertTrue(run_conformance((self.case("contained", batches=batches, request=request),)).passed)

    def test_negative_identity_unit_final_and_ordinal(self):
        original = self.batches[0]
        unit_batch = replace(original.batch, metadata=replace(original.batch.metadata, price_unit=PriceUnit(2, "USD")))
        examples = (replace(original, request_id="other"), replace(original, ordinal=1),
                    replace(original, final=False), replace(original, batch=unit_batch))
        for i, invalid in enumerate(examples):
            report = run_conformance((self.case(str(i), batches=(invalid,), expected=SourceErrorCode.SCHEMA),))
            self.assertTrue(report.passed)
            self.assertEqual(report.outcomes[0].observed_error, SourceErrorCode.SCHEMA)

    def test_order_and_duplicate_intervals_reject(self):
        batch = self.batches[0].batch
        for indices in ((1, 0), (0, 0)):
            cols = tuple(Column(c.name, tuple(c.values[i] for i in indices)) for c in batch.columns)
            bad = replace(self.batches[0], batch=replace(batch, columns=cols))
            self.assertTrue(run_conformance((self.case(str(indices), batches=(bad,), expected=SourceErrorCode.SCHEMA),)).passed)

    def test_actual_batch_row_and_chunk_limits(self):
        limited = replace(self.request, max_batch_rows=1)
        self.assertTrue(run_conformance((self.case("oversized-envelope", request=limited, expected=SourceErrorCode.LIMIT),)).passed)
        for request in (replace(self.request, max_rows=1, max_batch_rows=1), replace(limited, max_batches=1)):
            self.source_error(SourceErrorCode.LIMIT, lambda: tuple(self.adapter.iter_batches(request, NeverCancelled())))
        self.source_error(SourceErrorCode.LIMIT, lambda: run_conformance((self.case("x"),), max_cases=0))
        self.source_error(SourceErrorCode.LIMIT, lambda: run_conformance((self.case("x"), self.case("y")), max_cases=1))

    def test_error_facts_do_not_certify_partial_delivery(self):
        for code in SourceErrorCode:
            report = run_conformance((self.case(code.value, batches=(), expected=code, captured=code),))
            self.assertTrue(report.passed)
        self.source_error(SourceErrorCode.SCHEMA, lambda: self.case("partial", captured=SourceErrorCode.CANCELLED))
        unexpected = run_conformance((self.case("wrong-error", batches=(), expected=SourceErrorCode.CANCELLED,
                                               captured=SourceErrorCode.TRANSPORT),))
        self.assertFalse(unexpected.passed)
        self.assertEqual(unexpected.outcomes[0].observed_error, SourceErrorCode.TRANSPORT)

    def test_real_cancel_before_and_between(self):
        class Token:
            cancelled = True
            def is_cancelled(self):
                return self.cancelled
        token = Token()
        self.source_error(SourceErrorCode.CANCELLED, lambda: tuple(self.adapter.iter_batches(self.request, token)))
        token.cancelled = False
        iterator = self.adapter.iter_batches(replace(self.request, max_batch_rows=1), token)
        self.assertFalse(next(iterator).final)
        token.cancelled = True
        self.source_error(SourceErrorCode.CANCELLED, lambda: next(iterator))

    def test_live_unit_snapshot_and_range_unsupported(self):
        self.assertTrue(run_conformance((self.case("live", expected=SourceErrorCode.UNSUPPORTED, live=True),)).passed)
        for request in (replace(self.request, price_unit=PriceUnit(2, "USD")),
                        replace(self.request, snapshot_id="other"), replace(self.request, end_ns=201)):
            self.source_error(SourceErrorCode.UNSUPPORTED, lambda: tuple(self.adapter.iter_batches(request, NeverCancelled())))

    def test_precision_and_version_rejection(self):
        for changes in ({"schema_version": "2"}, {"start_ns": 100.5}):
            self.source_error(SourceErrorCode.SCHEMA, lambda: replace(self.request, **changes))
        batch = self.adapter.data
        cols = tuple(replace(c, values=(100.5, 102.5)) if c.name == "open" else c for c in batch.columns)
        with self.assertRaises(ContractError):
            replace(batch, columns=cols)

    def test_bad_source_ohlc_maps_safe_schema_error(self):
        batch = self.adapter.data
        columns = tuple(replace(c, values=(98, 104)) if c.name == "high" else c for c in batch.columns)
        malformed = replace(batch, columns=columns)
        with self.assertRaises(SourceError) as caught:
            replace(self.adapter, data=malformed)
        self.assertEqual(caught.exception.code, SourceErrorCode.SCHEMA)
        self.assertIsInstance(caught.exception.__cause__, ContractError)
        self.assertEqual(str(caught.exception), "synthetic fixture violates canonical source contract")

    def test_bad_source_bounds_map_safe_schema_error(self):
        with self.assertRaises(SourceError) as caught:
            replace(self.adapter, end_ns=2**63)
        self.assertEqual(caught.exception.code, SourceErrorCode.SCHEMA)
        self.assertIsInstance(caught.exception.__cause__, ContractError)

    def test_case_report_ownership_and_schema(self):
        owned = [self.batches[0]]
        case = self.case("owned", batches=owned)
        owned.clear()
        self.assertEqual(case.batches, self.batches)
        self.source_error(SourceErrorCode.SCHEMA, lambda: run_conformance(iter((case,))))
        self.source_error(SourceErrorCode.SCHEMA, lambda: run_conformance(()))
        self.source_error(SourceErrorCode.SCHEMA, lambda: run_conformance((case, case)))
        self.source_error(SourceErrorCode.SCHEMA, lambda: replace(case, expected_error="cancelled"))
        self.source_error(SourceErrorCode.SCHEMA, lambda: ConformanceOutcome("x", "cancelled", None))
        self.source_error(SourceErrorCode.SCHEMA, lambda: ConformanceReport((object(),)))


if __name__ == "__main__":
    unittest.main()
