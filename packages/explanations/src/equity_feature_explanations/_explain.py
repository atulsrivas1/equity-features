"""Closed, bounded projections of supplied content and reported references."""
from __future__ import annotations
from dataclasses import dataclass
import json
from typing import cast
from equity_feature_contracts import (
    AvailabilitySpec, CanonicalBatch, ConfigSpec, ContractError, EntityKey,
    EvidenceRow, FeatureColumn, FeatureResult, InputBinding, QualityRow, ResultMetadata, Status,
    builtin_registry,
)
from equity_feature_evidence import (
    ContentFingerprint, EnvironmentDeclaration, EvidenceDisclosure, EvidenceError,
    ExecutionClaim, ExecutionReceipt, FormulaBinding, PackageVersion,
    InputFingerprint, decode_receipt, encode_receipt, fingerprint_batch,
    fingerprint_config, fingerprint_result, make_receipt, receipt_digest,
)

MAX_BYTES = 262144
MAX_NODES = 16384
MAX_DEPTH = 20
MAX_CONTENT_BYTES = 33554432
_CODES = ('invalid_schema', 'unsupported_version', 'inconsistent_binding', 'duplicate', 'limit_exceeded')
# Admitted producer backend versions: earlier releases plus the current features version (tools/_versions.py).
_LEGACY_BACKEND_VERSIONS = ('0.0.4a4', '0.0.4a5', '0.0.4a6', '0.0.4a7')


class ExplanationError(ValueError):
    """Fixed payload-free validation failure."""
    def __init__(self, code: str = 'invalid_schema') -> None:
        if type(code) is not str or code not in _CODES: code = 'invalid_schema'
        self.code = code
        super().__init__('Explanation rejected: ' + code)


def _require(condition: bool, code: str = 'invalid_schema') -> None:
    if not condition: raise ExplanationError(code)


def _label(value: str, *, maximum: int = 1024) -> None:
    _require(type(value) is str and bool(value.strip()))
    _require(len(value) <= (256 if maximum == 1024 else 8192), 'limit_exceeded')
    _require(not any(ord(c) < 32 or 127 <= ord(c) <= 159 or 0xD800 <= ord(c) <= 0xDFFF for c in value))
    _require(len(value.encode('utf-8')) <= maximum, 'limit_exceeded')


def _integer(value: int, maximum: int) -> None:
    _require(type(value) is int and 0 <= value <= maximum)


def _entity(value: EntityKey) -> None:
    _require(type(value) is EntityKey)
    _label(value.instrument_id); _label(value.session_id)


def _mapped(error: EvidenceError | ContractError) -> ExplanationError:
    return ExplanationError(str(error.code))


def _receipt_json(value: ExecutionReceipt) -> dict[str, object]:
    _require(type(value) is ExecutionReceipt)
    try:
        raw = encode_receipt(value)
        _require(decode_receipt(raw) == value)
        return cast(dict[str, object], json.loads(raw))
    except (EvidenceError, ContractError) as error:
        raise _mapped(error) from None


def _binding_json(binding: InputBinding, content: ContentFingerprint) -> dict[str, object]:
    """Reuse the public bounded receipt schema to validate borrowed metadata."""
    _require(type(binding) is InputBinding and type(content) is ContentFingerprint)
    try:
        value = ExecutionReceipt(
            ResultMetadata(binding.metadata.namespace, 'summary', AvailabilitySpec(0, 0, 0),
                '0' * 64, (binding,), 'declaration', '1'),
            ContentFingerprint('configuration', '0' * 64, 0),
            (InputFingerprint(binding.role, binding.metadata.source.input_id, content),),
            ContentFingerprint('feature_result', '0' * 64, 0), (),
            EnvironmentDeclaration('caller', 'declared', 'declared', (PackageVersion('contracts', 'declared'),)),
            ExecutionClaim(), EvidenceDisclosure('not_supplied', 0))
        metadata = cast(dict[str, object], _receipt_json(value)['metadata'])
        return cast(list[dict[str, object]], metadata['inputs'])[0]
    except (EvidenceError, ContractError) as error:
        raise _mapped(error) from None


@dataclass(frozen=True)
class InputSummary:
    binding: InputBinding
    content: ContentFingerprint
    content_verified: bool

    def __post_init__(self) -> None:
        _require(type(self) is InputSummary)
        _require(type(self.content_verified) is bool)
        _binding_json(self.binding, self.content)


