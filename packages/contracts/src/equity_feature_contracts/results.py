"""Typed immutable result tables, quality, provenance and bounded evidence."""
from __future__ import annotations
from dataclasses import asdict, dataclass
from enum import StrEnum
from fractions import Fraction
import hashlib
import json
import math
import re
from typing import TypeAlias
from .errors import ContractError, ErrorCode
from .inputs import BatchMetadata, DataKind, I64_MIN, I64_MAX
from .specs import AvailabilitySpec, IntervalSpec

class Status(StrEnum):
    AVAILABLE = "available"
    INSUFFICIENT_HISTORY = "insufficient_history"
    MISSING_INPUT = "missing_input"
    INCOMPLETE_COVERAGE = "incomplete_coverage"
    NOT_APPLICABLE = "not_applicable"

class Reason(StrEnum):
    ABSENT_INPUT = "absent_input"
    NULL_FIELD = "null_field"
    OBSERVED_EMPTY = "observed_empty"
    NO_ELIGIBLE_OBSERVATIONS = "no_eligible_observations"
    MISSING_ACTION_EVIDENCE = "missing_action_evidence"
    INSUFFICIENT_HISTORY = "insufficient_history"
    GOVERNED_GAP = "governed_gap"
    UNKNOWN_AVAILABILITY = "unknown_availability"
    FUTURE_KNOWLEDGE = "future_knowledge"
    PARTIAL_UNIVERSE = "partial_universe"
    ZERO_DENOMINATOR = "zero_denominator"
    EMPTY_UNIVERSE = "empty_universe"
    INELIGIBLE = "ineligible"
    FUTURE_MARKET = "future_market"

class ValueType(StrEnum):
    INT64 = "int64"
    DECIMAL128 = "decimal128"
    FLOAT64 = "float64"
    STRING = "string"
    BOOL = "bool"
    BREADTH_COUNTS = "breadth_counts"
    BREADTH_FRACTION = "breadth_fraction"
    TIME_WEIGHTED_SPREAD = "time_weighted_spread"
    QUOTE_STATE_COUNTS = "quote_state_counts"
    SAMPLED_SPREAD = "sampled_spread"
    TOP_K_TRADES = "top_k_trades"
    INTERVAL_OHLCV = "interval_ohlcv"
    INTERVAL_VOLUME_SHARES = "interval_volume_shares"

def _label(value: str) -> None:
    if type(value) is not str or not value.strip():
        raise ContractError(ErrorCode.INVALID_SCHEMA, "nonempty result identity/unit required")

def _count(value: int) -> None:
    if type(value) is not int or not 0 <= value <= I64_MAX:
        raise ContractError(ErrorCode.BOUNDS, "nonnegative int64 count required")

@dataclass(frozen=True)
class EntityKey:
    instrument_id: str
    session_id: str

    def __post_init__(self) -> None:
        _label(self.instrument_id); _label(self.session_id)

@dataclass(frozen=True)
class BreadthCounts:
    advancing: int
    declining: int
    unchanged: int
    expected: int

    def __post_init__(self) -> None:
        for value in (self.advancing, self.declining, self.unchanged, self.expected): _count(value)
        if not 0 < self.eligible <= self.expected:
            raise ContractError(ErrorCode.BOUNDS, "positive eligible breadth within expected universe required")

    @property
    def eligible(self) -> int:
        return self.advancing + self.declining + self.unchanged

    @property
    def coverage(self) -> Fraction:
        return Fraction(self.eligible, self.expected)

@dataclass(frozen=True)
class BreadthFraction:
    above: int
    eligible: int
    expected: int

    def __post_init__(self) -> None:
        for value in (self.above, self.eligible, self.expected): _count(value)
        if not 0 < self.eligible <= self.expected or self.above > self.eligible:
            raise ContractError(ErrorCode.BOUNDS, "breadth numerator/eligible/expected mismatch")

    @property
    def fraction(self) -> Fraction:
        return Fraction(self.above, self.eligible)

    @property
    def coverage(self) -> Fraction:
        return Fraction(self.eligible, self.expected)

