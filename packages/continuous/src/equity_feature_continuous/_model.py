"""Own immutable supplied snapshots; no calendar, acquisition or calculation dispatch."""
from __future__ import annotations
from dataclasses import dataclass
import hashlib
import json
from typing import NoReturn, TypeVar, cast
from equity_feature_contracts import (
    AdjustmentSpec, AvailabilitySpec, ContractError, Coverage, ErrorCode,
    IntervalSpec, PriceUnit, SourceBinding,
)
from ._rational import Rational, validate_rational

I64_MIN = -(2**63)
I64_MAX = 2**63 - 1
ROLES = ('continuous_coverage', 'reference_coverage', 'continuous', 'reference',
         'continuous_feed', 'reference_feed', 'conversion')
REASONS = ('incomplete_coverage', 'unknown_availability', 'future_knowledge',
           'absent_observation', 'null_price', 'stale_observation', 'mismatch',
           'absent_fact', 'unknown', 'stale', 'outage', 'not_live',
           'not_scheduled_freeze', 'observed_empty')
METRICS = {
    'basis': ('cross_venue.basis', 'cross_venue.premium'),
    'freeze': ('cross_venue.freeze_max_abs', 'cross_venue.freeze_mean_abs'),
    'reopen': ('cross_venue.reopen_gap', 'cross_venue.reopen_premium'),
}
BYTE_LIMITS = {'continuous_config': 65536, 'continuous_input': 16777216,
               'continuous_result': 1048576}
T = TypeVar('T')


def _fail(code: ErrorCode, message: str) -> NoReturn:
    raise ContractError(code, message) from None


def _label(value: object) -> None:
    if type(value) is not str or not value or value != value.strip():
        _fail(ErrorCode.INVALID_SCHEMA, 'nonempty continuous identity required')
    text = value
    try:
        size = len(text.encode('utf-8'))
    except UnicodeEncodeError:
        _fail(ErrorCode.INVALID_SCHEMA, 'valid UTF8 continuous identity required')
        return
    if size > 128:
        _fail(ErrorCode.BOUNDS, 'continuous identity exceeds declared bytes')


def _ns(value: object) -> None:
    if type(value) is not int:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact integer UTCns required')
    if not I64_MIN <= value <= I64_MAX:
        _fail(ErrorCode.BOUNDS, 'UTCns exceeds int64')


def _sequence(value: object, cls: type[T], limit: int) -> tuple[T, ...]:
    if type(value) not in (list, tuple):
        _fail(ErrorCode.INVALID_SCHEMA, 'bounded concrete collection required')
    values = cast('list[object] | tuple[object, ...]', value)
    if len(values) > limit:
        _fail(ErrorCode.BOUNDS, 'continuous collection exceeds declared count')
    if any(type(item) is not cls for item in values):
        _fail(ErrorCode.INVALID_SCHEMA, 'exact typed collection members required')
    return tuple(cast(T, item) for item in values)


def _interval(value: object) -> None:
    if type(value) is not IntervalSpec:
        _fail(ErrorCode.INVALID_SCHEMA, 'typed finite interval required')
    span = value
    _label(span.name); _ns(span.start_ns); _ns(span.end_ns)
    if span.start_ns >= span.end_ns:
        _fail(ErrorCode.BOUNDS, 'positive half-open interval required')


def _digest_label(value: object) -> None:
    if type(value) is not str or len(value) != 64 or any(c not in '0123456789abcdef' for c in value):
        _fail(ErrorCode.INVALID_SCHEMA, 'exact lowercase SHA256 identity required')


@dataclass(frozen=True, slots=True)
class PriceObservation:
    observation_id: str
    event_ns: int
    order_key: int
    price: int | None
    known_at_ns: int | None

    def __post_init__(self) -> None:
        _observation(self)


def _observation(value: PriceObservation) -> None:
    if type(value) is not PriceObservation:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact observation required')
    _label(value.observation_id); _ns(value.event_ns)
    if type(value.order_key) is not int:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact observation order required')
    if not 0 <= value.order_key <= I64_MAX:
        _fail(ErrorCode.BOUNDS, 'observation order exceeds declared bounds')
    if value.price is not None:
        if type(value.price) is not int:
            _fail(ErrorCode.INVALID_SCHEMA, 'exact scaled price required')
        if not 0 < value.price <= I64_MAX:
            _fail(ErrorCode.BOUNDS, 'positive int64 scaled price required')
    if value.known_at_ns is not None:
        _ns(value.known_at_ns)
        if value.known_at_ns < value.event_ns:
            _fail(ErrorCode.INVALID_SCHEMA, 'observation knowledge precedes event')


