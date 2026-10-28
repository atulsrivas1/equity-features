"""Drive every EF5 contract fixture through the pure library (`equity_features_intraday` EF5 producers).

For each of the 89 result fixtures (candle, structure, technical, known_at KA-set) the compact notation is expanded
to supplied BAR chunks, a governed grid context and a final configuration (market cutoff C is the end of the last
delivered slot, K = C + 100 s, `ka` maps to K - (100 - ka) s, exactly as the contract states), every selected output is
run alone and jointly, and the library result is compared with the contract literal: value by the contract acceptance
rule, status, reasons, expected and observed counts, witnesses and the echoed adjustment basis. For each of the 57
refusal recipes the recorded mutation is applied to its base fixture and the library must refuse with exactly the
recorded error code. No fixture value is computed here: the expectations are the contract literals that the independent
stdlib expander (`tools/contract_fixtures/ef5_fixture_expand.py`, gate `tools/verify_ef5_fixtures.py`) recomputes.

Run from an environment with the packages installed: `python tools/verify_ef5_library.py`; exit 0 only if everything holds.
"""
from __future__ import annotations

import copy
import importlib.util
import json
import math
import sys
from pathlib import Path
from typing import Any

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ContractError, Coverage, DataKind,
    ErrorCode, InputScope, IntervalCoverage, PriceUnit, SessionSpec, SourceBinding,
)
from equity_features_intraday import (
    ADJUSTMENT_LABELS, IntradayContext, IntradayRun, build_ef5_config, compute_ef5, require_ef5_capability,
)

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "ef5" / "PRICE_STRUCTURES_CONTRACT_PROPOSAL.json"
EXPANDER = ROOT / "tools" / "contract_fixtures" / "ef5_fixture_expand.py"
T0 = 1_700_000_000_000_000_000
SEC = 10 ** 9
BAR = 60 * SEC
DAY = 86_400 * SEC
KA_DEFAULT = 50  # the compact notation's default known_at token, stated here and passed explicitly (fixture-only)
LISTS = ("candle_fixtures", "structure_fixtures", "technical_fixtures", "ka_fixtures")
MODE = {"session_reset": "reset", "governed_history": "carry"}
LABEL_OF = {"raw": "unadjusted", "split": "split_adjusted"}


def load_expander() -> Any:
    spec = importlib.util.spec_from_file_location("ef5_fixture_expand", EXPANDER)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def ends(fx: dict[str, Any], n: int) -> list[int]:
    if fx.get("grid") == "daily":
        offsets = fx.get("ends_s")
        return [T0 + (offsets[i] if offsets else (i + 1) * 86400) * SEC for i in range(n)]
    return [T0 + (i + 1) * BAR for i in range(n)]


def starts(fx: dict[str, Any], n: int) -> list[int]:
    width = DAY if fx.get("grid") == "daily" else BAR
    return [end - width for end in ends(fx, n)]


def adjustment_spec(label: str | None, spec: dict[str, Any] | None) -> AdjustmentSpec:
    """The shared AdjustmentSpec of a declared label; shared validation faults surface as the shared refusal."""
    spec = spec or {}
    if label == "split_adjusted":
        kwargs = {k: spec[k] for k in ("policy_version", "action_snapshot", "anchor") if k in spec}
        return AdjustmentSpec(basis="split", **kwargs)
    return AdjustmentSpec(basis="raw", **({"policy_version": spec["policy_version"]} if "policy_version" in spec else {}))


