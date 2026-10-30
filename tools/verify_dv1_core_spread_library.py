"""Drive every DV1-3 contract fixture through the pure library (`equity_features.dv1` core spread producer).

For each of the 21 core-spread result fixtures (CS01..CS21) the compact notation (leg facts {inst, kind, t, p, ss, pf, act,
rev, ka, op}, cutoff C, knowledge cutoff K) is expanded to one REFERENCE `legs` role (the EF4 leg-fact grammar plus the
operand label `op`), a target session and a final configuration (a `ka` token is the instant itself, exactly as the EF4
leg notation) and the library result is compared with the contract literal BIT FOR BIT: the float64 hex string and sign
of the value (there is no tolerance band in DV1), status, reasons, expected and observed counts and witnesses. Every output
is run alone and both together; in the joint run the combined evidence list is the lexical concatenation truncated to
`evidence_limit`. The contract literal names a witness `slot:<index>` in declared order (fund k start is slot 2k, its end
slot 2k + 1) and the gate compares it directly; a literal of any other form (such as the former `leg:` form) fails.
For each of the 16 refusal recipes whose base is a core-spread fixture the recorded mutation is applied and the library must refuse with exactly the recorded error code.

The wrong-convention rivals recorded in the contract (range for stdev and stdev for range, first-trade, first-bar and
prior-close operands) must differ from the library value, and the shipped EF4 `core.benchmark_return_dispersion_fraction`
(read only, run through its own public path on the same prior_close and window_start inputs of CS01, CS06 and CS07) must
publish the same bits as the DV1 range output, so the deprecated range id is shown unchanged.

No expectation is computed here and the library is not used to derive one: every expected value is the contract literal
that the independent stdlib expander (`tools/contract_fixtures/dv1_fixture_expand.py`, gate
`tools/verify_dv1_fixtures.py`) recomputes. Internal, synthetic, pre-release.

Run from an environment with the packages installed: `python tools/verify_dv1_core_spread_library.py`; exit 0 only if
everything holds.
"""
from __future__ import annotations

import base64
import copy
import json
import re
import struct
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path
from typing import Any

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, ContractError, Coverage,
    DataKind, EntityKey, ErrorCode, PriceUnit, SessionSpec, SourceBinding,
)
from equity_features.dv1 import (
    CORE_RANGE, CORE_STDEV, build_core_spread_config, compute_dv1, dv1_definitions, require_dv1_capability,
)
from equity_features.ef4._relative_excess import CORE_DISPERSION, build_relative_excess_config, compute_relative_excess

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "dv1" / "DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json"
PINNED_RESULTS = 21
PINNED_REFUSALS = 16
EF4_EQUAL = ("CS01", "CS06", "CS07")  # the equal-value fixtures against the frozen EF4 inputs CB01, CB07 and CB03
OUTPUTS = (CORE_RANGE, CORE_STDEV)  # lexical order


def reference_id(fund: str, kind: str, profile: str | None) -> str:
    """Closed x1 reference grammar: `x1:` followed by the URL-safe base64 (no padding) of the component text."""
    inner = f"{fund}#start#{profile}#A" if kind == "start" else f"{fund}#end#A"
    return "x1:" + base64.urlsafe_b64encode(inner.encode("utf-8")).rstrip(b"=").decode("ascii")


def leg_text(fact: dict[str, Any], *, operand: bool) -> str:
    """Closed ordered leg text; the DV1 text carries the operand label of a start leg, the EF4 text never does."""
    if fact["kind"] == "end":
        return f"slot=A;rev={fact['rev']};act={fact['act']}"
    op = f";op={fact['op']}" if operand and "op" in fact else ""
    return f"profile={fact['pf']};slot=A{op};rev={fact['rev']};act={fact['act']}"


