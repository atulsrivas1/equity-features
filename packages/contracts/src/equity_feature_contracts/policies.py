"""Owned supplied-action policy and point-in-time reference evidence, schema1."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json

from .errors import ContractError, ErrorCode
from .inputs import AdjustmentSpec, CanonicalBatch, DataKind, I64_MAX, I64_MIN
from .results import EntityKey, InputBinding, Reason, Status
from .specs import AvailabilitySpec


def _ns(value: int) -> None:
    if type(value) is not int or not I64_MIN <= value <= I64_MAX:
        raise ContractError(ErrorCode.BOUNDS, "policy requires exact int64 UTCns")


def _label(value: str) -> None:
    if type(value) is not str or not value.strip():
        raise ContractError(ErrorCode.INVALID_SCHEMA, "nonempty policy/evidence identity required")


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                    ensure_ascii=True, allow_nan=False).encode("utf-8")).hexdigest()


@dataclass(frozen=True)
class ActionPolicy:
    adjustment: AdjustmentSpec
    anchor_ns: int
    representation: str = "apply_factors"
    quantity_basis: str = "raw_shares"
    dividend_convention: str = "none"
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported action policy schema")
        if type(self.adjustment) is not AdjustmentSpec:
            raise ContractError(ErrorCode.INVALID_CONFIG, "typed output adjustment required")
        _ns(self.anchor_ns)
        versions = {"raw": "raw-v1", "split": "split-factors-v1",
                    "total_return": "total-return-reinvest-v1"}
        convention = "supplied_reinvestment_factors" if self.adjustment.basis == "total_return" else "none"
        if self.adjustment.policy_version != versions[self.adjustment.basis] or self.dividend_convention != convention:
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "unknown factor policy or dividend convention")
        if self.representation not in ("apply_factors", "caller_transformed"):
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "explicit supported input representation required")
        if self.quantity_basis not in ("raw_shares", "split_shares") or (self.adjustment.basis == "raw" and self.quantity_basis != "raw_shares"):
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "incompatible declared quantity basis")

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class ReferenceFact:
    row_index: int
    reference_id: str
    fact_kind: str
    effective_start_ns: int
    effective_end_ns: int | None
    known_at_ns: int | None
    factor_num: int | None = None
    factor_den: int | None = None
    text: str | None = None

    def __post_init__(self) -> None:
        if type(self.row_index) is not int or not 0 <= self.row_index <= I64_MAX:
            raise ContractError(ErrorCode.BOUNDS, "nonnegative reference row index required")
        _label(self.reference_id); _label(self.fact_kind); _ns(self.effective_start_ns)
        if self.effective_end_ns is not None:
            _ns(self.effective_end_ns)
            if self.effective_end_ns <= self.effective_start_ns:
                raise ContractError(ErrorCode.BOUNDS, "positive half-open reference interval required")
        if self.known_at_ns is not None:
            _ns(self.known_at_ns)
        for factor in (self.factor_num, self.factor_den):
            if factor is not None and (type(factor) is not int or not 0 < factor <= I64_MAX):
                raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "positive int64 rational factors required")
        if self.text is not None and type(self.text) is not str:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "reference text must be string or null")


def _admission(entity: EntityKey, config_digest: str, availability: AvailabilitySpec,
               reference: InputBinding | None, facts: tuple[ReferenceFact, ...],
               status: Status, reasons: tuple[Reason, ...]) -> tuple[tuple[ReferenceFact, ...], tuple[Reason, ...]]:
    if type(entity) is not EntityKey or type(availability) is not AvailabilitySpec:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "typed entity and availability required")
    if type(config_digest) is not str or len(config_digest) != 64 or any(x not in "0123456789abcdef" for x in config_digest):
        raise ContractError(ErrorCode.INVALID_CONFIG, "canonical configuration SHA256 required")
    if reference is not None and (type(reference) is not InputBinding or reference.kind != DataKind.REFERENCE):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "typed reference binding required")
    if type(facts) not in (tuple, list) or any(type(x) is not ReferenceFact for x in facts):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete immutable reference facts required")
    if type(reasons) not in (tuple, list) or any(type(x) is not Reason for x in reasons):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "concrete typed policy reasons required")
    if type(status) is not Status or status not in (Status.AVAILABLE, Status.MISSING_INPUT, Status.INCOMPLETE_COVERAGE):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "supported policy readiness required")
    if (status == Status.AVAILABLE) != (not reasons):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "policy readiness/reasons disagree")
    if facts and reference is None:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "selected facts require original reference binding")
    if reference is not None and any(x.row_index >= reference.metadata.coverage.observed for x in facts):
        raise ContractError(ErrorCode.BOUNDS, "selected reference row exceeds supplied population binding")
    if len({x.reference_id for x in facts}) != len(facts) or len({x.row_index for x in facts}) != len(facts):
        raise ContractError(ErrorCode.DUPLICATE, "duplicate selected reference identity/index")
    if status == Status.AVAILABLE and any(availability.knowledge_reason(x.known_at_ns) is not None for x in facts):
        raise ContractError(ErrorCode.BOUNDS, "available reference facts must meet original knowledge policy")
    return tuple(facts), tuple(reasons)


@dataclass(frozen=True)
class PolicyAdmission:
    entity: EntityKey
    policy: ActionPolicy
    config_digest: str
    availability: AvailabilitySpec
    reference: InputBinding | None
    facts: tuple[ReferenceFact, ...]
    status: Status
    reasons: tuple[Reason, ...] = ()

    def __post_init__(self) -> None:
        facts, reasons = _admission(self.entity, self.config_digest, self.availability,
                                   self.reference, self.facts, self.status, self.reasons)
        if type(self.policy) is not ActionPolicy:
            raise ContractError(ErrorCode.INVALID_CONFIG, "typed action policy required")
        if self.policy.anchor_ns > self.availability.market_cutoff_ns:
            raise ContractError(ErrorCode.BOUNDS, "action anchor cannot exceed market cutoff")
        if self.reference is not None and self.policy.adjustment.basis != "raw" and self.reference.metadata.source.snapshot_id != self.policy.adjustment.action_snapshot:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "policy snapshot must match supplied reference binding")
        if self.status == Status.AVAILABLE and self.policy.adjustment.basis != "raw" and (self.reference is None or not self.reference.metadata.coverage.complete):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "available adjusted policy needs complete supplied snapshot")
        if (self.policy.adjustment.basis == "raw" and facts) or (self.policy.adjustment.basis == "split" and any(x.fact_kind != "split_factor" for x in facts)):
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "selected factors disagree with policy basis")
        if any(x.fact_kind not in ("split_factor", "dividend_factor") or x.effective_end_ns is not None or x.effective_start_ns > self.policy.anchor_ns for x in facts):
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "instantaneous supported factors within anchor required")
        if self.status == Status.AVAILABLE and any(x.factor_num is None or x.factor_den is None for x in facts):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "available factors require both rational operands")
        object.__setattr__(self, "facts", facts); object.__setattr__(self, "reasons", reasons)

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))


@dataclass(frozen=True)
class AdjustmentApplication:
    admission: PolicyAdmission
    original_input: InputBinding
    batch: CanonicalBatch | None
    status: Status
    reasons: tuple[Reason, ...] = ()

    def __post_init__(self) -> None:
        if type(self.admission) is not PolicyAdmission or type(self.original_input) is not InputBinding:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed admission/original input required")
        if type(self.status) is not Status or self.status not in (Status.AVAILABLE, Status.MISSING_INPUT, Status.INCOMPLETE_COVERAGE):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "supported application readiness required")
        if type(self.reasons) not in (tuple, list) or any(type(x) is not Reason for x in self.reasons):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "typed application reasons required")
        object.__setattr__(self, "reasons", tuple(self.reasons))
        if (self.status == Status.AVAILABLE) != (self.batch is not None) or (self.status == Status.AVAILABLE) != (not self.reasons):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "application value/readiness/reasons disagree")
        if self.batch is not None:
            if type(self.batch) is not CanonicalBatch or self.admission.status != Status.AVAILABLE:
                raise ContractError(ErrorCode.INVALID_SCHEMA, "ready application requires canonical batch/admission")
            if self.batch.kind != self.original_input.kind or self.batch.metadata.adjustment != self.admission.policy.adjustment:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "output kind/basis disagrees with application")
            if (self.batch.metadata.namespace, self.batch.metadata.price_unit, self.batch.metadata.coverage) != (self.original_input.metadata.namespace, self.original_input.metadata.price_unit, self.original_input.metadata.coverage):
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "output namespace/unit/coverage must preserve input")


@dataclass(frozen=True)
class ClassificationAdmission:
    entity: EntityKey
    fact_kind: str
    effective_ns: int
    config_digest: str
    availability: AvailabilitySpec
    reference: InputBinding | None
    facts: tuple[ReferenceFact, ...]
    status: Status
    reasons: tuple[Reason, ...] = ()

    def __post_init__(self) -> None:
        facts, reasons = _admission(self.entity, self.config_digest, self.availability,
                                   self.reference, self.facts, self.status, self.reasons)
        _ns(self.effective_ns)
        if self.fact_kind not in ("sector_membership", "universe_membership"):
            raise ContractError(ErrorCode.INVALID_CONFIG, "explicit supported classification kind required")
        if self.effective_ns > self.availability.market_cutoff_ns:
            raise ContractError(ErrorCode.BOUNDS, "classification selection cannot exceed market cutoff")
        if len(facts) > 1:
            raise ContractError(ErrorCode.DUPLICATE, "ambiguous applicable classification facts")
        if any(x.fact_kind != self.fact_kind or x.effective_start_ns > self.effective_ns or
               (x.effective_end_ns is not None and self.effective_ns >= x.effective_end_ns) for x in facts):
            raise ContractError(ErrorCode.BOUNDS, "classification fact outside requested half-open interval")
        if self.status == Status.AVAILABLE and (len(facts) != 1 or facts[0].text is None or not facts[0].text.strip()):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "available classification requires one nonempty text fact")
        if self.status == Status.AVAILABLE and (self.reference is None or not self.reference.metadata.coverage.complete):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "available classification requires complete reference coverage")
        object.__setattr__(self, "facts", facts); object.__setattr__(self, "reasons", reasons)

    @property
    def text(self) -> str | None:
        return self.facts[0].text if self.status == Status.AVAILABLE else None

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))
