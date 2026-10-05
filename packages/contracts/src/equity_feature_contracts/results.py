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
from .specs import AvailabilitySpec

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

ResultCell: TypeAlias = int | float | str | bool | BreadthCounts | BreadthFraction | None

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
    else: valid = type(value) is BreadthFraction
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
                if q.status != Status.AVAILABLE and value is not None and not (q.status == Status.INCOMPLETE_COVERAGE and isinstance(value,(BreadthCounts,BreadthFraction))):
                    raise ContractError(ErrorCode.INVALID_SCHEMA,"unavailable scalar must be null")
                if isinstance(value,(BreadthCounts,BreadthFraction)):
                    if q.observed != value.eligible or q.expected != value.expected or (q.status == Status.AVAILABLE) != (value.eligible == value.expected):
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"breadth partial status/coverage mismatch")
        if len(self.evidence)>self.metadata.evidence_limit: raise ContractError(ErrorCode.BOUNDS,"evidence exceeds explicit bound")
        evidence_keys = {(x.entity,x.feature_id,x.input_id,x.row_id) for x in self.evidence}
        if len(evidence_keys) != len(self.evidence): raise ContractError(ErrorCode.DUPLICATE,"duplicate evidence identity")
        inputs = {x.metadata.source.input_id:x for x in self.metadata.inputs}
        for e in self.evidence:
            if (e.entity,e.feature_id) not in keys or e.input_id not in inputs: raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"unbound evidence identity")
            knowledge_reason = self.metadata.availability.knowledge_reason(e.known_at_ns)
            if e.use == "consumed":
                if knowledge_reason is not None:
                    raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"evidence cannot claim unknown/future causal knowledge")
                kind = inputs[e.input_id].kind
                cutoff = self.metadata.availability.market_cutoff_ns
                if e.boundary == "closing_auction":
                    if kind != DataKind.TRADE or e.event_ns != cutoff:
                        raise ContractError(ErrorCode.BOUNDS,"closing-auction evidence must be trade at cutoff")
                elif e.boundary == "completed_interval":
                    if kind not in (DataKind.BAR,DataKind.DAILY) or e.event_ns > cutoff:
                        raise ContractError(ErrorCode.BOUNDS,"completed evidence requires bounded bar/daily input")
                elif e.event_ns > cutoff or (kind in (DataKind.TRADE,DataKind.QUOTE) and e.event_ns == cutoff):
                    raise ContractError(ErrorCode.BOUNDS,"ordinary event evidence outside market bound")
            elif e.exclusion_reason in (Reason.UNKNOWN_AVAILABILITY,Reason.FUTURE_KNOWLEDGE) and knowledge_reason != e.exclusion_reason.value:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"exclusion knowledge reason contradicts evidence")
            elif e.exclusion_reason == Reason.FUTURE_MARKET and e.event_ns <= self.metadata.availability.market_cutoff_ns:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"future market exclusion contradicts bound")

    def metadata_json(self) -> str:
        value = {"metadata":asdict(self.metadata),"features":[{"feature_id":c.feature_id,"algorithm_version":c.algorithm_version,"schema_version":c.schema_version,"dtype":c.dtype.value,"unit":c.unit} for c in sorted(self.values,key=lambda x:x.feature_id)]}
        return json.dumps(value,sort_keys=True,separators=(",",":"),ensure_ascii=True)

    def require_same_identity(self, other: FeatureResult) -> None:
        if self.metadata_json() != other.metadata_json():
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"incompatible result identities")
