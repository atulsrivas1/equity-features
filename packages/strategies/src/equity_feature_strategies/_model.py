"""Closed immutable scanner values. No acquisition, computation adapters or publication."""
from __future__ import annotations

from dataclasses import dataclass
import math
import re
from typing import TypeVar, cast

from equity_feature_contracts import (AdjustmentSpec, AvailabilitySpec, DataKind, FeatureResult,
                                     InputScope, PriceUnit, ValueType)

VERSION = '0.1.0a1'
FEATURES = {
    'session.trade.count': (ValueType.INT64, 'trades'),
    'session.trade.volume': (ValueType.INT64, 'shares'),
    'session.price.open_close_return': (ValueType.FLOAT64, 'fraction'),
    'history.return': (ValueType.FLOAT64, 'fraction'),
    'baseline.relative_volume': (ValueType.FLOAT64, 'fraction'),
}
CODES = frozenset(('invalid_schema', 'invalid_config', 'incompatible_version', 'inconsistent_identity',
    'duplicate', 'invalid_unit', 'bounds', 'unsupported_feature', 'unsupported_adjustment',
    'numerical_bounds', 'precision_bounds'))
UNAVAILABLE = frozenset(('absent_feature', 'absent_entity', 'insufficient_history', 'missing_input',
                         'incomplete_coverage', 'not_applicable'))
T = TypeVar('T')


class StrategyError(ValueError):
    """Closed immutable code with a fixed message that never echoes supplied facts."""
    __slots__ = ('__code',)

    def __init__(self, code: str) -> None:
        if type(code) is not str or code not in CODES:
            code = 'invalid_schema'
        object.__setattr__(self, '_StrategyError__code', code)
        super().__init__('strategy ' + code)

    @property
    def code(self) -> str:
        return self.__code

    def __setattr__(self, name: str, value: object) -> None:
        if name in ('code', '_StrategyError__code') and hasattr(self, '_StrategyError__code'):
            raise AttributeError('immutable error code')
        super().__setattr__(name, value)

    def __delattr__(self, name: str) -> None:
        if name in ('code', '_StrategyError__code'):
            raise AttributeError('immutable error code')
        super().__delattr__(name)


def require(condition: bool, code: str = 'invalid_schema') -> None:
    if not condition:
        raise StrategyError(code)


def label(value: object) -> None:
    require(type(value) is str)
    text = cast(str, value)
    require(bool(text.strip()) and not any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in text))


def sha(value: object) -> None:
    require(type(value) is str and re.fullmatch('[0-9a-f]{64}', cast(str, value)) is not None)


def version(value: object, expected: str) -> None:
    require(type(value) is str)
    require(value == expected, 'incompatible_version')


def integer(value: object, minimum: int = 0) -> None:
    require(type(value) is int)
    require(minimum <= cast(int, value) <= 2**63 - 1, 'bounds')


def sequence(value: object, kind: type[T]) -> tuple[T, ...]:
    require(type(value) in (tuple, list))
    items = cast(tuple[object, ...] | list[object], value)
    require(all(type(item) is kind for item in items))
    return tuple(cast(T, item) for item in items)


def scalar(value: object) -> None:
    if type(value) is int:
        integer(value, -(2**63))
    else:
        require(type(value) is float and math.isfinite(cast(float, value)))


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
class FeatureRequirement:
    feature_id: str
    schema_version: str
    algorithm_version: str
    dtype: ValueType
    unit: str
    expected_result_config_digest: str
    expected_input_semantic_digest: str

    def __post_init__(self) -> None:
        require(type(self) is FeatureRequirement)
        label(self.feature_id)
        require(self.feature_id in FEATURES, 'unsupported_feature')
        version(self.schema_version, '1'); version(self.algorithm_version, 'v1')
        label(self.unit)
        require(type(self.dtype) is ValueType)
        require((self.dtype, self.unit) == FEATURES[self.feature_id], 'invalid_unit')
        sha(self.expected_result_config_digest); sha(self.expected_input_semantic_digest)


@dataclass(frozen=True)
class Predicate:
    requirement: FeatureRequirement
    operator: str
    threshold: int | float

    def __post_init__(self) -> None:
        require(type(self) is Predicate and type(self.requirement) is FeatureRequirement)
        require(type(self.operator) is str and self.operator in ('lt', 'le', 'eq', 'ge', 'gt'), 'invalid_config')
        if self.requirement.dtype is ValueType.INT64:
            integer(self.threshold, -(2**63))
        else:
            require(type(self.threshold) is float and math.isfinite(self.threshold), 'invalid_config')