@dataclass(frozen=True)
class EvidenceReference:
    index: int
    row: EvidenceRow

    def __post_init__(self) -> None:
        _require(type(self) is EvidenceReference)
        _integer(self.index, 4095)
        _require(type(self.row) is EvidenceRow)
        _entity(self.row.entity)
        for text in (self.row.feature_id, self.row.input_id, self.row.row_id): _label(text)
        try:
            row = self.row
            _require(EvidenceRow(row.entity, row.feature_id, row.input_id, row.row_id,
                row.event_ns, row.known_at_ns, row.effective_start_ns, row.effective_end_ns,
                row.use, row.exclusion_reason, row.boundary) == row)
        except ContractError as error:
            raise _mapped(error) from None


@dataclass(frozen=True)
class ExplanationFinding:
    code: str
    role: str | None = None
    evidence_index: int | None = None

    def __post_init__(self) -> None:
        _require(type(self) is ExplanationFinding)
        _require(type(self.code) is str)
        if self.code == 'input_content_unverified':
            _require(type(self.role) is str and self.evidence_index is None)
            _label(cast(str, self.role))
        elif self.code == 'reported_exclusion':
            _require(self.role is None and type(self.evidence_index) is int)
            _integer(cast(int, self.evidence_index), 4095)
        else:
            _require(self.code in ('retained_detail_omitted', 'global_evidence_truncated',
                'global_evidence_not_supplied', 'global_evidence_unknown', 'result_unavailable'))
            _require(self.role is None and self.evidence_index is None)


@dataclass(frozen=True)
class Explanation:
    receipt: ExecutionReceipt
    entity: EntityKey
    feature_id: str
    formula_version: str
    formula: str
    formula_document: str
    quality: QualityRow
    inputs: tuple[InputSummary, ...]
    evidence: tuple[EvidenceReference, ...]
    selected_retained_count: int
    display_limit: int
    source_authenticated: bool = False
    execution_verified: bool = False
    schema_version: str = '1'

    def __post_init__(self) -> None:
        _require(type(self) is Explanation)
        _receipt_json(self.receipt); _entity(self.entity)
        for text in (self.feature_id, self.formula_version, self.formula_document): _label(text)
        _label(self.formula, maximum=8192)
        _require(type(self.schema_version) is str and self.schema_version == '1', 'unsupported_version')
        _require(type(self.source_authenticated) is bool and not self.source_authenticated)
        _require(type(self.execution_verified) is bool and not self.execution_verified)
        _require(type(self.inputs) is tuple and len(self.inputs) <= 64, 'limit_exceeded')
        _require(type(self.evidence) is tuple and len(self.evidence) <= 64, 'limit_exceeded')
        _integer(self.selected_retained_count, 4096); _integer(self.display_limit, 64)
        _require(self.selected_retained_count <= self.receipt.evidence.retained_count)
        _require(len(self.evidence) == min(self.display_limit, self.selected_retained_count))
        _require(type(self.quality) is QualityRow)
        _require(self.quality.entity == self.entity and self.quality.feature_id == self.feature_id, 'inconsistent_binding')
        _require(self.entity.session_id == self.receipt.metadata.session_id, 'inconsistent_binding')
        try:
            q = self.quality
            _require(QualityRow(q.entity, q.feature_id, q.status, q.expected, q.observed, q.reasons) == q)
            definition = builtin_registry().get(self.feature_id)
            for formula in self.receipt.formulas:
                _require(formula.formula_version == builtin_registry().get(formula.feature_id).algorithm_version == 'v1', 'unsupported_version')
        except ContractError as error:
            raise _mapped(error) from None
        _require(self.formula_version == definition.algorithm_version == 'v1', 'unsupported_version')
        _require(self.formula == definition.formula and self.formula_document == definition.formula_document, 'inconsistent_binding')
        _require(FormulaBinding(self.feature_id, self.formula_version) in self.receipt.formulas, 'inconsistent_binding')
        _require(self.receipt.metadata.math_policy_version == 'v1' and self.receipt.metadata.backend_id == 'python-exact'
            and self.receipt.metadata.backend_version in _LEGACY_BACKEND_VERSIONS, 'unsupported_version')
        _require(len(self.inputs) == len(self.receipt.inputs))
        for summary, reference, binding in zip(self.inputs, self.receipt.inputs, self.receipt.metadata.inputs, strict=True):
            _require(type(summary) is InputSummary)
            InputSummary.__post_init__(summary)
            _require(summary.binding == binding and summary.content == reference.content and binding.role == reference.role, 'inconsistent_binding')
        indices: list[int] = []; keys: set[tuple[EntityKey, str, str, str]] = set()
        input_ids = {x.input_id for x in self.receipt.inputs}
        for reference_row in self.evidence:
            _require(type(reference_row) is EvidenceReference)
            EvidenceReference.__post_init__(reference_row)
            row = reference_row.row
            _require(reference_row.index < self.receipt.evidence.retained_count)
            _require(row.entity == self.entity and row.feature_id == self.feature_id and row.input_id in input_ids, 'inconsistent_binding')
            key = (row.entity, row.feature_id, row.input_id, row.row_id)
            _require(key not in keys, 'duplicate'); keys.add(key); indices.append(reference_row.index)
        _require(indices == sorted(set(indices)), 'duplicate')
        _encoded(self)

    @property
    def receipt_digest(self) -> str:
        return receipt_digest(self.receipt)

    @property
    def displayed_count(self) -> int:
        return len(self.evidence)

    @property
    def omitted_retained_count(self) -> int:
        return self.selected_retained_count - self.displayed_count

    @property
    def findings(self) -> tuple[ExplanationFinding, ...]:
        rows = [ExplanationFinding('input_content_unverified', x.binding.role) for x in self.inputs if not x.content_verified]
        rows += [ExplanationFinding('reported_exclusion', evidence_index=x.index) for x in self.evidence if x.row.use == 'excluded']
        if self.omitted_retained_count: rows.append(ExplanationFinding('retained_detail_omitted'))
        if self.receipt.evidence.state != 'retained_complete':
            rows.append(ExplanationFinding('global_evidence_' + self.receipt.evidence.state))
        if self.quality.status != Status.AVAILABLE: rows.append(ExplanationFinding('result_unavailable'))
        _require(len(rows) <= 131, 'limit_exceeded')
        return tuple(rows)


