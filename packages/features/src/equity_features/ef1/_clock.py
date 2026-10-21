"""Pure supplied-schedule clock; original causal evidence is an actual input."""
from __future__ import annotations

from collections.abc import Mapping
from fractions import Fraction
from typing import Any

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, FeatureColumn,
    FeatureResult, InputBinding, QualityRow, Reason, ResultMetadata, Status, checked_int64,
)
from equity_features import __version__
from ._anchor import _admit_common, _columns, _ready, _reasons
from ._context import calendar_proof_id, decode_ef1_context, fail, label
from ._definitions import ef1_definitions


def _calendar_ready(proof: CanonicalBatch | None, config: ConfigSpec,
                    context: Mapping[str, Any], entity: EntityKey) -> tuple[Status, tuple[Reason, ...]]:
    if proof is None:
        return Status.MISSING_INPUT, (Reason.ABSENT_INPUT,)
    if proof.kind != DataKind.REFERENCE:
        fail(ErrorCode.INVALID_SCHEMA, "calendar provenance must be REFERENCE")
    if proof.row_count > 1:
        fail(ErrorCode.DUPLICATE, "one exact calendar declaration required")
    _admit_common(proof, config, entity)
    columns = _columns(proof)
    if any(name in columns for name in ("price", "factor_num", "factor_den")):
        fail(ErrorCode.INVALID_SCHEMA, "calendar proof has unused numerical payload")
    calendar = context["calendar"]
    if proof.metadata.source.snapshot_id != calendar["revision"]:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "calendar proof revision mismatch")
    if proof.metadata.source.mapping_version != "ef1-reference-map1":
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported calendar proof mapping")
    if not proof.row_count:
        return Status.MISSING_INPUT, (Reason.ABSENT_INPUT,)
    if columns["reference_id"][0] != calendar_proof_id(context):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "calendar declaration hash mismatch")
    if (columns["fact_kind"][0] != "ef1.calendar.provenance"
            or columns.get("text", (None,))[0] != "supplied_schedule"):
        fail(ErrorCode.INVALID_SCHEMA, "closed calendar provenance vocabulary required")
    start_ns = columns["effective_start_ns"][0]
    end_ns = columns.get("effective_end_ns", (None,))[0]
    starts = [row[2] for row in calendar["sessions"]] + [row[1] for row in calendar["segments"]]
    ends = [row[3] for row in calendar["sessions"]] + [row[2] for row in calendar["segments"]]
    if (start_ns is None or end_ns is None or start_ns >= end_ns
            or start_ns > min(starts) or end_ns < max(ends)):
        fail(ErrorCode.BOUNDS, "finite calendar proof interval must cover the entire supplied schedule")
    reasons: tuple[Reason, ...] = () if proof.metadata.coverage.complete else (Reason.GOVERNED_GAP,)
    # Calendar proof is causal in every requested availability mode. Generic
    # reconstruction admission must not waive its original knowledge evidence.
    known_at_ns = columns.get("known_at_ns", (None,))[0]
    if known_at_ns is None:
        reasons = _reasons(reasons, (Reason.UNKNOWN_AVAILABILITY,))
    elif known_at_ns > config.availability.knowledge_cutoff_ns:
        reasons = _reasons(reasons, (Reason.FUTURE_KNOWLEDGE,))
    return _ready(reasons)


def compute_clock(batches: tuple[CanonicalBatch, ...] | list[CanonicalBatch], config: ConfigSpec,
                  *, entity: EntityKey) -> FeatureResult:
    context = decode_ef1_context(config)
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    label(entity.session_id)
    if type(batches) not in (tuple, list) or len(batches) > 1:
        fail(ErrorCode.INVALID_SCHEMA, "one actual calendar provenance role at most")
    if batches and type(batches[0]) is not CanonicalBatch:
        fail(ErrorCode.INVALID_SCHEMA, "actual present CanonicalBatch required")
    proof = batches[0] if batches else None
    status, reasons = _calendar_ready(proof, config, context, entity)
    bindings = () if proof is None else (InputBinding("calendar_provenance", proof.kind, proof.metadata),)
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability,
                              config.digest, bindings, "python-exact", __version__)
    expected = None if proof is None else proof.metadata.coverage.expected
    observed = 0 if proof is None else proof.row_count
    values: dict[str, int | float | bool | str] = {}
    if status == Status.AVAILABLE:
        # Wide subtraction precedes checked published nanosecond coefficients.
        duration = checked_int64(config.session.close_ns - config.session.open_ns)
        elapsed = checked_int64(min(max(config.availability.market_cutoff_ns - config.session.open_ns, 0), duration))
        remaining = checked_int64(duration - elapsed)
        phase = "closed"
        for name, start_ns, end_ns in context["calendar"]["segments"]:
            if start_ns <= config.availability.market_cutoff_ns < end_ns:
                phase = name
                break
        values = {"early_close": context["calendar"]["early_close"], "phase": phase,
                  "regular_elapsed_ns": elapsed, "regular_fraction": float(Fraction(elapsed, duration)),
                  "regular_remaining_ns": remaining}
    columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    for definition in ef1_definitions(config):
        name = definition.feature_id.rsplit(".", 1)[1]
        columns.append(FeatureColumn(definition.feature_id, "v1", definition.dtype, definition.unit,
                                     (entity,), (values.get(name),)))
        quality.append(QualityRow(entity, definition.feature_id, status, expected, observed, reasons))
    return FeatureResult(tuple(columns), tuple(quality), metadata)
