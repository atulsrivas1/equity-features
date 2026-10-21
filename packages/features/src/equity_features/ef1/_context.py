"""Bounded mathematical selections; acquired provenance stays in canonical inputs."""
from __future__ import annotations

from collections.abc import Mapping
from dataclasses import replace
import hashlib
import json
from types import MappingProxyType
from typing import Any, NoReturn, cast

from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ConfigSpec, ContractError, ErrorCode,
    Parameter, PriceUnit, SessionSpec, WindowSpec,
)

_KEYS = {"version", "producer", "calendar", "selection"}
_DEFINITION_KEYS = {"anchor_id", "reset_id", "start_ns", "selection_policy_id", "revision"}
_CALENDAR_KEYS = {"calendar_id", "revision", "timezone", "target_date", "sessions", "segments",
                  "scheduled_close_ns", "early_close"}
_I64_MIN, _I64_MAX = -(2**63), 2**63 - 1


def fail(code: ErrorCode, message: str) -> NoReturn:
    raise ContractError(code, message)


def label(value: object) -> str:
    if type(value) is not str or not value.strip():
        fail(ErrorCode.INVALID_SCHEMA, "nonempty exact string required")
    if len(value) > 128 or any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value):
        fail(ErrorCode.BOUNDS, "unsafe or over-limit identity")
    if len(value.encode("utf-8")) > 512:
        fail(ErrorCode.BOUNDS, "over-limit UTF8 identity")
    return value


def _integer(value: object) -> int:
    if type(value) is not int or not _I64_MIN <= value <= _I64_MAX:
        fail(ErrorCode.BOUNDS, "exact int64 UTCns required")
    return value


def _tree(value: Any, depth: int = 0) -> None:
    if depth > 8:
        fail(ErrorCode.BOUNDS, "context nesting limit exceeded")
    if type(value) is dict:
        if len(value) > 64:
            fail(ErrorCode.BOUNDS, "context collection limit exceeded")
        for key, item in value.items():
            label(key)
            _tree(item, depth + 1)
    elif type(value) is list:
        if len(value) > 64:
            fail(ErrorCode.BOUNDS, "context collection limit exceeded")
        for item in value:
            _tree(item, depth + 1)
    elif type(value) is str:
        label(value)
    elif value is not None and type(value) is not int and type(value) is not bool:
        fail(ErrorCode.INVALID_CONFIG, "unsupported context scalar")


def canonical_json(value: Any) -> str:
    """Canonical ASCII mathematical JSON, including the anchor-proof hash boundary."""
    try:
        text = json.dumps(value, ensure_ascii=True, sort_keys=True,
                          separators=(",", ":"), allow_nan=False)
    except (ValueError, TypeError, OverflowError):
        fail(ErrorCode.INVALID_CONFIG, "invalid mathematical context")
    if len(text) > 4096 or len(text.encode("ascii")) > 4096:
        fail(ErrorCode.BOUNDS, "context exceeds4096ASCIIbytes")
    return text


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            fail(ErrorCode.DUPLICATE, "duplicate context field")
        result[key] = value
    return result


def _constant(_: str) -> None:
    fail(ErrorCode.INVALID_CONFIG, "nonfinite context constant")


def _date_label(value: object) -> str:
    """Validate a supplied Gregorian date without an OS calendar/timezone lookup."""
    text = label(value)
    if len(text) != 10 or text[4] != "-" or text[7] != "-" or any(
            char not in "0123456789" for char in text[:4] + text[5:7] + text[8:]):
        fail(ErrorCode.INVALID_CONFIG, "exact Gregorian date label required")
    year, month, day = int(text[:4]), int(text[5:7]), int(text[8:])
    if not 1 <= year <= 9999 or not 1 <= month <= 12:
        fail(ErrorCode.BOUNDS, "Gregorian date outside bounds")
    leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
    lengths = (31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31)
    if not 1 <= day <= lengths[month - 1]:
        fail(ErrorCode.BOUNDS, "Gregorian date outside bounds")
    return text