@dataclass(frozen=True, slots=True, init=False)
class Leg:
    instrument_id: str
    feed_id: str
    product_id: str
    underlying_id: str
    quantity_unit: str
    price_kind: str
    source: SourceBinding
    price_unit: PriceUnit
    adjustment: AdjustmentSpec
    scope: IntervalSpec
    coverage: Coverage
    coverage_known_at_ns: int | None
    observations: tuple[PriceObservation, ...]

    def __init__(self, instrument_id: str, feed_id: str, product_id: str,
                 underlying_id: str, quantity_unit: str, price_kind: str,
                 source: SourceBinding, price_unit: PriceUnit, adjustment: AdjustmentSpec,
                 scope: IntervalSpec, coverage: Coverage, coverage_known_at_ns: int | None,
                 observations: tuple[PriceObservation, ...] | list[PriceObservation]) -> None:
        object.__setattr__(self, 'instrument_id', instrument_id)
        object.__setattr__(self, 'feed_id', feed_id)
        object.__setattr__(self, 'product_id', product_id)
        object.__setattr__(self, 'underlying_id', underlying_id)
        object.__setattr__(self, 'quantity_unit', quantity_unit)
        object.__setattr__(self, 'price_kind', price_kind)
        object.__setattr__(self, 'source', source)
        object.__setattr__(self, 'price_unit', price_unit)
        object.__setattr__(self, 'adjustment', adjustment)
        object.__setattr__(self, 'scope', scope)
        object.__setattr__(self, 'coverage', coverage)
        object.__setattr__(self, 'coverage_known_at_ns', coverage_known_at_ns)
        object.__setattr__(self, 'observations', _sequence(observations, PriceObservation, 4096))
        _leg(self)


def _leg(value: Leg) -> None:
    if type(value) is not Leg:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact typed leg required')
    for label in (value.instrument_id, value.feed_id, value.product_id, value.underlying_id, value.quantity_unit):
        _label(label)
    if type(value.price_kind) is not str:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact price-kind string required')
    if value.price_kind != 'last_trade':
        _fail(ErrorCode.UNSUPPORTED_CAPABILITY, 'only supplied last trades supported')
    if type(value.source) is not SourceBinding:
        _fail(ErrorCode.INVALID_SCHEMA, 'public source binding required')
    for label in (value.source.source_id, value.source.snapshot_id, value.source.mapping_version, value.source.input_id):
        _label(label)
    if type(value.price_unit) is not PriceUnit:
        _fail(ErrorCode.INVALID_SCHEMA, 'public price unit required')
    if type(value.price_unit.scale) is not int or not 0 <= value.price_unit.scale <= 18:
        _fail(ErrorCode.INVALID_UNIT, 'explicit supported price scale required')
    _label(value.price_unit.currency)
    if type(value.adjustment) is not AdjustmentSpec:
        _fail(ErrorCode.INVALID_SCHEMA, 'public adjustment required')
    for label in (value.adjustment.basis, value.adjustment.policy_version,
                  value.adjustment.action_snapshot, value.adjustment.anchor):
        _label(label)
    if (value.adjustment.basis, value.adjustment.policy_version, value.adjustment.action_snapshot, value.adjustment.anchor) != ('raw', 'raw-v1', 'none', 'none'):
        _fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, 'initial continuous profile requires default raw adjustment')
    _interval(value.scope)
    if type(value.coverage) is not Coverage:
        _fail(ErrorCode.INVALID_SCHEMA, 'public coverage required')
    c = value.coverage
    if type(c.complete) is not bool or type(c.observed) is not int or not 0 <= c.observed <= I64_MAX:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact coverage assertion required')
    if c.expected is not None and (type(c.expected) is not int or not c.observed <= c.expected <= I64_MAX):
        _fail(ErrorCode.INVALID_SCHEMA, 'valid coverage population required')
    rows = _sequence(value.observations, PriceObservation, 4096)
    if c.observed != len(rows) or (c.complete and c.expected != c.observed):
        _fail(ErrorCode.INVALID_SCHEMA, 'coverage must bind every delivered observation')
    if value.coverage_known_at_ns is not None:
        _ns(value.coverage_known_at_ns)
        if value.coverage_known_at_ns < value.scope.end_ns:
            _fail(ErrorCode.INVALID_SCHEMA, 'coverage knowledge precedes delivered scope end')
    previous: tuple[int, int, bytes] | None = None
    ids: set[str] = set()
    for row in rows:
        _observation(row)
        if not value.scope.start_ns <= row.event_ns < value.scope.end_ns:
            _fail(ErrorCode.BOUNDS, 'observation outside delivered scope')
        if row.observation_id in ids:
            _fail(ErrorCode.DUPLICATE, 'duplicate observation identity')
        ids.add(row.observation_id)
        key = (row.event_ns, row.order_key, row.observation_id.encode('utf-8'))
        if previous is not None and key <= previous:
            _fail(ErrorCode.INVALID_ORDER, 'observation order must be canonical')
        previous = key


