"""Drive every DV1-6 window-extreme contract fixture through the pure library (`equity_features.dv1`).

For each of the 25 window result fixtures (WX01..WX25) the compact notation is expanded to one daily BAR role (the
`high` and `low` columns on the intraday basis, the `close` column on the close basis, exactly the fields the
fixture's INPUT contract names), a governed daily grid and a final configuration (market cutoff C is the end of the
last delivered slot, a forming slot is not delivered, K = C + 100 s, `ka` maps to K - (100 - ka) s, exactly as the
contract states). Every selected output is run alone and all four jointly, and the library result is compared with
the contract literal BIT FOR BIT: the float64 hex string and sign of each price, the exact integer of each offset,
status, reasons, expected and observed counts, witnesses, the output dtype and unit, and the echoed adjustment basis.
There is no tolerance band in DV1. For each of the 10 refusal recipes whose base is a window fixture the recorded
mutation is applied and the library must refuse with exactly the recorded error code. The wrong-convention rivals
recorded in the contract (earliest wins a tie, the other basis, a 252-versus-253 window) must differ from the
library's value. Where a fixture records a cross-check the library is run once more on the prefix that ends one session
before the target with the prior period, and max(prior extreme, target field) must equal the window extreme bit for bit.

No expectation is computed here and the library is not used to derive one: every expected value is the contract literal
that the independent stdlib expander (`tools/contract_fixtures/dv1_fixture_expand.py`, gate
`tools/verify_dv1_fixtures.py`) recomputes. Internal, synthetic, pre-release.

Run from an environment with the packages installed: `python tools/verify_dv1_window_library.py`; exit 0 only if
everything holds.
"""
from __future__ import annotations

import copy
import json
import struct
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ContractError, Coverage, DataKind,
    InputScope, IntervalCoverage, PriceUnit, SessionSpec, SourceBinding,
)
from equity_features.dv1 import build_window_extreme_config, compute_dv1, dv1_definitions, require_dv1_capability
from equity_features.ef3 import DailyGrid

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "dv1" / "DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json"
T0 = 1_700_000_000_000_000_000
SEC = 10 ** 9
DAY = 86_400 * SEC
KA_DEFAULT = 50  # the compact notation's default known_at token, stated here and passed explicitly (fixture-only)
LABEL_OF = {"raw": "unadjusted", "split": "split_adjusted"}
HLC = {"high": 0, "low": 1, "close": 2}
PINNED_RESULTS = 25
PINNED_REFUSALS = 10
HIGH_SIDE = ("history.window_high", "history.window_high_offset")


def adjustment_spec(label: str | None, spec: dict[str, Any] | None) -> AdjustmentSpec:
    """The shared AdjustmentSpec of a declared label; shared validation faults surface as the shared refusal."""
    spec = spec or {}
    if label == "split_adjusted":
        return AdjustmentSpec(basis="split", **{k: spec[k] for k in ("policy_version", "action_snapshot", "anchor") if k in spec})
    return AdjustmentSpec(basis="raw", **({"policy_version": spec["policy_version"]} if "policy_version" in spec else {}))


def parts(cell: Any) -> tuple[Any, Any]:
    """(body, ka) of one compact cell; a dict carries a row and an own known_at token."""
    if isinstance(cell, dict):
        return cell["row"], cell["ka"]
    return cell, KA_DEFAULT


def cells_of(fx: dict[str, Any]) -> list[Any]:
    """The slot list of a fixture, expanding `slots_fill` {n, base, set}."""
    if "slots_fill" in fx:
        fill = fx["slots_fill"]
        cells = [list(fill["base"]) for _ in range(fill["n"])]
        for index, row in fill["set"].items():
            cells[int(index)] = list(row)
        return cells
    return list(fx["slots"])