def _clock_calendar(value: Any) -> None:
    if type(value) is not dict or set(value) != _CALENDAR_KEYS:
        fail(ErrorCode.INVALID_CONFIG, "exact supplied calendar fields required")
    for key in ("calendar_id", "revision", "timezone"):
        label(value[key])
    _date_label(value["target_date"])
    _integer(value["scheduled_close_ns"])
    if type(value["early_close"]) is not bool:
        fail(ErrorCode.INVALID_CONFIG, "explicit Boolean early-close declaration required")
    sessions = value["sessions"]
    if type(sessions) is not list or not 1 <= len(sessions) <= 64:
        fail(ErrorCode.BOUNDS, "bounded nonempty supplied sessions required")
    ids: set[str] = set()
    previous_end: int | None = None
    previous_date: str | None = None
    for row in sessions:
        if type(row) is not list or len(row) != 4:
            fail(ErrorCode.INVALID_CONFIG, "exact calendar session row required")
        name, civil_date = label(row[0]), _date_label(row[1])
        start_ns, end_ns = _integer(row[2]), _integer(row[3])
        if name in ids:
            fail(ErrorCode.DUPLICATE, "duplicate governed session identity")
        if start_ns >= end_ns:
            fail(ErrorCode.BOUNDS, "positive supplied session interval required")
        if previous_end is not None and start_ns < previous_end or previous_date is not None and civil_date < previous_date:
            fail(ErrorCode.INVALID_ORDER, "supplied calendar sessions are unordered")
        ids.add(name)
        previous_end, previous_date = end_ns, civil_date
    segments = value["segments"]
    if type(segments) is not list or not 1 <= len(segments) <= 3:
        fail(ErrorCode.BOUNDS, "bounded supplied phase segments required")
    seen: set[str] = set()
    previous_end = None
    previous_rank = -1
    ranks = {"premarket": 0, "regular": 1, "postmarket": 2}
    for row in segments:
        if type(row) is not list or len(row) != 3 or type(row[0]) is not str or row[0] not in ranks:
            fail(ErrorCode.INVALID_CONFIG, "closed calendar phase row required")
        name = row[0]
        start_ns, end_ns = _integer(row[1]), _integer(row[2])
        if name in seen:
            fail(ErrorCode.DUPLICATE, "duplicate phase segment")
        if start_ns >= end_ns:
            fail(ErrorCode.BOUNDS, "positive phase interval required")
        if ranks[name] <= previous_rank or previous_end is not None and start_ns < previous_end:
            fail(ErrorCode.INVALID_ORDER, "overlapping or unordered phase segments")
        seen.add(name)
        previous_end, previous_rank = end_ns, ranks[name]
    if "regular" not in seen:
        fail(ErrorCode.INVALID_CONFIG, "actual regular phase required")


def _parse(text: object) -> dict[str, Any]:
    if type(text) is not str:
        fail(ErrorCode.INVALID_CONFIG, "context must be an ASCII string")
    if len(text) > 4096:
        fail(ErrorCode.BOUNDS, "context exceeds4096codepoints")
    if not text.isascii() or any(ord(c) < 32 or ord(c) == 127 for c in text):
        fail(ErrorCode.INVALID_CONFIG, "canonical ASCII context required")
    try:
        raw = json.loads(text, object_pairs_hook=_pairs, parse_constant=_constant)
    except ContractError:
        raise
    except (ValueError, TypeError, RecursionError):
        fail(ErrorCode.INVALID_CONFIG, "invalid mathematical JSON")
    _tree(raw)
    if type(raw) is not dict or set(raw) != _KEYS:
        fail(ErrorCode.INVALID_CONFIG, "exact EF1 context fields required")
    if raw["version"] != "ef1-context1":
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported EF1 context")
    if raw["producer"] == "anchor":
        if raw["calendar"] is not None:
            fail(ErrorCode.INVALID_CONFIG, "anchor producer has no calendar context")
        selection = raw["selection"]
        if type(selection) is not dict or set(selection) != {"mode", "definition"}:
            fail(ErrorCode.INVALID_CONFIG, "exact anchor selection required")
        if selection["mode"] not in ("trades", "bars_actual_notional"):
            fail(ErrorCode.UNSUPPORTED_CAPABILITY, "unsupported anchor sampling")
        definition = selection["definition"]
        if type(definition) is not dict or set(definition) != _DEFINITION_KEYS:
            fail(ErrorCode.INVALID_CONFIG, "exact anchor definition required")
        for key in _DEFINITION_KEYS - {"start_ns"}:
            label(definition[key])
        _integer(definition["start_ns"])
    elif raw["producer"] == "clock":
        if type(raw["selection"]) is not dict or raw["selection"]:
            fail(ErrorCode.INVALID_CONFIG, "clock selection must be an empty object")
        _clock_calendar(raw["calendar"])
    else:
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "EF1 producer is not implemented")
    if canonical_json(raw) != text:
        fail(ErrorCode.INVALID_CONFIG, "noncanonical mathematical JSON")
    return cast(dict[str, Any], raw)


def _freeze(value: Any) -> Any:
    if type(value) is dict:
        return MappingProxyType({key: _freeze(item) for key, item in value.items()})
    if type(value) is list:
        return tuple(_freeze(item) for item in value)
    return value