@dataclass(frozen=True)
class IntervalOHLCVRow:
    interval: IntervalSpec
    open_price: float | None
    high_price: float | None
    low_price: float | None
    close_price: float | None
    volume: int | None
    quality: QualityRow

    def __post_init__(self) -> None:
        if type(self.interval) is not IntervalSpec or type(self.quality) is not QualityRow:
            raise ContractError(ErrorCode.INVALID_SCHEMA,"typed interval and quality required")
        if self.quality.status != Status.AVAILABLE:
            if any(x is not None for x in (self.open_price,self.high_price,self.low_price,self.close_price,self.volume)):
                raise ContractError(ErrorCode.INVALID_SCHEMA,"unavailable interval row must be null")
        else:
            _count(self.volume)  # type: ignore[arg-type]
            prices=(self.open_price,self.high_price,self.low_price,self.close_price)
            if self.volume == 0:
                if any(x is not None for x in prices): raise ContractError(ErrorCode.INVALID_SCHEMA,"empty interval has no prices")
            elif any(type(x) is not float or not math.isfinite(x) or x <= 0 for x in prices):
                raise ContractError(ErrorCode.INVALID_SCHEMA,"positive finite interval prices required")
            elif not self.low_price <= self.open_price <= self.high_price or not self.low_price <= self.close_price <= self.high_price:  # type: ignore[operator]
                raise ContractError(ErrorCode.INVALID_SCHEMA,"interval OHLC coherence required")

@dataclass(frozen=True)
class IntervalVolumeShareRow:
    interval: IntervalSpec
    share: float | None
    quality: QualityRow

    def __post_init__(self) -> None:
        if type(self.interval) is not IntervalSpec or type(self.quality) is not QualityRow:
            raise ContractError(ErrorCode.INVALID_SCHEMA,"typed interval and quality required")
        if self.quality.status == Status.AVAILABLE:
            if type(self.share) is not float or not math.isfinite(self.share) or not 0 <= self.share <= 1:
                raise ContractError(ErrorCode.BOUNDS,"interval share fraction required")
        elif self.share is not None:
            raise ContractError(ErrorCode.INVALID_SCHEMA,"unavailable share must be null")

@dataclass(frozen=True)
class IntervalOHLCV:
    rows: tuple[IntervalOHLCVRow, ...]

    def __post_init__(self) -> None:
        _interval_rows(self.rows,IntervalOHLCVRow)
        object.__setattr__(self,"rows",tuple(self.rows))

@dataclass(frozen=True)
class IntervalVolumeShares:
    rows: tuple[IntervalVolumeShareRow, ...]

    def __post_init__(self) -> None:
        _interval_rows(self.rows,IntervalVolumeShareRow)
        object.__setattr__(self,"rows",tuple(self.rows))

def _interval_rows(rows: tuple[IntervalOHLCVRow, ...] | tuple[IntervalVolumeShareRow, ...], expected: type[IntervalOHLCVRow] | type[IntervalVolumeShareRow]) -> None:
    if type(rows) not in (tuple,list) or any(type(x) is not expected for x in rows):
        raise ContractError(ErrorCode.INVALID_SCHEMA,"concrete typed interval rows required")
    if len({x.interval.name for x in rows}) != len(rows):
        raise ContractError(ErrorCode.DUPLICATE,"duplicate interval output name")

@dataclass(frozen=True)
class TopKTradeRow:
    input_id: str
    event_id: str
    event_ns: int
    order_key: int
    known_at_ns: int | None
    price: int
    size: int

    def __post_init__(self) -> None:
        _label(self.input_id); _label(self.event_id)
        for value in (self.event_ns,self.order_key,self.known_at_ns):
            if value is not None and (type(value) is not int or not I64_MIN <= value <= I64_MAX):
                raise ContractError(ErrorCode.BOUNDS,"exact int64 trade ordering required")
        if type(self.event_ns) is not int or type(self.order_key) is not int:
            raise ContractError(ErrorCode.INVALID_SCHEMA,"nonnull trade ordering required")
        for value in (self.price,self.size):
            if type(value) is not int or not 0 < value <= I64_MAX:
                raise ContractError(ErrorCode.BOUNDS,"positive int64 trade payload required")

    @property
    def rank_key(self) -> tuple[int,int,int,str]:
        return (-self.size,self.event_ns,self.order_key,self.event_id)