def expand(fx: dict[str, Any]) -> tuple[DailyGrid, tuple[CanonicalBatch | None, ...], Any]:
    """Fixture -> (grid, role batches, config); every contract refusal is a ContractError raised here or later."""
    p = fx["params"]
    cells = cells_of(fx)
    n = len(cells)
    target = fx.get("target", n - 1)
    starts = [T0 + i * DAY for i in range(n)]
    ends = [start + DAY for start in starts]
    forming = {i for i, cell in enumerate(cells) if cell == "forming"}
    last = max(i for i in range(n) if i not in forming)  # the last delivered slot
    cutoff = ends[last]
    knowledge = cutoff + 100 * SEC

    def known(ka: Any) -> Any:
        return None if ka is None else knowledge - (100 - ka) * SEC

    sessions = tuple(SessionSpec("SYN", f"D{i}", starts[i], ends[i], "UTC") for i in range(n))
    grid = DailyGrid(fx.get("instrument_id", "X"), "SYN-CAL", "SYN-GRID", "r1", sessions, target)
    unit = PriceUnit(fx["unit"]["scale"], fx["unit"]["currency"])
    basis = adjustment_spec(fx.get("adjustment"), fx.get("adjustment_spec"))
    # Stage order of the contract: configuration is built (and refused) before any data is shaped.
    availability = AvailabilitySpec(cutoff, knowledge, knowledge)
    config = build_window_extreme_config(
        grid, availability=availability, adjustment=basis, price_unit=unit, evidence_limit=p.get("evidence_limit"),
        offset_unit=fx.get("offset_unit"), **{k: p.get(k) for k in ("policy_version", "period", "extreme_basis")})
    fields = ("close",) if p.get("extreme_basis") == "close" else ("high", "low")
    delivery = fx.get("delivery", list(range(n)))
    rows: list[tuple[int, Any, Any]] = []
    coverage: dict[int, Coverage] = {}
    for i in delivery:
        body, ka = parts(cells[i])
        if i in forming or body == "absent":
            continue
        if body == "gap":
            coverage[i] = Coverage(1, 0, False)
            continue
        rows.append((i, body, known(ka)))
        coverage[i] = Coverage(1, 1, True)
    intervals = tuple(IntervalCoverage(f"slot:{i}", starts[i], ends[i], coverage[i]) for i in sorted(coverage))
    metadata = BatchMetadata("SYN", SourceBinding("SYN-SRC", "snap1", "dv1-map1", "daily-000"),
                             Coverage(None, len(rows), False), unit, basis, "none", "shares", "declared", "reject",
                             InputScope(starts[0], ends[-1], "dv1-regular"), intervals)
    columns = (Column("instrument_id", tuple(grid.instrument_id for _ in rows)),
               Column("session_id", tuple(f"D{r[0]}" for r in rows)),
               Column("start_ns", tuple(starts[r[0]] for r in rows)),
               Column("end_ns", tuple(ends[r[0]] for r in rows)),
               *(Column(field, tuple(r[1][HLC[field]] for r in rows)) for field in fields),
               Column("known_at_ns", tuple(r[2] for r in rows)))
    return grid, (CanonicalBatch(DataKind.BAR, columns, metadata),), config


def run(fx: dict[str, Any], features: tuple[str, ...] | None = None) -> Any:
    grid, batches, config = expand(fx)
    chosen = features or tuple(fx["outputs"])
    for feature in chosen:
        require_dv1_capability(feature, "batch")
    dv1_definitions(grid, config)
    return compute_dv1(batches, grid, config, features=chosen), config


def bits(value: float) -> int:
    return int(struct.unpack(">Q", struct.pack(">d", value))[0])


def exact(want: dict[str, Any] | None, value: Any) -> bool:
    """Bit for bit: a float has the same bit pattern and hex string, an offset is the exact int (never bool or float)."""
    if want is None or value is None:
        return want is None and value is None
    if "int" in want:
        return type(value) is int and value == want["int"]
    target = float.fromhex(want["hex"])
    return type(value) is float and value.hex() == want["hex"] and bits(value) == bits(target) and bits(target) == bits(want["float64"])


def compare(fx: dict[str, Any], result: Any, config: Any, features: tuple[str, ...]) -> list[str]:
    problems: list[str] = []
    expected = fx["expected"]
    if tuple(c.feature_id for c in result.values) != tuple(sorted(features)):
        return ["selected outputs differ"]
    limit = fx["params"]["evidence_limit"]
    found: dict[str, list[str]] = {f: [] for f in features}
    for row in result.evidence:
        found[row.feature_id].append(row.row_id)
    basis = LABEL_OF[config.adjustment.basis]
    bindings = {LABEL_OF[b.metadata.adjustment.basis] for b in result.metadata.inputs}
    for column in result.values:
        quality, = (q for q in result.quality if q.feature_id == column.feature_id)
        want = expected[column.feature_id]
        value, = column.values
        got = (quality.status.value, [r.value for r in quality.reasons], quality.expected, quality.observed)
        literal = (want["status"], want["reasons"], want["expected"], want["observed"])
        if not exact(want["value"], value) or got != literal:
            problems.append(f"{column.feature_id}: value {value!r} {got} != {want['value']} {literal}")
        offset = column.feature_id.endswith("_offset")
        if (column.dtype.value, column.unit) != (("int64", fx["offset_unit"]) if offset else ("float64", "currency/share")):
            problems.append(f"{column.feature_id}: dtype/unit {column.dtype.value}/{column.unit}")
        if want["basis"] != basis or bindings != {basis}:
            problems.append(f"{column.feature_id}: basis {basis} {bindings} != {want['basis']}")
        if len(features) == 1 and found[column.feature_id] != want["witnesses"]:
            problems.append(f"{column.feature_id}: witnesses {found[column.feature_id]} != {want['witnesses']}")
    if len(features) > 1:
        flat = [w for f in sorted(features) for w in found[f]]
        joint = [w for f in sorted(features) for w in expected[f]["witnesses"]]
        # The evidence limit bounds the whole result list, as in EF3 and EF5.
        if flat != joint[:limit] or any(len(found[f]) > limit for f in features):
            problems.append(f"joint evidence {flat} != {joint[:limit]}")
    return problems


