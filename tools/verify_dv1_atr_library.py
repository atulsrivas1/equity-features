"""Drive every DV1-2 contract fixture through the pure library (`equity_features.dv1` simple-mean ATR producer).

For each of the 20 ATR result fixtures (AT01..AT20) the compact notation (slots of [high, low, close] cells) is expanded
to one high/low/close daily BAR role, a governed daily grid and a final configuration (market cutoff C is the end of the
last delivered slot, a forming slot is delivered by nothing, K = C + 100 s, `ka` maps to K - (100 - ka) s, exactly as the
contract states) and the library result is compared with the contract literal BIT FOR BIT: the float64 hex string and sign
of the value (there is no tolerance band in DV1), status, reasons, expected and observed counts, witnesses and the echoed
adjustment basis. For each of the 27 refusal recipes whose base is an ATR fixture the recorded mutation is applied and
the library must refuse with exactly the recorded error code (the wire-stage row-width check belongs to the compact
notation, so the gate's decoder raises it; the library never sees a malformed row).

The wrong-convention rivals recorded in the contract (Wilder ATR, prior-only mean, high-minus-low-only mean) must differ
from the library value (the two records where the conventions coincide, AT02 and AT04, must be equal), and the shipped
Wilder `history.atr`, run through its own public path with an explicit anchor at session 1, must reproduce the recorded
Wilder rival, so the two conventions are shown apart on the same inputs and `history.atr` is shown unchanged.

No expectation is computed here and the library is not used to derive one: every expected value is the contract literal
that the independent stdlib expander (`tools/contract_fixtures/dv1_fixture_expand.py`, gate
`tools/verify_dv1_fixtures.py`) recomputes. Internal, synthetic, pre-release.

Run from an environment with the packages installed: `python tools/verify_dv1_atr_library.py`; exit 0 only if everything holds.
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
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, ContractError, Coverage,
    DataKind, EntityKey, ErrorCode, InputScope, IntervalCoverage, Parameter, PriceUnit, SessionSpec, SourceBinding,
    WindowSpec,
)
from equity_feature_contracts.history import HistoryContext
from equity_features.dv1 import build_atr_simple_mean_config, compute_dv1, dv1_definitions, require_dv1_capability
from equity_features.ef3 import DailyGrid
from equity_features.history import compute_history

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "dv1" / "DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json"
T0 = 1_700_000_000_000_000_000
SEC = 10 ** 9
DAY = 86_400 * SEC
KA_DEFAULT = 50  # the compact notation's default known_at token, stated here and passed explicitly (fixture-only)
BASIS = {"unadjusted": "raw", "split_adjusted": "split"}
LABEL_OF = {"raw": "unadjusted", "split": "split_adjusted"}
FEATURE = "history.atr_simple_mean"
COINCIDE = {"AT02", "AT04"}  # the two records where the Wilder rival equals the simple mean by construction
PINNED_RESULTS = 20
PINNED_REFUSALS = 27


def adjustment_spec(label: str | None, spec: dict[str, Any] | None) -> AdjustmentSpec | None:
    """The shared AdjustmentSpec of a declared label (None when undeclared); shared validation faults surface as such."""
    if label is None:
        return None
    spec = spec or {}
    fields = {k: spec[k] for k in ("policy_version", "action_snapshot", "anchor") if k in spec}
    return AdjustmentSpec(basis=BASIS.get(label, label), **fields)


def parts(cell: Any) -> tuple[Any, Any]:
    """(body, ka) of one compact cell; a dict carries a row and an own known_at token."""
    if isinstance(cell, dict):
        return cell["row"], cell["ka"]
    return cell, KA_DEFAULT


def decode_row(body: Any) -> tuple[Any, Any, Any]:
    """Wire stage of the compact notation: a slot row is exactly [high, low, close]."""
    if not isinstance(body, list) or len(body) != 3:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "a slot row is exactly [high, low, close]")
    return body[0], body[1], body[2]


def expand(fx: dict[str, Any]) -> tuple[DailyGrid, tuple[CanonicalBatch | None, ...], ConfigSpec]:
    """Fixture -> (grid, daily role batches, config); every contract refusal is a ContractError raised here or later."""
    assert "slots_fill" not in fx, "slots_fill is not used by the ATR fixtures"
    p = fx["params"]
    slots = fx["slots"]
    n = len(slots)
    starts = [T0 + i * DAY for i in range(n)]
    ends = [start + DAY for start in starts]
    forming = {i for i, cell in enumerate(slots) if cell == "forming"}
    last = max(i for i in range(n) if i not in forming)  # the last delivered slot
    cutoff = ends[last - 1] if fx.get("delivered_after_cutoff") else ends[last]
    knowledge = cutoff + 100 * SEC

    def known(ka: Any) -> Any:
        return None if ka is None else knowledge - (100 - ka) * SEC

    sessions = tuple(SessionSpec("SYN", f"D{i}", starts[i], ends[i], "UTC") for i in range(n))
    grid = DailyGrid(fx.get("instrument_id", "X"), "SYN-CAL", "SYN-GRID", "r1", sessions, fx.get("target", n - 1))
    unit = PriceUnit(fx["unit"]["scale"], fx["unit"]["currency"])
    basis = adjustment_spec(fx.get("adjustment"), fx.get("adjustment_spec"))
    # Stage order of the contract: configuration is built (and refused) before any data is shaped.
    availability = AvailabilitySpec(cutoff, knowledge, knowledge)
    config = build_atr_simple_mean_config(
        grid, policy_version=p.get("policy_version"), period=p.get("period"), availability=availability,
        adjustment=basis, price_unit=unit, evidence_limit=p.get("evidence_limit"))
    assert basis is not None  # an undeclared adjustment was refused by the configuration above
    delivery = fx.get("delivery", list(range(n)))
    rows: list[tuple[int, tuple[Any, Any, Any], Any]] = []
    coverage: dict[int, Coverage] = {}
    for i in delivery:
        body, ka = parts(slots[i])
        if i in forming or body == "absent":
            continue
        if body == "gap":
            coverage[i] = Coverage(1, 0, False)
            continue
        rows.append((i, decode_row(body), known(ka)))
        coverage[i] = Coverage(1, 1, True)
    if fx.get("coverage") == "undeclared":
        coverage = {}
    elif fx.get("coverage") == "partial":
        coverage.pop(delivery[0], None)  # the oldest delivered slot has no coverage entry
    intervals = tuple(IntervalCoverage(f"slot:{i}", starts[i], ends[i], coverage[i]) for i in sorted(coverage))
    instrument = fx.get("batch_instrument", grid.instrument_id)
    metadata = BatchMetadata("SYN", SourceBinding("SYN-SRC", "snap1", "dv1-map1", "daily-000"),
                             Coverage(None, len(rows), False), unit, basis, "none", "shares", "declared", "reject",
                             InputScope(starts[0], ends[-1], "dv1-regular"), intervals)
    columns = (Column("instrument_id", tuple(instrument for _ in rows)),
               Column("session_id", tuple(f"D{r[0]}" for r in rows)),
               Column("start_ns", tuple(starts[r[0]] for r in rows)),
               Column("end_ns", tuple(ends[r[0]] for r in rows)),
               Column("high", tuple(r[1][0] for r in rows)),
               Column("low", tuple(r[1][1] for r in rows)),
               Column("close", tuple(r[1][2] for r in rows)),
               Column("known_at_ns", tuple(r[2] for r in rows)))
    batch = CanonicalBatch(DataKind.BAR, columns, metadata)
    return grid, (batch,), config


def run(fx: dict[str, Any]) -> tuple[Any, Any]:
    grid, batches, config = expand(fx)
    chosen = tuple(fx["outputs"])
    for feature in chosen:
        require_dv1_capability(feature, fx.get("capability", "batch"))
    definitions = dv1_definitions(grid, config)
    for definition in definitions:
        text = definition.formula
        if "SIMPLE" not in text or "Wilder" not in text or "history.atr" not in text:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "discovery description does not name the convention")
    return compute_dv1(batches, grid, config, features=chosen), config


def bits(value: float) -> int:
    return int(struct.unpack(">Q", struct.pack(">d", value))[0])


def exact(want: dict[str, Any] | None, value: Any) -> bool:
    """Bit for bit: same float64 bit pattern (so the same sign of zero) and the same hex string."""
    if want is None or value is None:
        return want is None and value is None
    target = float.fromhex(want["hex"])
    return (type(value) is float and value.hex() == want["hex"] and bits(value) == bits(target)
            and bits(target) == bits(want["float64"]))


def compare(fx: dict[str, Any], result: Any, config: Any) -> list[str]:
    problems: list[str] = []
    want = fx["expected"][FEATURE]
    if tuple(c.feature_id for c in result.values) != (FEATURE,):
        return ["selected outputs differ"]
    column, = result.values
    quality, = result.quality
    value, = column.values
    got = (quality.status.value, [r.value for r in quality.reasons], quality.expected, quality.observed)
    literal = (want["status"], want["reasons"], want["expected"], want["observed"])
    if not exact(want["value"], value) or got != literal:
        problems.append(f"value {value!r} {got} != {want['value']} {literal}")
    if column.unit != f"{config.price_unit.currency}/share" or column.dtype.value != "float64":
        problems.append(f"unit/dtype {column.unit} {column.dtype}")
    basis = LABEL_OF[config.adjustment.basis]
    bindings = {LABEL_OF[b.metadata.adjustment.basis] for b in result.metadata.inputs}
    if want["basis"] != basis or (bindings and bindings != {basis}):
        problems.append(f"basis {basis} {bindings} != {want['basis']}")
    witnesses = [row.row_id for row in result.evidence]
    if witnesses != want["witnesses"]:
        problems.append(f"witnesses {witnesses} != {want['witnesses']}")
    if value is None and result.evidence:
        problems.append("an unavailable output emitted evidence")
    return problems


def shipped_wilder(fx: dict[str, Any]) -> float:
    """The shipped Wilder `history.atr` through its public path (anchor at session 1, all sessions delivered)."""
    n = len(fx["slots"])
    p = fx["params"]
    sessions = tuple(SessionSpec("synthetic", f"S{i}", i * 10 + 1, i * 10 + 10, "supplied") for i in range(n))
    rows = [decode_row(parts(cell)[0]) for cell in fx["slots"]]
    values = dict(instrument_id=("A",) * n, session_id=tuple(s.session_id for s in sessions),
                  start_ns=tuple(s.open_ns for s in sessions), end_ns=tuple(s.close_ns for s in sessions),
                  high=tuple(r[0] for r in rows), low=tuple(r[1] for r in rows), close=tuple(r[2] for r in rows),
                  known_at_ns=tuple(s.close_ns for s in sessions))
    unit = PriceUnit(fx["unit"]["scale"], fx["unit"]["currency"])
    batch = CanonicalBatch(DataKind.DAILY, tuple(Column(name, val) for name, val in values.items()),
                           BatchMetadata("synthetic", SourceBinding("fixture", "r1", "v1", "prices"),
                                         Coverage(n, n, True), unit))
    target = sessions[n - 1]
    context = HistoryContext(EntityKey("A", target.session_id), "grid-v1", sessions,
                             tuple(Coverage(1, 1, True) for _ in range(n)), initialization_anchor="S1")
    config = ConfigSpec(identity="history", algorithm_version="v1",
                        parameters=(Parameter("period", p["period"]), Parameter("evidence_limit", 0)),
                        session=target, window=WindowSpec(p["period"], target.session_id,
                                                          tuple(s.session_id for s in sessions), "completed_eod"),
                        availability=AvailabilitySpec(target.close_ns, target.close_ns + 5, target.close_ns + 5),
                        price_unit=unit)
    result = compute_history(batch, config, context=context, feature_ids=("history.atr",))
    value = result.values[0].values[0]
    assert type(value) is float
    return value


def rival_problems(fx: dict[str, Any], result: Any) -> list[str]:
    """Each recorded rival differs from the library value (equal only where the contract records the coincidence)."""
    problems: list[str] = []
    value = result.values[0].values[0]
    for rival in fx.get("wrong_convention", []):
        literal = float(Fraction(rival["exact"]))
        equal = value == literal
        if rival["convention"] == "wilder_atr" and fx["id"] in COINCIDE:
            if not equal:
                problems.append(f"{rival['convention']}: recorded coincidence {literal!r} != library {value!r}")
        elif equal:
            problems.append(f"{rival['convention']}: library value equals the rival {literal!r}")
        if rival["convention"] == "wilder_atr":
            shipped = shipped_wilder(fx)
            if shipped != literal and abs(shipped - literal) > 1e-15 * abs(literal):
                problems.append(f"history.atr (Wilder) {shipped!r} differs from the contract rival {literal!r}")
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
    by_id = {fx["id"]: fx for fx in doc["atr_fixtures"]}
    refusals = [rf for rf in doc["refusal_fixtures"] if rf["base"] in by_id]
    problems: list[str] = []
    if (len(by_id), len(refusals)) != (PINNED_RESULTS, PINNED_REFUSALS):
        problems.append(f"pinned counts {(PINNED_RESULTS, PINNED_REFUSALS)} != contract {(len(by_id), len(refusals))}")
    coincide = 0
    for fx in by_id.values():
        try:
            result, config = run(fx)
        except ContractError as error:
            problems.append(f"{fx['id']}: refused {error.code.name}: {error}")
            continue
        problems += [f"{fx['id']}: {p}" for p in compare(fx, result, config)]
        problems += [f"{fx['id']}: {p}" for p in rival_problems(fx, result)]
        coincide += int(fx["id"] in COINCIDE)
    if coincide != len(COINCIDE):
        problems.append("the two recorded coincidence fixtures (AT02, AT04) are missing")
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
    # RF73 (contract text): coverage declared for only some delivered slots is the recorded code; its base is a window
    # fixture, so the same mutation is applied here to an ATR base and the expected code is read from the contract.
    rf73 = next(rf for rf in doc["refusal_fixtures"] if rf["id"] == "RF73")
    partial = apply(by_id["AT01"], rf73["mutation"])
    try:
        run(partial)
    except ContractError as error:
        codes.add(error.code.name)
        if error.code.name != rf73["error_code"]:
            problems.append(f"RF73 on AT01: refused {error.code.name} expected {rf73['error_code']} ({error})")
    else:
        problems.append(f"RF73 on AT01: not refused (expected {rf73['error_code']})")
    for line in problems:
        print("MISMATCH", line)
    if problems:
        print(f"{len(problems)} MISMATCH(ES)")
        return 1
    print(f"DV1 ATR library: {len(by_id)} simple-mean ATR result fixtures (bit for bit) and {len(refusals)} refusals plus RF73 on AT01 "
          f"({len(codes)} codes) match the contract; the Wilder rivals differ and shipped history.atr reproduces them")
    return 0


if __name__ == "__main__":
    sys.exit(main())
