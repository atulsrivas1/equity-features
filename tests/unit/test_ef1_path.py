"""Frozen independent literal path goldens, canonical controls and boundary tests.

The JSON is the reviewed mathematical specification, never generated from outputs.
"""
from copy import deepcopy
from dataclasses import replace
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import unittest

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ContractError,
    Coverage, DataKind, EntityKey, ErrorCode, InputScope, PriceUnit, SessionSpec,
    SourceBinding, WindowSpec,
)
from equity_features.ef1 import build_ef1_config, compute_ef1, ef1_definitions

SPEC = json.loads((Path(__file__).resolve().parents[2] / "docs/ef1/PATH_CONTRACT_PROPOSAL.json").read_text())
PROFILES = SPEC["profiles"]
ENTITY = EntityKey("X", "S")
UNIT = PriceUnit(0, "USD")


def literal(case):
    row = deepcopy(next(item for item in SPEC["fixtures"] if item["id"] == case))
    if "based_on" in row:
        result = literal(row["based_on"])
        result.update(row)
        return result
    return row


def configuration(fixture, *, mode="known_at", knowledge=None, session=None, calendar=None):
    gap = fixture.get("producer", "path_gap") == "path_gap"
    calendar = deepcopy(PROFILES["gap_calendar" if gap else "drive_calendar"] if calendar is None else calendar)
    selection = {"sampling": fixture.get("sampling", "eligible_trade")}
    if not gap:
        selection["duration_ns"] = fixture.get("duration_ns", 5)
    cutoff = fixture.get("C", 13)
    knowledge = cutoff if knowledge is None else knowledge
    return build_ef1_config({"version": "ef1-context1", "producer": "path_gap" if gap else "path_drive",
                             "calendar": calendar, "selection": selection},
        session=SessionSpec("SYN", "S", 10, 30, "UTC", scheduled_close_ns=30) if session is None else session,
        window=WindowSpec(2 if gap else 1, "S", ("P", "S") if gap else ("S",), "completed_eod"),
        availability=AvailabilitySpec(cutoff, knowledge, max(cutoff, knowledge), mode,
                                     "fixture" if mode == "reconstruction" else None),
        price_unit=UNIT, adjustment=AdjustmentSpec())


def batch(kind, names, rows, *, cutoff=13, coverage=None, source=None):
    count = len(rows)
    daily = kind == DataKind.DAILY
    return CanonicalBatch(kind, tuple(Column(name, tuple(row[index] for row in rows))
        for index, name in enumerate(names)), BatchMetadata("SYN",
        SourceBinding("SYN-DAILY" if daily else "SYN-PATH", "R1", "ef1-path-map1",
                      source or ("prior" if daily else "path")),
        Coverage(count, count, True) if coverage is None else Coverage(*coverage), UNIT,
        scope=InputScope(-10 if daily else 10, 0 if daily else cutoff, "supplied_path", False, False)))


def proof(config, *, known=-10):
    # Independent literal calendar serialization, not a production proof helper.
    context = json.loads(config.parameters[0].value)
    calendar = context["calendar"]
    digest = hashlib.sha256(json.dumps(calendar, sort_keys=True, ensure_ascii=True,
                                      separators=(",", ":")).encode("ascii")).hexdigest()
    values = ["X", "S", "c1:" + digest, "ef1.calendar.provenance", -10, 30, "supplied_schedule", known]
    return CanonicalBatch(DataKind.REFERENCE, tuple(Column(name, (value,)) for name, value in
        zip(PROFILES["calendar_columns"], values, strict=True)), BatchMetadata("SYN",
        SourceBinding("SYN-CALENDAR", "R1", "ef1-reference-map1", "calendar"), Coverage(1, 1, True), None))


def inputs(fixture, config):
    result = [proof(config)]
    gap = fixture.get("producer", "path_gap") == "path_gap"
    if fixture.get("path", "present") is not None:
        trades = fixture.get("sampling", "eligible_trade") == "eligible_trade"
        result.append(batch(DataKind.TRADE if trades else DataKind.BAR,
            fixture.get("columns", PROFILES["trade_columns" if trades else "bar_columns"]), fixture["rows"],
            cutoff=fixture["C"] if gap else min(fixture["C"], 15), coverage=fixture["path_coverage"]))
    if gap and fixture.get("prior", "prior_row_P10") is not None:
        result.append(batch(DataKind.DAILY, fixture.get("replace_prior_columns", PROFILES["daily_columns"]),
            [fixture.get("replace_prior_row", fixture.get("prior_row", PROFILES[fixture.get("prior", "prior_row_P10")]))]))
    return tuple(result)