@dataclass(frozen=True)
class Ranking:
    requirement: FeatureRequirement
    direction: str

    def __post_init__(self) -> None:
        require(type(self) is Ranking and type(self.requirement) is FeatureRequirement)
        require(type(self.direction) is str and self.direction in ('ascending', 'descending'), 'invalid_config')


@dataclass(frozen=True)
class StrategyConfig:
    predicates: tuple[Predicate, ...]
    ranking: Ranking
    top_k: int
    schema_version: str = 'strategy-config:1'
    algorithm_version: str = 'scanner-and-rank:v1'

    def __post_init__(self) -> None:
        require(type(self) is StrategyConfig and type(self.ranking) is Ranking)
        version(self.schema_version, 'strategy-config:1'); version(self.algorithm_version, 'scanner-and-rank:v1')
        object.__setattr__(self, 'predicates', sequence(self.predicates, Predicate))
        integer(self.top_k)
        seen: dict[str, FeatureRequirement] = {}
        for requirement in [p.requirement for p in self.predicates] + [self.ranking.requirement]:
            require(requirement.feature_id not in seen or seen[requirement.feature_id] == requirement, 'invalid_config')
            seen[requirement.feature_id] = requirement

    @property
    def identity_digest(self) -> str:
        from ._codec import digest
        return digest('strategy-config:1', self)


@dataclass(frozen=True)
class IntervalSemantic:
    name: str
    start_ns: int
    end_ns: int

    def __post_init__(self) -> None:
        require(type(self) is IntervalSemantic)
        label(self.name); integer(self.start_ns, -(2**63)); integer(self.end_ns, -(2**63))
        require(self.start_ns < self.end_ns, 'bounds')


@dataclass(frozen=True)
class InputSemantic:
    role: str
    kind: DataKind
    schema_version: str
    namespace: str
    source_id: str
    mapping_version: str
    price_unit: PriceUnit | None
    adjustment: AdjustmentSpec
    sampling: str
    quantity_unit: str
    ordering: str
    duplicate_policy: str
    scope: InputScope | None
    interval_bounds: tuple[IntervalSemantic, ...]

    def __post_init__(self) -> None:
        require(type(self) is InputSemantic and type(self.kind) is DataKind)
        for value in (self.role, self.namespace, self.source_id, self.mapping_version):
            label(value)
        version(self.schema_version, '1')
        require(self.price_unit is None or type(self.price_unit) is PriceUnit)
        require(type(self.adjustment) is AdjustmentSpec and (self.scope is None or type(self.scope) is InputScope))
        require(type(self.sampling) is str and self.sampling in ('none', 'trade_snapshot', 'continuous'))
        require(type(self.quantity_unit) is str and self.quantity_unit == 'shares', 'invalid_unit')
        require(type(self.ordering) is str and self.ordering in ('declared', 'unsorted'))
        require(type(self.duplicate_policy) is str and self.duplicate_policy in ('reject', 'preserve'))
        intervals = sequence(self.interval_bounds, IntervalSemantic)
        require(len({v.name for v in intervals}) == len(intervals), 'duplicate')
        object.__setattr__(self, 'interval_bounds', tuple(sorted(intervals, key=lambda v: v.name)))


@dataclass(frozen=True)
class StrategyRequest:
    namespace: str
    session_id: str
    availability: AvailabilitySpec
    universe: tuple[Entity, ...]
    feature_results: tuple[FeatureResult, ...]
    config: StrategyConfig
    schema_version: str = 'strategy-request:1'

    def __post_init__(self) -> None:
        from ._codec import feature_result_digest
        from ._engine import admit
        require(type(self) is StrategyRequest and type(self.config) is StrategyConfig)
        label(self.namespace); label(self.session_id)
        version(self.schema_version, 'strategy-request:1')
        require(type(self.availability) is AvailabilitySpec)
        require(self.availability.mode == 'known_at', 'invalid_config')
        universe = sequence(self.universe, Entity)
        require(len(set(universe)) == len(universe), 'duplicate')
        object.__setattr__(self, 'universe', tuple(sorted(universe)))
        results = sequence(self.feature_results, FeatureResult)
        object.__setattr__(self, 'feature_results', tuple(sorted(results, key=feature_result_digest)))
        admit(self)

    @property
    def identity_digest(self) -> str:
        from ._codec import digest
        return digest('strategy-request:1', self)