def _components(config: ConfigSpec) -> None:
    if type(config) is not ConfigSpec:
        fail(ErrorCode.INVALID_CONFIG, "canonical ConfigSpec required")
    # Revalidate public owned scalar/record components, without reading a clock.
    replace(config.session)
    replace(config.window)
    replace(config.availability)
    replace(config.adjustment)
    if config.price_unit is not None:
        if type(config.price_unit) is not PriceUnit:
            fail(ErrorCode.INVALID_UNIT, "canonical PriceUnit required")
        replace(config.price_unit)
        label(config.price_unit.currency)
    for text in (config.session.namespace, config.session.session_id,
                 config.session.timezone_label,
                 config.adjustment.basis, config.adjustment.policy_version,
                 config.adjustment.action_snapshot, config.adjustment.anchor):
        label(text)
    for interval in config.session.intervals:
        label(interval.name)


def decode_ef1_context(config: ConfigSpec) -> Mapping[str, Any]:
    """Validate a canonical config and return a recursively immutable detached selection."""
    _components(config)
    if (config.algorithm_version, config.schema_version) != ("v1", "1"):
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported EF1 config identity/version")
    if len(config.parameters) != 1 or config.parameters[0].name != "ef1_context_json":
        fail(ErrorCode.INVALID_CONFIG, "one exact EF1 context parameter required")
    raw = _parse(config.parameters[0].value)
    if config.identity != "ef1." + raw["producer"]:
        fail(ErrorCode.INCOMPATIBLE_VERSION, "EF1 producer/config identity mismatch")
    if raw["producer"] == "anchor":
        if type(config.price_unit) is not PriceUnit:
            fail(ErrorCode.INVALID_UNIT, "anchor prices require an explicit PriceUnit")
        if config.window != WindowSpec(1, config.session.session_id,
                                       (config.session.session_id,), "completed_eod"):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "anchor window must be target-only")
        if raw["selection"]["definition"]["start_ns"] >= config.availability.market_cutoff_ns:
            fail(ErrorCode.BOUNDS, "anchor must strictly precede cutoff")
    else:
        calendar = raw["calendar"]
        ids = tuple(row[0] for row in calendar["sessions"])
        if config.session.session_id not in ids or config.window != WindowSpec(
                len(ids), config.session.session_id, ids, "completed_eod"):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "clock governed window mismatch")
        target = next(row for row in calendar["sessions"] if row[0] == config.session.session_id)
        regular = next(row for row in calendar["segments"] if row[0] == "regular")
        if (target[1], target[2], target[3], calendar["timezone"]) != (
                calendar["target_date"], config.session.open_ns, config.session.close_ns,
                config.session.timezone_label) or tuple(regular[1:]) != (
                    config.session.open_ns, config.session.close_ns):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "actual target date/regular schedule mismatch")
        scheduled = calendar["scheduled_close_ns"]
        if (scheduled, calendar["early_close"]) != (
                config.session.scheduled_close_ns, config.session.early_close):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "actual scheduled-close declarations differ")
        if scheduled < config.session.close_ns or calendar["early_close"] != (config.session.close_ns < scheduled):
            fail(ErrorCode.BOUNDS, "inconsistent actual/scheduled close")
    return cast(Mapping[str, Any], _freeze(raw))


def build_ef1_config(selection: dict[str, Any], *, session: SessionSpec,
                     window: WindowSpec, availability: AvailabilitySpec,
                     price_unit: PriceUnit | None, adjustment: AdjustmentSpec) -> ConfigSpec:
    """Build the exact reviewed config from the full context envelope, not source facts."""
    if type(selection) is not dict:
        fail(ErrorCode.INVALID_CONFIG, "concrete mathematical context dictionary required")
    _tree(selection)
    text = canonical_json(selection)
    raw = _parse(text)
    config = ConfigSpec("ef1." + raw["producer"], "v1", (Parameter("ef1_context_json", text),),
                        session, window, availability, adjustment, price_unit)
    decode_ef1_context(config)
    return config


def anchor_proof_id(context: Mapping[str, Any]) -> str:
    """Return the exact hash identity expected from an actual anchor declaration."""
    definition = dict(context["selection"]["definition"])
    return "a1:" + hashlib.sha256(canonical_json(definition).encode("ascii")).hexdigest()


def calendar_proof_id(context: Mapping[str, Any]) -> str:
    calendar = dict(context["calendar"])
    return "c1:" + hashlib.sha256(canonical_json(calendar).encode("ascii")).hexdigest()
