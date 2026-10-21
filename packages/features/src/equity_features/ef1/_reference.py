"""Pure supplied classification/action admission with original causal witnesses.

These gates consume declarations. They neither fetch facts nor transform prices.
"""
from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from equity_feature_contracts import (
    AdjustmentSpec, CanonicalBatch, ConfigSpec, DataKind, EntityKey, ErrorCode,
    EvidenceRow, FeatureColumn, FeatureResult, InputBinding, QualityRow, Reason,
    ResultMetadata, Status, checked_int64, validate_batch,
)
from equity_features import __version__
from ._anchor import _admit_common, _columns
from ._context import _action_policy, decode_ef1_context, fail, label
from ._definitions import ef1_definitions
from ._status import _decoded

_CLASS_ROLES = ("classification_facts", "classification_history", "classification_projection")
_ACTION_ROLES = ("market", "action_facts", "action_history", "action_projection",
                 "source_representation", "source_quantity_basis")
_FAILED = ("action_policy_mismatch", "revision_mismatch", "wrong_scope",
           "outside_effective_interval", "future_knowledge", "membership_absent")
_UNKNOWN = ("absent_reference", "incomplete_reference", "incomplete_projection",
            "historical_proof_unknown", "missing_text", "unknown_availability")
_KINDS = {"sector_membership": "s", "universe_membership": "u", "industry_membership": "i"}
_PROOFS = {
    "classification_history": ("ef1.classification.history", ("historical", "current_only", "unknown")),
    "classification_projection": ("ef1.reference.projection", ("complete", "partial", "unknown")),
    "action_history": ("ef1.action.history", ("historical", "current_only", "unknown")),
    "action_projection": ("ef1.reference.projection", ("complete", "partial", "unknown")),
    "source_representation": ("ef1.action.representation", ("raw", "caller_transformed")),
    "source_quantity_basis": ("ef1.action.quantity_basis", ("raw_shares", "split_shares")),
}
Columns = dict[str, tuple[Any, ...]]
Witness = tuple[str, int]


def _optional(columns: Columns, name: str, index: int) -> Any:
    return columns[name][index] if name in columns else None


def _reference(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey) -> Columns:
    """Reference-specific structural admission preserves blank membership text."""
    if batch.kind != DataKind.REFERENCE:
        fail(ErrorCode.INVALID_SCHEMA, "reference role must contain REFERENCE")
    meta = batch.metadata
    if meta.namespace != config.session.namespace or meta.coverage.observed != batch.row_count:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "actual reference namespace/population mismatch")
    if meta.ordering != "declared" or meta.duplicate_policy != "reject":
        fail(ErrorCode.INVALID_ORDER, "ordered unique reference population required")
    for value in (meta.namespace, meta.source.source_id, meta.source.snapshot_id,
                  meta.source.mapping_version, meta.source.input_id):
        label(value)
    for interval in meta.interval_coverage:
        label(interval.name)
    if meta.source.mapping_version != "ef1-reference-map1":
        fail(ErrorCode.INCOMPATIBLE_VERSION, "unsupported reference mapping")
    columns = _columns(batch)
    for column in batch.columns:
        for value in column.values:
            if type(value) is str:
                if column.name != "text":
                    label(value)
                elif (len(value) > 128 or len(value.encode("utf-8", errors="surrogatepass")) > 512
                      or any(ord(c) < 32 or ord(c) == 127 or 0xD800 <= ord(c) <= 0xDFFF for c in value)):
                    fail(ErrorCode.BOUNDS, "unsafe or over-limit original reference text")
    if any(value != entity.instrument_id for value in columns["instrument_id"]) or any(
            value != entity.session_id for value in columns["session_id"]):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "one actual requested entity required")
    validate_batch(batch, required_fields=())
    return columns


def _complete(batch: CanonicalBatch) -> bool:
    coverage = batch.metadata.coverage
    return coverage.complete and coverage.expected == coverage.observed == batch.row_count


def _fact_rows(role: str, columns: Columns, selection: Mapping[str, Any]) -> None:
    if role == "classification_facts":
        if any(any(value is not None for value in columns.get(name, ())) for name in ("price", "factor_num", "factor_den")):
            fail(ErrorCode.INVALID_SCHEMA, "classification rows have no numerical payload")
        if any(kind not in _KINDS for kind in columns["fact_kind"]):
            fail(ErrorCode.INVALID_SCHEMA, "closed classification fact kind required")
    else:
        if any(any(value is not None for value in columns.get(name, ())) for name in ("price", "text")):
            fail(ErrorCode.INVALID_SCHEMA, "action factors have no price/text payload")
        for i, kind in enumerate(columns["fact_kind"]):
            if kind not in ("split_factor", "dividend_factor"):
                fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "closed action factor kind required")
            if _optional(columns, "effective_end_ns", i) is not None:
                fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "factor boundary must be instantaneous")
            if any(type(_optional(columns, name, i)) is not int or _optional(columns, name, i) <= 0
                   for name in ("factor_num", "factor_den")):
                fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "positive exact supplied rational factors required")


