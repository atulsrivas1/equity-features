"""Bounded mathematical selection; acquired anchor facts stay in canonical inputs."""
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
    if raw["producer"] != "anchor":
        fail(ErrorCode.UNSUPPORTED_CAPABILITY, "only the anchor producer is implemented")
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
    if type(config.price_unit) is not PriceUnit:
        fail(ErrorCode.INVALID_UNIT, "anchor prices require an explicit PriceUnit")
    replace(config.price_unit)
    for text in (config.session.namespace, config.session.session_id,
                 config.session.timezone_label, config.price_unit.currency,
                 config.adjustment.basis, config.adjustment.policy_version,
                 config.adjustment.action_snapshot, config.adjustment.anchor):
        label(text)
    for interval in config.session.intervals:
        label(interval.name)


def decode_ef1_context(config: ConfigSpec) -> Mapping[str, Any]:
    """Validate a canonical config and return a recursively immutable detached selection."""
    _components(config)
    if (config.identity, config.algorithm_version, config.schema_version) != ("ef1.anchor", "v1", "1"):
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported EF1 config identity/version")
    if len(config.parameters) != 1 or config.parameters[0].name != "ef1_context_json":
        fail(ErrorCode.INVALID_CONFIG, "one exact EF1 context parameter required")
    raw = _parse(config.parameters[0].value)
    if config.window != WindowSpec(1, config.session.session_id,
                                   (config.session.session_id,), "completed_eod"):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "anchor window must be target-only")
    if raw["selection"]["definition"]["start_ns"] >= config.availability.market_cutoff_ns:
        fail(ErrorCode.BOUNDS, "anchor must strictly precede cutoff")
    return cast(Mapping[str, Any], _freeze(raw))


def build_ef1_config(selection: dict[str, Any], *, session: SessionSpec,
                     window: WindowSpec, availability: AvailabilitySpec,
                     price_unit: PriceUnit, adjustment: AdjustmentSpec) -> ConfigSpec:
    """Build the exact reviewed config from the full context envelope, not source facts."""
    if type(selection) is not dict:
        fail(ErrorCode.INVALID_CONFIG, "concrete mathematical context dictionary required")
    _tree(selection)
    text = canonical_json(selection)
    config = ConfigSpec("ef1.anchor", "v1", (Parameter("ef1_context_json", text),),
                        session, window, availability, adjustment, price_unit)
    decode_ef1_context(config)
    return config


def anchor_proof_id(context: Mapping[str, Any]) -> str:
    """Return the exact hash identity expected from an actual anchor declaration."""
    definition = dict(context["selection"]["definition"])
    return "a1:" + hashlib.sha256(canonical_json(definition).encode("ascii")).hexdigest()
