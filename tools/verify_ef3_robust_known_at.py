"""Verify the EF3 contract E amendment E-A2 (known_at gating of bounds, edge and population facts).

Reads the fixtures of `docs/ef3/ROBUST_PACE_AMENDMENT_E_A2.json`, expands each into canonical batches with the
documented `known_at` per fact, runs the pure E producers and compares value (exact rational converted once to
binary64), status, reasons and counts with the hand-derived literal. Run from a source checkout:
`python tools/verify_ef3_robust_known_at.py`; exit status 0 only if every fixture matches.
"""
from __future__ import annotations

import base64
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, Coverage, DataKind,
    EntityKey, FeatureResult, InputScope, Parameter, PriceUnit, SessionSpec, SourceBinding, WindowSpec, validate_batch,
)
from equity_features.ef3 import compute_ef3_robust

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs" / "ef3" / "ROBUST_PACE_AMENDMENT_E_A2.json"
NS, SNAP, STEP, SPAN, K = "SYN", "snap-1", 1000, 300, 100
DEFAULT_KNOWN = 50
ENTITY_ID = "X"
FIELDS = ("instrument_id", "session_id", "reference_id", "fact_kind", "effective_start_ns", "effective_end_ns", "text",
          "known_at_ns")


def ref(text: str) -> str:
    return "x1:" + base64.urlsafe_b64encode(text.encode()).rstrip(b"=").decode()


def batch(kind: DataKind, names: tuple[str, ...], rows: list[tuple[Any, ...]], input_id: str, unit: PriceUnit | None,
          lo: int, hi: int) -> CanonicalBatch:
    columns = tuple(Column(name, tuple(row[i] for row in rows)) for i, name in enumerate(names))
    metadata = BatchMetadata(NS, SourceBinding("SYN-SRC", SNAP, "ef3-map1", input_id), Coverage(None, len(rows), False),
                             unit, AdjustmentSpec(), "none", "shares", "declared", "reject", InputScope(lo, hi, "ef3"), ())
    built = CanonicalBatch(kind, columns, metadata)
    validate_batch(built, required_fields=())
    return built


def known(table: dict[str, Any], key: str) -> int | None:
    return table[key] if key in table else DEFAULT_KNOWN


def reference(rows: list[tuple[Any, ...]], input_id: str, lo: int, hi: int, absent: bool) -> CanonicalBatch:
    """A reference role; `absent` omits the known_at_ns column altogether (the amendment treats it as null)."""
    if absent:
        return batch(DataKind.REFERENCE, FIELDS[:-1], [row[:-1] for row in rows], input_id, None, lo, hi)
    return batch(DataKind.REFERENCE, FIELDS, rows, input_id, None, lo, hi)


def bounds_batch(count: int, table: dict[str, Any], entity: str, excluded: dict[str, Any] | None = None,
                 absent: bool = False) -> CanonicalBatch:
    rows = [(entity, str(i), ref("GRID"), "ef3.session.bounds", i * STEP, i * STEP + SPAN, SNAP, known(table, str(i)))
            for i in range(count)]
    for session, when in (excluded or {}).items():
        i = int(session)
        rows.append((entity, session, ref("EXCL"), "ef3.session.excluded", i * STEP, i * STEP + SPAN, "holiday", when))
    rows.sort(key=lambda row: (row[4], row[2]))
    return reference(rows, "sessions", 0, (count - 1) * STEP + SPAN, absent)


def population_batch(members: Any, target: int, table: dict[str, Any], absent: bool = False) -> CanonicalBatch:
    rows = [(m, str(target), ref("POP"), "ef3.population.member", target * STEP, target * STEP + SPAN, SNAP,
             known(table, m)) for m in members]
    return reference(rows, "population", target * STEP, target * STEP + SPAN, absent)


def daily(entries: list[tuple[str, int, int]], input_id: str, last: int) -> CanonicalBatch:
    rows = [(who, str(i), i * STEP, i * STEP + SPAN, value, DEFAULT_KNOWN) for who, i, value in entries]
    names = ("instrument_id", "session_id", "start_ns", "end_ns", "volume", "known_at_ns")
    return batch(DataKind.DAILY, names, rows, input_id, PriceUnit(0, "USD"), 0, last * STEP + SPAN)