@dataclass(frozen=True, slots=True)
class FeedFact:
    fact_id: str
    revision: str
    feed_id: str
    product_id: str
    interval: IntervalSpec
    state: str
    known_at_ns: int | None

    def __post_init__(self) -> None:
        _feed(self)


def _feed(value: FeedFact) -> None:
    if type(value) is not FeedFact:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact feed fact required')
    for label in (value.fact_id, value.revision, value.feed_id, value.product_id):
        _label(label)
    _interval(value.interval)
    if type(value.state) is not str or value.state not in ('live', 'scheduled_freeze', 'outage', 'stale', 'unknown'):
        _fail(ErrorCode.INVALID_SCHEMA, 'closed supplied feed state required')
    if value.known_at_ns is not None:
        _ns(value.known_at_ns)


@dataclass(frozen=True, slots=True)
class ConversionFact:
    fact_id: str
    revision: str
    continuous_instrument_id: str
    reference_instrument_id: str
    underlying_id: str
    continuous_quantity_unit: str
    reference_quantity_unit: str
    currency: str
    interval: IntervalSpec
    reference_units_numerator: int
    continuous_units_denominator: int
    known_at_ns: int | None

    def __post_init__(self) -> None:
        _conversion(self)


def _conversion(value: ConversionFact) -> None:
    if type(value) is not ConversionFact:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact conversion fact required')
    for label in (value.fact_id, value.revision, value.continuous_instrument_id,
                  value.reference_instrument_id, value.underlying_id,
                  value.continuous_quantity_unit, value.reference_quantity_unit, value.currency):
        _label(label)
    _interval(value.interval)
    for ratio in (value.reference_units_numerator, value.continuous_units_denominator):
        if type(ratio) is not int:
            _fail(ErrorCode.INVALID_SCHEMA, 'exact conversion integers required')
        if not 0 < ratio <= I64_MAX:
            _fail(ErrorCode.BOUNDS, 'positive int64 conversion required')
    if value.known_at_ns is not None:
        _ns(value.known_at_ns)


@dataclass(frozen=True, slots=True)
class ContinuousConfig:
    identity: str
    schema_version: str
    algorithm_version: str
    operation: str
    window: IntervalSpec
    availability: AvailabilitySpec
    anchor_ns: int | None
    reopen_ns: int | None
    max_continuous_age_ns: int
    max_reference_age_ns: int
    max_mismatch_ns: int
    top_k: int
    weighting: str
    reference_mode: str

    def __post_init__(self) -> None:
        _config(self)

    @property
    def identity_digest(self) -> str:
        return hashlib.sha256(encode_payload('continuous_config', config_payload(self))).hexdigest()


