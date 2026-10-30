"""Gate for the shared DV1 configuration checks and the shared status module (story DV1-5a, C-A).

All four DV1 producers (relative log statistics, simple-mean ATR, window extremes, core spread) must refuse each bad
configuration input with the same error code, in the contract stage order (parameters, units and adjustment, cutoff,
policy label, identity), because they call one config-check module (`equity_features.dv1._config_check`) and, for the
daily-grid producers, one status module (`equity_features.dv1._status`). Per producer and per bad input:

- RF22 currency (lower case, two letters, four letters, empty): INVALID_UNIT in all four;
- RF21 adjustment pair (raw with split-factors-v1, split with raw-v1): UNSUPPORTED_ADJUSTMENT in the three producers that
  carry an adjustment basis; the core spread producer has no adjustment basis, never compares it, and publishes the same
  result whatever adjustment the legs batch declares;
- cutoff before the target session open: BOUNDS in all four;
- policy label other than the producer's own: INCOMPATIBLE_VERSION in all four;
- stage order: a parameter fault beats a currency fault, a currency fault beats an adjustment fault, an adjustment
  fault beats a policy-label fault (and the cutoff fault comes before the policy label).

It also runs the contract's coverage admission refusals (RF11 undeclared coverage, RF73 partial coverage) against each
of the three daily-grid producers: same code in each. The core spread producer has no coverage entries; its
partial-universe and absent-input admission is shown by dropping one fund's legs and by delivering none.

Every fixture used here is a contract fixture (RL03, AT01, WX01, CS01) driven through the existing gates' expanders; no
expected value is derived from the library. Internal, synthetic, pre-release.

Run from an environment with the packages installed: `python tools/verify_dv1_shared_checks.py`; exit 0 only if
everything holds.
"""
from __future__ import annotations

import copy
import dataclasses
import functools
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any, Callable

from equity_feature_contracts import ContractError, ErrorCode
from equity_features.dv1 import build_core_spread_config, compute_dv1

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "docs" / "dv1" / "DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json"
BASES = {"relative_log": ("verify_dv1_library", "relative_log_fixtures", "RL03"),
         "atr": ("verify_dv1_atr_library", "atr_fixtures", "AT01"),
         "window": ("verify_dv1_window_library", "window_fixtures", "WX01"),
         "core_spread": ("verify_dv1_core_spread_library", "core_spread_fixtures", "CS01")}
DAILY = ("relative_log", "atr", "window")
# producer -> (parameter that is faulted for the parameter-stage check, bad value)
PARAMETER_FAULT = {"relative_log": ("window", 1), "atr": ("period", 0), "window": ("period", 0),
                   "core_spread": ("evidence_limit", -1)}
PINNED_CASES = 63


def load(name: str) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, ROOT / "tools" / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def code_of(call: Callable[[], object]) -> str | None:
    try:
        call()
    except ContractError as error:
        return error.code.name
    return None


