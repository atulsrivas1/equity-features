"""Closed, bounded daily observation configuration; no acquired facts."""
from __future__ import annotations

from collections.abc import Mapping
from datetime import date
import json
from math import gcd
import re
from typing import Any, cast

from equity_feature_contracts import ConfigSpec, ContractError, ErrorCode, PriceUnit, SourceBinding, WindowSpec
from ._context import _components, _freeze, _tree, canonical_json, fail

ROLES = ("calendar_manifest", "calendar_slots", "observation_coverage", "raw_observations", "common_observations", "basis_provenance")


def exact_keys(value: Any, keys: set[str], code: ErrorCode = ErrorCode.INVALID_SCHEMA) -> None:
    if type(value) is not dict or set(value) != keys:
        fail(code, "closed daily field set required")


def identity(value: Any) -> str:
    if type(value) is not str or not 1 <= len(value) <= 128 or any(not 32 <= ord(c) < 127 for c in value):
        fail(ErrorCode.BOUNDS, "bounded printable ASCII identity required")
    return value


def day(value: Any) -> date:
    if type(value) is not str or re.fullmatch(r"[0-9]{4}-[0-9]{2}-[0-9]{2}", value) is None:
        fail(ErrorCode.INVALID_SCHEMA, "canonical civil date required")
    try:
        parsed = date.fromisoformat(value)
    except ValueError:
        fail(ErrorCode.BOUNDS, "invalid civil date")
    return parsed


def integer(value: Any, lo: int = -(2**63), hi: int = 2**63 - 1) -> int:
    if type(value) is not int or not lo <= value <= hi:
        fail(ErrorCode.BOUNDS, "exact bounded integer required")
    return value


def rational(num: Any, den: Any) -> None:
    integer(num, 1, 1_000_000); integer(den, 1, 1_000_000)
    if gcd(num, den) != 1:
        fail(ErrorCode.INVALID_SCHEMA, "reduced rational required")


def parse_json(text: Any, limit: int, code: ErrorCode = ErrorCode.INVALID_SCHEMA) -> dict[str, Any]:
    if type(text) is not str or len(text) > limit or not text.isascii():
        fail(ErrorCode.BOUNDS, "bounded ASCII JSON required")
    def pairs(rows: list[tuple[str, Any]]) -> dict[str, Any]:
        out: dict[str, Any] = {}
        for key, value in rows:
            if key in out:
                fail(ErrorCode.DUPLICATE, "duplicate JSON key")
            out[key] = value
        return out
    try:
        value = json.loads(text, object_pairs_hook=pairs,
            parse_constant=lambda _: fail(code, "nonfinite JSON scalar"),
            parse_float=lambda _: fail(code, "integer JSON profile required"))
    except ContractError:
        raise
    except (ValueError, TypeError, RecursionError):
        fail(code, "invalid JSON")
    _tree(value)
    if type(value) is not dict or json.dumps(value, ensure_ascii=True, sort_keys=True, separators=(",", ":"), allow_nan=False) != text:
        fail(code, "canonical JSON object required")
    return cast(dict[str, Any], value)


