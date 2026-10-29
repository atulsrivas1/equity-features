"""Drive every DV1-1 contract fixture through the pure library (`equity_features.dv1` relative log-return producer).

For each of the 23 relative-log result fixtures (RL01..RL23) the compact notation is expanded to two close-only daily
BAR roles, a governed daily grid and a final configuration (market cutoff C is the end of the last delivered slot, a
forming slot is delivered by neither series, K = C + 100 s, `ka` maps to K - (100 - ka) s, exactly as the contract
states); every selected output is run alone and jointly and the library result is compared with the contract literal
BIT FOR BIT: the float64 hex string and sign of the value (there is no tolerance band in DV1), status, reasons, expected
and observed counts, witnesses and the echoed adjustment basis. For each of the 12 refusal recipes whose base is a
relative-log fixture the recorded mutation is applied and the library must refuse with exactly the recorded error code.
The wrong-convention rivals recorded in the contract (simple-return beta and correlation) must differ from the
library's log value, and the shipped simple-return producer (`relative.beta`, `relative.correlation`, ef3-rel1) must
reproduce those rival literals, so the two conventions are shown apart on the same inputs.

No expectation is computed here and the library is not used to derive one: every expected value is the contract literal
that the independent stdlib expander (`tools/contract_fixtures/dv1_fixture_expand.py`, gate
`tools/verify_dv1_fixtures.py`) recomputes at 250 digits. Internal, synthetic, pre-release.

Run from an environment with the packages installed: `python tools/verify_dv1_library.py`; exit 0 only if everything holds.
"""
from __future__ import annotations

import copy
import json
import struct
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ContractError, Coverage, DataKind,
    InputScope, IntervalCoverage, PriceUnit, SessionSpec, SourceBinding,
)
from equity_features.dv1 import build_relative_log_config, compute_dv1, dv1_definitions, require_dv1_capability
from equity_features.ef3 import DailyGrid, build_relative_stats_config, compute_ef3

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "dv1" / "DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json"
T0 = 1_700_000_000_000_000_000
SEC = 10 ** 9
DAY = 86_400 * SEC
KA_DEFAULT = 50  # the compact notation's default known_at token, stated here and passed explicitly (fixture-only)
LABEL_OF = {"raw": "unadjusted", "split": "split_adjusted"}
SIMPLE = {"relative.log_return_beta": "relative.beta", "relative.log_return_correlation": "relative.correlation"}
PINNED_RESULTS = 23
PINNED_REFUSALS = 12


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


