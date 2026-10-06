"""Owned supplied-result collections; no dependency execution or source access."""
from __future__ import annotations
from dataclasses import asdict, dataclass
import hashlib
import json
from typing import TypeAlias

from .breadth import BreadthResult, SMAInput
from .buckets import BucketContext, IntervalBaseline
from .errors import ContractError, ErrorCode
from .history import HistoryContext, SMAReference
from .inputs import DataKind
from .registry import builtin_registry
from .relative import ReturnReference
from .results import FeatureResult, InputBinding, ValueType
from .specs import AvailabilitySpec, ConfigSpec, SessionSpec
from .volume import VolumeBaseline

ResultCompanion: TypeAlias = SMAReference | VolumeBaseline | IntervalBaseline | ReturnReference | BreadthResult
ComponentContext: TypeAlias = HistoryContext | BucketContext
_QUOTES = frozenset(("session.quote.sampled_spread", "session.quote.state_counts", "session.quote.time_weighted_spread"))


def _digest(value: object) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=True, allow_nan=False).encode()).hexdigest()


def _labels(values: tuple[str, ...]) -> None:
    if type(values) not in (tuple, list) or any(type(v) is not str or not v.strip() for v in values):
        raise ContractError(ErrorCode.INVALID_CONFIG, "concrete nonempty instance identities required")
    if len(set(values)) != len(values):
        raise ContractError(ErrorCode.DUPLICATE, "duplicate instance identity")


@dataclass(frozen=True)
class FamilyResult:
    instance_id: str
    result: FeatureResult
    config: ConfigSpec
    context: ComponentContext | None = None
    companion: ResultCompanion | None = None
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported component schema")
        _labels((self.instance_id,))
        if type(self.result) is not FeatureResult or type(self.config) is not ConfigSpec:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned result and config required")
        if self.context is not None and type(self.context) not in (HistoryContext, BucketContext):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned history or bucket context required")
        if self.companion is not None:
            if type(self.companion) not in (SMAReference, VolumeBaseline, IntervalBaseline, ReturnReference, BreadthResult):
                raise ContractError(ErrorCode.INVALID_SCHEMA, "owned typed result companion required")
            if self.companion.result != self.result:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "companion/result mismatch")
            if isinstance(self.companion, (VolumeBaseline, IntervalBaseline, ReturnReference)):
                if self.companion.config != self.config or (self.context is not None and self.companion.context != self.context):
                    raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "companion config/context mismatch")
        r, cfg = self.result, self.config
        m = r.metadata
        if cfg.algorithm_version != "v1" or m.math_policy_version != "v1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "composition requires delivered v1 mathematics")
        if (m.config_digest, m.namespace, m.session_id, m.availability) != (cfg.digest, cfg.session.namespace, cfg.session.session_id, cfg.availability):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "component config/timing mismatch")
        if not r.values:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "nonempty supplied result required")
        ids = {c.feature_id for c in r.values}
        registry = builtin_registry()
        for col in r.values:
            definition = registry.get(col.feature_id)
            registry.require_capability(col.feature_id, "batch")
            if col.algorithm_version != definition.algorithm_version:
                raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "component algorithm mismatch")
            output = definition.outputs[0]
            dtype = ValueType(output.dtype)
            unit = output.unit
            if col.feature_id.startswith("history.") and unit == "currency/share":
                if cfg.price_unit is None:
                    raise ContractError(ErrorCode.INVALID_UNIT, "history price output requires explicit currency")
                unit = f"{cfg.price_unit.currency}/share"
            if col.dtype != dtype or col.unit != unit:
                raise ContractError(ErrorCode.INVALID_SCHEMA, "contradictory delivered builtin output schema")
            backend = "python-exact-compensated" if col.feature_id in _QUOTES else "python-exact"
            if m.backend_id != backend:
                raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unqualified feature/backend pairing")
        params = {p.name: p.value for p in cfg.parameters}
        limit = 1 if ids == {"session.quote.time_weighted_spread"} else params.get("observation_limit", 0) if ids <= _QUOTES else params.get("evidence_limit", 0)
        if type(limit) is not int or limit < 0 or m.evidence_limit != limit:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "component evidence bound mismatch")
        ctx = self.owned_context
        contexts = [b for b in m.inputs if b.role in ("history_context", "bucket_context")]
        needs_history = any(i.startswith("history.") or i == "baseline.daily_volume" for i in ids)
        needs_bucket = "baseline.interval_volume" in ids
        if (needs_history and type(ctx) is not HistoryContext) or (needs_bucket and type(ctx) is not BucketContext) or ((needs_history or needs_bucket) and not contexts):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "producer requires owned consumed context")
        if contexts:
            role = "bucket_context" if type(ctx) is BucketContext else "history_context"
            if ctx is None or len(contexts) != 1 or contexts[0].role != role or contexts[0].kind != DataKind.REFERENCE or contexts[0].metadata.source.input_id != ctx.identity_digest:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "exact consumed context required")
        if ctx is not None:
            if not contexts or cfg.window.governed_sessions != tuple(s.session_id for s in ctx.sessions) or cfg.session != next(s for s in ctx.sessions if s.session_id == ctx.entity.session_id):
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "component governed grid/target mismatch")
            if any(c.entities != (ctx.entity,) for c in r.values):
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "context/component entity mismatch")
        if type(self.companion) is SMAReference:
            if type(ctx) is not HistoryContext:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "SMA companion requires history context")
            SMAInput(self.companion, cfg, ctx)
        for binding in m.inputs:
            if (binding.role == "daily_history" and binding.kind != DataKind.DAILY) or (binding.role == "bucket_history" and binding.kind != DataKind.BAR):
                raise ContractError(ErrorCode.INVALID_SCHEMA, "direct normalized frame kind mismatch")
            if binding.role in ("bars", "trades", "quotes", "quote_seed", "prior_close", "daily_history", "bucket_history"):
                if binding.metadata.price_unit != cfg.price_unit:
                    raise ContractError(ErrorCode.INVALID_UNIT, "component source price unit mismatch")
                if binding.metadata.adjustment != cfg.adjustment:
                    raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "component source adjustment mismatch")

    @property
    def owned_context(self) -> ComponentContext | None:
        if self.context is not None:
            return self.context
        if isinstance(self.companion, (VolumeBaseline, IntervalBaseline, ReturnReference)):
            return self.companion.context
        return None


