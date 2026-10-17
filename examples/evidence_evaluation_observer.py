"""Generic supplied-evidence observer for EQ117; no fixture or expected-answer access.

Trusted local files, not a sandbox or authenticity service. No calculation I/O.
Producer declarations and independently recomputed findings stay separate.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import re
import stat
from typing import Any

import equity_feature_agent_evidence as events
import equity_feature_agent_ledger as ledger
import equity_feature_contracts as contracts
from equity_feature_bundles import BundleError, read_bundle
from equity_feature_bundles.replay import replay_bundle
from equity_feature_diagnostics import DecisionContext, DiagnosticPolicy, KnowledgeCheck, evaluate_diagnostics
from equity_feature_evidence import canonical_content, encode_receipt, fingerprint_batch, fingerprint_config, fingerprint_result
from equity_feature_explanations import encode_explanation, explain_result

ARMS = ('ordinary_log', 'evidence_ledger')
COMMON = {'bundle.zip', 'task.json', 'declared-reports.json', 'terminal.json'}
CAPS = {'bundle.zip': 1048576, 'task.json': 4096, 'declared-reports.json': 65536,
        'terminal.json': 16384, 'plain-log.json': 32768, 'events.json': 131072,
        'export.json': 131072}


class ObservationError(ValueError):
    def __init__(self, code: str = 'invalid_evidence') -> None:
        self.code = code
        super().__init__(code)


def require(condition: bool, code: str = 'invalid_evidence') -> None:
    if not condition:
        raise ObservationError(code)


def encoded(value: Any, *, lf: bool = True) -> bytes:
    return (json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=True,
                       allow_nan=False) + ('\n' if lf else '')).encode('ascii')


def _pairs(values: list[tuple[str, Any]]) -> dict[str, Any]:
    out: dict[str, Any] = {}
    for key, value in values:
        require(key not in out, 'duplicate_key')
        out[key] = value
    return out


def parsed(raw: bytes, *, lf: bool = True) -> Any:
    require(type(raw) is bytes and raw.isascii())
    try:
        value = json.loads(raw, object_pairs_hook=_pairs,
                           parse_constant=lambda _: (_ for _ in ()).throw(ObservationError()))
    except (ValueError, UnicodeError, RecursionError):
        raise ObservationError('invalid_json') from None
    require(encoded(value, lf=lf) == raw, 'noncanonical_json')
    return value


def shape(value: Any, keys: set[str]) -> dict[str, Any]:
    require(type(value) is dict and set(value) == keys)
    return value


def digest(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def hash_verify(raw: bytes, wanted: str, length: int) -> bool:
    require(type(wanted) is str and re.fullmatch('[0-9a-f]{64}', wanted) is not None)
    require(type(length) is int and length >= 0)
    return len(raw) == length and digest(raw) == wanted


def read_file(path: Path) -> bytes:
    require(path.name in CAPS and stat.S_ISREG(path.lstat().st_mode), 'invalid_file')
    with path.open('rb') as stream:
        raw = stream.read(CAPS[path.name] + 1)
    require(len(raw) <= CAPS[path.name], 'limit_exceeded')
    return raw


def fp(value: Any) -> dict[str, Any]:
    return {k: getattr(value, k) for k in ('domain', 'digest', 'byte_length', 'schema_version',
                                         'canonicalization', 'algorithm')}


def strict_projection(report: Any) -> dict[str, Any]:
    context = report.context
    out = {k: getattr(report, k) for k in ('schema_version', 'requested_count', 'passed_count',
        'failed_count', 'unknown_count', 'assessed_count', 'unknown_prerequisite_count',
        'admission', 'source_authenticated', 'historical_acquisition_verified')}
    out.update(context=dict(namespace=context.namespace,
        entity=dict(instrument_id=context.entity.instrument_id, session_id=context.entity.session_id),
        availability={k: getattr(context.availability, k) for k in ('market_cutoff_ns',
            'knowledge_cutoff_ns', 'evaluation_ns', 'mode', 'reconstruction_reason')}),
        policy={k: getattr(report.policy, k) for k in ('policy_id', 'mode', 'unknown_action')},
        not_requested=list(report.not_requested), findings=[])
    for finding in report.findings:
        row = {k: getattr(finding, k) for k in ('check_id', 'subject_id', 'kind', 'status',
                'severity', 'assessed', 'unknown_prerequisites', 'age_ns')}
        row.update(content=None if finding.content is None else fp(finding.content), reasons=list(finding.reasons))
        out['findings'].append(row)
    return out


def _declared_report(value: Any, bundle: Any, entity: Any) -> dict[str, Any]:
    keys = {'schema_version', 'requested_count', 'passed_count', 'failed_count', 'unknown_count',
        'assessed_count', 'unknown_prerequisite_count', 'admission', 'source_authenticated',
        'historical_acquisition_verified', 'context', 'policy', 'findings', 'not_requested'}
    report = shape(value, keys)
    require(report['schema_version'] == '1' and report['source_authenticated'] is False
            and report['historical_acquisition_verified'] is False)
    require(report['policy'] == dict(policy_id='eq116-known-rows', mode='strict', unknown_action='deny'))
    context = dict(namespace=bundle.result.metadata.namespace,
        entity=dict(instrument_id=entity.instrument_id, session_id=entity.session_id),
        availability={k: getattr(bundle.configuration.availability, k) for k in (
            'market_cutoff_ns', 'knowledge_cutoff_ns', 'evaluation_ns', 'mode', 'reconstruction_reason')})
    require(report['context'] == context, 'context_mismatch')
    require(type(report['findings']) is list and len(report['findings']) <= 16)
    counters = ('requested_count', 'passed_count', 'failed_count', 'unknown_count', 'assessed_count', 'unknown_prerequisite_count')
    require(all(type(report[k]) is int and 0 <= report[k] <= 64 for k in counters))
    require(report['requested_count'] == len(report['findings']))
    for item in report['findings']:
        shape(item, {'check_id', 'subject_id', 'kind', 'status', 'severity', 'assessed',
                     'unknown_prerequisites', 'age_ns', 'content', 'reasons'})
        require(item['kind'] == 'knowledge_time' and item['status'] in ('passed', 'failed', 'unknown'))
        require(type(item['assessed']) is bool and type(item['unknown_prerequisites']) is int)
        require(type(item['check_id']) is str and len(item['check_id']) <= 128)
        require(type(item['subject_id']) is str and len(item['subject_id']) <= 128)
        require(type(item['reasons']) is list and len(item['reasons']) <= 16)
        require(item['content'] == fp(bundle.inputs[0].content), 'content_mismatch')
    require(report['passed_count'] == sum(x['status'] == 'passed' for x in report['findings']))
    require(report['failed_count'] == sum(x['status'] == 'failed' for x in report['findings']))
    require(report['unknown_count'] == sum(x['status'] == 'unknown' for x in report['findings']))
    require(report['assessed_count'] == sum(x['assessed'] for x in report['findings']))
    wanted_admission = 'denied' if report['failed_count'] or report['unknown_count'] else 'admitted'
    require(report['admission'] == wanted_admission)
    return report


def recompute_strict(bundle: Any, entity: Any) -> dict[str, Any] | None:
    require(len(bundle.inputs) == 1 and bundle.inputs[0].role == 'trades')
    retained = bundle.inputs[0].batch
    if retained is None:
        return None
    columns = {column.name: column.values for column in retained.columns}
    require('known_at_ns' in columns and 'event_id' in columns)
    known, ids = columns['known_at_ns'], columns['event_id']
    require(0 < len(known) == len(ids) <= 16)
    checks = tuple(KnowledgeCheck('known-' + str(i + 1), bundle.inputs[0].input_id + ':' + row_id,
                    stamp, content=fingerprint_batch(retained))
                   for i, (stamp, row_id) in enumerate(zip(known, ids, strict=True)))
    return strict_projection(evaluate_diagnostics(
        DecisionContext(bundle.result.metadata.namespace, entity, bundle.configuration.availability),
        DiagnosticPolicy('eq116-known-rows', 'strict', 'deny'), checks))


def assessment(result: Any, narrative: str) -> tuple[str, str]:
    require(type(narrative) is str and narrative.isascii() and len(narrative) <= 128)
    selected = [x for x in result.values if x.feature_id == 'session.trade.count']
    require(len(selected) == 1 and len(selected[0].values) == 1)
    count = selected[0].values[0]
    if count is None:
        return 'unavailable', 'DEFER'
    require(type(count) is int and count >= 0)
    match = re.fullmatch(r'session\.trade\.count=(0|[1-9][0-9]*)', narrative)
    if match is None:
        return 'unsupported', 'DEFER'
    return ('matched', 'DEFER') if int(match.group(1)) == count else ('mismatch', 'REJECT')


def _plain(directory: Path, bundle: Any, task: dict[str, Any], reports: dict[str, Any], terminal: dict[str, Any]) -> tuple[str, str]:
    raw = read_file(directory / 'plain-log.json')
    rows = parsed(raw)
    require(type(rows) is list and 1 <= len(rows) <= 8)
    kinds = ('request', 'model', 'calculation_call', 'calculation_result', 'diagnostic_call',
             'diagnostic_result', 'feature_read', 'decision')
    case_id = rows[0]['case_id']
    require(type(case_id) is str and len(case_id) <= 128)
    for index, row in enumerate(rows):
        shape(row, {'schema', 'case_id', 'sequence', 'kind', 'facts'})
        require(row['schema'] == 'eq116.plain.v1' and row['case_id'] == case_id
                and type(row['sequence']) is int and row['sequence'] == index + 1 and row['kind'] == kinds[index])
    require(len(rows) >= 7)
    context, strict = reports['strict']['context'], reports['strict']
    cf, inf, rf = fp(fingerprint_config(bundle.configuration)), fp(bundle.inputs[0].content), fp(fingerprint_result(bundle.result))
    expected = [dict(request_key=case_id, objective='inspect supplied trade count', narrative=task['narrative'], context=context),
        None,
        dict(request_sequence=1, tool='compute_trades', version='0.0.4a4', configuration=cf, input=inf),
        dict(call_sequence=3, outcome='succeeded', output=rf, payload=canonical_content(bundle.result).decode('ascii')),
        dict(request_sequence=1, tool='evaluate_diagnostics', version='0.1.0a1', input=inf, policy=strict['policy']),
        dict(call_sequence=5, outcome='succeeded', report=strict),
        dict(result_sequence=4, configuration=cf, input=inf, output=rf, receipt=encode_receipt(bundle.receipt).decode('ascii'),
             feature_ids=['session.trade.count'], context=context)]
    for row, want in zip(rows[:7], expected, strict=True):
        if want is not None:
            require(encoded(row['facts']) == encoded(want), 'plain_content_mismatch')
    model = shape(rows[1]['facts'], {'provider', 'model', 'version', 'identity_state'})
    declaration = events.ModelSubject(model['provider'], model['model'], model['version'], events.ModelIdentityState(model['identity_state']))
    if len(rows) == 8:
        decision = shape(rows[-1]['facts'], {'request_sequence', 'feature_read_sequences', 'action', 'reason_code'})
        require(decision['request_sequence'] == 1 and decision['feature_read_sequences'] == [7])
        require(decision['action'] in ('DEFER', 'REJECT') and type(decision['reason_code']) is str)
    shape(terminal, {'record_count', 'byte_length', 'digest'})
    require(type(terminal['record_count']) is int and len(rows) <= terminal['record_count'] <= 8)
    require(type(terminal['byte_length']) is int and 0 <= terminal['byte_length'] <= 32768)
    require(type(terminal['digest']) is str and re.fullmatch('[0-9a-f]{64}', terminal['digest']) is not None)
    if len(rows) < terminal['record_count']:
        anchor = 'not_covered'
    else:
        require(hash_verify(raw, terminal['digest'], terminal['byte_length']), 'anchor_mismatch')
        anchor = 'matched_terminal'
    require(read_file(directory / 'export.json') == raw, 'export_mismatch')
    return anchor, declaration.identity_state.value


def _events(directory: Path, bundle: Any, task: dict[str, Any], reports: dict[str, Any], terminal: dict[str, Any]) -> tuple[str, str]:
    expected = ledger.Checkpoint(**shape(terminal, {'chain_id', 'sequence', 'head_hash'}))
    values = parsed(read_file(directory / 'events.json'))
    require(type(values) is list and 7 <= len(values) <= 8)
    trace = tuple(events.decode_event(encoded(v, lf=False)) for v in values)
    checked = ledger.verify_events(trace, chain_id=expected.chain_id, expected=expected)
    kinds = (events.RequestSubject, events.ModelSubject, events.ToolCallSubject,
             events.ToolResultSubject, events.ToolCallSubject, events.ToolResultSubject,
             events.FeatureReadSubject, events.DecisionSubject)
    require(tuple(type(e.subject) for e in trace) == kinds[:len(trace)], 'unexpected_graph')
    request = trace[0].subject
    require(request.objective == 'inspect supplied trade count')
    require(request.context is not None and request.context.namespace == bundle.result.metadata.namespace
            and request.context.session_id == bundle.result.metadata.session_id
            and request.context.availability == bundle.configuration.availability, 'context_mismatch')
    require(type(task['narrative']) is str and len(task['narrative']) <= 128)
    configuration_fp = fingerprint_config(bundle.configuration)
    input_fp = bundle.inputs[0].content
    for index, name, version, arguments in (
        (2, 'compute_trades', '0.0.4a4', (events.Argument('configuration', configuration_fp.digest), events.Argument('input', input_fp.digest))),
        (4, 'evaluate_diagnostics', '0.1.0a1', (events.Argument('input', input_fp.digest), events.Argument('policy_id', 'eq116-known-rows')))):
        call = trace[index].subject
        require(call.request == events.event_reference(trace[0]) and call.tool_name == name and call.tool_version == version)
        require(call.arguments == events.ArgumentSet(events.DisclosureState.RETAINED_COMPLETE, 2, arguments), 'argument_mismatch')
        result = trace[index + 1].subject
        kind = events.PayloadKind.TOOL_RESULT if index == 2 else events.PayloadKind.DIAGNOSTIC_REPORT
        require(result.call == events.event_reference(trace[index]) and result.outcome is events.ToolOutcome.SUCCEEDED
                and result.payload.kind is kind and result.payload.state is events.DisclosureState.RETAINED_COMPLETE)
    feature = trace[6].subject
    require(feature.result == events.event_reference(trace[3]) and feature.feature_ids == ('session.trade.count',))
    if len(trace) == 8:
        decision = trace[7].subject
        require(decision.request == events.event_reference(trace[0]) and decision.feature_reads == (events.event_reference(trace[6]),))
    store = ledger.Ledger.open(str((directory / 'ledger.sqlite').resolve()))
    try:
        actual = store.verify(expected=expected)
        require(actual == checked, 'store_export_mismatch')
        page = store.export_page(after=0, through=actual.head, limit=8)
        ledger.verify_page(page, start=ledger.Checkpoint(expected.chain_id, 0, '0' * 64), through=actual.head)
        require(tuple(events.encode_event(e) for e in page.events) == tuple(events.encode_event(e) for e in trace))
    finally:
        store.close()
    require(read_file(directory / 'export.json') == encoded(values), 'export_mismatch')
    models = [e.subject for e in trace if type(e.subject) is events.ModelSubject]
    require(len(models) == 1)
    for event in trace:
        subject = event.subject
        if type(subject) is events.ToolCallSubject:
            require(subject.tool_name in ('compute_trades', 'evaluate_diagnostics'))
            require(subject.tool_version == ('0.0.4a4' if subject.tool_name == 'compute_trades' else '0.1.0a1'))
        elif type(subject) is events.ToolResultSubject:
            payload = canonical_content(bundle.result) if subject.payload.kind is events.PayloadKind.TOOL_RESULT else encoded(reports['strict'], lf=False)
            require(events.verify_payload(subject.payload, payload).retained_matched, 'payload_mismatch')
        elif type(subject) is events.FeatureReadSubject:
            require(subject.receipt.state is events.DisclosureState.RETAINED_COMPLETE, 'partial_trace_payload')
            require(events.verify_payload(subject.receipt, encode_receipt(bundle.receipt)).retained_matched)
            require(subject.configuration == fingerprint_config(bundle.configuration) and subject.output == fingerprint_result(bundle.result))
            require(subject.inputs == bundle.receipt.inputs)
            require(subject.context is not None and subject.context.namespace == bundle.result.metadata.namespace
                    and subject.context.session_id == bundle.result.metadata.session_id
                    and subject.context.availability == bundle.configuration.availability)
    return checked.anchor_status.value, models[0].identity_state.value


def actual_replay(bundle: Any) -> tuple[str, int]:
    """Count entries to the actual supported calculator and restore its binding."""
    import equity_features.session as session
    original = session.compute_trades
    calls = 0
    def counted(*args: Any, **kwargs: Any) -> Any:
        nonlocal calls
        calls += 1
        return original(*args, **kwargs)
    session.compute_trades = counted
    try:
        report = replay_bundle(bundle)
    finally:
        session.compute_trades = original
    require(type(report.calculation_count) is int and report.calculation_count == calls, 'calculator_count_mismatch')
    return report.status, calls


def observe(directory: Path, arm: str) -> dict[str, Any]:
    require(arm in ARMS and stat.S_ISDIR(directory.lstat().st_mode))
    wanted = COMMON | {'export.json'} | ({'plain-log.json'} if arm == 'ordinary_log' else {'events.json', 'ledger.sqlite'})
    require({p.name for p in directory.iterdir()} == wanted, 'unexpected_file')
    require(all(stat.S_ISREG(p.lstat().st_mode) for p in directory.iterdir()), 'invalid_file')
    task = shape(parsed(read_file(directory / 'task.json')), {'schema', 'trial_id', 'narrative'})
    require(task['schema'] == 'eq117.task.v1' and type(task['trial_id']) is str and len(task['trial_id']) <= 128)
    base = dict(load='verified', consistency=None, anchor=None, retention=None, model_identity=None,
        narrative_status=None, decision=None, declared_strict_admission=None, recomputed_strict_admission=None,
        recomputed_strict_reason=None, declared_strict=None, recomputed_strict=None, native_result=None,
        configuration=None, input_fingerprints=None, advisory_verification=None, explanation_verification=None,
        replay_status='refused_before_calculator', calculator_calls=0,
        source_authenticated=False, execution_verified=False)
    try:
        bundle = read_bundle(read_file(directory / 'bundle.zip'))
    except BundleError as exc:
        require(exc.code == 'integrity_mismatch', 'invalid_bundle')
        base['load'] = 'integrity_mismatch'
        return base
    require(len(bundle.inputs) == 1 and bundle.inputs[0].role == 'trades')
    require(bundle.receipt.configuration == fingerprint_config(bundle.configuration)
            and bundle.receipt.output == fingerprint_result(bundle.result), 'receipt_mismatch')
    entities = {entity for column in bundle.result.values for entity in column.entities}
    require(len(entities) == 1)
    entity = next(iter(entities))
    reports = shape(parsed(read_file(directory / 'declared-reports.json')), {'strict', 'advisory', 'explanation'})
    declared = _declared_report(reports['strict'], bundle, entity)
    require(type(reports['advisory']) is str and type(reports['explanation']) is str)
    require(len(reports['advisory']) <= 16384 and len(reports['explanation']) <= 32768)
    # This recomputes a public explanation from supplied content, never a fixture.
    explanation = encode_explanation(explain_result(bundle.result, bundle.receipt, bundle.configuration,
                                        entity=entity, feature_id='session.trade.count', evidence_limit=16))
    require(explanation == reports['explanation'].encode('ascii'), 'explanation_mismatch')
    strict = recompute_strict(bundle, entity)
    if strict is not None:
        require(encoded(strict) == encoded(declared), 'declared_diagnostic_mismatch')
    terminal = parsed(read_file(directory / 'terminal.json'))
    anchor, model = _plain(directory, bundle, task, reports, terminal) if arm == 'ordinary_log' else _events(directory, bundle, task, reports, terminal)
    narrative, decision = assessment(bundle.result, task['narrative'])
    replay_status, calculator_calls = actual_replay(bundle)
    base.update(consistency='verified', anchor=anchor, retention='missing' if bundle.inputs[0].batch is None else 'complete',
        model_identity=model, narrative_status=narrative, decision=decision, declared_strict_admission=declared['admission'],
        recomputed_strict_admission='UNKNOWN' if strict is None else strict['admission'],
        recomputed_strict_reason='retained_input_missing' if strict is None else None,
        declared_strict=declared, recomputed_strict=strict,
        native_result=json.loads(canonical_content(bundle.result)), configuration=json.loads(canonical_content(bundle.configuration)),
        input_fingerprints=[dict(role=x.role, input_id=x.input_id, content=fp(x.content)) for x in bundle.inputs],
        advisory_verification='declared_unverified', explanation_verification='recomputed_matched',
        replay_status=replay_status, calculator_calls=calculator_calls)
    return base