def config(identity: str, algorithm: str, params: list[Parameter], window: int, target: int, market_cutoff: int,
           ) -> ConfigSpec:
    session = SessionSpec(NS, str(target), target * STEP, target * STEP + SPAN, "UTC")
    timing = AvailabilitySpec(market_cutoff, K, max(K, market_cutoff), "known_at")
    return ConfigSpec(identity, algorithm, tuple(params), session,
                      WindowSpec(window, session.session_id, (session.session_id,), "prior_only"), timing,
                      AdjustmentSpec(), PriceUnit(0, "USD"))


def history(fx: dict[str, Any]) -> FeatureResult:
    count = len(fx["series"]) + 1
    params = [Parameter("policy_version", "ef3-robust1"), Parameter("field", "volume"),
              Parameter("window", fx["window"]), Parameter("min_history", fx["min_history"]),
              Parameter("evidence_limit", 0), Parameter("quantile_num", 1), Parameter("quantile_den", 2)]
    pop: dict[str, Any] = fx.get("population") or {}
    absent = fx.get("absent_known_at", [])
    selected = tuple(sorted(fx["expected"]))
    with_cohort = any(f.startswith("cohort.") for f in selected)
    if with_cohort:
        params.append(Parameter("min_population", pop["min_population"]))
    cfg = config("ef3.robust_history", "ef3-robust-history-v1", params, fx["window"], count - 1,
                 (count - 1) * STEP + SPAN)
    series = daily([(ENTITY_ID, i, v) for i, v in enumerate([*fx["series"], fx["target"]])], "series", count - 1)
    sessions = bounds_batch(count, fx["bounds_known_at"], ENTITY_ID, fx.get("excluded"), "bounds" in absent)
    population = values = None
    if pop:
        population = population_batch(pop["members"], count - 1, pop["known_at"], "population" in absent)
        if with_cohort:
            values = daily([(m, count - 1, v) for m, v in pop["members"].items()], "cohort", count - 1)
    return compute_ef3_robust([series, sessions, population, values], cfg,
                              entity=EntityKey(ENTITY_ID, str(count - 1)), features=selected)


def cohort(fx: dict[str, Any]) -> FeatureResult:
    members = fx["members"]
    params = [Parameter("policy_version", "ef3-robust1"), Parameter("field", "volume"), Parameter("window", 1),
              Parameter("min_history", 1), Parameter("evidence_limit", 0),
              Parameter("min_population", fx["min_population"])]
    cfg = config("ef3.robust_history", "ef3-robust-history-v1", params, 1, 0, SPAN)
    population = population_batch(members, 0, fx["population_known_at"], "population" in fx.get("absent_known_at", []))
    values = daily([(m, 0, v) for m, v in members.items()], "cohort", 0)
    sessions = (bounds_batch(1, fx["bounds_known_at"], fx["target_member"]) if "bounds_known_at" in fx else None)
    return compute_ef3_robust([None, sessions, population, values], cfg, entity=EntityKey(fx["target_member"], "0"),
                              features=tuple(sorted(fx["expected"])))


