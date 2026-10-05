"""Caller-owned governed historical session context, schema1."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json
from fractions import Fraction

from .errors import ContractError, ErrorCode
from .inputs import Coverage, DataKind, I64_MAX, PriceUnit
from .policies import PolicyAdmission
from .results import EntityKey, FeatureResult, Status, ValueType
from .specs import SessionSpec


@dataclass(frozen=True)
class HistoryContext:
    entity: EntityKey
    grid_version: str
    sessions: tuple[SessionSpec, ...]
    slot_coverage: tuple[Coverage, ...]
    initialization_anchor: str | None = None
    action_admission: PolicyAdmission | None = None
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported historical context schema")
        if type(self.entity) is not EntityKey or type(self.grid_version) is not str or not self.grid_version.strip():
            raise ContractError(ErrorCode.INVALID_CONFIG, "typed entity and explicit grid version required")
        if type(self.sessions) not in (tuple, list) or not self.sessions or any(type(x) is not SessionSpec for x in self.sessions):
            raise ContractError(ErrorCode.INVALID_CONFIG, "concrete governed session grid required")
        if type(self.slot_coverage) not in (tuple, list) or any(type(x) is not Coverage for x in self.slot_coverage):
            raise ContractError(ErrorCode.INVALID_CONFIG, "concrete per-slot coverage required")
        object.__setattr__(self, "sessions", tuple(self.sessions))
        object.__setattr__(self, "slot_coverage", tuple(self.slot_coverage))
        ids = tuple(x.session_id for x in self.sessions)
        if len(set(ids)) != len(ids):
            raise ContractError(ErrorCode.DUPLICATE, "duplicate governed session ID")
        if self.entity.session_id not in ids or len(self.slot_coverage) != len(ids):
            raise ContractError(ErrorCode.INVALID_CONFIG, "target and one certificate per slot required")
        if any(x.namespace != self.sessions[0].namespace for x in self.sessions):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "one historical namespace required")
        if any(a.close_ns > b.open_ns for a, b in zip(self.sessions, self.sessions[1:])):
            raise ContractError(ErrorCode.INVALID_ORDER, "governed sessions must be increasing and nonoverlapping")
        if any(x.expected != 1 or x.observed not in (0, 1) for x in self.slot_coverage):
            raise ContractError(ErrorCode.INVALID_CONFIG, "each governed slot expects one normalized daily row")
        if self.initialization_anchor is not None and (type(self.initialization_anchor) is not str or self.initialization_anchor not in ids):
            raise ContractError(ErrorCode.INVALID_CONFIG, "initialization anchor must be an explicit governed session")
        if self.action_admission is not None:
            if type(self.action_admission) is not PolicyAdmission or self.action_admission.entity != self.entity:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "action evidence must bind historical target")
            if self.action_admission.reference is not None and self.action_admission.reference.metadata.namespace != self.sessions[0].namespace:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "historical action namespace mismatch")

    @property
    def identity_digest(self) -> str:
        return hashlib.sha256(json.dumps(asdict(self), sort_keys=True, separators=(",", ":"),
                                         ensure_ascii=True, allow_nan=False).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class SMAReference:
    """Exact mean witness paired with a single qualified SMA result; schema1."""
    result: FeatureResult
    numerator: int | None
    denominator: int | None
    price_unit: PriceUnit
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported SMA reference schema")
        if type(self.result) is not FeatureResult or type(self.price_unit) is not PriceUnit:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed SMA result and price unit required")
        if len(self.result.values) != 1 or len(self.result.quality) != 1:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "single SMA cell/quality required")
        column = self.result.values[0]
        if column.feature_id != "history.sma" or column.algorithm_version != "v1" or column.dtype != ValueType.FLOAT64 or len(column.values) != 1:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "single v1 Float64 SMA required")
        if column.unit != f"{self.price_unit.currency}/share":
            raise ContractError(ErrorCode.INVALID_UNIT, "SMA witness unit mismatch")
        bindings = [b for b in self.result.metadata.inputs if b.role == "daily_history"]
        if any(b.kind != DataKind.DAILY or b.metadata.price_unit != self.price_unit for b in bindings):
            raise ContractError(ErrorCode.INVALID_UNIT, "SMA witness source unit mismatch")
        quality = self.result.quality[0]
        if quality.status != Status.AVAILABLE:
            if self.numerator is not None or self.denominator is not None:
                raise ContractError(ErrorCode.INVALID_SCHEMA, "unavailable SMA has no exact operands")
            return
        if len(bindings) != 1:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "available SMA needs exact daily input binding")
        if type(self.numerator) is not int or not 0 < self.numerator < 10**38:
            raise ContractError(ErrorCode.OVERFLOW, "positive decimal128 SMA sum required")
        if type(self.denominator) is not int or not 1 <= self.denominator <= I64_MAX:
            raise ContractError(ErrorCode.BOUNDS, "positive int64 SMA count required")
        if not self.denominator <= self.numerator <= self.denominator*I64_MAX:
            raise ContractError(ErrorCode.BOUNDS, "mean outside positive int64 coefficient range")
        if self.denominator != quality.expected or self.denominator != quality.observed:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "SMA operands/coverage disagree")
        if column.values[0] != float(Fraction(self.numerator, self.denominator*10**self.price_unit.scale)):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "SMA exact operands/Float64 projection disagree")

    def compare_price(self, coefficient: int, unit: PriceUnit) -> int:
        """Return -1/0/+1 for exact supplied price versus this available mean."""
        if type(unit) is not PriceUnit or unit != self.price_unit:
            raise ContractError(ErrorCode.INVALID_UNIT, "comparison requires identical price unit")
        if type(coefficient) is not int or not 1 <= coefficient <= I64_MAX:
            raise ContractError(ErrorCode.BOUNDS, "positive int64 comparison price required")
        if self.numerator is None or self.denominator is None:
            raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY, "unavailable SMA cannot be compared")
        difference = coefficient*self.denominator-self.numerator
        return (difference > 0)-(difference < 0)
