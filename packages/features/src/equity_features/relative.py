"""Arithmetic comparisons of compatible supplied return dependencies."""
from __future__ import annotations
from dataclasses import replace
from typing import cast
from equity_feature_contracts import (
    BatchMetadata, ClassificationAdmission, ConfigSpec, ContractError, Coverage, DataKind,
    EntityKey, ErrorCode, EvidenceRow, FeatureColumn, FeatureResult, InputBinding,
    QualityRow, Reason, ResultMetadata, SourceBinding, Status, ValueType,
)
from equity_feature_contracts.relative import RelativeSpec, ReturnReference, _configuration
from . import __version__
from .volume import _add

_IDS = ("relative.market_return", "relative.sector_return")


def _binding(role: str, digest: str, config: ConfigSpec) -> InputBinding:
    return InputBinding(role, DataKind.REFERENCE, BatchMetadata(config.session.namespace,
                        SourceBinding("caller-supplied-relative", "schema1", "relative-reference-v1", digest),
                        Coverage(1, 1, True), None))


def _admit(reference: ReturnReference, entity: EntityKey, config: ConfigSpec, symbol: bool) -> None:
    if type(reference) is not ReturnReference:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "owned return dependency required")
    cfg = reference.config
    period, _ = _configuration(config)
    other_period, _ = _configuration(cfg)
    if reference.context.entity != entity or cfg.session != config.session or cfg.session.namespace != config.session.namespace or cfg.window.governed_sessions != config.window.governed_sessions or cfg.window.selected_sessions() != config.window.selected_sessions() or period != other_period or cfg.availability != config.availability:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "return entity/calendar/horizon/cutoff alignment required")
    if cfg.price_unit != config.price_unit:
        raise ContractError(ErrorCode.INVALID_UNIT, "return scale/currency alignment required")
    left, right = cfg.adjustment, config.adjustment
    if (left.basis, left.policy_version, left.anchor) != (right.basis, right.policy_version, right.anchor) or (symbol and left != right):
        raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "return adjustment policy/anchor alignment required")
    if reference.result.metadata.backend_version != __version__:
        raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "return backend version requires caller rebuild")