@dataclass(frozen=True)
class TopKTrades:
    k: int
    rows: tuple[TopKTradeRow, ...]

    def __post_init__(self) -> None:
        if type(self.k) is not int or not 1 <= self.k <= 10000:
            raise ContractError(ErrorCode.BOUNDS,"topK bound1..10000 required")
        if type(self.rows) not in (tuple,list) or any(type(x) is not TopKTradeRow for x in self.rows):
            raise ContractError(ErrorCode.INVALID_SCHEMA,"concrete typed topK rows required")
        object.__setattr__(self,"rows",tuple(self.rows))
        if len(self.rows) > self.k:
            raise ContractError(ErrorCode.BOUNDS,"topK retained bound exceeded")
        if len({(x.input_id,x.event_id) for x in self.rows}) != len(self.rows):
            raise ContractError(ErrorCode.DUPLICATE,"duplicate topK source/event identity")
        if tuple(x.rank_key for x in self.rows) != tuple(sorted(x.rank_key for x in self.rows)):
            raise ContractError(ErrorCode.INVALID_ORDER,"topK rows must be ranked")

@dataclass(frozen=True)
class QuoteStateCounts:
    normal: int
    locked: int
    crossed: int
    invalid: int

    def __post_init__(self) -> None:
        for value in (self.normal,self.locked,self.crossed,self.invalid): _count(value)
        _count(self.total)

    @property
    def total(self) -> int: return self.normal+self.locked+self.crossed+self.invalid

    @property
    def valid(self) -> int: return self.normal+self.locked

@dataclass(frozen=True)
class QuoteObservation:
    input_id: str
    event_id: str
    event_ns: int
    order_key: int
    known_at_ns: int | None
    bid: int | None
    ask: int | None
    state: str
    spread: float | None
    bps: float | None

    def __post_init__(self) -> None:
        _label(self.input_id); _label(self.event_id)
        for value in (self.event_ns,self.order_key,self.known_at_ns,self.bid,self.ask):
            if value is not None and (type(value) is not int or not I64_MIN <= value <= I64_MAX):
                raise ContractError(ErrorCode.BOUNDS,"exact int64 quote observation required")
        if type(self.event_ns) is not int or type(self.order_key) is not int:
            raise ContractError(ErrorCode.INVALID_SCHEMA,"nonnull quote ordering required")
        if self.bid is None or self.ask is None or self.bid <= 0 or self.ask <= 0: expected="invalid"
        elif self.bid > self.ask: expected="crossed"
        elif self.bid == self.ask: expected="locked"
        else: expected="normal"
        if self.state != expected:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"quote state contradicts original prices")
        if expected == "invalid":
            if self.spread is not None or self.bps is not None:
                raise ContractError(ErrorCode.INVALID_SCHEMA,"invalid quote diagnostics must be null")
        elif any(type(x) is not float or not math.isfinite(x) for x in (self.spread,self.bps)):
            raise ContractError(ErrorCode.INVALID_SCHEMA,"finite quote diagnostics required")
        elif expected == "locked" and (self.spread != 0 or self.bps != 0):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"locked diagnostics must be zero")
        elif expected == "normal" and (self.spread <= 0 or self.bps <= 0):  # type: ignore[operator]
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"normal diagnostics must be positive")
        elif expected == "crossed" and (self.spread >= 0 or self.bps >= 0):  # type: ignore[operator]
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"crossed diagnostics must be negative")