def rival_problems(fx: dict[str, Any], result: Any) -> list[str]:
    """Each recorded rival convention differs from the library's value (unless the record is marked equal)."""
    problems: list[str] = []
    values = {c.feature_id: c.values[0] for c in result.values}
    for rival in fx.get("wrong_convention", []):
        got = values.get(rival["output"])
        literal: Any = rival["int"] if "int" in rival else float(Fraction(rival["exact"]))
        if got == literal and not rival.get("equal"):
            problems.append(f"{rival['output']}: value equals the rival {rival['convention']} {literal!r}")
    return problems


def cross_problems(fx: dict[str, Any], result: Any) -> list[str]:
    """max(prior extreme over P-1 sessions ending before the target, target high) equals the window high, bit for bit."""
    prior = fx["cross_check"]["prior_period"]
    cells = cells_of(fx)
    target = fx.get("target", len(cells) - 1)
    shifted = copy.deepcopy(fx)
    shifted["target"] = target - 1
    shifted["params"]["period"] = prior
    shifted["params"]["extreme_basis"] = "intraday"
    shifted["outputs"] = ["history.window_high", "history.window_low"]
    try:
        before, _ = run(shifted)
    except ContractError as error:
        return [f"prior-period run refused {error.code.name}: {error}"]
    got = {c.feature_id: c.values[0] for c in before.values}
    scale = fx["unit"]["scale"]
    high_t, low_t = cells[target][0], cells[target][1]
    window = {c.feature_id: c.values[0] for c in result.values}
    problems = []
    for name, field, pick in (("history.window_high", high_t, max), ("history.window_low", low_t, min)):
        merged = pick(got[name], float(Fraction(field, 10 ** scale)))
        if window[name] is None or window[name].hex() != merged.hex():
            problems.append(f"{name}: window {window[name]!r} != {pick.__name__}(prior {got[name]!r}, target {field})")
    return problems


def apply(base: dict[str, Any], mutations: list[dict[str, Any]]) -> dict[str, Any]:
    fx = copy.deepcopy(base)
    for step in mutations:
        keys = (step.get("delete") or step["set"]).split(".")[1:]
        cursor: Any = fx
        for key in keys[:-1]:
            cursor = cursor[int(key)] if isinstance(cursor, list) else cursor[key]
        last: Any = int(keys[-1]) if isinstance(cursor, list) else keys[-1]
        if "delete" in step:
            del cursor[last]
        else:
            cursor[last] = step["value"]
    return fx


def main() -> int:
    doc = json.loads(CONTRACT.read_text(encoding="utf-8"))
    by_id = {fx["id"]: fx for fx in doc["window_fixtures"]}
    refusals = [rf for rf in doc["refusal_fixtures"] if rf["base"] in by_id]
    problems: list[str] = []
    if (len(by_id), len(refusals)) != (PINNED_RESULTS, PINNED_REFUSALS):
        problems.append(f"pinned counts {(PINNED_RESULTS, PINNED_REFUSALS)} != contract {(len(by_id), len(refusals))}")
    runs = 0
    for fx in by_id.values():
        outputs = tuple(sorted(fx["expected"]))
        for features in [(f,) for f in outputs] + [outputs]:
            runs += 1
            try:
                result, config = run(fx, features)
            except ContractError as error:
                problems.append(f"{fx['id']} {features}: refused {error.code.name}: {error}")
                continue
            problems += [f"{fx['id']}: {p}" for p in compare(fx, result, config, features)]
            if features == outputs:
                problems += [f"{fx['id']}: {p}" for p in rival_problems(fx, result)]
                if fx.get("cross_check"):
                    problems += [f"{fx['id']}: {p}" for p in cross_problems(fx, result)]
    codes: set[str] = set()
    for rf in refusals:
        mutated = apply(by_id[rf["base"]], rf["mutation"])
        try:
            run(mutated)
        except ContractError as error:
            codes.add(error.code.name)
            if error.code.name != rf["error_code"]:
                problems.append(f"{rf['id']}: refused {error.code.name} expected {rf['error_code']} ({error})")
        else:
            problems.append(f"{rf['id']}: not refused (expected {rf['error_code']})")
    for line in problems:
        print("MISMATCH", line)
    if problems:
        print(f"{len(problems)} MISMATCH(ES)")
        return 1
    print(f"DV1 window library: {len(by_id)} window-extreme result fixtures ({runs} runs, bit for bit) and "
          f"{len(refusals)} refusals ({len(codes)} codes) match the contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
