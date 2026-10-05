"""Immutable definition discovery. R0 has no calculator/callback execution."""
from __future__ import annotations
from dataclasses import asdict, dataclass, replace
import hashlib
import json
import re
from typing import Any
from .errors import ContractError, ErrorCode
from .inputs import DataKind, I64_MAX, schema_for
from .results import ValueType

@dataclass(frozen=True)
class Capabilities:
    batch: bool = False
    update: bool = False
    restore: bool = False
    merge: bool = False

    def __post_init__(self) -> None:
        flags = (self.batch,self.update,self.restore,self.merge)
        if any(type(x) is not bool for x in flags) or any(flags):
            raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY,"R0 definitions cannot claim calculator/callback capabilities")

@dataclass(frozen=True)
class InputRequirement:
    role: str
    schema_id: str
    fields: tuple[str, ...]
    kind: DataKind | None = None
    sampling: str = "none"
    rule: str = "supplied complete admitted input"

    def __post_init__(self) -> None:
        _text(self.role); _text(self.rule)
        if self.schema_id not in ("canonical:1","result:1","evidence:1","session:1","window:1","availability:1"):
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION,"unsupported requirement schema")
        if type(self.fields) not in (tuple,list) or any(type(x) is not str or not x.strip() for x in self.fields):
            raise ContractError(ErrorCode.INVALID_SCHEMA,"concrete field names required")
        object.__setattr__(self,"fields",tuple(self.fields))
        if len(set(self.fields))!=len(self.fields): raise ContractError(ErrorCode.DUPLICATE,"duplicate required field")
        if self.schema_id == "canonical:1":
            if type(self.kind) is not DataKind: raise ContractError(ErrorCode.INVALID_SCHEMA,"canonical kind required")
            for field in self.fields: schema_for(self.kind).field(field)
        else:
            if self.kind is not None: raise ContractError(ErrorCode.INVALID_SCHEMA,"logical schema has no canonical kind")
            fields = {
                "result:1": {"values","quality","metadata","evidence"},
                "evidence:1": {"entity","feature_id","input_id","row_id","event_ns","known_at_ns","effective_start_ns","effective_end_ns","use","exclusion_reason","boundary"},
                "session:1": {"namespace","session_id","open_ns","close_ns","timezone_label","intervals","scheduled_close_ns","early_close","include_opening_auction","include_closing_auction"},
                "window:1": {"count","target_session_id","governed_sessions","anchor"},
                "availability:1": {"market_cutoff_ns","knowledge_cutoff_ns","evaluation_ns","mode","reconstruction_reason"},
            }
            if any(name not in fields[self.schema_id] for name in self.fields):
                raise ContractError(ErrorCode.INVALID_SCHEMA,"unknown logical schema field")
        if self.sampling not in ("none","sampled_or_continuous","continuous") or (self.kind != DataKind.QUOTE and self.sampling!="none"):
            raise ContractError(ErrorCode.UNSUPPORTED_SAMPLING,"invalid requirement sampling")

@dataclass(frozen=True)
class OutputField:
    name: str
    dtype: str
    unit: str
    nullable: bool = True

    def __post_init__(self) -> None:
        _text(self.name); _text(self.unit)
        if self.dtype not in tuple(x.value for x in ValueType)+("evidence:1",) or type(self.nullable) is not bool:
            raise ContractError(ErrorCode.INVALID_SCHEMA,"unsupported output field/type/nullability")

@dataclass(frozen=True)
class FeatureDefinition:
    feature_id: str
    description: str
    requirements: tuple[InputRequirement, ...]
    outputs: tuple[OutputField, ...]
    formula: str
    warmup: str
    timing: str
    missing_policy: str
    formula_document: str
    default_periods: tuple[int, ...] = ()
    initialization: str = "none"
    planned_release: str = "R3"
    algorithm_version: str = "v1"
    schema_version: str = "1"
    capabilities: Capabilities = Capabilities()

    def __post_init__(self) -> None:
        for value in (self.feature_id,self.description,self.formula,self.warmup,self.timing,self.missing_policy,self.formula_document,self.initialization,self.algorithm_version): _text(value)
        if self.schema_version != "1" or self.planned_release not in ("R1","R2","R3"):
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION,"unsupported definition schema/release")
        if type(self.capabilities) is not Capabilities:
            raise ContractError(ErrorCode.INVALID_SCHEMA,"typed actual capabilities required")
        for rows,expected in ((self.requirements,InputRequirement),(self.outputs,OutputField)):
            if type(rows) not in (tuple,list) or not rows or any(type(x) is not expected for x in rows):
                raise ContractError(ErrorCode.INVALID_SCHEMA,"concrete nonempty typed schema metadata required")
        object.__setattr__(self,"requirements",tuple(self.requirements));object.__setattr__(self,"outputs",tuple(self.outputs))
        if len({x.role for x in self.requirements}) != len(self.requirements) or len({x.name for x in self.outputs})!=len(self.outputs):
            raise ContractError(ErrorCode.DUPLICATE,"duplicate input role/output field")
        if type(self.default_periods) not in (tuple,list) or any(type(x) is not int or not 1<=x<=I64_MAX for x in self.default_periods):
            raise ContractError(ErrorCode.INVALID_CONFIG,"positive concrete default periods required")
        object.__setattr__(self,"default_periods",tuple(self.default_periods))
        if len(set(self.default_periods))!=len(self.default_periods):
            raise ContractError(ErrorCode.DUPLICATE,"duplicate default period")

    def to_json(self) -> str:
        return json.dumps(asdict(self),sort_keys=True,separators=(",",":"),ensure_ascii=True)

    @classmethod
    def from_json(cls,text: str) -> FeatureDefinition:
        if type(text) is not str: raise ContractError(ErrorCode.INVALID_SCHEMA,"in-memory definition JSON required")
        try: return _decode(json.loads(text,object_pairs_hook=_unique))
        except ContractError: raise
        except (ValueError,TypeError,KeyError,AttributeError) as error:
            raise ContractError(ErrorCode.INVALID_SCHEMA,"invalid definition metadata") from error