def main() -> int:
    doc = json.loads(CONTRACT.read_text(encoding="utf-8"))
    problems: list[str] = []
    cases = 0
    tools: dict[str, ModuleType] = {}
    fixtures: dict[str, dict[str, Any]] = {}
    for producer, (module, key, base) in BASES.items():
        tools[producer] = load(module)
        fixtures[producer] = next(fx for fx in doc[key] if fx["id"] == base)

    def build(producer: str, fx: dict[str, Any]) -> Any:
        return tools[producer].expand(fx)

    def mutate(producer: str, *steps: tuple[str, Any]) -> dict[str, Any]:
        fx = copy.deepcopy(fixtures[producer])
        for path, value in steps:
            cursor = fx
            keys = path.split(".")
            for k in keys[:-1]:
                cursor = cursor.setdefault(k, {})
            cursor[keys[-1]] = value
        return fx

    def expect(producer: str, label: str, steps: tuple[tuple[str, Any], ...], want: str | None) -> None:
        nonlocal cases
        cases += 1
        got = code_of(lambda: build(producer, mutate(producer, *steps)))
        if got != want:
            problems.append(f"{producer}: {label}: refused {got} expected {want}")

    for producer in BASES:
        if code_of(functools.partial(build, producer, fixtures[producer])) is not None:
            problems.append(f"{producer}: the unmutated base fixture is refused")
        for currency in ("usd", "US", "USDD", ""):
            expect(producer, f"RF22 currency {currency!r}", (("unit.currency", currency),), "INVALID_UNIT")
        expect(producer, "policy label", (("params.policy_version", "dv1-other"),), "INCOMPATIBLE_VERSION")
        name, bad = PARAMETER_FAULT[producer]
        expect(producer, "parameter beats currency", ((f"params.{name}", bad), ("unit.currency", "usd")),
               "INVALID_CONFIG")
        expect(producer, "currency beats policy label", (("unit.currency", "usd"), ("params.policy_version", "x")),
               "INVALID_UNIT")
    for producer in DAILY:
        for label, spec in (("raw with split policy", ("unadjusted", {"policy_version": "split-factors-v1"})),
                            ("split with raw policy", ("split_adjusted", {"policy_version": "raw-v1", "action_snapshot": "a1",
                                                                         "anchor": "k1"})),
                            ("raw with unknown policy", ("unadjusted", {"policy_version": "other-v1"}))):
            expect(producer, f"RF21 {label}", (("adjustment", spec[0]), ("adjustment_spec", spec[1])),
                   "UNSUPPORTED_ADJUSTMENT")
        bad_pair = (("adjustment", "unadjusted"), ("adjustment_spec", {"policy_version": "split-factors-v1"}))
        expect(producer, "currency beats adjustment pair", bad_pair + (("unit.currency", "usd"),), "INVALID_UNIT")
        expect(producer, "adjustment pair beats policy label", bad_pair + (("params.policy_version", "x"),),
               "UNSUPPORTED_ADJUSTMENT")
        expect(producer, "parameter beats adjustment pair", bad_pair + ((f"params.{PARAMETER_FAULT[producer][0]}",
                                                                          PARAMETER_FAULT[producer][1]),),
               "INVALID_CONFIG")

    # Cutoff: replace the availability of a valid configuration with a cutoff before the target session open. The
    # producer rebuilds the canonical envelope from the configuration, so the cutoff stage runs there.
    for producer in BASES:
        cases += 2
        built = build(producer, fixtures[producer])
        if producer == "core_spread":
            batches, config, entity = built
            opened = config.session.open_ns
            grid = None
        else:
            grid, batches, config = built
            opened = grid.target.open_ns
            entity = None
        early = dataclasses.replace(config.availability, market_cutoff_ns=opened - 1)
        broken = dataclasses.replace(config, availability=early)
        features = tuple(fixtures[producer]["outputs"])
        got = code_of(lambda: compute_dv1(batches, grid, broken, features=features, entity=entity))
        if got != "BOUNDS":
            problems.append(f"{producer}: cutoff before the target session open: refused {got} expected BOUNDS")
        # A policy label fault in the same configuration is reported after the cutoff stage (cutoff first). The core
        # spread compute path defers its label to follow the input unit checks (the EF4 order, DV1-3), so its
        # cutoff-before-label order is shown on the configuration builder, which is the contract's config stage.
        both = dataclasses.replace(broken, parameters=tuple(
            dataclasses.replace(p, value="x") if p.name == "policy_version" else p for p in broken.parameters))
        if producer == "core_spread":
            p = fixtures[producer]["params"]
            got = code_of(lambda: build_core_spread_config(
                policy_version="x", core_benchmark_ids=p["core_benchmark_ids"], core_profile=p["core_profile"],
                alignment_tolerance_ns=p["alignment_tolerance_ns"], max_endpoint_age_ns=p["max_endpoint_age_ns"],
                window_ns=p.get("window_ns"), session=config.session, availability=early,
                price_unit=config.price_unit, evidence_limit=p["evidence_limit"]))
        else:
            got = code_of(lambda: compute_dv1(batches, grid, both, features=features, entity=entity))
        if got != "BOUNDS":
            problems.append(f"{producer}: cutoff beats policy label: refused {got} expected BOUNDS")

    # Coverage admission (RF11 undeclared, RF73 partial) identical in the three daily-grid producers.
    by_id = {rf["id"]: rf for rf in doc["refusal_fixtures"]}
    for rid, value in (("RF11", "undeclared"), ("RF73", "partial")):
        want = by_id[rid]["error_code"]
        for producer in DAILY:
            cases += 1
            fx = mutate(producer, ("coverage", value))
            if producer == "relative_log":
                got = code_of(functools.partial(admit_relative, tools[producer], fx, value))
            else:
                got = code_of(functools.partial(tools[producer].run, fx))
            if got != want:
                problems.append(f"{producer}: {rid} {value} coverage: refused {got} expected {want}")

    # Core spread: partial universe (one fund's legs missing) and absent input; no coverage entries exist there.
    core = tools["core_spread"]
    cases += 2
    partial = copy.deepcopy(fixtures["core_spread"])
    partial["facts"] = [f for f in partial["facts"] if f["inst"] != partial["params"]["core_benchmark_ids"][-1]]
    result, _ = core.run(partial)
    reasons = {r.value for q in result.quality for r in q.reasons}
    if reasons != {"partial_universe"}:
        problems.append(f"core_spread: partial universe reasons {sorted(reasons)}")
    absent = copy.deepcopy(fixtures["core_spread"])
    absent["facts"] = []
    result, _ = core.run(absent)
    reasons = {r.value for q in result.quality for r in q.reasons}
    if reasons != {"absent_input"}:
        problems.append(f"core_spread: absent input reasons {sorted(reasons)}")

    # Core spread never compares the adjustment: a legs batch declaring a split adjustment gives identical output.
    cases += 1
    batches, config, entity = core.expand(fixtures["core_spread"])
    plain = compute_dv1(batches, None, config, features=tuple(fixtures["core_spread"]["outputs"]), entity=entity)
    batch = batches[0]
    split = dataclasses.replace(batch.metadata, adjustment=dataclasses.replace(
        batch.metadata.adjustment, basis="split", policy_version="split-factors-v1", action_snapshot="a1", anchor="k1"))
    other = dataclasses.replace(batch, metadata=split)
    again = compute_dv1((other,), None, config, features=tuple(fixtures["core_spread"]["outputs"]), entity=entity)
    if [c.values for c in plain.values] != [c.values for c in again.values]:
        problems.append("core_spread: a different declared adjustment changed the result")

    if cases != PINNED_CASES:
        problems.append(f"case count {cases} != pinned {PINNED_CASES}")
    for line in problems:
        print("MISMATCH", line)
    if problems:
        print(f"{len(problems)} MISMATCH(ES)")
        return 1
    print(f"DV1 shared checks: {cases} cases over four producers hold (currency, adjustment pair, cutoff, policy label, "
          "stage order, coverage admission, core spread ignores the adjustment)")
    return 0


def admit_relative(module: ModuleType, fx: dict[str, Any], value: str) -> None:
    """The relative-log expander has no coverage switch: apply it to the delivered batches, then compute."""
    grid, batches, config = module.expand(fx)
    changed: list[Any] = []
    for batch in batches:
        if batch is None:
            changed.append(batch)
            continue
        intervals = () if value == "undeclared" else batch.metadata.interval_coverage[1:]
        changed.append(dataclasses.replace(batch, metadata=dataclasses.replace(batch.metadata, interval_coverage=intervals)))
    compute_dv1(tuple(changed), grid, config, features=tuple(fx["outputs"]))


if __name__ == "__main__":
    raise SystemExit(main())
