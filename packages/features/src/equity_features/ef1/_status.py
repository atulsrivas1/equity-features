"""Pure current supplied state with causal complete-prefix and finite validity proof."""
from __future__ import annotations

from base64 import urlsafe_b64decode, urlsafe_b64encode
from collections.abc import Mapping
from typing import Any

from equity_feature_contracts import (
    CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode, EvidenceRow, FeatureColumn,
    FeatureResult, InputBinding, QualityRow, Reason, ResultMetadata, Status, checked_int64,
)
from equity_features import __version__
from ._anchor import _admit_common, _columns, _ready, _reasons
from ._clock import _calendar_ready
from ._context import decode_ef1_context, fail, label
from ._definitions import ef1_definitions

_ROLES = ("calendar_provenance", "status_states", "status_prefix", "status_validity")
_DIMENSIONS = {"trading": ("t", ("active", "halted", "closed")),
               "quoting": ("q", ("enabled", "disabled")), "ssr": ("s", ("on", "off"))}


def _decoded(token: str) -> str:
    """Decode only canonical, reversible, unpadded UTF8 base64url identities."""
    if not token or any(c not in "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_" for c in token):
        fail(ErrorCode.INVALID_SCHEMA, "canonical unpadded base64url required")
    try:
        raw = urlsafe_b64decode(token + "=" * ((-len(token)) % 4))
        value = raw.decode("utf-8")
    except (ValueError, UnicodeError):
        fail(ErrorCode.INVALID_SCHEMA, "invalid UTF8 base64url identity")
    if urlsafe_b64encode(raw).decode("ascii").rstrip("=") != token:
        fail(ErrorCode.INVALID_SCHEMA, "noncanonical base64url identity")
    return label(value)


def _state_identity(reference_id: str, dimension: str, epoch: str) -> int:
    parts = reference_id.split(":")
    if len(parts) != 5 or parts[:2] != ["s1", dimension]:
        fail(ErrorCode.INVALID_SCHEMA, "closed status state identity required")
    if _decoded(parts[2]) != epoch:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "status epoch mismatch")
    sequence = parts[3]
    if len(sequence) != 19 or any(c not in "0123456789" for c in sequence) or int(sequence) > 2**63 - 1:
        fail(ErrorCode.INVALID_SCHEMA, "exact nonnegative int64 seq19 required")
    _decoded(parts[4])
    return int(sequence)


def _causal(columns: dict[str, tuple[Any, ...]], index: int, cutoff: int) -> tuple[Reason, ...]:
    known = _optional(columns, "known_at_ns", index)
    if known is None:
        return (Reason.UNKNOWN_AVAILABILITY,)
    return (Reason.FUTURE_KNOWLEDGE,) if known > cutoff else ()


def _optional(columns: dict[str, tuple[Any, ...]], name: str, index: int) -> Any:
    values = columns.get(name)
    return None if values is None else values[index]


def _reference(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey) -> dict[str, tuple[Any, ...]]:
    if batch.kind != DataKind.REFERENCE:
        fail(ErrorCode.INVALID_SCHEMA, "status roles must be actual REFERENCE batches")
    if batch.row_count > 4096:
        fail(ErrorCode.BOUNDS, "status reference work bound exceeded")
    _admit_common(batch, config, entity)
    if batch.metadata.source.mapping_version != "ef1-reference-map1":
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported status reference mapping")
    columns = _columns(batch)
    if any(name in columns for name in ("price", "factor_num", "factor_den")):
        fail(ErrorCode.INVALID_SCHEMA, "status references have no numerical payload")
    return columns


def _states(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey,
            selection: Mapping[str, Any]) -> dict[str, tuple[Any, ...]]:
    columns = _reference(batch, config, entity)
    dimension, texts = _DIMENSIONS[selection["dimension"]]
    previous: int | None = None
    for i, reference_id in enumerate(columns["reference_id"]):
        sequence = _state_identity(reference_id, dimension, selection["epoch"])
        if previous is not None and sequence <= previous:
            fail(ErrorCode.DUPLICATE if sequence == previous else ErrorCode.INVALID_ORDER,
                 "strict supplied status sequence order required")
        previous = sequence
        if (columns["fact_kind"][i] != "ef1.status." + selection["dimension"]
                or _optional(columns, "text", i) not in texts):
            fail(ErrorCode.INVALID_SCHEMA, "closed selected status fact/text required")
    return columns