def _config(value: ContinuousConfig) -> None:
    if type(value) is not ContinuousConfig:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact continuous config required')
    _label(value.identity)
    if type(value.schema_version) is not str or type(value.algorithm_version) is not str:
        _fail(ErrorCode.INVALID_SCHEMA, 'explicit schema and algorithm versions required')
    if value.schema_version != '1' or value.algorithm_version != '1':
        _fail(ErrorCode.INCOMPATIBLE_VERSION, 'unsupported continuous version')
    if type(value.operation) is not str:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact operation string required')
    if value.operation not in METRICS:
        _fail(ErrorCode.UNSUPPORTED_CAPABILITY, 'unsupported continuous operation')
    _interval(value.window)
    if type(value.availability) is not AvailabilitySpec:
        _fail(ErrorCode.INVALID_SCHEMA, 'public availability required')
    a = value.availability
    for time in (a.market_cutoff_ns, a.knowledge_cutoff_ns, a.evaluation_ns):
        _ns(time)
    if type(a.mode) is not str or a.mode != 'known_at':
        _fail(ErrorCode.UNSUPPORTED_CAPABILITY, 'continuous reconstruction is unsupported')
    if a.reconstruction_reason is not None or max(a.market_cutoff_ns, a.knowledge_cutoff_ns) > a.evaluation_ns or value.window.end_ns > min(a.market_cutoff_ns, a.knowledge_cutoff_ns):
        _fail(ErrorCode.INVALID_CONFIG, 'completed causal analysis required')
    for age in (value.max_continuous_age_ns, value.max_reference_age_ns, value.max_mismatch_ns):
        if type(age) is not int or not 0 <= age <= I64_MAX:
            _fail(ErrorCode.INVALID_CONFIG, 'bounded exact age limits required')
    if type(value.top_k) is not int or not 1 <= value.top_k <= 32:
        _fail(ErrorCode.INVALID_CONFIG, 'topK must be within declared bounds')
    if type(value.weighting) is not str or type(value.reference_mode) is not str:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact weighting and reference strings required')
    if value.weighting != 'observation_count' or value.reference_mode != 'supplied_last_trade':
        _fail(ErrorCode.UNSUPPORTED_CAPABILITY, 'unsupported weighting or reference mode')
    if value.operation == 'basis':
        anchor = value.anchor_ns
        if type(anchor) is not int or not value.window.start_ns <= anchor < value.window.end_ns or anchor >= a.market_cutoff_ns or value.reopen_ns is not None:
            _fail(ErrorCode.INVALID_CONFIG, 'basis requires only an interior causal anchor')
    elif value.operation == 'freeze':
        if value.anchor_ns is not None or value.reopen_ns is not None:
            _fail(ErrorCode.INVALID_CONFIG, 'freeze has no anchor or reopen argument')
    elif type(value.reopen_ns) is not int or not value.window.start_ns < value.reopen_ns < value.window.end_ns or value.anchor_ns is not None:
        _fail(ErrorCode.INVALID_CONFIG, 'reopen requires only an interior boundary')


@dataclass(frozen=True, slots=True, init=False)
class ContinuousInput:
    config: ContinuousConfig
    continuous: Leg
    reference: Leg
    feed_facts: tuple[FeedFact, ...]
    conversion_facts: tuple[ConversionFact, ...]

    def __init__(self, config: ContinuousConfig, continuous: Leg, reference: Leg,
                 feed_facts: tuple[FeedFact, ...] | list[FeedFact],
                 conversion_facts: tuple[ConversionFact, ...] | list[ConversionFact]) -> None:
        # Preserve normative validation order before touching later collections.
        _config(config); _leg(continuous); _leg(reference)
        _pair(config, continuous, reference)
        object.__setattr__(self, 'config', config)
        object.__setattr__(self, 'continuous', continuous)
        object.__setattr__(self, 'reference', reference)
        object.__setattr__(self, 'feed_facts', _feeds(feed_facts))
        object.__setattr__(self, 'conversion_facts', _conversions(conversion_facts, continuous, reference))
        _input(self)

    @property
    def identity_digest(self) -> str:
        return hashlib.sha256(encode_payload('continuous_input', input_payload(self))).hexdigest()


def _nonoverlap(groups: dict[tuple[str, ...], list[IntervalSpec]]) -> None:
    for intervals in groups.values():
        ordered = sorted(intervals, key=lambda p: (p.start_ns, p.end_ns))
        if any(left.end_ns > right.start_ns for left, right in zip(ordered, ordered[1:])):
            _fail(ErrorCode.INVALID_SCHEMA, 'same-domain supplied facts overlap')


def _pair(cfg: ContinuousConfig, c: Leg, r: Leg) -> None:
    if c.price_unit.currency != r.price_unit.currency:
        _fail(ErrorCode.INVALID_UNIT, 'cross-currency comparison unsupported')
    if c.underlying_id != r.underlying_id:
        _fail(ErrorCode.INCONSISTENT_IDENTITY, 'declared underlying identities differ')
    if max(c.scope.end_ns, r.scope.end_ns) > cfg.availability.market_cutoff_ns:
        _fail(ErrorCode.BOUNDS, 'delivered scope exceeds market cutoff')
    if cfg.operation == 'basis':
        anchor = cast(int, cfg.anchor_ns)
        if not c.scope.start_ns <= anchor < c.scope.end_ns or not r.scope.start_ns <= anchor < r.scope.end_ns:
            _fail(ErrorCode.BOUNDS, 'basis scopes must cover the anchor lookup')
    elif cfg.operation == 'freeze':
        if (c.scope.start_ns, c.scope.end_ns) != (cfg.window.start_ns, cfg.window.end_ns) or r.scope.end_ns != cfg.window.start_ns:
            _fail(ErrorCode.BOUNDS, 'freeze requires exact population and pre-window reference scope')
    elif (c.scope.start_ns, c.scope.end_ns) != (cfg.window.start_ns, cfg.reopen_ns) or r.scope.start_ns > cast(int, cfg.reopen_ns) or r.scope.end_ns != cfg.window.end_ns:
        _fail(ErrorCode.BOUNDS, 'reopen requires complete pre-boundary and analysis-ending scopes')