def compute_relative(symbol: ReturnReference | None, market: ReturnReference | None,
                     sector: ReturnReference | None, membership: ClassificationAdmission | None,
                     config: ConfigSpec, *, spec: RelativeSpec, feature_ids: tuple[str, ...]) -> FeatureResult:
    """Requested market/sector differences only; never calculate a missing return."""
    _, limit = _configuration(config)
    if type(spec) is not RelativeSpec or spec.entity.session_id != config.session.session_id:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "typed relative specification must match target")
    if type(feature_ids) not in (tuple, list) or not feature_ids or any(type(x) is not str or x not in _IDS for x in feature_ids):
        raise ContractError(ErrorCode.UNSUPPORTED_CAPABILITY, "implemented relative batch IDs only")
    if len(set(feature_ids)) != len(feature_ids):
        raise ContractError(ErrorCode.DUPLICATE, "duplicate relative request")
    inputs = [_binding("relative_spec", spec.identity_digest, config)]
    columns: list[FeatureColumn] = []
    qualities: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    seen_evidence: dict[tuple[str, str, str], EvidenceRow] = {}
    frames: dict[str, str] = {}
    admitted: dict[str, ReturnReference] = {}

    def retain(role: str, reference: ReturnReference) -> None:
        if role in admitted:
            return
        for b in reference.result.metadata.inputs:
            if b.kind == DataKind.DAILY:
                key = b.metadata.source.input_id
                owner = reference.context.entity.instrument_id
                if key in frames and frames[key] != owner:
                    raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "distinct-instrument normalized daily frames need distinct IDs")
                frames[key] = owner
            _add(inputs, replace(b, role=role+"."+b.role))
        _add(inputs, _binding(role+"_return_reference", reference.identity_digest, config))
        admitted[role] = reference

    if symbol is not None:
        _admit(symbol, spec.entity, config, True)
        retain("symbol", symbol)

    def borrow(row: EvidenceRow, feature_id: str) -> None:
        mapped = replace(row, entity=spec.entity, feature_id=feature_id)
        key = (mapped.feature_id, mapped.input_id, mapped.row_id)
        same = seen_evidence.get(key)
        if same is not None:
            if same != mapped:
                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "conflicting original-row evidence")
        else:
            seen_evidence[key] = mapped
            if len(evidence) < limit:
                evidence.append(mapped)

    for feature_id in feature_ids:
        is_sector = feature_id == "relative.sector_return"
        benchmark = sector if is_sector else market
        expected_entity = spec.sector_benchmark.entity if is_sector and spec.sector_benchmark is not None else spec.market_benchmark if not is_sector else None
        status = Status.AVAILABLE
        reasons: list[Reason] = []
        observed = 0
        pair = (("symbol", symbol), ("sector" if is_sector else "market", benchmark))
        if benchmark is not None:
            if expected_entity is None:
                raise ContractError(ErrorCode.INVALID_CONFIG, "supplied benchmark requires explicit expected identity")
            _admit(benchmark, expected_entity, config, False)
            if symbol is not None:
                selected = set(config.window.selected_sessions())
                lhs = tuple(s for s in symbol.context.sessions if s.session_id in selected)
                rhs = tuple(s for s in benchmark.context.sessions if s.session_id in selected)
                if symbol.context.grid_version != benchmark.context.grid_version or lhs != rhs:
                    raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "exact selected endpoint grid alignment required")
            retain("sector" if is_sector else "market", benchmark)
        for _, reference in pair:
            if reference is None:
                if status == Status.AVAILABLE:
                    status = Status.MISSING_INPUT
                reasons.append(Reason.ABSENT_INPUT)
            else:
                q = reference.result.quality[0]
                if q.status == Status.AVAILABLE:
                    observed += 1
                else:
                    if status == Status.AVAILABLE:
                        status = q.status
                    reasons.extend(q.reasons)
                for e in reference.result.evidence:
                    borrow(e, feature_id)
        if is_sector:
            point = spec.membership_effective_ns
            if spec.sector_benchmark is not None and (point is None or not config.session.open_ns <= point < config.session.close_ns or point > config.availability.market_cutoff_ns):
                raise ContractError(ErrorCode.INVALID_CONFIG, "explicit membership point inside target and <=C required")
            if membership is None or spec.sector_benchmark is None:
                if membership is not None:
                    raise ContractError(ErrorCode.INVALID_CONFIG, "membership requires explicit sector mapping")
                if status == Status.AVAILABLE:
                    status = Status.MISSING_INPUT
                reasons.append(Reason.ABSENT_INPUT)
            else:
                if type(membership) is not ClassificationAdmission or membership.entity != spec.entity or membership.fact_kind != "sector_membership" or membership.effective_ns != point or membership.config_digest != config.digest or membership.availability != config.availability:
                    raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "sector membership entity/point/config/timing mismatch")
                if membership.reference is not None:
                    _add(inputs, replace(membership.reference, role="membership."+membership.reference.role))
                _add(inputs, _binding("membership_admission", membership.identity_digest, config))
                if membership.status == Status.AVAILABLE:
                    if membership.text != spec.sector_benchmark.sector_id:
                        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "membership sector ID differs from explicit benchmark mapping")
                    observed += 1
                else:
                    if status == Status.AVAILABLE:
                        status = membership.status
                    reasons.extend(membership.reasons)
                if membership.reference is not None:
                    for f in membership.facts:
                        borrow(EvidenceRow(spec.entity, feature_id, membership.reference.metadata.source.input_id,
                                           str(f.row_index), f.effective_start_ns, f.known_at_ns,
                                           f.effective_start_ns, f.effective_end_ns,
                                           "consumed" if membership.status == Status.AVAILABLE else "excluded",
                                           None if membership.status == Status.AVAILABLE else membership.reasons[0]), feature_id)
        value = None
        if status == Status.AVAILABLE:
            value = cast(float, cast(ReturnReference, symbol).result.values[0].values[0])-cast(float, cast(ReturnReference, benchmark).result.values[0].values[0])
        columns.append(FeatureColumn(feature_id, "v1", ValueType.FLOAT64, "fraction", (spec.entity,), (value,)))
        qualities.append(QualityRow(spec.entity, feature_id, status, 3 if is_sector else 2, observed, tuple(dict.fromkeys(reasons))))
    return FeatureResult(tuple(columns), tuple(qualities),
                         ResultMetadata(config.session.namespace, config.session.session_id, config.availability,
                                        config.digest, tuple(inputs), "python-exact", __version__, limit), tuple(evidence))
