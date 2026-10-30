"""Drive the 11 DV1 contract fixtures of `session.price.range_over_open` through the built-in R1 library (DV1-4a).

`session.price.range_over_open` is a built-in R1 catalog entry, not a dv1 producer. The shipped R1 session reductions read
completed bars, so each contract trade (price p, size s) is delivered as one degenerate bar (open = high = low = close = p,
volume = s) in event order; a zero-size trade is delivered as a zero-volume bar with null prices (the R1 admission rule for
an ineligible interval), so its price never enters the open, high or low, exactly the eligibility the contract states
(RO08, RO09). The mapping is a delivery shape and computes nothing. Every expected value is the contract literal that the
independent stdlib expander (`tools/contract_fixtures/dv1_fixture_expand.py`, gate `tools/verify_dv1_fixtures.py`)
recomputes; this gate derives no expectation from the library.

Compared BIT FOR BIT against the contract literal (there is no tolerance band in DV1): status, reasons, and for an
available value the float64 hex string and the sign of zero. Fixtures that list modes (RO06) are also run through
update (two chunks), restore (state export and restore between the chunks) and merge (the two chunk accumulators), and each
mode must equal the batch result bit for bit.

NOT compared, by design of the shipped R1 quality rows: the contract states expected = observed = 1 (one session) and
the witness `session:S1`, while an R1 quality row counts the delivered bars (expected and observed equal the number of
rows, including an ineligible one) and carries no evidence rows. This gate asserts the library side of that difference
(observed equals the delivered row count, no evidence) so it is visible and not silently ignored; it is raised as a
question for the Product Owner.

Wrong-convention rivals recorded in the contract (the close denominator, and for RO11 the official daily-bar open) must
differ from the library value, and the shipped `session.price.range_fraction` run on the same bars must publish exactly
the close-denominator rival, so the unchanged id is shown to be the rival and not the new id. The catalog assertions pin
40 built-ins, the new id's batch/update/restore/merge capabilities, and that no version label moved.

Run from an environment with the packages installed: `python tools/verify_dv1_range_over_open_library.py`; exit 0 only if
everything holds. Internal, synthetic, pre-release.
"""
from __future__ import annotations

import json
import sys
from dataclasses import asdict, replace
from fractions import Fraction
from pathlib import Path
from typing import Any

from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, ContractError, Coverage, DataKind, EntityKey,
    FeatureResult, InputScope, Parameter, PartitionSpan, PrefixCoverage, PriceUnit, SessionSpec, SourceBinding,
    StreamPopulation, WindowSpec, builtin_registry,
)
from equity_features.incremental import SessionAccumulator
from equity_features.session import compute_bars

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "tools"))
CONTRACT = ROOT / "docs" / "dv1" / "DEFINITION_VARIANTS_CONTRACT_PROPOSAL.json"
PINNED_FIXTURES = 11
NEW_ID = "session.price.range_over_open"
SHIPPED_ID = "session.price.range_fraction"
ENTITY = EntityKey("A", "S")
FAILURES: list[str] = []
CHECKS = 0