def _feeds(value: object) -> tuple[FeedFact, ...]:
    facts = _sequence(value, FeedFact, 256)
    ids: set[str] = set()
    groups: dict[tuple[str, ...], list[IntervalSpec]] = {}
    for fact in facts:
        _feed(fact)
        if fact.fact_id in ids:
            _fail(ErrorCode.DUPLICATE, 'duplicate feed fact identity')
        ids.add(fact.fact_id)
        groups.setdefault((fact.feed_id, fact.product_id), []).append(fact.interval)
    _nonoverlap(groups)
    return facts


def _conversions(value: object, c: Leg, r: Leg) -> tuple[ConversionFact, ...]:
    facts = _sequence(value, ConversionFact, 256)
    ids: set[str] = set()
    groups: dict[tuple[str, ...], list[IntervalSpec]] = {}
    for mapping in facts:
        _conversion(mapping)
        if mapping.fact_id in ids:
            _fail(ErrorCode.DUPLICATE, 'duplicate conversion fact identity')
        ids.add(mapping.fact_id)
        if (mapping.continuous_instrument_id, mapping.reference_instrument_id) == (c.instrument_id, r.instrument_id):
            if mapping.currency != c.price_unit.currency:
                _fail(ErrorCode.INVALID_UNIT, 'conversion currency differs')
            if (mapping.underlying_id, mapping.continuous_quantity_unit, mapping.reference_quantity_unit) != (c.underlying_id, c.quantity_unit, r.quantity_unit):
                _fail(ErrorCode.INCONSISTENT_IDENTITY, 'conversion identities or quantity units differ')
        domain = (mapping.continuous_instrument_id, mapping.reference_instrument_id,
                  mapping.underlying_id, mapping.continuous_quantity_unit,
                  mapping.reference_quantity_unit, mapping.currency)
        groups.setdefault(domain, []).append(mapping.interval)
    _nonoverlap(groups)
    return facts


def _input(value: ContinuousInput) -> None:
    if type(value) is not ContinuousInput:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact continuous snapshot required')
    _config(value.config); _leg(value.continuous); _leg(value.reference)
    _pair(value.config, value.continuous, value.reference)
    _feeds(value.feed_facts)
    _conversions(value.conversion_facts, value.continuous, value.reference)


def _proof(value: str) -> None:
    if type(value) is not str:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact input proof pointer required')
    parts = value.split('/')
    if len(parts) == 3 and parts[0] == '' and parts[1] in ('continuous', 'reference') and parts[2] in ('scope', 'coverage', 'coverage_known_at_ns'):
        return
    index: str | None = None
    limit = 0
    if len(parts) == 4 and parts[0] == '' and parts[1] in ('continuous', 'reference') and parts[2] == 'observations':
        index, limit = parts[3], 4096
    elif len(parts) == 3 and parts[0] == '' and parts[1] in ('feed_facts', 'conversion_facts'):
        index, limit = parts[2], 256
    if index is None or not index or len(index) > 4 or any(c not in '0123456789' for c in index) or (len(index) > 1 and index[0] == '0') or int(index) >= limit:
        _fail(ErrorCode.INVALID_SCHEMA, 'canonical bounded input proof pointer required')


@dataclass(frozen=True, slots=True, init=False)
class RoleReadiness:
    role: str
    status: str
    reasons: tuple[str, ...]
    proofs: tuple[str, ...]

    def __init__(self, role: str, status: str, reasons: tuple[str, ...] | list[str],
                 proofs: tuple[str, ...] | list[str]) -> None:
        object.__setattr__(self, 'role', role); object.__setattr__(self, 'status', status)
        object.__setattr__(self, 'reasons', _sequence(reasons, str, 14))
        object.__setattr__(self, 'proofs', _sequence(proofs, str, 4096))
        _role(self)


def _role(value: RoleReadiness) -> None:
    if type(value) is not RoleReadiness or type(value.role) is not str or value.role not in ROLES or type(value.status) is not str or value.status not in ('ready', 'unavailable', 'blocked', 'not_applicable'):
        _fail(ErrorCode.INVALID_SCHEMA, 'closed typed readiness role required')
    reasons = _sequence(value.reasons, str, 14)
    if any(r not in REASONS for r in reasons) or reasons != tuple(r for r in REASONS if r in reasons):
        _fail(ErrorCode.INVALID_SCHEMA, 'ordered unique closed reasons required')
    proofs = _sequence(value.proofs, str, 4096)
    if len(set(proofs)) != len(proofs):
        _fail(ErrorCode.INVALID_SCHEMA, 'unique consumed proof pointers required')
    for proof in proofs:
        _proof(proof)
    if value.status == 'ready' and reasons or value.status == 'blocked' and (reasons or proofs) or value.status == 'unavailable' and not reasons:
        _fail(ErrorCode.INVALID_SCHEMA, 'readiness status contradicts its reasons')
    if value.status == 'not_applicable' and (value.role != 'continuous' or reasons != ('observed_empty',)):
        _fail(ErrorCode.INVALID_SCHEMA, 'only proven empty population is not applicable')


