"""Validate docs/plans/design-coverage-map.json (schema ef-design-coverage-map1); standard library only.

Internal, synthetic, pre-release. The map is the hand-maintained input of the feature coverage table: one row per design
item, with the status, the output ids that serve it and the evidence. This script never runs feature code and reads the
design repository only when --design-root is given (to check design_section). It checks:

* schema: required keys, enumerations, unique design ids, item and per-family counts equal the declared design basis;
* every mapped output id exists in the core catalogue sources: the ownership manifest, the dotted id literals of the
  library sources, or a family that is composed from a prefix and a name in one named source file;
* an output's release agrees with the ownership manifest where the manifest names it, and a derived `implemented` row
  never cites a still-planned DV1 output as its primary or operand;
* status rules: `missing` is derived (no outputs, no assertion); `implemented` is derived unless provisional; `partial`,
  `differs` and `out_of_library_scope` are asserted and cite a record that exists; a provisional row names its clearing
  check; a `differs` row names the existing output and the variant;
* evidence references resolve to files in this repository;
* the posture wording rules (no provider names, no banned claims) hold for the map text.

Usage: python tools/verify_design_coverage_map.py [--root DIR]; exit 0 only if every check holds.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

MAP_PATH = "docs/plans/design-coverage-map.json"
MANIFEST_PATH = "docs/plans/equity-output-ownership.json"
SCHEMA = "ef-design-coverage-map1"
FAMILIES = ("price-technicals", "volume-radar", "market-context", "universe-profile", "company-events", "presets",
            "watchlists", "scanner-lifecycle", "strategies")
KINDS = ("condition", "preset", "watchlist_rule", "lifecycle", "strategy", "catalogue", "chart", "alert")
STATUSES = ("implemented", "partial", "missing", "differs", "out_of_library_scope")
ASSERTED_STATUSES = ("partial", "differs", "out_of_library_scope")
ROLES = ("primary", "operand", "variant", "existing_differs")
RELEASES = ("R1", "R2", "R17", "EF1", "EF2", "EF3", "EF4", "EF5", "DV1")  # delivery order
EVIDENCE_KINDS = ("gate", "test", "doc", "fixture")
COMPOSITIONS = ("none", "consumer_arith")
BASES = ("ruling", "adopted_from_parity_check")
ID_PREFIXES = ("session", "history", "baseline", "relative", "breadth", "pace", "robust", "cohort", "mean", "adaptive",
               "intraday", "channel", "trend", "retracement", "path", "projection", "vwap", "quote", "tape", "rate", "core",
               "candle", "structure", "technical", "calendar", "reference", "cross_venue")
LITERAL = re.compile(r"""["']((?:%s)(?:\.[a-z0-9_]+)+)["']""" % "|".join(ID_PREFIXES))
# Families whose ids are composed as prefix + name inside one source file (the literal full id never appears).
COMPOSED = {
    "session.gap.": "packages/features/src/equity_features/ef1/_definitions.py",
    "session.gap_endpoint.": "packages/features/src/equity_features/ef1/_definitions.py",
    "session.opening_drive.": "packages/features/src/equity_features/ef1/_definitions.py",
    "session.daily_observations.": "packages/features/src/equity_features/ef1/_definitions.py",
    "session.status_history.": "packages/features/src/equity_features/ef1/_definitions.py",
    "session.open_observation.": "packages/features/src/equity_features/ef1/_definitions.py",
    "session.extended.": "packages/features/src/equity_features/ef1/_definitions.py",
    "calendar.period.": "packages/features/src/equity_features/ef1/_definitions.py",
    "trend.ichimoku.": "packages/intraday/src/equity_features_intraday/_channels_registry.py",
    "channel.keltner.": "packages/intraday/src/equity_features_intraday/_channels_registry.py",
    "channel.donchian.": "packages/intraday/src/equity_features_intraday/_channels_registry.py",
    "channel.pivot.": "packages/intraday/src/equity_features_intraday/_channels_registry.py",
    "channel.squeeze.": "packages/intraday/src/equity_features_intraday/_channels_registry.py",
}
# Seed statuses (CV0): I implemented (confirmed), V implemented (provisional), P partial, M missing, D differs,
# O out of library scope. A row that departs from this table (for example differs to implemented, or provisional to
# confirmed) must carry a `promotion_record` that resolves to a listed record section and, when the row becomes
# implemented, an evidence entry of kind fixture that resolves (PO rulings 2026-10-30 section 2).
BASELINE = dict(token.split(":") for token in """
P1:P P2:P P3:I P4:P P5:I P6:V P7:P P8:I P9:I P10:I P11:P P12:P P13:P P14:V P15:D P16:M P17:V P18:M P19:M P20:I
P21:I P22:M P23:M P24:I P25:V P26:I P27:O P28:O P29:O P30:P P31:P P32:P P33:P P34:P P35:P P36:V P37:V P38:P
P39:P P40:D P41:D P42:D P43:M V1:I V2:I V3:I V4:I V5:O V5b:P V6:I V7:I V8:M V9:P V10:I V11:I V12a:D V12b:V
V12c:M V13:P V14:P V15:M V16:M V17:P V18:P V19:P V20:M V21:I V22:I V23:M V24:M V25:M V26:M V27:M V28:M V29:M
V30:M V31:M V32:M V33:M V34:M V35:M V36:M M1:I M2:I M3:I M4:I M5:I M6:I M7:I M8:I M9:I M10:I M11:D M12:I M13:M
M14:M M15:M M16:P M17:M M18:I M19:M M20:P M21:M M22:M U1:O U2:M U3:M U4:P U5:P U6:P U7:P U8:P U9:M U10:M U11:P
U12:P C1:M C2:M C3:M C4:M C5:M C6:M C7:M C8:M C9:M C10:P C11:M C12:M C13:M C14:M C15:M C16:M C17:M C18:M C19:M
C20:M C21:M C22:M C23:M C24:M S1:P S2:P S3:P S4:P S5:I S6:P S7:I S8:P S9:P S10:P S11:O S12:O W1:O W2:O W3:P
W4:O W5:O L1:O L2:O L3:P T1:O T2:O T3:O T4:P T5:P T6:O
""".split())
STATUS_CODE = {"implemented": "I", "partial": "P", "missing": "M", "differs": "D", "out_of_library_scope": "O"}
# Sections of the reconciliation record that can rule on a status class (basis `ruling`).
RULING_SECTIONS = {"partial": {1}, "differs": {1, 2}, "implemented": {1}, "out_of_library_scope": {3}}
# Final counts after the PO adoption record (2026-10-30): implemented confirmed 33 + provisional 7 (never summed).
EXPECTED = {"implemented": 33, "provisional": 7, "partial": 44, "missing": 59, "differs": 6, "out_of_library_scope": 17}
GAP_CODE = re.compile(r"^G[1-9]$")
EF_DOCS = ("docs/ef1", "docs/ef2")
DESIGN_ID = re.compile(r"^[A-Z][0-9]+[a-z]?$")
DESIGN_REF = re.compile(r"^[a-z0-9-]+\.md:[0-9]+$")
DATE = re.compile(r"^20[0-9]{2}-[0-9]{2}-[0-9]{2}$")
# Wording rules for the map text: no provider names, no release or performance claims.
BANNED = re.compile(r"\b(databento|fmp|edgar|finra|massive|tempest|covered|fixed|production|releasable|speedup|faster)\b", re.I)


def _load(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def _manifest_releases(manifest: dict[str, Any]) -> tuple[dict[str, str], set[str]]:
    releases: dict[str, str] = {}
    dv1: set[str] = set()
    for row in manifest["outputs"]:
        releases[row["canonical_name"]] = row["planned_delivery"]
    for key, value in manifest.items():
        if key.endswith("_delivered_outputs"):
            for row in value["entries"]:
                releases[row["canonical_name"]] = row["planned_delivery"]
                if row["planned_delivery"] == "DV1":
                    dv1.add(row["canonical_name"])
    return releases, dv1


def _contract_text(root: Path) -> str:
    return "\n".join(p.read_text(encoding="utf-8") for rel in EF_DOCS for p in sorted((root / rel).rglob("*.json")))


def _source_ids(root: Path) -> tuple[set[str], dict[str, str]]:
    literals: set[str] = set()
    for path in sorted(root.glob("packages/*/src/**/*.py")):
        literals.update(LITERAL.findall(path.read_text(encoding="utf-8")))
    texts = {rel: (root / rel).read_text(encoding="utf-8") for rel in sorted(set(COMPOSED.values())) if (root / rel).is_file()}
    return literals, texts


def _exists(feature_id: str, manifest_ids: set[str], literals: set[str], texts: dict[str, str], contracts: str) -> bool:
    if feature_id in manifest_ids or feature_id in literals:
        return True
    for prefix, rel in COMPOSED.items():
        if feature_id.startswith(prefix) and rel in texts:
            name = feature_id[len(prefix):]
            text = texts[rel]
            # the composed id must also be named in an EF1/EF2 contract JSON (an invented suffix fails here)
            if "." not in name and ('"%s"' % prefix) in text and ('"%s"' % name) in text and ('"%s"' % feature_id) in contracts:
                return True
    return False


def _sections(root: Path, rel: str) -> set[int]:
    path = root / rel
    if not path.is_file():
        return set()
    return {int(m) for m in re.findall(r"^## ([0-9]+)\.", path.read_text(encoding="utf-8"), re.M)}


def _ref_sections(ref: str) -> set[int]:
    return {int(m) for m in re.findall("\u00a7([0-9]+)", ref)}


def _heading_at(path: Path, line: int) -> str | None:
    lines = path.read_text(encoding="utf-8").splitlines()
    if not 1 <= line <= len(lines):
        return None
    for number in range(line, 0, -1):
        if lines[number - 1].startswith("#"):
            return lines[number - 1].lstrip("#").strip()
    return None


def check(root: Path, design_root: Path | None = None) -> list[str]:
    errors: list[str] = []

    def bad(where: str, message: str) -> None:
        errors.append(where + ": " + message)

    map_file = root / MAP_PATH
    doc = _load(map_file)
    manifest = _load(root / MANIFEST_PATH)
    releases, dv1_planned = _manifest_releases(manifest)
    literals, texts = _source_ids(root)
    contracts = _contract_text(root)
    manifest_ids = set(releases)

    if doc.get("schema") != SCHEMA:
        bad("schema", "expected " + SCHEMA)
    for key in ("posture", "design_basis", "core_basis", "sources", "items", "extras"):
        if key not in doc:
            bad("schema", "missing top-level key " + key)
    if errors:
        return errors
    basis = doc["design_basis"]
    items: list[dict[str, Any]] = doc["items"]
    if basis.get("item_count") != len(items):
        bad("design_basis", "item_count %s != %d items" % (basis.get("item_count"), len(items)))
    family_counts: dict[str, int] = {}
    for item in items:
        family_counts[str(item.get("family"))] = family_counts.get(str(item.get("family")), 0) + 1
    if basis.get("family_counts") != family_counts:
        bad("design_basis", "family_counts %s != actual %s" % (basis.get("family_counts"), family_counts))
    if not re.fullmatch(r"[0-9a-f]{40}", str(basis.get("commit", ""))):
        bad("design_basis", "commit must be a full sha")

    records = doc["sources"].get("records", {})
    for name, rel in records.items():
        path = root / rel
        if not path.is_file():
            bad("sources.records." + name, "record file missing: " + rel)
            continue
        lines = path.read_text(encoding="utf-8").splitlines()
        if len(lines) < 3 or not lines[0].startswith("Source: work/") or lines[1] != "" or not lines[2].strip():
            bad("sources.records." + name, "record needs a one-line 'Source: work/...' header, a blank line, then the verbatim body")

    legend = doc.get("capability_gaps", {})
    if not all(("G%d" % n) in legend for n in range(1, 10)):
        bad("capability_gaps", "legend must define G1 to G9")
    seen: set[str] = set()
    for item in items:
        did = str(item.get("design_id"))
        where = "item " + did
        for key in ("design_id", "family", "kind", "title", "design_ref", "design_section", "status", "status_basis",
                    "composition", "outputs", "delivering_release", "evidence", "note"):
            if key not in item:
                bad(where, "missing key " + key)
        if any(k not in item for k in ("design_id", "family", "kind", "status", "status_basis", "outputs", "evidence")):
            continue
        if not DESIGN_ID.match(did):
            bad(where, "design_id shape")
        if did in seen:
            bad(where, "duplicate design_id")
        seen.add(did)
        if item["family"] not in FAMILIES:
            bad(where, "unknown family " + str(item["family"]))
        if item["kind"] not in KINDS:
            bad(where, "unknown kind " + str(item["kind"]))
        if item["status"] not in STATUSES:
            bad(where, "unknown status " + str(item["status"]))
            continue
        if not DESIGN_REF.match(str(item.get("design_ref"))):
            bad(where, "design_ref must be file.md:line")
        if item.get("composition") not in COMPOSITIONS:
            bad(where, "unknown composition")
        if not str(item.get("title", "")).strip() or not str(item.get("design_section", "")).strip():
            bad(where, "title and design_section must be non-empty")

        outputs: list[dict[str, Any]] = item["outputs"]
        ids: set[str] = set()
        for out in outputs:
            oid = str(out.get("id"))
            if oid in ids:
                bad(where, "duplicate output " + oid)
            ids.add(oid)
            if out.get("role") not in ROLES:
                bad(where, "output %s: unknown role %s" % (oid, out.get("role")))
            if out.get("release") not in RELEASES:
                bad(where, "output %s: unknown release %s" % (oid, out.get("release")))
            if not _exists(oid, manifest_ids, literals, texts, contracts):
                bad(where, "output id %s is not in the ownership manifest or the library sources" % oid)
            if oid in releases and releases[oid] != out.get("release"):
                bad(where, "output %s: release %s disagrees with the manifest (%s)" % (oid, out.get("release"), releases[oid]))
            if releases.get(oid) == "DV1" and out.get("release") != "DV1":
                bad(where, "output %s is DV1 in the manifest" % oid)
        roles = [str(o.get("role")) for o in outputs]
        base = [o for o in outputs if o.get("role") in ("primary", "operand")]
        expected = max((str(o["release"]) for o in base), key=RELEASES.index) if base and all(o.get("release") in RELEASES for o in base) else None
        if item.get("delivering_release") != expected:
            bad(where, "delivering_release %s != %s (latest release over primary and operand outputs)" % (item.get("delivering_release"), expected))

        status = item["status"]
        asserted = item.get("asserted")
        provisional = bool(item.get("provisional", False))
        if provisional and status != "implemented":
            bad(where, "only an implemented row can be provisional")
        if provisional and not str(item.get("clearing_check", "")).strip():
            bad(where, "provisional row must name its clearing_check")
        if not provisional and "clearing_check" in item:
            bad(where, "clearing_check only on provisional rows")
        if item.get("data_feed_item") and status != "missing":
            bad(where, "data_feed_item only on missing rows")
        if status == "missing":
            if outputs or asserted is not None or item["status_basis"] != "derived":
                bad(where, "missing is derived: no outputs, no assertion")
        elif status == "implemented":
            if not provisional and (asserted is not None or item["status_basis"] != "derived"):
                bad(where, "implemented is derived: no assertion unless provisional")
            if provisional and (asserted is None or item["status_basis"] != "asserted"):
                bad(where, "a provisional row cites the record that makes it provisional")
            if "primary" not in roles or "existing_differs" in roles:
                bad(where, "implemented needs a primary output and no existing_differs output")
            planned = [o["id"] for o in base if o["id"] in dv1_planned]
            if planned:
                bad(where, "implemented cites DV1 outputs as primary or operand (delivery is per the PO; use role variant): %s" % planned)
            if not item["evidence"]:
                bad(where, "implemented needs evidence")
        else:
            if asserted is None or item["status_basis"] != "asserted":
                bad(where, status + " is asserted and needs an asserted block with a PO record")
            if status == "differs" and not ("existing_differs" in roles and "variant" in roles):
                bad(where, "differs names the existing output (existing_differs) and the variant")
            if status != "differs" and "existing_differs" in roles:
                bad(where, "existing_differs only on differs rows")
        base_code = BASELINE.get(did)
        code = "V" if provisional else STATUS_CODE[status]
        if base_code is None:
            bad(where, "design_id is not in the seed baseline (add it to BASELINE with a PO record)")
        elif code != base_code:
            promo = item.get("promotion_record")
            promo_sections = _ref_sections(str(promo.get("record_ref", ""))) if isinstance(promo, dict) else set()
            ok = isinstance(promo, dict) and promo.get("record") in records.values() and bool(promo_sections) and \
                promo_sections <= _sections(root, str(promo.get("record")))
            if not ok:
                bad(where, "status %s departs from the seed (%s); needs a promotion_record that resolves to a listed record section" % (code, base_code))
            if base_code in ("D", "V") and code == "I" and not any(
                    e.get("kind") == "fixture" and (root / str(e.get("ref"))).is_file() for e in item["evidence"]):
                bad(where, "promotion from %s to confirmed needs a fixture evidence ref that resolves" % base_code)
        elif "promotion_record" in item:
            bad(where, "promotion_record on a row that matches the seed")
        if asserted is not None:
            if asserted.get("by") != "PO" or not DATE.match(str(asserted.get("date"))):
                bad(where, "asserted needs by=PO and an ISO date")
            if asserted.get("basis") not in BASES:
                bad(where, "asserted.basis must be one of %s" % (BASES,))
            ref = str(asserted.get("record_ref", ""))
            if not ref.strip():
                bad(where, "asserted.record_ref is empty")
            if asserted.get("record") not in (records.get("R1"), records.get("R3")) or not (root / str(asserted.get("record"))).is_file():
                bad(where, "asserted record must be the reconciliation record (R1) or the adoption record (R3), not %s" % asserted.get("record"))
            else:
                wanted = _ref_sections(ref)
                present = _sections(root, str(asserted.get("record")))
                if not wanted or not wanted <= present:
                    bad(where, "record_ref %r names a section that is not a heading of the record (sections %s)" % (ref, sorted(present)))
                elif asserted.get("record") == records.get("R3") and wanted != {3}:
                    bad(where, "adoption record rulings are in section 3 (the table), not %r" % ref)
                elif asserted.get("record") != records.get("R3") and asserted.get("basis") == "ruling" and not wanted & RULING_SECTIONS[status]:
                    bad(where, "record_ref %r is not a section that rules on a %s row (expected one of %s)" % (ref, status, sorted(RULING_SECTIONS[status])))
        for gap in item.get("capability_gap", []):
            if not GAP_CODE.match(str(gap)) or str(gap) not in doc.get("capability_gaps", {}):
                bad(where, "capability_gap %s is not in the capability_gaps legend" % gap)
        if design_root is not None:
            ref_file, _, ref_line = str(item.get("design_ref")).partition(":")
            for sub in ("docs/features", "engineering/stories"):
                design_file = design_root / sub / ref_file
                if design_file.is_file():
                    if _heading_at(design_file, int(ref_line or 0)) != item.get("design_section"):
                        bad(where, "design_section %r is not the heading at %s" % (item.get("design_section"), item.get("design_ref")))
                    break
            else:
                bad(where, "design file %s not found under the design root" % ref_file)
        for ev in item["evidence"]:
            if ev.get("kind") not in EVIDENCE_KINDS or not (root / str(ev.get("ref"))).is_file():
                bad(where, "evidence %s does not resolve to a file in this repository" % (ev.get("ref"),))

    for extra in doc["extras"]:
        for out in extra.get("outputs", []):
            if not _exists(str(out.get("id")), manifest_ids, literals, texts, contracts):
                bad("extra " + str(extra.get("extra_id")), "output id %s not found" % out.get("id"))

    tally: dict[str, int] = {}
    for item in items:
        key = "provisional" if item.get("provisional") else str(item.get("status"))
        tally[key] = tally.get(key, 0) + 1
    if tally != EXPECTED:
        bad("counts", "%s != expected %s (a change needs a new PO record and an update of EXPECTED)" % (tally, EXPECTED))
    for wording_file in (map_file, root / "docs/plans/DESIGN_COVERAGE_MAP.md"):
        hit = BANNED.search(wording_file.read_text(encoding="utf-8"))
        if hit:
            bad("wording", "banned term in %s: %s" % (wording_file.name, hit.group(0)))
    return errors


def counts(root: Path) -> str:
    doc = _load(root / MAP_PATH)
    items = doc["items"]
    by_status: dict[str, int] = {}
    for item in items:
        key = "provisional" if item.get("provisional") else item["status"]
        by_status[key] = by_status.get(key, 0) + 1
    order = ("implemented", "provisional", "partial", "missing", "differs", "out_of_library_scope")
    parts = ["%s=%d" % (("implemented_confirmed" if k == "implemented" else "implemented_provisional" if k == "provisional" else k), by_status.get(k, 0)) for k in order]
    return "%d items; %s; extras=%d" % (len(items), " ".join(parts), len(doc["extras"]))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--root", default=str(Path(__file__).resolve().parents[1]))
    parser.add_argument("--design-root", default="", help="optional watchyourlist-design checkout: also check design_section against the heading at design_ref")
    root = Path(parser.parse_args().root).resolve()
    args = parser.parse_args()
    errors = check(root, Path(args.design_root).resolve() if args.design_root else None)
    if errors:
        print("FAIL: %d problem(s)" % len(errors))
        for line in errors:
            print("  " + line)
        return 1
    print("design coverage map verified: " + counts(root))
    return 0


if __name__ == "__main__":
    sys.exit(main())