def check(name: str, ok: bool, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILURES.append(name + (": " + detail if detail else ""))


def config(unit: PriceUnit) -> ConfigSpec:
    return ConfigSpec("bars-demo", "v1", (Parameter("eligibility_policy", "synthetic-v1"),),
                      SessionSpec("demo", "S", 100, 200, "supplied"), WindowSpec(1, "S", ("P", "S", "future")),
                      AvailabilitySpec(200, 210, 210), price_unit=unit)


def bars(trades: list[list[int]], unit: PriceUnit) -> CanonicalBatch:
    """One degenerate bar per contract trade, in event order, inside the session scope."""
    n = len(trades)
    data = {"instrument_id": ("A",) * n, "session_id": ("S",) * n,
            "start_ns": tuple(100 + 10 * i for i in range(n)), "end_ns": tuple(110 + 10 * i for i in range(n)),
            "open": tuple(p if s else None for p, s in trades), "high": tuple(p if s else None for p, s in trades),
            "low": tuple(p if s else None for p, s in trades), "close": tuple(p if s else None for p, s in trades),
            "volume": tuple(s for _, s in trades),
            "known_at_ns": tuple(110 + 10 * i for i in range(n))}
    meta = BatchMetadata("demo", SourceBinding("synthetic", "s1", "m1", "bars"), Coverage(n, n, True), unit,
                         scope=InputScope(100, 200, "synthetic-v1"))
    return CanonicalBatch(DataKind.BAR, tuple(Column(k, v) for k, v in data.items()), meta)


def chunk(batch: CanonicalBatch, lo: int, hi: int) -> CanonicalBatch:
    cols = tuple(Column(c.name, c.values[lo:hi]) for c in batch.columns)
    return replace(batch, columns=cols, metadata=replace(batch.metadata, coverage=Coverage(hi - lo, hi - lo, True)))


def cell(result: FeatureResult, feature_id: str) -> tuple[Any, Any]:
    col = next(c for c in result.values if c.feature_id == feature_id)
    quality = next(q for q in result.quality if q.feature_id == feature_id)
    return col.values[0], quality


def accumulator(batch: CanonicalBatch, cfg: ConfigSpec) -> SessionAccumulator:
    return SessionAccumulator("bars", cfg, entity=ENTITY, population=StreamPopulation.from_batch(batch))


def restored(a: SessionAccumulator) -> SessionAccumulator:
    return SessionAccumulator.restore_state(a.export_state(), a.family, a.config, entity=a.entity, population=a.population)


def compare(fx_id: str, mode: str, value: Any, quality: Any, literal: dict[str, Any], rows: int) -> None:
    where = f"{fx_id} {mode}"
    check(where + " status", str(quality.status) == literal["status"], f"{quality.status} != {literal['status']}")
    check(where + " reasons", [str(r) for r in quality.reasons] == literal["reasons"], f"{quality.reasons} != {literal['reasons']}")
    lit = literal["value"]
    if lit is None:
        check(where + " value null", value is None, repr(value))
        return
    check(where + " value is float", isinstance(value, float), repr(value))
    if isinstance(value, float):
        check(where + " hex", value.hex() == lit["hex"], f"{value.hex()} != {lit['hex']}")
        check(where + " float64", value == lit["float64"], f"{value!r} != {lit['float64']!r}")
        check(where + " sign of zero", str(value) == str(float(lit["float64"])), repr(value))
    # library side of the documented difference: R1 quality rows count delivered bars and carry no evidence
    check(where + " R1 quality counts delivered bars", quality.observed == rows == quality.expected,
          f"expected {quality.expected} observed {quality.observed} rows {rows}")


def run_fixture(fx: dict[str, Any]) -> None:
    unit = PriceUnit(fx["unit"]["scale"], fx["unit"]["currency"])
    cfg = config(unit)
    literal = fx["expected"][NEW_ID]
    check(fx["id"] + " outputs", fx["outputs"] == [NEW_ID])
    if fx["trades"] == "absent":
        result = compute_bars(None, cfg, entity=ENTITY)
        value, quality = cell(result, NEW_ID)
        check(fx["id"] + " batch status", str(quality.status) == literal["status"], str(quality.status))
        check(fx["id"] + " batch reasons", [str(r) for r in quality.reasons] == literal["reasons"], str(quality.reasons))
        check(fx["id"] + " batch null", value is None and literal["value"] is None)
        return
    batch = bars(fx["trades"], unit)
    n = batch.row_count
    result = compute_bars(batch, cfg, entity=ENTITY)
    value, quality = cell(result, NEW_ID)
    if literal["value"] is None:
        check(fx["id"] + " batch status", str(quality.status) == literal["status"], str(quality.status))
        check(fx["id"] + " batch reasons", [str(r) for r in quality.reasons] == literal["reasons"], str(quality.reasons))
        check(fx["id"] + " batch null", value is None)
    else:
        compare(fx["id"], "batch", value, quality, literal, n)
    # wrong-convention rivals must differ; the shipped id is the close-denominator rival
    shipped, _ = cell(result, SHIPPED_ID)
    for rival in fx.get("wrong_convention", []):
        exact = Fraction(rival["exact"])
        check(fx["id"] + " rival " + rival["convention"] + " differs", value is not None and value != float(exact),
              f"{value!r} equals rival {rival['exact']}")
        if rival["convention"] == "close_denominator":
            check(fx["id"] + " shipped range_fraction is the close rival", shipped == float(exact), f"{shipped!r} != {exact}")
    # lifecycle modes: update (chunks), restore between chunks, merge of the chunk accumulators
    if "chunks" in fx:
        certificate = PrefixCoverage(batch.metadata.scope.end_ns, batch.metadata.coverage, batch.metadata.interval_coverage)
        (a0, a1), (b0, b1) = fx["chunks"]
        check(fx["id"] + " chunks cover the delivery", (a0, a1, b0, b1) == (0, a1, a1, n))
        first, second = chunk(batch, a0, a1), chunk(batch, b0, b1)
        upd = accumulator(batch, cfg)
        upd.update(first, start_ordinal=a0)
        upd.update(second, start_ordinal=b0)
        rst = accumulator(batch, cfg)
        rst.update(first, start_ordinal=a0)
        rst = restored(rst)
        rst.update(second, start_ordinal=b0)
        left, right = accumulator(batch, cfg), accumulator(batch, cfg)
        left.update(first, start_ordinal=0)
        right.update(second, start_ordinal=0)
        merged = left.merge_partitions(right, left=PartitionSpan(a0, a1), right=PartitionSpan(b0, b1))
        for mode, acc in (("update", upd), ("restore", rst), ("merge", merged)):
            final = acc.finalize(certificate)
            v, q = cell(final, NEW_ID)
            compare(fx["id"], mode, v, q, literal, n)
            check(fx["id"] + " " + mode + " equals batch", asdict(final) == asdict(result))


def catalog_checks() -> None:
    registry = builtin_registry()
    ids = [d.feature_id for d in registry.list_features()]
    check("40 built-ins", len(ids) == 40, str(len(ids)))
    check("new id follows range_fraction", ids.index(NEW_ID) == ids.index(SHIPPED_ID) + 1)
    definition = registry.get(NEW_ID)
    check("capabilities batch/update/restore/merge", (definition.capabilities.batch, definition.capabilities.update,
          definition.capabilities.restore, definition.capabilities.merge) == (True, True, True, True))
    check("algorithm v1, float64 fraction", definition.algorithm_version == "v1" and
          (definition.outputs[0].dtype, definition.outputs[0].unit) == ("float64", "fraction"))
    check("description names the operand, formula (H-L)/O", "first eligible regular-session trade" in definition.description and definition.formula == "(H-L)/O")
    check("range_fraction unchanged", registry.get(SHIPPED_ID).formula == "(H-L)/C")
    import equity_feature_contracts as contracts
    import equity_features
    from _versions import VERSIONS
    check("versions unchanged in C1", (contracts.__version__, equity_features.__version__) == ("0.0.4a5", "0.0.4a6")
          and (VERSIONS["contracts"], VERSIONS["features"]) == ("0.0.4a5", "0.0.4a6"),
          f"{contracts.__version__} {equity_features.__version__}")
    # a non-positive open is refused at canonical admission (contract C8); the defensive zero branch is not reachable
    unit = PriceUnit(0, "USD")
    for bad in (0, -1):
        try:
            compute_bars(bars([[bad, 5], [10, 5]], unit), config(unit), entity=ENTITY)
            check(f"open {bad} refused at admission", False, "computed")
        except ContractError as error:
            check(f"open {bad} refused at admission", True, str(error.code))


def main() -> int:
    doc = json.loads(CONTRACT.read_text(encoding="utf-8"))
    fixtures = doc["range_over_open_fixtures"]
    check("11 contract fixtures", len(fixtures) == PINNED_FIXTURES, str(len(fixtures)))
    for fx in fixtures:
        run_fixture(fx)
    catalog_checks()
    if FAILURES:
        print("FAIL: %d of %d checks" % (len(FAILURES), CHECKS))
        for line in FAILURES:
            print("  " + line)
        return 1
    print("OK: %d checks, %d range_over_open fixtures, library equals the contract bit for bit" % (CHECKS, len(fixtures)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