def expand(fx: dict[str, Any], simple: bool = False, deliver_forming: bool = False) -> tuple[DailyGrid, tuple[CanonicalBatch | None, ...], Any]:
    """Fixture -> (grid, role batches, config); every contract refusal is a ContractError raised here or later."""
    p = fx["params"]
    series = {"instrument": fx["inst"], "benchmark": fx["bench"]}
    n = len(next(s for s in series.values() if s != "absent"))
    target = fx.get("target", n - 1)
    starts = [T0 + i * DAY for i in range(n)]
    ends = [start + DAY for start in starts]
    forming = {i for s in series.values() if s != "absent" for i, cell in enumerate(s) if cell == "forming"}
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
    kwargs = {k: p.get(k) for k in ("policy_version", "benchmark_id", "window", "min_pairs")}
    if simple:
        kwargs["policy_version"] = "ef3-rel1"
        config = build_relative_stats_config(grid, availability=availability, adjustment=basis, price_unit=unit,
                                             evidence_limit=p["evidence_limit"], **kwargs)
    else:
        config = build_relative_log_config(grid, availability=availability, adjustment=basis, price_unit=unit,
                                           evidence_limit=p["evidence_limit"], **kwargs)
    delivery = fx.get("delivery", list(range(n)))
    batches: list[CanonicalBatch | None] = []
    for role, instrument in (("instrument", grid.instrument_id), ("benchmark", p.get("benchmark_id"))):
        cells = series[role]
        if cells == "absent":
            batches.append(None)
            continue
        rows: list[tuple[int, Any, Any]] = []
        coverage: dict[int, Coverage] = {}
        for i in delivery:
            body, ka = parts(cells[i])
            if (i in forming and not deliver_forming) or body == "absent":
                continue
            if body == "gap":
                coverage[i] = Coverage(1, 0, False)
                continue
            if i in forming and body == "forming":
                continue  # the forming cell itself never carries a value
            rows.append((i, body, known(ka)))
            coverage[i] = Coverage(1, 1, True)
        intervals = tuple(IntervalCoverage(f"slot:{i}", starts[i], ends[i], coverage[i]) for i in sorted(coverage))
        tag = "inst" if role == "instrument" else "bench"
        metadata = BatchMetadata("SYN", SourceBinding("SYN-SRC", "snap1", "dv1-map1", f"{tag}-000"),
                                 Coverage(None, len(rows), False), unit, basis, "none", "shares", "declared", "reject",
                                 InputScope(starts[0], ends[-1], "dv1-regular"), intervals)
        columns = (Column("instrument_id", tuple(instrument for _ in rows)),
                   Column("session_id", tuple(f"D{r[0]}" for r in rows)),
                   Column("start_ns", tuple(starts[r[0]] for r in rows)),
                   Column("end_ns", tuple(ends[r[0]] for r in rows)),
                   Column("close", tuple(r[1] for r in rows)),
                   Column("known_at_ns", tuple(r[2] for r in rows)))
        batches.append(CanonicalBatch(DataKind.BAR, columns, metadata))
    return grid, tuple(batches), config


def run(fx: dict[str, Any], features: tuple[str, ...] | None = None, simple: bool = False) -> Any:
    grid, batches, config = expand(fx, simple)
    chosen = features or tuple(fx["outputs"])
    if simple:
        return compute_ef3(batches, grid, config, features=chosen), config
    for feature in chosen:
        require_dv1_capability(feature, "batch")
    dv1_definitions(grid, config)
    return compute_dv1(batches, grid, config, features=chosen), config


def bits(value: float) -> int:
    return int(struct.unpack(">Q", struct.pack(">d", value))[0])


def exact(want: dict[str, Any] | None, value: Any) -> bool:
    """Bit for bit: same float64 bit pattern (so the same sign of zero) and the same hex string."""
    if want is None or value is None:
        return want is None and value is None
    target = float.fromhex(want["hex"])
    return type(value) is float and value.hex() == want["hex"] and bits(value) == bits(target) and bits(target) == bits(want["float64"])


def compare(fx: dict[str, Any], result: Any, config: Any, features: tuple[str, ...]) -> list[str]:
    problems: list[str] = []
    expected = fx["expected"]
    if tuple(c.feature_id for c in result.values) != tuple(sorted(features)):
        return ["selected outputs differ"]
    limit = fx["params"]["evidence_limit"]
    role_of = {b.metadata.source.input_id: b.role for b in result.metadata.inputs}
    found: dict[str, list[str]] = {f: [] for f in features}
    for row in result.evidence:
        found[row.feature_id].append(f"{role_of[row.input_id]}/{row.row_id}")
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
        if want["basis"] != basis or bindings != {basis}:
            problems.append(f"{column.feature_id}: basis {basis} {bindings} != {want['basis']}")
        if len(features) == 1 and found[column.feature_id] != want["witnesses"]:
            problems.append(f"{column.feature_id}: witnesses {found[column.feature_id]} != {want['witnesses']}")
    if len(features) > 1:
        flat = [w for f in sorted(features) for w in found[f]]
        joint = [w for f in sorted(features) for w in expected[f]["witnesses"]]
        # The evidence limit bounds the whole result list, as in EF3 and EF5.
        if "joint_evidence" in fx and flat != fx["joint_evidence"]:
            problems.append(f"joint evidence {flat} != contract joint_evidence {fx['joint_evidence']}")
        if flat != joint[:limit] or any(len(found[f]) > limit for f in features):
            problems.append(f"joint evidence {flat} != {joint[:limit]}")
    return problems