def _proof_rows(role: str, batch: CanonicalBatch, columns: Columns,
                target: CanonicalBatch | None, selection: Mapping[str, Any],
                relations: dict[str, set[tuple[str, str, str]]]) -> None:
    if any(any(value is not None for value in columns.get(name, ())) for name in ("price", "factor_num", "factor_den")):
        fail(ErrorCode.INVALID_SCHEMA, "proof rows have no numerical payload")
    expected_kind, texts = _PROOFS[role]
    group = "market" if role.startswith("source_") else "facts"
    source = batch.metadata.source
    if target is not None and (source.source_id, source.snapshot_id) != (
            target.metadata.source.source_id, target.metadata.source.snapshot_id):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "proof source/revision must match actual target even when empty")
    for i, reference_id in enumerate(columns["reference_id"]):
        parts = reference_id.split(":")
        if role == "classification_history":
            if len(parts) != 5 or parts[:2] != ["h1", _KINDS[selection["fact_kind"]]]:
                fail(ErrorCode.INVALID_SCHEMA, "closed classification history identity required")
            if _decoded(parts[2]) != selection["scope_id"]:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "classification history scope mismatch")
            target_id, certificate = _decoded(parts[3]), _decoded(parts[4])
        elif role == "action_history":
            if len(parts) != 4 or parts[0] != "a1":
                fail(ErrorCode.INVALID_SCHEMA, "closed action history identity required")
            if _decoded(parts[1]) != selection["scope_id"]:
                fail(ErrorCode.INCONSISTENT_IDENTITY, "action history scope mismatch")
            target_id, certificate = _decoded(parts[2]), _decoded(parts[3])
        else:
            prefix = "q1" if role.startswith("source_") else "r1"
            if len(parts) != 3 or parts[0] != prefix:
                fail(ErrorCode.INVALID_SCHEMA, "closed source/projection identity required")
            target_id, certificate = _decoded(parts[1]), _decoded(parts[2])
        label(certificate)
        if target_id == source.input_id:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "proof cannot name itself as its target")
        relation = (target_id, source.source_id, source.snapshot_id)
        relations.setdefault(group, set()).add(relation)
        if target is not None and relation != (target.metadata.source.input_id,
                target.metadata.source.source_id, target.metadata.source.snapshot_id):
            fail(ErrorCode.INCONSISTENT_IDENTITY, "proof must bind actual target/source/revision")
        if columns["fact_kind"][i] != expected_kind or _optional(columns, "text", i) not in texts:
            fail(ErrorCode.INVALID_SCHEMA, "closed proof fact/text vocabulary required")
        if _optional(columns, "effective_end_ns", i) is None:
            fail(ErrorCode.BOUNDS, "finite positive proof interval required")


def _knowledge(columns: Columns, index: int, knowledge: int,
               findings: set[str], reasons: set[Reason]) -> bool:
    known = _optional(columns, "known_at_ns", index)
    if known is None:
        findings.add("unknown_availability")
        reasons.add(Reason.UNKNOWN_AVAILABILITY)
        return False
    if known > knowledge:
        findings.add("future_knowledge")
        reasons.add(Reason.FUTURE_KNOWLEDGE)
        return False
    return True


def _applicable(columns: Columns, start: int, end: int | None) -> list[int]:
    if end is None:
        return [i for i, left in enumerate(columns["effective_start_ns"])
                if left <= start and (_optional(columns, "effective_end_ns", i) is None
                                     or start < columns["effective_end_ns"][i])]
    return [i for i, left in enumerate(columns["effective_start_ns"])
            if left <= start and end <= columns["effective_end_ns"][i]]


def _selected(columns: Columns, start: int, end: int | None) -> int | None:
    applicable = _applicable(columns, start, end)
    if len(applicable) > 1:
        fail(ErrorCode.DUPLICATE, "ambiguous applicable reference rows before knowledge arbitration")
    return applicable[0] if applicable else None