def _certificate(batch: CanonicalBatch, state: CanonicalBatch | None, config: ConfigSpec,
                 entity: EntityKey, selection: Mapping[str, Any], role: str,
                 relations: set[tuple[str, str, str]]) -> dict[str, tuple[Any, ...]]:
    columns = _reference(batch, config, entity)
    dimension = _DIMENSIONS[selection["dimension"]][0]
    if state is not None and (batch.metadata.source.source_id, batch.metadata.source.snapshot_id) != (
            state.metadata.source.source_id, state.metadata.source.snapshot_id):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "status proof source/revision mismatch")
    for i, reference_id in enumerate(columns["reference_id"]):
        parts = reference_id.split(":")
        if len(parts) != 5 or parts[:2] != ["p1", dimension]:
            fail(ErrorCode.INVALID_SCHEMA, "closed selected status certificate identity required")
        epoch, target = _decoded(parts[2]), _decoded(parts[3])
        _decoded(parts[4])
        relations.add((target, batch.metadata.source.source_id, batch.metadata.source.snapshot_id))
        if epoch != selection["epoch"]:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "status certificate epoch mismatch")
        if state is not None and target != state.metadata.source.input_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "certificate must bind actual status input/source/revision")
        kind = "prefix_complete" if role == "status_prefix" else "validity"
        if columns["fact_kind"][i] != "ef1.status." + kind or _optional(columns, "text", i) != dimension:
            fail(ErrorCode.INVALID_SCHEMA, "closed status certificate vocabulary required")
        if _optional(columns, "effective_end_ns", i) is None:
            fail(ErrorCode.BOUNDS, "finite positive status certificate interval required")
    return columns