@dataclass(frozen=True)
class SampledSpread:
    sampling: str
    total: int
    valid: int
    mean_spread: float | None
    mean_bps: float | None
    observation_limit: int
    rows: tuple[QuoteObservation, ...] = ()

    def __post_init__(self) -> None:
        if self.sampling not in ("trade_snapshot","continuous"):
            raise ContractError(ErrorCode.UNSUPPORTED_SAMPLING,"explicit quote sampling required")
        _count(self.total); _count(self.valid)
        if self.valid > self.total or type(self.observation_limit) is not int or not 0 <= self.observation_limit <= 10000:
            raise ContractError(ErrorCode.BOUNDS,"quote population/observation bound mismatch")
        if type(self.rows) not in (tuple,list) or any(type(x) is not QuoteObservation for x in self.rows):
            raise ContractError(ErrorCode.INVALID_SCHEMA,"concrete typed quote observations required")
        object.__setattr__(self,"rows",tuple(self.rows))
        if len(self.rows) != min(self.observation_limit,self.total):
            raise ContractError(ErrorCode.BOUNDS,"quote diagnostic bound/count mismatch")
        if len({(x.input_id,x.event_id) for x in self.rows}) != len(self.rows):
            raise ContractError(ErrorCode.DUPLICATE,"duplicate quote diagnostic identity")
        keys=tuple((x.event_ns,x.order_key) for x in self.rows)
        if any(a >= b for a,b in zip(keys,keys[1:])):
            raise ContractError(ErrorCode.INVALID_ORDER,"quote diagnostics must preserve total input order")
        if self.valid == 0:
            if self.mean_spread is not None or self.mean_bps is not None:
                raise ContractError(ErrorCode.INVALID_SCHEMA,"zero-valid means must be null")
        elif any(type(x) is not float or not math.isfinite(x) or x < 0 for x in (self.mean_spread,self.mean_bps)):
            raise ContractError(ErrorCode.INVALID_SCHEMA,"finite nonnegative valid means required")

    @property
    def truncated(self) -> bool: return len(self.rows) < self.total

@dataclass(frozen=True)
class QuoteDurations:
    normal: int
    locked: int
    crossed: int
    invalid: int
    expired: int
    unknown: int

    def __post_init__(self) -> None:
        for value in (self.normal,self.locked,self.crossed,self.invalid,self.expired,self.unknown): _count(value)
        _count(self.total)
        if self.total == 0: raise ContractError(ErrorCode.BOUNDS,"positive target duration required")

    @property
    def total(self) -> int: return self.normal+self.locked+self.crossed+self.invalid+self.expired+self.unknown

    @property
    def valid(self) -> int: return self.normal+self.locked

    @property
    def valid_fraction(self) -> float: return float(Fraction(self.valid,self.total))

@dataclass(frozen=True)
class TimeWeightedSpread:
    durations: QuoteDurations
    mean_spread: float | None
    mean_bps: float | None
    max_age_ns: int
    initial_state: str

    def __post_init__(self) -> None:
        if type(self.durations) is not QuoteDurations or self.initial_state not in ("seed","inactive","unknown"):
            raise ContractError(ErrorCode.INVALID_SCHEMA,"typed durations/explicit initial state required")
        if type(self.max_age_ns) is not int or not 1 <= self.max_age_ns <= I64_MAX:
            raise ContractError(ErrorCode.BOUNDS,"positive int64 max age required")
        if self.initial_state == "inactive" and self.durations.unknown:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"known inactive initialization cannot have unknown time")
        if self.durations.valid == 0 or self.durations.unknown > 0:
            if self.mean_spread is not None or self.mean_bps is not None:
                raise ContractError(ErrorCode.INVALID_SCHEMA,"unknown/zero-valid time means must be null")
        elif any(type(x) is not float or not math.isfinite(x) or x < 0 for x in (self.mean_spread,self.mean_bps)):
            raise ContractError(ErrorCode.INVALID_SCHEMA,"finite nonnegative time means required")

ResultCell: TypeAlias = int | float | str | bool | TimeWeightedSpread | QuoteStateCounts | SampledSpread | TopKTrades | BreadthCounts | BreadthFraction | IntervalOHLCV | IntervalVolumeShares | None