def _population(batch: CanonicalBatch | None, findings: set[str], reasons: set[Reason]) -> None:
    if batch is None:
        findings.add("absent_reference")
        reasons.add(Reason.ABSENT_INPUT)
    elif not _complete(batch):
        findings.add("incomplete_reference")
        reasons.add(Reason.GOVERNED_GAP)


def _proof(role: str, batch: CanonicalBatch | None, columns: Columns | None,
           index: int | None, knowledge: int, findings: set[str], reasons: set[Reason],
           witnesses: list[Witness]) -> str | None:
    missing = "incomplete_projection" if role.endswith("projection") else (
        "historical_proof_unknown" if role.endswith("history") else "incomplete_reference")
    if batch is None:
        findings.add(missing)
        reasons.add(Reason.ABSENT_INPUT)
        return None
    if not _complete(batch):
        findings.add("incomplete_reference")
        reasons.add(Reason.GOVERNED_GAP)
    if index is None or columns is None:
        findings.add(missing)
        reasons.add(Reason.ABSENT_INPUT)
        return None
    if not _knowledge(columns, index, knowledge, findings, reasons):
        return None
    witnesses.append((role, index))
    text = columns["text"][index]
    if role.endswith("history") and text != "historical":
        findings.add("historical_proof_unknown")
        reasons.add(Reason.UNKNOWN_AVAILABILITY)
    if role.endswith("projection") and text != "complete":
        findings.add("incomplete_projection")
        reasons.add(Reason.GOVERNED_GAP)
    return text


def _market(batch: CanonicalBatch, config: ConfigSpec, entity: EntityKey,
            selection: Mapping[str, Any]) -> Columns:
    if batch.kind not in (DataKind.TRADE, DataKind.BAR, DataKind.DAILY):
        fail(ErrorCode.INVALID_SCHEMA, "action market must be TRADE/BAR/DAILY")
    _admit_common(batch, config, entity)
    if batch.metadata.price_unit != config.price_unit:
        fail(ErrorCode.INVALID_UNIT, "action market price unit mismatch")
    scope = batch.metadata.scope
    if scope is None or not (selection["scope_start_ns"] <= scope.start_ns < scope.end_ns
                            <= selection["scope_end_ns"] and scope.end_ns <= config.availability.market_cutoff_ns):
        fail(ErrorCode.BOUNDS, "actual positive market scope must be contained in action scope/cutoff")
    label(scope.eligibility_policy)
    if (scope.include_opening_auction, scope.include_closing_auction) != (
            config.session.include_opening_auction, config.session.include_closing_auction):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "actual market auction policy mismatch")
    validate_batch(batch, session=config.session, availability=config.availability, required_fields=())
    columns = _columns(batch)
    for i in range(batch.row_count):
        if batch.kind == DataKind.TRADE:
            time = columns["event_ns"][i]
            closing = (_optional(columns, "condition", i) == "closing_auction"
                       and time == scope.end_ns == config.session.close_ns
                       and scope.include_closing_auction)
            if time < scope.start_ns or time >= scope.end_ns and not closing:
                fail(ErrorCode.BOUNDS, "market event outside actual input scope")
        elif columns["start_ns"][i] < scope.start_ns or columns["end_ns"][i] > scope.end_ns:
            fail(ErrorCode.BOUNDS, "market interval outside actual input scope")
    return columns


