"""Pure bounded daily observation admission, selection and exact reduction."""
from __future__ import annotations

from dataclasses import asdict
from datetime import date, timedelta
from fractions import Fraction
import hashlib
import json
from typing import Any, cast

from equity_feature_contracts import (
    AdjustmentSpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode,
    EvidenceRow, FeatureColumn, FeatureResult, InputBinding, PriceUnit,
    QualityRow, Reason, ResultMetadata, Status, validate_batch,
)
from equity_features import __version__
from ._context import decode_ef1_context, fail
from ._daily_context import ROLES, day, exact_keys, identity, integer, parse_json, rational
from ._definitions import ef1_definitions

FIELDS = ("close", "high", "low", "open")
KINDS = dict(zip(ROLES, ("calendar_manifest", "calendar_slot", "observation_coverage", "raw_observation", "common_observation", "basis_provenance")))
KEYS = {
    "calendar_manifest": {"version", "calendar_id", "revision", "timezone", "history_start_date", "target_date", "slot_count", "slots_sha256", "calendar_source"},
    "calendar_slots": {"date"},
    "observation_coverage": {"state", "raw_reference_id", "common_reference_id", "basis_reference_id"},
    "raw_observations": {"date", "open", "high", "low", "close", "volume", "invalid_fields"},
    "common_observations": {"date", "raw_reference_id", "open", "high", "low", "close"},
    "basis_provenance": {"raw_reference_id", "common_reference_id", "raw_source", "common_source", "raw_price_unit", "common_price_unit", "common_adjustment", "factor_num", "factor_den"},
}
LIMITS = dict(zip(ROLES, (2048, 512, 512, 768, 768, 1536)))
REASON_ORDER = (Reason.ABSENT_INPUT, Reason.NULL_FIELD, Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE, Reason.GOVERNED_GAP)
Row = dict[str, Any]


def _json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _hash(value: Any) -> str:
    return hashlib.sha256(_json(value).encode("ascii")).hexdigest()


def _known(row: Row, config: ConfigSpec) -> list[Reason]:
    k = row["known_at_ns"]
    return [Reason.UNKNOWN_AVAILABILITY] if k is None else ([Reason.FUTURE_KNOWLEDGE] if k > config.availability.knowledge_cutoff_ns else [])


def _coherent(p: Row) -> bool:
    return all(p[f] is not None and p[f] > 0 for f in FIELDS) and p["low"] <= min(p["open"], p["close"]) <= max(p["open"], p["close"]) <= p["high"]


def _known_invalid(p: Row) -> bool:
    if any(p[f] is not None and p[f] <= 0 for f in FIELDS):
        return True
    return any(p[left] is not None and p[right] is not None and p[left] > p[right]
        for left, right in (("low", "open"), ("low", "close"), ("low", "high"), ("open", "high"), ("close", "high")))


def _admission(p: Row, admission: Any) -> bool | None:
    # Known exclusions dominate unknown operands; otherwise membership is unknown.
    if p["invalid_fields"] or _known_invalid(p):
        return False
    if all(p[f] is not None for f in FIELDS):
        if not _coherent(p):
            return False
        lower, upper = admission["lower_range_ratio"], admission["upper_range_ratio"]
        if lower is not None and p["low"] * lower[1] < min(p["open"], p["close"]) * lower[0]:
            return False
        if upper is not None and p["high"] * upper[1] > max(p["open"], p["close"]) * upper[0]:
            return False
        return True
    return None


def _price_integer(value: Any, *, volume: bool = False) -> None:
    if value is None:
        return
    if type(value) is not int:
        fail(ErrorCode.INVALID_SCHEMA, "exact integer observation cell required")
    if not -(2**63) <= value <= 2**63 - 1:
        fail(ErrorCode.OVERFLOW, "daily observation exceeds int64")
    if volume and value < 0:
        fail(ErrorCode.INVALID_SCHEMA, "nonnegative volume required")


