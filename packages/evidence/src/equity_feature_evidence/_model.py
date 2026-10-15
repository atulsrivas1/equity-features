"""Closed immutable receipt declarations; no acquisition or execution authority."""
from __future__ import annotations

from dataclasses import dataclass
import json
import re
from equity_feature_contracts import inputs as i, results as r, specs as s

MAX_BYTES = 1048576
MAX_NODES = 32768
MAX_DEPTH = 16


class EvidenceError(ValueError):
    """Fixed, payload-free receipt error with a stable code."""

    def __init__(self, code: str = 'invalid_schema') -> None:
        if type(code) is not str or code not in ('invalid_schema', 'unsupported_version', 'inconsistent_binding', 'duplicate', 'limit_exceeded'):
            code = 'invalid_schema'
        self.code = code
        super().__init__('Receipt rejected: ' + code)


def require(condition: bool, code: str = 'invalid_schema') -> None:
    if not condition:
        raise EvidenceError(code)


def label(value: object) -> None:
    require(type(value) is str)
    assert isinstance(value, str)
    require(bool(value.strip()))
    require(len(value) <= 256, 'limit_exceeded')
    require(not any(ord(c) < 32 or 127 <= ord(c) <= 159 or 0xD800 <= ord(c) <= 0xDFFF for c in value))
    require(len(value.encode('utf-8')) <= 1024, 'limit_exceeded')


def integer(value: object, *, nonnegative: bool = False) -> None:
    require(type(value) is int)
    assert isinstance(value, int)
    require((0 if nonnegative else i.I64_MIN) <= value <= i.I64_MAX)


def sequence(value: object, member: type[object], maximum: int) -> tuple[object, ...]:
    require(type(value) in (tuple, list))
    assert isinstance(value, (tuple, list))
    require(len(value) <= maximum, 'limit_exceeded')
    require(all(type(item) is member for item in value))
    return tuple(value)


@dataclass(frozen=True)
class ContentFingerprint:
    domain: str
    digest: str
    byte_length: int
    schema_version: str = '1'
    canonicalization: str = 'typed-json-v1'
    algorithm: str = 'sha256'

    def __post_init__(self) -> None:
        require(type(self.domain) is str and self.domain in ('canonical_batch', 'feature_result', 'configuration'))
        require(type(self.digest) is str and re.fullmatch('[0-9a-f]{64}', self.digest) is not None)
        integer(self.byte_length, nonnegative=True)
        require(type(self.schema_version) is str and self.schema_version == '1', 'unsupported_version')
        require(type(self.canonicalization) is str and self.canonicalization == 'typed-json-v1', 'unsupported_version')
        require(type(self.algorithm) is str and self.algorithm == 'sha256', 'unsupported_version')


@dataclass(frozen=True)
class InputFingerprint:
    role: str
    input_id: str
    content: ContentFingerprint

    def __post_init__(self) -> None:
        label(self.role); label(self.input_id)
        require(type(self.content) is ContentFingerprint and self.content.domain == 'canonical_batch')


@dataclass(frozen=True)
class FormulaBinding:
    feature_id: str
    formula_version: str

    def __post_init__(self) -> None:
        label(self.feature_id); label(self.formula_version)


@dataclass(frozen=True)
class PackageVersion:
    name: str
    version: str

    def __post_init__(self) -> None:
        label(self.name); label(self.version)


@dataclass(frozen=True)
class EnvironmentDeclaration:
    python_implementation: str
    python_version: str
    platform: str
    packages: tuple[PackageVersion, ...]

    def __post_init__(self) -> None:
        for text in (self.python_implementation, self.python_version, self.platform): label(text)
        sequence(self.packages, PackageVersion, 64)
        require(bool(self.packages))
        object.__setattr__(self, 'packages', tuple(sorted(self.packages, key=lambda p: p.name)))
        require(len({p.name for p in self.packages}) == len(self.packages), 'duplicate')


@dataclass(frozen=True)
class ExecutionClaim:
    executed_at_ns: int | None = None
    clock_source: str | None = None
    uncertainty_ns: int | None = None

    def __post_init__(self) -> None:
        if self.executed_at_ns is not None: integer(self.executed_at_ns)
        if self.clock_source is not None: label(self.clock_source)
        if self.uncertainty_ns is not None: integer(self.uncertainty_ns, nonnegative=True)
        require(self.executed_at_ns is not None or (self.clock_source is None and self.uncertainty_ns is None))