def changed(original, **changes):
    columns = {column.name: column.values for column in original.columns}
    columns.update(changes)
    return replace(original, columns=tuple(Column(name, values) for name, values in columns.items()))


class EF1Paths(unittest.TestCase):
    def error(self, code, call):
        with self.assertRaises(ContractError) as caught:
            call()
        self.assertEqual(caught.exception.code, code)

    def assert_fixture(self, fixture):
        config = configuration(fixture)
        result = compute_ef1(inputs(fixture, config), config, entity=ENTITY)
        self.assertEqual(tuple(column.feature_id for column in result.values),
                         tuple(definition.feature_id for definition in ef1_definitions(config)))
        for column, expected in zip(result.values, fixture["expected_values_in_output_order"], strict=True):
            if type(expected) is str:
                self.assertAlmostEqual(column.values[0], float(Fraction(expected)), delta=1e-12)
            else:
                self.assertEqual(column.values, (expected,))
                if expected is not None:
                    self.assertIs(type(column.values[0]), type(expected))
        for quality in result.quality:
            expected = fixture.get("quality_each", fixture.get("first_fill_quality") if
                quality.feature_id.endswith("first_fill_ns") else fixture.get("quality_other"))
            self.assertEqual([quality.status.value, quality.expected, quality.observed,
                              [reason.value for reason in quality.reasons]], expected)
        self.assertEqual(len(result.evidence), fixture["evidence_count"])
        self.assertEqual(result.metadata.evidence_limit, 7 if fixture.get("producer", "path_gap") == "path_gap" else 4)
        for suffix, expected in (fixture.get("witnesses", {}) if fixture["evidence_count"] else {}).items():
            self.assertEqual(sorted(row.row_id for row in result.evidence if row.feature_id.endswith("." + suffix)), sorted(expected))
        supplied = inputs(fixture, config)
        self.assertEqual({binding.metadata.source.input_id: binding.metadata for binding in result.metadata.inputs},
                         {item.metadata.source.input_id: item.metadata for item in supplied})
        by_id = {item.metadata.source.input_id: item for item in supplied}
        for witness in result.evidence:
            original = by_id[witness.input_id]
            columns = {column.name: column.values for column in original.columns}
            if original.kind == DataKind.TRADE:
                index = columns["event_id"].index(witness.row_id)
                self.assertEqual((witness.event_ns, witness.known_at_ns, witness.boundary,
                                  witness.effective_start_ns, witness.effective_end_ns),
                                 (columns["event_ns"][index], columns["known_at_ns"][index], "ordinary", None, None))
            else:
                ids = tuple("daily:" + session if original.kind == DataKind.DAILY else
                    "bar:" + str(start) + ":" + str(end) for session, start, end in
                    zip(columns["session_id"], columns["start_ns"], columns["end_ns"], strict=True))
                index = ids.index(witness.row_id)
                self.assertEqual((witness.event_ns, witness.known_at_ns, witness.boundary,
                                  witness.effective_start_ns, witness.effective_end_ns),
                    (columns["end_ns"][index], columns["known_at_ns"][index], "completed_interval",
                     columns["start_ns"][index], columns["end_ns"][index]))
            self.assertEqual(witness.entity, ENTITY)
            self.assertEqual(witness.use, "consumed")
            self.assertIsNone(witness.exclusion_reason)
        return result

    def control(self, index):
        control = deepcopy(SPEC["canonical_policy_controls"][index])
        fixture = literal(control.get("based_on", "G01"))
        fixture.update(control)
        if "expected_error" not in control:
            return self.assert_fixture(fixture)
        if control["kind"] == "bar":
            fixture["sampling"] = "completed_bar_close"
        config = configuration(fixture)
        kind = DataKind(control["kind"])
        base = literal("G02" if kind == DataKind.BAR else "G01")
        base["C"] = fixture["C"]
        supplied = list(inputs(base, config))
        replacement = batch(kind, control["columns"], control.get("rows", [control.get("row")]), cutoff=13)
        supplied[2 if kind == DataKind.DAILY else 1] = replacement
        self.error(ErrorCode(control["expected_error"]), lambda: compute_ef1(tuple(supplied), config, entity=ENTITY))

    def test_g01(self): self.assert_fixture(literal("G01"))
    def test_g01_prefix(self): self.assert_fixture(literal("G01-prefix-C12"))
    def test_g02(self): self.assert_fixture(literal("G02"))
    def test_g03(self): self.assert_fixture(literal("G03"))
    def test_g03_zero(self): self.assert_fixture(literal("G03-zero"))
    def test_d01(self): self.assert_fixture(literal("D01"))
    def test_d01_prefix(self): self.assert_fixture(literal("D01-prefix-C14"))
    def test_g04_reversal(self): self.assert_fixture(literal("G04-reversal"))
    def test_g05_overshoot(self): self.assert_fixture(literal("G05-overshoot-expand"))
    def test_g06_empty(self): self.assert_fixture(literal("G06-empty"))
    def test_g07_null_prior(self): self.assert_fixture(literal("G07-null-prior"))
    def test_g08_missing_path(self): self.assert_fixture(literal("G08-path-missing"))
    def test_g09_missing_prior(self): self.assert_fixture(literal("G09-prior-missing"))
    def test_g10_unknown_population(self): self.assert_fixture(literal("G10-unknown-population"))
    def test_cp01(self): self.control(0)
    def test_cp02(self): self.control(1)
    def test_cp03(self): self.control(2)
    def test_cp04(self): self.control(3)
    def test_cp05(self): self.control(4)
    def test_cp06(self): self.control(5)
    def test_cp07(self): self.control(6)
    def test_cp08(self): self.control(7)
    def test_cp09(self): self.control(8)

    def test_original_knowledge_all_required_roles_both_modes(self):
        for case in ("G01", "G02"):
            fixture = literal(case)
            for mode in ("known_at", "reconstruction"):
                config = configuration(fixture, mode=mode)
                for role in range(3):
                    for known, reason in ((None, "unknown_availability"), (14, "future_knowledge")):
                        with self.subTest(case=case, mode=mode, role=role, known=known):
                            supplied = list(inputs(fixture, config))
                            original = supplied[role]
                            times = list(next(c.values for c in original.columns if c.name == "known_at_ns"))
                            times[0] = known
                            supplied[role] = changed(original, known_at_ns=tuple(times))
                            result = compute_ef1(tuple(supplied), config, entity=ENTITY)
                            self.assertTrue(all(q.status.value == "missing_input" and [r.value for r in q.reasons] == [reason] for q in result.quality))
                            self.assertFalse(result.evidence)

    def test_missing_proof_and_present_roles(self):
        fixture = literal("G01")
        config = configuration(fixture)
        supplied = inputs(fixture, config)
        result = compute_ef1(supplied[1:], config, entity=ENTITY)
        self.assertTrue(all(q.status.value == "missing_input" and q.observed == 4 for q in result.quality))
        for bad in ((None,), (supplied[1], supplied[0]), (supplied[0], supplied[0]),
                    (supplied[0], supplied[2], supplied[1])):
            self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1(bad, config, entity=ENTITY))

    def test_endpoint_trade_rejected_completed_bar_admitted(self):
        fixture = literal("D01")
        config = configuration(fixture)
        supplied = list(inputs(fixture, config))
        supplied[1] = changed(supplied[1], event_ns=(10, 12, 15))
        self.error(ErrorCode.BOUNDS, lambda: compute_ef1(tuple(supplied), config, entity=ENTITY))
        fixture.update(sampling="completed_bar_close", rows=[["X", "S", 10, 15, 10, 12, 9, 11, 1, 15]],
            path_coverage=[1, 1, True], expected_values_in_output_order=["0", "1/10", "1/10"],
            quality_each=["available", 1, 1, []], evidence_count=3,
            witnesses={"return": ["bar:10:15"], "excursion_up": ["bar:10:15"], "excursion_down": ["bar:10:15"]})
        self.assert_fixture(fixture)

    def test_downward_reversal_and_earliest_clamped_ties(self):
        fixture = literal("G04-reversal")
        fixture.update(prior="prior_row_P12", rows=[["X", "S", 10, 0, "a", True, 10, 1, 10],
            ["X", "S", 11, 1, "b", True, 13, 1, 11], ["X", "S", 12, 2, "c", True, 11, 1, 12]])
        self.assert_fixture(fixture)
        fixture = literal("G01")
        fixture.update(rows=[["X", "S", 10, 0, "a", True, 12, 1, 10],
            ["X", "S", 11, 1, "b", True, 9, 1, 11], ["X", "S", 11, 2, "c", True, 8, 1, 11]],
            expected_values_in_output_order=["1", True, 11, "0"], witnesses={
                "fill_fraction": ["a", "b"], "filled": ["b"], "first_fill_ns": ["b"],
                "remaining_fraction": ["a", "daily:P", "c"]})
        self.assert_fixture(fixture)

    def test_duplicate_ids_keys_and_reverse_order(self):
        fixture = literal("G01")
        config = configuration(fixture)
        supplied = inputs(fixture, config)
        for changes, code in (({"event_id": ("a", "a", "c")}, ErrorCode.DUPLICATE),
                ({"event_ns": (10, 10, 12), "order_key": (0, 0, 2)}, ErrorCode.DUPLICATE),
                ({"event_ns": (11, 10, 12)}, ErrorCode.INVALID_ORDER)):
            self.error(code, lambda: compute_ef1((supplied[0], changed(supplied[1], **changes), supplied[2]), config, entity=ENTITY))

    def test_ineligible_unknown_row_is_population_not_operand(self):
        fixture = literal("G01")
        fixture["rows"].insert(1, ["X", "S", 10, 1, "unused", False, None, None, None])
        fixture.update(path_coverage=[4, 4, True], quality_each=["available", 5, 5, []])
        self.assert_fixture(fixture)

    def test_all_ineligible_and_zero_volume(self):
        fixture = literal("G06-empty")
        fixture.update(rows=[["X", "S", 11, 0, "a", False, None, None, None]], path_coverage=[1, 1, True],
                       quality_each=["not_applicable", 2, 2, ["no_eligible_observations"]])
        self.assert_fixture(fixture)
        fixture.update(sampling="completed_bar_close", rows=[["X", "S", 10, 12, None, None, None, None, 0, None]])
        self.assert_fixture(fixture)

    def test_combined_readiness_and_counts(self):
        fixture = literal("G10-unknown-population")
        config = configuration(fixture)
        supplied = list(inputs(fixture, config))
        supplied[1] = changed(supplied[1], known_at_ns=(None, 11, 12))
        result = compute_ef1(tuple(supplied), config, entity=ENTITY)
        self.assertTrue(all(q.status.value == "missing_input" and q.expected is None and q.observed == 4 and
            [r.value for r in q.reasons] == ["governed_gap", "unknown_availability"] for q in result.quality))

    def test_drive_cutoff_after_window_retains_exact_scope(self):
        fixture = literal("D01")
        fixture["C"] = 40
        self.assert_fixture(fixture)
        config = configuration(fixture)
        supplied = list(inputs(fixture, config))
        supplied[1] = replace(supplied[1], metadata=replace(supplied[1].metadata,
            scope=InputScope(10, 40, "supplied_path", False, False)))
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(tuple(supplied), config, entity=ENTITY))

    def test_invalid_gap_cutoffs_and_drive_duration(self):
        for cutoff in (10, 31):
            fixture = literal("G01")
            fixture["C"] = cutoff
            self.error(ErrorCode.BOUNDS, lambda: configuration(fixture))
        for duration in (0, -1, 21):
            fixture = literal("D01")
            fixture["duration_ns"] = duration
            self.error(ErrorCode.BOUNDS, lambda: configuration(fixture))

    def test_prior_shape_bounds_session_and_original_volume(self):
        fixture = literal("G01")
        config = configuration(fixture)
        supplied = inputs(fixture, config)
        for bad in (changed(supplied[2], session_id=("OTHER",)), changed(supplied[2], start_ns=(-9,))):
            self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1((*supplied[:2], bad), config, entity=ENTITY))
        for rows in ([], [["X", "P", -10, 0, 10, 0], ["X", "P", -10, 0, 10, 0]]):
            prior = batch(DataKind.DAILY, PROFILES["daily_columns"], rows)
            self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1((*supplied[:2], prior), config, entity=ENTITY))

    def test_unit_basis_scope_auction_and_input_identity(self):
        fixture = literal("G01")
        config = configuration(fixture)
        supplied = inputs(fixture, config)
        for meta, code in ((replace(supplied[1].metadata, price_unit=PriceUnit(1, "USD")), ErrorCode.INVALID_UNIT),
                (replace(supplied[1].metadata, scope=InputScope(10, 13, "other", False, False)), ErrorCode.INCONSISTENT_IDENTITY),
                (replace(supplied[1].metadata, scope=InputScope(10, 13, "supplied_path", True, False)), ErrorCode.INCONSISTENT_IDENTITY),
                (replace(supplied[1].metadata, source=SourceBinding("S", "R1", "M", "prior")), ErrorCode.DUPLICATE)):
            self.error(code, lambda: compute_ef1((supplied[0], replace(supplied[1], metadata=meta), supplied[2]), config, entity=ENTITY))

    def test_auction_conditions_are_strict(self):
        fixture = literal("G01")
        config = configuration(fixture)
        supplied = inputs(fixture, config)
        for conditions in (("opening_auction", None, None), (None, "closing_auction", None)):
            self.error(ErrorCode.BOUNDS, lambda: compute_ef1((supplied[0], changed(supplied[1], condition=conditions), supplied[2]), config, entity=ENTITY))

    def test_count_overflow_precedes_missing_readiness(self):
        fixture = literal("G01")
        config = configuration(fixture)
        supplied = inputs(fixture, config)
        path = replace(supplied[1], metadata=replace(supplied[1].metadata, coverage=Coverage(2**63 - 1, 3, False)))
        self.error(ErrorCode.OVERFLOW, lambda: compute_ef1((path,), config, entity=ENTITY))

    def test_bar_positive_first_open_and_sampled_extrema(self):
        fixture = literal("D01")
        fixture.update(sampling="completed_bar_close", rows=[
            ["X", "S", 10, 11, None, None, None, None, 0, None],
            ["X", "S", 11, 13, 10, 50, 1, 12, 2, 13],
            ["X", "S", 13, 15, 12, 50, 1, 11, 1, 15]],
            expected_values_in_output_order=["0", "1/5", "1/10"], evidence_count=4,
            witnesses={"return": ["bar:11:13", "bar:13:15"], "excursion_up": ["bar:11:13"], "excursion_down": ["bar:13:15"]})
        result = self.assert_fixture(fixture)
        self.assertTrue(all(row.boundary == "completed_interval" and row.event_ns == row.effective_end_ns for row in result.evidence))

    def test_bar_straddle_overlap_and_duplicate(self):
        fixture = literal("G02")
        config = configuration(fixture)
        supplied = inputs(fixture, config)
        for start, end in ((9, 12), (10, 13)):
            self.error(ErrorCode.BOUNDS, lambda: compute_ef1((supplied[0], changed(supplied[1], start_ns=(start,), end_ns=(end,)), supplied[2]), config, entity=ENTITY))
        for rows, code in (([["X", "S", 10, 12, 12, 13, 9, 11, 2, 12]] * 2, ErrorCode.DUPLICATE),
                ([["X", "S", 10, 12, 12, 13, 9, 11, 2, 12], ["X", "S", 11, 12, 12, 13, 9, 11, 2, 12]], ErrorCode.INVALID_ORDER)):
            path = batch(DataKind.BAR, PROFILES["bar_columns"], rows, cutoff=12)
            self.error(code, lambda: compute_ef1((supplied[0], path, supplied[2]), config, entity=ENTITY))

    def test_absent_operand_columns_remain_missing(self):
        fixture = literal("G01")
        config = configuration(fixture)
        supplied = inputs(fixture, config)
        for field in ("price", "size", "known_at_ns"):
            path = replace(supplied[1], columns=tuple(c for c in supplied[1].columns if c.name != field))
            result = compute_ef1((supplied[0], path, supplied[2]), config, entity=ENTITY)
            reason = "unknown_availability" if field == "known_at_ns" else "absent_input"
            self.assertTrue(all(q.status.value == "missing_input" and [r.value for r in q.reasons] == [reason] for q in result.quality))

    def test_calendar_covers_prior_and_strict_dates(self):
        fixture = literal("G01")
        config = configuration(fixture)
        supplied = inputs(fixture, config)
        self.error(ErrorCode.BOUNDS, lambda: compute_ef1((changed(supplied[0], effective_start_ns=(0,)), *supplied[1:]), config, entity=ENTITY))
        calendar = deepcopy(PROFILES["gap_calendar"])
        calendar["sessions"][0][1] = calendar["sessions"][1][1]
        self.error(ErrorCode.BOUNDS, lambda: configuration(fixture, calendar=calendar))

    def test_drive_complete_empty(self):
        fixture = literal("D01")
        fixture.update(rows=[], path_coverage=[0, 0, True], expected_values_in_output_order=[None, None, None],
            quality_each=["not_applicable", 0, 0, ["no_eligible_observations"]], evidence_count=0, witnesses={})
        self.assert_fixture(fixture)

    def test_downward_bar_high_crossing_is_not_close_hit(self):
        fixture = literal("G02")
        fixture.update(prior="prior_row_P12", rows=[["X", "S", 10, 12, 10, 13, 9, 11, 2, 12]])
        self.assert_fixture(fixture)

    def test_first_sample_need_not_start_at_open(self):
        fixture = literal("G01")
        fixture["rows"][0][2] = 11
        fixture["rows"][0][-1] = 11
        self.assert_fixture(fixture)

    def test_structural_invalid_unused_cell_wins_missing_proof(self):
        fixture = literal("G02")
        config = configuration(fixture)
        supplied = inputs(fixture, config)
        bad = changed(supplied[1], high=(None,))
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1((bad, supplied[2]), config, entity=ENTITY))

    def test_nonoverlapping_bar_gaps_preserve_declared_coverage(self):
        fixture = literal("D01")
        fixture.update(sampling="completed_bar_close", rows=[
            ["X", "S", 10, 11, 10, 10, 10, 10, 1, 11],
            ["X", "S", 14, 15, 10, 11, 10, 11, 1, 15]], path_coverage=[2, 2, True],
            expected_values_in_output_order=["0", "1/10", "1/10"], quality_each=["available", 2, 2, []],
            evidence_count=4, witnesses={"return": ["bar:10:11", "bar:14:15"],
                "excursion_up": ["bar:14:15"], "excursion_down": ["bar:10:11"]})
        self.assert_fixture(fixture)
        fixture.update(path_coverage=[2, 2, False], expected_values_in_output_order=[None, None, None],
                       quality_each=["incomplete_coverage", 2, 2, ["governed_gap"]], evidence_count=0)
        self.assert_fixture(fixture)

    def test_drive_original_opening_knowledge_and_combined_prefix(self):
        fixture = literal("D01-prefix-C14")
        for mode in ("known_at", "reconstruction"):
            config = configuration(fixture, mode=mode)
            supplied = inputs(fixture, config)
            result = compute_ef1((supplied[0], changed(supplied[1], known_at_ns=(None, 12))), config, entity=ENTITY)
            self.assertTrue(all(q.status.value == "missing_input" and [r.value for r in q.reasons] ==
                               ["governed_gap", "unknown_availability"] for q in result.quality))
            self.assertFalse(result.evidence)

    def test_drive_endpoint_overflow_is_explicit(self):
        fixture = literal("D01")
        fixture["duration_ns"] = 2**63 - 1
        self.error(ErrorCode.OVERFLOW, lambda: configuration(fixture))

    def test_wrong_entity_basis_and_selected_kind(self):
        fixture = literal("G01")
        config = configuration(fixture)
        supplied = inputs(fixture, config)
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1(supplied, config, entity=EntityKey("Y", "S")))
        adjustment = AdjustmentSpec("split", "v1", "actions", "prior")
        path = replace(supplied[1], metadata=replace(supplied[1].metadata, adjustment=adjustment))
        self.error(ErrorCode.UNSUPPORTED_ADJUSTMENT, lambda: compute_ef1((supplied[0], path, supplied[2]), config, entity=ENTITY))
        bar = batch(DataKind.BAR, PROFILES["bar_columns"], [], cutoff=13)
        self.error(ErrorCode.INVALID_SCHEMA, lambda: compute_ef1((supplied[0], bar, supplied[2]), config, entity=ENTITY))

    def test_closed_context_and_exact_governed_window(self):
        fixture = literal("G01")
        config = configuration(fixture)
        self.error(ErrorCode.INCONSISTENT_IDENTITY, lambda: compute_ef1((),
            replace(config, window=WindowSpec(1, "S", ("S",), "completed_eod")), entity=ENTITY))
        context = json.loads(config.parameters[0].value)
        context["selection"]["inferred_coverage"] = True
        self.error(ErrorCode.INVALID_CONFIG, lambda: build_ef1_config(context, session=config.session,
            window=config.window, availability=config.availability, price_unit=config.price_unit,
            adjustment=config.adjustment))