def leg_batch(fx: dict[str, Any], unit: PriceUnit, *, operand: bool) -> CanonicalBatch | None:
    """One REFERENCE batch of the fixture's leg facts in the declared (time, reference id) order; None when none."""
    rows = []
    for fact in fx["facts"]:
        rows.append({"fact_kind": "ef4.leg.start" if fact["kind"] == "start" else "ef4.leg.end",
                     "instrument_id": fact["inst"], "session_id": fact["ss"],
                     "reference_id": reference_id(fact["inst"], fact["kind"], fact.get("pf")),
                     "effective_start_ns": fact["t"], "effective_end_ns": None, "known_at_ns": fact["ka"],
                     "price": fact["p"], "text": leg_text(fact, operand=operand)})
    if not rows:
        return None
    rows.sort(key=lambda row: (row["effective_start_ns"], row["reference_id"]))
    names = ("fact_kind", "instrument_id", "session_id", "reference_id", "effective_start_ns", "effective_end_ns",
             "known_at_ns", "price", "text")
    columns = tuple(Column(name, tuple(row[name] for row in rows)) for name in names)
    metadata = BatchMetadata("SYN", SourceBinding("SYN-SRC", "snap1", "dv1-map1", "legs"),
                             Coverage(len(rows), len(rows), True), unit, AdjustmentSpec(), "none", "shares", "declared",
                             "reject", None, ())
    return CanonicalBatch(DataKind.REFERENCE, columns, metadata)


def environment(fx: dict[str, Any]) -> tuple[SessionSpec, AvailabilitySpec, PriceUnit, EntityKey]:
    """Target session S1 spanning every fact time and the cutoff; K and C as the contract states."""
    times = [fact["t"] for fact in fx["facts"]] + [fx["C"]]
    session = SessionSpec("SYN", "S1", min(times) - 1, max(times) + 1, "UTC")
    availability = AvailabilitySpec(fx["C"], fx["K"], max(fx["K"], fx["C"]), "known_at")
    unit = PriceUnit(fx["unit"]["scale"], fx["unit"]["currency"])
    return session, availability, unit, EntityKey(fx["instrument"], "S1")


def expand(fx: dict[str, Any]) -> tuple[tuple[CanonicalBatch | None, ...], ConfigSpec, EntityKey]:
    """Fixture -> (legs role, config, entity); every contract refusal is a ContractError raised here or later."""
    p = fx["params"]
    session, availability, unit, entity = environment(fx)
    # Stage order of the contract: configuration is built (and refused) before any data is shaped.
    config = build_core_spread_config(
        policy_version=p.get("policy_version"), core_benchmark_ids=p.get("core_benchmark_ids"),
        core_profile=p.get("core_profile"), alignment_tolerance_ns=p.get("alignment_tolerance_ns"),
        max_endpoint_age_ns=p.get("max_endpoint_age_ns"), window_ns=p.get("window_ns"), session=session,
        availability=availability, price_unit=unit, evidence_limit=p.get("evidence_limit"))
    return (leg_batch(fx, unit, operand=True),), config, entity


def run(fx: dict[str, Any], chosen: tuple[str, ...] | None = None) -> tuple[Any, ConfigSpec]:
    batches, config, entity = expand(fx)
    chosen = tuple(fx["outputs"]) if chosen is None else chosen
    for feature in chosen:
        require_dv1_capability(feature, fx.get("capability", "batch"))
    for definition in dv1_definitions(None, config):
        text = definition.formula
        stdev = definition.feature_id == CORE_STDEV
        if "daily_bar_open" not in text or ("POPULATION" not in text if stdev else "RANGE" not in text):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "discovery description does not name the convention")
        if definition.unit != "fraction" or definition.dtype.value != "float64":
            raise ContractError(ErrorCode.INVALID_SCHEMA, "unit or dtype differs from the contract")
    return compute_dv1(batches, None, config, features=chosen, entity=entity), config


def bits(value: float) -> int:
    return int(struct.unpack(">Q", struct.pack(">d", value))[0])


