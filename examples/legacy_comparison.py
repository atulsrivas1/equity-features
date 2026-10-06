"""Captured synthetic Go observations compared with actual public APIs and hand goldens."""
from fractions import Fraction
import json
import math
from pathlib import Path
from typing import TypedDict, cast
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Cell, Column, ConfigSpec,
    Coverage, DataKind, EntityKey, FeatureResult, HistoryContext, Parameter,
    PriceUnit, SessionSpec, SourceBinding, Status, WindowSpec,
)
from equity_features.history import compute_history

class Vector(TypedDict):
    name: str
    period: int
    close: list[int]
    high: list[int]
    low: list[int]

class Observation(TypedDict):
    name: str
    ema: float | None
    atr: float | None
    ema_class: str
    atr_class: str

class Payload(TypedDict):
    schema_version: str
    vectors: list[Vector]
    observed: list[Observation]


def calculate(v: Vector, feature: str) -> FeatureResult:
    n = len(v["close"])
    sessions = tuple(SessionSpec("synthetic", f"S{i}", 10*i+1, 10*i+10, "supplied") for i in range(n))
    ids = tuple(s.session_id for s in sessions)
    ctx = HistoryContext(EntityKey("A", ids[-1]), "synthetic-grid", sessions, (Coverage(1, 1, True),)*n,
                         initialization_anchor=ids[1] if feature == "atr" else ids[0])
    fields: dict[str, tuple[Cell, ...]] = {
        "instrument_id": ("A",)*n, "session_id": ids,
        "start_ns": tuple(s.open_ns for s in sessions), "end_ns": tuple(s.close_ns for s in sessions),
        "known_at_ns": tuple(s.close_ns for s in sessions),
        "close": tuple(v["close"]), "high": tuple(v["high"]), "low": tuple(v["low"]),
    }
    unit = PriceUnit(0, "USD")
    batch = CanonicalBatch(DataKind.DAILY, tuple(Column(k, xs) for k, xs in fields.items()),
                           BatchMetadata("synthetic", SourceBinding("synthetic", "r1", "v1", v["name"]), Coverage(n, n, True), unit))
    cfg = ConfigSpec("legacy-"+feature, "v1", (Parameter("period", v["period"]),), sessions[-1],
                     WindowSpec(v["period"], ids[-1], ids, "completed_eod"),
                     AvailabilitySpec(sessions[-1].close_ns, sessions[-1].close_ns, sessions[-1].close_ns), price_unit=unit)
    return compute_history(batch, cfg, context=ctx, feature_ids=("history."+feature,))


def verify() -> None:
    payload = cast(Payload, json.loads((Path(__file__).resolve().parents[1]/"tests/references/legacy_comparison.json").read_text(encoding="utf-8")))
    assert payload["schema_version"] == "1"
    goldens: dict[str, tuple[Fraction | None, Fraction | None]] = {
        "ordinary": (Fraction(975, 8), Fraction(122, 9)), "short": (None, None),
        "flat": (Fraction(100), Fraction(0)), "period1": (Fraction(130), Fraction(18)),
        "wide_tick": (Fraction(2**63-1), Fraction(1)),
    }
    observed = {r["name"]: r for r in payload["observed"]}
    assert len(observed) == len(payload["observed"]) == len(goldens) == len(payload["vectors"])
    for vector in payload["vectors"]:
        name = vector["name"]
        for index, feature in enumerate(("ema", "atr")):
            result = calculate(vector, feature)
            actual = result.values[0].values[0]
            expected = goldens[name][index]
            legacy = observed[name]["ema"] if feature == "ema" else observed[name]["atr"]
            classification = observed[name]["ema_class"] if feature == "ema" else observed[name]["atr_class"]
            if expected is None:
                assert actual is None and result.quality[0].status == Status.INSUFFICIENT_HISTORY
                assert legacy is None and classification == "nan"
                continue
            assert type(actual) is float and result.quality[0].status == Status.AVAILABLE
            assert math.isclose(actual, float(expected), rel_tol=1e-12, abs_tol=1e-12)
            assert legacy is not None and classification == "finite"
            if name == "wide_tick" and feature == "atr":
                assert actual == 1.0 and legacy == 0.0
            else:
                assert math.isclose(legacy, float(expected), rel_tol=1e-12, abs_tol=1e-12)
    print("Five captured Go vectors/public EMA-ATR APIs verified; wide integer ATR exact1 versus Float64 legacy0.")


if __name__ == "__main__":
    verify()
