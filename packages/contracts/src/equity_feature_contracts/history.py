"""Caller-owned governed historical session context, schema1."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json

from .errors import ContractError, ErrorCode
from .inputs import Coverage
from .policies import PolicyAdmission
from .results import EntityKey
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
