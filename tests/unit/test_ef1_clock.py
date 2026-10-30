"""Independent C01 clock schedules and original canonical proof fixtures."""
from copy import deepcopy
from dataclasses import replace
import hashlib
import json
import unittest

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ContractError,
    Coverage, DataKind, EntityKey, ErrorCode, Reason, SessionSpec, SourceBinding, Status,
    ValueType, WindowSpec, builtin_registry,
)
from equity_features import __version__
from equity_features.ef1 import build_ef1_config, compute_ef1, decode_ef1_context, ef1_definitions

ENTITY = EntityKey("X", "S")
CALENDAR = {"calendar_id": "C01", "revision": "R1", "timezone": "UTC",
            "target_date": "2026-01-02", "sessions": [["S", "2026-01-02", 10, 30]],
            "segments": [["premarket", 0, 10], ["regular", 10, 30], ["postmarket", 30, 40]],
            "scheduled_close_ns": 40, "early_close": True}


def config(cutoff=20, *, knowledge=20, calendar=None, session=None):
    calendar = deepcopy(CALENDAR if calendar is None else calendar)
    return build_ef1_config({"version": "ef1-context1", "producer": "clock",
                             "calendar": calendar, "selection": {}},
                            session=SessionSpec("SYN", "S", 10, 30, "UTC",
                                                scheduled_close_ns=40, early_close=True) if session is None else session,
                            window=WindowSpec(len(calendar["sessions"]), "S",
                                              tuple(row[0] for row in calendar["sessions"]), "completed_eod"),
                            availability=AvailabilitySpec(cutoff, knowledge, max(cutoff, knowledge)),
                            price_unit=None, adjustment=AdjustmentSpec())


def proof(*, calendar=None, known_at=5, start=0, end=40, complete=True):
    calendar = CALENDAR if calendar is None else calendar
    # Independent canonical serialization, not a library helper as the oracle.
    text = json.dumps(calendar, ensure_ascii=True, sort_keys=True, separators=(",", ":"))
    data = {"instrument_id": ("X",), "session_id": ("S",),
            "reference_id": ("c1:" + hashlib.sha256(text.encode("ascii")).hexdigest(),),
            "fact_kind": ("ef1.calendar.provenance",), "effective_start_ns": (start,),
            "effective_end_ns": (end,), "text": ("supplied_schedule",), "known_at_ns": (known_at,)}
    metadata = BatchMetadata("SYN", SourceBinding("F", calendar["revision"], "ef1-reference-map1", "cp"),
                             Coverage(1 if complete else 2, 1, complete), None)
    return CanonicalBatch(DataKind.REFERENCE, tuple(Column(k, v) for k, v in data.items()), metadata)


def changed(batch, **changes):
    columns = {c.name: c.values for c in batch.columns}
    columns.update(changes)
    return replace(batch, columns=tuple(Column(k, v) for k, v in columns.items()))


def view(result):
    return {c.feature_id.rsplit(".", 1)[1]: c.values[0] for c in result.values}