@dataclass(frozen=True)
class PredicateDisposition:
    predicate_index: int
    feature_id: str
    state: str
    reason: str | None

    def __post_init__(self) -> None:
        require(type(self) is PredicateDisposition)
        integer(self.predicate_index)
        require(type(self.feature_id) is str and self.feature_id in FEATURES, 'unsupported_feature')
        require(type(self.state) is str and self.state in ('pass', 'fail', 'unavailable'))
        require((self.reason is None and self.state != 'unavailable') or
                (type(self.reason) is str and self.reason in UNAVAILABLE and self.state == 'unavailable'))


@dataclass(frozen=True)
class StrategyRow:
    entity: Entity
    status: str
    predicate_dispositions: tuple[PredicateDisposition, ...]
    ranking_value: int | float | None
    ranking_reason: str | None
    rank: int | None

    def __post_init__(self) -> None:
        require(type(self) is StrategyRow and type(self.entity) is Entity)
        dispositions = sequence(self.predicate_dispositions, PredicateDisposition)
        require(tuple(d.predicate_index for d in dispositions) == tuple(range(len(dispositions))))
        object.__setattr__(self, 'predicate_dispositions', dispositions)
        if self.ranking_value is None:
            require(type(self.ranking_reason) is str and self.ranking_reason in UNAVAILABLE)
        else:
            scalar(self.ranking_value); require(self.ranking_reason is None)
        unavailable = self.ranking_value is None or any(d.state == 'unavailable' for d in dispositions)
        expected = 'unavailable' if unavailable else 'nonmatching' if any(d.state == 'fail' for d in dispositions) else 'matching'
        require(type(self.status) is str and self.status == expected)
        if self.status == 'matching':
            integer(self.rank, 1)
        else:
            require(self.rank is None)


@dataclass(frozen=True)
class StrategyResult:
    config_digest: str
    request_digest: str
    input_content_digests: tuple[str, ...]
    rows: tuple[StrategyRow, ...]
    ranked: tuple[Entity, ...]
    selected: tuple[Entity, ...]
    expected: int
    eligible: int
    matching: int
    coverage_numerator: int
    coverage_denominator: int
    readiness: str
    schema_version: str = 'strategy-result:1'
    algorithm_version: str = 'scanner-and-rank:v1'
    producer_version: str = VERSION

    def __post_init__(self) -> None:
        require(type(self) is StrategyResult)
        version(self.schema_version, 'strategy-result:1'); version(self.algorithm_version, 'scanner-and-rank:v1')
        version(self.producer_version, VERSION); sha(self.config_digest); sha(self.request_digest)
        digests = sequence(self.input_content_digests, str)
        for value in digests:
            sha(value)
        object.__setattr__(self, 'input_content_digests', tuple(sorted(digests)))
        rows = tuple(sorted(sequence(self.rows, StrategyRow), key=lambda r: r.entity))
        require(len({r.entity for r in rows}) == len(rows), 'duplicate')
        object.__setattr__(self, 'rows', rows)
        for name in ('ranked', 'selected'):
            object.__setattr__(self, name, sequence(getattr(self, name), Entity))
        for count in (self.expected, self.eligible, self.matching, self.coverage_numerator, self.coverage_denominator):
            integer(count)
        matches = sorted((r for r in rows if r.status == 'matching'), key=lambda r: cast(int, r.rank))
        require([r.rank for r in matches] == list(range(1, len(matches) + 1)))
        require(self.ranked == tuple(r.entity for r in matches))
        require(self.selected == self.ranked[:len(self.selected)] and len(self.selected) <= len(self.ranked))
        require(self.expected == len(rows) and self.eligible == sum(r.status != 'unavailable' for r in rows))
        require(self.matching == len(matches) and self.coverage_numerator == self.eligible and self.coverage_denominator == self.expected)
        expected = 'empty_universe' if not rows else 'complete' if self.eligible == self.expected else 'incomplete'
        require(type(self.readiness) is str and self.readiness == expected)

    @property
    def identity_digest(self) -> str:
        from ._codec import digest
        return digest('strategy-result:1', self)