def _rows(batch: CanonicalBatch, role: str, config: ConfigSpec, entity: EntityKey) -> list[Row]:
    if batch.row_count > (1 if role == "calendar_manifest" else 1024 if role == "calendar_slots" else 1023):
        fail(ErrorCode.BOUNDS, "daily row bound exceeded")
    columns = {c.name: c.values for c in batch.columns}
    if any(name in columns for name in ("price", "factor_num", "factor_den")):
        fail(ErrorCode.INVALID_SCHEMA, "outer observation price/factor fields must be absent")
    required = {"instrument_id", "session_id", "reference_id", "fact_kind", "effective_start_ns", "effective_end_ns", "text", "known_at_ns"}
    if set(columns) != required:
        fail(ErrorCode.INVALID_SCHEMA, "exact daily reference columns required")
    rows: list[Row] = []
    for i in range(batch.row_count):
        row: Row = {name: values[i] for name, values in columns.items()}
        for name in ("instrument_id", "session_id", "reference_id", "fact_kind"):
            identity(row[name])
        if row["instrument_id"] != entity.instrument_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "daily instrument mismatch")
        if row["fact_kind"] != "ef1.daily." + KINDS[role]:
            fail(ErrorCode.INVALID_SCHEMA, "wrong daily role kind")
        for name in ("effective_start_ns", "effective_end_ns"):
            integer(row[name])
        if row["known_at_ns"] is not None:
            integer(row["known_at_ns"])
        p = parse_json(row["text"], LIMITS[role])
        exact_keys(p, KEYS[role])
        if role in ("calendar_slots", "raw_observations", "common_observations"):
            day(p["date"])
        if role in ("raw_observations", "common_observations"):
            for f in FIELDS:
                _price_integer(p[f])
            if role == "raw_observations":
                _price_integer(p["volume"], volume=True)
                invalid = p["invalid_fields"]
                if type(invalid) is not list or any(type(f) is not str or f not in FIELDS for f in invalid) or invalid != sorted(set(invalid)) or any(p[f] is not None for f in invalid):
                    fail(ErrorCode.INVALID_SCHEMA, "exact nonfinite field markers required")
            else:
                identity(p["raw_reference_id"])
        elif role == "observation_coverage":
            if p["state"] not in ("present", "absent_in_snapshot", "unknown"):
                fail(ErrorCode.INVALID_SCHEMA, "closed observation coverage state required")
            if p["state"] == "present":
                identity(p["raw_reference_id"])
                for name in ("common_reference_id", "basis_reference_id"):
                    if p[name] is not None:
                        identity(p[name])
            elif any(p[name] is not None for name in ("raw_reference_id", "common_reference_id", "basis_reference_id")):
                fail(ErrorCode.INVALID_SCHEMA, "absence cannot name observations")
        elif role == "calendar_manifest":
            for name in ("version", "calendar_id", "revision", "timezone", "slots_sha256"):
                identity(p[name])
            day(p["history_start_date"]); day(p["target_date"])
            integer(p["slot_count"], 1, 1024)
            exact_keys(p["calendar_source"], {"source_id", "snapshot_id", "mapping_version", "input_id"})
            for value in p["calendar_source"].values():
                identity(value)
        elif role == "basis_provenance":
            identity(p["raw_reference_id"]); identity(p["common_reference_id"])
            for name in ("raw_source", "common_source"):
                exact_keys(p[name], {"source_id", "snapshot_id", "mapping_version", "input_id"})
                for value in p[name].values():
                    identity(value)
            for name in ("raw_price_unit", "common_price_unit"):
                exact_keys(p[name], {"scale", "currency"})
                PriceUnit(**p[name])
            exact_keys(p["common_adjustment"], {"basis", "policy_version", "action_snapshot", "anchor"})
            AdjustmentSpec(**p["common_adjustment"])
            if p["factor_num"] is not None:
                if type(p["factor_num"]) is not int:
                    fail(ErrorCode.INVALID_SCHEMA, "exact factor integer required")
                integer(p["factor_num"], 1, 1_000_000)
            if p["factor_den"] is not None:
                if type(p["factor_den"]) is not int:
                    fail(ErrorCode.INVALID_SCHEMA, "exact factor integer required")
                integer(p["factor_den"], 1, 1_000_000)
            if p["factor_num"] is not None and p["factor_den"] is not None:
                rational(p["factor_num"], p["factor_den"])
        row["payload"] = p
        rows.append(row)
    return rows