def exact(want: dict[str, Any] | None, value: Any) -> bool:
    """Bit for bit: same float64 bit pattern (so the same sign of zero) and the same hex string."""
    if want is None or value is None:
        return want is None and value is None
    target = float.fromhex(want["hex"])
    return (type(value) is float and value.hex() == want["hex"] and bits(value) == bits(target)
            and bits(target) == bits(want["float64"]))


def slot_names(fx: dict[str, Any], witnesses: list[str]) -> list[str]:
    """The contract witnesses are already declared-order ordinals `slot:<index>`; any other form (for example the old
    `leg:<fund>:<kind>` literal) fails loudly. No name map."""
    for witness in witnesses:
        if re.fullmatch(r"slot:(0|[1-9][0-9]*)", witness) is None:
            raise ValueError(f"{fx['id']}: witness {witness!r} is not a slot:<index> ordinal")
    return list(witnesses)


def compare(fx: dict[str, Any], result: Any, config: Any, features: tuple[str, ...]) -> list[str]:
    problems: list[str] = []
    ordered = tuple(sorted(features))
    if tuple(c.feature_id for c in result.values) != ordered:
        return [f"selected outputs {[c.feature_id for c in result.values]} differ from {list(ordered)}"]
    expected_witnesses: list[str] = []
    for column, quality in zip(result.values, result.quality):
        want = fx["expected"][column.feature_id]
        value, = column.values
        got = (quality.status.value, [r.value for r in quality.reasons], quality.expected, quality.observed)
        literal = (want["status"], want["reasons"], want["expected"], want["observed"])
        if not exact(want["value"], value) or got != literal:
            problems.append(f"{column.feature_id}: value {value!r} {got} != {want['value']} {literal}")
        if column.unit != "fraction" or column.dtype.value != "float64":
            problems.append(f"{column.feature_id}: unit/dtype {column.unit} {column.dtype}")
        if value is None and any(row.feature_id == column.feature_id for row in result.evidence):
            problems.append(f"{column.feature_id}: an unavailable output emitted evidence")
        expected_witnesses += slot_names(fx, want["witnesses"])
    limit = fx["params"]["evidence_limit"]
    found = [row.row_id for row in result.evidence]
    if found != expected_witnesses[:limit]:
        problems.append(f"witnesses {found} != {expected_witnesses[:limit]}")
    bindings = {b.role for b in result.metadata.inputs}
    if bindings - {"legs"}:
        problems.append(f"unexpected input bindings {bindings}")
    return problems


def run_all(fx: dict[str, Any]) -> list[str]:
    """Every selected output alone, then jointly (the joint evidence list is capped once by the limit)."""
    problems: list[str] = []
    for chosen in [(name,) for name in sorted(fx["outputs"])] + [tuple(sorted(fx["outputs"]))]:
        try:
            result, config = run(fx, chosen)
        except ContractError as error:
            problems.append(f"{chosen}: refused {error.code.name}: {error}")
            continue
        problems += [f"{chosen}: {p}" for p in compare(fx, result, config, chosen)]
    return problems


def rival_problems(fx: dict[str, Any]) -> list[str]:
    """Each recorded rival differs from the library value of its output."""
    problems: list[str] = []
    result, _ = run(fx)
    values = {c.feature_id: c.values[0] for c in result.values}
    for rival in fx.get("wrong_convention", []):
        literal = float(Fraction(rival["exact"])) if rival["exact"] is not None else float(Decimal(rival["decimal"]))
        if values[rival["output"]] == literal:
            problems.append(f"{rival['convention']}: library {rival['output']} equals the rival {literal!r}")
    return problems


