"""Immutable supplied facts for elapsed forward price returns."""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import TypeVar, cast
from equity_feature_contracts import AvailabilitySpec

VERSION = '0.1.0a1'
CODES = frozenset(('invalid_schema', 'invalid_config', 'incompatible_version', 'inconsistent_identity',
    'duplicate', 'invalid_unit', 'bounds', 'unsupported_feature', 'unsupported_adjustment',
    'numerical_bounds', 'precision_bounds'))
T = TypeVar('T')


class LabelError(ValueError):
    """Closed immutable code; messages never echo supplied values."""
    __slots__ = ('__code',)
    __code: str

    def __init__(self, code: str) -> None:
        if type(code) is not str or code not in CODES:
            code = 'invalid_schema'
        object.__setattr__(self, '_LabelError__code', code)
        super().__init__('label ' + code)

    @property
    def code(self) -> str:
        return self.__code

    def __setattr__(self, name: str, value: object) -> None:
        if name in ('code', '_LabelError__code') and hasattr(self, '_LabelError__code'):
            raise AttributeError('immutable error code')
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if name in ('code', '_LabelError__code'):
            raise AttributeError('immutable error code')
        super().__delattr__(name)


def require(condition: bool, code: str = 'invalid_schema') -> None:
    if not condition:
        raise LabelError(code)


def label(value: object) -> None:
    require(type(value) is str)
    text = cast(str, value)
    require(bool(text.strip()) and not any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in text))


def sha(value: object) -> None:
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', value) is not None)


def integer(value: object, minimum: int = -(2**63)) -> None:
    require(type(value) is int)
    require(minimum <= cast(int, value) <= 2**63 - 1, 'bounds')


def version(value: object, expected: str) -> None:
    require(type(value) is str)
    require(value == expected, 'incompatible_version')


def sequence(value: object, kind: type[T]) -> tuple[T, ...]:
    require(type(value) in (tuple, list))
    items = cast(tuple[object, ...] | list[object], value)
    require(all(type(item) is kind for item in items))
    return tuple(cast(T, item) for item in items)


def price(value: object) -> None:
    require(type(value) is float)
    require(math.isfinite(cast(float, value)) and cast(float, value) > 0.0, 'bounds')


def availability(value: AvailabilitySpec) -> None:
    require(type(value) is AvailabilitySpec)
    require(type(value.mode) is str)
    require(value.mode == 'known_at' and value.reconstruction_reason is None, 'inconsistent_identity')
    for stamp in (value.market_cutoff_ns, value.knowledge_cutoff_ns, value.evaluation_ns):
        integer(stamp)
    require(max(value.market_cutoff_ns, value.knowledge_cutoff_ns) <= value.evaluation_ns, 'inconsistent_identity')


@dataclass(frozen=True, order=True)
class Entity:
    namespace: str
    instrument_id: str
    session_id: str

    def __post_init__(self) -> None:
        require(type(self) is Entity)
        for value in (self.namespace, self.instrument_id, self.session_id):
            label(value)


@dataclass(frozen=True)
class BasisWitness:
    basis: str
    policy_version: str
    action_snapshot: str
    anchor_id: str
    source_revision: str
    effective_ns: int
    known_at_ns: int | None

    def __post_init__(self) -> None:
        require(type(self) is BasisWitness and type(self.basis) is str)
        require(self.basis in ('raw', 'split'), 'unsupported_adjustment')
        for value in (self.policy_version, self.action_snapshot, self.anchor_id, self.source_revision):
            label(value)
        if self.basis == 'raw':
            require((self.policy_version, self.action_snapshot, self.anchor_id) == ('raw-v1', 'none', 'none'), 'inconsistent_identity')
        else:
            require(all(v != 'none' for v in (self.policy_version, self.action_snapshot, self.anchor_id, self.source_revision)), 'inconsistent_identity')
        integer(self.effective_ns)
        if self.known_at_ns is not None:
            integer(self.known_at_ns)


@dataclass(frozen=True)
class LabelOrigin:
    entity: Entity
    signal_request_digest: str
    signal_result_digest: str
    signal_availability: AvailabilitySpec
    anchor_event_ns: int
    anchor_price: float
    anchor_known_at_ns: int
    anchor_source_revision: str
    anchor_basis: BasisWitness
    schema_version: str = 'label-origin:1'

    def __post_init__(self) -> None:
        require(type(self) is LabelOrigin and type(self.entity) is Entity and type(self.anchor_basis) is BasisWitness)
        version(self.schema_version, 'label-origin:1')
        sha(self.signal_request_digest); sha(self.signal_result_digest)
        availability(self.signal_availability)
        integer(self.anchor_event_ns); price(self.anchor_price)
        require(self.anchor_known_at_ns is not None, 'inconsistent_identity')
        integer(self.anchor_known_at_ns); label(self.anchor_source_revision)
        require(self.anchor_event_ns <= self.signal_availability.market_cutoff_ns and
            self.anchor_known_at_ns <= self.signal_availability.knowledge_cutoff_ns and
            self.anchor_basis.known_at_ns is not None and
            self.anchor_basis.known_at_ns <= self.signal_availability.knowledge_cutoff_ns and
            self.anchor_basis.effective_ns <= self.anchor_event_ns, 'inconsistent_identity')

    @property
    def identity_digest(self) -> str:
        from ._codec import digest
        return digest('label-origin:1', self)