def _text(value: str) -> None:
    if type(value) is not str or not value.strip():
        raise ContractError(ErrorCode.INVALID_SCHEMA,"nonempty metadata text required")

def _unique(pairs: list[tuple[str,Any]]) -> dict[str,Any]:
    result: dict[str,Any] = {}
    for key,value in pairs:
        if key in result: raise ContractError(ErrorCode.DUPLICATE,"duplicate metadata JSON key")
        result[key] = value
    return result

def _decode(raw: Any) -> FeatureDefinition:
    requirements = []
    for item in raw.pop("requirements"):
        kind = item.pop("kind")
        requirements.append(InputRequirement(kind=DataKind(kind) if kind is not None else None,**item))
    outputs = tuple(OutputField(**x) for x in raw.pop("outputs"))
    capabilities = Capabilities(**raw.pop("capabilities"))
    return FeatureDefinition(requirements=tuple(requirements),outputs=outputs,capabilities=capabilities,**raw)

from ._catalog import CATALOG_ROWS
_BUILTINS = tuple(FeatureDefinition.from_json(row) for row in CATALOG_ROWS)
_BUILTIN_IDS = frozenset(x.feature_id for x in _BUILTINS)
_BUILTIN_DIGEST = hashlib.sha256("".join(x.to_json() for x in _BUILTINS).encode()).hexdigest()

@dataclass(frozen=True)
class Registry:
    namespace: str = "caller"
    custom: tuple[FeatureDefinition, ...] = ()

    def __post_init__(self) -> None:
        if type(self.namespace) is not str or re.fullmatch("[a-z][a-z0-9_]{0,31}",self.namespace) is None:
            raise ContractError(ErrorCode.INVALID_CONFIG,"lowercase caller namespace required")
        if type(self.custom) not in (tuple,list) or any(type(x) is not FeatureDefinition for x in self.custom):
            raise ContractError(ErrorCode.INVALID_SCHEMA,"concrete typed custom definitions required")
        object.__setattr__(self,"custom",tuple(sorted(self.custom,key=lambda x:x.feature_id)))
        if len({x.feature_id for x in self.custom})!=len(self.custom): raise ContractError(ErrorCode.DUPLICATE,"duplicate custom ID")
        for definition in self.custom:
            if definition.feature_id in _BUILTIN_IDS:
                raise ContractError(ErrorCode.DUPLICATE,"reserved built-in ID cannot be overwritten")
            if re.fullmatch(re.escape(self.namespace)+":[a-z][a-z0-9_.]{0,63}",definition.feature_id) is None:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY,"custom ID must use this caller namespace")

    def list_features(self, *, family: str | None = None, capability: str | None = None) -> tuple[FeatureDefinition, ...]:
        if capability not in (None,"batch","update","restore","merge"):
            raise ContractError(ErrorCode.INVALID_CONFIG,"unknown capability mode")
        definitions = _BUILTINS+self.custom
        if family is not None:
            _text(family)
            definitions = tuple(x for x in definitions if x.feature_id.startswith((family+".",family+":")))
        # Actual execution flags are all false under the R0 metadata-only contract.
        return () if capability is not None else definitions

    def get(self,feature_id: str) -> FeatureDefinition:
        _text(feature_id)
        for definition in _BUILTINS+self.custom:
            if definition.feature_id == feature_id: return definition
        raise ContractError(ErrorCode.UNKNOWN_FEATURE,"unknown feature ID")

    def with_definition(self,definition: FeatureDefinition) -> Registry:
        return replace(self,custom=self.custom+(definition,))

    def require_capability(self,feature_id: str,mode: str) -> None:
        self.get(feature_id)
        if mode not in ("batch","update","restore","merge"):
            raise ContractError(ErrorCode.INVALID_CONFIG,"unknown capability mode")
        raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY,"R0 defines metadata; numerical/custom execution is not implemented")

    def to_json(self) -> str:
        return json.dumps({"schema_version":"1","builtin_scope_version":"1","builtin_digest":_BUILTIN_DIGEST,"namespace":self.namespace,"custom":[asdict(x) for x in self.custom]},sort_keys=True,separators=(",",":"),ensure_ascii=True)

    @classmethod
    def from_json(cls,text: str) -> Registry:
        if type(text) is not str: raise ContractError(ErrorCode.INVALID_SCHEMA,"in-memory registry JSON required")
        try:
            raw = json.loads(text,object_pairs_hook=_unique)
            if set(raw)!={"schema_version","builtin_scope_version","builtin_digest","namespace","custom"}:
                raise ContractError(ErrorCode.INVALID_SCHEMA,"unknown/missing registry metadata field")
            if raw["schema_version"]!="1" or raw["builtin_scope_version"]!="1" or raw["builtin_digest"]!=_BUILTIN_DIGEST:
                raise ContractError(ErrorCode.INCOMPATIBLE_VERSION,"incompatible registry/definition snapshot")
            return cls(raw["namespace"],tuple(_decode(x) for x in raw["custom"]))
        except ContractError: raise
        except (ValueError,TypeError,KeyError,AttributeError) as error:
            raise ContractError(ErrorCode.INVALID_SCHEMA,"invalid registry metadata") from error

def builtin_registry() -> Registry:
    return Registry()