@dataclass(frozen=True)
class EvidenceDisclosure:
    state: str
    retained_count: int
    total_count: int | None = None

    def __post_init__(self) -> None:
        require(type(self.state) is str and self.state in ('retained_complete', 'truncated', 'not_supplied', 'unknown'))
        integer(self.retained_count, nonnegative=True)
        if self.total_count is not None: integer(self.total_count, nonnegative=True)
        if self.state == 'retained_complete': require(self.total_count == self.retained_count)
        elif self.state == 'truncated': require(self.total_count is not None and self.total_count > self.retained_count)
        elif self.state == 'not_supplied': require(self.retained_count == 0 and self.total_count is None)
        else: require(self.total_count is None)


@dataclass(frozen=True)
class ExecutionReceipt:
    metadata: r.ResultMetadata
    configuration: ContentFingerprint
    inputs: tuple[InputFingerprint, ...]
    output: ContentFingerprint
    formulas: tuple[FormulaBinding, ...]
    environment: EnvironmentDeclaration
    execution: ExecutionClaim
    evidence: EvidenceDisclosure
    schema_version: str = '1'
    canonicalization: str = 'receipt-json-v1'
    domain: str = 'equity-feature.execution-receipt'

    def __post_init__(self) -> None:
        require(type(self.schema_version) is str and self.schema_version == '1', 'unsupported_version')
        require(type(self.canonicalization) is str and self.canonicalization == 'receipt-json-v1', 'unsupported_version')
        require(type(self.domain) is str and self.domain == 'equity-feature.execution-receipt')
        require(type(self.metadata) is r.ResultMetadata)
        require(type(self.configuration) is ContentFingerprint and self.configuration.domain == 'configuration')
        require(type(self.output) is ContentFingerprint and self.output.domain == 'feature_result')
        require(type(self.environment) is EnvironmentDeclaration and type(self.execution) is ExecutionClaim and type(self.evidence) is EvidenceDisclosure)
        # Bounds precede list copying/sorting; contract metadata is borrowed only as immutable tuples.
        sequence(self.inputs, InputFingerprint, 64); sequence(self.formulas, FormulaBinding, 256)
        require(type(self.metadata.inputs) is tuple and len(self.metadata.inputs) <= 64, 'limit_exceeded')
        validate_tree(self)
        object.__setattr__(self, 'inputs', tuple(sorted(self.inputs, key=lambda x: x.role)))
        object.__setattr__(self, 'formulas', tuple(sorted(self.formulas, key=lambda x: x.feature_id)))
        require(len({x.role for x in self.inputs}) == len(self.inputs), 'duplicate')
        require(len({x.input_id for x in self.inputs}) == len(self.inputs), 'duplicate')
        require(len({x.feature_id for x in self.formulas}) == len(self.formulas), 'duplicate')
        actual = {(x.role, x.input_id) for x in self.inputs}
        expected = {(x.role, x.metadata.source.input_id) for x in self.metadata.inputs}
        require(actual == expected, 'inconsistent_binding')