@dataclass(frozen=True, slots=True)
class MetricValue:
    id: str
    value: Rational | None

    def __post_init__(self) -> None:
        if type(self) is not MetricValue or type(self.id) is not str or self.id not in tuple(item for names in METRICS.values() for item in names):
            _fail(ErrorCode.INVALID_SCHEMA, 'own closed metric identity required')
        if self.value is not None:
            validate_rational(self.value)


@dataclass(frozen=True, slots=True)
class SelectedObservation:
    role: str
    observation_id: str

    def __post_init__(self) -> None:
        if type(self) is not SelectedObservation or type(self.role) is not str or self.role not in ('continuous', 'reference'):
            _fail(ErrorCode.INVALID_SCHEMA, 'selected price role required')
        _label(self.observation_id)


@dataclass(frozen=True, slots=True)
class DeviationWitness:
    role: str
    observation_id: str
    reference_id: str
    conversion_fact_id: str
    deviation: Rational

    def __post_init__(self) -> None:
        if type(self) is not DeviationWitness or type(self.role) is not str or self.role != 'continuous':
            _fail(ErrorCode.INVALID_SCHEMA, 'continuous deviation witness required')
        for label in (self.observation_id, self.reference_id, self.conversion_fact_id):
            _label(label)
        validate_rational(self.deviation)


@dataclass(frozen=True, slots=True, init=False)
class ContinuousResult:
    algorithm_version: str
    operation: str
    config_digest: str
    input_digest: str
    status: str
    roles: tuple[RoleReadiness, ...]
    metrics: tuple[MetricValue, ...]
    selected: tuple[SelectedObservation, ...]
    top_k: tuple[DeviationWitness, ...]
    population_count: int | None
    available_at_ns: int | None

    def __init__(self, algorithm_version: str, operation: str, config_digest: str,
                 input_digest: str, status: str, roles: tuple[RoleReadiness, ...] | list[RoleReadiness],
                 metrics: tuple[MetricValue, ...] | list[MetricValue],
                 selected: tuple[SelectedObservation, ...] | list[SelectedObservation],
                 top_k: tuple[DeviationWitness, ...] | list[DeviationWitness],
                 population_count: int | None, available_at_ns: int | None) -> None:
        object.__setattr__(self, 'algorithm_version', algorithm_version)
        object.__setattr__(self, 'operation', operation)
        object.__setattr__(self, 'config_digest', config_digest)
        object.__setattr__(self, 'input_digest', input_digest)
        object.__setattr__(self, 'status', status)
        object.__setattr__(self, 'roles', _sequence(roles, RoleReadiness, 7))
        object.__setattr__(self, 'metrics', _sequence(metrics, MetricValue, 2))
        object.__setattr__(self, 'selected', _sequence(selected, SelectedObservation, 4097))
        object.__setattr__(self, 'top_k', _sequence(top_k, DeviationWitness, 32))
        object.__setattr__(self, 'population_count', population_count)
        object.__setattr__(self, 'available_at_ns', available_at_ns)
        _result(self)

    @property
    def identity_digest(self) -> str:
        return hashlib.sha256(encode_payload('continuous_result', result_payload(self))).hexdigest()