def expand(fx: dict[str, Any]) -> tuple[Any, Any, Any, tuple[str, ...], str]:
    """Fixture -> (context, chunks, config, features, call); every contract refusal is a ContractError raised here or later."""
    p = fx["params"]
    n_all = fx.get("target", len(fx["slots"]) - 1) + 1
    slots = fx["slots"][:n_all]
    n = len(slots)
    daily = fx.get("grid") == "daily"
    end_ns, start_ns = ends(fx, n), starts(fx, n)
    forming = slots[-1] == "forming"
    cutoff = (end_ns[n - 2] if n >= 2 else start_ns[0]) if forming else end_ns[-1]
    knowledge = cutoff + 100 * SEC
    cols = ("open", "high", "low", "close", "volume") if fx.get("columns", "ohlcv") == "ohlcv" else ("close",)
    width = len(cols)
    label = fx.get("adjustment")

    def known(ka: Any) -> Any:
        return ka if ka is None or isinstance(ka, float) else knowledge - (100 - ka) * SEC

    if daily:
        sessions = tuple(SessionSpec("SYN", f"D{i}", start_ns[i], end_ns[i], "UTC") for i in range(n))
        runs = tuple(IntradayRun(f"D{i}", start_ns[i], DAY, 1) for i in range(n))
    else:
        sessions = (SessionSpec("SYN", "S1", T0, T0 + n * BAR, "UTC"),)
        runs = (IntradayRun("S1", T0, BAR, n),)
    profile = p.get("epoch_profile")
    context = IntradayContext("X", "SYN-CAL", "SYN-GRID", "r1", sessions, runs, 0, n - 1, MODE.get(profile, "reset"))
    unit = PriceUnit(fx["unit"]["scale"], fx["unit"]["currency"])
    basis = adjustment_spec(label, fx.get("adjustment_spec"))
    # rows: (slot index, identity tuple, values, known_at, row basis)
    rows: list[tuple[int, str, str, int, int, tuple[Any, ...], Any, str | None]] = []
    coverage: dict[int, tuple[int, int, bool]] = {}
    row_basis: str | None = None
    for i, slot in enumerate(slots):
        body, ka, _ = (slot.get("row"), slot.get("ka", KA_DEFAULT), None) if isinstance(slot, dict) else (slot, KA_DEFAULT, None)
        wire: dict[str, Any] = {}
        versions: list[dict[str, Any]] | None = None
        if isinstance(slot, dict):
            wire = slot.get("wire", {})
            versions = slot.get("versions")
            body = wire.get("row", body) if wire else body
            ka = wire.get("ka", ka) if wire else ka
        if isinstance(slot, str) and slot != "null":
            if slot == "gap":
                coverage[i] = (1, 0, False)
            elif slot == "empty":
                coverage[i] = (0, 0, True)
            continue
        if slot == "null":
            body = [None] * width
        for version in versions or [{"ka": ka}]:
            values = tuple(body) if body is not None else (None,) * width
            if len(values) != width:
                raise ContractError(ErrorCode.INVALID_SCHEMA, "row width differs from the delivered columns")
            ident = ("X" if "inst" not in wire else wire["inst"], wire.get("ss", f"D{i}" if daily else "S1"),
                     wire.get("start", start_ns[i]), wire.get("end", end_ns[i]))
            rows.append((i, *ident, values, known(version["ka"] if "ka" in version else ka), wire.get("basis")))
        coverage[i] = (1, 1, True)
        if wire.get("basis") is not None:
            row_basis = wire["basis"]
    chunk_adjustment = basis if row_basis is None else adjustment_spec(row_basis, {"policy_version": "split-factors-v1",
                                                                       "action_snapshot": "snap", "anchor": "anchor"})
    declared = fx.get("coverage", "declared") == "declared"
    names = ("instrument_id", "session_id", "start_ns", "end_ns", *cols, "known_at_ns")
    chunks: list[CanonicalBatch] = []
    for session in sessions:
        members = [i for i in range(n) if (f"D{i}" if daily else "S1") == session.session_id]
        chunk_rows = [r for r in rows if r[0] in members]
        intervals = tuple(IntervalCoverage(f"slot:{i}", start_ns[i], end_ns[i], Coverage(*coverage[i]))
                          for i in members if i in coverage and declared)
        metadata = BatchMetadata("SYN", SourceBinding("SYN-SRC", "snap1", "ef5-map1", f"bars-{len(chunks):03}"),
                                 Coverage(None, len(chunk_rows), False), unit, chunk_adjustment, "none", "shares",
                                 "declared", "reject", InputScope(session.open_ns, session.close_ns, "ef5-regular"),
                                 intervals)
        columns = tuple(Column(name, tuple(r[1 + j] if j < 4 else None for r in chunk_rows)) for j, name in
                        enumerate(names[:4]))
        data = tuple(Column(name, tuple(r[5][j] for r in chunk_rows)) for j, name in enumerate(cols))
        stamps = (Column("known_at_ns", tuple(r[6] for r in chunk_rows)),)
        chunk = CanonicalBatch(DataKind.BAR, columns + data + stamps, metadata)
        chunks.append(chunk)
    params = {k: p.get(k) for k in ("policy_version", "epoch_profile", "evidence_limit")}
    for name in ("doji_body_max_fraction", "swing_strength", "lookback", "trend_window", "trend_count"):
        if fx["producer"] == {"doji_body_max_fraction": "candle", "swing_strength": "structure", "lookback": "structure",
                              "trend_window": "technical", "trend_count": "technical"}[name]:
            params[name] = p.get(name)
    extra = {k: v for k, v in p.items() if k not in params}
    config = build_ef5_config(
        fx["producer"], context, availability=AvailabilitySpec(cutoff, knowledge, knowledge), adjustment=basis,
        price_unit=unit, adjustment_label=label, adjustment_policy_version=(fx.get("adjustment_spec") or {}).get(
            "policy_version"), **params, **extra)
    context_for_call = None if ("context" in fx and fx["context"] is None) else context
    return context_for_call, tuple(chunks), config, tuple(fx["outputs"]), fx.get("call", "compute")


