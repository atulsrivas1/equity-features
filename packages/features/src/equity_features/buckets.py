"""Independent individual-bucket baselines; supplied quantities only."""
from __future__ import annotations
from fractions import Fraction
from typing import cast
from equity_feature_contracts import (
    BatchMetadata, CanonicalBatch, Column, ConfigSpec, ContractError, Coverage, DataKind,
    ErrorCode, EvidenceRow, FeatureColumn, FeatureResult, InputBinding, QualityRow,
    Reason, ResultMetadata, SourceBinding, Status, ValueType, checked_decimal128, validate_batch,
)
from equity_feature_contracts.buckets import BucketContext, BucketVolume, IntervalBaseline, _configuration
from . import __version__
from .volume import _add, _identity_binding, _retain_proof


def _context(config: ConfigSpec, context: BucketContext) -> InputBinding:
    return InputBinding("bucket_context", DataKind.REFERENCE,
                        BatchMetadata(config.session.namespace, SourceBinding("caller-bucket-context", context.grid_version,
                                      "bucket-context-v1", context.identity_digest),
                                      Coverage(len(context.sessions), len(context.sessions), True), None))


def _rows(batch: CanonicalBatch | None, config: ConfigSpec, context: BucketContext) -> dict[str, int]:
    if batch is None:
        return {}
    if type(batch) is not CanonicalBatch or batch.kind != DataKind.BAR:
        raise ContractError(ErrorCode.INVALID_SCHEMA, "owned individual bucket BAR rows required")
    if batch.metadata.namespace != config.session.namespace or batch.metadata.adjustment != config.adjustment:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "bucket source namespace/basis mismatch")
    if batch.metadata.price_unit != config.price_unit:
        raise ContractError(ErrorCode.INVALID_UNIT, "bucket source price metadata mismatch")
    if batch.metadata.coverage.observed != batch.row_count:
        raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "bucket actual frame count mismatch")
    validate_batch(batch, required_fields=())
    fields = {c.name: c.values for c in batch.columns}
    grid = {s.session_id: (i, s) for i, s in enumerate(context.sessions)}
    result: dict[str, int] = {}
    previous = -1
    for index in range(batch.row_count):
        sid = cast(str, fields["session_id"][index])
        if fields["instrument_id"][index] != context.entity.instrument_id or sid not in grid:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "bucket row outside declared instrument/grid")
        position, session = grid[sid]
        if position <= previous:
            raise ContractError(ErrorCode.INVALID_ORDER, "one row per ordered bucket slot required")
        start, end = context.bucket.bounds(session)
        if end > session.close_ns or (fields["start_ns"][index], fields["end_ns"][index]) != (start, end):
            raise ContractError(ErrorCode.BOUNDS, "exact eligible whole historical bucket required")
        scope = batch.metadata.scope
        if scope is not None and (start < scope.start_ns or end > scope.end_ns):
            raise ContractError(ErrorCode.BOUNDS, "bucket row outside declared original scope")
        result[sid] = index
        previous = position
    for session, certificate in zip(context.sessions, context.slot_coverage, strict=True):
        if certificate.observed != int(session.session_id in result):
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "bucket certificate contradicts row presence")
    return result


def _result(feature: str, value: float | None, status: Status, reasons: list[Reason], expected: int,
            observed: int, config: ConfigSpec, context: BucketContext, inputs: list[InputBinding],
            evidence: list[EvidenceRow], limit: int) -> FeatureResult:
    return FeatureResult((FeatureColumn(feature, "v1", ValueType.FLOAT64,
                                         "shares" if feature == "baseline.interval_volume" else "fraction",
                                         (context.entity,), (value,)),),
                         (QualityRow(context.entity, feature, status, expected, observed, tuple(dict.fromkeys(reasons))),),
                         ResultMetadata(config.session.namespace, context.entity.session_id, config.availability,
                                        config.digest, tuple(inputs), "python-exact", __version__, limit), tuple(evidence))