@dataclass(frozen=True)
class PriceObservation:
    event_ns: int
    price: float
    known_at_ns: int | None
    source_revision: str
    origin_anchor_digest: str
    basis: BasisWitness

    def __post_init__(self) -> None:
        require(type(self) is PriceObservation and type(self.basis) is BasisWitness)
        integer(self.event_ns); price(self.price)
        if self.known_at_ns is not None:
            integer(self.known_at_ns)
        label(self.source_revision); sha(self.origin_anchor_digest)


@dataclass(frozen=True)
class LabelConfig:
    horizon_ns: int
    schema_version: str = 'label-config:1'
    algorithm_version: str = 'forward-price-return:v1'

    def __post_init__(self) -> None:
        require(type(self) is LabelConfig)
        version(self.schema_version, 'label-config:1'); version(self.algorithm_version, 'forward-price-return:v1')
        integer(self.horizon_ns, 1)

    @property
    def identity_digest(self) -> str:
        from ._codec import digest
        return digest('label-config:1', self)


def path(value: object) -> tuple[PriceObservation, ...]:
    rows = sequence(value, PriceObservation)
    require(len({r.event_ns for r in rows}) == len(rows), 'duplicate')
    if rows:
        require(all(r.basis == rows[0].basis and r.source_revision == rows[0].source_revision and
            r.origin_anchor_digest == rows[0].origin_anchor_digest for r in rows), 'inconsistent_identity')
    return tuple(sorted(rows, key=lambda row: row.event_ns))


@dataclass(frozen=True)
class LabelRequest:
    origin: LabelOrigin
    availability: AvailabilitySpec
    observations: tuple[PriceObservation, ...]
    config: LabelConfig
    schema_version: str = 'label-request:1'

    def __post_init__(self) -> None:
        require(type(self) is LabelRequest and type(self.origin) is LabelOrigin and type(self.config) is LabelConfig)
        version(self.schema_version, 'label-request:1'); availability(self.availability)
        signal = self.origin.signal_availability
        require(self.availability.market_cutoff_ns >= signal.market_cutoff_ns and
            self.availability.knowledge_cutoff_ns >= signal.knowledge_cutoff_ns and
            self.availability.evaluation_ns >= signal.evaluation_ns, 'inconsistent_identity')
        integer(self.origin.anchor_event_ns + self.config.horizon_ns)
        rows = path(self.observations)
        require(all(r.origin_anchor_digest == self.origin.identity_digest for r in rows), 'inconsistent_identity')
        object.__setattr__(self, 'observations', rows)

    @property
    def identity_digest(self) -> str:
        from ._codec import digest
        return digest('label-request:1', self)


@dataclass(frozen=True)
class LabelResult:
    entity: Entity
    origin_digest: str
    config_digest: str
    request_digest: str
    path_content_digest: str
    availability: AvailabilitySpec
    horizon_endpoint_ns: int
    status: str
    reasons: tuple[str, ...]
    value: float | None
    label_known_at_ns: int | None
    schema_version: str = 'label-result:1'
    algorithm_version: str = 'forward-price-return:v1'
    unit: str = 'fraction'
    producer_version: str = VERSION

    def __post_init__(self) -> None:
        require(type(self) is LabelResult and type(self.entity) is Entity)
        version(self.schema_version, 'label-result:1'); version(self.algorithm_version, 'forward-price-return:v1')
        version(self.producer_version, VERSION)
        require(type(self.unit) is str and self.unit == 'fraction', 'invalid_unit')
        for value in (self.origin_digest, self.config_digest, self.request_digest, self.path_content_digest):
            sha(value)
        availability(self.availability); integer(self.horizon_endpoint_ns)
        require(type(self.status) is str and self.status in ('pending', 'incomplete', 'mature'))
        reasons = sequence(self.reasons, str)
        object.__setattr__(self, 'reasons', reasons)
        if self.status == 'mature':
            require(not reasons and type(self.value) is float and math.isfinite(self.value))
            integer(self.label_known_at_ns)
            require(cast(int, self.label_known_at_ns) <= self.availability.knowledge_cutoff_ns and
                self.horizon_endpoint_ns <= self.availability.market_cutoff_ns, 'inconsistent_identity')
        else:
            require(self.value is None and self.label_known_at_ns is None)
            allowed = (('missing_anchor_endpoint',), ('missing_horizon_endpoint',),
                ('missing_anchor_endpoint', 'missing_horizon_endpoint')) if self.status == 'incomplete' else (
                ('horizon_not_elapsed',), ('unknown_availability',), ('future_knowledge',),
                ('unknown_availability', 'future_knowledge'), ('basis_not_effective',))
            require(reasons in allowed)
            require((reasons == ('horizon_not_elapsed',)) == (self.horizon_endpoint_ns > self.availability.market_cutoff_ns), 'inconsistent_identity')

    @property
    def identity_digest(self) -> str:
        from ._codec import digest
        return digest('label-result:1', self)