def shipped_ef4_dispersion(fx: dict[str, Any]) -> float | None:
    """The frozen EF4 `core.benchmark_return_dispersion_fraction` through its own public path on the same legs."""
    p = fx["params"]
    session, availability, unit, entity = environment(fx)
    config = build_relative_excess_config(
        policy_version="ef4-rel1", alignment_tolerance_ns=p["alignment_tolerance_ns"],
        max_endpoint_age_ns=p["max_endpoint_age_ns"], window_ns=p.get("window_ns"),
        core_benchmark_ids=p["core_benchmark_ids"], core_profile=p["core_profile"], session=session,
        availability=availability, adjustment=AdjustmentSpec(), price_unit=unit, evidence_limit=p["evidence_limit"])
    result = compute_relative_excess((leg_batch(fx, unit, operand=False), None), config, entity=entity,
                                     features=(CORE_DISPERSION,))
    value = result.values[0].values[0]
    return value if type(value) is float else None


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
        elif isinstance(cursor, list) and last == len(cursor):
            cursor.append(step["value"])  # one past the end adds the fact
        else:
            cursor[last] = step["value"]
    return fx


def main() -> int:
    doc = json.loads(CONTRACT.read_text(encoding="utf-8"))
    by_id = {fx["id"]: fx for fx in doc["core_spread_fixtures"]}
    refusals = [rf for rf in doc["refusal_fixtures"] if rf["base"] in by_id]
    problems: list[str] = []
    if (len(by_id), len(refusals)) != (PINNED_RESULTS, PINNED_REFUSALS):
        problems.append(f"pinned counts {(PINNED_RESULTS, PINNED_REFUSALS)} != contract {(len(by_id), len(refusals))}")
    ruled = {output: 0 for output in OUTPUTS}
    equal = 0
    for fx in by_id.values():
        found = run_all(fx)
        problems += [f"{fx['id']}: {p}" for p in found]
        if found:
            continue
        problems += [f"{fx['id']}: {p}" for p in rival_problems(fx)]
        for rival in fx.get("wrong_convention", []):
            ruled[rival["output"]] += 1
        if fx["id"] in EF4_EQUAL:
            shipped = shipped_ef4_dispersion(fx)
            want = fx["expected"][CORE_RANGE]["value"]
            if not exact(want, shipped):
                problems.append(f"{fx['id']}: shipped EF4 dispersion id {shipped!r} != range literal {want}")
            equal += 1
    if equal != len(EF4_EQUAL):
        problems.append("the EF4 equal-value fixtures (CS01, CS06, CS07) were not all compared")
    for output, count in ruled.items():
        if not count:
            problems.append(f"{output} has no wrong-convention fixture")
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
    # Contract text (regular open paragraph): the op token is ignored for prior_close and window_start. The literals of CS01,
    # CS06 and CS07 must hold unchanged when every start leg carries a foreign operand label.
    for name in EF4_EQUAL:
        carried = copy.deepcopy(by_id[name])
        for fact in carried["facts"]:
            if fact["kind"] == "start":
                fact["op"] = "first_trade_price"
        problems += [f"{name} with op on non-regular_open legs: {p}" for p in run_all(carried)]
    # RF22 (contract text): a lower-case currency is INVALID_UNIT for every producer; its base is an ATR fixture, so the
    # same mutation is applied here to a core base and the expected code is read from the contract.
    rf22 = next(rf for rf in doc["refusal_fixtures"] if rf["id"] == "RF22")
    mutation = [{"set": "fixture.unit.currency", "value": "usd"}]
    try:
        run(apply(by_id["CS02"], mutation))
    except ContractError as error:
        codes.add(error.code.name)
        if error.code.name != rf22["error_code"]:
            problems.append(f"RF22 on CS02: refused {error.code.name} expected {rf22['error_code']} ({error})")
    else:
        problems.append(f"RF22 on CS02: not refused (expected {rf22['error_code']})")
    for line in problems:
        print("MISMATCH", line)
    if problems:
        print(f"{len(problems)} MISMATCH(ES)")
        return 1
    print(f"DV1 core spread library: {len(by_id)} core-spread result fixtures (bit for bit, each output alone and joint) and "
          f"{len(refusals)} refusals plus RF22 on CS02 ({len(codes)} codes) match the contract; op is ignored on prior_close and window_start; the rivals differ and the "
          f"shipped EF4 range id publishes the same bits as the DV1 range output on CS01, CS06 and CS07")
    return 0


if __name__ == "__main__":
    sys.exit(main())