def compute_interval_baseline(batch: CanonicalBatch | None, config: ConfigSpec, *, context: BucketContext) -> IntervalBaseline:
    """Mean of exactly N required prior whole buckets; early-close absence is not0."""
    period, limit, basis = _configuration(config, context)
    rows = _rows(batch, config, context)
    slots = {s.session_id: (s, c) for s, c in zip(context.sessions, context.slot_coverage, strict=True)}
    volume = batch.column("volume") if batch is not None else None
    known = batch.column("known_at_ns") if batch is not None else None
    inputs = [_context(config, context)]
    if batch is not None:
        inputs.append(InputBinding("bucket_history", DataKind.BAR, batch.metadata))
    action = context.action_admission
    if action is not None and action.reference is not None:
        inputs.append(action.reference)
    values: list[int] = []
    reasons: list[Reason] = []
    evidence: list[EvidenceRow] = []
    for sid in config.window.selected_sessions():
        session, certificate = slots[sid]
        start, end = context.bucket.bounds(session)
        row = rows.get(sid)
        knowledge = cast(int | None, known.values[row]) if known is not None and row is not None else None
        reason = None
        if end > session.close_ns:
            reason = Reason.INELIGIBLE
        elif row is None or not certificate.complete:
            reason = Reason.GOVERNED_GAP
        elif end > config.availability.market_cutoff_ns:
            reason = Reason.FUTURE_MARKET
        elif (kr := config.availability.knowledge_reason(knowledge)) is not None:
            reason = Reason(kr)
        elif volume is None:
            reason = Reason.ABSENT_INPUT
        elif volume.values[row] is None:
            reason = Reason.NULL_FIELD
        if reason is None:
            values.append(cast(int, cast(Column, volume).values[cast(int, row)]))
        else:
            reasons.append(reason)
        if batch is not None and row is not None and len(evidence) < limit:
            evidence.append(EvidenceRow(context.entity, "baseline.interval_volume", batch.metadata.source.input_id,
                                        str(row), end, knowledge, start, end,
                                        "consumed" if reason is None else "excluded", reason, "completed_interval"))
    status = Status.AVAILABLE
    if batch is None or volume is None:
        status = Status.MISSING_INPUT
        reasons.append(Reason.ABSENT_INPUT)
    elif not config.window.history_complete:
        status = Status.INSUFFICIENT_HISTORY
        reasons.append(Reason.INSUFFICIENT_HISTORY)
    elif any(r in (Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE) for r in reasons):
        status = Status.MISSING_INPUT
    elif reasons:
        status = Status.INCOMPLETE_COVERAGE
    if action is not None and action.status != Status.AVAILABLE:
        status = action.status
        reasons.extend(action.reasons)
    numerator = checked_decimal128(sum(values)) if status == Status.AVAILABLE else None
    value = float(Fraction(numerator, period)) if numerator is not None else None
    return IntervalBaseline(_result("baseline.interval_volume", value, status, reasons, period, len(values),
                                   config, context, inputs, evidence, limit), config, context,
                            numerator, period if numerator is not None else None, basis)