def rival_problems(fx: dict[str, Any], log_result: Any) -> list[str]:
    """Each recorded simple-return rival differs from the log value, and the shipped simple producer reproduces it."""
    problems: list[str] = []
    log_values = {c.feature_id: c.values[0] for c in log_result.values}
    try:
        simple, _ = run(fx, tuple(SIMPLE[o] for o in fx["outputs"]), simple=True)
    except ContractError as error:
        return [f"simple producer refused {error.code.name}: {error}"] if "forming" not in json.dumps([fx["inst"], fx["bench"]]) else []
    simple_values = {c.feature_id: c.values[0] for c in simple.values}
    for rival in fx.get("wrong_convention", []):
        output = rival["output"]
        literal = float(Fraction(rival["exact"])) if "exact" in rival else float(Decimal(rival["decimal"]))
        value = log_values.get(output)
        if value is not None and value == literal:
            problems.append(f"{output}: log value equals the rival {rival['convention']} {literal!r}")
        got = simple_values.get(SIMPLE[output])
        if got is None or (got != literal and abs(got - literal) > 1e-15 * abs(literal)):
            problems.append(f"{SIMPLE[output]}: simple producer {got!r} differs from the contract rival {literal!r}")
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
    by_id = {fx["id"]: fx for fx in doc["relative_log_fixtures"]}
    refusals = [rf for rf in doc["refusal_fixtures"] if rf["base"] in by_id]
    problems: list[str] = []
    if (len(by_id), len(refusals)) != (PINNED_RESULTS, PINNED_REFUSALS):
        problems.append(f"pinned counts {(PINNED_RESULTS, PINNED_REFUSALS)} != contract {(len(by_id), len(refusals))}")
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
            if len(features) == len(outputs) and fx.get("wrong_convention"):
                problems += [f"{fx['id']}: {p}" for p in rival_problems(fx, result)]
    # A forming slot must never be delivered: the library refuses a row past the market cutoff (BOUNDS), so a
    # forming slot is never read as a value; "delivered in neither series" is fixture notation only.
    forming_fixtures = [fx for fx in by_id.values() if any(c == "forming" for s_ in (fx["inst"], fx["bench"])
                                                           if s_ != "absent" for c in s_)]
    if not forming_fixtures:
        problems.append("no fixture marks a forming slot")
    for fx in forming_fixtures:
        grid, batches, _ = expand(fx)
        starts = {sess.session_id for sess in grid.sessions}
        for batch in batches:
            if batch is None:
                continue
            ids = set(next(c.values for c in batch.columns if c.name == "session_id"))
            forming_ids = {f"D{i}" for s_ in (fx["inst"], fx["bench"]) if s_ != "absent"
                           for i, c in enumerate(s_) if c == "forming"}
            if ids & forming_ids or not forming_ids <= starts:
                problems.append(f"{fx['id']}: a forming slot is delivered")
        try:
            g2, b2, c2 = expand(fx, deliver_forming=True)
            compute_dv1(b2, g2, c2, features=tuple(fx["outputs"]))
        except ContractError as error:
            if error.code.name != "BOUNDS":
                problems.append(f"{fx['id']}: forced forming delivery refused {error.code.name}, expected BOUNDS")
        else:
            problems.append(f"{fx['id']}: forced forming delivery was not refused")
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
    print(f"DV1 library: {len(by_id)} relative-log result fixtures ({runs} runs, bit for bit) and {len(refusals)} refusals "
          f"({len(codes)} codes) match the contract")
    return 0


if __name__ == "__main__":
    sys.exit(main())