def _population(batch: CanonicalBatch, rows: list[Row], role: str, config: ConfigSpec) -> None:
    """Population errors follow complete tuple grammar checks."""
    if len({r["reference_id"] for r in rows}) != len(rows) or len({r["session_id"] for r in rows}) != len(rows):
        fail(ErrorCode.DUPLICATE, "duplicate daily record/session")
    if role in ("calendar_slots", "raw_observations", "common_observations") and len({r["payload"]["date"] for r in rows}) != len(rows):
        fail(ErrorCode.DUPLICATE, "duplicate daily civil date")
    if any(r["effective_start_ns"] >= r["effective_end_ns"] for r in rows):
        fail(ErrorCode.BOUNDS, "positive daily interval required")
    if role not in ("calendar_manifest", "calendar_slots") and any(r["effective_end_ns"] > min(config.session.open_ns, config.availability.market_cutoff_ns) for r in rows):
        fail(ErrorCode.BOUNDS, "historical fact must complete before target")
    if any(a["effective_start_ns"] >= b["effective_start_ns"] for a, b in zip(rows, rows[1:])):
        fail(ErrorCode.INVALID_ORDER, "strict chronological daily rows required")
    if batch.metadata.coverage.observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "daily physical population mismatch")
    validate_batch(batch, required_fields=())


def _start(d: date, period: str) -> date:
    return d - timedelta(days=d.weekday()) if period == "iso_week" else d.replace(day=1, month=1) if period == "civil_ytd" else d.replace(day=1)