def _entity_json(value: EntityKey) -> dict[str, str]:
    return {'instrument_id': value.instrument_id, 'session_id': value.session_id}


def _row_json(row: EvidenceRow) -> dict[str, object]:
    return {'entity': _entity_json(row.entity), 'feature_id': row.feature_id,
        'input_id': row.input_id, 'row_id': row.row_id, 'event_ns': row.event_ns,
        'known_at_ns': row.known_at_ns, 'effective_start_ns': row.effective_start_ns,
        'effective_end_ns': row.effective_end_ns, 'use': row.use,
        'exclusion_reason': row.exclusion_reason.value if row.exclusion_reason is not None else None,
        'boundary': row.boundary}


def _encoded(value: Explanation) -> bytes:
    rc = _receipt_json(value.receipt)
    meta = cast(dict[str, object], rc['metadata'])
    bindings = cast(list[dict[str, object]], meta['inputs'])
    references = cast(list[dict[str, object]], rc['inputs'])
    q = value.quality
    root = {'schema_version': value.schema_version, 'receipt': rc, 'receipt_digest': value.receipt_digest,
        'entity': _entity_json(value.entity), 'feature_id': value.feature_id,
        'formula_version': value.formula_version, 'formula': value.formula, 'formula_document': value.formula_document,
        'quality': {'entity': _entity_json(q.entity), 'feature_id': q.feature_id,
            'status': q.status.value, 'expected': q.expected, 'observed': q.observed, 'reasons': [r.value for r in q.reasons]},
        'inputs': [{'binding': binding, 'content': reference['content'], 'content_verified': summary.content_verified}
            for summary, reference, binding in zip(value.inputs, references, bindings, strict=True)],
        'evidence': [{'index': x.index, 'row': _row_json(x.row)} for x in value.evidence],
        'selected_retained_count': value.selected_retained_count, 'display_limit': value.display_limit,
        'displayed_count': value.displayed_count, 'omitted_retained_count': value.omitted_retained_count,
        'source_authenticated': value.source_authenticated, 'execution_verified': value.execution_verified,
        'findings': [{'code': x.code, 'role': x.role, 'evidence_index': x.evidence_index} for x in value.findings]}
    nodes = 0
    def visit(obj: object, depth: int) -> None:
        nonlocal nodes
        nodes += 1
        _require(nodes <= MAX_NODES, 'limit_exceeded')
        if type(obj) in (dict, list): _require(depth + 1 <= MAX_DEPTH, 'limit_exceeded')
        if type(obj) is dict:
            for k, v in cast(dict[str, object], obj).items(): visit(k, depth + 1); visit(v, depth + 1)
        elif type(obj) is list:
            for v in cast(list[object], obj): visit(v, depth + 1)
    visit(root, 0)
    raw = json.dumps(root, sort_keys=True, separators=(',', ':'), ensure_ascii=True, allow_nan=False).encode('utf-8')
    _require(len(raw) <= MAX_BYTES, 'limit_exceeded')
    return raw


def encode_explanation(value: Explanation) -> bytes:
    _require(type(value) is Explanation)
    Explanation.__post_init__(value)
    return _encoded(value)