class EF1Clocks(unittest.TestCase):
    def error(self, expected, call):
        with self.assertRaises(ContractError) as caught:
            call()
        self.assertEqual(caught.exception.code, expected)

    def test_c01_independent_half_open_boundaries_and_clipping(self):
        for cutoff, phase, elapsed, remaining, fraction in (
                (-1, "closed", 0, 20, 0.0), (0, "premarket", 0, 20, 0.0),
                (10, "regular", 0, 20, 0.0), (15, "regular", 5, 15, 0.25),
                (20, "regular", 10, 10, 0.5), (30, "postmarket", 20, 0, 1.0),
                (40, "closed", 20, 0, 1.0)):
            with self.subTest(cutoff=cutoff):
                result = compute_ef1((proof(),), config(cutoff), entity=ENTITY)
                self.assertEqual(view(result), {"phase": phase, "regular_elapsed_ns": elapsed,
                    "regular_remaining_ns": remaining, "regular_fraction": fraction, "early_close": True})
                self.assertTrue(all(q.status == Status.AVAILABLE and not q.reasons for q in result.quality))

    def test_complete_headers_actual_metadata_and_read_only_context(self):
        c, p = config(), proof()
        result = compute_ef1((p,), c, entity=ENTITY)
        self.assertEqual({x.feature_id.rsplit(".", 1)[1]: (x.dtype, x.unit) for x in ef1_definitions(c)}, {
            "phase": (ValueType.STRING, "state"), "early_close": (ValueType.BOOL, "boolean"),
            "regular_elapsed_ns": (ValueType.INT64, "ns"),
            "regular_remaining_ns": (ValueType.INT64, "ns"),
            "regular_fraction": (ValueType.FLOAT64, "fraction")})
        self.assertEqual(tuple(x.feature_id for x in result.values), tuple(sorted(x.feature_id for x in result.values)))
        self.assertTrue(all((q.expected, q.observed) == (1, 1) for q in result.quality))
        self.assertEqual(result.metadata.config_digest, c.digest)
        self.assertEqual(result.metadata.availability, c.availability)
        self.assertEqual(result.metadata.inputs[0].role, "calendar_provenance")
        self.assertEqual(result.metadata.inputs[0].metadata, p.metadata)
        self.assertEqual((result.metadata.backend_id, result.metadata.backend_version), ("python-exact", __version__))
        self.assertEqual(result.evidence, ())
        with self.assertRaises(TypeError):
            decode_ef1_context(c)["calendar"]["revision"] = "changed"
        self.assertEqual(len(builtin_registry().list_features()), 40)

    def test_frozen_c01_literal_cutoffs(self):
        for cutoff, knowledge, evaluation, phase, elapsed, remaining, fraction in (
                (10, 10, 40, "regular", 0, 20, 0.0),
                (20, 20, 40, "regular", 10, 10, 0.5),
                (30, 30, 40, "postmarket", 20, 0, 1.0),
                (40, 40, 40, "closed", 20, 0, 1.0)):
            with self.subTest(cutoff=cutoff):
                c = replace(config(cutoff, knowledge=knowledge),
                            availability=AvailabilitySpec(cutoff, knowledge, evaluation))
                result = compute_ef1((proof(),), c, entity=ENTITY)
                self.assertEqual(view(result), {"phase": phase, "regular_elapsed_ns": elapsed,
                    "regular_remaining_ns": remaining, "regular_fraction": fraction, "early_close": True})
                self.assertEqual(result.metadata.availability, c.availability)
                self.assertTrue(all(q.status == Status.AVAILABLE and not q.reasons for q in result.quality))

    def test_reconstruction_retains_causal_calendar_proof_requirement(self):
        availability = AvailabilitySpec(20, 20, 40, "reconstruction", "explicit supplied-clock replay")
        c = replace(config(), availability=availability)
        omitted = replace(proof(), columns=tuple(x for x in proof().columns if x.name != "known_at_ns"))
        for p, reason in ((omitted, Reason.UNKNOWN_AVAILABILITY),
                          (proof(known_at=None), Reason.UNKNOWN_AVAILABILITY),
                          (proof(known_at=21), Reason.FUTURE_KNOWLEDGE)):
            with self.subTest(reason=reason, columns=p.columns):
                result = compute_ef1((p,), c, entity=ENTITY)
                self.assertTrue(all(v is None for v in view(result).values()))
                self.assertTrue(all(q.status == Status.MISSING_INPUT and q.reasons == (reason,)
                                    for q in result.quality))
                self.assertEqual(result.metadata.availability, availability)
                self.assertEqual(result.metadata.inputs[0].metadata, p.metadata)
        result = compute_ef1((proof(known_at=20),), c, entity=ENTITY)
        self.assertEqual(view(result), {"phase": "regular", "regular_elapsed_ns": 10,
            "regular_remaining_ns": 10, "regular_fraction": 0.5, "early_close": True})
        self.assertTrue(all(q.status == Status.AVAILABLE and not q.reasons for q in result.quality))
        self.assertEqual(result.metadata.availability, availability)

    def test_absent_empty_unknown_future_and_exact_known_at(self):
        empty = replace(proof(), columns=tuple(Column(c.name, ()) for c in proof().columns),
                        metadata=replace(proof().metadata, coverage=Coverage(0, 0, True)))
        for batches, reason in (((), Reason.ABSENT_INPUT), ((empty,), Reason.ABSENT_INPUT),
                                ((proof(known_at=None),), Reason.UNKNOWN_AVAILABILITY),
                                ((proof(known_at=21),), Reason.FUTURE_KNOWLEDGE)):
            result = compute_ef1(batches, config(), entity=ENTITY)
            self.assertTrue(all(v is None for v in view(result).values()))
            self.assertTrue(all(q.status == Status.MISSING_INPUT and q.reasons == (reason,) for q in result.quality))
            self.assertEqual(len(result.metadata.inputs), len(batches))
        self.assertTrue(all(q.status == Status.AVAILABLE for q in
                            compute_ef1((proof(known_at=20),), config(), entity=ENTITY).quality))

    def test_gap_readiness_does_not_become_closed(self):
        result = compute_ef1((proof(complete=False),), config(40), entity=ENTITY)
        self.assertTrue(all(v is None for v in view(result).values()))
        self.assertTrue(all(q.status == Status.INCOMPLETE_COVERAGE and q.reasons == (Reason.GOVERNED_GAP,)
                            for q in result.quality))

    def test_exact_hash_revision_entity_and_closed_payload(self):
        for bad in (changed(proof(), reference_id=("c1:" + "0" * 64,)),
                    changed(proof(), instrument_id=("OTHER",)),
                    replace(proof(), metadata=replace(proof().metadata,
                        source=SourceBinding("F", "R2", "ef1-reference-map1", "cp")))):
            self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1((bad,), config(), entity=ENTITY))
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(
            (changed(proof(), text=("inferred",)),), config(), entity=ENTITY))

    def test_finite_proof_covers_all_governed_sessions_and_segments(self):
        for start, end in ((1, 40), (0, 35), (0, None), (40, 40)):
            self.error(ErrorCode.BOUNDS, lambda: compute_ef1((proof(start=start, end=end),), config(), entity=ENTITY))
        calendar = deepcopy(CALENDAR)
        calendar["sessions"].insert(0, ["PRIOR", "2026-01-01", -30, -10])
        self.error(ErrorCode.BOUNDS, lambda: compute_ef1((proof(calendar=calendar),), config(calendar=calendar), entity=ENTITY))
        result = compute_ef1((proof(calendar=calendar, start=-30),), config(calendar=calendar), entity=ENTITY)
        self.assertEqual(view(result)["regular_elapsed_ns"], 10)

    def test_actual_session_and_early_close_are_hash_bound(self):
        calendar = deepcopy(CALENDAR)
        calendar["scheduled_close_ns"] = 50
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: config(calendar=calendar))
        session = SessionSpec("SYN", "S", 10, 30, "UTC", scheduled_close_ns=30)
        calendar["scheduled_close_ns"], calendar["early_close"] = 30, False
        c = config(calendar=calendar, session=session)
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1((proof(),), c, entity=ENTITY))
        self.assertFalse(view(compute_ef1((proof(calendar=calendar),), c, entity=ENTITY))["early_close"])

    def test_supplied_dst_utc_offsets_need_no_timezone_lookup(self):
        # Two independently supplied UTC opens one hour apart for the same civil session clock.
        for date, open_ns in (("2026-03-06", 52_200_000_000_000), ("2026-03-09", 48_600_000_000_000)):
            calendar = deepcopy(CALENDAR)
            calendar.update(timezone="America/New_York", target_date=date,
                            sessions=[["S", date, open_ns, open_ns + 20]],
                            segments=[["regular", open_ns, open_ns + 20]],
                            scheduled_close_ns=open_ns + 20, early_close=False)
            session = SessionSpec("SYN", "S", open_ns, open_ns + 20, "America/New_York",
                                  scheduled_close_ns=open_ns + 20)
            result = compute_ef1((proof(calendar=calendar, start=open_ns, end=open_ns + 20),),
                                config(open_ns + 5, calendar=calendar, session=session), entity=ENTITY)
            self.assertEqual((view(result)["regular_elapsed_ns"], view(result)["regular_fraction"]), (5, 0.25))

    def test_malformed_schedule_and_concrete_role_limits(self):
        calendar = deepcopy(CALENDAR)
        calendar["segments"][0][0] = []
        self.error(ErrorCode.INVALID_CONFIG, lambda: config(calendar=calendar))
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1((proof(), proof()), config(), entity=ENTITY))
        calendar = deepcopy(CALENDAR)
        calendar["target_date"] = "2026-02-30"
        self.error(ErrorCode.BOUNDS, lambda: config(calendar=calendar))

    def test_elapsed_ns_overflow_is_typed_not_wrapped(self):
        start, end = -(2**63), 2**63 - 1
        calendar = deepcopy(CALENDAR)
        calendar.update(sessions=[["S", "2026-01-02", start, end]],
                        segments=[["regular", start, end]], scheduled_close_ns=end, early_close=False)
        session = SessionSpec("SYN", "S", start, end, "UTC", scheduled_close_ns=end)
        self.error(ErrorCode.OVERFLOW, lambda: compute_ef1(
            (proof(calendar=calendar, start=start, end=end),),
            config(20, calendar=calendar, session=session), entity=ENTITY))

    def test_calendar_context_bound_is_enforced_without_truncation(self):
        calendar = deepcopy(CALENDAR)
        calendar["sessions"] = [["session-" + str(i) + "-" + "x" * 100,
                                 "2026-01-01", -200 + i * 2, -199 + i * 2]
                                for i in range(32)] + calendar["sessions"]
        self.error(ErrorCode.BOUNDS, lambda: config(calendar=calendar))


if __name__ == "__main__":
    unittest.main()