def run(fx: dict[str, Any], features: tuple[str, ...] | None = None) -> Any:
    context, chunks, config, outputs, call = expand(fx)
    chosen = features or outputs
    if call != "compute":
        for feature in chosen:
            require_ef5_capability(feature, call)
    return compute_ef5(fx["producer"], chunks, context, config, features=chosen), config


def accepts(want: dict[str, Any] | None, value: Any) -> bool:
    if want is None or value is None:
        return want is None and value is None
    if "bool" in want:
        return bool(type(value) is bool and value is want["bool"])
    if "int" in want:
        return type(value) is int and value == want["int"]
    r = float.fromhex(want["hex"])
    if want["acceptance"] in ("exact_float64", "exact_plus_zero"):
        return value.hex() == r.hex() and math.copysign(1.0, value) == math.copysign(1.0, r)
    return abs(value - r) <= max(8 * math.ulp(r), 1e-12 * abs(r))


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
        if not accepts(want["value"], value) or got != literal:
            problems.append(f"{column.feature_id}: value {value!r} {got} != {want['value']} {literal}")
        if want["basis"] != basis or bindings - {basis}:
            problems.append(f"{column.feature_id}: basis {basis} {bindings} != {want['basis']}")
        if len(features) == 1 and found[column.feature_id] != want["witnesses"]:
            problems.append(f"{column.feature_id}: witnesses {found[column.feature_id]} != {want['witnesses']}")
    if len(features) > 1:
        flat = [r.row_id for r in result.evidence]
        joint = [w for f in sorted(features) for w in expected[f]["witnesses"]][:limit]
        if flat != joint:
            problems.append(f"joint evidence {flat} != {joint}")
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
    by_id = {fx["id"]: fx for key in LISTS for fx in doc[key]}
    problems: list[str] = []
    runs = 0
    for fx in by_id.values():
        outputs = tuple(sorted(fx["expected"]))
        for features in [(f,) for f in outputs] + ([outputs] if len(outputs) > 1 else []):
            runs += 1
            try:
                result, config = run(fx, features)
            except ContractError as error:
                problems.append(f"{fx['id']} {features}: refused {error.code.name}: {error}")
                continue
            problems += [f"{fx['id']}: {p}" for p in compare(fx, result, config, features)]
    codes: set[str] = set()
    for rf in doc["refusal_fixtures"]:
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
    print(f"EF5 library: {len(by_id)} result fixtures ({runs} runs) and {len(doc['refusal_fixtures'])} refusals "
          f"({len(codes)} codes) match the contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