def pace(fx: dict[str, Any]) -> FeatureResult:
    prior, offsets = fx["prior_cells"], fx["grid_offsets"]
    target = len(prior)
    params = [Parameter("policy_version", "ef3-pace1"), Parameter("profile", "bucket"), Parameter("window", len(prior)),
              Parameter("min_history", fx.get("min_history", len(prior))), Parameter("grid_version", "ef3-grid1"),
              Parameter("evidence_limit", 0), Parameter("scale_num", fx["scale"][0]),
              Parameter("scale_den", fx["scale"][1])]
    cfg = config("ef3.volume_pace_robust", "ef3-volume-pace-robust-v1", params, len(prior), target,
                 target * STEP + fx["cutoff_offset"])
    absent = fx.get("absent_known_at", [])
    edges = [(ENTITY_ID, str(target), ref(f"ef3-grid1#{i}"), "ef3.bucket.edge", o, None, "ef3-grid1",
              known(fx["edge_known_at"], str(i))) for i, o in enumerate(offsets)]
    grid = reference(edges, "grid", target * STEP, target * STEP + max(offsets) + 1, "edge" in absent)
    sessions = bounds_batch(target + 1, fx["bounds_known_at"], ENTITY_ID, fx.get("excluded"), "bounds" in absent)
    bars = []
    for i, cells in [*enumerate(prior), (target, fx["target_cells"])]:
        for c, volume in enumerate(cells):
            if volume is not None:
                bars.append((ENTITY_ID, str(i), i * STEP + offsets[c], i * STEP + offsets[c + 1], volume, DEFAULT_KNOWN))
    names = ("instrument_id", "session_id", "start_ns", "end_ns", "volume", "known_at_ns")
    bar_batch = batch(DataKind.BAR, names, bars, "bars", PriceUnit(0, "USD"), 0, target * STEP + max(offsets))
    return compute_ef3_robust([grid, sessions, bar_batch], cfg, entity=EntityKey(ENTITY_ID, str(target)),
                              features=tuple(sorted(fx["expected"])))


def mean(fx: dict[str, Any]) -> FeatureResult:
    count = len(fx["series"]) + 1
    params = [Parameter("policy_version", "ef3-mean1"), Parameter("field", "volume"),
              Parameter("numerator_window", fx["numerator_window"]), Parameter("baseline_window", fx["baseline_window"]),
              Parameter("numerator_inclusion", "prior_only"), Parameter("baseline_inclusion", "prior_only"),
              Parameter("evidence_limit", 0)]
    cfg = config("ef3.volume_ratio_mean", "ef3-volume-ratio-mean-v1", params,
                 max(fx["numerator_window"], fx["baseline_window"]), count - 1, (count - 1) * STEP + SPAN)
    series = daily([(ENTITY_ID, i, v) for i, v in enumerate([*fx["series"], fx["target"]])], "series", count - 1)
    sessions = bounds_batch(count, fx["bounds_known_at"], ENTITY_ID, None, "bounds" in fx.get("absent_known_at", []))
    return compute_ef3_robust([series, sessions], cfg, entity=EntityKey(ENTITY_ID, str(count - 1)),
                              features=tuple(sorted(fx["expected"])))


RUN = {"history": history, "cohort": cohort, "pace": pace, "mean": mean}


def check(fx: dict[str, Any]) -> list[str]:
    problems: list[str] = []
    result = RUN[fx["kind"]](fx)
    if sorted(c.feature_id for c in result.values) != sorted(fx["expected"]):
        return [f"{fx['id']}: selected outputs differ"]
    for column in result.values:
        want = fx["expected"][column.feature_id]
        quality = next(q for q in result.quality if q.feature_id == column.feature_id)
        value = column.values[0]
        literal: float | int | None = None
        if want["exact"] is not None:
            literal = int(Fraction(want["exact"])) if column.feature_id == "cohort.rank" else float(Fraction(want["exact"]))
        got = (value, quality.status.value, [r.value for r in quality.reasons], quality.expected, quality.observed)
        exp = (literal, want["status"], want["reasons"], want["expected"], want["observed"])
        if got != exp:
            problems.append(f"{fx['id']} {column.feature_id}: got {got} want {exp}")
    return problems


def main() -> int:
    document = json.loads(DOCUMENT.read_text(encoding="utf-8"))
    fixtures = document["fixtures"]
    failed = 0
    for fx in fixtures:
        problems = check(fx)
        failed += bool(problems)
        for line in problems:
            print("MISMATCH", line)
    print(f"EF3 E-A2 known_at gating: {len(fixtures) - failed}/{len(fixtures)} fixtures match")
    return 1 if failed or len(fixtures) != document["fixture_count"] else 0


if __name__ == "__main__":
    sys.exit(main())