def compute_reference(batches: tuple[CanonicalBatch | None, ...] | list[CanonicalBatch | None] | list[CanonicalBatch],
                      config: ConfigSpec, *, entity: EntityKey) -> FeatureResult:
    """Evaluate one complete original reference producer, preserving every actual binding."""
    context = decode_ef1_context(config)
    classification = context["producer"] == "reference_classification"
    if context["producer"] not in ("reference_classification", "reference_action"):
        fail(ErrorCode.INVALID_CONFIG, "reference producer required")
    if type(entity) is not EntityKey or entity.session_id != config.session.session_id:
        fail(ErrorCode.INCONSISTENT_IDENTITY, "exact target entity required")
    label(entity.instrument_id)
    label(entity.session_id)
    slots = _CLASS_ROLES if classification else _ACTION_ROLES
    if type(batches) not in (tuple, list) or len(batches) != len(slots) or any(
            batch is not None and type(batch) is not CanonicalBatch for batch in batches):
        fail(ErrorCode.INVALID_SCHEMA, "exact nullable reference role slots required")
    roles = {role: batch for role, batch in zip(slots, batches, strict=True) if batch is not None}
    if len({batch.metadata.source.input_id for batch in roles.values()}) != len(roles):
        fail(ErrorCode.DUPLICATE, "distinct actual role input identities required")
    if sum(batch.row_count for role, batch in roles.items() if role != "market") > 4096:
        fail(ErrorCode.BOUNDS, "aggregate reference row limit exceeded")
    selection = context["selection"]
    columns = {role: (_market(batch, config, entity, selection) if role == "market" else
                      _reference(batch, config, entity)) for role, batch in roles.items()}
    relations: dict[str, set[tuple[str, str, str]]] = {}
    fact_role = "classification_facts" if classification else "action_facts"
    for role, batch in roles.items():
        if role == "market":
            continue
        if role == fact_role:
            _fact_rows(role, columns[role], selection)
        else:
            target = roles.get("market" if role.startswith("source_") else fact_role)
            _proof_rows(role, batch, columns[role], target, selection, relations)
    for group_roles in (("classification_history", "classification_projection"),) if classification else (
            ("action_history", "action_projection"), ("source_representation", "source_quantity_basis")):
        source_pairs = {(roles[role].metadata.source.source_id, roles[role].metadata.source.snapshot_id)
                        for role in group_roles if role in roles}
        if len(source_pairs) > 1:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "proof population source/revision must be coherent even when empty")
    if any(len(group) > 1 for group in relations.values()):
        fail(ErrorCode.INCONSISTENT_IDENTITY, "proofs must name one coherent actual target/source/revision")
    # All structural and applicability duplicate checks precede knowledge/assessment.
    selected: dict[str, int | None] = {}
    for role in slots:
        if role not in roles or role in ("market", "action_facts"):
            continue
        if classification:
            start, end = selection["effective_ns"], None
            if role == fact_role:
                matching = {name: tuple(value for i, value in enumerate(values)
                            if columns[role]["fact_kind"][i] == selection["fact_kind"])
                            for name, values in columns[role].items()}
                indices = [i for i, kind in enumerate(columns[role]["fact_kind"]) if kind == selection["fact_kind"]]
                index = _selected(matching, start, end)
                selected[role] = None if index is None else indices[index]
                continue
        elif role.startswith("source_"):
            market = roles.get("market")
            if market is None:
                selected[role] = None
                continue
            scope = market.metadata.scope
            if scope is None:
                fail(ErrorCode.BOUNDS, "positive actual market scope required")
            start, end = scope.start_ns, scope.end_ns
            if market.kind == DataKind.TRADE:
                applicable = [i for i in _applicable(columns[role], start, end)
                    if all(columns[role]["effective_start_ns"][i] <= time < columns[role]["effective_end_ns"][i]
                           for time in columns["market"]["event_ns"])]
                if len(applicable) > 1:
                    fail(ErrorCode.DUPLICATE, "ambiguous source proof intervals before knowledge arbitration")
                selected[role] = applicable[0] if applicable else None
                continue
        else:
            start, end = selection["scope_start_ns"], selection["scope_end_ns"]
        selected[role] = _selected(columns[role], start, end)
    findings: set[str] = set()
    reasons: set[Reason] = set()
    witnesses: list[Witness] = []
    knowledge = config.availability.knowledge_cutoff_ns
    facts = roles.get(fact_role)
    _population(facts, findings, reasons)
    if classification:
        index = selected.get(fact_role)
        if index is not None:
            _knowledge(columns[fact_role], index, knowledge, findings, reasons)
            if not (_optional(columns[fact_role], "text", index) or "").strip():
                findings.add("missing_text")
                reasons.add(Reason.NULL_FIELD)
            known = _optional(columns[fact_role], "known_at_ns", index)
            if known is not None and known <= knowledge:
                witnesses.append((fact_role, index))
    else:
        policy = _action_policy(selection["policy"])
        market = roles.get("market")
        _population(market, findings, reasons)
        if market is not None:
            for i in range(market.row_count):
                _knowledge(columns["market"], i, knowledge, findings, reasons)
            expected_adjustment = AdjustmentSpec() if policy.representation == "apply_factors" else policy.adjustment
            if market.metadata.adjustment != expected_adjustment:
                findings.add("action_policy_mismatch")
                reasons.add(Reason.INELIGIBLE)
        if facts is not None and policy.adjustment.basis != "raw":
            if facts.metadata.source.snapshot_id != policy.adjustment.action_snapshot:
                findings.add("revision_mismatch")
                reasons.add(Reason.INELIGIBLE)
            required: list[int] = []
            for i, time in enumerate(columns[fact_role]["effective_start_ns"]):
                if selection["scope_start_ns"] < time <= policy.anchor_ns:
                    if policy.adjustment.basis == "split" and columns[fact_role]["fact_kind"][i] != "split_factor":
                        fail(ErrorCode.UNSUPPORTED_ADJUSTMENT, "split policy requires split factors only")
                    required.append(i)
                    _knowledge(columns[fact_role], i, knowledge, findings, reasons)
                    if market is not None and policy.representation == "apply_factors" and market.kind != DataKind.TRADE:
                        for left, right in zip(columns["market"]["start_ns"], columns["market"]["end_ns"], strict=True):
                            if left < time < right:
                                fail(ErrorCode.BOUNDS, "market interval straddles applicable factor boundary")
            if required:
                for i in dict.fromkeys((required[0], required[-1])):
                    known = _optional(columns[fact_role], "known_at_ns", i)
                    if known is not None and known <= knowledge:
                        witnesses.append((fact_role, i))
    for role in slots:
        if role not in _PROOFS:
            continue
        text = _proof(role, roles.get(role), columns.get(role), selected.get(role), knowledge,
                      findings, reasons, witnesses)
        if not classification and text is not None:
            expected_text = ("raw" if policy.representation == "apply_factors" else "caller_transformed") if role == "source_representation" else (
                "raw_shares" if policy.representation == "apply_factors" else policy.quantity_basis)
            if role.startswith("source_") and text != expected_text:
                findings.add("action_policy_mismatch")
                reasons.add(Reason.INELIGIBLE)
    if classification and not findings and selected.get(fact_role) is None:
        findings.add("membership_absent")
        reasons.add(Reason.NO_ELIGIBLE_OBSERVATIONS)
    failed = next((reason for reason in _FAILED if reason in findings), None)
    unknown = next((reason for reason in _UNKNOWN if reason in findings), None)
    state, diagnostic = ("failed", failed) if failed else (("unknown", unknown) if unknown else ("passed", "none"))
    value: str | None = None
    if classification and state == "passed":
        index = selected.get(fact_role)
        if index is None:
            fail(ErrorCode.INCONSISTENT_IDENTITY, "passed classification requires one actual selected membership")
        value = columns[fact_role]["text"][index]
    bindings = tuple(InputBinding(role, batch.kind, batch.metadata) for role, batch in roles.items())
    metadata = ResultMetadata(config.session.namespace, entity.session_id, config.availability,
                              config.digest, bindings, "python-exact", __version__, evidence_limit=9 if classification else 12)
    expected: int | None = 1
    observed = 1
    if classification:
        expected_counts = tuple(batch.metadata.coverage.expected for batch in roles.values())
        expected = checked_int64(sum(n for n in expected_counts if n is not None)) if (
            len(roles) == len(slots) and all(n is not None for n in expected_counts)) else None
        observed = checked_int64(sum(batch.row_count for batch in roles.values()))
    quality_reasons = tuple(sorted(reasons, key=lambda reason: reason.value))
    if not reasons:
        value_status = Status.AVAILABLE
    elif any(reason in reasons for reason in (Reason.ABSENT_INPUT, Reason.NULL_FIELD, Reason.UNKNOWN_AVAILABILITY,
                                              Reason.FUTURE_KNOWLEDGE, Reason.INELIGIBLE)):
        value_status = Status.MISSING_INPUT
    elif Reason.GOVERNED_GAP in reasons:
        value_status = Status.INCOMPLETE_COVERAGE
    else:
        value_status = Status.NOT_APPLICABLE
    result_columns: list[FeatureColumn] = []
    quality: list[QualityRow] = []
    evidence: list[EvidenceRow] = []
    for definition in ef1_definitions(config):
        factual = definition.feature_id == "reference.classification.value"
        output = value if factual else (diagnostic if definition.feature_id.endswith("_reason") else state)
        result_columns.append(FeatureColumn(definition.feature_id, "v1", definition.dtype,
                                           definition.unit, (entity,), (output,)))
        quality.append(QualityRow(entity, definition.feature_id, value_status if factual else Status.AVAILABLE,
                                  expected if factual else 1, observed if factual else 1,
                                  quality_reasons if factual else ()))
        if not factual or state == "passed":
            for role, i in witnesses:
                data = columns[role]
                if data["effective_start_ns"][i] > config.availability.market_cutoff_ns:
                    continue
                evidence.append(EvidenceRow(entity, definition.feature_id, roles[role].metadata.source.input_id,
                    data["reference_id"][i], data["effective_start_ns"][i], _optional(data, "known_at_ns", i),
                    data["effective_start_ns"][i], _optional(data, "effective_end_ns", i)))
    return FeatureResult(tuple(result_columns), tuple(quality), metadata, tuple(evidence))