def compute_daily(batches: Any, config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    decode_ef1_context(config)
    if config.price_unit is None:
        fail(ErrorCode.INVALID_UNIT, "explicit daily common price unit required")
    common_unit = config.price_unit
    rr: Row | None
    cc: Row | None
    bb: Row | None
    cov: Row | None
    # Detach immutable mappings to canonical plain mathematical dictionaries.
    ctx = json.loads(cast(str, config.parameters[0].value))
    cal, admission, selection = ctx["calendar"], ctx["admission"], ctx["selection"]
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact daily target entity required")
    identity(entity.instrument_id)
    if type(batches) not in (tuple, list) or len(batches) != 6:
        fail(ErrorCode.INVALID_SCHEMA, "exact six nullable daily roles required")
    if any(b is not None and (type(b) is not CanonicalBatch or b.kind != DataKind.REFERENCE) for b in batches):
        fail(ErrorCode.INVALID_SCHEMA, "actual REFERENCE daily roles required")
    # Role spelling is checked across the whole tuple before any row grammar.
    for role, batch in zip(ROLES, batches):
        if batch is not None and any(c.name == "fact_kind" and any(v != "ef1.daily." + KINDS[role] for v in c.values) for c in batch.columns):
            fail(ErrorCode.INVALID_SCHEMA, "wrong daily positional role")
    actual = {r: b for r, b in zip(ROLES, batches) if b is not None}
    rows = {r: _rows(b, r, config, entity) for r, b in actual.items()}
    for role, batch in actual.items():
        _population(batch, rows[role], role, config)
    raw_unit = PriceUnit(**ctx["raw_price_unit"])
    for role, batch in actual.items():
        m = batch.metadata
        if m.namespace != config.session.namespace:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "daily namespace mismatch")
        if m.ordering != "declared" or m.duplicate_policy != "reject":
            fail(ErrorCode.INVALID_ORDER, "declared unique daily order required")
        if m.sampling != "none" or m.quantity_unit != "shares":
            fail(ErrorCode.INVALID_UNIT, "daily sampling/quantity mismatch")
        for source_value in asdict(m.source).values():
            identity(source_value)
        if asdict(m.source) != ctx["sources"][role]:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "daily role source binding mismatch")
        expected_unit = raw_unit if role == "raw_observations" else config.price_unit if role == "common_observations" else None
        if m.price_unit != expected_unit:
            fail(ErrorCode.INVALID_UNIT, "daily role price unit mismatch")
        expected_adjustment = config.adjustment if role == "common_observations" else AdjustmentSpec("raw", "raw-v1", "none", "none")
        if m.adjustment != expected_adjustment:
            fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "daily role basis mismatch")
        if m.interval_coverage:
            fail(ErrorCode.INVALID_SCHEMA, "daily interval coverage must be empty")
    slot_rows = rows.get("calendar_slots", [])
    slots = {r["session_id"]: r for r in slot_rows}
    historical = [r for r in slot_rows if r["session_id"] != entity.session_id]
    manifest_rows = rows.get("calendar_manifest", [])
    manifest = manifest_rows[0] if manifest_rows else None
    calendar_ready = bool(slot_rows and manifest)
    target = slots.get(entity.session_id)
    # Physical completed-time violations precede exact join/interval diagnostics.
    for role in ROLES:
        for r in rows.get(role, []):
            if r["effective_start_ns"] >= r["effective_end_ns"]:
                fail(ErrorCode.BOUNDS, "positive daily interval required")
            if role not in ("calendar_manifest",) and r["session_id"] != entity.session_id and r["effective_end_ns"] > min(config.session.open_ns, config.availability.market_cutoff_ns):
                fail(ErrorCode.BOUNDS, "historical daily fact is not completed")
            if role not in ("calendar_manifest", "calendar_slots") and r["session_id"] == entity.session_id:
                fail(ErrorCode.BOUNDS, "target observations are forbidden")
    if slot_rows:
        if target is None or (target["effective_start_ns"], target["effective_end_ns"], target["payload"]["date"]) != (config.session.open_ns, config.session.close_ns, cal["target_date"]):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "daily target calendar mismatch")
        dates = [r["payload"]["date"] for r in slot_rows]
        if dates != sorted(set(dates)) or any(not cal["history_start_date"] <= d <= cal["target_date"] for d in dates):
            fail(ErrorCode.INVALID_ORDER, "daily civil calendar order/fence mismatch")
        if any(a["effective_end_ns"] > b["effective_start_ns"] for a, b in zip(slot_rows, slot_rows[1:])):
            fail(ErrorCode.BOUNDS, "overlapping daily calendar slots")
        for r in slot_rows:
            if r["reference_id"] != r["session_id"]:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "daily slot identity mismatch")
    for role, batch in actual.items():
        m = batch.metadata
        if m.scope is None or (m.scope.end_ns, m.scope.eligibility_policy, m.scope.include_opening_auction, m.scope.include_closing_auction) != (config.session.close_ns, "ef1_daily_observations_v2", False, False) or slot_rows and m.scope.start_ns != slot_rows[0]["effective_start_ns"]:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "exact daily batch scope required")
        if role in ("calendar_manifest", "calendar_slots") and batch.row_count and (m.coverage.expected != batch.row_count or not m.coverage.complete):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "complete actual calendar population required")
        if role == "observation_coverage" and slot_rows and m.coverage.expected != len(historical):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "coverage expected calendar population mismatch")
    if manifest is not None:
        p = manifest["payload"]
        if manifest["reference_id"] != cal["manifest_reference_id"] or manifest["session_id"] != entity.session_id or _hash(p) != cal["manifest_sha256"]:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "daily manifest binding mismatch")
        if p["version"] != "ef1-daily-calendar-manifest1" or any(p[k] != cal[k] for k in ("calendar_id", "revision", "timezone", "history_start_date", "target_date")) or p["calendar_source"] != ctx["sources"]["calendar_slots"]:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "daily manifest declaration mismatch")
        if slot_rows:
            preimage = {"version": "ef1-daily-calendar-slots1", "namespace": config.session.namespace, "instrument_id": entity.instrument_id,
                **{k: cal[k] for k in ("calendar_id", "revision", "timezone", "history_start_date", "target_date")},
                "calendar_source": ctx["sources"]["calendar_slots"], "slots": [{"session_id": r["session_id"], "date": r["payload"]["date"], "open_ns": r["effective_start_ns"], "close_ns": r["effective_end_ns"], "known_at_ns": r["known_at_ns"]} for r in slot_rows]}
            if p["slot_count"] != len(slot_rows) or p["slots_sha256"] != _hash(preimage) or (manifest["effective_start_ns"], manifest["effective_end_ns"]) != (slot_rows[0]["effective_start_ns"], config.session.close_ns):
                fail(ErrorCode.INCONSISTENT_IDENTITY, "daily calendar digest/interval mismatch")
    coverage = {r["session_id"]: r for r in rows.get("observation_coverage", [])}
    raw = {r["session_id"]: r for r in rows.get("raw_observations", [])}
    common = {r["session_id"]: r for r in rows.get("common_observations", [])}
    basis = {r["session_id"]: r for r in rows.get("basis_provenance", [])}
    for role in ROLES[2:]:
        for r in rows.get(role, []):
            slot = slots.get(r["session_id"])
            if slot is not None:
                if (r["effective_start_ns"], r["effective_end_ns"]) != (slot["effective_start_ns"], slot["effective_end_ns"]):
                    fail(ErrorCode.INCONSISTENT_IDENTITY, "daily fact slot interval mismatch")
                if "date" in r["payload"] and r["payload"]["date"] != slot["payload"]["date"]:
                    fail(ErrorCode.INCONSISTENT_IDENTITY, "daily fact civil date mismatch")
            elif slot_rows:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "daily fact outside supplied calendar")
    for sid, cov in coverage.items():
        p = cov["payload"]
        rr = raw.get(sid)
        if p["state"] == "present":
            if rr is None and actual.get("raw_observations") is not None or rr is not None and rr["reference_id"] != p["raw_reference_id"]:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "daily present raw join mismatch")
            for role, by_sid, field in (("common_observations", common, "common_reference_id"), ("basis_provenance", basis, "basis_reference_id")):
                joined = by_sid.get(sid)
                if joined is not None and joined["reference_id"] != p[field]:
                    fail(ErrorCode.INCONSISTENT_IDENTITY, "daily existing common/basis join mismatch")
        elif rr is not None or sid in common or sid in basis:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "existing daily facts contradict non-present coverage")
    # Existing declarations must agree even when a physical parent role is
    # absent. Missingness cannot conceal contradictory retained source IDs.
    for sid in dict.fromkeys((*coverage, *raw, *common, *basis)):
        declared_raw_ids: set[str] = set()
        declared_common_ids: set[str] = set()
        cov = coverage.get(sid)
        if cov is not None and cov["payload"]["state"] == "present":
            declared_raw_ids.add(cov["payload"]["raw_reference_id"])
            if cov["payload"]["common_reference_id"] is not None:
                declared_common_ids.add(cov["payload"]["common_reference_id"])
        rr = raw.get(sid)
        if rr is not None:
            declared_raw_ids.add(rr["reference_id"])
        for by_sid in (common, basis):
            declared = by_sid.get(sid)
            if declared is not None:
                declared_raw_ids.add(declared["payload"]["raw_reference_id"])
        cc, bb = common.get(sid), basis.get(sid)
        if cc is not None:
            declared_common_ids.add(cc["reference_id"])
        if bb is not None:
            declared_common_ids.add(bb["payload"]["common_reference_id"])
        if len(declared_common_ids) > 1:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "contradictory declared common observation IDs")
        if len(declared_raw_ids) > 1:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "contradictory declared raw observation IDs")
    for sid, rr in raw.items():
        if coverage and sid not in coverage:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "unlisted raw observation")
    for sid, cc in common.items():
        rr = raw.get(sid)
        if rr is None and "raw_observations" in actual or rr is not None and cc["payload"]["raw_reference_id"] != rr["reference_id"]:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "orphan daily common row")
    for sid, bb in basis.items():
        rr, cc, p = raw.get(sid), common.get(sid), bb["payload"]
        if rr is None and "raw_observations" in actual:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "orphan daily basis raw parent")
        if (rr is not None and p["raw_reference_id"] != rr["reference_id"]) or (cc is not None and p["common_reference_id"] != cc["reference_id"]):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "orphan daily basis row")
        for field, role in (("raw_source", "raw_observations"), ("common_source", "common_observations")):
            if p[field] != ctx["sources"][role]:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "daily basis original source mismatch")
        if p["raw_price_unit"] != asdict(raw_unit) or p["common_price_unit"] != asdict(common_unit):
            fail(ErrorCode.INVALID_UNIT, "daily basis price units mismatch")
        if p["common_adjustment"] != asdict(config.adjustment):
            fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "daily basis adjustment mismatch")
        if config.adjustment.basis == "raw" and p["factor_num"] is not None and p["factor_den"] is not None and (p["factor_num"], p["factor_den"]) != (1, 1):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "raw identity requires factor one")
    # Raw cap is a population restriction before quality admission and selector.
    delivered = list(raw)
    cap = admission["raw_observation_lookback"]
    population = delivered[-cap:] if cap is not None else delivered
    admitted = {sid: _admission(raw[sid]["payload"], admission) for sid in population}
    eligible = [sid for sid in population if admitted[sid] is True]
    gates = cap is not None or admission["minimum_admitted_history"] > 0 or admission["require_latest_supplied_admitted"]
    gate_slots: set[str] = set()
    if gates:
        boundary = population[0] if cap is not None and len(population) == cap else None
        gate_slots = {r["session_id"] for r in historical if boundary is None or r["effective_start_ns"] >= slots[boundary]["effective_start_ns"]}
    kind = selection["kind"]
    target_date = day(cal["target_date"])
    governed_gap = False
    if kind == "last_observations":
        selected = eligible[-selection["N"]:]
        boundary = selected[0] if len(selected) == selection["N"] else None
        decision = {r["session_id"] for r in historical if boundary is None or r["effective_start_ns"] >= slots[boundary]["effective_start_ns"]}
        if cap is not None and len(population) == cap:
            decision &= gate_slots
    else:
        current_start = _start(target_date, selection["period"])
        if kind == "pre_target":
            required_start = current_start
            selected = [sid for sid in eligible if current_start <= day(raw[sid]["payload"]["date"]) < target_date]
            decision = {r["session_id"] for r in historical if current_start <= day(r["payload"]["date"]) < target_date}
        else:
            prior = [sid for sid in eligible if day(raw[sid]["payload"]["date"]) < current_start]
            chosen = _start(day(raw[prior[-1]]["payload"]["date"]), selection["period"]) if prior else None
            required_start = chosen if chosen is not None else day(cal["history_start_date"])
            selected = [sid for sid in prior if _start(day(raw[sid]["payload"]["date"]), selection["period"]) == chosen]
            decision = {r["session_id"] for r in historical if required_start <= day(r["payload"]["date"]) < current_start}
            if chosen is None and _start(day(cal["history_start_date"]), selection["period"]) != day(cal["history_start_date"]):
                governed_gap = True
        governed_gap |= day(cal["history_start_date"]) > required_start
    required = decision | gate_slots
    expected: int | None = len(required) if calendar_ready and not governed_gap else None
    observed = sum(sid in coverage and coverage[sid]["payload"]["state"] != "unknown" for sid in required) if calendar_ready else 0
    base: list[Reason] = []
    if "raw_observations" not in actual:
        base.append(Reason.ABSENT_INPUT)
    if not calendar_ready:
        base.append(Reason.ABSENT_INPUT)
    else:
        assert manifest is not None and target is not None
        base.extend(_known(manifest, config))
        base.extend(_known(target, config))
        if governed_gap:
            base.append(Reason.GOVERNED_GAP)
        for sid in sorted(required):
            base.extend(_known(slots[sid], config))
            cov = coverage.get(sid)
            if cov is None:
                base.append(Reason.ABSENT_INPUT if not rows.get("observation_coverage") else Reason.GOVERNED_GAP)
                continue
            base.extend(_known(cov, config))
            state = cov["payload"]["state"]
            if state == "unknown":
                base.append(Reason.GOVERNED_GAP)
            elif state == "present":
                rr = raw.get(sid)
                if rr is None:
                    base.append(Reason.ABSENT_INPUT)
                else:
                    base.extend(_known(rr, config))
                    if _admission(rr["payload"], admission) is None:
                        base.append(Reason.NULL_FIELD)
    price_reasons = list(base)
    for sid in selected:
        rr, cc, bb = raw[sid], common.get(sid), basis.get(sid)
        if cc is None or bb is None:
            price_reasons.append(Reason.ABSENT_INPUT)
        if cc is not None:
            price_reasons.extend(_known(cc, config))
            if _known_invalid(cc["payload"]):
                fail(ErrorCode.INCONSISTENT_IDENTITY, "selected common known geometry mismatch")
            if any(cc["payload"][f] is None for f in FIELDS):
                price_reasons.append(Reason.NULL_FIELD)
            elif not _coherent(cc["payload"]):
                fail(ErrorCode.INCONSISTENT_IDENTITY, "selected common geometry mismatch")
        if bb is not None:
            price_reasons.extend(_known(bb, config))
            if bb["payload"]["factor_num"] is None or bb["payload"]["factor_den"] is None:
                price_reasons.append(Reason.NULL_FIELD)
        if cc is not None and bb is not None:
            p = bb["payload"]
            for f in FIELDS:
                left = None if cc["payload"][f] is None or p["factor_den"] is None else cc["payload"][f] * 10**raw_unit.scale * p["factor_den"]
                right = None if rr["payload"][f] is None or p["factor_num"] is None else rr["payload"][f] * 10**common_unit.scale * p["factor_num"]
                if any(v is not None and abs(v) >= 10**38 for v in (left, right)):
                    fail(ErrorCode.OVERFLOW, "selected basis product exceeds decimal128")
                if left is not None and right is not None and left != right:
                    fail(ErrorCode.INCONSISTENT_IDENTITY, "selected common factor equality mismatch")
    gate_status: Status | None = None
    gate_reason: Reason | None = None
    if gates and not base:
        if not eligible:
            gate_status, gate_reason = Status.NOT_APPLICABLE, Reason.NO_ELIGIBLE_OBSERVATIONS
        elif admission["require_latest_supplied_admitted"] and population and admitted[population[-1]] is not True:
            gate_status, gate_reason = Status.NOT_APPLICABLE, Reason.INELIGIBLE
        elif len(eligible) < admission["minimum_admitted_history"]:
            gate_status, gate_reason = Status.INSUFFICIENT_HISTORY, Reason.INSUFFICIENT_HISTORY
    values: list[FeatureColumn] = []
    qualities: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    ordered_required = [r["session_id"] for r in historical if r["session_id"] in required]
    for definition in ef1_definitions(config):
        name = definition.feature_id.rsplit(".", 1)[1]
        count = name == "selected_observed_count"
        reasons = tuple(r for r in REASON_ORDER if r in (base if count else price_reasons))
        status = Status.MISSING_INPUT if any(r != Reason.GOVERNED_GAP for r in reasons) else Status.INCOMPLETE_COVERAGE if reasons else Status.AVAILABLE
        if not base and gate_status is not None:
            assert gate_reason is not None
            status, reasons = gate_status, (gate_reason,)
        if status == Status.AVAILABLE and not count:
            if kind == "last_observations" and len(selected) < selection["N"]:
                status, reasons = Status.INSUFFICIENT_HISTORY, (Reason.INSUFFICIENT_HISTORY,)
            elif not selected:
                status, reasons = Status.NOT_APPLICABLE, (Reason.NO_ELIGIBLE_OBSERVATIONS,)
        value: Any = None
        witness: str | None = None
        if status == Status.AVAILABLE:
            if count:
                value = len(selected)
            else:
                witness = selected[0] if name == "open" else min(selected, key=lambda sid: (-common[sid]["payload"][name] if name == "high" else common[sid]["payload"][name], raw[sid]["payload"]["date"], raw[sid]["reference_id"]))
                value = float(Fraction(common[witness]["payload"][name], 10**common_unit.scale))
        values.append(FeatureColumn(definition.feature_id, "daily-observations-v2", definition.dtype, definition.unit, (entity,), (value,)))
        qualities.append(QualityRow(entity, definition.feature_id, status, expected, observed, reasons))
        if status != Status.AVAILABLE:
            continue
        witnesses: list[tuple[str, Row]] = []
        if manifest is not None:
            witnesses.append(("calendar_manifest", manifest))
        if ordered_required:
            for sid in (ordered_required[0], ordered_required[-1]):
                if sid in coverage:
                    witnesses.append(("observation_coverage", coverage[sid]))
        if count:
            if selected:
                witnesses.extend(("raw_observations", raw[sid]) for sid in (selected[0], selected[-1]))
            if cap is not None and len(population) == cap and population and population[0] in coverage:
                witnesses.append(("observation_coverage", coverage[population[0]]))
        elif witness is not None:
            witnesses.extend((("raw_observations", raw[witness]), ("common_observations", common[witness]), ("basis_provenance", basis[witness])))
        if admission["require_latest_supplied_admitted"] and population:
            witnesses.append(("raw_observations", raw[population[-1]]))
        for role, r in witnesses:
            evidence.append(EvidenceRow(entity, definition.feature_id, actual[role].metadata.source.input_id, r["reference_id"], r["effective_start_ns"], r["known_at_ns"], r["effective_start_ns"], r["effective_end_ns"]))
    evidence = sorted({(r.feature_id, r.input_id, r.row_id): r for r in evidence}.values(), key=lambda r: (r.feature_id, r.input_id, r.row_id))
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability, config.digest,
        tuple(InputBinding(r, actual[r].kind, actual[r].metadata) for r in sorted(actual)), "ef1", __version__, math_policy_version="v1", evidence_limit=28)
    return FeatureResult(tuple(values), tuple(qualities), metadata, tuple(evidence))