@dataclass(frozen=True)
class CompositionSpec:
    namespace: str
    session: SessionSpec
    availability: AvailabilitySpec
    instance_ids: tuple[str, ...]
    mode: str = "batch"
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported composition schema")
        if self.mode != "batch":
            raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY, "composition supports supplied batch results only")
        if type(self.session) is not SessionSpec or type(self.availability) is not AvailabilitySpec or self.namespace != self.session.namespace:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "composition namespace/session/timing required")
        _labels(self.instance_ids)
        object.__setattr__(self, "instance_ids", tuple(self.instance_ids))


@dataclass(frozen=True)
class FeatureBundle:
    spec: CompositionSpec
    components: tuple[FamilyResult, ...]
    missing_instances: tuple[str, ...]
    schema_version: str = "1"

    def __post_init__(self) -> None:
        if self.schema_version != "1":
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "unsupported bundle schema")
        if type(self.spec) is not CompositionSpec or type(self.components) not in (tuple, list) or any(type(c) is not FamilyResult for c in self.components):
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned composition and concrete components required")
        object.__setattr__(self, "components", tuple(self.components))
        _labels(self.missing_instances)
        object.__setattr__(self, "missing_instances", tuple(self.missing_instances))
        ids = tuple(c.instance_id for c in self.components)
        _labels(ids)
        if any(i not in self.spec.instance_ids for i in ids):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "undeclared component")
        if ids != tuple(i for i in self.spec.instance_ids if i in ids) or self.missing_instances != tuple(i for i in self.spec.instance_ids if i not in ids):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "exact declared ordering and missing instances required")
        sources: dict[str, InputBinding] = {}
        owners: dict[str, tuple[str, ...]] = {}
        buckets: dict[str, str] = {}
        proofs: dict[tuple[str, str], tuple[int, int | None]] = {}
        for component in self.components:
            cfg, m, ctx = component.config, component.result.metadata, component.owned_context
            if cfg.session != self.spec.session or cfg.availability != self.spec.availability or m.namespace != self.spec.namespace:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "bundle target/timing mismatch")
            session_output = all(col.feature_id.startswith("session.") for col in component.result.values)
            population = tuple(sorted({entity.instrument_id for col in component.result.values for entity in col.entities}))
            for binding in m.inputs:
                key = binding.metadata.source.input_id
                previous = sources.get(key)
                if previous is not None and (previous.kind != binding.kind or previous.metadata != binding.metadata):
                    raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "contradictory shared original source identity")
                sources[key] = binding
                if binding.role in ("daily_history", "bucket_history"):
                    if ctx is None or (binding.role == "bucket_history" and type(ctx) is not BucketContext):
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "direct normalized frame needs owned context")
                    owner = (ctx.entity.instrument_id,)
                    if key in owners and owners[key] != owner:
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "contradictory normalized frame ownership")
                    owners[key] = owner
                    if binding.role == "bucket_history" and isinstance(ctx, BucketContext):
                        bucket = _digest(asdict(ctx.bucket))
                        if key in buckets and buckets[key] != bucket:
                            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "contradictory normalized bucket scope")
                        buckets[key] = bucket
                elif session_output and binding.kind != DataKind.REFERENCE:
                    if not population:
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "direct session frame requires declared instrument population")
                    if key in owners and owners[key] != population:
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "contradictory direct session frame ownership")
                    owners[key] = population
            for row in component.result.evidence:
                key_row = (row.input_id, row.row_id)
                original = (row.event_ns, row.known_at_ns)
                if key_row in proofs and proofs[key_row] != original:
                    raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "contradictory original row timing proof")
                proofs[key_row] = original

    @property
    def identity_digest(self) -> str:
        return _digest(asdict(self))
