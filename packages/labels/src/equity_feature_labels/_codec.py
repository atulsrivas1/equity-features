"""Closed canonical in-memory encoding; no decoder or external access."""
from __future__ import annotations
import hashlib
import json
import math
from typing import cast
from equity_feature_contracts import AvailabilitySpec, __version__ as CORE_VERSION
from . import _model as m

# The one contracts version this distribution is built against (pinned in pyproject.toml; tools/verify_versions.py checks both).
_CONTRACTS_VERSION = "0.0.4a5"

RECORDS: dict[type[object], tuple[str, tuple[str, ...]]] = {
    AvailabilitySpec: ('specs.AvailabilitySpec', ('market_cutoff_ns', 'knowledge_cutoff_ns', 'evaluation_ns', 'mode', 'reconstruction_reason')),
    m.Entity: ('Entity', ('namespace', 'instrument_id', 'session_id')),
    m.BasisWitness: ('BasisWitness', ('basis', 'policy_version', 'action_snapshot', 'anchor_id', 'source_revision', 'effective_ns', 'known_at_ns')),
    m.LabelOrigin: ('LabelOrigin', ('schema_version', 'entity', 'signal_request_digest', 'signal_result_digest', 'signal_availability', 'anchor_event_ns', 'anchor_price', 'anchor_known_at_ns', 'anchor_source_revision', 'anchor_basis')),
    m.PriceObservation: ('PriceObservation', ('event_ns', 'price', 'known_at_ns', 'source_revision', 'origin_anchor_digest', 'basis')),
    m.LabelConfig: ('LabelConfig', ('schema_version', 'algorithm_version', 'horizon_ns')),
    m.LabelRequest: ('LabelRequest', ('schema_version', 'origin', 'availability', 'observations', 'config')),
    m.LabelResult: ('LabelResult', ('schema_version', 'algorithm_version', 'entity', 'origin_digest', 'config_digest', 'request_digest', 'path_content_digest', 'availability', 'horizon_endpoint_ns', 'status', 'reasons', 'value', 'unit', 'label_known_at_ns', 'producer_version')),
}
DOMAINS: dict[str, type[object]] = {'label-origin:1': m.LabelOrigin, 'label-config:1': m.LabelConfig,
    'label-request:1': m.LabelRequest, 'label-result:1': m.LabelResult, 'label-price-path:1': tuple}


def _fields(value: object) -> dict[str, object]:
    fields = {name: getattr(value, name) for name in RECORDS[type(value)][1]}
    if type(value) is AvailabilitySpec:
        m.availability(value)
    return fields


def _encoded(value: object, active: set[int]) -> object:
    kind = type(value)
    if value is None or kind is bool:
        return value
    if kind is str:
        text = cast(str, value)
        m.require(not any(0xD800 <= ord(c) <= 0xDFFF for c in text))
        return text
    if kind is int:
        return {'int': str(value)}
    if kind is float:
        number = cast(float, value)
        m.require(math.isfinite(number))
        return {'float64': number.hex()}
    m.require(kind in (tuple, list) or kind in RECORDS)
    identity = id(value)
    m.require(identity not in active)
    active.add(identity)
    try:
        if kind in (tuple, list):
            return [_encoded(item, active) for item in cast(tuple[object, ...] | list[object], value)]
        return {'record': RECORDS[kind][0],
            'fields': {name: _encoded(field, active) for name, field in _fields(value).items()}}
    finally:
        active.remove(identity)


def encode(value: object) -> bytes:
    """Encode this distribution's closed records and primitives as canonical ASCII."""
    m.version(CORE_VERSION, _CONTRACTS_VERSION)
    return json.dumps(_encoded(value, set()), sort_keys=True, separators=(',', ':'),
        ensure_ascii=True, allow_nan=False).encode('ascii')


def digest(domain: str, value: object) -> str:
    """SHA256(domain + NUL + complete canonical content); no authenticity claim."""
    m.require(type(domain) is str)
    m.require(domain in DOMAINS, 'incompatible_version')
    if domain == 'label-price-path:1':
        value = m.path(value)
    else:
        m.require(type(value) is DOMAINS[domain])
    return hashlib.sha256(domain.encode('ascii') + b'\0' + encode(value)).hexdigest()


def origin_digest(origin: m.LabelOrigin) -> str:
    return digest('label-origin:1', origin)


def path_content_digest(observations: tuple[m.PriceObservation, ...] | list[m.PriceObservation]) -> str:
    return digest('label-price-path:1', observations)