def _result(value: ContinuousResult) -> None:
    if type(value) is not ContinuousResult:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact own result required')
    if type(value.algorithm_version) is not str:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact result algorithm string required')
    if value.algorithm_version != '1':
        _fail(ErrorCode.INCOMPATIBLE_VERSION, 'unsupported result algorithm')
    if type(value.operation) is not str or value.operation not in METRICS:
        _fail(ErrorCode.INVALID_SCHEMA, 'closed result operation required')
    _digest_label(value.config_digest); _digest_label(value.input_digest)
    if type(value.status) is not str or value.status not in ('available', 'missing_input', 'incomplete_coverage', 'not_applicable'):
        _fail(ErrorCode.INVALID_SCHEMA, 'closed result status required')
    roles = _sequence(value.roles, RoleReadiness, 7)
    for role in roles:
        _role(role)
    if tuple(r.role for r in roles) != ROLES:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact ordered seven roles required')
    metrics = _sequence(value.metrics, MetricValue, 2)
    for metric in metrics:
        MetricValue.__post_init__(metric)
    if tuple(m.id for m in metrics) != METRICS[value.operation]:
        _fail(ErrorCode.INVALID_SCHEMA, 'exact ordered operation metrics required')
    selected = _sequence(value.selected, SelectedObservation, 4097)
    for observation in selected:
        SelectedObservation.__post_init__(observation)
    if len({(s.role, s.observation_id) for s in selected}) != len(selected):
        _fail(ErrorCode.INVALID_SCHEMA, 'unique selected role and observation required')
    continuous = tuple(s.observation_id for s in selected if s.role == 'continuous')
    reference = tuple(s.observation_id for s in selected if s.role == 'reference')
    if tuple(s.role for s in selected) != ('continuous',) * len(continuous) + ('reference',) * len(reference) or len(reference) > 1:
        _fail(ErrorCode.INVALID_SCHEMA, 'continuous then held reference selection required')
    if value.operation != 'freeze' and len(continuous) > 1:
        _fail(ErrorCode.INVALID_SCHEMA, 'single continuous selection required')
    if value.operation == 'basis' and reference and not continuous:
        _fail(ErrorCode.INVALID_SCHEMA, 'basis reference depends on continuous selection')
    if (roles[2].status == 'ready' and not continuous) or (roles[3].status == 'ready' and not reference):
        _fail(ErrorCode.INVALID_SCHEMA, 'ready price role requires selected observation')
    witnesses = _sequence(value.top_k, DeviationWitness, 32)
    for witness in witnesses:
        DeviationWitness.__post_init__(witness)
    if len({w.observation_id for w in witnesses}) != len(witnesses):
        _fail(ErrorCode.INVALID_SCHEMA, 'unique deviation witnesses required')
    if value.operation != 'freeze':
        if value.population_count is not None or witnesses:
            _fail(ErrorCode.INVALID_SCHEMA, 'only freeze has population and deviations')
    elif type(value.population_count) is not int or not 0 <= value.population_count <= 4096:
        _fail(ErrorCode.INVALID_SCHEMA, 'bounded freeze population required')
    if value.operation == 'freeze' and value.population_count is not None and len(continuous) != value.population_count:
        _fail(ErrorCode.INVALID_SCHEMA, 'freeze population must bind every selected continuous row')
    if any(w.observation_id not in continuous or not reference or w.reference_id != reference[0] for w in witnesses):
        _fail(ErrorCode.INVALID_SCHEMA, 'deviation witnesses must bind selected observations')
    incomplete = any('incomplete_coverage' in r.reasons for r in roles)
    if value.status == 'available':
        if any(r.status != 'ready' for r in roles) or any(m.value is None for m in metrics):
            _fail(ErrorCode.INVALID_SCHEMA, 'available result requires ready roles and values')
        if value.operation == 'freeze' and (value.population_count is None or value.population_count == 0 or not witnesses or len(witnesses) > value.population_count):
            _fail(ErrorCode.INVALID_SCHEMA, 'available freeze needs positive population')
    elif value.status == 'not_applicable':
        if value.operation != 'freeze' or value.population_count != 0 or witnesses or roles[2].status != 'not_applicable' or any(r.status != 'ready' for i, r in enumerate(roles) if i != 2) or roles[6].proofs:
            _fail(ErrorCode.INVALID_SCHEMA, 'not applicable requires otherwise ready empty freeze')
    elif value.status == 'incomplete_coverage':
        if not incomplete:
            _fail(ErrorCode.INVALID_SCHEMA, 'incomplete result needs incomplete coverage evidence')
    elif incomplete or not any(r.status == 'unavailable' for r in roles):
        _fail(ErrorCode.INVALID_SCHEMA, 'missing result needs unavailable evidence without incomplete coverage')
    if value.status != 'available' and (any(m.value is not None for m in metrics) or witnesses):
        _fail(ErrorCode.INVALID_SCHEMA, 'unavailable numerical fields must be null')
    if value.status in ('available', 'not_applicable'):
        if value.available_at_ns is None:
            _fail(ErrorCode.INVALID_SCHEMA, 'admitted result requires original availability')
        _ns(value.available_at_ns)
    elif value.available_at_ns is not None:
        _fail(ErrorCode.INVALID_SCHEMA, 'unavailable result has no availability time')


def _interval_payload(value: IntervalSpec) -> dict[str, object]:
    return dict(name=value.name, start_ns=value.start_ns, end_ns=value.end_ns)