def compute_interval_relative_volume(target: BucketVolume | None, baseline: IntervalBaseline | None,
                                     config: ConfigSpec, *, context: BucketContext) -> FeatureResult:
    """Consume the matching supplied mean and target bucket without aggregation."""
    _, limit, basis = _configuration(config, context)
    inputs = [_context(config, context)]
    status = Status.AVAILABLE
    reasons: list[Reason] = []
    evidence: list[EvidenceRow] = []
    proofs: dict[tuple[str, str], EvidenceRow] = {}
    observed = 0
    if baseline is None:
        status = Status.MISSING_INPUT
        reasons.append(Reason.ABSENT_INPUT)
    else:
        if type(baseline) is not IntervalBaseline:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned interval baseline required")
        if baseline.config != config or baseline.context != context or baseline.quantity_basis != basis or baseline.result.metadata.backend_id != "python-exact" or baseline.result.metadata.backend_version != __version__:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "interval dependency/config/context/version mismatch")
        for binding in baseline.result.metadata.inputs:
            _add(inputs, binding)
        _add(inputs, _identity_binding("interval_baseline_reference", baseline.identity_digest, config))
        q = baseline.result.quality[0]
        if q.status != Status.AVAILABLE:
            status = q.status
            reasons.extend(q.reasons)
        else:
            observed += 1
        for e in baseline.result.evidence:
            _retain_proof(evidence, proofs, EvidenceRow(e.entity, "baseline.interval_relative_volume", e.input_id, e.row_id,
                                        e.event_ns, e.known_at_ns, e.effective_start_ns, e.effective_end_ns,
                                        e.use, e.exclusion_reason, e.boundary), limit)
    start, end = context.bucket.bounds(config.session)
    reason = Reason.INELIGIBLE if end > config.session.close_ns else None
    if target is None:
        reason = reason or Reason.ABSENT_INPUT
    else:
        if type(target) is not BucketVolume:
            raise ContractError(ErrorCode.INVALID_SCHEMA, "owned target bucket volume required")
        if target.entity != context.entity or target.bucket != context.bucket or target.quantity_basis != basis or target.source.metadata.namespace != config.session.namespace or target.source.metadata.price_unit != config.price_unit or target.source.metadata.adjustment != config.adjustment:
            raise ContractError(ErrorCode.INCONSISTENT_IDENTITY, "target bucket entity/grid/unit/basis mismatch")
        if target.interval.start_ns != start or target.interval.end_ns > end or target.interval.end_ns > config.session.close_ns or target.interval.include_opening_auction != config.session.include_opening_auction or target.interval.include_closing_auction != config.session.include_closing_auction:
            raise ContractError(ErrorCode.BOUNDS, "target bucket selected interval/session mismatch")
        _add(inputs, target.source)
        _add(inputs, _identity_binding("bucket_target_certificate", target.identity_digest, config))
        if reason is None:
            if target.interval.end_ns > config.availability.market_cutoff_ns:
                reason = Reason.FUTURE_MARKET
            elif (kr := config.availability.knowledge_reason(target.known_at_ns)) is not None:
                reason = Reason(kr)
            elif target.interval.end_ns != end or not target.coverage.complete:
                reason = Reason.GOVERNED_GAP
            elif target.volume is None:
                reason = Reason.NULL_FIELD
        if reason is None:
            observed += 1
        _retain_proof(evidence, proofs, EvidenceRow(context.entity, "baseline.interval_relative_volume", target.source.metadata.source.input_id,
                                        str(target.row_index), target.interval.end_ns, target.known_at_ns,
                                        target.interval.start_ns, target.interval.end_ns,
                                        "consumed" if reason is None else "excluded", reason, "completed_interval"), limit)
    if reason is not None:
        reasons.append(reason)
        if status == Status.AVAILABLE:
            status = Status.INCOMPLETE_COVERAGE if reason in (Reason.INELIGIBLE, Reason.GOVERNED_GAP, Reason.FUTURE_MARKET) else Status.MISSING_INPUT
    action = context.action_admission
    if action is not None:
        if action.reference is not None:
            _add(inputs, action.reference)
        if action.status != Status.AVAILABLE:
            status = action.status
            reasons.extend(action.reasons)
    value = None
    if status == Status.AVAILABLE:
        ref, fact = cast(IntervalBaseline, baseline), cast(BucketVolume, target)
        if ref.numerator == 0:
            status = Status.NOT_APPLICABLE
            reasons.append(Reason.ZERO_DENOMINATOR)
        else:
            value = float(Fraction(cast(int, fact.volume)*cast(int, ref.denominator), cast(int, ref.numerator)))
    return _result("baseline.interval_relative_volume", value, status, reasons, 2, observed,
                   config, context, inputs, evidence, limit)