def explain_result(result: FeatureResult, receipt: ExecutionReceipt, configuration: ConfigSpec, *,
        entity: EntityKey, feature_id: str, inputs: tuple[tuple[str, CanonicalBatch], ...] = (),
        evidence_limit: int = 16) -> Explanation:
    """Validate supplied facts; reported references do not prove actual consumption."""
    _require(type(result) is FeatureResult and type(configuration) is ConfigSpec)
    _receipt_json(receipt); _entity(entity); _label(feature_id); _integer(evidence_limit, 64)
    _require(type(inputs) is tuple and len(inputs) <= 64, 'limit_exceeded')
    _require(type(result.values) is tuple and len(result.values) <= 256, 'limit_exceeded')
    _require(type(result.quality) is tuple and len(result.quality) <= 10000, 'limit_exceeded')
    _require(type(result.evidence) is tuple and len(result.evidence) <= 4096, 'limit_exceeded')
    entity_count = 0
    for column in result.values:
        _require(type(column) is FeatureColumn and type(column.entities) is tuple)
        entity_count += len(column.entities)
        _require(entity_count <= 10000, 'limit_exceeded')
    _require(configuration.schema_version == '1' and configuration.algorithm_version == 'v1'
        and result.metadata.schema_version == '1' and result.metadata.math_policy_version == 'v1', 'unsupported_version')
    _require(result.metadata.backend_id == 'python-exact' and result.metadata.backend_version in _LEGACY_BACKEND_VERSIONS, 'unsupported_version')
    try:
        config_fp = fingerprint_config(configuration); output_fp = fingerprint_result(result)
        total = config_fp.byte_length + output_fp.byte_length
        _require(total <= MAX_CONTENT_BYTES, 'limit_exceeded')
        meta = result.metadata
        _require(meta.namespace == configuration.session.namespace and meta.session_id == configuration.session.session_id
            and meta.availability == configuration.availability and meta.config_digest == configuration.digest
            and entity.session_id == meta.session_id, 'inconsistent_binding')
        FeatureResult(result.values, result.quality, result.metadata, result.evidence)
        registry = builtin_registry()
        for column in result.values:
            definition = registry.get(column.feature_id)
            _require(column.schema_version == '1' and column.algorithm_version == definition.algorithm_version == 'v1', 'unsupported_version')
            _require(len(definition.outputs) == 1 and column.dtype.value == definition.outputs[0].dtype
                and column.unit == definition.outputs[0].unit, 'inconsistent_binding')
        expected = make_receipt(result, configuration=config_fp, inputs=receipt.inputs, output=output_fp,
            formulas=tuple(FormulaBinding(x.feature_id, x.algorithm_version) for x in result.values),
            environment=receipt.environment, execution=receipt.execution, evidence=receipt.evidence)
        _require(expected == receipt, 'inconsistent_binding')
        supplied: dict[str, CanonicalBatch] = {}
        source_ids: set[str] = set()
        declared = {x.role: (x, binding) for x, binding in zip(receipt.inputs, meta.inputs, strict=True)}
        for pair in inputs:
            _require(type(pair) is tuple and len(pair) == 2)
            role, batch = pair; _label(role); _require(type(batch) is CanonicalBatch)
            _require(role not in supplied, 'duplicate')
            _require(role in declared, 'inconsistent_binding')
            fp = fingerprint_batch(batch); total += fp.byte_length
            _require(total <= MAX_CONTENT_BYTES, 'limit_exceeded')
            _require(batch.metadata.source.input_id not in source_ids, 'duplicate')
            reference, binding = declared[role]
            _require(fp == reference.content and binding.kind == batch.kind and binding.metadata == batch.metadata, 'inconsistent_binding')
            supplied[role] = batch; source_ids.add(batch.metadata.source.input_id)
        keys: set[tuple[EntityKey, str, str, str]] = set()
        retained: list[EvidenceReference] = []
        ids = {x.input_id for x in receipt.inputs}
        for index, row in enumerate(result.evidence):
            EvidenceReference(index, row)
            key = (row.entity, row.feature_id, row.input_id, row.row_id)
            _require(key not in keys, 'duplicate'); keys.add(key)
            _require(row.input_id in ids, 'inconsistent_binding')
            if row.entity == entity and row.feature_id == feature_id: retained.append(EvidenceReference(index, row))
        qualities = [q for q in result.quality if q.entity == entity and q.feature_id == feature_id]
        _require(len(qualities) == 1, 'inconsistent_binding')
        definition = registry.get(feature_id)
        return Explanation(receipt, entity, feature_id, definition.algorithm_version, definition.formula,
            definition.formula_document, qualities[0],
            tuple(InputSummary(binding, reference.content, reference.role in supplied)
                for reference, binding in zip(receipt.inputs, meta.inputs, strict=True)),
            tuple(retained[:evidence_limit]), len(retained), evidence_limit)
    except (EvidenceError, ContractError) as error:
        raise _mapped(error) from None
