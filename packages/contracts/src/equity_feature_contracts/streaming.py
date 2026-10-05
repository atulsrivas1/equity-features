"""Owned declarations for pure chunk delivery and explicit requested-prefix coverage."""
from __future__ import annotations
from dataclasses import dataclass
from .errors import ContractError, ErrorCode
from .inputs import (BatchMetadata, CanonicalBatch, Column, Coverage, DataKind,
    I64_MIN, I64_MAX, IntervalCoverage)
from .validation import validate_batch

@dataclass(frozen=True)
class StreamPopulation:
    kind: DataKind
    fields: tuple[str, ...]
    metadata: BatchMetadata
    identity_policy: str = 'caller-certified-global-unique-v1'

    def __post_init__(self) -> None:
        if type(self.kind) is not DataKind or type(self.metadata) is not BatchMetadata or self.identity_policy != 'caller-certified-global-unique-v1':
            raise ContractError(ErrorCode.INVALID_SCHEMA,'typed stable caller-certified population required')
        if type(self.fields) not in (tuple,list) or any(type(x) is not str for x in self.fields):
            raise ContractError(ErrorCode.INVALID_SCHEMA,'concrete fixed canonical field names required')
        object.__setattr__(self,'fields',tuple(self.fields))
        CanonicalBatch(self.kind,tuple(Column(name,()) for name in self.fields),self.metadata)
        if self.metadata.scope is None:
            raise ContractError(ErrorCode.INVALID_CONFIG,'stream population requires explicit final target scope')

    @classmethod
    def from_batch(cls, batch: CanonicalBatch) -> StreamPopulation:
        if type(batch) is not CanonicalBatch or not batch.metadata.coverage.complete or batch.metadata.coverage.observed != batch.row_count:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'complete actual population needed for from_batch')
        validate_batch(batch,required_fields=())
        return cls(batch.kind,tuple(c.name for c in batch.columns),batch.metadata)

@dataclass(frozen=True)
class PrefixCoverage:
    cutoff_ns: int
    coverage: Coverage
    interval_coverage: tuple[IntervalCoverage, ...] = ()

    def __post_init__(self) -> None:
        if type(self.cutoff_ns) is not int or not I64_MIN <= self.cutoff_ns <= I64_MAX or type(self.coverage) is not Coverage:
            raise ContractError(ErrorCode.INVALID_SCHEMA,'exact cutoff/typed prefix coverage required')
        if type(self.interval_coverage) not in (tuple,list) or any(type(x) is not IntervalCoverage for x in self.interval_coverage):
            raise ContractError(ErrorCode.INVALID_SCHEMA,'concrete typed interval certificates required')
        object.__setattr__(self,'interval_coverage',tuple(self.interval_coverage))
        if len({x.name for x in self.interval_coverage}) != len(self.interval_coverage):
            raise ContractError(ErrorCode.DUPLICATE,'duplicate prefix interval certificate')
        if any(x.end_ns > self.cutoff_ns for x in self.interval_coverage):
            raise ContractError(ErrorCode.BOUNDS,'interval certificate exceeds requested prefix')

@dataclass(frozen=True)
class AccumulatorState:
    schema_version: str
    implementation_version: str
    binding_digest: str
    payload: str
    payload_digest: str

    def __post_init__(self) -> None:
        import hashlib
        import re
        if any(type(x) is not str or not x for x in (self.schema_version,self.implementation_version,self.binding_digest,self.payload,self.payload_digest)):
            raise ContractError(ErrorCode.INVALID_SCHEMA,'owned text state envelope required')
        if len(self.payload.encode('utf-8')) > 16*1024*1024:
            raise ContractError(ErrorCode.BOUNDS,'state text exceeds16MiB bound')
        if any(re.fullmatch('[0-9a-f]{64}',x) is None for x in (self.binding_digest,self.payload_digest)) or hashlib.sha256(self.payload.encode('utf-8')).hexdigest() != self.payload_digest:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,'state digest mismatch')

@dataclass(frozen=True)
class PartitionSpan:
    start_ordinal: int
    end_ordinal: int

    def __post_init__(self) -> None:
        if any(type(x) is not int or not 0 <= x <= I64_MAX for x in (self.start_ordinal,self.end_ordinal)) or self.start_ordinal >= self.end_ordinal:
            raise ContractError(ErrorCode.BOUNDS,'nonempty exact global population ordinal span required')

    @property
    def count(self) -> int: return self.end_ordinal-self.start_ordinal