def config_payload(value: ContinuousConfig) -> dict[str, object]:
    _config(value); a = value.availability
    return dict(identity=value.identity, schema_version=value.schema_version,
                algorithm_version=value.algorithm_version, operation=value.operation,
                window=_interval_payload(value.window), availability=dict(
                    market_cutoff_ns=a.market_cutoff_ns, knowledge_cutoff_ns=a.knowledge_cutoff_ns,
                    evaluation_ns=a.evaluation_ns, mode=a.mode, reconstruction_reason=a.reconstruction_reason),
                anchor_ns=value.anchor_ns, reopen_ns=value.reopen_ns,
                max_continuous_age_ns=value.max_continuous_age_ns,
                max_reference_age_ns=value.max_reference_age_ns,
                max_mismatch_ns=value.max_mismatch_ns, top_k=value.top_k,
                weighting=value.weighting, reference_mode=value.reference_mode)


def _leg_payload(value: Leg) -> dict[str, object]:
    return dict(instrument_id=value.instrument_id, feed_id=value.feed_id, product_id=value.product_id,
                underlying_id=value.underlying_id, quantity_unit=value.quantity_unit,
                price_kind=value.price_kind, source=dict(source_id=value.source.source_id,
                    snapshot_id=value.source.snapshot_id, mapping_version=value.source.mapping_version,
                    input_id=value.source.input_id),
                price_unit=dict(scale=value.price_unit.scale, currency=value.price_unit.currency),
                adjustment=dict(basis=value.adjustment.basis, policy_version=value.adjustment.policy_version,
                    action_snapshot=value.adjustment.action_snapshot, anchor=value.adjustment.anchor),
                scope=_interval_payload(value.scope), coverage=dict(expected=value.coverage.expected,
                    observed=value.coverage.observed, complete=value.coverage.complete),
                coverage_known_at_ns=value.coverage_known_at_ns,
                observations=[dict(observation_id=r.observation_id, event_ns=r.event_ns,
                    order_key=r.order_key, price=r.price, known_at_ns=r.known_at_ns) for r in value.observations])


def input_payload(value: ContinuousInput) -> dict[str, object]:
    _input(value)
    return dict(config=config_payload(value.config), continuous=_leg_payload(value.continuous),
                reference=_leg_payload(value.reference), feed_facts=[dict(fact_id=f.fact_id,
                    revision=f.revision, feed_id=f.feed_id, product_id=f.product_id,
                    interval=_interval_payload(f.interval), state=f.state, known_at_ns=f.known_at_ns) for f in value.feed_facts],
                conversion_facts=[dict(fact_id=f.fact_id, revision=f.revision,
                    continuous_instrument_id=f.continuous_instrument_id,
                    reference_instrument_id=f.reference_instrument_id, underlying_id=f.underlying_id,
                    continuous_quantity_unit=f.continuous_quantity_unit,
                    reference_quantity_unit=f.reference_quantity_unit, currency=f.currency,
                    interval=_interval_payload(f.interval), reference_units_numerator=f.reference_units_numerator,
                    continuous_units_denominator=f.continuous_units_denominator,
                    known_at_ns=f.known_at_ns) for f in value.conversion_facts])


def _rational_payload(value: Rational | None) -> dict[str, object] | None:
    return None if value is None else dict(numerator=value.numerator, denominator=value.denominator)


def result_payload(value: ContinuousResult) -> dict[str, object]:
    _result(value)
    return dict(algorithm_version=value.algorithm_version, operation=value.operation,
                config_digest=value.config_digest, input_digest=value.input_digest,
                status=value.status, roles=[dict(role=r.role, status=r.status,
                    reasons=list(r.reasons), proofs=list(r.proofs)) for r in value.roles],
                metrics=[dict(id=m.id, value=_rational_payload(m.value)) for m in value.metrics],
                selected=[dict(role=s.role, observation_id=s.observation_id) for s in value.selected],
                top_k=[dict(role=w.role, observation_id=w.observation_id, reference_id=w.reference_id,
                    conversion_fact_id=w.conversion_fact_id, deviation=_rational_payload(w.deviation)) for w in value.top_k],
                population_count=value.population_count, available_at_ns=value.available_at_ns)


def encode_payload(kind: str, payload: dict[str, object]) -> bytes:
    raw = json.dumps(dict(kind=kind, schema_version='1', payload=payload), sort_keys=True,
                     separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('utf-8')
    if len(raw) > BYTE_LIMITS[kind]:
        _fail(ErrorCode.BOUNDS, 'encoded continuous representation exceeds declared bytes')
    return raw
