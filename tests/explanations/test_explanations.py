"""Pre-code byte oracles, independent reported facts and content negatives."""
from dataclasses import replace, FrozenInstanceError
import hashlib
import json
from pathlib import Path
import sys
import unittest
from unittest.mock import patch
from equity_feature_contracts import (
    AvailabilitySpec, BatchMetadata, CanonicalBatch, Column, ConfigSpec, ContractError, Coverage,
    DataKind, EntityKey, EvidenceRow, FeatureColumn, FeatureResult, InputBinding,
    InputScope, Parameter, PriceUnit, QualityRow, Reason, ResultMetadata, SessionSpec,
    SourceBinding, Status, ValueType, WindowSpec, builtin_registry,
)
from equity_feature_evidence import (
    EnvironmentDeclaration, EvidenceDisclosure, ExecutionClaim, PackageVersion,
    make_content_receipt, make_receipt, fingerprint_config, fingerprint_result,
    fingerprint_batch, FormulaBinding,
)
from equity_feature_explanations import (
    Explanation, ExplanationError, ExplanationFinding, EvidenceReference, InputSummary,
    explain_result, encode_explanation,
)
from equity_feature_explanations import _explain as implementation


def fixture():
    entity = EntityKey('A', 'S'); fid = 'session.trade.count'
    cfg = ConfigSpec('explain-fixture', 'v1', (Parameter('eligibility_policy', 'example-v1'),),
        SessionSpec('demo', 'S', 100, 200, 'caller'), WindowSpec(1, 'S', ('P', 'S')),
        AvailabilitySpec(200, 210, 210), price_unit=PriceUnit(0, 'USD'))
    batch = CanonicalBatch(DataKind.TRADE, tuple(Column(n, v) for n, v in (
        ('instrument_id', ('A',) * 3), ('session_id', ('S',) * 3), ('event_ns', (110, 130, 160)),
        ('order_key', (1, 2, 3)), ('event_id', ('t1', 't2', 't3')), ('eligible', (True,) * 3),
        ('price', (100, 102, 101)), ('size', (2, 3, 5)), ('known_at_ns', (110, 130, 210)),
    )), BatchMetadata('demo', SourceBinding('synthetic', 'snapshot1', 'map1', 'trades1'),
        Coverage(3, 3, True), PriceUnit(0, 'USD'), scope=InputScope(100, 200, 'example-v1')))
    result = FeatureResult((FeatureColumn(fid, 'v1', ValueType.INT64, 'trades', (entity,), (3,)),),
        (QualityRow(entity, fid, Status.AVAILABLE, 3, 3),),
        ResultMetadata('demo', 'S', cfg.availability, cfg.digest,
            (InputBinding('trades', DataKind.TRADE, batch.metadata),), 'python-exact', '0.0.4a4'))
    return cfg, batch, result, receipt(cfg, batch, result), entity, fid


def receipt(cfg, batch, result, disclosure=None):
    return make_content_receipt(result, cfg, (('trades', batch),) if batch is not None else (),
        EnvironmentDeclaration('CPython', '3.12', 'hand-authored-fixture',
            (PackageVersion('equity-feature-contracts', '0.0.4a4'),)),
        ExecutionClaim(), disclosure or EvidenceDisclosure('not_supplied', 0))


def retained():
    cfg, batch, result, _, entity, fid = fixture()
    rows = (EvidenceRow(entity, fid, 'trades1', 't4', 200, 200, use='excluded', exclusion_reason=Reason.FUTURE_MARKET),
        EvidenceRow(entity, fid, 'trades1', 't1', 110, 110))
    result = replace(result, metadata=replace(result.metadata, evidence_limit=2), evidence=rows)
    return cfg, batch, result, receipt(cfg, batch, result, EvidenceDisclosure('retained_complete', 2, 2)), entity, fid


def lexical_stats(obj, depth=0):
    if isinstance(obj, dict):
        children = [lexical_stats(x, depth + 1) for pair in obj.items() for x in pair]
        return 1 + sum(n for n, _ in children), max([depth + 1] + [d for _, d in children])
    if isinstance(obj, list):
        children = [lexical_stats(x, depth + 1) for x in obj]
        return 1 + sum(n for n, _ in children), max([depth + 1] + [d for _, d in children])
    return 1, depth