def decode_daily(config: ConfigSpec) -> Mapping[str, Any]:
    _components(config)
    identity(config.session.namespace); identity(config.session.session_id)
    if (config.identity, config.algorithm_version, config.schema_version) != ("ef1.daily_observations", "daily-observations-v2", "1"):
        fail(ErrorCode.INCOMPATIBLE_VERSION, "daily config version mismatch")
    if len(config.parameters) != 1 or config.parameters[0].name != "ef1_context":
        fail(ErrorCode.INVALID_CONFIG, "one exact daily context required")
    raw = parse_json(config.parameters[0].value, 4096, ErrorCode.INVALID_CONFIG)
    exact_keys(raw, {"version", "producer", "calendar", "selection", "admission", "sources", "raw_price_unit"}, ErrorCode.INVALID_CONFIG)
    if (raw["version"], raw["producer"]) != ("ef1-daily-context2", "daily_observations"):
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported daily context")
    a = raw["admission"]
    exact_keys(a, {"profile", "policy_id", "lower_range_ratio", "upper_range_ratio", "raw_observation_lookback", "minimum_admitted_history", "require_latest_supplied_admitted"}, ErrorCode.INVALID_CONFIG)
    if a["profile"] != "exact_integer_price_units_v1":
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "unsupported raw numeric profile")
    identity(a["policy_id"])
    for name in ("lower_range_ratio", "upper_range_ratio"):
        ratio = a[name]
        if ratio is not None:
            if type(ratio) is not list or len(ratio) != 2:
                fail(ErrorCode.INVALID_CONFIG, "exact rational pair required")
            rational(*ratio)
    if a["raw_observation_lookback"] is not None:
        integer(a["raw_observation_lookback"], 1, 1023)
    integer(a["minimum_admitted_history"], 0, 1023)
    if type(a["require_latest_supplied_admitted"]) is not bool:
        fail(ErrorCode.INVALID_CONFIG, "exact latest guard Boolean required")
    s = raw["selection"]
    if type(s) is not dict:
        fail(ErrorCode.INVALID_CONFIG, "closed daily selector required")
    if s.get("kind") == "last_observations":
        exact_keys(s, {"kind", "N"}, ErrorCode.INVALID_CONFIG)
        if type(s["N"]) is not int or not 1 <= s["N"] <= 252:
            fail(ErrorCode.INVALID_CONFIG, "last observation count must be 1 through 252")
    elif s.get("kind") in ("pre_target", "latest_observed_prior"):
        exact_keys(s, {"kind", "period"}, ErrorCode.INVALID_CONFIG)
        if s["period"] not in (("iso_week", "civil_month", "civil_ytd") if s["kind"] == "pre_target" else ("iso_week", "civil_month")):
            fail(ErrorCode.INVALID_CONFIG, "unsupported daily period")
    else:
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "unsupported daily selector")
    c = raw["calendar"]
    exact_keys(c, {"calendar_id", "revision", "timezone", "history_start_date", "target_date", "manifest_reference_id", "manifest_sha256"}, ErrorCode.INVALID_CONFIG)
    for name in ("calendar_id", "revision", "timezone", "manifest_reference_id"):
        identity(c[name])
    if day(c["history_start_date"]) > day(c["target_date"]) or c["timezone"] != config.session.timezone_label:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "daily calendar fence mismatch")
    if type(c["manifest_sha256"]) is not str or re.fullmatch("[0-9a-f]{64}", c["manifest_sha256"]) is None:
        fail(ErrorCode.INVALID_CONFIG, "exact calendar digest required")
    exact_keys(raw["sources"], set(ROLES), ErrorCode.INVALID_CONFIG)
    for role in ROLES:
        source = raw["sources"][role]
        exact_keys(source, {"source_id", "snapshot_id", "mapping_version", "input_id"}, ErrorCode.INVALID_CONFIG)
        for value in source.values():
            identity(value)
        SourceBinding(**source)
        if source["mapping_version"] != "ef1-daily-map2":
            fail(ErrorCode.INCOMPATIBLE_VERSION, "daily mapping mismatch")
    if len({s["input_id"] for s in raw["sources"].values()}) != 6:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "distinct daily input IDs required")
    exact_keys(raw["raw_price_unit"], {"scale", "currency"}, ErrorCode.INVALID_CONFIG)
    unit = PriceUnit(**raw["raw_price_unit"])
    if config.price_unit is None or unit.currency != config.price_unit.currency:
        fail(ErrorCode.INVALID_UNIT, "daily same currency required")
    if config.adjustment.basis == "total_return":
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "total return daily basis unsupported")
    if config.window != WindowSpec(1, config.session.session_id, (config.session.session_id,), "prior_only"):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "daily target-only prior window required")
    if not config.session.open_ns <= config.availability.market_cutoff_ns <= config.session.close_ns:
        fail(ErrorCode.BOUNDS, "daily cutoff outside target")
    return cast(Mapping[str, Any], _freeze(raw))
