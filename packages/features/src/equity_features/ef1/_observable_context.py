"""Closed observable-v2 mathematical context; no acquisition or mutable state."""
from __future__ import annotations

import json
import re
from collections.abc import Mapping
from typing import Any, cast

from equity_feature_contracts import AdjustmentSpec, ConfigSpec, ErrorCode, PriceUnit, WindowSpec
from ._context import (_clock_calendar, _components, _constant, _freeze, _pairs,
                       _tree, canonical_json, fail)

PRODUCERS = ("opening_trade", "opening_trade_seconds", "status_history")
TOKEN = re.compile(r"[A-Za-z0-9._-]{1,64}\Z", re.ASCII)


def parse_observable(text: object) -> dict[str, Any]:
    if type(text) is not str:
        fail(ErrorCode.INVALID_CONFIG, "observable context must be text")
    if len(text) > 4096:
        fail(ErrorCode.BOUNDS, "observable context exceeds4096bytes")
    if not text.isascii():
        fail(ErrorCode.INVALID_CONFIG, "ASCII observable context required")
    try:
        raw = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    except (ValueError, TypeError, RecursionError):
        fail(ErrorCode.INVALID_CONFIG, "invalid observable JSON")
    _tree(raw)
    if type(raw) is not dict or set(raw) != {"version", "producer", "calendar", "selection"}:
        fail(ErrorCode.INVALID_CONFIG, "closed observable context required")
    if raw["version"] != "ef1-observable-context2" or raw["producer"] not in PRODUCERS:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported observable version/producer")
    if type(raw["calendar"]) is dict and raw["calendar"].get("sessions") == []:
        fail(ErrorCode.INVALID_CONFIG, "target is not a supplied governed session")
    _clock_calendar(raw["calendar"])
    s = raw["selection"]
    if type(s) is not dict or set(s) != {"epoch", "publisher", "source_id", "source_snapshot", "mapping_version",
            "population", "include_opening_auction", "action_map", "flag_map"}:
        fail(ErrorCode.INVALID_CONFIG, "closed observable selection required")
    for name in ("epoch", "publisher", "source_id", "source_snapshot"):
        if type(s[name]) is not str or TOKEN.fullmatch(s[name]) is None:
            fail(ErrorCode.INVALID_CONFIG, "bounded original selection token required")
    if s["mapping_version"] != "ef1-observable-map2" or s["population"] != "regular_half_open_v2":
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported observable mapping/population")
    if type(s["include_opening_auction"]) is not bool:
        fail(ErrorCode.INVALID_CONFIG, "explicit opening auction Boolean required")
    if raw["producer"] != "status_history":
        if s["action_map"] != [] or s["flag_map"] != []:
            fail(ErrorCode.INVALID_CONFIG, "opening cannot select history interpretations")
    else:
        if s["include_opening_auction"] or type(s["action_map"]) is not list or len(s["action_map"]) > 64:
            fail(ErrorCode.INVALID_CONFIG, "bounded history interpretation required")
        previous = -1
        for row in s["action_map"]:
            if type(row) is not list or len(row) != 2 or type(row[0]) is not int or not 0 <= row[0] <= 65535:
                fail(ErrorCode.INVALID_CONFIG, "exact uint16 action mapping required")
            if row[0] <= previous or row[1] not in ("halt", "initial", "active", "resume", "irrelevant", "unknown"):
                fail(ErrorCode.INVALID_CONFIG, "strict unique closed action mapping required")
            previous = row[0]
        flags = s["flag_map"]
        if type(flags) is not list or len(flags) != 3:
            fail(ErrorCode.INVALID_CONFIG, "three original flag mappings required")
        for row, name in zip(flags, ("trading", "quoting", "ssr")):
            if type(row) is not list or len(row) != 3 or row[0] != name or row[1] == row[2] or any(
                    type(v) is not str or re.fullmatch(r"[0-7][0-9a-f]", v) is None for v in row[1:]):
                fail(ErrorCode.INVALID_CONFIG, "ordered distinct original ASCII flag bytes required")
    if canonical_json(raw) != text:
        fail(ErrorCode.INVALID_CONFIG, "canonical observable JSON required")
    return cast(dict[str, Any], raw)


def decode_observable(config: ConfigSpec) -> Mapping[str, Any]:
    _components(config)
    if (config.algorithm_version, config.schema_version) != ("observable-v2", "1"):
        fail(ErrorCode.INCOMPATIBLE_VERSION, "observable config version mismatch")
    if len(config.parameters) != 1 or config.parameters[0].name != "ef1_context_json":
        fail(ErrorCode.INVALID_CONFIG, "one observable context parameter required")
    raw = parse_observable(config.parameters[0].value)
    if config.identity != "ef1." + raw["producer"]:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "observable producer identity mismatch")
    c, s = raw["calendar"], config.session
    if len(c["sessions"]) != 1 or c["sessions"][0] != [s.session_id, c["target_date"], s.open_ns, s.close_ns]:
        fail(ErrorCode.INVALID_CONFIG, "actual target governed calendar required")
    if config.window != WindowSpec(1, s.session_id, (s.session_id,), "completed_eod"):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "observable target-only window required")
    regular = next(row for row in c["segments"] if row[0] == "regular")
    if regular[1:] != [s.open_ns, s.close_ns] or (c["timezone"], c["scheduled_close_ns"], c["early_close"]) != (
            s.timezone_label, s.scheduled_close_ns, s.early_close):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "observable schedule mismatch")
    if c["scheduled_close_ns"] < s.close_ns or c["early_close"] != (s.close_ns < c["scheduled_close_ns"]):
        fail(ErrorCode.BOUNDS, "inconsistent scheduled close")
    if s.include_closing_auction or s.include_opening_auction != raw["selection"]["include_opening_auction"]:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "observable auction policy mismatch")
    if raw["producer"] == "status_history":
        if config.price_unit is not None or config.adjustment != AdjustmentSpec("raw", "raw-v1", "none", "none"):
            fail(ErrorCode.INVALID_CONFIG, "history requires raw adjustment and no price unit")
    elif type(config.price_unit) is not PriceUnit:
        fail(ErrorCode.INVALID_UNIT, "opening requires actual market PriceUnit")
    return cast(Mapping[str, Any], _freeze(raw))