@dataclass(frozen=True)
class FeatureColumn:
    feature_id: str
    algorithm_version: str
    dtype: ValueType
    unit: str
    entities: tuple[EntityKey, ...]
    values: tuple[ResultCell, ...]
    schema_version: str = "1"

    def __post_init__(self) -> None:
        for label in (self.feature_id, self.algorithm_version, self.unit): _label(label)
        if self.schema_version != "1" or type(self.dtype) is not ValueType:
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported result schema/type")
        if type(self.entities) not in (tuple, list) or type(self.values) not in (tuple, list) or any(type(x) is not EntityKey for x in self.entities):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete typed result columns required")
        object.__setattr__(self, "entities", tuple(self.entities)); object.__setattr__(self, "values", tuple(self.values))
        if len(self.entities) != len(self.values):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "result column length mismatch")
        if len(set(self.entities)) != len(self.entities):
            raise ContractError(ErrorCode.DUPLICATE, "duplicate result key")
        for value in self.values: _value(self.dtype, value)

def _value(dtype: ValueType, value: ResultCell) -> None:
    if value is None: return
    if dtype == ValueType.INT64:
        valid = type(value) is int and I64_MIN <= value <= I64_MAX
    elif dtype == ValueType.DECIMAL128:
        valid = type(value) is int and -(10**38) < value < 10**38
    elif dtype == ValueType.FLOAT64:
        valid = type(value) is float and math.isfinite(value)
    elif dtype == ValueType.STRING: valid = type(value) is str
    elif dtype == ValueType.BOOL: valid = type(value) is bool
    elif dtype == ValueType.BREADTH_COUNTS: valid = type(value) is BreadthCounts
    elif dtype == ValueType.BREADTH_FRACTION: valid = type(value) is BreadthFraction
    elif dtype == ValueType.TIME_WEIGHTED_SPREAD: valid = type(value) is TimeWeightedSpread
    elif dtype == ValueType.QUOTE_STATE_COUNTS: valid = type(value) is QuoteStateCounts
    elif dtype == ValueType.SAMPLED_SPREAD: valid = type(value) is SampledSpread
    elif dtype == ValueType.TOP_K_TRADES: valid = type(value) is TopKTrades
    elif dtype == ValueType.INTERVAL_OHLCV: valid = type(value) is IntervalOHLCV
    else: valid = type(value) is IntervalVolumeShares
    if not valid:
        code = ErrorCode.OVERFLOW if type(value) is int and dtype in (ValueType.INT64, ValueType.DECIMAL128) else ErrorCode.INVALID_SCHEMA
        raise ContractError(code, "result type/precision mismatch")

@dataclass(frozen=True)
class QualityRow:
    entity: EntityKey
    feature_id: str
    status: Status
    expected: int | None
    observed: int
    reasons: tuple[Reason, ...] = ()

    def __post_init__(self) -> None:
        _label(self.feature_id); _count(self.observed)
        if type(self.entity) is not EntityKey or type(self.status) is not Status or type(self.reasons) not in (tuple, list) or any(type(x) is not Reason for x in self.reasons):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed quality row required")
        object.__setattr__(self, "reasons", tuple(self.reasons))
        if len(set(self.reasons)) != len(self.reasons): raise ContractError(ErrorCode.DUPLICATE, "duplicate quality reason")
        if self.expected is not None:
            _count(self.expected)
            if self.observed > self.expected: raise ContractError(ErrorCode.BOUNDS, "observed coverage above expected")
        if self.status == Status.AVAILABLE and (self.expected is None or self.observed != self.expected):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "available quality requires complete declared coverage")
        if self.status != Status.AVAILABLE and not self.reasons:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "unavailable/partial status requires reason")

@dataclass(frozen=True)
class InputBinding:
    role: str
    kind: DataKind
    metadata: BatchMetadata
    schema_version: str = "1"

    def __post_init__(self) -> None:
        _label(self.role)
        if type(self.kind) is not DataKind or type(self.metadata) is not BatchMetadata or self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "typed schema1 input binding required")