def compute_status(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None] | list[CanonicalBatch], config: ConfigSpec,
                   *, entity: EntityKey) -> FeatureResult:
    """Evaluate exactly one dimension; assessment readiness is independent of facts."""
    context = decode_ef1_context(config)
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    label(entity.session_id)
    if type(batches) not in (tuple, list) or len(batches) != 4:
        fail(ErrorCode.INVALID_SCHEMA, "exactly four concrete status role slots required")
    if any(batch is not None and type(batch) is not CanonicalBatch for batch in batches):
        fail(ErrorCode.INVALID_SCHEMA, "each status slot must be CanonicalBatch or None")
    roles = {role: batch for role, batch in zip(_ROLES, batches, strict=True) if batch is not None}
    if any(batch.kind != DataKind.REFERENCE for batch in roles.values()):
        fail(ErrorCode.INVALID_SCHEMA, "every present status slot must be REFERENCE")
    if sum(batch.row_count for batch in roles.values()) > 4096:
        fail(ErrorCode.BOUNDS, "aggregate status reference work bound exceeded")
    if len({batch.metadata.source.input_id for batch in roles.values()}) != len(roles):
        fail(ErrorCode.DUPLICATE, "distinct actual role input identities required")
    selection = context["selection"]
    state = roles.get("status_states")
    state_columns = None if state is None else _states(state, config, entity, selection)
    relations: set[tuple[str, str, str]] = set()
    certificates = {role: _certificate(batch, state, config, entity, selection, role, relations)
                    for role, batch in roles.items() if role in ("status_prefix", "status_validity")}
    proof_sources = {(batch.metadata.source.source_id, batch.metadata.source.snapshot_id)
                     for role, batch in roles.items() if role in ("status_prefix", "status_validity")}
    if len(relations) > 1 or len(proof_sources) > 1:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "status proofs must declare one coherent target/source/revision")
    _, calendar_reasons = _calendar_ready(roles.get("calendar_provenance"), config, context, entity)
    reasons = calendar_reasons
    findings: set[str] = set()
    if Reason.ABSENT_INPUT in reasons:
        findings.add("absent_input")
    if Reason.GOVERNED_GAP in reasons:
        findings.add("incomplete_status_prefix")
    cutoff, knowledge = config.availability.market_cutoff_ns, config.availability.knowledge_cutoff_ns
    seed_id = selection["seed_reference_id"]
    if seed_id is not None:
        _state_identity(seed_id, _DIMENSIONS[selection["dimension"]][0], selection["epoch"])
    seed: int | None = None
    selected: int | None = None
    if state_columns is not None and seed_id in state_columns["reference_id"]:
        seed = state_columns["reference_id"].index(seed_id)
        if state_columns["effective_start_ns"][seed] < cutoff:
            for i in range(seed, len(state_columns["reference_id"])):
                if state_columns["effective_start_ns"][i] >= cutoff:
                    break
                selected = i
                reasons = _reasons(reasons, _causal(state_columns, i, knowledge))
    if seed is None or selected is None:
        findings.add("absent_input")
        reasons = _reasons(reasons, (Reason.ABSENT_INPUT,))
    if state is not None and not state.metadata.coverage.complete:
        findings.add("incomplete_status_prefix")
        reasons = _reasons(reasons, (Reason.GOVERNED_GAP,))
    applicable_proofs: dict[str, int] = {}
    prefix_ready = False
    # Count interval-applicable rows before any knowledge arbitration or dependent
    # validity evaluation, so ambiguity rejects even when another prerequisite fails.
    for role in ("status_prefix", "status_validity"):
        batch = roles.get(role)
        if batch is None or not batch.row_count:
            findings.add("absent_input")
            reasons = _reasons(reasons, (Reason.ABSENT_INPUT,))
            continue
        columns = certificates[role]
        if not batch.metadata.coverage.complete:
            findings.add("incomplete_status_prefix")
            reasons = _reasons(reasons, (Reason.GOVERNED_GAP,))
        if role == "status_prefix":
            applicable = [i for i in range(batch.row_count) if seed is not None and state_columns is not None
                and columns["effective_start_ns"][i] <= state_columns["effective_start_ns"][seed]
                and cutoff <= columns["effective_end_ns"][i]]
        else:
            applicable = [i for i in range(batch.row_count)
                if columns["effective_start_ns"][i] <= cutoff < columns["effective_end_ns"][i]]
        if len(applicable) > 1:
            fail(ErrorCode.DUPLICATE, "ambiguous overlapping applicable status proofs")
        if applicable:
            applicable_proofs[role] = applicable[0]
            if role == "status_validity":
                # Original knowledge of a scope-applicable required proof is
                # independent of transition readiness; semantic expiry is not.
                reasons = _reasons(reasons, _causal(columns, applicable[0], knowledge))
        if role == "status_prefix" and seed is not None and selected is not None:
            if not applicable:
                findings.add("incomplete_status_prefix")
                reasons = _reasons(reasons, (Reason.GOVERNED_GAP,))
            else:
                reasons = _reasons(reasons, _causal(columns, applicable[0], knowledge))
            prefix_ready = not reasons
    # Prefix and required-transition readiness establish which event is current.
    # Validity/expiry cannot describe an event whose current identity is unproved.
    if prefix_ready and selected is not None and state_columns is not None:
        validity = applicable_proofs.get("status_validity")
        validity_batch = roles.get("status_validity")
        if validity is None and validity_batch is not None and validity_batch.row_count:
            findings.add("outside_effective_interval")
            reasons = _reasons(reasons, (Reason.INELIGIBLE,))
        end = _optional(state_columns, "effective_end_ns", selected)
        if end is not None and cutoff >= end:
            findings.add("outside_effective_interval")
            reasons = _reasons(reasons, (Reason.INELIGIBLE,))
    for reason in (Reason.UNKNOWN_AVAILABILITY, Reason.FUTURE_KNOWLEDGE):
        if reason in reasons:
            findings.add(reason.value)
    factual_status, reasons = _ready(reasons)
    age: int | None = None
    value: str | None = None
    state_status, state_reasons = factual_status, reasons
    if not reasons and selected is not None and state_columns is not None:
        age = checked_int64(cutoff - state_columns["effective_start_ns"][selected])
        value = state_columns["text"][selected]
        if selection["max_age_ns"] is not None and age > selection["max_age_ns"]:
            value = None
            state_status, state_reasons = Status.MISSING_INPUT, (Reason.INELIGIBLE,)
            findings.add("stale_state")
    diagnostic = next((reason for reason in ("absent_input", "incomplete_status_prefix", "unknown_availability",
        "future_knowledge", "outside_effective_interval", "stale_state") if reason in findings), "none")
    values = {selection["dimension"] + "_state": value, selection["dimension"] + "_age_ns": age,
              "admission_state": "ready" if diagnostic == "none" else "unavailable", "admission_reason": diagnostic}
    bindings = tuple(InputBinding(role, batch.kind, batch.metadata) for role, batch in roles.items())
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability,
                              config.digest, bindings, "python-exact", __version__, evidence_limit=2)
    expected_counts = tuple(b.metadata.coverage.expected for b in roles.values())
    expected = checked_int64(sum(n for n in expected_counts if n is not None)) if (
        len(roles) == 4 and all(n is not None for n in expected_counts)) else None
    observed = sum(b.row_count for b in roles.values())
    result_columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for definition in ef1_definitions(config):
        name = definition.feature_id.rsplit(".", 1)[1]
        result_columns.append(FeatureColumn(definition.feature_id, "v1", definition.dtype, definition.unit,
                                           (entity,), (values[name],)))
        if name.startswith("admission_"):
            quality.append(QualityRow(entity, definition.feature_id, Status.AVAILABLE, 1, 1))
        else:
            status, output_reasons = (state_status, state_reasons) if name.endswith("_state") else (factual_status, reasons)
            quality.append(QualityRow(entity, definition.feature_id, status, expected, observed, output_reasons))
            if age is not None and selected is not None and state_columns is not None and state is not None:
                rejected = name.endswith("_state") and value is None
                evidence.append(EvidenceRow(entity, definition.feature_id, state.metadata.source.input_id,
                    state_columns["reference_id"][selected], state_columns["effective_start_ns"][selected],
                    _optional(state_columns, "known_at_ns", selected),
                    state_columns["effective_start_ns"][selected], _optional(state_columns, "effective_end_ns", selected),
                    "excluded" if rejected else "consumed", Reason.INELIGIBLE if rejected else None))
    return FeatureResult(tuple(result_columns), tuple(quality), metadata, tuple(evidence))