class ExplanationTests(unittest.TestCase):
    def operation(self, values=None, **kwargs):
        cfg, batch, result, ref, entity, fid = values or fixture()
        return explain_result(result, ref, cfg, entity=entity, feature_id=fid,
            inputs=(('trades', batch),) if batch is not None else (), **kwargs)

    def rejects(self, code, call):
        with self.assertRaises(ExplanationError) as cm: call()
        self.assertEqual(cm.exception.code, code)
        self.assertEqual(str(cm.exception), 'Explanation rejected: ' + code)

    def test_independent_zero_reference_wire(self):
        expected = (Path(__file__).parents[2] / 'docs/stories/EQ-099_EXPLANATION_ORACLE.json').read_bytes()
        self.assertEqual((len(expected), hashlib.sha256(expected).hexdigest()),
            (3829, '12da2aa17eb6173a6846e825f425c2b526570a395946bd73967fbcc05587f0eb'))
        value = self.operation()
        self.assertEqual(encode_explanation(value), expected)
        self.assertEqual((value.displayed_count, value.omitted_retained_count), (0, 0))
        self.assertEqual(value.findings, (ExplanationFinding('global_evidence_not_supplied'),))

    def test_independent_retained_excluded_wire(self):
        expected = (Path(__file__).parents[2] / 'docs/stories/EQ-099_REFERENCE_ORACLE.json').read_bytes()
        self.assertEqual((len(expected), hashlib.sha256(expected).hexdigest()),
            (4180, '3513cdd0a60d855e34644b36ee67ca2728d2fdf69070a7a6c4dc6f7bf4e2da49'))
        value = self.operation(retained(), evidence_limit=1)
        self.assertEqual(encode_explanation(value), expected)
        self.assertEqual(value.evidence[0].index, 0)
        self.assertEqual(value.evidence[0].row.event_ns, 200)
        self.assertEqual(value.findings, (ExplanationFinding('reported_exclusion', evidence_index=0),
            ExplanationFinding('retained_detail_omitted')))

    def test_display_zero_omits_retained_not_missing_proof(self):
        value = self.operation(retained(), evidence_limit=0)
        self.assertEqual((value.selected_retained_count, value.displayed_count, value.omitted_retained_count), (2, 0, 2))
        self.assertEqual(value.findings, (ExplanationFinding('retained_detail_omitted'),))
        self.assertEqual(value.receipt.evidence.state, 'retained_complete')

    def test_global_disclosure_stays_global(self):
        cfg, batch, result, ref, entity, fid = retained()
        for disclosure, code in [(EvidenceDisclosure('truncated', 2, 8), 'global_evidence_truncated'),
                                 (EvidenceDisclosure('unknown', 2), 'global_evidence_unknown')]:
            ref = receipt(cfg, batch, result, disclosure)
            value = self.operation((cfg, batch, result, ref, entity, fid), evidence_limit=1)
            self.assertEqual(value.receipt.evidence, disclosure)
            self.assertEqual(value.omitted_retained_count, 1)
            self.assertIn(ExplanationFinding(code), value.findings)
            self.assertFalse(value.execution_verified); self.assertFalse(value.source_authenticated)

    def test_missing_supplied_content_retains_declaration(self):
        cfg, batch, result, ref, entity, fid = fixture()
        value = explain_result(result, ref, cfg, entity=entity, feature_id=fid)
        self.assertEqual(value.inputs[0].binding.metadata, batch.metadata)
        self.assertFalse(value.inputs[0].content_verified)
        self.assertEqual(value.findings[0], ExplanationFinding('input_content_unverified', 'trades'))

    def test_changed_value_same_metadata_rejected(self):
        cfg, batch, result, ref, entity, fid = fixture()
        changed = replace(batch, columns=tuple(replace(c, values=(2, 3, 6)) if c.name == 'size' else c for c in batch.columns))
        self.assertEqual(changed.metadata, batch.metadata)
        self.rejects('inconsistent_binding', lambda: self.operation((cfg, changed, result, ref, entity, fid)))

    def test_consistently_rebound_configuration_context_negatives(self):
        cfg, batch, result, ref, entity, fid = fixture()
        variants = (replace(cfg, identity='other'), replace(cfg, session=replace(cfg.session, namespace='other')),
            replace(cfg, session=replace(cfg.session, session_id='T'), window=replace(cfg.window, target_session_id='T', governed_sessions=('P', 'T'))),
            replace(cfg, availability=AvailabilitySpec(190, 210, 210)))
        for changed in variants:
            with self.subTest(changed=changed):
                rebound = make_receipt(result, configuration=fingerprint_config(changed), inputs=ref.inputs,
                    output=ref.output, formulas=ref.formulas, environment=ref.environment, execution=ref.execution, evidence=ref.evidence)
                self.rejects('inconsistent_binding', lambda: self.operation((changed, batch, result, rebound, entity, fid)))

    def test_configuration_version_refusal(self):
        cfg, batch, result, ref, entity, fid = fixture()
        self.rejects('unsupported_version', lambda: self.operation((replace(cfg, algorithm_version='v2'), batch, result, ref, entity, fid)))

    def test_output_mutation_same_metadata(self):
        cfg, batch, result, ref, entity, fid = fixture()
        changed = replace(result, values=(replace(result.values[0], values=(4,)),))
        self.assertEqual(changed.metadata, result.metadata)
        self.rejects('inconsistent_binding', lambda: self.operation((cfg, batch, changed, ref, entity, fid)))

    def test_rebound_unknown_policy_refusal(self):
        cfg, batch, result, ref, entity, fid = fixture()
        changed = replace(result, metadata=replace(result.metadata, math_policy_version='v2'))
        updated = receipt(cfg, batch, changed)
        self.rejects('unsupported_version', lambda: self.operation((cfg, batch, changed, updated, entity, fid)))

    def test_conflict_outside_display_prefix_rejected(self):
        cfg, batch, result, ref, entity, fid = retained()
        rows = (result.evidence[0], result.evidence[1], replace(result.evidence[1], known_at_ns=120))
        metadata = replace(result.metadata, evidence_limit=3)
        with self.assertRaises(ContractError): replace(result, metadata=metadata, evidence=rows)
        # Deliberately bypass normal frozen construction; old contracts already reject it.
        changed = object.__new__(FeatureResult)
        for name, value in [('values', result.values), ('quality', result.quality), ('metadata', metadata), ('evidence', rows)]:
            object.__setattr__(changed, name, value)
        updated = receipt(cfg, batch, changed, EvidenceDisclosure('retained_complete', 3, 3))
        self.rejects('duplicate', lambda: self.operation((cfg, batch, changed, updated, entity, fid), evidence_limit=1))

    def test_unknown_proof_with_zero_retained(self):
        cfg, batch, result, ref, entity, fid = fixture()
        for state, total in [('retained_complete', 0), ('unknown', None), ('not_supplied', None)]:
            updated = receipt(cfg, batch, result, EvidenceDisclosure(state, 0, total))
            value = self.operation((cfg, batch, result, updated, entity, fid))
            self.assertEqual((value.selected_retained_count, value.omitted_retained_count), (0, 0))
            self.assertEqual(value.receipt.evidence.state, state)

    def test_exact_focus(self):
        cfg, batch, result, ref, entity, fid = fixture()
        self.rejects('inconsistent_binding', lambda: self.operation((cfg, batch, result, ref, EntityKey('B', 'S'), fid)))
        self.rejects('inconsistent_binding', lambda: self.operation((cfg, batch, result, ref, EntityKey('A', 'T'), fid)))

    def test_bad_limits_and_exact_tuple(self):
        for limit in (True, False, -1, 65, 1.0, None):
            self.rejects('invalid_schema', lambda: self.operation(evidence_limit=limit))
        cfg, batch, result, ref, entity, fid = fixture()
        self.rejects('limit_exceeded', lambda: explain_result(result, ref, cfg, entity=entity, feature_id=fid, inputs=[]))

    def test_duplicate_and_unknown_supplied_roles(self):
        cfg, batch, result, ref, entity, fid = fixture()
        self.rejects('duplicate', lambda: explain_result(result, ref, cfg, entity=entity, feature_id=fid,
            inputs=(('trades', batch), ('trades', batch))))
        self.rejects('inconsistent_binding', lambda: explain_result(result, ref, cfg, entity=entity, feature_id=fid,
            inputs=(('other', batch),)))

    def test_direct_constructor_contradictions(self):
        value = self.operation(retained(), evidence_limit=1)
        for change in ({'display_limit': 0}, {'selected_retained_count': 0}, {'source_authenticated': True},
            {'execution_verified': 0}, {'formula': 'invented'}, {'entity': EntityKey('B', 'S')},
            {'evidence': (replace(value.evidence[0], index=2),)}):
            with self.subTest(change=change), self.assertRaises(ExplanationError): replace(value, **change)
        with self.assertRaises(FrozenInstanceError): value.display_limit = 0

    def test_finding_closed_grammar(self):
        for args in [('unknown',), ('reported_exclusion',), ('retained_detail_omitted', 'trades'),
            ('input_content_unverified', None), ('reported_exclusion', None, True)]:
            with self.assertRaises(ExplanationError): ExplanationFinding(*args)

    def test_exact_byte_node_depth_limits(self):
        value = self.operation(retained(), evidence_limit=1)
        raw = encode_explanation(value); nodes, depth = lexical_stats(json.loads(raw))
        with patch.object(implementation, 'MAX_BYTES', len(raw)), patch.object(implementation, 'MAX_NODES', nodes), patch.object(implementation, 'MAX_DEPTH', depth):
            self.assertEqual(encode_explanation(value), raw)
        for name, bound in [('MAX_BYTES', len(raw) - 1), ('MAX_NODES', nodes - 1), ('MAX_DEPTH', depth - 1)]:
            with patch.object(implementation, name, bound): self.rejects('limit_exceeded', lambda: encode_explanation(value))

    def test_aggregate_content_budget(self):
        cfg, batch, result, ref, entity, fid = fixture()
        size = ref.configuration.byte_length + ref.output.byte_length + ref.inputs[0].content.byte_length
        with patch.object(implementation, 'MAX_CONTENT_BYTES', size): self.operation()
        with patch.object(implementation, 'MAX_CONTENT_BYTES', size - 1): self.rejects('limit_exceeded', self.operation)

    def test_unchanged_facts_and_no_calculator_import(self):
        values = retained(); before = tuple(repr(x) for x in values)
        imports = set(sys.modules)
        value = self.operation(values, evidence_limit=1)
        self.assertEqual(tuple(repr(x) for x in values), before)
        self.assertFalse(any(n == 'equity_features' or n.startswith('equity_features.') for n in set(sys.modules) - imports))
        self.assertEqual(value.quality, values[2].quality[0])

    def test_actual_optional_producer_missing_empty_partial(self):
        try:
            from equity_features.session import compute_trades
        except ImportError:
            self.skipTest('Optional actual calculator is absent in light consumer')
        cfg, batch, _, _, entity, fid = fixture()
        variants = [None, replace(batch, columns=tuple(replace(c, values=()) for c in batch.columns),
            metadata=replace(batch.metadata, coverage=Coverage(0, 0, True))),
            replace(batch, columns=tuple(replace(c, values=c.values[:2]) for c in batch.columns),
                metadata=replace(batch.metadata, coverage=Coverage(3, 2, False)))]
        expected = [(Status.MISSING_INPUT, None, 0, (Reason.ABSENT_INPUT,)),
            (Status.AVAILABLE, 0, 0, ()), (Status.INCOMPLETE_COVERAGE, 3, 2, (Reason.GOVERNED_GAP,))]
        for supplied, target in zip(variants, expected, strict=True):
            result = compute_trades(supplied, cfg, entity=entity)
            ref = receipt(cfg, supplied, result)
            value = self.operation((cfg, supplied, result, ref, entity, fid))
            q = value.quality
            self.assertEqual((q.status, q.expected, q.observed, q.reasons), target)
            if supplied is not None and supplied.row_count == 0:
                vwap = explain_result(result, ref, cfg, entity=entity, feature_id='session.trade.vwap')
                self.assertEqual((vwap.quality.status, vwap.quality.reasons),
                    (Status.NOT_APPLICABLE, (Reason.NO_ELIGIBLE_OBSERVATIONS,)))

    def test_independent_seven_state_matrix(self):
        matrix = json.loads((Path(__file__).parents[2] / 'docs/stories/EQ-099_COUNT_ORACLE.json').read_bytes())
        cfg, batch, base, _, entity, fid = fixture()
        other = 'session.trade.volume'
        columns = base.values + (FeatureColumn(other, 'v1', ValueType.INT64, 'shares', (entity,), (10,)),)
        qualities = base.quality + (replace(base.quality[0], feature_id=other),)
        for state, global_count, total, focused, limit, displayed, omitted in matrix['cases']:
            with self.subTest(state=state, focused=focused, limit=limit):
                rows = tuple(EvidenceRow(entity, fid if i < focused else other, 'trades1', 't' + str(i + 1), 110 + i * 10, 110 + i * 10) for i in range(global_count))
                result = FeatureResult(columns, qualities, replace(base.metadata, evidence_limit=global_count), rows)
                ref = receipt(cfg, batch, result, EvidenceDisclosure(state, global_count, total))
                value = self.operation((cfg, batch, result, ref, entity, fid), evidence_limit=limit)
                self.assertEqual((value.selected_retained_count, value.displayed_count, value.omitted_retained_count), (focused, displayed, omitted))
                self.assertEqual(value.receipt.evidence.state, state)
                self.assertEqual(value.receipt.evidence.total_count, total)

    def test_excluded_knowledge_boundaries_are_reported_verbatim(self):
        cfg, batch, base, _, entity, fid = fixture()
        for known, reason in [(None, Reason.UNKNOWN_AVAILABILITY), (211, Reason.FUTURE_KNOWLEDGE)]:
            row = EvidenceRow(entity, fid, 'trades1', 'reported', 110, known, use='excluded', exclusion_reason=reason)
            result = replace(base, metadata=replace(base.metadata, evidence_limit=1), evidence=(row,))
            ref = receipt(cfg, batch, result, EvidenceDisclosure('retained_complete', 1, 1))
            value = self.operation((cfg, batch, result, ref, entity, fid))
            self.assertEqual(value.evidence[0].row, row)
            self.assertEqual(value.findings, (ExplanationFinding('reported_exclusion', evidence_index=0),))
            with self.assertRaises(ContractError): replace(result, evidence=(replace(row, use='consumed', exclusion_reason=None),))

    def test_consistent_input_hash_with_conflicting_result_metadata(self):
        cfg, batch, result, ref, entity, fid = fixture()
        changed = replace(batch, metadata=replace(batch.metadata, price_unit=PriceUnit(2, 'USD')))
        updated = replace(ref, inputs=(replace(ref.inputs[0], content=fingerprint_batch(changed)),))
        self.rejects('inconsistent_binding', lambda: self.operation((cfg, changed, result, updated, entity, fid)))

    def test_all_result_column_versions_and_backend(self):
        cfg, batch, result, _, entity, fid = fixture()
        variants = [replace(result, metadata=replace(result.metadata, backend_version='next')),
            replace(result, values=(replace(result.values[0], algorithm_version='v2'),))]
        for result in variants:
            updated = receipt(cfg, batch, result)
            self.rejects('unsupported_version', lambda: self.operation((cfg, batch, result, updated, entity, fid)))

    def test_closed_public_record_subclasses(self):
        class SubFinding(ExplanationFinding): pass
        class SubReference(EvidenceReference): pass
        class SubSummary(InputSummary): pass
        class SubExplanation(Explanation): pass
        value = self.operation(retained(), evidence_limit=1)
        self.rejects('invalid_schema', lambda: SubFinding('result_unavailable'))
        self.rejects('invalid_schema', lambda: SubReference(0, value.evidence[0].row))
        self.rejects('invalid_schema', lambda: SubSummary(value.inputs[0].binding, value.inputs[0].content, True))
        self.rejects('invalid_schema', lambda: SubExplanation(value.receipt, value.entity, value.feature_id,
            value.formula_version, value.formula, value.formula_document, value.quality, value.inputs,
            value.evidence, value.selected_retained_count, value.display_limit))

    def test_focused_and_unfocused_catalog_dtype_units(self):
        cfg, batch, base, _, entity, fid = fixture()
        focused = base.values[0]
        other_id = 'session.trade.volume'
        other = FeatureColumn(other_id, 'v1', ValueType.INT64, 'shares', (entity,), (10,))
        other_quality = replace(base.quality[0], feature_id=other_id)
        cases = [((replace(focused, dtype=ValueType.STRING, values=('3',)),), base.quality),
            ((replace(focused, unit='invented'),), base.quality),
            ((focused, replace(other, dtype=ValueType.FLOAT64, values=(10.0,))), base.quality + (other_quality,)),
            ((focused, replace(other, unit='invented')), base.quality + (other_quality,))]
        for columns, quality in cases:
            with self.subTest(columns=columns):
                result = replace(base, values=columns, quality=quality)
                updated = receipt(cfg, batch, result)
                self.rejects('inconsistent_binding', lambda: self.operation((cfg, batch, result, updated, entity, fid)))


if __name__ == '__main__': unittest.main()
