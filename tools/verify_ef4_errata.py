"""Regression recipes for the PO rulings E1, E2 and E4 (docs/ef4/EF4_ERRATA_RECIPES.json); no frozen contract is edited.

E1: the shared TopKTrades check is rank-aware (constructor `ranking`; FeatureResult binds the ranking to the feature id).
E2: an undeclared batch that delivers rows is refused INVALID_SCHEMA; zero rows with no declaration stays undeclared.
Tape (DP-T12): a declared incomplete coverage is `governed_gap`, never read as complete.
E4: governed_history with a window above 63 is refused INVALID_CONFIG at configuration.
Run from a source checkout with the library importable: `python tools/verify_ef4_errata.py`; exit 0 only if all hold.
"""
from __future__ import annotations

import dataclasses
import json
import sys
from pathlib import Path
from typing import Any

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ContractError, Coverage, DataKind,
    DType, EntityKey, InputScope, PriceUnit, SessionSpec, SourceBinding, TopKTradeRow, TopKTrades, schema_for,
)
from equity_features.ef4 import build_notional_top_k_config, compute_trade_top_k_notional
from equity_features.ef4._common import declared_coverage
from equity_features_intraday._path_config import _check

ROOT = Path(__file__).resolve().parents[1]
DOCUMENT = ROOT / "docs" / "ef4" / "EF4_ERRATA_RECIPES.json"


def rows(order: str) -> tuple[TopKTradeRow, ...]:
    """price*size a=10, b=6, c=1 and sizes a=1, b=2, c=1: the notional order is a, b, c and the size order b, a, c."""
    a = TopKTradeRow("i", "a", 1, 1, 10, 10, 1)
    b = TopKTradeRow("i", "b", 2, 2, 10, 3, 2)
    c = TopKTradeRow("i", "c", 3, 3, 10, 1, 1)
    return (a, b, c) if order == "notional_order" else (b, a, c)


def cell(dtype: DType, i: int) -> Any:
    return {DType.STRING: f"e{i}", DType.BOOL: True}.get(dtype, i)


def code_of(call: Any) -> str:
    try:
        call()
    except ContractError as error:
        return str(error.code.value)
    return "ok"


def notional_result(coverage: Coverage = Coverage(3, 3, True)) -> Any:
    session = SessionSpec("SYN", "S", 0, 100, "UTC")
    availability = AvailabilitySpec(100, 100, 100)
    adjustment, unit = AdjustmentSpec(), PriceUnit(0, "USD")
    config = build_notional_top_k_config(policy_version="ef4-notional1", top_k=3, evidence_limit=3,
                                         eligibility_policy="regular", session=session, availability=availability,
                                         adjustment=adjustment, price_unit=unit)
    data = [("I", "S", 1, 1, "a", True, 10, 1, 10), ("I", "S", 2, 2, "b", True, 3, 2, 10),
            ("I", "S", 3, 3, "c", True, 1, 1, 10)]
    names = ("instrument_id", "session_id", "event_ns", "order_key", "event_id", "eligible", "price", "size",
             "known_at_ns")
    columns = tuple(Column(name, tuple(row[i] for row in data)) for i, name in enumerate(names))
    meta = BatchMetadata("SYN", SourceBinding("SYN-SRC", "snap", "map1", "trades"), coverage, unit,
                         adjustment, "none", "shares", "declared", "reject", InputScope(0, 100, "regular"), ())
    return compute_trade_top_k_notional((CanonicalBatch(DataKind.TRADE, columns, meta),), config,
                                        entity=EntityKey("I", "S"), features=("tape.top_k_notional",))


def renamed(result: Any, feature_id: str) -> Any:
    def swap(x: Any) -> Any:
        return dataclasses.replace(x, feature_id=feature_id)
    return dataclasses.replace(result, values=tuple(swap(x) for x in result.values),
                               quality=tuple(swap(x) for x in result.quality),
                               evidence=tuple(swap(x) for x in result.evidence))


def run(recipe: dict[str, Any]) -> str:
    kind = recipe["kind"]
    if kind == "topk_constructor":
        return code_of(lambda: TopKTrades(3, rows(recipe["rows"]), ranking=recipe["ranking"]))
    if kind == "topk_result_feature":
        result = notional_result()
        if code_of(lambda: renamed(result, "tape.top_k_notional")) != "ok":
            return "base_refused"
        return code_of(lambda: renamed(result, recipe["feature_id"]))
    if kind == "coverage":
        n = recipe["rows"]
        dkind = DataKind.QUOTE if recipe["role"] == "quote" else DataKind.TRADE
        columns = tuple(Column(f.name, tuple(cell(f.dtype, i) for i in range(n)))
                        for f in schema_for(dkind).fields if f.required)
        meta = BatchMetadata("SYN", SourceBinding("SYN-SRC", "snap", "map1", "in"),
                             Coverage(recipe["expected"], n, recipe["complete"]), PriceUnit(0, "USD"), AdjustmentSpec(),
                             "continuous" if dkind == DataKind.QUOTE else "none", "shares", "declared", "reject", None, ())
        batch = CanonicalBatch(dkind, columns, meta)
        outcome: list[str] = []
        failure = code_of(lambda: outcome.append(declared_coverage(batch, 0, 100)))
        return failure if failure != "ok" else outcome[0]
    if kind == "tape_coverage":
        result = notional_result(Coverage(recipe["expected"], 3, recipe["complete"]))
        row = result.quality[0]
        return "+".join([row.status.value, *sorted(r.value for r in row.reasons)])
    if kind == "path_config":
        refused = code_of(lambda: _check("ef4-path1", recipe["window"], recipe["profile"], 0))
        edges = (code_of(lambda: _check("ef4-path1", 63, "governed_history", 0)),
                 code_of(lambda: _check("ef4-path1", 64, "session_reset", 0)))
        return refused if edges == ("ok", "ok") else "edge_changed"
    return "unknown_kind"


def main() -> int:
    document = json.loads(DOCUMENT.read_text(encoding="utf-8"))
    problems: list[str] = []
    recipes = document["recipes"]
    if document["recipe_count"] != len(recipes):
        problems.append(f"recipe_count {document['recipe_count']} != {len(recipes)}")
    for recipe in recipes:
        got = run(recipe)
        if got != recipe["expect"]:
            problems.append(f"{recipe['id']}: got {got!r} want {recipe['expect']!r}")
    for line in problems:
        print("FAIL", line)
    if not problems:
        print(f"OK: {len(recipes)} errata recipes (E1, E2, E4, DP-T12 gap) hold")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main())
