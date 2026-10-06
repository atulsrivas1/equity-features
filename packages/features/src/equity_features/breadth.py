"""Pure aggregation of explicitly supplied compatible member results."""
from __future__ import annotations
from dataclasses import replace
from typing import cast
from equity_feature_contracts import (
    BatchMetadata, BreadthCounts, BreadthFraction, ConfigSpec, ContractError, Coverage,
    DataKind, EntityKey, ErrorCode, EvidenceRow, FeatureColumn, InputBinding, QualityRow, HistoryContext,
    Reason, ResultCell, ResultMetadata, SourceBinding, Status, ValueType, FeatureResult,
)
from equity_feature_contracts.breadth import (
    BreadthResult, BreadthSpec, DeclaredUniverseSpec, MemberExclusion, MemberFeatures,
    _configuration,
)
from . import __version__
from .volume import _add


def _definition(role: str, digest: str, config: ConfigSpec) -> InputBinding:
    return InputBinding(role, DataKind.REFERENCE, BatchMetadata(config.session.namespace,
                        SourceBinding("caller-supplied-breadth", "schema1", "breadth-reference-v1", digest), Coverage(1, 1, True), None))


def _compute(members: tuple[MemberFeatures, ...] | None, config: ConfigSpec, universe: DeclaredUniverseSpec | None, spec: BreadthSpec, direction: bool) -> BreadthResult:
    n, limit = _configuration(config, direction)
    fid = "breadth.direction_counts" if direction else "breadth.above_sma_fraction"
    if type(spec) is not BreadthSpec or spec.entity.session_id != config.session.session_id:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "aggregate target must match breadth config")
    if members is not None and (type(members) not in (tuple, list) or any(type(x) is not MemberFeatures for x in members)):
        raise ContractError(ErrorCode.INVALID_SCHEMA, "owned concrete member results required")
    supplied = tuple(members or ())
    if len({x.entity.instrument_id for x in supplied}) != len(supplied):
        raise ContractError(ErrorCode.DUPLICATE, "duplicate supplied universe member")
    if any(x.entity.session_id != spec.entity.session_id for x in supplied):
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "member target mismatch")
    inputs: list[InputBinding] = [_definition("breadth_spec", spec.identity_digest, config)]
    evidence: list[EvidenceRow] = []
    exclusions: list[MemberExclusion] = []
    proofs: dict[tuple[str, str], EvidenceRow] = {}
    frames: dict[str, str] = {}
    selected_grid: object = None
    expected: int | None = None
    eligible = advancing = declining = unchanged = above = 0
    status = Status.MISSING_INPUT
    reasons: tuple[Reason, ...] = (Reason.ABSENT_INPUT,)

    def retain(entity: EntityKey, bindings: tuple[InputBinding, ...], role: str, digest: str) -> None:
        for b in bindings:
            if b.kind == DataKind.DAILY:
                key = b.metadata.source.input_id
                if key in frames and frames[key] != entity.instrument_id:
                    raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "distinct member daily frames require distinct IDs")
                frames[key] = entity.instrument_id
            _add(inputs, replace(b, role=entity.instrument_id+"."+role+"."+b.role))
        _add(inputs, _definition(entity.instrument_id+"."+role+"_identity", digest, config))

    def borrow(e: EvidenceRow) -> None:
        e = replace(e, entity=spec.entity, feature_id=fid)
        key = e.input_id, e.row_id
        if key in proofs and proofs[key] != e:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "conflicting supplied original-row proof")
        if key not in proofs:
            proofs[key] = e
            if len(evidence) < limit:
                evidence.append(e)

    def align(cfg: ConfigSpec, context: HistoryContext, result: FeatureResult) -> None:
        nonlocal selected_grid
        other_n, _ = _configuration(cfg, direction)
        if cfg.session != config.session or cfg.window.governed_sessions != config.window.governed_sessions or cfg.window.selected_sessions() != config.window.selected_sessions() or other_n != n or cfg.availability != config.availability:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "member horizon/grid/config/C-K-E mismatch")
        if cfg.price_unit != config.price_unit:
            raise ContractError(ErrorCode.INVALID_UNIT, "member currency/scale mismatch")
        a, b = cfg.adjustment, config.adjustment
        if (a.basis, a.policy_version, a.anchor) != (b.basis, b.policy_version, b.anchor):
            raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "member adjustment policy/anchor mismatch")
        if result.metadata.backend_version != __version__:
            raise ContractError(ErrorCode.INCOMPATIBLE_VERSION, "member backend requires caller rebuild")
        ctx = context
        ids = set(config.window.selected_sessions())
        grid = (ctx.grid_version, tuple(s for s in ctx.sessions if s.session_id in ids))
        if selected_grid is not None and selected_grid != grid:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "exact selected member grids must align")
        selected_grid = grid

    if universe is not None:
        if type(universe) is not DeclaredUniverseSpec or universe.namespace != config.session.namespace or universe.session_id != config.session.session_id or not config.session.open_ns <= universe.effective_ns < config.session.close_ns or universe.effective_ns > config.availability.market_cutoff_ns:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "declared universe namespace/target/evaluation mismatch")
        if any(x.entity.instrument_id not in universe.members for x in supplied):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "extra supplied universe member")
        inputs.append(_definition("declared_universe", universe.identity_digest, config))
        expected = len(universe.members)
        if not expected:
            status, reasons = Status.NOT_APPLICABLE, (Reason.EMPTY_UNIVERSE,)
        elif members is not None:
            by_id = {x.entity.instrument_id: x for x in supplied}
            for instrument in universe.members:
                entity = EntityKey(instrument, spec.entity.session_id)
                member = by_id.get(instrument)
                qstatus = Status.MISSING_INPUT
                qreasons: tuple[Reason, ...] = (Reason.ABSENT_INPUT,)
                value: float | None = None
                is_above: bool | None = None
                if member is not None:
                    if direction and member.return_reference is not None:
                        ref = member.return_reference
                        align(ref.config, ref.context, ref.result)
                        retain(entity, ref.result.metadata.inputs, "return", ref.identity_digest)
                        for e in ref.result.evidence:
                            borrow(e)
                        q = ref.result.quality[0]
                        qstatus, qreasons = q.status, q.reasons
                        if qstatus == Status.AVAILABLE:
                            value = cast(float, ref.result.values[0].values[0])
                    elif not direction:
                        sma, close = member.sma, member.close
                        ready = 0
                        if sma is not None:
                            align(sma.config, sma.context, sma.reference.result)
                            retain(entity, sma.reference.result.metadata.inputs, "sma", sma.identity_digest)
                            for e in sma.reference.result.evidence:
                                borrow(e)
                            q = sma.reference.result.quality[0]
                            qstatus, qreasons = q.status, q.reasons
                            ready += qstatus == Status.AVAILABLE
                        if close is not None:
                            m = close.source.metadata
                            if m.namespace != config.session.namespace or m.price_unit != config.price_unit:
                                raise ContractError(ErrorCode.INVALID_UNIT, "completed close namespace/unit mismatch")
                            a, b = m.adjustment, config.adjustment
                            if (a.basis, a.policy_version, a.anchor) != (b.basis, b.policy_version, b.anchor) or (sma is not None and a != sma.config.adjustment):
                                raise ContractError(ErrorCode.UNSUPPORTED_ADJUSTMENT, "close/SMA actual basis mismatch")
                            if (close.interval.start_ns, close.interval.end_ns) != (config.session.open_ns, config.session.close_ns) or close.interval.include_opening_auction != config.session.include_opening_auction or close.interval.include_closing_auction != config.session.include_closing_auction:
                                raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "completed close requires exact actual full session")
                            retain(entity, (close.source,), "close", close.identity_digest)
                            cs = Status.AVAILABLE
                            cr: tuple[Reason, ...] = ()
                            if close.coefficient is None:
                                cs, cr = Status.MISSING_INPUT, (Reason.NULL_FIELD,)
                            elif config.session.close_ns > config.availability.market_cutoff_ns:
                                cs, cr = Status.INCOMPLETE_COVERAGE, (Reason.FUTURE_MARKET,)
                            elif not close.coverage.complete:
                                cs, cr = Status.INCOMPLETE_COVERAGE, (Reason.GOVERNED_GAP,)
                            elif config.availability.knowledge_reason(close.known_at_ns) is not None:
                                cs = Status.MISSING_INPUT
                                cr = (Reason(cast(str, config.availability.knowledge_reason(close.known_at_ns))),)
                            ready += cs == Status.AVAILABLE
                            if qstatus == Status.AVAILABLE or sma is None:
                                qstatus, qreasons = cs, cr
                            borrow(EvidenceRow(entity, fid, m.source.input_id, str(close.row_index), config.session.close_ns, close.known_at_ns,
                                               close.interval.start_ns, close.interval.end_ns, "consumed" if cs == Status.AVAILABLE else "excluded", None if cs == Status.AVAILABLE else cr[0], "completed_interval"))
                        if ready == 2:
                            assert sma is not None and close is not None and config.price_unit is not None
                            is_above = sma.reference.compare_price(cast(int, close.coefficient), config.price_unit) > 0
                            qstatus, qreasons = Status.AVAILABLE, ()
                        elif sma is None or close is None:
                            qstatus, qreasons = Status.MISSING_INPUT, (Reason.ABSENT_INPUT,)
                if qstatus == Status.AVAILABLE:
                    eligible += 1
                    if direction:
                        advancing += cast(float, value) > 0
                        declining += cast(float, value) < 0
                        unchanged += cast(float, value) == 0
                    else:
                        above += bool(is_above)
                else:
                    exclusions.append(MemberExclusion(entity, fid, qstatus, qreasons))
            status = Status.AVAILABLE if eligible == expected else Status.INCOMPLETE_COVERAGE
            reasons = () if status == Status.AVAILABLE else (Reason.PARTIAL_UNIVERSE,)
    cell: ResultCell = None
    if eligible:
        cell = BreadthCounts(advancing, declining, unchanged, cast(int, expected)) if direction else BreadthFraction(above, eligible, cast(int, expected))
    result = FeatureResult((FeatureColumn(fid, "v1", ValueType.BREADTH_COUNTS if direction else ValueType.BREADTH_FRACTION, "members" if direction else "fraction", (spec.entity,), (cell,)),),
                           (QualityRow(spec.entity, fid, status, expected, eligible, reasons),),
                           ResultMetadata(config.session.namespace, config.session.session_id, config.availability, config.digest, tuple(inputs), "python-exact", __version__, limit), tuple(evidence))
    return BreadthResult(result, tuple(exclusions))


def compute_direction_breadth(members: tuple[MemberFeatures, ...] | None, config: ConfigSpec, *, universe: DeclaredUniverseSpec | None, spec: BreadthSpec) -> BreadthResult:
    """Count exact supplied positive/negative/zero returns in declared U."""
    return _compute(members, config, universe, spec, True)


def compute_above_sma_breadth(members: tuple[MemberFeatures, ...] | None, config: ConfigSpec, *, universe: DeclaredUniverseSpec | None, spec: BreadthSpec) -> BreadthResult:
    """Compare completed closes to supplied exact SMA witnesses; never recalculate."""
    return _compute(members, config, universe, spec, False)