def record_fields(value: object) -> tuple[tuple[str, object], ...]:
    """Explicit fixed projection; no reflection, object dictionaries or class discovery."""
    if type(value) is ExecutionReceipt:
        return (('domain', value.domain), ('schema_version', value.schema_version), ('canonicalization', value.canonicalization), ('metadata', value.metadata), ('configuration', value.configuration), ('inputs', value.inputs), ('output', value.output), ('formulas', value.formulas), ('environment', value.environment), ('execution', value.execution), ('evidence', value.evidence))
    if type(value) is ContentFingerprint:
        return (('domain', value.domain), ('schema_version', value.schema_version), ('canonicalization', value.canonicalization), ('algorithm', value.algorithm), ('digest', value.digest), ('byte_length', value.byte_length))
    if type(value) is InputFingerprint: return (('role', value.role), ('input_id', value.input_id), ('content', value.content))
    if type(value) is FormulaBinding: return (('feature_id', value.feature_id), ('formula_version', value.formula_version))
    if type(value) is PackageVersion: return (('name', value.name), ('version', value.version))
    if type(value) is EnvironmentDeclaration: return (('python_implementation', value.python_implementation), ('python_version', value.python_version), ('platform', value.platform), ('packages', value.packages))
    if type(value) is ExecutionClaim: return (('executed_at_ns', value.executed_at_ns), ('clock_source', value.clock_source), ('uncertainty_ns', value.uncertainty_ns))
    if type(value) is EvidenceDisclosure: return (('state', value.state), ('retained_count', value.retained_count), ('total_count', value.total_count))
    if type(value) is r.ResultMetadata:
        require(type(value.inputs) is tuple and len(value.inputs) <= 64, 'limit_exceeded')
        return (('namespace', value.namespace), ('session_id', value.session_id), ('availability', value.availability), ('config_digest', value.config_digest), ('inputs', value.inputs), ('backend_id', value.backend_id), ('backend_version', value.backend_version), ('evidence_limit', value.evidence_limit), ('schema_version', value.schema_version), ('math_policy_version', value.math_policy_version))
    if type(value) is s.AvailabilitySpec: return (('market_cutoff_ns', value.market_cutoff_ns), ('knowledge_cutoff_ns', value.knowledge_cutoff_ns), ('evaluation_ns', value.evaluation_ns), ('mode', value.mode), ('reconstruction_reason', value.reconstruction_reason))
    if type(value) is r.InputBinding: return (('role', value.role), ('kind', value.kind), ('metadata', value.metadata), ('schema_version', value.schema_version))
    if type(value) is i.BatchMetadata:
        require(type(value.interval_coverage) is tuple and len(value.interval_coverage) <= 256, 'limit_exceeded')
        return (('namespace', value.namespace), ('source', value.source), ('coverage', value.coverage), ('price_unit', value.price_unit), ('adjustment', value.adjustment), ('sampling', value.sampling), ('quantity_unit', value.quantity_unit), ('ordering', value.ordering), ('duplicate_policy', value.duplicate_policy), ('scope', value.scope), ('interval_coverage', value.interval_coverage))
    if type(value) is i.SourceBinding: return (('source_id', value.source_id), ('snapshot_id', value.snapshot_id), ('mapping_version', value.mapping_version), ('input_id', value.input_id))
    if type(value) is i.Coverage: return (('expected', value.expected), ('observed', value.observed), ('complete', value.complete))
    if type(value) is i.PriceUnit: return (('scale', value.scale), ('currency', value.currency))
    if type(value) is i.AdjustmentSpec: return (('basis', value.basis), ('policy_version', value.policy_version), ('action_snapshot', value.action_snapshot), ('anchor', value.anchor))
    if type(value) is i.InputScope: return (('start_ns', value.start_ns), ('end_ns', value.end_ns), ('eligibility_policy', value.eligibility_policy), ('include_opening_auction', value.include_opening_auction), ('include_closing_auction', value.include_closing_auction))
    if type(value) is i.IntervalCoverage: return (('name', value.name), ('start_ns', value.start_ns), ('end_ns', value.end_ns), ('coverage', value.coverage))
    raise EvidenceError()


def validate_tree(value: object) -> None:
    """Budget the fixed shape before allocating its JSON projection."""
    nodes = 0
    size = 0

    def charge(count: int) -> None:
        nonlocal size
        size += count
        require(size <= MAX_BYTES, 'limit_exceeded')

    def visit(item: object, depth: int) -> None:
        nonlocal nodes
        nodes += 1
        require(nodes <= MAX_NODES, 'limit_exceeded')
        if item is None: charge(4); return
        if type(item) is bool: charge(4 if item else 5); return
        if type(item) is int: integer(item); charge(len(str(item))); return
        if type(item) is str: label(item); charge(len(json.dumps(item, ensure_ascii=True))); return
        if type(item) is i.DataKind: label(item.value); charge(len(json.dumps(item.value))); return
        require(depth < MAX_DEPTH, 'limit_exceeded')
        if type(item) in (tuple, list):
            assert isinstance(item, (tuple, list))
            charge(2 + max(0, len(item) - 1))
            # Lists are allowed only for receipt collections before their bounded copy.
            for child in item: visit(child, depth + 1)
            return
        fields = record_fields(item)
        charge(2 + max(0, len(fields) - 1) + len(fields))
        for key, child in fields:
            visit(key, depth + 1); visit(child, depth + 1)

    visit(value, 0)


def make_receipt(result: r.FeatureResult, *, configuration: ContentFingerprint,
                 inputs: tuple[InputFingerprint, ...], output: ContentFingerprint,
                 formulas: tuple[FormulaBinding, ...], environment: EnvironmentDeclaration,
                 execution: ExecutionClaim, evidence: EvidenceDisclosure) -> ExecutionReceipt:
    """Bind declarations to the supplied result; content is NOT recomputed here."""
    require(type(result) is r.FeatureResult)
    sequence(formulas, FormulaBinding, 256)
    require({(x.feature_id, x.formula_version) for x in formulas} == {(x.feature_id, x.algorithm_version) for x in result.values}, 'inconsistent_binding')
    require(type(evidence) is EvidenceDisclosure and evidence.retained_count == len(result.evidence), 'inconsistent_binding')
    return ExecutionReceipt(result.metadata, configuration, inputs, output, formulas, environment, execution, evidence)