@dataclass(frozen=True)
class ResultMetadata:
    namespace: str
    session_id: str
    availability: AvailabilitySpec
    config_digest: str
    inputs: tuple[InputBinding, ...]
    backend_id: str
    backend_version: str
    evidence_limit: int = 0
    schema_version: str = "1"
    math_policy_version: str = "v1"

    def __post_init__(self) -> None:
        for label in (self.namespace, self.session_id, self.backend_id, self.backend_version, self.math_policy_version): _label(label)
        if type(self.availability) is not AvailabilitySpec or type(self.config_digest) is not str or re.fullmatch("[0-9a-f]{64}", self.config_digest) is None:
            raise ContractError(ErrorCode.INVALID_CONFIG, "typed timing and canonical SHA256 config digest required")
        if self.schema_version != "1": raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported result metadata schema")
        if type(self.inputs) not in (tuple, list) or any(type(x) is not InputBinding for x in self.inputs):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete typed input bindings required")
        object.__setattr__(self, "inputs", tuple(sorted(self.inputs, key=lambda x: x.role)))
        if len({x.role for x in self.inputs}) != len(self.inputs) or len({x.metadata.source.input_id for x in self.inputs}) != len(self.inputs):
            raise ContractError(ErrorCode.DUPLICATE, "duplicate input role/identity")
        if any(x.metadata.namespace != self.namespace for x in self.inputs):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "input/result namespace mismatch")
        _count(self.evidence_limit)

    def to_json(self) -> str:
        return json.dumps(asdict(self), sort_keys=True, separators=(",", ":"), ensure_ascii=True, allow_nan=False)

    @property
    def identity_digest(self) -> str:
        return hashlib.sha256(self.to_json().encode()).hexdigest()

@dataclass(frozen=True)
class EvidenceRow:
    entity: EntityKey
    feature_id: str
    input_id: str
    row_id: str
    event_ns: int
    known_at_ns: int | None
    effective_start_ns: int | None = None
    effective_end_ns: int | None = None
    use: str = "consumed"
    exclusion_reason: Reason | None = None
    boundary: str = "ordinary"

    def __post_init__(self) -> None:
        if self.boundary not in ("ordinary","completed_interval","closing_auction"):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "unsupported evidence boundary")
        if self.use not in ("consumed","excluded") or (self.use == "consumed" and self.exclusion_reason is not None) or (self.use == "excluded" and type(self.exclusion_reason) is not Reason):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "explicit evidence use/reason required")
        if type(self.entity) is not EntityKey: raise ContractError(ErrorCode.INVALID_SCHEMA, "typed evidence entity required")
        for label in (self.feature_id, self.input_id, self.row_id): _label(label)
        if type(self.event_ns) is not int:
            raise ContractError(ErrorCode.BOUNDS, "nonnull exact event UTCns required")
        for value in (self.event_ns, self.known_at_ns, self.effective_start_ns, self.effective_end_ns):
            if value is not None and (type(value) is not int or not I64_MIN <= value <= I64_MAX):
                raise ContractError(ErrorCode.BOUNDS, "exact UTCns evidence required")
        if self.effective_start_ns is not None and self.effective_end_ns is not None and self.effective_start_ns >= self.effective_end_ns:
            raise ContractError(ErrorCode.BOUNDS, "invalid evidence effective bounds")

def _past_market_bound(evidence: EvidenceRow, kind: DataKind, cutoff: int) -> bool:
    """Shared cutoff predicate for consumption and market exclusion evidence."""
    if evidence.boundary == "closing_auction":
        if kind != DataKind.TRADE:
            raise ContractError(ErrorCode.BOUNDS, "closing-auction evidence requires trade input")
        inclusive = True
    elif evidence.boundary == "completed_interval":
        if kind not in (DataKind.BAR, DataKind.DAILY):
            raise ContractError(ErrorCode.BOUNDS, "completed evidence requires bar/daily input")
        inclusive = True
    else:
        inclusive = kind not in (DataKind.TRADE, DataKind.QUOTE)
    return evidence.event_ns > cutoff or (evidence.event_ns == cutoff and not inclusive)

@dataclass(frozen=True)
class FeatureResult:
    values: tuple[FeatureColumn, ...]
    quality: tuple[QualityRow, ...]
    metadata: ResultMetadata
    evidence: tuple[EvidenceRow, ...] = ()

    def __post_init__(self) -> None:
        if type(self.metadata) is not ResultMetadata: raise ContractError(ErrorCode.INVALID_SCHEMA, "typed result metadata required")
        for name, rows, expected in (("values",self.values,FeatureColumn),("quality",self.quality,QualityRow),("evidence",self.evidence,EvidenceRow)):
            if type(rows) not in (tuple,list) or any(type(x) is not expected for x in rows):
                raise ContractError(ErrorCode.INVALID_SCHEMA, f"concrete typed {name} table required")
        object.__setattr__(self,"values",tuple(self.values)); object.__setattr__(self,"quality",tuple(self.quality)); object.__setattr__(self,"evidence",tuple(self.evidence))
        if len({c.feature_id for c in self.values}) != len(self.values): raise ContractError(ErrorCode.DUPLICATE,"duplicate feature column")
        qualities = {(q.entity,q.feature_id):q for q in self.quality}
        if len(qualities) != len(self.quality): raise ContractError(ErrorCode.DUPLICATE,"duplicate quality key")
        keys = {(entity,c.feature_id) for c in self.values for entity in c.entities}
        if keys != set(qualities): raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"value/quality keys must match exactly")
        for c in self.values:
            for entity,value in zip(c.entities,c.values,strict=True):
                q = qualities[entity,c.feature_id]
                if entity.session_id != self.metadata.session_id: raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"result session mismatch")
                if q.status == Status.AVAILABLE and value is None: raise ContractError(ErrorCode.INVALID_SCHEMA,"available result cannot be null")
                if q.status != Status.AVAILABLE and value is not None and not (isinstance(value,TimeWeightedSpread) and q.status in (Status.NOT_APPLICABLE,Status.INCOMPLETE_COVERAGE)) and not (q.status == Status.NOT_APPLICABLE and isinstance(value,SampledSpread) and value.valid == 0) and not (q.status == Status.INCOMPLETE_COVERAGE and isinstance(value,(BreadthCounts,BreadthFraction,IntervalOHLCV,IntervalVolumeShares))):
                    raise ContractError(ErrorCode.INVALID_SCHEMA,"unavailable scalar must be null")
                if isinstance(value,TimeWeightedSpread):
                    targets=[b for b in self.metadata.inputs if b.role == "quotes" and b.kind == DataKind.QUOTE]
                    if len(targets) != 1:
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"time spread needs one quote target")
                    seeds=[b for b in self.metadata.inputs if b.role == "quote_seed"]
                    if seeds and (value.initial_state != "seed" or len(seeds) != 1 or seeds[0].kind != DataKind.QUOTE or seeds[0].metadata.sampling != "continuous"):
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"time initialization contradicts seed binding")
                    target=targets[0].metadata
                    if target.sampling != "continuous" or not target.coverage.complete or target.scope is None or target.scope.end_ns != self.metadata.availability.market_cutoff_ns:
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"time duration requires complete continuous target scope")
                    if q.expected != target.coverage.expected or q.observed != target.coverage.observed or value.durations.total != target.scope.end_ns-target.scope.start_ns:
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"time duration/population conservation mismatch")
                    expected_status=Status.INCOMPLETE_COVERAGE if value.durations.unknown else Status.AVAILABLE if value.durations.valid else Status.NOT_APPLICABLE
                    if q.status != expected_status:
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"time denominator/unknown duration status mismatch")
                if isinstance(value,(QuoteStateCounts,SampledSpread)):
                    bindings=[b for b in self.metadata.inputs if b.role == "quotes" and b.kind == DataKind.QUOTE]
                    if len(bindings) != 1 or not bindings[0].metadata.coverage.complete or bindings[0].metadata.coverage.observed != value.total:
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"quote output requires complete matching target binding")
                    if isinstance(value,SampledSpread):
                        if value.sampling != bindings[0].metadata.sampling:
                            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"sampled label contradicts source sampling")
                        peers=[v for col in self.values for key,v in zip(col.entities,col.values,strict=True) if key == entity and isinstance(v,QuoteStateCounts)]
                        if any(peer.total != value.total or peer.valid != value.valid for peer in peers):
                            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"sampled denominator contradicts state counts")
                    if q.observed != value.total or q.expected != value.total:
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"complete quote output population/quality mismatch")
                    if isinstance(value,SampledSpread) and (q.status == Status.AVAILABLE) != (value.valid > 0):
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"sampled valid denominator/status mismatch")
                if isinstance(value,(BreadthCounts,BreadthFraction)):
                    if q.observed != value.eligible or q.expected != value.expected or (q.status == Status.AVAILABLE) != (value.eligible == value.expected):
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"breadth partial status/coverage mismatch")
                if isinstance(value,(IntervalOHLCV,IntervalVolumeShares)):
                    ready=sum(row.quality.status == Status.AVAILABLE for row in value.rows)
                    if q.expected != len(value.rows) or q.observed != ready or (q.status == Status.AVAILABLE) != (ready == len(value.rows)):
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"interval aggregate quality mismatch")
                    if any(row.quality.entity != entity or row.quality.feature_id != c.feature_id for row in value.rows):
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"interval quality key mismatch")
        if len(self.evidence)>self.metadata.evidence_limit: raise ContractError(ErrorCode.BOUNDS,"evidence exceeds explicit bound")
        evidence_keys = {(x.entity,x.feature_id,x.input_id,x.row_id) for x in self.evidence}
        if len(evidence_keys) != len(self.evidence): raise ContractError(ErrorCode.DUPLICATE,"duplicate evidence identity")
        for c in self.values:
            for entity,value in zip(c.entities,c.values,strict=True):
                if isinstance(value,(TopKTrades,SampledSpread)):
                    matched = [e for e in self.evidence if e.entity == entity and e.feature_id == c.feature_id]
                    if len(matched) != len(value.rows):
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"bounded rows require exact evidence binding")
                    for row in value.rows:
                        if not any(e.input_id == row.input_id and e.row_id == row.event_id and e.event_ns == row.event_ns and e.known_at_ns == row.known_at_ns and e.use == "consumed" for e in matched):
                            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"bounded original event evidence mismatch")
        inputs = {x.metadata.source.input_id:x for x in self.metadata.inputs}
        for e in self.evidence:
            if (e.entity,e.feature_id) not in keys or e.input_id not in inputs: raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"unbound evidence identity")
            knowledge_reason = self.metadata.availability.knowledge_reason(e.known_at_ns)
            cutoff = self.metadata.availability.market_cutoff_ns
            past_market_bound = _past_market_bound(e, inputs[e.input_id].kind, cutoff)
            if e.use == "consumed":
                if knowledge_reason is not None:
                    raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"evidence cannot claim unknown/future causal knowledge")
                if e.boundary == "closing_auction" and e.event_ns != cutoff:
                    raise ContractError(ErrorCode.BOUNDS,"closing-auction evidence must be trade at cutoff")
                if past_market_bound:
                    raise ContractError(ErrorCode.BOUNDS,"event evidence outside market bound")
            elif e.exclusion_reason in (Reason.UNKNOWN_AVAILABILITY,Reason.FUTURE_KNOWLEDGE) and knowledge_reason != e.exclusion_reason.value:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"exclusion knowledge reason contradicts evidence")
            elif e.exclusion_reason == Reason.FUTURE_MARKET and not past_market_bound:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"future market exclusion contradicts bound")

    def metadata_json(self) -> str:
        value = {"metadata":asdict(self.metadata),"features":[{"feature_id":c.feature_id,"algorithm_version":c.algorithm_version,"schema_version":c.schema_version,"dtype":c.dtype.value,"unit":c.unit} for c in sorted(self.values,key=lambda x:x.feature_id)]}
        return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)

    def require_same_identity(self, other: FeatureResult) -> None:
        if self.metadata_json() != other.metadata_json():
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"incompatible result identities")
